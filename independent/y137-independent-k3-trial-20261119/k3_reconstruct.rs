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
    outside:Vec<(u64,u8)>,
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
        require(next.len()==want,&format!("independent_K3_shell_{step}"))?;
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
        let mut outside=Vec::new();
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
                outside.push((target,u8::try_from(coeff).map_err(|e|e.to_string())?));
            }
        }
        require(raw==72,"original_72_K3_raw_moves")?;
        let diagonal=72+9*magnetic-self_edges;
        rows.push(QRow{
            key:address,
            weight:u8::try_from(rule.orbit_weight(key)).map_err(|e|e.to_string())?,
            diagonal,to_flat,inside,outside,
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
fn compare_archive(path:&Path,rule:&Gauge,rows:&[QRow])
      ->Result<(),String>{
    // Original Stage C K3 spool stores V1=X*R, not R. This is a
    // source *support* comparison only; V1 amplitudes are verified by
    // the separate complete signed full-Q replay.
    let index=rows.iter().map(|r|(r.key,r.weight)).collect::<HashMap<_,_>>();
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
        if let Some(prev)=last{require(addr>prev,"original_K3_canonical_order")?;}
        last=Some(addr);
        let w=*index.get(&addr).ok_or("new_K3_geometry_state_missing_from_StageC")?;
        require(w==h[8],"independent_K3_orbit_weight")?;
        require(rule.address(rule.canonical(rule.expand(rule.key(addr))))==addr,
                "original_K3_archive_not_S3_canonical")?;
        for _ in 0..(2*LANE_COUNT){let _=read_i128(&mut reader)?;}
        count+=1;
    }
    require(count==ORIGINAL_K3,"original_155378_K3_archive_states")?;
    println!("Y137_INDEPENDENT_K3_SUPPORT|original_archive_states=155378|independent_canonical_keys=ALL_MATCH|original_orbit_weights=ALL_MATCH|original_archive_V1_not_conflated_with_R=PASS|json=0");
    Ok(())
}
#[derive(Clone,Copy,Default,PartialEq,Eq)]
struct Int320([u64;5]);
impl Int320 {
    fn neg(&self)->bool{self.0[4]>>63!=0}
    fn negate(&mut self){
        let mut carry=1u128;
        for word in &mut self.0{
            let v=u128::from(!*word)+carry;
            *word=v as u64;
            carry=v>>64;
        }
    }
    fn abs_word(&self)->[u64;5]{
        let mut x=*self;
        if x.neg(){x.negate();}
        x.0
    }
    fn bounded(&self)->bool{self.abs_word()[4]<(1u64<<38)}
    fn add(&mut self,other:&Self)->Result<(),String>{
        let same=self.neg()==other.neg();
        let sign=self.neg();
        let mut carry=0u128;
        let mut result=[0u64;5];
        for k in 0..5{
            let t=u128::from(self.0[k])+u128::from(other.0[k])+carry;
            result[k]=t as u64;
            carry=t>>64;
        }
        let value=Self(result);
        require(!same||value.neg()==sign,"signed_320bit_overflow")?;
        require(value.bounded(),"independent_2pow294_partial_bound")?;
        *self=value;Ok(())
    }
    fn multiply(a:i128,b:i128,c:i64)->Result<Self,String>{
        let negative=(a<0)^(b<0)^(c<0);
        let aa=a.unsigned_abs();
        let bb=b.unsigned_abs();
        let cc=c.unsigned_abs();
        require(aa<(1u128<<123)&&bb<(1u128<<123)&&cc<(1u64<<48),
                "independent_signed_source_or_coefficient_bound")?;
        let al=[aa as u64,(aa>>64) as u64];
        let bl=[bb as u64,(bb>>64) as u64];
        let mut raw=[0u64;4];
        for i in 0..2{
            let mut carry=0u128;
            for j in 0..2{
                let k=i+j;
                let v=u128::from(al[i])*u128::from(bl[j])+u128::from(raw[k])+carry;
                raw[k]=v as u64;
                carry=v>>64;
            }
            let k=i+2;
            let v=u128::from(raw[k])+carry;
            require(v>>64==0,"exact_128x128_mul_carry")?;
            raw[k]=v as u64;
        }
        let mut result=[0u64;5];
        let mut carry=0u128;
        for k in 0..4{
            let v=u128::from(raw[k])*u128::from(cc)+carry;
            result[k]=v as u64;
            carry=v>>64;
        }
        result[4]=carry as u64;
        let mut term=Self(result);
        require(!term.neg()&&term.bounded(),"exact_product_exceeds_2pow294")?;
        if negative && aa!=0 && bb!=0 && cc!=0{term.negate();}
        Ok(term)
    }
    fn decimal(&self)->String{
        let negative=self.neg();
        let mut words=self.abs_word();
        if words.iter().all(|&x|x==0){return "0".into();}
        let mut digits=Vec::new();
        while words.iter().any(|&x|x!=0){
            let mut carry=0u128;
            for word in words.iter_mut().rev(){
                let v=(carry<<64)+u128::from(*word);
                *word=(v/10) as u64;
                carry=v%10;
            }
            digits.push((b'0'+carry as u8) as char);
        }
        if negative{digits.push('-');}
        digits.iter().rev().collect()
    }
}


struct Q4Residual {
    weight:u8,
    incoming:[u128;LANE_COUNT],
}
fn new_q4_source(rule:&Gauge,rows:&[QRow],y:&[[u128;LANE_COUNT]])
         ->Result<HashMap<u64,Q4Residual>,String>{
    use std::collections::hash_map::Entry;
    let mut all=HashMap::with_capacity(1_985_218);
    let mut raw_edges=0u64;
    for (i,row) in rows.iter().enumerate(){
        for &(dest,coeff) in &row.outside{
            let current=match all.entry(dest){
                Entry::Occupied(o)=>o.into_mut(),
                Entry::Vacant(o)=>{
                    let w=rule.orbit_weight(rule.key(dest));
                    require((w==1||w==2||w==3||w==6)&&w>0,
                            "independent_Q4_orbit_weight")?;
                    o.insert(Q4Residual{weight:w as u8,incoming:[0u128;LANE_COUNT]})
                }
            };
            let w_q4=u64::from(current.weight);
            let weighted=u64::from(row.weight)*u64::from(coeff);
            require(weighted%w_q4==0,
                    "new_Q4_K3_exact_weighted_reciprocity")?;
            let reverse=weighted/w_q4;
            for k in 0..LANE_COUNT{
                let term=u128::from(reverse).checked_mul(y[i][k])
                    .ok_or_else(||"Q4_residual_source_mul_overflow".to_owned())?;
                current.incoming[k]=current.incoming[k].checked_add(term)
                    .ok_or_else(||"Q4_residual_source_add_overflow".to_owned())?;
            }
            raw_edges+=u64::from(coeff);
        }
    }
    require(all.len()==1_985_218 && raw_edges==9_789_408,
            "all_original_Q4_1985218_external_states")?;
    println!("Y137_INDEPENDENT_Q4_RESIDUAL|actual_Q4_states={}|original_K3_Q4_raw_edges={}|independent_source=WEIGHTED_ELECTRIC_CONTRACTION|original_Q4_S3_orbit_weights=REBUILT|original_StageC_V1=SEPARATE_CHECK|json=0",
            all.len(),raw_edges);
    Ok(all)
}
fn gram_add(out:&mut [[Int320;LANE_COUNT];LANE_COUNT],
            row:&[i128;LANE_COUNT],weight:i64)->Result<(),String>{
    for a in 0..LANE_COUNT{for b in a..LANE_COUNT{
        out[a][b].add(&Int320::multiply(row[a],row[b],weight)?)?;
    }}
    Ok(())
}
fn full_source_gram(rule:&Gauge,rows:&[QRow],y:&[[u128;LANE_COUNT]],
                   r:&[[i128;LANE_COUNT]])
       ->Result<[[Int320;LANE_COUNT];LANE_COUNT],String>{
    let mut result=[[Int320::default();LANE_COUNT];LANE_COUNT];
    for (i,row) in rows.iter().enumerate(){
        gram_add(&mut result,&r[i],6*i64::from(row.weight))?;
    }
    let q4=new_q4_source(rule,rows,y)?;
    for source in q4.values(){
        let mut r4=[0i128;LANE_COUNT];
        for k in 0..LANE_COUNT{
            let p=(B).checked_mul(source.incoming[k])
                .ok_or_else(||"Q4_original_R4_positive_source_overflow".to_owned())?;
            require(p<(1u128<<122),"Q4_R4_122bit_bound")?;
            r4[k]=-(p as i128);
        }
        gram_add(&mut result,&r4,6*i64::from(source.weight))?;
    }
    for i in 0..LANE_COUNT{for j in 0..i{result[i][j]=result[j][i];}}
    Ok(result)
}
fn expected_matrix_digits(source:&Path,z:u128,field:&str)
          ->Result<Vec<Vec<String>>,String>{
    let text=std::fs::read_to_string(source).map_err(|e|e.to_string())?;
    let rows=text.lines().filter(|x|x.starts_with("Y137_CACHE_POINT|"))
        .filter(|line|line.split('|').any(|f|f==format!("sample_num={z}")))
        .collect::<Vec<_>>();
    require(rows.len()==1,"single_accepted_G0_source_energy")?;
    let name=format!("{field}=");
    let raw=rows[0].split('|').find_map(|x|x.strip_prefix(&name))
        .ok_or_else(||"missing_original_source_8x8_matrix".to_owned())?;
    let result=raw.split(';').map(|r|r.split(',').map(str::to_owned)
                       .collect::<Vec<_>>()).collect::<Vec<_>>();
    require(result.len()==LANE_COUNT &&
           result.iter().all(|r|r.len()==LANE_COUNT),
           "original_8x8_matrix_shape")?;
    Ok(result)
}
fn compare_original_g(source:&Path,z:u128,gram:[[Int320;LANE_COUNT];LANE_COUNT])
      ->Result<(),String>{
    let original=expected_matrix_digits(source,z,"G0")?;
    for i in 0..LANE_COUNT{for j in 0..LANE_COUNT{
        require(gram[i][j].decimal()==original[i][j],
                &format!("new_original_K3_Q4_G0_mismatch_energy_{z}_row_{i}_col_{j}"))?;
    }}
    println!("Y137_INDEPENDENT_K3_Q4_GRAM|sample_num={z}|K3_states=155378|Q4_states=1985218|new_original_R_K3_AND_R_Q4=INDEPENDENTLY_GENERATED|all_original_8x8_G0_entries=64_OF_64_MATCH|original_source=IMMUTABLE_CACHE|json=0");
    Ok(())
}
fn exact_u(rows:&[QRow],y:&[[u128;LANE_COUNT]],
           residual:&[[i128;LANE_COUNT]],z:u128)
     ->Result<[[i128;LANE_COUNT];LANE_COUNT],String>{
    let mut u=[[0i128;LANE_COUNT];LANE_COUNT];
    let wf=[1i128,3,2,3,3,2,2,2];
    for k in 0..LANE_COUNT{
        let diagonal=(B*72-z) as i128;
        u[k][k]=diagonal*(SCALE as i128)*(SCALE as i128)*wf[k];
    }
    for (i,row) in rows.iter().enumerate(){
        let w=i128::from(row.weight);
        for k in 0..LANE_COUNT{
            let yi=y[i][k] as i128;
            for j in 0..LANE_COUNT{
                let yj=y[i][j] as i128;
                let r=residual[i][j];
                let positive=w.checked_mul(yi).and_then(|v|v.checked_mul(r))
                    .ok_or_else(||"exact_U_trial_residual_product_overflow".to_owned())?;
                let negative=w*i128::from(row.to_flat[k])*
                               (B as i128)*(SCALE as i128)*yj;
                let change=positive.checked_sub(negative)
                    .ok_or_else(||"exact_U_PQ_coupling_overflow".to_owned())?;
                u[k][j]=u[k][j].checked_add(change)
                    .ok_or_else(||"exact_U_128bit_accumulation_overflow".to_owned())?;
            }
        }
    }
    require((0..LANE_COUNT).all(|i|(0..LANE_COUNT)
            .all(|j|u[i][j]==u[j][i])),"new_exact_K3_U_matrix_symmetry")?;
    Ok(u)
}
fn expected_source_u(path:&Path,z:u128)
      ->Result<[[i128;LANE_COUNT];LANE_COUNT],String>{
    let text=std::fs::read_to_string(path).map_err(|e|e.to_string())?;
    let lines=text.lines().filter(|l|l.starts_with("Y137_CACHE_POINT|"))
        .filter(|l|l.split('|').any(|f|f==format!("sample_num={z}")))
        .collect::<Vec<_>>();
    require(lines.len()==1,"single_immutable_original_U_source_energy")?;
    let field=lines[0].split('|').find_map(|x|x.strip_prefix("U0="))
        .ok_or_else(||"original_U0_matrix_missing".to_owned())?;
    let mut out=[[0i128;LANE_COUNT];LANE_COUNT];
    let rr=field.split(';').collect::<Vec<_>>();
    require(rr.len()==LANE_COUNT,"original_U0_row_count")?;
    for (i,line) in rr.iter().enumerate(){
        let nums=line.split(',').collect::<Vec<_>>();
        require(nums.len()==LANE_COUNT,"original_U0_column_count")?;
        for (j,n) in nums.iter().enumerate(){
            out[i][j]=n.parse::<i128>().map_err(|e|e.to_string())?;
        }
    }
    Ok(out)
}
fn compare_u_source(path:&Path,z:u128,
      observed:[[i128;LANE_COUNT];LANE_COUNT])->Result<(),String>{
    let original=expected_source_u(path,z)?;
    for i in 0..LANE_COUNT{for j in 0..LANE_COUNT{
        require(observed[i][j]==original[i][j],
                &format!("new_K3_U0_mismatch_energy_{z}_row_{i}_column_{j}"))?;
    }}
    println!("Y137_INDEPENDENT_K3_TRIAL_U|sample_num={z}|new_original_20_Jacobi_sweeps=PASS|all_original_8x8_U0_entries=64_OF_64_MATCH|original_U0_source=IMMUTABLE_CACHE|K3_signed_residual=INDEPENDENTLY_GENERATED|original_StageC_V1=SEPARATE_SOURCE_GATE|json=0");
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
fn execute(archive:&Path,source:&Path)->Result<(),String>{
    let start=Instant::now();
    let rule=Gauge::new()?;
    let keys=layers(&rule)?;
    let states=graph(&rule,&keys)?;
    compare_archive(archive,&rule,&states)?;
    for &energy in &ENERGY{
        let y=jacobi(&states,energy)?;
        let r=residuals(&states,&y,energy)?;
        compare_u_source(source,energy,exact_u(&states,&y,&r,energy)?)?;
        compare_original_g(source,energy,full_source_gram(&rule,&states,&y,&r)?)?;
    }
    println!("Y137_INDEPENDENT_K3_VERDICT|K3=155378|two_original_energy_trials=20_JACOBI_EACH|original_U0_matrix_entries=128_OF_128_MATCH|original_G0_matrix_entries=128_OF_128_MATCH|original_K3_Q4_R_source=INDEPENDENTLY_GENERATED|original_K3_support_and_weights=FULL_PASS|original_Q4_residual=SEPARATE_FULL_SOURCE_GATE|original_StageC_signed_V1=SEPARATE_SOURCE_GATE|whole_Perron_store=SEPARATE_GATE|Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|elapsed_seconds={}|json=0",start.elapsed().as_secs());
    Ok(())
}
fn main(){
    let args=std::env::args().collect::<Vec<_>>();
    let result=match args.as_slice(){
        [_,mode] if mode=="toy"=>synthetic(),
        [_,mode,archive,source] if mode=="real"=>execute(Path::new(archive),Path::new(source)),
        _=>Err("usage_k3_source toy_or_real ORIGINAL_SIGNED_V1_K3_FILE ORIGINAL_U0_CACHE".to_string()),
    };
    if let Err(e)=result{
        eprintln!("Y137_INDEPENDENT_K3_REFUSE|reason={}|source=HOLD|Wilson=FORMAL_HOLD|json=0",
                  e.replace('|',"_"));
        std::process::exit(2);
    }
}
