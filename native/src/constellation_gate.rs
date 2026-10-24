//! Pinned Asolaria/Clasy constellation audit, not a replacement runtime.
//! Integer-only verification of original local ternary transition keys,
//! completion barriers, and a *label-only* gauge-invariant torus indexing
//! proposal. C1, Z-instant and Shadow Cat torus residual semantics remain
//! intentionally UNBOUND pending a source-derived mathematical contract.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::constellation_oscillator::{
    advance_completed_barrier, bind_roles, level_transition_keys,
    RepresentationEdge, TransitionKey, TransitionRole,
};
use crate::torus2::{canonical, gauge_fix, gauge_transform, Torus2, DIM};
use crate::trit::Trit;
use crate::{hex, sha256};
use std::path::Path;

pub const UPSTREAM_COMMIT: &str = "63cbf283b900457f8dfc59ac0e42d3efcbc9aedb";
pub const ORIG_TRIT_BLOB: &str = "3fb7ba9228cab4c40cdfc2732588e868a45b76ed";
pub const ORIG_OSCILLATOR_BLOB: &str = "619344880359eaa5f0fcd0d3e12a83cd39425ff5";
const TRIT_SOURCE: &[u8] = include_bytes!("../vendor/constellation_lattice/trit.rs");
const OSCILLATOR_SOURCE: &[u8] =
    include_bytes!("../vendor/constellation_lattice/oscillator.rs");

/// No proof/implementation has yet bound these names to a canonical
/// Yang-Mills gauge observable or to a sourced Constellation residual rule.
pub const C1_CONNECTED: bool = false;
pub const Z_INSTANT_CONNECTED: bool = false;
pub const SHADOW_CAT_TORI_CONNECTED: bool = false;

/// The ternary lattice's existing enum is the *only* owner of direction.
fn encode_key(key: TransitionKey, sink: &mut Vec<u8>) {
    sink.push(key.level);
    sink.extend_from_slice(&key.sector.to_le_bytes());
    sink.push(key.edge.ordinal());
    sink.push(key.direction.arithmetic_projection() as u8);
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Contract {
    pub level_sectors: [usize; 3],
    pub level_keys: [usize; 3],
    pub all_key_sha: String,
    pub pinned_source_sha: String,
    pub torus_orbit_sha: String,
    pub torus_orbits: usize,
    pub invariant_projection_only: bool,
}

/// Use original transition functions and original Gauss-canonical basis.
/// Modulo-243 addressing below is explicitly an observer *index probe*,
/// not a map of the gauge Hamiltonian into a constellation dynamics.
pub fn inspect() -> Result<Contract, String> {
    let sectors = [3_usize, 27, 243];
    let mut key_counts = [0; 3];
    let mut previous_level = None;
    let mut all = Vec::new();
    for (level, count) in sectors.into_iter().enumerate() {
        let keys = level_transition_keys(level as u8, count)?;
        if keys.len() != count * RepresentationEdge::ALL.len() * Trit::ALL.len() {
            return Err("missing Constellation local keys".into());
        }
        for key in &keys {
            if key.inverse().inverse() != *key ||
                !keys.contains(&key.inverse()) {
                return Err("local ternary inverse missing".into());
            }
            let roles = bind_roles(*key);
            if roles.len() != TransitionRole::ALL.len() ||
                roles.iter().any(|binding| binding.key != *key) {
                return Err("role binding lost transition identity".into());
            }
            encode_key(*key, &mut all);
        }
        key_counts[level] = keys.len();
        if let Some((prior_level, prior_sectors, prior_keys)) = previous_level {
            let barrier = advance_completed_barrier(
                prior_level, prior_sectors, prior_keys
            )?;
            if barrier.next_level != level as u8 ||
               barrier.next_sectors != count {
                return Err("constellation level recurrence changed".into());
            }
            if advance_completed_barrier(
                prior_level, prior_sectors, prior_keys - 1
            ).is_ok() {
                return Err("partial barrier incorrectly accepted".into());
            }
        }
        previous_level = Some((level as u8, count, keys.len()));
    }
    // The Gauss-invariant orbit *labels* can be indexed by the old 243-sector
    // namespace. This says nothing about physically connecting toroidal loops.
    let torus = Torus2::build()?;
    if torus.keys.len() != DIM { return Err("torus basis dimension changed".into()); }
    let mut samples = Vec::with_capacity(DIM * 4);
    for (index, rep) in torus.representatives.iter().enumerate() {
        let mut raw = [0u8; 8];
        for (i, &edge) in [2usize, 3, 5, 6, 7].iter().enumerate() {
            raw[edge] = rep[i];
        }
        let canonical_key = canonical(gauge_fix(raw));
        if canonical_key != torus.keys[index] {
            return Err("torus canonical key disagrees with representative".into());
        }
        let sector = canonical_key % 243;
        for site in 0..4 {
            for g in 0..6 {
                let rotated = gauge_transform(raw, site, g);
                if canonical(gauge_fix(rotated)) % 243 != sector {
                    return Err("observer index is gauge dependent".into());
                }
            }
        }
        let value = u32::try_from(sector).map_err(|_| "sector overflow")?;
        samples.extend_from_slice(&value.to_le_bytes());
    }
    let mut source = Vec::with_capacity(TRIT_SOURCE.len() + OSCILLATOR_SOURCE.len());
    source.extend_from_slice(TRIT_SOURCE);
    source.extend_from_slice(OSCILLATOR_SOURCE);
    Ok(Contract {
        level_sectors: [3, 27, 243],
        level_keys: key_counts,
        all_key_sha: hex(&sha256(&all)),
        pinned_source_sha: hex(&sha256(&source)),
        torus_orbit_sha: hex(&sha256(&samples)),
        torus_orbits: DIM,
        invariant_projection_only: true,
    })
}

pub struct Evidence {
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    pub anchor: String,
    pub measure: String,
}

pub fn generate() -> Result<Evidence, String> {
    let contract = inspect()?;
    let source = &contract.pinned_source_sha;
    let sh = &source[..16];
    let body = format!(
        "HBP|schema=hebc.constellation.audit.v1|scope=source_transition_and_observer_index_only|clasy_commit={UPSTREAM_COMMIT}|trit_blob={ORIG_TRIT_BLOB}|oscillator_blob={ORIG_OSCILLATOR_BLOB}|source_sha={source}|sh={sh}|sectors=3,27,243|key_counts=45,405,3645|key_sha={}|torus_basis={}|index_sha={}|c1_binding=UNVERIFIED|z_instant_binding=UNVERIFIED|shadow_cat_torus_binding=UNVERIFIED|physics_gap_inference=NONE|prev={}",
        contract.all_key_sha, contract.torus_orbits,
        contract.torus_orbit_sha,hex(&[0u8; 32])
    );
    let record_sha = sha256(body.as_bytes());
    let mut chain_input=Vec::new();
    chain_input.extend_from_slice(&[0u8;32]);
    chain_input.extend_from_slice(&record_sha);
    let chain = sha256(&chain_input);
    let row = format!(
        "{body}|record_sha={}|chain={}|json=0\n",
        hex(&record_sha),hex(&chain)
    );
    let index = format!(
        "HBI|schema=hebc.constellation.audit.v1|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        row.len(),hex(&sha256(row.as_bytes())),hex(&chain)
    );
    let anchor = format!(
        "ANCHOR|schema=hebc.constellation.audit.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(row.as_bytes())),hex(&sha256(index.as_bytes())),hex(&chain)
    );
    let measure = format!(
        "CONSTELLATION|result=PASS|source=CLASY_X3_PINNED|sectors=3,27,243|local_keys=45,405,3645|roles_per_key=6|torus_orbits=1393|projection=GAUGE_INVARIANT_LABEL_ONLY|c1=UNVERIFIED|z_instant=UNVERIFIED|shadow_cat_tori=UNVERIFIED|source_sha={source}|key_sha={}|index_sha={}|json=0\n",
        contract.all_key_sha,contract.torus_orbit_sha
    );
    Ok(Evidence {
        hbp:row.into_bytes(),
        hbi:index.into_bytes(),
        anchor,measure,
    })
}

pub fn verify(receipts: &Evidence) -> Result<(), String> {
    let computed = generate()?;
    if computed.hbp != receipts.hbp ||
       computed.hbi != receipts.hbi ||
       computed.anchor != receipts.anchor ||
       computed.measure != receipts.measure {
        return Err("constellation source/transition/gauge projection replay mismatch".into());
    }
    Ok(())
}

pub fn save(directory: &Path, evidence: &Evidence) -> Result<(), String> {
    std::fs::create_dir_all(directory).map_err(|e| e.to_string())?;
    for (file, data) in [
        ("run.hbp", evidence.hbp.as_slice()),
        ("index.hbi", evidence.hbi.as_slice()),
        ("run.anchor", evidence.anchor.as_bytes()),
        ("run.measure", evidence.measure.as_bytes()),
    ] {
        std::fs::write(directory.join(file), data).map_err(|e|e.to_string())?;
    }
    Ok(())
}

pub fn verify_directory(directory: &Path) -> Result<(), String> {
    let evidence=Evidence {
        hbp:std::fs::read(directory.join("run.hbp")).map_err(|e|e.to_string())?,
        hbi:std::fs::read(directory.join("index.hbi")).map_err(|e|e.to_string())?,
        anchor:std::fs::read_to_string(directory.join("run.anchor")).map_err(|e|e.to_string())?,
        measure:std::fs::read_to_string(directory.join("run.measure")).map_err(|e|e.to_string())?,
    };
    verify(&evidence)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn original_constellation_contract_and_gauss_labels_replay(){
        let info=inspect().unwrap();
        assert_eq!(info.level_sectors,[3,27,243]);
        assert_eq!(info.level_keys,[45,405,3645]);
        assert_eq!(info.torus_orbits,1393);
        assert!(info.invariant_projection_only);
        assert_eq!(generate().unwrap().hbp,generate().unwrap().hbp);
    }
    #[test]
    fn unmapped_residual_terms_must_not_claim_a_physical_bridge() {
        let evidence=generate().unwrap();
        assert!(evidence.measure.contains("c1=UNVERIFIED"));
        assert!(evidence.measure.contains("z_instant=UNVERIFIED"));
        assert!(evidence.measure.contains("shadow_cat_tori=UNVERIFIED"));
        assert!(evidence.hbp.windows(b"physics_gap_inference=NONE".len())
            .any(|w|w==b"physics_gap_inference=NONE"));
    }
    #[test]
    fn tampered_index_or_missing_key_is_rejected() {
        assert!(advance_completed_barrier(1,27,404).is_err());
        assert!(advance_completed_barrier(1,27,405).is_ok());
        let good=generate().unwrap();
        verify(&good).unwrap();
        let mut bad=generate().unwrap();
        bad.hbi[15] ^= 1;
        assert!(verify(&bad).is_err());
        let mut altered=generate().unwrap();
        altered.hbp[25] ^= 1;
        assert!(verify(&altered).is_err());
    }
}
