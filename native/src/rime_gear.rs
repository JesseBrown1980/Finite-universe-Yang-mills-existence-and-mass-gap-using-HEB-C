//! Stage 2F — shadow-cat Rime gear connection as a finite exact model.
//! Pins original Law 70's 3-level retention 2/3 and Law 71's signed
//! per-calling presence -1/3 WITHOUT conflating their distinct origins.
//! Three conceptual torus roles join through a shared IS, with no direct
//! WAS-WILL edge. "Instant" is a same-process atomic logical read of an
//! already-arrived snapshot, not FTL remote information transfer.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::{hex,sha256};
use std::path::Path;

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum TorusRole { Was, Is, Will }
impl TorusRole {
    const ALL:[Self;3]=[Self::Was,Self::Is,Self::Will];
    const fn code(self)->u8 {
        match self {Self::Was=>0,Self::Is=>1,Self::Will=>2}
    }
}

/// Directed/mediated calling topology. A direct temporal connection
/// between WAS and WILL is explicitly forbidden by Law 71 §71.2.
pub const fn mediated_call(a:TorusRole,b:TorusRole)->bool {
    matches!(
        (a,b),
        (TorusRole::Was,TorusRole::Is)|
        (TorusRole::Is,TorusRole::Was)|
        (TorusRole::Is,TorusRole::Will)|
        (TorusRole::Will,TorusRole::Is)
    )
}

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Thirds {
    pub signed_calling:i64,
    pub retained:i64,
    pub passed:i64,
    pub denominator:i64,
}

/// Exact integer calculations in units of thirds:
/// Law 71 signed *calling* -1/3, Law 70's n=3 *NO-CALL pass*
/// retains 2/3 and passes 1/3. They are two different operators;
/// the relation 3 + (-1) == 2 is a permitted *bookkeeping convention*
/// and not independently proved to be the same physical mechanism.
pub fn thirds()->Thirds {
    Thirds{signed_calling:-1,retained:2,passed:1,denominator:3}
}

/// A frozen central IS snapshot can be read through all three roles.
/// Its origin/provenance is an *already arrived* byte buffer.
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Snapshot {
    pub source_sha:String,
    pub source_departure:u64,
    pub source_arrival:u64,
    pub play_epoch:u64,
    pub is_revision:u64,
    pub frozen_sha:String,
    pub views:[String;3],
}
pub fn freeze(source:&[u8],departure:u64,arrival:u64,play:u64,revision:u64)
    -> Result<Snapshot,String> {
    if departure>arrival||arrival>play {
        return Err("a current play cannot contain data that has not arrived".into());
    }
    let source_sha=hex(&sha256(source));
    let mut frame=Vec::new();
    frame.extend_from_slice(b"HEBC-RIME-GEAR-IS-V1");
    frame.extend_from_slice(&revision.to_le_bytes());
    frame.extend_from_slice(&play.to_le_bytes());
    frame.extend_from_slice(source);
    let frozen_sha=hex(&sha256(&frame));
    let views=std::array::from_fn(|_|frozen_sha.clone());
    Ok(Snapshot{source_sha,source_departure:departure,source_arrival:arrival,
        play_epoch:play,is_revision:revision,frozen_sha,views})
}
pub fn validate_snapshot(snapshot:&Snapshot)->Result<(),String>{
    let t=thirds();
    if t.signed_calling!=-1||t.retained+t.passed!=t.denominator ||
       t.denominator+t.signed_calling!=t.retained {
        return Err("signed and retained third bookkeeping changed".into());
    }
    if mediated_call(TorusRole::Was,TorusRole::Will) ||
       !mediated_call(TorusRole::Is,TorusRole::Was) ||
       !mediated_call(TorusRole::Is,TorusRole::Will) {
        return Err("wrong mediated temporal topology".into());
    }
    if snapshot.source_departure>snapshot.source_arrival ||
       snapshot.source_arrival>snapshot.play_epoch ||
       snapshot.views.iter().any(|v|v!=&snapshot.frozen_sha) {
        return Err("stale/forged freeze or invalid light provenance".into());
    }
    Ok(())
}
#[derive(Clone,Debug)]
pub struct Audit {
    pub hbp:Vec<u8>,pub hbi:Vec<u8>,pub anchor:String,pub measure:String
}
pub fn generate()->Result<Audit,String>{
    let old=freeze(b"source-time-slice",2,5,7,0)?;
    validate_snapshot(&old)?;
    let next=freeze(b"source-time-slice",2,5,8,1)?;
    validate_snapshot(&next)?;
    if old.views==next.views {return Err("frozen revision did not change".into());}
    // What the two peripheral tori observe depends on the *selected*
    // frozen frame. When the main process changes its pointer to NEXT,
    // the old immutable copies do not change. This proves no shared
    // memory notification to an independent distant receiver.
    let cached_remote=old.views[TorusRole::Will.code() as usize].clone();
    if cached_remote!=old.frozen_sha || cached_remote==next.frozen_sha {
        return Err("missing stale-snapshot control".into());
    }
    if freeze(b"source-time-slice",2,9,8,1).is_ok() {
        return Err("accepted information before its arrival".into());
    }
    let t=thirds();
    let mut words=Vec::new();
    for role in TorusRole::ALL {words.push(role.code());}
    let topology_sha=hex(&sha256(&words));
    let mut material=Vec::new();
    material.extend_from_slice(topology_sha.as_bytes());
    material.extend_from_slice(old.frozen_sha.as_bytes());
    material.extend_from_slice(next.frozen_sha.as_bytes());
    let source_sha=hex(&sha256(&material));
    let sh=&source_sha[..16];
    let body=format!(
        "HBP|schema=hebc.rime.gear.v1|source_law=LAW70_LAW71|roles=WAS_IS_WILL|edges=WAS_IS,IS_WILL|direct_WAS_WILL=0|calling={}/{}|retained={}/{}|passed={}/{}|separate_laws=1|source_arrived_before_play=1|cached_remote_auto_updates=0|instant_scope=ATOMIC_LOCAL_SNAPSHOT|physical_ftl_proven=0|source_sha={source_sha}|sh={sh}|prev={}",
        t.signed_calling,t.denominator,t.retained,t.denominator,
        t.passed,t.denominator,hex(&[0u8;32])
    );
    let record_sha=sha256(body.as_bytes());
    let mut hash_input=Vec::new();
    hash_input.extend_from_slice(&[0u8;32]);hash_input.extend_from_slice(&record_sha);
    let chain=sha256(&hash_input);
    let hbp=format!("{body}|record_sha={}|chain={}|json=0\n",hex(&record_sha),hex(&chain)).into_bytes();
    let hbi=format!(
        "HBI|schema=hebc.rime.gear.v1|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        hbp.len(),hex(&sha256(&hbp)),hex(&chain)
    ).into_bytes();
    let anchor=format!(
        "ANCHOR|schema=hebc.rime.gear.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain)
    );
    let measure=format!(
        "RIMEGEAR|result=PASS|toruses=3|mediator=IS|cat_branches_per_torus=3|signed=-1/3|retained=2/3|passed=1/3|relation_type=BOOKKEEPING_NOT_DERIVED_COUPLING|instant=LOCAL_FREEZE|remote_auto_update=0|ftl_proven=0|source_sha={source_sha}|json=0\n"
    );
    Ok(Audit{hbp,hbi,anchor,measure})
}
pub fn verify(a:&Audit)->Result<(),String>{
    let b=generate()?;
    if b.hbp!=a.hbp||b.hbi!=a.hbi||b.anchor!=a.anchor||b.measure!=a.measure {
        return Err("Rime graph/provenance/hash replay mismatch".into());
    }
    Ok(())
}
pub fn write(directory:&Path,a:&Audit)->Result<(),String>{
    std::fs::create_dir_all(directory).map_err(|e|e.to_string())?;
    for (name,bytes) in [
        ("run.hbp",a.hbp.as_slice()),("index.hbi",a.hbi.as_slice()),
        ("run.anchor",a.anchor.as_bytes()),("run.measure",a.measure.as_bytes())
    ] {std::fs::write(directory.join(name),bytes).map_err(|e|e.to_string())?;}
    Ok(())
}
pub fn verify_directory(directory:&Path)->Result<(),String>{
    let r=Audit {
        hbp:std::fs::read(directory.join("run.hbp")).map_err(|e|e.to_string())?,
        hbi:std::fs::read(directory.join("index.hbi")).map_err(|e|e.to_string())?,
        anchor:std::fs::read_to_string(directory.join("run.anchor")).map_err(|e|e.to_string())?,
        measure:std::fs::read_to_string(directory.join("run.measure")).map_err(|e|e.to_string())?,
    };
    verify(&r)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn exact_thirds_and_mediate_only(){
        let t=thirds();
        assert_eq!(t.signed_calling,-1);
        assert_eq!(t.retained,2);
        assert_eq!(t.passed,1);
        assert_eq!(t.denominator,3);
        for &a in &TorusRole::ALL{
            for &b in &TorusRole::ALL{
                assert_eq!(mediated_call(a,b),matches!(
                    (a,b),(TorusRole::Was,TorusRole::Is)|
                    (TorusRole::Is,TorusRole::Was)|
                    (TorusRole::Is,TorusRole::Will)|
                    (TorusRole::Will,TorusRole::Is)
                ));
            }
        }
    }
    #[test]
    fn central_gear_is_shared_snapshot_not_remote_ftl(){
        let old=freeze(b"light",0,4,5,0).unwrap();
        let new=freeze(b"light",0,4,6,1).unwrap();
        assert_ne!(old.views,new.views);
        assert_eq!(old.views[2],old.frozen_sha);
        assert_ne!(old.views[2],new.frozen_sha);
        validate_snapshot(&old).unwrap();
        validate_snapshot(&new).unwrap();
        assert!(freeze(b"new remote measurement",7,9,8,1).is_err());
        let mut forged=new.clone();
        forged.views[2]=old.frozen_sha;
        assert!(validate_snapshot(&forged).is_err());
    }
    #[test]
    fn exact_receipt_replay_and_adversarial_mutation(){
        let a=generate().unwrap();
        verify(&a).unwrap();
        let mut forged=generate().unwrap();
        forged.hbp[90]^=1;
        assert!(verify(&forged).is_err());
        let mut bad_index=generate().unwrap();
        bad_index.hbi[40]^=1;
        assert!(verify(&bad_index).is_err());
    }
}
