//! Exactly scaled-integer wave test for the finite 1,393-state S3 operator.
//! Every amplitude is q_t / D^t. No rounding, division, floats or JSON.
//! The specified second-order recurrence is exact over the rationals;
//! this is NOT real-time unitary quantum evolution.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]
use std::cmp::Ordering;
use crate::{hex, sha256, torus2::{Torus2, DIM}};

pub const MAX_WAVE_STEPS: usize = 243;
const INITIAL_AMPLITUDE: i128 = 1;
const BASE: u128 = 1_000_000_000;

/// Arbitrary-size signed integer with 1e9 little-endian limbs. A private
/// self-contained representation avoids a network Cargo dependency.
#[derive(Clone, Debug, PartialEq, Eq)]
struct Big {
    negative: bool,
    limbs: Vec<u32>,
}
impl Big {
    fn zero() -> Self { Self { negative:false, limbs:Vec::new() } }
    fn from_int(x:i128) -> Self {
        if x==0 {return Self::zero();}
        let negative=x<0;
        let mut v=x.unsigned_abs();
        let mut limbs=Vec::new();
        while v!=0 { limbs.push((v%BASE) as u32); v/=BASE; }
        Self { negative,limbs }
    }
    fn is_zero(&self) -> bool {self.limbs.is_empty()}
    fn canonical(mut self) -> Self {
        while self.limbs.last()==Some(&0) {self.limbs.pop();}
        if self.limbs.is_empty(){self.negative=false;}
        self
    }
    fn compare_magnitude(&self,other:&Self)->Ordering{
        match self.limbs.len().cmp(&other.limbs.len()){
            Ordering::Equal=>self.limbs.iter().rev().cmp(other.limbs.iter().rev()),
            x=>x,
        }
    }
    fn magnitude_sum(a:&Self,b:&Self)->Vec<u32>{
        let mut carry=0_u64;
        let mut out=Vec::with_capacity(a.limbs.len().max(b.limbs.len())+1);
        for i in 0..a.limbs.len().max(b.limbs.len()) {
            let v=carry+u64::from(*a.limbs.get(i).unwrap_or(&0))+
                u64::from(*b.limbs.get(i).unwrap_or(&0));
            out.push((v%(BASE as u64)) as u32);
            carry=v/(BASE as u64);
        }
        if carry>0 {out.push(carry as u32);}
        out
    }
    /// a and b are unsigned magnitudes with a>=b.
    fn magnitude_difference(a:&Self,b:&Self)->Vec<u32>{
        let mut borrow=0_i64;
        let mut out=Vec::with_capacity(a.limbs.len());
        for i in 0..a.limbs.len(){
            let mut v=i64::from(a.limbs[i])-
                i64::from(*b.limbs.get(i).unwrap_or(&0))-borrow;
            borrow=0;
            if v<0 {v+=BASE as i64;borrow=1;}
            out.push(v as u32);
        }
        debug_assert_eq!(borrow,0);
        out
    }
    fn negated(&self)->Self {
        let mut t=self.clone();
        if !t.is_zero(){t.negative=!t.negative;}
        t
    }
    fn add(&self,other:&Self)->Self{
        if self.negative==other.negative {
            Self{negative:self.negative,limbs:Self::magnitude_sum(self,other)}.canonical()
        }else{
            match self.compare_magnitude(other){
                Ordering::Greater=>Self{negative:self.negative,limbs:Self::magnitude_difference(self,other)}.canonical(),
                Ordering::Less=>Self{negative:other.negative,limbs:Self::magnitude_difference(other,self)}.canonical(),
                Ordering::Equal=>Self::zero(),
            }
        }
    }
    fn sub(&self,other:&Self)->Self{self.add(&other.negated())}
    fn mul_int(&self,factor:i128)->Self{
        if factor==0||self.is_zero(){return Self::zero();}
        let mut carry=0_u128;
        let magnitude=factor.unsigned_abs();
        let mut limbs=Vec::with_capacity(self.limbs.len()+6);
        for &limb in &self.limbs {
            let v=u128::from(limb)*magnitude+carry;
            limbs.push((v%BASE) as u32);
            carry=v/BASE;
        }
        while carry>0 {limbs.push((carry%BASE) as u32);carry/=BASE;}
        Self{negative:self.negative != (factor<0),limbs}.canonical()
    }
    fn decimal_digits(&self)->usize{
        if let Some(&top)=self.limbs.last(){
            (self.limbs.len()-1)*9+top.to_string().len()
        }else{1}
    }
    fn encode(&self,bytes:&mut Vec<u8>){
        bytes.push(u8::from(self.negative));
        bytes.extend_from_slice(&(self.limbs.len() as u32).to_le_bytes());
        for v in &self.limbs{bytes.extend_from_slice(&v.to_le_bytes());}
    }
}
fn hash_state(state:&[Big])->String{
    let mut bytes=Vec::new();
    bytes.extend_from_slice(b"HEBC-EXACT-SCALED-WAVE-V1");
    for x in state{x.encode(&mut bytes);}
    hex(&sha256(&bytes))
}
fn apply_electric(t:&Torus2,state:&[Big])->Vec<Big>{
    t.electric.iter().map(|row|{
        let mut accum=Big::zero();
        for &(j,v) in row {accum=accum.add(&state[j].mul_int(i128::from(v)));}
        accum
    }).collect()
}
fn apply_hamiltonian(t:&Torus2,je:i64,jb:i64,state:&[Big],electric:&[Big])->Vec<Big>{
    (0..DIM).map(|i|electric[i].mul_int(i128::from(je))
        .add(&state[i].mul_int(i128::from(jb)*i128::from(t.magnetic[i])))).collect()
}
fn measure(t:&Torus2,state:&[Big],electric:&[Big],je:i64,jb:i64,
    step:usize,divisor:i128,changed:bool)->String{
    let electric_active=electric.iter().filter(|x|!x.is_zero()).count();
    let magnetic_active=(0..DIM).filter(|&i|t.magnetic[i]!=0&&!state[i].is_zero()).count();
    let flat_active=(0..DIM).filter(|&i|t.magnetic[i]==0&&!state[i].is_zero()).count();
    let nonzero=state.iter().filter(|x|!x.is_zero()).count();
    let max_digits=state.iter().map(Big::decimal_digits).max().unwrap_or(1);
    format!("HEBC-WAVE|result=MEASURED|mode=EXACT_INTEGER_SCALED|step={step}|JE={je}|JB={jb}|denominator_base={divisor}|denominator_power={step}|electric_active={electric_active}|magnetic_active={magnetic_active}|flat_active={flat_active}|nonzero={nonzero}|max_numerator_digits={max_digits}|changed={}|state_sha={}|json=0\n",u8::from(changed),hash_state(state))
}

/// Exact rational second-order update without any division in the recurrence.
/// For amplitudes x[t]=N[t]/D^t and x[-1]=x[0]=1, we have
///   N[0]=1, N[1]=D*1-H*1,
///   N[t+1]=(2D I-H)N[t]-D^2 N[t-1], for t>=1.
/// This implements the previous *unrounded* rational recurrence exactly.
pub fn evolve(t:&Torus2,je:i64,jb:i64,steps:usize)->Result<String,String>{
    if !(0..=10).contains(&je)||!(0..=10_000).contains(&jb)||
       steps==0||steps>MAX_WAVE_STEPS {
        return Err("JE must be 0..10, JB must be 0..10000, steps must be 1..243".into());
    }
    if t.electric.len()!=DIM||t.weights.len()!=DIM {return Err("full torus required".into());}
    let d=4_i128*(48_i128*i128::from(je)+12_i128*i128::from(jb))+1;
    let d2=d*d;
    let mut prev=vec![Big::from_int(INITIAL_AMPLITUDE);DIM];
    let mut electric=apply_electric(t,&prev);
    let mut output=format!("HEBC-WAVE|result=PASS|kind=BEGIN|physical_dim={DIM}|JE={je}|JB={jb}|steps={steps}|scheme=EXACT_INTEGER_NUMERATOR_RECURRENCE|division=NONE|rounding=NONE|denominator_base={d}|real_time_unitary=0|continuum_YM_proven=0|json=0\n");
    output.push_str(&measure(t,&prev,&electric,je,jb,0,d,false));
    let start_sha=hash_state(&prev);
    let h0=apply_hamiltonian(t,je,jb,&prev,&electric);
    let mut current=(0..DIM).map(|i|prev[i].mul_int(d).sub(&h0[i])).collect::<Vec<_>>();
    let mut changed_frames=0_usize;
    let mut electric_ever_active=false;
    let mut mag_ever_active=false;
    let mut electric_first=None;
    let mut electric_varied=false;
    let mut magnetic_first=None;
    let mut magnetic_varied=false;
    for step in 1..=steps{
        electric=apply_electric(t,&current);
        let changed=current.iter().zip(&prev).any(|(x,y)|x!=&y.mul_int(d));
        if changed {changed_frames+=1;}
        let ecount=electric.iter().filter(|x|!x.is_zero()).count();
        let mcount=(0..DIM).filter(|&i|t.magnetic[i]!=0&&!current[i].is_zero()).count();
        electric_ever_active|=ecount>0;
        mag_ever_active|=mcount>0;
        if let Some(last)=electric_first{electric_varied|=last!=ecount}else{electric_first=Some(ecount)}
        if let Some(last)=magnetic_first{magnetic_varied|=last!=mcount}else{magnetic_first=Some(mcount)}
        output.push_str(&measure(t,&current,&electric,je,jb,step,d,changed));
        if step==steps{break;}
        let h=apply_hamiltonian(t,je,jb,&current,&electric);
        let next=(0..DIM).map(|i|current[i].mul_int(2*d)
            .sub(&h[i]).sub(&prev[i].mul_int(d2))).collect::<Vec<_>>();
        prev=current;
        current=next;
    }
    let final_sha=hash_state(&current);
    output.push_str(&format!("HEBC-WAVE|result=PASS|kind=END|JE={je}|JB={jb}|steps={steps}|state_changed={}|changed_frames={changed_frames}|electric_active_seen={}|magnetic_active_seen={}|electric_varied={}|magnetic_varied={}|initial_state_sha={start_sha}|final_state_sha={final_sha}|division=NONE|rounding=NONE|new_physical_particles_created=0|physics_claim=FINITE_MODEL_ONLY|json=0\n",u8::from(changed_frames>0),u8::from(electric_ever_active),u8::from(mag_ever_active),u8::from(electric_varied),u8::from(magnetic_varied)));
    Ok(output)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test] fn integer_big_signed_arithmetic(){
        let a=Big::from_int(9_999_999_999);
        let b=Big::from_int(-3_000_000_000);
        assert_eq!(a.add(&b),Big::from_int(6_999_999_999));
        assert_eq!(a.sub(&b),Big::from_int(12_999_999_999));
        assert_eq!(b.mul_int(-3),Big::from_int(9_000_000_000));
        assert_eq!(Big::from_int(123).mul_int(0),Big::zero());
        let mut large=Big::from_int(1);
        for _ in 0..243 {large=large.mul_int(12_345);}
        assert!(large.decimal_digits()>900);
        assert_eq!(large.sub(&large),Big::zero());
        assert_eq!(large.negated().add(&large),Big::zero());
    }
    #[test] fn exact_electric_null_and_magnetic_control(){
        let t=Torus2::build().unwrap();
        let e=evolve(&t,1,0,27).unwrap();
        let m=evolve(&t,0,1,27).unwrap();
        let c=evolve(&t,1,1,27).unwrap();
        assert!(e.contains("kind=END|JE=1|JB=0|steps=27|state_changed=0"));
        assert!(m.contains("kind=END|JE=0|JB=1|steps=27|state_changed=1"));
        assert!(c.contains("kind=END|JE=1|JB=1|steps=27|state_changed=1"));
        assert!(c.contains("electric_active_seen=1"));
        assert_ne!(m,c);
        assert_eq!(c,evolve(&t,1,1,27).unwrap());
    }
    #[test] fn exact_no_rounding_controls(){
        let t=Torus2::build().unwrap();
        let a=evolve(&t,2,5,9).unwrap();
        assert!(a.contains("scheme=EXACT_INTEGER_NUMERATOR_RECURRENCE|division=NONE|rounding=NONE"));
        assert!(a.contains("denominator_power=9"));
        assert!(evolve(&t,0,0,244).is_err());
        assert!(evolve(&t,1,-1,10).is_err());
        assert!(evolve(&t,1,10001,10).is_err());
    }
}
