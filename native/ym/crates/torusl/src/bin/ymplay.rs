//! Play, don't build (kernel-pump principle) for the zero-momentum sectors.
//!
//!   ymplay keys LX LY SX SY RESIDUE MODULUS OUT
//!       stream one residue class of the gauge-fixed space and write the sorted
//!       representative keys of sector (SX, SY) (u64 little endian)
//!   ymplay merge OUT IN...
//!       merge disjoint sorted key files into one address file
//!   ymplay manifest LX LY SX SY ADDR STATES OUT
//!       write the address manifest: lattice, sector, configuration space, key
//!       encoding, expected state count STATES (from an independent route: the
//!       character formula of ymstream, or ymsec), byte length 8*STATES, the
//!       file's SHA-256 and the SHA-256 of this executable. Refused unless the
//!       file holds exactly STATES keys.
//!   ymplay matrix LX LY SX SY ADDR MANIFEST OUT
//!       check ADDR against MANIFEST (scope, count, length, digest), then
//!       generate every row on demand (exact key lookup) and write it in the
//!       ymsec matrix format, for byte comparison with a stored matrix
//!   ymplay row LX LY SX SY ADDR MANIFEST I
//!       the same checks, then one row
//! Every failure exits 2.
//! Integer-only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::io::{Read, Write};
use torusl::play::{play_row, Address, Ctx};
use torusl::{Lat, G};

fn fail(e: &str) -> ! {
    println!("YMPLAY|error={e}|json=0");
    std::process::exit(2)
}

fn read_bytes(path: &str) -> Vec<u8> {
    let mut b = Vec::new();
    std::fs::File::open(path).and_then(|mut f| f.read_to_end(&mut b)).unwrap_or_else(|e| fail(&format!("read:{e}")));
    b
}

#[allow(clippy::too_many_arguments)]
fn manifest_line(lx: usize, ly: usize, sx: i64, sy: i64, space: u64, states: usize, sha: &str, tool: &str) -> String {
    format!(
        "YMPLAY_MANIFEST|L={lx}x{ly}|sector={sx},{sy}|space={space}|encoding=u64le_sorted_unique|states={states}|bytes={}|sha256={sha}|ymplay_sha256={tool}|json=0",
        8 * states
    )
}

/// The address file must match its manifest exactly.
fn check_manifest(man: &str, addr_bytes: &[u8], lx: usize, ly: usize, sx: i64, sy: i64, space: u64) {
    let text = String::from_utf8(read_bytes(man)).unwrap_or_else(|_| fail("manifest_not_utf8"));
    let lines: Vec<&str> = text.lines().filter(|l| l.starts_with("YMPLAY_MANIFEST|")).collect();
    if lines.len() != 1 {
        fail("manifest_needs_exactly_one_record");
    }
    let f: std::collections::BTreeMap<&str, &str> = lines[0].split('|').skip(1).filter_map(|p| p.split_once('=')).collect();
    let get = |k: &str| *f.get(k).unwrap_or_else(|| fail(&format!("manifest_missing_{k}")));
    let states: usize = get("states").parse().unwrap_or_else(|_| fail("manifest_states"));
    if get("L") != format!("{lx}x{ly}") || get("sector") != format!("{sx},{sy}") || get("space") != space.to_string() {
        fail("manifest_scope_mismatch");
    }
    if get("encoding") != "u64le_sorted_unique" {
        fail("manifest_encoding");
    }
    if get("bytes") != (8 * states).to_string() || addr_bytes.len() != 8 * states {
        fail("address_length_not_manifest_count");
    }
    if get("sha256") != torusl::sha::sha256_hex(addr_bytes) {
        fail("address_digest_mismatch");
    }
}

fn read_keys(path: &str) -> Vec<u64> {
    let mut b = Vec::new();
    std::fs::File::open(path).and_then(|mut f| f.read_to_end(&mut b)).unwrap_or_else(|e| fail(&format!("read:{e}")));
    if b.len() % 8 != 0 {
        fail(&format!("truncated_key_file|file={path}"));
    }
    b.chunks_exact(8).map(|c| u64::from_le_bytes([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]])).collect()
}

fn write_keys(path: &str, keys: &[u64]) {
    let mut out = std::io::BufWriter::new(std::fs::File::create(path).unwrap_or_else(|e| fail(&format!("write:{e}"))));
    for k in keys {
        if out.write_all(&k.to_le_bytes()).is_err() {
            fail("write_keys");
        }
    }
    if out.flush().is_err() {
        fail("write_keys_flush");
    }
}

fn arg<T: std::str::FromStr>(a: &[String], i: usize) -> T {
    a.get(i).and_then(|v| v.parse().ok()).unwrap_or_else(|| fail("bad_arguments"))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let t0 = std::time::Instant::now();
    match a.get(1).map(String::as_str) {
        Some("keys") => {
            let (lx, ly, sx, sy): (usize, usize, i64, i64) = (arg(&a, 2), arg(&a, 3), arg(&a, 4), arg(&a, 5));
            let (res, m): (u64, u64) = (arg(&a, 6), arg(&a, 7));
            let g = G::new();
            let lat = Lat::new(lx, ly);
            let ctx = Ctx::new(&g, &lat);
            let mut s = ctx.scratch();
            let total = 6u64.pow(u32::try_from(lat.free.len()).unwrap_or(0));
            let mut keys = Vec::new();
            for id in (res..total).step_by(usize::try_from(m).unwrap_or(1)) {
                let q = ctx.decode(id);
                // least member of its conjugation class
                let is_min = (1..6).all(|c| {
                    let row = &ctx.conj[c];
                    q.iter().enumerate().map(|(i, &v)| u64::from(row[v as usize]) * ctx.pow6[i]).sum::<u64>() >= id
                });
                if is_min && ctx.representative(id, sx, sy, &mut s).is_some() {
                    keys.push(id);
                }
            }
            write_keys(&a[8], &keys);
            println!("YMPLAY_KEYS|L={lx}x{ly}|sector={sx},{sy}|class={res}/{m}|keys={}|ms={}|json=0", keys.len(), t0.elapsed().as_millis());
        }
        Some("merge") => {
            let mut all: Vec<u64> = a[3..].iter().flat_map(|p| read_keys(p)).collect();
            let n = all.len();
            all.sort_unstable();
            all.dedup();
            if all.len() != n {
                println!("YMPLAY|error=overlapping_key_files|json=0");
                std::process::exit(2);
            }
            write_keys(&a[2], &all);
            println!("YMPLAY_MERGE|inputs={}|keys={}|json=0", a.len() - 3, all.len());
        }
        Some("manifest") => {
            let (lx, ly, sx, sy): (usize, usize, i64, i64) = (arg(&a, 2), arg(&a, 3), arg(&a, 4), arg(&a, 5));
            let states: usize = arg(&a, 7);
            let lat = Lat::new(lx, ly);
            let space = 6u64.pow(u32::try_from(lat.free.len()).unwrap_or(0));
            let bytes = read_bytes(&a[6]);
            if bytes.len() != 8 * states {
                fail(&format!("address_holds_{}_bytes_expected_{}", bytes.len(), 8 * states));
            }
            let keys = read_keys(&a[6]);
            if let Err(e) = Address::checked(keys, space) {
                fail(&e);
            }
            let exe = std::env::current_exe().map(|p| torusl::sha::sha256_hex(&read_bytes(&p.display().to_string()))).unwrap_or_default();
            let line = manifest_line(lx, ly, sx, sy, space, states, &torusl::sha::sha256_hex(&bytes), &exe);
            std::fs::write(&a[8], format!("{line}\n")).unwrap_or_else(|e| fail(&format!("write:{e}")));
            println!("{line}");
        }
        Some("matrix") | Some("row") => {
            let (lx, ly, sx, sy): (usize, usize, i64, i64) = (arg(&a, 2), arg(&a, 3), arg(&a, 4), arg(&a, 5));
            let g = G::new();
            let lat = Lat::new(lx, ly);
            let ctx = Ctx::new(&g, &lat);
            let mut s = ctx.scratch();
            let space = 6u64.pow(u32::try_from(lat.free.len()).unwrap_or(0));
            check_manifest(a.get(7).map(String::as_str).unwrap_or_else(|| fail("usage")), &read_bytes(&a[6]), lx, ly, sx, sy, space);
            let addr = Address::checked(read_keys(&a[6]), space).unwrap_or_else(|e| fail(&e));
            let n = addr.keys.len();
            if a[1] == "row" {
                let i: usize = arg(&a, 8);
                if i >= n {
                    fail("row_index_out_of_range");
                }
                let (row, mag, w) = play_row(&ctx, &addr, i, sx, sy, &mut s).unwrap_or_else(|e| {
                    println!("YMPLAY|error={e}|json=0");
                    std::process::exit(2)
                });
                let r = row.iter().map(|(c, z)| format!("{c}:{z}")).collect::<Vec<_>>().join(",");
                println!("YMPLAY_ROW|L={lx}x{ly}|sector={sx},{sy}|i={i}|key={}|weight={w}|magnetic={mag}|entries={r}|ms={}|json=0", addr.keys[i], t0.elapsed().as_millis());
                return;
            }
            let mut rows = Vec::with_capacity(n);
            let mut wts = Vec::with_capacity(n);
            let mut mags = Vec::with_capacity(n);
            for i in 0..n {
                let (row, mag, w) = play_row(&ctx, &addr, i, sx, sy, &mut s).unwrap_or_else(|e| {
                    println!("YMPLAY|error={e}|json=0");
                    std::process::exit(2)
                });
                rows.push(row);
                mags.push(mag);
                wts.push(w);
            }
            let mut out = std::io::BufWriter::new(std::fs::File::create(a.get(8).map(String::as_str).unwrap_or_else(|| fail("usage"))).unwrap_or_else(|e| fail(&format!("write:{e}"))));
            let join = |v: &[i64]| v.iter().map(i64::to_string).collect::<Vec<_>>().join(" ");
            let mut ok = writeln!(out, "{n}").is_ok();
            ok &= writeln!(out, "{}", join(&wts)).is_ok();
            ok &= writeln!(out, "{}", join(&mags)).is_ok();
            let mut nnz = 0usize;
            for (i, row) in rows.iter().enumerate() {
                for &(c, z) in row {
                    nnz += 1;
                    if c >= i {
                        ok &= writeln!(out, "{i} {c} {z}").is_ok();
                    }
                }
            }
            ok &= out.flush().is_ok();
            if !ok {
                fail("matrix_write_failed");
            }
            println!("YMPLAY_MATRIX|L={lx}x{ly}|sector={sx},{sy}|states={n}|nnz={nnz}|write=ok|ms={}|json=0", t0.elapsed().as_millis());
        }
        _ => fail("usage"),
    }
}
