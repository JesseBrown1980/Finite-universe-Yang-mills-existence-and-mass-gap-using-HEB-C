//! Integer-only deterministic second-order wave-equation test on the exact
//! 1393-state gauge-invariant finite S3 Hamiltonian.
//!
//! This is NOT real-time Schrodinger unitary dynamics: it is the finite
//! discrete wave equation delta² q + H q / D = 0 with rounded integer
//! arithmetic. It tests whether the operator produces measurable observable
//! changes under controlled initial conditions, not 4D Yang-Mills evolution.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::{hex, sha256, torus2::{Torus2, DIM}};

pub const MAX_WAVE_STEPS: usize = 243;
pub const OPERATOR_SHA: &str =
    "b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3";
const INITIAL_AMPLITUDE: i128 = 1_000_000_000;
const MAX_AMPLITUDE: i128 = 1_000_000_000_000_000;

fn rounded_ratio(n: i128, d: i128) -> Result<i128, String> {
    if d<=0 { return Err("integer denominator must be positive".into()); }
    let mag=n.checked_abs().ok_or("integer absolute overflow")?;
    let value=mag.checked_add(d/2).ok_or("integer quotient overflow")? / d;
    Ok(if n<0 { -value } else { value })
}
fn integer_sha(state: &[i128]) -> String {
    let mut bytes=Vec::with_capacity(state.len()*16);
    for x in state { bytes.extend_from_slice(&x.to_le_bytes()); }
    hex(&sha256(&bytes))
}
fn summary(torus:&Torus2,q:&[i128],je:i64,jb:i64,step:usize,changed:bool)
    -> Result<String,String>
{
    let e=torus.apply(1,0,q)?;
    let mut norm=0_i128;
    let mut m_num=0_i128;
    let mut e_num=0_i128;
    let mut flat=0_i128;
    let mut nonzero=0_usize;
    let mut minimum=i128::MAX;
    let mut maximum=i128::MIN;
    for i in 0..DIM {
        let w=i128::from(torus.weights[i]);
        let q2=q[i].checked_mul(q[i]).ok_or("amplitude squared overflow")?;
        let mass=w.checked_mul(q2).ok_or("weighted amplitude overflow")?;
        norm=norm.checked_add(mass).ok_or("norm overflow")?;
        m_num=m_num.checked_add(mass*i128::from(torus.magnetic[i]))
            .ok_or("magnetic moment overflow")?;
        e_num=e_num.checked_add(w*q[i]*e[i]).ok_or("electric moment overflow")?;
        if torus.magnetic[i]==0 { flat+=mass; }
        if q[i]!=0 { nonzero+=1; }
        minimum=minimum.min(q[i]);
        maximum=maximum.max(q[i]);
    }
    if norm<=0 || e_num<0 {return Err("invalid integer norm or electric form".into());}
    let mag_milli=m_num.checked_mul(1000).ok_or("magnet ratio overflow")?/norm;
    let elec_milli=e_num.checked_mul(1000).ok_or("electric ratio overflow")?/norm;
    let flat_milli=flat.checked_mul(1000).ok_or("flat ratio overflow")?/norm;
    let total_milli=i128::from(je)*elec_milli+i128::from(jb)*mag_milli;
    Ok(format!("HEBC-WAVE|result=MEASURED|mode=INTEGER_DISCRETE_WAVE|step={step}|JE={je}|JB={jb}|magnetic_milli={mag_milli}|electric_milli={elec_milli}|coupled_energy_milli={total_milli}|flat_weight_milli={flat_milli}|nonzero={nonzero}|min_amplitude={minimum}|max_amplitude={maximum}|changed={}|state_sha={}|json=0\n",
        u8::from(changed),integer_sha(q)))
}

/// A deterministic full-space wave update, including weighted electric graph
/// transfers and all magnetic plaquette potential values on each step.
/// No projection towards a pre-selected eigenstate or gap is performed.
pub fn evolve(torus:&Torus2,je:i64,jb:i64,steps:usize)->Result<String,String>{
    if !(0..=10).contains(&je)||!(0..=10).contains(&jb)||
        steps==0||steps>MAX_WAVE_STEPS{
        return Err("JE/JB must be 0..10 and steps must be 1..243".into());
    }
    if torus.electric.len()!=DIM || torus.weights.len()!=DIM{
        return Err("full 1393-state torus required".into());
    }
    let divisor=4_i128*(48_i128*i128::from(je)+12_i128*i128::from(jb))+1;
    let mut prev=vec![INITIAL_AMPLITUDE;DIM];
    let mut current=prev.clone();
    let mut output=format!("HEBC-WAVE|result=PASS|kind=BEGIN|physical_dim={DIM}|operator_sha={OPERATOR_SHA}|JE={je}|JB={jb}|steps={steps}|scheme=SECOND_ORDER_INTEGER_QUANTIZED|time_kind=DISCRETE_STEPS|integer_divisor={divisor}|gauge_reduced=1|real_time_unitary=0|continuum_YM_proven=0|json=0\n");
    output.push_str(&summary(torus,&current,je,jb,0,false)?);
    let start_sha=integer_sha(&current);
    let mut changed_frames=0_usize;
    let mut electric_ever_positive=false;
    let mut mag_first=None;
    let mut mag_varied=false;
    let mut kinetic_first=None;
    let mut kinetic_varied=false;
    for step in 1..=steps{
        let h=torus.apply(je,jb,&current)?;
        let mut next=Vec::with_capacity(DIM);
        for i in 0..DIM {
            let acceleration=rounded_ratio(h[i],divisor)?;
            let value=current[i].checked_mul(2)
                .and_then(|x|x.checked_sub(prev[i]))
                .and_then(|x|x.checked_sub(acceleration))
                .ok_or("second order integer update overflow")?;
            if value.checked_abs().ok_or("abs overflow")?>MAX_AMPLITUDE {
                return Err("amplitude guard; fail closed".into());
            }
            next.push(value);
        }
        let is_changed=next!=current;
        if is_changed {changed_frames+=1;}
        let observation=summary(torus,&next,je,jb,step,is_changed)?;
        let mag=observation.split('|').find_map(|part|
            part.strip_prefix("magnetic_milli=").and_then(|v|v.parse::<i128>().ok()))
            .ok_or("missing magnetic measurement")?;
        let elec=observation.split('|').find_map(|part|
            part.strip_prefix("electric_milli=").and_then(|v|v.parse::<i128>().ok()))
            .ok_or("missing electric measurement")?;
        electric_ever_positive|=elec>0;
        if let Some(m)=mag_first { mag_varied|=mag!=m; } else { mag_first=Some(mag); }
        if let Some(e)=kinetic_first { kinetic_varied|=elec!=e; } else { kinetic_first=Some(elec); }
        output.push_str(&observation);
        prev=current;
        current=next;
    }
    let end_sha=integer_sha(&current);
    output.push_str(&format!("HEBC-WAVE|result=PASS|kind=END|JE={je}|JB={jb}|steps={steps}|state_changed={}|changed_frames={changed_frames}|electric_positive_seen={}|magnetic_varied={}|electric_varied={}|initial_state_sha={start_sha}|final_state_sha={end_sha}|new_physical_particles_created=0|physics_claim=FINITE_MODEL_ONLY|json=0\n",
        u8::from(start_sha!=end_sha),u8::from(electric_ever_positive),u8::from(mag_varied),u8::from(kinetic_varied)));
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn integer_division_rounding_has_no_floats(){
        assert_eq!(rounded_ratio(10,3).unwrap(),3);
        assert_eq!(rounded_ratio(-10,3).unwrap(),-3);
        assert_eq!(rounded_ratio(11,3).unwrap(),4);
        assert!(rounded_ratio(10,0).is_err());
    }
    #[test]
    fn full_operator_control_vs_interacting_change(){
        let t=Torus2::build().unwrap();
        let electric=evolve(&t,1,0,27).unwrap();
        let magnetic=evolve(&t,0,1,27).unwrap();
        let coupled=evolve(&t,1,1,27).unwrap();
        assert!(electric.contains("kind=END|JE=1|JB=0|steps=27|state_changed=0"));
        assert!(magnetic.contains("kind=END|JE=0|JB=1|steps=27|state_changed=1"));
        assert!(coupled.contains("kind=END|JE=1|JB=1|steps=27|state_changed=1"));
        assert_ne!(magnetic,coupled);
        assert!(coupled.contains("electric_positive_seen=1"));
        assert_eq!(coupled,evolve(&t,1,1,27).unwrap());
    }
    #[test]
    fn guard_rejects_invalid_requests(){
        let t=Torus2::build().unwrap();
        assert!(evolve(&t,-1,1,1).is_err());
        assert!(evolve(&t,1,1,244).is_err());
        assert!(evolve(&t,1,1,0).is_err());
    }
}
