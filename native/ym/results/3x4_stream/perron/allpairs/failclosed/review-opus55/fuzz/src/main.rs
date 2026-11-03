//! Exact test of W H = (W H)^T on a stored room stream, pair by pair, with no random vector.
//!
//! Every off-diagonal entry z_hj needs a partner z_jh in the row of j, with w_h z_hj = w_j z_jh in exact integers.
//! An entry with no partner fails. Rows come through `roomio::stream`, so every pass recomputes the payload merkle.
//!
//! Memory stays bounded. A pass keeps the upper entries (j > h) of one window of rows, then walks every row and answers
//! each lower entry (j < h) whose partner row lies in that window. The next pass starts where this window ended.
//!
//!   allpairs DEV OFFSET [CAP_ENTRIES]
//!
//! DEV is a segio spec. CAP_ENTRIES bounds the upper entries one window holds, at 8 bytes each. Exit 0 only when every
//! gate holds, exit 2 when one fails, exit 1 when the stream cannot be read or its merkle differs. Integer only, json=0.

#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::cmp::Ordering;
use std::io::{Read, Seek, SeekFrom};

#[allow(dead_code)]
#[path = "C:/tmp/opus55/ym-review-wt/native/ym/crates/torusl/src/segio.rs"]
mod segio;

#[allow(dead_code)]
#[path = "C:/tmp/opus55/ym-review-wt/native/ym/crates/torusl/src/sha.rs"]
mod sha;

#[allow(dead_code)]
#[path = "C:/tmp/opus55/ym-review-wt/native/ym/crates/torusl/src/roomio.rs"]
mod roomio;

/// 3.5 GiB of upper entries in one window.
const DEFAULT_CAP: usize = 470_000_000;
/// A window index stays a u32, with room for one more row past the cap.
const MAX_CAP: usize = 4_000_000_000;
const MAX_DETAIL: usize = 16;

/// What one walk over every row counts. No pair is compared here.
#[derive(Default)]
struct Census {
    rows: u64,
    entries: u64,
    diag: u64,
    upper: u64,
    lower: u64,
    not_ascending: u64,
    out_of_range: u64,
    zero_z: u64,
    positive_off: u64,
    row_sum_nonzero: u64,
    zero_weight: u64,
    missing_diag: u64,
    sum_w: u128,
    flat_w: Vec<u32>,
}

impl Census {
    fn row(&mut self, h: usize, row: &roomio::Row, n: usize) {
        self.rows += 1;
        self.zero_weight += u64::from(row.w == 0);
        self.sum_w += u128::from(row.w);
        if row.mag == 0 {
            self.flat_w.push(row.w);
        }
        let mut sum = 0i64;
        let mut has_diag = false;
        let mut prev: Option<usize> = None;
        for (j, z) in row.entries() {
            self.entries += 1;
            self.not_ascending += u64::from(prev.is_some_and(|p| j <= p));
            prev = Some(j);
            self.out_of_range += u64::from(j >= n);
            self.zero_z += u64::from(z == 0);
            self.positive_off += u64::from(j != h && z > 0);
            sum += i64::from(z);
            match j.cmp(&h) {
                Ordering::Less => self.lower += 1,
                Ordering::Equal => {
                    self.diag += 1;
                    has_diag = true;
                }
                Ordering::Greater => self.upper += 1,
            }
        }
        self.missing_diag += u64::from(!has_diag);
        self.row_sum_nonzero += u64::from(sum != 0);
    }

    fn structure_clean(&self) -> bool {
        [self.not_ascending, self.out_of_range, self.zero_z, self.positive_off, self.row_sum_nonzero, self.zero_weight, self.missing_diag].iter().all(|&v| v == 0)
    }
}

/// The upper entries of the rows start..end, kept in row order. Columns stay in stored order, ascending in a clean row.
struct Window {
    start: usize,
    end: usize,
    closed: bool,
    cap: usize,
    off: Vec<u32>,
    w: Vec<u32>,
    ent: Vec<(u32, i32)>,
}

impl Window {
    fn new(start: usize, cap: usize, reserve: usize) -> Window {
        Window { start, end: start, closed: false, cap, off: vec![0], w: Vec::new(), ent: Vec::with_capacity(reserve) }
    }

    fn holds(&self, i: usize) -> bool {
        (self.start..self.end).contains(&i)
    }

    fn upper(&self, i: usize) -> (u32, &[(u32, i32)]) {
        let r = i - self.start;
        (self.w[r], &self.ent[self.off[r] as usize..self.off[r + 1] as usize])
    }

    /// The first row of a window always enters, so every pass advances.
    fn admit(&mut self, h: usize, row: &roomio::Row) {
        if self.closed || h < self.start {
            return;
        }
        let count = row.entries().filter(|&(j, _)| j > h).count();
        if self.ent.len() + count > self.cap && h > self.start {
            self.closed = true;
            return;
        }
        // Each column was read from a u32, so the cast keeps it exactly.
        self.ent.extend(row.entries().filter(|&(j, _)| j > h).map(|(j, z)| (j as u32, z)));
        self.w.push(row.w);
        self.off.push(self.ent.len() as u32);
        self.end = h + 1;
    }
}

#[derive(Default)]
struct PassOut {
    start: usize,
    end: usize,
    stored: u64,
    lookups: u64,
    found: u64,
    value_mismatch: u64,
    lower_without_upper: u64,
    upper_without_lower: u64,
    secs: u64,
}

fn note(detail: &mut Vec<String>, text: String) {
    if detail.len() < MAX_DETAIL {
        detail.push(text);
    }
}

/// Answers every lower entry of row h whose partner row is in the window.
fn answer(win: &Window, h: usize, row: &roomio::Row, out: &mut PassOut, detail: &mut Vec<String>) {
    for (i, z_hi) in row.entries() {
        if i >= h || !win.holds(i) {
            continue;
        }
        let (w_i, upper) = win.upper(i);
        out.lookups += 1;
        // Each column was read from a u32, and h is below n, itself checked against the u32 range by the caller.
        match upper.binary_search_by_key(&(h as u32), |e| e.0) {
            Ok(p) => {
                out.found += 1;
                let z_ih = upper[p].1;
                // |w| < 2^32 and |z| <= 2^31, so each product fits in i64.
                if i64::from(w_i) * i64::from(z_ih) != i64::from(row.w) * i64::from(z_hi) {
                    out.value_mismatch += 1;
                    note(detail, format!("ALLPAIRS_BAD|kind=value_mismatch|i={i}|h={h}|w_i={w_i}|z_ih={z_ih}|w_h={}|z_hi={z_hi}|json=0", row.w));
                }
            }
            Err(_) => {
                out.lower_without_upper += 1;
                note(detail, format!("ALLPAIRS_BAD|kind=lower_without_upper|row={h}|col={i}|z={z_hi}|json=0"));
            }
        }
    }
}

/// One walk over every row, with the window starting at row `start`. The census runs on the first walk.
fn one_pass(dev: &mut segio::Dev, off: u64, hdr: &roomio::Hdr, start: usize, (cap, reserve): (usize, usize), mut census: Option<&mut Census>, detail: &mut Vec<String>) -> Result<PassOut, String> {
    let t0 = std::time::Instant::now();
    let mut win = Window::new(start, cap, reserve);
    let mut out = PassOut { start, ..PassOut::default() };
    let n = hdr.n;
    roomio::stream(dev, off, hdr, |h, row| {
        if let Some(c) = census.as_deref_mut() {
            c.row(h, row, n);
        }
        if h >= start {
            answer(&win, h, row, &mut out, detail);
            win.admit(h, row);
        }
    })?;
    out.end = win.end;
    out.stored = win.ent.len() as u64;
    out.upper_without_lower = out.stored.saturating_sub(out.found);
    out.secs = t0.elapsed().as_secs();
    Ok(out)
}

struct Outcome {
    census: Census,
    passes: Vec<PassOut>,
    detail: Vec<String>,
}

impl Outcome {
    fn total(&self, f: impl Fn(&PassOut) -> u64) -> u64 {
        self.passes.iter().map(f).sum()
    }

    /// Windows follow one another from row 0 to row n, with nothing left out.
    fn covers(&self, n: usize) -> bool {
        let mut at = 0;
        for p in &self.passes {
            if p.start != at || p.end <= p.start {
                return false;
            }
            at = p.end;
        }
        at == n
    }

    /// Every entry is accounted for: each upper entry was stored once and answered once, with an equal value.
    fn pairs_clean(&self, n: usize) -> bool {
        let c = &self.census;
        self.covers(n)
            && c.upper == c.lower
            && c.entries == c.upper + c.lower + c.diag
            && self.total(|p| p.stored) == c.upper
            && self.total(|p| p.found) == c.upper
            && self.total(|p| p.value_mismatch) == 0
            && self.total(|p| p.lower_without_upper) == 0
            && self.total(|p| p.upper_without_lower) == 0
    }
}

fn run(dev: &mut segio::Dev, off: u64, hdr: &roomio::Hdr, cap: usize, mut each: impl FnMut(usize, &PassOut)) -> Result<Outcome, String> {
    if u32::try_from(hdr.n).is_err() {
        return Err("n does not fit in u32".into());
    }
    let cap = cap.clamp(1, MAX_CAP);
    let mut census = Census::default();
    let mut passes: Vec<PassOut> = Vec::new();
    let mut detail = Vec::new();
    let room_bound = usize::try_from(hdr.payload / 8).map_err(|_| "payload")?;
    let mut start = 0;
    while start < hdr.n {
        let reserve = if passes.is_empty() {
            cap.min(room_bound)
        } else {
            let kept: u64 = passes.iter().map(|p| p.stored).sum();
            cap.min(usize::try_from(census.upper.saturating_sub(kept)).map_err(|_| "upper")?)
        };
        let first = passes.is_empty();
        let p = one_pass(dev, off, hdr, start, (cap, reserve), first.then_some(&mut census), &mut detail)?;
        if p.end <= start {
            return Err(format!("no progress at row {start}"));
        }
        start = p.end;
        each(passes.len(), &p);
        passes.push(p);
    }
    Ok(Outcome { census, passes, detail })
}

/// The header line again, for the fields `roomio::Hdr` leaves out.
fn raw_header(dev: &mut segio::Dev, off: u64) -> Result<String, String> {
    let mut blk = vec![0u8; 4096];
    dev.seek(SeekFrom::Start(off)).map_err(|e| format!("seek: {e}"))?;
    dev.read_exact(&mut blk).map_err(|e| format!("read header: {e}"))?;
    let end = blk.iter().position(|&b| b == b'\n').ok_or("no header line")?;
    Ok(String::from_utf8_lossy(&blk[..end]).to_string())
}

fn field<'a>(line: &'a str, key: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(key))
}

/// Gauge-fixed codes of an AxB periodic lattice: 6^(links - V + 1) = 6^(V + 1), since links = 2V.
fn codes(lattice: &str, nl: Option<&str>) -> Option<u128> {
    let (a, b) = lattice.split_once('x')?;
    let v = a.parse::<u32>().ok()?.checked_mul(b.parse::<u32>().ok()?)?;
    if nl?.parse::<u32>().ok()? != v.checked_mul(2)? {
        return None;
    }
    6u128.checked_pow(v.checked_add(1)?)
}

fn real_main(a: &[String]) -> Result<bool, String> {
    let t0 = std::time::Instant::now();
    let spec = a.get(1).ok_or("usage: allpairs DEV OFFSET [CAP_ENTRIES]")?;
    let off: u64 = a.get(2).ok_or("missing OFFSET")?.parse().map_err(|_| "bad OFFSET")?;
    let cap: usize = match a.get(3) {
        Some(v) => v.parse().map_err(|_| "bad CAP_ENTRIES")?,
        None => DEFAULT_CAP,
    };
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    let line = raw_header(&mut dev, off)?;
    let o = run(&mut dev, off, &hdr, cap, |k, p| {
        println!(
            "ALLPAIRS_PASS|pass={k}|rows_from={}|rows_to={}|upper_stored={}|lookups={}|found={}|value_mismatch={}|lower_without_upper={}|upper_without_lower={}|merkle=PASS|secs={}|json=0",
            p.start, p.end, p.stored, p.lookups, p.found, p.value_mismatch, p.lower_without_upper, p.upper_without_lower, p.secs
        );
    })?;
    let c = &o.census;
    for d in &o.detail {
        println!("{d}");
    }
    let header_entries = field(&line, "entries=").and_then(|v| v.parse::<u64>().ok());
    let entries_gate = match header_entries {
        Some(v) if v == c.entries => "PASS",
        Some(_) => "FAIL",
        None => "OPEN",
    };
    let expected = codes(&hdr.lattice, field(&line, "nl="));
    let count_gate = match expected {
        Some(v) if v == c.sum_w => "PASS",
        Some(_) => "FAIL",
        None => "OPEN",
    };
    let flat_w_sum: u64 = c.flat_w.iter().map(|&w| u64::from(w)).sum();
    let flat_list: Vec<String> = c.flat_w.iter().map(u32::to_string).collect();
    let pass = o.pairs_clean(hdr.n) && c.structure_clean() && entries_gate != "FAIL" && count_gate != "FAIL";
    println!(
        "ALLPAIRS|L={}|sector={}|n={}|rows_read={}|entries={}|header_entries={entries_gate}|diag={}|pairs={}|passes={}|cap_entries={cap}|value_mismatch={}|lower_without_upper={}|upper_without_lower={}|columns_not_ascending={}|column_out_of_range={}|zero_z={}|positive_offdiag={}|row_sum_nonzero={}|zero_weight={}|missing_diag={}|flats={}|flat_w={}|flat_w_sum={flat_w_sum}|sum_w={}|codes={}|whole_space_count={count_gate}|merkle=PASS|verdict={}|secs={}|json=0",
        hdr.lattice,
        hdr.sector,
        hdr.n,
        c.rows,
        c.entries,
        c.diag,
        c.upper,
        o.passes.len(),
        o.total(|p| p.value_mismatch),
        o.total(|p| p.lower_without_upper),
        o.total(|p| p.upper_without_lower),
        c.not_ascending,
        c.out_of_range,
        c.zero_z,
        c.positive_off,
        c.row_sum_nonzero,
        c.zero_weight,
        c.missing_diag,
        c.flat_w.len(),
        flat_list.join(","),
        c.sum_w,
        expected.map_or("-".to_string(), |v| v.to_string()),
        if pass { "PASS" } else { "FAIL" },
        t0.elapsed().as_secs()
    );
    Ok(pass)
}

#[allow(dead_code)]
fn tool_main() {
    let a: Vec<String> = std::env::args().collect();
    match real_main(&a) {
        Ok(true) => {}
        Ok(false) => std::process::exit(2),
        Err(e) => {
            println!("ALLPAIRS|verdict=FAIL|reason={e}|json=0");
            eprintln!("allpairs: {e}");
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU32, Ordering as AtomicOrdering};

    static NEXT: AtomicU32 = AtomicU32::new(0);

    fn temp() -> std::path::PathBuf {
        std::env::temp_dir().join(format!("allpairs-test-{}-{}", std::process::id(), NEXT.fetch_add(1, AtomicOrdering::Relaxed)))
    }

    fn check_file(p: &std::path::Path, n: usize, cap: usize) -> Result<Outcome, String> {
        let mut dev = segio::open(p.to_str().unwrap(), false).unwrap();
        let hdr = roomio::read_hdr(&mut dev, 0).unwrap();
        assert_eq!(hdr.n, n);
        run(&mut dev, 0, &hdr, cap, |_, _| {})
    }

    fn check(rows: &[roomio::TestRow], cap: usize) -> Outcome {
        let p = temp();
        roomio::write_test_stream(&p, rows);
        let o = check_file(&p, rows.len(), cap).unwrap();
        std::fs::remove_file(p).unwrap();
        o
    }

    fn gcd(a: u32, b: u32) -> u32 {
        if b == 0 {
            a
        } else {
            gcd(b, a % b)
        }
    }

    /// A W-self-adjoint store of 40 rows with zero row sums: w_h z_hj = w_j z_jh = -lcm(w_h, w_j) on the chosen pairs.
    fn store() -> Vec<roomio::TestRow> {
        let n = 40u32;
        let w: Vec<u32> = (0..n).map(|h| 1 + (h * 5 + 3) % 12).collect();
        let joined = |a: u32, b: u32| a != b && ((a * 7 + b * 7 + a * b) % 5 == 0 || a.abs_diff(b) == 1 || a.min(b) == 1 && a.max(b) == 39);
        (0..n)
            .map(|h| {
                let wh = w[h as usize];
                let mut ent = Vec::new();
                let mut off = 0i32;
                for j in 0..n {
                    if joined(h, j) {
                        let wj = w[j as usize];
                        let z = -i32::try_from(wj / gcd(wh, wj)).unwrap();
                        off += z;
                        ent.push((j, z));
                    }
                }
                ent.push((h, -off));
                ent.sort_unstable_by_key(|e| e.0);
                let mag = u16::from(h != 0) * 3;
                (wh, mag, ent)
            })
            .collect()
    }

    fn entry(r: &mut [roomio::TestRow], h: usize, j: u32) -> &mut i32 {
        &mut r[h].2.iter_mut().find(|e| e.0 == j).unwrap().1
    }

    const CAPS: [usize; 7] = [1, 2, 3, 5, 8, 13, 100_000];

    #[test]
    fn a_clean_store_passes_at_every_cap_with_the_same_count() {
        let r = store();
        let mut pairs = None;
        for cap in CAPS {
            let o = check(&r, cap);
            assert!(o.pairs_clean(r.len()) && o.census.structure_clean(), "cap {cap}");
            assert!(o.covers(r.len()));
            assert_eq!(o.census.diag, 40);
            assert_eq!(*pairs.get_or_insert(o.census.upper), o.census.upper);
            assert_eq!(o.census.entries, o.census.diag + 2 * o.census.upper);
        }
        assert!(pairs.unwrap() > 39);
        assert_eq!(check(&r, 1).passes.len(), 39, "the last row holds no upper entry, so it shares a window");
        assert_eq!(check(&r, 100_000).passes.len(), 1);
    }

    #[test]
    fn one_changed_value_with_its_row_sum_kept_is_found_at_every_cap() {
        for cap in CAPS {
            for (h, j) in [(1usize, 39u32), (39, 1), (5, 6), (6, 5)] {
                let mut r = store();
                *entry(&mut r, h, j) -= 1;
                *entry(&mut r, h, h as u32) += 1;
                let o = check(&r, cap);
                assert_eq!(o.total(|p| p.value_mismatch), 1, "cap {cap} pair {h},{j}");
                assert_eq!(o.census.row_sum_nonzero, 0);
                assert!(!o.pairs_clean(r.len()));
                assert_eq!(o.detail.len(), 1);
                let (lo, hi) = (h.min(j as usize), h.max(j as usize));
                assert!(o.detail[0].contains(&format!("|i={lo}|h={hi}|")), "{}", o.detail[0]);
            }
        }
    }

    #[test]
    fn an_upper_entry_with_no_partner_fails() {
        for cap in CAPS {
            let mut r = store();
            r[39].2.retain(|e| e.0 != 1);
            let o = check(&r, cap);
            assert_eq!(o.total(|p| p.upper_without_lower), 1, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_without_upper), 0);
            assert!(!o.pairs_clean(r.len()));
        }
    }

    #[test]
    fn a_lower_entry_with_no_partner_fails() {
        for cap in CAPS {
            let mut r = store();
            r[1].2.retain(|e| e.0 != 39);
            let o = check(&r, cap);
            assert_eq!(o.total(|p| p.lower_without_upper), 1, "cap {cap}");
            assert_eq!(o.total(|p| p.upper_without_lower), 0);
            assert!(!o.pairs_clean(r.len()));
        }
    }

    #[test]
    fn a_diagonal_change_trips_the_row_sum_and_no_pair() {
        let mut r = store();
        *entry(&mut r, 7, 7) += 1;
        let o = check(&r, 5);
        assert_eq!(o.census.row_sum_nonzero, 1);
        assert!(!o.census.structure_clean());
        assert!(o.pairs_clean(r.len()));
    }

    #[test]
    fn a_changed_weight_breaks_every_pair_of_that_row() {
        let mut r = store();
        r[9].0 += 1;
        let neighbours = r[9].2.iter().filter(|e| e.0 != 9).count() as u64;
        let o = check(&r, 3);
        assert_eq!(o.total(|p| p.value_mismatch), neighbours);
        assert!(!o.pairs_clean(r.len()));
    }

    #[test]
    fn a_change_that_keeps_the_weighted_equality_passes_this_test() {
        // Scope: this test reads the stored equality alone. Recomputing the row from the rules is fullrebuild's test.
        let mut r = store();
        let (wa, wb) = (r[5].0, r[6].0);
        let g = gcd(wa, wb);
        *entry(&mut r, 5, 6) -= i32::try_from(wb / g).unwrap();
        *entry(&mut r, 6, 5) -= i32::try_from(wa / g).unwrap();
        *entry(&mut r, 5, 5) += i32::try_from(wb / g).unwrap();
        *entry(&mut r, 6, 6) += i32::try_from(wa / g).unwrap();
        let o = check(&r, 4);
        assert!(o.pairs_clean(r.len()) && o.census.structure_clean());
    }

    #[test]
    fn structural_faults_are_counted() {
        let mut r = store();
        r[3].2.swap(0, 1);
        let o = check(&r, 100_000);
        assert_eq!(o.census.not_ascending, 1);
        assert!(!o.census.structure_clean());

        let mut r = store();
        *entry(&mut r, 4, 5) = 2;
        *entry(&mut r, 4, 4) -= 2 - *entry(&mut store(), 4, 5);
        assert_eq!(check(&r, 100_000).census.positive_off, 1);

        let mut r = store();
        r[8].2.retain(|e| e.0 != 8);
        assert_eq!(check(&r, 100_000).census.missing_diag, 1);

        let mut r = store();
        r[8].0 = 0;
        assert_eq!(check(&r, 100_000).census.zero_weight, 1);

        let mut r = store();
        r[39].2.push((40, -1));
        assert_eq!(check(&r, 100_000).census.out_of_range, 1);
    }

    #[test]
    fn the_largest_stored_values_do_not_overflow() {
        let r = vec![(u32::MAX, 3, vec![(1, i32::MIN)]), (u32::MAX, 3, vec![(0, i32::MIN)])];
        let o = check(&r, 100);
        assert_eq!(o.total(|p| p.value_mismatch), 0);
        assert_eq!(o.total(|p| p.found), 1);
        let r = vec![(u32::MAX, 3, vec![(1, i32::MIN)]), (u32::MAX, 3, vec![(0, i32::MIN + 1)])];
        assert_eq!(check(&r, 100).total(|p| p.value_mismatch), 1);
    }

    #[test]
    fn damage_without_a_repaired_merkle_stops_the_run() {
        let p = temp();
        roomio::write_test_stream(&p, &store());
        let mut b = std::fs::read(&p).unwrap();
        b[4096 + 8 + 4] ^= 1;
        std::fs::write(&p, b).unwrap();
        let e = check_file(&p, 40, 100_000).err().unwrap();
        std::fs::remove_file(p).unwrap();
        assert!(e.contains("merkle"), "{e}");
    }

    #[test]
    fn the_count_of_codes_needs_a_matching_link_count() {
        assert_eq!(codes("3x4", Some("24")), Some(13_060_694_016));
        assert_eq!(codes("2x2", Some("8")), Some(7_776));
        assert_eq!(codes("3x4", Some("23")), None);
        assert_eq!(codes("3x4", None), None);
        assert_eq!(codes("1x40", None), None);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
// Second seat's harness, appended to an otherwise unchanged copy of allpairs.rs: main is renamed tool_main, and the three
// #[path] lines point into the checkout. The oracle below shares no code with the tool: its own SHA-256, its own header
// and row parser, its own pair test by hash map. It calls the tool's real_main for the verdict and run() for the counters.
//
//   fuzz fuzz SEED ITERATIONS TMPFILE     random stores, malformed and clean, at random caps
//   fuzz sweep STORE TMPFILE              one fault at a time on every entry of a real store, at several caps
//
// Exit 1 when the tool and the oracle disagree in a class the prediction did not name. Integer only, json=0.

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let code = review::main(&a);
    std::process::exit(code);
}

mod review {
    use std::collections::HashMap;
    use std::panic::{catch_unwind, AssertUnwindSafe};

    // ------------------------------------------------------------ PRNG
    pub struct Rng(u64);
    impl Rng {
        fn next(&mut self) -> u64 {
            self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = self.0;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            z ^ (z >> 31)
        }
        fn below(&mut self, n: u64) -> u64 {
            self.next() % n.max(1)
        }
        fn pick<'a, T>(&mut self, v: &'a [T]) -> &'a T {
            &v[self.below(v.len() as u64) as usize]
        }
    }

    // ------------------------------------------------------------ own SHA-256, as in the second seat's reader
    fn sha_tables() -> ([u32; 64], [u32; 8]) {
        let mut primes: Vec<u64> = Vec::new();
        let mut c = 2u64;
        while primes.len() < 64 {
            if primes.iter().all(|p| c % p != 0) {
                primes.push(c);
            }
            c += 1;
        }
        let root = |v: u128, e: u32| {
            let (mut lo, mut hi) = (0u128, 1u128 << 37);
            while hi - lo > 1 {
                let m = (lo + hi) / 2;
                if m.pow(e) <= v {
                    lo = m;
                } else {
                    hi = m;
                }
            }
            lo
        };
        let mut k = [0u32; 64];
        let mut h = [0u32; 8];
        for (i, s) in k.iter_mut().enumerate() {
            *s = (root(u128::from(primes[i]) << 96, 3) & 0xFFFF_FFFF) as u32;
        }
        for (i, s) in h.iter_mut().enumerate() {
            *s = (root(u128::from(primes[i]) << 64, 2) & 0xFFFF_FFFF) as u32;
        }
        (k, h)
    }

    pub struct Sha256 {
        k: [u32; 64],
        h0: [u32; 8],
    }

    impl Sha256 {
        pub fn new() -> Sha256 {
            let (k, h0) = sha_tables();
            Sha256 { k, h0 }
        }
        pub fn hex(&self, d: &[u8]) -> String {
            let mut h = self.h0;
            let mut m = d.to_vec();
            m.push(0x80);
            while m.len() % 64 != 56 {
                m.push(0);
            }
            m.extend_from_slice(&((d.len() as u64).wrapping_mul(8)).to_be_bytes());
            for b in m.chunks_exact(64) {
                let mut w = [0u32; 64];
                for (i, c) in b.chunks_exact(4).enumerate() {
                    w[i] = u32::from_be_bytes([c[0], c[1], c[2], c[3]]);
                }
                for i in 16..64 {
                    let (a, e) = (w[i - 15], w[i - 2]);
                    let s0 = a.rotate_right(7) ^ a.rotate_right(18) ^ (a >> 3);
                    let s1 = e.rotate_right(17) ^ e.rotate_right(19) ^ (e >> 10);
                    w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
                }
                let mut v = h;
                for (wi, ki) in w.iter().zip(self.k.iter()) {
                    let bs1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
                    let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
                    let t1 = v[7].wrapping_add(bs1).wrapping_add(ch).wrapping_add(*ki).wrapping_add(*wi);
                    let bs0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
                    let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
                    let t2 = bs0.wrapping_add(maj);
                    v = [t1.wrapping_add(t2), v[0], v[1], v[2], v[3].wrapping_add(t1), v[4], v[5], v[6]];
                }
                for (x, y) in h.iter_mut().zip(v) {
                    *x = x.wrapping_add(y);
                }
            }
            let mut s = String::with_capacity(64);
            for w in h {
                for b in w.to_be_bytes() {
                    s.push(char::from_digit(u32::from(b >> 4), 16).unwrap_or('?'));
                    s.push(char::from_digit(u32::from(b & 15), 16).unwrap_or('?'));
                }
            }
            s
        }
        pub fn merkle(&self, payload: &[u8]) -> String {
            let mut hx = String::new();
            for c in payload.chunks(16 << 20) {
                hx.push_str(&self.hex(c));
            }
            self.hex(hx.as_bytes())
        }
    }

    // ------------------------------------------------------------ stores
    #[derive(Clone)]
    pub struct R {
        w: u32,
        mag: u16,
        ent: Vec<(u32, i32)>,
    }

    fn gcd(a: u32, b: u32) -> u32 {
        if b == 0 {
            a
        } else {
            gcd(b, a % b)
        }
    }

    /// A clean store: ring plus chords, w_h z_hj = w_j z_jh by construction, positive diagonal, zero row sums.
    /// With target = Some(t) the weights sum to t.
    fn clean_store(rng: &mut Rng, n: usize, target: Option<u64>) -> Vec<R> {
        let mut w: Vec<u32> = (0..n).map(|_| 1 + rng.below(12) as u32).collect();
        if let Some(t) = target {
            w = vec![1; n];
            let mut left = t - n as u64;
            while left > 0 {
                let i = rng.below(n as u64) as usize;
                let add = 1 + rng.below(left.min(97));
                w[i] += add as u32;
                left -= add;
            }
        }
        let mut edges: HashMap<(usize, usize), i32> = HashMap::new();
        for a in 0..n {
            let b = (a + 1) % n;
            if a != b {
                edges.insert((a.min(b), a.max(b)), 1 + rng.below(3) as i32);
            }
        }
        for _ in 0..rng.below(2 * n as u64) {
            let (a, b) = (rng.below(n as u64) as usize, rng.below(n as u64) as usize);
            if a != b {
                edges.insert((a.min(b), a.max(b)), 1 + rng.below(3) as i32);
            }
        }
        let mut rows: Vec<R> = (0..n).map(|h| R { w: w[h], mag: if rng.below(5) == 0 { 0 } else { 3 + rng.below(9) as u16 }, ent: Vec::new() }).collect();
        for (&(a, b), &k) in &edges {
            let g = gcd(w[a], w[b]);
            rows[a].ent.push((b as u32, -((w[b] / g) as i32) * k));
            rows[b].ent.push((a as u32, -((w[a] / g) as i32) * k));
        }
        for (h, r) in rows.iter_mut().enumerate() {
            let s: i32 = r.ent.iter().map(|e| e.1).sum();
            r.ent.push((h as u32, -s));
            r.ent.sort_unstable_by_key(|e| e.0);
        }
        rows
    }

    pub fn serialize(rows: &[R]) -> Vec<u8> {
        let mut p = Vec::new();
        for r in rows {
            p.extend_from_slice(&r.w.to_le_bytes());
            p.extend_from_slice(&r.mag.to_le_bytes());
            p.extend_from_slice(&(r.ent.len() as u16).to_le_bytes());
            for (j, z) in &r.ent {
                p.extend_from_slice(&j.to_le_bytes());
                p.extend_from_slice(&z.to_le_bytes());
            }
        }
        p
    }

    fn file_bytes(line: &str, payload: &[u8]) -> Vec<u8> {
        let mut b = line.as_bytes().to_vec();
        b.push(b'\n');
        if b.len() < 4096 {
            b.resize(4096, 0);
        }
        b.extend_from_slice(payload);
        b
    }

    fn header_line(fields: &[(String, String)]) -> String {
        let mut s = String::from("YMROOMHDR");
        for (k, v) in fields {
            s.push('|');
            s.push_str(k);
            s.push('=');
            s.push_str(v);
        }
        s
    }

    // ------------------------------------------------------------ oracle
    #[derive(Default, Clone, PartialEq, Eq, Debug)]
    pub struct Truth {
        rows: u64,
        entries: u64,
        diag: u64,
        upper: u64,
        lower: u64,
        not_ascending: u64,
        out_of_range: u64,
        zero_z: u64,
        positive_off: u64,
        row_sum_nonzero: u64,
        zero_weight: u64,
        missing_diag: u64,
        sum_w: u128,
        mismatch: u64,
        lonely_lower: u64,
        lonely_upper: u64,
        trailing_nonzero: u64,
        structure_clean: bool,
    }

    pub enum Expect {
        /// exit 1, the reason word is for the report
        Err(&'static str),
        /// exit 0 or 2
        Verdict { pass: bool, truth: Box<Truth>, n0: bool, entries_open: bool, count_open: bool, sym_true: bool },
    }

    fn fld<'a>(line: &'a str, key: &str) -> Option<&'a str> {
        line.split('|').find_map(|kv| kv.strip_prefix(key))
    }

    fn oracle_codes(line: &str) -> Option<u128> {
        let l = fld(line, "L=")?;
        let (a, b) = l.split_once('x')?;
        let (a, b): (u32, u32) = (a.parse().ok()?, b.parse().ok()?);
        let v = a.checked_mul(b)?;
        let nl: u32 = fld(line, "nl=")?.parse().ok()?;
        if nl != v.checked_mul(2)? {
            return None;
        }
        6u128.checked_pow(v.checked_add(1)?)
    }

    pub fn oracle(file: &[u8], sha: &Sha256) -> Expect {
        if file.len() < 4096 {
            return Expect::Err("short_header");
        }
        let Some(eol) = file[..4096].iter().position(|&b| b == b'\n') else {
            return Expect::Err("no_newline");
        };
        let line = String::from_utf8_lossy(&file[..eol]).to_string();
        if !line.starts_with("YMROOMHDR|") || fld(&line, "w_self_adjoint=") != Some("PASS") {
            return Expect::Err("not_header");
        }
        let Some(n) = fld(&line, "n=").and_then(|v| v.parse::<u64>().ok()) else {
            return Expect::Err("bad_n");
        };
        let Some(payload) = fld(&line, "payload_bytes=").and_then(|v| v.parse::<u64>().ok()) else {
            return Expect::Err("bad_payload");
        };
        if n > u64::from(u32::MAX) {
            return Expect::Err("n_too_large");
        }
        let entries_field = fld(&line, "entries=").and_then(|v| v.parse::<u64>().ok());
        let expected = oracle_codes(&line);
        if n == 0 {
            let truth = Truth { structure_clean: true, ..Truth::default() };
            let entries_ok = entries_field.map_or(true, |v| v == 0);
            let count_ok = expected.map_or(true, |v| v == 0);
            return Expect::Verdict { pass: entries_ok && count_ok, truth: Box::new(truth), n0: true, entries_open: entries_field.is_none(), count_open: expected.is_none(), sym_true: true };
        }
        let end = 4096u64.saturating_add(payload);
        if (file.len() as u64) < end {
            return Expect::Err("payload_past_file");
        }
        let pl = &file[4096..end as usize];
        // rows
        let mut t = Truth::default();
        let mut p = 0usize;
        let mut wts: Vec<u32> = Vec::new();
        let mut upper: HashMap<(u32, u32), i64> = HashMap::new();
        let mut lower: Vec<(u32, u32, i64)> = Vec::new();
        let mut dup_or_disorder = false;
        for h in 0..n {
            if p + 8 > pl.len() {
                return Expect::Err("rows_past_payload");
            }
            let w = u32::from_le_bytes([pl[p], pl[p + 1], pl[p + 2], pl[p + 3]]);
            let cnt = usize::from(u16::from_le_bytes([pl[p + 6], pl[p + 7]]));
            if p + 8 + 8 * cnt > pl.len() {
                return Expect::Err("rows_past_payload");
            }
            let mut q = p + 8;
            let mut prev: Option<u32> = None;
            let mut sum = 0i64;
            let mut has_diag = false;
            t.rows += 1;
            t.sum_w += u128::from(w);
            t.zero_weight += u64::from(w == 0);
            wts.push(w);
            for _ in 0..cnt {
                let j = u32::from_le_bytes([pl[q], pl[q + 1], pl[q + 2], pl[q + 3]]);
                let z = i32::from_le_bytes([pl[q + 4], pl[q + 5], pl[q + 6], pl[q + 7]]);
                q += 8;
                t.entries += 1;
                if prev.is_some_and(|x| j <= x) {
                    t.not_ascending += 1;
                    dup_or_disorder = true;
                }
                prev = Some(j);
                if u64::from(j) >= n {
                    t.out_of_range += 1;
                }
                if z == 0 {
                    t.zero_z += 1;
                }
                if u64::from(j) != h && z > 0 {
                    t.positive_off += 1;
                }
                sum += i64::from(z);
                let v = i128::from(w) * i128::from(z);
                let v64 = i64::try_from(v).unwrap_or(i64::MAX);
                match u64::from(j).cmp(&h) {
                    std::cmp::Ordering::Equal => {
                        t.diag += 1;
                        has_diag = true;
                    }
                    std::cmp::Ordering::Greater => {
                        t.upper += 1;
                        upper.insert((h as u32, j), v64);
                    }
                    std::cmp::Ordering::Less => {
                        t.lower += 1;
                        lower.push((j, h as u32, v64));
                    }
                }
            }
            t.row_sum_nonzero += u64::from(sum != 0);
            t.missing_diag += u64::from(!has_diag);
            p = q;
        }
        // Padding after the last row.
        t.trailing_nonzero = pl[p..].iter().filter(|&&b| b != 0).count() as u64;
        // Merkle.
        if sha.merkle(pl) != fld(&line, "payload_merkle=").unwrap_or("") {
            return Expect::Err("merkle");
        }
        // Pairs, by hash map, on the rows as stored.
        let mut used: HashMap<(u32, u32), bool> = HashMap::new();
        for (a, b, v) in &lower {
            match upper.get(&(*a, *b)) {
                Some(u) => {
                    used.insert((*a, *b), true);
                    if u != v {
                        t.mismatch += 1;
                    }
                }
                None => t.lonely_lower += 1,
            }
        }
        t.lonely_upper = upper.keys().filter(|k| !used.contains_key(k)).count() as u64;
        t.structure_clean = t.not_ascending == 0 && t.out_of_range == 0 && t.zero_z == 0 && t.positive_off == 0 && t.row_sum_nonzero == 0 && t.zero_weight == 0 && t.missing_diag == 0;
        let pairs_clean = t.mismatch == 0 && t.lonely_lower == 0 && t.lonely_upper == 0 && t.upper == t.lower;
        let entries_ok = entries_field.map_or(true, |v| v == t.entries);
        let count_ok = expected.map_or(true, |v| v == t.sum_w);
        let sym_true = pairs_clean && !dup_or_disorder && t.out_of_range == 0;
        let pass = t.structure_clean && pairs_clean && entries_ok && count_ok;
        Expect::Verdict { pass, truth: Box::new(t), n0: false, entries_open: entries_field.is_none(), count_open: expected.is_none(), sym_true }
    }

    // ------------------------------------------------------------ one case
    #[derive(Default)]
    struct Tally {
        cases: u64,
        tool_err: u64,
        tool_fail: u64,
        tool_pass: u64,
        strict_pass: u64,
        pass_n0: u64,
        pass_entries_open: u64,
        pass_count_open: u64,
        pass_trailing_nonzero: u64,
        pass_clean: u64,
        false_pass_main_property: u64,
        disagree_verdict: u64,
        disagree_err: u64,
        disagree_counters: u64,
        cap_variant_counters: u64,
        masked_unpaired: u64,
        panics: u64,
    }

    fn run_counters(path: &str, cap: usize) -> Option<(u64, u64, u64, u64, u64)> {
        let mut dev = super::segio::open(path, false).ok()?;
        let hdr = super::roomio::read_hdr(&mut dev, 0).ok()?;
        let o = super::run(&mut dev, 0, &hdr, cap, |_, _| {}).ok()?;
        Some((o.total(|p| p.value_mismatch), o.total(|p| p.lower_without_upper), o.total(|p| p.upper_without_lower), o.census.upper, o.total(|p| p.found)))
    }

    fn record(tag: &str, file: &[u8], seed: u64, iter: u64, shown: &mut HashMap<String, u32>, note: String) {
        let seen = shown.entry(tag.to_string()).or_insert(0);
        if *seen < 3 {
            *seen += 1;
            eprintln!("FUZZ_EXAMPLE|class={tag}|seed={seed}|iter={iter}|{note}|json=0");
            let dir = "C:/tmp/opus55/allpairs-review-20261103/fuzz/examples";
            let _ = std::fs::create_dir_all(dir);
            let _ = std::fs::write(format!("{dir}/{tag}-{seed}-{iter}.bin"), file);
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn one_case(file: &[u8], cap: usize, cap2: usize, tmp: &str, sha: &Sha256, tally: &mut Tally, seed: u64, iter: u64, shown: &mut HashMap<String, u32>) {
        if std::fs::write(tmp, file).is_err() {
            eprintln!("FUZZ_FAIL|write|json=0");
            std::process::exit(9);
        }
        tally.cases += 1;
        let args: Vec<String> = vec!["allpairs".into(), tmp.to_string(), "0".into(), cap.to_string()];
        let got = catch_unwind(AssertUnwindSafe(|| super::real_main(&args)));
        let want = oracle(file, sha);
        let Ok(got) = got else {
            tally.panics += 1;
            record("panic", file, seed, iter, shown, format!("cap={cap}"));
            return;
        };
        match (&got, &want) {
            (Err(e), Expect::Err(_)) => {
                let _ = e;
                tally.tool_err += 1;
            }
            (Err(e), Expect::Verdict { .. }) => {
                tally.tool_err += 1;
                tally.disagree_err += 1;
                record("tool_err_oracle_verdict", file, seed, iter, shown, format!("cap={cap}|tool={e}"));
            }
            (Ok(v), Expect::Err(why)) => {
                tally.disagree_err += 1;
                record("tool_verdict_oracle_err", file, seed, iter, shown, format!("cap={cap}|tool={v}|oracle={why}"));
            }
            (Ok(v), Expect::Verdict { pass, truth, n0, entries_open, count_open, sym_true }) => {
                if *v {
                    tally.tool_pass += 1;
                } else {
                    tally.tool_fail += 1;
                }
                if v != pass {
                    tally.disagree_verdict += 1;
                    record("verdict", file, seed, iter, shown, format!("cap={cap}|tool={v}|oracle={pass}"));
                }
                if *v {
                    let trailing = truth.trailing_nonzero > 0;
                    if *n0 {
                        tally.pass_n0 += 1;
                    }
                    if *entries_open {
                        tally.pass_entries_open += 1;
                    }
                    if *count_open {
                        tally.pass_count_open += 1;
                    }
                    if trailing {
                        tally.pass_trailing_nonzero += 1;
                    }
                    if !*n0 && !*entries_open && !*count_open && !trailing {
                        tally.pass_clean += 1;
                        tally.strict_pass += 1;
                    }
                    if !*sym_true {
                        tally.false_pass_main_property += 1;
                        record("false_pass", file, seed, iter, shown, format!("cap={cap}"));
                    }
                }
                // Counters. They must be exact, at both caps, whenever every row's columns ascend strictly.
                if !*n0 {
                    if let (Some(a), Some(b)) = (run_counters(tmp, cap), run_counters(tmp, cap2)) {
                        if truth.not_ascending == 0 {
                            let want3 = (truth.mismatch, truth.lonely_lower, truth.lonely_upper);
                            if (a.0, a.1, a.2) != want3 || (b.0, b.1, b.2) != want3 || a.3 != truth.upper {
                                tally.disagree_counters += 1;
                                record("counters", file, seed, iter, shown, format!("cap={cap}|cap2={cap2}|tool={a:?}|tool2={b:?}|want={want3:?}"));
                            }
                        } else {
                            if a != b {
                                tally.cap_variant_counters += 1;
                            }
                            if truth.lonely_upper > 0 && a.2 == 0 {
                                tally.masked_unpaired += 1;
                                record("masked_unpaired", file, seed, iter, shown, format!("cap={cap}|tool_upper_without_lower=0|truth={}", truth.lonely_upper));
                            }
                        }
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------ mutations
    fn fields_for(rows: &[R], payload: &[u8], sha: &Sha256, lattice: &str, nl: Option<u32>) -> Vec<(String, String)> {
        let entries: usize = rows.iter().map(|r| r.ent.len()).sum();
        let mut f = vec![("L".to_string(), lattice.to_string()), ("sector".to_string(), "Sx+Sy+".to_string()), ("n".to_string(), rows.len().to_string())];
        if let Some(v) = nl {
            f.push(("nl".to_string(), v.to_string()));
        }
        f.push(("rooms".to_string(), (rows.len() + entries).to_string()));
        f.push(("entries".to_string(), entries.to_string()));
        f.push(("payload_bytes".to_string(), payload.len().to_string()));
        f.push(("stream_bytes".to_string(), (payload.len() + 4096).to_string()));
        f.push(("chunk".to_string(), "16MiB".to_string()));
        f.push(("payload_merkle".to_string(), sha.merkle(payload)));
        f.push(("keys_sha256".to_string(), "0".repeat(64)));
        f.push(("w_self_adjoint".to_string(), "PASS".to_string()));
        f.push(("json".to_string(), "0".to_string()));
        f
    }

    fn set(f: &mut [(String, String)], k: &str, v: String) {
        if let Some(e) = f.iter_mut().find(|e| e.0 == k) {
            e.1 = v;
        }
    }

    fn mutate_rows(rng: &mut Rng, rows: &mut Vec<R>) {
        let n = rows.len();
        if n == 0 {
            return;
        }
        let h = rng.below(n as u64) as usize;
        let e = rows[h].ent.len();
        let k = if e == 0 { 0 } else { rng.below(e as u64) as usize };
        match rng.below(20) {
            0 if e > 0 => rows[h].ent[k].1 -= 1,
            1 if e > 0 => {
                rows[h].ent[k].1 -= 1;
                if let Some(d) = rows[h].ent.iter_mut().find(|x| x.0 == h as u32) {
                    d.1 += 1;
                }
            }
            2 if e > 0 => {
                rows[h].ent.remove(k);
            }
            3 => {
                let j = rng.below(n as u64 + 2) as u32;
                let z = -1 - rng.below(5) as i32;
                rows[h].ent.push((j, z));
                rows[h].ent.sort_by_key(|x| x.0);
            }
            4 if e > 1 => rows[h].ent.swap(k, 0),
            5 if e > 0 => {
                let c = rows[h].ent[k];
                rows[h].ent.insert(k, c);
            }
            6 if e > 0 => rows[h].ent[k].0 = *rng.pick(&[n as u32, n as u32 + 1, u32::MAX, 0x8000_0000]),
            7 if e > 0 => rows[h].ent[k].1 = *rng.pick(&[0, i32::MIN, i32::MAX, 1, -1]),
            8 => rows[h].w = *rng.pick(&[0, 1, u32::MAX, rows[h].w.wrapping_add(1), rows[h].w.wrapping_mul(2)]),
            9 => {
                for r in rows.iter_mut() {
                    r.w = r.w.wrapping_mul(2);
                }
            }
            10 => rows[h].mag = rng.below(40) as u16,
            11 => {
                rows.pop();
            }
            12 => {
                let r = R { w: 1, mag: 3, ent: vec![(n as u32, 0)] };
                rows.push(r);
            }
            13 if n > 1 => rows.swap(h, (h + 1) % n),
            14 if e > 1 => {
                // Delete a partner elsewhere and double a lower entry here: found stays equal to stored, the structure test must carry it.
                let lower: Vec<(u32, i32)> = rows[h].ent.iter().copied().filter(|x| (x.0 as usize) < h).collect();
                if let Some(&(i, z)) = lower.first() {
                    let pos = rows[h].ent.iter().position(|x| x.0 == i).unwrap_or(0);
                    rows[h].ent.insert(pos, (i, z));
                    let ups: Vec<u32> = rows[i as usize].ent.iter().map(|x| x.0).filter(|&j| j as usize > i as usize && j as usize != h && (j as usize) < n).collect();
                    if let Some(&m) = ups.first() {
                        rows[m as usize].ent.retain(|x| x.0 != i);
                    }
                }
            }
            15 if e > 0 => {
                // A symmetric change that keeps the weighted equality, and both diagonals.
                let (j, _) = rows[h].ent[k];
                if j as usize != h && (j as usize) < n {
                    let (wa, wb) = (rows[h].w, rows[j as usize].w);
                    if wa > 0 && wb > 0 {
                        let g = gcd(wa, wb);
                        let (da, db) = ((wb / g) as i32, (wa / g) as i32);
                        for (row, col, d) in [(h, j, da), (j as usize, h as u32, db)] {
                            if let Some(x) = rows[row].ent.iter_mut().find(|x| x.0 == col) {
                                x.1 = x.1.wrapping_sub(d);
                            }
                            let dg = row as u32;
                            if let Some(x) = rows[row].ent.iter_mut().find(|x| x.0 == dg) {
                                x.1 = x.1.wrapping_add(d);
                            }
                        }
                    }
                }
            }
            16 if e > 0 => {
                // Delete both sides of a pair, keep the row sums.
                let (j, z) = rows[h].ent[k];
                if j as usize != h && (j as usize) < n {
                    let z2 = rows[j as usize].ent.iter().find(|x| x.0 == h as u32).map(|x| x.1);
                    rows[h].ent.retain(|x| x.0 != j);
                    if let Some(d) = rows[h].ent.iter_mut().find(|x| x.0 == h as u32) {
                        d.1 = d.1.wrapping_add(z);
                    }
                    if let Some(z2) = z2 {
                        rows[j as usize].ent.retain(|x| x.0 != h as u32);
                        if let Some(d) = rows[j as usize].ent.iter_mut().find(|x| x.0 == j) {
                            d.1 = d.1.wrapping_add(z2);
                        }
                    }
                }
            }
            17 if e > 0 => {
                let (j, z) = rows[h].ent[k];
                rows[h].ent[k] = (j + 1, z);
            }
            18 => rows[h].ent.clear(),
            _ => {}
        }
    }

    fn mutate_header(rng: &mut Rng, f: &mut Vec<(String, String)>, rows_len: usize) {
        match rng.below(19) {
            18 => {
                set(f, "n", "0".into());
                f.retain(|e| e.0 != "entries" && e.0 != "nl");
            }
            0 => set(f, "n", "0".into()),
            1 => set(f, "n", (rows_len + 1 + rng.below(3) as usize).to_string()),
            2 => set(f, "n", rows_len.saturating_sub(1 + rng.below(3) as usize).to_string()),
            3 => f.retain(|e| e.0 != "entries"),
            4 => set(f, "entries", "abc".into()),
            5 => set(f, "entries", "1".into()),
            6 => f.retain(|e| e.0 != "nl"),
            7 => set(f, "nl", "7".into()),
            8 => set(f, "L", "3y4".into()),
            9 => f.retain(|e| e.0 != "L"),
            10 => f.retain(|e| e.0 != "w_self_adjoint"),
            11 => set(f, "w_self_adjoint", "FAIL".into()),
            12 => f.retain(|e| e.0 != "payload_merkle"),
            13 => f.retain(|e| e.0 != "n"),
            14 => f.retain(|e| e.0 != "payload_bytes"),
            15 => set(f, "n", "4294967296".into()),
            16 => set(f, "n", "abc".into()),
            _ => set(f, "payload_merkle", "0".repeat(64)),
        }
    }

    pub fn fuzz(seed: u64, iters: u64, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let mut rng = Rng(seed);
        let mut t = Tally::default();
        let mut shown: HashMap<String, u32> = HashMap::new();
        let t0 = std::time::Instant::now();
        for iter in 0..iters {
            // Half the stores make the count gate reachable: L and nl with weights that sum to 6^(V+1).
            let (lattice, nl, target): (String, Option<u32>, Option<u64>) = match rng.below(4) {
                0 => ("1x1".into(), Some(2), Some(36)),
                1 => ("1x2".into(), Some(4), Some(216)),
                2 => ("1x40".into(), None, None),
                _ => ("2x2".into(), Some(8), Some(7776)),
            };
            let max_n: u64 = if target == Some(36) { 30 } else { 40 };
            let n = 2 + rng.below(max_n - 1) as usize;
            let mut rows = clean_store(&mut rng, n, target);
            let muts = match rng.below(10) {
                0..=2 => 0,
                3..=7 => 1,
                _ => 2 + rng.below(3),
            };
            for _ in 0..muts {
                mutate_rows(&mut rng, &mut rows);
            }
            let mut payload = serialize(&rows);
            // Padding: none, zeros, or nonzero.
            match rng.below(6) {
                0 | 1 => payload.resize(payload.len() + 8 * rng.below(64) as usize, 0),
                2 => {
                    let k = 1 + rng.below(64) as usize;
                    for _ in 0..k {
                        payload.push(rng.below(256) as u8);
                    }
                }
                _ => {}
            }
            // Byte damage in the payload, before or after the merkle.
            let mut fields = fields_for(&rows, &payload, &sha, &lattice, nl);
            match rng.below(12) {
                0 if !payload.is_empty() => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                    set(&mut fields, "payload_merkle", sha.merkle(&payload));
                }
                1 if !payload.is_empty() => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                }
                _ => {}
            }
            if rng.below(5) == 0 {
                mutate_header(&mut rng, &mut fields, rows.len());
            }
            if rng.below(40) == 0 {
                // A payload_bytes that lies, with a merkle over what it names when it can.
                let extra = rng.below(32);
                let new = if rng.below(2) == 0 { (payload.len() as u64).saturating_sub(extra) } else { payload.len() as u64 + extra };
                set(&mut fields, "payload_bytes", new.to_string());
                if new <= payload.len() as u64 {
                    set(&mut fields, "payload_merkle", sha.merkle(&payload[..new as usize]));
                }
            }
            let line = header_line(&fields);
            let mut file = file_bytes(&line, &payload);
            if rng.below(60) == 0 {
                let cut = rng.below(file.len() as u64) as usize;
                file.truncate(cut);
            }
            if rng.below(60) == 0 {
                file.extend_from_slice(&[0xAB; 16]);
            }
            let pairs: u64 = rows.iter().enumerate().map(|(h, r)| r.ent.iter().filter(|e| e.0 as usize > h).count() as u64).sum();
            let caps = [0usize, 1, 2, 3, 5, 8, 13, 21, 34, pairs as usize, pairs as usize + 1, 470_000_000];
            let cap = *rng.pick(&caps);
            let cap2 = *rng.pick(&caps);
            one_case(&file, cap, cap2, tmp, &sha, &mut t, seed, iter, &mut shown);
        }
        let _ = std::fs::remove_file(tmp);
        eprintln!(
            "FUZZ_DONE|seed={seed}|cases={}|tool_exit1={}|tool_exit2={}|tool_exit0={}|pass_clean_all_gates={}|pass_with_n0={}|pass_with_entries_open={}|pass_with_count_open={}|pass_with_nonzero_padding={}|false_pass_main_property={}|disagree_verdict={}|disagree_exit_class={}|disagree_counters_on_ascending_rows={}|cap_variant_counters_on_non_ascending_rows={}|masked_unpaired_on_non_ascending_rows={}|panics={}|secs={}|json=0",
            t.cases,
            t.tool_err,
            t.tool_fail,
            t.tool_pass,
            t.pass_clean,
            t.pass_n0,
            t.pass_entries_open,
            t.pass_count_open,
            t.pass_trailing_nonzero,
            t.false_pass_main_property,
            t.disagree_verdict,
            t.disagree_err,
            t.disagree_counters,
            t.cap_variant_counters,
            t.masked_unpaired,
            t.panics,
            t0.elapsed().as_secs()
        );
        i32::from(t.false_pass_main_property > 0 || t.disagree_verdict > 0 || t.disagree_err > 0 || t.disagree_counters > 0 || t.panics > 0)
    }

    // ------------------------------------------------------------ sweep over a real store
    fn load_rows(path: &str) -> (Vec<R>, String) {
        let b = std::fs::read(path).unwrap_or_default();
        let eol = b.iter().position(|&x| x == b'\n').unwrap_or(0);
        let line = String::from_utf8_lossy(&b[..eol]).to_string();
        let n: usize = fld(&line, "n=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let mut p = 4096usize;
        let mut rows = Vec::with_capacity(n);
        for _ in 0..n {
            let w = u32::from_le_bytes([b[p], b[p + 1], b[p + 2], b[p + 3]]);
            let mag = u16::from_le_bytes([b[p + 4], b[p + 5]]);
            let cnt = usize::from(u16::from_le_bytes([b[p + 6], b[p + 7]]));
            p += 8;
            let mut ent = Vec::with_capacity(cnt);
            for _ in 0..cnt {
                ent.push((u32::from_le_bytes([b[p], b[p + 1], b[p + 2], b[p + 3]]), i32::from_le_bytes([b[p + 4], b[p + 5], b[p + 6], b[p + 7]])));
                p += 8;
            }
            rows.push(R { w, mag, ent });
        }
        (rows, line)
    }

    fn write_rows(rows: &[R], lattice: &str, nl: u32, sha: &Sha256, tmp: &str) -> Result<(), String> {
        let payload = serialize(rows);
        let f = fields_for(rows, &payload, sha, lattice, Some(nl));
        std::fs::write(tmp, file_bytes(&header_line(&f), &payload)).map_err(|e| e.to_string())
    }

    fn outcome(tmp: &str, cap: usize) -> Result<super::Outcome, String> {
        let mut dev = super::segio::open(tmp, false).map_err(|e| e.to_string())?;
        let hdr = super::roomio::read_hdr(&mut dev, 0)?;
        super::run(&mut dev, 0, &hdr, cap, |_, _| {})
    }

    pub fn sweep(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let n = base.len();
        let pairs: u64 = base.iter().enumerate().map(|(h, r)| r.ent.iter().filter(|e| e.0 as usize > h).count() as u64).sum();
        let caps = [0usize, 1, 3, 13, 100, pairs as usize, 470_000_000];
        let t0 = std::time::Instant::now();
        // Clean rows with the padding gone: every cap passes.
        let _ = write_rows(&base, &lattice, nl, &sha, tmp);
        let mut bad = 0u64;
        for cap in caps {
            match outcome(tmp, cap) {
                Ok(o) if o.pairs_clean(n) && o.census.structure_clean() && o.census.upper == pairs => {}
                _ => {
                    bad += 1;
                    eprintln!("SWEEP_BAD|case=clean|cap={cap}|json=0");
                }
            }
        }
        let mut runs = 0u64;
        let (mut value_ok, mut delete_ok, mut move_ok, mut weight_ok) = (0u64, 0u64, 0u64, 0u64);
        let off_entries = 2 * pairs;
        // One fault at a time, on every off-diagonal entry, at every cap.
        for h in 0..n {
            for k in 0..base[h].ent.len() {
                let (j, z) = base[h].ent[k];
                if j as usize == h {
                    continue;
                }
                let (lo, hi) = (h.min(j as usize), h.max(j as usize));
                for cap in caps {
                    // Changed value, row sum kept: one mismatch, named exactly.
                    let mut r = base.clone();
                    r[h].ent[k].1 = z - 1;
                    if let Some(d) = r[h].ent.iter_mut().find(|e| e.0 == h as u32) {
                        d.1 += 1;
                    }
                    let _ = write_rows(&r, &lattice, nl, &sha, tmp);
                    runs += 1;
                    let ok = outcome(tmp, cap).is_ok_and(|o| {
                        o.total(|p| p.value_mismatch) == 1
                            && o.total(|p| p.lower_without_upper) == 0
                            && o.total(|p| p.upper_without_lower) == 0
                            && o.census.structure_clean()
                            && !o.pairs_clean(n)
                            && o.detail.len() == 1
                            && o.detail[0].contains(&format!("|i={lo}|h={hi}|"))
                    });
                    value_ok += u64::from(ok);
                    if !ok {
                        bad += 1;
                        eprintln!("SWEEP_BAD|case=value|h={h}|j={j}|cap={cap}|json=0");
                    }
                    // Deleted entry, row sum kept: exactly one unpaired entry, on the right side.
                    let mut r = base.clone();
                    r[h].ent.remove(k);
                    if let Some(d) = r[h].ent.iter_mut().find(|e| e.0 == h as u32) {
                        d.1 += z;
                    }
                    let _ = write_rows(&r, &lattice, nl, &sha, tmp);
                    runs += 1;
                    let up = (j as usize) > h;
                    let ok = outcome(tmp, cap).is_ok_and(|o| {
                        let (lw, uw) = (o.total(|p| p.lower_without_upper), o.total(|p| p.upper_without_lower));
                        o.total(|p| p.value_mismatch) == 0 && o.census.row_sum_nonzero == 0 && !o.pairs_clean(n) && if up { lw == 1 && uw == 0 } else { lw == 0 && uw == 1 }
                    });
                    delete_ok += u64::from(ok);
                    if !ok {
                        bad += 1;
                        eprintln!("SWEEP_BAD|case=delete|h={h}|j={j}|cap={cap}|json=0");
                    }
                }
            }
        }
        // Moved column, at the first free column above it, row sum kept: two unpaired, or one more when the new column has a partner to find.
        for h in 0..n {
            for k in 0..base[h].ent.len() {
                let (j, z) = base[h].ent[k];
                if j as usize == h {
                    continue;
                }
                let cols: Vec<u32> = base[h].ent.iter().map(|e| e.0).collect();
                let Some(fresh) = (j + 1..n as u32).find(|c| !cols.contains(c)) else {
                    continue;
                };
                // Keep it ascending: only moves that stay between its neighbours.
                if base[h].ent.get(k + 1).is_some_and(|e| e.0 <= fresh) {
                    continue;
                }
                for cap in [1usize, 13, pairs as usize, 470_000_000] {
                    let mut r = base.clone();
                    r[h].ent[k] = (fresh, z);
                    let _ = write_rows(&r, &lattice, nl, &sha, tmp);
                    runs += 1;
                    let partner_exists = base[fresh as usize].ent.iter().any(|e| e.0 == h as u32);
                    let ok = outcome(tmp, cap).is_ok_and(|o| {
                        let un = o.total(|p| p.lower_without_upper) + o.total(|p| p.upper_without_lower);
                        !o.pairs_clean(n) && un == 2 && !partner_exists
                    });
                    move_ok += u64::from(ok);
                    if !ok {
                        bad += 1;
                        eprintln!("SWEEP_BAD|case=move|h={h}|j={j}|fresh={fresh}|cap={cap}|json=0");
                    }
                }
            }
        }
        // Changed weight: every pair of the row breaks.
        for h in 0..n {
            for cap in caps {
                let mut r = base.clone();
                r[h].w += 1;
                let _ = write_rows(&r, &lattice, nl, &sha, tmp);
                runs += 1;
                let deg = base[h].ent.iter().filter(|e| e.0 as usize != h).count() as u64;
                let ok = outcome(tmp, cap).is_ok_and(|o| o.total(|p| p.value_mismatch) == deg && !o.pairs_clean(n));
                weight_ok += u64::from(ok);
                if !ok {
                    bad += 1;
                    eprintln!("SWEEP_BAD|case=weight|h={h}|cap={cap}|json=0");
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        eprintln!(
            "SWEEP_DONE|store={store}|n={n}|pairs={pairs}|off_entries={off_entries}|caps={caps:?}|runs={runs}|value_ok={value_ok}|delete_ok={delete_ok}|move_ok={move_ok}|weight_ok={weight_ok}|bad={bad}|secs={}|json=0",
            t0.elapsed().as_secs()
        );
        i32::from(bad > 0)
    }

    // ------------------------------------------------------------ every bit, with the merkle repaired
    fn call(tmp: &str, cap: usize) -> Result<i32, ()> {
        let args: Vec<String> = vec!["allpairs".into(), tmp.to_string(), "0".into(), cap.to_string()];
        match catch_unwind(AssertUnwindSafe(|| super::real_main(&args))) {
            Ok(Ok(true)) => Ok(0),
            Ok(Ok(false)) => Ok(2),
            Ok(Err(_)) => Ok(1),
            Err(_) => Err(()),
        }
    }

    pub fn bitflip(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let payload = serialize(&base);
        let fields = fields_for(&base, &payload, &sha, &lattice, Some(nl));
        const NAMES: [&str; 7] = ["w", "mag", "cnt", "off_column", "off_value", "diag_column", "diag_value"];
        let mut kind = vec![0u8; payload.len()];
        let mut q = 0usize;
        for (h, r) in base.iter().enumerate() {
            for (b, k) in [(4usize, 0u8), (2, 1), (2, 2)] {
                for _ in 0..b {
                    kind[q] = k;
                    q += 1;
                }
            }
            for e in &r.ent {
                let (c, v) = if e.0 as usize == h { (5u8, 6u8) } else { (3, 4) };
                for t in 0..8 {
                    kind[q] = if t < 4 { c } else { v };
                    q += 1;
                }
            }
        }
        let caps = [470_000_000usize, 100, 13];
        let mut flips = [0u64; 7];
        let mut exits = [[0u64; 3]; 7];
        let mut panics = 0u64;
        let t0 = std::time::Instant::now();
        let mut turn = 0usize;
        for byte in 0..payload.len() {
            for bit in 0..8 {
                let mut p = payload.clone();
                p[byte] ^= 1 << bit;
                let mut f = fields.clone();
                set(&mut f, "payload_merkle", sha.merkle(&p));
                if std::fs::write(tmp, file_bytes(&header_line(&f), &p)).is_err() {
                    return 9;
                }
                let k = kind[byte] as usize;
                flips[k] += 1;
                turn += 1;
                match call(tmp, caps[turn % 3]) {
                    Ok(c) => exits[k][if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1,
                    Err(()) => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        for k in 0..7 {
            eprintln!("BITFLIP|field={}|flips={}|exit0={}|exit1={}|exit2={}|json=0", NAMES[k], flips[k], exits[k][0], exits[k][1], exits[k][2]);
        }
        eprintln!("BITFLIP_DONE|store={store}|payload_bytes={}|flips={}|panics={panics}|secs={}|json=0", payload.len(), payload.len() * 8, t0.elapsed().as_secs());
        i32::from(panics > 0)
    }

    pub fn headerflip(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let payload = serialize(&base);
        let fields = fields_for(&base, &payload, &sha, &lattice, Some(nl));
        let hl = header_line(&fields);
        // Which field each byte of the line belongs to. A separator belongs to the field before it.
        let mut names: Vec<String> = Vec::new();
        let mut cur = String::new();
        for part in hl.split('|') {
            let name = part.split('=').next().unwrap_or("").to_string();
            for _ in 0..part.len() + 1 {
                names.push(name.clone());
            }
            cur = name;
        }
        names.truncate(hl.len() + 1);
        names[hl.len()] = "newline".to_string();
        let _ = cur;
        let clean = file_bytes(&hl, &payload);
        let mut tally: Vec<(String, [u64; 4])> = Vec::new();
        let mut panics = 0u64;
        // Every bit of the line and its newline, then every bit of 64 bytes of the zeros after it.
        for byte in 0..hl.len() + 1 + 64 {
            let name = if byte <= hl.len() { names[byte].clone() } else { "zeros_after_newline".to_string() };
            if !tally.iter().any(|t| t.0 == name) {
                tally.push((name.clone(), [0; 4]));
            }
            for bit in 0..8 {
                let mut b = clean.clone();
                b[byte] ^= 1 << bit;
                if std::fs::write(tmp, &b).is_err() {
                    return 9;
                }
                let e = tally.iter_mut().find(|t| t.0 == name).map(|t| &mut t.1);
                match (call(tmp, 470_000_000), e) {
                    (Ok(c), Some(e)) => {
                        e[0] += 1;
                        e[1 + if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1;
                    }
                    _ => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        for (name, e) in &tally {
            eprintln!("HEADERFLIP|field={name}|flips={}|exit0={}|exit1={}|exit2={}|json=0", e[0], e[1], e[2], e[3]);
        }
        eprintln!("HEADERFLIP_DONE|store={store}|line_bytes={}|panics={panics}|json=0", hl.len());
        i32::from(panics > 0)
    }

    pub fn main(a: &[String]) -> i32 {
        match a.get(1).map(String::as_str) {
            Some("bitflip") => bitflip(a.get(2).map_or("", String::as_str), a.get(3).map_or("flip.tmp", String::as_str)),
            Some("headerflip") => headerflip(a.get(2).map_or("", String::as_str), a.get(3).map_or("flip.tmp", String::as_str)),
            Some("fuzz") => {
                let seed = a.get(2).and_then(|v| v.parse().ok()).unwrap_or(1);
                let iters = a.get(3).and_then(|v| v.parse().ok()).unwrap_or(1000);
                let tmp = a.get(4).cloned().unwrap_or_else(|| "fuzz.tmp".to_string());
                fuzz(seed, iters, &tmp)
            }
            Some("sweep") => {
                let store = a.get(2).cloned().unwrap_or_default();
                let tmp = a.get(3).cloned().unwrap_or_else(|| "sweep.tmp".to_string());
                sweep(&store, &tmp)
            }
            _ => {
                eprintln!("usage: fuzz fuzz SEED ITERS TMP | sweep STORE TMP | bitflip STORE TMP | headerflip STORE TMP");
                9
            }
        }
    }

    #[cfg(test)]
    mod t {
        use super::*;
        #[test]
        fn sha_known_answer() {
            let s = Sha256::new();
            assert_eq!(s.hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
        }
    }
}
