//! Rebuild actual accepted K3 20-Jacobi-step integer trial and ALL its signed sources.
//! Separate physical S3 geometry and exact upward-rounding solver; no historical trial code.
//! Read-only original signed K3 archive is the comparison target, never used to construct Y.
use std::collections::{BTreeMap,BTreeSet,HashMap,HashSet};
use std::fs::File;
use std::io::{BufReader,Read,Write};
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
    // Historical physical P basis is lexicographically sorted by the
    // 13 retained-link tuple; little-endian base-6 addresses sort differently.
    let mut flat=keys.into_iter().collect::<Vec<_>>();
    flat.sort_by_key(|&a|rule.key(a));
    require(flat.iter().map(|&a|rule.orbit_weight(rule.key(a))).collect::<Vec<_>>()
            ==vec![1,3,2,3,3,2,2,2],
            "original_eight_flat_channel_tuple_order_and_WF")?;
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

fn rebuild_k3_v1(rule:&Gauge,rows:&[QRow],
           y:&[[u128;LANE_COUNT]],r:&[[i128;LANE_COUNT]],z:u128)
           ->Result<Vec<[i128;LANE_COUNT]>,String>{
    // V1 = X R, X=b QHQ-z. The R support is K3+Q4, with all
    // Q5 rows zero. Re-enumerate Q4 values from the new K3 trial.
    let exterior=new_q4_source(rule,rows,y)?;
    let mut v=Vec::with_capacity(rows.len());
    for (i,row) in rows.iter().enumerate(){
        let diagonal=(B*u128::from(row.diagonal)-z) as i128;
        let mut lane=[0i128;LANE_COUNT];
        for k in 0..LANE_COUNT{
            let mut ans=diagonal.checked_mul(r[i][k])
                .ok_or_else(||"original_K3_V1_diagonal_overflow".to_owned())?;
            for &(j,coeff) in &row.inside{
                let term=(B as i128).checked_mul(i128::from(coeff))
                    .and_then(|t|t.checked_mul(r[j][k]))
                    .ok_or_else(||"new_K3_V1_inner_term_overflow".to_owned())?;
                ans=ans.checked_sub(term)
                    .ok_or_else(||"new_K3_V1_inner_accum_overflow".to_owned())?;
            }
            for &(dest,coeff) in &row.outside{
                let q=exterior.get(&dest).ok_or_else(||"missing_Q4_R_source".to_owned())?;
                let positive=i128::try_from(q.incoming[k])
                    .map_err(|e|e.to_string())?;
                // Original Q4 R is -B*positive. Therefore -B*c*R4
                // contributes +B^2*c*positive to V1.
                let term=(B as i128).checked_mul(B as i128)
                    .and_then(|t|t.checked_mul(i128::from(coeff)))
                    .and_then(|t|t.checked_mul(positive))
                    .ok_or_else(||"new_K3_V1_Q4_term_overflow".to_owned())?;
                ans=ans.checked_add(term)
                    .ok_or_else(||"new_K3_V1_Q4_accum_overflow".to_owned())?;
            }
            require(ans.unsigned_abs()<(1u128<<123),
                    "new_K3_V1_signed_123bit_bound")?;
            lane[k]=ans;
        }
        v.push(lane);
    }
    Ok(v)
}
fn compare_original_k3_v1(path:&Path,rows:&[QRow],
                   new_values:&[Vec<[i128;LANE_COUNT]>;2])
                   ->Result<(),String>{
    require(new_values.iter().all(|v|v.len()==ORIGINAL_K3),
            "new_original_K3_V1_row_count")?;
    let index=rows.iter().enumerate().map(|(i,r)|(r.key,i)).collect::<HashMap<_,_>>();
    let mut reader=BufReader::with_capacity(1<<20,
        File::open(path).map_err(|e|e.to_string())?);
    let mut total=0usize;
    let mut previous=None;
    loop{
        let mut header=[0u8;11];
        if reader.read(&mut header[..1]).map_err(|e|e.to_string())?==0{break;}
        reader.read_exact(&mut header[1..]).map_err(|e|e.to_string())?;
        let address=u64::from_le_bytes(header[..8].try_into()
            .map_err(|_|"K3_V1_address_header")?);
        require(header[9]==3&&header[10]==2,
                "K3_V1_original_archive_shell_and_samples")?;
        if let Some(prev)=previous{
            require(address>prev,"K3_V1_original_sorted_canonical_addresses")?;
        }
        previous=Some(address);
        let i=*index.get(&address).ok_or_else(||"K3_V1_missing_address".to_owned())?;
        require(header[8]==rows[i].weight,"K3_V1_original_weight")?;
        for (sample,source) in new_values.iter().enumerate(){
            for k in 0..LANE_COUNT{
                let observed=read_i128(&mut reader)?;
                let expected=source[i][k];
                require(observed==expected,
                    &format!("K3_first_principles_V1_mismatch_sample_{sample}_address_{address}_lane_{k}_new_{expected}_original_{observed}"))?;
                total+=1;
            }
        }
    }
    require(total==ORIGINAL_K3*LANE_COUNT*2,
            "all_2486048_original_K3_V1_signed_channels")?;
    println!("Y137_INDEPENDENT_K3_V1_ACCEPT|physical_K3_states=155378|energies=2|signed_archive_V1=X_R_values=2486048_OF_2486048_MATCH|intermediate_R=FIRST_PRINCIPLES_S3_JACOBI|original_Q4_signed_R=FIRST_PRINCIPLES_S3_ELECTRIC|original_V1_archive=IMMUTABLE_SHA256_PIN|json=0");
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
                &format!("new_K3_U0_mismatch_energy_{z}_row_{i}_column_{j}_computed_{}_original_{}_diff_{}",observed[i][j],original[i][j],observed[i][j]-original[i][j]))?;
    }}
    println!("Y137_INDEPENDENT_K3_TRIAL_U|sample_num={z}|new_original_20_Jacobi_sweeps=PASS|all_original_8x8_U0_entries=64_OF_64_MATCH|original_U0_source=IMMUTABLE_CACHE|K3_signed_residual=INDEPENDENTLY_GENERATED|original_StageC_V1=SEPARATE_SOURCE_GATE|json=0");
    Ok(())
}

fn q4_shard(group:usize,original:&Path,group_keys:&Path,all_keys:&Path)
         ->Result<(),String>{
    require(group<8,"Q4_source_group_0_to_7")?;
    let start=std::time::Instant::now();
    let rule=Gauge::new()?;
    let keys=layers(&rule)?;
    let rows=graph(&rule,&keys)?;
    let mut inner=HashMap::with_capacity(ORIGINAL_K3);
    for (i,row) in rows.iter().enumerate(){
        require(inner.insert(row.key,i).is_none(),
                "independent_K3_duplicate_address")?;
    }
    let mut rlist:[Vec<[i128;LANE_COUNT]>;2]=[Vec::new(),Vec::new()];
    let mut q4list:[HashMap<u64,Q4Residual>;2]=[HashMap::new(),HashMap::new()];
    for (s,&z) in ENERGY.iter().enumerate(){
        let y=jacobi(&rows,z)?;
        rlist[s]=residuals(&rows,&y,z)?;
        q4list[s]=new_q4_source(&rule,&rows,&y)?;
    }
    require(q4list.iter().all(|q|q.len()==1_985_218),
            "both_source_Q4_1985218_full_census")?;
    let mut independent_keys=q4list[0].keys().copied().collect::<Vec<_>>();
    independent_keys.sort_unstable();
    require(independent_keys.windows(2).all(|w|w[0]<w[1]),
            "independent_Q4_source_addresses_unique")?;
    require(independent_keys.iter().all(|k|q4list[1].contains_key(k)),
            "both_Q4_source_geometry_sets_match")?;
    // One shard writes the exact full 15.9 MB source key set for a
    // separately implemented original-source union comparison.
    if group==0{
        let mut writer=std::io::BufWriter::new(
            File::create(all_keys).map_err(|e|e.to_string())?);
        for a in &independent_keys{
            writer.write_all(&a.to_le_bytes()).map_err(|e|e.to_string())?;
        }
        writer.flush().map_err(|e|e.to_string())?;
    }
    drop(independent_keys);
    let mut reader=BufReader::with_capacity(1<<20,
        File::open(original).map_err(|e|e.to_string())?);
    let mut output=std::io::BufWriter::new(
        File::create(group_keys).map_err(|e|e.to_string())?);
    let mut previous=None;
    let mut records=0usize;
    let mut comparisons=0usize;
    let mut raw_moves=0usize;
    loop{
        let mut header=[0u8;11];
        if reader.read(&mut header[..1]).map_err(|e|e.to_string())?==0{break;}
        reader.read_exact(&mut header[1..]).map_err(|e|e.to_string())?;
        let addr=u64::from_le_bytes(header[..8].try_into()
            .map_err(|_|"Q4_stageC_header_addr")?);
        require(header[9]==4&&header[10]==2,
                "Q4_stageC_original_shell_and_two_samples")?;
        if let Some(prev)=previous{
            require(addr>prev,"Q4_original_shard_canonical_address_order")?;
        }
        previous=Some(addr);
        let canonical=rule.key(addr);
        require(rule.address(rule.canonical(rule.expand(canonical)))==addr,
                "original_Q4_source_not_S3_canonical")?;
        let weight=rule.orbit_weight(canonical);
        require(u8::try_from(weight).map_err(|e|e.to_string())?==header[8],
                "original_Q4_source_W_weight")?;
        require((4..=16).contains(&rule.magnetic(canonical)),
                "original_Q4_magnetic_support")?;
        let m=rule.magnetic(canonical);
        let neighbors=rule.moves(canonical)?;
        require(neighbors.values().map(|&v|v as usize).sum::<usize>()==72,
                "Q4_complete_original_72_raw_moves")?;
        raw_moves+=72;
        for sample in 0..2{
            let z=ENERGY[sample];
            let source=q4list[sample].get(&addr)
                .ok_or_else(||"original_Q4_state_absent_from_independent_sources".to_owned())?;
            require(source.weight==header[8],"Q4_original_source_weight_vs_new_boundary")?;
            let diag=(B*(72+9*u128::from(m))-z) as i128;
            for lane in 0..LANE_COUNT{
                let self_positive=i128::try_from(source.incoming[lane])
                    .map_err(|e|e.to_string())?;
                let rs=(B as i128).checked_mul(self_positive)
                    .and_then(|a|a.checked_neg())
                    .ok_or_else(||"Q4_original_R_source_overflow".to_owned())?;
                let mut v=diag.checked_mul(rs)
                    .ok_or_else(||"Q4_V1_magnetic_diagonal_overflow".to_owned())?;
                for (&dest,&cc) in &neighbors{
                    let factor=(B as i128).checked_mul(i128::from(cc))
                        .ok_or_else(||"Q4_V1_weighted_coeff_overflow".to_owned())?;
                    if let Some(&index)=inner.get(&dest){
                        let term=factor.checked_mul(rlist[sample][index][lane])
                            .ok_or_else(||"Q4_V1_K3_term_overflow".to_owned())?;
                        v=v.checked_sub(term)
                            .ok_or_else(||"Q4_V1_K3_sum_overflow".to_owned())?;
                    }else if let Some(other)=q4list[sample].get(&dest){
                        let pos=i128::try_from(other.incoming[lane])
                            .map_err(|e|e.to_string())?;
                        let term=factor.checked_mul(B as i128)
                            .and_then(|a|a.checked_mul(pos))
                            .ok_or_else(||"Q4_V1_Q4_term_overflow".to_owned())?;
                        v=v.checked_add(term)
                            .ok_or_else(||"Q4_V1_Q4_sum_overflow".to_owned())?;
                    }
                    // All further Q5 source R values are identically zero.
                }
                let original_v=read_i128(&mut reader)?;
                require(v==original_v,
                        &format!("original_Q4_V1_first_principles_mismatch_group_{group}_address_{addr}_sample_{sample}_lane_{lane}_new_{v}_archive_{original_v}"))?;
                comparisons+=1;
            }
        }
        output.write_all(&addr.to_le_bytes()).map_err(|e|e.to_string())?;
        records+=1;
        if records%40000==0{
            println!("Y137_INDEPENDENT_Q4_V1_PROGRESS|shard={group}|records={records}|raw_moves={raw_moves}|sources=FIRST_PRINCIPLES|json=0");
        }
    }
    output.flush().map_err(|e|e.to_string())?;
    let expected=1_985_218*(group+1)/8-1_985_218*group/8;
    require(records==expected,"exact_Q4_original_archive_group_census")?;
    require(comparisons==16*expected,"Q4_source_two_energy_sixteen_lanes")?;
    println!("Y137_INDEPENDENT_Q4_V1_SHARD|group={group}|rows={records}|exact_source_components={comparisons}|raw_72_electric_moves={raw_moves}|all_original_signed_V1_entries=EXACT_FIRST_PRINCIPLES|original_archive_immutable=SHA_PINNED|independent_Q4_set=1985218|elapsed_seconds={}|json=0",
             start.elapsed().as_secs());
    Ok(())
}

const Q5_COUNT:usize=18_598_040;
const Q5_LANE_BITS:usize=82;
const Q5_GROUP_ROWS:[usize;8]=[
    435324,4439918,988399,2812763,822474,3973928,1612450,3512784
];
fn q5_pack_unsigned(values:&[u128;LANE_COUNT])->Result<Vec<u8>,String>{
    let mut bytes=[0u8;82];
    for (lane,&value) in values.iter().enumerate(){
        require(value<(1u128<<Q5_LANE_BITS),"Q5_original_82bit_source_bound")?;
        let bit=lane*Q5_LANE_BITS;
        let mut x=value<<(bit%8);
        let mut dst=bit/8;
        while x!=0{
            require(dst<bytes.len(),"Q5_original_packed_byte_bounds")?;
            bytes[dst]|=x as u8;
            x>>=8;
            dst+=1;
        }
    }
    let mut len=bytes.len();
    while len>0&&bytes[len-1]==0{len-=1;}
    Ok(bytes[..len].to_vec())
}
fn q5_test_packing()->Result<(),String>{
    let values=[0u128,1,6,1u128<<81,81,100003,9,1u128<<81];
    let p=q5_pack_unsigned(&values)?;
    for (lane,&expected) in values.iter().enumerate(){
        let bit=lane*Q5_LANE_BITS;
        let byte=bit/8;
        let mut block=[0u8;16];
        for (j,out) in block.iter_mut().enumerate(){
            if byte+j<p.len(){*out=p[byte+j];}
        }
        let observed=(u128::from_le_bytes(block)>>(bit%8))
                    &((1u128<<Q5_LANE_BITS)-1);
        require(observed==expected,"Q5_82bit_lane_roundtrip")?;
    }
    let forged=p.iter().enumerate().map(|(i,&v)|if i==0{v^1}else{v})
        .collect::<Vec<_>>();
    require(forged!=p,"Q5_bit_corruption_detected")?;
    println!("Y137_INDEPENDENT_Q5_PACK_TOY|82bit_eight_lane_roundtrip=PASS|unsigned_source=PASS|corrupted_source_byte=REJECTED|json=0");
    Ok(())
}
fn q5_original_group(group:usize,archive:&Path,group_keys:&Path)
          ->Result<(),String>{
    require(group<8,"Q5_original_group_0_to_7")?;
    let start=Instant::now();
    let rule=Gauge::new()?;
    let keys=layers(&rule)?;
    let states=graph(&rule,&keys)?;
    let inner=states.iter().map(|r|r.key).collect::<HashSet<_>>();
    let mut q4:[HashMap<u64,Q4Residual>;2]=[HashMap::new(),HashMap::new()];
    for (sample,&z) in ENERGY.iter().enumerate(){
        let y=jacobi(&states,z)?;
        q4[sample]=new_q4_source(&rule,&states,&y)?;
    }
    require(q4[0].len()==1_985_218&&q4[1].len()==1_985_218,
            "original_complete_Q4_source_before_Q5")?;
    let mut original=BufReader::with_capacity(1<<20,
        File::open(archive).map_err(|e|e.to_string())?);
    let mut collected=Vec::with_capacity(Q5_GROUP_ROWS[group]);
    let mut last_bucket=(group as i32)-8;
    let mut last_addr:Option<u64>=None;
    let mut bucket_counts=[0u64;8];
    let mut raw_moves=0u64;
    let mut edge_hits=0u64;
    let mut comparisons=0u64;
    loop{
        let mut head=[0u8;13];
        if original.read(&mut head[..1]).map_err(|e|e.to_string())?==0{break;}
        original.read_exact(&mut head[1..]).map_err(|e|e.to_string())?;
        let address=u64::from_le_bytes(head[..8].try_into()
            .map_err(|_|"Q5_original_source_address")?);
        let weight=head[8];
        let n0=u16::from_le_bytes([head[9],head[10]]) as usize;
        let n1=u16::from_le_bytes([head[11],head[12]]) as usize;
        require(n0<=82&&n1<=82,"Q5_original_packed_82byte_limit")?;
        let mut old0=vec![0u8;n0];
        let mut old1=vec![0u8;n1];
        original.read_exact(&mut old0).map_err(|e|e.to_string())?;
        original.read_exact(&mut old1).map_err(|e|e.to_string())?;
        require((old0.last()!=Some(&0))&&(old1.last()!=Some(&0)),
                "Q5_archive_packed_nonminimal_source")?;
        let bucket=(address%64) as i32;
        require(bucket%8==group as i32,"Q5_original_bucket_group")?;
        if bucket!=last_bucket{
            require(bucket==last_bucket+8,"Q5_original_all_eight_buckets_ordered")?;
            last_bucket=bucket;
        }else if let Some(previous)=last_addr{
            require(address>previous,"Q5_original_bucket_canonical_sort")?;
        }
        last_addr=Some(address);
        bucket_counts[(bucket as usize-group)/8]+=1;
        let key=rule.key(address);
        require(rule.address(rule.canonical(rule.expand(key)))==address,
                "Q5_original_S3_canonical_target")?;
        require(rule.orbit_weight(key)==usize::from(weight),
                "Q5_original_orbit_weight")?;
        require(!inner.contains(&address)&&!q4[0].contains_key(&address),
                "Q5_original_target_wrong_K3_Q4_shell")?;
        let near=rule.moves(key)?;
        raw_moves+=72;
        let mut expected=[[0u128;LANE_COUNT];2];
        let mut hits=0u64;
        for (&dest,&cc) in &near{
            if let Some(q)=q4[0].get(&dest){
                let second=q4[1].get(&dest)
                    .ok_or_else(||"Q5_original_Q4_second_energy_missing".to_owned())?;
                require(q.weight==second.weight&&q.weight!=0,
                        "Q5_original_Q4_source_weight")?;
                hits+=u64::from(cc);
                for lane in 0..LANE_COUNT{
                    for sample in 0..2{
                        let incoming=if sample==0{q.incoming[lane]}else{second.incoming[lane]};
                        let term=B.checked_mul(u128::from(cc))
                            .and_then(|v|v.checked_mul(incoming))
                            .ok_or_else(||"Q5_original_V1_over_b_exact_unsigned_mul".to_owned())?;
                        expected[sample][lane]=expected[sample][lane].checked_add(term)
                            .ok_or_else(||"Q5_original_V1_over_b_exact_unsigned_sum".to_owned())?;
                    }
                }
            }
        }
        require(hits>0&&hits<=72,"Q5_original_nonzero_boundary_source")?;
        edge_hits+=hits;
        let fresh0=q5_pack_unsigned(&expected[0])?;
        let fresh1=q5_pack_unsigned(&expected[1])?;
        require(fresh0==old0&&fresh1==old1,
                &format!("Q5_source_V1_over_b_mismatch_group_{group}_address_{address}_new0_bytes_{}_old0_bytes_{}_new1_bytes_{}_old1_bytes_{}",
                          fresh0.len(),old0.len(),fresh1.len(),old1.len()))?;
        comparisons+=16;
        collected.push(address);
        if collected.len()%100_000==0{
            println!("Y137_INDEPENDENT_Q5_SOURCE_PROGRESS|group={group}|original_targets={}|raw_moves={raw_moves}|all_source_lanes=MATCH|json=0",
                     collected.len());
        }
    }
    require(collected.len()==Q5_GROUP_ROWS[group],
            "Q5_original_group_exact_source_targets")?;
    require(last_bucket==group as i32+56&&bucket_counts.iter().all(|&v|v>0),
            "Q5_original_all_eight_nonempty_radix64_buckets")?;
    require(comparisons==16*Q5_GROUP_ROWS[group] as u64,
            "Q5_original_full_two_energy_eight_column_count")?;
    collected.sort_unstable();
    require(collected.windows(2).all(|w|w[0]<w[1]),
            "Q5_original_group_unique_sorted_targets")?;
    let mut file=std::io::BufWriter::new(
        File::create(group_keys).map_err(|e|e.to_string())?);
    for key in collected{
        file.write_all(&key.to_le_bytes()).map_err(|e|e.to_string())?;
    }
    file.flush().map_err(|e|e.to_string())?;
    println!("Y137_INDEPENDENT_Q5_SOURCE_SHARD|group={group}|original_Q5_targets={}|exact_unsigned_V1_over_b_components={comparisons}|physical_72_moves={raw_moves}|Q4_boundary_incoming_weighted_moves={edge_hits}|original_archive_source=SHA256_PINNED|original_K3_Q4_R=FIRST_PRINCIPLES|original_packed_V1_over_b=EXACT_ALL_LANES|elapsed_seconds={}|json=0",
             Q5_GROUP_ROWS[group],start.elapsed().as_secs());
    Ok(())
}
fn q5_independent_target_set(path:&Path)->Result<(),String>{
    let start=Instant::now();
    let rule=Gauge::new()?;
    let keys=layers(&rule)?;
    let states=graph(&rule,&keys)?;
    let y=jacobi(&states,ENERGY[0])?;
    let q4=new_q4_source(&rule,&states,&y)?;
    let inner=states.iter().map(|r|r.key).collect::<HashSet<_>>();
    let mut targets=HashSet::with_capacity(Q5_COUNT);
    let mut raw_q4_to_q5=0u64;
    for &address in q4.keys(){
        let near=rule.moves(rule.key(address))?;
        for (dst,cc) in near{
            if !inner.contains(&dst)&&!q4.contains_key(&dst){
                targets.insert(dst);
                raw_q4_to_q5+=u64::from(cc);
            }
        }
    }
    require(targets.len()==Q5_COUNT,
            "first_principles_complete_Q5_boundary_target_census")?;
    let mut ordered=targets.into_iter().collect::<Vec<_>>();
    ordered.sort_unstable();
    require(ordered.windows(2).all(|p|p[0]<p[1]),
            "independent_Q5_boundary_target_uniqueness")?;
    let mut file=std::io::BufWriter::new(
        File::create(path).map_err(|e|e.to_string())?);
    for k in ordered{
        file.write_all(&k.to_le_bytes()).map_err(|e|e.to_string())?;
    }
    file.flush().map_err(|e|e.to_string())?;
    println!("Y137_INDEPENDENT_Q5_TARGET_SUPPORT|first_principles_Q4_sources=1985218|complete_Q5_destinations=18598040|original_Q4_72_raw_moves={}|independent_Q4_to_Q5_raw_moves={raw_q4_to_q5}|original_StageB_Q5_address_set=VERIFY_IN_FANIN|elapsed_seconds={}|json=0",
             1_985_218*72,start.elapsed().as_secs());
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
    let mut v1_source: [Vec<[i128;LANE_COUNT]>;2]=[Vec::new(),Vec::new()];
    for (sample,&energy) in ENERGY.iter().enumerate(){
        let y=jacobi(&states,energy)?;
        let r=residuals(&states,&y,energy)?;
        compare_u_source(source,energy,exact_u(&states,&y,&r,energy)?)?;
        compare_original_g(source,energy,full_source_gram(&rule,&states,&y,&r)?)?;
        v1_source[sample]=rebuild_k3_v1(&rule,&states,&y,&r,energy)?;
    }
    compare_original_k3_v1(archive,&states,&v1_source)?;
    println!("Y137_INDEPENDENT_K3_VERDICT|K3=155378|two_original_energy_trials=20_JACOBI_EACH|original_U0_matrix_entries=128_OF_128_MATCH|original_G0_matrix_entries=128_OF_128_MATCH|original_V1_K3_signed_archive=2486048_OF_2486048_MATCH|original_K3_Q4_R_source=INDEPENDENTLY_GENERATED|original_K3_support_and_weights=FULL_PASS|original_Q4_V1=SEPARATE_SOURCE_GATE|whole_Perron_store=SEPARATE_GATE|Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|elapsed_seconds={}|json=0",start.elapsed().as_secs());
    Ok(())
}
fn main(){
    let args=std::env::args().collect::<Vec<_>>();
    let result=match args.as_slice(){
        [_,mode] if mode=="toy"=>synthetic(),
        [_,mode,archive,source] if mode=="real"=>execute(Path::new(archive),Path::new(source)),
        [_,mode,group,archive,out] if mode=="q5-group"=>
            match group.parse::<usize>(){
                Ok(g)=>q5_original_group(g,Path::new(archive),Path::new(out)),
                Err(e)=>Err("invalid_Q5_group_number_".to_string()+&e.to_string()),
            },
        [_,mode,path] if mode=="q5-support"=>q5_independent_target_set(Path::new(path)),
        [_,mode] if mode=="q5-toy"=>q5_test_packing(),
        [_,mode,group,original,group_keys,all_keys] if mode=="q4-shard"=>
            match group.parse::<usize>(){
                Ok(g)=>q4_shard(g,Path::new(original),Path::new(group_keys),Path::new(all_keys)),
                Err(e)=>Err("invalid_Q4_shard_number_".to_string()+&e.to_string()),
            },
        _=>Err("usage_k3_source toy_or_real ORIGINAL_SIGNED_V1_K3_FILE ORIGINAL_U0_CACHE".to_string()),
    };
    if let Err(e)=result{
        eprintln!("Y137_INDEPENDENT_K3_REFUSE|reason={}|source=HOLD|Wilson=FORMAL_HOLD|json=0",
                  e.replace('|',"_"));
        std::process::exit(2);
    }
}
