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
        Some("spectrum") => spectrum_cmd(&args),
        Some("sector") => sector_cmd(&args),
        Some("serve") => match argument(&args, 2, 5088u16) {
            Ok(port) => service(port),
            Err(e) => Err(e),
        },
        _ => Err("usage: hebc run [steps=243] [side=4] [probes_per_tick=8192] [dir=evidence-native] | verify [dir] | gap | spectrum [JE=1] [JB=1] | sector single|double|torus2 | cache-demo [steps=243] [side=4] | address [ordinal] | serve [port=5088]".into()),
    };
    if let Err(e) = result {
        eprintln!("FAIL|reason={e}|json=0");
        std::process::exit(1);
    }
}
