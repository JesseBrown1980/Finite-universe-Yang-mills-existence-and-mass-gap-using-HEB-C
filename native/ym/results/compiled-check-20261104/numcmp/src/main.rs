//! Every operation of the vendored num crates that the `std` feature changes, over an exact input set, from one source built both ways:
//! `cargo +1.81.0 build --release --locked` (std off) and the same with `--features with_std_paths` (std on, the crates' default).
//! By reading the vendored source those operations are BigUint to_str_radix, from_str_radix and their callers (Display, FromStr, parse_bytes,
//! to_radix_be, from_radix_be), BigUint sqrt, cbrt and nth_root, and the same three roots on the primitive integers.
//! Integer only. Each result is also checked in integers, r^k <= n < (r + 1)^k and parse(print(n)) = n. json=0.
//! usage: numcmp digest        one row per input class, with the SHA-256 of the bytes that class produced
//!        numcmp dump          those bytes, for a byte-for-byte compare of two builds
//!        numcmp mxcsr         the SSE sticky flags around each operation (x86_64); bit 0x20 is set by a rounding float operation
#![allow(deprecated)]

use num_bigint::{BigInt, BigUint, Sign};
use num_integer::Roots;
use num_traits::{Num, One, Zero};
use std::io::Write;
use std::str::FromStr;

const K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
    0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

#[derive(Clone)]
struct Sha {
    h: [u32; 8],
    buf: Vec<u8>,
    len: u64,
}

impl Sha {
    fn new() -> Sha {
        Sha { h: [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19], buf: Vec::with_capacity(64), len: 0 }
    }
    fn block(h: &mut [u32; 8], b: &[u8]) {
        let mut w = [0u32; 64];
        for (i, c) in b.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([c[0], c[1], c[2], c[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut v = *h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let mj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(mj);
            v = [t1.wrapping_add(t2), v[0], v[1], v[2], v[3].wrapping_add(t1), v[4], v[5], v[6]];
        }
        for (a, b) in h.iter_mut().zip(v.iter()) {
            *a = a.wrapping_add(*b);
        }
    }
    fn update(&mut self, mut d: &[u8]) {
        self.len += d.len() as u64;
        if !self.buf.is_empty() {
            let take = (64 - self.buf.len()).min(d.len());
            self.buf.extend_from_slice(&d[..take]);
            d = &d[take..];
            if self.buf.len() == 64 {
                let b = std::mem::take(&mut self.buf);
                Sha::block(&mut self.h, &b);
            }
        }
        let mut chunks = d.chunks_exact(64);
        for c in &mut chunks {
            Sha::block(&mut self.h, c);
        }
        self.buf.extend_from_slice(chunks.remainder());
    }
    fn hex(&self) -> String {
        let mut c = self.clone();
        let bits = self.len * 8;
        c.update(&[0x80]);
        while c.buf.len() != 56 {
            c.update(&[0]);
        }
        c.update(&bits.to_be_bytes());
        c.h.iter().map(|x| format!("{x:08x}")).collect()
    }
}

struct Sink {
    all: Sha,
    class: Sha,
    class_name: &'static str,
    class_inputs: u64,
    class_bytes: u64,
    inputs: u64,
    bytes: u64,
    failed: u64,
    dump: bool,
}

impl Sink {
    fn put(&mut self, s: &str) {
        self.all.update(s.as_bytes());
        self.class.update(s.as_bytes());
        self.class_bytes += s.len() as u64;
        self.bytes += s.len() as u64;
        self.class_inputs += 1;
        self.inputs += 1;
        if self.dump {
            let out = std::io::stdout();
            out.lock().write_all(s.as_bytes()).expect("stdout");
        }
    }
    fn check(&mut self, ok: bool, what: &str) {
        if !ok {
            self.failed += 1;
            eprintln!("NUMCMP_FAILED|class={}|input_index={}|what={what}|json=0", self.class_name, self.class_inputs);
        }
    }
    fn begin(&mut self, name: &'static str) {
        self.class = Sha::new();
        self.class_name = name;
        self.class_inputs = 0;
        self.class_bytes = 0;
    }
    fn end(&mut self) {
        if !self.dump {
            println!("NUMCMP_CLASS|class={}|rows={}|bytes={}|sha256={}|json=0", self.class_name, self.class_inputs, self.class_bytes, self.class.hex());
        }
    }
}

struct Rng(u64);

impl Rng {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    /// exactly `bits` bits, top bit set
    fn big(&mut self, bits: u64) -> BigUint {
        if bits == 0 {
            return BigUint::zero();
        }
        let mut n = BigUint::zero();
        let mut left = bits;
        while left > 0 {
            let take = left.min(32);
            let word = (self.next() >> 32) as u32 & (((1u64 << take) - 1) as u32);
            n = (n << take) + word;
            left -= take;
        }
        n | (BigUint::one() << (bits - 1))
    }
}

fn pow2(k: u64) -> BigUint {
    BigUint::one() << k
}

fn root_ok(n: &BigUint, r: &BigUint, k: u32) -> bool {
    let up = r + 1u32;
    &r.pow(k) <= n && &up.pow(k) > n
}

/// One BigUint through every changed operation. `heavy` adds cbrt and nth_root, which cost more at these sizes.
fn one(sink: &mut Sink, n: &BigUint, heavy: bool) {
    let dec = n.to_string();
    let hex = n.to_str_radix(16);
    let r3 = n.to_str_radix(3);
    let r7 = n.to_str_radix(7);
    let r27 = n.to_str_radix(27);
    let r36 = n.to_str_radix(36);
    sink.check(BigUint::from_str(&dec).as_ref() == Ok(n), "from_str");
    sink.check(BigUint::parse_bytes(dec.as_bytes(), 10).as_ref() == Some(n), "parse_bytes");
    sink.check(<BigUint as Num>::from_str_radix(&hex, 16).as_ref() == Ok(n), "radix16");
    sink.check(<BigUint as Num>::from_str_radix(&r3, 3).as_ref() == Ok(n), "radix3");
    sink.check(<BigUint as Num>::from_str_radix(&r7, 7).as_ref() == Ok(n), "radix7");
    sink.check(<BigUint as Num>::from_str_radix(&r27, 27).as_ref() == Ok(n), "radix27");
    sink.check(<BigUint as Num>::from_str_radix(&r36, 36).as_ref() == Ok(n), "radix36");
    let be10 = n.to_radix_be(10);
    sink.check(BigUint::from_radix_be(&be10, 10).as_ref() == Some(n), "be10");
    let le7 = n.to_radix_le(7);
    sink.check(BigUint::from_radix_le(&le7, 7).as_ref() == Some(n), "le7");
    let digits_match = dec.as_bytes().iter().zip(be10.iter()).all(|(c, d)| *c == b'0' + *d) && dec.len() == be10.len();
    sink.check(digits_match, "be10_digits");
    let s = n.sqrt();
    sink.check(root_ok(n, &s, 2), "sqrt");
    let neg = BigInt::from_biguint(Sign::Minus, n.clone());
    let neg_text = neg.to_string();
    sink.check(BigInt::from_str(&neg_text).as_ref() == Ok(&neg), "neg_parse");
    let plus = BigInt::from_biguint(Sign::Plus, n.clone());
    sink.check(plus.sqrt().to_biguint().as_ref() == Some(&s), "bigint_sqrt");
    // arithmetic the feature leaves alone, as a control on the same values
    let control = (n * n + 7u32) / 3u32 + n % 97u32;
    let mut row = format!("d={dec}|h={hex}|r3={r3}|r7={r7}|r27={r27}|r36={r36}|s={s}|n={neg_text}|c={control}");
    if heavy {
        let c = n.cbrt();
        sink.check(root_ok(n, &c, 3), "cbrt");
        let r5 = n.nth_root(5);
        sink.check(root_ok(n, &r5, 5), "root5");
        let r7th = n.nth_root(7);
        sink.check(root_ok(n, &r7th, 7), "root7");
        sink.check(BigInt::from_biguint(Sign::Minus, n.clone()).cbrt() == BigInt::from_biguint(Sign::Minus, c.clone()), "neg_cbrt");
        row.push_str(&format!("|cb={c}|r5={r5}|r7th={r7th}"));
    }
    row.push('\n');
    sink.put(&row);
}

macro_rules! unsigned_roots {
    ($name:ident, $t:ty) => {
        fn $name(sink: &mut Sink, x: $t) {
            let mut row = format!("{x}|{}|{}", x.sqrt(), x.cbrt());
            let big = BigUint::from(x);
            sink.check(root_ok(&big, &BigUint::from(x.sqrt()), 2), "prim_sqrt");
            sink.check(root_ok(&big, &BigUint::from(x.cbrt()), 3), "prim_cbrt");
            for k in [2u32, 3, 4, 5, 7, 9, 16, 33, 64, 127, 128, 129] {
                let r = x.nth_root(k);
                sink.check(root_ok(&big, &BigUint::from(r), k), "prim_nth");
                row.push_str(&format!("|{r}"));
            }
            row.push('\n');
            sink.put(&row);
        }
    };
}
unsigned_roots!(roots_u8, u8);
unsigned_roots!(roots_u16, u16);
unsigned_roots!(roots_u32, u32);
unsigned_roots!(roots_u64, u64);
unsigned_roots!(roots_u128, u128);
unsigned_roots!(roots_usize, usize);

macro_rules! signed_roots {
    ($name:ident, $t:ty) => {
        fn $name(sink: &mut Sink, x: $t) {
            let mut row = format!("{x}|{}", x.cbrt());
            for k in [1u32, 3, 5, 7, 9, 33, 127] {
                row.push_str(&format!("|{}", x.nth_root(k)));
            }
            if x >= 0 {
                row.push_str(&format!("|{}", x.sqrt()));
            }
            let want = BigInt::from(x).cbrt();
            sink.check(want == BigInt::from(x.cbrt()), "signed_cbrt");
            row.push('\n');
            sink.put(&row);
        }
    };
}
signed_roots!(roots_i8, i8);
signed_roots!(roots_i16, i16);
signed_roots!(roots_i32, i32);
signed_roots!(roots_i64, i64);
signed_roots!(roots_i128, i128);
signed_roots!(roots_isize, isize);

fn run(dump: bool) -> u64 {
    let mut sink = Sink { all: Sha::new(), class: Sha::new(), class_name: "", class_inputs: 0, class_bytes: 0, inputs: 0, bytes: 0, failed: 0, dump };
    let mut rng = Rng(88172645463325252);

    // Perfect squares and their neighbours, up to and past 2^4096.
    sink.begin("squares");
    let mut sizes: Vec<u64> = (1..=600).collect();
    sizes.extend((600..=11000).step_by(97));
    for (i, bits) in sizes.iter().enumerate() {
        let x = rng.big(*bits);
        let n = &x * &x;
        sink.check(n.sqrt() == x, "square_root_of_a_square");
        if !n.is_zero() {
            one(&mut sink, &(&n - 1u32), i % 4 == 0);
        }
        one(&mut sink, &n, i % 4 == 0);
        one(&mut sink, &(&n + 1u32), i % 4 == 0);
    }
    sink.end();

    // Squares of 2^k - 1, where a rounded guess lands above the root.
    sink.begin("squares_of_all_ones");
    for k in (1..=700u64).chain((700..=5200).step_by(23)) {
        let x = pow2(k) - 1u32;
        let n = &x * &x;
        sink.check(n.sqrt() == x, "square_of_all_ones");
        one(&mut sink, &(&n - 1u32), k % 16 == 0);
        one(&mut sink, &n, k % 16 == 0);
        one(&mut sink, &(&n + 1u32), k % 16 == 0);
    }
    sink.end();

    // Powers of 2 and their neighbours.
    sink.begin("powers_of_2");
    for k in (0..=4400u64).chain((4400..=20000).step_by(61)) {
        let n = pow2(k);
        if k > 0 {
            one(&mut sink, &(&n - 1u32), k % 16 == 0);
        }
        one(&mut sink, &n, k % 16 == 0);
        one(&mut sink, &(&n + 1u32), k % 16 == 0);
    }
    sink.end();

    // Where the float paths change branch: the u32, u64, 2^53 and 2^1024 edges, and the 2^4096 line named in the work order.
    sink.begin("boundaries");
    for base in [31u64, 32, 33, 52, 53, 54, 63, 64, 65, 106, 127, 128, 129, 511, 512, 513, 1022, 1023, 1024, 1025, 1026, 2046, 2047, 2048, 2049, 2050, 4095, 4096, 4097, 8191, 8192, 8193] {
        let c = pow2(base);
        for d in 0..=256u32 {
            one(&mut sink, &(&c + d), d == 0 || d == 256);
            if c > BigUint::from(d) {
                one(&mut sink, &(&c - d), d == 256);
            }
        }
    }
    // The largest binary64 value, and the first integer that rounds past it, with neighbours and squares.
    let top = (pow2(53) - 1u32) << 971u32;
    let past = (pow2(54) - 1u32) << 970u32;
    for c in [&top, &past] {
        for d in 0..=64u32 {
            one(&mut sink, &(c + d), true);
            one(&mut sink, &(c - d), true);
        }
        let sq = c * c;
        one(&mut sink, &(&sq - 1u32), true);
        one(&mut sink, &sq, true);
        one(&mut sink, &(&sq + 1u32), true);
    }
    sink.end();

    // Digit-count edges of the capacity estimates.
    sink.begin("radix_powers");
    for (base, last) in [(10u32, 2600u32), (3, 5000), (7, 3000), (27, 1700), (36, 1500)] {
        let mut p = BigUint::one();
        for k in 0..=last {
            if k % 3 == 0 || k < 400 {
                if k > 0 {
                    one(&mut sink, &(&p - 1u32), false);
                }
                one(&mut sink, &p, false);
                one(&mut sink, &(&p + 1u32), false);
            }
            p *= base;
        }
    }
    sink.end();

    // Random values, every size to 8192 bits and sparse above 2^4096 to 2^24000.
    sink.begin("random");
    for i in 0..12000u64 {
        let bits = 1 + rng.next() % 8192;
        let n = rng.big(bits);
        one(&mut sink, &n, i % 8 == 0);
    }
    for i in 0..1200u64 {
        let bits = 4097 + rng.next() % 19904;
        let n = rng.big(bits);
        one(&mut sink, &n, i % 16 == 0);
    }
    sink.end();

    // Text the parsers take and refuse.
    sink.begin("parse_cases");
    for t in [
        "", "-", "+", "_", "0", "-0", "+0", "00", "000000000000000000000000000000", "1_000", "_1", "1_", "1__2", "12a", "a12", " 1", "1 ", "+-1", "--1", "++1", "0x10", "1e9", "1.5", "٣",
        "340282366920938463463374607431768211456", "-340282366920938463463374607431768211456", "000000000000000000000000000000000000000340282366920938463463374607431768211456",
        "1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1",
    ] {
        let a = format!("{:?}", BigInt::from_str(t).map(|v| v.to_string()).map_err(|e| e.to_string()));
        let b = format!("{:?}", BigUint::from_str(t).map(|v| v.to_string()).map_err(|e| e.to_string()));
        let c = format!("{:?}", <BigUint as Num>::from_str_radix(t, 36).map(|v| v.to_string()).map_err(|e| e.to_string()));
        let d = format!("{:?}", BigInt::parse_bytes(t.as_bytes(), 7).map(|v| v.to_string()));
        sink.put(&format!("{t:?}|{a}|{b}|{c}|{d}\n"));
    }
    sink.end();

    // The primitive roots: every u8, i8, u16, i16, then edges and random values.
    sink.begin("primitive_roots");
    for x in 0..=u8::MAX {
        roots_u8(&mut sink, x);
    }
    for x in i8::MIN..=i8::MAX {
        roots_i8(&mut sink, x);
    }
    for x in 0..=u16::MAX {
        roots_u16(&mut sink, x);
    }
    for x in i16::MIN..=i16::MAX {
        roots_i16(&mut sink, x);
    }
    let mut edges: Vec<u128> = Vec::new();
    for k in 0..128u32 {
        let p = 1u128 << k;
        edges.extend([p - 1, p, p + 1]);
    }
    for k in 1..=65536u128 {
        edges.extend([k * k - 1, k * k, k * k + 1]);
    }
    for k in (1..=2642245u128).step_by(1021) {
        let c = k * k * k;
        edges.extend([c - 1, c, c + 1]);
    }
    for k in (0..=u64::MAX as u128).step_by(1 << 50) {
        edges.extend([k * k, k.saturating_mul(k).saturating_add(1)]);
    }
    for _ in 0..120000 {
        let bits = 1 + rng.next() % 128;
        let hi = rng.next() as u128;
        let lo = rng.next() as u128;
        let v = (hi << 64) | lo;
        edges.push(if bits >= 128 { v } else { v & ((1u128 << bits) - 1) });
    }
    for v in &edges {
        let w = *v;
        if let Ok(x) = u32::try_from(w) {
            roots_u32(&mut sink, x);
        }
        if let Ok(x) = u64::try_from(w) {
            roots_u64(&mut sink, x);
            roots_usize(&mut sink, x as usize);
        }
        if w % 8 == 0 || w > u64::MAX as u128 {
            roots_u128(&mut sink, w);
        }
        if let Ok(x) = i32::try_from(w) {
            roots_i32(&mut sink, x);
            roots_i32(&mut sink, -x);
        }
        if let Ok(x) = i64::try_from(w) {
            roots_i64(&mut sink, x);
            roots_i64(&mut sink, -x);
            roots_isize(&mut sink, x as isize);
            roots_isize(&mut sink, -(x as isize));
        }
        if let Ok(x) = i128::try_from(w) {
            if w % 8 == 1 {
                roots_i128(&mut sink, x);
                roots_i128(&mut sink, -x);
            }
        }
    }
    sink.end();

    if !dump {
        println!("NUMCMP_DONE|rows={}|bytes={}|sha256={}|failed={}|json=0", sink.inputs, sink.bytes, sink.all.hex(), sink.failed);
    }
    sink.failed
}

#[cfg(target_arch = "x86_64")]
fn mxcsr() {
    use std::arch::x86_64::{_mm_getcsr, _mm_setcsr};
    fn clear() {
        unsafe { _mm_setcsr(_mm_getcsr() & !0x3f) }
    }
    fn flags() -> u32 {
        unsafe { _mm_getcsr() & 0x3f }
    }
    let big = BigInt::from(2).pow(200) + BigInt::from(1);
    let huge = BigInt::from(2).pow(5000) + BigInt::from(1);
    clear();
    let r = big.sqrt();
    let f_sqrt = flags();
    clear();
    let h = huge.sqrt();
    let f_huge = flags();
    clear();
    let c = big.cbrt();
    let f_cbrt = flags();
    clear();
    let s = big.to_string();
    let f_display = flags();
    clear();
    let p = BigInt::from_str("1606938044258990275541962092341162602522202993782792835301377").expect("parse");
    let f_parse = flags();
    clear();
    let t = &big * &big + &big;
    let f_mul = flags();
    clear();
    let q = &t / &big;
    let f_div = flags();
    println!("MXCSR|sqrt={f_sqrt:#x}|sqrt_above_2_4096={f_huge:#x}|cbrt={f_cbrt:#x}|display={f_display:#x}|parse={f_parse:#x}|mul_add={f_mul:#x}|div={f_div:#x}|json=0");
    assert!(r > BigInt::from(0) && h > BigInt::from(0) && c > BigInt::from(0) && !s.is_empty() && p == big && q > BigInt::from(0));
}

#[cfg(not(target_arch = "x86_64"))]
fn mxcsr() {
    println!("MXCSR|result=NOT_MEASURED|reason=not_x86_64|json=0");
}

fn main() {
    let mode = std::env::args().nth(1).unwrap_or_default();
    let code = match mode.as_str() {
        "digest" => run(false),
        "dump" => run(true),
        "mxcsr" => {
            mxcsr();
            0
        }
        _ => {
            eprintln!("usage: numcmp digest|dump|mxcsr");
            2
        }
    };
    std::process::exit(if code == 0 { 0 } else { 1 });
}
