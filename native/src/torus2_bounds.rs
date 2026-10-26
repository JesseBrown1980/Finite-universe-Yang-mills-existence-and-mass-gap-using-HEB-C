//! Stage 2G: *quantitative*, conservative rational enclosures for the
//! lowest two eigenvalues of the existing 1,393-state weighted S3 torus.
//!
//! No floating point, guessed Ritz roots, dense diagonalization, or new model.
//! The bounds are deliberately not tight: they come from a positive Collatz
//! witness, the EXACT electric-only Poincare gap 6, and a two-vector min-max
//! upper bound in the correct Gauss-weighted inner product.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::torus2::{Torus2,DIM};
use crate::{character,hex,sha256};
use std::path::Path;

pub const DENOM:i128=1_000_000;
const SCALE:i128=1_000_000_000_000;
const ITERATIONS:usize=256;

#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Enclosure {
    pub je:i64,
    pub jb:i64,
    pub e0_lower:i128,
    pub e0_upper:i128,
    pub e1_lower:i128,
    pub e1_upper:i128,
    pub gap_lower:i128,
    pub gap_upper:i128,
    pub witness_sha:String,
    pub min_witness:i128,
    pub max_witness:i128,
}
fn ceil_div(n:i128,d:i128)->i128 {
    // d>0; div_euclid handles signed numerators without an unjustified
    // truncation-to-zero lower/upper bound.
    -((-n).div_euclid(d))
}
fn weighted_dot(a:&[i128],b:&[i128],w:&[u64])->Result<i128,String>{
    let mut sum=0i128;
    for ((&x,&y),&weight) in a.iter().zip(b).zip(w) {
        let term=x.checked_mul(y)
            .and_then(|n|n.checked_mul(i128::from(weight)))
            .ok_or("weighted dot multiplication overflow")?;
        sum=sum.checked_add(term).ok_or("weighted dot addition overflow")?;
    }
    Ok(sum)
}

/// Return conservative rational intervals for E0, E1 and E1-E0.
///
/// Proof, in the orbit-value Hilbert space with diagonal weights w:
/// 1. For positive v, l=min(Hv/v) <= E0 <= u=max(Hv/v)
///    by Collatz-Wielandt for the irreducible stoquastic H.
/// 2. For f_i=v_i*g_i, exact ground-state transform gives
///    <f,Hf>_w = sum_i w_i v_i^2 (Hv)_i/v_i *g_i^2
///             + JE/2 *sum_ij w_i(-E_ij)v_i v_j (g_i-g_j)^2.
///    The pure electric E has exactly proven Gauss-sector gap 6.
///    Comparing the weighted Dirichlet forms and variances shows that
///    E1(H) >= l + 6*JE*(min(v)/max(v))^2.
///    This does not assert v is the exact ground eigenvector.
/// 3. The integer Wilson difference z_i=v_i*(chi(Wx)-chi(Wy)) is
///    checked *exactly* to obey <v,z>_w=<v,H z>_w=0.
///    Hence the H compression on span(v,z) is diagonal. Provided
///    Rayleigh(z)>=u>=Rayleigh(v), Courant-Fischer gives E1<=Rayleigh(z).
///
/// All rounding is outward to denominator DENOM. This is a certified
/// finite-volume bound, not a tight spectral solver or continuum mass gap.
pub fn enclose(je:i64,jb:i64)->Result<Enclosure,String>{
    if !matches!((je,jb),(1,1)|(3,5)) {
        return Err("certified witness supports only (JE,JB)=(1,1),(3,5)".into());
    }
    let m=Torus2::build()?;
    m.electric_gap_witness()?;
    // Nonnegative, primitive shift M=shift*I-H. Positive integer power
    // iteration constructs a trial vector; the certificate never assumes
    // its convergence or numerical accuracy.
    let mut largest_diag=0i128;
    for (i,row) in m.electric.iter().enumerate(){
        let diag=row.iter().find(|(j,_)|*j==i).map(|(_,x)|*x)
            .ok_or("missing electric diagonal")?;
        let entry=i128::from(je)*i128::from(diag)
            +i128::from(jb)*i128::from(m.magnetic[i]);
        largest_diag=largest_diag.max(entry);
    }
    let shift=largest_diag+1;
    let mut v=vec![SCALE;DIM];
    for _ in 0..ITERATIONS {
        let hv=m.apply(je,jb,&v)?;
        let mut mv=Vec::with_capacity(DIM);
        for i in 0..DIM {
            let n=shift.checked_mul(v[i]).and_then(|x|x.checked_sub(hv[i]))
                .ok_or("shifted iterate overflow")?;
            if n<=0 {return Err("shifted nonnegative iterate failed".into());}
            mv.push(n);
        }
        let max_mv=*mv.iter().max().ok_or("missing vector")?;
        v=mv.iter().map(|&x| (x*SCALE+max_mv/2)/max_mv).collect();
        if v.iter().any(|&x|x<=0) {return Err("positive witness lost".into());}
    }
    let hv=m.apply(je,jb,&v)?;
    let mut lower=i128::MAX;
    let mut upper=i128::MIN;
    for (&h,&x) in hv.iter().zip(&v) {
        lower=lower.min((h*DENOM).div_euclid(x));
        upper=upper.max(ceil_div(h*DENOM,x));
    }
    let vmin=*v.iter().min().ok_or("no witness")?;
    let vmax=*v.iter().max().ok_or("no witness")?;
    // Conservative floor of 6*JE*(vmin/vmax)^2.
    let delta=6*i128::from(je)*vmin*vmin*DENOM/(vmax*vmax);
    let gap_lower=delta-(upper-lower);
    if gap_lower<=0 {return Err("positive gap cannot be certified from this witness".into());}

    // In spanning-tree gauge x0=y0=identity and the two length-two Wilson
    // holonomies are stored at free coordinates q[0] and q[2].
    let z:Vec<i128>=v.iter().zip(&m.representatives)
        .map(|(&x,q)|x*i128::from(character(q[0])-character(q[2])))
        .collect();
    let hz=m.apply(je,jb,&z)?;
    let vz=weighted_dot(&v,&z,&m.weights)?;
    let vhz=weighted_dot(&v,&hz,&m.weights)?;
    if vz!=0 || vhz!=0 {
        return Err("Wilson difference is not exactly H-orthogonal to positive witness".into());
    }
    let zz=weighted_dot(&z,&z,&m.weights)?;
    let zhz=weighted_dot(&z,&hz,&m.weights)?;
    if zz<=0 || zhz<=0 {return Err("invalid two-dimensional Ritz trial".into());}
    let e1_upper=ceil_div(zhz*DENOM,zz);
    if e1_upper<=upper {return Err("two-vector Ritz ordering cannot be certified".into());}
    let e1_lower=lower+delta;
    if e1_lower>e1_upper {return Err("inconsistent spectral enclosures".into());}

    let mut bytes=Vec::with_capacity(DIM*32+16);
    bytes.extend_from_slice(&je.to_le_bytes());
    bytes.extend_from_slice(&jb.to_le_bytes());
    for (&a,&b) in v.iter().zip(&z) {
        bytes.extend_from_slice(&a.to_le_bytes());
        bytes.extend_from_slice(&b.to_le_bytes());
    }
    Ok(Enclosure {
        je,jb,e0_lower:lower,e0_upper:upper,
        e1_lower,e1_upper,
        gap_lower,gap_upper:e1_upper-lower,
        witness_sha:hex(&sha256(&bytes)),
        min_witness:vmin,max_witness:vmax,
    })
}
pub struct Certificate {
    pub hbp:Vec<u8>,
    pub hbi:Vec<u8>,
    pub anchor:String,
    pub measure:String,
}
pub fn certificate(je:i64,jb:i64)->Result<Certificate,String>{
    let b=enclose(je,jb)?;
    let static_receipt=crate::torus2::certificate(je,jb)?;
    let static_anchor_sha=hex(&sha256(static_receipt.anchor.as_bytes()));
    let body=format!(
        "HBP|schema=hebc.s3.torus2.bounds.v1|geometry=periodic_2x2|states={DIM}|JE={je}|JB={jb}|scale={DENOM}|iterations={ITERATIONS}|E0=[{},{}]|E1=[{},{}]|gap=[{},{}]|gap_positive=1|method=POSITIVE_WITNESS_POINCARE_TWO_VECTOR_MINMAX|electric_gap=6|vmin={}|vmax={}|witness_sha={}|static_anchor_sha={static_anchor_sha}|tight=0|continuum_proven=0|prev={}",
        b.e0_lower,b.e0_upper,b.e1_lower,b.e1_upper,
        b.gap_lower,b.gap_upper,b.min_witness,b.max_witness,
        b.witness_sha,hex(&[0u8;32])
    );
    let record_sha=sha256(body.as_bytes());
    let mut chain_input=Vec::with_capacity(64);
    chain_input.extend_from_slice(&[0u8;32]);
    chain_input.extend_from_slice(&record_sha);
    let chain=sha256(&chain_input);
    let hbp=format!("{body}|record_sha={}|chain={}|json=0\n",hex(&record_sha),hex(&chain)).into_bytes();
    let sh=&b.witness_sha[..16];
    let hbi=format!(
        "HBI|schema=hebc.s3.torus2.bounds.v1|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        hbp.len(),hex(&sha256(&hbp)),hex(&chain)
    ).into_bytes();
    let anchor=format!(
        "ANCHOR|schema=hebc.s3.torus2.bounds.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain)
    );
    let measure=format!(
        "TORUS2BOUNDS|result=PASS|states={DIM}|JE={je}|JB={jb}|E0=[{},{}]/{DENOM}|E1=[{},{}]/{DENOM}|gap=[{},{}]/{DENOM}|positive=1|rigorous=1|tight=0|method=COLLATZ_POINCARE_MINMAX|witness_sha={}|static_anchor_sha={static_anchor_sha}|json=0\n",
        b.e0_lower,b.e0_upper,b.e1_lower,b.e1_upper,b.gap_lower,
        b.gap_upper,b.witness_sha
    );
    Ok(Certificate {hbp,hbi,anchor,measure})
}
pub fn verify(c:&Certificate,je:i64,jb:i64)->Result<(),String>{
    let expected=certificate(je,jb)?;
    if c.hbp!=expected.hbp || c.hbi!=expected.hbi ||
       c.anchor!=expected.anchor || c.measure!=expected.measure {
        return Err("integer torus spectral witness / receipt mismatch".into());
    }
    Ok(())
}
pub fn save(directory:&Path,c:&Certificate)->Result<(),String>{
    std::fs::create_dir_all(directory).map_err(|e|e.to_string())?;
    for (name,bytes) in [
        ("run.hbp",c.hbp.as_slice()),("index.hbi",c.hbi.as_slice()),
        ("run.anchor",c.anchor.as_bytes()),("run.measure",c.measure.as_bytes())
    ] {std::fs::write(directory.join(name),bytes).map_err(|e|e.to_string())?;}
    Ok(())
}
pub fn verify_directory(directory:&Path,je:i64,jb:i64)->Result<(),String>{
    let c=Certificate {
        hbp:std::fs::read(directory.join("run.hbp")).map_err(|e|e.to_string())?,
        hbi:std::fs::read(directory.join("index.hbi")).map_err(|e|e.to_string())?,
        anchor:std::fs::read_to_string(directory.join("run.anchor")).map_err(|e|e.to_string())?,
        measure:std::fs::read_to_string(directory.join("run.measure")).map_err(|e|e.to_string())?,
    };
    verify(&c,je,jb)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn two_independent_mixed_couplings_have_rational_positive_bounds(){
        let a=enclose(1,1).unwrap();
        let b=enclose(3,5).unwrap();
        assert_eq!((a.e0_lower,a.e0_upper,a.gap_lower),(7634198,7634199,671034));
        assert_eq!((b.e0_lower,b.e0_upper,b.gap_lower),(36699227,36699228,344589));
        for c in [a,b] {
            assert!(c.e0_lower<=c.e0_upper);
            assert!(c.e1_lower<=c.e1_upper);
            assert!(c.gap_lower>0 && c.gap_upper>=c.gap_lower);
        }
        assert!(enclose(0,0).is_err());
        assert!(enclose(1,0).is_err());
    }
    #[test]
    fn witness_and_hbp_hbi_anchor_are_deterministic_and_fail_closed(){
        let c=certificate(1,1).unwrap();
        verify(&c,1,1).unwrap();
        assert_eq!(c.hbp,certificate(1,1).unwrap().hbp);
        assert!(verify(&c,3,5).is_err());
        let mut changed=certificate(1,1).unwrap();
        changed.hbp[73]^=1;
        assert!(verify(&changed,1,1).is_err());
        let mut changed=certificate(1,1).unwrap();
        changed.hbi[35]^=1;
        assert!(verify(&changed,1,1).is_err());
    }
}
