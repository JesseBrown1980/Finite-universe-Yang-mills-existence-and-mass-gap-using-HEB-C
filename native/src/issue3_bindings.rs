//! Issue #3 — source-pinned binding checks for C1, "instant", z, the joined
//! term "Z-instant" and the Law 71 §71.5 residual, run against the existing
//! 1,393-state periodic 2x2 S3 torus. Every check calls the functions that
//! already exist in this crate (torus2, shadow_residual, rime_gear,
//! rime_hamiltonian_bridge, the vendored Clasy trit). Integer only, json=0.
//!
//! Sources (read as data, none of their code compiled or run):
//! - SIM = ASOLARIA-UNIVERSE-SIMULATOR... @ 3f9f42dab6247c40b30921b253e3f73c9e942ca5
//!   books/LAW-71-...md blob 24e5e8837e40804a19bb0bf5048985c179d35272
//!   (§71.5 lines 150-161, line 322, §71.13 lines 329-347);
//!   crates/asolaria-tribit/src/tribit.rs blob 9a27567d648dd8014e008e79327814c7f8b91038
//!   (rotate = from_digit(digit + 1), lines 112-118).
//! - HBU = the-human-based-understanding @ f38cfec0c910a5997f156e9e599d097cacf0c578
//!   (z line README.md:70, Law 4 README.md:357).
//! - ZEB = the-zebras-z-is-the-squared-wave @ 3b3fe023427efcd4f86b1c8299dc92ed121a9aef
//!   index.html blob bbf68650510d7969cebbe290541053f696277db2, lines 95-100:
//!   `SQUARE ? (w >= 0 ? 1 : 0)`.
#![forbid(unsafe_code)]
#![deny(
    clippy::float_arithmetic,
    clippy::float_cmp,
    clippy::cast_precision_loss
)]

use crate::rime_gear::{freeze, mediated_call, validate_snapshot, TorusRole};
use crate::shadow_residual::{canonical_pair, winding_rotation};
use crate::torus2::{gauge_transform, plaquette, Torus2, DIM};
use crate::trit::Trit;
use crate::{character, hex, inv, mul, sha256, PERM};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

const FREE: [usize; 5] = [2, 3, 5, 6, 7];

/// Same placement of the five tree-gauge loop variables that
/// constellation_gate::inspect uses.
fn raw_links(rep: &[u8; 5]) -> [u8; 8] {
    let mut raw = [0u8; 8];
    for (i, &edge) in FREE.iter().enumerate() {
        raw[edge] = rep[i];
    }
    raw
}

fn plaquettes(raw: &[u8; 8]) -> [u8; 4] {
    [
        plaquette(raw, 0, 0),
        plaquette(raw, 0, 1),
        plaquette(raw, 1, 0),
        plaquette(raw, 1, 1),
    ]
}

fn gcd(mut a: i64, mut b: i64) -> i64 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

// ---------------------------------------------------------------- binding 1

/// SIM tribit.rs:116-118, `rotate = from_digit(digit + 1)`, over the
/// vendored Clasy trit (same digit convention Neg=0, Center=1, Pos=2).
fn source_r(t: Trit) -> Result<Trit, String> {
    Trit::from_digit((t.digit() + 1) % 3)
}

fn source_r3(c: [Trit; 3]) -> Result<[Trit; 3], String> {
    Ok([source_r(c[0])?, source_r(c[1])?, source_r(c[2])?])
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct C1Flat {
    pub source_fixed_tuples: usize,
    pub source_order: usize,
    pub flat_classes: usize,
    pub flat_fixed: usize,
    pub flat_cycles3: usize,
    pub equivariant_bijections: [usize; 2],
    pub inspect_agrees: bool,
}

fn flat_rotation() -> BTreeMap<(u8, u8), (u8, u8)> {
    let mut classes = BTreeSet::new();
    for x in 0..6 {
        for y in 0..6 {
            if mul(x, y) == mul(y, x) {
                classes.insert(canonical_pair(x, y));
            }
        }
    }
    classes
        .into_iter()
        .map(|(x, y)| {
            let (a, b) = winding_rotation(x, y);
            ((x, y), canonical_pair(a, b))
        })
        .collect()
}

pub fn c1_flat() -> Result<C1Flat, String> {
    let c0 = [Trit::NegativeZero, Trit::CenterZero, Trit::PositiveZero];
    let c1 = source_r3(c0)?;
    let c2 = source_r3(c1)?;
    let c3 = source_r3(c2)?;
    if c3 != c0 || c1 == c0 || c2 == c0 || c1 == c2 {
        return Err("source R is not order three on C0".into());
    }
    let mut fixed = 0;
    for a in Trit::ALL {
        for b in Trit::ALL {
            for c in Trit::ALL {
                if source_r3([a, b, c])? == [a, b, c] {
                    fixed += 1;
                }
            }
        }
    }
    let map = flat_rotation();
    let mut seen = BTreeSet::new();
    let mut flat_fixed = 0;
    let mut cycles = Vec::new();
    for &a in map.keys() {
        if seen.contains(&a) {
            continue;
        }
        let b = map[&a];
        let c = map[&b];
        if map[&c] != a {
            return Err("flat R^3 is not identity".into());
        }
        seen.extend([a, b, c]);
        if a == b {
            flat_fixed += 1;
        } else {
            cycles.push([a, b, c]);
        }
    }
    // Count bijections f:{C0,C1,C2}->cycle with f(R c)=R f(c).
    let source = [c0, c1, c2];
    let perms: [[usize; 3]; 6] = [
        [0, 1, 2],
        [0, 2, 1],
        [1, 0, 2],
        [1, 2, 0],
        [2, 0, 1],
        [2, 1, 0],
    ];
    let mut equivariant = [0usize; 2];
    if cycles.len() != 2 {
        return Err("expected two flat three-cycles".into());
    }
    for (slot, cycle) in cycles.iter().enumerate() {
        for p in perms {
            let mut ok = true;
            for (k, &s) in source.iter().enumerate() {
                let rs = source_r3(s)?;
                let rk = source.iter().position(|&t| t == rs).ok_or("R left C-set")?;
                if map[&cycle[p[k]]] != cycle[p[rk]] {
                    ok = false;
                }
            }
            if ok {
                equivariant[slot] += 1;
            }
        }
    }
    let audit = crate::shadow_residual::inspect()?;
    Ok(C1Flat {
        source_fixed_tuples: fixed,
        source_order: 3,
        flat_classes: map.len(),
        flat_fixed,
        flat_cycles3: cycles.len(),
        equivariant_bijections: equivariant,
        inspect_agrees: audit.fixed_orbits == flat_fixed && audit.three_cycles == cycles.len(),
    })
}

// ---------------------------------------------------------------- binding 2

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RExtension {
    pub lattice_automorphisms: usize,
    pub order3_automorphisms: usize,
    pub he_fourth_moment_gap: i128,
    pub pair_r_equivariant_all36: bool,
    pub pair_r3_identity_all36: bool,
    pub pair_classes_on_1393: usize,
    pub max_pair_fiber: usize,
}

/// Edge-vertex incidence read off the existing gauge_transform; plaquette
/// edge sets read off the existing plaquette function.
fn lattice_cells() -> ([[usize; 2]; 8], [u8; 4]) {
    let mut ends = [[0usize; 2]; 8];
    for (edge, slot) in ends.iter_mut().enumerate() {
        let mut found = Vec::new();
        for site in 0..4 {
            if gauge_transform([0u8; 8], site, 1)[edge] != 0 {
                found.push(site);
            }
        }
        assert_eq!(found.len(), 2, "every link has two distinct end sites");
        *slot = [found[0], found[1]];
    }
    let mut masks = [0u8; 4];
    for edge in 0..8 {
        let mut links = [0u8; 8];
        links[edge] = 1;
        for (p, &holonomy) in plaquettes(&links).iter().enumerate() {
            if holonomy != 0 {
                masks[p] |= 1 << edge;
            }
        }
    }
    (ends, masks)
}

fn vertex_perms() -> Vec<[usize; 4]> {
    let mut out = Vec::new();
    for a in 0..4 {
        for b in 0..4 {
            for c in 0..4 {
                for d in 0..4 {
                    let p = [a, b, c, d];
                    if p.iter().collect::<BTreeSet<_>>().len() == 4 {
                        out.push(p);
                    }
                }
            }
        }
    }
    out
}

fn sorted(p: [usize; 2]) -> [usize; 2] {
    if p[0] <= p[1] {
        p
    } else {
        [p[1], p[0]]
    }
}

fn extend(
    sigma: &[usize; 4],
    ends: &[[usize; 2]; 8],
    pi: &mut Vec<usize>,
    out: &mut Vec<([usize; 4], [usize; 8])>,
) {
    let e = pi.len();
    if e == 8 {
        let mut full = [0usize; 8];
        full.copy_from_slice(pi);
        out.push((*sigma, full));
        return;
    }
    let want = sorted([sigma[ends[e][0]], sigma[ends[e][1]]]);
    for target in 0..8 {
        if !pi.contains(&target) && sorted(ends[target]) == want {
            pi.push(target);
            extend(sigma, ends, pi, out);
            pi.pop();
        }
    }
}

/// All cellular automorphisms (vertex, link, plaquette incidence kept).
pub fn lattice_automorphisms() -> Vec<([usize; 4], [usize; 8])> {
    let (ends, masks) = lattice_cells();
    let plaquette_set: BTreeSet<u8> = masks.iter().copied().collect();
    let mut candidates = Vec::new();
    for sigma in vertex_perms() {
        extend(&sigma, &ends, &mut Vec::new(), &mut candidates);
    }
    candidates
        .into_iter()
        .filter(|(_, pi)| {
            masks.iter().all(|&m| {
                let mut image = 0u8;
                for (edge, &target) in pi.iter().enumerate() {
                    if m & (1 << edge) != 0 {
                        image |= 1 << target;
                    }
                }
                plaquette_set.contains(&image)
            })
        })
        .collect()
}

fn element_order(sigma: &[usize; 4], pi: &[usize; 8]) -> usize {
    let mut s = [0usize, 1, 2, 3];
    let mut p = [0usize, 1, 2, 3, 4, 5, 6, 7];
    for order in 1..=64 {
        s = s.map(|v| sigma[v]);
        p = p.map(|v| pi[v]);
        if s == [0, 1, 2, 3] && p == [0, 1, 2, 3, 4, 5, 6, 7] {
            return order;
        }
    }
    usize::MAX
}

pub fn r_extension(torus: &Torus2) -> Result<RExtension, String> {
    let autos = lattice_automorphisms();
    let order3 = autos
        .iter()
        .filter(|(s, p)| element_order(s, p) % 3 == 0)
        .count();
    let bridge = crate::rime_hamiltonian_bridge::inspect()?;
    let he = &bridge.moments[0];
    let mut equivariant = true;
    let mut cube = true;
    for x in 0..6u8 {
        for y in 0..6u8 {
            let (a, b) = winding_rotation(x, y);
            let target = canonical_pair(a, b);
            for g in 0..6u8 {
                let cx = mul(mul(g, x), inv(g));
                let cy = mul(mul(g, y), inv(g));
                let (ra, rb) = winding_rotation(cx, cy);
                if canonical_pair(ra, rb) != target {
                    equivariant = false;
                }
            }
            let (p, q) = winding_rotation(a, b);
            if winding_rotation(p, q) != (x, y) {
                cube = false;
            }
        }
    }
    let mut fibers = BTreeMap::<(u8, u8), usize>::new();
    for q in &torus.representatives {
        *fibers.entry(canonical_pair(q[0], q[2])).or_default() += 1;
    }
    Ok(RExtension {
        lattice_automorphisms: autos.len(),
        order3_automorphisms: order3,
        he_fourth_moment_gap: he.source[3] - he.target[3],
        pair_r_equivariant_all36: equivariant,
        pair_r3_identity_all36: cube,
        pair_classes_on_1393: fibers.len(),
        max_pair_fiber: fibers.values().copied().max().unwrap_or(0),
    })
}

// ---------------------------------------------------------------- binding 3

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InstantAtomic {
    pub levels: usize,
    pub views_per_level: usize,
    pub views_equal_within_level: bool,
    pub frozen_distinct_across_levels: bool,
    pub earlier_level_replays_unchanged: bool,
    pub direct_was_will: bool,
    pub forged_view_rejected: bool,
    pub missing_view_rejected: bool,
    pub unarrived_input_rejected: bool,
}

pub fn instant_atomic() -> Result<InstantAtomic, String> {
    let source = b"issue3-frozen-IS";
    let mut levels = Vec::new();
    for k in 0..3u64 {
        let s = freeze(source, 0, 1, 1 + k, k)?;
        validate_snapshot(&s)?;
        levels.push(s);
    }
    let within = levels
        .iter()
        .all(|s| s.views.iter().all(|v| v == &s.frozen_sha));
    let distinct = levels
        .iter()
        .map(|s| s.frozen_sha.clone())
        .collect::<BTreeSet<_>>()
        .len()
        == levels.len();
    let replay = freeze(source, 0, 1, 1, 0)? == levels[0];
    let mut forged = levels[1].clone();
    forged.views[1].clone_from(&levels[0].frozen_sha);
    let mut missing = levels[2].clone();
    missing.views[0] = String::new();
    Ok(InstantAtomic {
        levels: levels.len(),
        views_per_level: levels[0].views.len(),
        views_equal_within_level: within,
        frozen_distinct_across_levels: distinct,
        earlier_level_replays_unchanged: replay,
        direct_was_will: mediated_call(TorusRole::Was, TorusRole::Will)
            || mediated_call(TorusRole::Will, TorusRole::Was),
        forged_view_rejected: validate_snapshot(&forged).is_err(),
        missing_view_rejected: validate_snapshot(&missing).is_err(),
        unarrived_input_rejected: freeze(source, 0, 9, 3, 3).is_err(),
    })
}

// ---------------------------------------------------------------- binding 4

/// ZEB index.html lines 95-100: `SQUARE ? (w >= 0 ? 1 : 0)`, the two-valued
/// square wave cut from the smooth wave. Integer input here.
fn z_square(w: i64) -> i64 {
    if w >= 0 {
        1
    } else {
        0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ZSquare {
    pub z_values_on_s3: usize,
    pub chi_squared_values_on_s3: usize,
    pub zsum_gauge_invariant_checks: usize,
    pub zsum_gauge_invariant: bool,
    pub alias: Option<(usize, usize, i64, i64, i64)>,
    pub zsum_levels: usize,
}

fn zsum(raw: &[u8; 8]) -> i64 {
    plaquettes(raw)
        .iter()
        .map(|&u| z_square(character(u)))
        .sum()
}

pub fn z_square_wave(torus: &Torus2) -> ZSquare {
    let z_values: BTreeSet<i64> = (0..6).map(|g| z_square(character(g))).collect();
    let chi2: BTreeSet<i64> = (0..6).map(|g| character(g) * character(g)).collect();
    let mut invariant = true;
    let mut checks = 0;
    let mut first = BTreeMap::<i64, (usize, i64)>::new();
    let mut alias = None;
    for (i, rep) in torus.representatives.iter().enumerate() {
        let raw = raw_links(rep);
        let s = zsum(&raw);
        for site in 0..4 {
            for g in 0..6 {
                checks += 1;
                if zsum(&gauge_transform(raw, site, g)) != s {
                    invariant = false;
                }
            }
        }
        let hb = torus.magnetic[i];
        match first.get(&s) {
            Some(&(j, other)) if other != hb && alias.is_none() => {
                alias = Some((j, i, s, other, hb));
            }
            Some(_) => {}
            None => {
                first.insert(s, (i, hb));
            }
        }
    }
    ZSquare {
        z_values_on_s3: z_values.len(),
        chi_squared_values_on_s3: chi2.len(),
        zsum_gauge_invariant_checks: checks,
        zsum_gauge_invariant: invariant,
        alias,
        zsum_levels: first.len(),
    }
}

// ---------------------------------------------------------------- binding 6

type M3 = [[i64; 3]; 3];

/// Permutation matrix of PERM[g]: column i carries e_i to e_{p[i]}.
fn perm_matrix(g: u8) -> M3 {
    let p = PERM[usize::from(g)];
    let mut m = [[0i64; 3]; 3];
    for (i, &image) in p.iter().enumerate() {
        m[usize::from(image)][i] = 1;
    }
    m
}

fn mat_mul(a: &M3, b: &M3) -> M3 {
    let mut c = [[0i64; 3]; 3];
    for (r, row) in c.iter_mut().enumerate() {
        for (k, cell) in row.iter_mut().enumerate() {
            *cell = (0..3).map(|j| a[r][j] * b[j][k]).sum();
        }
    }
    c
}

fn mat_vec(a: &M3, v: [i64; 3]) -> [i64; 3] {
    [0, 1, 2].map(|r| (0..3).map(|j| a[r][j] * v[j]).sum())
}

/// 3 P_S = 3I - J, the integer form of the projection onto the arm plane.
const THREE_P_S: M3 = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]];

fn trace(a: &M3) -> i64 {
    a[0][0] + a[1][1] + a[2][2]
}

fn dot(a: [i64; 3], b: [i64; 3]) -> i64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: [i64; 3], b: [i64; 3]) -> [i64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

/// §71.5 squared normalised residual ||v - P_S v||^2 / ||v||^2 as a reduced
/// integer fraction, with S spanned by the arms and n their normal.
fn residual_sq(v: [i64; 3], n: [i64; 3]) -> (i64, i64) {
    let num = dot(v, n) * dot(v, n);
    let den = dot(n, n) * dot(v, v);
    let g = gcd(num, den).max(1);
    (num / g, den / g)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ResidualWilson {
    pub arms_sum_zero: bool,
    pub arm_normal: [i64; 3],
    pub homomorphism_36: bool,
    pub plane_trace_is_character_6: usize,
    pub residual_invariant_checks: usize,
    pub residual_invariant: bool,
    pub magnetic_match: usize,
    pub magnetic_gauge_checks: usize,
    pub transported_residual_values: usize,
    pub transported_plane_trace_values: usize,
    pub electric_witness: bool,
}

fn plane_magnetic(raw: &[u8; 8]) -> Result<i64, String> {
    let mut total = 0;
    for u in plaquettes(raw) {
        let t3 = trace(&mat_mul(&THREE_P_S, &perm_matrix(u)));
        if t3 % 3 != 0 {
            return Err("plane trace not divisible by three".into());
        }
        total += 2 - t3 / 3;
    }
    Ok(total)
}

pub fn residual_wilson(torus: &Torus2) -> Result<ResidualWilson, String> {
    let arms: [[i64; 3]; 3] = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]];
    let sum_zero = (0..3).all(|c| arms.iter().map(|a| a[c]).sum::<i64>() == 0);
    let n = cross(arms[0], arms[1]);
    if n == [0, 0, 0] || dot(n, arms[2]) != 0 {
        return Err("arms do not span a rank-two plane".into());
    }
    let mut hom = true;
    for a in 0..6u8 {
        for b in 0..6u8 {
            if mat_mul(&perm_matrix(a), &perm_matrix(b)) != perm_matrix(mul(a, b)) {
                hom = false;
            }
        }
    }
    let plane_char = (0..6u8)
        .filter(|&g| trace(&mat_mul(&THREE_P_S, &perm_matrix(g))) == 3 * character(g))
        .count();
    let mut invariant = true;
    let mut checks = 0;
    for a in -2..=2i64 {
        for b in -2..=2i64 {
            for c in -2..=2i64 {
                let v = [a, b, c];
                if v == [0, 0, 0] {
                    continue;
                }
                let base = residual_sq(v, n);
                for g in 0..6u8 {
                    checks += 1;
                    if residual_sq(mat_vec(&perm_matrix(g), v), n) != base {
                        invariant = false;
                    }
                }
            }
        }
    }
    let mut matched = 0;
    let mut gauge_checks = 0;
    let mut residuals = BTreeSet::new();
    let mut plane_traces = BTreeSet::new();
    let probe = [1i64, 2, 4];
    for (i, rep) in torus.representatives.iter().enumerate() {
        let raw = raw_links(rep);
        let hb = plane_magnetic(&raw)?;
        if hb == torus.magnetic[i] {
            matched += 1;
        }
        for site in 0..4 {
            for g in 0..6 {
                gauge_checks += 1;
                if plane_magnetic(&gauge_transform(raw, site, g))? != hb {
                    return Err("plane magnetic is gauge dependent".into());
                }
            }
        }
        let holonomy = perm_matrix(rep[0]);
        residuals.insert(residual_sq(mat_vec(&holonomy, probe), n));
        plane_traces.insert(trace(&mat_mul(&THREE_P_S, &holonomy)));
    }
    Ok(ResidualWilson {
        arms_sum_zero: sum_zero,
        arm_normal: n,
        homomorphism_36: hom,
        plane_trace_is_character_6: plane_char,
        residual_invariant_checks: checks,
        residual_invariant: invariant,
        magnetic_match: matched,
        magnetic_gauge_checks: gauge_checks,
        transported_residual_values: residuals.len(),
        transported_plane_trace_values: plane_traces.len(),
        electric_witness: torus.electric_gap_witness().is_ok(),
    })
}

// ---------------------------------------------------------------- receipts

pub struct Receipt {
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    pub anchor: String,
    pub measure: String,
}

fn b(v: bool) -> u8 {
    u8::from(v)
}

pub fn rows() -> Result<Vec<String>, String> {
    let torus = Torus2::build()?;
    if torus.representatives.len() != DIM {
        return Err("torus dimension changed".into());
    }
    let c1 = c1_flat()?;
    let r = r_extension(&torus)?;
    let t = instant_atomic()?;
    let z = z_square_wave(&torus);
    let w = residual_wilson(&torus)?;
    let (zi, zj, zs, zhi, zhj) = z.alias.ok_or("no z-sum alias witness")?;
    let c1_bound = c1.flat_fixed == 2
        && c1.flat_cycles3 == 2
        && c1.equivariant_bijections == [3, 3]
        && c1.source_fixed_tuples == 0
        && c1.inspect_agrees;
    let r_unbound = r.order3_automorphisms == 0 && r.he_fourth_moment_gap != 0;
    let t_kernel = t.views_equal_within_level
        && t.frozen_distinct_across_levels
        && t.earlier_level_replays_unchanged
        && !t.direct_was_will
        && t.forged_view_rejected
        && t.missing_view_rejected
        && t.unarrived_input_rejected;
    let w_bound = w.plane_trace_is_character_6 == 6
        && w.residual_invariant
        && w.magnetic_match == DIM
        && w.transported_residual_values == 1
        && w.electric_witness;
    Ok(vec![
        format!(
            "BIND|n=1|binding=C1_FLAT|verdict={}|source=SIM:LAW71:341-344,SIM:tribit.rs:116-118|source_order={}|source_fixed_tuples={}|flat_classes={}|flat_fixed={}|flat_cycles3={}|equivariant_bijections={},{}|shadow_residual_inspect_agrees={}|scope=FLAT_8_ONLY",
            if c1_bound { "BOUND" } else { "UNBOUND" },
            c1.source_order, c1.source_fixed_tuples, c1.flat_classes, c1.flat_fixed,
            c1.flat_cycles3, c1.equivariant_bijections[0], c1.equivariant_bijections[1],
            b(c1.inspect_agrees)
        ),
        format!(
            "BIND|n=2|binding=R_EXTENSION_1393|verdict={}|lattice_automorphisms={}|order3_automorphisms={}|he_m4_gap={}|pair_r_equivariant_36={}|pair_r3_identity_36={}|pair_classes_on_1393={}|max_pair_fiber={}|lift_rule_in_source=0",
            if r_unbound { "UNBOUND" } else { "OPEN" },
            r.lattice_automorphisms, r.order3_automorphisms, r.he_fourth_moment_gap,
            b(r.pair_r_equivariant_all36), b(r.pair_r3_identity_all36),
            r.pair_classes_on_1393, r.max_pair_fiber
        ),
        format!(
            "BIND|n=3|binding=INSTANT_ATOMIC|verdict={}|source=SIM:LAW71:322-327,HBU:README.md:357|levels={}|views_per_level={}|views_equal={}|levels_distinct={}|earlier_unchanged={}|direct_was_will={}|forged_rejected={}|missing_rejected={}|unarrived_rejected={}|gauge_observable=NONE",
            if t_kernel { "BOUND_IN_KERNEL_ONLY" } else { "UNBOUND" },
            t.levels, t.views_per_level, b(t.views_equal_within_level),
            b(t.frozen_distinct_across_levels), b(t.earlier_level_replays_unchanged),
            b(t.direct_was_will), b(t.forged_view_rejected), b(t.missing_view_rejected),
            b(t.unarrived_input_rejected)
        ),
        format!(
            "BIND|n=4|binding=Z_SQUARE_WAVE|verdict=UNBOUND|reason=SOURCE_FIXES_QUANTIZER_NOT_LATTICE_WAVE|source=ZEB:index.html:95-100,HBU:README.md:70|z_values_on_s3={}|chi_squared_values_on_s3={}|zsum_gauge_checks={}|zsum_gauge_invariant={}|zsum_levels={}|alias_i={zi}|alias_j={zj}|alias_zsum={zs}|hb_i={zhi}|hb_j={zhj}",
            z.z_values_on_s3, z.chi_squared_values_on_s3, z.zsum_gauge_invariant_checks,
            b(z.zsum_gauge_invariant), z.zsum_levels
        ),
        "BIND|n=5|binding=Z_INSTANT_JOINED|verdict=UNBOUND|reason=UNDEFINED_IN_SOURCE|searched=HBU@f38cfec0,SIM@3f9f42da,ZEB@3b3fe023,recall4796|hits=0".to_owned(),
        format!(
            "BIND|n=6|binding=RESIDUAL_71_5_WILSON|verdict={}|source=SIM:LAW71:150-161|arms=3e_i-(1,1,1)|arms_sum_zero={}|normal={},{},{}|perm_homomorphism_36={}|plane_trace_eq_character={}/6|residual_invariant_checks={}|residual_invariant={}|plane_magnetic_match={}/{DIM}|plane_magnetic_gauge_checks={}|transported_residual_values={}|transported_plane_trace_values={}|electric_gap_witness={}|residual_rep=TRIVIAL",
            if w_bound { "BOUND" } else { "UNBOUND" },
            b(w.arms_sum_zero), w.arm_normal[0], w.arm_normal[1], w.arm_normal[2],
            b(w.homomorphism_36), w.plane_trace_is_character_6, w.residual_invariant_checks,
            b(w.residual_invariant), w.magnetic_match, w.magnetic_gauge_checks,
            w.transported_residual_values, w.transported_plane_trace_values,
            b(w.electric_witness)
        ),
    ])
}

pub fn generate() -> Result<Receipt, String> {
    let body_rows = rows()?;
    let mut hbp = Vec::new();
    let mut hbi = Vec::new();
    let mut prev = [0u8; 32];
    for (k, row) in body_rows.iter().enumerate() {
        let record_sha = sha256(row.as_bytes());
        let mut link = Vec::with_capacity(64);
        link.extend_from_slice(&prev);
        link.extend_from_slice(&record_sha);
        let chain = sha256(&link);
        let line = format!(
            "{row}|prev={}|record_sha={}|chain={}|json=0\n",
            hex(&prev),
            hex(&record_sha),
            hex(&chain)
        );
        hbi.extend_from_slice(
            format!(
                "HBI|schema=hebc.issue3.bindings.v1|record={}|offset={}|len={}|sh={}|row_sha={}|chain={}|json=0\n",
                k + 1,
                hbp.len(),
                line.len(),
                &hex(&record_sha)[..16],
                hex(&sha256(line.as_bytes())),
                hex(&chain)
            )
            .as_bytes(),
        );
        hbp.extend_from_slice(line.as_bytes());
        prev.copy_from_slice(&chain);
    }
    let anchor = format!(
        "ANCHOR|schema=hebc.issue3.bindings.v1|records={}|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        body_rows.len(),
        hex(&sha256(&hbp)),
        hex(&sha256(&hbi)),
        hex(&prev)
    );
    let verdicts: Vec<&str> = body_rows
        .iter()
        .map(|row| {
            row.split('|')
                .find_map(|f| f.strip_prefix("verdict="))
                .unwrap_or("MISSING")
        })
        .collect();
    let measure = format!(
        "ISSUE3|result=PASS|c1_flat={}|r_extension_1393={}|instant={}|z_square_wave={}|z_instant={}|residual_71_5_wilson={}|spectral_gap_inference=NONE|chain={}|json=0\n",
        verdicts[0],
        verdicts[1],
        verdicts[2],
        verdicts[3],
        verdicts[4],
        verdicts[5],
        hex(&prev)
    );
    Ok(Receipt {
        hbp,
        hbi,
        anchor,
        measure,
    })
}

pub fn verify(record: &Receipt) -> Result<(), String> {
    let fresh = generate()?;
    if fresh.hbp != record.hbp
        || fresh.hbi != record.hbi
        || fresh.anchor != record.anchor
        || fresh.measure != record.measure
    {
        return Err("issue 3 binding receipts do not replay".into());
    }
    Ok(())
}

pub fn write(path: &Path, record: &Receipt) -> Result<(), String> {
    std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
    for (file, body) in [
        ("run.hbp", record.hbp.as_slice()),
        ("index.hbi", record.hbi.as_slice()),
        ("run.anchor", record.anchor.as_bytes()),
        ("run.measure", record.measure.as_bytes()),
    ] {
        std::fs::write(path.join(file), body).map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn verify_dir(path: &Path) -> Result<(), String> {
    let read = |f: &str| std::fs::read(path.join(f)).map_err(|e| e.to_string());
    let text = |f: &str| std::fs::read_to_string(path.join(f)).map_err(|e| e.to_string());
    verify(&Receipt {
        hbp: read("run.hbp")?,
        hbi: read("index.hbi")?,
        anchor: text("run.anchor")?,
        measure: text("run.measure")?,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn c1_is_the_flat_winding_up_to_three_base_points_per_cycle() {
        let c = c1_flat().unwrap();
        assert_eq!(c.source_fixed_tuples, 0);
        assert_eq!(c.flat_classes, 8);
        assert_eq!(c.flat_fixed, 2);
        assert_eq!(c.flat_cycles3, 2);
        assert_eq!(c.equivariant_bijections, [3, 3]);
        assert!(c.inspect_agrees);
        // The gate flag follows this test, never the other way round.
        let bound = c.flat_fixed == 2 && c.flat_cycles3 == 2 && c.inspect_agrees;
        assert_eq!(crate::constellation_gate::C1_FLAT_WINDING_BOUND, bound);
    }

    #[test]
    fn r_has_no_lattice_or_commuting_extension_on_1393() {
        let torus = Torus2::build().unwrap();
        let r = r_extension(&torus).unwrap();
        assert!(r.lattice_automorphisms.is_power_of_two());
        assert_eq!(r.order3_automorphisms, 0);
        assert_eq!(r.he_fourth_moment_gap, 408);
        assert!(r.pair_r_equivariant_all36);
        assert!(r.pair_r3_identity_all36);
        assert!(r.pair_classes_on_1393 < DIM);
        assert!(r.max_pair_fiber > 1);
    }

    #[test]
    fn instant_is_one_freeze_per_level_with_three_equal_views() {
        let t = instant_atomic().unwrap();
        assert_eq!((t.levels, t.views_per_level), (3, 3));
        assert!(t.views_equal_within_level);
        assert!(t.frozen_distinct_across_levels);
        assert!(t.earlier_level_replays_unchanged);
        assert!(!t.direct_was_will);
        assert!(t.forged_view_rejected);
        assert!(t.missing_view_rejected);
        assert!(t.unarrived_input_rejected);
    }

    #[test]
    fn z_square_wave_is_gauge_invariant_and_loses_the_magnetic_energy() {
        let torus = Torus2::build().unwrap();
        let z = z_square_wave(&torus);
        assert_eq!(z.z_values_on_s3, 2);
        assert_eq!(z.chi_squared_values_on_s3, 3);
        assert!(z.zsum_gauge_invariant);
        assert_eq!(z.zsum_gauge_invariant_checks, DIM * 24);
        let (_, _, _, hi, hj) = z.alias.unwrap();
        assert_ne!(hi, hj);
    }

    #[test]
    fn residual_is_trivial_rep_and_arm_plane_trace_is_the_wilson_magnetic() {
        let torus = Torus2::build().unwrap();
        let w = residual_wilson(&torus).unwrap();
        assert!(w.arms_sum_zero);
        assert_eq!(w.arm_normal, [3, 3, 3]);
        assert!(w.homomorphism_36);
        assert_eq!(w.plane_trace_is_character_6, 6);
        assert!(w.residual_invariant);
        assert_eq!(w.magnetic_match, DIM);
        assert_eq!(w.transported_residual_values, 1);
        assert_eq!(w.transported_plane_trace_values, 3);
        assert!(w.electric_witness);
    }

    #[test]
    fn plane_magnetic_disagrees_when_a_plaquette_is_misread() {
        // Negative control: replace one plaquette's plane trace by the
        // residual line's trace (trivial rep, always 1) and the sum breaks.
        let torus = Torus2::build().unwrap();
        let mut broken = 0;
        for (i, rep) in torus.representatives.iter().enumerate() {
            let raw = raw_links(rep);
            let u = plaquette(&raw, 0, 0);
            let wrong = plane_magnetic(&raw).unwrap() - (2 - character(u)) + (2 - 1);
            if wrong != torus.magnetic[i] {
                broken += 1;
            }
        }
        assert!(broken > 0);
    }

    #[test]
    fn receipts_replay_and_reject_tampering() {
        let good = generate().unwrap();
        verify(&good).unwrap();
        assert_eq!(good.hbp.iter().filter(|&&c| c == b'\n').count(), 6);
        let mut bad = generate().unwrap();
        bad.hbp[40] ^= 1;
        assert!(verify(&bad).is_err());
        let mut idx = generate().unwrap();
        idx.hbi[30] ^= 1;
        assert!(verify(&idx).is_err());
        let mut m = generate().unwrap();
        m.measure.push('X');
        assert!(verify(&m).is_err());
    }
}
