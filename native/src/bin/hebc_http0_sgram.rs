//! HEB-C HTTP-0 / SG-RAM headless backend test ground, Rust 1.81.
//! HTTP-0 = virtual addressing/dispatch, not a new wire protocol.
//! Loopback transport = ordinary HTTP/1.1, HBP/HBI evidence = disk shards.
//! 23B address labels use no per-address allocation. Active computation,
 //! socket buffers and operating system DO use RAM. No JSON, JS or GPU.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use hebc_finite_yang_mills::{
    address, clasy_portal, hex, sha256, torus2_bounds, virtual_qtrit, VIRTUAL_KERNELS,
};
use std::env;
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::time::Duration;

const MAX_STEPS: u64 = 243;
const MAX_HEADER: usize = 2048;

fn arg<T: std::str::FromStr>(item: Option<&String>, name: &str) -> Result<T,String> {
    item.ok_or_else(||format!("missing {name}"))?.parse()
        .map_err(|_|format!("invalid {name}"))
}
fn validate_steps(steps:u64)->Result<(),String>{
    if (1..=MAX_STEPS).contains(&steps) {Ok(())}
    else {Err("steps must be 1..243".into())}
}
fn shard(root:&Path, ordinal:u64, steps:u64)->PathBuf {
    root.join(format!("kernel-{ordinal:020}-ticks-{steps:03}"))
}
fn staging_shard(root:&Path,ordinal:u64,steps:u64)->PathBuf{
    root.join(format!(".inflight-{ordinal:020}-ticks-{steps:03}"))
}
/// Verify a folder against both the original HBI/HBP receipt chain and a
/// fresh source replay. This works for committed shards and staging shards.
fn verify_folder(folder:&Path, ordinal:u64, steps:u64)->Result<String,String>{
    validate_steps(steps)?;
    let count=clasy_portal::load_and_verify(folder)?;
    if count!=steps as usize {return Err("record count mismatch".into());}
    let calc=clasy_portal::calculate(ordinal,1,steps)?;
    for (filename,original) in [
        ("run.hbp",calc.hbp.as_slice()),
        ("index.hbi",calc.hbi.as_slice()),
        ("run.anchor",calc.anchor.as_bytes()),
        ("run.measure",calc.report.as_bytes())
    ]{
        if fs::read(folder.join(filename)).map_err(|e|e.to_string())?!=original {
            return Err(format!("recomputed record mismatch {filename}"));
        }
    }
    Ok(format!("HTTP0SGRAM|result=PASS|action=verify|ordinal={ordinal}|virtual_id={}|ticks={steps}|records={count}|source_sha={}|final_sha={}|anchor_sha={}|json=0\n",
        address(ordinal),calc.source_sha,calc.final_sha,hex(&sha256(calc.anchor.as_bytes()))))
}
fn replay(root:&Path, ordinal:u64, steps:u64)->Result<String,String>{
    verify_folder(&shard(root,ordinal,steps),ordinal,steps)
}
/// Explicit offline recovery: promote only a completely replay-verified
/// staging directory. Never overwrite a previously committed shard.
fn recover(root:&Path, ordinal:u64, steps:u64)->Result<String,String>{
    validate_steps(steps)?;
    let output=shard(root,ordinal,steps);
    if output.exists(){return Err("committed shard already exists; recovery refused".into());}
    let staging=staging_shard(root,ordinal,steps);
    verify_folder(&staging,ordinal,steps)?;
    if output.exists(){return Err("committed shard appeared; recovery refused".into());}
    fs::rename(&staging,&output).map_err(|e|e.to_string())?;
    replay(root,ordinal,steps)?;
    Ok(format!("HTTP0SGRAM|result=PASS|action=recover|ordinal={ordinal}|ticks={steps}|source=VERIFIED_INFLIGHT|json=0\n"))
}
/// Explicit offline quarantine for an incomplete or suspect staging directory.
/// Does not erase evidence, does not trust its contents, and never replaces a
/// pre-existing quarantine directory. Operator must stop writers first.
fn quarantine(root:&Path, ordinal:u64, steps:u64)->Result<String,String>{
    validate_steps(steps)?;
    let staging=staging_shard(root,ordinal,steps);
    if !staging.is_dir(){return Err("staging shard not found".into());}
    for serial in 0..10_000u16{
        let candidate=root.join(format!(".quarantine-{ordinal:020}-ticks-{steps:03}-{serial:04}"));
        if !candidate.exists(){
            fs::rename(&staging,&candidate).map_err(|e|e.to_string())?;
            return Ok(format!("HTTP0SGRAM|result=PASS|action=quarantine|ordinal={ordinal}|ticks={steps}|slot={serial}|trusted=0|json=0\n"));
        }
    }
    Err("no quarantine slot available".into())
}
fn persist(root:&Path, ordinal:u64, steps:u64)->Result<String,String>{
    validate_steps(steps)?;
    fs::create_dir_all(root).map_err(|e|e.to_string())?;
    let output=shard(root,ordinal,steps);
    if output.exists(){return replay(root,ordinal,steps);}
    // No overwriting committed evidence. A concurrent writer is rejected
    // by exclusive staging-dir creation; interrupted writes remain inspectable.
    let staging=staging_shard(root,ordinal,steps);
    fs::create_dir(&staging).map_err(|_|"staging exists or cannot be created")?;
    let data=clasy_portal::calculate(ordinal,1,steps)?;
    clasy_portal::verify(&data.hbp,&data.hbi,&data.anchor)?;
    clasy_portal::save(&staging,&data)?;
    fs::rename(&staging,&output).map_err(|e|e.to_string())?;
    replay(root,ordinal,steps)?;
    Ok(format!("HTTP0SGRAM|result=PASS|action=run|ordinal={ordinal}|virtual_id={}|ticks={steps}|active_kernels=1|allocated_namespace_states=0|backend=HBP_HBI_DISK_SHARDS|source_sha={}|final_sha={}|json=0\n",
        address(ordinal),data.source_sha,data.final_sha))
}
fn finite_gap(je:i64,jb:i64)->Result<String,String>{
    let b=torus2_bounds::enclose(je,jb)?;
    // These are Stage 2H thresholds from the native torus2_inertia model,
    // independently supported by PR #9. They are references, NOT recomputed
    // here: this route executes only Stage 2G Collatz-Poincare enclose().
    let stage2h_t=match (je,jb){
        (1,1)=>13_240,
        (3,5)=>50_840,
        _=>return Err("no Stage 2H threshold for coupling".into()),
    };
    Ok(format!("HTTP0SGRAM|result=PASS|action=finite_s3_gap|JE={je}|JB={jb}|physical_dim=1393|E0=[{},{}]/1000000|E1=[{},{}]/1000000|gap=[{},{}]/1000000|E1_source=STAGE2G_COLLATZ_POINCARE|E1_stage2g=[{},{}]/1000000|E1_stage2h_strict_gt_reference={stage2h_t}/1000|E1_stage2h_source=NATIVE_STAGE2H_PR9|E1_stage2h_verified_this_request=0|continuum_proven=0|json=0\n",
        b.e0_lower,b.e0_upper,b.e1_lower,b.e1_upper,b.gap_lower,b.gap_upper,
        b.e1_lower,b.e1_upper))
}
fn route(root:&Path, method:&str, path:&str)->(u16,String){
    if method=="GET" && path=="/health"{
        return(200,format!("HTTP0SGRAM|health=OK|transport=HTTP/1.1|namespace={VIRTUAL_KERNELS}|allocated_namespace_states=0|gpu_required=0|json=0\n"));
    }
    match (method,path.trim_start_matches('/').split('/').collect::<Vec<_>>().as_slice()){
        ("GET",["qtrit",s])=>match s.parse::<u64>(){
            Ok(n)=>(200,format!("HTTP0SGRAM|result=PASS|action=address|ordinal={n}|virtual_id={}|value={}|allocated_namespace_states=0|json=0\n",address(n),virtual_qtrit(n))),
            Err(_)=>(400,"HTTP0SGRAM|error=invalid_ordinal|json=0\n".into()),
        },
        ("GET",["finite-gap",a,b])=>match(a.parse::<i64>(),b.parse::<i64>()){
            (Ok(je),Ok(jb))=>match finite_gap(je,jb){
                Ok(line)=>(200,line),
                Err(_)=>(400,"HTTP0SGRAM|error=uncertified_couplings|json=0\n".into()),
            },
            _=>(400,"HTTP0SGRAM|error=invalid_couplings|json=0\n".into())
        },
        ("GET",["verify",a,b])=>match(a.parse::<u64>(),b.parse::<u64>()){
            (Ok(ordinal),Ok(steps))=>match replay(root,ordinal,steps){
                Ok(line)=>(200,line),
                Err(_)=>(409,"HTTP0SGRAM|error=shard_verification_failed|json=0\n".into()),
            },
            _=>(400,"HTTP0SGRAM|error=invalid_shard_request|json=0\n".into())
        },
        ("POST",["run",a,b])=>match(a.parse::<u64>(),b.parse::<u64>()){
            (Ok(ordinal),Ok(steps))=>match persist(root,ordinal,steps){
                Ok(line)=>(200,line),
                Err(_)=>(409,"HTTP0SGRAM|error=run_failed|json=0\n".into()),
            },
            _=>(400,"HTTP0SGRAM|error=invalid_run_request|json=0\n".into())
        },
        _=>(404,"HTTP0SGRAM|error=not_found|json=0\n".into())
    }
}
fn request_line(stream:&mut TcpStream)->Result<(String,String),String>{
    stream.set_read_timeout(Some(Duration::from_secs(3)))
        .map_err(|e|e.to_string())?;
    let mut buf=[0u8;MAX_HEADER];let mut length=0usize;
    loop{
        if length==buf.len(){return Err("oversized HTTP header".into());}
        let n=stream.read(&mut buf[length..]).map_err(|e|e.to_string())?;
        if n==0{return Err("truncated HTTP header".into());}
        length+=n;
        if buf[..length].windows(4).any(|w|w==b"\r\n\r\n"){break;}
    }
    let head=std::str::from_utf8(&buf[..length]).map_err(|_|"non-utf8 HTTP")?;
    let line=head.split("\r\n").next().ok_or("missing request")?;
    let mut tokens=line.split_ascii_whitespace();
    let method=tokens.next().ok_or("missing method")?;
    let path=tokens.next().ok_or("missing path")?;
    let version=tokens.next().ok_or("missing version")?;
    if tokens.next().is_some()||version!="HTTP/1.1"||
       !matches!(method,"GET"|"POST")||!path.starts_with('/')||path.contains('?'){
        return Err("invalid HTTP request".into());
    }
    // The backend accepts no request body; reject body framing to keep it
    // a tiny smoke/test surface rather than a general HTTP parser.
    for row in head.split("\r\n").skip(1){
        let low=row.to_ascii_lowercase();
        if low.starts_with("transfer-encoding:") ||
           (low.starts_with("content-length:") && low.trim()!="content-length: 0"){
            return Err("request body not supported".into());
        }
    }
    Ok((method.to_owned(),path.to_owned()))
}
fn handle(mut stream:TcpStream, root:&Path)->Result<(),String>{
    let (status,body)=match request_line(&mut stream){
        Ok((m,p))=>route(root,&m,&p),
        Err(_)=>(400,"HTTP0SGRAM|error=malformed_request|json=0\n".into()),
    };
    let reason=match status{
        200=>"200 OK",400=>"400 Bad Request",404=>"404 Not Found",_=>"409 Conflict",
    };
    let header=format!("HTTP/1.1 {reason}\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n",body.len());
    stream.write_all(header.as_bytes()).map_err(|e|e.to_string())?;
    stream.write_all(body.as_bytes()).map_err(|e|e.to_string())
}
/// Connection-level failures, including an early disconnect and broken pipe,
/// are never fatal to the listener. The bounded request count includes failed
/// accepts and closed clients, so this test server cannot run forever.
fn serve_listener(listener:TcpListener,root:&Path,max_requests:usize)->Result<(),String>{
    if max_requests==0||max_requests>10000{return Err("max_requests bound: 1..10000".into());}
    for connection in listener.incoming().take(max_requests){
        match connection {
            Ok(stream)=>{
                if let Err(_err)=handle(stream,root){
                    eprintln!("HTTP0SGRAM|event=client_error|action=continue|json=0");
                }
            }
            Err(_err)=>{
                eprintln!("HTTP0SGRAM|event=accept_error|action=continue|json=0");
            }
        }
    }
    Ok(())
}
fn serve(root:&Path,port:u16,max_requests:usize)->Result<(),String>{
    if max_requests==0||max_requests>10000{return Err("max_requests bound: 1..10000".into());}
    let listener=TcpListener::bind(("127.0.0.1",port)).map_err(|e|e.to_string())?;
    println!("HTTP0SGRAM|server=READY|transport=HTTP/1.1|bind=127.0.0.1|port={port}|max_requests={max_requests}|json=0");
    serve_listener(listener,root,max_requests)
}
fn main(){
    let args:Vec<String>=env::args().collect();
    let result=(||->Result<String,String>{
        match args.get(1).map(String::as_str){
            Some("address")=>{
                let ordinal=arg::<u64>(args.get(2),"ordinal")?;
                Ok(format!("HTTP0SGRAM|result=PASS|action=address|ordinal={ordinal}|virtual_id={}|value={}|allocated_namespace_states=0|json=0\n",address(ordinal),virtual_qtrit(ordinal)))
            }
            Some("run")=>{
                let root=Path::new(args.get(2).ok_or("missing root")?);
                persist(root,arg(args.get(3),"ordinal")?,arg(args.get(4),"ticks")?)
            }
            Some("verify")=>{
                let root=Path::new(args.get(2).ok_or("missing root")?);
                replay(root,arg(args.get(3),"ordinal")?,arg(args.get(4),"ticks")?)
            }
            Some("recover")=>{
                let root=Path::new(args.get(2).ok_or("missing root")?);
                recover(root,arg(args.get(3),"ordinal")?,arg(args.get(4),"ticks")?)
            }
            Some("quarantine")=>{
                let root=Path::new(args.get(2).ok_or("missing root")?);
                quarantine(root,arg(args.get(3),"ordinal")?,arg(args.get(4),"ticks")?)
            }
            Some("finite-gap")=>finite_gap(arg(args.get(2),"JE")?,arg(args.get(3),"JB")?),
            Some("serve")=>{
                let root=Path::new(args.get(2).ok_or("missing root")?);
                let port=args.get(3).map_or(Ok(5097),|_|arg(args.get(3),"port"))?;
                let limit=args.get(4).map_or(Ok(64),|_|arg(args.get(4),"max_requests"))?;
                serve(root,port,limit)?;
                Ok("HTTP0SGRAM|server=STOPPED|json=0\n".into())
            }
            _=>Err("usage: hebc_http0_sgram address ORDINAL | run ROOT ORDINAL TICKS | verify ROOT ORDINAL TICKS | recover ROOT ORDINAL TICKS | quarantine ROOT ORDINAL TICKS | finite-gap JE JB | serve ROOT [PORT=5097] [MAX_REQUESTS=64]".into())
        }
    })();
    match result{
        Ok(line)=>print!("{line}"),
        Err(e)=>{eprintln!("HTTP0SGRAM|result=FAIL|reason={e}|json=0");std::process::exit(1);}
    }
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test]
    fn virtual_addresses_are_unallocated(){
        assert!(route(Path::new("."),"GET","/health").1.contains("allocated_namespace_states=0"));
        assert_eq!(route(Path::new("."),"GET","/qtrit/22999999999").0,200);
        assert_eq!(route(Path::new("."),"GET","/qtrit/x").0,400);
        assert_eq!(route(Path::new("."),"GET","/unknown").0,404);
        assert_eq!(route(Path::new("."),"POST","/run/0/244").0,409);
    }
    #[test]
    fn abandoned_client_cannot_kill_server(){
        use std::net::Shutdown;
        use std::thread;
        let listener=TcpListener::bind("127.0.0.1:0").unwrap();
        let address=listener.local_addr().unwrap();
        let root=std::env::temp_dir();
        let server=thread::spawn(move||serve_listener(listener,&root,2));
        // A peer can vanish after TCP connect, before sending any HTTP
        // request. The next valid request must be served by that listener.
        let abandoned=TcpStream::connect(address).unwrap();
        abandoned.shutdown(Shutdown::Both).unwrap();
        drop(abandoned);
        let mut healthy=TcpStream::connect(address).unwrap();
        healthy.write_all(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n").unwrap();
        let mut response=String::new();
        healthy.read_to_string(&mut response).unwrap();
        assert!(response.starts_with("HTTP/1.1 200 OK"),"{response}");
        assert!(response.contains("health=OK"),"{response}");
        assert!(server.join().unwrap().is_ok());
    }
    #[test]
    fn staging_recovery_never_promotes_unverified_content(){
        let root=std::env::temp_dir().join(format!(
            "hebc-http0-sgram-recovery-{}",std::process::id()));
        if root.exists(){fs::remove_dir_all(&root).unwrap();}
        fs::create_dir_all(&root).unwrap();
        let stage=staging_shard(&root,19,3);
        fs::create_dir(&stage).unwrap();
        fs::write(stage.join("run.hbp"),b"incomplete").unwrap();
        assert!(recover(&root,19,3).is_err());
        assert!(!shard(&root,19,3).exists());
        // Incomplete evidence must remain inspectable in quarantine.
        assert!(quarantine(&root,19,3).unwrap().contains("trusted=0"));
        assert!(!stage.exists());
        let quarantined=root.join(".quarantine-00000000000000000019-ticks-003-0000");
        assert!(quarantined.join("run.hbp").exists());
        let valid=clasy_portal::calculate(19,1,3).unwrap();
        fs::create_dir(&stage).unwrap();
        clasy_portal::save(&stage,&valid).unwrap();
        assert!(recover(&root,19,3).unwrap().contains("action=recover"));
        assert!(replay(&root,19,3).unwrap().contains("result=PASS"));
        assert!(!stage.exists());
        assert!(recover(&root,19,3).is_err());
        fs::remove_dir_all(&root).unwrap();
    }
    #[test]
    fn bound_provenance_does_not_claim_stage2h_execution(){
        for (je,jb,ref_threshold) in [(1,1,"13240/1000"),(3,5,"50840/1000")] {
            let line=finite_gap(je,jb).unwrap();
            assert!(line.contains("E1_source=STAGE2G_COLLATZ_POINCARE"));
            assert!(line.contains("E1_stage2g=["));
            assert!(line.contains(&format!("E1_stage2h_strict_gt_reference={ref_threshold}")));
            assert!(line.contains("E1_stage2h_verified_this_request=0"));
        }
    }
    #[test]
    fn persist_replay_and_corruption_rejected(){
        let root=std::env::temp_dir().join(format!("hebc-http0-sgram-test-{}",std::process::id()));
        if root.exists(){fs::remove_dir_all(&root).unwrap();}
        let first=persist(&root,5,3).unwrap();
        assert!(first.contains("action=run"));
        assert!(persist(&root,5,3).unwrap().contains("action=verify"));
        let filepath=shard(&root,5,3).join("run.hbp");
        let original=fs::read(&filepath).unwrap();
        let mut modified=original.clone();modified[10]^=1;
        fs::write(&filepath,modified).unwrap();
        assert!(replay(&root,5,3).is_err());
        assert!(persist(&root,5,3).is_err());
        fs::write(&filepath,original).unwrap();
        assert!(replay(&root,5,3).unwrap().contains("result=PASS"));
        fs::remove_dir_all(&root).unwrap();
    }
}
