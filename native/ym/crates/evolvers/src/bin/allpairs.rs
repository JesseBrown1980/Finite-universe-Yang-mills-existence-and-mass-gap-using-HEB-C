//! Exact test of W H = (W H)^T on a stored room stream, pair by pair, with no random vector.
//!
//! Every off-diagonal entry z_hj needs its own partner z_jh in the row of j, with w_h z_hj = w_j z_jh in exact integers.
//! An entry with no partner fails, and a lower entry that finds every partner already taken fails. Rows come through
//! `roomscan::scan`, so every pass recomputes the payload merkle and accounts for every payload byte.
//!
//! A pass keeps the upper entries (j > h) of one window of rows, then walks every row and answers each lower entry (j < h)
//! whose partner row lies in that window. The next pass starts where this window ended. A window holds at most CAP_ENTRIES
//! upper entries, unless its first row alone holds more, and at most max(CAP_ENTRIES, 2^20) rows. So memory is 8 bytes per
//! upper entry, 1 bit per upper entry and 8 bytes per row of the window, plus read buffers of a few 64 MiB chunks.
//!
//!   allpairs DEV OFFSET [CAP_ENTRIES]
//!
//! DEV is a segio spec, a regular file or a run of sectors. The output names the store by its payload merkle and the
//! SHA-256 of its 4096-byte header block, and names itself by the SHA-256 of its own file. store_identity reads PASS only when that block is one of the blocks in `TRUSTED`.
//! Bytes of the file past the stream stay unread, and their count is printed as bytes_after_stream.
//!
//! Exit 0 only when the pairs and the structure are clean and all five gates read PASS: header_entries, whole_space_count,
//! header_rooms, padding and store_identity. Exit 2 when any of them does not. Exit 1 when the stream cannot be read or
//! holds no rows, when its merkle differs, when the header repeats a key, writes n= or payload_bytes= outside canonical
//! form, or gives sizes that do not fit the layout. Integer only, json=0.

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

#[allow(dead_code)]
#[path = "../../../torusl/src/roomscan.rs"]
mod roomscan;

/// 3.5 GiB of upper entries in one window.
const DEFAULT_CAP: usize = 470_000_000;
/// A window index stays a u32, with room for one more row past the cap.
const MAX_CAP: usize = 4_000_000_000;
/// A window holds at most max(cap, this) rows.
const MIN_ROW_CAP: usize = 1_048_576;
const MAX_DETAIL: usize = 16;
/// The flat weights printed. All of them are counted and summed.
const MAX_FLAT_LIST: usize = 64;
const HEADER_BLOCK: u64 = 4096;
const MIB: u64 = 1_048_576;

/// A store this tool can certify: its exact header line, and the SHA-256 of its whole 4096-byte header block. That block
/// holds the payload merkle, and every pass checks the merkle against the rows, so these two values bind every field of
/// the header and every payload byte to the row of this table.
struct Trusted<'a> {
    line: &'a str,
    header_sha256: &'a str,
}

const TRUSTED: [Trusted<'static>; 4] = [
    Trusted {
        line: "YMROOMHDR|L=2x2|sector=Sx+Sy+|n=211|nl=8|rooms=2818|entries=2607|payload_bytes=1044480|stream_bytes=1048576|chunk=16MiB|payload_merkle=b7c5847b6cb3a92b41877d14164ec97ad5c67091d7a03492460632a4b416d883|keys_sha256=9a2591690b4ed2575668a1d70477baae767e184bd81df7e9f62068485e01d96f|w_self_adjoint=PASS|json=0",
        header_sha256: "00fcacf55296e9269fe413e8ad36a526b143981e239993c2baeb0ae43c78ab5a",
    },
    Trusted {
        line: "YMROOMHDR|L=2x3|sector=Sx+Sy+|n=2646|nl=12|rooms=77602|entries=74956|payload_bytes=1044480|stream_bytes=1048576|chunk=16MiB|payload_merkle=40433ac6c49b0e5e450044ed476599b1cf2757ad613020075e4505dc8175aa97|keys_sha256=ea8b8808a0f5400b12b125de84eadea6f9766b0796148656476a7ba54ba6fc2e|w_self_adjoint=PASS|json=0",
        header_sha256: "99a1cdb82387f5395d0a1ab5031313600f8b25c4fde874f75bfc15389e913c0d",
    },
    Trusted {
        line: "YMROOMHDR|L=3x3|sector=Sx+Sy+|n=288645|nl=18|rooms=15697314|entries=15408669|payload_bytes=125825024|stream_bytes=125829120|chunk=16MiB|payload_merkle=c0059b361fecc6e729e31b6078a6badda4be7fa40ea4f924b6af5fbf3b77ab83|keys_sha256=edd911b0d1dc2c280a83ae0efc67119057fe897c98bd8da336ce4ba936a80cbb|w_self_adjoint=PASS|json=0",
        header_sha256: "035d84766c9f62ba0fbfb23d4c85795cf42ab19502042ed50b83cb4076ebe373",
    },
    Trusted {
        line: "YMROOMHDR|L=3x4|sector=Sx+Sy+|n=45508080|nl=24|rooms=3356267422|entries=3310759342|payload_bytes=26850881536|stream_bytes=26850885632|chunk=16MiB|payload_merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|keys_sha256=bf5a1a43f99f4acd5f73f7da55e628e5bedbd5b4b29ef1b21c87b789d0d13b79|w_self_adjoint=PASS|json=0",
        header_sha256: "65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21",
    },
];

/// A gate compares what the header or the table says with what the rows gave. OPEN means there was nothing to compare with.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Gate {
    Pass,
    Fail,
    Open,
}

impl Gate {
    fn compare<T: PartialEq>(expected: Option<T>, counted: T) -> Gate {
        match expected {
            Some(v) if v == counted => Gate::Pass,
            Some(_) => Gate::Fail,
            None => Gate::Open,
        }
    }
}

impl std::fmt::Display for Gate {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            Gate::Pass => "PASS",
            Gate::Fail => "FAIL",
            Gate::Open => "OPEN",
        })
    }
}

/// The verdict passes only when the pairs and the structure are clean and every gate reads PASS.
fn verdict(pairs_clean: bool, structure_clean: bool, gates: &[Gate]) -> bool {
    pairs_clean && structure_clean && gates.iter().all(|&g| g == Gate::Pass)
}

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
    flats: u64,
    flat_w_sum: u128,
    flat_w: Vec<u32>,
}

impl Census {
    fn row(&mut self, h: usize, row: &roomscan::Row, n: usize) {
        self.rows += 1;
        self.zero_weight += u64::from(row.w == 0);
        self.sum_w += u128::from(row.w);
        if row.mag == 0 {
            self.flats += 1;
            self.flat_w_sum += u128::from(row.w);
            if self.flat_w.len() < MAX_FLAT_LIST {
                self.flat_w.push(row.w);
            }
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

/// How much one window may hold, and how much to set aside for its entries at the start.
#[derive(Clone, Copy)]
struct Limits {
    cap: usize,
    row_cap: usize,
    reserve: usize,
}

/// The upper entries of the rows start..end, sorted by column inside each row, with one bit per entry for "answered".
struct Window {
    start: usize,
    end: usize,
    closed: bool,
    limits: Limits,
    off: Vec<u32>,
    w: Vec<u32>,
    ent: Vec<(u32, i32)>,
    answered: Vec<u64>,
}

impl Window {
    fn new(start: usize, limits: Limits) -> Window {
        Window { start, end: start, closed: false, limits, off: vec![0], w: Vec::new(), ent: Vec::with_capacity(limits.reserve), answered: Vec::with_capacity(limits.reserve.div_ceil(64)) }
    }

    fn holds(&self, i: usize) -> bool {
        (self.start..self.end).contains(&i)
    }

    /// The weight of row i, and where its upper entries lie in `ent`.
    fn span(&self, i: usize) -> (u32, usize, usize) {
        let r = i - self.start;
        (self.w[r], self.off[r] as usize, self.off[r + 1] as usize)
    }

    fn is_answered(&self, at: usize) -> bool {
        (self.answered[at / 64] >> (at % 64)) & 1 == 1
    }

    fn mark_answered(&mut self, at: usize) {
        self.answered[at / 64] |= 1u64 << (at % 64);
    }

    /// The first row of a window always enters, so every pass advances.
    fn admit(&mut self, h: usize, row: &roomscan::Row) {
        if self.closed || h < self.start {
            return;
        }
        let count = row.entries().filter(|&(j, _)| j > h).count();
        let full = self.ent.len() + count > self.limits.cap || self.w.len() >= self.limits.row_cap;
        if full && h > self.start {
            self.closed = true;
            return;
        }
        let from = self.ent.len();
        // Each column was read from a u32, so the cast keeps it exactly.
        self.ent.extend(row.entries().filter(|&(j, _)| j > h).map(|(j, z)| (j as u32, z)));
        // Columns ascend in a clean row. Sorting the rest keeps every count below exact, at every cap.
        let part = &mut self.ent[from..];
        if !part.windows(2).all(|p| p[0].0 <= p[1].0) {
            part.sort_by_key(|e| e.0);
        }
        self.answered.resize(self.ent.len().div_ceil(64), 0);
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
    answered: u64,
    value_mismatch: u64,
    lower_without_upper: u64,
    upper_without_lower: u64,
    lower_repeated: u64,
    secs: u64,
}

fn note(detail: &mut Vec<String>, text: String) {
    if detail.len() < MAX_DETAIL {
        detail.push(text);
    }
}

/// Answers every lower entry of row h whose partner row is in the window. Each stored entry takes one lower entry.
fn answer(win: &mut Window, h: usize, row: &roomscan::Row, out: &mut PassOut, detail: &mut Vec<String>) {
    for (i, z_hi) in row.entries() {
        if i >= h || !win.holds(i) {
            continue;
        }
        let (w_i, lo, hi) = win.span(i);
        out.lookups += 1;
        // h is below n, itself checked against the u32 range by the caller.
        let col = h as u32;
        let first = lo + win.ent[lo..hi].partition_point(|e| e.0 < col);
        let same = win.ent[first..hi].iter().take_while(|e| e.0 == col).count();
        if same == 0 {
            out.lower_without_upper += 1;
            note(detail, format!("ALLPAIRS_BAD|kind=lower_without_upper|row={h}|col={i}|z={z_hi}|json=0"));
            continue;
        }
        out.found += 1;
        let Some(at) = (first..first + same).find(|&at| !win.is_answered(at)) else {
            out.lower_repeated += 1;
            note(detail, format!("ALLPAIRS_BAD|kind=lower_repeated|row={h}|col={i}|z={z_hi}|json=0"));
            continue;
        };
        win.mark_answered(at);
        out.answered += 1;
        let z_ih = win.ent[at].1;
        // |w| < 2^32 and |z| <= 2^31, so each product fits in i64.
        if i64::from(w_i) * i64::from(z_ih) != i64::from(row.w) * i64::from(z_hi) {
            out.value_mismatch += 1;
            note(detail, format!("ALLPAIRS_BAD|kind=value_mismatch|i={i}|h={h}|w_i={w_i}|z_ih={z_ih}|w_h={}|z_hi={z_hi}|json=0", row.w));
        }
    }
}

/// One walk over every row, with the window starting at row `start`. The census runs on the first walk.
fn one_pass(dev: &mut segio::Dev, at: &roomscan::Layout, start: usize, limits: Limits, mut census: Option<&mut Census>, detail: &mut Vec<String>) -> Result<(PassOut, roomscan::End), String> {
    let t0 = std::time::Instant::now();
    let mut win = Window::new(start, limits);
    let mut out = PassOut { start, ..PassOut::default() };
    let n = at.n;
    let end = roomscan::scan(dev, at, |h, row| {
        if let Some(c) = census.as_deref_mut() {
            c.row(h, row, n);
        }
        if h >= start {
            answer(&mut win, h, row, &mut out, detail);
            win.admit(h, row);
        }
    })?;
    out.end = win.end;
    out.stored = win.ent.len() as u64;
    out.upper_without_lower = out.stored - out.answered;
    if out.upper_without_lower > 0 {
        for r in 0..win.w.len() {
            for e in win.off[r] as usize..win.off[r + 1] as usize {
                if !win.is_answered(e) {
                    note(detail, format!("ALLPAIRS_BAD|kind=upper_without_lower|row={}|col={}|z={}|json=0", start + r, win.ent[e].0, win.ent[e].1));
                }
            }
            if detail.len() >= MAX_DETAIL {
                break;
            }
        }
    }
    out.secs = t0.elapsed().as_secs();
    Ok((out, end))
}

struct Outcome {
    census: Census,
    passes: Vec<PassOut>,
    detail: Vec<String>,
    end: roomscan::End,
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
            && self.total(|p| p.answered) == c.upper
            && self.total(|p| p.value_mismatch) == 0
            && self.total(|p| p.lower_without_upper) == 0
            && self.total(|p| p.upper_without_lower) == 0
            && self.total(|p| p.lower_repeated) == 0
    }
}

fn effective_cap(requested: usize) -> usize {
    requested.clamp(1, MAX_CAP)
}

fn run(dev: &mut segio::Dev, off: u64, hdr: &roomio::Hdr, requested_cap: usize, mut each: impl FnMut(usize, &PassOut)) -> Result<Outcome, String> {
    if u32::try_from(hdr.n).is_err() {
        return Err("n does not fit in u32".into());
    }
    if hdr.n == 0 {
        return Err("n is 0, so there are no rows to read and no merkle to compute".into());
    }
    let cap = effective_cap(requested_cap);
    let row_cap = cap.max(MIN_ROW_CAP);
    let at = roomscan::Layout { off, n: hdr.n, payload: hdr.payload, merkle: &hdr.merkle };
    let mut census = Census::default();
    let mut passes: Vec<PassOut> = Vec::new();
    let mut detail = Vec::new();
    let room_bound = usize::try_from(hdr.payload / 8).map_err(|_| "payload")?;
    let mut start = 0;
    let mut last = None;
    while start < hdr.n {
        let reserve = if passes.is_empty() {
            cap.min(room_bound)
        } else {
            let kept: u64 = passes.iter().map(|p| p.stored).sum();
            cap.min(usize::try_from(census.upper.saturating_sub(kept)).map_err(|_| "upper")?)
        };
        let first = passes.is_empty();
        let (p, end) = one_pass(dev, &at, start, Limits { cap, row_cap, reserve }, first.then_some(&mut census), &mut detail)?;
        if p.end <= start {
            return Err(format!("no progress at row {start}"));
        }
        start = p.end;
        each(passes.len(), &p);
        passes.push(p);
        last = Some(end);
    }
    let end = last.ok_or("no pass ran")?;
    Ok(Outcome { census, passes, detail, end })
}

/// The whole header block, and its line, for what `roomio::Hdr` leaves out.
fn raw_header(dev: &mut segio::Dev, off: u64) -> Result<(Vec<u8>, String), String> {
    let mut blk = vec![0u8; HEADER_BLOCK as usize];
    dev.seek(SeekFrom::Start(off)).map_err(|e| format!("seek: {e}"))?;
    dev.read_exact(&mut blk).map_err(|e| format!("read header: {e}"))?;
    let end = blk.iter().position(|&b| b == b'\n').ok_or("no header line")?;
    let line = String::from_utf8_lossy(&blk[..end]).to_string();
    Ok((blk, line))
}

fn field<'a>(line: &'a str, key: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(key))
}

/// A key that appears twice gives two answers, and `field` and `roomio` read only the first.
fn repeated_key(line: &str) -> Option<&str> {
    let mut keys: Vec<&str> = line.split('|').filter_map(|kv| kv.split_once('=').map(|(k, _)| k)).collect();
    keys.sort_unstable();
    keys.windows(2).find(|p| p[0] == p[1]).map(|p| p[0])
}

/// A number in its one canonical decimal form, with no sign and no leading zero.
fn number<T: std::str::FromStr + ToString>(v: &str) -> Option<T> {
    let n = v.parse::<T>().ok()?;
    (n.to_string() == v).then_some(n)
}

/// `roomio` reads n= and payload_bytes= leniently and reads a repeated key once, so this tool refuses both forms itself.
fn check_header(line: &str, hdr: &roomio::Hdr) -> Result<(), String> {
    if hdr.n == 0 {
        return Err("n is 0, so there are no rows to read and no merkle to compute".into());
    }
    if let Some(k) = repeated_key(line) {
        return Err(format!("header repeats {k}="));
    }
    if field(line, "n=").and_then(number::<usize>) != Some(hdr.n) || field(line, "payload_bytes=").and_then(number::<u64>) != Some(hdr.payload) {
        return Err("header writes n= or payload_bytes= outside canonical form".into());
    }
    Ok(())
}

/// The layout `ymroom build` writes: a 4096-byte header block, the rows, then zero padding to a multiple of 1 MiB. Every size
/// is checked here, before any memory is set aside from it. Returns rooms=.
fn check_sizes(line: &str, hdr: &roomio::Hdr, off: u64, store_len: u64) -> Result<u64, String> {
    let rooms = field(line, "rooms=").and_then(number::<u64>).ok_or("header has no canonical rooms=")?;
    let stream = field(line, "stream_bytes=").and_then(number::<u64>).ok_or("header has no canonical stream_bytes=")?;
    if hdr.payload.checked_add(HEADER_BLOCK) != Some(stream) {
        return Err("header stream_bytes= is not payload_bytes= + 4096".into());
    }
    if stream % MIB != 0 {
        return Err("header stream_bytes= is not a multiple of 1 MiB".into());
    }
    let used = rooms.checked_mul(8).filter(|&u| u <= hdr.payload).ok_or("header rooms= does not fit in payload_bytes=")?;
    if hdr.payload - used >= MIB {
        return Err("header payload_bytes= leaves 1 MiB or more of padding".into());
    }
    if hdr.n as u64 > rooms {
        return Err("header n= exceeds rooms=".into());
    }
    if off.checked_add(stream).map_or(true, |end| end > store_len) {
        return Err("store is shorter than its stream_bytes=".into());
    }
    Ok(rooms)
}

/// Bytes the store holds: the sectors of a segio run, or the length of a regular file.
fn store_bytes(spec: &str, dev: &segio::Dev) -> Result<u64, String> {
    match dev.capacity() {
        Some(v) => Ok(v),
        None => std::fs::metadata(spec).map(|m| m.len()).map_err(|e| format!("store length: {e}")),
    }
}

fn key_of(kv: &str) -> &str {
    kv.split_once('=').map_or(kv, |(k, _)| k)
}

/// The keys whose fields differ between two header lines, or header_block when the lines agree and the block does not.
fn differing_fields(want: &str, got: &str) -> String {
    let mut keys: Vec<&str> = want.split('|').chain(got.split('|')).map(key_of).collect();
    keys.sort_unstable();
    keys.dedup();
    let token = |line: &'_ str, k: &str| line.split('|').find(|kv| key_of(kv) == k).map(str::to_string);
    let differs: Vec<&str> = keys.into_iter().filter(|k| token(want, k) != token(got, k)).collect();
    if differs.is_empty() {
        "header_block".to_string()
    } else {
        differs.join(",")
    }
}

/// PASS when the header block is a block of the table. FAIL when the table holds this lattice under another block, naming
/// what differs. OPEN when the table holds no such lattice.
fn identity_gate(table: &[Trusted], header_sha256: &str, line: &str) -> (Gate, String) {
    if table.iter().any(|t| t.header_sha256 == header_sha256 && t.line == line) {
        return (Gate::Pass, "-".to_string());
    }
    let lattice = field(line, "L=");
    match table.iter().find(|t| field(t.line, "L=") == lattice) {
        Some(t) => (Gate::Fail, differing_fields(t.line, line)),
        None => (Gate::Open, "-".to_string()),
    }
}

/// Every payload byte is accounted for: the rows fill rooms= exactly, and all that follows them is zero and under 1 MiB.
fn padding_gate(end: &roomscan::End, rooms: u64, payload: u64) -> Gate {
    let rows_fill_rooms = rooms.checked_mul(8) == Some(end.row_bytes);
    let every_byte = end.row_bytes.checked_add(end.padding_bytes) == Some(payload);
    if rows_fill_rooms && every_byte && end.padding_nonzero == 0 && end.padding_bytes < MIB {
        Gate::Pass
    } else {
        Gate::Fail
    }
}

/// Gauge-fixed codes of an AxB periodic lattice: 6^(links - V + 1) = 6^(V + 1), since links = 2V.
fn codes(lattice: &str, nl: Option<&str>) -> Option<u128> {
    let (a, b) = lattice.split_once('x')?;
    let v = number::<u32>(a)?.checked_mul(number::<u32>(b)?)?;
    if v == 0 || number::<u32>(nl?)? != v.checked_mul(2)? {
        return None;
    }
    6u128.checked_pow(v.checked_add(1)?)
}

/// What the whole tool found. `main` reads the verdict, and the tests read the rest.
#[cfg_attr(not(test), allow(dead_code))]
struct Report {
    pass: bool,
    requested: usize,
    effective: usize,
    entries: Gate,
    count: Gate,
    rooms: Gate,
    padding: Gate,
    identity: Gate,
    differs: String,
    outcome: Outcome,
}

fn run_tool(a: &[String], table: &[Trusted], exe_sha256: &str) -> Result<Report, String> {
    let t0 = std::time::Instant::now();
    let spec = a.get(1).ok_or("usage: allpairs DEV OFFSET [CAP_ENTRIES]")?;
    let off: u64 = a.get(2).ok_or("missing OFFSET")?.parse().map_err(|_| "bad OFFSET")?;
    let requested: usize = match a.get(3) {
        Some(v) => v.parse().map_err(|_| "bad CAP_ENTRIES")?,
        None => DEFAULT_CAP,
    };
    let cap = effective_cap(requested);
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    let (block, line) = raw_header(&mut dev, off)?;
    check_header(&line, &hdr)?;
    let store_len = store_bytes(spec, &dev)?;
    let rooms = check_sizes(&line, &hdr, off, store_len)?;
    // check_sizes holds off + payload + 4096 within the store.
    let after_stream = store_len - off - hdr.payload - HEADER_BLOCK;
    let header_sha256 = sha::sha256_hex(&block);
    let (identity, differs) = identity_gate(table, &header_sha256, &line);
    let o = run(&mut dev, off, &hdr, requested, |k, p| {
        println!(
            "ALLPAIRS_PASS|pass={k}|rows_from={}|rows_to={}|upper_stored={}|lookups={}|found={}|value_mismatch={}|lower_without_upper={}|upper_without_lower={}|lower_repeated={}|merkle=PASS|secs={}|json=0",
            p.start, p.end, p.stored, p.lookups, p.found, p.value_mismatch, p.lower_without_upper, p.upper_without_lower, p.lower_repeated, p.secs
        );
    })?;
    let c = &o.census;
    for d in &o.detail {
        println!("{d}");
    }
    let entries_gate = Gate::compare(field(&line, "entries=").and_then(number::<u64>), c.entries);
    let expected = codes(&hdr.lattice, field(&line, "nl="));
    let count_gate = Gate::compare(expected, c.sum_w);
    let rooms_gate = Gate::compare(Some(rooms), c.rows + c.entries);
    let padding = padding_gate(&o.end, rooms, hdr.payload);
    let pass = verdict(o.pairs_clean(hdr.n), c.structure_clean(), &[entries_gate, count_gate, rooms_gate, padding, identity]);
    let flat_list: Vec<String> = c.flat_w.iter().map(u32::to_string).collect();
    println!(
        "ALLPAIRS|L={}|sector={}|n={}|rows_read={}|entries={}|header_entries={entries_gate}|diag={}|pairs={}|passes={}|cap_requested={requested}|cap_entries={cap}|value_mismatch={}|lower_without_upper={}|upper_without_lower={}|lower_repeated={}|columns_not_ascending={}|column_out_of_range={}|zero_z={}|positive_offdiag={}|row_sum_nonzero={}|zero_weight={}|missing_diag={}|flats={}|flat_w={}|flat_w_listed={}|flat_w_sum={}|sum_w={}|codes={}|whole_space_count={count_gate}|rooms={rooms}|header_rooms={rooms_gate}|padding_bytes={}|padding_nonzero={}|padding={padding}|bytes_after_stream={after_stream}|store_identity={identity}|identity_differs={differs}|payload_merkle={}|header_sha256={header_sha256}|merkle=PASS|verdict={}|exe_sha256={exe_sha256}|secs={}|json=0",
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
        o.total(|p| p.lower_repeated),
        c.not_ascending,
        c.out_of_range,
        c.zero_z,
        c.positive_off,
        c.row_sum_nonzero,
        c.zero_weight,
        c.missing_diag,
        c.flats,
        flat_list.join(","),
        c.flat_w.len(),
        c.flat_w_sum,
        c.sum_w,
        expected.map_or("-".to_string(), |v| v.to_string()),
        o.end.padding_bytes,
        o.end.padding_nonzero,
        o.end.merkle,
        if pass { "PASS" } else { "FAIL" },
        t0.elapsed().as_secs()
    );
    Ok(Report { pass, requested, effective: cap, entries: entries_gate, count: count_gate, rooms: rooms_gate, padding, identity, differs, outcome: o })
}

/// The SHA-256 of the running executable, so the output names what printed it. A reader can compare this with a build of its own.
fn own_hash() -> String {
    std::env::current_exe().and_then(std::fs::read).map_or("-".to_string(), |b| sha::sha256_hex(&b))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    match run_tool(&a, &TRUSTED, &own_hash()) {
        Ok(r) if r.pass => {}
        Ok(_) => std::process::exit(2),
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
            assert!(o.detail.iter().any(|d| d.contains("kind=upper_without_lower|row=1|col=39|")), "{:?}", o.detail);
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

    #[test]
    fn the_count_of_codes_reads_only_a_well_formed_lattice_and_link_count() {
        assert_eq!(codes("7x6", Some("84")), Some(6u128.pow(43)));
        for (l, nl) in [
            ("", "8"),
            ("4", "8"),
            ("2x", "8"),
            ("x2", "8"),
            ("axb", "8"),
            ("2x2x2", "16"),
            ("+2x2", "8"),
            ("02x2", "8"),
            ("2x2", ""),
            ("2x2", "abc"),
            ("2x2", "-8"),
            ("2x2", "+8"),
            ("2x2", "08"),
            ("2x2", "7"),
            ("0x4", "0"),
            ("65536x65536", "8"),
            ("65536x32768", "0"),
            ("7x7", "98"),
        ] {
            assert_eq!(codes(l, Some(nl)), None, "L={l} nl={nl}");
        }
    }

    #[test]
    fn only_clean_rows_and_every_gate_at_pass_let_the_verdict_pass() {
        let gates = [Gate::Pass, Gate::Fail, Gate::Open];
        let mut combos = 0;
        let mut passing = Vec::new();
        for pairs in [true, false] {
            for structure in [true, false] {
                for a in gates {
                    for b in gates {
                        for c in gates {
                            for d in gates {
                                for e in gates {
                                    combos += 1;
                                    if verdict(pairs, structure, &[a, b, c, d, e]) {
                                        passing.push((pairs, structure, a, b, c, d, e));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        assert_eq!(combos, 972);
        assert_eq!(passing, vec![(true, true, Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass)]);
    }

    #[test]
    fn a_gate_reads_pass_only_on_an_equal_value_and_open_on_no_value() {
        assert_eq!(Gate::compare(Some(4u64), 4), Gate::Pass);
        assert_eq!(Gate::compare(Some(5u64), 4), Gate::Fail);
        assert_eq!(Gate::compare(None, 4u64), Gate::Open);
        assert_eq!((Gate::Pass.to_string(), Gate::Fail.to_string(), Gate::Open.to_string()), ("PASS".to_string(), "FAIL".to_string(), "OPEN".to_string()));
    }

    #[test]
    fn a_number_has_one_written_form() {
        assert_eq!(number::<u64>("2607"), Some(2607));
        assert_eq!(number::<u64>("0"), Some(0));
        for bad in ["", "+2607", "-2607", "02607", "00", "26 07", "2607 ", " 2607", "abc", "0x10", "18446744073709551616"] {
            assert_eq!(number::<u64>(bad), None, "{bad:?}");
        }
    }

    #[test]
    fn a_repeated_key_is_named() {
        assert_eq!(repeated_key("YMROOMHDR|L=2x2|n=1|nl=8|entries=9"), None);
        assert_eq!(repeated_key("YMROOMHDR|L=2x2|n=1|nl=8|n=2"), Some("n"));
        assert_eq!(repeated_key("YMROOMHDR|entries=1|entries=1"), Some("entries"));
    }

    // ---- Stores in the full layout, as `ymroom build` writes them.

    const TEST_KEYS: &str = "keysha";

    fn block_of(line: &str) -> Vec<u8> {
        let mut b = line.as_bytes().to_vec();
        b.push(b'\n');
        b.resize(HEADER_BLOCK as usize, 0);
        b
    }

    fn merkle_of(payload: &[u8]) -> String {
        let mut shas = String::new();
        for c in payload.chunks(16 * 1_048_576) {
            shas.push_str(&sha::sha256_hex(c));
        }
        sha::sha256_hex(shas.as_bytes())
    }

    fn payload_of(rows: &[roomio::TestRow], total: usize) -> Vec<u8> {
        let mut p = Vec::new();
        for (w, mag, ent) in rows {
            p.extend_from_slice(&w.to_le_bytes());
            p.extend_from_slice(&mag.to_le_bytes());
            p.extend_from_slice(&u16::try_from(ent.len()).unwrap().to_le_bytes());
            for (j, z) in ent {
                p.extend_from_slice(&j.to_le_bytes());
                p.extend_from_slice(&z.to_le_bytes());
            }
        }
        assert!(p.len() <= total);
        p.resize(total, 0);
        p
    }

    fn line_of(rows: &[roomio::TestRow], lattice: &str, nl: u64, payload: &[u8]) -> String {
        let entries: usize = rows.iter().map(|r| r.2.len()).sum();
        format!(
            "YMROOMHDR|L={lattice}|sector=Sx+Sy+|n={}|nl={nl}|rooms={}|entries={entries}|payload_bytes={}|stream_bytes={}|chunk=16MiB|payload_merkle={}|keys_sha256={TEST_KEYS}|w_self_adjoint=PASS|json=0",
            rows.len(),
            rows.len() + entries,
            payload.len(),
            payload.len() + 4096,
            merkle_of(payload)
        )
    }

    /// Two rows of weight 108, 6^3 codes in all on L=1x2: 6 rooms, 4 entries, 1 pair, padded to 1 MiB.
    fn two_rows() -> Vec<roomio::TestRow> {
        vec![(108, 3, vec![(0, 1), (1, -1)]), (108, 3, vec![(0, -1), (1, 1)])]
    }

    const ONE_STREAM: usize = 1_048_576 - 4096;

    fn clean() -> (Vec<u8>, String) {
        let r = two_rows();
        let p = payload_of(&r, ONE_STREAM);
        let line = line_of(&r, "1x2", 4, &p);
        (p, line)
    }

    fn tool_with(line: &str, block_edit: impl Fn(&mut Vec<u8>), payload: &[u8], trusted_lines: &[&str], cap: &str) -> Result<Report, String> {
        let mut block = block_of(line);
        block_edit(&mut block);
        let mut bytes = block;
        bytes.extend_from_slice(payload);
        let p = temp();
        std::fs::write(&p, bytes).unwrap();
        let hashes: Vec<String> = trusted_lines.iter().map(|l| sha::sha256_hex(&block_of(l))).collect();
        let table: Vec<Trusted> = trusted_lines.iter().zip(&hashes).map(|(l, h)| Trusted { line: l, header_sha256: h }).collect();
        let a = ["allpairs".to_string(), p.to_str().unwrap().to_string(), "0".to_string(), cap.to_string()];
        let r = run_tool(&a, &table, "-");
        std::fs::remove_file(p).unwrap();
        r
    }

    /// The clean store with one header edit, under a table that trusts the clean header.
    fn edited(from: &str, to: &str) -> Result<Report, String> {
        let (p, line) = clean();
        assert!(line.contains(from), "{from} in {line}");
        tool_with(&line.replacen(from, to, 1), |_| {}, &p, &[line.as_str()], "100")
    }

    /// The clean store with one header edit, under a table that trusts that edit, so the gate under test decides alone.
    fn edited_and_trusted(from: &str, to: &str) -> Result<Report, String> {
        let (p, line) = clean();
        assert!(line.contains(from), "{from} in {line}");
        let e = line.replacen(from, to, 1);
        tool_with(&e, |_| {}, &p, &[e.as_str()], "100")
    }

    #[test]
    fn the_trusted_table_holds_together() {
        let mut seen = Vec::new();
        for t in &TRUSTED {
            assert_eq!(sha::sha256_hex(&block_of(t.line)), t.header_sha256, "{}", t.line);
            assert_eq!(repeated_key(t.line), None);
            let num = |k: &str| field(t.line, k).and_then(number::<u64>).unwrap();
            let (n, rooms, entries, payload, stream) = (num("n="), num("rooms="), num("entries="), num("payload_bytes="), num("stream_bytes="));
            assert_eq!(rooms, n + entries);
            assert_eq!(stream, payload + HEADER_BLOCK);
            assert_eq!(stream % MIB, 0);
            assert!(rooms * 8 <= payload && payload - rooms * 8 < MIB);
            assert_eq!(field(t.line, "sector="), Some("Sx+Sy+"));
            assert_eq!(field(t.line, "w_self_adjoint="), Some("PASS"));
            let lattice = field(t.line, "L=").unwrap();
            assert!(codes(lattice, field(t.line, "nl=")).is_some());
            assert!(!seen.contains(&lattice));
            seen.push(lattice);
            assert_eq!(field(t.line, "payload_merkle=").unwrap().len(), 64);
        }
    }

    #[test]
    fn a_clean_store_with_a_trusted_header_passes_the_whole_tool() {
        let (p, line) = clean();
        let r = tool_with(&line, |_| {}, &p, &[line.as_str()], "100").unwrap();
        assert!(r.pass);
        assert_eq!((r.entries, r.count, r.rooms, r.padding, r.identity), (Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass));
        assert_eq!(r.differs, "-");
        assert_eq!(r.outcome.end.merkle, field(&line, "payload_merkle=").unwrap());
        assert_eq!((r.outcome.end.row_bytes, r.outcome.end.padding_bytes, r.outcome.end.padding_nonzero), (48, ONE_STREAM as u64 - 48, 0));
    }

    #[test]
    fn every_count_gate_at_open_or_fail_decides_alone() {
        for (from, to, entries, count) in [
            ("|entries=4", "", Gate::Open, Gate::Pass),
            ("entries=4", "entries=", Gate::Open, Gate::Pass),
            ("entries=4", "entries=abc", Gate::Open, Gate::Pass),
            ("entries=4", "entries=-4", Gate::Open, Gate::Pass),
            ("entries=4", "entries=+4", Gate::Open, Gate::Pass),
            ("entries=4", "entries=04", Gate::Open, Gate::Pass),
            ("entries=4", "entries=18446744073709551616", Gate::Open, Gate::Pass),
            ("|nl=4", "", Gate::Pass, Gate::Open),
            ("nl=4", "nl=", Gate::Pass, Gate::Open),
            ("nl=4", "nl=abc", Gate::Pass, Gate::Open),
            ("nl=4", "nl=-4", Gate::Pass, Gate::Open),
            ("nl=4", "nl=+4", Gate::Pass, Gate::Open),
            ("nl=4", "nl=04", Gate::Pass, Gate::Open),
            ("nl=4", "nl=3", Gate::Pass, Gate::Open),
            ("L=1x2|", "", Gate::Pass, Gate::Open),
            ("L=1x2", "L=", Gate::Pass, Gate::Open),
            ("L=1x2", "L=2", Gate::Pass, Gate::Open),
            ("L=1x2", "L=axb", Gate::Pass, Gate::Open),
            ("L=1x2", "L=1x2x1", Gate::Pass, Gate::Open),
            ("L=1x2", "L=+1x2", Gate::Pass, Gate::Open),
            ("L=1x2|sector=Sx+Sy+|n=2|nl=4", "L=0x4|sector=Sx+Sy+|n=2|nl=0", Gate::Pass, Gate::Open),
            ("L=1x2", "L=65536x65536", Gate::Pass, Gate::Open),
            ("L=1x2|sector=Sx+Sy+|n=2|nl=4", "L=65536x32768|sector=Sx+Sy+|n=2|nl=0", Gate::Pass, Gate::Open),
            ("L=1x2|sector=Sx+Sy+|n=2|nl=4", "L=7x7|sector=Sx+Sy+|n=2|nl=98", Gate::Pass, Gate::Open),
            ("entries=4", "entries=5", Gate::Fail, Gate::Pass),
            ("L=1x2|sector=Sx+Sy+|n=2|nl=4", "L=1x3|sector=Sx+Sy+|n=2|nl=6", Gate::Pass, Gate::Fail),
        ] {
            let r = edited_and_trusted(from, to).unwrap_or_else(|e| panic!("{from} -> {to}: {e}"));
            assert!(!r.pass, "{from} -> {to}");
            assert_eq!((r.entries, r.count), (entries, count), "{from} -> {to}");
            assert_eq!(r.identity, Gate::Pass, "{from} -> {to}");
            assert!(r.outcome.pairs_clean(2), "{from} -> {to}");
        }
    }

    #[test]
    fn a_malformed_header_or_an_empty_store_stops_the_tool() {
        for (from, to, reason) in [
            ("|n=2|", "|n=0|", "n is 0"),
            ("|n=2|", "|", "missing n="),
            ("|n=2|", "|n=abc|", "missing n="),
            ("|n=2|", "|n=-2|", "missing n="),
            ("|n=2|", "|n=+2|", "canonical"),
            ("|n=2|", "|n=02|", "canonical"),
            ("|n=2|", "|n=7|", "exceeds rooms="),
            ("|n=2|", "|n=2|n=2|", "repeats n="),
            ("|n=2|", "|n=2|n=1|", "repeats n="),
            ("entries=4", "entries=4|entries=4", "repeats entries="),
            ("entries=4", "entries=4|entries=5", "repeats entries="),
            ("nl=4", "nl=4|nl=4", "repeats nl="),
            ("L=1x2", "L=1x2|L=1x3", "repeats L="),
            ("rooms=6", "rooms=6|rooms=6", "repeats rooms="),
            ("|payload_bytes=1044480|", "|", "missing payload_bytes="),
            ("|payload_bytes=1044480|", "|payload_bytes=abc|", "missing payload_bytes="),
            ("|payload_bytes=1044480|", "|payload_bytes=+1044480|", "canonical"),
            ("|payload_bytes=1044480|", "|payload_bytes=01044480|", "canonical"),
            ("|payload_bytes=1044480|", "|payload_bytes=1044472|", "stream_bytes="),
            ("|payload_bytes=1044480|", "|payload_bytes=1044488|", "stream_bytes="),
            ("|payload_bytes=1044480|", "|payload_bytes=1044480|payload_bytes=1044480|", "repeats payload_bytes="),
            ("|rooms=6", "", "rooms="),
            ("rooms=6", "rooms=abc", "rooms="),
            ("rooms=6", "rooms=+6", "rooms="),
            ("rooms=6", "rooms=06", "rooms="),
            ("rooms=6", "rooms=999999999", "does not fit"),
            ("rooms=6", "rooms=18446744073709551615", "does not fit"),
            ("rooms=6", "rooms=1", "exceeds rooms="),
            ("|stream_bytes=1048576", "", "stream_bytes="),
            ("stream_bytes=1048576", "stream_bytes=abc", "stream_bytes="),
            ("stream_bytes=1048576", "stream_bytes=1048577", "stream_bytes="),
            ("stream_bytes=1048576", "stream_bytes=2097152", "stream_bytes="),
            ("w_self_adjoint=PASS", "w_self_adjoint=FAIL", "w_self_adjoint"),
            ("|w_self_adjoint=PASS", "", "w_self_adjoint"),
            ("YMROOMHDR|", "YMROOMHDX|", "YMROOMHDR"),
        ] {
            let e = edited(from, to).err().unwrap_or_else(|| panic!("{from} -> {to} ran"));
            assert!(e.contains(reason), "{from} -> {to}: {e}");
        }
        let (p, line) = clean();
        let at = line.find("payload_merkle=").unwrap();
        let bad = format!("{}payload_merkle={}{}", &line[..at], "0".repeat(64), &line[at + "payload_merkle=".len() + 64..]);
        let e = tool_with(&bad, |_| {}, &p, &[line.as_str()], "100").err().unwrap();
        assert!(e.contains("merkle"), "{e}");
    }

    // ---- D3. Every payload byte is accounted for.

    fn repaired(mut payload: Vec<u8>, edit: impl Fn(&mut Vec<u8>)) -> (Vec<u8>, String) {
        edit(&mut payload);
        let line = line_of(&two_rows(), "1x2", 4, &payload);
        (payload, line)
    }

    #[test]
    fn d3_a_nonzero_byte_past_the_last_row_fails_alone() {
        for at in [48usize, 49, 1000, ONE_STREAM - 1] {
            let (p, line) = repaired(clean().0, |b| b[at] = 1);
            let r = tool_with(&line, |_| {}, &p, &[line.as_str()], "100").unwrap();
            assert!(!r.pass, "byte {at}");
            assert_eq!(r.padding, Gate::Fail, "byte {at}");
            assert_eq!(r.outcome.end.padding_nonzero, 1, "byte {at}");
            assert_eq!((r.entries, r.count, r.rooms, r.identity), (Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass), "byte {at}");
            assert!(r.outcome.pairs_clean(2));
        }
    }

    #[test]
    fn d3_a_bad_row_placed_after_the_last_fails_alone() {
        let (p, line) = repaired(clean().0, |b| {
            let row: Vec<u8> = [7u32.to_le_bytes().to_vec(), 3u16.to_le_bytes().to_vec(), 2u16.to_le_bytes().to_vec(), 0u32.to_le_bytes().to_vec(), (-5i32).to_le_bytes().to_vec(), 2u32.to_le_bytes().to_vec(), 5i32.to_le_bytes().to_vec()].concat();
            b[48..48 + row.len()].copy_from_slice(&row);
        });
        let r = tool_with(&line, |_| {}, &p, &[line.as_str()], "100").unwrap();
        assert!(!r.pass);
        assert_eq!(r.padding, Gate::Fail);
        assert_eq!(r.outcome.census.rows, 2);
    }

    #[test]
    fn d3_rooms_that_differ_from_the_rows_fail_alone() {
        let r = edited_and_trusted("rooms=6", "rooms=7").unwrap();
        assert!(!r.pass);
        assert_eq!(r.rooms, Gate::Fail);
        assert_eq!(r.padding, Gate::Fail);
        assert_eq!(r.identity, Gate::Pass);
    }

    // ---- D4. Sizes are checked before memory is set aside, and what memory holds is bounded.

    #[test]
    fn d4_a_payload_far_past_the_rows_stops_first() {
        let r = two_rows();
        let p = payload_of(&r, 3 * 1_048_576 - 4096);
        let line = line_of(&r, "1x2", 4, &p);
        let e = tool_with(&line, |_| {}, &p, &[line.as_str()], "100").err().unwrap();
        assert!(e.contains("1 MiB or more of padding"), "{e}");
    }

    #[test]
    fn d4_a_store_shorter_than_its_header_says_stops_first() {
        let (p, line) = clean();
        let e = tool_with(&line, |_| {}, &p[..1000], &[line.as_str()], "100").err().unwrap();
        assert!(e.contains("shorter"), "{e}");
    }

    #[test]
    fn d4_sizes_near_the_top_of_the_range_stop_without_wrapping() {
        let hdr = |n: usize, payload: u64| roomio::Hdr { n, payload, merkle: String::new(), lattice: String::new(), sector: String::new() };
        let line = |rooms: &str, stream: &str| format!("YMROOMHDR|rooms={rooms}|stream_bytes={stream}");
        assert!(check_sizes(&line("6", "1048576"), &hdr(2, 1_044_480), 0, 1_048_576).is_ok());
        assert!(check_sizes(&line("6", "1048576"), &hdr(2, 1_044_480), 1, 1_048_576).is_err());
        assert!(check_sizes(&line("6", "1048576"), &hdr(2, 1_044_480), u64::MAX, u64::MAX).is_err());
        assert!(check_sizes(&line("2305843009213693952", "4096"), &hdr(2, 0), 0, u64::MAX).is_err());
        assert!(check_sizes(&line("6", "18446744073709551615"), &hdr(2, u64::MAX), 0, u64::MAX).is_err());
        let e = check_sizes(&line("137438952960", "1099511627776"), &hdr(2, 1_099_511_623_680), 0, 1_048_576).err().unwrap();
        assert!(e.contains("shorter"), "claims 1 TiB in 1 MiB: {e}");
    }

    #[test]
    fn d4_flat_weights_are_all_counted_and_only_some_listed() {
        let rows: Vec<roomio::TestRow> = (0..200u32).map(|h| (h + 1, 0, vec![(h, 0)])).collect();
        let o = check(&rows, 100);
        assert_eq!(o.census.flats, 200);
        assert_eq!(o.census.flat_w.len(), MAX_FLAT_LIST);
        assert_eq!(o.census.flat_w_sum, 200 * 201 / 2);
    }

    #[test]
    fn d4_a_window_stops_at_its_row_cap() {
        let mut win = Window::new(0, Limits { cap: 100, row_cap: 3, reserve: 0 });
        let row = roomscan::Row::empty(1, 3);
        for h in 0..5 {
            win.admit(h, &row);
        }
        assert_eq!((win.end, win.w.len(), win.closed), (3, 3, true));
    }

    // ---- D5. Both caps are reported.

    #[test]
    fn d5_the_requested_and_the_effective_cap_are_both_reported() {
        let (p, line) = clean();
        for (cap, requested, effective, passes) in [("0", 0, 1, 1), ("1", 1, 1, 1), ("100", 100, 100, 1), ("18446744073709551615", usize::MAX, MAX_CAP, 1)] {
            let r = tool_with(&line, |_| {}, &p, &[line.as_str()], cap).unwrap();
            assert!(r.pass, "cap {cap}");
            assert_eq!((r.requested, r.effective, r.outcome.passes.len()), (requested, effective, passes), "cap {cap}");
        }
    }

    // ---- D6. A store passes only as a store the table names.

    #[test]
    fn d6_a_store_labelled_as_another_fails_identity_and_names_what_differs() {
        // Clean by every other gate, and labelled L=1x2 like the store the table trusts.
        let mut rows = two_rows();
        rows[0].2[1].1 = -2;
        rows[1].2[0].1 = -2;
        rows[0].2[0].1 = 2;
        rows[1].2[1].1 = 2;
        let p = payload_of(&rows, ONE_STREAM);
        let other = line_of(&rows, "1x2", 4, &p);
        let trusted = clean().1;
        let r = tool_with(&other, |_| {}, &p, &[trusted.as_str()], "100").unwrap();
        assert!(!r.pass);
        assert_eq!(r.identity, Gate::Fail);
        assert_eq!(r.differs, "payload_merkle");
        assert_eq!((r.entries, r.count, r.rooms, r.padding), (Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass));
        assert!(r.outcome.pairs_clean(2) && r.outcome.census.structure_clean());
    }

    #[test]
    fn d6_a_lattice_outside_the_table_reads_open() {
        let (p, line) = clean();
        let r = tool_with(&line, |_| {}, &p, &[], "100").unwrap();
        assert!(!r.pass);
        assert_eq!(r.identity, Gate::Open);
        for t in &TRUSTED {
            assert_eq!(identity_gate(&TRUSTED, t.header_sha256, t.line), (Gate::Pass, "-".to_string()));
        }
        assert_eq!(identity_gate(&TRUSTED, "no-such-hash", "YMROOMHDR|L=9x9|n=1"), (Gate::Open, "-".to_string()));
        assert_eq!(identity_gate(&TRUSTED, "no-such-hash", "YMROOMHDR|n=1"), (Gate::Open, "-".to_string()));
    }

    #[test]
    fn d6_the_real_three_by_four_header_passes_and_a_four_row_store_with_its_label_fails() {
        let t = &TRUSTED[3];
        assert_eq!(identity_gate(&TRUSTED, &sha::sha256_hex(&block_of(t.line)), t.line).0, Gate::Pass);
        let w = 3_265_173_504u32;
        let rows: Vec<roomio::TestRow> = vec![(w, 3, vec![(0, 2), (1, -1), (3, -1)]), (w, 3, vec![(0, -1), (1, 2), (2, -1)]), (w, 3, vec![(1, -1), (2, 2), (3, -1)]), (w, 3, vec![(0, -1), (2, -1), (3, 2)])];
        let p = payload_of(&rows, ONE_STREAM);
        let line = line_of(&rows, "3x4", 24, &p);
        let a = {
            let f = temp();
            let mut b = block_of(&line);
            b.extend_from_slice(&p);
            std::fs::write(&f, b).unwrap();
            let r = run_tool(&["allpairs".to_string(), f.to_str().unwrap().to_string(), "0".to_string()], &TRUSTED, "-").unwrap();
            std::fs::remove_file(f).unwrap();
            r
        };
        assert!(!a.pass);
        assert_eq!(a.identity, Gate::Fail);
        assert_eq!((a.entries, a.count, a.rooms, a.padding), (Gate::Pass, Gate::Pass, Gate::Pass, Gate::Pass), "the other gates pass this store");
        for key in ["n", "rooms", "entries", "payload_bytes", "stream_bytes", "payload_merkle", "keys_sha256"] {
            assert!(a.differs.split(',').any(|k| k == key), "{key} in {}", a.differs);
        }
    }

    // ---- D7. Every missing counterpart is counted, at every cap.

    #[test]
    fn d7_the_reviewer_case_counts_one_unpaired_and_one_repeated() {
        for cap in CAPS {
            // Pick h and m, both above i and both joined to i. Double h's entry for i and delete m's.
            let base = store();
            let i = (0..40usize).find(|&i| base[i].2.iter().filter(|e| e.0 as usize > i).count() >= 2).unwrap();
            let above: Vec<usize> = base[i].2.iter().map(|e| e.0 as usize).filter(|&j| j > i).collect();
            let (h, m) = (above[0], above[1]);
            let mut r = base;
            let z = *entry(&mut r, h, i as u32);
            let at = r[h].2.iter().position(|e| e.0 == i as u32).unwrap();
            r[h].2.insert(at, (i as u32, z));
            r[m].2.retain(|e| e.0 != i as u32);
            let o = check(&r, cap);
            assert_eq!(o.total(|p| p.upper_without_lower), 1, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_repeated), 1, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_without_upper), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.found), o.census.lower, "cap {cap}");
            assert_eq!(o.total(|p| p.answered), o.total(|p| p.stored) - 1, "cap {cap}");
            assert!(!o.pairs_clean(r.len()));
        }
    }

    #[test]
    fn d7_two_equal_entries_each_take_their_own_partner() {
        // Two rows joined twice, so every entry has a partner and only the column gate reports the repeat.
        for cap in CAPS {
            let r = vec![(1u32, 3u16, vec![(0u32, 2i32), (1, -1), (1, -1)]), (1, 3, vec![(0, -1), (0, -1), (1, 2)])];
            let o = check(&r, cap);
            assert_eq!(o.total(|p| p.upper_without_lower), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_repeated), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.answered), 2, "cap {cap}");
            assert_eq!(o.census.not_ascending, 2, "cap {cap}");
            assert!(!o.census.structure_clean());
        }
    }

    #[test]
    fn d7_counts_on_rows_out_of_order_are_the_same_at_every_cap() {
        let mut reference = None;
        for cap in CAPS {
            let mut r = store();
            for h in [3usize, 11, 27] {
                r[h].2.reverse();
            }
            let o = check(&r, cap);
            assert_eq!(o.total(|p| p.value_mismatch), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.upper_without_lower), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_without_upper), 0, "cap {cap}");
            assert_eq!(o.total(|p| p.lower_repeated), 0, "cap {cap}");
            let row = (o.census.upper, o.total(|p| p.found), o.total(|p| p.answered), o.census.not_ascending);
            assert_eq!(*reference.get_or_insert(row), row, "cap {cap}");
            assert!(!o.census.structure_clean());
        }
    }

    // ---- D8. The whole header block is bound to the table.

    #[test]
    fn d8_a_change_anywhere_in_the_header_block_fails_identity() {
        // Every bit of the 3x4 block, and every bit of each line and the byte after it for the others.
        for (k, t) in TRUSTED.iter().enumerate() {
            let clean_block = block_of(t.line);
            let bits = if k == 3 { clean_block.len() * 8 } else { (t.line.len() + 2) * 8 };
            for bit in 0..bits {
                let mut b = clean_block.clone();
                b[bit / 8] ^= 1 << (bit % 8);
                let end = b.iter().position(|&x| x == b'\n').unwrap_or(b.len());
                let line = String::from_utf8_lossy(&b[..end]).to_string();
                let (gate, _) = identity_gate(&TRUSTED, &sha::sha256_hex(&b), &line);
                assert_ne!(gate, Gate::Pass, "bit {bit} of {}", t.line);
            }
        }
    }

    #[test]
    fn d8_each_field_the_tool_only_prints_or_leaves_unread_now_fails_identity() {
        for (from, to, differs) in [
            ("sector=Sx+Sy+", "sector=OTHER", "sector"),
            ("|sector=Sx+Sy+", "", "sector"),
            ("chunk=16MiB", "chunk=1MiB", "chunk"),
            ("|chunk=16MiB", "", "chunk"),
            ("keys_sha256=keysha", "keys_sha256=other", "keys_sha256"),
            ("|json=0", "|json=1", "json"),
            ("|json=0", "", "json"),
            ("|json=0", "|json=0|extra=1", "extra"),
        ] {
            let r = edited(from, to).unwrap_or_else(|e| panic!("{from} -> {to}: {e}"));
            assert!(!r.pass, "{from} -> {to}");
            assert_eq!(r.identity, Gate::Fail, "{from} -> {to}");
            assert_eq!(r.differs, differs, "{from} -> {to}");
        }
    }

    #[test]
    fn d8_a_byte_after_the_header_line_fails_identity_as_the_block() {
        let (p, line) = clean();
        let r = tool_with(
            &line,
            |b| {
                let at = b.iter().position(|&x| x == b'\n').unwrap() + 1;
                b[at] = 1;
            },
            &p,
            &[line.as_str()],
            "100",
        )
        .unwrap();
        assert!(!r.pass);
        assert_eq!((r.identity, r.differs.as_str()), (Gate::Fail, "header_block"));
    }
}
