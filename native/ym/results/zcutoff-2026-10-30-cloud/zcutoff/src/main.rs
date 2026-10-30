//! zcutoff: a collapsing vortex in the finite D3Q27 lattice gas at L = 24, 48, 96 (see PREREG.md). Rust 1.81, std only, integer and
//! ternary only: every channel holds a trit 0..2, every diagnostic is an exact integer, json=0.
//! usage: zcutoff GATES.lut
use std::collections::{BTreeMap, BTreeSet};

const K: usize = 27;

#[derive(Clone, Copy)]
struct Vel {
    x: i64,
    y: i64,
    z: i64,
    e: i64,
}

struct Gate {
    q: [usize; 4],
    lut: [u8; 81],
}

fn velocities() -> [Vel; K] {
    let mut v = [Vel { x: 0, y: 0, z: 0, e: 0 }; K];
    let mut i = 0;
    for x in -1..=1i64 {
        for y in -1..=1i64 {
            for z in -1..=1i64 {
                v[i] = Vel { x, y, z, e: x * x + y * y + z * z };
                i += 1;
            }
        }
    }
    v
}

fn decode(mut code: usize) -> [usize; 4] {
    let mut o = [0usize; 4];
    for d in o.iter_mut() {
        *d = code % 3;
        code /= 3;
    }
    o
}

fn encode(d: [u8; 4]) -> usize {
    d[0] as usize + 3 * d[1] as usize + 9 * d[2] as usize + 27 * d[3] as usize
}

/// The repo's gate construction, with ordered maps in place of std::map / std::set.
fn gates(v: &[Vel; K]) -> Vec<Gate> {
    let mut pairs: BTreeMap<(i64, i64, i64, i64), Vec<[usize; 2]>> = BTreeMap::new();
    for a in 0..K {
        for b in a + 1..K {
            pairs.entry((v[a].x + v[b].x, v[a].y + v[b].y, v[a].z + v[b].z, v[a].e + v[b].e)).or_default().push([a, b]);
        }
    }
    let mut quads: BTreeSet<[usize; 4]> = BTreeSet::new();
    for p in pairs.values() {
        for i in 0..p.len() {
            for j in i + 1..p.len() {
                let mut q = [p[i][0], p[i][1], p[j][0], p[j][1]];
                q.sort_unstable();
                if q[0] != q[1] && q[1] != q[2] && q[2] != q[3] {
                    quads.insert(q);
                }
            }
        }
    }
    let mut out = Vec::new();
    for q in quads {
        let mut lut = [0u8; 81];
        let mut cls: BTreeMap<[i64; 5], Vec<usize>> = BTreeMap::new();
        for (mask, l) in lut.iter_mut().enumerate() {
            let d = decode(mask);
            let mut k5 = [0i64; 5];
            for (j, &dj) in d.iter().enumerate() {
                let (w, vel) = (dj as i64, v[q[j]]);
                k5[0] += w;
                k5[1] += w * vel.x;
                k5[2] += w * vel.y;
                k5[3] += w * vel.z;
                k5[4] += w * vel.e;
            }
            cls.entry(k5).or_default().push(mask);
            *l = mask as u8;
        }
        for codes in cls.values() {
            let c: Vec<usize> = codes.iter().copied().filter(|&m| m != 40).collect();
            for pair in c.chunks_exact(2) {
                lut[pair[0]] = pair[1] as u8;
                lut[pair[1]] = pair[0] as u8;
            }
        }
        if lut.iter().enumerate().any(|(m, &l)| l as usize != m) {
            out.push(Gate { q, lut });
        }
    }
    out
}



fn collide(s: &mut [u8], t: usize, g: &[Gate], v_cells: usize) {
    for cell in 0..v_cells {
        let base = cell * K;
        for j in 0..32usize {
            let gate = &g[(t * 32 + cell * 17 + j * 37) % g.len()];
            let code = encode([s[base + gate.q[0]], s[base + gate.q[1]], s[base + gate.q[2]], s[base + gate.q[3]]]);
            let d = decode(gate.lut[code] as usize);
            for (k, &qk) in gate.q.iter().enumerate() {
                s[base + qk] = d[k] as u8;
            }
        }
    }
}

fn stream(s: &mut Vec<u8>, v: &[Vel; K], l: usize) {
    let mut next = vec![0u8; s.len()];
    let w = |a: usize, c: i64| ((a as i64 + c + l as i64) % l as i64) as usize;
    for x in 0..l {
        for y in 0..l {
            for z in 0..l {
                for (ki, vel) in v.iter().enumerate() {
                    let (nx, ny, nz) = (w(x, vel.x), w(y, vel.y), w(z, vel.z));
                    next[((nx * l + ny) * l + nz) * K + ki] = s[((x * l + y) * l + z) * K + ki];
                }
            }
        }
    }
    *s = next;
}

const PX: usize = 22;
const MX: usize = 4;
const PY: usize = 16;
const MY: usize = 10;

fn push(s: &mut [u8], cell: usize, plus: usize, minus: usize, sign: i64) {
    let (from, to) = if sign > 0 { (minus, plus) } else { (plus, minus) };
    let b = cell * K;
    if s[b + from] >= 1 && s[b + to] <= 1 {
        s[b + from] -= 1;
        s[b + to] += 1;
    }
}

/// Collapsing swirl: cells with d^2 * 4T <= L^2 (T - t) (doubled coordinates) and (7 cell + 13 t) mod 4 = 0.
fn force(s: &mut [u8], t: usize, l: usize, tt: usize, control: bool) {
    let li = l as i64;
    for x in 0..l {
        let dx2 = 2 * x as i64 + 1 - li;
        for y in 0..l {
            let dy2 = 2 * y as i64 + 1 - li;
            let d2 = dx2 * dx2 + dy2 * dy2;
            if d2 * 4 * tt as i64 > li * li * (tt as i64 - t as i64) {
                continue;
            }
            for z in 0..l {
                let cell = (x * l + y) * l + z;
                if (7 * cell + 13 * t) % 4 != 0 {
                    continue;
                }
                if control {
                    let h = 31 * cell + 17 * t;
                    let sx = if h & 1 == 0 { 1 } else { -1 };
                    let sy = if (h >> 1) & 1 == 0 { 1 } else { -1 };
                    push(s, cell, PX, MX, sx);
                    push(s, cell, PY, MY, sy);
                } else {
                    push(s, cell, PX, MX, -dy2.signum());
                    push(s, cell, PY, MY, dx2.signum());
                }
            }
        }
    }
}

struct Row {
    mass: i64,
    e2: i64,
    bad: i64,
    jmax: i64,
    wmax: i64,
    core: i64,
}

fn measure(s: &[u8], v: &[Vel; K], l: usize) -> Row {
    let vc = l * l * l;
    let (mut jx, mut jy, mut jz) = (vec![0i64; vc], vec![0i64; vc], vec![0i64; vc]);
    let mut r = Row { mass: 0, e2: 0, bad: 0, jmax: 0, wmax: 0, core: 0 };
    for cell in 0..vc {
        for (ki, vel) in v.iter().enumerate() {
            let n = s[cell * K + ki] as i64;
            if n > 2 {
                r.bad += 1;
            }
            r.mass += n;
            r.e2 += n * vel.e;
            jx[cell] += n * vel.x;
            jy[cell] += n * vel.y;
            jz[cell] += n * vel.z;
        }
        r.jmax = r.jmax.max(jx[cell] * jx[cell] + jy[cell] * jy[cell] + jz[cell] * jz[cell]);
    }
    let id = |x: i64, y: i64, z: i64| {
        let m = |a: i64| a.rem_euclid(l as i64) as usize;
        (m(x) * l + m(y)) * l + m(z)
    };
    let mut w2 = vec![0i64; vc];
    for x in 0..l as i64 {
        for y in 0..l as i64 {
            for z in 0..l as i64 {
                let wx = (jz[id(x, y + 1, z)] - jz[id(x, y - 1, z)]) - (jy[id(x, y, z + 1)] - jy[id(x, y, z - 1)]);
                let wy = (jx[id(x, y, z + 1)] - jx[id(x, y, z - 1)]) - (jz[id(x + 1, y, z)] - jz[id(x - 1, y, z)]);
                let wz = (jy[id(x + 1, y, z)] - jy[id(x - 1, y, z)]) - (jx[id(x, y + 1, z)] - jx[id(x, y - 1, z)]);
                let c = id(x, y, z);
                w2[c] = wx * wx + wy * wy + wz * wz;
                r.wmax = r.wmax.max(w2[c]);
            }
        }
    }
    r.core = if r.wmax > 0 { w2.iter().filter(|&&w| w * 2 >= r.wmax).count() as i64 } else { 0 };
    r
}


fn isqrt(v: i64) -> i64 {
    if v < 2 {
        return v;
    }
    let (mut x, mut y) = (v, (v + 1) / 2);
    while y < x {
        x = y;
        y = (x + v / x) / 2;
    }
    x
}

/// Axis vorticity OZ (sum along the vortex line) and RCORE (ring of largest mean azimuthal momentum).
fn measure2(s: &[u8], v: &[Vel; K], l: usize) -> (i64, i64) {
    let vc = l * l * l;
    let (mut jx, mut jy) = (vec![0i64; vc], vec![0i64; vc]);
    for cell in 0..vc {
        for (ki, vel) in v.iter().enumerate() {
            let n = s[cell * K + ki] as i64;
            jx[cell] += n * vel.x;
            jy[cell] += n * vel.y;
        }
    }
    let li = l as i64;
    let id = |x: i64, y: i64, z: i64| (x.rem_euclid(li) as usize * l + y.rem_euclid(li) as usize) * l + z.rem_euclid(li) as usize;
    let mut oz = 0i64;
    for x in [li / 2 - 1, li / 2] {
        for y in [li / 2 - 1, li / 2] {
            for z in 0..li {
                oz += (jy[id(x + 1, y, z)] - jy[id(x - 1, y, z)]) - (jx[id(x, y + 1, z)] - jx[id(x, y - 1, z)]);
            }
        }
    }
    let nr = l + 2;
    let (mut sa, mut cnt) = (vec![0i64; nr], vec![0i64; nr]);
    for x in 0..li {
        let dx2 = 2 * x + 1 - li;
        for y in 0..li {
            let dy2 = 2 * y + 1 - li;
            let k = (isqrt(dx2 * dx2 + dy2 * dy2) / 2) as usize;
            if k >= nr {
                continue;
            }
            for z in 0..li {
                let c = id(x, y, z);
                sa[k] += jx[c] * (-dy2) + jy[c] * dx2;
                cnt[k] += 1;
            }
        }
    }
    let mut best = 0usize;
    for k in 0..nr {
        if cnt[k] == 0 {
            continue;
        }
        // mean_k = sa[k] / (cnt[k] (2k+1)) compared exactly
        let lhs = sa[k] as i128 * (cnt[best] as i128 * (2 * best as i128 + 1));
        let rhs = sa[best] as i128 * (cnt[k] as i128 * (2 * k as i128 + 1));
        if cnt[best] == 0 || lhs > rhs {
            best = k;
        }
    }
    (oz, best as i64)
}

/// Largest |j|^2 over every cell state: |j|^2 is convex in n, so the maximum is at n in {0, 2}^27;
/// the rest channel adds nothing, leaving 2^26 subsets, walked in Gray-code order.
fn caps(v: &[Vel; K]) -> (i64, i64) {
    let moving: Vec<Vel> = v.iter().copied().filter(|c| c.e > 0).collect();
    let (mut sx, mut sy, mut sz) = (0i64, 0i64, 0i64);
    let mut best = 0i64;
    for i in 1u64..(1u64 << moving.len()) {
        let bit = i.trailing_zeros() as usize;
        let gray_on = ((i ^ (i >> 1)) >> bit) & 1 == 1;
        let c = moving[bit];
        let sg = if gray_on { 2 } else { -2 };
        sx += sg * c.x;
        sy += sg * c.y;
        sz += sg * c.z;
        best = best.max(sx * sx + sy * sy + sz * sz);
    }
    let jaxis = 2 * v.iter().filter(|c| c.x == 1).count() as i64;
    (best, jaxis)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: zcutoff GATES.lut");
        std::process::exit(3);
    }
    let glut = std::fs::read(&args[1]).unwrap_or_else(|_| std::process::exit(3));
    let v = velocities();
    let g = gates(&v);
    let mut mine = Vec::with_capacity(g.len() * 85);
    for gate in &g {
        mine.extend(gate.q.iter().map(|&q| q as u8));
        mine.extend_from_slice(&gate.lut);
    }
    if mine != glut {
        println!("ZCUT_INPUT|gates_equal_repo=0|result=INCONCLUSIVE|json=0");
        std::process::exit(3);
    }
    let (jcap, jaxis) = caps(&v);
    let wcap = 3 * (4 * jaxis) * (4 * jaxis);
    println!("ZCUT_CAPS|gates={}|gates_equal_repo=1|JCAP={jcap}|JAXIS={jaxis}|WCAP={wcap}|json=0", g.len());
    let mut c1 = true;
    let mut c2 = true;
    let mut summ: Vec<(usize, i64, usize, i64, i64)> = Vec::new(); // L, max WMAX, tick, min CORE, max JMAX
    let mut summ2: Vec<(i64, i64, i64, i64)> = Vec::new(); // drive peak OZ, control max |OZ|, drive WMAX, control WMAX
    for l in [24usize, 48, 96] {
        let tt = 2 * l;
        let vc = l * l * l;
        let mut s = vec![1u8; vc * K];
        let r0 = measure(&s, &v, l);
        let (mut wbest, mut wtick, mut cmin, mut jbest) = (0i64, 0usize, i64::MAX, 0i64);
        let (mut ozbest, mut oztick, mut rmin, mut rend) = (i64::MIN, 0usize, i64::MAX, 0i64);
        for t in 0..=tt {
            let r = if t == 0 { Row { ..r0 } } else { measure(&s, &v, l) };
            c1 &= r.bad == 0 && r.mass == r0.mass && r.e2 == r0.e2;
            c2 &= r.jmax <= jcap && r.wmax <= wcap;
            if t % 8 == 0 || t == tt {
                println!(
                    "ZCUT_ROW|L={l}|t={t}|mass={}|E2={}|JMAX={}|WMAX={}|CORE={}|json=0",
                    r.mass, r.e2, r.jmax, r.wmax, r.core
                );
            }
            if r.wmax > wbest {
                wbest = r.wmax;
                wtick = t;
            }
            if r.wmax > 0 {
                cmin = cmin.min(r.core);
            }
            jbest = jbest.max(r.jmax);
            let (oz, rc) = measure2(&s, &v, l);
            if oz > ozbest {
                ozbest = oz;
                oztick = t;
            }
            if t >= 1 {
                rmin = rmin.min(rc);
            }
            if t == tt {
                rend = rc;
            }
            if t % 8 == 0 || t == tt {
                println!("ZCUT2_ROW|arm=DRIVE|L={l}|t={t}|OZ={oz}|RCORE={rc}|json=0");
            }
            if t < tt {
                collide(&mut s, t, &g, vc);
                force(&mut s, t, l, tt, false);
                stream(&mut s, &v, l);
            }
        }
        println!(
            "ZCUT_SUM|L={l}|T={tt}|max_WMAX={wbest}|at_tick={wtick}|WMAX_over_WCAP_permille={}|min_CORE={cmin}|max_JMAX={jbest}|P=max_WMAX*L2={}|json=0",
            wbest * 1000 / wcap,
            wbest * (l * l) as i64
        );
        // CONTROL arm: same pushed cells and ticks, scrambled push signs
        let mut sc = vec![1u8; vc * K];
        let (mut cw, mut coz) = (0i64, 0i64);
        for t in 0..=tt {
            let r = measure(&sc, &v, l);
            c1 &= r.bad == 0 && r.mass == r0.mass && r.e2 == r0.e2;
            cw = cw.max(r.wmax);
            let (oz, rc) = measure2(&sc, &v, l);
            coz = coz.max(oz.abs());
            if t % 8 == 0 || t == tt {
                println!("ZCUT2_ROW|arm=CONTROL|L={l}|t={t}|OZ={oz}|RCORE={rc}|WMAX={}|json=0", r.wmax);
            }
            if t < tt {
                collide(&mut sc, t, &g, vc);
                force(&mut sc, t, l, tt, true);
                stream(&mut sc, &v, l);
            }
        }
        println!(
            "ZCUT2_SUM|L={l}|drive_peak_OZ={ozbest}|at_tick={oztick}|control_max_abs_OZ={coz}|drive_max_WMAX={wbest}|control_max_WMAX={cw}|RCORE_min={rmin}|RCORE_end={rend}|RCORE_end_permille_of_L={}|json=0",
            rend * 1000 / l as i64
        );
        summ.push((l, wbest, wtick, cmin, jbest));
        summ2.push((ozbest, coz, wbest, cw));
    }
    let p: Vec<i64> = summ.iter().map(|&(l, w, _, _, _)| w * (l * l) as i64).collect();
    let c3 = p[0] < p[1] && p[1] < p[2];
    let c4a = summ.iter().all(|&(_, _, _, c, _)| (1..i64::MAX).contains(&c));
    // (min CORE)/L^3 strictly decreasing: c_a * L_b^3 > c_b * L_a^3 for a < b
    let vol = |i: usize| (summ[i].3, (summ[i].0 * summ[i].0 * summ[i].0) as i64);
    let dec = |a: usize, b: usize| {
        let ((ca, la), (cb, lb)) = (vol(a), vol(b));
        ca * lb > cb * la
    };
    let c4 = c4a && dec(0, 1) && dec(1, 2);
    println!("ZCUT_RATIO|P48_over_P24_permille={}|P96_over_P48_permille={}|json=0", p[1] * 1000 / p[0].max(1), p[2] * 1000 / p[1].max(1));
    let pf = |b: bool| if b { "PASS" } else { "FAIL" };
    println!("ZCUT_RESULT|C1={}|C2={}|C3={}|C4={}|json=0", pf(c1), pf(c2), pf(c3), pf(c4));
    let a1 = summ2.iter().all(|&(o, c, _, _)| o > 10 * c);
    let a2 = summ2[0].0 < summ2[1].0 && summ2[1].0 < summ2[2].0;
    let a3 = summ2.iter().all(|&(_, _, wd, wc)| (wd - wc).abs() * 4 <= wd);
    println!(
        "ZCUT2_RATIO|OZ48_over_OZ24_permille={}|OZ96_over_OZ48_permille={}|json=0",
        summ2[1].0 * 1000 / summ2[0].0.max(1),
        summ2[2].0 * 1000 / summ2[1].0.max(1)
    );
    println!("ZCUT2_RESULT|A1={}|A2={}|A3={}|json=0", pf(a1), pf(a2), pf(a3));
}
