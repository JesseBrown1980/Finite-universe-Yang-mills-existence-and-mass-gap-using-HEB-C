//! Stage 2I: Independent spectral verification and finite-volume scaling
//! for the 1,393-state periodic 2x2 S3 torus Hamiltonian.
//!
//! Acceptance criteria for Issue #2:
//! 1. Certified rational bounds for E0, E1, and Delta at (1,1) and (3,5) using
//!    an independent verification module that does NOT share the parameterization,
//!    receipt schema, or execution path of Stage 2H (torus2_inertia.rs).
//! 2. Exact finite-volume comparison across single-plaquette (dim=3),
//!    double-plaquette (dim=11), and periodic torus (dim=1393), accounting for
//!    energy density E0/F, glueball vs. torelon winding states, and flat vacua.
//! 3. Exact Courant-Fischer min-max upper bound via an antisymmetric Wilson
//!    trial state z. Also record a separate *uncertified* truncated-array
//!    Cauchy-Schwarz defect diagnostic (legacy field: kato_var_*).
//! 4. Deterministic HBP/HBI/SHA receipts, replay verification, and tamper rejection.
//!
//! Rust 1.81, zero floating-point arithmetic, zero JSON, safe standard library.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::double_plaquette::{certify_gap as double_certify_gap, DoublePlaquette};
use crate::hamiltonian::spectrum as single_spectrum;
use crate::torus2::{Torus2, DIM};
use crate::{character, hex, sha256};
use std::path::Path;

pub const DENOM: i128 = 1_000_000;
const THRESH_DEN: i128 = 1_000;
const POWER_SCALE: i128 = 1_000_000;
const FACTOR_SCALE: i128 = 1_000_000;
const INDEPENDENT_RANK_STRENGTH: i128 = 48; // Independent from Stage 2H's 60
const GROUND_ITERS: usize = 256;
const EXCITED_ITERS: usize = 512;
const EXCITED_SCALE: i128 = 1_000_000_000;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct IndependentResult {
    pub je: i64,
    pub jb: i64,
    pub threshold: i128,
    pub e0_lower: i128,
    pub e0_upper: i128,
    pub e1_lower: i128,
    pub e1_upper: i128,
    pub gap_lower: i128,
    pub gap_upper: i128,
    pub min_cholesky_pivot: i128,
    pub residual_margin: i128,
    pub kato_variance_num: i128,
    pub kato_variance_den: i128,
    pub witness_sha: String,
}

#[derive(Clone, Debug)]
pub struct Certificate {
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    pub anchor: String,
    pub measure: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct VolumeScalingRow {
    pub geometry: &'static str,
    pub vertices: usize,
    pub links: usize,
    pub plaquettes: usize,
    pub physical_dim: usize,
    pub je: i64,
    pub jb: i64,
    pub e0_lower_per_face: i128,
    pub e0_upper_per_face: i128,
    pub e0_denom: i128,
    pub gap_lower: i128,
    pub gap_upper: i128,
    pub gap_denom: i128,
    pub mode_type: &'static str,
}

fn sqrt_floor(n: u128) -> u128 {
    if n == 0 {
        return 0;
    }
    let bits = 128 - n.leading_zeros();
    let mut x = 1u128 << bits.div_ceil(2);
    loop {
        let next = (x + n / x) / 2;
        if next >= x {
            return x;
        }
        x = next;
    }
}

fn div_round(n: i128, d: i128) -> i128 {
    assert!(d > 0);
    let mag = n.abs();
    let q = mag / d;
    let r = mag % d;
    let value = q + if r > d / 2 { 1 } else { 0 };
    if n < 0 {
        -value
    } else {
        value
    }
}

fn ceil_div(n: i128, d: i128) -> i128 {
    assert!(d > 0);
    -((-n).div_euclid(d))
}

fn dot_w(a: &[i128], b: &[i128], w: &[u64]) -> Result<i128, String> {
    let mut sum = 0i128;
    for ((&x, &y), &weight) in a.iter().zip(b).zip(w) {
        let term = x
            .checked_mul(y)
            .and_then(|p| p.checked_mul(i128::from(weight)))
            .ok_or("weighted dot overflow")?;
        sum = sum.checked_add(term).ok_or("weighted dot sum overflow")?;
    }
    Ok(sum)
}

/// Independent integer Cholesky positive-definiteness verification.
///
/// Constructs approximate integer factor L for (A - fudge * I) * S^2.
/// Proves that residual R = A * S^2 - L L^T has positive diagonal
/// and is strictly diagonally dominant, guaranteeing A * S^2 is strictly positive definite.
fn independent_cholesky_pd(a: &[Vec<i128>], fudge: i128) -> Result<(i128, i128), String> {
    let n = a.len();
    if n == 0 || fudge <= 0 || a.iter().any(|row| row.len() != n) {
        return Err("invalid matrix for independent Cholesky".into());
    }
    let scale2 = FACTOR_SCALE * FACTOR_SCALE;
    let mut l = vec![vec![0i128; n]; n];
    let mut min_pivot = i128::MAX;

    for i in 0..n {
        for j in 0..=i {
            if a[i][j] != a[j][i] {
                return Err("asymmetric entry in independent matrix".into());
            }
            let entry = if i == j { a[i][j] - fudge } else { a[i][j] };
            let q = entry.checked_mul(scale2).ok_or("scaled entry overflow")?;
            let mut used = 0i128;
            for k in 0..j {
                let item = l[i][k].checked_mul(l[j][k]).ok_or("product overflow")?;
                used = used.checked_add(item).ok_or("sum overflow")?;
            }
            let r = q.checked_sub(used).ok_or("subtraction overflow")?;
            if i == j {
                if r <= 0 {
                    return Err(format!("nonpositive pivot at row {i}"));
                }
                let p = sqrt_floor(r as u128) as i128;
                if p == 0 {
                    return Err("zero pivot".into());
                }
                l[i][j] = p;
                min_pivot = min_pivot.min(p);
            } else {
                l[i][j] = div_round(r, l[j][j]);
            }
        }
    }

    let mut min_margin = i128::MAX;
    let mut prefix = 0i128;
    for (i, row) in l.iter().enumerate() {
        let later = (n - i - 1) as i128 * ((row[i] + 1) / 2);
        let radius = prefix.checked_add(later).ok_or("radius overflow")?;
        let margin = fudge
            .checked_mul(scale2)
            .and_then(|f| f.checked_sub(radius))
            .ok_or("margin overflow")?;
        if margin <= 0 {
            return Err(format!("residual margin failure at row {i}"));
        }
        min_margin = min_margin.min(margin);
        prefix = prefix.checked_add((row[i] + 1) / 2).ok_or("prefix overflow")?;
    }

    Ok((min_pivot, min_margin))
}

fn positive_ground_witness(m: &Torus2, je: i64, jb: i64) -> Result<Vec<i128>, String> {
    let largest_diag = m
        .electric
        .iter()
        .enumerate()
        .map(|(i, row)| {
            let diag = row.iter().find(|(j, _)| *j == i).map(|(_, q)| *q).unwrap_or(0);
            i128::from(je) * i128::from(diag) + i128::from(jb) * i128::from(m.magnetic[i])
        })
        .max()
        .ok_or("missing diagonal")?;
    let shift = largest_diag + 1;
    let mut v = vec![POWER_SCALE; DIM];
    for _ in 0..GROUND_ITERS {
        let hv = m.apply(je, jb, &v)?;
        let mut p = Vec::with_capacity(DIM);
        for (&x, &hx) in v.iter().zip(&hv) {
            let y = shift * x - hx;
            if y <= 0 {
                return Err("positive power witness failed".into());
            }
            p.push(y);
        }
        let max = *p.iter().max().ok_or("missing max vector element")?;
        v = p.iter().map(|&x| (x * POWER_SCALE + max / 2) / max).collect();
        if v.iter().any(|&x| x <= 0) {
            return Err("positive iterate degenerated".into());
        }
    }
    Ok(v)
}

fn build_lifted_operator(
    m: &Torus2,
    v: &[i128],
    je: i64,
    jb: i64,
    tnum: i128,
) -> Result<(Vec<Vec<i128>>, i128), String> {
    let norm = v.iter().zip(&m.weights).try_fold(0i128, |sum, (&x, &w)| {
        sum.checked_add(x.checked_mul(x)?.checked_mul(i128::from(w))?)
    }).ok_or("norm overflow")?;
    let u: Vec<i128> = v.iter().zip(&m.weights).map(|(&x, &w)| x * i128::from(w)).collect();
    let mut a = vec![vec![0i128; DIM]; DIM];
    let bulk = THRESH_DEN * norm;
    for (i, row) in a.iter_mut().enumerate() {
        for (j, cell) in row.iter_mut().enumerate() {
            *cell = INDEPENDENT_RANK_STRENGTH * THRESH_DEN * u[i] * u[j];
        }
        let w = i128::from(m.weights[i]);
        row[i] += norm * w * (THRESH_DEN * i128::from(jb) * i128::from(m.magnetic[i]) - tnum);
        for &(j, entry) in &m.electric[i] {
            row[j] += bulk * w * i128::from(je) * i128::from(entry);
        }
    }
    Ok((a, norm))
}

fn excited_witness_and_residual(
    m: &Torus2,
    v: &[i128],
    je: i64,
    jb: i64,
    threshold: i128,
) -> Result<(i128, i128, i128), String> {
    let mut z: Vec<i128> = v
        .iter()
        .zip(&m.representatives)
        .map(|(&x, q)| x * i128::from(character(q[0]) - character(q[2])))
        .collect();
    let max_start = z.iter().map(|x| x.abs()).max().ok_or("missing excited trial")?;
    if max_start == 0 {
        return Err("zero excited trial".into());
    }
    for x in &mut z {
        *x = div_round(*x * EXCITED_SCALE, max_start);
    }

    let shift: i128 = m
        .electric
        .iter()
        .enumerate()
        .map(|(i, row)| {
            let diag = row.iter().find(|(j, _)| *j == i).map(|(_, x)| *x).unwrap_or(0);
            2 * i128::from(je) * i128::from(diag) + i128::from(jb) * i128::from(m.magnetic[i])
        })
        .max()
        .unwrap_or(0)
        + 1;

    for _ in 0..EXCITED_ITERS {
        let hz = m.apply(je, jb, &z)?;
        let next: Vec<i128> = z.iter().zip(&hz).map(|(&x, &h)| shift * x - h).collect();
        let magnitude = next.iter().map(|x| x.abs()).max().ok_or("missing excited step")?;
        if magnitude == 0 {
            return Err("zero excited step".into());
        }
        z = next.iter().map(|&x| div_round(x * EXCITED_SCALE, magnitude)).collect();
    }

    let hz = m.apply(je, jb, &z)?;
    let hv = m.apply(je, jb, v)?;
    if dot_w(v, &z, &m.weights)? != 0
        || dot_w(v, &hz, &m.weights)? != 0
        || dot_w(&z, &hv, &m.weights)? != 0
    {
        return Err("antisymmetric Wilson trial lost exact H-orthogonality".into());
    }

    let vv = dot_w(v, v, &m.weights)?;
    let vhv = dot_w(v, &hv, &m.weights)?;
    let zz = dot_w(&z, &z, &m.weights)?;
    let zhz = dot_w(&z, &hz, &m.weights)?;
    if vv <= 0 || zz <= 0 || zhz <= 0 || vhv * THRESH_DEN >= threshold * vv {
        return Err("Ritz ordering not certified".into());
    }

    // This is NOT an exact Kato-Temple variance for the original z:
    // z and Hz are separately truncated below, so generally
    // hz_scaled != H(z_scaled). It is a nonnegative, truncated-pair
    // Cauchy-Schwarz diagnostic ONLY; it certifies no eigenvalue interval.
    // The exact min-max E1 upper bound uses the untruncated z and Hz.
    let z_scaled: Vec<i128> = z.iter().map(|&x| x / 1_000).collect();
    let hz_scaled: Vec<i128> = hz.iter().map(|&x| x / 1_000).collect();
    let zz_s = dot_w(&z_scaled, &z_scaled, &m.weights)?;
    let zhz_s = dot_w(&z_scaled, &hz_scaled, &m.weights)?;
    let hzhz_s = dot_w(&hz_scaled, &hz_scaled, &m.weights)?;

    let var_num = hzhz_s
        .checked_mul(zz_s)
        .and_then(|a| a.checked_sub(zhz_s * zhz_s))
        .ok_or("variance overflow")?;
    let var_den = zz_s.checked_mul(zz_s).ok_or("variance denom overflow")?;

    let e1_upper = ceil_div(zhz * DENOM, zz);
    Ok((e1_upper, var_num, var_den))
}

pub fn certify_independent(je: i64, jb: i64) -> Result<IndependentResult, String> {
    let threshold = match (je, jb) {
        (1, 1) => 13_240,
        (3, 5) => 50_840,
        _ => return Err("supported independent verifier couplings: (1,1),(3,5)".into()),
    };
    let earlier = crate::torus2_bounds::enclose(je, jb)?;
    if earlier.e0_upper * THRESH_DEN >= threshold * DENOM {
        return Err("ground-state enclosure not below proposed threshold".into());
    }
    let m = Torus2::build()?;
    let v = positive_ground_witness(&m, je, jb)?;
    let (a, norm) = build_lifted_operator(&m, &v, je, jb, threshold)?;
    let (min_pivot, min_margin) = independent_cholesky_pd(&a, norm)?;

    let e1_lower = threshold * (DENOM / THRESH_DEN);
    let (e1_upper, var_num, var_den) =
        excited_witness_and_residual(&m, &v, je, jb, threshold)?;
    if e1_upper <= e1_lower {
        return Err("excited upper bound below certified threshold".into());
    }
    let gap_lower = e1_lower - earlier.e0_upper;
    let gap_upper = e1_upper - earlier.e0_lower;

    let mut bytes = Vec::new();
    bytes.extend_from_slice(&je.to_le_bytes());
    bytes.extend_from_slice(&jb.to_le_bytes());
    bytes.extend_from_slice(&threshold.to_le_bytes());
    for item in &v {
        bytes.extend_from_slice(&item.to_le_bytes());
    }

    Ok(IndependentResult {
        je,
        jb,
        threshold,
        e0_lower: earlier.e0_lower,
        e0_upper: earlier.e0_upper,
        e1_lower,
        e1_upper,
        gap_lower,
        gap_upper,
        min_cholesky_pivot: min_pivot,
        residual_margin: min_margin,
        kato_variance_num: var_num,
        kato_variance_den: var_den,
        witness_sha: hex(&sha256(&bytes)),
    })
}

pub fn certificate(je: i64, jb: i64) -> Result<Certificate, String> {
    let b = certify_independent(je, jb)?;
    let body = format!(
        "HBP|schema=hebc.s3.stage2i.independent.v1|JE={je}|JB={jb}|physical_dim={DIM}|threshold_num={}|threshold_den={THRESH_DEN}|E0=[{},{}]/{DENOM}|E1=[{},{}]/{DENOM}|gap=[{},{}]/{DENOM}|rank_strength={INDEPENDENT_RANK_STRENGTH}|factor_scale={FACTOR_SCALE}|ground_iters={GROUND_ITERS}|excited_iters={EXCITED_ITERS}|min_pivot={}|residual_margin={}|kato_var_num={}|kato_var_den={}|witness_sha={}|method=REIMPLEMENTED_RANK_LIFTING_CHOLESKY_MINMAX_TRUNCATED_DIAGNOSTIC|continuum_proven=0|prev={}",
        b.threshold,
        b.e0_lower,
        b.e0_upper,
        b.e1_lower,
        b.e1_upper,
        b.gap_lower,
        b.gap_upper,
        b.min_cholesky_pivot,
        b.residual_margin,
        b.kato_variance_num,
        b.kato_variance_den,
        b.witness_sha,
        hex(&[0u8; 32])
    );
    let rec = sha256(body.as_bytes());
    let chain = sha256(&[[0u8; 32].as_slice(), rec.as_slice()].concat());
    let hbp = format!("{body}|record_sha={}|chain={}|json=0\n", hex(&rec), hex(&chain)).into_bytes();
    let hbi = format!(
        "HBI|schema=hebc.s3.stage2i.independent.v1|record=1|offset=0|len={}|row_sha={}|chain={}|json=0\n",
        hbp.len(),
        hex(&sha256(&hbp)),
        hex(&chain)
    )
    .into_bytes();
    let anchor = format!(
        "ANCHOR|schema=hebc.s3.stage2i.independent.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),
        hex(&sha256(&hbi)),
        hex(&chain)
    );
    let measure = format!(
        "TORUS2INDEPENDENT|result=PASS|JE={je}|JB={jb}|E0=[{},{}]/{DENOM}|E1=[{},{}]/{DENOM}|gap=[{},{}]/{DENOM}|strict_E1_threshold={}/{THRESH_DEN}|independent_cholesky=PASS|margin={}|json=0\n",
        b.e0_lower,
        b.e0_upper,
        b.e1_lower,
        b.e1_upper,
        b.gap_lower,
        b.gap_upper,
        b.threshold,
        b.residual_margin
    );
    Ok(Certificate {
        hbp,
        hbi,
        anchor,
        measure,
    })
}

pub fn save(dir: &Path, c: &Certificate) -> Result<(), String> {
    std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    for (name, bytes) in [
        ("run.hbp", c.hbp.as_slice()),
        ("index.hbi", c.hbi.as_slice()),
        ("run.anchor", c.anchor.as_bytes()),
        ("run.measure", c.measure.as_bytes()),
    ] {
        std::fs::write(dir.join(name), bytes).map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn verify_dir(dir: &Path, je: i64, jb: i64) -> Result<(), String> {
    let expected = certificate(je, jb)?;
    for (name, bytes) in [
        ("run.hbp", expected.hbp.as_slice()),
        ("index.hbi", expected.hbi.as_slice()),
        ("run.anchor", expected.anchor.as_bytes()),
        ("run.measure", expected.measure.as_bytes()),
    ] {
        if std::fs::read(dir.join(name)).map_err(|e| e.to_string())? != bytes {
            return Err(format!("independent verifier replay mismatch: {name}"));
        }
    }
    Ok(())
}

/// Compare three distinct finite geometries (not a controlled periodic-volume limit).
pub fn finite_volume_scaling() -> Result<Vec<VolumeScalingRow>, String> {
    let mut rows = Vec::new();
    let double_model = DoublePlaquette::build()?;
    let couplings = [(1, 1), (3, 5)];

    for (je, jb) in couplings {
        // 1. Single plaquette (dim=3, F=1)
        let s = single_spectrum(je, jb)?;
        rows.push(VolumeScalingRow {
            geometry: "single_open_plaquette",
            vertices: 4,
            links: 4,
            plaquettes: 1,
            physical_dim: 3,
            je,
            jb,
            e0_lower_per_face: s.lower[0],
            e0_upper_per_face: s.upper[0],
            e0_denom: 65536,
            gap_lower: s.gap_lower,
            gap_upper: s.gap_upper,
            gap_denom: 65536,
            mode_type: "contractible_0++_glueball",
        });

        // 2. Double plaquette (dim=11, F=2)
        let d = double_certify_gap(&double_model, je, jb)?;
        // d.ground is odd half-integers / 2, so energy per face has denom = 4
        rows.push(VolumeScalingRow {
            geometry: "double_open_plaquette",
            vertices: 6,
            links: 7,
            plaquettes: 2,
            physical_dim: 11,
            je,
            jb,
            e0_lower_per_face: d.ground[0],
            e0_upper_per_face: d.ground[1],
            e0_denom: 4,
            gap_lower: d.gap[0],
            gap_upper: d.gap[1],
            gap_denom: 2,
            mode_type: "contractible_0++_glueball",
        });

        // 3. Periodic 2x2 torus (dim=1393, F=4)
        let t = certify_independent(je, jb)?;
        rows.push(VolumeScalingRow {
            geometry: "periodic_2x2_torus",
            vertices: 4,
            links: 8,
            plaquettes: 4,
            physical_dim: 1393,
            je,
            jb,
            e0_lower_per_face: t.e0_lower,
            e0_upper_per_face: t.e0_upper,
            e0_denom: DENOM * 4,
            gap_lower: t.gap_lower,
            gap_upper: t.gap_upper,
            gap_denom: DENOM,
            mode_type: "noncontractible_torelon_doublet",
        });
    }

    Ok(rows)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn independent_cholesky_pd_controls() {
        // Strict PD matrix [[4, 1], [1, 3]]
        let a = vec![vec![4i128, 1i128], vec![1i128, 3i128]];
        let res = independent_cholesky_pd(&a, 1);
        assert!(res.is_ok());
        let (min_pivot, min_margin) = res.unwrap();
        assert!(min_pivot > 0);
        assert!(min_margin > 0);

        // Indefinite matrix [[1, 2], [2, 1]]
        let indef = vec![vec![1i128, 2i128], vec![2i128, 1i128]];
        assert!(independent_cholesky_pd(&indef, 1).is_err());
    }

    #[test]
    fn independent_certification_matches_stage2h_enclosures() {
        let r11 = certify_independent(1, 1).unwrap();
        assert_eq!(r11.threshold, 13_240);
        assert_eq!(r11.e0_lower, 7_634_198);
        assert_eq!(r11.e0_upper, 7_634_199);
        assert_eq!(r11.e1_lower, 13_240_000);
        assert_eq!(r11.e1_upper, 13_242_733);
        assert_eq!(r11.gap_lower, 5_605_801);
        assert_eq!(r11.gap_upper, 5_608_535);
        assert!(r11.min_cholesky_pivot > 0);
        assert!(r11.residual_margin > 0);
        assert!(r11.kato_variance_num >= 0);
        assert!(r11.kato_variance_den > 0);

        let r35 = certify_independent(3, 5).unwrap();
        assert_eq!(r35.threshold, 50_840);
        assert_eq!(r35.e0_lower, 36_699_227);
        assert_eq!(r35.e0_upper, 36_699_228);
        assert_eq!(r35.e1_lower, 50_840_000);
        assert_eq!(r35.e1_upper, 50_842_050);
        assert_eq!(r35.gap_lower, 14_140_772);
        assert_eq!(r35.gap_upper, 14_142_823);
        assert!(r35.min_cholesky_pivot > 0);
        assert!(r35.residual_margin > 0);
    }

    #[test]
    fn cross_geometry_density_comparison_does_not_claim_extensivity() {
        let rows = finite_volume_scaling().unwrap();
        assert_eq!(rows.len(), 6); // 3 geometries * 2 couplings

        // Check at (1,1): ground state energy density E0/F is ~1.91 across all three sizes
        let single_11 = &rows[0];
        let double_11 = &rows[1];
        let torus_11 = &rows[2];

        // Single: ~1.9095 (125140 / 65536)
        let s_dens = single_11.e0_lower_per_face * 1000 / single_11.e0_denom;
        assert!((1900..=1920).contains(&s_dens));

        // Double: ~2.00 (8 / 4 = 2)
        let d_dens = (double_11.e0_lower_per_face + double_11.e0_upper_per_face) * 1000
            / (2 * double_11.e0_denom);
        assert!((1900..=2100).contains(&d_dens));

        // Torus: ~1.9085 (7634198 / 4000000)
        let t_dens = torus_11.e0_lower_per_face * 1000 / torus_11.e0_denom;
        assert!((1900..=1920).contains(&t_dens));

        // Gap comparison only. The mode_type strings below are provisional
        // interpretations, NOT independently certified eigenmode labels.
        assert_eq!(single_11.mode_type, "contractible_0++_glueball");
        assert_eq!(double_11.mode_type, "contractible_0++_glueball");
        assert_eq!(torus_11.mode_type, "noncontractible_torelon_doublet");
    }
}
