//! hebc_ym_http0: HEB-C HTTP-0 execution and verification layer for the finite
//! S3 Yang-Mills sector tools (torusl/ymsec, evolvers/flatcomp+cluster,
//! sturmrs/shellschur), copied unchanged from The-matrix-law-essentials.
//!
//! The backend never does mathematics itself. It runs one tool per job, splits
//! the tool's output into
//!   run.hbp      canonical scientific lines (runtime fields such as ms= removed)
//!   index.hbi    per-line offsets, line SHA-256 and a running hash chain
//!   run.anchor   job spec + digests of run.hbp and index.hbi
//!   run.measure  runtime metadata only (removed fields, wall time, tool shas)
//! and stores them in a disk shard. `verify` re-executes the job in a fresh
//! staging directory and compares run.hbp, index.hbi and run.anchor byte for
//! byte; run.measure is never compared. A headless command and its HTTP-0 route
//! call the same function, so they produce identical canonical bytes.
//!
//! Shards: ROOT/shards/<id>; staging: ROOT/shards/.inflight-<id>; an existing
//! staging directory blocks the job until an operator runs `quarantine`.
//! HEBC_YM_FRESH=1 refuses to reuse an existing shard (forces recomputation).
//! Sector matrices live in ROOT/matrices and are checked against the SHA-256
//! recorded by their `sector` shard before any job reads them.
//!
//! Job specs (slash separated, integers only):
//!   sector/LX/LY/SX/SY
//!   flatcomp/LX/LY/SX/SY
//!   cluster/LX/LY/SX/SY/JE/JB/WANT/GUARD
//!   count/LX/LY/SX/SY/JE/JB/T/FDIG/TOL          (shellschur, MAXSWEEP 4000)
//!   countcols/LX/LY/SX/SY/JE/JB/T/FDIG/TOL/A/B  (shellschur columns A..B-1)
//! usage: hebc_ym_http0 job ROOT SPEC | verify ROOT SPEC | cat ROOT SPEC |
//!        quarantine ROOT SPEC | serve ROOT PORT MAX_REQUESTS        json=0
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use hebc_finite_yang_mills::{hex, sha256};
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, Instant};

const MAX_HEADER: usize = 2048;
const RUNTIME_FIELDS: [&str; 2] = ["ms=", "elapsed_ms="];

struct Spec {
    kind: String,
    nums: Vec<i64>,
}

fn parse_spec(spec: &str) -> Result<Spec, String> {
    let mut parts = spec.trim_matches('/').split('/');
    let kind = parts.next().ok_or("empty spec")?.to_string();
    let nums: Vec<i64> = parts.map(|p| p.parse::<i64>().map_err(|_| format!("non-integer spec field {p}"))).collect::<Result<_, _>>()?;
    let want = match kind.as_str() {
        "sector" | "flatcomp" => 4,
        "cluster" => 8,
        "count" => 9,
        "countcols" => 11,
        _ => return Err(format!("unknown job kind {kind}")),
    };
    if nums.len() != want {
        return Err(format!("{kind} needs {want} integer fields"));
    }
    if !(2..=4).contains(&nums[0]) || !(2..=6).contains(&nums[1]) || nums[2].abs() != 1 || nums[3].abs() != 1 {
        return Err("lattice or sector out of range".into());
    }
    Ok(Spec { kind, nums })
}

fn canonical_spec(s: &Spec) -> String {
    let mut out = s.kind.clone();
    for n in &s.nums {
        out.push('/');
        out.push_str(&n.to_string());
    }
    out
}

fn shard_id(s: &Spec) -> String {
    canonical_spec(s).replace('/', "_")
}

fn tool(name: &str) -> Result<PathBuf, String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let p = exe.parent().ok_or("no exe dir")?.join(name);
    if !p.exists() {
        return Err(format!("tool {name} not built next to the backend"));
    }
    Ok(p)
}

fn matrix_path(root: &Path, s: &Spec) -> PathBuf {
    root.join("matrices").join(format!("s{}{}_{}_{}.matrix", s.nums[0], s.nums[1], s.nums[2], s.nums[3]))
}

fn file_sha(p: &Path) -> Result<String, String> {
    Ok(hex(&sha256(&fs::read(p).map_err(|e| format!("read {}: {e}", p.display()))?)))
}

/// The matrix a job reads must be the one its sector shard recorded.
fn checked_matrix(root: &Path, s: &Spec) -> Result<PathBuf, String> {
    let sec = Spec { kind: "sector".into(), nums: s.nums[..4].to_vec() };
    let hbp = root.join("shards").join(shard_id(&sec)).join("run.hbp");
    let text = fs::read_to_string(&hbp).map_err(|_| format!("missing sector shard for {}", canonical_spec(&sec)))?;
    let want = text
        .lines()
        .find_map(|l| l.strip_prefix("MATRIX_SHA|sha256=").and_then(|r| r.split('|').next()))
        .ok_or("sector shard lacks MATRIX_SHA")?
        .to_string();
    let m = matrix_path(root, s);
    let got = file_sha(&m)?;
    if got != want {
        return Err(format!("matrix sha mismatch for {}: {got} != {want}", m.display()));
    }
    Ok(m)
}

fn run_tool(name: &str, args: &[String], envs: &[(&str, String)]) -> Result<(String, Vec<(String, String)>), String> {
    let path = tool(name)?;
    let mut cmd = Command::new(&path);
    cmd.args(args);
    for (k, v) in envs {
        cmd.env(k, v);
    }
    let out = cmd.output().map_err(|e| format!("spawn {name}: {e}"))?;
    let stdout = String::from_utf8(out.stdout).map_err(|_| "non-utf8 tool output")?;
    let code = out.status.code().unwrap_or(-1);
    // sturmrs-family tools exit 2 for an AMBIGUOUS count: kept as a result, not a crash
    if code != 0 && code != 2 {
        return Err(format!("{name} exited {code}: {}", stdout.lines().last().unwrap_or("")));
    }
    let meta = vec![(format!("{name}_sha256"), file_sha(&path)?), (format!("{name}_exit"), code.to_string())];
    Ok((stdout, meta))
}

/// Execute one job; returns raw tool output lines (canonical + runtime fields)
/// and runtime metadata. Pure function of (spec, inputs in ROOT, tool binaries).
fn execute(root: &Path, s: &Spec) -> Result<(String, Vec<(String, String)>), String> {
    let n = &s.nums;
    let st = |k: usize| n[k].to_string();
    match s.kind.as_str() {
        "sector" => {
            fs::create_dir_all(root.join("matrices")).map_err(|e| e.to_string())?;
            let m = matrix_path(root, s);
            let tmp = m.with_extension("matrix.part");
            let (mut out, meta) = run_tool("ymsec", &[st(0), st(1), st(2), st(3), tmp.display().to_string()], &[])?;
            let sha = file_sha(&tmp)?;
            let bytes = fs::metadata(&tmp).map_err(|e| e.to_string())?.len();
            fs::rename(&tmp, &m).map_err(|e| e.to_string())?;
            out.push_str(&format!("MATRIX_SHA|sha256={sha}|bytes={bytes}|file={}|json=0\n", m.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "flatcomp" => run_tool("flatcomp", &[checked_matrix(root, s)?.display().to_string()], &[]),
        "cluster" => run_tool("cluster", &[checked_matrix(root, s)?.display().to_string(), st(4), st(5), st(6), st(7)], &[]),
        "count" | "countcols" => {
            let m = checked_matrix(root, s)?.display().to_string();
            let envs = if s.kind == "countcols" { vec![("SHELLSCHUR_COLS", format!("{}:{}", n[9], n[10]))] } else { vec![] };
            run_tool("shellschur", &[m, st(4), st(5), st(6), "-1".into(), st(7), st(8), "4000".into()], &envs)
        }
        _ => Err("unknown kind".into()),
    }
}

/// Split each line into canonical text and removed runtime fields.
fn canonicalize(raw: &str) -> (String, String) {
    let (mut hbp, mut measure) = (String::new(), String::new());
    for (k, line) in raw.lines().filter(|l| !l.is_empty()).enumerate() {
        let mut kept: Vec<&str> = Vec::new();
        for field in line.split('|') {
            if RUNTIME_FIELDS.iter().any(|p| field.starts_with(p)) {
                measure.push_str(&format!("MEASURE|line={k}|{field}|json=0\n"));
            } else {
                kept.push(field);
            }
        }
        hbp.push_str(&kept.join("|"));
        hbp.push('\n');
    }
    (hbp, measure)
}

fn index(hbp: &str) -> String {
    let (mut out, mut chain, mut off) = (String::new(), hex(&sha256(b"HEBC-YM-HBI-ROOT")), 0usize);
    for (k, line) in hbp.lines().enumerate() {
        let ls = hex(&sha256(line.as_bytes()));
        chain = hex(&sha256(format!("{chain}{ls}").as_bytes()));
        out.push_str(&format!("HBI|line={k}|offset={off}|len={}|sha={ls}|chain={chain}|json=0\n", line.len()));
        off += line.len() + 1;
    }
    out
}

fn write_shard(dir: &Path, spec: &str, raw: &str, meta: &[(String, String)], wall_ms: u128) -> Result<(String, String), String> {
    let (hbp, measure) = canonicalize(raw);
    let hbi = index(&hbp);
    let hs = hex(&sha256(hbp.as_bytes()));
    let anchor = format!("ANCHOR|spec={spec}|hbp_sha256={hs}|hbi_sha256={}|lines={}|json=0\n", hex(&sha256(hbi.as_bytes())), hbp.lines().count());
    let mut m = measure;
    for (k, v) in meta {
        m.push_str(&format!("MEASURE|{k}={v}|json=0\n"));
    }
    m.push_str(&format!("MEASURE|wall_ms={wall_ms}|json=0\n"));
    for (name, body) in [("run.hbp", &hbp), ("index.hbi", &hbi), ("run.anchor", &anchor), ("run.measure", &m), ("spec", &format!("{spec}\n"))] {
        fs::write(dir.join(name), body).map_err(|e| e.to_string())?;
    }
    Ok((hs, hbp))
}

fn staging(root: &Path, id: &str) -> PathBuf {
    root.join("shards").join(format!(".inflight-{id}"))
}

fn result_fields(hbp: &str) -> String {
    // short echo of the scientific verdicts for the response line
    let mut v: Vec<String> = Vec::new();
    for l in hbp.lines() {
        for f in l.split('|') {
            if ["negative=", "result=", "flat_states=", "sector_states=", "converged=", "w_self_adjoint="].iter().any(|p| f.starts_with(p)) {
                v.push(f.to_string());
            }
        }
    }
    v.join(",")
}

fn job(root: &Path, spec_text: &str) -> Result<String, String> {
    let s = parse_spec(spec_text)?;
    let spec = canonical_spec(&s);
    let id = shard_id(&s);
    let shards = root.join("shards");
    fs::create_dir_all(&shards).map_err(|e| e.to_string())?;
    let out = shards.join(&id);
    if out.exists() {
        if std::env::var("HEBC_YM_FRESH").as_deref() == Ok("1") {
            return Err(format!("shard {id} exists and HEBC_YM_FRESH=1 refuses to reuse it"));
        }
        return verify(root, spec_text).map(|l| l.replace("action=verify", "action=replay_existing"));
    }
    let stage = staging(root, &id);
    fs::create_dir(&stage).map_err(|_| format!("staging {id} exists: another writer or an interrupted run; operator must quarantine"))?;
    let t0 = Instant::now();
    let (raw, meta) = execute(root, &s)?;
    let (hs, hbp) = write_shard(&stage, &spec, &raw, &meta, t0.elapsed().as_millis())?;
    fs::rename(&stage, &out).map_err(|e| e.to_string())?;
    Ok(format!("HEBC_YM|result=PASS|action=run|spec={spec}|hbp_sha256={hs}|verdicts={}|json=0\n", result_fields(&hbp)))
}

fn verify(root: &Path, spec_text: &str) -> Result<String, String> {
    let s = parse_spec(spec_text)?;
    let spec = canonical_spec(&s);
    let id = shard_id(&s);
    let out = root.join("shards").join(&id);
    if !out.exists() {
        return Err(format!("no shard {id}"));
    }
    let tmp = root.join("shards").join(format!(".verify-{id}-{}", std::process::id()));
    fs::create_dir(&tmp).map_err(|e| e.to_string())?;
    let res = (|| -> Result<String, String> {
        // a sector re-run writes its matrix again; it must reproduce the same bytes
        let (raw, meta) = execute(root, &s)?;
        let (hs, hbp) = write_shard(&tmp, &spec, &raw, &meta, 0)?;
        for f in ["run.hbp", "index.hbi", "run.anchor"] {
            if fs::read(out.join(f)).map_err(|e| e.to_string())? != fs::read(tmp.join(f)).map_err(|e| e.to_string())? {
                return Err(format!("recomputed {f} differs for {spec}"));
            }
        }
        Ok(format!("HEBC_YM|result=PASS|action=verify|spec={spec}|hbp_sha256={hs}|compared=run.hbp,index.hbi,run.anchor|verdicts={}|json=0\n", result_fields(&hbp)))
    })();
    let _ = fs::remove_dir_all(&tmp);
    res
}

fn cat(root: &Path, spec_text: &str) -> Result<String, String> {
    let s = parse_spec(spec_text)?;
    fs::read_to_string(root.join("shards").join(shard_id(&s)).join("run.hbp")).map_err(|_| "no shard".into())
}

fn quarantine(root: &Path, spec_text: &str) -> Result<String, String> {
    let s = parse_spec(spec_text)?;
    let id = shard_id(&s);
    let stage = staging(root, &id);
    if !stage.exists() {
        return Err("no staging directory".into());
    }
    let mut k = 0u32;
    let q = loop {
        let q = root.join("shards").join(format!(".quarantine-{id}-{k}"));
        if !q.exists() {
            break q;
        }
        k += 1;
    };
    fs::rename(&stage, &q).map_err(|e| e.to_string())?;
    Ok(format!("HEBC_YM|result=PASS|action=quarantine|spec={}|moved_to={}|json=0\n", canonical_spec(&s), q.file_name().and_then(|f| f.to_str()).unwrap_or("")))
}

fn route(root: &Path, method: &str, path: &str) -> (u16, String) {
    if method == "GET" && path == "/health" {
        return (200, "HEBC_YM|health=OK|transport=HTTP/1.1|bind=127.0.0.1|json=0\n".into());
    }
    let (head, rest) = path.trim_start_matches('/').split_once('/').unwrap_or((path, ""));
    let r = match (method, head) {
        ("POST", "job") => job(root, rest),
        ("GET", "verify") => verify(root, rest),
        ("GET", "shard") => cat(root, rest),
        _ => return (404, "HEBC_YM|error=not_found|json=0\n".into()),
    };
    match r {
        Ok(body) => (200, body),
        Err(e) => (409, format!("HEBC_YM|result=FAIL|reason={}|json=0\n", e.replace('|', "/"))),
    }
}

fn request_line(stream: &mut TcpStream) -> Result<(String, String), String> {
    stream.set_read_timeout(Some(Duration::from_secs(3))).map_err(|e| e.to_string())?;
    let mut buf = [0u8; MAX_HEADER];
    let mut length = 0usize;
    loop {
        if length == buf.len() {
            return Err("oversized HTTP header".into());
        }
        let n = stream.read(&mut buf[length..]).map_err(|e| e.to_string())?;
        if n == 0 {
            return Err("truncated HTTP header".into());
        }
        length += n;
        if buf[..length].windows(4).any(|w| w == b"\r\n\r\n") {
            break;
        }
    }
    let head = std::str::from_utf8(&buf[..length]).map_err(|_| "non-utf8 HTTP")?;
    let line = head.split("\r\n").next().ok_or("missing request")?;
    let mut t = line.split_ascii_whitespace();
    let (method, path, version) = (t.next().ok_or("method")?, t.next().ok_or("path")?, t.next().ok_or("version")?);
    if t.next().is_some() || version != "HTTP/1.1" || !matches!(method, "GET" | "POST") || !path.starts_with('/') || path.contains('?') || path.contains("..") {
        return Err("invalid HTTP request".into());
    }
    for row in head.split("\r\n").skip(1) {
        let low = row.to_ascii_lowercase();
        if low.starts_with("transfer-encoding:") || (low.starts_with("content-length:") && low.trim() != "content-length: 0") {
            return Err("request body not supported".into());
        }
    }
    Ok((method.to_owned(), path.to_owned()))
}

fn handle(mut stream: TcpStream, root: &Path) -> Result<(), String> {
    let (status, body) = match request_line(&mut stream) {
        Ok((m, p)) => route(root, &m, &p),
        Err(_) => (400, "HEBC_YM|error=malformed_request|json=0\n".into()),
    };
    let reason = match status {
        200 => "200 OK",
        400 => "400 Bad Request",
        404 => "404 Not Found",
        _ => "409 Conflict",
    };
    let header = format!("HTTP/1.1 {reason}\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n", body.len());
    stream.write_all(header.as_bytes()).map_err(|e| e.to_string())?;
    stream.write_all(body.as_bytes()).map_err(|e| e.to_string())
}

fn serve(root: &Path, port: u16, max_requests: usize) -> Result<String, String> {
    if max_requests == 0 || max_requests > 10000 {
        return Err("max_requests bound: 1..10000".into());
    }
    let listener = TcpListener::bind(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    println!("HEBC_YM|server=READY|transport=HTTP/1.1|bind=127.0.0.1|port={port}|max_requests={max_requests}|json=0");
    for c in listener.incoming().take(max_requests) {
        match c {
            Ok(stream) => {
                if handle(stream, root).is_err() {
                    eprintln!("HEBC_YM|event=client_error|action=continue|json=0");
                }
            }
            Err(_) => eprintln!("HEBC_YM|event=accept_error|action=continue|json=0"),
        }
    }
    Ok("HEBC_YM|server=STOPPED|json=0\n".into())
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let r = (|| -> Result<String, String> {
        let root = Path::new(a.get(2).ok_or("missing ROOT")?);
        let spec = || a.get(3).ok_or_else(|| "missing SPEC".to_string());
        match a.get(1).map(String::as_str) {
            Some("job") => job(root, spec()?),
            Some("verify") => verify(root, spec()?),
            Some("cat") => cat(root, spec()?),
            Some("quarantine") => quarantine(root, spec()?),
            Some("serve") => {
                let port = a.get(3).and_then(|s| s.parse().ok()).ok_or("PORT")?;
                let maxr = a.get(4).and_then(|s| s.parse().ok()).ok_or("MAX_REQUESTS")?;
                serve(root, port, maxr)
            }
            _ => Err("usage: hebc_ym_http0 job|verify|cat|quarantine ROOT SPEC | serve ROOT PORT MAX_REQUESTS".into()),
        }
    })();
    match r {
        Ok(s) => print!("{s}"),
        Err(e) => {
            println!("HEBC_YM|result=FAIL|reason={}|json=0", e.replace('|', "/"));
            std::process::exit(1);
        }
    }
}
