package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"flag"
	"fmt"
	"math/big"
	"os"
	"strconv"
	"strings"
)

// refCheck is a deliberately simple, slow reference: the whole store is held
// in memory and every arithmetic step uses math/big, so it shares no integer
// code with ymcheck. Output format matches ymcheck minus secs, plus
// max_num_bits (bit length of the largest |numerator|).
func refCheck(args []string) {
	fs := flag.NewFlagSet("ref", flag.ExitOnError)
	store := fs.String("store", "", "store file")
	seed := fs.Uint64("seed", 20261102, "symmetry seed")
	fs.Parse(args)
	bad := func(format string, a ...any) {
		fmt.Printf("FAIL|reason="+format+"|json=0\n", a...)
		os.Exit(2)
	}
	raw, err := os.ReadFile(*store)
	if err != nil || len(raw) < headerBytes {
		bad("short_stream")
	}
	nl := bytes.IndexByte(raw[:headerBytes], '\n')
	if nl < 0 || !bytes.HasPrefix(raw, []byte("YMROOMHDR|")) {
		bad("header")
	}
	vals := map[string][]string{}
	for _, f := range strings.Split(strings.TrimRight(string(raw[:nl]), " "), "|") {
		if k, v, ok := strings.Cut(f, "="); ok {
			vals[k] = append(vals[k], v)
		}
	}
	if len(vals["n"]) != 1 || len(vals["payload_bytes"]) != 1 || len(vals["payload_merkle"]) != 1 {
		bad("header_fields")
	}
	n, err1 := strconv.ParseInt(vals["n"][0], 10, 64)
	pb, err2 := strconv.ParseInt(vals["payload_bytes"][0], 10, 64)
	if err1 != nil || err2 != nil || n < 1 || pb < 8*n {
		bad("header_values")
	}
	if int64(len(raw)) < headerBytes+pb {
		bad("short_stream")
	}
	payload := raw[headerBytes : headerBytes+pb]
	for _, c := range raw[headerBytes+pb:] {
		if c != 0 {
			bad("nonzero_padding")
		}
	}
	if merkleHex(payload) != vals["payload_merkle"][0] {
		bad("merkle_mismatch")
	}
	type dv struct {
		path, sha string
		d         []*big.Int
	}
	var ds []dv
	for _, path := range fs.Args() {
		b, err := os.ReadFile(path)
		if err != nil || int64(len(b)) != 8*n {
			bad("d_length")
		}
		sum := sha256.Sum256(b)
		x := dv{path: path, sha: hex.EncodeToString(sum[:])}
		for i := int64(0); i < n; i++ {
			x.d = append(x.d, big.NewInt(int64(binary.LittleEndian.Uint64(b[8*i:]))))
		}
		ds = append(ds, x)
	}
	type best struct {
		q           *big.Int
		h, mag, cnt int64
	}
	bests := make([]*best, len(ds))
	zero := big.NewInt(0)
	cMag := big.NewInt(1000 * JB)
	cZ := big.NewInt(1000 * JE)
	lhs, rhs := new(big.Int), new(big.Int)
	var flat, nonflat, entries, diagNotOnce int64
	minNZ, maxMag := int64(1<<16), int64(0)
	minW, maxW := int64(1<<32), int64(-1)
	maxBits := 0
	pos := int64(0)
	xy := func(j int64) (*big.Int, *big.Int) {
		x, y := xyRef(*seed, uint64(j))
		return big.NewInt(x), big.NewInt(y)
	}
	for h := int64(0); h < n; h++ {
		if pos+8 > pb {
			bad("payload_ends_inside_row")
		}
		w := int64(binary.LittleEndian.Uint32(payload[pos:]))
		mag := int64(binary.LittleEndian.Uint16(payload[pos+4:]))
		cnt := int64(binary.LittleEndian.Uint16(payload[pos+6:]))
		pos += 8
		if pos+8*cnt > pb {
			bad("payload_ends_inside_row")
		}
		js := make([]int64, cnt)
		zs := make([]*big.Int, cnt)
		rowSum, zx, zy := new(big.Int), new(big.Int), new(big.Int)
		diag := 0
		for e := int64(0); e < cnt; e++ {
			js[e] = int64(binary.LittleEndian.Uint32(payload[pos:]))
			zs[e] = big.NewInt(int64(int32(binary.LittleEndian.Uint32(payload[pos+4:]))))
			pos += 8
			if js[e] >= n {
				bad("column_out_of_range")
			}
			if js[e] == h {
				diag++
			} else if zs[e].Cmp(zero) > 0 {
				bad("positive_offdiagonal")
			}
			rowSum.Add(rowSum, zs[e])
			x, y := xy(js[e])
			zx.Add(zx, new(big.Int).Mul(zs[e], x))
			zy.Add(zy, new(big.Int).Mul(zs[e], y))
		}
		if rowSum.Sign() != 0 {
			bad("row_sum_nonzero")
		}
		if diag != 1 {
			diagNotOnce++
		}
		xh, yh := xy(h)
		W := big.NewInt(w)
		lhs.Add(lhs, new(big.Int).Mul(new(big.Int).Mul(W, xh), zy))
		rhs.Add(rhs, new(big.Int).Mul(new(big.Int).Mul(W, yh), zx))
		entries += cnt
		minW, maxW = min(minW, w), max(maxW, w)
		if mag == 0 {
			flat++
		} else {
			nonflat++
			minNZ, maxMag = min(minNZ, mag), max(maxMag, mag)
		}
		for k := range ds {
			dh := ds[k].d[h]
			if mag == 0 {
				if dh.Sign() != 0 {
					bad("flat_row_d_nonzero")
				}
				continue
			}
			if dh.Sign() <= 0 {
				bad("nonflat_row_d_nonpositive")
			}
			s := new(big.Int)
			for e := range js {
				s.Add(s, new(big.Int).Mul(zs[e], ds[k].d[js[e]]))
			}
			num := new(big.Int).Mul(new(big.Int).Mul(cMag, big.NewInt(mag)), dh)
			num.Add(num, new(big.Int).Mul(cZ, s))
			maxBits = max(maxBits, new(big.Int).Abs(num).BitLen())
			// Floor by definition: the q with q*d <= num < (q+1)*d.
			q := new(big.Int).Quo(num, dh)
			if new(big.Int).Mul(q, dh).Cmp(num) > 0 {
				q.Sub(q, big.NewInt(1))
			}
			b := bests[k]
			switch {
			case b == nil || q.Cmp(b.q) < 0:
				bests[k] = &best{q, h, mag, 1}
			case q.Cmp(b.q) == 0:
				b.cnt++
			}
		}
	}
	if pos != pb {
		bad("payload_has_bytes_after_row_n")
	}
	if lhs.Cmp(rhs) != 0 {
		bad("w_symmetry_mismatch")
	}
	if nonflat == 0 {
		bad("no_nonflat_rows")
	}
	for k, x := range ds {
		b := bests[k]
		fmt.Printf("CERT|d=%s|d_sha256=%s|t_cert=%s|row=%d|mag=%d|rows_at_min=%d|json=0\n", x.path, x.sha, b.q, b.h, b.mag, b.cnt)
	}
	fmt.Printf("STORE|n=%d|payload_bytes=%d|merkle=PASS|flat_rows=%d|min_nonzero_mag=%d|max_mag=%d|"+
		"row_sums_zero=PASS|w_symmetry=PASS|seed=%d|entries=%d|nonflat_rows=%d|diag_not_once_rows=%d|"+
		"min_w=%d|max_w=%d|padding_bytes=%d|payload_merkle=%s|w_symmetry_lhs=%s|max_num_bits=%d|json=0\n",
		n, pb, flat, minNZ, maxMag, *seed, entries, nonflat, diagNotOnce, minW, maxW,
		int64(len(raw))-headerBytes-pb, vals["payload_merkle"][0], lhs, maxBits)
}

// xyRef is the same SplitMix64 vector definition as ymcheck's xyAt.
func xyRef(seed, j uint64) (int64, int64) {
	z := seed + (j+1)*0x9E3779B97F4A7C15
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	z ^= z >> 31
	return int64(int32(uint32(z>>32))) >> 1, int64(int32(uint32(z))) >> 1
}

// ---------------------------------------------------------------------------
// Exact smallest eigenvalue of H' = (JB/JE)*M + Z on the non-flat rows.
//
// H' is W-self-adjoint, so A(t) = W*(1e6*H' - t*I) is symmetric and congruent
// to a symmetric matrix similar to 1e6*H' - t*I. By Sylvester's law of inertia
// A(t) is positive semidefinite iff 1e6*lambda_min(H') >= t. PSD is decided
// exactly by "all principal minors >= 0" (fraction-free Bareiss determinants).
// Bisection over integers t gives t_floor = floor(1e6*lambda_min).

func eigen(args []string) {
	fs := flag.NewFlagSet("eigen", flag.ExitOnError)
	store := fs.String("store", "", "store")
	fs.Parse(args)
	p := parseStoreFile(*store)
	var idx []int
	pos := map[int]int{}
	for h, r := range p.rows {
		if r.mag != 0 {
			pos[h] = len(idx)
			idx = append(idx, h)
		}
	}
	k := len(idx)
	if k == 0 || k > 12 {
		die("eigen needs 1..12 non-flat rows, have %d", k)
	}
	H := make([][]*big.Int, k)
	for a := range H {
		H[a] = make([]*big.Int, k)
		for b := range H[a] {
			H[a][b] = new(big.Int)
		}
	}
	for a, h := range idx {
		r := p.rows[h]
		H[a][a].Add(H[a][a], big.NewInt(int64(JB/JE)*int64(r.mag)))
		for _, e := range r.ents {
			if b, ok := pos[int(e.j)]; ok {
				H[a][b].Add(H[a][b], big.NewInt(int64(e.z)))
			}
		}
	}
	million := big.NewInt(1000000)
	A0 := make([][]*big.Int, k) // 1e6 * W * H'
	for a := range A0 {
		A0[a] = make([]*big.Int, k)
		w := big.NewInt(int64(p.rows[idx[a]].w))
		for b := range A0[a] {
			A0[a][b] = new(big.Int).Mul(new(big.Int).Mul(million, w), H[a][b])
		}
	}
	for a := range A0 {
		for b := range A0 {
			if A0[a][b].Cmp(A0[b][a]) != 0 {
				die("W*H' is not symmetric at %d,%d", a, b)
			}
		}
	}
	psd := func(t *big.Int) bool {
		M := make([][]*big.Int, k)
		for a := range M {
			M[a] = make([]*big.Int, k)
			for b := range M[a] {
				M[a][b] = new(big.Int).Set(A0[a][b])
			}
			M[a][a].Sub(M[a][a], new(big.Int).Mul(t, big.NewInt(int64(p.rows[idx[a]].w))))
		}
		for mask := 1; mask < 1<<k; mask++ {
			var sub []int
			for a := 0; a < k; a++ {
				if mask>>a&1 == 1 {
					sub = append(sub, a)
				}
			}
			S := make([][]*big.Int, len(sub))
			for i, a := range sub {
				S[i] = make([]*big.Int, len(sub))
				for j, b := range sub {
					S[i][j] = new(big.Int).Set(M[a][b])
				}
			}
			if bareissDet(S).Sign() < 0 {
				return false
			}
		}
		return true
	}
	// Gershgorin lower bound and min-diagonal upper bound for lambda_min.
	var lo, hi *big.Int
	for a := 0; a < k; a++ {
		g := new(big.Int).Set(H[a][a])
		for b := 0; b < k; b++ {
			if b != a {
				g.Sub(g, new(big.Int).Abs(H[a][b]))
			}
		}
		g.Mul(g, million)
		g.Sub(g, big.NewInt(1))
		d := new(big.Int).Mul(H[a][a], million)
		d.Add(d, big.NewInt(1))
		if lo == nil || g.Cmp(lo) < 0 {
			lo = g
		}
		if hi == nil || d.Cmp(hi) < 0 {
			hi = d
		}
	}
	if !psd(lo) || psd(hi) {
		die("bracket failed")
	}
	one := big.NewInt(1)
	for new(big.Int).Sub(hi, lo).Cmp(one) > 0 {
		mid := new(big.Int).Add(lo, hi)
		mid.Rsh(mid, 1)
		if psd(mid) {
			lo = mid
		} else {
			hi = mid
		}
	}
	fmt.Printf("EIGEN|nonflat=%d|t_floor=%s|psd_at_t_floor=%v|psd_at_t_floor_plus_1=%v|json=0\n",
		k, lo, psd(lo), psd(new(big.Int).Add(lo, one)))
}

func bareissDet(m [][]*big.Int) *big.Int {
	k := len(m)
	if k == 0 {
		return big.NewInt(1)
	}
	sign := 1
	prev := big.NewInt(1)
	for i := 0; i < k-1; i++ {
		if m[i][i].Sign() == 0 {
			r := i + 1
			for r < k && m[r][i].Sign() == 0 {
				r++
			}
			if r == k {
				return big.NewInt(0)
			}
			m[i], m[r] = m[r], m[i]
			sign = -sign
		}
		for r := i + 1; r < k; r++ {
			for c := i + 1; c < k; c++ {
				v := new(big.Int).Mul(m[r][c], m[i][i])
				v.Sub(v, new(big.Int).Mul(m[r][i], m[i][c]))
				m[r][c] = v.Quo(v, prev)
			}
		}
		prev = m[i][i]
	}
	d := new(big.Int).Set(m[k-1][k-1])
	if sign < 0 {
		d.Neg(d)
	}
	return d
}
