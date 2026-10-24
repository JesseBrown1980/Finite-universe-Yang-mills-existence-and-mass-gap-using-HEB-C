//! Stage 2E — source-grounded Shadow Cat residual / S3 torus bridge audit.
//!
//! The *only* proposed new mathematical link is the order-three SL(2,Z)
//! automorphism on the **flat commuting holonomy** representation variety.
//! This is a real gauge-invariant C3 action, not a proof of the source's
//! claimed physical residual emission, C1/IS instant transfer, or a symmetry
//! of the full interacting Kogut–Susskind Hamiltonian.
//!
//! Source: Asolaria universe-simulator books/LAW-71 section 71.13,
//! books/LAW-70, and temporal-exchant intake (all primary source).
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::torus2::{Torus2,DIM};
use crate::{hex,inv,mul,sha256};
use std::collections::BTreeMap;
use std::path::Path;

fn conjugate(g:u8,x:u8)->u8 {mul(mul(g,x),inv(g))}
/// Based Wilson holonomies transformed by global gauge conjugation.
/// Flatness means x and y commute, so this is a homomorphism Z^2 -> S3.
fn canonical_pair(x:u8,y:u8)->(u8,u8) {
    (0..6).map(|g|(conjugate(g,x),conjugate(g,y)))
        .min().expect("S3 identity exists")
}

/// R = [[0,-1],[1,-1]] on the two torus winding generators.
/// For COMMUTING holonomies only: (x,y) -> (y^-1, x y^-1).
/// R^3=id. This is a genuine C3 / order-three mapping-class action on
/// the finite flat-connection moduli space, not on all nonflat lattice fields.
fn winding_rotation(x:u8,y:u8)->(u8,u8) {
    (inv(y),mul(x,inv(y)))
}

#[derive(Debug,Clone)]
pub struct Audit {
    pub flat_orbits: usize,
    pub fixed_orbits: usize,
    pub three_cycles: usize,
    pub moving_orbits: usize,
    pub magnetic_alias: (usize,usize,usize,i64,i64),
    pub electric_flat_leak: (usize,usize,i64),
    pub cycle_sha: String,
    pub operator_sha: String,
}

/// Prove exact source-compatible cyclic structure *only* on flat torus
/// sectors. Prove non-extension of a lossy 243-label projection to even
/// the magnetic operator, and non-closure of flat sector under H_E.
pub fn inspect() -> Result<Audit,String>{
    let torus=Torus2::build()?;
    let mut representatives=BTreeMap::<(u8,u8),usize>::new();
    for (i,(&potential,q)) in torus.magnetic.iter()
        .zip(&torus.representatives).enumerate() {
        if potential==0 {
            // In spanning tree gauge x0=y0=identity. The two noncontractible
            // length-two loops have holonomies x2=q[0], y1=q[2].
            let x=q[0];let y=q[2];
            if mul(x,y)!=mul(y,x) {
                return Err("flat torus has noncommuting cycles".into());
            }
            let label=canonical_pair(x,y);
            if representatives.insert(label,i).is_some() {
                return Err("duplicate flat gauge orbit label".into());
            }
        }
    }
    if representatives.len()!=8{return Err("expected eight flat orbits".into());}
    // Independently enumerate all Hom(Z^2,S3)/conjugation classes.
    let mut all=BTreeMap::<(u8,u8),bool>::new();
    for x in 0..6 {
        for y in 0..6 {
            if mul(x,y)==mul(y,x) {
                all.insert(canonical_pair(x,y),true);
            }
        }
    }
    if all.len()!=8 || all.keys().ne(representatives.keys()) {
        return Err("flat-sector classes disagree with group-theoretic enumeration".into());
    }
    let mut mapping=BTreeMap::new();
    for &(x,y) in representatives.keys() {
        let (nx,ny)=winding_rotation(x,y);
        if mul(nx,ny)!=mul(ny,nx){
            return Err("mapping class broke flatness".into());
        }
        let tgt=canonical_pair(nx,ny);
        if !representatives.contains_key(&tgt) {return Err("R escaped flat moduli".into());}
        for g in 0..6 {
            let transformed=winding_rotation(conjugate(g,x),conjugate(g,y));
            if canonical_pair(transformed.0,transformed.1)!=tgt {
                return Err("R is not independent of based gauge choice".into());
            }
        }
        mapping.insert((x,y),tgt);
    }
    if mapping.len()!=8 || mapping.values().collect::<std::collections::BTreeSet<_>>().len()!=8{
        return Err("R not a bijection".into());
    }
    let mut visited=std::collections::BTreeSet::new();
    let mut fixed=0;
    let mut triple=0;
    let mut cycle_bytes=Vec::new();
    for &origin in mapping.keys() {
        if !visited.insert(origin) {continue;}
        let first=*mapping.get(&origin).ok_or("missing C1")?;
        let second=*mapping.get(&first).ok_or("missing C2")?;
        let third=*mapping.get(&second).ok_or("missing closure")?;
        if third!=origin {return Err("C0/C1/C2 fails closure".into());}
        if first==origin {
            fixed+=1;
            if second!=origin {return Err("invalid fixed point".into());}
        } else {
            if first==second || second==origin {return Err("order-three collapsed".into());}
            visited.insert(first);
            visited.insert(second);
            triple+=1;
        }
        for (x,y) in [origin,first,second] {
            cycle_bytes.extend_from_slice(&[x,y]);
        }
    }
    if fixed!=2 || triple!=2 || visited.len()!=8 {
        return Err("unexpected C3 orbit cycle count".into());
    }

    // Gauge rotations (conjugations) act as IDENTITY on physical orbit classes.
    // Hence the nontrivial winding R is a different action, not residual
    // gauge conjugation dressed up as C1/C2.
    for &(x,y) in representatives.keys(){
        for g in 0..6 {
            if canonical_pair(conjugate(g,x),conjugate(g,y))!=(x,y) {
                return Err("physical gauge projection is not invariant".into());
            }
        }
    }

    // IMPORTANT COUNTEREXAMPLE: an address modulo 243 is many-to-one.
    // It cannot define an H_B action on the 243 labels if two physical
    // orbit states bearing the same label have different H_B diagonals.
    let mut labels=BTreeMap::<usize,(usize,i64)>::new();
    let mut alias=None;
    for (i,&key) in torus.keys.iter().enumerate() {
        let sector=key%243;
        let p=torus.magnetic[i];
        if let Some(&(j,other_p))=labels.get(&sector){
            if other_p!=p && alias.is_none(){
                alias=Some((i,j,sector,p,other_p));
            }
        } else {
            labels.insert(sector,(i,p));
        }
    }
    let magnetic_alias=alias.ok_or("no failure witness for 243-sector magnetic action")?;

    // Actual electric operator links the flat and nonflat magnetic sectors.
    // Therefore the eight-dimensional flat subspace is not an invariant
    // subspace under the mixed-coupling Hamiltonian when J_E>0.
    let mut leak=None;
    for (i,row) in torus.electric.iter().enumerate(){
        if torus.magnetic[i]!=0 {continue;}
        for &(j,coeff) in row {
            if i!=j && coeff!=0 && torus.magnetic[j]!=0 {
                leak=Some((i,j,coeff));
                break;
            }
        }
        if leak.is_some() {break;}
    }
    let electric_flat_leak=leak.ok_or("electric operator unexpectedly preserves flat-only subspace")?;

    let mut operator_bytes=Vec::new();
    for i in 0..DIM {
        operator_bytes.extend_from_slice(&(torus.keys[i] as u64).to_le_bytes());
        operator_bytes.extend_from_slice(&torus.weights[i].to_le_bytes());
        operator_bytes.extend_from_slice(&torus.magnetic[i].to_le_bytes());
        for &(j,value) in &torus.electric[i] {
            operator_bytes.extend_from_slice(&(j as u64).to_le_bytes());
            operator_bytes.extend_from_slice(&value.to_le_bytes());
        }
    }
    Ok(Audit {
        flat_orbits:representatives.len(),
        fixed_orbits:fixed,
        three_cycles:triple,
        moving_orbits:triple*3,
        magnetic_alias,
        electric_flat_leak,
        cycle_sha:hex(&sha256(&cycle_bytes)),
        operator_sha:hex(&sha256(&operator_bytes)),
    })
}

pub struct Receipt {
    pub hbp:Vec<u8>,
    pub hbi:Vec<u8>,
    pub anchor:String,
    pub measure:String,
}
pub fn generate() ->Result<Receipt,String>{
    let a=inspect()?;
    let sh=&a.operator_sha[..16];
    let (ai,aj,sector,p,other)=a.magnetic_alias;
    let (fi,fj,coeff)=a.electric_flat_leak;
    let body=format!(
        "HBP|schema=hebc.shadow_torus.math.v1|scope=FLAT_S3_MODULI_ONLY|C0_C1_C2=ORDER3_WINDING|source_law=ASOLARIA_LAW71_71_13|flat_orbits={}|fixed={}|cycles3={}|moving={}|cycle_sha={}|operator_sha={}|sh={sh}|magnetic_alias_i={ai}|magnetic_alias_j={aj}|alias_sector={sector}|potential_i={p}|potential_j={other}|electric_cross_i={fi}|electric_cross_j={fj}|cross_coeff={coeff}|law70_5_over_6=NO_CALL_ONLY|z_instant=LOGICAL_FREEZE_NOT_PHYSICAL_PROPAGATION|full_interacting_bridge=NOT_ESTABLISHED|prev={}",
        a.flat_orbits,a.fixed_orbits,a.three_cycles,a.moving_orbits,a.cycle_sha,
        a.operator_sha,hex(&[0u8;32])
    );
    let record_sha=sha256(body.as_bytes());
    let mut raw=Vec::new();
    raw.extend_from_slice(&[0u8;32]);
    raw.extend_from_slice(&record_sha);
    let chain=sha256(&raw);
    let hbp=format!("{body}|record_sha={}|chain={}|json=0\n",hex(&record_sha),hex(&chain)).into_bytes();
    let hbi=format!(
        "HBI|schema=hebc.shadow_torus.math.v1|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        hbp.len(),hex(&sha256(&hbp)),hex(&chain)
    ).into_bytes();
    let anchor=format!(
        "ANCHOR|schema=hebc.shadow_torus.math.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain)
    );
    let measure=format!(
        "SHADOWRESIDUAL|result=PASS|flat=8|c3_cycles=2|fixed=2|moving=6|R3=IDENTITY|gauge_invariant=1|magnetic_label_quotient=FAIL|flat_subspace_HE_invariant=0|full_H_symmetry=NOT_ESTABLISHED|c1=FLAT_STRUCTURAL_MATCH|z_instant=LOGICAL_IS_ONLY|source_law70=NO_CALL_MODE|operator_sha={}|cycle_sha={}|json=0\n",
        a.operator_sha,a.cycle_sha
    );
    Ok(Receipt{hbp,hbi,anchor,measure})
}

pub fn verify(record:&Receipt)->Result<(),String>{
    let fresh=generate()?;
    if fresh.hbp!=record.hbp || fresh.hbi!=record.hbi ||
       fresh.anchor!=record.anchor || fresh.measure!=record.measure {
        return Err("source-backed residual torus audit has changed".into());
    }
    Ok(())
}
pub fn write(path:&Path,record:&Receipt)->Result<(),String>{
    std::fs::create_dir_all(path).map_err(|e|e.to_string())?;
    for (file,body) in [
        ("run.hbp",record.hbp.as_slice()),("index.hbi",record.hbi.as_slice()),
        ("run.anchor",record.anchor.as_bytes()),("run.measure",record.measure.as_bytes())
    ] {
        std::fs::write(path.join(file),body).map_err(|e|e.to_string())?;
    }
    Ok(())
}
pub fn verify_dir(path:&Path)->Result<(),String>{
    let r=Receipt{
        hbp:std::fs::read(path.join("run.hbp")).map_err(|e|e.to_string())?,
        hbi:std::fs::read(path.join("index.hbi")).map_err(|e|e.to_string())?,
        anchor:std::fs::read_to_string(path.join("run.anchor")).map_err(|e|e.to_string())?,
        measure:std::fs::read_to_string(path.join("run.measure")).map_err(|e|e.to_string())?,
    };
    verify(&r)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn exact_c1_c2_winding_closure_in_physical_flat_moduli(){
        let a=inspect().unwrap();
        assert_eq!(a.flat_orbits,8);
        assert_eq!(a.three_cycles,2);
        assert_eq!(a.fixed_orbits,2);
        assert_eq!(a.moving_orbits,6);
    }
    #[test]
    fn obstructed_full_interacting_bridge_and_noninjective_address(){
        let a=inspect().unwrap();
        assert_ne!(a.magnetic_alias.3,a.magnetic_alias.4);
        assert_ne!(a.electric_flat_leak.2,0);
    }
    #[test]
    fn source_law70_ratio_is_not_a_hamiltonian_eigenvalue_claim(){
        // 5/6 is a lighthouse-specific transient NO-CALL mode; not a
        // generic eigenvalue. The 1/6 observer is an indexing role,
        // not Born-rule probability or a quantum excitation energy.
        let record=generate().unwrap();
        assert!(record.measure.contains("source_law70=NO_CALL_MODE"));
        assert!(record.measure.contains("full_H_symmetry=NOT_ESTABLISHED"));
    }
    #[test]
    fn source_law67_tetrahedral_minus_one_third_exact_integer_gram() {
        // Four 3D vectors with even parity of negative signs. Squared
        // norm=3 and every offdiagonal dot product=-1; hence normalized
        // overlap exactly -1/3. This is Law 67 geometry, NOT an
        // independent verification of Law 71's residual emission.
        let tetra:[[i64;3];4]=[
            [1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1],
        ];
        for axis in 0..3 {
            assert_eq!(tetra.iter().map(|v|v[axis]).sum::<i64>(),0);
        }
        for i in 0..4 {
            for j in 0..4 {
                let dot:i64=(0..3).map(|a|tetra[i][a]*tetra[j][a]).sum();
                assert_eq!(dot,if i==j {3} else {-1});
            }
        }
    }
    #[test]
    fn unscaled_integer_torus_hamiltonian_cannot_have_five_sixths_eigenvalue(){
        // det(6 H - 5 I) = det(I mod 6) = 1 mod 6. It cannot
        // vanish, whatever the dimension and integer couplings. Verify
        // entrywise congruence for the ACTUAL gauge-projected H.
        let torus=Torus2::build().unwrap();
        for (je,jb) in [(0,0),(1,0),(0,1),(1,1),(3,5)] {
            for (i,row) in torus.electric.iter().enumerate() {
                let mut diagonal=0i64;
                for &(j,v) in row {
                    if i==j { diagonal=v; }
                    else { assert_eq!((6*je*v).rem_euclid(6),0); }
                }
                let h_ii=je*diagonal+jb*torus.magnetic[i];
                assert_eq!((6*h_ii-5).rem_euclid(6),1);
            }
        }
        // This excludes the exact rational *energy* 5/6 for any
        // integral JE, JB, not a normalized transfer-matrix eigenvalue.
    }
    #[test]
    fn hbp_hbi_and_negative_controls(){
        let good=generate().unwrap();
        verify(&good).unwrap();
        let other=generate().unwrap();
        assert_eq!(good.hbp,other.hbp);
        assert_eq!(good.hbi,other.hbi);
        assert_eq!(good.anchor,other.anchor);
        let mut altered=generate().unwrap();
        altered.hbp[50]^=1;
        assert!(verify(&altered).is_err());
        let mut idx=generate().unwrap();
        idx.hbi[20]^=1;
        assert!(verify(&idx).is_err());
    }
}
