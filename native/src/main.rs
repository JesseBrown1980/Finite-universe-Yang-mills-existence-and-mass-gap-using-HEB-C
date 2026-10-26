//! Headless HEB-C CLI. Rust 1.81, native integer calculations, no JavaScript/JSON/float.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::env;
use std::fs;
use std::io::{Read, Write};
use std::net::TcpListener;
use std::path::Path;
use std::time::Instant;

use hebc_finite_yang_mills::{
    address, gap_certificate, hex, sha256, verify_ledger, virtual_qtrit, Lattice, Ledger,
    VIRTUAL_KERNELS,
};

fn argument<T: std::str::FromStr>(args: &[String], index: usize, default: T) -> Result<T, String> {
    match args.get(index) {
        Some(s) => s.parse::<T>().map_err(|_| format!("invalid argument {index}: {s}")),
        None => Ok(default),
    }
}

fn run(args: &[String]) -> Result<(), String> {
    let steps: u64 = argument(args, 2, 243)?;
    let side: usize = argument(args, 3, 4)?;
    let probes: u64 = argument(args, 4, 8_192)?;
    let directory = args.get(5).map(String::as_str).unwrap_or("evidence-native");
    if steps == 0 || steps > 100_000 || !(2..=512).contains(&side) ||
       probes > 1_000_000 || steps.checked_mul(probes).is_none() {
        return Err("bounds: steps=1..100000 side=2..512 probes=0..1000000".into());
    }
    if !gap_certificate() { return Err("finite graph gap certificate failed".into()); }
    let mut lattice = Lattice::new(side, 0x4845_4243_5353_3331);
    let source = lattice.bytes();
    let initial_digest = hex(&sha256(&source));
    let mut ledger = Ledger::new();
    let start = Instant::now();
    let mut probe_checksum = 0u64;
    let mut qtrit_sum = 0i64;
    for t in 1..=steps {
        lattice.advance();
        let state = lattice.bytes();
        ledger.append(t, side, lattice.action(), &state, &source);
        for i in 0..probes {
            let ordinal = (t - 1) * probes + i;
            let virtual_id = address(ordinal);
            probe_checksum = probe_checksum.wrapping_add(virtual_id);
            qtrit_sum += i64::from(virtual_qtrit(ordinal));
        }
    }
    let elapsed_ns = start.elapsed().as_nanos();
    fs::create_dir_all(directory).map_err(|e| e.to_string())?;
    let dir = Path::new(directory);
    fs::write(dir.join("run.hbp"), &ledger.hbp).map_err(|e| e.to_string())?;
    fs::write(dir.join("index.hbi"), &ledger.hbi).map_err(|e| e.to_string())?;
    fs::write(dir.join("run.anchor"), ledger.anchor()).map_err(|e| e.to_string())?;
    let record_count = verify_ledger(
        &ledger.hbp, &ledger.hbi, &ledger.anchor()
    )?;
    let output_sha = hex(&sha256(&lattice.bytes()));
    let record = format!(
        "MEASURE|model=S3_gauge_equivariant_toy|rust=1.81|ticks={steps}|side={side}|state_bytes={}|virtual_namespace={VIRTUAL_KERNELS}|actual_probes={}|probe_checksum={probe_checksum}|qtrit_sum={qtrit_sum}|initial_sha={initial_digest}|final_sha={output_sha}|elapsed_ns={elapsed_ns}|hbp_records={record_count}|graph_gap=3|gap_scope=Cayley_only|json=0\n",
        lattice.bytes().len(), steps * probes
    );
    fs::write(dir.join("run.measure"), &record).map_err(|e| e.to_string())?;
    print!("{record}");
    Ok(())
}

fn verify(args: &[String]) -> Result<(), String> {
    let dir = Path::new(args.get(2).map(String::as_str).unwrap_or("evidence-native"));
    let hbp = fs::read(dir.join("run.hbp")).map_err(|e| e.to_string())?;
    let hbi = fs::read(dir.join("index.hbi")).map_err(|e| e.to_string())?;
    let anchor = fs::read_to_string(dir.join("run.anchor")).map_err(|e| e.to_string())?;
    let n = verify_ledger(&hbp, &hbi, &anchor)?;
    println!("VERIFY|result=PASS|records={n}|anchor_sha={}|json=0", hex(&sha256(anchor.as_bytes())));
    Ok(())
}

fn service(port: u16) -> Result<(), String> {
    // The HTTP-0 computation/addressing namespace is internal. This optional
    // localhost adapter uses conventional HTTP/1.1 framing, not a fictitious protocol.
    let listener = TcpListener::bind(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    println!("SERVE|transport=HTTP/1.1|kernel=HTTP-0|host=127.0.0.1|port={port}|json=0");
    for incoming in listener.incoming() {
        let mut stream = incoming.map_err(|e| e.to_string())?;
        let mut data = [0u8; 1024];
        let len = stream.read(&mut data).map_err(|e| e.to_string())?;
        let request = std::str::from_utf8(&data[..len]).unwrap_or("");
        let line = request.lines().next().unwrap_or("");
        let path = line.strip_prefix("GET ").and_then(|r| r.split(' ').next()).unwrap_or("");
        let (code, payload) = if path == "/health" {
            ("200 OK", "HTTP0|health=OK|native=rust1.81|json=0\n".to_owned())
        } else if path == "/gap" {
            ("200 OK", format!("GAP|group=S3|graph_gap=3|certified={}|scope=Cayley_only|json=0\n", u8::from(gap_certificate())))
        } else if path == "/rime-gear" {
            match hebc_finite_yang_mills::rime_gear::generate() {
                Ok(a) => ("200 OK",a.measure),
                Err(_) => ("500 Internal Server Error",
                    "HTTP0|error=rime_gear_audit_failed|json=0\n".to_owned())
            }
        } else if path == "/shadow-residual" {
            match hebc_finite_yang_mills::shadow_residual::generate() {
                Ok(audit) => ("200 OK", audit.measure),
                Err(_) => ("500 Internal Server Error",
                    "HTTP0|error=shadow_residual_audit_failed|json=0\n".to_owned())
            }
        } else if path == "/constellation" {
            match hebc_finite_yang_mills::constellation_gate::generate() {
                Ok(evidence) => ("200 OK",evidence.measure),
                Err(_) => ("500 Internal Server Error","HTTP0|error=constellation_audit_failed|json=0\n".to_owned())
            }
        } else if let Some(request) = path.strip_prefix("/clasy/") {
            let parts:Vec<&str>=request.split('/').collect();
            if parts.len() != 3 {
                ("400 Bad Request","HTTP0|error=clasy_requires_ordinal_nu_steps|json=0\n".to_owned())
            } else {
                let parsed = (
                    parts[0].parse::<u64>(),
                    parts[1].parse::<u64>(),
                    parts[2].parse::<u64>(),
                );
                match parsed {
                    (Ok(ordinal),Ok(nu),Ok(steps)) if (1..=243).contains(&steps) => {
                        match hebc_finite_yang_mills::clasy_portal::calculate(ordinal,nu,steps) {
                            Ok(run) => ("200 OK",run.report),
                            Err(_) => ("400 Bad Request","HTTP0|error=invalid_clasy_request|json=0\n".to_owned()),
                        }
                    }
                    _ => ("400 Bad Request","HTTP0|error=invalid_clasy_parameters|json=0\n".to_owned()),
                }
            }
        } else if let Some(request) = path.strip_prefix("/torus2/") {
            let parts:Vec<&str>=request.split('/').collect();
            if parts.len()!=2 {
                ("400 Bad Request","HTTP0|error=torus2_requires_couplings|json=0\n".to_owned())
            } else {
                match (parts[0].parse::<i64>(),parts[1].parse::<i64>()) {
                    (Ok(je),Ok(jb)) => match hebc_finite_yang_mills::torus2::certificate(je,jb) {
                        Ok(r) => ("200 OK",r.measure),
                        Err(_) => ("400 Bad Request","HTTP0|error=invalid_torus2_couplings|json=0\n".to_owned()),
                    },
                    _ => ("400 Bad Request","HTTP0|error=invalid_torus2_couplings|json=0\n".to_owned()),
                }
            }
        } else if let Some(request) = path.strip_prefix("/double-spectrum/") {
            let parts:Vec<&str>=request.split('/').collect();
            if parts.len()!=2 {
                ("400 Bad Request","HTTP0|error=double_requires_couplings|json=0\n".to_owned())
            } else {
                match (parts[0].parse::<i64>(),parts[1].parse::<i64>()) {
                    (Ok(je),Ok(jb)) => match hebc_finite_yang_mills::double_plaquette::certificate(je,jb) {
                        Ok(r) => ("200 OK",r.report),
                        Err(_) => ("400 Bad Request","HTTP0|error=invalid_double_couplings|json=0\n".to_owned()),
                    },
                    _ => ("400 Bad Request","HTTP0|error=invalid_double_couplings|json=0\n".to_owned()),
                }
            }
        } else if let Some(request) = path.strip_prefix("/spectrum/") {
            let parts:Vec<&str>=request.split('/').collect();
            if parts.len()!=2 {
                ("400 Bad Request","HTTP0|error=missing_couplings|json=0\n".to_owned())
            } else {
                match (parts[0].parse::<i64>(),parts[1].parse::<i64>()) {
                    (Ok(je),Ok(jb)) => {
                        match hebc_finite_yang_mills::hamiltonian::spectrum(je,jb) {
                            Ok(e) => (
                                "200 OK",
                                format!(
                                    "HTTP0|kernel=s3_one_plaquette|JE={je}|JB={jb}|gap=[{},{}]/65536|positive={}|json=0\n",
                                    e.gap_lower,e.gap_upper,u8::from(e.rigorously_positive())
                                ),
                            ),
                            Err(_) => ("400 Bad Request","HTTP0|error=coupling_bounds|json=0\n".to_owned())
                        }
                    }
                    _ => ("400 Bad Request","HTTP0|error=invalid_couplings|json=0\n".to_owned())
                }
            }
        } else if let Some(id) = path.strip_prefix("/qtrit/").and_then(|s| s.parse::<u64>().ok()) {
            let mapped = address(id);
            ("200 OK", format!("QTRIT|ordinal={id}|address={mapped}|value={}|allocated=0|json=0\n", virtual_qtrit(id)))
        } else {
            ("404 Not Found", "HTTP0|error=not_found|json=0\n".to_owned())
        };
        let header = format!(
            "HTTP/1.1 {code}\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n",
            payload.len()
        );
        stream.write_all(header.as_bytes()).map_err(|e| e.to_string())?;
        stream.write_all(payload.as_bytes()).map_err(|e| e.to_string())?;
    }
    Ok(())
}


fn cache_demo(args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::KernelCache;
    let steps: u64 = argument(args, 2, 243)?;
    let side: usize = argument(args, 3, 4)?;
    if steps > 100_000 || !(2..=32).contains(&side) {
        return Err("invalid cache-demo bounds".into());
    }
    let mut cache = KernelCache::new();
    let start = Instant::now();
    let first = cache.state_after(side, 0x4845_4243_5353_3331, steps);
    let compute_ns = start.elapsed().as_nanos();
    let second_start = Instant::now();
    let second = cache.state_after(side, 0x4845_4243_5353_3331, steps);
    let reuse_ns = second_start.elapsed().as_nanos();
    if first != second || cache.hits != 1 || cache.misses != 1 || cache.active_states() != 1 {
        return Err("cache consistency failure".into());
    }
    println!("CACHE|mode=verified_reuse|steps={steps}|side={side}|states_active=1|hits=1|misses=1|computed_ns={compute_ns}|reuse_ns={reuse_ns}|sha={}|json=0", hex(&sha256(&second)));
    Ok(())
}


/// Produce a direct, certified finite single-plaquette interacting spectrum.
/// The eigenvalues are reported as exact *rational intervals* because
/// irrational algebraic roots cannot be printed as exact finite decimals.
fn spectrum_cmd(args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::hamiltonian::{physical_hamiltonian, spectrum, DENOM};
    let je: i64 = argument(args, 2, 1)?;
    let jb: i64 = argument(args, 3, 1)?;
    let h = physical_hamiltonian(je, jb)?;
    let e = spectrum(je, jb)?;
    let mut bytes = Vec::new();
    for row in h {
        for val in row {
            bytes.extend_from_slice(&val.to_le_bytes());
        }
    }
    println!(
        "SPECTRUM|geometry=single_plaquette|gauge_group=S3|links=4|raw_basis=1296|gauss_dim=3|JE={je}|JB={jb}|E0=[{},{}]/{DENOM}|E1=[{},{}]/{DENOM}|E2=[{},{}]/{DENOM}|gap=[{},{}]/{DENOM}|positive={}|hamiltonian_sha256={}|integer_only=1|json=0",
        e.lower[0], e.upper[0], e.lower[1], e.upper[1], e.lower[2], e.upper[2],
        e.gap_lower, e.gap_upper, u8::from(e.rigorously_positive()), hex(&sha256(&bytes))
    );
    Ok(())
}

fn sector_cmd(args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::hamiltonian::gauss_dimension;
    let (name, vertices, links) = match args.get(2).map(String::as_str) {
        Some("single") => ("single_open_plaquette", 4, 4),
        Some("double") => ("double_open_plaquette", 6, 7),
        Some("torus2") => ("periodic_2x2_torus", 4, 8),
        _ => return Err("sector requires single|double|torus2".into())
    };
    let dim = gauss_dimension(vertices, links)?;
    let qtrits = 2 * links;
    println!("GAUSS|geometry={name}|vertices={vertices}|links={links}|link_qtrits={qtrits}|physical_hilbert_dim={dim}|operator=spectrum_only_single|json=0");
    Ok(())
}


/// Clasy X3 finite shell evolution on a single virtual HTTP-0 address, with
/// full HBI/HBP/SHA/SH/HASH record and an independently recalculated replay.
fn clasy_run(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::clasy_portal::{calculate,save,verify};
    let ordinal:u64=argument(args,2,0)?;
    let nu:u64=argument(args,3,1)?;
    let steps:u64=argument(args,4,243)?;
    let directory=args.get(5).map(String::as_str).unwrap_or("clasy-evidence");
    let record=calculate(ordinal,nu,steps)?;
    let verified=verify(&record.hbp,&record.hbi,&record.anchor)?;
    save(Path::new(directory),&record)?;
    print!("{}",record.report);
    println!("CLASYVERIFY|records={verified}|complete_reexecution=PASS|dir={directory}|json=0");
    Ok(())
}

fn clasy_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::clasy_portal::load_and_verify;
    let directory=args.get(2).map(String::as_str).unwrap_or("clasy-evidence");
    let records=load_and_verify(Path::new(directory))?;
    println!("CLASYVERIFY|result=PASS|records={records}|dir={directory}|json=0");
    Ok(())
}

/// A bounded collection of *actual* independent 81-mode computations.
/// The virtual namespace does not allocate inactive kernels.
fn clasy_batch(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::clasy_portal::{calculate,save,verify};
    use continuum_clay_variation::P;
    let count:u64=argument(args,2,81)?;
    let steps:u64=argument(args,3,243)?;
    let directory=args.get(4).map(String::as_str).unwrap_or("clasy-batch");
    if count==0 || count>243 || steps==0 || steps>243 {
        return Err("batch range: count=1..243 steps=1..243".into());
    }
    let root=Path::new(directory);
    fs::create_dir_all(root).map_err(|e|e.to_string())?;
    let start=Instant::now();
    let mut digest_input=Vec::new();
    for ordinal in 0..count {
        let nu=[0,1,P-1,P,P+1,u64::MAX][(ordinal%6) as usize];
        let record=calculate(ordinal,nu,steps)?;
        verify(&record.hbp,&record.hbi,&record.anchor)?;
        save(&root.join(format!("kernel-{ordinal:03}")),&record)?;
        digest_input.extend_from_slice(&sha256(record.anchor.as_bytes()));
    }
    let elapsed_ns=start.elapsed().as_nanos();
    let bundle_sha=hex(&sha256(&digest_input));
    let report=format!(
        "CLASYBATCH|result=PASS|kernels={count}|ticks_per_kernel={steps}|actual_steps={}|modes_per_kernel=81|virtual_namespace={VIRTUAL_KERNELS}|bundle_sha={bundle_sha}|elapsed_ns={elapsed_ns}|json=0\n",
        count*steps
    );
    fs::write(root.join("batch.measure"),&report).map_err(|e|e.to_string())?;
    print!("{report}");
    Ok(())
}


/// True interacting S3 two-plaquette spectrum, fully Gauss projected from
/// 6^7 raw configurations. This is a static Hamiltonian spectral certificate.
fn double_spectrum(args:&[String])->Result<(),String> {
    use hebc_finite_yang_mills::double_plaquette::{
        certificate,save_certificate,verify_certificate,
    };
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let directory=args.get(4).map(String::as_str).unwrap_or("double-evidence");
    let data=certificate(je,jb)?;
    verify_certificate(&data.hbp,&data.hbi,&data.anchor)?;
    save_certificate(Path::new(directory),&data)?;
    print!("{}",data.report);
    Ok(())
}
fn double_verify(args:&[String])->Result<(),String> {
    use hebc_finite_yang_mills::double_plaquette::verify_certificate_dir;
    let directory=args.get(2).map(String::as_str).unwrap_or("double-evidence");
    verify_certificate_dir(Path::new(directory))?;
    println!("DOUBLEVERIFY|result=PASS|regenerated=1|dir={directory}|json=0");
    Ok(())
}


/// Exact torus operator reconstruction; mixed-coupling gap is qualitative only.
/// Never label a Perron-Frobenius uniqueness proof a quantitative spectral bound.
fn torus2_spectrum(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2::{certificate,save_certificate,verify_certificate};
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let dir=args.get(4).map(String::as_str).unwrap_or("torus2-evidence");
    let receipt=certificate(je,jb)?;
    verify_certificate(&receipt.hbp,&receipt.hbi,&receipt.anchor)?;
    save_certificate(Path::new(dir),&receipt)?;
    print!("{}",receipt.measure);
    Ok(())
}
fn torus2_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2::verify_dir;
    let dir=args.get(2).map(String::as_str).unwrap_or("torus2-evidence");
    verify_dir(Path::new(dir))?;
    println!("TORUS2VERIFY|result=PASS|reconstructed=1|dir={dir}|json=0");
    Ok(())
}


/// Stage 2G: exact rational (conservative) mixed-coupling 1,393-state
/// E0/E1/gap enclosures, not floating-point estimates or continuum claims.
fn torus2_bounds_cmd(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2_bounds::{certificate,save,verify};
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let dir=args.get(4).map(String::as_str).unwrap_or("torus2-bounds");
    let c=certificate(je,jb)?;
    verify(&c,je,jb)?;
    save(Path::new(dir),&c)?;
    print!("{}",c.measure);
    Ok(())
}
fn torus2_bounds_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2_bounds::verify_directory;
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let dir=args.get(4).map(String::as_str).unwrap_or("torus2-bounds");
    verify_directory(Path::new(dir),je,jb)?;
    println!("TORUS2BOUNDSVERIFY|result=PASS|JE={je}|JB={jb}|source_recomputed=1|dir={dir}|json=0");
    Ok(())
}

/// Stage 2H: exact integer rank-one inertia plus symmetry-protected Ritz
/// upper bound, on the unchanged 1393-state S3 periodic torus operator.
fn torus2_inertia_cmd(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2_inertia::{certificate,save};
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let dir=args.get(4).map(String::as_str).unwrap_or("torus2-inertia");
    let c=certificate(je,jb)?;
    save(Path::new(dir),&c)?;
    print!("{}",c.measure);
    Ok(())
}
fn torus2_inertia_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::torus2_inertia::verify_dir;
    let je:i64=argument(args,2,1)?;
    let jb:i64=argument(args,3,1)?;
    let dir=args.get(4).map(String::as_str).unwrap_or("torus2-inertia");
    verify_dir(Path::new(dir),je,jb)?;
    println!("TORUS2INERTIAVERIFY|result=PASS|JE={je}|JB={jb}|source_recomputed=1|dir={dir}|json=0");
    Ok(())
}

fn torus2_independent_cmd(args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::torus2_independent::{certificate, save};
    let je: i64 = argument(args, 2, 1)?;
    let jb: i64 = argument(args, 3, 1)?;
    let dir = args.get(4).map(String::as_str).unwrap_or("torus2-independent");
    let c = certificate(je, jb)?;
    save(Path::new(dir), &c)?;
    print!("{}", c.measure);
    Ok(())
}

fn torus2_independent_verify(args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::torus2_independent::verify_dir;
    let je: i64 = argument(args, 2, 1)?;
    let jb: i64 = argument(args, 3, 1)?;
    let dir = args.get(4).map(String::as_str).unwrap_or("torus2-independent");
    verify_dir(Path::new(dir), je, jb)?;
    println!("TORUS2INDEPENDENTVERIFY|result=PASS|JE={je}|JB={jb}|source_recomputed=1|dir={dir}|json=0");
    Ok(())
}

fn torus2_scaling_cmd(_args: &[String]) -> Result<(), String> {
    use hebc_finite_yang_mills::torus2_independent::finite_volume_scaling;
    let rows = finite_volume_scaling()?;
    for r in rows {
        println!(
            "SCALING|geometry={}|V={}|E={}|faces={}|physical_dim={}|JE={}|JB={}|E0_per_face=[{},{}]/{}|gap=[{},{}]/{}|mode={}|json=0",
            r.geometry, r.vertices, r.links, r.plaquettes, r.physical_dim,
            r.je, r.jb,
            r.e0_lower_per_face, r.e0_upper_per_face, r.e0_denom,
            r.gap_lower, r.gap_upper, r.gap_denom,
            r.mode_type
        );
    }
    Ok(())
}

fn constellation_audit(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::constellation_gate::{generate,save,verify};
    let directory=args.get(2).map(String::as_str).unwrap_or("constellation-evidence");
    let audit=generate()?;
    verify(&audit)?;
    save(Path::new(directory),&audit)?;
    print!("{}",audit.measure);
    Ok(())
}

fn constellation_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::constellation_gate::verify_directory;
    let directory=args.get(2).map(String::as_str).unwrap_or("constellation-evidence");
    verify_directory(Path::new(directory))?;
    println!("CONSTELLATIONVERIFY|result=PASS|scope=SOURCE_AND_INDEX_ONLY|dir={directory}|json=0");
    Ok(())
}


fn shadow_residual_audit(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::shadow_residual::{generate,verify,write};
    let dir=args.get(2).map(String::as_str).unwrap_or("shadow-residual-evidence");
    let record=generate()?;
    verify(&record)?;
    write(Path::new(dir),&record)?;
    print!("{}",record.measure);
    Ok(())
}
fn shadow_residual_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::shadow_residual::verify_dir;
    let dir=args.get(2).map(String::as_str).unwrap_or("shadow-residual-evidence");
    verify_dir(Path::new(dir))?;
    println!("SHADOWRESIDUALVERIFY|result=PASS|scope=FLAT_S3_ONLY|dir={dir}|json=0");
    Ok(())
}


fn rime_gear_audit(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::rime_gear::{generate,verify,write};
    let dir=args.get(2).map(String::as_str).unwrap_or("rime-gear-evidence");
    let a=generate()?;
    verify(&a)?;
    write(Path::new(dir),&a)?;
    print!("{}",a.measure);
    Ok(())
}
fn rime_gear_verify(args:&[String])->Result<(),String>{
    use hebc_finite_yang_mills::rime_gear::verify_directory;
    let dir=args.get(2).map(String::as_str).unwrap_or("rime-gear-evidence");
    verify_directory(Path::new(dir))?;
    println!("RIMEGEARVERIFY|result=PASS|source=LAW70_LAW71|dir={dir}|json=0");
    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let result = match args.get(1).map(String::as_str) {
        Some("run") => run(&args),
        Some("verify") => verify(&args),
        Some("gap") => {
            if gap_certificate() {
                println!("GAP|group=S3|laplacian=all_transpositions|spectrum=0,3,3,3,3,6|first_positive=3|scope=finite_graph_only|json=0");
                Ok(())
            } else {
                Err("integer spectral certificate failed".into())
            }
        }
        Some("address") => match argument(&args, 2, 0u64) {
            Ok(id) => {
                println!("QTRIT|ordinal={id}|virtual_id={}|value={}|json=0", address(id), virtual_qtrit(id));
                Ok(())
            }
            Err(e) => Err(e),
        },
        Some("cache-demo") => cache_demo(&args),
        Some("clasy-run") => clasy_run(&args),
        Some("clasy-verify") => clasy_verify(&args),
        Some("clasy-batch") => clasy_batch(&args),
        Some("double-spectrum") => double_spectrum(&args),
        Some("double-verify") => double_verify(&args),
        Some("torus2-spectrum") => torus2_spectrum(&args),
        Some("torus2-verify") => torus2_verify(&args),
        Some("torus2-bounds") => torus2_bounds_cmd(&args),
        Some("torus2-bounds-verify") => torus2_bounds_verify(&args),
        Some("torus2-inertia") => torus2_inertia_cmd(&args),
        Some("torus2-inertia-verify") => torus2_inertia_verify(&args),
                Some("torus2-independent") => torus2_independent_cmd(&args),
        Some("torus2-independent-verify") => torus2_independent_verify(&args),
        Some("torus2-scaling") => torus2_scaling_cmd(&args),
        Some("constellation-audit") => constellation_audit(&args),
        Some("constellation-verify") => constellation_verify(&args),
        Some("shadow-residual-audit") => shadow_residual_audit(&args),
        Some("shadow-residual-verify") => shadow_residual_verify(&args),
        Some("rime-gear-audit") => rime_gear_audit(&args),
        Some("rime-gear-verify") => rime_gear_verify(&args),
        Some("spectrum") => spectrum_cmd(&args),
        Some("sector") => sector_cmd(&args),
        Some("serve") => match argument(&args, 2, 5088u16) {
            Ok(port) => service(port),
            Err(e) => Err(e),
        },
        _ => Err("usage: hebc run [steps=243] [side=4] [probes_per_tick=8192] [dir=evidence-native] | verify [dir] | gap | spectrum [JE=1] [JB=1] | sector single|double|torus2 | double-spectrum [JE=1] [JB=1] [dir] | double-verify [dir] | torus2-spectrum [JE=1] [JB=1] [dir] | torus2-verify [dir] | torus2-bounds [JE=1] [JB=1] [dir] | torus2-bounds-verify [JE=1] [JB=1] [dir] | torus2-inertia [JE=1] [JB=1] [dir] | torus2-inertia-verify [JE=1] [JB=1] [dir] | cache-demo [steps=243] [side=4] | torus2-independent [JE=1] [JB=1] [dir] | torus2-independent-verify [JE=1] [JB=1] [dir] | torus2-scaling | constellation-audit [dir] | constellation-verify [dir] | shadow-residual-audit [dir] | shadow-residual-verify [dir] | rime-gear-audit [dir] | rime-gear-verify [dir] | clasy-run [ordinal=0] [nu=1] [steps=243] [dir] | clasy-verify [dir] | clasy-batch [count=81] [steps=243] [dir] | address [ordinal] | serve [port=5088]".into()),
    };
    if let Err(e) = result {
        eprintln!("FAIL|reason={e}|json=0");
        std::process::exit(1);
    }
}
