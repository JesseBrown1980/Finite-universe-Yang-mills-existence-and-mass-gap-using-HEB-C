//! Second seat's reader for a `ymroom build` stream, written from the format in the sources with no code taken from
//! `roomio`, `segio`, `sha` or `allpairs`. One sequential read of the whole store, O(1) memory for the pair tests.
//!
//! Measures, in the one pass: the row census; the windows `allpairs` would cut at CAP, with the lower entries that land
//! in each; the payload merkle; each sector file's SHA-256; the padding after the last row and the raw tail after the
//! payload; and two order-independent tests that the upper triples (h, j, w_h z_hj), j > h, are the same multiset as the
//! lower triples (j, h, w_h z_hj), j < h:
//!   A. a product fingerprint over GF(2^127 - 1) at a random point r: false pass <= N / (2^127 - 1) for any stores fixed
//!      before r is drawn, N the larger multiset, with no assumption about any hash;
//!   B. a keyed sum of SipHash-2-4 modulo 2^61 - 1: false pass about 2^-61 if SipHash-2-4 is a PRF.
//!
//!   review-reader SPEC --r HEX --k0 HEX --k1 HEX [--cap N] [--manifest FILE]
//!
//! SPEC is a path or seg:<first>:<count>:<seglen>:<prefix>. Exit 0 only when every test below passes and n >= 1, exit 2
//! when one fails, exit 1 when the store cannot be read. Integer only, std only, json=0.

#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::fs::File;
use std::io::Read;
use std::sync::mpsc::{sync_channel, Receiver, SyncSender};
use std::sync::Arc;

const BUF: usize = 16 << 20;
const LEAF: u64 = 16 << 20;
const HDR: u64 = 4096;
const P127: u128 = (1u128 << 127) - 1;
const P61: u64 = (1u64 << 61) - 1;
const LIST_MAX: usize = 64;

// ---------------------------------------------------------------- SHA-256, FIPS 180-4, constants derived by integer roots

fn first_primes(k: usize) -> Vec<u64> {
    let mut out: Vec<u64> = Vec::with_capacity(k);
    let mut c = 2u64;
    while out.len() < k {
        if out.iter().all(|p| c % p != 0) {
            out.push(c);
        }
        c += 1;
    }
    out
}

/// Largest x with x^e <= v, by bisection. e is 2 or 3, v < 2^112.
fn iroot(v: u128, e: u32) -> u128 {
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
}

pub struct ShaTables {
    k: [u32; 64],
    h0: [u32; 8],
}

impl ShaTables {
    fn new() -> ShaTables {
        let p = first_primes(64);
        let mut k = [0u32; 64];
        let mut h0 = [0u32; 8];
        for (i, slot) in k.iter_mut().enumerate() {
            *slot = (iroot(u128::from(p[i]) << 96, 3) & 0xFFFF_FFFF) as u32;
        }
        for (i, slot) in h0.iter_mut().enumerate() {
            *slot = (iroot(u128::from(p[i]) << 64, 2) & 0xFFFF_FFFF) as u32;
        }
        ShaTables { k, h0 }
    }
}

struct Sha<'a> {
    t: &'a ShaTables,
    h: [u32; 8],
    pend: [u8; 64],
    fill: usize,
    total: u64,
}

impl<'a> Sha<'a> {
    fn new(t: &'a ShaTables) -> Sha<'a> {
        Sha { t, h: t.h0, pend: [0; 64], fill: 0, total: 0 }
    }

    fn block(&mut self, b: &[u8]) {
        let mut w = [0u32; 64];
        for (i, c) in b.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([c[0], c[1], c[2], c[3]]);
        }
        for i in 16..64 {
            let a = w[i - 15];
            let e = w[i - 2];
            let s0 = a.rotate_right(7) ^ a.rotate_right(18) ^ (a >> 3);
            let s1 = e.rotate_right(17) ^ e.rotate_right(19) ^ (e >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut v = self.h;
        for (wi, ki) in w.iter().zip(self.t.k.iter()) {
            let bs1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(bs1).wrapping_add(ch).wrapping_add(*ki).wrapping_add(*wi);
            let bs0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = bs0.wrapping_add(maj);
            v[7] = v[6];
            v[6] = v[5];
            v[5] = v[4];
            v[4] = v[3].wrapping_add(t1);
            v[3] = v[2];
            v[2] = v[1];
            v[1] = v[0];
            v[0] = t1.wrapping_add(t2);
        }
        for (x, y) in self.h.iter_mut().zip(v) {
            *x = x.wrapping_add(y);
        }
    }

    fn update(&mut self, mut d: &[u8]) {
        self.total = self.total.wrapping_add(d.len() as u64);
        if self.fill > 0 {
            let take = d.len().min(64 - self.fill);
            self.pend[self.fill..self.fill + take].copy_from_slice(&d[..take]);
            self.fill += take;
            d = &d[take..];
            if self.fill == 64 {
                let p = self.pend;
                self.block(&p);
                self.fill = 0;
            }
        }
        let mut it = d.chunks_exact(64);
        for b in &mut it {
            self.block(b);
        }
        let r = it.remainder();
        if !r.is_empty() {
            self.pend[..r.len()].copy_from_slice(r);
            self.fill = r.len();
        }
    }

    fn hex(mut self) -> String {
        let bits = self.total.wrapping_mul(8);
        self.update(&[0x80]);
        while self.fill != 56 {
            self.update(&[0]);
        }
        self.update(&bits.to_be_bytes());
        let mut s = String::with_capacity(64);
        for w in self.h {
            for b in w.to_be_bytes() {
                s.push(char::from_digit(u32::from(b >> 4), 16).unwrap_or('?'));
                s.push(char::from_digit(u32::from(b & 15), 16).unwrap_or('?'));
            }
        }
        s
    }
}

// ---------------------------------------------------------------- GF(2^127 - 1)

fn red127(x: u128) -> u128 {
    let y = (x & P127) + (x >> 127);
    if y >= P127 {
        y - P127
    } else {
        y
    }
}

fn mul127(a: u128, b: u128) -> u128 {
    let (a1, a0) = (a >> 64, a & 0xFFFF_FFFF_FFFF_FFFF);
    let (b1, b0) = (b >> 64, b & 0xFFFF_FFFF_FFFF_FFFF);
    let ll = a0 * b0;
    let mid = a1 * b0 + a0 * b1;
    let hh = a1 * b1;
    // total = hh 2^128 + mid 2^64 + ll, and 2^128 = 2 modulo 2^127 - 1.
    let t1 = red127(hh << 1);
    let t2 = red127((mid >> 64) << 1);
    let t3 = red127((mid & 0xFFFF_FFFF_FFFF_FFFF) << 64);
    let t4 = red127(ll);
    red127(red127(t1 + t2) + red127(t3 + t4))
}

fn encode(lo: u32, hi: u32, v: i64) -> u128 {
    let shifted = (v as u64) ^ (1u64 << 63);
    (u128::from(lo) << 95) | (u128::from(hi & 0x7FFF_FFFF) << 64) | u128::from(shifted)
}

// ---------------------------------------------------------------- SipHash-2-4

#[inline(always)]
fn sipround(v: &mut [u64; 4]) {
    v[0] = v[0].wrapping_add(v[1]);
    v[1] = v[1].rotate_left(13) ^ v[0];
    v[0] = v[0].rotate_left(32);
    v[2] = v[2].wrapping_add(v[3]);
    v[3] = v[3].rotate_left(16) ^ v[2];
    v[0] = v[0].wrapping_add(v[3]);
    v[3] = v[3].rotate_left(21) ^ v[0];
    v[2] = v[2].wrapping_add(v[1]);
    v[1] = v[1].rotate_left(17) ^ v[2];
    v[2] = v[2].rotate_left(32);
}

fn sip_init(k0: u64, k1: u64) -> [u64; 4] {
    [k0 ^ 0x736f_6d65_7073_6575, k1 ^ 0x646f_7261_6e64_6f6d, k0 ^ 0x6c79_6765_6e65_7261, k1 ^ 0x7465_6462_7974_6573]
}

fn sip_word(v: &mut [u64; 4], m: u64) {
    v[3] ^= m;
    sipround(v);
    sipround(v);
    v[0] ^= m;
}

fn sip_final(v: &mut [u64; 4]) -> u64 {
    v[2] ^= 0xFF;
    sipround(v);
    sipround(v);
    sipround(v);
    sipround(v);
    v[0] ^ v[1] ^ v[2] ^ v[3]
}

/// SipHash-2-4 of three little-endian words, 24 bytes.
#[inline(always)]
fn sip3(k0: u64, k1: u64, a: u64, b: u64, c: u64) -> u64 {
    let mut v = sip_init(k0, k1);
    sip_word(&mut v, a);
    sip_word(&mut v, b);
    sip_word(&mut v, c);
    sip_word(&mut v, 24u64 << 56);
    sip_final(&mut v)
}

/// SipHash-2-4 of any bytes, for the known-answer test and to check `sip3`.
#[cfg(test)]
fn sip_bytes(k0: u64, k1: u64, d: &[u8]) -> u64 {
    let mut v = sip_init(k0, k1);
    let mut it = d.chunks_exact(8);
    for c in &mut it {
        sip_word(&mut v, u64::from_le_bytes([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]]));
    }
    let mut last = (d.len() as u64 & 0xFF) << 56;
    for (i, b) in it.remainder().iter().enumerate() {
        last |= u64::from(*b) << (8 * i);
    }
    sip_word(&mut v, last);
    sip_final(&mut v)
}

fn red61(x: u64) -> u64 {
    let y = (x & P61) + (x >> 61);
    if y >= P61 {
        y - P61
    } else {
        y
    }
}

// ---------------------------------------------------------------- the row walk

struct Windows {
    cap: u64,
    start: Vec<u64>,
    upper: Vec<u64>,
    lower: Vec<u64>,
    cur: u64,
}

impl Windows {
    fn new(cap: u64) -> Windows {
        Windows { cap, start: vec![0], upper: vec![0], lower: vec![0], cur: 0 }
    }

    fn admit(&mut self, h: u64, count: u64) {
        let open_at = self.start[self.start.len() - 1];
        if self.cur + count > self.cap && h > open_at {
            self.start.push(h);
            self.upper.push(0);
            self.lower.push(0);
            self.cur = 0;
        }
        self.cur += count;
        let k = self.upper.len() - 1;
        self.upper[k] += count;
    }

    #[inline(always)]
    fn note_lower(&mut self, i: u64) {
        let k = self.start.partition_point(|&s| s <= i) - 1;
        self.lower[k] += 1;
    }
}

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
    flat_w: Vec<u32>,
    flat_rows: Vec<u64>,
    flat_off: u64,
    max_cnt: u32,
    max_w: u32,
    min_z: i32,
    max_z: i32,
    max_abs_v: u64,
    payload_rooms: u64,
    used_rooms: u64,
    trailing_rooms: u64,
    trailing_nonzero: u64,
    odd_bytes: u64,
}

struct Walk {
    n: u64,
    r: u128,
    k0: u64,
    k1: u64,
    h: u64,
    left: u32,
    w: u32,
    mag: u16,
    prev: Option<u32>,
    sum: i64,
    row_diag: u32,
    row_upper: u64,
    row_off: u64,
    c: Census,
    prod_upper: u128,
    prod_lower: u128,
    sum61: u64,
    bucket61: Vec<u64>,
    win: Windows,
}

impl Walk {
    fn new(n: u64, r: u128, k0: u64, k1: u64, cap: u64) -> Walk {
        Walk {
            n,
            r,
            k0,
            k1,
            h: 0,
            left: 0,
            w: 0,
            mag: 0,
            prev: None,
            sum: 0,
            row_diag: 0,
            row_upper: 0,
            row_off: 0,
            c: Census::default(),
            prod_upper: 1,
            prod_lower: 1,
            sum61: 0,
            bucket61: vec![0; usize::try_from(n >> 16).unwrap_or(0) + 1],
            win: Windows::new(cap),
        }
    }

    fn end_row(&mut self) {
        self.c.rows += 1;
        self.c.zero_weight += u64::from(self.w == 0);
        self.c.missing_diag += u64::from(self.row_diag == 0);
        self.c.row_sum_nonzero += u64::from(self.sum != 0);
        self.c.sum_w += u128::from(self.w);
        if self.mag == 0 {
            self.c.flats += 1;
            self.c.flat_off += self.row_off;
            if self.c.flat_w.len() < LIST_MAX {
                self.c.flat_w.push(self.w);
                self.c.flat_rows.push(self.h);
            }
        }
        self.win.admit(self.h, self.row_upper);
        self.h += 1;
    }

    fn begin_row(&mut self, w: u32, mag: u16, cnt: u16) {
        self.w = w;
        self.mag = mag;
        self.left = u32::from(cnt);
        self.prev = None;
        self.sum = 0;
        self.row_diag = 0;
        self.row_upper = 0;
        self.row_off = 0;
        self.c.max_cnt = self.c.max_cnt.max(u32::from(cnt));
        self.c.max_w = self.c.max_w.max(w);
        if cnt == 0 {
            self.end_row();
        }
    }

    #[inline(always)]
    fn entry(&mut self, j: u32, z: i32) {
        self.c.entries += 1;
        if let Some(p) = self.prev {
            self.c.not_ascending += u64::from(j <= p);
        }
        self.prev = Some(j);
        let jw = u64::from(j);
        self.c.out_of_range += u64::from(jw >= self.n);
        self.c.zero_z += u64::from(z == 0);
        self.sum += i64::from(z);
        self.c.min_z = self.c.min_z.min(z);
        self.c.max_z = self.c.max_z.max(z);
        if jw == self.h {
            self.c.diag += 1;
            self.row_diag += 1;
        } else {
            self.row_off += 1;
            self.c.positive_off += u64::from(z > 0);
            let v = i64::from(self.w) * i64::from(z);
            self.c.max_abs_v = self.c.max_abs_v.max(v.unsigned_abs());
            let h32 = self.h as u32;
            let up = jw > self.h;
            let (lo, hi) = if up { (h32, j) } else { (j, h32) };
            let m = encode(lo, hi, v);
            let fac = red127(self.r + P127 - red127(m));
            let t = red61(sip3(self.k0, self.k1, u64::from(lo), u64::from(hi), v as u64));
            let slot = usize::try_from(u64::from(lo) >> 16).unwrap_or(0);
            let delta = if up {
                self.c.upper += 1;
                self.row_upper += 1;
                self.prod_upper = mul127(self.prod_upper, fac);
                t
            } else {
                self.c.lower += 1;
                self.prod_lower = mul127(self.prod_lower, fac);
                self.win.note_lower(jw);
                P61 - t
            };
            self.sum61 = red61(self.sum61 + delta);
            if let Some(s) = self.bucket61.get_mut(slot) {
                *s = red61(*s + delta);
            }
        }
        self.left -= 1;
        if self.left == 0 {
            self.end_row();
        }
    }

    fn feed(&mut self, d: &[u8]) {
        let mut it = d.chunks_exact(8);
        for room in &mut it {
            let a = u32::from_le_bytes([room[0], room[1], room[2], room[3]]);
            let b = u32::from_le_bytes([room[4], room[5], room[6], room[7]]);
            self.c.payload_rooms += 1;
            if self.left > 0 {
                self.c.used_rooms += 1;
                self.entry(a, b as i32);
            } else if self.h < self.n {
                self.c.used_rooms += 1;
                self.begin_row(a, (b & 0xFFFF) as u16, (b >> 16) as u16);
            } else {
                self.c.trailing_rooms += 1;
                self.c.trailing_nonzero += u64::from(a != 0 || b != 0);
            }
        }
        // Only the end of the payload can leave bytes that do not fill a room.
        let odd = it.remainder();
        self.c.odd_bytes += odd.len() as u64;
        self.c.trailing_nonzero += u64::from(odd.iter().any(|&x| x != 0));
    }
}

// ---------------------------------------------------------------- the store

struct Store {
    files: Vec<String>,
    seglen: u64,
}

fn parse_spec(s: &str) -> Result<Store, String> {
    if let Some(rest) = s.strip_prefix("seg:") {
        let mut p = rest.splitn(4, ':');
        let mut num = || p.next().and_then(|t| t.parse::<u64>().ok()).ok_or("seg spec");
        let first = num()?;
        let count = num()?;
        let seglen = num()?;
        let prefix = p.next().ok_or("seg spec")?;
        if count == 0 || seglen == 0 {
            return Err("seg spec: zero count or length".into());
        }
        let end = first.checked_add(count).ok_or("seg spec: range")?;
        let files = (first..end).map(|k| format!("{prefix}{k:03}.rooms")).collect();
        Ok(Store { files, seglen })
    } else {
        Ok(Store { files: vec![s.to_string()], seglen: 0 })
    }
}

fn kv<'a>(line: &'a str, key: &str) -> Option<&'a str> {
    line.split('|').find_map(|part| part.split_once('=').filter(|(k, _)| *k == key).map(|(_, v)| v))
}

type Msg = (u64, Arc<Vec<u8>>);

fn read_all(st: &Store, senders: [SyncSender<Msg>; 3]) -> Result<u64, String> {
    let mut off = 0u64;
    let mut idx = 0usize;
    let mut cur: Option<File> = None;
    let mut in_file = 0u64;
    loop {
        let mut buf = vec![0u8; BUF];
        let mut fill = 0usize;
        while fill < BUF {
            if cur.is_none() {
                if idx == st.files.len() {
                    break;
                }
                let f = File::open(&st.files[idx]).map_err(|e| format!("open {}: {e}", st.files[idx]))?;
                let len = f.metadata().map_err(|e| format!("metadata: {e}"))?.len();
                if st.seglen > 0 && len != st.seglen {
                    return Err(format!("{}: length {len} is not {}", st.files[idx], st.seglen));
                }
                cur = Some(f);
                in_file = 0;
            }
            let got = match cur.as_mut() {
                Some(f) => f.read(&mut buf[fill..]).map_err(|e| format!("read: {e}"))?,
                None => 0,
            };
            if got == 0 {
                if st.seglen > 0 && in_file != st.seglen {
                    return Err(format!("{}: read {in_file} bytes", st.files[idx]));
                }
                cur = None;
                idx += 1;
            } else {
                fill += got;
                in_file += got as u64;
            }
        }
        if fill == 0 {
            return Ok(off);
        }
        buf.truncate(fill);
        let a = Arc::new(buf);
        for tx in &senders {
            tx.send((off, Arc::clone(&a))).map_err(|_| "a consumer stopped")?;
        }
        off += fill as u64;
        if fill < BUF {
            return Ok(off);
        }
    }
}

fn sector_hashes(t: &ShaTables, rx: Receiver<Msg>, seglen: u64) -> Vec<String> {
    let mut out = Vec::new();
    let mut sha = Sha::new(t);
    let mut done = 0u64;
    for (_, buf) in rx {
        let mut d: &[u8] = &buf;
        while !d.is_empty() {
            let room = if seglen == 0 { d.len() } else { usize::try_from(seglen - done).unwrap_or(d.len()).min(d.len()) };
            sha.update(&d[..room]);
            done += room as u64;
            d = &d[room..];
            if seglen > 0 && done == seglen {
                let full = std::mem::replace(&mut sha, Sha::new(t));
                out.push(full.hex());
                done = 0;
            }
        }
    }
    if done > 0 {
        out.push(sha.hex());
    }
    out
}

fn merkle(t: &ShaTables, rx: Receiver<Msg>, payload: u64) -> (String, u64) {
    let mut root = Sha::new(t);
    let mut leaf = Sha::new(t);
    let mut in_leaf = 0u64;
    let mut seen = 0u64;
    let (from, to) = (HDR, HDR.saturating_add(payload));
    for (off, buf) in rx {
        let s = off.max(from);
        let e = (off + buf.len() as u64).min(to);
        if s >= e {
            continue;
        }
        let mut d = &buf[usize::try_from(s - off).unwrap_or(0)..usize::try_from(e - off).unwrap_or(0)];
        seen += d.len() as u64;
        while !d.is_empty() {
            let take = usize::try_from(LEAF - in_leaf).unwrap_or(d.len()).min(d.len());
            leaf.update(&d[..take]);
            in_leaf += take as u64;
            d = &d[take..];
            if in_leaf == LEAF {
                let full = std::mem::replace(&mut leaf, Sha::new(t));
                root.update(full.hex().as_bytes());
                in_leaf = 0;
            }
        }
    }
    if in_leaf > 0 {
        root.update(leaf.hex().as_bytes());
    }
    (root.hex(), seen)
}

fn walker(mut w: Walk, rx: Receiver<Msg>, payload: u64) -> (Walk, u64) {
    let (from, to) = (HDR, HDR.saturating_add(payload));
    let mut tail_nonzero = 0u64;
    for (off, buf) in rx {
        let end = off + buf.len() as u64;
        let (s, e) = (off.max(from), end.min(to));
        if s < e {
            w.feed(&buf[usize::try_from(s - off).unwrap_or(0)..usize::try_from(e - off).unwrap_or(0)]);
        }
        if end > to {
            let t = off.max(to);
            let tail = &buf[usize::try_from(t - off).unwrap_or(0)..];
            tail_nonzero += tail.iter().filter(|&&b| b != 0).count() as u64;
        }
    }
    (w, tail_nonzero)
}

fn codes(lattice: &str, nl: Option<&str>) -> Option<u128> {
    let (a, b) = lattice.split_once('x')?;
    let v = u64::from(a.parse::<u32>().ok()?) * u64::from(b.parse::<u32>().ok()?);
    if nl?.parse::<u64>().ok()? != 2 * v {
        return None;
    }
    6u128.checked_pow(u32::try_from(v + 1).ok()?)
}

fn opt(a: &[String], key: &str) -> Option<String> {
    a.iter().position(|x| x == key).and_then(|i| a.get(i + 1)).cloned()
}

fn hex64(a: &[String], key: &str) -> Result<u64, String> {
    let s = opt(a, key).ok_or(format!("missing {key}"))?;
    u64::from_str_radix(&s, 16).map_err(|_| format!("bad {key}"))
}

fn join_list<T: ToString>(v: &[T]) -> String {
    v.iter().map(T::to_string).collect::<Vec<_>>().join(",")
}

fn real_main(a: &[String]) -> Result<bool, String> {
    let t0 = std::time::Instant::now();
    let spec = a.get(1).ok_or("usage: review-reader SPEC --r HEX --k0 HEX --k1 HEX [--cap N] [--manifest FILE]")?;
    let r = u128::from_str_radix(&opt(a, "--r").ok_or("missing --r")?, 16).map_err(|_| "bad --r")?;
    if r >= P127 {
        return Err("r must be below 2^127 - 1".into());
    }
    let (k0, k1) = (hex64(a, "--k0")?, hex64(a, "--k1")?);
    let cap: u64 = opt(a, "--cap").unwrap_or_else(|| "470000000".into()).parse().map_err(|_| "bad --cap")?;
    if cap == 0 {
        return Err("cap must be at least 1".into());
    }
    let st = parse_spec(spec)?;
    let mut blk = vec![0u8; HDR as usize];
    File::open(&st.files[0]).map_err(|e| format!("open: {e}"))?.read_exact(&mut blk).map_err(|e| format!("header: {e}"))?;
    let eol = blk.iter().position(|&b| b == b'\n').ok_or("no header line")?;
    let line = std::str::from_utf8(&blk[..eol]).map_err(|_| "header is not utf-8")?.to_string();
    let tables = ShaTables::new();
    let mut hs = Sha::new(&tables);
    hs.update(&blk);
    let header_block_sha = hs.hex();
    println!("REVIEW_HEADER|sha256_of_block={header_block_sha}|line={line}|json=0");
    if !line.starts_with("YMROOMHDR|") {
        return Err("not YMROOMHDR".into());
    }
    let num = |k: &str| kv(&line, k).and_then(|v| v.parse::<u64>().ok()).ok_or(format!("missing {k}"));
    let n = num("n")?;
    let payload = num("payload_bytes")?;
    let merkle_hdr = kv(&line, "payload_merkle").unwrap_or("").to_string();
    if n >= 1u64 << 31 {
        return Err("n is too large for this reader".into());
    }
    let (t_s, r_s) = sync_channel::<Msg>(4);
    let (t_m, r_m) = sync_channel::<Msg>(4);
    let (t_w, r_w) = sync_channel::<Msg>(4);
    let walk = Walk::new(n, r, k0, k1, cap);
    let seglen = st.seglen;
    let (w, tail_nonzero, stream_bytes, merkle_hex, merkle_seen, sector_hex) = std::thread::scope(|sc| -> Result<_, String> {
        let tb = &tables;
        let ts = sc.spawn(move || sector_hashes(tb, r_s, seglen));
        let tm = sc.spawn(move || merkle(tb, r_m, payload));
        let tw = sc.spawn(move || walker(walk, r_w, payload));
        let read = read_all(&st, [t_s, t_m, t_w]);
        let sector_hex = ts.join().map_err(|_| "sector thread")?;
        let (m, seen) = tm.join().map_err(|_| "merkle thread")?;
        let (w, tn) = tw.join().map_err(|_| "walk thread")?;
        Ok((w, tn, read?, m, seen, sector_hex))
    })?;
    // Sector hashes against the manifest, when one is given.
    let mut sectors_match = 0usize;
    let manifest_given = opt(a, "--manifest").is_some();
    let mut want: Vec<(String, String)> = Vec::new();
    if let Some(mpath) = opt(a, "--manifest") {
        let text = std::fs::read_to_string(&mpath).map_err(|e| format!("manifest: {e}"))?;
        for l in text.lines() {
            let mut p = l.split_whitespace();
            if let (Some(h), Some(nm)) = (p.next(), p.next()) {
                let base = nm.trim_start_matches('*').rsplit('/').next().unwrap_or(nm).to_string();
                want.push((base, h.to_string()));
            }
        }
    }
    for (name, hx) in st.files.iter().zip(&sector_hex) {
        let base = name.rsplit('/').next().unwrap_or(name);
        let hit = want.iter().find(|(b, _)| b == base).map(|(_, h)| h == hx);
        println!("REVIEW_SECTOR|name={base}|sha256={hx}|manifest_match={}|json=0", u8::from(hit == Some(true)));
        sectors_match += usize::from(hit == Some(true));
    }
    let c = &w.c;
    for k in 0..w.win.start.len() {
        let to = w.win.start.get(k + 1).copied().unwrap_or(c.rows);
        println!("REVIEW_WINDOW|k={k}|rows_from={}|rows_to={to}|upper_stored={}|lower_into_window={}|json=0", w.win.start[k], w.win.upper[k], w.win.lower[k]);
    }
    let buckets_nonzero = w.bucket61.iter().filter(|&&s| s != 0).count();
    let first_bucket = w.bucket61.iter().position(|&s| s != 0).map_or("-".to_string(), |p| p.to_string());
    let entries_field = kv(&line, "entries").and_then(|v| v.parse::<u64>().ok());
    let rooms_field = kv(&line, "rooms").and_then(|v| v.parse::<u64>().ok());
    let expected = codes(kv(&line, "L").unwrap_or(""), kv(&line, "nl"));
    let structure = [c.not_ascending, c.out_of_range, c.zero_z, c.positive_off, c.row_sum_nonzero, c.zero_weight, c.missing_diag].iter().all(|&v| v == 0);
    let pairs_ok = c.upper == c.lower && w.prod_upper == w.prod_lower && w.sum61 == 0 && buckets_nonzero == 0 && w.prod_upper != 0;
    let merkle_ok = merkle_hex == merkle_hdr && merkle_seen == payload;
    let complete = n >= 1 && c.rows == n && w.left == 0;
    let count_fields = entries_field == Some(c.entries) && rooms_field == Some(c.used_rooms) && expected == Some(c.sum_w);
    let manifest_ok = !manifest_given || sectors_match == st.files.len();
    let padding_clean = c.trailing_nonzero == 0 && c.odd_bytes == 0;
    let pass = complete && structure && pairs_ok && merkle_ok && count_fields && manifest_ok && padding_clean;
    println!(
        "REVIEW_READER|L={}|sector={}|n={n}|rows={}|entries={}|diag={}|upper={}|lower={}|not_ascending={}|out_of_range={}|zero_z={}|positive_off={}|row_sum_nonzero={}|zero_weight={}|missing_diag={}|sum_w={}|codes={}|flats={}|flat_w={}|flat_rows={}|flat_off_entries={}|max_cnt={}|max_w={}|min_z={}|max_z={}|max_abs_wz={}|used_rooms={}|trailing_rooms={}|trailing_nonzero_rooms={}|odd_bytes={}|tail_nonzero_bytes={tail_nonzero}|stream_read={stream_bytes}|merkle={merkle_hex}|merkle_match={}|sectors_match={sectors_match}/{}|fingerprint_upper={:032x}|fingerprint_lower={:032x}|fingerprint_equal={}|keyed_sum61={}|buckets_nonzero={buckets_nonzero}|first_bucket={first_bucket}|windows={}|cap={cap}|verdict={}|secs={}|float_used=0|json=0",
        kv(&line, "L").unwrap_or(""),
        kv(&line, "sector").unwrap_or(""),
        c.rows,
        c.entries,
        c.diag,
        c.upper,
        c.lower,
        c.not_ascending,
        c.out_of_range,
        c.zero_z,
        c.positive_off,
        c.row_sum_nonzero,
        c.zero_weight,
        c.missing_diag,
        c.sum_w,
        expected.map_or("-".to_string(), |v| v.to_string()),
        c.flats,
        join_list(&c.flat_w),
        join_list(&c.flat_rows),
        c.flat_off,
        c.max_cnt,
        c.max_w,
        c.min_z,
        c.max_z,
        c.max_abs_v,
        c.used_rooms,
        c.trailing_rooms,
        c.trailing_nonzero,
        c.odd_bytes,
        u8::from(merkle_ok),
        st.files.len(),
        w.prod_upper,
        w.prod_lower,
        u8::from(w.prod_upper == w.prod_lower),
        w.sum61,
        w.win.start.len(),
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
            println!("REVIEW_READER|verdict=FAIL|reason={e}|json=0");
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sha_hex(d: &[u8]) -> String {
        let t = ShaTables::new();
        let mut s = Sha::new(&t);
        s.update(d);
        s.hex()
    }

    #[test]
    fn sha256_known_answers() {
        assert_eq!(sha_hex(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
        assert_eq!(sha_hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
        assert_eq!(sha_hex(&vec![b'a'; 1_000_000]), "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
        // Split updates give the same digest.
        let t = ShaTables::new();
        let d = vec![b'a'; 1_000_000];
        let mut s = Sha::new(&t);
        let mut p = 0;
        let mut step = 1;
        while p < d.len() {
            let e = (p + step).min(d.len());
            s.update(&d[p..e]);
            p = e;
            step = step * 3 % 977 + 1;
        }
        assert_eq!(s.hex(), "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    }

    #[test]
    fn siphash_known_answer() {
        let k0 = u64::from_le_bytes([0, 1, 2, 3, 4, 5, 6, 7]);
        let k1 = u64::from_le_bytes([8, 9, 10, 11, 12, 13, 14, 15]);
        let m: Vec<u8> = (0u8..15).collect();
        assert_eq!(sip_bytes(k0, k1, &m), 0xa129_ca61_49be_45e5);
        let mut b = Vec::new();
        for w in [5u64, 123_456_789, u64::MAX - 3] {
            b.extend_from_slice(&w.to_le_bytes());
        }
        assert_eq!(sip_bytes(k0, k1, &b), sip3(k0, k1, 5, 123_456_789, u64::MAX - 3));
    }

    #[test]
    fn mul127_matches_shift_and_add() {
        let slow = |mut a: u128, mut b: u128| {
            let mut r = 0u128;
            while b > 0 {
                if b & 1 == 1 {
                    r = red127(r + a);
                }
                a = red127((a << 1 & P127) | a >> 126);
                b >>= 1;
            }
            r
        };
        let mut x = 0x1234_5678_9abc_def0_1122_3344_5566_7788u128 & P127;
        let mut y = 0x0fed_cba9_8765_4321_8877_6655_4433_2211u128 & P127;
        for _ in 0..2000 {
            assert_eq!(mul127(x, y), slow(x, y));
            x = red127(mul127(x, x) + 3);
            y = red127(mul127(y, x) + 7);
        }
        assert_eq!(mul127(P127 - 1, P127 - 1), 1);
        assert_eq!(mul127(1, P127 - 1), P127 - 1);
    }

    #[test]
    fn encode_is_injective_on_the_edges() {
        let mut seen = std::collections::HashSet::new();
        for lo in [0u32, 1, 45_508_079, u32::MAX] {
            for hi in [1u32, 2, 45_508_079, 0x7FFF_FFFF] {
                for v in [i64::MIN, i64::MIN + 1, -2, -1, 0, 1, 2, i64::MAX] {
                    assert!(seen.insert(encode(lo, hi, v)));
                    assert!(encode(lo, hi, v) < (1u128 << 127));
                }
            }
        }
    }

    #[test]
    fn roots_give_the_standard_constants() {
        let t = ShaTables::new();
        assert_eq!(t.k[0], 0x428a_2f98);
        assert_eq!(t.k[63], 0xc671_78f2);
        assert_eq!(t.h0[0], 0x6a09_e667);
        assert_eq!(t.h0[7], 0x5be0_cd19);
    }

    #[test]
    fn windows_close_like_the_rule() {
        let mut w = Windows::new(5);
        for (h, c) in [(0u64, 3u64), (1, 2), (2, 1), (3, 9), (4, 0), (5, 5)] {
            w.admit(h, c);
        }
        // Row 3 alone overfills its window, so the empty row 4 closes it, as in allpairs' admit.
        assert_eq!(w.start, vec![0, 2, 3, 4]);
        assert_eq!(w.upper, vec![5, 1, 9, 5]);
    }
}
