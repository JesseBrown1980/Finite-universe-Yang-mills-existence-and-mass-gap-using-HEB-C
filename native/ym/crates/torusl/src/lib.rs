//! Shared S3 group and periodic-lattice gauge construction (Stage 2C,
//! generalised to Lx x Ly). Used by the `torusl` builder and the
//! matrix-free `onfly` operator. Integer-only, Rust 1.81, no external crates.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

pub mod play;
pub mod sha;

pub const PERM: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
pub const TRANS: [u8; 3] = [1, 2, 5];

pub fn mul_raw(a: u8, b: u8) -> u8 {
    let p = PERM[a as usize];
    let q = PERM[b as usize];
    let t = [p[q[0] as usize], p[q[1] as usize], p[q[2] as usize]];
    PERM.iter().position(|x| *x == t).map_or(255, |v| v as u8)
}

pub struct G {
    pub mul: [[u8; 6]; 6],
    pub inv: [u8; 6],
}

impl G {
    pub fn new() -> G {
        let mut mul = [[0u8; 6]; 6];
        for a in 0..6u8 {
            for b in 0..6u8 {
                mul[a as usize][b as usize] = mul_raw(a, b);
            }
        }
        let mut inv = [0u8; 6];
        for a in 0..6usize {
            inv[a] = (0..6u8).find(|&b| mul[a][b as usize] == 0).unwrap_or(255);
        }
        G { mul, inv }
    }
    pub fn m(&self, a: u8, b: u8) -> u8 {
        self.mul[a as usize][b as usize]
    }
    pub fn i(&self, a: u8) -> u8 {
        self.inv[a as usize]
    }
}

pub fn character(a: u8) -> i64 {
    if a == 0 {
        2
    } else if a == 3 || a == 4 {
        -1
    } else {
        0
    }
}

pub struct Lat {
    pub lx: usize,
    pub ly: usize,
    pub n: usize,
    pub edges: Vec<(usize, usize)>,
    pub tree: Vec<usize>, // in the order h is propagated
    pub free: Vec<usize>,
}

impl Lat {
    pub fn new(lx: usize, ly: usize) -> Lat {
        let n = lx * ly;
        let site = |x: usize, y: usize| (x % lx) * ly + (y % ly);
        let mut edges = vec![(0, 0); 2 * n];
        for x in 0..lx {
            for y in 0..ly {
                let a = site(x, y);
                edges[a] = (a, site(x + 1, y));
                edges[n + a] = (a, site(x, y + 1));
            }
        }
        let mut tree = Vec::new();
        for y in 0..ly - 1 {
            tree.push(n + site(0, y));
        }
        for x in 0..lx - 1 {
            for y in 0..ly {
                tree.push(site(x, y));
            }
        }
        let free: Vec<usize> = (0..2 * n).filter(|e| !tree.contains(e)).collect();
        Lat { lx, ly, n, edges, tree, free }
    }
    pub fn site(&self, x: usize, y: usize) -> usize {
        (x % self.lx) * self.ly + (y % self.ly)
    }
    pub fn encode(&self, q: &[u8]) -> usize {
        let mut id = 0;
        let mut p = 1;
        for &v in q {
            id += usize::from(v) * p;
            p *= 6;
        }
        id
    }
    pub fn decode(&self, mut id: usize) -> Vec<u8> {
        (0..self.free.len())
            .map(|_| {
                let v = (id % 6) as u8;
                id /= 6;
                v
            })
            .collect()
    }
    pub fn canonical(&self, g: &G, q: &[u8]) -> usize {
        (0..6u8)
            .map(|c| self.encode(&q.iter().map(|&x| g.m(g.m(c, x), g.i(c))).collect::<Vec<_>>()))
            .min()
            .unwrap_or(usize::MAX)
    }
    pub fn representative(&self, q: &[u8]) -> Vec<u8> {
        let mut links = vec![0u8; 2 * self.n];
        for (i, &e) in self.free.iter().enumerate() {
            links[e] = q[i];
        }
        links
    }
    pub fn gauge_fix(&self, g: &G, links: &[u8]) -> Vec<u8> {
        let mut h = vec![0u8; self.n];
        let mut set = vec![false; self.n];
        set[0] = true;
        for &e in &self.tree {
            let (t, hd) = self.edges[e];
            debug_assert!(set[t] && !set[hd]);
            h[hd] = g.m(h[t], links[e]);
            set[hd] = true;
        }
        self.free
            .iter()
            .map(|&e| {
                let (t, hd) = self.edges[e];
                g.m(g.m(h[t], links[e]), g.i(h[hd]))
            })
            .collect()
    }
    pub fn magnetic(&self, g: &G, s: &[u8]) -> i64 {
        let mut act = 0;
        for x in 0..self.lx {
            for y in 0..self.ly {
                let a = self.site(x, y);
                let right = self.site(x + 1, y);
                let up = self.site(x, y + 1);
                let p = g.m(g.m(g.m(s[a], s[self.n + right]), g.i(s[up])), g.i(s[self.n + a]));
                act += 2 - character(p);
            }
        }
        act
    }
}


impl Default for G {
    fn default() -> Self {
        G::new()
    }
}

impl Lat {
    /// size of the global-conjugation orbit of a free-loop configuration
    pub fn weight(&self, g: &G, q: &[u8]) -> i64 {
        let mut codes: Vec<usize> = (0..6u8)
            .map(|c| self.encode(&q.iter().map(|&x| g.m(g.m(c, x), g.i(c))).collect::<Vec<_>>()))
            .collect();
        codes.sort_unstable();
        codes.dedup();
        i64::try_from(codes.len()).unwrap_or(0)
    }
}
