//! zcalib: viscosity, sound speed and equation of state on the current gates (see PREREG.md). Rust 1.81, std only, integer and
//! ternary only: every channel holds a trit 0..2, every diagnostic is an exact integer, json=0.
//! usage: zcalib GATES.lut
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



struct Box3 {
    lx: usize,
    ly: usize,
    lz: usize,
}

impl Box3 {
    fn cells(&self) -> usize {
        self.lx * self.ly * self.lz
    }
    fn idx(&self, x: usize, y: usize, z: usize) -> usize {
        (x * self.ly + y) * self.lz + z
    }
}

fn collide(s: &mut [u8], t: usize, g: &[Gate], vc: usize) {
    for cell in 0..vc {
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

fn stream(s: &mut Vec<u8>, v: &[Vel; K], b: &Box3) {
    let mut next = vec![0u8; s.len()];
    let w = |a: usize, c: i64, l: usize| ((a as i64 + c + l as i64) % l as i64) as usize;
    for x in 0..b.lx {
        for y in 0..b.ly {
            for z in 0..b.lz {
                for (ki, vel) in v.iter().enumerate() {
                    let (nx, ny, nz) = (w(x, vel.x, b.lx), w(y, vel.y, b.ly), w(z, vel.z, b.lz));
                    next[b.idx(nx, ny, nz) * K + ki] = s[b.idx(x, y, z) * K + ki];
                }
            }
        }
    }
    *s = next;
}

/// mass, energy, occupancy violations
fn totals(s: &[u8], v: &[Vel; K]) -> (i64, i64, i64) {
    let (mut m, mut e, mut bad) = (0i64, 0i64, 0i64);
    for (i, &n) in s.iter().enumerate() {
        let n = n as i64;
        if n > 2 {
            bad += 1;
        }
        m += n;
        e += n * v[i % K].e;
    }
    (m, e, bad)
}

const PX: usize = 22;
const MX: usize = 4;
const REST: usize = 13;

/// shear: returns (A series, conservation ok)
fn shear(ly: usize, v: &[Vel; K], g: &[Gate], ticks: usize) -> (Vec<i64>, bool) {
    let b = Box3 { lx: 8, ly, lz: 8 };
    let vc = b.cells();
    let mut s = vec![1u8; vc * K];
    for x in 0..b.lx {
        for y in 0..ly {
            for z in 0..b.lz {
                let c = b.idx(x, y, z) * K;
                let (from, to) = if y < ly / 2 { (MX, PX) } else { (PX, MX) };
                s[c + from] -= 1;
                s[c + to] += 1;
            }
        }
    }
    let t0 = totals(&s, v);
    let mut ok = true;
    let mut a = Vec::with_capacity(ticks + 1);
    for t in 0..=ticks {
        let tt = totals(&s, v);
        ok &= tt.0 == t0.0 && tt.1 == t0.1 && tt.2 == 0;
        let mut sum = 0i64;
        for x in 0..b.lx {
            for y in 0..ly {
                for z in 0..b.lz {
                    let c = b.idx(x, y, z) * K;
                    let jx: i64 = (0..K).map(|k| s[c + k] as i64 * v[k].x).sum();
                    sum += if y < ly / 2 { jx } else { -jx };
                }
            }
        }
        a.push(sum);
        if t < ticks {
            collide(&mut s, t, g, vc);
            stream(&mut s, v, &b);
        }
    }
    (a, ok)
}

/// sound: returns (D series, conservation ok)
fn sound(lx: usize, v: &[Vel; K], g: &[Gate], ticks: usize) -> (Vec<i64>, bool) {
    let b = Box3 { lx, ly: 8, lz: 8 };
    let vc = b.cells();
    let mut s = vec![1u8; vc * K];
    for x in 0..lx {
        for y in 0..b.ly {
            for z in 0..b.lz {
                s[b.idx(x, y, z) * K + REST] = if x < lx / 2 { 2 } else { 0 };
            }
        }
    }
    let t0 = totals(&s, v);
    let mut ok = true;
    let mut d = Vec::with_capacity(ticks + 1);
    for t in 0..=ticks {
        let tt = totals(&s, v);
        ok &= tt.0 == t0.0 && tt.1 == t0.1 && tt.2 == 0;
        let mut sum = 0i64;
        for x in 0..lx {
            for y in 0..b.ly {
                for z in 0..b.lz {
                    let c = b.idx(x, y, z) * K;
                    let rho: i64 = (0..K).map(|k| s[c + k] as i64).sum();
                    sum += if x < lx / 2 { rho } else { -rho };
                }
            }
        }
        d.push(sum);
        if t < ticks {
            collide(&mut s, t, g, vc);
            stream(&mut s, v, &b);
        }
    }
    (d, ok)
}

/// sound2 (addendum): moving-channel density step; returns (D series, conservation ok)
fn sound2(lx: usize, v: &[Vel; K], g: &[Gate], ticks: usize) -> (Vec<i64>, bool) {
    let b = Box3 { lx, ly: 8, lz: 8 };
    let vc = b.cells();
    let mut s = vec![1u8; vc * K];
    for x in 0..lx {
        for y in 0..b.ly {
            for z in 0..b.lz {
                let c = b.idx(x, y, z) * K;
                let n = if x < lx / 2 { 2 } else { 0 };
                s[c + PX] = n;
                s[c + MX] = n;
            }
        }
    }
    let t0 = totals(&s, v);
    let mut ok = true;
    let mut d = Vec::with_capacity(ticks + 1);
    for t in 0..=ticks {
        let tt = totals(&s, v);
        ok &= tt.0 == t0.0 && tt.1 == t0.1 && tt.2 == 0;
        let mut sum = 0i64;
        for x in 0..lx {
            for y in 0..b.ly {
                for z in 0..b.lz {
                    let c = b.idx(x, y, z) * K;
                    let rho: i64 = (0..K).map(|k| s[c + k] as i64).sum();
                    sum += if x < lx / 2 { rho } else { -rho };
                }
            }
        }
        d.push(sum);
        if t < ticks {
            collide(&mut s, t, g, vc);
            stream(&mut s, v, &b);
        }
    }
    (d, ok)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: zcalib GATES.lut");
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
        println!("ZCAL_INPUT|gates_equal_repo=0|result=INCONCLUSIVE|json=0");
        std::process::exit(3);
    }
    println!("ZCAL_INPUT|gates={}|gates_equal_repo=1|json=0", g.len());
    let pf = |b: bool| if b { "PASS" } else { "FAIL" };
    let mut k1 = true;
    let mut inconclusive = false;
    // K3: equation of state at the uniform state
    let tr: i64 = v.iter().map(|c| c.e).sum();
    let rho: i64 = K as i64;
    let k3 = tr == 2 * rho;
    println!("ZCAL_EOS|TrPi={tr}|rho={rho}|TrPi_over_rho_is_2={}|cs2=2/3|json=0", i64::from(k3));
    // shear
    let mut halves = Vec::new();
    let mut nu2: Vec<(i128, i128)> = Vec::new();
    for ly in [24usize, 48] {
        let ticks = 12 * ly;
        let (a, ok) = shear(ly, &v, &g, ticks);
        k1 &= ok;
        for (t, x) in a.iter().enumerate() {
            if t % 4 == 0 {
                println!("ZCAL_SHEAR_ROW|Ly={ly}|t={t}|A={x}|json=0");
            }
        }
        let th = (0..a.len()).find(|&t| 2 * a[t] <= a[0]);
        match th {
            None => {
                inconclusive = true;
                println!("ZCAL_SHEAR|Ly={ly}|A0={}|T_half=none|json=0", a[0]);
            }
            Some(th) => {
                // nu = ln2 Ly^2 / (4 pi^2 T_half), in micro-units, outward rounded
                let l2 = (ly * ly) as i128;
                let thi = th as i128;
                let lo = 693_147i128 * l2 * 1_000_000 / (4 * 9_869_605 * thi);
                let hi = (693_148i128 * l2 * 1_000_000 + 4 * 9_869_604 * thi - 1) / (4 * 9_869_604 * thi);
                println!(
                    "ZCAL_SHEAR|Ly={ly}|A0={}|T_half={th}|nu_micro=[{lo},{hi}]|json=0",
                    a[0]
                );
                halves.push(th as i64);
                if let Some(tq) = (0..a.len()).find(|&t| 4 * a[t] <= a[0]) {
                    let dt = (tq - th) as i128;
                    let lo2 = 693_147i128 * l2 * 1_000_000 / (4 * 9_869_605 * dt);
                    let hi2 = (693_148i128 * l2 * 1_000_000 + 4 * 9_869_604 * dt - 1) / (4 * 9_869_604 * dt);
                    println!("ZCAL2_SHEAR|Ly={ly}|T_q={tq}|nu2_micro=[{lo2},{hi2}]|json=0");
                    nu2.push((lo2, hi2));
                } else {
                    println!("ZCAL2_SHEAR|Ly={ly}|T_q=none|json=0");
                }
            }
        }
    }
    let k2 = halves.len() == 2 && 2 * halves[1] >= 7 * halves[0] && 2 * halves[1] <= 9 * halves[0];
    // sound
    for lx in [24usize, 36, 48, 60, 72] {
        let ticks = 8 * lx;
        let (d, ok) = sound(lx, &v, &g, ticks);
        k1 &= ok;
        for (t, x) in d.iter().enumerate() {
            if t % 4 == 0 {
                println!("ZCAL_SOUND_ROW|Lx={lx}|t={t}|D={x}|json=0");
            }
        }
        let sgn = |x: i64| x.signum();
        let mut cross = Vec::new();
        for t in 1..d.len() {
            if sgn(d[t]) != sgn(d[t - 1]) && sgn(d[t]) != 0 {
                cross.push(t as i64);
            }
        }
        if cross.len() < 5 {
            inconclusive = true;
            println!("ZCAL_SOUND|Lx={lx}|crossings={}|result=INCONCLUSIVE|json=0", cross.len());
            continue;
        }
        let num = 2 * lx as i64;
        let den = cross[4] - cross[0];
        println!(
            "ZCAL_SOUND|Lx={lx}|D0={}|t1={}|t5={}|c={num}/{den}|c_micro={}|crossings_first8={:?}|json=0",
            d[0],
            cross[0],
            cross[4],
            num * 1_000_000 / den,
            &cross[..cross.len().min(8)]
        );
    }
    let mut s2_ok = true;
    let mut s2_all = true;
    for lx in [24usize, 36, 48, 60, 72] {
        let (d, ok) = sound2(lx, &v, &g, 8 * lx);
        k1 &= ok;
        for (t, x) in d.iter().enumerate() {
            if t % 4 == 0 {
                println!("ZCAL2_SOUND_ROW|Lx={lx}|t={t}|D={x}|json=0");
            }
        }
        let mut cross = Vec::new();
        for t in 1..d.len() {
            if d[t].signum() != d[t - 1].signum() && d[t].signum() != 0 {
                cross.push(t as i64);
            }
        }
        if cross.len() < 5 {
            s2_all = false;
            println!("ZCAL2_SOUND|Lx={lx}|crossings={}|result=INCONCLUSIVE|json=0", cross.len());
            continue;
        }
        let (num, den) = (2 * lx as i64, cross[4] - cross[0]);
        s2_ok &= 2 * num >= den && 2 * num <= 3 * den;
        println!(
            "ZCAL2_SOUND|Lx={lx}|D0={}|c2={num}/{den}|c2_micro={}|crossings_first8={:?}|json=0",
            d[0],
            num * 1_000_000 / den,
            &cross[..cross.len().min(8)]
        );
    }
    let v2 = nu2.len() == 2 && {
        let (a, b) = (nu2[0], nu2[1]);
        let big = a.1.max(b.1);
        let diff = (a.0.max(b.0) - a.1.min(b.1)).max(0);
        diff * 100 < 15 * big
    };
    println!("ZCAL2_RESULT|V2={}|S2={}|json=0", pf(v2), if s2_all { pf(s2_ok) } else { "INCONCLUSIVE" });
    println!(
        "ZCAL_RESULT|K1={}|K2={}|K3={}|status={}|json=0",
        pf(k1),
        pf(k2),
        pf(k3),
        if inconclusive { "INCONCLUSIVE_PARTS" } else { "COMPLETE" }
    );
}
