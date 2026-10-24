//! Standalone Clasy X3 81-mode finite-field kernel behind the HEB-C virtual
//! address interface. This does NOT convert its shell law to Yang-Mills physics.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::{address, hex, sha256, VIRTUAL_KERNELS};
use continuum_clay_variation::{
    conserved_invariant81, predicted_step81, prism81, shell_total81, unprism81,
    OmegaOmnibitRoom, ShellModel81, K, P, DRIFT81,
};
use continuum_clay_variation::host8_audit::{identity, mix, word, TOTAL_ROOMS, SEED};
use std::fs;
use std::path::Path;

const GENESIS: [u8;32] = [0;32];
const LIMIT: u64 = 10_000;
const MODEL: &str = "clasy_x3_81_shell_v1";
pub const CLASY_UPSTREAM: &str = "63cbf283b900457f8dfc59ac0e42d3efcbc9aedb";

pub struct Run {
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    pub anchor: String,
    pub report: String,
    pub final_sha: String,
    pub source_sha: String,
}

fn field<'a>(row: &'a str, name: &str) -> Result<&'a str,String> {
    let mut found = None;
    for item in row.split('|').skip(1) {
        let (key,val) = item.split_once('=').ok_or("malformed field")?;
        if key == name && found.replace(val).is_some() { return Err("duplicate field".into()); }
    }
    found.ok_or_else(|| format!("missing {name}"))
}

/// Reconstruct exactly three canonical, globally indexed Host8 room addresses.
/// The virtual namespace is much larger than this *active* three-room task.
fn room_input(virtual_id: u64) -> Result<([u8;24],u64),String> {
    let base = (virtual_id % (TOTAL_ROOMS/3))*3;
    let mut bytes = [0u8;24];
    for i in 0..3u64 {
        let n = base+i;
        let stub = mix(word(n)? ^ SEED);
        identity(n,stub)?;
        bytes[(i as usize)*8..(i as usize+1)*8].copy_from_slice(&stub.to_le_bytes());
    }
    Ok((bytes,base))
}

fn state_bytes(state: &[u64; K]) -> Vec<u8> {
    let mut out = Vec::with_capacity(K*8);
    for &v in state { out.extend_from_slice(&v.to_le_bytes()); }
    out
}

pub fn calculate(ordinal: u64, nu: u64, steps: u64) -> Result<Run,String> {
    if steps == 0 || steps > LIMIT { return Err("steps must be 1..10000".into()); }
    let virtual_id = address(ordinal);
    let (room_bytes,base) = room_input(virtual_id)?;
    let source_sha = hex(&sha256(&room_bytes));
    let sh = &source_sha[..16];
    let room = OmegaOmnibitRoom::from_bytes(&room_bytes);
    let mut model = ShellModel81::from_room(room,nu,333_360);
    let initial = model.u;
    let q0 = shell_total81(&initial);
    let initial_transform = prism81(&initial);
    if initial_transform[0] != q0 || unprism81(&initial_transform) != initial {
        return Err("initial 81-point transform invalid".into());
    }
    let mut hbp = Vec::new();
    let mut hbi = Vec::new();
    let mut chain = GENESIS;
    for tick in 1..=steps {
        let expected = predicted_step81(&model.u,nu);
        model.step();
        if model.u != expected || conserved_invariant81(&model.u,nu,tick) != q0 ||
           model.u.iter().any(|&u|u >= P) {
            return Err(format!("Clasy invariant/independent step mismatch at {tick}"));
        }
        let state_sha = hex(&sha256(&state_bytes(&model.u)));
        let body = format!(
            "HBP|schema=hebc.clasy81.v1|kernel={MODEL}|source_commit={CLASY_UPSTREAM}|ordinal={ordinal}|virtual_id={virtual_id}|room_base={base}|source_sha={source_sha}|sh={sh}|nu={nu}|tick={tick}|q0={q0}|qnow={}|drift={DRIFT81}|invariant={q0}|state_sha={state_sha}|prev={}",
            shell_total81(&model.u), hex(&chain)
        );
        let rec_sha = sha256(body.as_bytes());
        let mut link = Vec::with_capacity(64);
        link.extend_from_slice(&chain);
        link.extend_from_slice(&rec_sha);
        chain = sha256(&link);
        let row = format!("{body}|record_sha={}|chain={}|json=0\n",hex(&rec_sha),hex(&chain));
        let off = hbp.len();
        let index = format!(
            "HBI|schema=hebc.clasy81.v1|tick={tick}|sh={sh}|offset={off}|len={}|row_sha={}|chain={}|json=0\n",
            row.len(), hex(&sha256(row.as_bytes())),hex(&chain)
        );
        hbp.extend_from_slice(row.as_bytes());
        hbi.extend_from_slice(index.as_bytes());
    }
    let final_transform = prism81(&model.u);
    if final_transform[0] != shell_total81(&model.u) ||
       unprism81(&final_transform) != model.u {
        return Err("final 81-point transform invalid".into());
    }
    let final_sha = hex(&sha256(&state_bytes(&model.u)));
    let anchor = format!(
        "ANCHOR|schema=hebc.clasy81.v1|kernel={MODEL}|ticks={steps}|source_commit={CLASY_UPSTREAM}|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain)
    );
    let report = format!(
        "CLASY81|result=PASS|ordinal={ordinal}|virtual_id={virtual_id}|active_rooms=3|modes=81|ticks={steps}|nu={nu}|q0={q0}|drift={DRIFT81}|source_sha={source_sha}|final_sha={final_sha}|records={steps}|virtual_namespace={VIRTUAL_KERNELS}|json=0\n"
    );
    Ok(Run{hbp,hbi,anchor,report,final_sha,source_sha})
}

/// Fail-closed byte-exact HBI, HBP, hash-chain and declared-invariant verifier.
/// This replays the recorded arithmetic invariant, and an independent call to
/// calculate(...) verifies the actual physics trajectory against the receipt bytes.
pub fn verify(hbp: &[u8],hbi: &[u8],anchor: &str) -> Result<usize,String> {
    if !hbp.ends_with(b"\n") || !hbi.ends_with(b"\n") || !anchor.ends_with('\n') {
        return Err("unterminated evidence".into());
    }
    let a=anchor.trim_end_matches('\n');
    if a.contains('\n') || !a.starts_with("ANCHOR|") ||
       field(a,"schema")? != "hebc.clasy81.v1" ||
       field(a,"kernel")? != MODEL || field(a,"source_commit")? != CLASY_UPSTREAM {
        return Err("invalid Clasy anchor".into());
    }
    let total=field(a,"ticks")?.parse::<usize>().map_err(|_|"bad tick count")?;
    if total == 0 || total > LIMIT as usize { return Err("invalid tick bound".into()); }
    if field(a,"hbp_sha")? != hex(&sha256(hbp)) ||
       field(a,"hbi_sha")? != hex(&sha256(hbi)) {
        return Err("root digest mismatch".into());
    }
    let records:Vec<&[u8]>=hbp.split_inclusive(|&x|x==b'\n').collect();
    let indices:Vec<&[u8]>=hbi.split_inclusive(|&x|x==b'\n').collect();
    if records.len()!=total || indices.len()!=total {return Err("row count mismatch".into());}
    let mut chain=GENESIS;
    let mut offset=0usize;
    let mut first: Option<(u64,u64,String)> = None;
    for (i,(&row,&index)) in records.iter().zip(indices.iter()).enumerate() {
        if !row.ends_with(b"\n") || !index.ends_with(b"\n") {return Err("short row".into());}
        let r=std::str::from_utf8(row).map_err(|_|"invalid HBP UTF8")?.trim_end();
        let idx=std::str::from_utf8(index).map_err(|_|"invalid HBI UTF8")?.trim_end();
        if !r.starts_with("HBP|") || !idx.starts_with("HBI|") ||
           field(r,"schema")? != "hebc.clasy81.v1" ||
           field(r,"kernel")? != MODEL || field(r,"source_commit")? != CLASY_UPSTREAM ||
           field(r,"json")? != "0" || field(idx,"schema")? != "hebc.clasy81.v1" ||
           field(idx,"json")? != "0" {
            return Err(format!("bad schema at {}",i+1));
        }
        let tick=i+1;
        if field(r,"tick")? != tick.to_string() ||
           field(idx,"tick")? != tick.to_string() ||
           field(idx,"offset")? != offset.to_string() ||
           field(idx,"len")? != row.len().to_string() ||
           field(idx,"row_sha")? != hex(&sha256(row)) ||
           field(r,"prev")? != hex(&chain) {
            return Err(format!("HBI or predecessor mismatch tick {tick}"));
        }
        let ordinal=field(r,"ordinal")?.parse::<u64>().map_err(|_|"ordinal")?;
        let vid=field(r,"virtual_id")?.parse::<u64>().map_err(|_|"virtual_id")?;
        let nu=field(r,"nu")?.parse::<u64>().map_err(|_|"nu")?;
        let source_sha=field(r,"source_sha")?.to_string();
        if source_sha.len()!=64 || field(r,"sh")? != &source_sha[..16] ||
           field(idx,"sh")? != &source_sha[..16] {
            return Err("SHA-to-SH locator disagreement".into());
        }
        if vid != address(ordinal) ||
           field(r,"room_base")? != (vid%(TOTAL_ROOMS/3)*3).to_string() ||
           field(r,"drift")? != DRIFT81.to_string() ||
           field(r,"q0")? != field(r,"invariant")? {
            return Err("Clasy coordinate/invariant mismatch".into());
        }
        let q0=field(r,"q0")?.parse::<u64>().map_err(|_|"q0")?;
        let qnow=field(r,"qnow")?.parse::<u64>().map_err(|_|"qnow")?;
        let expected_q = (q0 as u128+P as u128-
            ((tick as u128 * (nu%P) as u128 * DRIFT81 as u128)%P as u128))%P as u128;
        if qnow != expected_q as u64 {return Err("all-time invariant mismatch".into());}
        match &first {
            Some((o,n,s)) if *o!=ordinal || *n!=nu || *s!=source_sha =>
                return Err("kernel request changed mid-chain".into()),
            None => first=Some((ordinal,nu,source_sha)),
            _=>{}
        }
        let (body,_) = r.split_once("|record_sha=").ok_or("record SHA delimiter")?;
        let rec_sha=sha256(body.as_bytes());
        if field(r,"record_sha")? != hex(&rec_sha) {return Err("record SHA mismatch".into());}
        let mut link=Vec::with_capacity(64);
        link.extend_from_slice(&chain);
        link.extend_from_slice(&rec_sha);
        chain=sha256(&link);
        if field(r,"chain")? != hex(&chain) || field(idx,"chain")? != hex(&chain) {
            return Err("HASH link mismatch".into());
        }
        offset+=row.len();
    }
    if offset != hbp.len() || field(a,"chain")? != hex(&chain) {
        return Err("anchor end mismatch".into());
    }
    // Recalculate original model from pinned Clasy source; prevents a self-
    // consistent fake trace with a different final result passing verification.
    let (ordinal,nu,_) = first.ok_or("missing request")?;
    let rerun=calculate(ordinal,nu,total as u64)?;
    if rerun.hbp != hbp || rerun.hbi != hbi || rerun.anchor != anchor {
        return Err("re-execution mismatch".into());
    }
    Ok(total)
}

pub fn save(dir:&Path,run:&Run)->Result<(),String> {
    fs::create_dir_all(dir).map_err(|e|e.to_string())?;
    fs::write(dir.join("run.hbp"),&run.hbp).map_err(|e|e.to_string())?;
    fs::write(dir.join("index.hbi"),&run.hbi).map_err(|e|e.to_string())?;
    fs::write(dir.join("run.anchor"),&run.anchor).map_err(|e|e.to_string())?;
    fs::write(dir.join("run.measure"),&run.report).map_err(|e|e.to_string())?;
    Ok(())
}

pub fn load_and_verify(dir:&Path)->Result<usize,String> {
    let hbp=fs::read(dir.join("run.hbp")).map_err(|e|e.to_string())?;
    let hbi=fs::read(dir.join("index.hbi")).map_err(|e|e.to_string())?;
    let anchor=fs::read_to_string(dir.join("run.anchor")).map_err(|e|e.to_string())?;
    verify(&hbp,&hbi,&anchor)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn original_clasy_model_invariant_and_full_81_ntt() {
        for nu in [0,1,P-1,P,P+1,u64::MAX] {
            let record=calculate(11,nu,81).unwrap();
            assert_eq!(verify(&record.hbp,&record.hbi,&record.anchor),Ok(81));
            let again=calculate(11,nu,81).unwrap();
            assert_eq!(record.hbp,again.hbp);
            assert_eq!(record.hbi,again.hbi);
            assert_eq!(record.anchor,again.anchor);
        }
    }
    #[test]
    fn corrupted_trace_or_root_rejected() {
        let run=calculate(1,1,9).unwrap();
        let mut modified=run.hbp.clone();
        let i=modified.iter().position(|&b|b==b'q').unwrap();
        modified[i]=b'X';
        assert!(verify(&modified,&run.hbi,&run.anchor).is_err());
        let mut anchor=run.anchor.clone();
        anchor=anchor.replace(&hex(&sha256(&run.hbp)),&hex(&sha256(&modified)));
        assert!(verify(&modified,&run.hbi,&anchor).is_err());
        let mut index=run.hbi.clone();
        index[10]=b'X';
        assert!(verify(&run.hbp,&index,&run.anchor).is_err());
    }
    #[test]
    fn arithmetic_namespace_and_distinct_kernel_ids() {
        let a=calculate(0,1,3).unwrap();
        let b=calculate(22_999_999_999,1,3).unwrap();
        assert_ne!(a.source_sha,b.source_sha);
        assert_eq!(verify(&a.hbp,&a.hbi,&a.anchor),Ok(3));
        assert_eq!(verify(&b.hbp,&b.hbi,&b.anchor),Ok(3));
    }
}
