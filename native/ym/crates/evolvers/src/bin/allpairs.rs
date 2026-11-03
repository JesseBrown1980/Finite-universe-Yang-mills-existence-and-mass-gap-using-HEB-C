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
#[path = "../../../torusl/src/segio.rs"]
mod segio;

#[allow(dead_code)]
#[path = "../../../torusl/src/sha.rs"]
mod sha;

#[allow(dead_code)]
#[path = "../../../torusl/src/roomio.rs"]
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

fn main() {
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
