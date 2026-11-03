// Independent YM 3x4 Perron certificate verifier.
// Authored from the supplied wire format, without relying on repository verifiers.
// Go 1.23+, standard library only. No floating point in verification.
package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"hash"
	"io"
	"math/big"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"
)

const (
	expectedN              int64 = 45508080
	expectedPayload        int64 = 26850881536
	expectedZeroPadding    int64 = 742160
	expectedRawTailBytes   int64 = 349114368
	expectedRawTailNonzero int64 = 347747335
	expectedManifest             = "9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3"
	expectedMerkle               = "ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b"
	controlHash                  = "956b73bc6f4ec5712184eb52f67d8e0adab467c1ea843ba257126278368210da"
	blindHash                    = "34e71facb2689a46a44cb347604f0b361760020c8810748f6e9cc513daa53686"
	blind2Hash                   = "637fe9e293505d950503abbd615840471e4ef14a2a23128d44233992f82999fe"
	blind3Hash                   = "f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1"
	leafSize                     = 16 << 20
)

var hex64 = regexp.MustCompile(`^[0-9a-f]{64}$`)

type Config struct {
	dir, control, blind                              string
	n, payload                                       int64
	manifestHash, merkleHash, controlHash, blindHash string
	sectors                                          int
	paddingBytes, rawTailBytes, rawTailNonzero       int64
	fault                                            string
}

func die(err error) { fmt.Fprintln(os.Stderr, "FAIL:", err); os.Exit(1) }
func sameHash(actual, want, label string) error {
	if want != "" && actual != want {
		return fmt.Errorf("%s sha256 mismatch: got %s expected %s", label, actual, want)
	}
	return nil
}
func fileSHA(path string) (string, error) {
	f, e := os.Open(path)
	if e != nil {
		return "", e
	}
	defer f.Close()
	h := sha256.New()
	if _, e = io.Copy(h, f); e != nil {
		return "", e
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}
func manifest(path string, c Config) ([]string, error) {
	sum, e := fileSHA(path)
	if e != nil {
		return nil, e
	}
	if e = sameHash(sum, c.manifestHash, "manifest"); e != nil {
		return nil, e
	}
	f, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	defer f.Close()
	list := make([]string, c.sectors)
	seen := make(map[string]bool)
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 4096), 1<<20)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) != 2 || !hex64.MatchString(parts[0]) {
			return nil, fmt.Errorf("invalid manifest line %q", line)
		}
		name := strings.TrimPrefix(parts[1], "*")
		name = filepath.Base(name)
		found := false
		for k := 0; k < c.sectors; k++ {
			if name == fmt.Sprintf("sector-%d.rooms", 341+k) {
				if seen[name] {
					return nil, fmt.Errorf("duplicate manifest item %s", name)
				}
				seen[name] = true
				list[k] = parts[0]
				found = true
				break
			}
		}
		if !found {
			return nil, fmt.Errorf("unexpected manifest file %s", name)
		}
	}
	if e = sc.Err(); e != nil {
		return nil, e
	}
	for k, s := range list {
		if s == "" {
			return nil, fmt.Errorf("missing manifest sector %d", 341+k)
		}
	}
	return list, nil
}

// flipFirst mutates the first payload byte before both parser and Merkle hashing.
// This models a corrupted public payload without editing the on-disk store.
type flipFirst struct {
	reader io.Reader
	done   bool
}

func (f *flipFirst) Read(p []byte) (int, error) {
	n, e := f.reader.Read(p)
	if n > 0 && !f.done {
		p[0] ^= 2
		f.done = true
	}
	return n, e
}

type merkle struct {
	leaf          hash.Hash
	root          hash.Hash
	inLeaf, total int64
}

func newMerkle() *merkle { return &merkle{leaf: sha256.New(), root: sha256.New()} }
func (m *merkle) commit() {
	digest := m.leaf.Sum(nil)
	hexDigest := make([]byte, hex.EncodedLen(len(digest)))
	hex.Encode(hexDigest, digest)
	_, _ = m.root.Write(hexDigest)
	m.leaf.Reset()
	m.inLeaf = 0
}
func (m *merkle) Write(b []byte) (int, error) {
	n := len(b)
	for len(b) > 0 {
		take := int64(len(b))
		if take > leafSize-m.inLeaf {
			take = leafSize - m.inLeaf
		}
		_, _ = m.leaf.Write(b[:int(take)])
		b = b[int(take):]
		m.inLeaf += take
		m.total += take
		if m.inLeaf == leafSize {
			m.commit()
		}
	}
	return n, nil
}
func (m *merkle) final() string {
	if m.inLeaf > 0 {
		m.commit()
	}
	return hex.EncodeToString(m.root.Sum(nil))
}
func readHeader(stream io.Reader, c Config) error {
	buf := make([]byte, 4096)
	if _, e := io.ReadFull(stream, buf); e != nil {
		return e
	}
	ix := -1
	for i, b := range buf {
		if b == '\n' {
			ix = i
			break
		}
	}
	if ix < 0 {
		return errors.New("header line has no newline in its 4096 bytes")
	}
	for _, b := range buf[ix+1:] {
		if b != 0 {
			return errors.New("nonzero header padding")
		}
	}
	line := string(buf[:ix])
	if !strings.HasPrefix(line, "YMROOMHDR|") {
		return fmt.Errorf("wrong magic: %q", line[:min(len(line), 20)])
	}
	kv := make(map[string]string)
	for _, part := range strings.Split(line, "|") {
		p := strings.SplitN(part, "=", 2)
		if len(p) == 2 {
			if _, ok := kv[p[0]]; ok {
				return fmt.Errorf("duplicate header field %s", p[0])
			}
			kv[p[0]] = p[1]
		}
	}
	for key, want := range map[string]string{"n": strconv.FormatInt(c.n, 10), "payload_bytes": strconv.FormatInt(c.payload, 10), "payload_merkle": c.merkleHash} {
		if kv[key] != want {
			return fmt.Errorf("header %s got %q expected %q", key, kv[key], want)
		}
	}
	return nil
}

type vector struct {
	name  string
	bytes []byte
	file  *os.File
}

func openVector(path string, n int64, want, name string) (*vector, error) {
	f, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	closeErr := func(e error) (*vector, error) { f.Close(); return nil, e }
	st, e := f.Stat()
	if e != nil {
		return closeErr(e)
	}
	if st.Size() != 8*n {
		return closeErr(fmt.Errorf("%s bytes=%d, expected=%d", name, st.Size(), 8*n))
	}
	sum, e := fileSHA(path)
	if e != nil {
		return closeErr(e)
	}
	if e = sameHash(sum, want, name); e != nil {
		return closeErr(e)
	}
	if st.Size() > int64(int(^uint(0)>>1)) {
		return closeErr(errors.New("file too large to map on this architecture"))
	}
	data, e := syscall.Mmap(int(f.Fd()), 0, int(st.Size()), syscall.PROT_READ, syscall.MAP_SHARED)
	if e != nil {
		return closeErr(e)
	}
	return &vector{name: name, file: f, bytes: data}, nil
}
func (v *vector) at(h uint32) int64 { return int64(binary.LittleEndian.Uint64(v.bytes[int(h)*8:])) }
func (v *vector) close()            { _ = syscall.Munmap(v.bytes); _ = v.file.Close() }
func seeded(i uint32, seed uint64) (int64, int64) {
	// Independent deterministic integer test vectors: SplitMix64 (two draws per index).
	x := uint64(i) ^ seed
	next := func() uint64 {
		x += 0x9e3779b97f4a7c15
		z := x
		z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9
		z = (z ^ (z >> 27)) * 0x94d049bb133111eb
		return z ^ (z >> 31)
	}
	return int64(next()%7) - 3, int64(next()%7) - 3
}

type result struct {
	t   *big.Int
	row uint32
	mag uint16
}

func (a *result) consider(q *big.Int, h uint32, mag uint16) {
	if a.t == nil || q.Cmp(a.t) < 0 {
		a.t = new(big.Int).Set(q)
		a.row = h
		a.mag = mag
	}
}
func run(c Config) error {
	start := time.Now()
	wantSums, e := manifest(filepath.Join(c.dir, "SECTORS-341-374.sha256"), c)
	if e != nil {
		return e
	}
	v1, e := openVector(c.control, c.n, c.controlHash, "control")
	if e != nil {
		return e
	}
	defer v1.close()
	v2, e := openVector(c.blind, c.n, c.blindHash, "blind")
	if e != nil {
		return e
	}
	defer v2.close()
	files := make([]*os.File, 0, c.sectors)
	hashes := make([]hash.Hash, 0, c.sectors)
	readers := make([]io.Reader, 0, c.sectors)
	defer func() {
		for _, f := range files {
			_ = f.Close()
		}
	}()
	for k := 0; k < c.sectors; k++ {
		p := filepath.Join(c.dir, fmt.Sprintf("sector-%d.rooms", 341+k))
		f, err := os.Open(p)
		if err != nil {
			return err
		}
		files = append(files, f)
		h := sha256.New()
		hashes = append(hashes, h)
		readers = append(readers, io.TeeReader(f, h))
	}
	stream := bufio.NewReaderSize(io.MultiReader(readers...), 4<<20)
	if e = readHeader(stream, c); e != nil {
		return e
	}
	m := newMerkle()
	bounded := &io.LimitedReader{R: stream, N: c.payload}
	payloadSource := io.Reader(bounded)
	if c.fault == "payload" {
		payloadSource = &flipFirst{reader: payloadSource}
	}
	payload := bufio.NewReaderSize(io.TeeReader(payloadSource, m), 4<<20)
	const seed uint64 = 0x79D8C82AEA6808DE
	result1, result2 := result{}, result{}
	var flats int64
	var minMag uint16 = 65535
	var maxMag uint16
	allZero := true
	sumSym := new(big.Int)
	rowSym := new(big.Int)
	weight := new(big.Int)
	var deltaSum int64
	var head [8]byte
	var entry [8]byte
	var tmpZ, term, dz1, dz2, num1, num2, div1, div2, numerMag big.Int
	countNonflat := int64(0)
	for h := int64(0); h < c.n; h++ {
		if _, e = io.ReadFull(payload, head[:]); e != nil {
			return fmt.Errorf("row %d header: %w", h, e)
		}

		w := binary.LittleEndian.Uint32(head[:4])
		if w == 0 {
			return fmt.Errorf("row %d has zero multiplicity weight", h)
		}
		mag := binary.LittleEndian.Uint16(head[4:6])
		cnt := binary.LittleEndian.Uint16(head[6:8])
		if cnt == 0 {
			return fmt.Errorf("row %d has no entries", h)
		}
		if mag == 0 {
			flats++
		} else {
			countNonflat++
			if mag < minMag {
				minMag = mag
			}
			if mag > maxMag {
				maxMag = mag
			}
		}
		h32 := uint32(h)
		d1 := v1.at(h32)
		d2 := v2.at(h32)
		if c.fault == "d" && mag > 0 && countNonflat == 1 {
			d1 = 0
		}
		if mag == 0 {
			if d1 != 0 || d2 != 0 {
				return fmt.Errorf("flat row %d has nonzero d: %d / %d", h, d1, d2)
			}
		} else {
			if d1 <= 0 || d2 <= 0 {
				return fmt.Errorf("non-flat row %d has nonpositive d: %d / %d", h, d1, d2)
			}
		}
		xh, yh := seeded(h32, seed)
		dz1.SetInt64(0)
		dz2.SetInt64(0)
		deltaSum = 0
		var sumZ int64
		hasDiag := false
		for i := 0; i < int(cnt); i++ {
			if _, e = io.ReadFull(payload, entry[:]); e != nil {
				return fmt.Errorf("row %d entry %d: %w", h, i, e)
			}
			j := binary.LittleEndian.Uint32(entry[:4])
			z := int64(int32(binary.LittleEndian.Uint32(entry[4:8])))
			if int64(j) >= c.n {
				return fmt.Errorf("row %d invalid neighbor j=%d", h, j)
			}
			if j != h32 && z > 0 {
				return fmt.Errorf("row %d j=%d positive off-diagonal z=%d", h, j, z)
			}
			if j == h32 {
				hasDiag = true
			}
			sumZ += z
			tmpZ.SetInt64(z)
			term.SetInt64(v1.at(j))
			term.Mul(&term, &tmpZ)
			dz1.Add(&dz1, &term)
			term.SetInt64(v2.at(j))
			term.Mul(&term, &tmpZ)
			dz2.Add(&dz2, &term)
			xj, yj := seeded(j, seed)
			deltaSum += z * (xh*yj - yh*xj)
		}
		if !hasDiag {
			return fmt.Errorf("row %d missing diagonal", h)
		}
		if sumZ != 0 {
			allZero = false
			return fmt.Errorf("row %d has sum(z)=%d not zero", h, sumZ)
		}
		if deltaSum != 0 && w != 0 {
			rowSym.SetInt64(deltaSum)
			weight.SetUint64(uint64(w))
			rowSym.Mul(rowSym, weight)
			sumSym.Add(sumSym, rowSym)
		}
		if mag > 0 {
			// Exact floor((9,000,000 * mag * d[h] + 1,000,000 * sum(z*d[j])) / d[h]).
			numerMag.SetUint64(uint64(mag))
			numerMag.Mul(&numerMag, big.NewInt(9000000))
			num1.SetInt64(d1)
			num1.Mul(&num1, &numerMag)
			term.Mul(&dz1, big.NewInt(1000000))
			num1.Add(&num1, &term)
			div1.SetInt64(d1)
			num1.Div(&num1, &div1)
			result1.consider(&num1, h32, mag)
			num2.SetInt64(d2)
			num2.Mul(&num2, &numerMag)
			term.Mul(&dz2, big.NewInt(1000000))
			num2.Add(&num2, &term)
			div2.SetInt64(d2)
			num2.Div(&num2, &div2)
			result2.consider(&num2, h32, mag)
		}
	}
	// Check declared-payload zero padding and include it in the Merkle.
	var insidePadding, paddingNonzero int64
	var tail [1 << 20]byte
	for {
		got, err := payload.Read(tail[:])
		insidePadding += int64(got)
		for _, v := range tail[:got] {
			if v != 0 {
				paddingNonzero++
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("payload padding read: %w", err)
		}
	}
	if insidePadding != c.paddingBytes || paddingNonzero != 0 {
		return fmt.Errorf("payload padding mismatch: trailing=%d nonzero=%d expected=%d", insidePadding, paddingNonzero, c.paddingBytes)
	}
	if bounded.N != 0 {
		return fmt.Errorf("row stream shorter than declared payload by %d bytes", bounded.N)
	}
	if m.total != c.payload {
		return fmt.Errorf("payload bytes hashed %d, expected %d", m.total, c.payload)
	}
	if e = sameHash(m.final(), c.merkleHash, "payload merkle"); e != nil {
		return e
	}
	// Bytes after payload are authenticated by sector SHA-256, not Merkle.
	var rawTailBytes, rawTailNonzero int64
	var buf [1 << 20]byte
	for {
		n, err := stream.Read(buf[:])
		rawTailBytes += int64(n)
		for _, v := range buf[:n] {
			if v != 0 {
				rawTailNonzero++
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
	}
	if rawTailBytes != c.rawTailBytes || rawTailNonzero != c.rawTailNonzero {
		return fmt.Errorf("raw tail discrepancy: bytes=%d nonzero=%d expected_bytes=%d expected_nonzero=%d", rawTailBytes, rawTailNonzero, c.rawTailBytes, c.rawTailNonzero)
	}
	for k, h := range hashes {
		got := hex.EncodeToString(h.Sum(nil))
		if e = sameHash(got, wantSums[k], fmt.Sprintf("sector-%d", 341+k)); e != nil {
			return e
		}
	}
	if countNonflat == 0 {
		return errors.New("no non-flat rows")
	}
	if sumSym.Sign() != 0 {
		return fmt.Errorf("weighted self-adjoint integer residual=%s", sumSym.String())
	}
	if !allZero {
		return errors.New("row sums not all zero")
	}
	if result1.t == nil || result2.t == nil {
		return errors.New("missing Perron minimum")
	}
	if c.fault != "" {
		return errors.New("fault control unexpectedly reached certificate output")
	}
	fmt.Printf("PASS merkle=PASS sector_hashes=PASS vector_hashes=PASS row_sums_zero=PASS W_self_adjoint=PASS\n")
	fmt.Printf("control t_cert_milli=%s min_row=%d min_mag=%d\n", result1.t.String(), result1.row, result1.mag)
	fmt.Printf("blind t_cert_milli=%s min_row=%d min_mag=%d\n", result2.t.String(), result2.row, result2.mag)
	fmt.Printf("flat_rows=%d min_nonzero_mag=%d max_mag=%d weighted_residual=%s\n", flats, minMag, maxMag, sumSym.String())
	fmt.Printf("payload_zero_padding=%d raw_tail_bytes=%d raw_tail_nonzero=%d\n", insidePadding, rawTailBytes, rawTailNonzero)
	fmt.Printf("seconds=%d\n", int64(time.Since(start)/time.Second))
	return nil
}
func main() {
	var c Config
	flag.StringVar(&c.dir, "dir", ".", "directory containing sector rooms and manifest")
	flag.StringVar(&c.control, "control", "d93000000.bin", "control i64 vector")
	flag.StringVar(&c.blind, "blind", "d93700000-pass5.bin", "blind i64 vector")
	flag.StringVar(&c.fault, "fault", "", "negative control: payload or d")
	var fixture bool
	flag.BoolVar(&fixture, "fixture", false, "use deliberately small synthetic fixture dimensions and hashes supplied by flags")
	flag.Int64Var(&c.n, "n", expectedN, "row count (fixture only)")
	flag.Int64Var(&c.payload, "payload-bytes", expectedPayload, "payload bytes (fixture only)")
	flag.StringVar(&c.manifestHash, "manifest-sha", expectedManifest, "manifest SHA256 (fixture only)")
	flag.StringVar(&c.merkleHash, "merkle-sha", expectedMerkle, "payload Merkle SHA256 (fixture only)")
	flag.StringVar(&c.controlHash, "control-sha", controlHash, "control vector SHA256 (fixture only)")
	flag.StringVar(&c.blindHash, "blind-sha", blindHash, "blind vector SHA256 (fixture only)")
	flag.IntVar(&c.sectors, "sectors", 34, "number of sector files (fixture only)")
	flag.Int64Var(&c.paddingBytes, "expected-padding", expectedZeroPadding, "zero bytes inside payload (fixture only)")
	flag.Int64Var(&c.rawTailBytes, "expected-raw-tail", expectedRawTailBytes, "bytes after payload (fixture only)")
	flag.Int64Var(&c.rawTailNonzero, "expected-raw-tail-nonzero", expectedRawTailNonzero, "nonzero bytes after payload (fixture only)")
	flag.Parse()
	if c.fault != "" && c.fault != "payload" && c.fault != "d" {
		die(errors.New("unknown fault mode"))
	}
	if !fixture {
		if c.n != expectedN || c.payload != expectedPayload || c.manifestHash != expectedManifest || c.merkleHash != expectedMerkle || c.controlHash != controlHash || (c.blindHash != blindHash && c.blindHash != blind2Hash && c.blindHash != blind3Hash) || c.sectors != 34 || c.paddingBytes != expectedZeroPadding || c.rawTailBytes != expectedRawTailBytes || c.rawTailNonzero != expectedRawTailNonzero {
			die(errors.New("production constants cannot be overridden; --fixture required"))
		}
	}
	if c.n <= 0 || c.n > int64(^uint32(0)) || c.payload <= 0 || c.sectors < 1 || c.sectors > 34 || c.paddingBytes < 0 || c.rawTailBytes < 0 || c.rawTailNonzero < 0 || c.rawTailNonzero > c.rawTailBytes {
		die(errors.New("invalid dimensions"))
	}
	if err := run(c); err != nil {
		die(err)
	}
}
