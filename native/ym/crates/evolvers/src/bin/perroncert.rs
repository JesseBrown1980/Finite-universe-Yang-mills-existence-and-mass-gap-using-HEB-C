//! perroncert: a lower bound on the level above the flat cluster, from one exact pass over a sector.
//!
//! The sector rows of a `ymroom build` stream form H = JE*E + JB*M with every off-diagonal entry <= 0
//! (each move contributes -1, and every sign is +1 in Sx+Sy+). Let H' be H with the F flat rows and
//! columns removed. Two facts then give a bound on the (F+1)-th level:
//!   1. Cauchy interlacing, in the W-orthogonal basis: E_{F+1} >= lowest level of H'.
//!   2. Barta / Collatz-Wielandt: H' = s - N with N >= 0, so for ANY d > 0,
//!      lowest level of H' >= min_h (H'd)_h / d_h.
//!
//! The check pass evaluates that minimum in exact integers, in the units of roomschur (t_milli). It
//! needs nothing from the solver: d can come from anywhere, and a wrong d only gives a weaker bound.
//! The solver is Gauss-Seidel on (H' - t) d = source, in fixed point, starting from d = 0.
//!
//! usage: perroncert solve DEV OFFSET JE JB T_MILLI SWEEPS [D_OUT]
//!          PERRONCERT_CHECK_EVERY=k   check pass every k sweeps
//!          PERRONCERT_START=file      start from a saved d (any earlier solve, at any threshold)
//!          PERRONCERT_INNER=m:k       keep rows with M <= m in RAM and, after every full sweep, run up
//!                                     to k Gauss-Seidel sweeps on them alone. High rows are dominated
//!                                     by their diagonals, so this saves disk passes. It only changes d.
//!          D_OUT is rewritten after every sweep, so a killed run loses at most one sweep. A failed
//!          checkpoint only warns, because the sweeps do not depend on it. The final save must work.
//!        perroncert check DEV OFFSET JE JB D_FILE
//! Every pass recomputes the payload merkle. D_FILE is d as little-endian i64, one per row, and its
//! SHA-256 is in the result row.
//! Exit 0 with a PERRONCERT row, 2 on a failed condition (no certified value is printed).
//! Integer-only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

#[allow(dead_code)]
#[path = "../../../torusl/src/segio.rs"]
mod segio;
#[allow(dead_code)]
#[path = "../../../torusl/src/sha.rs"]
mod sha;
#[allow(dead_code)]
#[path = "../../../torusl/src/roomio.rs"]
mod roomio;

const SOURCE_BITS: u32 = 30;
const WRITE_TRIES: u32 = 15;

struct Model {
    dev: segio::Dev,
    off: u64,
    hdr: roomio::Hdr,
    je: i128,
    jb: i128,
}

struct Check {
    flats: usize,
    t_cert: i128,
    min_row: usize,
    min_mag: u16,
    d_min: i64,
    d_max: i64,
}

fn open_model(spec: &str, off: u64, je: i128, jb: i128) -> Result<Model, String> {
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    Ok(Model { dev, off, hdr, je, jb })
}

/// Low rows kept in RAM for the inner sweeps: diagonal, then (column, -z) in one flat list.
#[derive(Default)]
struct LowRows {
    rows: Vec<(u32, i128, usize)>,
    ents: Vec<(u32, u32)>,
}

impl LowRows {
    /// Sweeps these rows alone, up to `limit` times, and returns how many it ran.
    fn sweep(&self, u: i128, d: &mut [i64], limit: usize) -> Result<usize, String> {
        let source = u << SOURCE_BITS;
        for pass in 1..=limit {
            let mut biggest = 0i64;
            for (k, &(h, diag, start)) in self.rows.iter().enumerate() {
                let end = self.rows.get(k + 1).map_or(self.ents.len(), |r| r.2);
                let mut sum = source;
                for &(j, nz) in &self.ents[start..end] {
                    sum += u * i128::from(nz) * i128::from(d[j as usize]);
                }
                let v = i64::try_from(sum / diag).map_err(|_| format!("d out of range at row {h}: t is at or above the lowest level of H'"))?;
                biggest = biggest.max((v - d[h as usize]).abs());
                d[h as usize] = v;
            }
            if biggest <= 1 {
                return Ok(pass);
            }
        }
        Ok(limit)
    }
}

/// One in-place Gauss-Seidel sweep. Flat rows stay at 0, which is what removes them from H'.
/// Returns the largest change of any d_h. Any row whose diagonal is at or below t stops the solve.
/// Rows with M <= keep_mag are added to `low` if it is still empty when the sweep starts.
fn sweep(md: &mut Model, tn: i128, d: &mut [i64], keep_mag: Option<u16>, low: &mut LowRows) -> Result<i64, String> {
    let u = 1000 * md.je;
    let source = u << SOURCE_BITS;
    let jb = md.jb;
    let mut err: Option<String> = None;
    let mut biggest = 0i64;
    let keep = if low.rows.is_empty() { keep_mag } else { None };
    roomio::stream(&mut md.dev, md.off, &md.hdr, |h, row| {
        if row.mag == 0 || err.is_some() {
            return;
        }
        let mut diag = 1000 * jb * i128::from(row.mag) - tn;
        let mut sum = source;
        let kept = keep.is_some_and(|m| row.mag <= m);
        let start = low.ents.len();
        for (j, z) in row.entries() {
            if j == h {
                diag += u * i128::from(z);
            } else if z > 0 {
                err = Some(format!("positive off-diagonal at row {h} column {j}"));
            } else {
                sum += u * i128::from(-z) * i128::from(d[j]);
                if kept && z != 0 {
                    low.ents.push((u32::try_from(j).unwrap_or(u32::MAX), z.unsigned_abs()));
                }
            }
        }
        if kept {
            low.rows.push((u32::try_from(h).unwrap_or(u32::MAX), diag, start));
        }
        if diag <= 0 {
            err = Some(format!("row {h} has diagonal {diag}, at or below t"));
            return;
        }
        match i64::try_from(sum / diag) {
            Ok(v) => {
                biggest = biggest.max((v - d[h]).abs());
                d[h] = v;
            }
            Err(_) => err = Some(format!("d out of range at row {h}: t is at or above the lowest level of H'")),
        }
    })?;
    match err {
        Some(e) => Err(e),
        None => Ok(biggest),
    }
}

/// The certificate: exact minimum of (H'd)_h / d_h, rounded down, over the non-flat rows. It relies
/// only on the rows just read and on d being positive, both of which it checks itself.
fn check(md: &mut Model, d: &[i64]) -> Result<Check, String> {
    if d.len() != md.hdr.n {
        return Err(format!("d has {} rows, stream has {}", d.len(), md.hdr.n));
    }
    let u = 1000 * md.je;
    let jb = md.jb;
    let (mut flats, mut positive_off, mut nonpositive_d, mut flat_nonzero) = (0usize, 0u64, 0u64, 0u64);
    let mut best: Option<(i128, usize, u16)> = None;
    let (mut d_min, mut d_max) = (i64::MAX, 0i64);
    roomio::stream(&mut md.dev, md.off, &md.hdr, |h, row| {
        if row.mag == 0 {
            flats += 1;
            flat_nonzero += u64::from(d[h] != 0);
            return;
        }
        if d[h] <= 0 {
            nonpositive_d += 1;
            return;
        }
        d_min = d_min.min(d[h]);
        d_max = d_max.max(d[h]);
        let mut n = 1000 * jb * i128::from(row.mag) * i128::from(d[h]);
        for (j, z) in row.entries() {
            positive_off += u64::from(j != h && z > 0);
            n += u * i128::from(z) * i128::from(d[j]);
        }
        let ratio = n.div_euclid(i128::from(d[h]));
        if best.map_or(true, |b| ratio < b.0) {
            best = Some((ratio, h, row.mag));
        }
    })?;
    if positive_off > 0 {
        return Err(format!("{positive_off} positive off-diagonal entries: the bound does not apply"));
    }
    if nonpositive_d > 0 || flat_nonzero > 0 {
        return Err(format!("d is not positive on the non-flat rows and 0 on the flat rows: {nonpositive_d} nonpositive, {flat_nonzero} flat nonzero"));
    }
    let (t_cert, min_row, min_mag) = best.ok_or("no non-flat rows")?;
    Ok(Check { flats, t_cert, min_row, min_mag, d_min, d_max })
}

fn d_bytes(d: &[i64]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(d.len() * 8);
    for v in d {
        bytes.extend_from_slice(&v.to_le_bytes());
    }
    bytes
}

fn report(md: &Model, mode: &str, c: &Check, d: &[i64], ms: u128) -> String {
    format!(
        "PERRONCERT|L={}|sector={}|n={}|flats={}|JE={}|JB={}|mode={mode}|t_cert_milli={}|statement=E_flats_plus_1_at_least_t_cert|min_row={}|min_mag={}|d_min={}|d_max={}|d_sha256={}|positive_offdiag=0|merkle=PASS|ms={ms}|json=0",
        md.hdr.lattice,
        md.hdr.sector,
        md.hdr.n,
        c.flats,
        md.je,
        md.jb,
        c.t_cert,
        c.min_row,
        c.min_mag,
        c.d_min,
        c.d_max,
        sha::sha256_hex(&d_bytes(d))
    )
}

/// Windows can refuse the rename for a moment while a scanner holds the new file, so retry.
fn write_d(path: &str, d: &[i64]) -> Result<(), String> {
    let tmp = format!("{path}.tmp");
    let bytes = d_bytes(d);
    let mut last = String::new();
    for attempt in 0..WRITE_TRIES {
        if attempt > 0 {
            std::thread::sleep(std::time::Duration::from_secs(2));
        }
        match std::fs::write(&tmp, &bytes).and_then(|()| std::fs::rename(&tmp, path)) {
            Ok(()) => return Ok(()),
            Err(e) => last = format!("save {path}: {e}"),
        }
    }
    Err(last)
}

fn read_d(path: &str) -> Result<Vec<i64>, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("read {path}: {e}"))?;
    if bytes.len() % 8 != 0 {
        return Err(format!("{path}: length is not a multiple of 8"));
    }
    Ok(bytes.chunks_exact(8).map(|c| i64::from_le_bytes([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]])).collect())
}

fn run(a: &[String]) -> Result<(), String> {
    let t0 = std::time::Instant::now();
    let arg = |k: usize, what: &str| a.get(k).ok_or_else(|| format!("missing {what}"));
    let num = |k: usize, what: &str| -> Result<i128, String> { arg(k, what)?.parse().map_err(|_| format!("bad {what}")) };
    let off = u64::try_from(num(3, "OFFSET")?).map_err(|_| "bad OFFSET")?;
    let (je, jb) = (num(4, "JE")?, num(5, "JB")?);
    if je <= 0 || jb < 0 {
        return Err("JE must be positive and JB nonnegative".into());
    }
    let mut md = open_model(arg(2, "DEV")?, off, je, jb)?;
    match arg(1, "mode")?.as_str() {
        "check" => {
            let d = read_d(arg(6, "D_FILE")?)?;
            let c = check(&mut md, &d)?;
            println!("{}", report(&md, "check", &c, &d, t0.elapsed().as_millis()));
        }
        "solve" => {
            let tn = num(6, "T_MILLI")?;
            let sweeps = usize::try_from(num(7, "SWEEPS")?).map_err(|_| "bad SWEEPS")?;
            let every: usize = std::env::var("PERRONCERT_CHECK_EVERY").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
            let mut d = match std::env::var("PERRONCERT_START") {
                Ok(p) => read_d(&p)?,
                Err(_) => vec![0i64; md.hdr.n],
            };
            if d.len() != md.hdr.n {
                return Err(format!("start vector has {} rows, stream has {}", d.len(), md.hdr.n));
            }
            let inner = std::env::var("PERRONCERT_INNER").ok().and_then(|v| {
                let (m, k) = v.split_once(':')?;
                Some((m.parse::<u16>().ok()?, k.parse::<usize>().ok()?))
            });
            let mut low = LowRows::default();
            let mut saved = false;
            for s in 1..=sweeps {
                let biggest = sweep(&mut md, tn, &mut d, inner.map(|i| i.0), &mut low)?;
                if let Some((_, limit)) = inner {
                    let ran = low.sweep(1000 * je, &mut d, limit)?;
                    println!("PERRONCERT_INNER|sweep={s}|low_rows={}|low_entries={}|inner_sweeps={ran}|ms={}|json=0", low.rows.len(), low.ents.len(), t0.elapsed().as_millis());
                }
                if let Some(p) = a.get(8) {
                    saved = write_d(p, &d).map_err(|e| println!("PERRONCERT_WARN|{e}|json=0")).is_ok();
                }
                println!("PERRONCERT_SWEEP|sweep={s}|t_milli={tn}|biggest_change={biggest}|ms={}|json=0", t0.elapsed().as_millis());
                if every > 0 && s % every == 0 && s < sweeps {
                    let c = check(&mut md, &d)?;
                    println!("PERRONCERT_PROGRESS|sweep={s}|t_cert_milli={}|min_row={}|min_mag={}|d_max={}|ms={}|json=0", c.t_cert, c.min_row, c.min_mag, c.d_max, t0.elapsed().as_millis());
                }
            }
            if let (Some(p), false) = (a.get(8), saved) {
                write_d(p, &d)?;
            }
            let c = check(&mut md, &d)?;
            println!("{}", report(&md, "solve", &c, &d, t0.elapsed().as_millis()));
        }
        other => return Err(format!("unknown mode {other}")),
    }
    Ok(())
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if let Err(e) = run(&a) {
        println!("PERRONCERT_ERROR|{e}|json=0");
        std::process::exit(2);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp(name: &str) -> String {
        std::env::temp_dir().join(format!("perroncert-test-{}-{name}", std::process::id())).to_str().unwrap().to_string()
    }

    fn model(name: &str, rows: &[roomio::TestRow]) -> (Model, String) {
        let p = temp(name);
        roomio::write_test_stream(std::path::Path::new(&p), rows);
        (open_model(&p, 0, 1000, 9000).unwrap(), p)
    }

    /// Row 0 is flat. Rows 1 and 2 give H' = [[z1 + 9 m1, -a], [-a, z2 + 9 m2]] in units of JE.
    fn two_by_two(z1: i32, m1: u16, a: i32, z2: i32, m2: u16) -> Vec<roomio::TestRow> {
        vec![(1, 0, vec![(0, 54), (1, -1)]), (1, m1, vec![(0, -1), (1, z1), (2, -a)]), (1, m2, vec![(1, -a), (2, z2)])]
    }

    #[test]
    fn a_solved_vector_reaches_the_exact_lowest_level_from_below() {
        // H' = [[50, -5], [-5, 50]] with these masses: lowest level exactly 45.
        let (mut md, p) = model("exact", &two_by_two(23, 3, 5, 14, 4));
        let mut d = vec![0i64; 3];
        for _ in 0..400 {
            sweep(&mut md, 44_000_000, &mut d, None, &mut LowRows::default()).unwrap();
        }
        let c = check(&mut md, &d).unwrap();
        assert_eq!(c.flats, 1);
        assert!(c.t_cert <= 45_000_000, "{}", c.t_cert);
        assert!(c.t_cert > 44_000_000, "{}", c.t_cert);
        // The exact eigenvector (1, 1) gives exactly 45 on both rows.
        let c = check(&mut md, &[0, 1 << 20, 1 << 20]).unwrap();
        assert_eq!(c.t_cert, 45_000_000);
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn any_positive_vector_gives_a_valid_but_weaker_bound() {
        let (mut md, p) = model("weak", &two_by_two(23, 3, 5, 14, 4));
        let c = check(&mut md, &[0, 1, 3]).unwrap();
        // Row 1: 50 - 5*3 = 35. Row 2: 50 - 5/3 = 48.33. The minimum is 35, below the true 45.
        assert_eq!((c.t_cert, c.min_row), (35_000_000, 1));
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_coupling_into_a_flat_row_is_dropped() {
        // Row 1's only other entry goes to the flat row, so its level is its diagonal, 50.
        let rows = vec![(1, 0, vec![(0, 54), (1, -7)]), (1, 3, vec![(0, -7), (1, 23)])];
        let (mut md, p) = model("drop", &rows);
        assert!(check(&mut md, &[999, 5]).err().unwrap().contains("flat nonzero"));
        assert_eq!(check(&mut md, &[0, 5]).unwrap().t_cert, 50_000_000);
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_positive_off_diagonal_voids_the_bound() {
        let rows = vec![(1, 0, vec![(0, 54)]), (1, 3, vec![(1, 23), (2, 5)]), (1, 3, vec![(1, 5), (2, 23)])];
        let (mut md, p) = model("sign", &rows);
        assert!(check(&mut md, &[0, 1, 1]).is_err());
        assert!(sweep(&mut md, 1_000_000, &mut [0, 0, 0], None, &mut LowRows::default()).is_err());
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_vector_that_is_not_positive_is_refused() {
        let (mut md, p) = model("neg", &two_by_two(23, 3, 5, 14, 4));
        assert!(check(&mut md, &[0, 0, 1]).is_err());
        assert!(check(&mut md, &[0, -1, 1]).is_err());
        assert!(check(&mut md, &[0, 1]).is_err());
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_threshold_above_the_lowest_level_stops_the_solve() {
        // Lowest level 45, and both diagonals are 50. At t = 48 the iteration grows without bound.
        let (mut md, p) = model("above", &two_by_two(23, 3, 5, 14, 4));
        let mut d = vec![0i64; 3];
        let mut stopped = false;
        for _ in 0..4000 {
            if sweep(&mut md, 48_000_000, &mut d, None, &mut LowRows::default()).is_err() {
                stopped = true;
                break;
            }
        }
        assert!(stopped);
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn inner_sweeps_reach_the_same_bound_with_fewer_passes() {
        let (mut md, p) = model("inner", &two_by_two(23, 3, 5, 14, 4));
        let mut d = vec![0i64; 3];
        let mut low = LowRows::default();
        sweep(&mut md, 44_000_000, &mut d, Some(3), &mut low).unwrap();
        assert_eq!((low.rows.len(), low.ents.len()), (1, 2));
        assert!(low.sweep(1_000_000, &mut d, 5).is_ok());
        for _ in 0..3 {
            sweep(&mut md, 44_000_000, &mut d, Some(3), &mut low).unwrap();
            assert_eq!((low.rows.len(), low.ents.len()), (1, 2));
            low.sweep(1_000_000, &mut d, 400).unwrap();
        }
        let c = check(&mut md, &d).unwrap();
        assert!(c.t_cert > 44_000_000 && c.t_cert <= 45_000_000, "{}", c.t_cert);
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn d_files_round_trip_and_overwrite() {
        let p = temp("d.bin");
        write_d(&p, &[0, 1, -5, i64::MAX]).unwrap();
        assert_eq!(read_d(&p).unwrap(), vec![0, 1, -5, i64::MAX]);
        write_d(&p, &[7, 8]).unwrap();
        assert_eq!(read_d(&p).unwrap(), vec![7, 8]);
        assert!(!std::path::Path::new(&format!("{p}.tmp")).exists());
        std::fs::remove_file(p).unwrap();
    }
}
