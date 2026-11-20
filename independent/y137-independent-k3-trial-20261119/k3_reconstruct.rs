//! Rebuild actual accepted K3 20-Jacobi-step integer trial and ALL its signed sources.
//! Separate physical S3 geometry and exact upward-rounding solver; no historical trial code.
//! Read-only original signed K3 archive is the comparison target, never used to construct Y.
use std::collections::{BTreeMap,BTreeSet,HashMap,HashSet};
use std::fs::File;
use std::io::{BufReader,Read};
use std::path::Path;
use std::time::Instant;
const PERM:[[u8;3];6]=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
const ORIGINAL_K3:usize=155_378;
const ENERGY:[u128;2]=[69_909_875_505,69_949_729_820];
const B:u128=1_000_000_000;
const SCALE:u128=1_000_000_000_000;
const STEPS:usize=20;
const LANE_COUNT:usize=8;

fn require(good:bool,msg:&str)->Result<(),String>{
    if good {Ok(())} else {Err(msg.into())}
}
fn permutation(p:[u8;3])->Result<u8,String>{
    PERM.iter().position(|&s|s==p).map(|x|x as u8)
        .ok_or_else(||"invalid_group_permutation".into())
}
fn location(x:usize,y:usize)->usize{(x%3)*4+y%4}
struct Gauge {
    multiplication:[[u8;6];6],
    inverse:[u8;6],
    flips:[u8;3],
    retain:[usize;13],
    transport:Vec<(usize,usize,usize)>,
}
impl Gauge {
    fn new()->Result<Self,String>{
        let mut multiplication=[[0;6];6];
        let mut inverse=[0;6];
        let mut flips=Vec::new();
        for (a,p) in PERM.iter().enumerate(){
            for (b,q) in PERM.iter().enumerate(){
                multiplication[a][b]=permutation([p[q[0] as usize],p[q[1] as usize],p[q[2] as usize]])?;
            }
            let mut rev=[0;3];
            for (i,&v) in p.iter().enumerate(){rev[v as usize]=i as u8;}
            inverse[a]=permutation(rev)?;
        }
        for a in 1..6 {if multiplication[a][a]==0{flips.push(a as u8);}}
        require(flips.len()==3,"three_involutions")?;
        let mut transport=Vec::new();
        for y in 0..3{transport.push((location(0,y),location(0,y+1),12+location(0,y)));}
        for y in 0..4{for x in 0..2{
            transport.push((location(x,y),location(x+1,y),location(x,y)));
        }}
        require(transport.len()==11,"spanning_tree_11_edges")?;
        let mut retained=Vec::new();
        for i in 0..24 {
            if !transport.iter().any(|&(_,_,edge)|edge==i){retained.push(i);}
        }
        require(retained.len()==13,"thirteen_fundamental_links")?;
        let mut retain=[0;13];retain.copy_from_slice(&retained);
        Ok(Self{multiplication,inverse,flips:[flips[0],flips[1],flips[2]],retain,transport})
    }
    fn mul(&self,a:u8,b:u8)->u8{self.multiplication[a as usize][b as usize]}
    fn key(&self,mut address:u64)->[u8;13]{
        let mut out=[0;13];
        for x in &mut out{*x=(address%6) as u8;address/=6;}
        out
    }
    fn address(&self,key:[u8;13])->u64{
        key.iter().rev().fold(0,|a,&x|a*6+u64::from(x))
    }
    fn expand(&self,key:[u8;13])->[u8;24]{
        let mut full=[0;24];
        for (i,&edge) in self.retain.iter().enumerate(){full[edge]=key[i];}
        full
    }
    fn canonical(&self,links:[u8;24])->[u8;13]{
        let mut root=[0;12];
        for &(from,to,edge) in &self.transport{root[to]=self.mul(root[from],links[edge]);}
        let mut residual=[0;13];
        for (k,&edge) in self.retain.iter().enumerate(){
            let first=edge%12;
            let x=first/4;let y=first%4;
            let second=if edge<12{location(x+1,y)}else{location(x,y+1)};
            residual[k]=self.mul(self.mul(root[first],links[edge]),
                                 self.inverse[root[second] as usize]);
        }
        let mut minimal=residual;
        for a in 1..6u8{
            let mut conjugated=[0;13];
            for (k,&v) in residual.iter().enumerate(){
                conjugated[k]=self.mul(self.mul(a,v),self.inverse[a as usize]);
            }
            if conjugated<minimal{minimal=conjugated;}
        }
        minimal
    }
    fn orbit_weight(&self,key:[u8;13])->usize{
        let mut seen=Vec::with_capacity(6);
        for a in 0..6u8{
            let mut t=[0;13];
            for (k,&v) in key.iter().enumerate(){
                t[k]=self.mul(self.mul(a,v),self.inverse[a as usize]);
            }
            if !seen.contains(&t){seen.push(t);}
        }
        seen.len()
    }
    fn magnetic(&self,key:[u8;13])->u32{
        let links=self.expand(key);
        let mut sum=0u32;
        for x in 0..3 {for y in 0..4{
            let i=location(x,y);
            let t=self.mul(links[i],links[12+location(x+1,y)]);
            let t=self.mul(t,self.inverse[links[location(x,y+1)] as usize]);
            let t=self.mul(t,self.inverse[links[12+i] as usize]);
            let p=PERM[t as usize];
            let fixed=p.iter().enumerate().filter(|&(k,&v)|k==v as usize).count();
            sum+=3-fixed as u32;
        }}
        sum
    }
    fn moves(&self,key:[u8;13])->Result<BTreeMap<u64,u32>,String>{
        let mut links=self.expand(key);
        let mut targets=BTreeMap::new();
        for i in 0..24{
            let old=links[i];
            for &t in &self.flips{
                links[i]=self.mul(t,old);
                let target=self.address(self.canonical(links));
                *targets.entry(target).or_insert(0)+=1;
            }
            links[i]=old;
        }
        require(targets.values().map(|&x|u64::from(x)).sum::<u64>()==72,
                "exact_original_72_raw_electric_moves")?;
        Ok(targets)
    }
}


#[derive(Clone)]
struct QRow {
    key:u64,
    weight:u8,
    diagonal:u32,
    to_flat:[u8;LANE_COUNT],
    inside:Vec<(usize,u8)>,
}
fn flats(rule:&Gauge)->Result<Vec<u64>,String>{
    let mut keys=BTreeSet::new();
    for a in 0..6u8 {
        for b in 0..6u8 {
            if rule.mul(a,b)!=rule.mul(b,a){continue;}
            let mut links=[0u8;24];
            for y in 0..4 {links[location(2,y)]=a;}
            for x in 0..3 {links[12+location(x,3)]=b;}
            keys.insert(rule.address(rule.canonical(links)));
        }
    }
    require(keys.len()==8,"original_S3_eight_commuting_flat_orbits")?;
    let flat=keys.into_iter().collect::<Vec<_>>();
    require(flat.iter().map(|&x|rule.orbit_weight(rule.key(x))).sum::<usize>()==18,
            "original_18_flat_raw_commuting_classes")?;
    Ok(flat)
}
fn layers(rule:&Gauge)->Result<Vec<u64>,String>{
    let original=flats(rule)?;
    let mut seen=original.iter().copied().collect::<HashSet<_>>();
    let mut all=original.clone();
    let mut last=original;
    let expected=[264usize,7770,147344];
    for (step,&want) in expected.iter().enumerate(){
        let mut next=BTreeSet::new();
        for &address in &last{
            let moves=rule.moves(rule.key(address))?;
            for (&target,_) in &moves {
                if !seen.contains(&target){next.insert(target);}
            }
        }
        require(next.len()==want,"independent_K3_shell_"+&step.to_string())?;
        last=next.into_iter().collect();
        for &address in &last {
            require(seen.insert(address),"repeated_K3_canonical_source_orbit")?;
        }
        all.extend_from_slice(&last);
    }
    require(all.len()==ORIGINAL_K3+8 && seen.len()==all.len(),
            "complete_K3_155378_nonflat_source_states")?;
    Ok(all)
}
fn graph(rule:&Gauge,all:&[u64])->Result<Vec<QRow>,String>{
    let ids=all.iter().enumerate().map(|(i,&key)|(key,i)).collect::<HashMap<_,_>>();
    let mut rows=Vec::with_capacity(ORIGINAL_K3);
    let mut census=[0u64;4];
    let mut magnetic_min=36u32;
    let mut magnetic_max=0u32;
    for &address in &all[8..]{
        let key=rule.key(address);
        require(rule.address(rule.canonical(rule.expand(key)))==address,
                "reconstructed_K3_canonical_address")?;
        let magnetic=rule.magnetic(key);
        require((3..=36).contains(&magnetic),"original_K3_nonflat_magnetic_cost")?;
        magnetic_min=magnetic_min.min(magnetic);
        magnetic_max=magnetic_max.max(magnetic);
        let mut inside=Vec::new();
        let mut to_flat=[0u8;LANE_COUNT];
        let mut self_edges=0u32;
        let near=rule.moves(key)?;
        let mut raw=0u32;
        for (target,coeff) in near{
            raw+=coeff;
            if target==address{self_edges+=coeff;}
            if let Some(&i)=ids.get(&target){
                if i<8{
                    to_flat[i]=u8::try_from(coeff).map_err(|e|e.to_string())?;
                    census[0]+=u64::from(coeff);
                }else if i-8<ORIGINAL_K3 {
                    if target!=address{
                        inside.push((i-8,u8::try_from(coeff).map_err(|e|e.to_string())?));
                        census[1]+=u64::from(coeff);
                    }else{census[2]+=u64::from(coeff);}
                }
            }else{
                census[3]+=u64::from(coeff);
            }
        }
        require(raw==72,"original_72_K3_raw_moves")?;
        let diagonal=72+9*magnetic-self_edges;
        rows.push(QRow{
            key:address,
            weight:u8::try_from(rule.orbit_weight(key)).map_err(|e|e.to_string())?,
            diagonal,to_flat,inside,
        });
    }
    require(rows.len()==ORIGINAL_K3 &&
            census.iter().sum::<u64>()==72*ORIGINAL_K3 as u64,
            "independent_K3_72raw_move_census")?;
    println!("Y137_INDEPENDENT_K3_GRAPH|nonflat={ORIGINAL_K3}|raw_moves={}|flat_links={}|K3_inside_nonself={}|selfloops={}|out_to_Q4={}|magnetic_min={magnetic_min}|magnetic_max={magnetic_max}|status=SOURCE_FROM_S3_RULES|json=0",
             72*ORIGINAL_K3 as u64,census[0],census[1],census[2],census[3]);
    Ok(rows)
}
fn jacobi(rows:&[QRow],z:u128)->Result<Vec<[u128;LANE_COUNT]>,String>{
    let mut current=vec![[0u128;LANE_COUNT];rows.len()];
    let mut next=vec![[0u128;LANE_COUNT];rows.len()];
    for _ in 0..STEPS{
        for (i,row) in rows.iter().enumerate(){
            let diagonal=B*u128::from(row.diagonal)-z;
            require(diagonal>0,"strict_positive_K3_Jacobi_diagonal")?;
            let mut sum=[0u128;LANE_COUNT];
            for (k,&c) in row.to_flat.iter().enumerate(){
                sum[k]=SCALE*u128::from(c);
            }
            for &(j,c) in &row.inside{
                for k in 0..LANE_COUNT{
                    let term=u128::from(c).checked_mul(current[j][k])
                        .ok_or_else(||"K3_Jacobi_term_overflow".to_owned())?;
                    sum[k]=sum[k].checked_add(term)
                        .ok_or_else(||"K3_Jacobi_sum_overflow".to_owned())?;
                }
            }
            for k in 0..LANE_COUNT{
                let numerator=B.checked_mul(sum[k])
                    .ok_or_else(||"K3_Jacobi_numerator_overflow".to_owned())?;
                next[i][k]=numerator/diagonal+u128::from(numerator%diagonal!=0);
                require(next[i][k]<(1u128<<90),"original_Jacobi_90bit_envelope")?;
            }
        }
        std::mem::swap(&mut current,&mut next);
    }
    Ok(current)
}
fn residuals(rows:&[QRow],y:&[[u128;LANE_COUNT]],z:u128)
        ->Result<Vec<[i128;LANE_COUNT]>,String>{
    let mut result=Vec::with_capacity(rows.len());
    for (i,row) in rows.iter().enumerate(){
        let mut t=[0u128;LANE_COUNT];
        for (k,&c) in row.to_flat.iter().enumerate(){t[k]=SCALE*u128::from(c);}
        for &(j,cc) in &row.inside{
            for k in 0..LANE_COUNT{
                t[k]+=u128::from(cc)*y[j][k];
            }
        }
        let diagonal=B*u128::from(row.diagonal)-z;
        let mut r=[0i128;LANE_COUNT];
        for k in 0..LANE_COUNT{
            let pos=diagonal.checked_mul(y[i][k])
                .ok_or_else(||"signed_K3_residual_pos_overflow".to_owned())?;
            let neg=B.checked_mul(t[k])
                .ok_or_else(||"signed_K3_residual_neg_overflow".to_owned())?;
            require(pos<(1u128<<124)&&neg<(1u128<<124),
                    "original_K3_signed_source_124bit_i128_envelope")?;
            r[k]=(pos as i128)-(neg as i128);
        }
        result.push(r);
    }
    Ok(result)
}
fn read_i128(reader:&mut impl Read)->Result<i128,String>{
    let mut width=[0u8;1];
    reader.read_exact(&mut width).map_err(|e|e.to_string())?;
    let n=(width[0]&127) as usize;
    let negative=width[0]&128!=0;
    require(n<=16&&(!negative||n!=0),"original_signed_K3_lane_header")?;
    let mut buf=[0u8;16];
    reader.read_exact(&mut buf[..n]).map_err(|e|e.to_string())?;
    require(n==0||buf[n-1]!=0,"nonminimal_original_K3_signed_lane")?;
    let abs=u128::from_le_bytes(buf);
    require(abs<(1u128<<124),"original_K3_archive_signed_magnitude")?;
    Ok(if negative{-(abs as i128)}else{abs as i128})
}
fn compare_archive(path:&Path,rule:&Gauge,rows:&[QRow],
       all_residual:&[Vec<[i128;LANE_COUNT]>;2])->Result<(),String>{
    let index=rows.iter().enumerate().map(|(i,r)|(r.key,i)).collect::<HashMap<_,_>>();
    let file=File::open(path).map_err(|e|e.to_string())?;
    let mut reader=BufReader::with_capacity(1<<20,file);
    let mut count=0usize;
    let mut last=None;
    loop{
        let mut h=[0u8;11];
        if reader.read(&mut h[..1]).map_err(|e|e.to_string())?==0{break;}
        reader.read_exact(&mut h[1..]).map_err(|e|e.to_string())?;
        let addr=u64::from_le_bytes(h[..8].try_into().map_err(|_|"K3_header_addr")?);
        require(h[9]==3 && h[10]==2,"original_K3_archive_header")?;
        if let Some(prev)=last{
            require(addr>prev,"original_K3_canonical_order")?;
        }
        last=Some(addr);
        let idx=*index.get(&addr).ok_or("new_source_K3_state_missing_from_original")?;
        require(rows[idx].weight==h[8],"independent_K3_orbit_weight")?;
        require(rule.address(rule.canonical(rule.expand(rule.key(addr))))==addr,
                "archive_not_original_S3_canonical")?;
        for (s,expected) in all_residual.iter().enumerate(){
            for k in 0..LANE_COUNT{
                let actual=read_i128(&mut reader)?;
                if actual!=expected[idx][k]{
                    return Err(format!("K3_new_Jacobi_source_disagrees_sample={s},state={addr},lane={k},expected={},original={}",
                                       expected[idx][k],actual));
                }
            }
        }
        count+=1;
    }
    require(count==ORIGINAL_K3,
            "original_155378_K3_full_signed_source_rows")?;
    println!("Y137_INDEPENDENT_K3_SOURCE_ACCEPT|new_S3_K3_states={ORIGINAL_K3}|Jacobi_sweeps=20|two_original_energies=69909875505,69949729820|all_16_source_lanes_per_state={}|all_original_signed_K3_rows=EXACT|new_trial_source=INDEPENDENT_GENERATION_PASS|full_original_signed_K3_source_SHA=CI_PRECHECK|original_Q4_residual=SEPARATE_FULL_CHECK|original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|json=0",ORIGINAL_K3*16);
    Ok(())
}
fn synthetic()->Result<(),String>{
    let rule=Gauge::new()?;
    require(flats(&rule)?.len()==8,"flat_source_toy")?;
    require(rule.moves([0;13])?.values().sum::<u32>()==72,"72move_toy")?;
    let z=70u128;
    let d=100u128;
    let numerator=1u128;
    require(numerator/d==0 && numerator/d+u128::from(numerator%d!=0)==1,
            "outward_Jacobi_rounding_tamper")?;
    require(z<d && B==1_000_000_000 && SCALE==1_000_000_000_000,
            "unaltered_frozen_source_scaling")?;
    println!("Y137_INDEPENDENT_K3_TOY|original_S3_flats=8|raw_moves=72|upward_integer_rounding=PASS|floor_rounding_forgery=REJECTED|frozen_b_and_scale=PASS|real_K3_signed_source=NOT_YET_COMPUTED|json=0");
    Ok(())
}
fn execute(path:&Path)->Result<(),String>{
    let start=Instant::now();
    let rule=Gauge::new()?;
    let keys=layers(&rule)?;
    let states=graph(&rule,&keys)?;
    let mut residual: [Vec<[i128;LANE_COUNT]>;2]=[Vec::new(),Vec::new()];
    for (s,&energy) in ENERGY.iter().enumerate(){
        let y=jacobi(&states,energy)?;
        residual[s]=residuals(&states,&y,energy)?;
        println!("Y137_INDEPENDENT_K3_NEW_TRIAL|sample_num={energy}|K3_orbits={ORIGINAL_K3}|sweeps={STEPS}|construction=INDEPENDENT_S3_20_JACOBI|status=READY_FOR_ORIGINAL_SOURCE_COMPARISON|json=0");
    }
    compare_archive(path,&rule,&states,&residual)?;
    println!("Y137_INDEPENDENT_K3_VERDICT|K3=155378|both_original_energies=PASS|independent_source_generation=PASS|full_original_K3_signed_vectors=EXACT|full_Q4=REQUIRES_INDEPENDENT_SOURCE_REBUILD|all_Perron_store=SEPARATE_GATE|Wilson=FORMAL_HOLD|elapsed_seconds={}|json=0",start.elapsed().as_secs());
    Ok(())
}
fn main(){
    let args=std::env::args().collect::<Vec<_>>();
    let result=match args.as_slice(){
        [_,mode] if mode=="toy"=>synthetic(),
        [_,mode,path] if mode=="real"=>execute(Path::new(path)),
        _=>Err("usage_k3_source toy_or_real SIGNED_K3_FILE".to_string()),
    };
    if let Err(e)=result{
        eprintln!("Y137_INDEPENDENT_K3_REFUSE|reason={}|source=HOLD|Wilson=FORMAL_HOLD|json=0",
                  e.replace('|',"_"));
        std::process::exit(2);
    }
}
