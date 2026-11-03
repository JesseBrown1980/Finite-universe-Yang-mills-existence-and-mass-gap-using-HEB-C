//! Second-seat review core: S3 as Z3 semidirect Z2, the torus, and the definition of H.
//! Written from the definition, with no code from the reviewed tools. Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::HashMap;

/// A group element: k + 3 f, for the map x -> k + (-1)^f x on Z3.
pub type El = u8;
pub const ID: El = 0;

pub struct Group {
    pub mul: [[El; 6]; 6],
    pub inv: [El; 6],
    /// 0 identity, 1 transposition, 2 three-cycle, by counting fixed points of the action.
    pub class: [u8; 6],
    pub trans: [El; 3],
    /// conj[g][u] = g u g^-1.
    pub conj: [[El; 6]; 6],
}

fn action(e: El, x: u8) -> u8 {
    let k = e % 3;
    let f = e / 3;
    if f == 0 {
        (k + x) % 3
    } else {
        (k + 3 - x) % 3
    }
}

impl Group {
    #[must_use]
    pub fn new() -> Group {
        let mut mul = [[0u8; 6]; 6];
        for (a, row) in mul.iter_mut().enumerate() {
            for (b, cell) in row.iter_mut().enumerate() {
                let (ka, fa) = ((a % 3) as u8, (a / 3) as u8);
                let (kb, fb) = ((b % 3) as u8, (b / 3) as u8);
                let k = if fa == 0 { (ka + kb) % 3 } else { (ka + 3 - kb) % 3 };
                let f = fa ^ fb;
                *cell = k + 3 * f;
            }
        }
        // The product must be composition of the action, and identity must be element 0.
        for a in 0..6u8 {
            for b in 0..6u8 {
                for x in 0..3u8 {
                    assert_eq!(action(mul[a as usize][b as usize], x), action(a, action(b, x)));
                }
            }
        }
        let mut inv = [0u8; 6];
        for a in 0..6usize {
            for b in 0..6usize {
                if mul[a][b] == ID {
                    inv[a] = b as u8;
                }
            }
        }
        let mut class = [0u8; 6];
        let mut trans = [0u8; 3];
        let mut nt = 0;
        for (e, c) in class.iter_mut().enumerate() {
            let fixed = (0..3u8).filter(|&x| action(e as u8, x) == x).count();
            *c = match fixed {
                3 => 0,
                1 => {
                    trans[nt] = e as u8;
                    nt += 1;
                    1
                }
                0 => 2,
                _ => panic!("S3 has no element with two fixed points"),
            };
        }
        assert_eq!(nt, 3);
        let mut conj = [[0u8; 6]; 6];
        for g in 0..6usize {
            for u in 0..6usize {
                conj[g][u] = mul[mul[g][u] as usize][inv[g] as usize];
            }
        }
        Group { mul, inv, class, trans, conj }
    }

    #[inline]
    #[must_use]
    pub fn m(&self, a: El, b: El) -> El {
        self.mul[a as usize][b as usize]
    }

    #[inline]
    #[must_use]
    pub fn i(&self, a: El) -> El {
        self.inv[a as usize]
    }
}

impl Default for Group {
    fn default() -> Self {
        Self::new()
    }
}

/// M cost of one plaquette: 2 - chi, chi = fixed points - 1: identity 0, transposition 2, 3-cycle 3.
#[inline]
#[must_use]
pub fn cost_of_class(c: u8) -> u32 {
    [0, 2, 3][c as usize]
}

/// Patterns of a link, by the two holonomies in its frame.
pub const P_EE: usize = 0;
pub const P_ET: usize = 1;
pub const P_EC: usize = 2;
pub const P_TTS: usize = 3;
pub const P_TTD: usize = 4;
pub const P_TC: usize = 5;
pub const P_CC: usize = 6;
pub const NPAT: usize = 7;

/// The local rule as I derived it: (da, db, count) for each pattern.
pub const RULE: [&[(i32, i32, u32)]; NPAT] = [
    &[(2, 0, 3)],
    &[(0, 0, 1), (0, 1, 2)],
    &[(2, -1, 3)],
    &[(-2, 0, 1), (-2, 2, 2)],
    &[(-2, 1, 2), (-2, 2, 1)],
    &[(0, -1, 1), (0, 0, 2)],
    &[(2, -2, 3)],
];

#[derive(Clone)]
pub struct Torus {
    pub lx: usize,
    pub ly: usize,
    pub sites: usize,
    pub nl: usize,
    /// plaq[p] = [x(p), y(p + ex), x(p + ey), y(p)], read x, y, x^-1, y^-1.
    pub plaq: Vec<[usize; 4]>,
    /// The two plaquettes of each link.
    pub link_plaq: Vec<[usize; 2]>,
    /// For each link and each of its plaquettes: the other three links with an inverse flag, in reading order after the link.
    pub staple: Vec<[[(usize, bool); 3]; 2]>,
    pub src: Vec<usize>,
    pub dst: Vec<usize>,
}

impl Torus {
    #[must_use]
    pub fn new(lx: usize, ly: usize) -> Torus {
        let sites = lx * ly;
        let nl = 2 * sites;
        let s = |x: usize, y: usize| (x % lx) + lx * (y % ly);
        let xl = |x: usize, y: usize| 2 * s(x, y);
        let yl = |x: usize, y: usize| 2 * s(x, y) + 1;
        let mut plaq = vec![[0usize; 4]; sites];
        let mut src = vec![0usize; nl];
        let mut dst = vec![0usize; nl];
        for y in 0..ly {
            for x in 0..lx {
                plaq[s(x, y)] = [xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)];
                src[xl(x, y)] = s(x, y);
                dst[xl(x, y)] = s(x + 1, y);
                src[yl(x, y)] = s(x, y);
                dst[yl(x, y)] = s(x, y + 1);
            }
        }
        let mut link_plaq = vec![[usize::MAX; 2]; nl];
        let mut staple = vec![[[(0usize, false); 3]; 2]; nl];
        for y in 0..ly {
            for x in 0..lx {
                // x-link at (x, y): plaquette (x, y) walked right, up, left, down; plaquette (x, y-1) walked right, down, left, up.
                let l = xl(x, y);
                let dn = y + ly - 1;
                link_plaq[l] = [s(x, y), s(x, dn)];
                staple[l][0] = [(yl(x + 1, y), false), (xl(x, y + 1), true), (yl(x, y), true)];
                staple[l][1] = [(yl(x + 1, dn), true), (xl(x, dn), true), (yl(x, dn), false)];
                // y-link at (x, y): plaquette (x, y) walked up, right, down, left; plaquette (x-1, y) walked up, left, down, right.
                let l = yl(x, y);
                let lf = x + lx - 1;
                link_plaq[l] = [s(x, y), s(lf, y)];
                staple[l][0] = [(xl(x, y + 1), false), (yl(x + 1, y), true), (xl(x, y), true)];
                staple[l][1] = [(xl(lf, y + 1), true), (yl(lf, y), true), (xl(lf, y), false)];
            }
        }
        Torus { lx, ly, sites, nl, plaq, link_plaq, staple, src, dst }
    }

    /// Holonomy of a plaquette read from the plaquette list.
    #[inline]
    #[must_use]
    pub fn hol(&self, g: &Group, u: &[El], p: usize) -> El {
        let q = &self.plaq[p];
        let a = g.m(u[q[0]], u[q[1]]);
        let b = g.m(a, g.i(u[q[2]]));
        g.m(b, g.i(u[q[3]]))
    }

    /// The lump by recomputing every plaquette.
    #[must_use]
    pub fn lump_full(&self, g: &Group, u: &[El]) -> (u32, u32) {
        let (mut a, mut b) = (0, 0);
        for p in 0..self.sites {
            match g.class[self.hol(g, u, p) as usize] {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        (a, b)
    }

    /// The two frame holonomies of a link: both read starting with U_l forward.
    #[inline]
    #[must_use]
    pub fn frame(&self, g: &Group, u: &[El], l: usize) -> (El, El) {
        let mut out = [u[l]; 2];
        for (side, o) in out.iter_mut().enumerate() {
            for &(k, inv) in &self.staple[l][side] {
                let e = if inv { g.i(u[k]) } else { u[k] };
                *o = g.m(*o, e);
            }
        }
        (out[0], out[1])
    }

    #[inline]
    #[must_use]
    pub fn pattern(&self, g: &Group, u: &[El], l: usize) -> usize {
        let (x, y) = self.frame(g, u, l);
        pattern_of(g, x, y)
    }

    /// The n vector of a configuration.
    #[must_use]
    pub fn counts(&self, g: &Group, u: &[El]) -> [u32; NPAT] {
        let mut n = [0u32; NPAT];
        for l in 0..self.nl {
            n[self.pattern(g, u, l)] += 1;
        }
        n
    }
}

#[inline]
#[must_use]
pub fn pattern_of(g: &Group, x: El, y: El) -> usize {
    let (cx, cy) = (g.class[x as usize], g.class[y as usize]);
    match (cx.min(cy), cx.max(cy)) {
        (0, 0) => P_EE,
        (0, 1) => P_ET,
        (0, 2) => P_EC,
        (1, 1) => {
            if x == y {
                P_TTS
            } else {
                P_TTD
            }
        }
        (1, 2) => P_TC,
        _ => P_CC,
    }
}

/// ceil(2 sqrt n), by search on integers.
#[must_use]
pub fn ceil_two_root(n: u32) -> u32 {
    let mut v = 0u32;
    while v * v < 4 * n {
        v += 1;
    }
    v
}

/// The most links with both plaquettes inside a set of s plaquettes, as I derived it.
#[must_use]
pub fn adj_limit(s: u32, lx: u32, ly: u32) -> u32 {
    let p = lx * ly;
    if s == 0 {
        return 0;
    }
    if s == p {
        return 2 * s;
    }
    2 * s - ceil_two_root(s).min(lx.min(ly)).min(ceil_two_root(p - s))
}

/// The vector: one positive integer per lump, d = 0 on the flat lump.
#[derive(Clone)]
pub struct Vector {
    pub g: HashMap<(u32, u32), i128>,
}

impl Vector {
    /// Reads rows `G|id=..|a=..|b=..|g=..|json=0`.
    ///
    /// # Panics
    /// When the file cannot be read or a row is malformed.
    #[must_use]
    pub fn load(path: &str) -> Vector {
        let text = std::fs::read_to_string(path).expect("vector file");
        let mut g = HashMap::new();
        for line in text.lines() {
            if !line.starts_with("G|") {
                continue;
            }
            let (mut a, mut b, mut v) = (None, None, None);
            for part in line.split('|') {
                if let Some(x) = part.strip_prefix("a=") {
                    a = x.parse::<u32>().ok();
                } else if let Some(x) = part.strip_prefix("b=") {
                    b = x.parse::<u32>().ok();
                } else if let Some(x) = part.strip_prefix("g=") {
                    v = x.parse::<i128>().ok();
                }
            }
            let (a, b, v) = (a.expect("a"), b.expect("b"), v.expect("g"));
            assert!(v > 0, "non-positive g at {a} {b}");
            g.insert((a, b), v);
        }
        g.insert((0, 0), 0);
        Vector { g }
    }

    #[inline]
    #[must_use]
    pub fn d(&self, a: u32, b: u32) -> i128 {
        *self.g.get(&(a, b)).expect("lump in vector")
    }
}

/// Result of the exact ratio: numerator, denominator, lump, target-lump histogram.
pub type RatioOut = (i128, i128, (u32, u32), HashMap<(u32, u32), u32>);

/// Exact ratio by the definition: (r M d(x) + sum over 3 nl moves (d(x) - d(m x))) / d(x), with every move's lump recomputed in full.
/// Returns the numerator and the denominator d(x), the lump, and the histogram of target lumps.
pub fn ratio_from_definition(t: &Torus, g: &Group, u: &mut [El], v: &Vector, r_num: i128, r_den: i128) -> RatioOut {
    let (a, b) = t.lump_full(g, u);
    let d0 = v.d(a, b);
    let m = i128::from(2 * a + 3 * b);
    let mut hist: HashMap<(u32, u32), u32> = HashMap::new();
    let mut sum: i128 = 0;
    for l in 0..t.nl {
        let keep = u[l];
        for &s in &g.trans {
            u[l] = g.m(s, keep);
            let tl = t.lump_full(g, u);
            *hist.entry(tl).or_insert(0) += 1;
            sum += d0 - v.d(tl.0, tl.1);
        }
        u[l] = keep;
    }
    // R = r M + sum / d0 = (r_num M d0 + r_den sum) / (r_den d0)
    (r_num * m * d0 + r_den * sum, r_den * d0, (a, b), hist)
}

/// Floor of 10^6 num / den.
#[inline]
#[must_use]
pub fn micro(num: i128, den: i128) -> i128 {
    (num * 1_000_000).div_euclid(den)
}

/// xorshift64*, integer only.
pub struct Rng(pub u64);

impl Rng {
    #[inline]
    pub fn step(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x9E37_79B9_7F4A_7C15)
    }

    #[inline]
    pub fn below(&mut self, n: u64) -> u64 {
        // Top bits are the good ones.
        ((u128::from(self.step() >> 32) * u128::from(n)) >> 32) as u64
    }
}
