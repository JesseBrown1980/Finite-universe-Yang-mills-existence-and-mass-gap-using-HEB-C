//! Stage 2H: exact integer rank-one inertia and excited-state Ritz witnesses.
//!
//! Certifies E1 > rational threshold using positive definiteness of a
//! rank-one update to W(H-tI), not an uncertified floating-point eigenvalue.
//! The PD proof constructs an approximate *integer* Cholesky factor of
//! (A-fudge*I)*SCALE^2, and proves the residual is strictly diagonally
//! dominant with positive diagonal using exact outward error bounds.
//! No floating point, JSON, new physics operator, or third-party crate.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::torus2::{Torus2,DIM};
use crate::{character,hex,sha256};
use std::path::Path;

const DEN:i128=1_000;
const POWER_SCALE:i128=1_000_000;
const FACTOR_SCALE:i128=1_000_000;
const RANK_STRENGTH:i128=60;
const ITERATIONS:usize=256;
const EXCITED_ITERATIONS:usize=512;
const EXCITED_SCALE:i128=1_000_000_000;
const OUT_DEN:i128=1_000_000;

#[derive(Clone,Debug)]
pub struct ResultBounds {
    pub je:i64,
    pub jb:i64,
    pub threshold:i128,
    pub e0_lower:i128,
    pub e0_upper:i128,
    pub e1_lower:i128,
    pub e1_upper:i128,
    pub gap_lower:i128,
    pub gap_upper:i128,
    pub min_cholesky_pivot:i128,
    pub residual_margin:i128,
    pub witness_sha:String,
}

fn sqrt_floor(n:u128)->u128 {
    if n==0 {return 0;}
    let bits=128-n.leading_zeros();
    let mut x=1u128 << bits.div_ceil(2);
    loop {
        let next=(x+n/x)/2;
        if next>=x {return x;}
        x=next;
    }
}
fn div_round(n:i128,d:i128)->i128 {
    assert!(d>0);
    // Sign-symmetric rounding with ties toward zero. Required to keep
    // exact antisymmetric Wilson sectors invariant under normalization.
    let mag=n.abs();
    let q=mag/d;
    let r=mag%d;
    let value=q+if r>d/2 {1} else {0};
    if n<0 {-value} else {value}
}
fn ceil_div(n:i128,d:i128)->i128 {
    assert!(d>0);
    -((-n).div_euclid(d))
}
fn dot_w(a:&[i128],b:&[i128],w:&[u64])->Result<i128,String> {
    let mut s=0i128;
    for ((&x,&y),&weight) in a.iter().zip(b).zip(w) {
        let term=x.checked_mul(y).and_then(|q|q.checked_mul(i128::from(weight)))
            .ok_or("weighted product overflow")?;
        s=s.checked_add(term).ok_or("weighted sum overflow")?;
    }
    Ok(s)
}

/// Construct L with exact integer entries. For B=A-fudge*I, set Q=B*S^2.
/// By rounded division, each off-diagonal residual
/// |Q_ij-(LL^T)_ij| <= ceil(L_jj/2), where j=min(i,j).
/// By floor-square-root rounding, each diagonal residual is >= 0.
/// Thus A*S^2-LL^T has strictly positive diagonal and is strictly
/// diagonally dominant if fudge*S^2 exceeds every off-diagonal error sum.
/// Symmetric strict diagonal dominance implies positive definiteness.
/// No dependence on the accuracy of an external numerical factorization.
fn integer_cholesky_pd(a:&[Vec<i128>],fudge:i128)->Result<(i128,i128),String> {
    let n=a.len();
    if n==0||fudge<=0||a.iter().any(|row|row.len()!=n) {
        return Err("invalid PD matrix".into());
    }
    let scale2=FACTOR_SCALE*FACTOR_SCALE;
    let mut l=vec![vec![0i128;n];n];
    let mut min_pivot=i128::MAX;
    for i in 0..n {
        for j in 0..=i {
            if a[i][j]!=a[j][i] {return Err("rank-one matrix is not symmetric".into());}
            let entry=if i==j {a[i][j]-fudge} else {a[i][j]};
            let q=entry.checked_mul(scale2).ok_or("scaled PD entry overflow")?;
            let mut used=0i128;
            for k in 0..j {
                let item=l[i][k].checked_mul(l[j][k]).ok_or("Cholesky product overflow")?;
                used=used.checked_add(item).ok_or("Cholesky sum overflow")?;
            }
            let r=q.checked_sub(used).ok_or("Cholesky subtraction overflow")?;
            if i==j {
                if r<=0 {return Err(format!("nonpositive pivot at row {i}"));}
                let p=sqrt_floor(r as u128) as i128;
                if p==0 {return Err("zero integer Cholesky pivot".into());}
                l[i][j]=p;
                min_pivot=min_pivot.min(p);
            } else {
                l[i][j]=div_round(r,l[j][j]);
            }
        }
    }
    let mut min_margin=i128::MAX;
    let mut prefix=0i128;
    for (i,row) in l.iter().enumerate() {
        // For j<i the column-j rounding error is <= ceil(L_jj/2).
        // For j>i the column-i rounding error is <= ceil(L_ii/2).
        let later=(n-i-1) as i128 * ((row[i]+1)/2);
        let radius=prefix.checked_add(later).ok_or("radius overflow")?;
        let margin=fudge.checked_mul(scale2).and_then(|f|f.checked_sub(radius))
            .ok_or("strict PD margin overflow")?;
        if margin<=0 {return Err(format!("Cholesky residual not certified at row {i}"));}
        min_margin=min_margin.min(margin);
        prefix=prefix.checked_add((row[i]+1)/2).ok_or("prefix overflow")?;
    }
    Ok((min_pivot,min_margin))
}

fn positive_ground_witness(m:&Torus2,je:i64,jb:i64)->Result<Vec<i128>,String> {
    let largest_diag=m.electric.iter().enumerate().map(|(i,row)| {
        let diag=row.iter().find(|(j,_)|*j==i).map(|(_,q)|*q).unwrap_or(0);
        i128::from(je)*i128::from(diag)+i128::from(jb)*i128::from(m.magnetic[i])
    }).max().ok_or("missing diagonal")?;
    let shift=largest_diag+1;
    let mut v=vec![POWER_SCALE;DIM];
    for _ in 0..ITERATIONS {
        let hv=m.apply(je,jb,&v)?;
        let mut p=Vec::with_capacity(DIM);
        for (&x,&hx) in v.iter().zip(&hv) {
            let y=shift*x-hx;
            if y<=0 {return Err("positive power witness failed".into());}
            p.push(y);
        }
        let max=*p.iter().max().ok_or("power result missing")?;
        v=p.iter().map(|&x|(x*POWER_SCALE+max/2)/max).collect();
        if v.iter().any(|&x|x<=0) {return Err("positive iteration rounded to zero".into());}
    }
    Ok(v)
}
fn positive_rank_matrix(m:&Torus2,v:&[i128],je:i64,jb:i64,tnum:i128)
    ->Result<(Vec<Vec<i128>>,i128),String>
{
    let norm=v.iter().zip(&m.weights).try_fold(0i128,|sum,(&x,&w)|{
        sum.checked_add(x.checked_mul(x)?
            .checked_mul(i128::from(w))?)
    }).ok_or("rank norm overflow")?;
    let u:Vec<i128>=v.iter().zip(&m.weights)
        .map(|(&x,&w)|x*i128::from(w)).collect();
    let mut a=vec![vec![0i128;DIM];DIM];
    let bulk=DEN*norm;
    for (i,row) in a.iter_mut().enumerate() {
        for (j,cell) in row.iter_mut().enumerate() {
            *cell=RANK_STRENGTH*DEN*u[i]*u[j];
        }
        let w=i128::from(m.weights[i]);
        row[i]+=norm*w*(DEN*i128::from(jb)*i128::from(m.magnetic[i])-tnum);
        for &(j,entry) in &m.electric[i] {
            row[j]+=bulk*w*i128::from(je)*i128::from(entry);
        }
    }
    // Subtract a strictly positive exact rational fudge = 1/DEN.
    // Since the matrix uses denominator DEN*norm, its integer fudge is norm.
    Ok((a,norm))
}
fn improved_excited_upper(m:&Torus2,v:&[i128],je:i64,jb:i64,threshold:i128)
    ->Result<i128,String>
{
    // The x/y Wilson-character difference transforms in an antisymmetric
    // reflection sector, whereas v is reflection-symmetric. Applying the
    // same symmetric H and an odd integer rounding rule preserves that
    // sector. Confirm both inner products exactly before min-max.
    let mut z:Vec<i128>=v.iter().zip(&m.representatives)
        .map(|(&x,q)| x*i128::from(character(q[0])-character(q[2])))
        .collect();
    let max_start=z.iter().map(|x|x.abs()).max().ok_or("missing excited trial")?;
    if max_start==0 {return Err("zero excited trial".into());}
    for x in &mut z {*x=div_round(*x*EXCITED_SCALE,max_start);}
    // Gershgorin upper bound on lambda_max(H). The shift is strictly
    // above the full spectrum, so positive-spectrum contamination cannot
    // dominate the repeated (shift*I-H) iteration.
    let shift:i128=m.electric.iter().enumerate().map(|(i,row)|{
        let diag=row.iter().find(|(j,_)|*j==i).map(|(_,x)|*x).unwrap_or(0);
        2*i128::from(je)*i128::from(diag)+i128::from(jb)*i128::from(m.magnetic[i])
    }).max().unwrap_or(0)+1;
    for _ in 0..EXCITED_ITERATIONS {
        let hz=m.apply(je,jb,&z)?;
        let next:Vec<i128>=z.iter().zip(&hz).map(|(&x,&h)|shift*x-h).collect();
        let magnitude=next.iter().map(|x|x.abs()).max().ok_or("missing excited step")?;
        if magnitude==0 {return Err("zero excited step".into());}
        z=next.iter().map(|&x|div_round(x*EXCITED_SCALE,magnitude)).collect();
    }
    let hz=m.apply(je,jb,&z)?;
    let hv=m.apply(je,jb,v)?;
    if dot_w(v,&z,&m.weights)?!=0 || dot_w(v,&hz,&m.weights)?!=0 ||
        dot_w(&z,&hv,&m.weights)?!=0 {
        return Err("excited Wilson trial lost exact H-orthogonality".into());
    }
    let vv=dot_w(v,v,&m.weights)?;
    let vhv=dot_w(v,&hv,&m.weights)?;
    let zz=dot_w(&z,&z,&m.weights)?;
    let zhz=dot_w(&z,&hz,&m.weights)?;
    if vv<=0||zz<=0||zhz<=0||vhv*DEN>=threshold*vv {
        return Err("two-vector Ritz ordering not certified".into());
    }
    Ok(ceil_div(zhz*OUT_DEN,zz))
}
pub fn certify(je:i64,jb:i64)->Result<ResultBounds,String> {
    let threshold=match (je,jb) {(1,1)=>13_240,(3,5)=>50_840,
        _=>return Err("supported inertia couplings: (1,1),(3,5)".into())};
    let earlier=crate::torus2_bounds::enclose(je,jb)?;
    // This confirms a ground eigenvalue strictly below the chosen threshold.
    if earlier.e0_upper*DEN>=threshold*OUT_DEN {
        return Err("ground-state enclosure not below proposed threshold".into());
    }
    let m=Torus2::build()?;
    let v=positive_ground_witness(&m,je,jb)?;
    let (a,norm)=positive_rank_matrix(&m,&v,je,jb,threshold)?;
    let (min_pivot,min_margin)=integer_cholesky_pd(&a,norm)?;
    // Rank-one PSD modification of symmetric W(H-tI) removes at most one
    // nonpositive eigenvalue. A positive definite modified matrix proves
    // the second eigenvalue of H is STRICTLY above t.
    let e1_lower=threshold*(OUT_DEN/DEN);
    let e1_upper=improved_excited_upper(&m,&v,je,jb,threshold)?;
    if e1_upper<=e1_lower {
        return Err("Rayleigh upper below certified inertia threshold".into());
    }
    let gap_lower=e1_lower-earlier.e0_upper;
    let gap_upper=e1_upper-earlier.e0_lower;
    let mut bytes=Vec::new();
    bytes.extend_from_slice(&je.to_le_bytes());
    bytes.extend_from_slice(&jb.to_le_bytes());
    bytes.extend_from_slice(&threshold.to_le_bytes());
    for item in &v {bytes.extend_from_slice(&item.to_le_bytes());}
    Ok(ResultBounds{
        je,jb,threshold,e0_lower:earlier.e0_lower,e0_upper:earlier.e0_upper,
        e1_lower,e1_upper,gap_lower,gap_upper,
        min_cholesky_pivot:min_pivot,residual_margin:min_margin,
        witness_sha:hex(&sha256(&bytes)),
    })
}
pub struct Certificate {
    pub hbp:Vec<u8>,pub hbi:Vec<u8>,pub anchor:String,pub measure:String
}
pub fn certificate(je:i64,jb:i64)->Result<Certificate,String>{
    let b=certify(je,jb)?;
    let body=format!(
        "HBP|schema=hebc.s3.torus2.inertia.v1|JE={je}|JB={jb}|physical_dim={DIM}|threshold_num={}|threshold_den={DEN}|E0=[{},{}]/{OUT_DEN}|E1=[{},{}]/{OUT_DEN}|gap=[{},{}]/{OUT_DEN}|rank_strength={RANK_STRENGTH}|factor_scale={FACTOR_SCALE}|witness_iters={ITERATIONS}|excited_iters={EXCITED_ITERATIONS}|cholesky_min_pivot={}|strict_residual_margin={}|witness_sha={}|method=EXACT_INTEGER_RANKONE_PD_AND_RITZ|continuum_proven=0|prev={}",
        b.threshold,b.e0_lower,b.e0_upper,b.e1_lower,b.e1_upper,b.gap_lower,
        b.gap_upper,b.min_cholesky_pivot,b.residual_margin,b.witness_sha,hex(&[0u8;32])
    );
    let rec=sha256(body.as_bytes());
    let chain=sha256(&[[0u8;32].as_slice(),rec.as_slice()].concat());
    let hbp=format!("{body}|record_sha={}|chain={}|json=0\n",hex(&rec),hex(&chain)).into_bytes();
    let hbi=format!("HBI|schema=hebc.s3.torus2.inertia.v1|record=1|offset=0|len={}|row_sha={}|chain={}|json=0\n",
        hbp.len(),hex(&sha256(&hbp)),hex(&chain)).into_bytes();
    let anchor=format!("ANCHOR|schema=hebc.s3.torus2.inertia.v1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(&hbp)),hex(&sha256(&hbi)),hex(&chain));
    let measure=format!(
        "TORUS2INERTIA|result=PASS|JE={je}|JB={jb}|E0=[{},{}]/{OUT_DEN}|E1=[{},{}]/{OUT_DEN}|gap=[{},{}]/{OUT_DEN}|strict_E1_threshold={}/{DEN}|integer_cholesky=PASS|margin={}|json=0\n",
        b.e0_lower,b.e0_upper,b.e1_lower,b.e1_upper,b.gap_lower,b.gap_upper,
        b.threshold,b.residual_margin);
    Ok(Certificate{hbp,hbi,anchor,measure})
}
pub fn save(dir:&Path,c:&Certificate)->Result<(),String>{
    std::fs::create_dir_all(dir).map_err(|e|e.to_string())?;
    for (name,bytes) in [
        ("run.hbp",c.hbp.as_slice()),("index.hbi",c.hbi.as_slice()),
        ("run.anchor",c.anchor.as_bytes()),("run.measure",c.measure.as_bytes())
    ] {std::fs::write(dir.join(name),bytes).map_err(|e|e.to_string())?;}
    Ok(())
}
pub fn verify_dir(dir:&Path,je:i64,jb:i64)->Result<(),String>{
    let expected=certificate(je,jb)?;
    for (name,bytes) in [
        ("run.hbp",expected.hbp.as_slice()),("index.hbi",expected.hbi.as_slice()),
        ("run.anchor",expected.anchor.as_bytes()),("run.measure",expected.measure.as_bytes())
    ] {
        if std::fs::read(dir.join(name)).map_err(|e|e.to_string())?!=bytes {
            return Err(format!("inertia replay mismatch: {name}"));
        }
    }
    Ok(())
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]
    fn integer_root_and_signed_rounding(){
        for n in 0..100_000u128{
            let s=sqrt_floor(n);
            assert!(s*s<=n && (s+1)*(s+1)>n);
        }
        assert_eq!(div_round(-8,3),-3);
        assert_eq!(div_round(8,3),3);
        assert_eq!(div_round(-5,2),-2);
    }
    #[test]
    fn strict_positive_definiteness_controls(){
        assert!(integer_cholesky_pd(&[vec![8,2],vec![2,5]],1).is_ok());
        assert!(integer_cholesky_pd(&[vec![0,1],vec![1,0]],1).is_err());
        assert!(integer_cholesky_pd(&[vec![4,1],vec![0,4]],1).is_err());
    }
}
