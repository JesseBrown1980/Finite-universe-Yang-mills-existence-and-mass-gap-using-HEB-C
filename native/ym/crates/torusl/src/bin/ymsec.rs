//! Zero-momentum symmetry sectors of the FULL Lx x Ly S3 gauge-orbit
//! Hamiltonian (no vacuum-ball truncation). Integer-only, Rust 1.81.
//!
//! Group G = lattice translations (Lx*Ly) x C2v = {e, sx, sy, c2}:
//!   translation t : U'_mu(s + t) = U_mu(s)
//!   sx (x -> -x)  : U'_x(sx(s) - e_x) = U_x(s)^-1,  U'_y(sx(s)) = U_y(s)
//!   sy (y -> -y)  : U'_x(sy(s)) = U_x(s),  U'_y(sy(s) - e_y) = U_y(s)^-1
//!   c2 = sx sy.
//! H commutes with G: the electric term per link is a sum over the conjugacy
//! class of transpositions (invariant under U -> U^-1 and relabelling), the
//! magnetic term uses the real standard character (chi(U^-1) = chi(U)).
//! Sector (Sx, Sy): trivial character on translations (zero momentum),
//! chi(sx) = Sx, chi(sy) = Sy, chi(c2) = Sx*Sy. The four sectors together hold
//! the whole zero-momentum space; a D4 doublet appears as an equal-energy pair
//! across two of them.
//! Basis: one representative gauge orbit per G-orbit; G-orbits whose
//! stabiliser contains a character-odd element are dropped. Weight of a sector
//! state = (number of gauge orbits in its G-orbit) x (conjugation weight of the
//! representative). The sector operator is checked exactly to be W-self-adjoint
//! and written in the standard exchange format, so `cluster`, `sturmrs`,
//! `cluster_certify.py` and `jumpto` run on it unchanged.
//!
//! Structural checks (always run, on raw link configurations of sample states):
//!   group relations sx^2 = sy^2 = e, sx sy = sy sx = c2, and the semidirect
//!   relations sx t(a,b) sx = t(-a,b), sy t(a,b) sy = t(a,-b);
//!   commutation with H: for every op g, the electric move targets of g.x are
//!   exactly g applied to the move targets of x (as gauge orbits, with
//!   multiplicity), and the magnetic energy of g.x equals that of x.
//!   Sample size from YMSEC_CHECK_SAMPLES (0 = every gauge orbit; default 97).
//!
//! HEB-C additions: YMSEC_REFLECTIONS_ONLY=1 (G = C2v, every momentum) and
//! YMSEC_TRANS=x|y|d|a (translations along one line only; see main).
//!
//! usage: ymsec LX LY SX SY OUT_MATRIX        (SX, SY in {1, -1})     json=0
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::BTreeMap;
use std::io::Write;
use torusl::{Lat, G, TRANS};

#[derive(Clone, Copy)]
struct Op {
    tx: usize,
    ty: usize,
    p: u8, // 0 = e, 1 = sx, 2 = sy, 3 = c2
}

fn apply(g: &G, lat: &Lat, op: Op, u: &[u8]) -> Vec<u8> {
    let (lx, ly, n) = (lat.lx, lat.ly, lat.n);
    let mut out = vec![0u8; 2 * n];
    let fx = op.p == 1 || op.p == 3;
    let fy = op.p == 2 || op.p == 3;
    for x in 0..lx {
        for y in 0..ly {
            let s = lat.site(x, y);
            // point operation on the site
            let px = if fx { (lx - x) % lx } else { x };
            let py = if fy { (ly - y) % ly } else { y };
            let ux = u[s];
            let uy = u[n + s];
            // x-link
            let (dxx, vx) = if fx { ((px + lx - 1) % lx, g.i(ux)) } else { (px, ux) };
            // y-link
            let (dyy, vy) = if fy { ((py + ly - 1) % ly, g.i(uy)) } else { (py, uy) };
            // x-link lands at (dxx, py), y-link at (px, dyy); then translate
            let tx_site = lat.site((dxx + op.tx) % lx, (py + op.ty) % ly);
            let ty_site = lat.site((px + op.tx) % lx, (dyy + op.ty) % ly);
            out[tx_site] = vx;
            out[n + ty_site] = vy;
        }
    }
    out
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 6 {
        eprintln!("usage: ymsec LX LY SX SY OUT_MATRIX");
        std::process::exit(1);
    }
    let lx: usize = a[1].parse().unwrap_or(0);
    let ly: usize = a[2].parse().unwrap_or(0);
    let sxc: i64 = a[3].parse().unwrap_or(0);
    let syc: i64 = a[4].parse().unwrap_or(0);
    // HEB-C copy: the only change from 8fd12e6 is this guard, lx*ly <= 10 (was 9), to admit 2x5
    if !(2..=5).contains(&lx) || !(2..=5).contains(&ly) || lx * ly > 10 || sxc.abs() != 1 || syc.abs() != 1 {
        println!("YMSEC|error=bad_arguments|json=0");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    let g = G::new();
    let lat = Lat::new(lx, ly);
    let nl = 2 * lat.n;
    let k = lat.free.len();
    let tree = 6usize.pow(u32::try_from(k).unwrap_or(0));
    // gauge orbits: canonical keys and conjugation weights
    let mut is_key = vec![false; tree];
    for id in 0..tree {
        is_key[lat.canonical(&g, &lat.decode(id))] = true;
    }
    // HEB-C: YMSEC_REFLECTIONS_ONLY=1 uses G = C2v alone (no translations), so the
    // four sectors together span the WHOLE physical space, every momentum.
    let refl_only = std::env::var("YMSEC_REFLECTIONS_ONLY").as_deref() == Ok("1");
    // HEB-C: YMSEC_TRANS=x|y|d|a keeps only the translations along one line
    // K = {m*v}: v = (1,0), (0,1), (1,1) or (1,-1). The point operations kept are
    // those mapping K onto itself, so G' = K x| P is a group. Its sectors hold
    // V^K, the states invariant under K: the zero-momentum space plus the momenta
    // k with k.K = 0. Full space by Mobius inversion over these subgroups.
    let trans_mode = std::env::var("YMSEC_TRANS").unwrap_or_default();
    let trans: Vec<(usize, usize)> = match trans_mode.as_str() {
        "" => {
            let (tlx, tly) = if refl_only { (1, 1) } else { (lx, ly) };
            (0..tlx).flat_map(|tx| (0..tly).map(move |ty| (tx, ty))).collect()
        }
        "x" | "y" | "d" | "a" if !refl_only => {
            let v = match trans_mode.as_str() {
                "x" => (1, 0),
                "y" => (0, 1),
                "d" => (1, 1),
                _ => (1, ly - 1),
            };
            let mut set: Vec<(usize, usize)> = (0..lx * ly).map(|m| ((m * v.0) % lx, (m * v.1) % ly)).collect();
            set.sort_unstable();
            set.dedup();
            set
        }
        _ => {
            println!("YMSEC|error=bad_YMSEC_TRANS|json=0");
            std::process::exit(1);
        }
    };
    let point_image = |p: u8, (tx, ty): (usize, usize)| -> (usize, usize) {
        let fx = p == 1 || p == 3;
        let fy = p == 2 || p == 3;
        (if fx { (lx - tx) % lx } else { tx }, if fy { (ly - ty) % ly } else { ty })
    };
    let points: Vec<u8> = (0..4u8).filter(|&p| trans.iter().all(|&t| trans.contains(&point_image(p, t)))).collect();
    // canonical sector labels: a character value of an absent reflection must be +1
    let has = |p: u8| points.contains(&p);
    if (!has(1) && !has(3) && sxc != 1) || (!has(2) && !has(3) && syc != 1) || (!has(1) && !has(2) && has(3) && sxc != 1) {
        println!("YMSEC|error=noncanonical_sector_for_point_group|json=0");
        std::process::exit(1);
    }
    let ops: Vec<Op> = points
        .iter()
        .flat_map(|&p| trans.iter().map(move |&(tx, ty)| Op { tx, ty, p }))
        .collect();
    let chi = |op: &Op| -> i64 {
        match op.p {
            0 => 1,
            1 => sxc,
            2 => syc,
            _ => sxc * syc,
        }
    };
    let key_of = |raw: &[u8]| lat.canonical(&g, &lat.gauge_fix(&g, raw));
    // ---- structural checks on sample states (raw configurations) ----
    // sample size: YMSEC_CHECK_SAMPLES (0 = every gauge orbit, exhaustive); default 97
    let want_samples: usize = std::env::var("YMSEC_CHECK_SAMPLES").ok().and_then(|v| v.parse().ok()).unwrap_or(97);
    let all_keys: Vec<usize> = (0..tree).filter(|&id| is_key[id]).collect();
    let samples: Vec<usize> = if want_samples == 0 || want_samples >= all_keys.len() {
        all_keys
    } else {
        let step = (all_keys.len() / want_samples).max(1);
        all_keys.into_iter().step_by(step).take(want_samples).collect()
    };
    let opx = |tx: usize, ty: usize, p: u8| Op { tx, ty, p };
    let check = |keys: &[usize]| -> (bool, bool) {
    let mut rel_ok = true;
    let mut comm_ok = true;
    for &key in keys {
        let u = lat.representative(&lat.decode(key));
        let e = |op: Op, v: &[u8]| apply(&g, &lat, op, v);
        let sx = opx(0, 0, 1);
        let sy = opx(0, 0, 2);
        let c2 = opx(0, 0, 3);
        rel_ok &= e(sx, &e(sx, &u)) == u && e(sy, &e(sy, &u)) == u;
        rel_ok &= e(sx, &e(sy, &u)) == e(c2, &u) && e(sy, &e(sx, &u)) == e(c2, &u);
        for tx in 0..lx {
            for ty in 0..ly {
                let t = opx(tx, ty, 0);
                let tmx = opx((lx - tx) % lx, ty, 0);
                let tmy = opx(tx, (ly - ty) % ly, 0);
                rel_ok &= e(sx, &e(t, &e(sx, &u))) == e(tmx, &u);
                rel_ok &= e(sy, &e(t, &e(sy, &u))) == e(tmy, &u);
            }
        }
        // commutation with H
        let moves = |v: &[u8]| -> Vec<usize> {
            let mut out = Vec::with_capacity(3 * nl);
            for l in 0..nl {
                for &t in &TRANS {
                    let mut w = v.to_vec();
                    w[l] = g.m(t, w[l]);
                    out.push(key_of(&w));
                }
            }
            out.sort_unstable();
            out
        };
        let mx = moves(&u);
        let mag_u = lat.magnetic(&g, &u);
        for op in &ops {
            let gu = e(*op, &u);
            if lat.magnetic(&g, &gu) != mag_u {
                comm_ok = false;
            }
            let mut mapped: Vec<usize> = Vec::with_capacity(mx.len());
            for l in 0..nl {
                for &t in &TRANS {
                    let mut w = u.clone();
                    w[l] = g.m(t, w[l]);
                    mapped.push(key_of(&e(*op, &w)));
                }
            }
            mapped.sort_unstable();
            if mapped != moves(&gu) {
                comm_ok = false;
            }
        }
    }
    (rel_ok, comm_ok)
    };
    // targeted samples: the flat vacua (commuting holonomy pairs on the seams)
    // and the lowest-code gauge orbits (near-identity configurations)
    let mut special: Vec<usize> = Vec::new();
    for ha in 0..6u8 {
        for hb in 0..6u8 {
            if g.m(ha, hb) != g.m(hb, ha) {
                continue;
            }
            let mut links = vec![0u8; nl];
            for y in 0..ly {
                links[lat.site(lx - 1, y)] = ha;
            }
            for x in 0..lx {
                links[lat.n + lat.site(x, ly - 1)] = hb;
            }
            special.push(key_of(&links));
        }
    }
    special.extend((0..tree).filter(|&id| is_key[id]).take(100));
    special.sort_unstable();
    special.dedup();
    let (r1, c1) = check(&samples);
    let (r2, c2) = check(&special);
    let rel_ok = r1 && r2;
    let comm_ok = c1 && c2;
    if !(rel_ok && comm_ok) {
        println!("YMSEC|error=structural_check_failed|group_relations={}|commutes_with_H={}|json=0", u8::from(rel_ok), u8::from(comm_ok));
        std::process::exit(2);
    }
    // sector orbits
    const NONE: u32 = u32::MAX;
    let mut rep_of = vec![NONE; tree];
    let mut sgn = vec![0i8; tree]; // 0 unvisited, 2 dropped, +-1 sign
    let mut reps: Vec<usize> = Vec::new();
    let mut wts: Vec<i64> = Vec::new();
    let mut gauge_orbits = 0usize;
    let mut flat_states = 0usize;
    let mut mags: Vec<i64> = Vec::new();
    for key in 0..tree {
        if !is_key[key] {
            continue;
        }
        gauge_orbits += 1;
        if sgn[key] != 0 {
            continue;
        }
        let raw = lat.representative(&lat.decode(key));
        let mut img: BTreeMap<usize, i64> = BTreeMap::new();
        let mut dropped = false;
        for op in &ops {
            let j = key_of(&apply(&g, &lat, *op, &raw));
            let c = chi(op);
            match img.get(&j) {
                Some(&old) if old != c => dropped = true,
                Some(_) => {}
                None => {
                    img.insert(j, c);
                }
            }
        }
        if dropped {
            for &j in img.keys() {
                sgn[j] = 2;
            }
            continue;
        }
        let first = *img.keys().next().unwrap_or(&key);
        let cf = img[&first];
        let r = u32::try_from(reps.len()).unwrap_or(NONE);
        for (&j, &c) in &img {
            rep_of[j] = r;
            sgn[j] = i8::try_from(c * cf).unwrap_or(0);
        }
        let q = lat.decode(first);
        let m = lat.magnetic(&g, &lat.representative(&q));
        if m == 0 {
            flat_states += 1;
        }
        reps.push(first);
        mags.push(m);
        wts.push(i64::try_from(img.len()).unwrap_or(0) * lat.weight(&g, &q));
    }
    let n = reps.len();
    // traces of the reflections on the gauge-orbit space (fixed gauge orbits), and
    // the character formula d_s = (d + Sx Tr Rx + Sy Tr Ry + SxSy Tr Rc2) / |G|,
    // checked only when G = C2v (otherwise translations enter the formula)
    let (mut fx, mut fy, mut fc) = (0i64, 0i64, 0i64);
    // subgroup sectors: d_s = (1/|G'|) sum over G' of chi(g) * #(gauge orbits fixed by g)
    let mut sub_num: i64 = 0;
    if !trans_mode.is_empty() {
        for (key, _) in is_key.iter().enumerate().filter(|(_, &k)| k) {
            let raw = lat.representative(&lat.decode(key));
            for op in &ops {
                if key_of(&apply(&g, &lat, *op, &raw)) == key {
                    sub_num += chi(op);
                }
            }
        }
    }
    if refl_only {
        for (key, _) in is_key.iter().enumerate().filter(|(_, &k)| k) {
            let raw = lat.representative(&lat.decode(key));
            fx += i64::from(key_of(&apply(&g, &lat, opx(0, 0, 1), &raw)) == key);
            fy += i64::from(key_of(&apply(&g, &lat, opx(0, 0, 2), &raw)) == key);
            fc += i64::from(key_of(&apply(&g, &lat, opx(0, 0, 3), &raw)) == key);
        }
    }
    let go = i64::try_from(gauge_orbits).unwrap_or(0);
    let pred_num = go + sxc * fx + syc * fy + sxc * syc * fc;
    let gsize = i64::try_from(ops.len()).unwrap_or(0);
    let dims_ok = if refl_only {
        pred_num % 4 == 0 && pred_num / 4 == i64::try_from(n).unwrap_or(-1)
    } else if !trans_mode.is_empty() {
        sub_num % gsize == 0 && sub_num / gsize == i64::try_from(n).unwrap_or(-1)
    } else {
        true
    };
    // structural check on representatives with a nontrivial stabiliser
    let stab_keys: Vec<usize> = reps.iter().zip(wts.iter()).filter(|&(&k, &w)| {
        let gw = lat.weight(&g, &lat.decode(k));
        w / gw.max(1) < i64::try_from(ops.len()).unwrap_or(0)
    }).map(|(&k, _)| k).take(200).collect();
    let (r3, c3) = check(&stab_keys);
    if !(r3 && c3) {
        println!("YMSEC|error=structural_check_failed_on_stabiliser_states|json=0");
        std::process::exit(2);
    }
    let special_n = special.len() + stab_keys.len();
    // sector electric rows (diagonal 3*nl, -chi per move into the sector)
    let mut rows: Vec<BTreeMap<u32, i64>> = Vec::with_capacity(n);
    for (i, &key) in reps.iter().enumerate() {
        let raw = lat.representative(&lat.decode(key));
        let mut row: BTreeMap<u32, i64> = BTreeMap::new();
        *row.entry(u32::try_from(i).unwrap_or(NONE)).or_insert(0) += 3 * i64::try_from(nl).unwrap_or(0);
        for e in 0..nl {
            for &t in &TRANS {
                let mut nx = raw.clone();
                nx[e] = g.m(t, nx[e]);
                let j = key_of(&nx);
                if rep_of[j] == NONE {
                    continue;
                }
                *row.entry(rep_of[j]).or_insert(0) -= i64::from(sgn[j]);
            }
        }
        row.retain(|_, v| *v != 0);
        rows.push(row);
    }
    // exact W-self-adjointness
    let mut sa = true;
    for (i, row) in rows.iter().enumerate() {
        for (&c, &z) in row {
            let back = rows[c as usize].get(&u32::try_from(i).unwrap_or(NONE)).copied().unwrap_or(0);
            if wts[i] * z != wts[c as usize] * back {
                sa = false;
            }
        }
    }
    let f = std::fs::File::create(&a[5]).unwrap_or_else(|e| {
        println!("YMSEC|error=write:{e}|json=0");
        std::process::exit(1)
    });
    let mut out = std::io::BufWriter::new(f);
    let join = |v: &[i64]| v.iter().map(i64::to_string).collect::<Vec<_>>().join(" ");
    let mut ok = writeln!(out, "{n}").is_ok();
    ok &= writeln!(out, "{}", join(&wts)).is_ok();
    ok &= writeln!(out, "{}", join(&mags)).is_ok();
    let mut nnz = 0usize;
    for (i, row) in rows.iter().enumerate() {
        for (&c, &z) in row {
            nnz += 1;
            if c as usize >= i {
                ok &= writeln!(out, "{i} {c} {z}").is_ok();
            }
        }
    }
    ok &= out.flush().is_ok();
    println!(
        "YMSEC|L={lx}x{ly}|sector=Sx{}Sy{}|group={}|momenta={}|gauge_orbits={gauge_orbits}|sector_states={n}|trace_Rx={fx}|trace_Ry={fy}|trace_Rc2={fc}|character_formula_dim={}|flat_states={flat_states}|nnz={nnz}|group_relations=PASS|commutes_with_H=PASS|structural_samples={}|targeted_samples={special_n}|w_self_adjoint={}|write={}|ms={}|json=0",
        if sxc > 0 { "+" } else { "-" },
        if syc > 0 { "+" } else { "-" },
        ops.len(),
        if refl_only {
            "all".to_string()
        } else if trans_mode.is_empty() {
            "zero".to_string()
        } else {
            format!("line_{trans_mode}_points_{}", points.iter().map(u8::to_string).collect::<String>())
        },
        if refl_only || !trans_mode.is_empty() {
            if dims_ok { "PASS".to_string() } else { "FAIL".to_string() }
        } else {
            "n/a".to_string()
        },
        samples.len(),
        if sa { "PASS" } else { "FAIL" },
        if ok { "ok" } else { "failed" },
        t0.elapsed().as_millis()
    );
    if !sa || !ok || !dims_ok {
        std::process::exit(2);
    }
}
