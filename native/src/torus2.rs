//! Stage 2C: actual eight-link, four-face periodic 2x2 S3 torus.
//! 6^8 raw link configurations -> 6^5 tree-gauge configurations ->
//! 1,393 simultaneous-conjugation orbits. Safe integer-only Rust 1.81.
//! Exact electric-only gap and Perron-Frobenius simplicity are mathematical
//! spectral statements; NO uncertified mixed-coupling energy intervals.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]
use crate::{character, inv, mul};
use std::collections::{BTreeMap, VecDeque};

pub const DIM: usize = 1_393;
pub const TREE_STATE_COUNT: usize = 7_776;
pub const RAW_STATE_COUNT: usize = 1_679_616;
pub const GAUGE_TREE_MULTIPLICITY: usize = 216;
const TREE: [usize;3] = [0,1,4];
const FREE: [usize;5] = [2,3,5,6,7];
const TRANS: [u8;3] = [1,2,5];
const EDGES: [(usize,usize);8] = [
    (0,2), (1,3), (2,0), (3,1),
    (0,1), (1,0), (2,3), (3,2),
];

fn encode(values:[u8;5])->usize {
    let mut id=0;
    let mut power=1;
    for q in values {id+=usize::from(q)*power;power*=6;}
    id
}
fn decode(mut id:usize)->[u8;5] {
    let mut q=[0;5];
    for cell in &mut q {*cell=(id%6) as u8;id/=6;}
    q
}
fn conjugate(g:u8,x:u8)->u8 {mul(mul(g,x),inv(g))}
pub fn canonical(q:[u8;5])->usize {
    (0..6u8).map(|g|encode(q.map(|x|conjugate(g,x))))
        .min().expect("S3 has identity")
}
fn representative(q:[u8;5])->[u8;8] {
    let mut links=[0u8;8];
    for (i,&edge) in FREE.iter().enumerate(){links[edge]=q[i];}
    links
}
pub fn gauge_transform(mut links:[u8;8],site:usize,g:u8)->[u8;8] {
    assert!(site<4&&g<6);
    for (edge,&(tail,head)) in EDGES.iter().enumerate(){
        if tail==site {links[edge]=mul(g,links[edge]);}
        if head==site {links[edge]=mul(links[edge],inv(g));}
    }
    links
}
/// Gauge-fix the three actual spanning-tree links to identity, preserving
/// the five free loops. Residual root gauge action is global conjugation.
pub fn gauge_fix(links:[u8;8])->[u8;5] {
    let mut h=[0u8;4];
    h[2]=links[0]; // tree edge 0 -> 2
    h[1]=links[4]; // tree edge 0 -> 1
    h[3]=mul(h[1],links[1]); // tree edge 1 -> 3
    let mut q=[0;5];
    for (i,&edge) in FREE.iter().enumerate(){
        let (tail,head)=EDGES[edge];
        q[i]=mul(mul(h[tail],links[edge]),inv(h[head]));
    }
    q
}
fn index(x:usize,y:usize)->usize {(x%2)*2+(y%2)}
fn plaquette(s:&[u8;8],x:usize,y:usize)->u8{
    let a=index(x,y);
    let right=index(x+1,y);
    let up=index(x,y+1);
    // Periodic link variables: x[a],y[right],x[up]^-1,y[a]^-1
    mul(mul(mul(s[a],s[4+right]),inv(s[up])),inv(s[4+a]))
}
pub fn magnetic_potential(s:&[u8;8])->i64 {
    let mut action=0i64;
    for x in 0..2{
        for y in 0..2{action+=2-character(plaquette(s,x,y));}
    }
    action
}
fn wilson_x(s:&[u8;8])->u8 {mul(s[0],s[2])}
fn wilson_y(s:&[u8;8])->u8 {mul(s[4],s[5])}
#[derive(Clone,Debug)]
pub struct Torus2 {
    pub keys:Vec<usize>,
    pub weights:Vec<u64>,
    /// Tree-gauge-fixed representative in each physical Gauss orbit.
    pub representatives:Vec<[u8;5]>,
    /// Exactly 24 raw electric link generators summed and projected.
    /// Indexed sparse, nonpositive off diagonal, zero row sums.
    pub electric:Vec<Vec<(usize,i64)>>,
    pub magnetic:Vec<i64>,
}
impl Torus2 {
    pub fn build()->Result<Self,String>{
        let mut weights_by_key=vec![0u64;TREE_STATE_COUNT];
        for n in 0..TREE_STATE_COUNT{weights_by_key[canonical(decode(n))]+=1;}
        let keys:Vec<usize>=(0..TREE_STATE_COUNT).filter(|&i|weights_by_key[i]!=0).collect();
        if keys.len()!=DIM{return Err(format!("Gauss-reduced dimension {} != 1393",keys.len()));}
        let weights:Vec<u64>=keys.iter().map(|&k|weights_by_key[k]).collect();
        let representatives:Vec<[u8;5]>=keys.iter().map(|&k|decode(k)).collect();
        let mut index_by_key=vec![usize::MAX;TREE_STATE_COUNT];
        for (i,&k) in keys.iter().enumerate(){index_by_key[k]=i;}
        let mut electric=Vec::with_capacity(DIM);
        let mut magnetic=Vec::with_capacity(DIM);
        for q in &representatives {
            let raw=representative(*q);
            magnetic.push(magnetic_potential(&raw));
            let mut row=BTreeMap::<usize,i64>::new();
            *row.entry(index_by_key[canonical(*q)]).or_default()+=24;
            for edge in 0..8{
                for &t in &TRANS{
                    let mut next=raw;
                    next[edge]=mul(t,next[edge]);
                    let key=canonical(gauge_fix(next));
                    let j=index_by_key[key];
                    if j==usize::MAX{return Err("electric link escaped projected sector".into());}
                    *row.entry(j).or_default()-=1;
                }
            }
            electric.push(row.into_iter().filter(|(_,v)|*v!=0).collect());
        }
        let output=Self{keys,weights,representatives,electric,magnetic};
        output.validate()?;
        Ok(output)
    }
    pub fn validate(&self)->Result<(),String>{
        if self.keys.len()!=DIM || self.weights.len()!=DIM ||
           self.representatives.len()!=DIM ||
           self.electric.len()!=DIM || self.magnetic.len()!=DIM ||
           self.weights.iter().sum::<u64>()!=TREE_STATE_COUNT as u64 {
            return Err("incorrect Gauss orbit count".into());
        }
        if self.weights.iter().any(|&v|![1,2,3,6].contains(&v)) {
            return Err("invalid residual S3 conjugation orbit cardinality".into());
        }
        for (i,row) in self.electric.iter().enumerate() {
            if !(0..=12).contains(&self.magnetic[i]) ||
               row.iter().map(|(_,v)|*v).sum::<i64>()!=0 {
                return Err("magnetic bound / electric zero row sum".into());
            }
            for &(j,v) in row {
                if j>=DIM || (j!=i&&v>=0) {return Err("invalid sparse electric operator".into());}
                let back=self.electric[j].iter().find(|(k,_)|*k==i).map(|(_,v)|*v).unwrap_or(0);
                if i128::from(self.weights[i])*i128::from(v) !=
                   i128::from(self.weights[j])*i128::from(back) {
                    return Err("Gauss-weighted self-adjointness violated".into());
                }
            }
        }
        if !self.connected() {return Err("electric orbit graph is disconnected".into());}
        Ok(())
    }
    fn connected(&self)->bool{
        let mut seen=vec![false;DIM];
        let mut queue=VecDeque::new();
        queue.push_back(0usize);
        seen[0]=true;
        while let Some(i)=queue.pop_front(){
            for &(j,val) in &self.electric[i] {
                if i!=j&&val<0&&!seen[j]{seen[j]=true;queue.push_back(j);}
            }
        }
        seen.into_iter().all(|v|v)
    }
    pub fn nnz_electric(&self)->usize{self.electric.iter().map(Vec::len).sum()}
    pub fn flat_orbits(&self)->usize {self.magnetic.iter().filter(|&&v|v==0).count()}
    /// Exact integer action on arbitrary physical wavefunctions.
    pub fn apply(&self,je:i64,jb:i64,f:&[i128])->Result<Vec<i128>,String>{
        if je<0 || jb<0 || f.len()!=DIM{return Err("invalid coupling or vector".into());}
        let mut y=vec![0i128;DIM];
        for (i,row) in self.electric.iter().enumerate() {
            let mut e=0i128;
            for &(j,v) in row {
                let term=i128::from(v).checked_mul(f[j]).ok_or("electric multiplication overflow")?;
                e=e.checked_add(term).ok_or("electric addition overflow")?;
            }
            y[i]=i128::from(je).checked_mul(e)
                .and_then(|u|i128::from(jb).checked_mul(i128::from(self.magnetic[i]))
                    .and_then(|v|v.checked_mul(f[i]))
                    .and_then(|v|u.checked_add(v))))
                .ok_or("Hamiltonian application overflow")?;
        }
        Ok(y)
    }
    /// A noncontractible length-two Wilson loop in the standard representation
    /// is a physical eigenvector of the electric-only operator with E=6.
    /// Analytically the raw electric product spectrum is sums of {0,3,6};
    /// a gauge invariant excitation with only one excited link is impossible,
    /// because local gauge transformations act transitively on one link.
    /// Hence no physical E=3 state, giving the exact electric-only gap 6.
    pub fn electric_gap_witness(&self)->Result<(),String>{
        let f:Vec<i128>=self.representatives.iter()
            .map(|q|i128::from(character(wilson_x(&representative(*q)))))
            .collect();
        let mean:i128=f.iter().zip(&self.weights).map(|(f,w)|*f*i128::from(*w)).sum();
        if mean!=0{return Err("Wilson loop not orthogonal to ground state".into());}
        let ef=self.apply(1,0,&f)?;
        if !ef.iter().zip(&f).all(|(a,b)|*a==6*(*b)) {
            return Err("length-two Wilson loop is not an electric eigenmode".into());
        }
        Ok(())
    }
    pub fn verify_gauge_representatives(&self)->Result<(),String>{
        for (i,q) in self.representatives.iter().enumerate(){
            let s=representative(*q);
            if canonical(gauge_fix(s))!=self.keys[i] {return Err("canonical gauge fix".into());}
            for site in 0..4{
                for g in 0..6{
                    let transformed=gauge_transform(s,site,g);
                    if canonical(gauge_fix(transformed))!=self.keys[i] ||
                       magnetic_potential(&transformed)!=self.magnetic[i] {
                        return Err("local gauge transformation changes orbit or action".into());
                    }
                }
            }
        }
        Ok(())
    }
    /// Checks the exact flat-connection count and identifies noncontractible
    /// Wilson pairs for all magnetic-only zero-energy orbit states.
    pub fn flat_wilson_orbit_keys(&self)->Result<Vec<usize>,String>{
        let mut pairs=Vec::new();
        for (i,q) in self.representatives.iter().enumerate(){
            if self.magnetic[i]!=0 {continue;}
            let s=representative(*q);
            let px=wilson_x(&s);
            let py=wilson_y(&s);
            if mul(px,py)!=mul(py,px) {return Err("flat Wilson loops do not commute".into());}
            pairs.push(canonical_pair(px,py));
        }
        pairs.sort_unstable();
        pairs.dedup();
        if pairs.len()!=self.flat_orbits(){return Err("flat holonomy labels not unique".into());}
        Ok(pairs)
    }
}
fn canonical_pair(a:u8,b:u8)->usize{
    (0..6u8).map(|g|usize::from(conjugate(g,a))+6*usize::from(conjugate(g,b)))
        .min().expect("S3 identity")
}
/// Exact finite spectral diagnostics (no claimed mixed-coupling rational root
/// enclosure). When JE > 0 the connected, self-adjoint, stoquastic electric
/// graph implies by Perron-Frobenius a unique finite-volume ground state,
/// hence a strictly positive but UNQUANTIFIED excitation gap.
#[derive(Clone,Debug)]
pub struct Diagnostics {
    pub physical_states:usize,
    pub magnetic_flat_degeneracy:usize,
    pub electric_only_exact_gap:i64,
    pub nnz_electric:usize,
    pub connected:bool,
    pub qualitative_gap_positive:bool,
    pub quantitative_gap_certified:bool,
}
impl Torus2 {
    pub fn diagnostics(&self,je:i64,jb:i64)->Result<Diagnostics,String>{
        if !(0..=10).contains(&je)||!(0..=10).contains(&jb) {
            return Err("couplings must be integers 0..10".into());
        }
        self.electric_gap_witness()?;
        let flat=self.flat_wilson_orbit_keys()?.len();
        if flat!=8 {return Err("unexpected topological flat vacuum degeneracy".into());}
        let electric_only=6*je;
        let positive=je>0;
        Ok(Diagnostics {
            physical_states:DIM,
            magnetic_flat_degeneracy:flat,
            electric_only_exact_gap:electric_only,
            nnz_electric:self.nnz_electric(),
            connected:self.connected(),
            qualitative_gap_positive:positive,
            quantitative_gap_certified:jb==0,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn exact_torus_orbit_enumeration_independent_bfs() {
        let model=Torus2::build().unwrap();
        let mut visited=vec![false;TREE_STATE_COUNT];
        let mut sizes=Vec::new();
        for seed in 0..TREE_STATE_COUNT {
            if visited[seed]{continue;}
            visited[seed]=true;
            let mut queue=VecDeque::from([seed]);
            let mut size=0usize;
            while let Some(i)=queue.pop_front() {
                size+=1;
                let q=decode(i);
                for &t in &TRANS {
                    let next=encode(q.map(|g|conjugate(t,g)));
                    if !visited[next]{visited[next]=true;queue.push_back(next);}
                }
            }
            sizes.push(size);
        }
        sizes.sort_unstable();
        let mut weights:Vec<usize>=model.weights.iter().map(|&w|w as usize).collect();
        weights.sort_unstable();
        assert_eq!(sizes,weights);
        assert_eq!(sizes.len(),DIM);
        assert_eq!(sizes.iter().sum::<usize>()*GAUGE_TREE_MULTIPLICITY,RAW_STATE_COUNT);
        assert!(visited.into_iter().all(|x|x));
    }
    #[test]
    fn torus_four_plaquettes_are_periodic_and_gauge_invariant(){
        let m=Torus2::build().unwrap();
        m.verify_gauge_representatives().unwrap();
        for q in &m.representatives{
            let s=representative(*q);
            let sum:(i64,i64)=(
                (0..2).flat_map(|x|(0..2).map(move |y|2-character(plaquette(&s,x,y)))).sum(),
                magnetic_potential(&s),
            );
            assert_eq!(sum.0,sum.1);
        }
    }
    #[test]
    fn projected_sparse_operator_hermitian_positive_and_nontrivial(){
        let m=Torus2::build().unwrap();
        m.validate().unwrap();
        assert!(m.nnz_electric()>=DIM && m.nnz_electric()<DIM*25);
        assert_eq!(m.apply(1,0,&vec![1;DIM]).unwrap(),vec![0;DIM]);
        let mut wave=vec![0i128;DIM];
        for (i,item) in wave.iter_mut().enumerate(){*item=(i%7) as i128-3;}
        let hw=m.apply(3,5,&wave).unwrap();
        let norm:i128=wave.iter().zip(&hw).zip(&m.weights)
            .map(|((x,y),w)|x*y*i128::from(*w)).sum();
        assert!(norm>=0,"nonnegative electric + magnetic quadratic form");
    }
    #[test]
    fn torus_exact_electric_spectral_gap_and_magnetic_flat_degeneracy(){
        let m=Torus2::build().unwrap();
        m.electric_gap_witness().unwrap();
        assert_eq!(m.flat_wilson_orbit_keys().unwrap().len(),8);
        for (je,jb) in [(0,0),(1,0),(0,1),(1,1),(3,5)] {
            let d=m.diagnostics(je,jb).unwrap();
            assert!(d.connected);
            assert_eq!(d.qualitative_gap_positive,je>0);
            assert_eq!(d.quantitative_gap_certified,jb==0);
            assert_eq!(d.electric_only_exact_gap,6*je);
        }
    }
    #[test]
    fn torus_fail_closed_matrix_bounds_and_gauge_negative_controls(){
        let m=Torus2::build().unwrap();
        assert!(m.apply(-1,1,&vec![0;DIM]).is_err());
        assert!(m.apply(1,1,&vec![0;DIM-1]).is_err());
        assert!(m.diagnostics(11,0).is_err());
        let mut broken=m.clone();
        let first=broken.electric[0].iter().position(|(j,_)|*j!=0).unwrap();
        broken.electric[0][first].1-=1;
        assert!(broken.validate().is_err(),"Hermiticity or row sum should reject forged operator");
        let mut forged=m.clone();
        forged.magnetic[0]=13;
        assert!(forged.validate().is_err(),"forged Wilson potential should fail");
    }
}
