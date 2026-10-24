//! Stage 2: exact, finite non-Abelian S3 single-plaquette Hamiltonian.
//! No floating point. This is NOT a four-dimensional continuum Yang-Mills theorem.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]
use crate::{character, inv, mul};

pub const DENOM: i128 = 65_536; // exact rational eigenvalue enclosure resolution
pub const MAX_COUPLING: i64 = 100_000;
pub const CHARACTER_ORDER: [&str; 3] = ["trivial", "standard", "sign"];

fn sign_char(g: u8) -> i64 {
    match g { 1 | 2 | 5 => -1, _ => 1 }
}

fn chi(which: usize, g: u8) -> i64 {
    match which { 0 => 1, 1 => character(g), 2 => sign_char(g), _ => unreachable!() }
}

/// Hilbert-space dimension for a connected graph with V vertices and E links:
/// invariant functions on G^(E-V+1) under simultaneous conjugation.
pub fn gauss_dimension(vertices: usize, links: usize) -> Result<u64, String> {
    if vertices == 0 || links + 1 < vertices { return Err("invalid graph connectivity".into()); }
    let cycles = links + 1 - vertices;
    if cycles > 12 { return Err("exact count supported for at most 12 independent loops".into()); }
    // Burnside's lemma: [6^n + 3*2^n + 2*3^n]/6
    let power = |x: u64| x.checked_pow(cycles as u32).ok_or("overflow in Burnside") ;
    let count = power(6)? + 3 * power(2)? + 2 * power(3)?;
    Ok(count / 6)
}

/// The one-square Hilbert space has 6^4 link assignments. After averaging over
/// Gauss transformations on all four vertices, the invariant subspace has
/// three orbits, each determined by the plaquette holonomy conjugacy class.
/// Returns sizes of the identity/transposition/three-cycle orbits.
pub fn single_plaquette_gauss_orbits() -> [usize; 3] {
    let mut visited = [false; 1296];
    let mut orbits = [0usize; 3];
    let mut found = 0usize;
    let decode = |mut id: usize| -> [u8; 4] {
        let mut a = [0; 4];
        for x in &mut a { *x = (id % 6) as u8; id /= 6; }
        a
    };
    let encode = |a: [u8; 4]| -> usize {
        usize::from(a[0]) + 6 * usize::from(a[1]) +
            36 * usize::from(a[2]) + 216 * usize::from(a[3])
    };
    let class = |a: [u8; 4]| -> usize {
        let u = mul(mul(mul(a[0], a[1]), inv(a[2])), inv(a[3]));
        if u == 0 { 0 } else if u == 3 || u == 4 { 2 } else { 1 }
    };
    // Directed cycle v0->v1->v2->v3->v0, using U3 and U4 inverse in holonomy.
    const TAIL: [usize; 4] = [0, 1, 3, 0];
    const HEAD: [usize; 4] = [1, 2, 2, 3];
    for root in 0..1296 {
        if visited[root] { continue; }
        found += 1;
        let label = class(decode(root));
        let mut todo = vec![root];
        visited[root] = true;
        let mut count = 0usize;
        while let Some(id) = todo.pop() {
            count += 1;
            let links = decode(id);
            assert_eq!(class(links), label, "Gauss transformation changed class");
            for vertex in 0..4 {
                for g in 1..6u8 {
                    let mut next = links;
                    for edge in 0..4 {
                        if TAIL[edge] == vertex { next[edge] = mul(g, next[edge]); }
                        if HEAD[edge] == vertex { next[edge] = mul(next[edge], inv(g)); }
                    }
                    let key = encode(next);
                    if !visited[key] { visited[key] = true; todo.push(key); }
                }
            }
        }
        orbits[label] += count;
    }
    assert_eq!(found, 3, "Gauss orbit count");
    orbits
}

/// Clebsch-Gordan fusion by exact group-character orthogonality.
/// In an orthonormal character basis, <i|chi_standard|j>
/// = (1/6) sum_g chi_i(g) chi_standard(g) chi_j(g).
pub fn wilson_character_matrix() -> [[i64; 3]; 3] {
    let mut result = [[0; 3]; 3];
    for (i, row) in result.iter_mut().enumerate() {
        for (j, val) in row.iter_mut().enumerate() {
            let sum: i64 = (0..6u8).map(|g| chi(i, g) * character(g) * chi(j, g)).sum();
            assert_eq!(sum % 6, 0, "character basis matrix must be integral");
            *val = sum / 6;
        }
    }
    result
}

/// H = J_E * sum_{4 links} L_link + J_B * (2I - chi_standard(holonomy))
/// in the Gauss-law invariant single-plaquette character basis.
pub fn physical_hamiltonian(je: i64, jb: i64) -> Result<[[i64; 3]; 3], String> {
    if !(0..=MAX_COUPLING).contains(&je) || !(0..=MAX_COUPLING).contains(&jb) {
        return Err("couplings must be nonnegative and <= 100000".into());
    }
    let m = wilson_character_matrix();
    let casimir = [0_i64, 3, 6];
    let mut h = [[0_i64; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            h[i][j] = if i == j { 4 * je * casimir[i] + 2 * jb } else { 0 }
                - jb * m[i][j];
        }
    }
    Ok(h)
}

/// Counts eigenvalues strictly below rational x=num/DENOM (Sturm sequence).
/// Uses integer determinants of all leading principal minors; no division.
/// At zeros, ignore zero minors (limit from below at exact eigenvalues).
fn count_below(h: &[[i64; 3]; 3], num: i128) -> usize {
    let a = [h[0][0] as i128, h[1][1] as i128, h[2][2] as i128];
    let b0 = (h[0][1] as i128) * DENOM;
    let b1 = (h[1][2] as i128) * DENOM;
    let q0 = 1_i128;
    let q1 = a[0] * DENOM - num;
    let q2 = (a[1] * DENOM - num) * q1 - b0 * b0;
    let q3 = (a[2] * DENOM - num) * q2 - b1 * b1 * q1;
    let mut last = 1_i128;
    let mut changes = 0;
    for q in [q0, q1, q2, q3] {
        if q == 0 { continue; }
        if (q < 0) != (last < 0) { changes += 1; }
        last = q;
    }
    changes
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Enclosure {
    // Three exact rational eigenvalue enclosures. Endpoint values are
    // numerators; common positive denominator DENOM.
    pub lower: [i128; 3],
    pub upper: [i128; 3],
    pub gap_lower: i128,
    pub gap_upper: i128,
}
impl Enclosure {
    pub fn rigorously_positive(&self) -> bool { self.gap_lower > 0 }
}

/// Exact rational Sturm enclosures; no floats and no integer approximation
/// masquerading as an exact irrational eigenvalue.
pub fn spectrum(je: i64, jb: i64) -> Result<Enclosure, String> {
    let h = physical_hamiltonian(je, jb)?;
    let bound = ((24 * je + 4 * jb + 2) as i128) * DENOM;
    let mut lower = [0_i128; 3];
    let mut upper = [0_i128; 3];
    for index in 0..3 {
        let mut lo = -bound;
        let mut hi = bound;
        if count_below(&h, lo) > index || count_below(&h, hi) <= index {
            return Err("Sturm root bracketing failed".into());
        }
        while hi - lo > 1 {
            let mid = lo + (hi - lo) / 2;
            if count_below(&h, mid) > index { hi = mid; } else { lo = mid; }
        }
        lower[index] = lo;
        upper[index] = hi;
    }
    Ok(Enclosure {
        lower, upper,
        gap_lower: lower[1] - upper[0],
        gap_upper: upper[1] - lower[0],
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_character_orthogonality_and_clebsch_gordan() {
        let expected = [[0,1,0],[1,1,1],[0,1,0]];
        assert_eq!(wilson_character_matrix(), expected);
        for i in 0..3 {
            for j in 0..3 {
                let s: i64 = (0..6).map(|g| chi(i, g) * chi(j, g)).sum();
                assert_eq!(s, if i == j { 6 } else { 0 });
            }
        }
    }

    #[test]
    fn exhaustive_gauss_law_single_plaquette() {
        assert_eq!(single_plaquette_gauss_orbits(), [216,648,432]);
        assert_eq!(gauss_dimension(4,4), Ok(3));
        assert_eq!(gauss_dimension(6,7), Ok(11));
        assert_eq!(gauss_dimension(4,8), Ok(1393)); // periodic 2x2 lattice
    }

    #[test]
    fn hamiltonian_integer_hermiticity_and_limits() {
        for je in 0..=10 {
            for jb in 0..=10 {
                let h = physical_hamiltonian(je, jb).unwrap();
                for i in 0..3 {
                    for j in 0..3 { assert_eq!(h[i][j], h[j][i]); }
                }
                assert_eq!(h[0][0], 2*jb);
                assert_eq!(h[1][1], 12*je + jb);
                assert_eq!(h[2][2], 24*je + 2*jb);
                assert_eq!(h[0][1], -jb);
                assert_eq!(h[1][2], -jb);
                assert_eq!(h[0][2], 0);
            }
        }
    }

    #[test]
    fn rational_exact_strong_coupling_gap() {
        for je in 1..=64 {
            let got = spectrum(je, 0).unwrap();
            // Intervals width 1/DENOM enclose exact integer eigenvalues.
            for (i, energy) in [0, 12*je, 24*je].iter().enumerate() {
                let true_scaled = (*energy as i128) * DENOM;
                assert!(got.lower[i] <= true_scaled && true_scaled <= got.upper[i]);
            }
            assert!(got.gap_lower > 0);
            assert!(got.gap_lower <= 12_i128 * je as i128 * DENOM);
            assert!(got.gap_upper >= 12_i128 * je as i128 * DENOM);
        }
        let zero = spectrum(0,0).unwrap();
        assert!(!zero.rigorously_positive());
    }

    #[test]
    fn exact_interacting_sturm_brackets_and_gap() {
        for je in 0..=20 {
            for jb in 0..=20 {
                let h = physical_hamiltonian(je, jb).unwrap();
                let got = spectrum(je,jb).unwrap();
                for k in 0..3 {
                    assert_eq!(got.upper[k]-got.lower[k], 1);
                    // Lower endpoint has not passed root k, upper has.
                    assert!(count_below(&h, got.lower[k]) <= k);
                    assert!(count_below(&h, got.upper[k]) > k);
                }
                assert_eq!(got.gap_lower, got.lower[1]-got.upper[0]);
                assert_eq!(got.gap_upper, got.upper[1]-got.lower[0]);
                if je != 0 || jb != 0 {
                    assert!(got.rigorously_positive(), "gap not certified je={je} jb={jb}");
                }
            }
        }
    }

    #[test]
    fn rejecting_unbounded_couplings_and_topology() {
        assert!(spectrum(-1,1).is_err());
        assert!(spectrum(1,-1).is_err());
        assert!(spectrum(MAX_COUPLING+1,0).is_err());
        assert!(gauss_dimension(0,0).is_err());
        assert!(gauss_dimension(10,1).is_err());
    }

    #[test]
    fn independent_integer_characteristic_polynomial_certificate() {
        // Unlike the Sturm recurrence, this is a direct Leibniz determinant
        // expansion of (lambda*I-H) with exact rational lambda=num/DENOM.
        fn polynomial(h: [[i64;3];3], num: i128) -> i128 {
            let mut a = [[0_i128; 3];3];
            for i in 0..3 {
                for j in 0..3 {
                    a[i][j] = if i == j { num } else { 0 } -
                        (h[i][j] as i128) * DENOM;
                }
            }
            a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
        }
        for je in 0..=32 {
            for jb in 0..=32 {
                let h = physical_hamiltonian(je,jb).unwrap();
                let e = spectrum(je,jb).unwrap();
                for k in 0..3 {
                    let at_lo = polynomial(h,e.lower[k]);
                    let at_hi = polynomial(h,e.upper[k]);
                    assert!(
                        at_lo == 0 || at_hi == 0 || at_lo.signum() != at_hi.signum(),
                        "determinant did not bracket a root je={je} jb={jb} index={k}"
                    );
                }
            }
        }
        // Magnetic-only limiting case has exact class-energy levels 0, 2J_B, 3J_B.
        for jb in 1..=32 {
            let e = spectrum(0,jb).unwrap();
            for (k, root) in [0_i128, 2*jb as i128, 3*jb as i128].iter().enumerate() {
                assert!(e.lower[k] <= root*DENOM && e.upper[k] >= root*DENOM);
            }
        }
    }

}
