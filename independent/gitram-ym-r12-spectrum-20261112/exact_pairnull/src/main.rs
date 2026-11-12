//! Exact pairwise-conditioned 9-trit count-table Metropolis-Hastings, integer-only.
//! Source: SHA-pinned GitRAM 3x3 frozen nine-leaf table at coupling r=12.
//! 3^9 = 19683 patterns. Every 2x2x2 trade preserves all 36 pair tables exactly.
//! Proposal: choose uniformly from currently FEASIBLE ORIENTED trades.
//! Stationary target (conditional multinomial pairwise log-linear model):
//!     P(counts | all pair margins) proportional to 1 / product_x counts[x]!
//! MH ratio: product(decremented old counts) / product(incremented old counts+1)
//!           times M(current)/M(proposed).
//! This exact stationary relation does not prove irreducibility or adequate mixing.
//! Receipt: no floats, no JSON, 3 independent hosted Rust 1.81 cells.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]
use std::collections::{BTreeSet, HashSet};
use std::env;
use std::fs;
use std::path::Path;

const N: usize = 19683;
const W: [usize; 9] = [1,3,9,27,81,243,729,2187,6561];
const SOURCE_SHA: &str = "2220ee3a11c66281b586de77f44999c06e863f0e9f83509a867047048326bbc7";
const STEPS: usize = 40000;
const BURN: usize = 10000;
const THIN: usize = 1000;
const PAIRS: [[u16;2];3] = [[0,1],[0,2],[1,2]];

#[derive(Clone,Copy)]
struct Cube { cells: [u16;8] }

struct Rng {state:u64}
impl Rng {
    fn new(seed:u64)->Self{Self{state:seed}}
    fn next64(&mut self)->u64{
        self.state=self.state.wrapping_add(0x9e3779b97f4a7c15);
        let mut z=self.state;
        z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);
        z^(z>>31)
    }
    fn below(&mut self,n:u128)->u128{
        assert!(n>0);
        let lim=u128::MAX-(u128::MAX % n);
        loop {
            let v=((self.next64() as u128)<<64)|(self.next64() as u128);
            if v<lim {return v%n}
        }
    }
}

fn from_row(line:&str)->Option<usize>{
    if !line.starts_with("LEAF|"){return None}
    let field=line.split('|').find(|x|x.starts_with("trits=")).expect("trits");
    let mut state=0usize;
    let mut n=0usize;
    for (i,x) in field.strip_prefix("trits=").unwrap().split(',').enumerate(){
        let trit:usize=x.parse().expect("trit number");
        assert!(i<9 && trit<3);
        state+=trit*W[i];
        n+=1;
    }
    assert_eq!(n,9);
    Some(state)
}
fn load(path:&Path)->Vec<u16>{
    let content=fs::read_to_string(path).expect("frozen nine leaves missing");
    let mut counts=vec![0u16;N];
    let mut rows=0usize;
    let mut keys=BTreeSet::new();
    for line in content.lines(){
        if line.starts_with("NINE_LEAF_FREEZE|"){
            assert!(line.contains("source_run=43222707802"));
            assert!(line.contains("rows=682"));
        } else if let Some(state)=from_row(line){
            let key:u64=line.split('|').find(|x|x.starts_with("key="))
                .expect("key").strip_prefix("key=").unwrap().parse().unwrap();
            assert!(keys.insert(key),"duplicate class key");
            counts[state]+=1;
            rows+=1;
        } else {panic!("unrecognized frozen leaf line")}
    }
    assert_eq!(rows,682);
    assert_eq!(counts.iter().map(|&x|x as usize).sum::<usize>(),682);
    assert_eq!(keys.len(),682);
    counts
}
fn pair_margins(counts:&[u16])->Vec<u32>{
    let mut result=vec![0u32;36*9];
    for (ix,&cnt) in counts.iter().enumerate(){
        if cnt==0 {continue}
        let mut trit=[0usize;9];
        for k in 0..9 {trit[k]=(ix/W[k])%3}
        let mut pair=0usize;
        for i in 0..9 {
            for j in (i+1)..9 {
                result[pair*9+3*trit[i]+trit[j]]+=cnt as u32;
                pair+=1;
            }
        }
        assert_eq!(pair,36);
    }
    result
}
fn three_equal(ix:usize)->bool{
    let first=ix%3;
    (1..9).all(|k|(ix/W[k])%3==first)
}
fn statistics(counts:&[u16],initial:&[u16])->(usize,usize,usize,usize,usize){
    let mut pats=0usize;let mut largest=0usize;let mut equal=0usize;let mut dist=0usize;
    let mut majority=0usize;
    for ix in 0..N {
        let c=counts[ix] as usize;
        if c>0 {
            pats+=1;
            largest=largest.max(c);
            if three_equal(ix){equal+=c}
            let mut votes=[0usize;3];
            for k in 0..9{votes[(ix/W[k])%3]+=1}
            majority+=c*votes.iter().max().copied().unwrap();
        }
        dist+=usize::from(counts[ix].abs_diff(initial[ix]));
    }
    assert_eq!(dist%2,0);
    (pats,largest,equal,dist/2,majority)
}
fn build()->(Vec<Cube>,Vec<Vec<u32>>){
    let mut cubes=Vec::with_capacity(84*27*729);
    let mut incidents:Vec<Vec<u32>>=(0..N).map(|_|Vec::with_capacity(672)).collect();
    for a in 0..9 {
        for b in (a+1)..9{
            for c in (b+1)..9{
                let rest:Vec<usize>=(0..9).filter(|&z|z!=a&&z!=b&&z!=c).collect();
                assert_eq!(rest.len(),6);
                for ia in 0..3 {
                    for ib in 0..3 {
                        for ic in 0..3 {
                            for context in 0..729usize {
                                let mut val=context;
                                let mut base=0usize;
                                for &k in &rest{base+=(val%3)*W[k];val/=3}
                                let mut cells=[0u16;8];
                                for mask in 0..8usize{
                                    let x=PAIRS[ia][(mask&1) as usize] as usize;
                                    let y=PAIRS[ib][((mask>>1)&1) as usize] as usize;
                                    let z=PAIRS[ic][((mask>>2)&1) as usize] as usize;
                                    let addr=base+x*W[a]+y*W[b]+z*W[c];
                                    assert!(addr<N);
                                    cells[mask]=addr as u16;
                                }
                                let id=cubes.len() as u32;
                                for &cell in &cells{incidents[cell as usize].push(id)}
                                cubes.push(Cube{cells});
                            }
                        }
                    }
                }
            }
        }
    }
    assert_eq!(cubes.len(),84*27*729);
    assert!(incidents.iter().all(|x|x.len()==672));
    (cubes,incidents)
}
struct Chain {
    counts:Vec<u16>,
    original:Vec<u16>,
    margins:Vec<u32>,
    cubes:Vec<Cube>,
    incidents:Vec<Vec<u32>>,
    active:Vec<u32>,
    slots:Vec<i32>,
    seen:Vec<u32>,
    epoch:u32,
    rng:Rng,
    proposed:usize,
    accepted:usize,
}
impl Chain {
    fn new(initial:Vec<u16>,seed:u64)->Self {
        let (cubes,incidents)=build();
        let nmoves=cubes.len()*2;
        let mut x=Self{
            margins:pair_margins(&initial),counts:initial.clone(),original:initial,
            cubes,incidents,active:Vec::new(),slots:vec![-1;nmoves],
            seen:vec![0;nmoves/2],epoch:1,rng:Rng::new(seed),
            proposed:0,accepted:0,
        };
        for cube in 0..x.cubes.len(){
            x.refresh(cube as u32*2);
            x.refresh(cube as u32*2+1);
        }
        x.verify();
        x
    }
    fn feasible(&self,mid:u32)->bool{
        let cube=self.cubes[(mid/2) as usize];
        let side=mid&1;
        for k in 0..8u32 {
            if (k.count_ones()&1)==side && self.counts[cube.cells[k as usize] as usize]==0 {
                return false
            }
        }
        true
    }
    fn refresh(&mut self,mid:u32){
        let yes=self.feasible(mid);
        let at=self.slots[mid as usize];
        if yes && at<0{
            self.slots[mid as usize]=self.active.len() as i32;
            self.active.push(mid);
        } else if !yes && at>=0{
            let index=at as usize;
            self.active.swap_remove(index);
            if index<self.active.len(){
                let moved=self.active[index];
                self.slots[moved as usize]=index as i32;
            }
            self.slots[mid as usize] = -1;
        }
    }
    fn update_count(&mut self,mid:u32){
        let cube=self.cubes[(mid/2) as usize].cells;
        let side=mid&1;
        for k in 0..8u32 {
            let idx=cube[k as usize] as usize;
            if (k.count_ones()&1)==side {
                assert!(self.counts[idx]>0);
                self.counts[idx]-=1;
            } else {self.counts[idx]+=1}
        }
        self.epoch+=1;
        for &ix in &cube{
            let n=self.incidents[ix as usize].len();
            for j in 0..n{
                let id=self.incidents[ix as usize][j] as usize;
                if self.seen[id]!=self.epoch {
                    self.seen[id]=self.epoch;
                    self.refresh((2*id) as u32);
                    self.refresh((2*id+1) as u32);
                }
            }
        }
    }
    fn swap_direction(mid:u32)->u32{mid^1}
    fn probability(&self,mid:u32)->(u128,u128){
        let cube=self.cubes[(mid/2) as usize];
        let side=mid&1;
        let mut numerator=1u128;
        let mut denominator=1u128;
        for k in 0..8u32{
            let count=self.counts[cube.cells[k as usize] as usize] as u128;
            if (k.count_ones()&1)==side{numerator*=count}
            else{denominator*=count+1}
        }
        (numerator,denominator)
    }
    fn advance(&mut self){
        if self.active.is_empty(){return}
        self.proposed+=1;
        let old_m=self.active.len() as u128;
        let mid=self.active[self.rng.below(old_m) as usize];
        assert!(self.feasible(mid));
        let (old_num,old_den)=self.probability(mid);
        assert!(old_num>0&&old_den>0);
        self.update_count(mid);
        let new_m=self.active.len() as u128;
        assert!(new_m>0 && self.feasible(Self::swap_direction(mid)));
        let num=old_num*old_m;
        let den=old_den*new_m;
        let accept=num>=den||self.rng.below(den)<num;
        if accept{self.accepted+=1}
        else{self.update_count(Self::swap_direction(mid))}
    }
    fn verify(&self){
        assert_eq!(pair_margins(&self.counts),self.margins,"ANY pairwise margin changed");
        assert_eq!(self.counts.iter().map(|&v|v as usize).sum::<usize>(),682);
        assert_eq!(self.active.iter().copied().collect::<HashSet<_>>().len(),self.active.len());
        for (ix,&mid) in self.active.iter().enumerate(){
            assert_eq!(self.slots[mid as usize],ix as i32);
            assert!(self.feasible(mid));
        }
    }
}
fn main(){
    let a:Vec<String>=env::args().collect();
    assert_eq!(a.len(),4,"usage: exact_pairnull INPUT-FROZEN.hbp SEED OUTPUT.hbp");
    let input=Path::new(&a[1]);
    let seed:u64=a[2].parse().expect("seed integer");
    let output=Path::new(&a[3]);
    let counts=load(input);
    let before=statistics(&counts,&counts);
    let mut chain=Chain::new(counts,seed);
    let initial_moves=chain.active.len();
    assert!(initial_moves>0,"trapped: no oriented cube moves");
    let first=chain.original.clone();
    // Verify an arbitrary move can be inverted exactly without changing pair marginals.
    let probe=chain.active[0];
    chain.update_count(probe);
    assert_eq!(pair_margins(&chain.counts),chain.margins);
    chain.update_count(Chain::swap_direction(probe));
    assert_eq!(chain.counts,first,"inverse trade failed");
    chain.verify();
    let mut result=vec![
        format!("CONTRACT|schema=gitram.ym.r12.nineleaf.pairnull.v1|source_run=43231913054|source_sha256={SOURCE_SHA}|fixed_margins=all36x9|arithmetic=integer_only|proposal=uniform_feasible_oriented_cube|target=conditional_multinomial_factorial|acceptance=exact_MH|json=0"),
        format!("INITIAL|seed={seed}|patterns={}|largest={}|all_equal={}|available_moves={initial_moves}|row_count=682|json=0",before.0,before.1,before.2),
    ];
    let mut n=0usize;
    let mut min_pat=usize::MAX;let mut max_pat=0usize;
    let mut min_largest=usize::MAX;let mut max_largest=0usize;
    let mut min_equal=usize::MAX;let mut max_equal=0usize;
    let mut min_dist=usize::MAX;let mut max_dist=0usize;
    let mut le_real=0usize;
    let mut states=HashSet::<Vec<u16>>::new();
    let mut min_moves=usize::MAX;let mut max_moves=0usize;
    for step in 1..=STEPS{
        chain.advance();
        if step%THIN==0{
            chain.verify();
            let stat=statistics(&chain.counts,&chain.original);
            min_moves=min_moves.min(chain.active.len());
            max_moves=max_moves.max(chain.active.len());
            result.push(format!("STEP|seed={seed}|tick={step}|patterns={}|largest={}|all_equal={}|min_row_edits={}|available_moves={}|accepted={}|proposed={}|json=0",
                stat.0,stat.1,stat.2,stat.3,chain.active.len(),chain.accepted,chain.proposed));
            if step>=BURN {
                n+=1;
                states.insert(chain.counts.clone());
                min_pat=min_pat.min(stat.0);max_pat=max_pat.max(stat.0);
                min_largest=min_largest.min(stat.1);max_largest=max_largest.max(stat.1);
                min_equal=min_equal.min(stat.2);max_equal=max_equal.max(stat.2);
                min_dist=min_dist.min(stat.3);max_dist=max_dist.max(stat.3);
                if stat.0<=before.0{le_real+=1}
            }
        }
    }
    assert_eq!(n,31);
    chain.verify();
    result.push(format!("SUMMARY|seed={seed}|steps={STEPS}|burn={BURN}|thinning={THIN}|samples={n}|unique_tables={}|accepted={}|proposed={}|initial_moves={initial_moves}|moves_min={min_moves}|moves_max={max_moves}|patterns_min={min_pat}|patterns_max={max_pat}|patterns_le_observed={le_real}|largest_min={min_largest}|largest_max={max_largest}|all_equal_min={min_equal}|all_equal_max={max_equal}|min_row_edits_min={min_dist}|min_row_edits_max={max_dist}|pair_margins_exact=PASS|mixing_proven=NO|json=0",states.len(),chain.accepted,chain.proposed));
    result.push(format!("GITRAM_SHARD_PASS|seed={seed}|pair_margins_exact=1|source_sha256={SOURCE_SHA}|json=0"));
    fs::create_dir_all(output.parent().expect("output directory")).unwrap();
    fs::write(output,result.join("\n")+"\n").unwrap();
    for line in result.iter().filter(|s|s.starts_with("CONTRACT|")||s.starts_with("INITIAL|")||s.starts_with("SUMMARY|")||s.starts_with("GITRAM_SHARD_PASS|")){println!("{line}")}
}
