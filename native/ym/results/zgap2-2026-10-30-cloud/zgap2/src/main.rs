//! zgap2: second-order gap coefficient c for the S3 torus (see PREREG.md). Rust 1.81, std only,
//! exact integer arithmetic (i128, every operation checked; overflow is INCONCLUSIVE), json=0.
mod big;
mod lat;
use big::Big;
use lat::{Lat, TRANS};
use std::collections::{BTreeMap, BTreeSet};

struct St {
    q: Vec<usize>,
    w: i64,
    m: i64,
}

struct Model {
    lat: Lat,
    st: BTreeMap<u64, St>,
    rows: BTreeMap<u64, (i64, BTreeMap<u64, i64>)>, // diag, off-diagonal E (negative counts)
}

impl Model {
    fn ensure(&mut self, q: Vec<usize>) -> u64 {
        let k = self.lat.key(&q);
        if let std::collections::btree_map::Entry::Vacant(v) = self.st.entry(k) {
            let w = self.lat.weight(&q);
            let m = self.lat.magnetic(&self.lat.rep(&q));
            v.insert(St { q, w, m });
        }
        k
    }
    fn row(&mut self, k: u64) {
        if self.rows.contains_key(&k) {
            return;
        }
        let raw = self.lat.rep(&self.st[&k].q);
        let mut diag = 3 * self.lat.links() as i64;
        let mut off: BTreeMap<u64, i64> = BTreeMap::new();
        for e in 0..self.lat.links() {
            for &t in &TRANS {
                let mut nx = raw.clone();
                nx[e] = self.lat.g.mul[t][nx[e]];
                let q = self.lat.gauge_fix(&nx);
                let j = self.ensure(q);
                if j == k {
                    diag -= 1;
                } else {
                    *off.entry(j).or_insert(0) -= 1;
                }
            }
        }
        self.rows.insert(k, (diag, off));
    }
}

fn seam(l: &Lat, a: usize, b: usize) -> Vec<usize> {
    let mut links = vec![0usize; l.links()];
    for y in 0..l.ly {
        links[l.site(l.lx - 1, y)] = a;
    }
    for x in 0..l.lx {
        links[l.n + l.site(x, l.ly - 1)] = b;
    }
    links
}


fn gcd(a: i64, b: i64) -> i64 {
    if b == 0 {
        a.abs()
    } else {
        gcd(b, a % b)
    }
}

fn lcm(a: i64, b: i64) -> i64 {
    a / gcd(a, b) * b
}

/// Number of eigenvalues of W^-1 S below t = tn / td (S symmetric, W positive diagonal):
/// the negative inertia of td*S - tn*W, from the signs of its leading principal minors (Bareiss).
/// None if a leading minor is zero (the caller moves t).
fn count_below(s: &[Vec<i128>], w: &[i128], tn: i128, td: i128) -> Option<usize> {
    let m = s.len();
    let mut a: Vec<Vec<Big>> = (0..m)
        .map(|i| (0..m).map(|j| Big::from_i128(td * s[i][j] - if i == j { tn * w[i] } else { 0 })).collect())
        .collect();
    let mut prev = Big::from_i128(1);
    let mut last_sign = 1;
    let mut changes = 0;
    for k in 0..m {
        let piv = a[k][k].clone();
        let sg = piv.signum();
        if sg == 0 {
            return None;
        }
        if sg != last_sign {
            changes += 1;
        }
        last_sign = sg;
        for i in k + 1..m {
            for j in k + 1..m {
                let v = piv.mul(&a[i][j]).sub(&a[i][k].mul(&a[k][j]));
                a[i][j] = v.div_exact(&prev)?;
            }
        }
        prev = piv;
    }
    Some(changes)
}

/// Enclosure [lo, hi] (units of 2^-bits) of the k-th smallest eigenvalue (k from 1) of W^-1 S / scale.
fn eig_k(s: &[Vec<i128>], w: &[i128], scale: i128, k: usize, bits: u32) -> Option<(i128, i128)> {
    let bound: i128 = (0..s.len()).map(|i| s[i].iter().map(|x| x.abs()).sum::<i128>() / w[i] + 1).max()? / scale + 2;
    let (mut lo, mut hi) = (-bound << bits, bound << bits);
    let td = 1i128 << bits;
    let cnt = |t: i128| -> Option<usize> {
        for nudge in 0..4i128 {
            if let Some(c) = count_below(s, w, (t * 4 + nudge) * scale, td * 4) {
                return Some(c);
            }
        }
        None
    };
    if cnt(lo)? >= k || cnt(hi)? < k {
        return None;
    }
    while hi - lo > 1 {
        let mid = lo + (hi - lo) / 2;
        if cnt(mid)? >= k {
            hi = mid;
        } else {
            lo = mid;
        }
    }
    Some((lo, hi))
}

/// Integer characteristic polynomial (Faddeev-LeVerrier), highest degree first.
fn charpoly(a: &[Vec<i128>]) -> Option<Vec<i128>> {
    let n = a.len();
    let mut c = vec![1i128];
    let mut mk = vec![vec![0i128; n]; n];
    for k in 1..=n {
        let mut am = vec![vec![0i128; n]; n];
        for (i, ai) in a.iter().enumerate() {
            for j in 0..n {
                let mut v = 0i128;
                for (l, mkl) in mk.iter().enumerate() {
                    v = v.checked_add(ai[l].checked_mul(mkl[j])?)?;
                }
                am[i][j] = v + if i == j { *c.last()? } else { 0 };
            }
        }
        mk = am;
        let mut tr = 0i128;
        for (i, ai) in a.iter().enumerate() {
            for (l, mkl) in mk.iter().enumerate() {
                tr = tr.checked_add(ai[l].checked_mul(mkl[i])?)?;
            }
        }
        if tr % k as i128 != 0 {
            return None;
        }
        c.push(-tr / k as i128);
    }
    Some(c)
}

const BITS: u32 = 40;

fn micro_floor(v: i128) -> i128 {
    (v * 1_000_000).div_euclid(1i128 << BITS)
}

fn micro_ceil(v: i128) -> i128 {
    -((-v * 1_000_000).div_euclid(1i128 << BITS))
}

fn fmt_micro(v: i128) -> String {
    let s = if v < 0 { "-" } else { "" };
    format!("{s}{}.{:06}", v.abs() / 1_000_000, v.abs() % 1_000_000)
}

struct Out {
    name: String,
    c_lo: i128,
    c_hi: i128,
    poly: Vec<i128>,
    poly_den: i128,
    d1: i64,
    k_gap: Option<(i128, i128)>,
    k_scalar: bool,
}
fn main() {
    if run().is_none() {
        println!("ZGAP_RESULT|status=INCONCLUSIVE|reason=arithmetic_or_enclosure|json=0");
        std::process::exit(3);
    }
}

fn run() -> Option<()> {
    let mut outs: Vec<Out> = Vec::new();
    let specs: Vec<(usize, usize)> = vec![(2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)];
    for (lx, ly) in specs {
        let lat = Lat::new(lx, ly);
        let mut md = Model { lat, st: BTreeMap::new(), rows: BTreeMap::new() };
        let mut vac = BTreeSet::new();
        let mut seeds = BTreeSet::new();
        for a in 0..6 {
            for b in 0..6 {
                let links = seam(&md.lat, a, b);
                let mm = md.lat.magnetic(&links);
                let q = md.lat.gauge_fix(&links);
                if mm == 0 {
                    vac.insert(md.ensure(q));
                } else if mm == 3 {
                    seeds.insert(md.ensure(q));
                }
            }
        }
        // closure of the M = 3 manifold under two electric flips
        let mut m3: BTreeSet<u64> = seeds.clone();
        let mut todo: Vec<u64> = seeds.into_iter().collect();
        while let Some(a) = todo.pop() {
            md.row(a);
            let js: Vec<u64> = md.rows[&a].1.keys().copied().collect();
            for j in js {
                if md.st[&j].m == 3 {
                    continue;
                }
                md.row(j);
                let bs: Vec<u64> = md.rows[&j].1.keys().copied().collect();
                for b in bs {
                    if md.st[&b].m == 3 && m3.insert(b) {
                        todo.push(b);
                    }
                }
            }
        }
        println!("ZGAP_SIZE|L={lx}x{ly}|vacua={}|m3_orbits={}|json=0", vac.len(), m3.len());
        let vac: Vec<u64> = vac.into_iter().collect();
        let m3v: Vec<u64> = m3.iter().copied().collect();
        for &a in vac.iter().chain(m3v.iter()) {
            md.row(a);
        }
        // first order: diagonals, and no flat-to-flat or M3-to-M3 off-diagonal entries
        let vd: BTreeSet<i64> = vac.iter().map(|a| md.rows[a].0).collect();
        let m3d: BTreeSet<i64> = m3v.iter().map(|a| md.rows[a].0).collect();
        let ff = vac.iter().map(|a| md.rows[a].1.keys().filter(|j| md.st[*j].m == 0).count()).sum::<usize>();
        let mm = m3v.iter().map(|a| md.rows[a].1.keys().filter(|j| md.st[*j].m == 3).count()).sum::<usize>();
        let d1 = m3d.iter().min().copied().unwrap_or(0) - vd.iter().max().copied().unwrap_or(0);
        println!(
            "ZGAP_FIRST|L={lx}x{ly}|vac_diag={:?}|m3_diag={:?}|flat_to_flat={ff}|m3_to_m3={mm}|d1={d1}|json=0",
            vd, m3d
        );
        // weighted second-order operator over a set P, intermediates outside P with denominators e0 - M_j
        let second = |md: &Model, set: &[u64], e0: i64| -> Option<(Vec<Vec<i128>>, i128, bool)> {
            let inset: BTreeSet<u64> = set.iter().copied().collect();
            let mut lc: i64 = 1;
            for a in set {
                for j in md.rows[a].1.keys() {
                    if !inset.contains(j) {
                        lc = lcm(lc, (e0 - md.st[j].m).abs());
                    }
                }
            }
            let idx: BTreeMap<u64, usize> = set.iter().enumerate().map(|(i, &a)| (a, i)).collect();
            let n = set.len();
            let mut k = vec![vec![0i128; n]; n];
            let mut divisible = true;
            for (ia, a) in set.iter().enumerate() {
                for (j, &eaj) in &md.rows[a].1 {
                    if inset.contains(j) {
                        continue;
                    }
                    let (wj, mj) = (md.st[j].w, md.st[j].m);
                    for (ib, b) in set.iter().enumerate() {
                        if let Some(&ebj) = md.rows[b].1.get(j) {
                            let num = md.st[b].w * ebj;
                            if num % wj != 0 {
                                divisible = false;
                            }
                            k[ia][ib] += eaj as i128 * (num / wj) as i128 * (lc / (e0 - mj)) as i128;
                        }
                    }
                }
            }
            let _ = idx;
            Some((k, lc as i128, divisible))
        };
        let (k0, lc0, div0) = second(&md, &vac, 0)?;
        // vacuum energy shift is -K0/r; kappa = eigenvalues of K0 (flat_law convention)
        let w0: Vec<i128> = vac.iter().map(|a| md.st[a].w as i128).collect();
        let s0: Vec<Vec<i128>> = (0..8).map(|i| (0..8).map(|j| w0[i] * k0[i][j]).collect()).collect();
        let sym0 = (0..8).all(|i| (0..8).all(|j| s0[i][j] == s0[j][i]));
        let scalar0 = (0..8).all(|i| (0..8).all(|j| k0[i][j] == if i == j { k0[0][0] } else { 0 }));
        let kmin = eig_k(&s0, &w0, lc0, 1, BITS)?;
        let k2 = eig_k(&s0, &w0, lc0, 2, BITS)?;
        let kmax = eig_k(&s0, &w0, lc0, 8, BITS)?;
        // H3 = P3 E Q3 (3 - M)^-1 Q3 E P3 over the M = 3 orbits
        let (h3, lc3, div3) = second(&md, &m3v, 3)?;
        // zero-momentum reduction over translation classes
        let mut class_of: BTreeMap<u64, usize> = BTreeMap::new();
        let mut classes: Vec<Vec<u64>> = Vec::new();
        for &a in &m3v {
            if class_of.contains_key(&a) {
                continue;
            }
            let raw = md.lat.rep(&md.st[&a].q);
            let mut cl = BTreeSet::new();
            for dx in 0..lx {
                for dy in 0..ly {
                    let t = md.lat.translate(&raw, dx, dy);
                    cl.insert(md.lat.key(&md.lat.gauge_fix(&t)));
                }
            }
            let id = classes.len();
            for &b in &cl {
                class_of.insert(b, id);
            }
            classes.push(cl.into_iter().collect());
        }
        let pos: BTreeMap<u64, usize> = m3v.iter().enumerate().map(|(i, &a)| (a, i)).collect();
        let nc = classes.len();
        let mut r = vec![vec![0i128; nc]; nc];
        for (ci, cl) in classes.iter().enumerate() {
            let a0 = pos[&cl[0]];
            for (dj, dl) in classes.iter().enumerate() {
                r[ci][dj] = dl.iter().map(|b| h3[a0][pos[b]]).sum();
            }
        }
        let wc: Vec<i128> = classes.iter().map(|cl| cl.iter().map(|a| md.st[a].w as i128).sum()).collect();
        let s3: Vec<Vec<i128>> = (0..nc).map(|i| (0..nc).map(|j| wc[i] * r[i][j]).collect()).collect();
        let sym3 = (0..nc).all(|i| (0..nc).all(|j| s3[i][j] == s3[j][i]));
        let lmin = eig_k(&s3, &wc, lc3, 1, BITS)?;
        println!(
            "ZGAP_SECOND|L={lx}x{ly}|Lc0={lc0}|Lc3={lc3}|weights_divide={}|K0_symmetric={}|K0_scalar={}|zero_momentum_classes={nc}|class_sizes={:?}|R3_symmetric={}|json=0",
            i64::from(div0 && div3), i64::from(sym0), i64::from(scalar0), classes.iter().map(|c| c.len()).collect::<Vec<_>>(), i64::from(sym3)
        );
        // c(inf) = -(lambda_min(H3) + kappa_min), enclosure
        let c_lo = kmax.0 - lmin.1;
        let c_hi = kmax.1 - lmin.0;
        // exact charpoly of (R/Lc3 + kappa I) when K0 is scalar: integer matrix over den = lcm(Lc0, Lc3)
        let den = lcm(lc0 as i64, lc3 as i64) as i128;
        let mut poly = Vec::new();
        if scalar0 {
            // c = kappa_top - lambda: charpoly of (kappa_top I - R/Lc3), integer over den
            let kap = k0[0][0] * (den / lc0);
            let t: Vec<Vec<i128>> = (0..nc).map(|i| (0..nc).map(|j| -r[i][j] * (den / lc3) + if i == j { kap } else { 0 }).collect()).collect();
            poly = charpoly(&t)?;
        }
        println!(
            "ZGAP_C|L={lx}x{ly}|H0_top_micro=[{},{}]|lambda_min_H3_micro=[{},{}]|c_inf_micro=[{},{}]|exact_charpoly_kappa_top_minus_R={:?}|den={den}|json=0",
            fmt_micro(micro_floor(kmax.0)), fmt_micro(micro_ceil(kmax.1)), fmt_micro(micro_floor(lmin.0)), fmt_micro(micro_ceil(lmin.1)),
            fmt_micro(micro_floor(c_lo)), fmt_micro(micro_ceil(c_hi)), poly
        );
        // published law: splitting of the two lowest vacuum levels (shift operator H0 = -kappa)
        let k_gap = Some((k2.0 - kmin.1, k2.1 - kmin.0));
        outs.push(Out { name: format!("{lx}x{ly}"), c_lo: micro_floor(c_lo), c_hi: micro_ceil(c_hi), poly, poly_den: den, d1, k_gap, k_scalar: scalar0 });
    }
    let get = |n: &str| outs.iter().find(|o| o.name == n);
    let pf = |b: bool| if b { "PASS" } else { "FAIL" };
    let p0 = outs.iter().all(|o| o.d1 == 0);
    let within = |n: &str, lo: i128, hi: i128| get(n).map_or(false, |o| o.c_lo >= lo && o.c_hi <= hi);
    let p2 = within("3x3", 21_095_802, 21_573_297);
    let p2b = within("2x2", 36_765_900, 37_108_530) && within("2x3", 34_499_682, 34_869_285) && within("2x4", 36_480_618, 36_787_041);
    // exact equality of the monic characteristic polynomials of (R/Lc3 + kappa I)
    let same_poly = |a: &Out, b: &Out| -> bool {
        if a.poly.is_empty() || a.poly.len() != b.poly.len() {
            return false;
        }
        let (da, db) = (Big::from_i128(a.poly_den), Big::from_i128(b.poly_den));
        let (mut pa, mut pb) = (Big::from_i128(1), Big::from_i128(1));
        for k in 0..a.poly.len() {
            if Big::from_i128(a.poly[k]).mul(&pb) != Big::from_i128(b.poly[k]).mul(&pa) {
                return false;
            }
            pa = pa.mul(&da);
            pb = pb.mul(&db);
        }
        true
    };
    let (o33, o34, o44) = (get("3x3")?, get("3x4")?, get("4x4")?);
    let disjoint = |a: &Out, b: &Out| a.c_hi < b.c_lo || b.c_hi < a.c_lo;
    let p3 = same_poly(o33, o34) && same_poly(o33, o44) && ["2x2", "2x3", "2x4"].iter().all(|n| get(n).map_or(false, |o| disjoint(o, o33)));
    let isqrt = |v: i128| -> i128 {
        // integer Newton iteration from above: floor(sqrt(v))
        if v < 2 {
            return v;
        }
        let mut x = v;
        let mut y = (x + 1) / 2;
        while y < x {
            x = y;
            y = (x + v / x) / 2;
        }
        x
    };
    let sc = 1i128 << BITS;
    // sqrt(14) - sqrt(6) enclosure at 2^-BITS: [floor(sqrt14) - ceil(sqrt6), ceil(sqrt14) - floor(sqrt6)]
    let (s14, s6) = (isqrt(14 * sc * sc), isqrt(6 * sc * sc));
    let law22 = (s14 - s6 - 1, s14 + 1 - s6);
    let contains = |n: &str, lo: i128, hi: i128| get(n).and_then(|o| o.k_gap).map_or(false, |(a, b)| a <= hi && b >= lo);
    let p4 = contains("2x2", law22.0, law22.1) && contains("2x3", 3 * sc, 3 * sc) && contains("2x4", 4 * sc, 4 * sc) && o33.k_scalar;
    for o in &outs {
        println!("ZGAP_SUMMARY|L={}|c_inf_micro=[{},{}]|d1={}|json=0", o.name, fmt_micro(o.c_lo), fmt_micro(o.c_hi), o.d1);
    }
    println!("ZGAP_RESULT|P0={}|P1=PENDING|P2={}|P2b={}|P3={}|P4={}|json=0", pf(p0), pf(p2), pf(p2b), pf(p3), pf(p4));
    Some(())
}
