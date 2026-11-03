//! Adversarial hunt on real link configurations for a ratio below the claimed t or a move that breaks the local rule.
//!
//!   hunt LX LY R_NUM R_DEN GFILE CLAIM_MICRO SEED SECONDS THREADS [sabotage] > out
//!
//! Every visited state is checked against the constraints, and audited states are recomputed from the definition of H.
//! Sabotage names: none, swap_rule, planar_adj, dent, wrong_m, nonzero_flat.
//! Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use review::{adj_limit, ceil_two_root, micro, pattern_of, ratio_from_definition, El, Group, Rng, Torus, Vector, NPAT, RULE};
use std::collections::{HashMap, HashSet};
use std::time::Instant;

const SCALE: i64 = 1_000_000;

type RuleTable = Vec<Vec<(i32, i32, u32)>>;
type BestRow = (i128, Vec<El>, [i32; NPAT]);

struct Cfg {
    lx: u32,
    ly: u32,
    r_num: i128,
    r_den: i128,
    claim: i128,
    rule: RuleTable,
    planar: bool,
    v: Vector,
    lumps: Vec<(u32, u32)>,
    idx: HashMap<(u32, u32), usize>,
    /// Exact per-pattern weights in units of 1 / d, and the same to micro units for the fast path.
    w: Vec<[Option<i128>; NPAT]>,
    wm: Vec<[i64; NPAT]>,
    m_of: Vec<i64>,
}

impl Cfg {
    fn adj(&self, s: u32) -> u32 {
        if self.planar {
            2 * s - ceil_two_root(s)
        } else {
            adj_limit(s, self.lx, self.ly)
        }
    }

    fn rm_micro(&self, i: usize) -> i64 {
        let rm = self.r_num * i128::from(self.m_of[i]) * i128::from(SCALE) / self.r_den;
        rm as i64
    }

    /// The fast objective in micro units, floor per pattern, so within about 100 micro of the exact value.
    #[inline]
    fn fast(&self, i: usize, n: &[i32; NPAT], rm: &[i64]) -> i64 {
        let mut s = rm[i];
        for (p, c) in n.iter().enumerate() {
            s += i64::from(*c) * self.wm[i][p];
        }
        s
    }

    /// Exact (num, den) by the rule table.
    fn exact(&self, i: usize, n: &[i32; NPAT]) -> (i128, i128) {
        let (a, b) = self.lumps[i];
        let d = self.v.d(a, b);
        let mut s: i128 = 0;
        for (p, c) in n.iter().enumerate() {
            if *c != 0 {
                let w = self.w[i][p].expect("a real pattern at this lump must have its moves inside the lumps");
                s += i128::from(*c) * w;
            }
        }
        (self.r_num * i128::from(self.m_of[i]) * d + self.r_den * s, self.r_den * d)
    }
}

struct St {
    u: Vec<El>,
    cls: Vec<u8>,
    pat: Vec<u8>,
    n: [i32; NPAT],
    a: u32,
    b: u32,
}

struct Near {
    /// The distinct links of the two plaquettes of each link.
    aff: Vec<Vec<usize>>,
}

impl Near {
    fn new(t: &Torus) -> Near {
        let mut plaq_links = vec![Vec::new(); t.sites];
        for l in 0..t.nl {
            for &p in &t.link_plaq[l] {
                plaq_links[p].push(l);
            }
        }
        let mut aff = Vec::with_capacity(t.nl);
        for l in 0..t.nl {
            let mut v: Vec<usize> = Vec::new();
            for &p in &t.link_plaq[l] {
                for &k in &plaq_links[p] {
                    if !v.contains(&k) {
                        v.push(k);
                    }
                }
            }
            aff.push(v);
        }
        Near { aff }
    }
}

impl St {
    fn build(t: &Torus, g: &Group, u: Vec<El>) -> St {
        let mut cls = vec![0u8; t.sites];
        let (mut a, mut b) = (0u32, 0u32);
        for (p, c) in cls.iter_mut().enumerate() {
            *c = g.class[t.hol(g, &u, p) as usize];
            match *c {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        let mut pat = vec![0u8; t.nl];
        let mut n = [0i32; NPAT];
        for (l, q) in pat.iter_mut().enumerate() {
            let (x, y) = t.frame(g, &u, l);
            let z = pattern_of(g, x, y);
            *q = z as u8;
            n[z] += 1;
        }
        St { u, cls, pat, n, a, b }
    }

    #[inline]
    fn set(&mut self, t: &Torus, g: &Group, near: &Near, l: usize, e: El) {
        self.u[l] = e;
        for &p in &t.link_plaq[l] {
            let c = g.class[t.hol(g, &self.u, p) as usize];
            let old = self.cls[p];
            if c != old {
                match old {
                    1 => self.a -= 1,
                    2 => self.b -= 1,
                    _ => {}
                }
                match c {
                    1 => self.a += 1,
                    2 => self.b += 1,
                    _ => {}
                }
                self.cls[p] = c;
            }
        }
        for &k in &near.aff[l] {
            let (x, y) = t.frame(g, &self.u, k);
            let z = pattern_of(g, x, y) as u8;
            let o = self.pat[k];
            if z != o {
                self.n[o as usize] -= 1;
                self.n[z as usize] += 1;
                self.pat[k] = z;
            }
        }
    }
}

/// Prescribes the holonomy of every plaquette but the root by a dual spanning tree, on top of a base configuration.
struct Dual {
    /// In BFS order from the root: (plaquette, parent link).
    order: Vec<(usize, usize)>,
}

impl Dual {
    fn new(t: &Torus, root: usize) -> Dual {
        let mut seen = vec![false; t.sites];
        seen[root] = true;
        let mut queue = vec![root];
        let mut order = Vec::new();
        let mut head = 0;
        while head < queue.len() {
            let q = queue[head];
            head += 1;
            for l in 0..t.nl {
                let [p0, p1] = t.link_plaq[l];
                let other = if p0 == q {
                    p1
                } else if p1 == q {
                    p0
                } else {
                    continue;
                };
                if !seen[other] {
                    seen[other] = true;
                    queue.push(other);
                    order.push((other, l));
                }
            }
        }
        Dual { order }
    }

    fn impose(&self, t: &Torus, g: &Group, u: &mut [El], target: &[El]) {
        for &(p, l) in self.order.iter().rev() {
            let side = usize::from(t.link_plaq[l][0] != p);
            let mut w: El = review::ID;
            for &(k, inv) in &t.staple[l][side] {
                let e = if inv { g.i(u[k]) } else { u[k] };
                w = g.m(w, e);
            }
            // U_l W = target in the frame of l.
            u[l] = g.m(target[p], g.i(w));
        }
    }
}

const THREE: [El; 2] = [1, 2];

fn pick(g: &Group, rng: &mut Rng, class: u8, policy: u64, fixed_t: El, fixed_c: El) -> El {
    match class {
        0 => review::ID,
        1 => {
            if policy == 0 {
                fixed_t
            } else {
                g.trans[rng.below(3) as usize]
            }
        }
        _ => {
            if policy == 0 {
                fixed_c
            } else {
                THREE[rng.below(2) as usize]
            }
        }
    }
}

/// One structured class pattern on the plaquettes.
fn family(t: &Torus, rng: &mut Rng, id: u64) -> Vec<u8> {
    let (lx, ly) = (t.lx, t.ly);
    let mut c = vec![0u8; t.sites];
    let at = |x: usize, y: usize| (x % lx) + lx * (y % ly);
    let kind = 1 + rng.below(2) as u8;
    let other = 3 - kind;
    match id {
        0 => {
            // A block of one kind.
            let (w, h) = (1 + rng.below(lx as u64) as usize, 1 + rng.below(ly as u64) as usize);
            for y in 0..h {
                for x in 0..w {
                    c[at(x, y)] = kind;
                }
            }
        }
        1 => {
            // Two blocks, of two kinds, touching.
            let (w, h) = (1 + rng.below(lx as u64) as usize, 1 + rng.below(ly as u64) as usize);
            for y in 0..h {
                for x in 0..w {
                    c[at(x, y)] = if x * 2 < w { kind } else { other };
                }
            }
        }
        2 => {
            // Stripes along an axis, of some width and period.
            let width = 1 + rng.below(ly as u64) as usize;
            for y in 0..width {
                for x in 0..lx {
                    c[at(x, y)] = kind;
                }
            }
        }
        3 => {
            let width = 1 + rng.below(lx as u64) as usize;
            for x in 0..width {
                for y in 0..ly {
                    c[at(x, y)] = kind;
                }
            }
        }
        4 => {
            // A checkerboard of kind and empty.
            for y in 0..ly {
                for x in 0..lx {
                    if (x + y) % 2 == 0 {
                        c[at(x, y)] = kind;
                    }
                }
            }
        }
        5 => {
            // A checkerboard of the two kinds.
            for y in 0..ly {
                for x in 0..lx {
                    c[at(x, y)] = if (x + y) % 2 == 0 { kind } else { other };
                }
            }
        }
        6 => {
            // The whole lattice of one kind.
            c.fill(kind);
        }
        7 => {
            // The whole lattice of random kinds.
            for v in &mut c {
                *v = 1 + rng.below(2) as u8;
            }
        }
        8 => {
            // Everything but a hole.
            c.fill(kind);
            let (w, h) = (1 + rng.below(lx as u64) as usize, 1 + rng.below(ly as u64) as usize);
            for y in 0..h {
                for x in 0..w {
                    c[at(x, y)] = 0;
                }
            }
        }
        9 => {
            // Rows of alternating kinds.
            let period = 2 + rng.below(2) as usize;
            for y in 0..ly {
                for x in 0..lx {
                    c[at(x, y)] = if y % period == 0 { kind } else { other };
                }
            }
        }
        10 => {
            // Diagonal stripes.
            let period = 2 + rng.below(3) as usize;
            for y in 0..ly {
                for x in 0..lx {
                    if (x + y) % period == 0 {
                        c[at(x, y)] = kind;
                    }
                }
            }
        }
        11 => {
            // A short snake of one kind.
            let len = 1 + rng.below(t.sites as u64) as usize;
            let (mut x, mut y) = (0usize, 0usize);
            for _ in 0..len {
                c[at(x, y)] = kind;
                if rng.below(2) == 0 {
                    x += 1;
                } else {
                    y += 1;
                }
            }
        }
        _ => {
            // Random density.
            let den = 1 + rng.below(8);
            for v in &mut c {
                if rng.below(8) < den {
                    *v = 1 + rng.below(2) as u8;
                }
            }
        }
    }
    c
}

struct Tally {
    visited: u64,
    audited: u64,
    audit_mismatch: u64,
    out_of_table: u64,
    below_claim: u64,
    below_claim_first: Option<Vec<El>>,
    outside_first: Option<(u32, u32, [i32; NPAT])>,
    /// Per lump: best exact ratio in micro units, and its configuration.
    best: Vec<Option<BestRow>>,
    signatures: HashSet<(u32, u32, [i32; NPAT])>,
    family_best: HashMap<u64, i128>,
}

impl Tally {
    fn new(n: usize) -> Tally {
        Tally {
            visited: 0,
            audited: 0,
            audit_mismatch: 0,
            out_of_table: 0,
            below_claim: 0,
            below_claim_first: None,
            outside_first: None,
            best: vec![None; n],
            signatures: HashSet::new(),
            family_best: HashMap::new(),
        }
    }
}

/// Checks one configuration from the definition: every move's lump is recomputed in full and compared with the rule applied to the frame patterns.
fn audit(t: &Torus, g: &Group, cfg: &Cfg, s: &mut St, tally: &mut Tally) {
    tally.audited += 1;
    let (a, b) = (s.a, s.b);
    let mut predicted: HashMap<(u32, u32), u32> = HashMap::new();
    for l in 0..t.nl {
        let pat = s.pat[l] as usize;
        for &(da, db, c) in &cfg.rule[pat] {
            let key = (a.wrapping_add_signed(da), b.wrapping_add_signed(db));
            *predicted.entry(key).or_insert(0) += c;
        }
    }
    let mut copy = s.u.clone();
    let (num, den, lump, hist) = ratio_from_definition(t, g, &mut copy, &cfg.v, cfg.r_num, cfg.r_den);
    if lump != (a, b) || hist != predicted {
        tally.audit_mismatch += 1;
    }
    if let Some(i) = cfg.idx.get(&(a, b)) {
        let (n2, d2) = cfg.exact(*i, &s.n);
        if d2 != den || n2 != num {
            tally.audit_mismatch += 1;
        }
    }
}

fn check_state(cfg: &Cfg, s: &St, tally: &mut Tally) -> bool {
    let (a, b) = (s.a, s.b);
    let tt = (s.n[3] + s.n[4]) as u32;
    let cc = s.n[6] as u32;
    let inner = tt + s.n[5] as u32 + cc;
    let ok = a % 2 == 0
        && 4 * a as i32 == s.n[1] + s.n[5] + 2 * (s.n[3] + s.n[4])
        && 4 * b as i32 == s.n[2] + s.n[5] + 2 * s.n[6]
        && tt <= cfg.adj(a)
        && cc <= cfg.adj(b)
        && inner <= cfg.adj(a + b);
    if !ok {
        tally.out_of_table += 1;
        if tally.outside_first.is_none() {
            tally.outside_first = Some((a, b, s.n));
        }
    }
    ok
}

fn record(cfg: &Cfg, s: &St, i: usize, fam: u64, tally: &mut Tally) {
    let (num, den) = cfg.exact(i, &s.n);
    let m = micro(num, den);
    let better = match &tally.best[i] {
        None => true,
        Some((b, _, _)) => m < *b,
    };
    if better {
        tally.best[i] = Some((m, s.u.clone(), s.n));
    }
    let e = tally.family_best.entry(fam).or_insert(m);
    if m < *e {
        *e = m;
    }
    if num * 1_000_000 < cfg.claim * den {
        tally.below_claim += 1;
        if tally.below_claim_first.is_none() {
            tally.below_claim_first = Some(s.u.clone());
        }
    }
}

struct Plan {
    /// Target lump index or None for a free descent on the ratio.
    target: Option<usize>,
    t0: i64,
    steps: u64,
}

#[allow(clippy::too_many_arguments)]
fn anneal(t: &Torus, g: &Group, near: &Near, cfg: &Cfg, rm: &[i64], rng: &mut Rng, s: &mut St, plan: &Plan, fam: u64, tally: &mut Tally) {
    let nl = t.nl as u64;
    let penalty: i64 = 40 * SCALE;
    let target = plan.target.map(|i| cfg.lumps[i]);
    let score = |s: &St| -> Option<i64> {
        let i = *cfg.idx.get(&(s.a, s.b))?;
        if s.a == 0 && s.b == 0 {
            return None;
        }
        let mut v = cfg.fast(i, &s.n, rm);
        if let Some((a0, b0)) = target {
            v += penalty * i64::from(s.a.abs_diff(a0) / 2 + s.b.abs_diff(b0));
        }
        Some(v)
    };
    let mut cur = score(s);
    let mut best_seen = i64::MAX;
    for k in 0..plan.steps {
        let temp = plan.t0 - plan.t0 * (k as i64) / (plan.steps as i64) + 1;
        let l = rng.below(nl) as usize;
        let keep = s.u[l];
        let mult = 1 + rng.below(5) as u8;
        let e = g.m(mult, keep);
        s.set(t, g, near, l, e);
        let new = score(s);
        let accept = match (cur, new) {
            (_, None) => false,
            (None, Some(_)) => true,
            (Some(c), Some(n)) => {
                let tz = i64::from(rng.step().trailing_zeros());
                n - c <= temp * tz
            }
        };
        if accept {
            cur = new;
            tally.visited += 1;
            check_state(cfg, s, tally);
            let i = cfg.idx[&(s.a, s.b)];
            let f = cfg.fast(i, &s.n, rm);
            let lumpbest = tally.best[i].as_ref().map_or(i128::MAX, |x| x.0);
            if i128::from(f) <= lumpbest.saturating_add(500) {
                record(cfg, s, i, fam, tally);
            }
            if f < best_seen {
                best_seen = f;
            }
            if tally.signatures.len() < 2_000_000 {
                tally.signatures.insert((s.a, s.b, s.n));
            }
            if k & 0xFFFF == 0 {
                audit(t, g, cfg, s, tally);
            }
        } else {
            s.set(t, g, near, l, keep);
        }
    }
}

fn worker(lx: usize, ly: usize, cfg: &Cfg, seed: u64, millis: u128) -> Tally {
    let t = Torus::new(lx, ly);
    let g = Group::new();
    let near = Near::new(&t);
    let rm: Vec<i64> = (0..cfg.lumps.len()).map(|i| cfg.rm_micro(i)).collect();
    let mut rng = Rng(seed | 1);
    let dual: Vec<Dual> = vec![Dual::new(&t, 0)];
    let mut tally = Tally::new(cfg.lumps.len());
    let start = Instant::now();
    let mut round = 0u64;
    while start.elapsed().as_millis() < millis {
        round += 1;
        let fam = rng.below(13);
        let classes = family(&t, &mut rng, fam);
        let mut u = vec![0u8; t.nl];
        match rng.below(3) {
            0 => {
                for e in &mut u {
                    *e = rng.below(6) as u8;
                }
            }
            1 => {
                // Identity, with a torus holonomy pair on one cut each.
                let (hx, hy) = (rng.below(6) as u8, rng.below(6) as u8);
                for y in 0..ly {
                    u[2 * ((lx - 1) + lx * y)] = hx;
                }
                for x in 0..lx {
                    u[2 * (x + lx * (ly - 1)) + 1] = hy;
                }
            }
            _ => {}
        }
        let policy = rng.below(2);
        let (ft, fc) = (g.trans[rng.below(3) as usize], THREE[rng.below(2) as usize]);
        let target: Vec<El> = classes.iter().map(|&c| pick(&g, &mut rng, c, policy, ft, fc)).collect();
        dual[0].impose(&t, &g, &mut u, &target);
        let mut s = St::build(&t, &g, u);
        if s.a == 0 && s.b == 0 {
            // A flat start: walk off it.
            for _ in 0..1 + rng.below(4) {
                let l = rng.below(t.nl as u64) as usize;
                let e = g.m(g.trans[rng.below(3) as usize], s.u[l]);
                s.set(&t, &g, &near, l, e);
            }
        }
        if s.a == 0 && s.b == 0 {
            continue;
        }
        if let Some(i) = cfg.idx.get(&(s.a, s.b)).copied() {
            tally.visited += 1;
            check_state(cfg, &s, &mut tally);
            record(cfg, &s, i, fam, &mut tally);
            audit(&t, &g, cfg, &mut s, &mut tally);
        }
        // Half the rounds free on the ratio, half pinned near a lump, in turn over the lumps.
        let target = if round % 2 == 0 {
            None
        } else {
            let i = (round / 2) as usize % cfg.lumps.len();
            if cfg.lumps[i] == (0, 0) {
                None
            } else {
                Some(i)
            }
        };
        let steps = 40_000 + rng.below(200_000);
        let t0 = (SCALE / 2) * (1 + rng.below(16) as i64);
        anneal(&t, &g, &near, cfg, &rm, &mut rng, &mut s, &Plan { target, t0, steps }, fam, &mut tally);
    }
    tally
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (lx, ly): (usize, usize) = (args[1].parse().expect("lx"), args[2].parse().expect("ly"));
    let (r_num, r_den): (i128, i128) = (args[3].parse().expect("r"), args[4].parse().expect("r"));
    let gfile = args[5].clone();
    let claim: i128 = args[6].parse().expect("claim");
    let seed: u64 = args[7].parse().expect("seed");
    let secs: u128 = args[8].parse().expect("secs");
    let threads: u64 = args[9].parse().expect("threads");
    let sabotage = args.get(10).cloned().unwrap_or_else(|| "none".to_string());
    assert!(threads <= 3, "at most 3 threads by the brief");
    let p = (lx * ly) as u32;
    let nl = 2 * p;
    let mut v = Vector::load(&gfile);
    let mut rule: RuleTable = RULE.iter().map(|r| r.to_vec()).collect();
    if sabotage == "swap_rule" {
        rule[3] = vec![(-2, 0, 2), (-2, 2, 1)];
    }
    if sabotage == "dent" {
        // A real lump's value lowered by a factor, so its upward neighbours gain.
        let x = v.g[&(0, 3)];
        v.g.insert((0, 3), x / 1000);
    }
    if sabotage == "nonzero_flat" {
        let x = v.g[&(2, 0)];
        v.g.insert((0, 0), x * 1000);
    }
    let mut lumps = Vec::new();
    for a in (0..=p).step_by(2) {
        for b in 0..=(p - a) {
            lumps.push((a, b));
        }
    }
    let mut idx = HashMap::new();
    for (i, l) in lumps.iter().enumerate() {
        idx.insert(*l, i);
    }
    let mut w: Vec<[Option<i128>; NPAT]> = Vec::with_capacity(lumps.len());
    let mut wm: Vec<[i64; NPAT]> = Vec::with_capacity(lumps.len());
    let mut m_of: Vec<i64> = Vec::with_capacity(lumps.len());
    for &(a, b) in &lumps {
        let mut row = [None; NPAT];
        let mut rowm = [0i64; NPAT];
        let d = v.d(a, b);
        if d > 0 {
            for (pat, moves) in rule.iter().enumerate() {
                let mut sum: Option<i128> = Some(0);
                for &(da, db, c) in moves {
                    let (ta, tb) = (i64::from(a) + i64::from(da), i64::from(b) + i64::from(db));
                    let d2 = if ta < 0 || tb < 0 {
                        None
                    } else {
                        v.g.get(&(ta as u32, tb as u32)).copied()
                    };
                    sum = match (sum, d2) {
                        (Some(s), Some(x)) => Some(s + i128::from(c) * (d - x)),
                        _ => None,
                    };
                }
                row[pat] = sum;
                if let Some(s) = sum {
                    rowm[pat] = micro(s, d) as i64;
                }
            }
        }
        w.push(row);
        wm.push(rowm);
        m_of.push(if sabotage == "wrong_m" { i64::from(2 * a + 2 * b) } else { i64::from(2 * a + 3 * b) });
    }
    let cfg = Cfg {
        lx: lx as u32,
        ly: ly as u32,
        r_num,
        r_den,
        claim,
        rule,
        planar: sabotage == "planar_adj",
        v,
        lumps,
        idx,
        w,
        wm,
        m_of,
    };
    println!("HUNT_START|Lx={lx}|Ly={ly}|nl={nl}|r={r_num}/{r_den}|file={gfile}|claim_micro={claim}|seed={seed}|seconds={secs}|threads={threads}|sabotage={sabotage}|json=0");
    let start = Instant::now();
    let mut tallies: Vec<Tally> = Vec::new();
    std::thread::scope(|sc| {
        let cfg_ref = &cfg;
        let mut hs = Vec::new();
        for th in 0..threads {
            let sd = seed.wrapping_mul(0x1000_0000_01B3).wrapping_add(th.wrapping_mul(0x9E37_79B9_7F4A_7C15)) | 1;
            hs.push(sc.spawn(move || worker(lx, ly, cfg_ref, sd, secs * 1000)));
        }
        for h in hs {
            tallies.push(h.join().expect("worker"));
        }
    });
    let mut all = Tally::new(cfg.lumps.len());
    for t in tallies {
        all.visited += t.visited;
        all.audited += t.audited;
        all.audit_mismatch += t.audit_mismatch;
        all.out_of_table += t.out_of_table;
        all.below_claim += t.below_claim;
        if all.below_claim_first.is_none() {
            all.below_claim_first = t.below_claim_first;
        }
        if all.outside_first.is_none() {
            all.outside_first = t.outside_first;
        }
        for (i, b) in t.best.into_iter().enumerate() {
            if let Some(x) = b {
                let better = match &all.best[i] {
                    None => true,
                    Some(y) => x.0 < y.0,
                };
                if better {
                    all.best[i] = Some(x);
                }
            }
        }
        all.signatures.extend(t.signatures);
        for (k, v2) in t.family_best {
            let e = all.family_best.entry(k).or_insert(v2);
            if v2 < *e {
                *e = v2;
            }
        }
    }
    let reached = all.best.iter().filter(|x| x.is_some()).count();
    let mut low: Vec<(i128, usize)> = all.best.iter().enumerate().filter_map(|(i, x)| x.as_ref().map(|y| (y.0, i))).collect();
    low.sort_unstable();
    let lowest = low.first().map_or(-1, |x| x.0);
    println!(
        "HUNT_RESULT|visited={}|audited={}|audit_mismatch={}|out_of_table={}|below_claim={}|lumps_reached={}/{}|signatures={}|lowest_real_micro={}|claim_micro={}|margin_micro={}|seconds={}|json=0",
        all.visited,
        all.audited,
        all.audit_mismatch,
        all.out_of_table,
        all.below_claim,
        reached,
        cfg.lumps.len() - 1,
        all.signatures.len(),
        lowest,
        claim,
        lowest - claim,
        start.elapsed().as_secs()
    );
    let mut fams: Vec<(&u64, &i128)> = all.family_best.iter().collect();
    fams.sort();
    for (k, v2) in fams {
        println!("FAMILY_BEST|family={k}|micro={v2}|json=0");
    }
    for (m, i) in low.iter().take(16) {
        let (a, b) = cfg.lumps[*i];
        let x = all.best[*i].as_ref().expect("reached");
        let config: String = x.1.iter().map(|e| char::from(b'0' + *e)).collect();
        println!("LOW|a={a}|b={b}|micro={m}|n={:?}|config={config}|json=0", x.2);
    }
    for (i, x) in all.best.iter().enumerate() {
        if let Some(y) = x {
            let (a, b) = cfg.lumps[i];
            println!("LUMPBEST|a={a}|b={b}|micro={}|n={:?}|json=0", y.0, y.2);
        }
    }
    if let Some((a, b, n)) = all.outside_first {
        println!("FIRST_OUTSIDE|a={a}|b={b}|n={n:?}|json=0");
    }
    if let Some(c) = all.below_claim_first {
        let config: String = c.iter().map(|e| char::from(b'0' + *e)).collect();
        println!("FIRST_BELOW|config={config}|json=0");
    }
    let red = all.audit_mismatch + all.out_of_table + all.below_claim;
    println!("HUNT_VERDICT|red={}|verdict={}|sabotage={sabotage}|json=0", red, if red == 0 { "CLEAN" } else { "RED" });
    if red != 0 {
        std::process::exit(2);
    }
}
