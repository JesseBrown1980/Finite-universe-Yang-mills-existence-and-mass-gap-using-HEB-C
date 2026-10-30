//! S3 torus lattice: comb gauge tree, free-loop encoding, global-conjugation orbit keys and Gauss
//! weights, magnetic action. Ported from The-matrix-law-essentials python/volume/flat_law.py.
use std::collections::BTreeSet;

pub const PERM: [[usize; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
pub const TRANS: [usize; 3] = [1, 2, 5];

pub struct Group {
    pub mul: [[usize; 6]; 6],
    pub inv: [usize; 6],
}

impl Group {
    pub fn new() -> Self {
        let mut mul = [[0usize; 6]; 6];
        for (a, pa) in PERM.iter().enumerate() {
            for (b, pb) in PERM.iter().enumerate() {
                let p: [usize; 3] = [pa[pb[0]], pa[pb[1]], pa[pb[2]]];
                mul[a][b] = PERM.iter().position(|&q| q == p).unwrap_or(0);
            }
        }
        let mut inv = [0usize; 6];
        for a in 0..6 {
            inv[a] = (0..6).find(|&b| mul[a][b] == 0).unwrap_or(0);
        }
        Group { mul, inv }
    }
}

pub fn chi(a: usize) -> i64 {
    match a {
        0 => 2,
        3 | 4 => -1,
        _ => 0,
    }
}

pub struct Lat {
    pub lx: usize,
    pub ly: usize,
    pub n: usize,
    pub edges: Vec<(usize, usize)>,
    pub tree: Vec<usize>,
    pub free: Vec<usize>,
    pub g: Group,
}

impl Lat {
    pub fn new(lx: usize, ly: usize) -> Self {
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
        let mut tree: Vec<usize> = (0..ly - 1).map(|y| n + site(0, y)).collect();
        for x in 0..lx - 1 {
            for y in 0..ly {
                tree.push(site(x, y));
            }
        }
        let ts: BTreeSet<usize> = tree.iter().copied().collect();
        let free = (0..2 * n).filter(|e| !ts.contains(e)).collect();
        Lat { lx, ly, n, edges, tree, free, g: Group::new() }
    }
    pub fn site(&self, x: usize, y: usize) -> usize {
        (x % self.lx) * self.ly + (y % self.ly)
    }
    pub fn links(&self) -> usize {
        2 * self.n
    }
    pub fn gauge_fix(&self, links: &[usize]) -> Vec<usize> {
        let m = &self.g.mul;
        let mut h = vec![0usize; self.n];
        for &e in &self.tree {
            let (t, hd) = self.edges[e];
            h[hd] = m[h[t]][links[e]];
        }
        self.free.iter().map(|&e| m[m[h[self.edges[e].0]][links[e]]][self.g.inv[h[self.edges[e].1]]]).collect()
    }
    fn conj(&self, q: &[usize], c: usize) -> Vec<usize> {
        let m = &self.g.mul;
        q.iter().map(|&x| m[m[c][x]][self.g.inv[c]]).collect()
    }
    fn code(q: &[usize]) -> u64 {
        q.iter().rev().fold(0u64, |acc, &v| acc * 6 + v as u64)
    }
    /// canonical key: min base-6 little-endian code over the 6 conjugations (as in torusl)
    pub fn key(&self, q: &[usize]) -> u64 {
        (0..6).map(|c| Self::code(&self.conj(q, c))).min().unwrap_or(0)
    }
    /// Gauss weight: number of distinct conjugates
    pub fn weight(&self, q: &[usize]) -> i64 {
        let s: BTreeSet<u64> = (0..6).map(|c| Self::code(&self.conj(q, c))).collect();
        s.len() as i64
    }
    pub fn rep(&self, q: &[usize]) -> Vec<usize> {
        let mut l = vec![0usize; 2 * self.n];
        for (i, &e) in self.free.iter().enumerate() {
            l[e] = q[i];
        }
        l
    }
    pub fn magnetic(&self, l: &[usize]) -> i64 {
        let m = &self.g.mul;
        let inv = &self.g.inv;
        let n = self.n;
        let mut act = 0;
        for x in 0..self.lx {
            for y in 0..self.ly {
                let (a, r, u) = (self.site(x, y), self.site(x + 1, y), self.site(x, y + 1));
                let p = m[m[m[l[a]][l[n + r]]][inv[l[u]]]][inv[l[n + a]]];
                act += 2 - chi(p);
            }
        }
        act
    }
    /// translate a raw link configuration by (dx, dy)
    pub fn translate(&self, l: &[usize], dx: usize, dy: usize) -> Vec<usize> {
        let n = self.n;
        let mut out = vec![0usize; 2 * n];
        for x in 0..self.lx {
            for y in 0..self.ly {
                let a = self.site(x, y);
                let b = self.site(x + dx, y + dy);
                out[b] = l[a];
                out[n + b] = l[n + a];
            }
        }
        out
    }
}
