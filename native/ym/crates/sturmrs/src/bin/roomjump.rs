//! roomjump: `roomschur` with three changes, everything else copied unchanged.
//! Integer-only, Rust 1.81, json=0. `roomschur.rs` itself is not modified (its
//! source hash is pinned by the memory-pilot workflow).
//!
//! 1. Read-ahead. A reader thread reads the next 64 MiB chunk and computes its
//!    16 MiB SHA-256 leaves while the current chunk is swept. Rows, their order
//!    and the payload merkle are exactly roomschur's.
//! 2. Interleaved enclosures. lo/hi of a state sit side by side ([i64; 2]), so a
//!    neighbour read touches one cache line instead of two. Same arithmetic.
//! 3. Jump-and-certify (ROOMJUMP_EVERY=J, 0 = off). Every J sweeps a column
//!    extrapolates the midpoints of its enclosures (scalar Aitken on the
//!    successive-difference norms) to a point x, then certifies x by one
//!    streamed residual pass: r = b*F - A_HH x exactly, R = max|r_h|, and since
//!    A_HH is strictly diagonally dominant with margin mu = H_min_margin
//!    (computed in pass 1, the same constant that bounds the starting box),
//!        |y* - x|_inf <= R / mu.
//!    Proof: take h with |e_h| maximal for e = y* - x; then A e = r gives
//!    |r_h| >= d_h|e_h| - sum_j |a_hj||e_j| >= mu |e_h|.
//!    The box x +- ceil(R/mu) is intersected with the Gauss-Seidel box. A bad
//!    jump only gives a wide box (AMBIGUOUS later), never a wrong one. An empty
//!    intersection stops the run as an arithmetic inconsistency.
//!    Timer hash: each column keeps a chain
//!      chain = sha256(chain | t=pass | sweep | kind | q | x_merkle | R | radius | box_merkle)
//!    over a process-wide pass clock t, and ROOMJUMP_CLOCK seals all chains.
//!
//! usage and every other environment variable: as roomschur. With jump on,
//! COL_BYTES = 24*n (enclosure pair + one midpoint vector).
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{Signed, Zero};
use std::io::{Read, Seek, SeekFrom};
use std::time::Instant;

#[path = "../../../torusl/src/sha.rs"]
mod sha;

#[allow(dead_code)]
#[path = "../../../torusl/src/segio.rs"]
mod segio;

type Iv = (BigInt, BigInt);

// ---- copied unchanged from shellschur.rs ----
fn cdiv(a: &BigInt, b: &BigInt) -> BigInt {
    -((-a).div_floor(b))
}
fn quotient(x: &Iv, y: &Iv, d: &Iv) -> Result<Iv, String> {
    if !d.0.is_positive() && !d.1.is_negative() {
        return Err("pivot interval contains zero".into());
    }
    let p = [&x.0 * &y.0, &x.0 * &y.1, &x.1 * &y.0, &x.1 * &y.1];
    let mut lo = p.iter().min().cloned().unwrap_or_default();
    let mut hi = p.iter().max().cloned().unwrap_or_default();
    let (mut dlo, mut dhi) = (d.0.clone(), d.1.clone());
    if dhi.is_negative() {
        let (l, h) = (-hi, -lo);
        lo = l;
        hi = h;
        let (a, b) = (-dhi, -dlo);
        dlo = a;
        dhi = b;
    }
    Ok(if !lo.is_negative() {
        (lo.div_floor(&dhi), cdiv(&hi, &dlo))
    } else if !hi.is_positive() {
        (lo.div_floor(&dlo), cdiv(&hi, &dhi))
    } else {
        (lo.div_floor(&dlo), cdiv(&hi, &dlo))
    })
}
fn ck(o: Option<i128>) -> Result<i128, String> {
    o.ok_or_else(|| "i128 overflow".to_string())
}
fn imul(lo: i128, hi: i128, c: i128) -> Result<(i128, i128), String> {
    let (a, b) = (ck(lo.checked_mul(c))?, ck(hi.checked_mul(c))?);
    Ok(if a <= b { (a, b) } else { (b, a) })
}
fn floor_div(a: i128, d: i128) -> i128 {
    Integer::div_floor(&a, &d)
}
fn ceil_div(a: i128, d: i128) -> i128 {
    -Integer::div_floor(&(-a), &d)
}
fn dense_inertia(mut s: Vec<Vec<Iv>>) -> (usize, usize, usize, bool) {
    let m = s.len();
    let mut alive = vec![true; m];
    let (mut neg, mut pos) = (0usize, 0usize);
    for step in 0..m {
        let mut best: Option<(usize, BigInt)> = None;
        for k in 0..m {
            if !alive[k] {
                continue;
            }
            let d = &s[k][k];
            let mag = if d.0.is_positive() {
                d.0.clone()
            } else if d.1.is_negative() {
                -d.1.clone()
            } else {
                continue;
            };
            if best.as_ref().map_or(true, |(_, b)| mag > *b) {
                best = Some((k, mag));
            }
        }
        let Some((k, _)) = best else { return (neg, pos, step, false) };
        alive[k] = false;
        let d = s[k][k].clone();
        if d.1.is_negative() {
            neg += 1;
        } else {
            pos += 1;
        }
        let live: Vec<usize> = (0..m).filter(|&i| alive[i]).collect();
        for (x, &i) in live.iter().enumerate() {
            for &j in &live[x..] {
                let Ok(c) = quotient(&s[i][k], &s[k][j], &d) else { return (neg, pos, step, false) };
                let o = s[i][j].clone();
                let v: Iv = (o.0 - &c.1, o.1 - &c.0);
                s[i][j] = v.clone();
                s[j][i] = v;
            }
        }
    }
    (neg, pos, m, true)
}
// ---- end of copy ----

const CHUNK: usize = 64 * 1_048_576;
const LEAF: usize = 16 * 1_048_576;
const QSHIFT: u32 = 32;
const QMAX: i128 = 1 << 40;

struct Hdr {
    n: usize,
    payload: u64,
    merkle: String,
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

fn read_hdr(dev: &mut segio::Dev, off: u64) -> Result<Hdr, String> {
    let mut blk = vec![0u8; 4096];
    dev.seek(SeekFrom::Start(off)).map_err(|e| format!("seek: {e}"))?;
    dev.read_exact(&mut blk).map_err(|e| format!("read header: {e}"))?;
    let end = blk.iter().position(|&b| b == b'\n').ok_or("no header line")?;
    let line = String::from_utf8_lossy(&blk[..end]).to_string();
    if !line.starts_with("YMROOMHDR|") || field(&line, "w_self_adjoint=") != Some("PASS") {
        return Err("not a YMROOMHDR stream with w_self_adjoint=PASS".into());
    }
    let p = |k: &str| field(&line, k).and_then(|v| v.parse::<u64>().ok()).ok_or_else(|| format!("missing {k}"));
    Ok(Hdr { n: usize::try_from(p("n=")?).map_err(|_| "n")?, payload: p("payload_bytes=")?, merkle: field(&line, "payload_merkle=").unwrap_or("").to_string() })
}

/// One streamed row: w, mag, entries (j, z) including the diagonal.
struct Row<'a> {
    w: i128,
    mag: i128,
    ent: &'a [u8],
}

type Chunk = Result<(Vec<u8>, String), String>;

/// Stream every row in index order, calling `f(h, rows)` for each complete chunk
/// of rows. A reader thread reads and hashes the next chunk meanwhile; the
/// 16 MiB SHA-256 merkle of the payload is recomputed exactly as roomschur does.
fn stream<F: FnMut(usize, &[Row])>(dev: &mut segio::Dev, off: u64, hdr: &Hdr, mut f: F) -> Result<(u64, String), String> {
    dev.seek(SeekFrom::Start(off + 4096)).map_err(|e| format!("seek: {e}"))?;
    let payload = hdr.payload;
    std::thread::scope(|sc| {
        let (tx, rx) = std::sync::mpsc::sync_channel::<Chunk>(1);
        let devr = &mut *dev;
        sc.spawn(move || {
            let mut left = payload;
            while left > 0 {
                let Ok(take) = usize::try_from(left.min(CHUNK as u64)) else {
                    let _ = tx.send(Err("chunk".into()));
                    return;
                };
                let mut buf = vec![0u8; take];
                if let Err(e) = devr.read_exact(&mut buf) {
                    let _ = tx.send(Err(format!("read rooms: {e}")));
                    return;
                }
                let mut hx = String::with_capacity(64 * take.div_ceil(LEAF));
                for c in buf.chunks(LEAF) {
                    hx.push_str(&sha::sha256_hex(c));
                }
                left -= take as u64;
                if tx.send(Ok((buf, hx))).is_err() {
                    return;
                }
            }
        });
        let mut carry: Vec<u8> = Vec::new();
        let mut shas: Vec<u8> = Vec::new();
        let mut h = 0usize;
        let mut read = 0u64;
        for msg in rx {
            let (buf, hx) = msg?;
            read += buf.len() as u64;
            shas.extend_from_slice(hx.as_bytes());
            carry.extend_from_slice(&buf);
            drop(buf);
            let mut rows: Vec<Row> = Vec::new();
            let mut p = 0usize;
            while h + rows.len() < hdr.n && p + 8 <= carry.len() {
                let w = u32::from_le_bytes(carry[p..p + 4].try_into().unwrap_or([0; 4]));
                let mag = u16::from_le_bytes(carry[p + 4..p + 6].try_into().unwrap_or([0; 2]));
                let cnt = usize::from(u16::from_le_bytes(carry[p + 6..p + 8].try_into().unwrap_or([0; 2])));
                if p + 8 + 8 * cnt > carry.len() {
                    break;
                }
                rows.push(Row { w: i128::from(w), mag: i128::from(mag), ent: &carry[p + 8..p + 8 + 8 * cnt] });
                p += 8 + 8 * cnt;
            }
            let got = rows.len();
            f(h, &rows);
            h += got;
            drop(rows);
            carry.drain(..p);
        }
        if read != payload {
            return Err(format!("stream read {read} of {payload} bytes"));
        }
        if h != hdr.n {
            return Err(format!("stream ended at row {h} of {}", hdr.n));
        }
        Ok((read, sha::sha256_hex(&shas)))
    })
}

fn ent(e: &[u8], k: usize) -> (usize, i128) {
    let j = u32::from_le_bytes(e[8 * k..8 * k + 4].try_into().unwrap_or([0; 4]));
    let z = i32::from_le_bytes(e[8 * k + 4..8 * k + 8].try_into().unwrap_or([0; 4]));
    (j as usize, i128::from(z))
}

/// Gauss-Seidel state of one core column.
struct Col {
    cb: usize,
    c: usize,
    b: Vec<(usize, i128)>, // B_{H,c}, ascending h
    bp: usize,
    iv: Vec<[i64; 2]>, // [lo, hi] per state
    sweeps: usize,
    width: i128,
    active: bool,
    err: Option<String>,
    // jump-and-certify
    pm: Vec<i64>, // previous midpoints, or the jump point while a certificate is pending
    nprev: Option<i128>,
    cert: bool,
    q: i128,
    rmax: i128,
    certs: usize,
    jumps: usize,
    chain: String,
}

fn to64(v: i128) -> Result<i64, String> {
    i64::try_from(v).map_err(|_| "enclosure outside i64".to_string())
}

fn mid(p: [i64; 2]) -> i64 {
    // floor((lo+hi)/2) of two i64 values always fits i64
    i64::try_from(floor_div(i128::from(p[0]) + i128::from(p[1]), 2)).unwrap_or(0)
}

/// 16 MiB leaf SHA-256 merkle of a vector's little-endian bytes.
fn merkle_bytes<I: Iterator<Item = i64>>(it: I) -> String {
    let mut leaf: Vec<u8> = Vec::with_capacity(LEAF);
    let mut hx = String::new();
    for v in it {
        leaf.extend_from_slice(&v.to_le_bytes());
        if leaf.len() == LEAF {
            hx.push_str(&sha::sha256_hex(&leaf));
            leaf.clear();
        }
    }
    if !leaf.is_empty() {
        hx.push_str(&sha::sha256_hex(&leaf));
    }
    sha::sha256_hex(hx.as_bytes())
}

fn run() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 6 {
        return Err("usage: roomjump DEV OFFSET JE JB TN [FDIG=9] [TOL=1000] [MAXSWEEP=400]".into());
    }
    let p = |k: usize, def: i128| a.get(k).and_then(|s| s.parse::<i128>().ok()).unwrap_or(def);
    let off: u64 = a[2].parse().map_err(|_| "bad OFFSET")?;
    let (je, jb, tn) = (p(3, 0), p(4, 0), p(5, 0));
    let shell_max: i128 = -1;
    let fdig = u32::try_from(p(6, 9)).map_err(|_| "bad FDIG")?;
    let tol = p(7, 1000);
    let maxsweep = usize::try_from(p(8, 400)).map_err(|_| "bad MAXSWEEP")?;
    let every: usize = std::env::var("ROOMJUMP_EVERY").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
    let point: usize = std::env::var("ROOMJUMP_POINT").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
    let jm = every > 0 || point > 0;
    let stop: i128 = std::env::var("ROOMJUMP_STOP").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
    let f: i128 = 10i128.pow(fdig);
    let t0 = Instant::now();
    let mut dev = segio::open(&a[1], false).map_err(|e| format!("open {}: {e}", a[1]))?;
    let hdr = read_hdr(&mut dev, off)?;
    let n = hdr.n;
    let mut clock = 0usize; // process-wide pass counter (the timer)
    // pass 0: diagonal, full off-diagonal sums, core, core rows kept in RAM
    let mut diag = vec![0i128; n];
    let mut core = vec![false; n];
    let mut rows_read_ms = Vec::new();
    let tp = Instant::now();
    let (bytes0, merkle0) = stream(&mut dev, off, &hdr, |h0, rows| {
        for (d, r) in rows.iter().enumerate() {
            let h = h0 + d;
            let mut dg = 1000 * jb * r.mag * r.w - tn * r.w;
            let mut off_sum = 0i128;
            for k in 0..r.ent.len() / 8 {
                let (j, z) = ent(r.ent, k);
                let v = 1000 * je * r.w * z;
                if j == h {
                    dg += v;
                } else {
                    off_sum += v.abs();
                }
            }
            diag[h] = dg;
            core[h] = dg - off_sum <= 0 || r.mag <= shell_max;
        }
    })?;
    clock += 1;
    if merkle0 != hdr.merkle {
        return Err(format!("payload merkle mismatch: header {} stream {merkle0}", hdr.merkle));
    }
    rows_read_ms.push(tp.elapsed().as_millis());
    let cidx: Vec<usize> = (0..n).filter(|&k| core[k]).collect();
    let m = cidx.len();
    // pass 1: margins inside H, core rows (off-diagonal entries) for b and S
    let mut core_rows: Vec<Vec<(usize, i128)>> = vec![Vec::new(); m];
    let mut cpos = vec![usize::MAX; n];
    for (q, &k) in cidx.iter().enumerate() {
        cpos[k] = q;
    }
    let mut min_margin: Option<i128> = None;
    let mut worst_num = 0i128;
    let mut bad_row: Option<usize> = None;
    let tp = Instant::now();
    stream(&mut dev, off, &hdr, |h0, rows| {
        for (d, r) in rows.iter().enumerate() {
            let h = h0 + d;
            if core[h] {
                for k in 0..r.ent.len() / 8 {
                    let (j, z) = ent(r.ent, k);
                    if j != h {
                        core_rows[cpos[h]].push((j, 1000 * je * r.w * z));
                    }
                }
                continue;
            }
            let mut off_h = 0i128;
            for k in 0..r.ent.len() / 8 {
                let (j, z) = ent(r.ent, k);
                if j != h && !core[j] {
                    off_h += (1000 * je * r.w * z).abs();
                }
            }
            let mg = diag[h] - off_h;
            if mg <= 0 && bad_row.is_none() {
                bad_row = Some(h);
            }
            min_margin = Some(min_margin.map_or(mg, |x: i128| x.min(mg)));
            worst_num = worst_num.max(ceil_div(1000 * off_h, diag[h]));
        }
    })?;
    clock += 1;
    rows_read_ms.push(tp.elapsed().as_millis());
    if let Some(h) = bad_row {
        return Err(format!("row {h} not dominant inside H"));
    }
    let min_margin = min_margin.ok_or("H is empty")?;
    let core_fp = cidx.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, &k| (h ^ (k as u64)).wrapping_mul(0x0100_0000_01b3));
    let tag = format!("n={n}|JE={je}|JB={jb}|t_milli={tn}|shell_max={shell_max}|core={m}|core_fp={core_fp:016x}|F=10^{fdig}");
    let mut s_lo = vec![vec![0i128; m]; m];
    let mut s_hi = vec![vec![0i128; m]; m];
    let (mut sweeps_max, mut width_max) = (0usize, 0i128);
    let (mut sweep_passes, mut cert_passes, mut point_passes) = (0usize, 0usize, 0usize);
    let mut chains: Vec<(usize, String)> = Vec::new();
    if let Ok(files) = std::env::var("ROOMSCHUR_MERGE") {
        let mut seen = vec![vec![false; m]; m];
        for path in files.split(',') {
            let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
            for line in text.lines().filter(|l| l.starts_with("SCOL|")) {
                if !line.contains(&format!("|{tag}|")) {
                    return Err(format!("SCOL line from a different run in {path}"));
                }
                let fld = |k: &str| -> Result<i128, String> { field(line, k).and_then(|v| v.parse().ok()).ok_or_else(|| format!("missing {k}")) };
                let (cb, ca) = (usize::try_from(fld("cb=")?).map_err(|_| "cb")?, usize::try_from(fld("ca=")?).map_err(|_| "ca")?);
                if cb >= m || ca >= m || seen[ca][cb] {
                    return Err(format!("SCOL record out of range or duplicate ca={ca} cb={cb}"));
                }
                s_lo[ca][cb] = fld("lo=")?;
                s_hi[ca][cb] = fld("hi=")?;
                seen[ca][cb] = true;
                sweeps_max = sweeps_max.max(usize::try_from(fld("sweeps=")?).unwrap_or(0));
                width_max = width_max.max(fld("ywidth=")?);
            }
        }
        if seen.iter().any(|row| row.iter().any(|x| !x)) {
            return Err("merge is missing SCOL records (every core entry is required)".into());
        }
    } else {
        let (ca0, cb1) = match std::env::var("ROOMSCHUR_COLS").ok().and_then(|v| v.split_once(':').map(|(x, y)| (x.parse::<usize>(), y.parse::<usize>()))) {
            Some((Ok(x), Ok(y))) => (x.min(m), y.min(m)),
            _ => (0, m),
        };
        let kcols: usize = std::env::var("ROOMSCHUR_K").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
        let budget: u128 = std::env::var("ROOMSCHUR_BUDGET").ok().and_then(|v| v.parse().ok()).ok_or("ROOMSCHUR_BUDGET (bytes) is required")?;
        // one more chunk in flight than roomschur (reader thread + channel slot)
        let reserve: u128 = (n as u128) * (16 + 16 + 1 + 8) + 5 * (CHUNK as u128);
        let col_bytes: u128 = (if jm { 24 } else { 16 }) * (n as u128);
        let cap = budget.saturating_sub(reserve) / col_bytes;
        let projected = (kcols as u128) * col_bytes + reserve;
        println!("ROOMSCHUR_ADMISSION|BUDGET={budget}|RESERVE={reserve}|COL_BYTES={col_bytes}|CAP={cap}|K={kcols}|projected={projected}|admitted={}|json=0", u8::from(projected <= budget));
        if projected > budget {
            return Err("admission refused: K*COL_BYTES + RESERVE > BUDGET".into());
        }
        if jm {
            println!("ROOMJUMP_MODE|every={every}|point={point}|stop={stop}|H_min_margin={min_margin}|qshift={QSHIFT}|qmax=2^40|json=0");
        }
        let threads: usize = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
        let mut cb = ca0;
        while cb < cb1 {
            let cbe = (cb + kcols).min(cb1);
            let mut cols: Vec<Col> = (cb..cbe)
                .map(|q| {
                    let c = cidx[q];
                    let b: Vec<(usize, i128)> = core_rows[q].iter().copied().filter(|&(h, _)| !core[h]).collect();
                    Col {
                        cb: q,
                        c,
                        b,
                        bp: 0,
                        iv: vec![[0; 2]; n],
                        sweeps: 0,
                        width: 0,
                        active: true,
                        err: None,
                        pm: if jm { vec![0; n] } else { Vec::new() },
                        nprev: None,
                        cert: false,
                        q: 0,
                        rmax: 0,
                        certs: 0,
                        jumps: 0,
                        chain: sha::sha256_hex(format!("{tag}|cb={q}").as_bytes()),
                    }
                })
                .collect();
            for col in &mut cols {
                let bmax = col.b.iter().map(|&(_, v)| v.abs()).max().unwrap_or(0);
                let beta = ceil_div(ck(bmax.checked_mul(f))?, min_margin);
                let b64 = to64(beta)?;
                for (pv, &cr) in col.iv.iter_mut().zip(core.iter()) {
                    if !cr {
                        *pv = [-b64, b64];
                    }
                }
                col.width = 2 * beta;
            }
            if point > 0 {
                // point mode: cheap Gauss-Seidel on the midpoint vector alone, then
                // one certificate pass turns the point into a rigorous box
                for pass in 1..=point {
                    let tq = Instant::now();
                    for col in &mut cols {
                        col.bp = 0;
                        col.rmax = 0;
                    }
                    let core_r = &core;
                    let diag_r = &diag;
                    let (_, mk) = stream(&mut dev, off, &hdr, |h0, rows| {
                        let per = cols.len().div_ceil(threads).max(1);
                        std::thread::scope(|sc| {
                            for part in cols.chunks_mut(per) {
                                sc.spawn(move || {
                                    for col in part.iter_mut().filter(|c| c.err.is_none()) {
                                        if let Err(e) = point_rows(col, h0, rows, core_r, diag_r, je, f) {
                                            col.err = Some(e);
                                        }
                                    }
                                });
                            }
                        });
                    })?;
                    clock += 1;
                    point_passes += 1;
                    if mk != hdr.merkle {
                        return Err(format!("payload merkle mismatch on point pass: {mk}"));
                    }
                    if let Some(e) = cols.iter().find_map(|c| c.err.clone()) {
                        return Err(e);
                    }
                    let dmax = cols.iter().map(|c| c.rmax).max().unwrap_or(0);
                    eprintln!("ROOMJUMP_POINTPASS|cols={cb}:{cbe}|pass={pass}|t={clock}|max_step={dmax}|pass_ms={}|ms={}|json=0", tq.elapsed().as_millis(), t0.elapsed().as_millis());
                    if dmax <= stop {
                        break;
                    }
                }
                for col in &mut cols {
                    col.cert = true;
                    col.q = 0;
                    col.bp = 0;
                    col.rmax = 0;
                }
                let core_r = &core;
                let diag_r = &diag;
                let (_, mk) = stream(&mut dev, off, &hdr, |h0, rows| {
                    let per = cols.len().div_ceil(threads).max(1);
                    std::thread::scope(|sc| {
                        for part in cols.chunks_mut(per) {
                            sc.spawn(move || {
                                for col in part.iter_mut().filter(|c| c.err.is_none()) {
                                    if let Err(e) = resid_rows(col, h0, rows, core_r, diag_r, je, f) {
                                        col.err = Some(e);
                                    }
                                }
                            });
                        }
                    });
                })?;
                clock += 1;
                cert_passes += 1;
                if mk != hdr.merkle {
                    return Err(format!("payload merkle mismatch on certificate pass: {mk}"));
                }
                if let Some(e) = cols.iter().find_map(|c| c.err.clone()) {
                    return Err(e);
                }
                for col in &mut cols {
                    apply_cert(col, &core, min_margin, clock)?;
                }
                eprintln!("ROOMJUMP_CERTPASS|cols={cb}:{cbe}|t={clock}|after_point=1|max_width={}|ms={}|json=0", cols.iter().map(|c| c.width).max().unwrap_or(0), t0.elapsed().as_millis());
            }
            loop {
                for col in &mut cols {
                    col.active = col.sweeps < maxsweep && col.width > tol;
                    if col.active {
                        col.sweeps += 1;
                        col.width = 0;
                        col.bp = 0;
                    }
                }
                if !cols.iter().any(|c| c.active) {
                    break;
                }
                let ts = Instant::now();
                let core_r = &core;
                let diag_r = &diag;
                let (_, mk) = stream(&mut dev, off, &hdr, |h0, rows| {
                    let per = cols.len().div_ceil(threads).max(1);
                    std::thread::scope(|sc| {
                        for part in cols.chunks_mut(per) {
                            sc.spawn(move || {
                                for col in part.iter_mut().filter(|c| c.active && c.err.is_none()) {
                                    if let Err(e) = gs_rows(col, h0, rows, core_r, diag_r, je, f) {
                                        col.err = Some(e);
                                    }
                                }
                            });
                        }
                    });
                })?;
                clock += 1;
                sweep_passes += 1;
                if mk != hdr.merkle {
                    return Err(format!("payload merkle mismatch on sweep: {mk}"));
                }
                if let Some(e) = cols.iter().find_map(|c| c.err.clone()) {
                    return Err(e);
                }
                eprintln!(
                    "ROOMSCHUR_SWEEP|cols={cb}:{cbe}|active={}|sweep_ms={}|max_width={}|ms={}|json=0",
                    cols.iter().filter(|c| c.active).count(),
                    ts.elapsed().as_millis(),
                    cols.iter().map(|c| c.width).max().unwrap_or(0),
                    t0.elapsed().as_millis()
                );
                if every == 0 {
                    continue;
                }
                // jump step: midpoints, difference norm, extrapolation
                for col in cols.iter_mut().filter(|c| c.active) {
                    plan_jump(col, core_r, every)?;
                }
                if !cols.iter().any(|c| c.cert) {
                    continue;
                }
                // certificate pass: exact residual of the jump point, streamed
                let tc = Instant::now();
                for col in cols.iter_mut().filter(|c| c.cert) {
                    col.bp = 0;
                    col.rmax = 0;
                }
                let (_, mk) = stream(&mut dev, off, &hdr, |h0, rows| {
                    let per = cols.len().div_ceil(threads).max(1);
                    std::thread::scope(|sc| {
                        for part in cols.chunks_mut(per) {
                            sc.spawn(move || {
                                for col in part.iter_mut().filter(|c| c.cert && c.err.is_none()) {
                                    if let Err(e) = resid_rows(col, h0, rows, core_r, diag_r, je, f) {
                                        col.err = Some(e);
                                    }
                                }
                            });
                        }
                    });
                })?;
                clock += 1;
                cert_passes += 1;
                if mk != hdr.merkle {
                    return Err(format!("payload merkle mismatch on certificate pass: {mk}"));
                }
                if let Some(e) = cols.iter().find_map(|c| c.err.clone()) {
                    return Err(e);
                }
                for col in cols.iter_mut().filter(|c| c.cert) {
                    apply_cert(col, core_r, min_margin, clock)?;
                }
                eprintln!(
                    "ROOMJUMP_CERTPASS|cols={cb}:{cbe}|t={clock}|pass_ms={}|max_width={}|ms={}|json=0",
                    tc.elapsed().as_millis(),
                    cols.iter().map(|c| c.width).max().unwrap_or(0),
                    t0.elapsed().as_millis()
                );
            }
            // S_{a,c}*F = B_ac*F - sum_h B_ah * y_h for every core a
            for col in &cols {
                sweeps_max = sweeps_max.max(col.sweeps);
                width_max = width_max.max(col.width);
                for (ca, &ar) in cidx.iter().enumerate() {
                    let mut bac = if ar == col.c { diag[col.c] } else { 0 };
                    let (mut acc_lo, mut acc_hi) = (0i128, 0i128);
                    for &(h, v) in &core_rows[ca] {
                        if core[h] {
                            if h == col.c {
                                bac = v;
                            }
                            continue;
                        }
                        let (pl, ph) = imul(i128::from(col.iv[h][0]), i128::from(col.iv[h][1]), v)?;
                        acc_lo = ck(acc_lo.checked_add(pl))?;
                        acc_hi = ck(acc_hi.checked_add(ph))?;
                    }
                    let bf = ck(bac.checked_mul(f))?;
                    s_lo[ca][col.cb] = bf - acc_hi;
                    s_hi[ca][col.cb] = bf - acc_lo;
                    println!("SCOL|{tag}|cb={}|ca={ca}|lo={}|hi={}|sweeps={}|ywidth={}|json=0", col.cb, s_lo[ca][col.cb], s_hi[ca][col.cb], col.sweeps, col.width);
                }
                if jm {
                    let bm = merkle_bytes(col.iv.iter().flat_map(|p| [p[0], p[1]]));
                    println!("ROOMJUMP_COL|cb={}|sweeps={}|certs={}|jumps={}|ywidth={}|box_merkle={bm}|chain={}|json=0", col.cb, col.sweeps, col.certs, col.jumps, col.width, col.chain);
                    chains.push((col.cb, col.chain.clone()));
                }
            }
            cb = cbe;
        }
        if jm {
            chains.sort();
            let all: String = chains.iter().fold(String::new(), |mut s, (c, h)| {
                s.push_str(&c.to_string());
                s.push(':');
                s.push_str(h);
                s.push(';');
                s
            });
            println!("ROOMJUMP_CLOCK|t={clock}|point_passes={point_passes}|sweep_passes={sweep_passes}|cert_passes={cert_passes}|columns={}|clock_root={}|json=0", chains.len(), sha::sha256_hex(all.as_bytes()));
        }
        if (ca0, cb1) != (0, m) {
            println!(
                "SHELL_SCHUR_COLS|{tag}|cols={ca0}:{cb1}|gs_sweeps_max={sweeps_max}|y_width_max={width_max}|room_bytes_per_pass={bytes0}|pass_ms={}|payload_merkle={merkle0}|ms={}|json=0",
                rows_read_ms.iter().map(u128::to_string).collect::<Vec<_>>().join(","),
                t0.elapsed().as_millis()
            );
            return Ok(());
        }
    }
    let mut s: Vec<Vec<Iv>> = vec![vec![(BigInt::zero(), BigInt::zero()); m]; m];
    for i in 0..m {
        for j in 0..m {
            let l = s_lo[i][j].max(s_lo[j][i]);
            let h = s_hi[i][j].min(s_hi[j][i]);
            if l > h {
                return Err("S enclosures disjoint (inconsistency)".into());
            }
            s[i][j] = (BigInt::from(l), BigInt::from(h));
        }
    }
    let (neg, pos, steps, ok) = dense_inertia(s);
    let core_edges: usize = core_rows.iter().map(|r| r.iter().filter(|&&(j, _)| core[j]).count()).sum::<usize>() / 2;
    let name = a[1].rsplit(['/', '\\']).next().unwrap_or("");
    println!(
        "SHELL_SCHUR|matrix={name}|n={n}|JE={je}|JB={jb}|t_milli={tn}|shell_max={shell_max}|core={m}|core_edges={core_edges}|H={}|H_min_margin={min_margin}|H_max_offdiag_over_diag_permille_ceil={worst_num}|F=10^{fdig}|gs_sweeps_max={sweeps_max}|y_width_max={width_max}|negative={neg}|positive_core={pos}|positive_H={}|eliminated={steps}|ambiguous={}|result={}|ms={}|json=0",
        n - m,
        n - m,
        if ok { 0 } else { m - steps },
        if ok { "PASS" } else { "AMBIGUOUS" },
        t0.elapsed().as_millis()
    );
    if !ok {
        std::process::exit(2);
    }
    Ok(())
}

/// After a sweep: compare this sweep's midpoints with the previous ones and,
/// every `every` sweeps, put the extrapolated point in `pm` and mark the column
/// for a certificate pass. Otherwise `pm` becomes this sweep's midpoints.
fn plan_jump(col: &mut Col, core: &[bool], every: usize) -> Result<(), String> {
    let mut nsum = 0i128;
    for ((pv, &pm), &cr) in col.iv.iter().zip(col.pm.iter()).zip(core.iter()) {
        if !cr {
            nsum = ck(nsum.checked_add((i128::from(mid(*pv)) - i128::from(pm)).abs()))?;
        }
    }
    let due = col.sweeps % every == 0;
    col.q = 0;
    if due {
        if let Some(dn) = col.nprev {
            if nsum > 0 && nsum < dn {
                let q = ck(nsum.checked_mul(1i128 << QSHIFT))? / (dn - nsum);
                if q <= QMAX {
                    col.q = q;
                }
            }
        }
    }
    let q = col.q;
    for ((pv, pm), &cr) in col.iv.iter().zip(col.pm.iter_mut()).zip(core.iter()) {
        if cr {
            continue;
        }
        let md = i128::from(mid(*pv));
        let x = if q > 0 {
            let step = floor_div(ck((md - i128::from(*pm)).checked_mul(q))?, 1i128 << QSHIFT);
            ck(md.checked_add(step))?
        } else {
            md
        };
        *pm = i64::try_from(x).unwrap_or(mid(*pv));
    }
    if due {
        col.cert = true;
        col.nprev = None;
    } else {
        col.nprev = Some(nsum);
    }
    Ok(())
}

/// One point Gauss-Seidel pass on `pm` (nearest-integer division); `rmax`
/// records the largest change, so a pass with rmax = 0 is a fixed point.
fn point_rows(col: &mut Col, h0: usize, rows: &[Row], core: &[bool], diag: &[i128], je: i128, f: i128) -> Result<(), String> {
    for (d, r) in rows.iter().enumerate() {
        let h = h0 + d;
        if core[h] {
            continue;
        }
        while col.bp < col.b.len() && col.b[col.bp].0 < h {
            col.bp += 1;
        }
        let bh = if col.bp < col.b.len() && col.b[col.bp].0 == h { col.b[col.bp].1 } else { 0 };
        let mut acc = ck(bh.checked_mul(f))?;
        for k in 0..r.ent.len() / 8 {
            let (j, z) = ent(r.ent, k);
            if j == h || core[j] {
                continue;
            }
            let v = 1000 * je * r.w * z;
            acc = ck(acc.checked_sub(ck(v.checked_mul(i128::from(col.pm[j])))?))?;
        }
        let dh = diag[h];
        let x = floor_div(ck(ck(acc.checked_mul(2))?.checked_add(dh))?, 2 * dh);
        let old = i128::from(col.pm[h]);
        col.rmax = col.rmax.max((x - old).abs());
        col.pm[h] = to64(x)?;
    }
    Ok(())
}

/// Residual of the jump point over rows h0..: r_h = b_h*F - d_h x_h - sum_j a_hj x_j.
fn resid_rows(col: &mut Col, h0: usize, rows: &[Row], core: &[bool], diag: &[i128], je: i128, f: i128) -> Result<(), String> {
    for (d, r) in rows.iter().enumerate() {
        let h = h0 + d;
        if core[h] {
            continue;
        }
        while col.bp < col.b.len() && col.b[col.bp].0 < h {
            col.bp += 1;
        }
        let bh = if col.bp < col.b.len() && col.b[col.bp].0 == h { col.b[col.bp].1 } else { 0 };
        let mut acc = ck(bh.checked_mul(f))?;
        acc = ck(acc.checked_sub(ck(diag[h].checked_mul(i128::from(col.pm[h])))?))?;
        for k in 0..r.ent.len() / 8 {
            let (j, z) = ent(r.ent, k);
            if j == h || core[j] {
                continue;
            }
            let v = 1000 * je * r.w * z;
            acc = ck(acc.checked_sub(ck(v.checked_mul(i128::from(col.pm[j])))?))?;
        }
        col.rmax = col.rmax.max(ck(acc.checked_abs())?);
    }
    Ok(())
}

/// Intersect the box with x +- ceil(R/mu), extend the timer chain, reset midpoints.
fn apply_cert(col: &mut Col, core: &[bool], mu: i128, clock: usize) -> Result<(), String> {
    let radius = ceil_div(col.rmax, mu);
    let xm = merkle_bytes(col.pm.iter().copied());
    let mut width = 0i128;
    for ((pv, pm), &cr) in col.iv.iter_mut().zip(col.pm.iter_mut()).zip(core.iter()) {
        if cr {
            continue;
        }
        let x = i128::from(*pm);
        let lo = i128::from(pv[0]).max(ck(x.checked_sub(radius))?);
        let hi = i128::from(pv[1]).min(ck(x.checked_add(radius))?);
        if lo > hi {
            return Err("certificate box disjoint from Gauss-Seidel box (inconsistency)".into());
        }
        *pv = [to64(lo)?, to64(hi)?];
        width = width.max(hi - lo);
        *pm = mid(*pv);
    }
    let kind = if col.q > 0 { "JUMP" } else { "CERT" };
    let bm = merkle_bytes(col.iv.iter().flat_map(|p| [p[0], p[1]]));
    col.chain = sha::sha256_hex(
        format!("{}|t={clock}|sweep={}|kind={kind}|q={}|x={xm}|R={}|radius={radius}|box={bm}", col.chain, col.sweeps, col.q, col.rmax).as_bytes(),
    );
    println!(
        "ROOMJUMP_EVT|cb={}|t={clock}|sweep={}|kind={kind}|q={}|R={}|radius={radius}|width_before={}|width_after={width}|x_merkle={xm}|box_merkle={bm}|chain={}|json=0",
        col.cb, col.sweeps, col.q, col.rmax, col.width, col.chain
    );
    col.width = width;
    col.cert = false;
    col.certs += 1;
    if col.q > 0 {
        col.jumps += 1;
    }
    Ok(())
}

/// One Gauss-Seidel pass of `col` over rows h0.. (shellschur's inner loop).
fn gs_rows(col: &mut Col, h0: usize, rows: &[Row], core: &[bool], diag: &[i128], je: i128, f: i128) -> Result<(), String> {
    for (d, r) in rows.iter().enumerate() {
        let h = h0 + d;
        if core[h] {
            continue;
        }
        while col.bp < col.b.len() && col.b[col.bp].0 < h {
            col.bp += 1;
        }
        let bh = if col.bp < col.b.len() && col.b[col.bp].0 == h { col.b[col.bp].1 } else { 0 };
        let base = ck(bh.checked_mul(f))?;
        let (mut nlo, mut nhi) = (base, base);
        for k in 0..r.ent.len() / 8 {
            let (j, z) = ent(r.ent, k);
            if j == h || core[j] {
                continue;
            }
            let v = 1000 * je * r.w * z;
            let [jl, jh] = col.iv[j];
            let (pl, ph) = imul(i128::from(jl), i128::from(jh), -v)?;
            nlo = ck(nlo.checked_add(pl))?;
            nhi = ck(nhi.checked_add(ph))?;
        }
        let dh = diag[h];
        let [ol, oh] = col.iv[h];
        let (ylo, yhi) = (floor_div(nlo, dh).max(i128::from(ol)), ceil_div(nhi, dh).min(i128::from(oh)));
        if ylo > yhi {
            return Err("empty enclosure (arithmetic inconsistency)".into());
        }
        col.iv[h] = [to64(ylo)?, to64(yhi)?];
        col.width = col.width.max(yhi - ylo);
    }
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        println!("ROOMSCHUR|error={e}|json=0");
        std::process::exit(1);
    }
}
