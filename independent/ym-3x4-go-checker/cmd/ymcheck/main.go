// Command ymcheck is an exact-integer checker for the YMROOMHDR 3x4 Perron
// certificate store. It was written only from the owner's published format and
// check specification (see README.md in the module root).
//
// Usage:
//
//	cat sector-341.rooms ... sector-374.rooms | ymcheck [flags] d1.bin [d2.bin ...]
//
// The store byte stream is read once from standard input and every d file is
// checked in that same single pass. Result rows (CERT and STORE) are printed
// only after the whole stream has been consumed and every check has passed.
// On any failed condition the program prints exactly one line
// FAIL|reason=<reason>|json=0 and exits with status 2, printing no value.
//
// Layout (the owner's payload-only decision): the store is the 4096-byte
// header plus payload_bytes. Inside the payload the n rows come first and
// every byte after the last row, up to payload_bytes, must be zero; those
// bytes are inside the merkle. Bytes after header+payload_bytes belong to the
// room file: they are read to end of input and counted, never interpreted
// and never required to be zero (the sector SHA-256 pins them).
//
// Arithmetic is integer only (no non-integer types anywhere): row products and
// sums use an exact signed 128-bit path built on math/bits, the W-symmetry
// accumulators use an exact signed 256-bit path, and every step whose result
// is not provably in range is checked and fails closed on overflow.
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"math/big"
	"math/bits"
	"os"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	headerBytes = 4096
	leafBytes   = 16 << 20 // 16 MiB merkle leaves
	headerMagic = "YMROOMHDR|"

	JE      = 1000
	JB      = 9000
	coefMag = 1000 * JB // multiplies mag*d[h]
	coefZ   = 1000 * JE // multiplies sum(z*d[j])

	maxCnt     = 65535 // cnt is a u16
	maxN       = 1 << 32
	batchRows  = 4096
	batchBytes = 2 << 20
)

// ---------------------------------------------------------------------------
// Fail-closed output.

var outMu sync.Mutex

func sanitize(s string) string {
	var b strings.Builder
	for _, r := range s {
		switch {
		case r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z', r >= '0' && r <= '9':
			b.WriteRune(r)
		case strings.ContainsRune("_:=,.@/+-", r):
			b.WriteRune(r)
		default:
			b.WriteByte('_')
		}
	}
	return b.String()
}

// fail prints the single FAIL line and exits 2. It never returns. It holds
// outMu forever so that no other output can follow or interleave.
func fail(format string, args ...any) {
	outMu.Lock()
	reason := sanitize(fmt.Sprintf(format, args...))
	os.Stdout.WriteString("FAIL|reason=" + reason + "|json=0\n")
	os.Exit(2)
}

// ---------------------------------------------------------------------------
// Exact signed 128-bit integers (two's complement, hi word carries the sign).

type i128 struct{ hi, lo uint64 }

func i128From64(v int64) i128 { return i128{uint64(v >> 63), uint64(v)} }

func (a i128) isNeg() bool { return a.hi>>63 != 0 }

func (a i128) negate() i128 {
	lo, c := bits.Add64(^a.lo, 1, 0)
	return i128{^a.hi + c, lo}
}

// add128 wraps modulo 2^128; callers use it only where the bound is proven.
func add128(a, b i128) i128 {
	lo, c := bits.Add64(a.lo, b.lo, 0)
	hi, _ := bits.Add64(a.hi, b.hi, c)
	return i128{hi, lo}
}

// addInt64 adds a sign-extended int64 (wraps modulo 2^128; bounded by callers).
func addInt64(a i128, v int64) i128 {
	lo, c := bits.Add64(a.lo, uint64(v), 0)
	return i128{a.hi + uint64(v>>63) + c, lo}
}

// addChecked returns ok=false if the exact sum is outside [-2^127, 2^127).
func addChecked(a, b i128) (i128, bool) {
	r := add128(a, b)
	if a.isNeg() == b.isNeg() && r.isNeg() != a.isNeg() {
		return i128{}, false
	}
	return r, true
}

// mul64x64 is the exact signed product of two int64 values (always fits).
func mul64x64(a, b int64) i128 {
	hi, lo := bits.Mul64(uint64(a), uint64(b))
	hi -= uint64(a>>63) & uint64(b)
	hi -= uint64(b>>63) & uint64(a)
	return i128{hi, lo}
}

// mulSmallChecked multiplies by a positive constant c; ok=false if the exact
// product has magnitude >= 2^127 (conservative: fails closed).
func mulSmallChecked(a i128, c uint64) (i128, bool) {
	neg := a.isNeg()
	m := a
	if neg {
		m = a.negate() // unsigned magnitude; -2^127 maps to 2^127
	}
	h0, l0 := bits.Mul64(m.lo, c)
	h1, l1 := bits.Mul64(m.hi, c)
	mid, carry := bits.Add64(h0, l1, 0)
	top := h1 + carry
	if top != 0 || mid>>63 != 0 {
		return i128{}, false
	}
	r := i128{mid, l0}
	if neg {
		r = r.negate()
	}
	return r, true
}

// floorDivPos returns floor(n / d) for d > 0, rounding toward minus infinity.
func floorDivPos(n i128, d int64) i128 {
	if d <= 0 {
		fail("internal:floor_div_nonpositive_divisor")
	}
	dd := uint64(d)
	neg := n.isNeg()
	m := n
	if neg {
		m = n.negate()
	}
	qhi := m.hi / dd
	rhi := m.hi % dd
	qlo, r := bits.Div64(rhi, m.lo, dd)
	q := i128{qhi, qlo}
	if neg {
		if r != 0 {
			q = add128(q, i128{0, 1})
		}
		q = q.negate()
	}
	return q
}

func cmp128(a, b i128) int {
	if a.hi != b.hi {
		if int64(a.hi) < int64(b.hi) {
			return -1
		}
		return 1
	}
	if a.lo != b.lo {
		if a.lo < b.lo {
			return -1
		}
		return 1
	}
	return 0
}

func (a i128) big() *big.Int {
	b := new(big.Int).SetUint64(a.hi)
	b.Lsh(b, 64)
	b.Or(b, new(big.Int).SetUint64(a.lo))
	if a.isNeg() {
		b.Sub(b, new(big.Int).Lsh(big.NewInt(1), 128))
	}
	return b
}

// ---------------------------------------------------------------------------
// Exact signed 256-bit accumulator (two's complement, little-endian words).

type i256 [4]uint64

func (a i256) isNeg() bool { return a[3]>>63 != 0 }

func (a i256) negate() i256 {
	var r i256
	var c uint64 = 1
	for k := 0; k < 4; k++ {
		r[k], c = bits.Add64(^a[k], 0, c)
	}
	return r
}

func (a *i256) add(b i256) {
	var c uint64
	a[0], c = bits.Add64(a[0], b[0], 0)
	a[1], c = bits.Add64(a[1], b[1], c)
	a[2], c = bits.Add64(a[2], b[2], c)
	a[3], _ = bits.Add64(a[3], b[3], c)
}

// mul64x128 is the exact signed product of an int64 and an i128 (< 2^191).
func mul64x128(a int64, b i128) i256 {
	neg := (a < 0) != b.isNeg()
	ma := uint64(a)
	if a < 0 {
		ma = uint64(-a) // MinInt64 maps to 2^63
	}
	mb := b
	if b.isNeg() {
		mb = b.negate()
	}
	h0, l0 := bits.Mul64(ma, mb.lo)
	h1, l1 := bits.Mul64(ma, mb.hi)
	w1, c := bits.Add64(h0, l1, 0)
	r := i256{l0, w1, h1 + c, 0}
	if neg {
		r = r.negate()
	}
	return r
}

func (a i256) big() *big.Int {
	b := new(big.Int)
	for k := 3; k >= 0; k-- {
		b.Lsh(b, 64)
		b.Or(b, new(big.Int).SetUint64(a[k]))
	}
	if a.isNeg() {
		b.Sub(b, new(big.Int).Lsh(big.NewInt(1), 256))
	}
	return b
}

// ---------------------------------------------------------------------------
// Deterministic test vectors x, y for the W-symmetry identity: x_j and y_j are
// the high and low 32-bit halves (arithmetic-shifted right by 1, so each lies in
// [-2^30, 2^30)) of the j-th SplitMix64 output for the seed.

const splitmixGamma = 0x9E3779B97F4A7C15

func xyAt(seed, j uint64) (int64, int64) {
	z := seed + (j+1)*splitmixGamma
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	z ^= z >> 31
	return int64(int32(uint32(z>>32))) >> 1, int64(int32(uint32(z))) >> 1
}

// ---------------------------------------------------------------------------
// Header.

type header struct {
	n            uint64
	payloadBytes uint64
	merkle       string
}

func parseHeader(block []byte) header {
	nl := -1
	for i, c := range block {
		if c == '\n' {
			nl = i
			break
		}
	}
	if nl < 0 {
		fail("header_parse:no_newline_in_first_4096_bytes")
	}
	for i, c := range block[nl+1:] {
		if c != 0 && c != ' ' && c != '\n' {
			fail("header_parse:unexpected_byte_after_header_line:offset=%d", nl+1+i)
		}
	}
	// The line may carry trailing NUL/space/CR padding before its newline;
	// the text itself may hold any byte except NUL.
	text := block[:nl]
	for len(text) > 0 && (text[len(text)-1] == 0 || text[len(text)-1] == ' ' || text[len(text)-1] == '\r') {
		text = text[:len(text)-1]
	}
	for i, c := range text {
		if c == 0 {
			fail("header_parse:nul_inside_header_text:offset=%d", i)
		}
	}
	line := string(text)
	if !strings.HasPrefix(line, headerMagic) {
		fail("header_parse:missing_YMROOMHDR_prefix")
	}
	seen := map[string]string{}
	for _, field := range strings.Split(line, "|")[1:] {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		if k == "n" || k == "payload_bytes" || k == "payload_merkle" {
			if _, dup := seen[k]; dup {
				fail("header_parse:duplicate_key:%s", k)
			}
			seen[k] = v
		}
	}
	var h header
	var err error
	nv, ok := seen["n"]
	if !ok {
		fail("header_parse:missing_n")
	}
	if h.n, err = strconv.ParseUint(nv, 10, 64); err != nil {
		fail("header_parse:bad_n")
	}
	pv, ok := seen["payload_bytes"]
	if !ok {
		fail("header_parse:missing_payload_bytes")
	}
	if h.payloadBytes, err = strconv.ParseUint(pv, 10, 64); err != nil {
		fail("header_parse:bad_payload_bytes")
	}
	mv, ok := seen["payload_merkle"]
	if !ok {
		fail("header_parse:missing_payload_merkle")
	}
	if len(mv) != 64 || strings.Trim(mv, "0123456789abcdef") != "" {
		fail("header_parse:payload_merkle_not_64_lowercase_hex")
	}
	h.merkle = mv
	if h.n == 0 || h.n > maxN {
		fail("header_parse:n_out_of_range:n=%d", h.n)
	}
	if h.payloadBytes < 8*h.n || h.payloadBytes > 1<<56 {
		fail("header_parse:payload_bytes_out_of_range:payload_bytes=%d,n=%d", h.payloadBytes, h.n)
	}
	return h
}

// ---------------------------------------------------------------------------
// d files.

type dfile struct {
	path string
	sha  string
	d    []int64
}

func loadD(path string, n uint64) dfile {
	for _, r := range path {
		if r == '|' || r < 0x20 || r == 0x7f {
			fail("bad_d_path")
		}
	}
	f, err := os.Open(path)
	if err != nil {
		fail("d_open_error:file=%s", path)
	}
	defer f.Close()
	h := sha256.New()
	d := make([]int64, n)
	buf := make([]byte, 1<<20)
	var idx uint64
	for idx < n {
		want := n - idx
		if want > uint64(len(buf)/8) {
			want = uint64(len(buf) / 8)
		}
		b := buf[:want*8]
		if _, err := io.ReadFull(f, b); err != nil {
			fail("d_length_not_8n:file=%s,short,rows_read=%d,n=%d", path, idx, n)
		}
		h.Write(b)
		for i := uint64(0); i < want; i++ {
			d[idx+i] = int64(binary.LittleEndian.Uint64(b[8*i:]))
		}
		idx += want
	}
	var one [1]byte
	k, err := io.ReadFull(f, one[:])
	if k != 0 || err != io.EOF {
		fail("d_length_not_8n:file=%s,long", path)
	}
	return dfile{path: path, sha: hex.EncodeToString(h.Sum(nil)), d: d}
}

// ---------------------------------------------------------------------------
// Per-worker statistics, merged at the end.

type certStat struct {
	have   bool
	minQ   i128
	minH   uint64
	minMag uint16
	atMin  uint64
}

func (cs *certStat) offer(q i128, h uint64, mag uint16, count uint64) {
	if !cs.have {
		*cs = certStat{true, q, h, mag, count}
		return
	}
	switch c := cmp128(q, cs.minQ); {
	case c < 0:
		*cs = certStat{true, q, h, mag, count}
	case c == 0:
		cs.atMin += count
		if h < cs.minH {
			cs.minH, cs.minMag = h, mag
		}
	}
}

type stats struct {
	certs                  []certStat
	flat, nonflat, entries uint64
	diagNotOnce            uint64
	minNZMag, maxMag       uint32
	minW, maxW             uint32
	rows                   uint64
	lhs, rhs               i256
}

func newStats(k int) *stats {
	return &stats{certs: make([]certStat, k), minNZMag: 1 << 16, minW: ^uint32(0)}
}

func (s *stats) merge(o *stats) {
	for k := range s.certs {
		if o.certs[k].have {
			s.certs[k].offer(o.certs[k].minQ, o.certs[k].minH, o.certs[k].minMag, o.certs[k].atMin)
		}
	}
	s.flat += o.flat
	s.nonflat += o.nonflat
	s.entries += o.entries
	s.diagNotOnce += o.diagNotOnce
	s.rows += o.rows
	s.minNZMag = min(s.minNZMag, o.minNZMag)
	s.maxMag = max(s.maxMag, o.maxMag)
	s.minW = min(s.minW, o.minW)
	s.maxW = max(s.maxW, o.maxW)
	s.lhs.add(o.lhs)
	s.rhs.add(o.rhs)
}

// ---------------------------------------------------------------------------
// Pipeline: reader -> (hashers, splitter) -> workers.

type checker struct {
	n            uint64
	payloadBytes uint64
	seed         uint64
	ds           []dfile
	digests      [][32]byte
	rowsEnd      uint64 // payload offset just after row n-1 (set by split)
	rowsEnded    bool
	afterBytes   uint64 // bytes on stdin after header+payload_bytes (not store)
	progress     bool
	start        time.Time
}

type leafJob struct {
	idx uint64
	buf []byte
}

type batch struct {
	h0   uint64
	rows int
	data []byte
}

func (c *checker) read(in io.Reader, hashJobs chan<- leafJob, chunks chan<- []byte) {
	leaves := uint64(len(c.digests))
	for i := uint64(0); i < leaves; i++ {
		size := uint64(leafBytes)
		if rem := c.payloadBytes - i*leafBytes; rem < size {
			size = rem
		}
		buf := make([]byte, size)
		if _, err := io.ReadFull(in, buf); err != nil {
			fail("short_stream:payload_leaf=%d_of_%d", i, leaves)
		}
		hashJobs <- leafJob{i, buf}
		chunks <- buf
		if c.progress && (i%64 == 63 || i+1 == leaves) {
			fmt.Fprintf(os.Stderr, "progress leaf=%d/%d secs=%d\n", i+1, leaves, int64(time.Since(c.start)/time.Second))
		}
	}
	close(hashJobs)
	close(chunks)
	// Bytes after header+payload_bytes are room-file bytes, not store: they are
	// drained to end of input (so the writer of a pipe never gets SIGPIPE) and
	// counted, but neither interpreted nor required to be zero.
	buf := make([]byte, 1<<20)
	for {
		k, err := in.Read(buf)
		c.afterBytes += uint64(k)
		if err == io.EOF {
			return
		}
		if err != nil {
			fail("read_error:after_payload")
		}
	}
}

func (c *checker) hash(jobs <-chan leafJob) {
	for j := range jobs {
		c.digests[j.idx] = sha256.Sum256(j.buf)
	}
}

// checkZeroTail fails closed on the first nonzero byte of tail, which starts
// at payload offset off and lies after row n-1 inside payload_bytes.
func (c *checker) checkZeroTail(tail []byte, off uint64) {
	for i, b := range tail {
		if b != 0 {
			fail("payload_zero_tail_nonzero:payload_offset=%d,byte=%d,rows_end_payload_offset=%d,n=%d",
				off+uint64(i), b, c.rowsEnd, c.n)
		}
	}
}

// split walks row boundaries (reading only cnt) in payload order, hands
// batches of whole rows to the workers, enforces the exact row count, records
// where row n-1 ends, and requires every later payload byte to be zero.
func (c *checker) split(chunks <-chan []byte, jobs chan<- batch) {
	var h uint64
	var carry []byte
	var off uint64 // payload offset of the start of the current chunk
	for chunk := range chunks {
		pos := 0
		if len(carry) > 0 {
			if len(carry) < 8 {
				take := min(8-len(carry), len(chunk))
				carry = append(carry, chunk[:take]...)
				pos = take
			}
			if len(carry) >= 8 {
				rl := 8 + 8*int(binary.LittleEndian.Uint16(carry[6:8]))
				take := min(rl-len(carry), len(chunk)-pos)
				carry = append(carry, chunk[pos:pos+take]...)
				pos += take
				if len(carry) == rl {
					jobs <- batch{h, 1, carry}
					h++
					carry = nil
				}
			}
			if carry != nil {
				off += uint64(len(chunk))
				continue
			}
		}
		start, h0, rows := pos, h, 0
		for h < c.n {
			if len(chunk)-pos < 8 {
				break
			}
			rl := 8 + 8*int(binary.LittleEndian.Uint16(chunk[pos+6:]))
			if len(chunk)-pos < rl {
				break
			}
			pos += rl
			h++
			rows++
			if rows == batchRows || pos-start >= batchBytes {
				jobs <- batch{h0, rows, chunk[start:pos]}
				start, h0, rows = pos, h, 0
			}
		}
		if rows > 0 {
			jobs <- batch{h0, rows, chunk[start:pos]}
		}
		if h == c.n {
			if !c.rowsEnded {
				c.rowsEnd, c.rowsEnded = off+uint64(pos), true
			}
			c.checkZeroTail(chunk[pos:], off+uint64(pos))
		} else if pos < len(chunk) {
			carry = append([]byte(nil), chunk[pos:]...)
		}
		off += uint64(len(chunk))
	}
	if len(carry) > 0 {
		fail("payload_ends_inside_row:h=%d", h)
	}
	if h != c.n {
		fail("payload_ends_before_row_n:rows=%d,n=%d", h, c.n)
	}
	if !c.rowsEnded {
		fail("internal:rows_end_not_recorded")
	}
	close(jobs)
}

func (c *checker) work(st *stats, jobs <-chan batch) {
	js := make([]uint32, maxCnt)
	zs := make([]int64, maxCnt)
	n := c.n
	seed := c.seed
	for b := range jobs {
		data := b.data
		p := 0
		for r := 0; r < b.rows; r++ {
			h := b.h0 + uint64(r)
			if len(data)-p < 8 {
				fail("internal:batch_row_header:h=%d", h)
			}
			w := binary.LittleEndian.Uint32(data[p:])
			mag := binary.LittleEndian.Uint16(data[p+4:])
			cnt := int(binary.LittleEndian.Uint16(data[p+6:]))
			p += 8
			if len(data)-p < 8*cnt {
				fail("internal:batch_row_body:h=%d", h)
			}
			// |rowSum| <= 65535*2^31 < 2^47; |zx|,|zy| <= 65535*2^61 < 2^77.
			var rowSum int64
			var zx, zy i128
			diag := 0
			for e := 0; e < cnt; e++ {
				j := binary.LittleEndian.Uint32(data[p:])
				z := int64(int32(binary.LittleEndian.Uint32(data[p+4:])))
				p += 8
				if uint64(j) >= n {
					fail("column_out_of_range:h=%d,j=%d,n=%d", h, j, n)
				}
				if uint64(j) == h {
					diag++
				} else if z > 0 {
					fail("positive_offdiagonal:h=%d,j=%d,z=%d", h, j, z)
				}
				rowSum += z
				x, y := xyAt(seed, uint64(j))
				zx = addInt64(zx, z*x)
				zy = addInt64(zy, z*y)
				js[e] = j
				zs[e] = z
			}
			if rowSum != 0 {
				fail("row_sum_nonzero:h=%d,sum=%d", h, rowSum)
			}
			if diag != 1 {
				st.diagNotOnce++
			}
			// |w*x_h| <= (2^32-1)*2^30 < 2^62, so it fits in int64.
			xh, yh := xyAt(seed, h)
			st.lhs.add(mul64x128(int64(w)*xh, zy))
			st.rhs.add(mul64x128(int64(w)*yh, zx))
			st.rows++
			st.entries += uint64(cnt)
			st.minW = min(st.minW, w)
			st.maxW = max(st.maxW, w)
			if mag == 0 {
				st.flat++
			} else {
				st.nonflat++
				st.minNZMag = min(st.minNZMag, uint32(mag))
				st.maxMag = max(st.maxMag, uint32(mag))
			}
			for k := range c.ds {
				d := c.ds[k].d
				dh := d[h]
				if mag == 0 {
					if dh != 0 {
						fail("flat_row_d_nonzero:file=%d,h=%d,d=%d", k+1, h, dh)
					}
					continue
				}
				if dh <= 0 {
					fail("nonflat_row_d_nonpositive:file=%d,h=%d,d=%d", k+1, h, dh)
				}
				// |z*d[j]| <= 2^31*2^63 = 2^94 and cnt <= 65535, so |s| < 2^110.
				var s i128
				for e := 0; e < cnt; e++ {
					s = add128(s, mul64x64(zs[e], d[js[e]]))
				}
				// coefMag*mag <= 9e6*65535 < 2^40 fits int64; the product < 2^103.
				t1 := mul64x64(int64(coefMag)*int64(mag), dh)
				t2, ok := mulSmallChecked(s, coefZ)
				if !ok {
					fail("arithmetic_overflow:file=%d,h=%d,term=1000*JE*sum", k+1, h)
				}
				num, ok := addChecked(t1, t2)
				if !ok {
					fail("arithmetic_overflow:file=%d,h=%d,term=numerator", k+1, h)
				}
				st.certs[k].offer(floorDivPos(num, dh), h, mag, 1)
			}
		}
		if p != len(data) {
			fail("internal:batch_length:h0=%d", b.h0)
		}
	}
}

func merkleRoot(digests [][32]byte) string {
	text := make([]byte, 0, 64*len(digests))
	for _, d := range digests {
		text = hex.AppendEncode(text, d[:])
	}
	sum := sha256.Sum256(text)
	return hex.EncodeToString(sum[:])
}

func main() {
	start := time.Now()
	seed := flag.Uint64("seed", 20261102, "seed for the x, y vectors of the W-symmetry identity")
	workers := flag.Int("workers", runtime.NumCPU(), "row-check worker goroutines")
	hashers := flag.Int("hashers", max(1, min(4, runtime.NumCPU()/2)), "SHA-256 leaf goroutines")
	expectN := flag.Uint64("expect-n", 0, "if nonzero, header n must equal this")
	expectPB := flag.Uint64("expect-payload-bytes", 0, "if nonzero, header payload_bytes must equal this")
	expectMerkle := flag.String("expect-merkle", "", "if set, header payload_merkle must equal this")
	progress := flag.Bool("progress", false, "print progress to stderr")
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: cat store-sectors... | ymcheck [flags] d1.bin [d2.bin ...]")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() == 0 {
		fail("usage:no_d_files")
	}
	if *workers < 1 || *hashers < 1 {
		fail("usage:workers_and_hashers_must_be_positive")
	}

	in := os.Stdin
	block := make([]byte, headerBytes)
	if _, err := io.ReadFull(in, block); err != nil {
		fail("short_stream:header")
	}
	hdr := parseHeader(block)
	if *expectN != 0 && hdr.n != *expectN {
		fail("header_pin_mismatch:n=%d,expected=%d", hdr.n, *expectN)
	}
	if *expectPB != 0 && hdr.payloadBytes != *expectPB {
		fail("header_pin_mismatch:payload_bytes=%d,expected=%d", hdr.payloadBytes, *expectPB)
	}
	if *expectMerkle != "" && hdr.merkle != *expectMerkle {
		fail("header_pin_mismatch:payload_merkle")
	}

	c := &checker{n: hdr.n, payloadBytes: hdr.payloadBytes, seed: *seed, progress: *progress, start: start}
	for _, p := range flag.Args() {
		c.ds = append(c.ds, loadD(p, hdr.n))
	}
	c.digests = make([][32]byte, (hdr.payloadBytes+leafBytes-1)/leafBytes)

	hashJobs := make(chan leafJob, 4)
	chunks := make(chan []byte, 4)
	jobs := make(chan batch, 4**workers)
	var hashWG, workWG, splitWG, readWG sync.WaitGroup
	for i := 0; i < *hashers; i++ {
		hashWG.Add(1)
		go func() { defer hashWG.Done(); c.hash(hashJobs) }()
	}
	all := make([]*stats, *workers)
	for i := range all {
		all[i] = newStats(len(c.ds))
		workWG.Add(1)
		go func(st *stats) { defer workWG.Done(); c.work(st, jobs) }(all[i])
	}
	splitWG.Add(1)
	go func() { defer splitWG.Done(); c.split(chunks, jobs) }()
	readWG.Add(1)
	go func() { defer readWG.Done(); c.read(in, hashJobs, chunks) }()
	readWG.Wait()
	splitWG.Wait()
	workWG.Wait()
	hashWG.Wait()

	// The merkle is checked here, after every goroutine has finished, so that a
	// structural error found by the splitter or a worker (including a nonzero
	// byte in the payload's zero tail) is always the reported reason.
	root := merkleRoot(c.digests)
	if root != hdr.merkle {
		fail("merkle_mismatch:computed=%s", root)
	}
	total := newStats(len(c.ds))
	for _, st := range all {
		total.merge(st)
	}
	if total.rows != hdr.n {
		fail("internal:row_count:%d", total.rows)
	}
	if total.lhs != total.rhs {
		fail("w_symmetry_mismatch:seed=%d", c.seed)
	}
	if total.nonflat == 0 {
		fail("no_nonflat_rows")
	}
	for k := range c.ds {
		if !total.certs[k].have {
			fail("internal:no_ratio:file=%d", k+1)
		}
	}

	var b strings.Builder
	for k, df := range c.ds {
		cs := total.certs[k]
		fmt.Fprintf(&b, "CERT|d=%s|d_sha256=%s|t_cert=%s|row=%d|mag=%d|rows_at_min=%d|json=0\n",
			df.path, df.sha, cs.minQ.big().String(), cs.minH, cs.minMag, cs.atMin)
	}
	fmt.Fprintf(&b, "STORE|n=%d|payload_bytes=%d|merkle=PASS|flat_rows=%d|min_nonzero_mag=%d|max_mag=%d|"+
		"row_sums_zero=PASS|w_symmetry=PASS|seed=%d|entries=%d|nonflat_rows=%d|diag_not_once_rows=%d|"+
		"min_w=%d|max_w=%d|rows_end_payload_offset=%d|payload_zero_tail_bytes=%d|after_payload_bytes=%d|"+
		"payload_merkle=%s|w_symmetry_lhs=%s|secs=%d|json=0\n",
		hdr.n, hdr.payloadBytes, total.flat, total.minNZMag, total.maxMag, c.seed, total.entries,
		total.nonflat, total.diagNotOnce, total.minW, total.maxW, c.rowsEnd, hdr.payloadBytes-c.rowsEnd,
		c.afterBytes, root, total.lhs.big().String(), int64(time.Since(start)/time.Second))
	outMu.Lock()
	if _, err := os.Stdout.WriteString(b.String()); err != nil {
		os.Exit(2)
	}
	os.Exit(0)
}
