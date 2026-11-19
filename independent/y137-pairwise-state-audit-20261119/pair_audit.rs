//! #137 independent pairwise physical-state audit on all 256 immutable cross-block graphs.
//! Exactly 279,034,296 original directed records = 139,517,148 pairs.
//! Separate S3 generator challenges sampled physical endpoints: not the original B4 producer.
//! All arithmetic exact; no unsafe, float, external crates, or hidden approvals.
use std::fs;
use std::path::Path;
use std::time::Instant;
use std::collections::BTreeMap;

const PERMS:[[u8;3];6]=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
const PARTS:usize=256;
const B:u64=6u64.pow(13);
const EXPECTED_PAIRS:u64=139_517_148;
const EXPECTED_FLUX:u64=837_222_984;
const EXPECTED_DIRECTED:u64=279_034_296;
const FULL_CHALLENGE_PER_PART:usize=16;
fn check(ok:bool,why:&str)->Result<(),String>{if ok{Ok(())}else{Err(why.into())}}

fn perm_index(p:[u8;3])->Result<u8,String>{
    PERMS.iter().position(|&x|x==p).map(|n|n as u8)
      .ok_or_else(||"invalid_s3_permutation".into())
}
fn xy(x:usize,y:usize)->usize {(x%3)*4+(y%4)}
#[derive(Clone)]
struct S3 {
    mul:[[u8;6];6], inv:[u8;6], trans:[u8;3],
    keep:[usize;13], tree:Vec<(usize,usize,usize)>,
}
impl S3 {
    fn new()->Result<Self,String>{
        let mut mul=[[0;6];6];
        let mut inv=[0;6];
        let mut t=Vec::new();
        for (i,p) in PERMS.iter().enumerate(){
            for (j,q) in PERMS.iter().enumerate(){
                mul[i][j]=perm_index([p[q[0] as usize],p[q[1] as usize],p[q[2] as usize]])?;
            }
            let mut reverse=[0;3];
            for (a,&b) in p.iter().enumerate(){reverse[b as usize]=a as u8;}
            inv[i]=perm_index(reverse)?;
        }
        for i in 1..6{if mul[i][i]==0{t.push(i as u8);}}
        check(t.len()==3,"exact_s3_transpositions")?;
        let mut tree=Vec::new();
        for y in 0..3{tree.push((xy(0,y),xy(0,y+1),12+xy(0,y)));}
        for y in 0..4{for x in 0..2{tree.push((xy(x,y),xy(x+1,y),xy(x,y)));}}
        check(tree.len()==11,"exact_tree_cardinality")?;
        let mut retained=Vec::new();
        for i in 0..24{
            if !tree.iter().any(|&(_,_,edge)|edge==i){retained.push(i);}
        }
        check(retained.len()==13,"exact_kept_cardinality")?;
        let mut keep=[0;13];keep.copy_from_slice(&retained);
        Ok(Self{mul,inv,trans:[t[0],t[1],t[2]],keep,tree})
    }
    fn compose(&self,a:u8,b:u8)->u8{self.mul[a as usize][b as usize]}
    fn decode(&self,mut addr:u64)->[u8;13]{
        let mut links=[0;13];
        for v in &mut links{*v=(addr%6) as u8;addr/=6;}
        links
    }
    fn address(&self,key:[u8;13])->u64{
        key.iter().rev().fold(0u64,|v,&x|v*6+u64::from(x))
    }
    fn weight(&self,key:[u8;13])->usize{
        let mut seen=Vec::new();
        for a in 0..6u8{
            let mut row=[0;13];
            for (j,&v) in key.iter().enumerate(){
                row[j]=self.compose(self.compose(a,v),self.inv[a as usize]);
            }
            if !seen.contains(&row){seen.push(row);}
        }
        seen.len()
    }
    fn canonical(&self,full:[u8;24])->[u8;13]{
        let mut gauge=[0;12];
        for &(from,to,edge) in &self.tree{
            gauge[to]=self.compose(gauge[from],full[edge]);
        }
        let mut reduced=[0;13];
        for (i,&edge) in self.keep.iter().enumerate(){
            let from=edge%12;
            let x=from/4;let y=from%4;
            let target=if edge<12{xy(x+1,y)}else{xy(x,y+1)};
            reduced[i]=self.compose(self.compose(gauge[from],full[edge]),
                self.inv[gauge[target] as usize]);
        }
        let mut best=reduced;
        for a in 1..6u8{
            let mut conjugated=[0;13];
            for (j,&v) in reduced.iter().enumerate(){
                conjugated[j]=self.compose(self.compose(a,v),self.inv[a as usize]);
            }
            if conjugated<best{best=conjugated;}
        }
        best
    }
    fn expand(&self,key:[u8;13])->[u8;24]{
        let mut full=[0;24];
        for (i,&edge) in self.keep.iter().enumerate(){full[edge]=key[i];}
        full
    }
    fn row(&self,key:[u8;13])->Result<BTreeMap<u64,u32>,String>{
        let mut full=self.expand(key);
        let mut result=BTreeMap::new();
        for edge in 0..24{
            let old=full[edge];
            for &step in &self.trans{
                full[edge]=self.compose(step,old);
                let dest=self.address(self.canonical(full));
                *result.entry(dest).or_insert(0)+=1;
            }
            full[edge]=old;
        }
        check(result.values().map(|&n|u64::from(n)).sum::<u64>()==72,
              "independent_s3_total_72_raw_moves")?;
        Ok(result)
    }
    fn magnetic(&self,key:[u8;13])->u32{
        let links=self.expand(key);
        let mut mag=0;
        for x in 0..3 {for y in 0..4 {
            let i=xy(x,y);
            let c=self.compose(links[i],links[12+xy(x+1,y)]);
            let c=self.compose(c,self.inv[links[xy(x,y+1)] as usize]);
            let c=self.compose(c,self.inv[links[12+i] as usize]);
            let p=PERMS[c as usize];
            let fixed=p.iter().enumerate().filter(|&(j,&v)|j==v as usize).count();
            mag+=3-fixed as u32;
        }}
        mag
    }
}
#[derive(Clone,Copy)]
struct Edge{lo:u64,hi:u64,signed:i16}
fn part(lo:u64,hi:u64)->usize{
    let mut h=lo.wrapping_mul(11_400_714_819_323_198_485)
        ^hi.wrapping_mul(14_029_467_366_897_019_727);
    h^=h>>33;
    h=h.wrapping_mul(13_797_801_002_366_949_169);
    ((h^(h>>29))&255) as usize
}
fn fnv(h:&mut u64,v:u64){
    for b in v.to_le_bytes(){
        *h^=u64::from(b);
        *h=h.wrapping_mul(1_099_511_628_211);
    }
}
#[derive(Clone,Copy)]
struct Expected{directed:u64,pairs:u64,flux:u64,fnv:u64}
fn field<'a>(s:&'a str,name:&str)->Result<&'a str,String>{
    s.split('|').filter_map(|k|k.strip_prefix(name).and_then(|q|q.strip_prefix('=')))
      .next().ok_or_else(||format!("missing_{name}"))
}
fn graph_expectations(path:&Path)->Result<Vec<Expected>,String>{
    let text=fs::read_to_string(path).map_err(|e|e.to_string())?;
    let mut out=Vec::new();
    for line in text.lines().filter(|s|s.starts_with("Y137_C_GRAPH_PART|")){
        let n=field(line,"part")?.parse::<usize>().map_err(|e|e.to_string())?;
        check(n==out.len()&&n<PARTS,"original_256_partition_sequence")?;
        check(field(line,"exact_balance")?=="PASS","original_pair_balance_label")?;
        let directed=field(line,"directed")?.parse::<u64>().map_err(|e|e.to_string())?;
        let pairs=field(line,"unordered_pairs")?.parse::<u64>().map_err(|e|e.to_string())?;
        let flux=field(line,"positive_flux_sum")?.parse::<u64>().map_err(|e|e.to_string())?;
        let fnv=u64::from_str_radix(field(line,"pair_fnv64")?,16).map_err(|e|e.to_string())?;
        check(directed==2*pairs,"balanced_partition_census")?;
        out.push(Expected{directed,pairs,flux,fnv});
    }
    check(out.len()==PARTS,"complete_256_partition_receipts")?;
    check(out.iter().map(|r|r.pairs).sum::<u64>()==EXPECTED_PAIRS
          && out.iter().map(|r|r.directed).sum::<u64>()==EXPECTED_DIRECTED
          && out.iter().map(|r|r.flux).sum::<u64>()==EXPECTED_FLUX,
          "archived_original_full_pair_census")?;
    Ok(out)
}
fn validate_pair_chunk(mut edges:Vec<Edge>,part_id:usize,rule:&S3,
                       physics:bool)->Result<(Expected,u64),String>{
    check(part_id<PARTS,"pair_partition_domain")?;
    edges.sort_unstable_by_key(|x|(x.lo,x.hi));
    let mut h=14_695_981_039_346_656_037u64;
    let mut accepted=0u64;
    let mut flux_sum=0u64;
    let mut sampled=0u64;
    let mut i=0usize;
    while i<edges.len(){
        let a=edges[i];
        check(a.lo<a.hi && a.hi<B && a.signed!=0,"valid_canonical_pair_and_nonzero_flux")?;
        check(part(a.lo,a.hi)==part_id,"full_pair_partition_routing")?;
        check(i+1<edges.len(),"missing_reverse_edge")?;
        let b=edges[i+1];
        check(b.lo==a.lo&&b.hi==a.hi,"missing_or_colliding_reverse_pair")?;
        check(i+2==edges.len()||edges[i+2].lo!=a.lo||edges[i+2].hi!=a.hi,
              "duplicate_pair_direction")?;
        let x=i32::from(a.signed);let y=i32::from(b.signed);
        check(x==-y&&x!=0,"exact_opposed_weighted_flux")?;
        let positive=x.max(y) as u64;
        check(1<=positive && positive<=432,"weighted_flux_domain")?;
        fnv(&mut h,a.lo);fnv(&mut h,a.hi);fnv(&mut h,positive);
        accepted+=1;flux_sum+=positive;
        if physics && (accepted==1||accepted%8192==0)&&sampled<FULL_CHALLENGE_PER_PART as u64{
            let left=rule.decode(a.lo);
            let right=rule.decode(a.hi);
            check(rule.address(rule.canonical(rule.expand(left)))==a.lo &&
                  rule.address(rule.canonical(rule.expand(right)))==a.hi,
                  "independent_both_endpoints_canonical")?;
            let wa=rule.weight(left) as u64;
            let wb=rule.weight(right) as u64;
            check((wa==1||wa==2||wa==3||wa==6)&&
                  (wb==1||wb==2||wb==3||wb==6),
                  "independent_s3_orbit_weights")?;
            let la=rule.row(left)?;
            let lb=rule.row(right)?;
            let ca=u64::from(*la.get(&a.hi).unwrap_or(&0));
            let cb=u64::from(*lb.get(&a.lo).unwrap_or(&0));
            check(ca>0&&cb>0&&wa*ca==wb*cb&&wa*ca==positive,
                  "independent_S3_weighted_pair_state_mismatch")?;
            check(rule.magnetic(left)>0&&rule.magnetic(right)>0,
                  "pair_endpoint_not_nonflat")?;
            sampled+=1;
        }
        i+=2;
    }
    Ok((Expected{directed:edges.len() as u64,pairs:accepted,flux:flux_sum,fnv:h},sampled))
}
fn real(dir:&Path,graph:&Path)->Result<(),String>{
    let expected=graph_expectations(graph)?;
    let rule=S3::new()?;
    let started=Instant::now();
    let mut totals=(0u64,0u64,0u64,0u64);
    for (p,want) in expected.iter().enumerate(){
        let filename=dir.join(format!("C-PAIR-{p:03}.bin"));
        let bytes=fs::read(&filename).map_err(|e|format!("read_original_partition_{p}:{e}"))?;
        check(bytes.len()%18==0 && bytes.len() as u64==18*want.directed,
              "original_18byte_directed_pair_partition_length")?;
        let mut entries=Vec::with_capacity(bytes.len()/18);
        for ch in bytes.chunks_exact(18){
            let lo=u64::from_le_bytes(ch[0..8].try_into().map_err(|_|"lo_bytes")?);
            let hi=u64::from_le_bytes(ch[8..16].try_into().map_err(|_|"hi_bytes")?);
            let signed=i16::from_le_bytes(ch[16..18].try_into().map_err(|_|"flux_bytes")?);
            entries.push(Edge{lo,hi,signed});
        }
        let (got,samples)=validate_pair_chunk(entries,p,&rule,true)?;
        check(got.directed==want.directed&&got.pairs==want.pairs
              &&got.flux==want.flux&&got.fnv==want.fnv,
              "original_pair_partition_independent_replay_disagreement")?;
        totals.0+=got.directed;totals.1+=got.pairs;
        totals.2+=got.flux;totals.3+=samples;
        println!("Y137_INDEPENDENT_PAIR_PART|partition={p}|directed={}|pairs={}|flux={}|original_digest={:016x}|pair_multiplicity=EXACT|S3_challenged_endpoint_pairs={samples}|weighted_reciprocity=PASS|json=0",
            got.directed,got.pairs,got.flux,got.fnv);
    }
    check(totals.0==EXPECTED_DIRECTED&&totals.1==EXPECTED_PAIRS
          &&totals.2==EXPECTED_FLUX&&totals.3==PARTS as u64*FULL_CHALLENGE_PER_PART as u64,
          "complete_independent_pairwise_acceptance_census")?;
    println!("Y137_INDEPENDENT_PAIR_VERDICT|partitions=256|directed={}|exact_unordered_pairs={}|positive_flux_sum={}|independent_S3_physical_edge_challenges={}|original_partition_digests=256_OF_256_PASS|all_reverse_weighted_edges=PASS|all_original_partition_routes=PASS|original_pair_archive_hashes=EXTERNAL_SHA256_REQUIRED|Q5_Q5_principal=SEPARATE_FULL_GATE|whole_mu3=INDEPENDENT_RECONSTRUCTION_OPEN|Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|elapsed_seconds={}|json=0",
        totals.0,totals.1,totals.2,totals.3,started.elapsed().as_secs());
    Ok(())
}
fn toy()->Result<(),String>{
    let rule=S3::new()?;
    check(rule.weight([0;13])==1,"identity_weight")?;
    check(rule.magnetic([0;13])==0,"identity_magnetic")?;
    check(rule.row([0;13])?.values().map(|&x|x as u64).sum::<u64>()==72,
          "source_free_electric_moves")?;
    let mut pair=None;
    let flat=rule.row([0;13])?;
    for (&target,&count) in &flat{
        if target>0 {
            pair=Some((0u64,target,count));break;
        }
    }
    let (lo,hi,count)=pair.ok_or("no_toy_edge")?;
    let pos=i16::try_from(count).map_err(|e|e.to_string())?;
    let records=vec![Edge{lo,hi,signed:pos},Edge{lo,hi,signed:-pos}];
    let (got,_) = validate_pair_chunk(records.clone(),part(lo,hi),&rule,false)?;
    check(got.pairs==1&&got.directed==2&&got.flux==u64::from(count),
          "true_s3_pair_toy")?;
    let mutants=[
        vec![records[0]],
        vec![records[0],records[0]],
        vec![records[0],records[1],records[1]],
        vec![records[0],Edge{signed:0,..records[1]}],
        vec![records[0],Edge{signed:pos.saturating_add(1),..records[1]}],
        vec![records[0],Edge{hi:hi+1,..records[1]}],
    ];
    let mut killed=0u32;
    for bad in mutants{
        if validate_pair_chunk(bad,part(lo,hi),&rule,false).is_err(){killed+=1;}
    }
    check(killed==6,"six_pair_tamper_controls")?;
    // Wrong partition is also rejected for an untouched real edge.
    check(validate_pair_chunk(records,(part(lo,hi)+1)%PARTS,&rule,false).is_err(),
          "pair_partition_routing_tamper")?;
    println!("Y137_INDEPENDENT_PAIR_TOY|original_S3_72_moves=PASS|physical_reciprocity=PASS|exact_pair_decode=PASS|planted_pair_tampers=7_REJECTED|real_139M_unordered_pairs=NOT_RUN|json=0");
    Ok(())
}
fn main(){
    let args:Vec<_>=std::env::args().collect();
    let outcome=match args.as_slice(){
        [_,cmd] if cmd=="toy"=>toy(),
        [_,cmd,folder,receipt] if cmd=="real"=>real(Path::new(folder),Path::new(receipt)),
        _=>Err("usage: pair_audit toy | real PAIR_DIRECTORY ORIGINAL_GRAPH_RECEIPT".into()),
    };
    if let Err(e)=outcome{
        eprintln!("Y137_INDEPENDENT_PAIR_REFUSE|reason={}|json=0",e.replace('|',"_"));
        std::process::exit(2);
    }
}
