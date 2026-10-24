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
    if steps == 0 || steps > 100_000 || !(2..=32).contains(&side) ||
       probes > 1_000_000 || steps.checked_mul(probes).is_none() {
        return Err("bounds: steps=1..100000 side=2..32 probes=0..1000000".into());
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
        Some("serve") => match argument(&args, 2, 5088u16) {
            Ok(port) => service(port),
            Err(e) => Err(e),
        },
        _ => Err("usage: hebc run [steps=243] [side=4] [probes_per_tick=8192] [dir=evidence-native] | verify [dir] | gap | address [ordinal] | serve [port=5088]".into()),
    };
    if let Err(e) = result {
        eprintln!("FAIL|reason={e}|json=0");
        std::process::exit(1);
    }
}
