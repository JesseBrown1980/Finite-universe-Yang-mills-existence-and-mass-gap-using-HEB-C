//! #137 genuinely new full 20,738,636-state signed μ3 source/operator reconstruction.
//! Reads immutable original signed K3/Q4 physical V1 and Q5 packed V1/b inputs;
//! independently regenerates all 72 S3 electric moves for every physical source.
//! Computes both full 8x8 signed moments with exact 320-bit signed arithmetic,
//! using the symmetric Dirichlet-row identity; imports NO historical Q5 B5 matrix.
//! Source values are immutable input premises and independently sampled elsewhere.
//! 8 disjoint address-mod-8 shards x 2 original frozen energy samples.
use std::collections::{HashMap,BTreeMap};
use std::fs::File;
use std::io::{BufReader,Read};
use std::path::Path;
use std::time::Instant;

const PERM:[[u8;3];6]=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
const N:usize=20_738_636;
const K3:usize=155_378;
const Q4:usize=1_985_218;
const Q5:usize=18_598_040;
const Q5_BY_GROUP:[usize;8]=[435324,4439918,988399,2812763,822474,3973928,1612450,3512784];
const Q5_BYTES:[u64;8]=[72717336,750840749,166069410,476041564,137545818,672121828,270439868,595123535];
const ENERGIES:[i64;2]=[69_909_875_505,69_949_729_820];
const B:i64=1_000_000_000;
const MAX_ADDR:u64=13_060_694_016;
const COLS:usize=8;
const U82:u128=(1u128<<82)-1;

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

#[derive(Clone,Copy)]
struct State{address:u64,weight:u8,shell:u8,v:[i128;COLS]}
struct Sources{list:Vec<State>,idx:HashMap<u64,usize>}
impl Sources{
    fn new()->Self{
        Self{list:Vec::with_capacity(N),idx:HashMap::with_capacity(N)}
    }
    fn push(&mut self,state:State)->Result<(),String>{
        require(state.address<MAX_ADDR &&
                (state.weight==1||state.weight==2||state.weight==3||state.weight==6),
                "canonical_address_or_weight_domain")?;
        let pos=self.list.len();
        require(self.idx.insert(state.address,pos).is_none(),
                "original_K3_Q4_Q5_source_support_collision")?;
        self.list.push(state);
        Ok(())
    }
}
fn take_exact(reader:&mut impl Read,n:usize)->Result<Vec<u8>,String>{
    let mut out=vec![0;n];
    reader.read_exact(&mut out).map_err(|e|format!("short_source_file:{e}"))?;
    Ok(out)
}
fn bytes_u64(s:&[u8])->Result<u64,String>{
    let x: [u8;8] = s.try_into().map_err(|_|"bad_u64_buffer")?;
    Ok(u64::from_le_bytes(x))
}
fn read_signed(path:&Path,shell:u8,sample:usize,all:&mut Sources)->Result<usize,String>{
    let mut reader=BufReader::with_capacity(1<<20,File::open(path).map_err(|e|e.to_string())?);
    let mut count=0usize;
    let mut last=None;
    loop{
        let mut header=[0u8;11];
        if reader.read(&mut header[..1]).map_err(|e|e.to_string())?==0{break;}
        reader.read_exact(&mut header[1..]).map_err(|e|e.to_string())?;
        let address=bytes_u64(&header[..8])?;
        require(header[9]==shell&&header[10]==2,"signed_source_shell_and_sample_count")?;
        if let Some(p)=last{require(address>p,"signed_source_canonical_order")?;}
        last=Some(address);
        let mut active=[0i128;COLS];
        for e in 0..2{
            for val in &mut active{
                let b=take_exact(&mut reader,1)?[0];
                let n=(b&127) as usize;
                let neg=(b&128)!=0;
                require(n<=24&&(!neg||n>0),"physical_signed_lane_header")?;
                let raw=take_exact(&mut reader,n)?;
                require(n==0||raw[n-1]!=0,"signed_nonminimal_magnitude")?;
                if e==sample{
                    require(n<=16,"signed_source_i128_width")?;
                    let mut words=[0u8;16];
                    words[..n].copy_from_slice(&raw);
                    let magnitude=u128::from_le_bytes(words);
                    require(magnitude<(1u128<<112),"signed_V1_source_magnitude_112bits")?;
                    *val=if neg{-(magnitude as i128)}else{magnitude as i128};
                }
            }
        }
        all.push(State{address,weight:header[8],shell,v:active})?;
        count+=1;
    }
    Ok(count)
}
fn unpack82(input:&[u8])->Result<[i128;COLS],String>{
    require(input.len()<=82 && (input.is_empty()||*input.last().unwrap_or(&0)!=0),
            "canonical_Q5_packed_sample")?;
    let mut padded=[0u8;98];
    padded[..input.len()].copy_from_slice(input);
    let mut out=[0i128;COLS];
    for (lane,x) in out.iter_mut().enumerate(){
        let start=82*lane;
        let byte=start/8;
        let shift=start%8;
        let block: [u8;16] = padded[byte..byte+16].try_into()
            .map_err(|_|"Q5_lane_window")?;
        let number=(u128::from_le_bytes(block)>>shift)&U82;
        let physical=number*B as u128;
        require(physical<(1u128<<112),"Q5_V1_physical_112bit_bound")?;
        *x=physical as i128;
    }
    Ok(out)
}
fn read_q5(path:&Path,group:usize,sample:usize,all:&mut Sources)
    ->Result<(usize,u64),String>
{
    let mut reader=BufReader::with_capacity(1<<20,File::open(path).map_err(|e|e.to_string())?);
    let mut count=0usize;
    let mut size=0u64;
    let mut bucket_index=0usize;
    let mut last=None;
    loop{
        let mut header=[0u8;13];
        if reader.read(&mut header[..1]).map_err(|e|e.to_string())?==0{break;}
        reader.read_exact(&mut header[1..]).map_err(|e|e.to_string())?;
        let address=bytes_u64(&header[..8])?;
        let n0=u16::from_le_bytes([header[9],header[10]]) as usize;
        let n1=u16::from_le_bytes([header[11],header[12]]) as usize;
        require(n0<=82 && n1<=82,"physical_Q5_packed_sample_size")?;
        let payload=take_exact(&mut reader,n0+n1)?;
        let bucket=address%64;
        require(bucket%8==group as u64,"Q5_incorrect_group")?;
        if bucket!= (group+8*bucket_index) as u64{
            require(bucket_index<7 && bucket==(group+8*(bucket_index+1)) as u64,
                    "Q5_bucket_canonical_sequence")?;
            bucket_index+=1;last=None;
        }
        if let Some(prior)=last {require(address>prior,"Q5_canonical_bucket_order")?;}
        last=Some(address);
        let selected=if sample==0{&payload[..n0]}else{&payload[n0..]};
        let amplitude=unpack82(selected)?;
        all.push(State{address,weight:header[8],shell:5,v:amplitude})?;
        count+=1;size+=(13+n0+n1) as u64;
    }
    require(bucket_index==7 && count==Q5_BY_GROUP[group]&&size==Q5_BYTES[group],
            "Q5_complete_8_bucket_census")?;
    Ok((count,size))
}
fn load_all(signed:&Path,q5:&Path,sample:usize)->Result<Sources,String>{
    let started=Instant::now();
    let mut all=Sources::new();
    let k3=read_signed(&signed.join("SIGNED-K3.v1"),3,sample,&mut all)?;
    require(k3==K3,"full_physical_K3_count")?;
    for g in 0..8{
        let q4_file=signed.join(format!("SIGNED-Q4-{g}.v1"));
        let n=read_signed(&q4_file,4,sample,&mut all)?;
        require(n==Q4*(g+1)/8-Q4*g/8,"signed_Q4_original_group_count")?;
    }
    require(all.list.len()==K3+Q4,"original_K3_Q4_signed_source_sum")?;
    for g in 0..8{
        let (_,bytes)=read_q5(&q5.join(format!("GROUP-{g}.v1")),g,sample,&mut all)?;
        require(bytes==Q5_BYTES[g],"original_Q5_group_source_bytes")?;
    }
    require(all.list.len()==N && all.idx.len()==N && K3+Q4+Q5==N,
            "full_independent_20M_original_source_support")?;
    println!("Y137_INDEPENDENT_DIRICHLET_SOURCE|sample_num={}|K3={K3}|Q4={Q4}|Q5={Q5}|unique_source_states={}|source_kind=ORIGINAL_IMMUTABLE_PREMISES|historical_B5_principal_import=NONE|load_seconds={}|json=0",
             ENERGIES[sample],all.idx.len(),started.elapsed().as_secs());
    Ok(all)
}
type Mat=[[Int320;COLS];COLS];
fn blank()->Mat{[[Int320::default();COLS];COLS]}
fn encode(m:&Mat)->String{
    let mut rows=Vec::new();
    for row in m{rows.push(row.iter().map(Int320::decimal).collect::<Vec<_>>().join(","));}
    rows.join(";")
}
fn evaluate(sources:&Sources,sample:usize,shard:usize)->Result<(),String>{
    let started=Instant::now();
    let rule=Gauge::new()?;
    let mut result=blank();
    let mut count=0u64;
    let mut moves=0u64;
    let mut census=[[0u64;4];3];
    let mut selfloops=0u64;
    let mut challenge=0u64;
    for state in &sources.list{
        if state.address%8!=shard as u64{continue;}
        let key=rule.key(state.address);
        require(rule.address(rule.canonical(rule.expand(key)))==state.address,
                "full_original_state_independent_S3_canonicality")?;
        require(rule.orbit_weight(key) as u8==state.weight,
                "full_original_state_independent_S3_weight")?;
        let magnetic=rule.magnetic(key);
        require((3..=36).contains(&magnetic),"all_sources_nonflat_magnetic_range")?;
        let row=rule.moves(key)?;
        let w=i64::from(state.weight);
        let mut neighbor=[0i128;COLS];
        let shell=(state.shell-3) as usize;
        let mut local_degree=0u64;
        for (&address,&multiplicity) in &row{
            let c=u64::from(multiplicity);
            local_degree+=c;
            if address==state.address{selfloops+=c;}
            if let Some(&k)=sources.idx.get(&address){
                let other=&sources.list[k];
                census[shell][(other.shell-3) as usize]+=c;
                for (lane,acc) in neighbor.iter_mut().enumerate(){
                    let term=other.v[lane].checked_mul(i128::from(multiplicity))
                        .ok_or_else(||"physical_neighbor_mul_i128_overflow".to_string())?;
                    *acc=acc.checked_add(term).ok_or_else(||"neighbor_i128_overflow".to_string())?;
                }
                // Independently confirm weighted reciprocity for sparse
                // rows in all shells; full cross-pair audit is separate.
                if count%8192==0 && address!=state.address{
                    let oth_key=rule.key(address);
                    let reverse=*rule.moves(oth_key)?.get(&state.address).unwrap_or(&0);
                    require(reverse>0 &&
                            u64::from(state.weight)*c==
                            u64::from(other.weight)*u64::from(reverse),
                            "sampled_full_state_weighted_reverse_edge")?;
                    challenge+=1;
                }
            }else{
                census[shell][3]+=c;
            }
        }
        require(local_degree==72,"full_state_72_move_degree")?;
        moves+=local_degree;
        count+=1;
        let z=ENERGIES[sample];
        let diagonal=6*w*(B*(72+9*i64::from(magnetic))-z);
        let mixed=-3*w*B;
        for a in 0..COLS{
            for b in a..COLS{
                let d=Int320::multiply(state.v[a],state.v[b],diagonal)?;
                result[a][b].add(&d)?;
                let left=Int320::multiply(state.v[a],neighbor[b],mixed)?;
                result[a][b].add(&left)?;
                let right=Int320::multiply(neighbor[a],state.v[b],mixed)?;
                result[a][b].add(&right)?;
            }
        }
    }
    for i in 0..COLS{for j in 0..i{result[i][j]=result[j][i];}}
    require(count>0 && moves==72*count,"disjoint_original_full_state_shard")?;
    let flat:Vec<String>=census.iter().flat_map(|v|v.iter().map(u64::to_string)).collect();
    println!("Y137_INDEPENDENT_FULL_DIRICHLET_SHARD|sample_num={}|shard={shard}|source_total={N}|K3={K3}|Q4={Q4}|Q5={Q5}|actual_rows={count}|all_raw_moves={moves}|block_census={}|selfloops={selfloops}|sampled_weighted_reverse_checks={challenge}|original_source_SHA256=WORKFLOW_PRECHECK|Q5_principal=REBUILT_NOT_IMPORTED|full_Dirichlet_identity=SYMMETRIC_REARRANGEMENT|matrix_8x8={}|elapsed_seconds={}|original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|json=0",
        ENERGIES[sample],flat.join(","),encode(&result),started.elapsed().as_secs());
    Ok(())
}
fn toy_dirichlet()->Result<(),String>{
    // Two distinct exact original-energy signed 8x8 matrix calculations:
    // full symmetric row regrouping vs supported-edge Dirichlet squares.
    let w=[1i64,2,3];
    let mag=[5i64,7,9];
    let edges=[[0i64,2,3],[1,0,3],[1,2,0]];
    let exterior=[67i64,68,69];
    let v=[
        [3i128,-5,7,-11,13,-17,19,-23],
        [-29,31,-37,41,-43,47,-53,59],
        [61,-67,71,-73,79,-83,89,-97],
    ];
    for &z in &ENERGIES {
        let mut symmetric=blank();
        let mut dirichlet=blank();
        for i in 0..3 {
            require(exterior[i]+edges[i].iter().sum::<i64>()==72,
                    "source_free_full_72_raw_moves")?;
            let mut near=[0i128;COLS];
            for (j,other) in v.iter().enumerate(){
                for k in 0..COLS {near[k]+=i128::from(edges[i][j])*other[k];}
                require(w[i]*edges[i][j]==w[j]*edges[j][i],
                        "source_free_weighted_pair_reciprocity")?;
            }
            let d=6*w[i]*(B*(72+9*mag[i])-z);
            let cross=-3*w[i]*B;
            let effective=6*w[i]*(B*(9*mag[i]+exterior[i])-z);
            for a in 0..COLS {for b in a..COLS{
                for (x,y,c) in [
                    (v[i][a],v[i][b],d),
                    (v[i][a],near[b],cross),
                    (near[a],v[i][b],cross)
                ]{
                    symmetric[a][b].add(&Int320::multiply(x,y,c)?)?;
                }
                dirichlet[a][b].add(&Int320::multiply(v[i][a],v[i][b],effective)?)?;
            }}
        }
        for i in 0..3 {for j in (i+1)..3{
            let coef=6*w[i]*B*edges[i][j];
            for a in 0..COLS {for b in a..COLS{
                dirichlet[a][b].add(&Int320::multiply(
                    v[i][a]-v[j][a],v[i][b]-v[j][b],coef)?)?;
            }}
        }}
        for a in 0..COLS {for b in 0..a{
            symmetric[a][b]=symmetric[b][a];
            dirichlet[a][b]=dirichlet[b][a];
        }}
        require(symmetric==dirichlet,
                "independent_8x8_symmetric_row_vs_Dirichlet_difference_identity")?;
        let mut corrupted=dirichlet;
        corrupted[0][0].add(&Int320::multiply(v[0][0],v[0][0],-6*w[0]*B)?)?;
        require(corrupted!=symmetric,
                "missing_original_support_zero_boundary_refused")?;
    }
    Ok(())
}

fn toy()->Result<(),String>{
    let rule=Gauge::new()?;
    let zero=[0;13];
    require(rule.orbit_weight(zero)==1 && rule.magnetic(zero)==0,
            "S3_identity_weight_and_field")?;
    require(rule.moves(zero)?.values().map(|&x|u64::from(x)).sum::<u64>()==72,
            "S3_independent_72_moves")?;
    let a=(1i128<<108)+123_456;
    let b=-((1i128<<107)+654_321);
    let x=Int320::multiply(a,b,36*B)?;
    let y=Int320::multiply(b,a,-36*B)?;
    let mut z=x;z.add(&y)?;
    require(z==Int320::default(),"exact_signed_320_cancellation")?;
    let v=Int320::multiply((1i128<<110)+1,(1i128<<109)+1,1_000_000_000)?;
    require(v.decimal()=="842498333348457493583344221469365405662482713764753588970611277825000000000",
            "exact_320_integer_golden_product")?;
    let lane=1u128<<81;
    let mut packed=vec![0u8;11];
    let u=lane;
    packed[..11].copy_from_slice(&u.to_le_bytes()[..11]);
    let decoded=unpack82(&packed)?;
    require(decoded[0]==(lane*B as u128) as i128 &&
            decoded[1..].iter().all(|&x|x==0),
            "original_Q5_82bit_packed_lanes")?;
    require(K3+Q4+Q5==N,"frozen_20M_threeblock_support")?;
    toy_dirichlet()?;
    println!("Y137_INDEPENDENT_FULL_DIRICHLET_TOY|S3_gauge_72moves=PASS|original_threeblock_support=20738636|signed_320_integer_golden=PASS|Q5_physical_82bit_packed=PASS|two_8x8_Dirichlet_toy_matrices=128_ENTRIES_PASS|full_original_third_moment=NOT_RUN|no_B5_precomputed_principal=PASS|json=0");
    Ok(())
}
fn main(){
    let args:Vec<String>=std::env::args().collect();
    let result=match args.as_slice(){
        [_,cmd] if cmd=="toy"=>toy(),
        [_,cmd,shard,signed,q5] if cmd=="real-both"=> {
            let g=shard.parse::<usize>().map_err(|e|e.to_string());
            match g{
                Ok(g) if g<8=>{
                    let mut outcome=Ok(());
                    for i in 0..2{
                        outcome=load_all(Path::new(signed),Path::new(q5),i)
                            .and_then(|source|evaluate(&source,i,g));
                        if outcome.is_err(){break;}
                    }
                    outcome
                },
                _=>Err("eight_disjoint_original_full_source_shards".into())
            }
        },
        [_,cmd,sample,shard,signed,q5] if cmd=="real"=>{
            let i=sample.parse::<usize>().map_err(|e|e.to_string());
            let g=shard.parse::<usize>().map_err(|e|e.to_string());
            match (i,g){
                (Ok(i),Ok(g)) if i<2 && g<8=>
                    load_all(Path::new(signed),Path::new(q5),i)
                        .and_then(|source|evaluate(&source,i,g)),
                _=>Err("two_original_sample_or_eight_shard_range".into()),
            }
        }
        _=>Err("usage: full_mu3 toy | real-both SHARD_0_7 SIGNED_DIR Q5_DIR | real SAMPLE SHARD SIGNED_DIR Q5_DIR".into()),
    };
    if let Err(e)=result{
        eprintln!("Y137_INDEPENDENT_FULL_DIRICHLET_HOLD|reason={}|full_mu3=OPEN|first_Wilson=FORMAL_HOLD|json=0",e.replace('|',"_"));
        std::process::exit(2);
    }
}
