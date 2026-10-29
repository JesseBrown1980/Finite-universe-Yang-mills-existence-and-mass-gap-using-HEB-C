//! roomschur: `shellschur` with the matrix streamed from Host8 rooms (the
//! `ymroom build` layout) instead of held in RAM. Integer-only, Rust 1.81, json=0.
//!
//! Same mathematics, same arithmetic, same output lines as `shellschur`
//! (SHELL_SCHUR / SCOL / SHELL_SCHUR_COLS, same tag and core fingerprint), so
//! its records can be compared with `shellschur` on any matrix both can read.
//! Differences are only where data lives:
//!   - each Gauss-Seidel sweep streams the rows from the room device in index
//!     order (rows are visited in the same order h = 0..n as in shellschur);
//!   - K core columns are swept together in one pass over the rooms, each column
//!     with its own sweep counter and stopping rule, so every column's sequence
//!     of updates is exactly the one shellschur performs for it alone;
//!   - lo/hi enclosures are stored as i64 (checked; any value outside i64 stops
//!     the run, nothing is rounded) and all arithmetic is i128 as in shellschur.
//!
//! usage: roomschur DEV OFFSET JE JB TN [FDIG=9] [TOL=1000] [MAXSWEEP=400]
//!   ROOMSCHUR_COLS=a:b   core columns a..b-1 (default: all), SCOL lines printed
//!   ROOMSCHUR_K=k        columns resident and swept together (default 1)
//!   ROOMSCHUR_MERGE=f1,f2,...   read SCOL lines and finish the inertia
//! Admission (PRODUCTION-ADMISSION rule, bytes are exact allocation sizes):
//!   RESERVE = n*(16 diag + 1 core) + read buffers, COL_BYTES = 16*n,
//!   a block of k columns is admitted only if k*COL_BYTES + RESERVE <= BUDGET,
//!   BUDGET from ROOMSCHUR_BUDGET (bytes, required).
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{Signed, Zero};
use std::io::{Read, Seek, SeekFrom};
use std::time::Instant;

#[path = "../../../torusl/src/sha.rs"]
mod sha;

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

struct Hdr {
    n: usize,
    payload: u64,
    merkle: String,
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

fn read_hdr(dev: &mut std::fs::File, off: u64) -> Result<Hdr, String> {
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

/// Stream every row in index order, calling `f(h, row)` for each complete chunk
/// of rows. The 16 MiB chunk SHA-256 merkle of the payload is recomputed.
fn stream<F: FnMut(usize, &[Row])>(dev: &mut std::fs::File, off: u64, hdr: &Hdr, mut f: F) -> Result<(u64, String), String> {
    dev.seek(SeekFrom::Start(off + 4096)).map_err(|e| format!("seek: {e}"))?;
    let mut left = hdr.payload;
    let mut carry: Vec<u8> = Vec::new();
    let mut buf = vec![0u8; CHUNK];
    let mut shas: Vec<u8> = Vec::new();
    let mut h = 0usize;
    let mut read = 0u64;
    while left > 0 {
        let take = usize::try_from(left.min(CHUNK as u64)).map_err(|_| "chunk")?;
        dev.read_exact(&mut buf[..take]).map_err(|e| format!("read rooms: {e}"))?;
        read += take as u64;
        left -= take as u64;
        for c in buf[..take].chunks(16 * 1_048_576) {
            shas.extend_from_slice(sha::sha256_hex(c).as_bytes());
        }
        carry.extend_from_slice(&buf[..take]);
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
    if h != hdr.n {
        return Err(format!("stream ended at row {h} of {}", hdr.n));
    }
    Ok((read, sha::sha256_hex(&shas)))
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
    lo: Vec<i64>,
    hi: Vec<i64>,
    sweeps: usize,
    width: i128,
    active: bool,
    err: Option<String>,
}

fn to64(v: i128) -> Result<i64, String> {
    i64::try_from(v).map_err(|_| "enclosure outside i64".to_string())
}

fn run() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 6 {
        return Err("usage: roomschur DEV OFFSET JE JB TN [FDIG=9] [TOL=1000] [MAXSWEEP=400]".into());
    }
    let p = |k: usize, def: i128| a.get(k).and_then(|s| s.parse::<i128>().ok()).unwrap_or(def);
    let off: u64 = a[2].parse().map_err(|_| "bad OFFSET")?;
    let (je, jb, tn) = (p(3, 0), p(4, 0), p(5, 0));
    let shell_max: i128 = -1;
    let fdig = u32::try_from(p(6, 9)).map_err(|_| "bad FDIG")?;
    let tol = p(7, 1000);
    let maxsweep = usize::try_from(p(8, 400)).map_err(|_| "bad MAXSWEEP")?;
    let f: i128 = 10i128.pow(fdig);
    let t0 = Instant::now();
    let mut dev = std::fs::OpenOptions::new().read(true).open(&a[1]).map_err(|e| format!("open {}: {e}", a[1]))?;
    let hdr = read_hdr(&mut dev, off)?;
    let n = hdr.n;
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
        let reserve: u128 = (n as u128) * (16 + 16 + 1 + 8) + 3 * (CHUNK as u128);
        let col_bytes: u128 = 16 * (n as u128);
        let cap = budget.saturating_sub(reserve) / col_bytes;
        let projected = (kcols as u128) * col_bytes + reserve;
        println!("ROOMSCHUR_ADMISSION|BUDGET={budget}|RESERVE={reserve}|COL_BYTES={col_bytes}|CAP={cap}|K={kcols}|projected={projected}|admitted={}|json=0", u8::from(projected <= budget));
        if projected > budget {
            return Err("admission refused: K*COL_BYTES + RESERVE > BUDGET".into());
        }
        let threads: usize = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
        let mut cb = ca0;
        while cb < cb1 {
            let cbe = (cb + kcols).min(cb1);
            let mut cols: Vec<Col> = (cb..cbe)
                .map(|q| {
                    let c = cidx[q];
                    let b: Vec<(usize, i128)> = core_rows[q].iter().copied().filter(|&(h, _)| !core[h]).collect();
                    Col { cb: q, c, b, bp: 0, lo: vec![0; n], hi: vec![0; n], sweeps: 0, width: 0, active: true, err: None }
                })
                .collect();
            for col in &mut cols {
                let bmax = col.b.iter().map(|&(_, v)| v.abs()).max().unwrap_or(0);
                let beta = ceil_div(ck(bmax.checked_mul(f))?, min_margin);
                let b64 = to64(beta)?;
                for ((l, hv), &cr) in col.lo.iter_mut().zip(col.hi.iter_mut()).zip(core.iter()) {
                    if !cr {
                        *l = -b64;
                        *hv = b64;
                    }
                }
                col.width = 2 * beta;
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
                        let (pl, ph) = imul(i128::from(col.lo[h]), i128::from(col.hi[h]), v)?;
                        acc_lo = ck(acc_lo.checked_add(pl))?;
                        acc_hi = ck(acc_hi.checked_add(ph))?;
                    }
                    let bf = ck(bac.checked_mul(f))?;
                    s_lo[ca][col.cb] = bf - acc_hi;
                    s_hi[ca][col.cb] = bf - acc_lo;
                    println!("SCOL|{tag}|cb={}|ca={ca}|lo={}|hi={}|sweeps={}|ywidth={}|json=0", col.cb, s_lo[ca][col.cb], s_hi[ca][col.cb], col.sweeps, col.width);
                }
            }
            cb = cbe;
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
            let (pl, ph) = imul(i128::from(col.lo[j]), i128::from(col.hi[j]), -v)?;
            nlo = ck(nlo.checked_add(pl))?;
            nhi = ck(nhi.checked_add(ph))?;
        }
        let dh = diag[h];
        let (ylo, yhi) = (floor_div(nlo, dh).max(i128::from(col.lo[h])), ceil_div(nhi, dh).min(i128::from(col.hi[h])));
        if ylo > yhi {
            return Err("empty enclosure (arithmetic inconsistency)".into());
        }
        col.lo[h] = to64(ylo)?;
        col.hi[h] = to64(yhi)?;
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
