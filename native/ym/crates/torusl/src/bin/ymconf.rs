//! ymconf: S3 gauge Hamiltonian on an open ROWS x COLS strip, vacuum sector or static-charge sector,
//! in the standard exchange format (weights, magnetic diagonal, electric triples) read by sturmrs.
//!
//! Gauge-invariant states: comb spanning tree (every vertical link of column 0, every horizontal link),
//! free links = the other vertical links (one per plaquette), orbit representatives under global
//! conjugation, weight = orbit size. Electric term E = sum over lattice links and transpositions t of
//! (1 - L_t): move the link, gauge-fix, take the orbit. Magnetic term M = sum over plaquettes of
//! (2 - chi_std(U_p)), diagonal.
//!
//! Charged sector (CH = 1): an auxiliary link l from b = (XB, row) to a = (XA, row), row = (ROWS-1)/2,
//! with no electric and no magnetic term. Gauge-invariant states with l in irrep R are the sector with
//! static charge R at b and its conjugate at a, each once. The std sector is selected exactly by the
//! penalty 10 (E_l - 3)^2 (0 on std, 90 on trivial and sign), which commutes with the Hamiltonian, so the
//! electric part written is Z = E + 10 (E_l - 3)^2.
//! Wilson mode (CH = 2, vacuum sector): the diagonal column is JB M + LAM chi_std(U_C) for the rectangle C
//! on rows 0..1 and columns XA..XB, so sturmrs called with JB = 1 counts H + lambda W(C) with
//! r = JB/JE and lambda = LAM/JE.
//! The written operator is checked exactly W-self-adjoint (w_i Z_ij = w_j Z_ji).
//! usage: ymconf ROWS COLS XA XB CH OUT_MATRIX [JB LAM]        json=0
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::{BTreeMap, HashMap};
use std::io::Write;
use torusl::{G, TRANS};

const PENALTY: i64 = 10;

struct Graph {
    edges: Vec<(usize, usize)>,
    hid: Vec<usize>,
    vid: Vec<usize>,
    cols: usize,
    tree: Vec<usize>,
    free: Vec<usize>,
    plaq: Vec<[usize; 4]>,
    lattice_links: usize,
    aux: Option<usize>,
    sites: usize,
}

fn chi_std(a: u8) -> i64 {
    match a {
        0 => 2,
        3 | 4 => -1,
        _ => 0,
    }
}

fn graph(rows: usize, cols: usize, charge: Option<(usize, usize)>) -> Graph {
    let site = |x: usize, y: usize| y * cols + x;
    let mut edges = Vec::new();
    let mut hid = vec![usize::MAX; rows * cols];
    let mut vid = vec![usize::MAX; rows * cols];
    for y in 0..rows {
        for x in 0..cols - 1 {
            hid[site(x, y)] = edges.len();
            edges.push((site(x, y), site(x + 1, y)));
        }
    }
    for y in 0..rows - 1 {
        for x in 0..cols {
            vid[site(x, y)] = edges.len();
            edges.push((site(x, y), site(x, y + 1)));
        }
    }
    // tree in root-outward order: column 0 verticals bottom-up, then each row's horizontals left to right
    let mut tree: Vec<usize> = (0..rows - 1).map(|y| vid[site(0, y)]).collect();
    for y in 0..rows {
        for x in 0..cols - 1 {
            tree.push(hid[site(x, y)]);
        }
    }
    let mut free: Vec<usize> = Vec::new();
    for y in 0..rows - 1 {
        for x in 1..cols {
            free.push(vid[site(x, y)]);
        }
    }
    let mut plaq = Vec::new();
    for y in 0..rows - 1 {
        for x in 0..cols - 1 {
            plaq.push([hid[site(x, y)], vid[site(x + 1, y)], hid[site(x, y + 1)], vid[site(x, y)]]);
        }
    }
    let lattice_links = edges.len();
    let row = (rows - 1) / 2;
    let aux = charge.map(|(xa, xb)| {
        edges.push((site(xb, row), site(xa, row)));
        free.push(edges.len() - 1);
        edges.len() - 1
    });
    Graph { edges, hid, vid, cols, tree, free, plaq, lattice_links, aux, sites: rows * cols }
}

struct Sys<'a> {
    g: &'a G,
    gr: &'a Graph,
}

impl Sys<'_> {
    fn raw(&self, q: &[u8]) -> Vec<u8> {
        let mut l = vec![0u8; self.gr.edges.len()];
        for (i, &e) in self.gr.free.iter().enumerate() {
            l[e] = q[i];
        }
        l
    }
    fn fix(&self, l: &[u8]) -> Vec<u8> {
        let mut h = vec![0u8; self.gr.sites];
        for &e in &self.gr.tree {
            let (t, hd) = self.gr.edges[e];
            h[hd] = self.g.m(h[t], l[e]);
        }
        self.gr.free.iter().map(|&e| self.g.m(self.g.m(h[self.gr.edges[e].0], l[e]), self.g.i(h[self.gr.edges[e].1]))).collect()
    }
    fn code(q: &[u8]) -> u64 {
        q.iter().rev().fold(0u64, |a, &v| a * 6 + u64::from(v))
    }
    fn conjugates(&self, q: &[u8]) -> Vec<u64> {
        (0..6u8).map(|c| Self::code(&q.iter().map(|&x| self.g.m(self.g.m(c, x), self.g.i(c))).collect::<Vec<u8>>())).collect()
    }
    fn key(&self, q: &[u8]) -> u64 {
        self.conjugates(q).into_iter().min().unwrap_or(0)
    }
    /// chi_std of the rectangle on rows 0..1, columns x0..x1 (counter-clockwise from (x0, 0))
    fn wilson(&self, l: &[u8], x0: usize, x1: usize) -> i64 {
        let gr = self.gr;
        let mut u = 0u8;
        for x in x0..x1 {
            u = self.g.m(u, l[gr.hid[x]]);
        }
        u = self.g.m(u, l[gr.vid[x1]]);
        for x in (x0..x1).rev() {
            u = self.g.m(u, self.g.i(l[gr.hid[gr.cols + x]]));
        }
        u = self.g.m(u, self.g.i(l[gr.vid[x0]]));
        chi_std(u)
    }
    fn magnetic(&self, l: &[u8]) -> i64 {
        self.gr.plaq.iter().map(|p| 2 - chi_std(self.g.m(self.g.m(self.g.m(l[p[0]], l[p[1]]), self.g.i(l[p[2]])), self.g.i(l[p[3]])))).sum()
    }
}

type Sparse = Vec<BTreeMap<usize, i64>>;

fn spmul(a: &Sparse, b: &Sparse) -> Sparse {
    a.iter()
        .map(|row| {
            let mut out: BTreeMap<usize, i64> = BTreeMap::new();
            for (&k, &x) in row {
                for (&j, &y) in &b[k] {
                    *out.entry(j).or_insert(0) += x * y;
                }
            }
            out.retain(|_, v| *v != 0);
            out
        })
        .collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let parsed: Option<Vec<usize>> = args.get(1..6).map(|s| s.iter().filter_map(|x| x.parse().ok()).collect());
    let (Some(p), Some(out)) = (parsed.filter(|p| p.len() == 5), args.get(6)) else {
        eprintln!("usage: ymconf ROWS COLS XA XB CH OUT_MATRIX [JB LAM]");
        std::process::exit(1);
    };
    let (rows, cols, xa, xb, ch) = (p[0], p[1], p[2], p[3], p[4]);
    let wl: Option<(i64, i64)> = match (args.get(7).and_then(|v| v.parse().ok()), args.get(8).and_then(|v| v.parse().ok())) {
        (Some(a), Some(b)) => Some((a, b)),
        _ => None,
    };
    let wilson_ok = ch == 2 && xa < xb && xb < cols && wl.is_some_and(|(jb, _)| jb >= 0);
    if !(2..=3).contains(&rows) || !(2..=5).contains(&cols) || ch > 2 || (ch == 1 && !(xa < xb && xb < cols)) || (ch == 0 && (xa | xb) != 0) || (ch == 2 && !wilson_ok) {
        eprintln!("CONF_MATRIX|result=FAIL|reason=geometry_out_of_range|json=0");
        std::process::exit(1);
    }
    let g = G::new();
    let gr = graph(rows, cols, if ch == 1 { Some((xa, xb)) } else { None });
    let ch_label = ch;
    let sys = Sys { g: &g, gr: &gr };
    let nf = gr.free.len();
    let total = 6u64.pow(nf as u32);
    // orbit representatives: configurations whose code is the minimum over the 6 conjugations
    let mut reps: Vec<Vec<u8>> = Vec::new();
    let mut weights: Vec<i64> = Vec::new();
    for c in 0..total {
        let q: Vec<u8> = (0..nf).map(|i| ((c / 6u64.pow(i as u32)) % 6) as u8).collect();
        let conj = sys.conjugates(&q);
        if conj.iter().min() == Some(&c) {
            let mut s = conj.clone();
            s.sort_unstable();
            s.dedup();
            weights.push(s.len() as i64);
            reps.push(q);
        }
    }
    let n = reps.len();
    let index: HashMap<u64, usize> = reps.iter().enumerate().map(|(i, q)| (Sys::code(q), i)).collect();
    let move_matrix = |links: &[usize]| -> Sparse {
        reps.iter()
            .map(|q| {
                let raw = sys.raw(q);
                let mut row: BTreeMap<usize, i64> = BTreeMap::new();
                *row.entry(index[&Sys::code(q)]).or_insert(0) += 3 * links.len() as i64;
                for &e in links {
                    for &t in &TRANS {
                        let mut l = raw.clone();
                        l[e] = g.m(t, l[e]);
                        let j = index[&sys.key(&sys.fix(&l))];
                        *row.entry(j).or_insert(0) -= 1;
                    }
                }
                row.retain(|_, v| *v != 0);
                row
            })
            .collect()
    };
    let lattice: Vec<usize> = (0..gr.lattice_links).collect();
    let mut z = move_matrix(&lattice);
    if let Some(l) = gr.aux {
        let el = move_matrix(&[l]);
        let el2 = spmul(&el, &el);
        for i in 0..n {
            let mut add: BTreeMap<usize, i64> = BTreeMap::new();
            for (&j, &v) in &el2[i] {
                *add.entry(j).or_insert(0) += v;
            }
            for (&j, &v) in &el[i] {
                *add.entry(j).or_insert(0) -= 6 * v;
            }
            *add.entry(i).or_insert(0) += 9;
            for (j, v) in add {
                *z[i].entry(j).or_insert(0) += PENALTY * v;
            }
            z[i].retain(|_, v| *v != 0);
        }
    }
    let mags: Vec<i64> = match (ch, wl) {
        (2, Some((jb, lam))) => reps.iter().map(|q| {
            let raw = sys.raw(q);
            jb * sys.magnetic(&raw) + lam * sys.wilson(&raw, xa, xb)
        }).collect(),
        _ => reps.iter().map(|q| sys.magnetic(&sys.raw(q))).collect(),
    };
    let mut adjoint = true;
    for i in 0..n {
        for (&j, &v) in &z[i] {
            adjoint &= weights[i] * v == weights[j] * z[j].get(&i).copied().unwrap_or(0);
        }
    }
    let join = |v: &[i64]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(" ");
    let mut text = format!("{n}\n{}\n{}\n", join(&weights), join(&mags));
    let mut entries = 0usize;
    for (i, row) in z.iter().enumerate() {
        for (&j, &v) in row.range(i..) {
            text.push_str(&format!("{i} {j} {v}\n"));
            entries += 1;
        }
    }
    let ok = adjoint && std::fs::File::create(out).and_then(|mut f| f.write_all(text.as_bytes())).is_ok();
    println!(
        "CONF_MATRIX|rows={rows}|cols={cols}|charge_row={}|xa={xa}|xb={xb}|charged={ch}|{}lattice_links={}|plaquettes={}|free_links={nf}|configurations={total}|states={n}|upper_entries={entries}|penalty={}|w_self_adjoint={}|json=0",
        (rows - 1) / 2,
        wl.filter(|_| ch == 2).map_or(String::new(), |(jb, lam)| format!("wilson_loop=1x{}|diag=JB*M+LAM*W|JB={jb}|LAM={lam}|", xb - xa)),
        gr.lattice_links,
        gr.plaq.len(),
        if ch_label == 1 { PENALTY } else { 0 },
        if adjoint { "PASS" } else { "FAIL" }
    );
    std::process::exit(if ok { 0 } else { 2 });
}
