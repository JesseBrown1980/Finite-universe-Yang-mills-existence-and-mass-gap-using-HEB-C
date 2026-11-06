package main

import (
	"bytes"
	"encoding/binary"
	"math/big"
	"math/rand/v2"
	"testing"
)

var (
	two64  = new(big.Int).Lsh(big.NewInt(1), 64)
	two127 = new(big.Int).Lsh(big.NewInt(1), 127)
	two128 = new(big.Int).Lsh(big.NewInt(1), 128)
)

func fromBig(b *big.Int) i128 {
	v := new(big.Int).Set(b)
	if v.Sign() < 0 {
		v.Add(v, two128)
	}
	lo := new(big.Int).And(v, new(big.Int).Sub(two64, big.NewInt(1))).Uint64()
	hi := new(big.Int).Rsh(v, 64).Uint64()
	return i128{hi, lo}
}

func edge64() []int64 {
	return []int64{0, 1, -1, 2, -2, 1 << 31, -(1 << 31), 1<<31 - 1, 1 << 62, -(1 << 62),
		9223372036854775807, -9223372036854775808, 3, 1000000, -9000000}
}

func rand64(r *rand.Rand) int64 {
	switch r.IntN(4) {
	case 0:
		return int64(r.Uint64())
	case 1:
		return int64(r.Uint64()) >> r.IntN(64)
	case 2:
		return edge64()[r.IntN(len(edge64()))]
	default:
		return int64(r.IntN(2001)) - 1000
	}
}

func randI128(r *rand.Rand) i128 {
	switch r.IntN(3) {
	case 0:
		return i128{r.Uint64(), r.Uint64()}
	case 1:
		return i128From64(rand64(r))
	default:
		v := randBig(r, 127)
		v.Rsh(v, uint(r.IntN(127)))
		if r.IntN(2) == 0 {
			v.Neg(v)
		}
		return fromBig(v)
	}
}

// randBig returns a uniform integer in [0, 2^bitsN) for bitsN <= 128.
func randBig(r *rand.Rand, bitsN uint) *big.Int {
	v := new(big.Int).SetUint64(r.Uint64())
	v.Lsh(v, 64)
	v.Or(v, new(big.Int).SetUint64(r.Uint64()))
	return v.Rsh(v, 128-bitsN)
}

func TestRoundTrip(t *testing.T) {
	r := rand.New(rand.NewPCG(1, 2))
	for i := 0; i < 20000; i++ {
		a := randI128(r)
		if fromBig(a.big()) != a {
			t.Fatalf("round trip %v", a)
		}
	}
}

func TestMul64x64(t *testing.T) {
	r := rand.New(rand.NewPCG(3, 4))
	for i := 0; i < 200000; i++ {
		a, b := rand64(r), rand64(r)
		want := new(big.Int).Mul(big.NewInt(a), big.NewInt(b))
		if got := mul64x64(a, b).big(); got.Cmp(want) != 0 {
			t.Fatalf("%d*%d got %s want %s", a, b, got, want)
		}
	}
}

func TestAddChecked(t *testing.T) {
	r := rand.New(rand.NewPCG(5, 6))
	lo := new(big.Int).Neg(two127)
	for i := 0; i < 200000; i++ {
		a, b := randI128(r), randI128(r)
		want := new(big.Int).Add(a.big(), b.big())
		inRange := want.Cmp(lo) >= 0 && want.Cmp(two127) < 0
		got, ok := addChecked(a, b)
		if ok != inRange || (ok && got.big().Cmp(want) != 0) {
			t.Fatalf("add %s+%s ok=%v want %s", a.big(), b.big(), ok, want)
		}
		if w := add128(a, b); inRange && w.big().Cmp(want) != 0 {
			t.Fatalf("add128")
		}
	}
}

func TestAddInt64(t *testing.T) {
	r := rand.New(rand.NewPCG(7, 8))
	for i := 0; i < 200000; i++ {
		v := randBig(r, 100)
		if r.IntN(2) == 0 {
			v.Neg(v)
		}
		a := fromBig(v)
		x := rand64(r)
		want := new(big.Int).Add(v, big.NewInt(x))
		if got := addInt64(a, x).big(); got.Cmp(want) != 0 {
			t.Fatalf("addInt64")
		}
	}
}

func TestMulSmallChecked(t *testing.T) {
	r := rand.New(rand.NewPCG(9, 10))
	cs := []uint64{1, 2, 3, 1000000, 9000000, 1 << 32, ^uint64(0)}
	for i := 0; i < 200000; i++ {
		a := randI128(r)
		c := cs[r.IntN(len(cs))]
		want := new(big.Int).Mul(a.big(), new(big.Int).SetUint64(c))
		abs := new(big.Int).Abs(want)
		got, ok := mulSmallChecked(a, c)
		if ok != (abs.Cmp(two127) < 0) || (ok && got.big().Cmp(want) != 0) {
			t.Fatalf("mul %s*%d ok=%v want %s", a.big(), c, ok, want)
		}
	}
}

func TestFloorDivPos(t *testing.T) {
	fixed := []struct{ n, d, q int64 }{
		{-20000000, 3, -6666667}, {-7, 2, -4}, {7, 2, 3}, {-6, 3, -2}, {6, 3, 2},
		{-1, 1000000007, -1}, {0, 5, 0}, {-9223372036854775808, 1, -9223372036854775808},
	}
	for _, f := range fixed {
		if got := floorDivPos(i128From64(f.n), f.d).big(); got.Cmp(big.NewInt(f.q)) != 0 {
			t.Fatalf("floor(%d/%d) got %s want %d", f.n, f.d, got, f.q)
		}
	}
	r := rand.New(rand.NewPCG(11, 12))
	for i := 0; i < 200000; i++ {
		n := randI128(r)
		d := rand64(r)
		if d < 0 {
			d = -(d + 1)
		}
		if d == 0 {
			d = 1
		}
		want := new(big.Int).Div(n.big(), big.NewInt(d)) // Euclidean == floor for d > 0
		if got := floorDivPos(n, d).big(); got.Cmp(want) != 0 {
			t.Fatalf("floor(%s/%d) got %s want %s", n.big(), d, got, want)
		}
	}
	// Exhaustive small range: compare with an independent definition of floor.
	for n := int64(-300); n <= 300; n++ {
		for d := int64(1); d <= 40; d++ {
			q := floorDivPos(i128From64(n), d).big().Int64()
			if !(q*d <= n && n < (q+1)*d) {
				t.Fatalf("floor(%d/%d)=%d", n, d, q)
			}
		}
	}
}

func TestCmp128(t *testing.T) {
	r := rand.New(rand.NewPCG(13, 14))
	for i := 0; i < 200000; i++ {
		a, b := randI128(r), randI128(r)
		if r.IntN(10) == 0 {
			b = a
		}
		if got, want := cmp128(a, b), a.big().Cmp(b.big()); got != want {
			t.Fatalf("cmp")
		}
	}
}

func TestMul64x128AndI256(t *testing.T) {
	r := rand.New(rand.NewPCG(15, 16))
	var acc i256
	sum := new(big.Int)
	for i := 0; i < 200000; i++ {
		a := rand64(r)
		b := randI128(r)
		want := new(big.Int).Mul(big.NewInt(a), b.big())
		p := mul64x128(a, b)
		if p.big().Cmp(want) != 0 {
			t.Fatalf("mul64x128 %d*%s", a, b.big())
		}
		acc.add(p)
		sum.Add(sum, want)
		if i%1000 == 0 && acc.big().Cmp(sum) != 0 {
			t.Fatalf("i256 accumulate")
		}
	}
	if acc.big().Cmp(sum) != 0 {
		t.Fatalf("i256 accumulate final")
	}
}

func TestXYRange(t *testing.T) {
	lo, hi := int64(0), int64(0)
	for j := uint64(0); j < 1<<20; j++ {
		x, y := xyAt(20261102, j)
		lo, hi = min(lo, x, y), max(hi, x, y)
		if x < -(1<<30) || x >= 1<<30 || y < -(1<<30) || y >= 1<<30 {
			t.Fatalf("range")
		}
	}
	if lo > -(1<<29) || hi < 1<<29 {
		t.Fatalf("x,y do not spread: %d %d", lo, hi)
	}
}

// TestSplitChunking feeds a random valid payload to the splitter in random
// chunk sizes (including 1..7 bytes, which split row headers) and checks that
// the batches reproduce every row, in order, with the right row index. In
// some trials the rows are followed by a zero tail inside the payload, and the
// recorded end of the rows must be the end of row n-1.
func TestSplitChunking(t *testing.T) {
	r := rand.New(rand.NewPCG(17, 18))
	for trial := 0; trial < 300; trial++ {
		n := 1 + r.IntN(200)
		var payload bytes.Buffer
		var rows [][]byte
		for h := 0; h < n; h++ {
			cnt := r.IntN(40)
			if r.IntN(50) == 0 {
				cnt = 3000 + r.IntN(2000)
			}
			row := make([]byte, 8+8*cnt)
			binary.LittleEndian.PutUint32(row, uint32(h*7+1))
			binary.LittleEndian.PutUint16(row[4:], uint16(r.IntN(5)))
			binary.LittleEndian.PutUint16(row[6:], uint16(cnt))
			for e := 0; e < cnt; e++ {
				binary.LittleEndian.PutUint32(row[8+8*e:], uint32(r.IntN(n)))
				binary.LittleEndian.PutUint32(row[12+8*e:], r.Uint32())
			}
			rows = append(rows, row)
			payload.Write(row)
		}
		rowsEnd := uint64(payload.Len())
		if trial%3 != 0 {
			payload.Write(make([]byte, []int{1, 7, 8, 9, 1000, 70000}[r.IntN(6)]))
		}
		data := payload.Bytes()
		chunks := make(chan []byte, 16)
		maxChunk := []int{1, 7, 8, 9, 64, 1000, 100000}[r.IntN(7)]
		var sizes []int
		for p := 0; p < len(data); {
			k := min(len(data)-p, 1+r.IntN(maxChunk))
			sizes = append(sizes, k)
			p += k
		}
		go func() {
			p := 0
			for _, k := range sizes {
				chunks <- append([]byte(nil), data[p:p+k]...)
				p += k
			}
			close(chunks)
		}()
		jobs := make(chan batch, 1<<16)
		c := &checker{n: uint64(n), payloadBytes: uint64(len(data))}
		c.split(chunks, jobs)
		var next uint64
		for b := range jobs {
			if b.h0 != next {
				t.Fatalf("trial %d: batch h0=%d want %d", trial, b.h0, next)
			}
			p := 0
			for i := 0; i < b.rows; i++ {
				want := rows[b.h0+uint64(i)]
				if !bytes.Equal(b.data[p:p+len(want)], want) {
					t.Fatalf("trial %d: row %d differs", trial, b.h0+uint64(i))
				}
				p += len(want)
			}
			if p != len(b.data) {
				t.Fatalf("trial %d: batch length", trial)
			}
			next += uint64(b.rows)
		}
		if next != uint64(n) {
			t.Fatalf("trial %d: rows %d want %d", trial, next, n)
		}
		if !c.rowsEnded || c.rowsEnd != rowsEnd {
			t.Fatalf("trial %d: rows end %d (recorded=%v) want %d", trial, c.rowsEnd, c.rowsEnded, rowsEnd)
		}
	}
}
