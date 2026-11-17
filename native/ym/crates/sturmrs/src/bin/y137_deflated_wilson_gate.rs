//! #137 — conservative two-state / deflated Wilson exact inequality.
//!
//! Assumptions for an actual theorem (NOT supplied merely by input parsing):
//!   u1,u2: orthonormal physical witnesses; Q=u1*u1^*+u2*u2^*.
//!   psi1,psi2: normalized exact simple E1,E2 eigenvectors.
//!   m1>=|<u2,psi1>|, m2>=|<u1,psi2>|;
//!   eps_i>=||(I-Q)psi_i||.
//!   wij>=|<ui,O uj>| and w21_lower<=|<u2,O u1>|.
//!   zj>=||(I-Q)O uj||, zstarj>=||(I-Q)O* uj||.
//!   op>=||O||.
//!
//! A rigorous sufficient inequality is c1^2*c2^2*w21_lower^2 > penalty^2,
//! c_i^2=1-m_i^2-eps_i^2 (strictly positive), with
//! penalty= m2*w11+m1*w22+m1*m2*w12
//!        +eps2*(z1+m1*z2)+eps1*(zstar2+m2*zstar1)
//!        +op*eps1*eps2.
//! Every number is exact rational BigInt. This verifies only the algebraic
//! gate for externally *proved* parameter intervals. No source-backed
//! eigenprojector/mixing/deflated-O inputs are supplied in this PR.
//! Thus even an algebraic PASS reports actual_Wilson_weight=HOLD.

use num_bigint::{BigInt, Sign};
use num_integer::Integer;
use num_traits::{One, Signed, Zero};
use std::collections::BTreeMap;
use std::env;
use std::fs;

#[derive(Clone, Debug, PartialEq, Eq)]
struct Rat {
    n: BigInt,
    d: BigInt,
}

impl Rat {
    fn new(n: BigInt, d: BigInt) -> Result<Self, String> {
        if d.is_zero() {
            return Err("zero denominator".to_owned());
        }
        let (n, d) = if d.sign() == Sign::Minus {
            (-n, -d)
        } else {
            (n, d)
        };
        let g = n.gcd(&d);
        Ok(Self { n: n / &g, d: d / &g })
    }
    fn parse(s: &str) -> Result<Self, String> {
        let fields: Vec<&str> = s.split('/').collect();
        if fields.len() != 2 {
            return Err("exact rational requires numerator/denominator".to_owned());
        }
        let mut parsed = Vec::new();
        for v in fields {
            let t = v.as_bytes();
            let sign = t.first().copied() == Some(b'-');
            let digits = if sign { &t[1..] } else { t };
            if digits.is_empty() || !digits.iter().all(u8::is_ascii_digit) {
                return Err("invalid signed decimal integer".to_owned());
            }
            let n = BigInt::parse_bytes(t, 10)
                .ok_or_else(|| "unable to parse signed decimal".to_owned())?;
            parsed.push(n);
        }
        Self::new(parsed[0].clone(), parsed[1].clone())
    }
    fn from_int(v: i32) -> Self {
        Self::new(BigInt::from(v), BigInt::one()).expect("nonzero denominator")
    }
    fn add(&self, b: &Self) -> Self {
        Self::new(&self.n * &b.d + &b.n * &self.d, &self.d * &b.d)
            .expect("nonzero positive denominator")
    }
    fn sub(&self, b: &Self) -> Self {
        Self::new(&self.n * &b.d - &b.n * &self.d, &self.d * &b.d)
            .expect("nonzero positive denominator")
    }
    fn mul(&self, b: &Self) -> Self {
        Self::new(&self.n * &b.n, &self.d * &b.d)
            .expect("nonzero positive denominator")
    }
    fn square(&self) -> Self {
        self.mul(self)
    }
    fn lt(&self, b: &Self) -> bool {
        &self.n * &b.d < &b.n * &self.d
    }
    fn positive(&self) -> bool {
        self.n.is_positive()
    }
    fn nonnegative(&self) -> bool {
        !self.n.is_negative()
    }
    fn printable(&self) -> String {
        format!("{}/{}", self.n, self.d)
    }
}

const INPUTS: [&str; 13] = [
    "mix_psi1_u2_max",
    "mix_psi2_u1_max",
    "outside_psi1_max",
    "outside_psi2_max",
    "wilson_11_abs_max",
    "wilson_22_abs_max",
    "wilson_12_abs_max",
    "wilson_21_abs_min",
    "deflated_o_u1_max",
    "deflated_o_u2_max",
    "deflated_ostar_u1_max",
    "deflated_ostar_u2_max",
    "wilson_operator_norm_max",
];

fn source_text(input: &str) -> Result<BTreeMap<String, Rat>, String> {
    let mut values=BTreeMap::new();
    for line in input.lines() {
        let line=line.trim();
        if line.is_empty() || line.starts_with('#') { continue; }
        let (key, val) = line.split_once('=')
            .ok_or_else(|| "each source row must be key=num/den".to_owned())?;
        if !INPUTS.contains(&key) || values.contains_key(key) {
            return Err(format!("unexpected or duplicated source field: {key}"));
        }
        values.insert(key.to_owned(),Rat::parse(val)?);
    }
    if values.len()!=INPUTS.len() {
        return Err(format!("missing exact fields: expected {}, got {}",INPUTS.len(),values.len()));
    }
    Ok(values)
}

fn calc(v: &BTreeMap<String,Rat>) -> Result<(Rat,Rat,bool),String> {
    let value=|key: &str| v.get(key).expect("validated complete exact input");
    let m1=value("mix_psi1_u2_max");
    let m2=value("mix_psi2_u1_max");
    let ep1=value("outside_psi1_max");
    let ep2=value("outside_psi2_max");
    let w11=value("wilson_11_abs_max");
    let w22=value("wilson_22_abs_max");
    let w12=value("wilson_12_abs_max");
    let w21=value("wilson_21_abs_min");
    let z1=value("deflated_o_u1_max");
    let z2=value("deflated_o_u2_max");
    let zs1=value("deflated_ostar_u1_max");
    let zs2=value("deflated_ostar_u2_max");
    let op=value("wilson_operator_norm_max");
    for (key,r) in v {
        if !r.nonnegative() {
            return Err(format!("negative interval upper/lower magnitude: {key}"));
        }
    }
    let one=Rat::from_int(1);
    if !m1.lt(&one) || !m2.lt(&one) || !ep1.lt(&one) || !ep2.lt(&one) {
        return Err("projection/mixing bound >=1 cannot establish fidelity".to_owned());
    }
    if !w21.lt(&op) && w21!=op {
        return Err("Wilson signal lower bound exceeds operator norm".to_owned());
    }
    for (key,upper) in [
        ("wilson_11_abs_max",w11),
        ("wilson_22_abs_max",w22),
        ("wilson_12_abs_max",w12),
        ("deflated_o_u1_max",z1),
        ("deflated_o_u2_max",z2),
        ("deflated_ostar_u1_max",zs1),
        ("deflated_ostar_u2_max",zs2),
    ] {
        if op.lt(upper) {
            return Err(format!("upper bound exceeds global operator ceiling: {key}"));
        }
    }
    let c1s=one.sub(&m1.square()).sub(&ep1.square());
    let c2s=one.sub(&m2.square()).sub(&ep2.square());
    if !c1s.positive() || !c2s.positive() {
        return Err("nonpositive certified lower squared witness fidelity".to_owned());
    }
    let mut penalty=m2.mul(w11).add(&m1.mul(w22));
    penalty=penalty.add(&m1.mul(m2).mul(w12));
    penalty=penalty.add(&ep2.mul(&z1.add(&m1.mul(z2))));
    penalty=penalty.add(&ep1.mul(&zs2.add(&m2.mul(zs1))));
    penalty=penalty.add(&op.mul(ep1).mul(ep2));
    let signal_square=c1s.mul(&c2s).mul(&w21.square());
    let contamination_square=penalty.square();
    let passes=contamination_square.lt(&signal_square);
    Ok((signal_square,contamination_square,passes))
}

fn example() -> String {
    [
        "mix_psi1_u2_max=1/100",
        "mix_psi2_u1_max=1/100",
        "outside_psi1_max=1/100",
        "outside_psi2_max=1/100",
        "wilson_11_abs_max=1/5",
        "wilson_22_abs_max=1/5",
        "wilson_12_abs_max=1/10",
        "wilson_21_abs_min=1/10",
        "deflated_o_u1_max=1/50",
        "deflated_o_u2_max=1/50",
        "deflated_ostar_u1_max=1/50",
        "deflated_ostar_u2_max=1/50",
        "wilson_operator_norm_max=14/1",
    ].join("\n")
}

fn verify_and_print(inputs: &str, scope: &str) -> Result<(),String> {
    let v=source_text(inputs)?;
    let (signal,contamination,pass)=calc(&v)?;
    println!("Y137_DEFLECTED_WILSON|scope={scope}|signal_lower_square={}|contamination_upper_square={}|algebraic_gate={}|source_authenticated=NO|actual_Wilson_weight=HOLD|json=0",
        signal.printable(),contamination.printable(),
        if pass {"PASS_CONDITIONAL"} else {"HOLD"});
    Ok(())
}

fn main() {
    let args: Vec<String>=env::args().collect();
    let result=if args.len()==2 && args[1]=="toy" {
        verify_and_print(&example(),"TOY_ONLY")
    } else if args.len()==3 && args[1]=="verify" {
        fs::read_to_string(&args[2])
            .map_err(|e|format!("receipt read: {e}"))
            .and_then(|s|verify_and_print(&s,"UNAUTHENTICATED_INPUT"))
    } else {
        Err("usage: y137_deflated_wilson_gate toy | verify EXACT_PARAMS.txt".to_owned())
    };
    if let Err(e)=result {
        eprintln!("Y137_DEFLECTED_WILSON_REFUSE|reason={e}|actual_Wilson_weight=HOLD|json=0");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn toy_passes_conservative_theorem() {
        let v=source_text(&example()).expect("toy receipt");
        let (_,_,pass)=calc(&v).expect("toy algebra");
        assert!(pass);
    }
    #[test]
    fn large_contamination_cannot_pass() {
        let s=example().replace("outside_psi2_max=1/100","outside_psi2_max=4/5");
        let (_,_,pass)=calc(&source_text(&s).expect("input")).expect("algebra");
        assert!(!pass);
    }
    #[test]
    fn missing_or_forged_input_rejected() {
        assert!(source_text("mix_psi1_u2_max=1/5").is_err());
        assert!(source_text(&format!("{}\nmix_psi1_u2_max=1/5",example())).is_err());
        assert!(source_text(&example().replace("1/50","1.0")).is_err());
        assert!(source_text(&example().replace("1/100","-1/100")).is_ok());
        assert!(calc(&source_text(&example().replace("1/100","-1/100")).expect("parsed")).is_err());
    }
    #[test]
    fn zero_gap_signal_holds() {
        let s=example().replace("wilson_21_abs_min=1/10","wilson_21_abs_min=0/1");
        let (_,_,pass)=calc(&source_text(&s).expect("input")).expect("algebra");
        assert!(!pass);
    }
}
