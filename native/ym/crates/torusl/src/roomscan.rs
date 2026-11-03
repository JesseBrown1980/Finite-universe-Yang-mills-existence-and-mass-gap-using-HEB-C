//! Strict read side of a `ymroom build` stream. Like `roomio::stream`, it recomputes the 16 MiB chunk merkle of the payload
//! on every pass and fails if that differs from the header's. It also accounts for every payload byte: the rows, then
//! whatever follows the last row, which it counts and keeps none of, so its buffers stay at a few chunks and one row however
//! long the padding is. Integer-only, json=0.
//!
//! `roomio.rs` stays as it is, since recorded runs of other tools are pinned to it. Include this with `#[path]` next to
//! `segio` and `sha`.

use crate::{segio, sha};
use std::io::{Read, Seek, SeekFrom};

const CHUNK: usize = 64 * 1_048_576;
const LEAF: usize = 16 * 1_048_576;

/// Where a stream lies, and what its header says about it.
pub struct Layout<'a> {
    pub off: u64,
    pub n: usize,
    pub payload: u64,
    pub merkle: &'a str,
}

/// One row: weight, magnetic number, and its entries as stored.
pub struct Row<'a> {
    pub w: u32,
    pub mag: u16,
    ent: &'a [u8],
}

impl Row<'_> {
    pub fn entries(&self) -> impl Iterator<Item = (usize, i32)> + '_ {
        self.ent.chunks_exact(8).map(|e| {
            let j = u32::from_le_bytes([e[0], e[1], e[2], e[3]]);
            let z = i32::from_le_bytes([e[4], e[5], e[6], e[7]]);
            (j as usize, z)
        })
    }
}

#[cfg(test)]
impl Row<'static> {
    /// A row of no entries, for unit tests.
    pub fn empty(w: u32, mag: u16) -> Row<'static> {
        Row { w, mag, ent: &[] }
    }
}

/// What one whole pass found. `row_bytes + padding_bytes` is every payload byte read.
pub struct End {
    pub merkle: String,
    pub row_bytes: u64,
    pub padding_bytes: u64,
    pub padding_nonzero: u64,
}

fn nonzero(b: &[u8]) -> u64 {
    b.iter().filter(|&&x| x != 0).count() as u64
}

/// Calls `f(h, row)` for every row in index order. A reader thread reads and hashes ahead.
pub fn scan<F: FnMut(usize, &Row)>(dev: &mut segio::Dev, at: &Layout, mut f: F) -> Result<End, String> {
    let first = at.off.checked_add(4096).ok_or("offset")?;
    dev.seek(SeekFrom::Start(first)).map_err(|e| format!("seek: {e}"))?;
    let payload = at.payload;
    std::thread::scope(|sc| -> Result<End, String> {
        let (tx, rx) = std::sync::mpsc::sync_channel::<Result<(Vec<u8>, String), String>>(1);
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
        let mut row_bytes = 0u64;
        let mut padding_bytes = 0u64;
        let mut padding_nonzero = 0u64;
        for msg in rx {
            let (buf, hx) = msg?;
            read += buf.len() as u64;
            shas.extend_from_slice(hx.as_bytes());
            if h == at.n {
                padding_bytes += buf.len() as u64;
                padding_nonzero += nonzero(&buf);
                continue;
            }
            carry.extend_from_slice(&buf);
            drop(buf);
            let mut p = 0usize;
            while h < at.n && p + 8 <= carry.len() {
                let cnt = usize::from(u16::from_le_bytes([carry[p + 6], carry[p + 7]]));
                if p + 8 + 8 * cnt > carry.len() {
                    break;
                }
                let row = Row {
                    w: u32::from_le_bytes([carry[p], carry[p + 1], carry[p + 2], carry[p + 3]]),
                    mag: u16::from_le_bytes([carry[p + 4], carry[p + 5]]),
                    ent: &carry[p + 8..p + 8 + 8 * cnt],
                };
                f(h, &row);
                h += 1;
                p += 8 + 8 * cnt;
            }
            row_bytes += p as u64;
            carry.drain(..p);
            if h == at.n {
                padding_bytes += carry.len() as u64;
                padding_nonzero += nonzero(&carry);
                carry = Vec::new();
            }
        }
        if read != payload {
            return Err(format!("stream read {read} of {payload} bytes"));
        }
        if h != at.n {
            return Err(format!("stream ended at row {h} of {}", at.n));
        }
        let merkle = sha::sha256_hex(&shas);
        if merkle != at.merkle {
            return Err(format!("payload merkle mismatch: header {} stream {merkle}", at.merkle));
        }
        Ok(End { merkle, row_bytes, padding_bytes, padding_nonzero })
    })
}
