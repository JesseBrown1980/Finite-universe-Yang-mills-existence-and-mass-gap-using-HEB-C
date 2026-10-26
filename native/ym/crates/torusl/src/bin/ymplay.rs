//! Play, don't build (kernel-pump principle) for the zero-momentum sectors.
//!
//!   ymplay keys LX LY SX SY RESIDUE MODULUS OUT
//!       stream one residue class of the gauge-fixed space and write the sorted
//!       representative keys of sector (SX, SY) (u64 little endian)
//!   ymplay merge OUT IN...
//!       merge disjoint sorted key files into one address file
//!   ymplay matrix LX LY SX SY ADDR OUT
//!       generate every row on demand from the address file (O(1) key lookup)
//!       and write it in the ymsec matrix format, for byte comparison with a
//!       stored matrix
//!   ymplay row LX LY SX SY ADDR I
//!       generate one row on demand
//! Integer-only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::io::{Read, Write};
use torusl::play::{play_row, Address, Ctx};
use torusl::{Lat, G};

fn read_keys(path: &str) -> Vec<u64> {
    let mut b = Vec::new();
    std::fs::File::open(path).and_then(|mut f| f.read_to_end(&mut b)).unwrap_or_else(|e| {
        println!("YMPLAY|error=read:{e}|json=0");
        std::process::exit(1)
    });
    if b.len() % 8 != 0 {
        println!("YMPLAY|error=truncated_key_file|file={path}|json=0");
        std::process::exit(2);
    }
    b.chunks_exact(8).map(|c| u64::from_le_bytes([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]])).collect()
}

fn write_keys(path: &str, keys: &[u64]) {
    let mut out = std::io::BufWriter::new(std::fs::File::create(path).unwrap_or_else(|e| {
        println!("YMPLAY|error=write:{e}|json=0");
        std::process::exit(1)
    }));
    for k in keys {
        if out.write_all(&k.to_le_bytes()).is_err() {
            std::process::exit(1);
        }
    }
    let _ = out.flush();
}

fn arg<T: std::str::FromStr>(a: &[String], i: usize) -> T {
    a.get(i).and_then(|v| v.parse().ok()).unwrap_or_else(|| {
        println!("YMPLAY|error=bad_arguments|json=0");
        std::process::exit(1)
    })
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
        Some("matrix") | Some("row") => {
            let (lx, ly, sx, sy): (usize, usize, i64, i64) = (arg(&a, 2), arg(&a, 3), arg(&a, 4), arg(&a, 5));
            let g = G::new();
            let lat = Lat::new(lx, ly);
            let ctx = Ctx::new(&g, &lat);
            let mut s = ctx.scratch();
            let space = 6u64.pow(u32::try_from(lat.free.len()).unwrap_or(0));
            let addr = Address::checked(read_keys(&a[6]), space).unwrap_or_else(|e| {
                println!("YMPLAY|error={e}|json=0");
                std::process::exit(2)
            });
            let n = addr.keys.len();
            if a[1] == "row" {
                let i: usize = arg(&a, 7);
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
            let mut out = std::io::BufWriter::new(std::fs::File::create(&a[7]).unwrap_or_else(|_| std::process::exit(1)));
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
            println!("YMPLAY_MATRIX|L={lx}x{ly}|sector={sx},{sy}|states={n}|nnz={nnz}|write={}|ms={}|json=0", if ok { "ok" } else { "failed" }, t0.elapsed().as_millis());
        }
        _ => {
            println!("YMPLAY|error=usage|json=0");
            std::process::exit(1);
        }
    }
}
