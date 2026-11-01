//! schurcert: inertia of a merged core Schur complement, by congruence and Gershgorin.
//!
//! Reads SCOL rows (roomschur, shellschur) and counts the negative eigenvalues of every symmetric
//! matrix inside the enclosures. It stands in only for the final dense interval LDL^T of a merge.
//! It trusts the enclosures and says nothing about the column solves. Integer-only, Rust 1.81, json=0.
//!
//! Interval elimination updates each entry from intervals that are not independent, so widths can
//! grow far past what the enclosures themselves imply. Here the enclosure enters once, linearly:
//!   1. S' = S / 2^Q, rounded outward; midpoint M and radius R, so |S' - M| <= R entrywise.
//!   2. X comes from a fixed-point elimination of M (largest |diagonal| first), scale 2^K. X only
//!      steers: rounding in it can lose decisions but cannot make a count wrong.
//!   3. T = X S' X^T / 2^K is enclosed as T' +- eps, computed exactly:
//!        T' = round(X M / 2^K) X^T,   eps_ij = ceil(||X_j||_1 / 2) + (|X|^ R |X|^^T)_ij,
//!      where |X|^ is |X| / 2^(K/2) rounded up.
//!   4. Gershgorin on Lam T Lam, Lam = diag(1/s_i), s_i = isqrt|T'_ii|. Row i is decided when
//!        floor(min|T_ii| / s_i) > sum_{j != i} ceil((|T'_ij| + eps_ij) / s_j).
//!
//! If every row is decided, T is nonsingular, so X is, and by Sylvester S has exactly as many
//! negative eigenvalues as rows with a negative centre. Any undecided row gives AMBIGUOUS and no
//! count. Release builds wrap on overflow and a wrapped sum could decide a row, so every product and
//! row sum has a bit budget. Over budget is an error, not a count.
//!
//! usage: schurcert FILE [FILE...]     WORKERS=n (default 1)
//!   SCHURCERT_WIDEN=f multiplies every radius by f, to measure slack. Only f=1 is a certificate.
//! Exit 0 on PASS, 2 on AMBIGUOUS, 1 on bad input.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::io::BufRead;
use std::time::Instant;

const Q: u32 = 20;
const K: u32 = 40;
const HALF_K: u32 = K / 2;
const BUDGET_BITS: u32 = 126;

struct Rows {
    m: usize,
    tag: String,
    lo: Vec<i128>,
    hi: Vec<i128>,
}

fn scol_field<'a>(line: &'a str, key: &str) -> Result<&'a str, String> {
    line.split('|').find_map(|kv| kv.strip_prefix(key)).ok_or_else(|| format!("SCOL row without {key}"))
}

fn read_rows(readers: Vec<Box<dyn BufRead>>) -> Result<Rows, String> {
    let mut rows: Option<Rows> = None;
    let mut seen: Vec<bool> = Vec::new();
    let mut count = 0usize;
    for mut reader in readers {
        let mut line = String::new();
        loop {
            line.clear();
            if reader.read_line(&mut line).map_err(|e| format!("read: {e}"))? == 0 {
                break;
            }
            if !line.starts_with("SCOL|") {
                continue;
            }
            let end = line.find("|cb=").ok_or("SCOL row without cb=")?;
            let tag = &line[5..end];
            let cur = match rows.as_mut() {
                Some(r) => r,
                None => {
                    let m: usize = scol_field(tag, "core=")?.parse().map_err(|_| "bad core=")?;
                    seen = vec![false; m * m];
                    rows.insert(Rows { m, tag: tag.to_string(), lo: vec![0; m * m], hi: vec![0; m * m] })
                }
            };
            if cur.tag != tag {
                return Err("SCOL rows from different runs".into());
            }
            let m = cur.m;
            let idx = |key: &str| -> Result<usize, String> { scol_field(&line[end..], key)?.parse().map_err(|_| format!("bad {key}")) };
            let val = |key: &str| -> Result<i128, String> { scol_field(&line[end..], key)?.parse().map_err(|_| format!("bad {key}")) };
            let (ca, cb) = (idx("ca=")?, idx("cb=")?);
            if ca >= m || cb >= m || seen[ca * m + cb] {
                return Err(format!("SCOL record out of range or duplicate ca={ca} cb={cb}"));
            }
            seen[ca * m + cb] = true;
            cur.lo[ca * m + cb] = val("lo=")?;
            cur.hi[ca * m + cb] = val("hi=")?;
            count += 1;
        }
    }
    let rows = rows.ok_or("no SCOL rows")?;
    if count != rows.m * rows.m {
        return Err(format!("{count} SCOL rows, need {}", rows.m * rows.m));
    }
    Ok(rows)
}

fn bit_len(v: u128) -> u32 {
    128 - v.leading_zeros()
}

fn max_bits(v: &[i128]) -> u32 {
    bit_len(v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0))
}

fn budget(what: &str, bits: u32) -> Result<(), String> {
    if bits > BUDGET_BITS {
        return Err(format!("overflow budget exceeded at {what}: {bits} bits"));
    }
    Ok(())
}

fn isqrt(n: u128) -> u128 {
    if n < 2 {
        return n;
    }
    let mut x = 1u128 << ((bit_len(n) + 1) / 2);
    loop {
        let y = (x + n / x) / 2;
        if y >= x {
            return x;
        }
        x = y;
    }
}

fn round_div(a: i128, d: i128) -> i128 {
    let (a, d) = if d < 0 { (-a, -d) } else { (a, d) };
    (a + d / 2).div_euclid(d)
}

fn par_rows<F>(out: &mut [i128], m: usize, threads: usize, f: F)
where
    F: Fn(usize, &mut [i128]) + Sync,
{
    let per = m.div_ceil(threads.max(1)).max(1);
    std::thread::scope(|sc| {
        for (c, part) in out.chunks_mut(per * m).enumerate() {
            let f = &f;
            sc.spawn(move || {
                for (d, row) in part.chunks_mut(m).enumerate() {
                    f(c * per + d, row);
                }
            });
        }
    });
}

struct Elim {
    x: Vec<i128>,
    negative: usize,
    positive: usize,
    unpivoted: usize,
}

/// Fixed-point elimination of the midpoint, largest |diagonal| first. Steers only.
fn eliminate(mid: &[i128], m: usize, threads: usize) -> Elim {
    let mut a = mid.to_vec();
    let mut x = vec![0i128; m * m];
    for (i, row) in x.chunks_mut(m).enumerate() {
        row[i] = 1i128 << K;
    }
    let mut alive = vec![true; m];
    let (mut negative, mut positive) = (0usize, 0usize);
    let mut left = m;
    while left > 0 {
        let pivot = (0..m).filter(|&i| alive[i]).max_by_key(|&i| a[i * m + i].unsigned_abs());
        let Some(pi) = pivot else { break };
        let p = a[pi * m + pi];
        if p == 0 {
            break;
        }
        if p < 0 {
            negative += 1;
        } else {
            positive += 1;
        }
        alive[pi] = false;
        left -= 1;
        let ap: Vec<i128> = a[pi * m..(pi + 1) * m].to_vec();
        let xp: Vec<(usize, i128)> = x[pi * m..(pi + 1) * m].iter().enumerate().filter(|(_, v)| **v != 0).map(|(q, v)| (q, *v)).collect();
        let cols: Vec<usize> = (0..m).filter(|&j| alive[j]).collect();
        let mut work: Vec<(usize, &mut [i128], &mut [i128])> =
            a.chunks_mut(m).zip(x.chunks_mut(m)).enumerate().filter(|(i, _)| alive[*i]).map(|(i, (ra, rx))| (i, ra, rx)).collect();
        let step = |w: &mut (usize, &mut [i128], &mut [i128])| {
            let f = round_div(ap[w.0] << K, p);
            if f == 0 {
                return;
            }
            for &j in &cols {
                w.1[j] -= (f * ap[j]) >> K;
            }
            for &(q, v) in &xp {
                w.2[q] -= (f * v) >> K;
            }
        };
        if work.len() < 64 || threads < 2 {
            work.iter_mut().for_each(step);
        } else {
            let per = work.len().div_ceil(threads);
            std::thread::scope(|sc| {
                for part in work.chunks_mut(per) {
                    let step = &step;
                    sc.spawn(move || part.iter_mut().for_each(step));
                }
            });
        }
    }
    Elim { x, negative, positive, unpivoted: left }
}

struct RowOut {
    row: usize,
    pivot_micro: i128,
    lhs: i128,
    rhs: i128,
    decided: bool,
}

struct Cert {
    negative: usize,
    positive: usize,
    ambiguous: usize,
    pivots_negative: usize,
    pivots_positive: usize,
    unpivoted: usize,
    x_bits: u32,
    max_raw_width: i128,
    rho_raw: i128,
    rows: Vec<RowOut>,
}

fn certify(rows: &Rows, threads: usize, widen: i128) -> Result<Cert, String> {
    let m = rows.m;
    let mut mid = vec![0i128; m * m];
    let mut rad = vec![0i128; m * m];
    let mut max_raw_width = 0i128;
    let mut rho_raw = 0i128;
    for i in 0..m {
        let mut row_sum = 0i128;
        for j in 0..m {
            let l = rows.lo[i * m + j].max(rows.lo[j * m + i]);
            let h = rows.hi[i * m + j].min(rows.hi[j * m + i]);
            if l > h {
                return Err(format!("S enclosures disjoint at {i},{j}"));
            }
            max_raw_width = max_raw_width.max(h - l);
            row_sum += h - l;
            let (sl, sh) = (l >> Q, -((-h) >> Q));
            let c = (sl + sh) >> 1;
            mid[i * m + j] = c;
            rad[i * m + j] = (sh - c).checked_mul(widen).ok_or("radius overflow")?;
        }
        rho_raw = rho_raw.max(row_sum / 2);
    }
    let elim = eliminate(&mid, m, threads);
    let x = elim.x;
    let x_bits = max_bits(&x);
    let sup: Vec<Vec<(usize, i128)>> = x.chunks(m).map(|r| r.iter().enumerate().filter(|(_, v)| **v != 0).map(|(q, v)| (q, *v)).collect()).collect();
    let m_bits = bit_len(m as u128);

    budget("X M", x_bits + max_bits(&mid) + m_bits)?;
    let mut yp = vec![0i128; m * m];
    par_rows(&mut yp, m, threads, |i, row| {
        for &(p, v) in &sup[i] {
            for (o, &z) in row.iter_mut().zip(&mid[p * m..(p + 1) * m]) {
                *o += v * z;
            }
        }
        for o in row.iter_mut() {
            *o = (*o + (1i128 << (K - 1))) >> K;
        }
    });

    budget("T'", max_bits(&yp) + x_bits + m_bits)?;
    let mut t = vec![0i128; m * m];
    par_rows(&mut t, m, threads, |i, row| {
        let yi = &yp[i * m..(i + 1) * m];
        for (o, s) in row.iter_mut().zip(&sup) {
            *o = s.iter().map(|&(q, v)| yi[q] * v).sum();
        }
    });
    drop(yp);

    let up: Vec<Vec<(usize, i128)>> = sup.iter().map(|s| s.iter().map(|&(q, v)| (q, (v.abs() + (1i128 << HALF_K) - 1) >> HALF_K)).collect()).collect();
    let up_bits = bit_len(up.iter().flatten().map(|&(_, v)| v.unsigned_abs()).max().unwrap_or(0));
    budget("X^ R", up_bits + max_bits(&rad) + m_bits)?;
    let mut b = vec![0i128; m * m];
    par_rows(&mut b, m, threads, |i, row| {
        for &(p, v) in &up[i] {
            for (o, &z) in row.iter_mut().zip(&rad[p * m..(p + 1) * m]) {
                *o += v * z;
            }
        }
    });
    budget("X^ R X^T", max_bits(&b) + up_bits + m_bits)?;
    let mut c = vec![0i128; m * m];
    par_rows(&mut c, m, threads, |i, row| {
        let bi = &b[i * m..(i + 1) * m];
        for (o, s) in row.iter_mut().zip(&up) {
            *o = s.iter().map(|&(q, v)| bi[q] * v).sum();
        }
    });
    drop(b);

    let half_l1: Vec<i128> = sup.iter().map(|s| (s.iter().map(|&(_, v)| v.abs()).sum::<i128>() + 1) / 2).collect();
    let root: Vec<i128> = (0..m).map(|i| i128::try_from(isqrt(t[i * m + i].unsigned_abs())).map(|v| v.max(1))).collect::<Result<_, _>>().map_err(|_| "root range")?;
    // Each a below is under 2^(entry bits + 2), and ceil(a / root) <= a, so m of them fit in this budget.
    budget("row sum", max_bits(&t).max(max_bits(&c)).max(max_bits(&half_l1)) + 2 + m_bits)?;

    let (mut negative, mut positive, mut ambiguous) = (0usize, 0usize, 0usize);
    let mut out = Vec::with_capacity(m);
    for i in 0..m {
        let centre = t[i * m + i];
        let eps = half_l1[i] + c[i * m + i];
        let mut rhs = 0i128;
        for j in 0..m {
            if j != i {
                let a = t[i * m + j].abs() + half_l1[j] + c[i * m + j];
                rhs += (a + root[j] - 1) / root[j];
            }
        }
        let (sign, least) = if centre - eps > 0 {
            (1, centre - eps)
        } else if centre + eps < 0 {
            (-1, -(centre + eps))
        } else {
            (0, 0)
        };
        let lhs = least / root[i];
        let decided = sign != 0 && lhs > rhs;
        if !decided {
            ambiguous += 1;
        } else if sign < 0 {
            negative += 1;
        } else {
            positive += 1;
        }
        let pivot_micro = (centre >> (K - Q)) / 1_000_000_000_000;
        out.push(RowOut { row: i, pivot_micro, lhs, rhs, decided });
    }
    Ok(Cert { negative, positive, ambiguous, pivots_negative: elim.negative, pivots_positive: elim.positive, unpivoted: elim.unpivoted, x_bits, max_raw_width, rho_raw, rows: out })
}

fn run() -> Result<i32, String> {
    let files: Vec<String> = std::env::args().skip(1).collect();
    if files.is_empty() {
        return Err("usage: schurcert FILE [FILE...]".into());
    }
    let threads: usize = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
    let widen: i128 = std::env::var("SCHURCERT_WIDEN").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
    let t0 = Instant::now();
    let mut readers: Vec<Box<dyn BufRead>> = Vec::new();
    for f in &files {
        let h = std::fs::File::open(f).map_err(|e| format!("open {f}: {e}"))?;
        readers.push(Box::new(std::io::BufReader::with_capacity(1 << 20, h)));
    }
    let rows = read_rows(readers)?;
    println!("SCHURCERT_INPUT|files={}|{}|m={}|q={Q}|k={K}|workers={threads}|read_ms={}|json=0", files.len(), rows.tag, rows.m, t0.elapsed().as_millis());
    let cert = certify(&rows, threads, widen)?;
    println!(
        "SCHURCERT_STEER|pivots_negative={}|pivots_positive={}|unpivoted={}|x_bits={}|max_raw_width={}|rho_raw={}|json=0",
        cert.pivots_negative, cert.pivots_positive, cert.unpivoted, cert.x_bits, cert.max_raw_width, cert.rho_raw
    );
    let mut tight: Vec<&RowOut> = cert.rows.iter().collect();
    tight.sort_by_key(|r| (r.decided, if r.rhs == 0 { i128::MAX } else { r.lhs / r.rhs }));
    for r in tight.iter().take(12) {
        println!("SCHURCERT_TIGHTEST|row={}|pivot_micro_JE_w={}|lhs={}|rhs={}|decided={}|json=0", r.row, r.pivot_micro, r.lhs, r.rhs, i32::from(r.decided));
    }
    let pass = cert.ambiguous == 0;
    println!(
        "SCHURCERT|method=congruence_gershgorin|widen={widen}|m={}|negative={}|positive={}|ambiguous={}|result={}|ms={}|json=0",
        rows.m,
        if pass { cert.negative.to_string() } else { "NONE".into() },
        if pass { cert.positive.to_string() } else { "NONE".into() },
        cert.ambiguous,
        if pass { "PASS" } else { "AMBIGUOUS" },
        t0.elapsed().as_millis()
    );
    Ok(if pass { 0 } else { 2 })
}

fn main() {
    match run() {
        Ok(code) => std::process::exit(code),
        Err(e) => {
            println!("SCHURCERT_ERROR|{e}|json=0");
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const UNIT: i128 = 1_000_000_000_000_000_000;

    /// S = Q D Q^T with Q unit lower triangular and integer, so Sylvester gives the inertia of S.
    fn known(m: usize, diag: &[i128], seed: u64) -> Vec<i128> {
        let mut s = seed;
        let mut q = vec![0i128; m * m];
        for i in 0..m {
            q[i * m + i] = 1;
            for j in 0..i {
                s = s.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
                // Sparse and small: dense random factors have inverses too large to steer with.
                q[i * m + j] = match s >> 60 {
                    0 => 1,
                    1 => -1,
                    _ => 0,
                };
            }
        }
        let mut out = vec![0i128; m * m];
        for i in 0..m {
            for j in 0..m {
                out[i * m + j] = (0..m).map(|p| q[i * m + p] * diag[p] * q[j * m + p]).sum();
            }
        }
        out
    }

    fn boxed(m: usize, s: &[i128], width: i128) -> Rows {
        Rows { m, tag: String::new(), lo: s.iter().map(|v| v - width).collect(), hi: s.iter().map(|v| v + width).collect() }
    }

    fn mixed(m: usize, negatives: usize) -> Vec<i128> {
        (0..m).map(|i| if i % (m / negatives) == 0 && i / (m / negatives) < negatives { -UNIT * (2 + (i as i128) % 5) } else { UNIT * (3 + (i as i128) % 7) }).collect()
    }

    #[test]
    fn exact_entries_match_sylvester() {
        for negatives in [1usize, 3, 7, 12] {
            let m = 36;
            let cert = certify(&boxed(m, &known(m, &mixed(m, negatives), 27), 0), 2, 1).unwrap();
            assert_eq!((cert.negative, cert.positive, cert.ambiguous), (negatives, m - negatives, 0));
        }
    }

    #[test]
    fn narrow_enclosures_keep_the_count() {
        let m = 36;
        let cert = certify(&boxed(m, &known(m, &mixed(m, 7), 81), 1_000_000_000), 1, 1).unwrap();
        assert_eq!((cert.negative, cert.positive, cert.ambiguous), (7, 29, 0));
    }

    #[test]
    fn widening_can_only_lose_decisions() {
        let m = 36;
        let rows = boxed(m, &known(m, &mixed(m, 7), 9), 1_000_000_000);
        let small = certify(&rows, 1, 100).unwrap();
        assert_eq!((small.negative, small.positive, small.ambiguous), (7, 29, 0));
        assert!(certify(&rows, 1, 1_000_000_000_000).unwrap().ambiguous > 0);
    }

    #[test]
    fn wide_enclosures_fail_closed() {
        let m = 36;
        let cert = certify(&boxed(m, &known(m, &mixed(m, 7), 243), 100 * UNIT), 1, 1).unwrap();
        assert!(cert.ambiguous > 0);
    }

    #[test]
    fn eigenvalue_inside_the_width_fails_closed() {
        let m = 30;
        let mut d = mixed(m, 5);
        d[17] = 1_000;
        let cert = certify(&boxed(m, &known(m, &d, 729), 1_000_000_000), 1, 1).unwrap();
        assert!(cert.ambiguous > 0);
    }

    #[test]
    fn zero_diagonal_fails_closed_not_wrong() {
        let s = [0, UNIT, UNIT, 0];
        let cert = certify(&boxed(2, &s, 0), 1, 1).unwrap();
        assert_eq!(cert.ambiguous, 2);
    }

    #[test]
    fn disjoint_enclosures_are_an_error() {
        let rows = Rows { m: 2, tag: String::new(), lo: vec![UNIT, 5, 7, UNIT], hi: vec![UNIT, 5, 7, UNIT] };
        assert!(certify(&rows, 1, 1).is_err());
    }

    #[test]
    fn missing_and_duplicate_rows_are_errors() {
        let tag = "SCOL|n=9|core=2|F=10^12";
        let row = |cb: usize, ca: usize| format!("{tag}|cb={cb}|ca={ca}|lo=1|hi=1|sweeps=0|ywidth=0|json=0\n");
        let read = |text: String| read_rows(vec![Box::new(std::io::Cursor::new(text))]);
        assert!(read(row(0, 0) + &row(0, 1) + &row(1, 0)).is_err());
        assert!(read(row(0, 0) + &row(0, 0) + &row(0, 1) + &row(1, 0)).is_err());
        assert!(read(row(0, 0) + &row(0, 1) + &row(1, 0) + &row(1, 1)).is_ok());
    }

    #[test]
    fn over_budget_is_an_error_not_a_count() {
        // T' is S / 2^Q * 2^K here: 2^122 passes every product budget but not the row sum's.
        let over = 1i128 << 102;
        assert!(matches!(certify(&boxed(2, &[over, 0, 0, over], 0), 1, 1), Err(e) if e.contains("row sum")));
        let under = 1i128 << 98;
        let cert = certify(&boxed(2, &[under, 0, 0, under], 0), 1, 1).unwrap();
        assert_eq!((cert.negative, cert.positive, cert.ambiguous), (0, 2, 0));
    }

    #[test]
    fn radius_overflow_is_an_error_not_a_count() {
        let rows = boxed(2, &[UNIT, 0, 0, UNIT], 1 << 30);
        assert!(certify(&rows, 1, i128::MAX).is_err());
    }

    #[test]
    fn isqrt_is_exact() {
        for n in [0u128, 1, 2, 3, 4, 15, 16, 17, 1 << 40, (1 << 90) + 12345, u128::from(u64::MAX) * u128::from(u64::MAX)] {
            let r = isqrt(n);
            assert!(r * r <= n && (r + 1).checked_mul(r + 1).map_or(true, |v| v > n));
        }
    }
}
