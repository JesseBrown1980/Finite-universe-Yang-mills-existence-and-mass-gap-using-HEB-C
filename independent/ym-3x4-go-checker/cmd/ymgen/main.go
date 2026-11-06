// Command ymgen builds synthetic YMROOMHDR stores and d files for the control
// suite, and carries two independent cross-checks of ymcheck:
//
//	ref    a slow reference checker that uses math/big for every arithmetic step
//	eigen  the exact floor(1e6 * lambda_min(H')) of a tiny store, by bisection
//	       on an exact positive-semidefiniteness test (all principal minors)
//
// Subcommands: random, text, dvec, dlist, dset, dresize, flip, remerkle, zpair,
// dump, fill, ref, eigen, bench. Integer arithmetic only.
package main

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
)

const (
	headerBytes = 4096
	leafBytes   = 16 << 20
	JE          = 1000
	JB          = 9000
)

func die(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "ymgen: "+format+"\n", args...)
	os.Exit(1)
}

// ---------------------------------------------------------------------------
// Store model and serialization.

type entry struct {
	j uint32
	z int32
}

type row struct {
	w    uint32
	mag  uint16
	ents []entry
}

func serializeRows(rows []row) []byte {
	var b bytes.Buffer
	var tmp [8]byte
	for _, r := range rows {
		if len(r.ents) > 65535 {
			die("row has %d entries", len(r.ents))
		}
		binary.LittleEndian.PutUint32(tmp[0:], r.w)
		binary.LittleEndian.PutUint16(tmp[4:], r.mag)
		binary.LittleEndian.PutUint16(tmp[6:], uint16(len(r.ents)))
		b.Write(tmp[:])
		for _, e := range r.ents {
			binary.LittleEndian.PutUint32(tmp[0:], e.j)
			binary.LittleEndian.PutUint32(tmp[4:], uint32(e.z))
			b.Write(tmp[:])
		}
	}
	return b.Bytes()
}

func merkleHex(payload []byte) string {
	var text []byte
	for p := 0; p < len(payload); p += leafBytes {
		sum := sha256.Sum256(payload[p:min(p+leafBytes, len(payload))])
		text = append(text, hex.EncodeToString(sum[:])...)
	}
	sum := sha256.Sum256(text)
	return hex.EncodeToString(sum[:])
}

type hdrOpts struct {
	n, pb          int64 // -1: true value
	merkle         string
	spaces         bool // pad the line with spaces up to byte 4095 instead of NULs after '\n'
	nulnl          bool // pad the line with NULs and put '\n' at byte 4095
	ztail          int64
	pad            int64
	padFill        string
	padSeed        uint64
	raw            string // if set, use this header line verbatim (no '\n')
	targetPayload  int64
	fillerColumnOf func(h int) uint32
}

func (o *hdrOpts) register(fs *flag.FlagSet) {
	fs.Int64Var(&o.n, "hdr-n", -1, "override header n")
	fs.Int64Var(&o.pb, "hdr-pb", -1, "override header payload_bytes")
	fs.StringVar(&o.merkle, "hdr-merkle", "", "override header payload_merkle")
	fs.BoolVar(&o.spaces, "hdr-spaces", false, "pad header line with spaces")
	fs.BoolVar(&o.nulnl, "hdr-nulnl", false, "pad header line with NULs, newline at byte 4095")
	fs.Int64Var(&o.ztail, "ztail", 0, "zero bytes after the last row INSIDE the payload (counted in payload_bytes, covered by the merkle)")
	fs.Int64Var(&o.pad, "pad", 4096, "bytes AFTER header+payload_bytes (the room-file tail, not store)")
	fs.StringVar(&o.padFill, "pad-fill", "zero", "content of the -pad bytes: "+fillModes)
	fs.Uint64Var(&o.padSeed, "pad-seed", 1, "seed for -pad-fill nonzero|rooms")
	fs.StringVar(&o.raw, "hdr-raw", "", "verbatim header line")
	fs.Int64Var(&o.targetPayload, "target-payload", 0, "append z=0 off-diagonal entries until the rows have exactly this many bytes (before -ztail)")
}

const fillModes = "zero | nonzero (SplitMix64 bytes, every byte in 1..255) | rooms (consecutive little-endian words mix64(seed+i), the shape of Host8 room stubs)"

// mix64 is the SplitMix64 finalizer.
func mix64(z uint64) uint64 {
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

// writeFill writes n bytes of the given fill mode to w.
func writeFill(w io.Writer, mode string, seed uint64, n int64) error {
	buf := make([]byte, 1<<20)
	r := &rng{seed}
	var word uint64 // index of the next rooms word
	for n > 0 {
		k := int(min(n, int64(len(buf))))
		b := buf[:k]
		switch mode {
		case "zero":
			clear(b)
		case "nonzero":
			for i := range b {
				b[i] = byte(1 + r.next()%255)
			}
		case "rooms":
			for i := 0; i < k; i += 8 {
				var tmp [8]byte
				binary.LittleEndian.PutUint64(tmp[:], mix64(seed+word))
				word++
				copy(b[i:], tmp[:])
			}
		default:
			die("unknown fill mode %q (want %s)", mode, fillModes)
		}
		if _, err := w.Write(b); err != nil {
			return err
		}
		n -= int64(k)
	}
	return nil
}

// fillCmd streams n fill bytes to stdout (or -out), for the pipe controls.
func fillCmd(args []string) {
	fs := flag.NewFlagSet("fill", flag.ExitOnError)
	n := fs.Int64("bytes", 0, "number of bytes")
	mode := fs.String("mode", "rooms", fillModes)
	seed := fs.Uint64("seed", 1, "seed")
	out := fs.String("out", "", "output file (default stdout)")
	fs.Parse(args)
	f := os.Stdout
	if *out != "" {
		var err error
		if f, err = os.Create(*out); err != nil {
			die("%v", err)
		}
		defer f.Close()
	}
	bw := bufio.NewWriterSize(f, 4<<20)
	if err := writeFill(bw, *mode, *seed, *n); err != nil {
		die("write: %v", err)
	}
	if err := bw.Flush(); err != nil {
		die("write: %v", err)
	}
}

func fillTo(rows []row, target int64) {
	size := int64(len(serializeRows(rows)))
	if target == 0 {
		return
	}
	extra := target - size
	if extra < 0 || extra%8 != 0 {
		die("target payload %d unreachable from %d", target, size)
	}
	n := len(rows)
	for h := 0; extra > 0; h = (h + 1) % n {
		if len(rows[h].ents) < 65535 {
			rows[h].ents = append(rows[h].ents, entry{uint32((h + 1) % n), 0})
			extra -= 8
		}
	}
}

func writeStore(path string, rows []row, o hdrOpts) {
	fillTo(rows, o.targetPayload)
	payload := serializeRows(rows)
	if o.ztail < 0 {
		die("negative -ztail")
	}
	payload = append(payload, make([]byte, o.ztail)...)
	n, pb, mk := int64(len(rows)), int64(len(payload)), merkleHex(payload)
	if o.n >= 0 {
		n = o.n
	}
	if o.pb >= 0 {
		pb = o.pb
	}
	if o.merkle != "" {
		mk = o.merkle
	}
	line := fmt.Sprintf("YMROOMHDR|format=synthetic-ymgen|n=%d|row=w:u32,mag:u16,cnt:u16,cnt*(j:u32,z:i32)|payload_bytes=%d|leaf_bytes=%d|payload_merkle=%s|end", n, pb, leafBytes, mk)
	if o.raw != "" {
		line = o.raw
	}
	hdr := make([]byte, headerBytes)
	if o.spaces || o.nulnl {
		if o.spaces {
			for i := range hdr {
				hdr[i] = ' '
			}
		}
		copy(hdr, line)
		hdr[headerBytes-1] = '\n'
	} else {
		copy(hdr, line+"\n")
	}
	if len(line)+1 > headerBytes {
		die("header too long")
	}
	f, err := os.Create(path)
	if err != nil {
		die("%v", err)
	}
	defer f.Close()
	bw := bufio.NewWriterSize(f, 4<<20)
	bw.Write(hdr)
	bw.Write(payload)
	if err := writeFill(bw, o.padFill, o.padSeed, o.pad); err != nil {
		die("write: %v", err)
	}
	if err := bw.Flush(); err != nil {
		die("write: %v", err)
	}
}

// ---------------------------------------------------------------------------
// Deterministic RNG (SplitMix64) for the generator.

type rng struct{ s uint64 }

func (r *rng) next() uint64 {
	r.s += 0x9E3779B97F4A7C15
	z := r.s
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

func (r *rng) intn(n int) int { return int(r.next() % uint64(n)) }

// randomStore builds a W-self-adjoint Laplacian-type store: for each symmetric
// edge {a,b} with coupling c, Z[a][b] = -c*w[b], Z[b][a] = -c*w[a] and the
// diagonals absorb +c*w[b], +c*w[a]. Then W*Z is symmetric and rows sum to 0.
func randomStore(args []string) {
	fs := flag.NewFlagSet("random", flag.ExitOnError)
	n := fs.Int("rows", 300, "rows")
	flat := fs.Int("flat", 20, "flat rows (mag=0)")
	deg := fs.Int("deg", 3, "edges started per row")
	wmax := fs.Int("wmax", 7, "max weight w")
	magmax := fs.Int("magmax", 6, "max mag")
	cmax := fs.Int("cmax", 4, "max coupling")
	seed := fs.Uint64("seed", 1, "seed")
	dup := fs.Bool("dup", false, "split some off-diagonal entries into duplicate entries")
	zeros := fs.Bool("zeros", false, "add some explicit z=0 off-diagonal entries")
	defect := fs.String("defect", "", "posoff|rowsum|asym|colrange|emptyflat")
	out := fs.String("out", "", "output store")
	var o hdrOpts
	o.register(fs)
	fs.Parse(args)
	r := &rng{*seed}
	N := *n
	w := make([]uint32, N)
	mag := make([]uint16, N)
	for h := range w {
		w[h] = uint32(1 + r.intn(*wmax))
		mag[h] = uint16(1 + r.intn(*magmax))
	}
	perm := make([]int, N)
	for i := range perm {
		perm[i] = i
	}
	for i := N - 1; i > 0; i-- {
		k := r.intn(i + 1)
		perm[i], perm[k] = perm[k], perm[i]
	}
	for _, h := range perm[:*flat] {
		mag[h] = 0
	}
	type key struct{ a, b int }
	edges := map[key]int{}
	for h := 0; h < N && N > 1; h++ {
		for k := 0; k < *deg; k++ {
			j := r.intn(N)
			if j == h {
				continue
			}
			edges[key{min(h, j), max(h, j)}] = 1 + r.intn(*cmax)
		}
	}
	keys := make([]key, 0, len(edges))
	for k := range edges {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool {
		if keys[i].a != keys[j].a {
			return keys[i].a < keys[j].a
		}
		return keys[i].b < keys[j].b
	})
	if *defect == "posoff" {
		if len(keys) == 0 {
			die("no edge for posoff")
		}
		edges[keys[0]] = -1
		fmt.Fprintf(os.Stderr, "defect posoff: edge %d-%d coupling -1\n", keys[0].a, keys[0].b)
	}
	diag := make([]int64, N)
	off := make([][]entry, N)
	for _, k := range keys {
		c := int64(edges[k])
		zab, zba := -c*int64(w[k.b]), -c*int64(w[k.a])
		diag[k.a] -= zab
		diag[k.b] -= zba
		off[k.a] = append(off[k.a], entry{uint32(k.b), int32(zab)})
		off[k.b] = append(off[k.b], entry{uint32(k.a), int32(zba)})
	}
	rows := make([]row, N)
	for h := 0; h < N; h++ {
		if diag[h] > 1<<31-1 || diag[h] < -(1<<31) {
			die("diagonal overflow at row %d", h)
		}
		ents := []entry{{uint32(h), int32(diag[h])}}
		for _, e := range off[h] {
			if *dup && e.z <= -2 && r.intn(3) == 0 {
				a := e.z / 2
				ents = append(ents, entry{e.j, a}, entry{e.j, e.z - a})
			} else {
				ents = append(ents, e)
			}
		}
		if *zeros && r.intn(4) == 0 && N > 1 {
			j := r.intn(N)
			if j != h {
				ents = append(ents, entry{uint32(j), 0})
			}
		}
		for i := len(ents) - 1; i > 0; i-- {
			k := r.intn(i + 1)
			ents[i], ents[k] = ents[k], ents[i]
		}
		rows[h] = row{w[h], mag[h], ents}
	}
	firstOff := func() (int, int) {
		for h := range rows {
			for i, e := range rows[h].ents {
				if int(e.j) != h && e.z != 0 {
					return h, i
				}
			}
		}
		die("no off-diagonal entry")
		return 0, 0
	}
	switch *defect {
	case "", "posoff":
	case "rowsum":
		bumpFirstNonflatDiagonal(rows)
	case "asym":
		h, _ := firstOff()
		rows[h].w++
		fmt.Fprintf(os.Stderr, "defect asym: row %d w -> %d\n", h, rows[h].w)
	case "colrange":
		h, i := firstOff()
		rows[h].ents[i].j = uint32(N)
		fmt.Fprintf(os.Stderr, "defect colrange: row %d entry %d j -> %d\n", h, i, N)
	case "emptyflat":
		for h := range rows {
			if rows[h].mag == 0 {
				fmt.Fprintf(os.Stderr, "defect emptyflat: row %d had %d entries\n", h, len(rows[h].ents))
			}
		}
	default:
		die("unknown defect %q", *defect)
	}
	writeStore(*out, rows, o)
}

func bumpFirstNonflatDiagonal(rows []row) {
	for h := range rows {
		if rows[h].mag == 0 {
			continue
		}
		for i := range rows[h].ents {
			if int(rows[h].ents[i].j) == h {
				rows[h].ents[i].z++
				fmt.Fprintf(os.Stderr, "defect rowsum: row %d diagonal +1\n", h)
				return
			}
		}
	}
	die("no non-flat diagonal")
}

// textStore reads rows "w mag : j:z j:z*k ..." (one per line, '#' comments).
func textStore(args []string) {
	fs := flag.NewFlagSet("text", flag.ExitOnError)
	in := fs.String("in", "", "text spec")
	out := fs.String("out", "", "output store")
	var o hdrOpts
	o.register(fs)
	fs.Parse(args)
	src, err := os.ReadFile(*in)
	if err != nil {
		die("%v", err)
	}
	var rows []row
	for _, ln := range strings.Split(string(src), "\n") {
		ln = strings.TrimSpace(strings.SplitN(ln, "#", 2)[0])
		if ln == "" {
			continue
		}
		head, body, ok := strings.Cut(ln, ":")
		if !ok {
			die("bad line %q", ln)
		}
		hf := strings.Fields(head)
		if len(hf) != 2 {
			die("bad head %q", head)
		}
		w, err1 := strconv.ParseUint(hf[0], 10, 32)
		m, err2 := strconv.ParseUint(hf[1], 10, 16)
		if err1 != nil || err2 != nil {
			die("bad head %q", head)
		}
		r := row{w: uint32(w), mag: uint16(m)}
		for _, tok := range strings.Fields(body) {
			js, zs, ok := strings.Cut(tok, ":")
			if !ok {
				die("bad token %q", tok)
			}
			rep := int64(1)
			if a, b, ok := strings.Cut(zs, "*"); ok {
				zs = a
				if rep, err = strconv.ParseInt(b, 10, 64); err != nil {
					die("bad rep %q", tok)
				}
			}
			j, err1 := strconv.ParseUint(js, 10, 32)
			z, err2 := strconv.ParseInt(zs, 10, 32)
			if err1 != nil || err2 != nil {
				die("bad token %q", tok)
			}
			for k := int64(0); k < rep; k++ {
				r.ents = append(r.ents, entry{uint32(j), int32(z)})
			}
		}
		rows = append(rows, r)
	}
	writeStore(*out, rows, o)
}

// ---------------------------------------------------------------------------
// Parsing a store file (no validation beyond structure; used by dvec, dump,
// zpair, eigen). ref has its own validating parser.

type parsed struct {
	raw     []byte
	n       int
	pb      int
	rows    []row
	rowOff  []int // absolute stream offset of each row
	merkle  string
	hdrLine string
}

func parseStoreFile(path string) *parsed {
	raw, err := os.ReadFile(path)
	if err != nil {
		die("%v", err)
	}
	if len(raw) < headerBytes {
		die("short store")
	}
	nl := bytes.IndexByte(raw[:headerBytes], '\n')
	if nl < 0 {
		die("no header newline")
	}
	p := &parsed{raw: raw, hdrLine: string(raw[:nl])}
	for _, f := range strings.Split(strings.TrimRight(p.hdrLine, " "), "|") {
		k, v, _ := strings.Cut(f, "=")
		switch k {
		case "n":
			p.n, _ = strconv.Atoi(v)
		case "payload_bytes":
			p.pb, _ = strconv.Atoi(v)
		case "payload_merkle":
			p.merkle = v
		}
	}
	pos := headerBytes
	for h := 0; h < p.n; h++ {
		if pos+8 > len(raw) {
			die("truncated at row %d", h)
		}
		r := row{w: binary.LittleEndian.Uint32(raw[pos:]), mag: binary.LittleEndian.Uint16(raw[pos+4:])}
		cnt := int(binary.LittleEndian.Uint16(raw[pos+6:]))
		p.rowOff = append(p.rowOff, pos)
		pos += 8
		for e := 0; e < cnt; e++ {
			r.ents = append(r.ents, entry{binary.LittleEndian.Uint32(raw[pos:]), int32(binary.LittleEndian.Uint32(raw[pos+4:]))})
			pos += 8
		}
		p.rows = append(p.rows, r)
	}
	return p
}

// ---------------------------------------------------------------------------
// d vectors.

func writeD(path string, d []int64) {
	b := make([]byte, 8*len(d))
	for i, v := range d {
		binary.LittleEndian.PutUint64(b[8*i:], uint64(v))
	}
	if err := os.WriteFile(path, b, 0o644); err != nil {
		die("%v", err)
	}
}

func readD(path string) []int64 {
	b, err := os.ReadFile(path)
	if err != nil {
		die("%v", err)
	}
	d := make([]int64, len(b)/8)
	for i := range d {
		d[i] = int64(binary.LittleEndian.Uint64(b[8*i:]))
	}
	return d
}

// dvec writes a d vector for a store: perron (integer power iteration on
// c*I - H' over the non-flat rows), random, big (values near 2^62) or const.
func dvec(args []string) {
	fs := flag.NewFlagSet("dvec", flag.ExitOnError)
	store := fs.String("store", "", "store")
	mode := fs.String("mode", "perron", "perron|random|big|const")
	seed := fs.Uint64("seed", 7, "seed")
	iters := fs.Int("iters", 4000, "power iterations")
	maxv := fs.Int64("max", 1<<40, "random: max value; perron: scale")
	out := fs.String("out", "", "output d file")
	fs.Parse(args)
	p := parseStoreFile(*store)
	n := p.n
	d := make([]int64, n)
	r := &rng{*seed}
	switch *mode {
	case "const":
		for h := range d {
			if p.rows[h].mag != 0 {
				d[h] = 1
			}
		}
	case "random":
		for h := range d {
			if p.rows[h].mag != 0 {
				d[h] = 1 + int64(r.next()%uint64(*maxv))
			}
		}
	case "big":
		for h := range d {
			if p.rows[h].mag != 0 {
				d[h] = 1<<62 - int64(r.next()%(1<<40))
			}
		}
	case "perron":
		// H'[h][j] = 9*mag[h]*[h==j] + Z[h][j], restricted to non-flat rows.
		hdiag := make([]int64, n)
		var shift int64
		for h, rw := range p.rows {
			if rw.mag == 0 {
				continue
			}
			hdiag[h] = int64(JB/JE) * int64(rw.mag)
			var abs int64
			for _, e := range rw.ents {
				if int(e.j) == h {
					hdiag[h] += int64(e.z)
				}
				abs += max(int64(e.z), -int64(e.z))
			}
			if abs+hdiag[h] > 1<<20 {
				die("perron mode needs small entries")
			}
			shift = max(shift, hdiag[h]+abs)
		}
		shift++
		v := make([]int64, n)
		for h := range v {
			if p.rows[h].mag != 0 {
				v[h] = *maxv
			}
		}
		nv := make([]int64, n)
		for it := 0; it < *iters; it++ {
			var top int64
			for h, rw := range p.rows {
				if rw.mag == 0 {
					continue
				}
				// (shift*I - H') v
				acc := (shift - int64(JB/JE)*int64(rw.mag)) * v[h]
				for _, e := range rw.ents {
					acc -= int64(e.z) * v[e.j]
				}
				nv[h] = acc
				top = max(top, acc)
			}
			for h := range v {
				if p.rows[h].mag != 0 {
					v[h] = max(1, nv[h]/(top / *maxv + 1))
				}
			}
		}
		for h := range d {
			if p.rows[h].mag != 0 {
				d[h] = max(1, v[h])
			}
		}
	default:
		die("unknown mode")
	}
	writeD(*out, d)
}

func dlist(args []string) {
	fs := flag.NewFlagSet("dlist", flag.ExitOnError)
	vals := fs.String("vals", "", "comma-separated int64 values")
	out := fs.String("out", "", "output")
	fs.Parse(args)
	var d []int64
	for _, s := range strings.Split(*vals, ",") {
		v, err := strconv.ParseInt(strings.TrimSpace(s), 10, 64)
		if err != nil {
			die("bad value %q", s)
		}
		d = append(d, v)
	}
	writeD(*out, d)
}

func dset(args []string) {
	fs := flag.NewFlagSet("dset", flag.ExitOnError)
	in := fs.String("in", "", "input d")
	out := fs.String("out", "", "output d")
	h := fs.Int("h", 0, "index")
	v := fs.Int64("v", 0, "value")
	fs.Parse(args)
	d := readD(*in)
	d[*h] = *v
	writeD(*out, d)
}

func dresize(args []string) {
	fs := flag.NewFlagSet("dresize", flag.ExitOnError)
	in := fs.String("in", "", "input")
	out := fs.String("out", "", "output")
	delta := fs.Int("delta", 0, "bytes to add (zeros) or remove")
	fs.Parse(args)
	b, err := os.ReadFile(*in)
	if err != nil {
		die("%v", err)
	}
	if *delta < 0 {
		b = b[:len(b)+*delta]
	} else {
		b = append(b, make([]byte, *delta)...)
	}
	os.WriteFile(*out, b, 0o644)
}

func flip(args []string) {
	fs := flag.NewFlagSet("flip", flag.ExitOnError)
	in := fs.String("in", "", "input")
	out := fs.String("out", "", "output")
	off := fs.Int("offset", 0, "byte offset")
	x := fs.Int("xor", 1, "xor mask")
	fs.Parse(args)
	b, err := os.ReadFile(*in)
	if err != nil {
		die("%v", err)
	}
	b[*off] ^= byte(*x)
	os.WriteFile(*out, b, 0o644)
}

// remerkle rewrites the header's payload_merkle to match the payload bytes.
func remerkle(args []string) {
	fs := flag.NewFlagSet("remerkle", flag.ExitOnError)
	in := fs.String("in", "", "input")
	out := fs.String("out", "", "output")
	fs.Parse(args)
	p := parseStoreFile(*in)
	mk := merkleHex(p.raw[headerBytes : headerBytes+p.pb])
	i := bytes.Index(p.raw[:headerBytes], []byte("payload_merkle="+p.merkle))
	if i < 0 {
		die("no merkle field")
	}
	copy(p.raw[i+len("payload_merkle="):], mk)
	os.WriteFile(*out, p.raw, 0o644)
}

// zpair changes four z values consistently (z_hj-=1, z_hh+=1, z_jh-=1,
// z_jj+=1 for a pair with w_h == w_j): structure, signs, row sums and
// W-symmetry all still hold, so only the merkle can catch it.
func zpair(args []string) {
	fs := flag.NewFlagSet("zpair", flag.ExitOnError)
	in := fs.String("in", "", "input")
	out := fs.String("out", "", "output")
	skip := fs.Int("skip", 0, "skip this many candidate pairs")
	fs.Parse(args)
	p := parseStoreFile(*in)
	find := func(h, j int) []int {
		var idx []int
		for i, e := range p.rows[h].ents {
			if int(e.j) == j {
				idx = append(idx, i)
			}
		}
		return idx
	}
	put := func(h, i int, z int32) {
		binary.LittleEndian.PutUint32(p.raw[p.rowOff[h]+8+8*i+4:], uint32(z))
	}
	for h := range p.rows {
		for _, e := range p.rows[h].ents {
			j := int(e.j)
			if j <= h || p.rows[h].w != p.rows[j].w {
				continue
			}
			hj, jh, hh, jj := find(h, j), find(j, h), find(h, h), find(j, j)
			if len(hj) != 1 || len(jh) != 1 || len(hh) != 1 || len(jj) != 1 {
				continue
			}
			if *skip > 0 {
				*skip--
				continue
			}
			put(h, hj[0], p.rows[h].ents[hj[0]].z-1)
			put(h, hh[0], p.rows[h].ents[hh[0]].z+1)
			put(j, jh[0], p.rows[j].ents[jh[0]].z-1)
			put(j, jj[0], p.rows[j].ents[jj[0]].z+1)
			fmt.Fprintf(os.Stderr, "zpair: rows %d,%d (w=%d)\n", h, j, p.rows[h].w)
			os.WriteFile(*out, p.raw, 0o644)
			return
		}
	}
	die("no candidate pair")
}

// dump prints "R h w mag cnt row_off" and "E h e j z j_off z_off" lines.
func dump(args []string) {
	fs := flag.NewFlagSet("dump", flag.ExitOnError)
	store := fs.String("store", "", "store")
	fs.Parse(args)
	p := parseStoreFile(*store)
	for h, r := range p.rows {
		fmt.Printf("R %d %d %d %d %d\n", h, r.w, r.mag, len(r.ents), p.rowOff[h])
		for i, e := range r.ents {
			o := p.rowOff[h] + 8 + 8*i
			fmt.Printf("E %d %d %d %d %d %d\n", h, i, e.j, e.z, o, o+4)
		}
	}
}

func main() {
	if len(os.Args) < 2 {
		die("usage: ymgen <random|text|dvec|dlist|dset|dresize|flip|remerkle|zpair|dump|fill|ref|eigen|bench> [flags]")
	}
	cmds := map[string]func([]string){
		"random": randomStore, "text": textStore, "dvec": dvec, "dlist": dlist, "dset": dset,
		"dresize": dresize, "flip": flip, "remerkle": remerkle, "zpair": zpair, "dump": dump,
		"fill": fillCmd, "ref": refCheck, "eigen": eigen, "bench": bench,
	}
	f, ok := cmds[os.Args[1]]
	if !ok {
		die("unknown subcommand %q", os.Args[1])
	}
	f(os.Args[2:])
}
