//! Stage 2I — exact RIME C3 flat-sector extension obstruction.
//!
//! The C3 winding action on eight flat S3 torus classes is well-defined.
//! No W-unitary operator U can BOTH map every normalized flat orbit-value
//! basis vector to its exact C3 rotated basis vector (up to phase) AND
//! commute with the native electric Hamiltonian, or either of the two
//! positive mixed-coupling Hamiltonians tested here. A fourth spectral
//! moment of one explicitly pinned pair gives an exact contradiction.
//! This does NOT exclude a different representation, modified dynamics,
//! or a less restrictive operator/observable bridge.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::torus2::{Torus2,DIM};
use crate::{hex,inv,mul,sha256};
use std::collections::{BTreeMap,BTreeSet};
use std::path::Path;

fn conjugate(g:u8,x:u8)->u8 {mul(mul(g,x),inv(g))}
fn pair_class(x:u8,y:u8)->(u8,u8) {
    (0..6u8).map(|g|(conjugate(g,x),conjugate(g,y)))
        .min().expect("S3 has identity")
}
fn rotate(x:u8,y:u8)->(u8,u8) {
    // Order-three SL(2,Z) action only on COMMUTING flat holonomies.
    (inv(y),mul(x,inv(y)))
}

#[derive(Debug,Clone,PartialEq,Eq)]
pub struct MomentWitness {
    pub je:i64,
    pub jb:i64,
    pub source:[i128;4],
    pub target:[i128;4],
}
#[derive(Debug,Clone,PartialEq,Eq)]
pub struct Audit {
    pub flat_states:usize,
    pub fixed:usize,
    pub cycles3:usize,
    pub source_pair:(u8,u8),
    pub target_pair:(u8,u8),
    pub source_index:usize,
    pub target_index:usize,
    pub source_weight:u64,
    pub target_weight:u64,
    pub moments:[MomentWitness;3],
    pub axis_swap_equal:bool,
    pub torus_anchor_sha:String,
    pub witness_sha:String,
}

fn flat_classes(m:&Torus2)->Result<BTreeMap<(u8,u8),usize>,String> {
    let mut out=BTreeMap::new();
    for (i,(&pot,q)) in m.magnetic.iter().zip(&m.representatives).enumerate() {
        if pot!=0 {continue;}
        let x=q[0];let y=q[2];
        if mul(x,y)!=mul(y,x) {
            return Err("noncommuting holonomies in flat orbit".into());
        }
        let label=pair_class(x,y);
        if out.insert(label,i).is_some() {
            return Err("duplicate flat holonomy class".into());
        }
    }
    if out.len()!=8 {return Err("expected eight flat gauge orbits".into());}
    Ok(out)
}

/// Exact moment M_k = <e_i,H^k e_i>_W / <e_i,e_i>_W
///                 = (H^k)_{ii}, for k=1..4.
/// The orbit-value basis has metric W=diag(orbit cardinalities).
fn moments(m:&Torus2,i:usize,je:i64,jb:i64)->Result<[i128;4],String> {
    if i>=DIM {return Err("bad spectral moment index".into());}
    let mut e=vec![0i128;DIM];
    e[i]=1;
    let mut result=[0i128;4];
    for value in &mut result {
        e=m.apply(je,jb,&e)?;
        *value=e[i];
    }
    Ok(result)
}
fn compare(m:&Torus2,a:usize,b:usize,je:i64,jb:i64)
    ->Result<MomentWitness,String>
{
    Ok(MomentWitness{je,jb,source:moments(m,a,je,jb)?,
        target:moments(m,b,je,jb)?})
}
pub fn inspect()->Result<Audit,String> {
    let m=Torus2::build()?;
    // Recheck that the actual source operator is self-adjoint in W.
    m.validate()?;
    let flats=flat_classes(&m)?;
    let mut image=BTreeMap::new();
    for (&(x,y),&i) in &flats {
        let target=pair_class(rotate(x,y).0,rotate(x,y).1);
        let &j=flats.get(&target).ok_or("rotation escaped flat space")?;
        // The exact basis permutation is W-unitary only if weights match.
        if m.weights[i]!=m.weights[j] {
            return Err("winding changes exact orbit basis normalization".into());
        }
        image.insert((x,y),target);
    }
    if image.values().collect::<BTreeSet<_>>().len()!=8 {
        return Err("flat rotation not a bijection".into());
    }
    let mut seen=BTreeSet::new();
    let mut fixed=0usize;
    let mut cycles3=0usize;
    for &x in image.keys(){
        if seen.contains(&x){continue;}
        let y=*image.get(&x).ok_or("first C3 image missing")?;
        let z=*image.get(&y).ok_or("second C3 image missing")?;
        if image.get(&z)!=Some(&x) {return Err("R^3 not identity".into());}
        if x==y {fixed+=1;seen.insert(x);}
        else if x!=z && y!=z {
            cycles3+=1;
            seen.insert(x);seen.insert(y);seen.insert(z);
        } else {return Err("C3 three-cycle collapsed".into());}
    }
    if fixed!=2 || cycles3!=2 || seen.len()!=8 {
        return Err("flat-sector orbit decomposition changed".into());
    }

    // Choose the canonical nontrivial conjugacy class of transposition
    // holonomy in y direction. The original source R sends (0,1)->(1,1).
    let source_pair=(0,1);
    let target_pair=*image.get(&source_pair).ok_or("source class missing")?;
    if target_pair!=(1,1) {return Err("canonical C3 winding target changed".into());}
    let source_index=*flats.get(&source_pair).ok_or("source index missing")?;
    let target_index=*flats.get(&target_pair).ok_or("target index missing")?;
    let wa=m.weights[source_index];let wb=m.weights[target_index];
    if wa!=3 || wb!=3 {return Err("witness orbit weights changed".into());}

    let moments=[
        compare(&m,source_index,target_index,1,0)?,
        compare(&m,source_index,target_index,1,1)?,
        compare(&m,source_index,target_index,3,5)?,
    ];
    // This test is the actual no-go: unitary conjugation preserving H
    // would preserve EVERY moment of a normalized basis state.
    for witness in &moments {
        if witness.source[..3]!=witness.target[..3] ||
           witness.source[3]==witness.target[3] {
            return Err("fourth-moment obstruction not reproduced".into());
        }
    }
    // Exact independently-checkable regression values (NOT float spectra).
    if moments[0].source != [24,600,15552,417192] ||
       moments[0].target != [24,600,15552,416784] ||
       moments[1].source != [24,600,15648,426792] ||
       moments[1].target != [24,600,15648,426384] ||
       moments[2].source != [72,5400,424224,35123112] ||
       moments[2].target != [72,5400,424224,35090064] {
        return Err("native fourth-moment witnesses differ from pinned values".into());
    }
    // Legitimate square-axis swap (x,0)<->(0,x) is NOT ruled out by
    // this obstruction; it is an important discriminating control.
    let x=*flats.get(&(1,0)).ok_or("axis x missing")?;
    let y=*flats.get(&(0,1)).ok_or("axis y missing")?;
    let axis_swap_equal=[(1,0),(1,1),(3,5)].iter()
        .try_fold(true,|prior,&(je,jb)|{
            Ok::<bool,String>(prior && self::moments(&m,x,je,jb)?==self::moments(&m,y,je,jb)?)
        })?;
    if !axis_swap_equal {return Err("valid square-axis swap control failed".into());}

    let prior=crate::torus2::certificate(1,1)?;
    let torus_anchor_sha=hex(&sha256(prior.anchor.as_bytes()));
    let mut bytes=Vec::new();
    bytes.extend_from_slice(torus_anchor_sha.as_bytes());
    for item in &moments{
        bytes.extend_from_slice(&item.je.to_le_bytes());
        bytes.extend_from_slice(&item.jb.to_le_bytes());
        for x in item.source.iter().chain(item.target.iter()) {
            bytes.extend_from_slice(&x.to_le_bytes());
        }
    }
    let witness_sha=hex(&sha256(&bytes));
    Ok(Audit{
        flat_states:flats.len(),fixed,cycles3,source_pair,target_pair,
        source_index,target_index,source_weight:wa,target_weight:wb,moments,
        axis_swap_equal,torus_anchor_sha,witness_sha,
    })
}

#[derive(Debug,Clone)]
pub struct Receipt {
    pub hbp:Vec<u8>,pub hbi:Vec<u8>,pub anchor:String,pub measure:String
}
pub fn generate()->Result<Receipt,String>{
    let a=inspect()?;
    let e=&a.moments[0];
    let h=&a.moments[1];
    let k=&a.moments[2];
    let body=format!(
        "HBP|schema=hebc.rime.torus.moment.v1|source_law=LAW71_C3|scope=NATIVE_1393_S3|flat={}|fixed={}|cycles3={}|C0=0,1|C1=1,1|source_index={}|target_index={}|orbit_weights={},{}|M1_M2_M3_match=1|E4={},{}|H11_4={},{}|H35_4={},{}|axis_swap_control=PASS|unitary_exact_basis_extension_commuting_HE=OBSTRUCTED|unitary_exact_basis_extension_commuting_H11=OBSTRUCTED|unitary_exact_basis_extension_commuting_H35=OBSTRUCTED|general_bridge=NOT_ESTABLISHED|law70_ratio_as_energy=0|instant_ftl_proven=0|torus_anchor_sha={}|witness_sha={}|json=0|prev={}",
        a.flat_states,a.fixed,a.cycles3,a.source_index,a.target_index,
        a.source_weight,a.target_weight,
        e.source[3],e.target[3],h.source[3],h.target[3],
        k.source[3],k.target[3],a.torus_anchor_sha,a.witness_sha,hex(&[0u8;32])
    );
    let record_sha=sha256(body.as_bytes());
    let mut chain_input=Vec::new();
    chain_input.extend_from_slice(&[0u8;32]);
    chain_input.extend_from_slice(&record_sha);
    let chain=sha256(&chain_input);
    let hbp=format!("{body}|record_sha={}|chain={}|json=0\n",
        hex(&record_sha),hex(&chain)).into_bytes();
    let hbi=format!(
        "HBI|schema=hebc.rime.torus.moment.v1|record=1|offset=0|len={}|row_sha={}|chain={}|json=0\n",
        hbp.len(),hex(&sha256(&hbp)),hex(&chain)).into_bytes();
    let anchor=format!(
        "ANCHOR|schema=hebc.rime.torus.moment.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain));
    let measure=format!(
        "RIMEMOMENT|result=PASS|states={DIM}|flat=8|C3=EXACT_FLAT_ONLY|source_index={}|target_index={}|electric_fourth={},{}|mixed_1_1_fourth={},{}|mixed_3_5_fourth={},{}|full_exact_basis_symmetry=NO_GO|broader_bridge=UNRESOLVED|witness_sha={}|json=0\n",
        a.source_index,a.target_index,
        e.source[3],e.target[3],h.source[3],h.target[3],
        k.source[3],k.target[3],a.witness_sha
    );
    Ok(Receipt{hbp,hbi,anchor,measure})
}
pub fn verify(a:&Receipt)->Result<(),String>{
    let b=generate()?;
    if a.hbp!=b.hbp||a.hbi!=b.hbi||a.anchor!=b.anchor||a.measure!=b.measure {
        return Err("RIME/torus moment provenance or replay mismatch".into());
    }
    Ok(())
}
pub fn save(path:&Path,a:&Receipt)->Result<(),String>{
    std::fs::create_dir_all(path).map_err(|e|e.to_string())?;
    for (name,bytes) in [
        ("run.hbp",a.hbp.as_slice()),("index.hbi",a.hbi.as_slice()),
        ("run.anchor",a.anchor.as_bytes()),("run.measure",a.measure.as_bytes())
    ] {std::fs::write(path.join(name),bytes).map_err(|e|e.to_string())?;}
    Ok(())
}
pub fn verify_directory(path:&Path)->Result<(),String>{
    let a=Receipt{
        hbp:std::fs::read(path.join("run.hbp")).map_err(|e|e.to_string())?,
        hbi:std::fs::read(path.join("index.hbi")).map_err(|e|e.to_string())?,
        anchor:std::fs::read_to_string(path.join("run.anchor")).map_err(|e|e.to_string())?,
        measure:std::fs::read_to_string(path.join("run.measure")).map_err(|e|e.to_string())?,
    };
    verify(&a)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]
    fn flat_c3_fourth_moment_is_exact_non_extension_witness(){
        let a=inspect().unwrap();
        assert_eq!((a.flat_states,a.fixed,a.cycles3),(8,2,2));
        assert_eq!((a.source_index,a.target_index),(271,276));
        assert_eq!(a.moments[0].source[3]-a.moments[0].target[3],408);
        assert_eq!(a.moments[1].source[3]-a.moments[1].target[3],408);
        assert_eq!(a.moments[2].source[3]-a.moments[2].target[3],33048);
        assert!(a.axis_swap_equal);
    }
    #[test]
    fn deterministic_receipts_reject_changed_hbp_and_hbi(){
        let a=generate().unwrap();
        verify(&a).unwrap();
        assert_eq!(a.hbp,generate().unwrap().hbp);
        let mut broken=a.clone();broken.hbp[100]^=1;
        assert!(verify(&broken).is_err());
        let mut broken=a;broken.hbi[40]^=1;
        assert!(verify(&broken).is_err());
    }
}
