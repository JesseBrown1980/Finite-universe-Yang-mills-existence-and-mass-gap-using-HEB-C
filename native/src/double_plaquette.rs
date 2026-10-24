//! Exact interacting two-plaquette S3 gauge Hamiltonian on seven shared links.
//! Fully Gauss-projected from 6^7 configurations to 11 invariant orbit states.
//! Uses only safe Rust 1.81 integer arithmetic and exact rational half-integer
//! spectral enclosures. This is FINITE S3, not a continuum Yang-Mills proof.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]
use crate::{character, inv, mul};

pub const RAW: usize = 279_936;
pub const DIM: usize = 11;
const EDGES: [(usize,usize);7] = [
    (0,1), (1,2), (3,2), (0,3), (1,4), (4,5), (2,5),
];
const TRANS: [u8;3] = [1,2,5]; // the three conjugate transpositions of S3
const COUPLING_LIMIT: i64 = 10;

fn decode(mut id:usize)->[u8;7] {
    let mut s=[0;7];
    for v in &mut s { *v=(id%6) as u8; id/=6; }
    s
}
#[cfg(test)]
fn encode(s:[u8;7])->usize {
    let mut id=0;
    let mut scale=1;
    for v in s {id+=usize::from(v)*scale; scale*=6;}
    id
}
/// Orientation:
/// left: 0->1->2->3->0, right: 1->4->5->2->1.
/// Shared edge 1->2 is traversed in opposite directions.
/// Right holonomy is transported from base 1 to base 0 using edge 0.
pub fn plaquettes(s:&[u8;7])->(u8,u8) {
    let left=mul(mul(mul(s[0],s[1]),inv(s[2])),inv(s[3]));
    let right=mul(mul(mul(s[4],s[5]),inv(s[6])),inv(s[1]));
    let transported=mul(mul(s[0],right),inv(s[0]));
    (left,transported)
}
fn conjugate(g:u8,v:u8)->u8 {mul(mul(g,v),inv(g))}
/// Canonical simultaneous-conjugation class of the two based holonomies.
/// Gauge fixing a connected spanning tree leaves precisely this residual action.
pub fn orbit_key(s:&[u8;7])->u8 {
    let (a,b)=plaquettes(s);
    (0..6u8).map(|g|6*conjugate(g,a)+conjugate(g,b))
        .min().expect("six group elements")
}
pub fn gauge_transform(mut state:[u8;7],vertex:usize,g:u8)->[u8;7] {
    assert!(vertex<6 && g<6);
    for (i,&(tail,head)) in EDGES.iter().enumerate(){
        if tail==vertex {state[i]=mul(g,state[i]);}
        if head==vertex {state[i]=mul(state[i],inv(g));}
    }
    state
}
fn potential(s:&[u8;7])->i64 {
    let (a,b)=plaquettes(s);
    4-character(a)-character(b)
}
#[derive(Debug,Clone)]
pub struct DoublePlaquette {
    pub keys:[u8;DIM],
    pub weights:[u64;DIM],
    pub representatives:[[u8;7];DIM],
    /// Electric operator in the orbit-*value* basis. Matrix need not look
    /// symmetric; the physical inner product uses positive orbit weights.
    pub electric:[[i64;DIM];DIM],
    /// Diagonal magnetic Wilson-character potential for both plaquettes.
    pub magnetic:[i64;DIM],
}
impl DoublePlaquette {
    pub fn build()->Result<Self,String> {
        let mut weights_by_key=[0u64;36];
        let mut rep_by_key=[[0u8;7];36];
        let mut seen=[false;36];
        for id in 0..RAW {
            let s=decode(id);
            let key=usize::from(orbit_key(&s));
            weights_by_key[key]+=1;
            if !seen[key] {
                rep_by_key[key]=s;
                seen[key]=true;
            }
        }
        let classes:Vec<usize>=(0..36).filter(|&k|seen[k]).collect();
        if classes.len()!=DIM {return Err("Gauss orbit dimension mismatch".into());}
        let mut keys=[0u8;DIM];
        let mut weights=[0u64;DIM];
        let mut representatives=[[0u8;7];DIM];
        let mut lookup=[usize::MAX;36];
        for (i,&key) in classes.iter().enumerate(){
            keys[i]=key as u8;
            weights[i]=weights_by_key[key];
            representatives[i]=rep_by_key[key];
            lookup[key]=i;
        }
        let mut electric=[[0i64;DIM];DIM];
        let mut magnetic=[0i64;DIM];
        for i in 0..DIM {
            let s=representatives[i];
            magnetic[i]=potential(&s);
            electric[i][i]=21;
            for edge in 0..7 {
                for &t in &TRANS {
                    let mut next=s;
                    next[edge]=mul(t,next[edge]);
                    let j=lookup[usize::from(orbit_key(&next))];
                    if j>=DIM {return Err("electric operator escaped physical sector".into());}
                    electric[i][j]-=1;
                }
            }
        }
        let model=Self{keys,weights,representatives,electric,magnetic};
        model.validate()?;
        Ok(model)
    }
    pub fn validate(&self)->Result<(),String> {
        if self.weights.iter().sum::<u64>() != RAW as u64 {return Err("orbit size total".into());}
        for i in 0..DIM {
            if self.weights[i]==0 || !(0..=6).contains(&self.magnetic[i]) {
                return Err("orbit weight/potential invalid".into());
            }
            if self.electric[i].iter().sum::<i64>()!=0 {
                return Err("electric row is not a Laplacian".into());
            }
            for j in 0..DIM {
                if i!=j && self.electric[i][j]>0 {return Err("positive offdiagonal".into());}
                let lhs=i128::from(self.weights[i])*i128::from(self.electric[i][j]);
                let rhs=i128::from(self.weights[j])*i128::from(self.electric[j][i]);
                if lhs!=rhs {return Err("weighted Hermiticity failed".into());}
            }
            for v in 0..6 {
                for &t in &TRANS {
                    let transformed=gauge_transform(self.representatives[i],v,t);
                    if orbit_key(&transformed)!=self.keys[i] ||
                       potential(&transformed)!=self.magnetic[i] {
                        return Err("Gauss transformation changes observable".into());
                    }
                }
            }
        }
        Ok(())
    }
    pub fn matrix(&self,je:i64,jb:i64)->Result<[[i64;DIM];DIM],String>{
        if !(0..=COUPLING_LIMIT).contains(&je) ||
           !(0..=COUPLING_LIMIT).contains(&jb) {
            return Err("integer spectrum couplings must be 0..10".into());
        }
        let mut h=[[0;DIM];DIM];
        for (i,row) in h.iter_mut().enumerate() {
            for (j,cell) in row.iter_mut().enumerate() {
                *cell=je*self.electric[i][j]+
                    if i==j {jb*self.magnetic[i]} else {0};
            }
        }
        Ok(h)
    }
}

fn mul_matrix(a:&[[i128;DIM];DIM],b:&[[i128;DIM];DIM],n:usize)
    ->Result<[[i128;DIM];DIM],String>{
    let mut out=[[0i128;DIM];DIM];
    for (i,row) in out.iter_mut().enumerate().take(n) {
        for (k,brow) in b.iter().enumerate().take(n) {
            for (j,cell) in row.iter_mut().enumerate().take(n) {
                let p=a[i][k].checked_mul(brow[j]).ok_or("matrix product overflow")?;
                *cell=cell.checked_add(p).ok_or("matrix sum overflow")?;
            }
        }
    }
    Ok(out)
}
/// Faddeev-LeVerrier: exact integer characteristic coefficients
/// det(lambda*I-H_n) for each leading principal minor of size n.
fn char_coefficients(h:&[[i64;DIM];DIM],n:usize)->Result<Vec<i128>,String>{
    let mut a=[[0i128;DIM];DIM];
    let mut b=[[0i128;DIM];DIM];
    for i in 0..n {
        b[i][i]=1;
        for j in 0..n {a[i][j]=i128::from(h[i][j]);}
    }
    let mut coefficients=vec![1i128];
    for k in 1..=n {
        let mut prod=mul_matrix(&a,&b,n)?;
        let mut trace=0i128;
        for (i,row) in prod.iter().enumerate().take(n) {
            trace=trace.checked_add(row[i]).ok_or("trace overflow")?;
        }
        let count=k as i128;
        if trace%count!=0 {return Err("nonintegral characteristic coefficient".into());}
        let c=-trace/count;
        coefficients.push(c);
        for (i,row) in prod.iter_mut().enumerate().take(n) {
            row[i]=row[i].checked_add(c).ok_or("characteristic overflow")?;
        }
        b=prod;
    }
    Ok(coefficients)
}
/// Sign of det(H_n - xI) with x=odd/2. No leading principal
/// determinant can vanish: a rational eigenvalue of an integer matrix
/// is an algebraic integer, hence an *integer*, never a half-integer.
/// This makes the principal-minor Sturm inertia test fail-closed.
fn principal_sign(poly:&[i128],odd:i128)->Result<i8,String> {
    let mut value=1i128;
    let mut factor=1i128;
    for &c in &poly[1..] {
        factor=factor.checked_mul(2).ok_or("denominator overflow")?;
        value=value.checked_mul(odd)
            .and_then(|v|c.checked_mul(factor).and_then(|p|v.checked_add(p)))
            .ok_or("rational polynomial evaluation overflow")?;
    }
    if poly.len()%2==0 {value = -value;}
    if value==0 {return Err("unexpected rational root at half-integer".into());}
    Ok(if value<0 {-1}else{1})
}
fn inertia_at(polys:&[Vec<i128>],k:i128)->Result<usize,String> {
    let x=2*k+1; // x/2 is k+1/2
    let mut last=1i8;
    let mut changes=0;
    for poly in polys {
        let sign=principal_sign(poly,x)?;
        if sign!=last {changes+=1;}
        last=sign;
    }
    Ok(changes)
}
#[derive(Debug,Clone,Copy,PartialEq,Eq)]
pub struct GapInterval {
    /// Half-integer endpoints expressed as odd integers / 2.
    pub ground:[i128;2],
    pub first:[i128;2],
    pub gap:[i128;2],
    pub denom:i128,
    pub positive:bool,
}
pub fn certify_gap(model:&DoublePlaquette,je:i64,jb:i64)->Result<GapInterval,String>{
    let h=model.matrix(je,jb)?;
    let mut polys=Vec::with_capacity(DIM);
    for n in 1..=DIM {polys.push(char_coefficients(&h,n)?);}
    // Gershgorin: every eigenvalue lies in [-R,R]. JE,JB <= 10,
    // and the row absolute sum is bounded by 42*JE + 6*JB.
    let radius=i128::from(42*je+6*jb+2);
    let find = |index:usize| -> Result<[i128;2],String>{
        let mut lo=-radius-1;
        let mut hi=radius+1;
        if inertia_at(&polys,lo)? > index || inertia_at(&polys,hi)? <= index {
            return Err("Sturm spectral search not bracketed".into());
        }
        while hi-lo>1 {
            let mid=lo+(hi-lo)/2;
            if inertia_at(&polys,mid)? > index {hi=mid;}
            else {lo=mid;}
        }
        // Eigenvalue belongs to (lo+1/2, hi+1/2) with hi=lo+1.
        Ok([2*lo+1,2*hi+1])
    };
    let ground=find(0)?;
    let first=find(1)?;
    let gap=[first[0]-ground[1],first[1]-ground[0]];
    Ok(GapInterval {ground,first,gap,denom:2,positive:gap[0]>0})
}


/// This is a *static spectral calculation*, not a fictitious 243-tick evolution.
/// The one-record HBP/HBI receipt contains the complete matrix-derived
/// certificate, and verification recomputes the original orbit projection.
#[derive(Debug,Clone)]
pub struct Certificate {
    pub hbp:Vec<u8>,
    pub hbi:Vec<u8>,
    pub anchor:String,
    pub report:String,
}
pub fn certificate(je:i64,jb:i64)->Result<Certificate,String>{
    use crate::{hex,sha256};
    let model=DoublePlaquette::build()?;
    let mat=model.matrix(je,jb)?;
    let gap=certify_gap(&model,je,jb)?;
    let mut bytes=Vec::new();
    bytes.extend_from_slice(b"HEBC-S3-DOUBLE7-11D-V1");
    for (&key,&weight) in model.keys.iter().zip(&model.weights) {
        bytes.push(key);
        bytes.extend_from_slice(&weight.to_le_bytes());
    }
    for (i,row) in mat.iter().enumerate() {
        for val in row {bytes.extend_from_slice(&val.to_le_bytes());}
        bytes.extend_from_slice(&model.magnetic[i].to_le_bytes());
    }
    let source_sha=hex(&sha256(&bytes));
    let sh=&source_sha[..16];
    let genesis=[0u8;32];
    let body=format!(
        "HBP|schema=HEBC-S3-DOUBLE7-11D-V1|kind=interacting_static_spectrum|vertices=6|links=7|physical_dim=11|raw_states=279936|JE={je}|JB={jb}|matrix_sha={source_sha}|sh={sh}|denom={}|E0_low={}|E0_high={}|E1_low={}|E1_high={}|gap_low={}|gap_high={}|positive={}|prev={}",
        gap.denom,gap.ground[0],gap.ground[1],gap.first[0],gap.first[1],
        gap.gap[0],gap.gap[1],u8::from(gap.positive),hex(&genesis)
    );
    let rec=sha256(body.as_bytes());
    let mut link=Vec::with_capacity(64);
    link.extend_from_slice(&genesis);
    link.extend_from_slice(&rec);
    let chain=sha256(&link);
    let row=format!("{body}|record_sha={}|chain={}|json=0\n",hex(&rec),hex(&chain));
    let index=format!(
        "HBI|schema=HEBC-S3-DOUBLE7-11D-V1|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        row.len(),hex(&sha256(row.as_bytes())),hex(&chain)
    );
    let anchor=format!(
        "ANCHOR|schema=HEBC-S3-DOUBLE7-11D-V1|records=1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
        hex(&sha256(row.as_bytes())),hex(&sha256(index.as_bytes())),hex(&chain)
    );
    let report=format!(
        "DOUBLE_GAP|model=S3_two_plaquette|vertices=6|links=7|raw_states=279936|gauss_dim=11|JE={je}|JB={jb}|E0=[{},{}]/2|E1=[{},{}]/2|gap=[{},{}]/2|positive={}|matrix_sha={source_sha}|json=0\n",
        gap.ground[0],gap.ground[1],gap.first[0],gap.first[1],
        gap.gap[0],gap.gap[1],u8::from(gap.positive)
    );
    Ok(Certificate{hbp:row.into_bytes(),hbi:index.into_bytes(),anchor,report})
}
fn read_field<'a>(text:&'a str,key:&str)->Result<&'a str,String>{
    let mut found=None;
    for item in text.trim_end_matches('\n').split('|').skip(1){
        let (k,v)=item.split_once('=').ok_or("broken field")?;
        if k==key && found.replace(v).is_some(){return Err("duplicate field".into());}
    }
    found.ok_or_else(||format!("missing {key}"))
}
pub fn verify_certificate(hbp:&[u8],hbi:&[u8],anchor:&str)->Result<(),String>{
    let row=std::str::from_utf8(hbp).map_err(|_|"HBP utf8")?;
    let je=read_field(row,"JE")?.parse::<i64>().map_err(|_|"JE integer")?;
    let jb=read_field(row,"JB")?.parse::<i64>().map_err(|_|"JB integer")?;
    let fresh=certificate(je,jb)?;
    if fresh.hbp!=hbp || fresh.hbi!=hbi || fresh.anchor!=anchor {
        return Err("exact matrix reconstruction / HBI / HBP / HASH mismatch".into());
    }
    Ok(())
}
pub fn save_certificate(dir:&std::path::Path,certificate:&Certificate)->Result<(),String>{
    std::fs::create_dir_all(dir).map_err(|e|e.to_string())?;
    std::fs::write(dir.join("run.hbp"),&certificate.hbp).map_err(|e|e.to_string())?;
    std::fs::write(dir.join("index.hbi"),&certificate.hbi).map_err(|e|e.to_string())?;
    std::fs::write(dir.join("run.anchor"),&certificate.anchor).map_err(|e|e.to_string())?;
    std::fs::write(dir.join("run.measure"),&certificate.report).map_err(|e|e.to_string())?;
    Ok(())
}
pub fn verify_certificate_dir(dir:&std::path::Path)->Result<(),String>{
    let hbp=std::fs::read(dir.join("run.hbp")).map_err(|e|e.to_string())?;
    let hbi=std::fs::read(dir.join("index.hbi")).map_err(|e|e.to_string())?;
    let anchor=std::fs::read_to_string(dir.join("run.anchor")).map_err(|e|e.to_string())?;
    verify_certificate(&hbp,&hbi,&anchor)
}

#[cfg(test)]
mod tests {
    use super::*;


    /// Independent Leibniz determinant calculation via a subset DP. This
    /// does NOT call the Faddeev-LeVerrier characteristic polynomial or its
    /// Sturm recurrence; every signed permutation is counted exactly.
    fn direct_integer_determinant(h:&[[i64;DIM];DIM],n:usize,odd:i128)->i128 {
        let mut dp=vec![0i128;1usize<<n];
        dp[0]=1;
        for mask in 0..(1usize<<n) {
            let row=mask.count_ones() as usize;
            if row==n {continue;}
            for col in 0..n {
                if mask & (1<<col)!=0 {continue;}
                let value=2*i128::from(h[row][col]) -
                    if row==col {odd} else {0};
                let greater=(mask>>(col+1)).count_ones();
                let signed=if greater%2==0 {value} else {-value};
                let added=dp[mask].checked_mul(signed)
                    .expect("small exact test determinant product fits i128");
                let next=mask|(1<<col);
                dp[next]=dp[next].checked_add(added)
                    .expect("small exact test determinant accumulation fits i128");
            }
        }
        dp[(1<<n)-1]
    }
    #[test]
    fn negative_controls_reject_false_hermiticity_and_forged_gauge_observable(){
        let mut corrupted=DoublePlaquette::build().unwrap();
        corrupted.electric[0][1]+=1;
        assert!(corrupted.validate().is_err(),
            "non-self-adjoint physical matrix must fail");
        let mut forged=DoublePlaquette::build().unwrap();
        forged.magnetic[1]=9;
        assert!(forged.validate().is_err(),
            "a gauge observable incompatible with plaquette holonomy must fail");
    }

    #[test]
    fn independent_leibniz_determinants_certify_all_low_energy_brackets(){
        let m=DoublePlaquette::build().unwrap();
        for (je,jb) in [(0,0),(1,0),(0,1),(1,1),(3,5)] {
            let h=m.matrix(je,jb).unwrap();
            let e=certify_gap(&m,je,jb).unwrap();
            for &odd in &[
                e.ground[0],e.ground[1],e.first[0],e.first[1]
            ]{
                let mut direct_signs=Vec::with_capacity(DIM);
                for n in 1..=DIM {
                    let exact=direct_integer_determinant(&h,n,odd);
                    assert_ne!(exact,0,"half-integer is not a rational eigenvalue");
                    let coefficients=char_coefficients(&h,n).unwrap();
                    assert_eq!(
                        if exact<0 {-1} else {1},
                        principal_sign(&coefficients,odd).unwrap(),
                        "independent determinant disagrees JE={je} JB={jb} n={n} x={odd}/2"
                    );
                    direct_signs.push(if exact<0 {-1i8}else{1i8});
                }
                let mut previous=1i8;
                let mut negatives=0;
                for sign in direct_signs {
                    if sign!=previous {negatives+=1;}
                    previous=sign;
                }
                assert_eq!(negatives,inertia_at(
                    &(1..=DIM).map(|n|char_coefficients(&h,n).unwrap()).collect::<Vec<_>>(),
                    (odd-1)/2
                ).unwrap(),"Leibniz vs Sturm inertia");
            }
        }
    }

    #[test]
    fn double_spectrum_certificate_integrity_and_full_reexecution(){
        let r=certificate(1,1).unwrap();
        verify_certificate(&r.hbp,&r.hbi,&r.anchor).unwrap();
        let mut tampered=r.hbp.clone();
        let first=tampered.iter().position(|v|*v==b'E').unwrap();
        tampered[first]=b'X';
        assert!(verify_certificate(&tampered,&r.hbi,&r.anchor).is_err());
        let r0=certificate(0,0).unwrap();
        assert!(r0.report.contains("|positive=0|"));
    }
    #[test]
    fn full_gauss_projection_and_integer_hermiticity(){
        let m=DoublePlaquette::build().unwrap();
        assert_eq!(m.keys,[0,1,3,6,7,8,9,18,19,21,22]);
        assert_eq!(m.weights,[7776,23328,15552,23328,23328,46656,46656,15552,46656,15552,15552]);
        assert_eq!(m.magnetic,[0,2,3,2,4,4,5,3,5,6,6]);
        assert_eq!(m.electric[0],[21,-9,0,-9,-3,0,0,0,0,0,0]);
        assert_eq!(m.electric[1],[-3,21,-6,-1,-3,-6,-2,0,0,0,0]);
        for i in 0..DIM {
            for vertex in 0..6{
                for g in 0..6{
                    let s=gauge_transform(m.representatives[i],vertex,g);
                    assert_eq!(orbit_key(&s),m.keys[i]);
                    assert_eq!(potential(&s),m.magnetic[i]);
                }
            }
        }
    }
    #[test]
    fn independent_exhaustive_gauge_orbits_from_vertex_moves(){
        let m=DoublePlaquette::build().unwrap();
        let mut seen=vec![false;RAW];
        for class in 0..DIM {
            let root=encode(m.representatives[class]);
            assert!(!seen[root]);
            seen[root]=true;
            let mut todo=vec![root];
            let mut count=0;
            while let Some(id)=todo.pop(){
                count+=1;
                let s=decode(id);
                assert_eq!(orbit_key(&s),m.keys[class]);
                for v in 0..6{
                    for &g in &TRANS{
                        let next=encode(gauge_transform(s,v,g));
                        if !seen[next] {seen[next]=true;todo.push(next);}
                    }
                }
            }
            assert_eq!(count as u64,m.weights[class],"independent Gauss orbit size");
        }
        assert!(seen.iter().all(|v|*v));
    }
    #[test]
    fn exact_weighted_electric_self_adjointness_and_raw_control(){
        let m=DoublePlaquette::build().unwrap();
        m.validate().unwrap();
        for je in 0..=5{
            for jb in 0..=5{
                let h=m.matrix(je,jb).unwrap();
                for i in 0..DIM {
                    for j in 0..DIM {
                        assert_eq!(
                            i128::from(m.weights[i])*i128::from(h[i][j]),
                            i128::from(m.weights[j])*i128::from(h[j][i])
                        );
                    }
                }
            }
        }
        assert!(m.matrix(-1,1).is_err());
        assert!(m.matrix(1,-1).is_err());
        assert!(m.matrix(11,1).is_err());
        // The electric operator has a constant zero-energy vector.
        for row in &m.electric {assert_eq!(row.iter().sum::<i64>(),0);}
    }
    #[test]
    fn exact_integer_finite_interacting_two_plaquette_gap(){
        let m=DoublePlaquette::build().unwrap();
        for (je,jb) in [(0,0),(1,0),(0,1),(1,1),(3,5)]{
            let e=certify_gap(&m,je,jb).unwrap();
            assert_eq!(e.denom,2);
            if je==0 && jb==0 {assert!(!e.positive);}
            else {assert!(e.positive,"JE={je} JB={jb} gap={:?}",e.gap);}
            assert!(e.ground[0]<e.ground[1]);
            assert!(e.first[0]<=e.first[1]);
        }
        let only_e=certify_gap(&m,1,0).unwrap();
        assert!(only_e.ground[0]<0 && only_e.ground[1]>0);
        assert!(only_e.first[0]<24 && only_e.first[1]>24); // E1=12 => numerator 24
        let only_b=certify_gap(&m,0,1).unwrap();
        assert!(only_b.first[0]<4 && only_b.first[1]>4); // E1=2
    }
}
