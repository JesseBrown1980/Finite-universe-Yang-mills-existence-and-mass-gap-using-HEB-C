//! Read side of a `ymroom build` stream, for tools other than roomschur and roomjump, which keep
//! their own pinned copies. Every pass recomputes the 16 MiB chunk merkle of the payload and fails
//! if it differs from the header's. Integer-only, json=0.
//!
//! Include with `#[path]` next to `segio` and `sha`, as roomschur does.

use crate::{segio, sha};
use std::io::{Read, Seek, SeekFrom};

const CHUNK: usize = 64 * 1_048_576;
const LEAF: usize = 16 * 1_048_576;

pub struct Hdr {
    pub n: usize,
    pub payload: u64,
    pub merkle: String,
    pub lattice: String,
    pub sector: String,
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

pub fn read_hdr(dev: &mut segio::Dev, off: u64) -> Result<Hdr, String> {
    let mut blk = vec![0u8; 4096];
    dev.seek(SeekFrom::Start(off)).map_err(|e| format!("seek: {e}"))?;
    dev.read_exact(&mut blk).map_err(|e| format!("read header: {e}"))?;
    let end = blk.iter().position(|&b| b == b'\n').ok_or("no header line")?;
    let line = String::from_utf8_lossy(&blk[..end]).to_string();
    if !line.starts_with("YMROOMHDR|") || field(&line, "w_self_adjoint=") != Some("PASS") {
        return Err("not a YMROOMHDR stream with w_self_adjoint=PASS".into());
    }
    let num = |k: &str| field(&line, k).and_then(|v| v.parse::<u64>().ok()).ok_or_else(|| format!("missing {k}"));
    let text = |k: &str| field(&line, k).unwrap_or("").to_string();
    Ok(Hdr { n: usize::try_from(num("n=")?).map_err(|_| "n")?, payload: num("payload_bytes=")?, merkle: text("payload_merkle="), lattice: text("L="), sector: text("sector=") })
}

/// One row: weight, magnetic number, and its nonzero entries with j ascending, diagonal included.
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

/// Calls `f(h, row)` for every row in index order. A reader thread reads and hashes ahead.
pub fn stream<F: FnMut(usize, &Row)>(dev: &mut segio::Dev, off: u64, hdr: &Hdr, mut f: F) -> Result<(), String> {
    dev.seek(SeekFrom::Start(off + 4096)).map_err(|e| format!("seek: {e}"))?;
    let payload = hdr.payload;
    let merkle = std::thread::scope(|sc| -> Result<String, String> {
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
        for msg in rx {
            let (buf, hx) = msg?;
            read += buf.len() as u64;
            shas.extend_from_slice(hx.as_bytes());
            carry.extend_from_slice(&buf);
            drop(buf);
            let mut p = 0usize;
            while h < hdr.n && p + 8 <= carry.len() {
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
            carry.drain(..p);
        }
        if read != payload {
            return Err(format!("stream read {read} of {payload} bytes"));
        }
        if h != hdr.n {
            return Err(format!("stream ended at row {h} of {}", hdr.n));
        }
        Ok(sha::sha256_hex(&shas))
    })?;
    if merkle != hdr.merkle {
        return Err(format!("payload merkle mismatch: header {} stream {merkle}", hdr.merkle));
    }
    Ok(())
}

/// A row for `write_test_stream`: weight, magnetic number, entries.
#[cfg(test)]
pub type TestRow = (u32, u16, Vec<(u32, i32)>);

/// Writes a small stream in the `ymroom build` layout, for unit tests.
#[cfg(test)]
pub fn write_test_stream(path: &std::path::Path, rows: &[TestRow]) {
    let mut payload = Vec::new();
    for (w, mag, ent) in rows {
        payload.extend_from_slice(&w.to_le_bytes());
        payload.extend_from_slice(&mag.to_le_bytes());
        payload.extend_from_slice(&u16::try_from(ent.len()).unwrap().to_le_bytes());
        for (j, z) in ent {
            payload.extend_from_slice(&j.to_le_bytes());
            payload.extend_from_slice(&z.to_le_bytes());
        }
    }
    let mut shas = String::new();
    for c in payload.chunks(LEAF) {
        shas.push_str(&sha::sha256_hex(c));
    }
    let line = format!(
        "YMROOMHDR|L=1x{}|sector=Sx+Sy+|n={}|payload_bytes={}|payload_merkle={}|w_self_adjoint=PASS|json=0\n",
        rows.len(),
        rows.len(),
        payload.len(),
        sha::sha256_hex(shas.as_bytes())
    );
    let mut bytes = line.into_bytes();
    bytes.resize(4096, 0);
    bytes.extend_from_slice(&payload);
    std::fs::write(path, bytes).unwrap();
}
