//! Rigorous Rayleigh-Ritz from above on the gauge-invariant space, in the sector of functions invariant under all lattice symmetries.
//!
//!   ritz LX LY R MCUT SWEEPS THREADS OUT_PREFIX [sabotage]
//!
//! The space: every gauge orbit reached from the M = 3 band by single-link moves that stay at 0 < M <= MCUT. Flats get psi = 0.
//! psi is any positive integer vector on it, so A/B is an upper bound on lambda_1(H'), and with the 8 flat states and psi as a 9-dimensional test
//! space, E_9 <= the top eigenvalue of [[3 nl I, c], [c^T, A/B]], where |c|^2 = C/B. A, B, C are printed in full; py_ritz_bound.py turns them into micro bounds.
//! With no truncation at all, the same vector also gives Barta's lower bound on lambda_1(H').
//! Sabotage names: none, unit_weight, wrong_m. Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use review::{adj_limit, cost_of_class, micro, ratio_from_definition, El, Group, Rng, Torus, Vector, ID, NPAT, RULE};
use std::collections::HashMap;
use std::hash::{BuildHasherDefault, Hasher};
use std::time::Instant;

#[derive(Default)]
struct KeyHasher(u64);

impl Hasher for KeyHasher {
    fn finish(&self) -> u64 {
        self.0
    }
    fn write(&mut self, bytes: &[u8]) {
        for b in bytes {
            self.0 = (self.0 ^ u64::from(*b)).wrapping_mul(0x0000_0100_0000_01B3);
        }
    }
    fn write_u128(&mut self, v: u128) {
        let x = (v as u64) ^ ((v >> 64) as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F);
        self.0 = (x ^ (x >> 29)).wrapping_mul(0x9E37_79B9_7F4A_7C15);
    }
}

type KeyMap = HashMap<u128, u32, BuildHasherDefault<KeyHasher>>;

struct Aut {
    link: Vec<(u32, bool)>,
    plaq: Vec<u32>,
}

fn lattice_group(t: &Torus) -> Vec<Aut> {
    let (lx, ly) = (t.lx, t.ly);
    let swaps: &[bool] = if lx == ly { &[false, true] } else { &[false] };
    let mut out = Vec::new();
    for &sw in swaps {
        for sx in [false, true] {
            for sy in [false, true] {
                for tx in 0..lx {
                    for ty in 0..ly {
                        let mut link = vec![(0u32, false); t.nl];
                        let mut plaq = vec![0u32; t.sites];
                        let place = |x: usize, y: usize, d: usize| 2 * ((x % lx) + lx * (y % ly)) + d;
                        for y in 0..ly {
                            for x in 0..lx {
                                for d in 0..2usize {
                                    let (mut xx, mut yy, mut dd, mut inv) = (x, y, d, false);
                                    if sx {
                                        if dd == 0 {
                                            xx = (2 * lx - xx - 1) % lx;
                                            inv = !inv;
                                        } else {
                                            xx = (lx - xx) % lx;
                                        }
                                    }
                                    if sy {
                                        if dd == 1 {
                                            yy = (2 * ly - yy - 1) % ly;
                                            inv = !inv;
                                        } else {
                                            yy = (ly - yy) % ly;
                                        }
                                    }
                                    if sw {
                                        std::mem::swap(&mut xx, &mut yy);
                                        dd = 1 - dd;
                                    }
                                    xx += tx;
                                    yy += ty;
                                    link[place(x, y, d)] = (place(xx, yy, dd) as u32, inv);
                                }
                                let (mut xx, mut yy) = (x, y);
                                if sx {
                                    xx = (2 * lx - xx - 1) % lx;
                                }
                                if sy {
                                    yy = (2 * ly - yy - 1) % ly;
                                }
                                if sw {
                                    std::mem::swap(&mut xx, &mut yy);
                                }
                                plaq[(x % lx) + lx * (y % ly)] = (((xx + tx) % lx) + lx * ((yy + ty) % ly)) as u32;
                            }
                        }
                        out.push(Aut { link, plaq });
                    }
                }
            }
        }
    }
    out
}

struct Canon<'a> {
    t: &'a Torus,
    g: &'a Group,
    auts: &'a [Aut],
    free: &'a [usize],
    tree_order: &'a [(usize, usize, usize)],
}

struct Scratch {
    img: Vec<El>,
    pot: Vec<El>,
    cand: Vec<u32>,
    cls: Vec<u8>,
    gf: Vec<El>,
}

impl Canon<'_> {
    fn scratch(&self) -> Scratch {
        Scratch { img: vec![0; self.t.nl], pot: vec![0; self.t.sites], cand: Vec::with_capacity(self.auts.len()), cls: vec![0; self.t.sites], gf: vec![0; self.free.len()] }
    }

    /// Fixes the tree gauge and then conjugation, and returns the key with the size of the conjugation stabilizer.
    #[inline]
    fn gauge_key(&self, u: &[El], sc: &mut Scratch) -> (u128, u32) {
        let g = self.g;
        sc.pot[0] = ID;
        for &(l, parent, child) in self.tree_order {
            sc.pot[child] = g.m(sc.pot[parent], u[l]);
        }
        for (i, &l) in self.free.iter().enumerate() {
            let (s, d) = (self.t.src[l], self.t.dst[l]);
            sc.gf[i] = g.m(g.m(sc.pot[s], u[l]), g.i(sc.pot[d]));
        }
        // Lexicographic minimum over the six conjugates, pruning.
        let mut alive: u8 = 0b11_1111;
        for &e in sc.gf.iter() {
            let mut low = 9u8;
            let mut next = 0u8;
            for c in 0..6usize {
                if alive & (1 << c) != 0 {
                    let v = g.conj[c][e as usize];
                    match v.cmp(&low) {
                        std::cmp::Ordering::Less => {
                            low = v;
                            next = 1 << c;
                        }
                        std::cmp::Ordering::Equal => next |= 1 << c,
                        std::cmp::Ordering::Greater => {}
                    }
                }
            }
            alive = next;
            if alive & alive.wrapping_sub(1) == 0 {
                break;
            }
        }
        let c = alive.trailing_zeros() as usize;
        let mut key: u128 = 0;
        for &e in sc.gf.iter() {
            key = key * 6 + u128::from(g.conj[c][e as usize]);
        }
        (key, alive.count_ones())
    }

    /// Canonical key of a configuration under the gauge group and the lattice group, with the whole-space weight of its class:
    /// the number of gauge-fixed configurations it stands for.
    fn canon(&self, u: &[El], sc: &mut Scratch) -> (u128, u32) {
        let t = self.t;
        for p in 0..t.sites {
            sc.cls[p] = self.g.class[t.hol(self.g, u, p) as usize];
        }
        let mut low = u64::MAX;
        sc.cand.clear();
        for (i, a) in self.auts.iter().enumerate() {
            let mut pat: u64 = 0;
            for (p, c) in sc.cls.iter().enumerate() {
                pat |= u64::from(*c) << (2 * a.plaq[p]);
            }
            match pat.cmp(&low) {
                std::cmp::Ordering::Less => {
                    low = pat;
                    sc.cand.clear();
                    sc.cand.push(i as u32);
                }
                std::cmp::Ordering::Equal => sc.cand.push(i as u32),
                std::cmp::Ordering::Greater => {}
            }
        }
        let mut best = u128::MAX;
        let mut stab = 0u32;
        let mut cstab = 0u32;
        let cand = std::mem::take(&mut sc.cand);
        for &i in &cand {
            let a = &self.auts[i as usize];
            for (l, &(to, inv)) in a.link.iter().enumerate() {
                sc.img[to as usize] = if inv { self.g.i(u[l]) } else { u[l] };
            }
            let img = std::mem::take(&mut sc.img);
            let (k, c) = self.gauge_key(&img, sc);
            sc.img = img;
            match k.cmp(&best) {
                std::cmp::Ordering::Less => {
                    best = k;
                    stab = 1;
                    cstab = c;
                }
                std::cmp::Ordering::Equal => stab += 1,
                std::cmp::Ordering::Greater => {}
            }
        }
        sc.cand = cand;
        let group = self.auts.len() as u32;
        assert!(group % stab == 0);
        (best, (group / stab) * (6 / cstab))
    }

    fn decode(&self, key: u128, u: &mut [El]) {
        u.fill(ID);
        let mut k = key;
        for &l in self.free.iter().rev() {
            u[l] = (k % 6) as u8;
            k /= 6;
        }
    }
}

struct Model {
    keys: Vec<u128>,
    weight: Vec<u32>,
    m: Vec<u16>,
    offs: Vec<u64>,
    adj: Vec<u32>,
}

fn expand_one(c: &Canon, key: u128, cut: u32, u: &mut [El], sc: &mut Scratch) -> Vec<(u128, u32, u16)> {
    let (t, g) = (c.t, c.g);
    c.decode(key, u);
    let mut cost = vec![0u8; t.sites];
    let mut m: u32 = 0;
    for (p, q) in cost.iter_mut().enumerate() {
        *q = g.class[t.hol(g, u, p) as usize];
        m += cost_of_class(*q);
    }
    let mut row = Vec::with_capacity(3 * t.nl);
    for l in 0..t.nl {
        let keep = u[l];
        let [p0, p1] = t.link_plaq[l];
        let base = m - cost_of_class(cost[p0]) - cost_of_class(cost[p1]);
        for &s in &g.trans {
            u[l] = g.m(s, keep);
            let new_m = base + cost_of_class(g.class[t.hol(g, u, p0) as usize]) + cost_of_class(g.class[t.hol(g, u, p1) as usize]);
            if new_m == 0 || new_m > cut {
                continue;
            }
            let (k, w) = c.canon(u, sc);
            row.push((k, w, new_m as u16));
        }
        u[l] = keep;
    }
    row
}

fn build(c: &Canon, cut: u32, seeds: &[Vec<El>], threads: usize) -> Model {
    let mut sc = c.scratch();
    let mut map: KeyMap = KeyMap::default();
    let mut keys: Vec<u128> = Vec::new();
    let mut weight: Vec<u32> = Vec::new();
    let mut m: Vec<u16> = Vec::new();
    for s in seeds {
        let total: u32 = (0..c.t.sites).map(|p| cost_of_class(c.g.class[c.t.hol(c.g, s, p) as usize])).sum();
        if total == 0 || total > cut {
            continue;
        }
        let (k, w) = c.canon(s, &mut sc);
        map.entry(k).or_insert_with(|| {
            keys.push(k);
            weight.push(w);
            m.push(total as u16);
            (keys.len() - 1) as u32
        });
    }
    let mut offs: Vec<u64> = vec![0];
    let mut adj: Vec<u32> = Vec::new();
    let mut done = 0usize;
    const BATCH: usize = 1 << 13;
    let start = Instant::now();
    let mut last = 0u64;
    while done < keys.len() {
        let end = (done + BATCH * threads).min(keys.len());
        let batch: &[u128] = &keys[done..end];
        let chunk = batch.len().div_ceil(threads);
        let mut parts: Vec<Vec<Vec<(u128, u32, u16)>>> = Vec::new();
        std::thread::scope(|scope| {
            let mut hs = Vec::new();
            for part in batch.chunks(chunk) {
                hs.push(scope.spawn(move || {
                    let mut sc = c.scratch();
                    let mut u = vec![0u8; c.t.nl];
                    part.iter().map(|k| expand_one(c, *k, cut, &mut u, &mut sc)).collect::<Vec<_>>()
                }));
            }
            for h in hs {
                parts.push(h.join().expect("expand"));
            }
        });
        for part in parts {
            for row in part {
                for (k, w, mm) in row {
                    let i = *map.entry(k).or_insert_with(|| {
                        keys.push(k);
                        weight.push(w);
                        m.push(mm);
                        (keys.len() - 1) as u32
                    });
                    adj.push(i);
                }
                offs.push(adj.len() as u64);
            }
        }
        done = end;
        let secs = start.elapsed().as_secs();
        if secs >= last + 30 {
            last = secs;
            println!("BUILD_PROGRESS|done={done}|states={}|edges={}|seconds={secs}|json=0", keys.len(), adj.len());
        }
    }
    Model { keys, weight, m, offs, adj }
}

/// W_i N_ij = W_j N_ji on every pair, exactly.
fn self_adjoint(md: &mut Model) -> (u64, u64) {
    let n = md.keys.len();
    for i in 0..n {
        let (a, b) = (md.offs[i] as usize, md.offs[i + 1] as usize);
        md.adj[a..b].sort_unstable();
    }
    let (mut pairs, mut bad) = (0u64, 0u64);
    for i in 0..n {
        let (a, b) = (md.offs[i] as usize, md.offs[i + 1] as usize);
        let row = &md.adj[a..b];
        let mut k = 0;
        while k < row.len() {
            let j = row[k];
            let mut e = k;
            while e < row.len() && row[e] == j {
                e += 1;
            }
            let c = (e - k) as u64;
            let (a2, b2) = (md.offs[j as usize] as usize, md.offs[j as usize + 1] as usize);
            let other = &md.adj[a2..b2];
            let lo = other.partition_point(|x| *x < i as u32);
            let hi = other.partition_point(|x| *x <= i as u32);
            let c2 = (hi - lo) as u64;
            pairs += 1;
            if u64::from(md.weight[i]) * c != u64::from(md.weight[j as usize]) * c2 {
                bad += 1;
            }
            k = e;
        }
    }
    (pairs, bad)
}

/// Exhaustive low-M audit on real orbits: every state of the model, every move recomputed from the definition, checked against the rule and the constraints, with the exact ratio of a vector.
fn audit_low_m(t: &Torus, g: &Group, c: &Canon, md: &Model, path: &str, r: i128) {
    let v = Vector::load(path);
    let mut u = vec![0u8; t.nl];
    let (mut low, mut at, mut low_n) = (i128::MAX, (0u32, 0u32), [0u32; NPAT]);
    let (mut outside, mut rule_bad, mut odd, mut m_bad, mut configs) = (0u64, 0u64, 0u64, 0u64, 0u64);
    let (ul, uy) = (t.lx as u32, t.ly as u32);
    for i in 0..md.keys.len() {
        c.decode(md.keys[i], &mut u);
        configs += u64::from(md.weight[i]);
        let (num, den, (a, b), hist) = ratio_from_definition(t, g, &mut u, &v, r, 1);
        if 2 * a + 3 * b != u32::from(md.m[i]) {
            m_bad += 1;
        }
        if a % 2 != 0 {
            odd += 1;
        }
        let n = t.counts(g, &u);
        let mut predicted: HashMap<(u32, u32), u32> = HashMap::new();
        for (pat, count) in n.iter().enumerate() {
            if *count != 0 {
                for &(da, db, m) in RULE[pat] {
                    *predicted.entry((a.wrapping_add_signed(da), b.wrapping_add_signed(db))).or_insert(0) += m * *count;
                }
            }
        }
        if predicted != hist {
            rule_bad += 1;
        }
        let (tt, cc, inner) = (n[3] + n[4], n[6], n[3] + n[4] + n[5] + n[6]);
        if 4 * a != n[1] + n[5] + 2 * tt || 4 * b != n[2] + n[5] + 2 * cc || tt > adj_limit(a, ul, uy) || cc > adj_limit(b, ul, uy) || inner > adj_limit(a + b, ul, uy) {
            outside += 1;
        }
        let m = micro(num, den);
        if m < low {
            low = m;
            at = (a, b);
            low_n = n;
        }
    }
    println!("LOWM_AUDIT|Lx={}|Ly={}|r={r}|mcut_states={}|configs={configs}|m_bad={m_bad}|a_odd={odd}|rule_bad={rule_bad}|outside={outside}|min_ratio_micro={low}|at_a={}|at_b={}|n={low_n:?}|file={path}|json=0", t.lx, t.ly, md.keys.len(), at.0, at.1);
}

/// A lower bound outside the claim: d is the actual vector on every orbit with M <= cut and one value per lump above it.
/// Rows at M <= cut are exact. Rows above it are the signature rows of my table, with a move into a lump at M <= cut bounded by the largest d in that lump.
/// So the minimum ratio is a rigorous lower bound on lambda_1(H') when the model holds every non-flat orbit with M <= cut, which py_lump_counts.py checks.
#[allow(clippy::too_many_arguments, clippy::too_many_lines)]
fn hybrid(t: &Torus, g: &Group, c: &Canon, md: &Model, r: i64, cut: u32, targets: &[i128], sweeps: usize, threads: usize, start_psi: &[i64], dump: &str) {
    const U: i128 = 1_000_000;
    const TOP_BITS: u32 = 90;
    type Row = (u32, Vec<(u32, u32)>);
    let p = t.sites as u32;
    let mut lumps: Vec<(u32, u32)> = Vec::new();
    for a in (0..=p).step_by(2) {
        for b in 0..=(p - a) {
            lumps.push((a, b));
        }
    }
    let idx: HashMap<(u32, u32), usize> = lumps.iter().enumerate().map(|(i, l)| (*l, i)).collect();
    let cost = |l: (u32, u32)| 2 * l.0 + 3 * l.1;
    let n = md.keys.len();
    // The lump of each state and its moves past the cut, per lump.
    let mut state_lump = vec![0u32; n];
    let mut out_offs: Vec<u32> = vec![0];
    let mut out_list: Vec<(u32, u32)> = Vec::new();
    let mut u = vec![0u8; t.nl];
    for (i, sl) in state_lump.iter_mut().enumerate() {
        c.decode(md.keys[i], &mut u);
        let mut cls = vec![0u8; t.sites];
        let (mut a, mut b) = (0u32, 0u32);
        for (q, x) in cls.iter_mut().enumerate() {
            *x = g.class[t.hol(g, &u, q) as usize];
            match *x {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        *sl = idx[&(a, b)] as u32;
        let mut tally: HashMap<u32, u32> = HashMap::new();
        for l in 0..t.nl {
            let keep = u[l];
            let [p0, p1] = t.link_plaq[l];
            for &e in &g.trans {
                u[l] = g.m(e, keep);
                let (mut a2, mut b2) = (a, b);
                for q in [p0, p1] {
                    match cls[q] {
                        1 => a2 -= 1,
                        2 => b2 -= 1,
                        _ => {}
                    }
                    match g.class[t.hol(g, &u, q) as usize] {
                        1 => a2 += 1,
                        2 => b2 += 1,
                        _ => {}
                    }
                }
                if cost((a2, b2)) > cut {
                    *tally.entry(idx[&(a2, b2)] as u32).or_insert(0) += 1;
                }
            }
            u[l] = keep;
        }
        out_list.extend(tally);
        out_offs.push(out_list.len() as u32);
    }
    // Signature rows of the lumps past the cut.
    let (ul, uy) = (t.lx as u32, t.ly as u32);
    let nl = t.nl as i64;
    let mut rows: Vec<Vec<Row>> = vec![Vec::new(); lumps.len()];
    for (li, &(a, b)) in lumps.iter().enumerate() {
        if cost((a, b)) <= cut {
            continue;
        }
        let (la, lb, li2) = (adj_limit(a, ul, uy), adj_limit(b, ul, uy), adj_limit(a + b, ul, uy));
        let mut seen: std::collections::HashSet<Row> = std::collections::HashSet::new();
        for tt in 0..=la {
            for tc in 0..=(4 * a - 2 * tt).min(4 * b) {
                let mut cc = 0u32;
                while 2 * cc + tc <= 4 * b && cc <= lb && tt + tc + cc <= li2 {
                    let et = 4 * a - 2 * tt - tc;
                    let ec = 4 * b - tc - 2 * cc;
                    let ee = nl - i64::from(et) - i64::from(ec) - i64::from(tt) - i64::from(tc) - i64::from(cc);
                    if ee >= 0 {
                        for tts in 0..=tt {
                            let counts = [ee as u32, et, ec, tts, tt - tts, tc, cc];
                            let mut near: HashMap<u32, u32> = HashMap::new();
                            let mut own = 0u32;
                            for (pat, count) in counts.iter().enumerate() {
                                if *count != 0 {
                                    for &(da, db, m) in RULE[pat] {
                                        let tgt = (a.wrapping_add_signed(da), b.wrapping_add_signed(db));
                                        if tgt == (a, b) {
                                            own += m * *count;
                                        } else if tgt != (0, 0) {
                                            *near.entry(idx[&tgt] as u32).or_insert(0) += m * *count;
                                        }
                                    }
                                }
                            }
                            let mut list: Vec<(u32, u32)> = near.into_iter().collect();
                            list.sort_unstable();
                            if seen.insert((own, list.clone())) {
                                rows[li].push((own, list));
                            }
                        }
                    }
                    cc += 1;
                }
            }
        }
    }
    let diag_of = |l: (u32, u32)| i128::from(r) * i128::from(cost(l)) + 3 * i128::from(nl);
    let mut order: Vec<usize> = (0..lumps.len()).filter(|i| cost(lumps[*i]) > cut).collect();
    order.sort_by_key(|i| cost(lumps[*i]));
    println!("HYBRID_SETUP|states={n}|rows_past_cut={}|lumps_past_cut={}|json=0", rows.iter().map(Vec::len).sum::<usize>(), order.len());
    let mut psi: Vec<i128> = start_psi.iter().map(|x| (i128::from(*x) + 1) << 50).collect();
    let mut gval: Vec<i128> = lumps
        .iter()
        .map(|l| {
            let m = cost(*l);
            if m <= cut {
                0
            } else {
                let drop = 2 * (m - cut);
                ((1i128 << 70) >> drop.min(60)).max(1)
            }
        })
        .collect();
    let mut dbar = vec![0i128; lumps.len()];
    let mut next = vec![0i128; n];
    let chunk = n.div_ceil(threads);
    let mut best = i128::MIN;
    let fill = |dbar: &mut Vec<i128>, psi: &[i128], gval: &[i128]| {
        dbar.fill(0);
        for (i, v) in psi.iter().enumerate() {
            let l = state_lump[i] as usize;
            if *v > dbar[l] {
                dbar[l] = *v;
            }
        }
        for &li in &order {
            dbar[li] = gval[li];
        }
    };
    for &target in targets {
        for _ in 0..sweeps {
            fill(&mut dbar, &psi, &gval);
            let (psi_ref, dbar_ref, out_offs_ref, out_list_ref) = (&psi, &dbar, &out_offs, &out_list);
            std::thread::scope(|scope| {
                for (tn, out) in next.chunks_mut(chunk).enumerate() {
                    scope.spawn(move || {
                        let base = tn * chunk;
                        for (j, slot) in out.iter_mut().enumerate() {
                            let i = base + j;
                            let mut s: i128 = 0;
                            for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                                s += psi_ref[q as usize];
                            }
                            for &(l, m) in &out_list_ref[out_offs_ref[i] as usize..out_offs_ref[i + 1] as usize] {
                                s += i128::from(m) * dbar_ref[l as usize];
                            }
                            let d = (i128::from(r) * i128::from(md.m[i]) + 3 * i128::from(nl)) * U - target;
                            *slot = (psi_ref[i] + s * U / d) / 2;
                        }
                    });
                }
            });
            std::mem::swap(&mut psi, &mut next);
            fill(&mut dbar, &psi, &gval);
            for &li in &order {
                let dl = diag_of(lumps[li]);
                let mut top: i128 = 0;
                for (own, near) in &rows[li] {
                    let mut s: i128 = 0;
                    for &(l, m) in near {
                        s += i128::from(m) * dbar[l as usize];
                    }
                    let den = (dl - i128::from(*own)) * U - target;
                    assert!(den > 0, "a row past the cut leaves no room at this target");
                    top = top.max(s * U / den);
                }
                let new = ((gval[li] + top) / 2).max(1);
                gval[li] = new;
                dbar[li] = new;
            }
            let high = psi.iter().copied().max().unwrap_or(1).max(gval.iter().copied().max().unwrap_or(1));
            let bits = 128 - high.leading_zeros();
            if bits > TOP_BITS {
                let sh = bits - TOP_BITS;
                for x in &mut psi {
                    *x >>= sh;
                }
                for x in &mut gval {
                    if *x > 0 {
                        *x = (*x >> sh).max(1);
                    }
                }
            }
            if bits < TOP_BITS {
                let sh = TOP_BITS - bits;
                for x in &mut psi {
                    *x <<= sh;
                }
                for x in &mut gval {
                    *x <<= sh;
                }
            }
        }
        // The exact value of this d.
        fill(&mut dbar, &psi, &gval);
        let mut min_a = i128::MAX;
        let mut zero = 0u64;
        for (i, pi) in psi.iter().enumerate() {
            if *pi <= 0 {
                zero += 1;
                continue;
            }
            let mut s: i128 = 0;
            for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                s += psi[q as usize];
            }
            for &(l, m) in &out_list[out_offs[i] as usize..out_offs[i + 1] as usize] {
                s += i128::from(m) * dbar[l as usize];
            }
            let dg = i128::from(r) * i128::from(md.m[i]) + 3 * i128::from(nl);
            let v = dg * U - (s * U + *pi - 1) / *pi;
            min_a = min_a.min(v);
        }
        let mut min_b = i128::MAX;
        for &li in &order {
            let dl = diag_of(lumps[li]);
            for (own, near) in &rows[li] {
                let mut s: i128 = 0;
                for &(l, m) in near {
                    s += i128::from(m) * dbar[l as usize];
                }
                let v = (dl - i128::from(*own)) * U - (s * U + gval[li] - 1) / gval[li];
                min_b = min_b.min(v);
            }
        }
        let cert = if zero == 0 { min_a.min(min_b) } else { i128::MIN };
        if cert > best {
            best = cert;
            let mut text = String::new();
            for (i, pi) in psi.iter().enumerate() {
                text.push_str(&format!("P|{}|{}\n", md.keys[i], pi));
            }
            for &li in &order {
                text.push_str(&format!("G|{}|{}|{}\n", lumps[li].0, lumps[li].1, gval[li]));
            }
            std::fs::write(dump, text).expect("write hybrid vector");
        }
        println!("HYBRID|Lx={}|Ly={}|r={r}|mcut={cut}|target_micro={target}|cert_micro={cert}|min_exact_rows={min_a}|min_table_rows={min_b}|psi_zero={zero}|json=0", t.lx, t.ly);
    }
    println!("HYBRID_BEST|Lx={}|Ly={}|r={r}|mcut={cut}|cert_micro={best}|json=0", t.lx, t.ly);
}

const PSI_TOP: i64 = 1 << 36;

fn rayleigh(md: &Model, psi: &[i64], diag: &[i64]) -> (i128, i128) {
    let (mut a_sum, mut b_sum) = (0i128, 0i128);
    for (i, pi) in psi.iter().enumerate() {
        let mut s: i128 = i128::from(diag[i]) * i128::from(*pi);
        for &t in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
            s -= i128::from(psi[t as usize]);
        }
        let w = i128::from(md.weight[i]) * i128::from(*pi);
        a_sum += w * s;
        b_sum += w * i128::from(*pi);
    }
    (a_sum, b_sum)
}

/// floor(10^6 a / b), for sums too large to multiply directly.
fn micro_of(a: i128, b: i128) -> i128 {
    let q = a.div_euclid(b);
    let mut r = a.rem_euclid(b);
    let mut bb = b;
    while r > i128::MAX / 2_000_000 {
        r >>= 1;
        bb >>= 1;
    }
    q * 1_000_000 + r * 1_000_000 / bb
}

fn solve(md: &Model, diag: &[i64], sweeps: usize, threads: usize, seed: &[i64]) -> Vec<i64> {
    let n = md.keys.len();
    let mut psi: Vec<i64> = seed.to_vec();
    let mut next = vec![0i64; n];
    let low_diag = *diag.iter().min().expect("non-empty");
    let (a0, b0) = rayleigh(md, &psi, diag);
    let mut lam = micro_of(a0, b0);
    println!("SWEEP|k=0|rho_micro={lam}|json=0");
    let chunk = n.div_ceil(threads);
    for k in 1..=sweeps {
        let cap = i128::from(low_diag) * 1_000_000 - 5_000;
        let shift = lam.min(cap);
        let psi_ref = &psi;
        std::thread::scope(|scope| {
            for (t, out) in next.chunks_mut(chunk).enumerate() {
                scope.spawn(move || {
                    let base = t * chunk;
                    for (j, slot) in out.iter_mut().enumerate() {
                        let i = base + j;
                        let mut s: i128 = 0;
                        for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                            s += i128::from(psi_ref[q as usize]);
                        }
                        let d = i128::from(diag[i]) * 1_000_000 - shift;
                        let v = s * 1_000_000 / d;
                        *slot = ((i128::from(psi_ref[i]) + v) / 2) as i64;
                    }
                });
            }
        });
        let top = *next.iter().max().expect("non-empty");
        assert!(top > 0);
        for (p, q) in psi.iter_mut().zip(next.iter()) {
            *p = ((i128::from(*q) * i128::from(PSI_TOP)) / i128::from(top)) as i64;
        }
        if k % 4 == 0 || k == sweeps {
            let (a1, b1) = rayleigh(md, &psi, diag);
            lam = micro_of(a1, b1);
        }
        if k % 40 == 0 || k == sweeps {
            println!("SWEEP|k={k}|rho_micro={lam}|json=0");
        }
    }
    psi
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (lx, ly): (usize, usize) = (args[1].parse().expect("lx"), args[2].parse().expect("ly"));
    let r: i64 = args[3].parse().expect("r");
    let cut: u32 = args[4].parse().expect("mcut");
    let sweeps: usize = args[5].parse().expect("sweeps");
    let threads: usize = args[6].parse().expect("threads");
    let prefix = args[7].clone();
    let sabotage = args.get(8).cloned().unwrap_or_else(|| "none".to_string());
    assert!(threads <= 3, "at most 3 threads by the brief");
    let t = Torus::new(lx, ly);
    let g = Group::new();
    let auts = lattice_group(&t);
    // Tree and free links.
    let mut is_tree = vec![false; t.nl];
    let mut tree_order = Vec::new();
    for y in 0..ly {
        if y > 0 {
            let l = 2 * (lx * (y - 1)) + 1;
            is_tree[l] = true;
            tree_order.push((l, lx * (y - 1), lx * y));
        }
        for x in 1..lx {
            let l = 2 * ((x - 1) + lx * y);
            is_tree[l] = true;
            tree_order.push((l, (x - 1) + lx * y, x + lx * y));
        }
    }
    let free: Vec<usize> = (0..t.nl).filter(|l| !is_tree[*l]).collect();
    assert_eq!(free.len(), t.sites + 1);
    let canon = Canon { t: &t, g: &g, auts: &auts, free: &free, tree_order: &tree_order };
    // Sanity of the group action and of the canonical form on random configurations.
    {
        let mut rng = Rng(0x1234_5678_9ABC_DEF1);
        let mut sc = canon.scratch();
        for _ in 0..200 {
            let u: Vec<El> = (0..t.nl).map(|_| rng.below(6) as u8).collect();
            let (k0, w0) = canon.canon(&u, &mut sc);
            for a in &auts {
                let mut img = vec![0u8; t.nl];
                for (l, &(to, inv)) in a.link.iter().enumerate() {
                    img[to as usize] = if inv { g.i(u[l]) } else { u[l] };
                }
                for p in 0..t.sites {
                    assert_eq!(g.class[t.hol(&g, &u, p) as usize], g.class[t.hol(&g, &img, a.plaq[p] as usize) as usize], "automorphism must carry plaquette classes");
                }
                let (k1, w1) = canon.canon(&img, &mut sc);
                assert_eq!((k0, w0), (k1, w1), "canonical form must be invariant under the lattice group");
            }
            // A random gauge transformation must not change the key.
            let h: Vec<El> = (0..t.sites).map(|_| rng.below(6) as u8).collect();
            let v: Vec<El> = (0..t.nl).map(|l| g.m(g.m(h[t.src[l]], u[l]), g.i(h[t.dst[l]]))).collect();
            assert_eq!(canon.canon(&v, &mut sc), (k0, w0), "canonical form must be gauge invariant");
        }
    }
    // Seeds: the M = 3 band, one defect at a corner of two cuts holding a non-commuting pair.
    let corner = |hx: El, hy: El| -> Vec<El> {
        let mut u = vec![ID; t.nl];
        for y in 0..ly {
            u[2 * ((lx - 1) + lx * y)] = hx;
        }
        for x in 0..lx {
            u[2 * (x + lx * (ly - 1)) + 1] = hy;
        }
        u
    };
    let mut seeds: Vec<Vec<El>> = Vec::new();
    let mut flats: Vec<Vec<El>> = Vec::new();
    for hx in 0..6u8 {
        for hy in 0..6u8 {
            let u = corner(hx, hy);
            if g.m(hx, hy) == g.m(hy, hx) {
                assert_eq!(t.lump_full(&g, &u), (0, 0));
                flats.push(u);
            } else {
                assert_eq!(t.lump_full(&g, &u), (0, 1));
                seeds.push(u);
            }
        }
    }
    assert_eq!(flats.len(), 18);
    assert_eq!(seeds.len(), 18);
    // Flat classes under conjugation only: their keys through the conjugation step.
    let mut flat_classes: HashMap<u128, u32> = HashMap::new();
    {
        let mut sc = canon.scratch();
        for f in &flats {
            let (k, st) = canon.gauge_key(f, &mut sc);
            flat_classes.insert(k, 6 / st);
        }
    }
    let flat_weight_total: u32 = flat_classes.values().sum();
    println!("FLATS|commuting_pairs={}|classes={}|weights_sum={flat_weight_total}|json=0", flats.len(), flat_classes.len());
    assert_eq!(flat_classes.len(), 8);
    assert_eq!(flat_weight_total, 18);
    let start = Instant::now();
    let mut md = build(&canon, cut, &seeds, threads);
    let n = md.keys.len();
    println!("MODEL|Lx={lx}|Ly={ly}|r={r}|mcut={cut}|group={}|states={n}|edges={}|build_seconds={}|json=0", auts.len(), md.adj.len(), start.elapsed().as_secs());
    let mut by_m: HashMap<u16, (u64, u64)> = HashMap::new();
    for i in 0..n {
        let e = by_m.entry(md.m[i]).or_insert((0, 0));
        e.0 += 1;
        e.1 += u64::from(md.weight[i]);
    }
    let mut ms: Vec<_> = by_m.iter().collect();
    ms.sort();
    for (mm, (c, w)) in ms {
        println!("MODEL_M|M={mm}|sector_states={c}|gauge_fixed_configs={w}|json=0");
    }
    let total_w: u64 = md.weight.iter().map(|w| u64::from(*w)).sum();
    let whole = 6u128.pow(free.len() as u32);
    let complete = u128::from(total_w) + 18 == whole;
    println!("COVERAGE|configs_in_model={total_w}|flats=18|whole={whole}|complete={}|json=0", i32::from(complete));
    if let Some(path) = args.iter().find_map(|x| x.strip_prefix("audit=")) {
        audit_low_m(&t, &g, &canon, &md, path, i128::from(r));
    }
    if sabotage == "unit_weight" {
        md.weight.fill(1);
    }
    let (pairs, bad) = self_adjoint(&mut md);
    println!("SELF_ADJOINT|pairs={pairs}|bad={bad}|json=0");
    if bad != 0 {
        println!("RITZ_VERDICT|verdict=RED|reason=not_self_adjoint|sabotage={sabotage}|json=0");
        std::process::exit(2);
    }
    let diag: Vec<i64> = md
        .m
        .iter()
        .map(|m| {
            let mm = if sabotage == "wrong_m" { i64::from(*m) - 1 } else { i64::from(*m) };
            r * mm + 3 * t.nl as i64
        })
        .collect();
    // Start: a fast decay with M, which is lattice-symmetric and positive.
    let mut seedv: Vec<i64> = Vec::with_capacity(n);
    for i in 0..n {
        let mut v = PSI_TOP;
        for _ in 3..md.m[i] {
            v = (v / 3).max(1);
        }
        seedv.push(v);
    }
    let psi = solve(&md, &diag, sweeps, threads, &seedv);
    let (a_sum, b_sum) = rayleigh(&md, &psi, &diag);
    // Couplings to the flat states.
    let mut sc = canon.scratch();
    let index: KeyMap = md.keys.iter().enumerate().map(|(i, k)| (*k, i as u32)).collect();
    let mut c_sum: i128 = 0;
    let mut seen_flat: HashMap<u128, ()> = HashMap::new();
    for f in &flats {
        let (fk, st) = canon.gauge_key(f, &mut sc);
        if seen_flat.insert(fk, ()).is_some() {
            continue;
        }
        let wf = i128::from(6 / st);
        let mut u = f.clone();
        let mut s: i128 = 0;
        for l in 0..t.nl {
            let keep = u[l];
            for &e in &g.trans {
                u[l] = g.m(e, keep);
                let (k, _) = canon.canon(&u, &mut sc);
                if let Some(i) = index.get(&k) {
                    s += i128::from(psi[*i as usize]);
                }
            }
            u[l] = keep;
        }
        c_sum += wf * s * s;
    }
    // Barta on the model: exact over the whole non-flat space only if the coverage is complete.
    let mut barta: Option<i128> = None;
    let positive = psi.iter().all(|x| *x > 0);
    if positive {
        for (i, pi) in psi.iter().enumerate() {
            let mut s: i128 = i128::from(diag[i]) * i128::from(*pi);
            for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                s -= i128::from(psi[q as usize]);
            }
            let v = (s * 1_000_000).div_euclid(i128::from(*pi));
            barta = Some(barta.map_or(v, |x: i128| x.min(v)));
        }
    }
    let barta_scope = if complete { "whole_space" } else { "truncated_model_only" };
    println!(
        "RITZ|Lx={lx}|Ly={ly}|r={r}|mcut={cut}|states={n}|sweeps={sweeps}|A={a_sum}|B={b_sum}|C={c_sum}|flat_diag={}|rho_micro={}|barta_micro={}|barta_scope={barta_scope}|positive={}|sabotage={sabotage}|json=0",
        3 * t.nl,
        micro_of(a_sum, b_sum),
        barta.unwrap_or(-1),
        i32::from(positive)
    );
    if let Some(list) = args.iter().find_map(|x| x.strip_prefix("hybrid=")) {
        let targets: Vec<i128> = list.split(',').map(|x| x.parse().expect("target")).collect();
        let hs: usize = args.iter().find_map(|x| x.strip_prefix("hsweeps=")).map_or(200, |x| x.parse().expect("hsweeps"));
        hybrid(&t, &g, &canon, &md, r, cut, &targets, hs, threads, &psi, &format!("{prefix}.hybrid"));
    }
    let sh = format!("{prefix}.psi");
    let mut text = String::with_capacity(n * 40);
    for (i, pi) in psi.iter().enumerate() {
        text.push_str(&format!("{}|{}|{}|{}\n", md.keys[i], md.m[i], md.weight[i], pi));
    }
    std::fs::write(&sh, text).expect("write psi");
    println!("RITZ_DONE|seconds={}|psi_file={sh}|json=0", start.elapsed().as_secs());
}
