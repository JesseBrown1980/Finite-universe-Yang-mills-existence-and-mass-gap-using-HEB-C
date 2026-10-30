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
//!   ddcore/LX/LY/SX/SY/JE/JB/T                  (diagonal-dominance core size at T)
//!   count/LX/LY/SX/SY/JE/JB/T/FDIG/TOL          (shellschur, MAXSWEEP 4000)
//!   countcols/LX/LY/SX/SY/JE/JB/T/FDIG/TOL/A/B  (shellschur columns A..B-1)
//!   countmerge/LX/LY/SX/SY/JE/JB/T/FDIG/TOL     (merge ROOT/scol/<count id>/*.hbp:
//!       the countcols shards' run.hbp files; every core entry exactly once)
//! Room-backed lane (zero momentum, Sx+Sy+ only: SX = SY = 1, no mode prefix):
//!   roomident/LX/LY/1/1     `ymroom text` compared byte for byte with the sector
//!       shard's matrix (builder identity gate P2)
//!   roombuild/LX/LY/1/1     `ymroom passa` + `ymroom build` into ROOT/rooms
//!   roomcount/LX/LY/1/1/JE/JB/T/FDIG/TOL          (roomschur, MAXSWEEP 4000)
//!   roomcountcols/LX/LY/1/1/JE/JB/T/FDIG/TOL/A/B  (roomschur columns A..B-1)
//!   roomcountmerge/LX/LY/1/1/JE/JB/T/FDIG/TOL     (merge ROOT/scol/<roomcount id>/)
//!   roomschur runs with ROOMSCHUR_K = 8 and ROOMSCHUR_BUDGET = 12 GiB; every room
//!   job checks the room file against the SHA-256 its roombuild shard recorded.
//! Static-charge lane (open ROWS x COLS strips, ymconf; CH = 1 charged std pair at (XA,row),(XB,row),
//! CH = 0 vacuum with XA = XB = 0):
//!   confmat/ROWS/COLS/XA/XB/CH                    build ROOT/matrices/conf_*.matrix
//!   confcount/ROWS/COLS/XA/XB/CH/JE/JB/T          sturmrs inertia count at T (milli-units)
//!   zconf                                         the sealed #56 perturbative calculation (zconfpt)
//! Wilson-loop lane (vacuum, rectangle on rows 0..1, columns X0..X1; diagonal JB M + LAM W):
//!   wilsonmat/ROWS/COLS/X0/X1/JB/LAM              build ROOT/matrices/wil_*.matrix (ymconf CH = 2)
//!   wilsoncount/ROWS/COLS/X0/X1/JB/LAM/JE/T       sturmrs at T with JE, JB = 1 (r = JB/JE, lambda = LAM/JE)
//!   wilsonseries/ROWS/COLS/METHOD/ORDER           exact strong-coupling series (ymwser; 0 orbit, 1 config)
//! Every other kind takes a sector-mode prefix: none (zero momentum), r (reflections
//! only, every momentum), or tx / ty / td / ta (translations along one line, the
//! sectors of V^K). Full space for a non-cyclic translation group by Mobius
//! inversion over the line subgroups: python/full_space_mobius.py.
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
const RUNTIME_FIELDS: [&str; 3] = ["ms=", "elapsed_ms=", "pass_ms="];
const ROOM_K: &str = "8";
const ROOM_BUDGET: u64 = 12 << 30;

struct Spec {
    kind: String,
    nums: Vec<i64>,
}

const MODES: [&str; 6] = ["tx", "ty", "td", "ta", "r", ""];
const BASES: [&str; 12] = ["sector", "flatcomp", "cluster", "countcols", "countmerge", "count", "ddcore", "roomident", "roombuild", "roomcountcols", "roomcountmerge", "roomcount"];

impl Spec {
    /// Sector mode prefix of the kind:
    /// "r" = reflection-only sectors (G = C2v, every momentum);
    /// "tx"/"ty"/"td"/"ta" = translations along one line (YMSEC_TRANS = x/y/d/a),
    /// sectors of V^K for K = that line of translations;
    /// "" = zero-momentum sectors (all translations).
    fn mode(&self) -> &str {
        MODES.iter().copied().find(|m| self.kind.strip_prefix(m).is_some_and(|b| BASES.contains(&b))).unwrap_or("")
    }
    fn base(&self) -> &str {
        &self.kind[self.mode().len()..]
    }
    fn with_base(&self, base: &str, nums: Vec<i64>) -> Spec {
        Spec { kind: format!("{}{base}", self.mode()), nums }
    }
    fn ymsec_env(&self) -> Vec<(&'static str, String)> {
        match self.mode() {
            "r" => vec![("YMSEC_REFLECTIONS_ONLY", "1".to_string())],
            "tx" => vec![("YMSEC_TRANS", "x".to_string())],
            "ty" => vec![("YMSEC_TRANS", "y".to_string())],
            "td" => vec![("YMSEC_TRANS", "d".to_string())],
            "ta" => vec![("YMSEC_TRANS", "a".to_string())],
            _ => vec![],
        }
    }
    fn matrix_prefix(&self) -> &str {
        match self.mode() {
            "" => "s",
            m => m,
        }
    }
}

const CONF_KINDS: [&str; 6] = ["confmat", "confcount", "zconf", "wilsonmat", "wilsoncount", "wilsonseries"];

fn parse_conf(kind: String, nums: Vec<i64>) -> Result<Spec, String> {
    if kind.starts_with("wilson") {
        let want = match kind.as_str() {
            "wilsonmat" => 6,
            "wilsoncount" => 8,
            _ => 4,
        };
        if nums.len() != want {
            return Err(format!("{kind} needs {want} integer fields"));
        }
        if kind == "wilsonseries" {
            if !(2..=3).contains(&nums[0]) || !(2..=4).contains(&nums[1]) || !(0..=1).contains(&nums[2]) || !(1..=6).contains(&nums[3]) {
                return Err("series geometry, method or order out of range".into());
            }
        } else if nums[0] != 2 || !(2..=5).contains(&nums[1]) || !(0 <= nums[2] && nums[2] < nums[3] && nums[3] < nums[1]) || nums[4] < 0 || (want == 8 && nums[6] <= 0) {
            return Err("wilson loop geometry or couplings out of range".into());
        }
        return Ok(Spec { kind, nums });
    }
    let want = match kind.as_str() {
        "confmat" => 5,
        "confcount" => 8,
        _ => 0,
    };
    if nums.len() != want {
        return Err(format!("{kind} needs {want} integer fields"));
    }
    if want > 0 {
        let (rows, cols, xa, xb, ch) = (nums[0], nums[1], nums[2], nums[3], nums[4]);
        let charged_ok = ch == 1 && 0 <= xa && xa < xb && xb < cols;
        let vacuum_ok = ch == 0 && xa == 0 && xb == 0;
        if !(2..=3).contains(&rows) || !(2..=5).contains(&cols) || !(charged_ok || vacuum_ok) {
            return Err("strip geometry out of range".into());
        }
        if want == 8 && (nums[5] <= 0 || nums[6] < 0) {
            return Err("JE must be positive and JB non-negative".into());
        }
    }
    Ok(Spec { kind, nums })
}

fn conf_matrix_path(root: &Path, s: &Spec) -> PathBuf {
    let n = &s.nums;
    root.join("matrices").join(format!("conf_{}_{}_{}_{}_{}.matrix", n[0], n[1], n[2], n[3], n[4]))
}

fn wil_matrix_path(root: &Path, s: &Spec) -> PathBuf {
    let n = &s.nums;
    root.join("matrices").join(format!("wil_{}_{}_{}_{}_{}_{}.matrix", n[0], n[1], n[2], n[3], n[4], n[5]))
}

/// The Wilson matrix a count reads must be the one its wilsonmat shard recorded.
fn checked_wil_matrix(root: &Path, s: &Spec) -> Result<PathBuf, String> {
    let m = Spec { kind: "wilsonmat".into(), nums: s.nums[..6].to_vec() };
    let hbp = root.join("shards").join(shard_id(&m)).join("run.hbp");
    let text = fs::read_to_string(&hbp).map_err(|_| format!("missing wilsonmat shard for {}", canonical_spec(&m)))?;
    let want = text
        .lines()
        .find_map(|l| l.strip_prefix("MATRIX_SHA|sha256=").and_then(|r| r.split('|').next()))
        .ok_or("wilsonmat shard lacks MATRIX_SHA")?
        .to_string();
    let p = wil_matrix_path(root, &m);
    let got = file_sha(&p)?;
    if got != want {
        return Err(format!("matrix sha mismatch for {}: {got} != {want}", p.display()));
    }
    Ok(p)
}

/// The strip matrix a count reads must be the one its confmat shard recorded.
fn checked_conf_matrix(root: &Path, s: &Spec) -> Result<PathBuf, String> {
    let m = Spec { kind: "confmat".into(), nums: s.nums[..5].to_vec() };
    let hbp = root.join("shards").join(shard_id(&m)).join("run.hbp");
    let text = fs::read_to_string(&hbp).map_err(|_| format!("missing confmat shard for {}", canonical_spec(&m)))?;
    let want = text
        .lines()
        .find_map(|l| l.strip_prefix("MATRIX_SHA|sha256=").and_then(|r| r.split('|').next()))
        .ok_or("confmat shard lacks MATRIX_SHA")?
        .to_string();
    let p = conf_matrix_path(root, &m);
    let got = file_sha(&p)?;
    if got != want {
        return Err(format!("matrix sha mismatch for {}: {got} != {want}", p.display()));
    }
    Ok(p)
}

fn parse_spec(spec: &str) -> Result<Spec, String> {
    let mut parts = spec.trim_matches('/').split('/');
    let kind = parts.next().ok_or("empty spec")?.to_string();
    let nums: Vec<i64> = parts.map(|p| p.parse::<i64>().map_err(|_| format!("non-integer spec field {p}"))).collect::<Result<_, _>>()?;
    if CONF_KINDS.contains(&kind.as_str()) {
        return parse_conf(kind, nums);
    }
    let mode = MODES.iter().copied().find(|m| kind.strip_prefix(m).is_some_and(|b| BASES.contains(&b))).ok_or(format!("unknown job kind {kind}"))?;
    let base = &kind[mode.len()..];
    let want = match base {
        "sector" | "flatcomp" | "roomident" | "roombuild" => 4,
        "ddcore" => 7,
        "cluster" => 8,
        "count" | "countmerge" | "roomcount" | "roomcountmerge" => 9,
        "countcols" | "roomcountcols" => 11,
        _ => return Err(format!("unknown job kind {kind}")),
    };
    if nums.len() != want {
        return Err(format!("{kind} needs {want} integer fields"));
    }
    if !(2..=4).contains(&nums[0]) || !(2..=6).contains(&nums[1]) || nums[2].abs() != 1 || nums[3].abs() != 1 {
        return Err("lattice or sector out of range".into());
    }
    if base.starts_with("room") && (!mode.is_empty() || nums[2] != 1 || nums[3] != 1 || nums[1] > 4 || nums[0] * nums[1] > 12) {
        return Err("room jobs are zero-momentum Sx+Sy+ only, LX*LY <= 12".into());
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
    root.join("matrices").join(format!("{}{}{}_{}_{}.matrix", s.matrix_prefix(), s.nums[0], s.nums[1], s.nums[2], s.nums[3]))
}

fn file_sha(p: &Path) -> Result<String, String> {
    Ok(hex(&sha256(&fs::read(p).map_err(|e| format!("read {}: {e}", p.display()))?)))
}

/// The matrix a job reads must be the one its sector shard recorded.
fn checked_matrix(root: &Path, s: &Spec) -> Result<PathBuf, String> {
    let sec = s.with_base("sector", s.nums[..4].to_vec());
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

fn rooms_dir(root: &Path) -> PathBuf {
    root.join("rooms")
}

fn room_path(root: &Path, s: &Spec) -> PathBuf {
    rooms_dir(root).join(format!("r{}{}_1_1.rooms", s.nums[0], s.nums[1]))
}

/// The room file a job streams must be the one its roombuild shard recorded.
fn checked_rooms(root: &Path, s: &Spec) -> Result<PathBuf, String> {
    let b = Spec { kind: "roombuild".into(), nums: s.nums[..4].to_vec() };
    let hbp = root.join("shards").join(shard_id(&b)).join("run.hbp");
    let text = fs::read_to_string(&hbp).map_err(|_| format!("missing roombuild shard for {}", canonical_spec(&b)))?;
    let want = text
        .lines()
        .find_map(|l| l.strip_prefix("ROOM_FILE|sha256=").and_then(|r| r.split('|').next()))
        .ok_or("roombuild shard lacks ROOM_FILE")?
        .to_string();
    let p = room_path(root, s);
    let got = file_sha(&p)?;
    if got != want {
        return Err(format!("room file sha mismatch for {}: {got} != {want}", p.display()));
    }
    Ok(p)
}

fn room_envs(cols: Option<(i64, i64)>, merge: Option<String>) -> Vec<(&'static str, String)> {
    let mut v = vec![("ROOMSCHUR_K", ROOM_K.to_string()), ("ROOMSCHUR_BUDGET", ROOM_BUDGET.to_string())];
    if let Some((a, b)) = cols {
        v.push(("ROOMSCHUR_COLS", format!("{a}:{b}")));
    }
    if let Some(m) = merge {
        v.push(("ROOMSCHUR_MERGE", m));
    }
    v
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
    match s.base() {
        "sector" => {
            fs::create_dir_all(root.join("matrices")).map_err(|e| e.to_string())?;
            let m = matrix_path(root, s);
            let tmp = m.with_extension("matrix.part");
            let env = s.ymsec_env();
            let (mut out, meta) = run_tool("ymsec", &[st(0), st(1), st(2), st(3), tmp.display().to_string()], &env)?;
            let sha = file_sha(&tmp)?;
            let bytes = fs::metadata(&tmp).map_err(|e| e.to_string())?.len();
            fs::rename(&tmp, &m).map_err(|e| e.to_string())?;
            out.push_str(&format!("MATRIX_SHA|sha256={sha}|bytes={bytes}|file={}|json=0\n", m.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "flatcomp" => run_tool("flatcomp", &[checked_matrix(root, s)?.display().to_string()], &[]),
        "ddcore" => run_tool("ddcore", &[checked_matrix(root, s)?.display().to_string(), st(4), st(5), st(6)], &[]),
        "cluster" => run_tool("cluster", &[checked_matrix(root, s)?.display().to_string(), st(4), st(5), st(6), st(7)], &[]),
        "count" | "countcols" => {
            let mp = checked_matrix(root, s)?;
            let m = mp.display().to_string();
            let envs = if s.base() == "countcols" { vec![("SHELLSCHUR_COLS", format!("{}:{}", n[9], n[10]))] } else { vec![] };
            let (mut out, meta) = run_tool("shellschur", &[m, st(4), st(5), st(6), "-1".into(), st(7), st(8), "4000".into()], &envs)?;
            if s.base() == "countcols" {
                // bind every SCOL record of this shard to the matrix that produced it
                out.push_str(&format!("INPUT_MATRIX|sha256={}|file={}|json=0\n", file_sha(&mp)?, mp.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            }
            Ok((out, meta))
        }
        "roomident" => {
            let mp = checked_matrix(root, s)?;
            fs::create_dir_all(rooms_dir(root)).map_err(|e| e.to_string())?;
            let tmp = rooms_dir(root).join(format!(".roomtext-{}", std::process::id()));
            let r = run_tool("ymroom", &["text".into(), st(0), st(1), tmp.display().to_string()], &[]);
            let room_sha = file_sha(&tmp);
            let room_bytes = fs::metadata(&tmp).map(|m| m.len());
            let _ = fs::remove_file(&tmp);
            let (mut out, meta) = r?;
            let (room_sha, room_bytes) = (room_sha?, room_bytes.map_err(|e| e.to_string())?);
            let msha = file_sha(&mp)?;
            let mbytes = fs::metadata(&mp).map_err(|e| e.to_string())?.len();
            out.push_str(&format!(
                "ROOM_IDENTITY|L={}x{}|sector=Sx+Sy+|ymsec_sha256={msha}|ymsec_bytes={mbytes}|ymroom_sha256={room_sha}|ymroom_bytes={room_bytes}|identical={}|json=0\n",
                n[0],
                n[1],
                u8::from(msha == room_sha && mbytes == room_bytes)
            ));
            Ok((out, meta))
        }
        "roombuild" => {
            fs::create_dir_all(rooms_dir(root)).map_err(|e| e.to_string())?;
            let rp = room_path(root, s);
            let pa = rp.with_extension("passa");
            let keys = rp.with_extension("keys");
            let tmp = rp.with_extension("rooms.part");
            let (mut out, mut meta) = run_tool("ymroom", &["passa".into(), st(0), st(1), pa.display().to_string()], &[])?;
            let states = fs::metadata(&pa).map_err(|e| e.to_string())?.len() / 16;
            let kf = fs::File::create(&keys).map_err(|e| e.to_string())?;
            kf.set_len(8 * states).map_err(|e| e.to_string())?;
            drop(kf);
            fs::File::create(&tmp).map_err(|e| e.to_string())?;
            let (out2, meta2) = run_tool("ymroom", &["build".into(), st(0), st(1), pa.display().to_string(), keys.display().to_string(), tmp.display().to_string(), "0".into()], &[])?;
            if !out2.contains("|w_self_adjoint=PASS|") || !out2.contains("|header_readback=EXACT|") {
                return Err("ymroom build did not report w_self_adjoint=PASS and header_readback=EXACT".into());
            }
            out.push_str(&out2);
            meta.extend(meta2);
            let sha = file_sha(&tmp)?;
            let bytes = fs::metadata(&tmp).map_err(|e| e.to_string())?.len();
            fs::rename(&tmp, &rp).map_err(|e| e.to_string())?;
            out.push_str(&format!("ROOM_FILE|sha256={sha}|bytes={bytes}|file={}|json=0\n", rp.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "roomcount" | "roomcountcols" => {
            let rp = checked_rooms(root, s)?;
            let cols = if s.base() == "roomcountcols" { Some((n[9], n[10])) } else { None };
            let (mut out, meta) = run_tool("roomschur", &[rp.display().to_string(), "0".into(), st(4), st(5), st(6), st(7), st(8), "4000".into()], &room_envs(cols, None))?;
            if cols.is_some() {
                out.push_str(&format!("INPUT_ROOMS|sha256={}|file={}|json=0\n", file_sha(&rp)?, rp.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            }
            Ok((out, meta))
        }
        "roomcountmerge" => {
            let rp = checked_rooms(root, s)?;
            let rsha = file_sha(&rp)?;
            let bind = format!("INPUT_ROOMS|sha256={rsha}|file={}|json=0", rp.file_name().and_then(|f| f.to_str()).unwrap_or(""));
            let (inputs, listing) = merge_inputs(root, s, "roomcount", "roomcountcols", &bind)?;
            let mut files: Vec<String> = Vec::new();
            for (k, body) in inputs.iter().enumerate() {
                let f = root.join("scol").join(format!(".merge-input-{}-{k}.hbp", std::process::id()));
                fs::write(&f, body).map_err(|e| e.to_string())?;
                files.push(f.display().to_string());
            }
            let r = run_tool("roomschur", &[rp.display().to_string(), "0".into(), st(4), st(5), st(6), st(7), st(8), "4000".into()], &room_envs(None, Some(files.join(","))));
            for f in &files {
                let _ = fs::remove_file(f);
            }
            let (out, meta) = r?;
            Ok((format!("{listing}{bind}\n{out}"), meta))
        }
        "countmerge" => {
            let mp = checked_matrix(root, s)?;
            let msha = file_sha(&mp)?;
            let bind = format!("INPUT_MATRIX|sha256={msha}|file={}|json=0", mp.file_name().and_then(|f| f.to_str()).unwrap_or(""));
            let (inputs, listing) = merge_inputs(root, s, "count", "countcols", &bind)?;
            let mut files: Vec<String> = Vec::new();
            for (k, body) in inputs.iter().enumerate() {
                let f = root.join("scol").join(format!(".merge-input-{}-{k}.hbp", std::process::id()));
                fs::write(&f, body).map_err(|e| e.to_string())?;
                files.push(f.display().to_string());
            }
            let r = run_tool("shellschur", &[mp.display().to_string(), st(4), st(5), st(6), "-1".into(), st(7), st(8), "4000".into()], &[("SHELLSCHUR_MERGE", files.join(","))]);
            for f in &files {
                let _ = fs::remove_file(f);
            }
            let (out, meta) = r?;
            Ok((format!("{listing}INPUT_MATRIX|sha256={msha}|file={}|json=0\n{out}", mp.file_name().and_then(|f| f.to_str()).unwrap_or("")), meta))
        }
        "confmat" => {
            fs::create_dir_all(root.join("matrices")).map_err(|e| e.to_string())?;
            let m = conf_matrix_path(root, s);
            let tmp = m.with_extension("matrix.part");
            let (mut out, meta) = run_tool("ymconf", &[st(0), st(1), st(2), st(3), st(4), tmp.display().to_string()], &[])?;
            if !out.contains("|w_self_adjoint=PASS|") {
                return Err("ymconf did not report w_self_adjoint=PASS".into());
            }
            let sha = file_sha(&tmp)?;
            let bytes = fs::metadata(&tmp).map_err(|e| e.to_string())?.len();
            fs::rename(&tmp, &m).map_err(|e| e.to_string())?;
            out.push_str(&format!("MATRIX_SHA|sha256={sha}|bytes={bytes}|file={}|json=0\n", m.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "confcount" => {
            let mp = checked_conf_matrix(root, s)?;
            let (mut out, meta) = run_tool("sturmrs", &[mp.display().to_string(), st(5), st(6), st(7)], &[])?;
            out.push_str(&format!("INPUT_MATRIX|sha256={}|file={}|json=0\n", file_sha(&mp)?, mp.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "zconf" => run_tool("zconfpt", &[], &[]),
        "wilsonmat" => {
            fs::create_dir_all(root.join("matrices")).map_err(|e| e.to_string())?;
            let m = wil_matrix_path(root, s);
            let tmp = m.with_extension("matrix.part");
            let (mut out, meta) = run_tool("ymconf", &[st(0), st(1), st(2), st(3), "2".into(), tmp.display().to_string(), st(4), st(5)], &[])?;
            if !out.contains("|w_self_adjoint=PASS|") {
                return Err("ymconf did not report w_self_adjoint=PASS".into());
            }
            let sha = file_sha(&tmp)?;
            let bytes = fs::metadata(&tmp).map_err(|e| e.to_string())?.len();
            fs::rename(&tmp, &m).map_err(|e| e.to_string())?;
            out.push_str(&format!("MATRIX_SHA|sha256={sha}|bytes={bytes}|file={}|json=0\n", m.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "wilsoncount" => {
            let mp = checked_wil_matrix(root, s)?;
            let (mut out, meta) = run_tool("sturmrs", &[mp.display().to_string(), st(6), "1".into(), st(7)], &[])?;
            out.push_str(&format!("INPUT_MATRIX|sha256={}|file={}|json=0\n", file_sha(&mp)?, mp.file_name().and_then(|f| f.to_str()).unwrap_or("")));
            Ok((out, meta))
        }
        "wilsonseries" => run_tool("ymwser", &[st(0), st(1), st(2), st(3)], &[]),
        _ => Err("unknown kind".into()),
    }
}

/// Collect the countcols shards for a countmerge job from ROOT/scol/<count id>/<shard dirs>.
/// Each must: pass shard integrity (index.hbi and run.anchor regenerated from
/// run.hbp, byte for byte); carry the same count parameters in its spec; record
/// INPUT_MATRIX equal to the merge's matrix SHA-256; and the column ranges must
/// partition 0..core exactly. Returns the run.hbp bodies and a canonical listing
/// of the inputs (spec + run.hbp SHA-256, in column order).
fn merge_inputs(root: &Path, s: &Spec, count_base: &str, cols_base: &str, bind: &str) -> Result<(Vec<String>, String), String> {
    let cs = s.with_base(count_base, s.nums.clone());
    let dir = root.join("scol").join(shard_id(&cs));
    let mut items: Vec<(i64, i64, String, String)> = Vec::new();
    let mut core: Option<i64> = None;
    for e in fs::read_dir(&dir).map_err(|_| format!("missing {}", dir.display()))? {
        let p = e.map_err(|e| e.to_string())?.path();
        if !p.is_dir() {
            continue;
        }
        let rd = |f: &str| fs::read_to_string(p.join(f)).map_err(|_| format!("{} lacks {f}", p.display()));
        let (hbp, hbi, anchor, spec) = (rd("run.hbp")?, rd("index.hbi")?, rd("run.anchor")?, rd("spec")?);
        let spec = spec.trim().to_string();
        let want_anchor = format!("ANCHOR|spec={spec}|hbp_sha256={}|hbi_sha256={}|lines={}|json=0\n", hex(&sha256(hbp.as_bytes())), hex(&sha256(index(&hbp).as_bytes())), hbp.lines().count());
        if index(&hbp) != hbi || want_anchor != anchor {
            return Err(format!("countcols shard {} fails integrity", p.display()));
        }
        let ps = parse_spec(&spec)?;
        if ps.kind != s.with_base(cols_base, vec![]).kind || ps.nums[..9] != s.nums[..] {
            return Err(format!("shard {spec} is not a {cols_base} shard of this count"));
        }
        if !hbp.lines().any(|l| l == bind) {
            return Err(format!("shard {spec} was not produced from the bound input ({bind})"));
        }
        let c: i64 = hbp
            .lines()
            .find(|l| l.starts_with("SHELL_SCHUR_COLS|"))
            .and_then(|l| l.split('|').find_map(|f| f.strip_prefix("core=")))
            .and_then(|v| v.parse().ok())
            .ok_or(format!("shard {spec} lacks SHELL_SCHUR_COLS core"))?;
        if core.is_some_and(|x| x != c) {
            return Err("countcols shards disagree on core size".into());
        }
        core = Some(c);
        items.push((ps.nums[9], ps.nums[10].min(c), spec, hbp));
    }
    items.sort();
    let core = core.ok_or("no countcols shards to merge")?;
    let mut next = 0i64;
    for (a, b, spec, _) in &items {
        if *a != next || b <= a {
            return Err(format!("column ranges do not partition 0..{core} at {spec}"));
        }
        next = *b;
    }
    if next != core {
        return Err(format!("column ranges end at {next}, core is {core}"));
    }
    let mut listing = String::new();
    for (a, b, spec, hbp) in &items {
        listing.push_str(&format!("MERGE_INPUT|cols={a}:{b}|spec={spec}|hbp_sha256={}|json=0\n", hex(&sha256(hbp.as_bytes()))));
    }
    Ok((items.into_iter().map(|t| t.3).collect(), listing))
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
            if ["negative=", "result=", "flat_states=", "sector_states=", "converged=", "w_self_adjoint=", "identical="].iter().any(|p| f.starts_with(p)) {
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
    let (raw, meta) = match execute(root, &s) {
        Ok(x) => x,
        Err(e) => {
            // a clean, reported failure leaves nothing in staging: remove it only
            // if it is empty (anything written there is kept for quarantine)
            let _ = fs::remove_dir(&stage);
            return Err(e);
        }
    };
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
