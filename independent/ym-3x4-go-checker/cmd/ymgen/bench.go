package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"flag"
	"fmt"
	"os"
)

// bench streams a large valid store to stdout without touching disk: pass 1
// computes payload_bytes and the merkle, pass 2 writes header, rows, padding.
// Each row has k off-diagonal partners with z=-1 (w=1), diagonal z=k, so W*Z
// is symmetric and rows sum to 0. mode=random pairs rows through k random
// involutions (partner = P^-1(P(h) xor 1), P a 4-round Feistel permutation),
// the worst case for memory locality; mode=local uses h+-1..h+-k/2 mod n.
func bench(args []string) {
	fs := flag.NewFlagSet("bench", flag.ExitOnError)
	logn := fs.Int("logn", 22, "n = 2^logn rows (even)")
	k := fs.Int("k", 72, "off-diagonal entries per row (even for local)")
	mode := fs.String("mode", "random", "random|local")
	seed := fs.Uint64("seed", 99, "seed")
	d1 := fs.String("d1", "", "write a random positive d file here")
	d2 := fs.String("d2", "", "write a second random positive d file here")
	inmem := fs.Bool("inmem", false, "keep the payload in RAM after pass 1 and stream it from there")
	fs.Parse(args)
	if *logn%2 != 0 || *logn < 8 || *logn > 30 {
		die("logn must be even in 8..30")
	}
	n := 1 << *logn
	half := uint(*logn / 2)
	mask := uint64(1)<<half - 1
	r := &rng{*seed}
	keys := make([][4]uint64, *k)
	for i := range keys {
		for j := range keys[i] {
			keys[i][j] = r.next()
		}
	}
	f := func(x, key uint64) uint64 {
		z := x ^ key
		z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
		z = (z ^ (z >> 27)) * 0x94D049BB133111EB
		return (z ^ (z >> 31)) & mask
	}
	partner := func(i, h int) int {
		if *mode == "local" {
			off := i/2 + 1
			if i%2 == 0 {
				return (h + off) % n
			}
			return (h - off + n) % n
		}
		kk := keys[i]
		L, R := uint64(h)>>half, uint64(h)&mask
		for t := 0; t < 4; t++ {
			L, R = R, L^f(R, kk[t])
		}
		y := (L<<half | R) ^ 1
		L, R = y>>half, y&mask
		for t := 3; t >= 0; t-- {
			L, R = R^f(L, kk[t]), L
		}
		return int(L<<half | R)
	}
	magOf := func(h int) uint16 {
		if h%97 == 0 {
			return 0
		}
		return uint16(1 + h%3)
	}
	buf := make([]byte, 8+8*(*k+1))
	rowBytes := func(h int) []byte {
		binary.LittleEndian.PutUint32(buf[0:], 1)
		binary.LittleEndian.PutUint16(buf[4:], magOf(h))
		binary.LittleEndian.PutUint16(buf[6:], uint16(*k+1))
		binary.LittleEndian.PutUint32(buf[8:], uint32(h))
		binary.LittleEndian.PutUint32(buf[12:], uint32(int32(*k)))
		for i := 0; i < *k; i++ {
			binary.LittleEndian.PutUint32(buf[16+8*i:], uint32(partner(i, h)))
			binary.LittleEndian.PutUint32(buf[20+8*i:], uint32(0xFFFFFFFF))
		}
		return buf
	}
	// Pass 1: merkle.
	h := sha256.New()
	fill := 0
	var text []byte
	var pb int64
	var payload []byte
	if *inmem {
		payload = make([]byte, 0, n*len(buf))
	}
	for row := 0; row < n; row++ {
		b := rowBytes(row)
		pb += int64(len(b))
		if *inmem {
			payload = append(payload, b...)
		}
		for len(b) > 0 {
			take := min(len(b), leafBytes-fill)
			h.Write(b[:take])
			fill += take
			b = b[take:]
			if fill == leafBytes {
				text = hex.AppendEncode(text, h.Sum(nil))
				h.Reset()
				fill = 0
			}
		}
	}
	if fill > 0 {
		text = hex.AppendEncode(text, h.Sum(nil))
	}
	sum := sha256.Sum256(text)
	mk := hex.EncodeToString(sum[:])
	for i, path := range []string{*d1, *d2} {
		if path == "" {
			continue
		}
		dr := &rng{*seed + uint64(i) + 1}
		d := make([]int64, n)
		for row := range d {
			if magOf(row) != 0 {
				d[row] = 1 + int64(dr.next()%(1<<40))
			}
		}
		writeD(path, d)
	}
	fmt.Fprintf(os.Stderr, "bench: n=%d payload_bytes=%d merkle=%s\n", n, pb, mk)
	// Pass 2: stream.
	w := bufio.NewWriterSize(os.Stdout, 4<<20)
	hdr := make([]byte, headerBytes)
	copy(hdr, fmt.Sprintf("YMROOMHDR|format=bench-%s|n=%d|payload_bytes=%d|payload_merkle=%s|\n", *mode, n, pb, mk))
	w.Write(hdr)
	if *inmem {
		for p := 0; p < len(payload); p += 4 << 20 {
			w.Write(payload[p:min(p+4<<20, len(payload))])
		}
	} else {
		for row := 0; row < n; row++ {
			w.Write(rowBytes(row))
		}
	}
	w.Write(make([]byte, 4096))
	if err := w.Flush(); err != nil {
		die("write: %v", err)
	}
}
