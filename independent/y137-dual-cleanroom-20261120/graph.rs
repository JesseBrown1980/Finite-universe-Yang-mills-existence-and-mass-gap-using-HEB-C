//! Clean-room S3 3x4 physical orbit and Wilson matched-Q-dual reconstruction.
//! No imports or calls to the historical Python graph or dual producers.
//! Standard library only; safe Rust; deterministic integer arithmetic.
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{BufWriter, Write};

const E1: i128 = 69_909_586_556;
const E2: i128 = 69_949_433_884;
const DEN: i128 = 1_000_000_000;
const SCALE: i128 = 1_000_000_000_000;
const V1: [i128;8] = [1_000_000_000,997_998_757,997_000_845,39_006_811,38_860_510,2_944_164,80_455,80_455];
const V2: [i128;8] = [112_491_544,-39_124_838,-114_340_075,1_000_000_000,978_089_453,221_700_078,5_301_152,5_301_152];

#[derive(Clone)]
struct Row { key: u64, w: u8, mag: u8, wilson: i8, dbase: i16, c: [u16;8], adj: Vec<(u32,u16)> }
struct Ext { key: u64, w:u8, src: Vec<(u32,u16)> }
struct Group { mul: [[u8;6];6],inv:[u8;6],conj:[[u8;6];6],char6:[i8;6],trans:[u8;3],kept:[usize;13],tree:[(usize,usize,usize);11] }
fn pos(x:usize,y:usize)->usize { (x%3)*4+(y%4) }
fn code(key:&[u8;13])->u64 { let mut scale=1u64; let mut out=0u64; for &v in key {out+=u64::from(v)*scale;scale*=6;} out }
fn decode(mut v:u64)->[u8;13] { let mut k=[0u8;13]; for item in &mut k { *item=(v%6) as u8;v/=6;} k }
fn perms()->[[u8;3];6] { [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]] }
impl Group {
 fn new()->Self {
  let p=perms();let mut mul=[[0u8;6];6];let mut inv=[0u8;6];let mut conj=[[0u8;6];6];let mut char6=[0i8;6];
  for a in 0..6 { char6[a]=(0..3).filter(|&k|usize::from(p[a][k])==k).count() as i8-1;
   for b in 0..6 { let perm=[p[a][usize::from(p[b][0])],p[a][usize::from(p[b][1])],p[a][usize::from(p[b][2])]];
    mul[a][b]=p.iter().position(|x|*x==perm).expect("closed S3") as u8;
   }
  }
  for a in 0..6 { inv[a]=(0..6).find(|&b|mul[a][b]==0&&mul[b][a]==0).expect("inverse") as u8; }
  for g in 0..6 { for a in 0..6 {conj[g][a]=mul[usize::from(mul[g][a])][usize::from(inv[g])];}}
  let trans:Vec<u8>=(1..6).filter(|&a|mul[a][a]==0).map(|a|a as u8).collect();assert_eq!(trans.len(),3);
  let mut tree=Vec::new();for y in 0..3 {tree.push((pos(0,y),pos(0,y+1),12+pos(0,y)));}
  for y in 0..4 {for x in 0..2 {tree.push((pos(x,y),pos(x+1,y),pos(x,y)));}}
  assert_eq!(tree.len(),11);
  let excluded:HashSet<usize>=tree.iter().map(|x|x.2).collect();
  let kept:Vec<usize>=(0..24).filter(|k|!excluded.contains(k)).collect();assert_eq!(kept.len(),13);
  Self{mul,inv,conj,char6,trans:trans.try_into().expect("3 transp"),kept:kept.try_into().expect("13 retained"),tree:tree.try_into().expect("11 tree")}
 }
 fn full(&self,k:u64)->[u8;24] {let key=decode(k);let mut u=[0u8;24];for (i,&j) in self.kept.iter().enumerate(){u[j]=key[i];}u}
 fn canonical(&self,u:&[u8;24])->u64 {
  let mut h=[0u8;12];
  for &(a,b,e) in &self.tree {h[b]=self.mul[usize::from(h[a])][usize::from(u[e])];}
  let mut z=[0u8;13];
  for (i,&e) in self.kept.iter().enumerate() {
   let src=e%12;let (x,y)=(src/4,src%4);let dst=if e<12 {pos(x+1,y)}else{pos(x,y+1)};
   let first=self.mul[usize::from(h[src])][usize::from(u[e])];
   z[i]=self.mul[usize::from(first)][usize::from(self.inv[usize::from(h[dst])])];
  }
  let mut best=z;
  for g in 1..6 {
   let mut t=[0u8;13];for i in 0..13 {t[i]=self.conj[g][usize::from(z[i])];}
   if t<best {best=t;}
  }
  code(&best)
 }
 fn weight(&self,k:u64)->u8 {let a=decode(k);let mut seen=[[0u8;13];6];let mut n=0usize;
  for g in 0..6 {let mut b=[0u8;13];for i in 0..13 {b[i]=self.conj[g][usize::from(a[i])];}
   if !seen[..n].contains(&b){seen[n]=b;n+=1;}
  }n as u8
 }
 fn mag(&self,k:u64)->u8 {let u=self.full(k);let mut total=0i32;
  for x in 0..3{for y in 0..4 {
   let i=pos(x,y);let r=pos(x+1,y);let top=pos(x,y+1);
   let a=self.mul[usize::from(u[i])][usize::from(u[12+r])];
   let b=self.mul[usize::from(a)][usize::from(self.inv[usize::from(u[top])])];
   let p=self.mul[usize::from(b)][usize::from(self.inv[usize::from(u[12+i])])];
   total+=2-i32::from(self.char6[usize::from(p)]);
  }}u8::try_from(total).expect("magnetic integer range")
 }
 fn wilson(&self,k:u64)->i8 {let u=self.full(k);let mut s=0i8;
  for y in 0..4 {let mut a=0u8;for x in 0..3 {a=self.mul[usize::from(a)][usize::from(u[pos(x,y)])];}s+=self.char6[usize::from(a)];}
  for x in 0..3 {let mut a=0u8;for y in 0..4 {a=self.mul[usize::from(a)][usize::from(u[12+pos(x,y)])];}s+=self.char6[usize::from(a)];}s
 }
 fn neighbors(&self,k:u64)->Vec<(u64,u16)> {let mut u=self.full(k);let mut counter:HashMap<u64,u16>=HashMap::with_capacity(70);
  for e in 0..24 {let old=u[e];for &t in &self.trans {u[e]=self.mul[usize::from(t)][usize::from(old)];
    let dst=self.canonical(&u);*counter.entry(dst).or_insert(0)+=1;
   }u[e]=old;
  }
  let sum:usize=counter.values().map(|x|usize::from(*x)).sum();assert_eq!(sum,72,"72 original reversible moves");
  let mut row:Vec<(u64,u16)>=counter.into_iter().collect();row.sort_unstable_by_key(|x|x.0);row
 }
 fn flats(&self)->Vec<u64>{let mut flats=HashSet::new();
  for a in 0..6 {for b in 0..6 {if self.mul[a][b]!=self.mul[b][a]{continue;}
   let mut u=[0u8;24];for y in 0..4 {u[pos(2,y)]=a as u8;}for x in 0..3 {u[12+pos(x,3)]=b as u8;}
   let key=self.canonical(&u);assert_eq!(self.mag(key),0);flats.insert(key);
  }}
  let mut res:Vec<u64>=flats.into_iter().collect();res.sort_unstable_by_key(|x|decode(*x));res
 }
}
fn ceil_positive(n:i128,d:i128)->i128{assert!(n>=0&&d>0);(n+d-1)/d}
fn sparse_y(rows:&[Row],energy:i128)->Vec<[i128;8]>{
 let n=rows.len();let mut y=vec![[0i128;8];n];
 for pass in 0..20 {let mut next=vec![[0i128;8];n];
  for (i,r) in rows.iter().enumerate(){let diag=DEN*i128::from(r.dbase)-energy;assert!(diag>0);
   let mut sums=[0i128;8];for k in 0..8{sums[k]=SCALE*i128::from(r.c[k]);}
   for &(j,c) in &r.adj {let src=&y[j as usize];for k in 0..8 {sums[k]+=i128::from(c)*src[k];}}
   for k in 0..8 {next[i][k]=ceil_positive(DEN*sums[k],diag);}
  }y=next;
  if pass==0||pass==19 {eprintln!("Y137_CLEANROOM_Y_PROGRESS|energy={}|sweep={}|state_count={}",energy,pass+1,n);}
 }y
}
fn q_from_y(y:&[[i128;8]],v:&[i128;8])->Vec<i128>{y.iter().map(|row|row.iter().zip(v).map(|(a,b)|a*b).sum::<i128>()).collect()}
fn dual(rows:&[Row],rhs:&[i128],energy:i128)->Vec<i128>{let n=rows.len();let mut u=vec![0i128;n];
 for pass in 0..20 {let mut next=vec![0i128;n];
  for (i,r) in rows.iter().enumerate(){let d=DEN*i128::from(r.dbase)-energy;let mut b=rhs[i];
   for &(j,c) in &r.adj {b+=i128::from(c)*u[j as usize];}
   next[i]=(DEN*b).div_euclid(d);
  }u=next;
  if pass==0||pass==19 {eprintln!("Y137_CLEANROOM_DUAL_PROGRESS|energy={}|sweep={}|state_count={}",energy,pass+1,n);}
 }u
}
fn w_u8<W:Write>(wr:&mut W,x:u8)->std::io::Result<()> {wr.write_all(&[x])}
fn w_u16<W:Write>(wr:&mut W,x:u16)->std::io::Result<()> {wr.write_all(&x.to_le_bytes())}
fn w_u32<W:Write>(wr:&mut W,x:u32)->std::io::Result<()> {wr.write_all(&x.to_le_bytes())}
fn w_u64<W:Write>(wr:&mut W,x:u64)->std::io::Result<()> {wr.write_all(&x.to_le_bytes())}
fn w_i16<W:Write>(wr:&mut W,x:i16)->std::io::Result<()> {wr.write_all(&x.to_le_bytes())}
fn w_i128<W:Write>(wr:&mut W,x:i128)->std::io::Result<()> {wr.write_all(&x.to_le_bytes())}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let filename=std::env::args().nth(1).expect("output binary path");let g=Group::new();
 let flats=g.flats();assert_eq!(flats.len(),8);let wp:Vec<u8>=flats.iter().map(|&k|g.weight(k)).collect();
 let op:Vec<i8>=flats.iter().map(|&k|g.wilson(k)).collect();
 assert_eq!(wp,vec![1,3,2,3,3,2,2,2]);assert_eq!(op,vec![14,8,5,6,0,2,-7,-7]);
 eprintln!("Y137_CLEANROOM_SOURCE|flats=8|W={:?}|Wilson={:?}",wp,op);
 let mut seen:HashSet<u64>=flats.iter().copied().collect();let mut layers=vec![flats.clone()];
 for depth in 1..=3 {let mut fresh=HashSet::<u64>::new();
  for &k in layers.last().expect("previous layer") {for (v,_) in g.neighbors(k) {if !seen.contains(&v){fresh.insert(v);}}}
  let mut nxt:Vec<u64>=fresh.into_iter().collect();nxt.sort_unstable();seen.extend(nxt.iter().copied());
  eprintln!("Y137_CLEANROOM_SHELL|depth={}|states={}",depth,nxt.len());layers.push(nxt);
 }
 assert_eq!([layers[0].len(),layers[1].len(),layers[2].len(),layers[3].len()],[8,264,7770,147344]);
 let all:Vec<u64>=layers.into_iter().flatten().collect();let n=all.len()-8;assert_eq!(n,155378);
 let mut index=HashMap::with_capacity(all.len());for (i,&k) in all.iter().enumerate(){index.insert(k,i as u32);}
 let mut rows=Vec::<Row>::with_capacity(n);let mut ext=Vec::<Ext>::new();let mut exindex=HashMap::<u64,u32>::new();
 let mut edge_count=0usize;let mut q_to_flat=0usize;
 for (i,&k) in all.iter().enumerate().skip(8){let i0=(i-8) as u32;let w=g.weight(k);let mag=g.mag(k);let wilson=g.wilson(k);
  let mut c=[0u16;8];let mut selfc=0u16;let mut adj=Vec::new();
  for (dst,moves) in g.neighbors(k) {
   if let Some(&j)=index.get(&dst){if j<8 {c[j as usize]+=moves;q_to_flat+=moves as usize;}
     else if j==i as u32{selfc+=moves;}else{adj.push((j-8,moves));edge_count+=1;}
   }else{
    let f=if let Some(&j)=exindex.get(&dst){j}else{let j=ext.len() as u32;let ww=g.weight(dst);
      ext.push(Ext{key:dst,w:ww,src:Vec::new()});exindex.insert(dst,j);j};
    let wc=u16::from(w)*moves;let ex=&mut ext[f as usize];assert_eq!(ex.key,dst);assert_eq!(wc%u16::from(ex.w),0);
    ex.src.push((i0,wc));
   }
  }
  let db=72i32+9*i32::from(mag)-i32::from(selfc);assert!(db>0&&db<32767);
  rows.push(Row{key:k,w,mag,wilson,dbase:db as i16,c,adj});
  if i0%20000==0{eprintln!("Y137_CLEANROOM_GRAPH_PROGRESS|Qrows={}|exterior={}|internal={}",i0,ext.len(),edge_count);}
 }
 assert_eq!(ext.len(),1985218);assert_eq!(edge_count,1356528);
 assert_eq!(q_to_flat,264);
 for (i,r) in rows.iter().enumerate(){for &(j,c) in &r.adj {let other=&rows[j as usize];
  let reverse=other.adj.iter().find(|(k,_)|*k==i as u32).map(|x|x.1).expect("reverse Q electric edge");
  assert_eq!(u32::from(r.w)*u32::from(c),u32::from(other.w)*u32::from(reverse),"physical W Q detailed balance");
 }}
 eprintln!("Y137_CLEANROOM_SOURCE_VERDICT|Q_states={}|Q_adj={}|Q4_states={}|PQ_weighted_edges={}|W_reciprocity=PASS",n,edge_count,ext.len(),q_to_flat);
 let y1=sparse_y(&rows,E1);let q1=q_from_y(&y1,&V1);drop(y1);
 let y2=sparse_y(&rows,E2);let q2=q_from_y(&y2,&V2);drop(y2);
 let rhs21:Vec<i128>=q1.iter().zip(&rows).map(|(q,r)|*q*(2*i128::from(r.wilson)-16)).collect();
 let rhs12:Vec<i128>=q2.iter().zip(&rows).map(|(q,r)|*q*(2*i128::from(r.wilson)-16)).collect();
 let u21=dual(&rows,&rhs21,E2);let u12=dual(&rows,&rhs12,E1);
 eprintln!("Y137_CLEANROOM_Q_DUAL|trial=2|duals=2|sweeps=20|Q_states={}|raw_Q_source=FRESH_S3",n);
 let file=File::create(filename)?;let mut out=BufWriter::new(file);out.write_all(b"Y137RAW1")?;
 w_u32(&mut out,n as u32)?;w_u32(&mut out,ext.len() as u32)?;w_u32(&mut out,edge_count as u32)?;
 for &w in &wp{w_u8(&mut out,w)?;}for &o in &op{w_u8(&mut out,o as u8)?;}
 for r in &rows{w_u64(&mut out,r.key)?;w_u8(&mut out,r.w)?;w_u8(&mut out,r.mag)?;
  w_u8(&mut out,r.wilson as u8)?;w_i16(&mut out,r.dbase)?;
  for &x in &r.c{w_u16(&mut out,x)?;}
  w_u16(&mut out,r.adj.len() as u16)?;
  for &(j,c) in &r.adj {w_u32(&mut out,j)?;w_u16(&mut out,c)?;}
 }
 for e in &ext{w_u64(&mut out,e.key)?;w_u8(&mut out,e.w)?;w_u16(&mut out,e.src.len() as u16)?;
  for &(src,wc) in &e.src {w_u32(&mut out,src)?;w_u16(&mut out,wc)?;}
 }
 for v in [&q1,&q2,&u21,&u12] {for &x in v {w_i128(&mut out,x)?;}}
 out.flush()?;eprintln!("Y137_CLEANROOM_BINARY_WRITTEN|rows={}|exterior={}|name=SOURCE.bin",n,ext.len());
 Ok(())
}
