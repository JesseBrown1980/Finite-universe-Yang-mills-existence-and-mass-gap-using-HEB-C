//! Room-backed builder for the zero-momentum Sx+Sy+ sector operator (Host8
//! rooms). Integer-only, Rust 1.81, json=0.
//!
//! Same operator as `ymsec LX LY 1 1`, built without its 6^k tables:
//!   pass A  streams the gauge-fixed space (the `ymstream` scan, one residue
//!           class per worker) and keeps every sector representative (least key
//!           of its G-orbit) with its weight and magnetic number;
//!   pass B  rebuilds each representative's electric row in index order, maps
//!           every move target to its representative index by binary search over
//!           the sorted keys, and writes the rows as 8-byte rooms.
//! In Sx+Sy+ every character is trivial, so no orbit is dropped and every sign
//! is +1; the row is diag 3*nl minus one per move into each target orbit, exactly
//! as `ymsec` builds it.
//!
//! Room layout (little-endian, one row after another in index order):
//!   header room  w:u32 | mag:u16 | cnt:u16          (cnt entries follow)
//!   entry room   j:u32 | z:i32                       (row's nonzero entries, j ascending)
//! The stream starts with a 4096-byte block holding one HBP line (zero padded)
//! and is zero padded to a multiple of 1 MiB.
//!
//! usage:
//!   ymroom text  LX LY OUT_MATRIX                      ymsec-format text (identity gate)
//!   ymroom passa LX LY OUT_PASSA                        pass A only -> rep table file
//!   ymroom build LX LY PASSA KEYS_ROOMS DEV OFFSET      pass B -> rooms on DEV at OFFSET
//! WORKERS=n threads (records identical for any n).
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::BTreeMap;
use std::io::{Read, Seek, SeekFrom, Write};
use torusl::sha::sha256_hex;
use torusl::{Lat, G, TRANS};

struct Ctx<'a> {
    g: &'a G,
    lat: &'a Lat,
    dest: Vec<Vec<(usize, bool)>>,
    pow6: Vec<u64>,
    conj: [[u8; 6]; 6],
}

// copied unchanged from ymstream.rs (build_ops / key / apply)
fn build_ops(lat: &Lat) -> Vec<Vec<(usize, bool)>> {
    let (lx, ly, n) = (lat.lx, lat.ly, lat.n);
    let mut dest = Vec::new();
    for p in 0..4u8 {
        for tx in 0..lx {
            for ty in 0..ly {
                let fx = p == 1 || p == 3;
                let fy = p == 2 || p == 3;
                let mut d = vec![(0usize, false); 2 * n];
                for x in 0..lx {
                    for y in 0..ly {
                        let s = lat.site(x, y);
                        let px = if fx { (lx - x) % lx } else { x };
                        let py = if fy { (ly - y) % ly } else { y };
                        let dxx = if fx { (px + lx - 1) % lx } else { px };
                        let dyy = if fy { (py + ly - 1) % ly } else { py };
                        d[s] = (lat.site((dxx + tx) % lx, (py + ty) % ly), fx);
                        d[n + s] = (n + lat.site((px + tx) % lx, (dyy + ty) % ly), fy);
                    }
                }
                dest.push(d);
            }
        }
    }
    dest
}

impl Ctx<'_> {
    fn key(&self, links: &[u8], h: &mut [u8], q: &mut [u8]) -> u64 {
        let (g, lat) = (self.g, self.lat);
        h[0] = 0;
        for &e in &lat.tree {
            let (t, hd) = lat.edges[e];
            h[hd] = g.m(h[t], links[e]);
        }
        for (i, &e) in lat.free.iter().enumerate() {
            let (t, hd) = lat.edges[e];
            q[i] = g.m(g.m(h[t], links[e]), g.i(h[hd]));
        }
        let mut best = u64::MAX;
        for row in &self.conj {
            let mut id = 0u64;
            for (i, &v) in q.iter().enumerate() {
                id += u64::from(row[v as usize]) * self.pow6[i];
            }
            best = best.min(id);
        }
        best
    }
    fn apply(&self, op: usize, u: &[u8], out: &mut [u8]) {
        for (l, &(d, inv)) in self.dest[op].iter().enumerate() {
            out[d] = if inv { self.g.i(u[l]) } else { u[l] };
        }
    }
    fn decode(&self, mut id: u64, q: &mut [u8]) {
        for v in q.iter_mut() {
            *v = (id % 6) as u8;
            id /= 6;
        }
    }
}

/// one representative: (key, weight, magnetic number)
type Rep = (u64, i64, i64);

fn pass_a(ctx: &Ctx, start: u64, step: u64, total: u64) -> Vec<Rep> {
    let lat = ctx.lat;
    let k = lat.free.len();
    let nops = ctx.dest.len();
    let (mut h, mut qb, mut buf) = (vec![0u8; lat.n], vec![0u8; k], vec![0u8; 2 * lat.n]);
    let mut q = vec![0u8; k];
    let mut out = Vec::new();
    for id in (start..total).step_by(usize::try_from(step).unwrap_or(1)) {
        ctx.decode(id, &mut q);
        let mut is_min = true;
        for row in ctx.conj.iter().skip(1) {
            let mut cid = 0u64;
            for (i, &v) in q.iter().enumerate() {
                cid += u64::from(row[v as usize]) * ctx.pow6[i];
            }
            if cid < id {
                is_min = false;
                break;
            }
        }
        if !is_min {
            continue;
        }
        let raw = lat.representative(&q);
        let mut is_rep = true;
        let mut stab = 0i64;
        for o in 0..nops {
            ctx.apply(o, &raw, &mut buf);
            let kk = ctx.key(&buf, &mut h, &mut qb);
            if kk < id {
                is_rep = false;
                break;
            }
            if kk == id {
                stab += 1;
            }
        }
        if !is_rep {
            continue;
        }
        // distinct gauge orbits in the G-orbit = |G| / |stabiliser| (ymsec: img.len())
        let gsz = i64::try_from(nops).unwrap_or(0);
        let w = (gsz / stab) * lat.weight(ctx.g, &q);
        out.push((id, w, lat.magnetic(ctx.g, &raw)));
    }
    out
}

fn reps_all(ctx: &Ctx, workers: u64) -> Vec<Rep> {
    let total = ctx.pow6.last().copied().unwrap_or(1) * 6;
    let mut all: Vec<Rep> = std::thread::scope(|sc| {
        let hs: Vec<_> = (0..workers).map(|w| sc.spawn(move || pass_a(ctx, w, workers, total))).collect();
        hs.into_iter().flat_map(|h| h.join().unwrap_or_else(|_| std::process::exit(2))).collect()
    });
    all.sort_unstable();
    all
}

/// electric row of representative i: (column, coefficient), ascending, nonzero
fn row(ctx: &Ctx, keys: &[u64], i: usize, h: &mut [u8], qb: &mut [u8], q: &mut [u8], b2: &mut [u8]) -> Vec<(u32, i64)> {
    let (g, lat) = (ctx.g, ctx.lat);
    let nl = 2 * lat.n;
    ctx.decode(keys[i], q);
    let raw = lat.representative(q);
    let mut r: BTreeMap<u32, i64> = BTreeMap::new();
    *r.entry(u32::try_from(i).unwrap_or(u32::MAX)).or_insert(0) += 3 * i64::try_from(nl).unwrap_or(0);
    let mut mv = raw.clone();
    for e in 0..nl {
        for &t in &TRANS {
            mv.copy_from_slice(&raw);
            mv[e] = g.m(t, mv[e]);
            let mut best = u64::MAX;
            for o in 0..ctx.dest.len() {
                ctx.apply(o, &mv, b2);
                best = best.min(ctx.key(b2, h, qb));
            }
            let j = keys.binary_search(&best).unwrap_or_else(|_| {
                println!("YMROOM|error=target_not_a_representative|row={i}|key={best}|json=0");
                std::process::exit(2)
            });
            *r.entry(u32::try_from(j).unwrap_or(u32::MAX)).or_insert(0) -= 1;
        }
    }
    r.into_iter().filter(|&(_, v)| v != 0).collect()
}

fn rows_chunk(ctx: &Ctx, keys: &[u64], lo: usize, hi: usize, workers: usize) -> Vec<Vec<(u32, i64)>> {
    let lat = ctx.lat;
    let per = (hi - lo).div_ceil(workers).max(1);
    std::thread::scope(|sc| {
        let hs: Vec<_> = (0..workers)
            .map(|w| {
                let (a, b) = ((lo + w * per).min(hi), (lo + (w + 1) * per).min(hi));
                sc.spawn(move || {
                    let k = lat.free.len();
                    let (mut h, mut qb, mut q, mut b2) = (vec![0u8; lat.n], vec![0u8; k], vec![0u8; k], vec![0u8; 2 * lat.n]);
                    (a..b).map(|i| row(ctx, keys, i, &mut h, &mut qb, &mut q, &mut b2)).collect::<Vec<_>>()
                })
            })
            .collect();
        hs.into_iter().flat_map(|h| h.join().unwrap_or_else(|_| std::process::exit(2))).collect()
    })
}

fn die(msg: &str) -> ! {
    println!("YMROOM|error={msg}|json=0");
    std::process::exit(1)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        die("usage");
    }
    let (lx, ly): (usize, usize) = (a[2].parse().unwrap_or(0), a[3].parse().unwrap_or(0));
    if !(2..=4).contains(&lx) || !(2..=4).contains(&ly) || lx * ly > 12 {
        die("bad_lattice");
    }
    let t0 = std::time::Instant::now();
    let g = G::new();
    let lat = Lat::new(lx, ly);
    let k = lat.free.len();
    let mut conj = [[0u8; 6]; 6];
    for c in 0..6u8 {
        for x in 0..6u8 {
            conj[c as usize][x as usize] = g.m(g.m(c, x), g.i(c));
        }
    }
    let ctx = Ctx { g: &g, lat: &lat, dest: build_ops(&lat), pow6: (0..k).map(|i| 6u64.pow(u32::try_from(i).unwrap_or(0))).collect(), conj };
    let workers: usize = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
    let nl = 2 * lat.n;
    match a[1].as_str() {
        "text" => {
            let reps = reps_all(&ctx, workers as u64);
            let keys: Vec<u64> = reps.iter().map(|r| r.0).collect();
            let rows = rows_chunk(&ctx, &keys, 0, keys.len(), workers);
            let mut out = std::io::BufWriter::new(std::fs::File::create(&a[4]).unwrap_or_else(|_| die("create")));
            let join = |v: Vec<i64>| v.iter().map(i64::to_string).collect::<Vec<_>>().join(" ");
            let mut ok = writeln!(out, "{}", keys.len()).is_ok();
            ok &= writeln!(out, "{}", join(reps.iter().map(|r| r.1).collect())).is_ok();
            ok &= writeln!(out, "{}", join(reps.iter().map(|r| r.2).collect())).is_ok();
            for (i, r) in rows.iter().enumerate() {
                for &(c, z) in r {
                    if c as usize >= i {
                        ok &= writeln!(out, "{i} {c} {z}").is_ok();
                    }
                }
            }
            ok &= out.flush().is_ok();
            println!("YMROOM_TEXT|L={lx}x{ly}|sector=Sx+Sy+|n={}|write={}|ms={}|json=0", keys.len(), u8::from(ok), t0.elapsed().as_millis());
        }
        "passa" => {
            let reps = reps_all(&ctx, workers as u64);
            let mut bytes = Vec::with_capacity(reps.len() * 16);
            for &(key, w, m) in &reps {
                bytes.extend_from_slice(&key.to_le_bytes());
                bytes.extend_from_slice(&u32::try_from(w).unwrap_or_else(|_| die("weight_range")).to_le_bytes());
                bytes.extend_from_slice(&u32::try_from(m).unwrap_or_else(|_| die("mag_range")).to_le_bytes());
            }
            std::fs::write(&a[4], &bytes).unwrap_or_else(|_| die("write_passa"));
            let flat = reps.iter().filter(|r| r.2 == 0).count();
            println!(
                "YMROOM_PASSA|L={lx}x{ly}|sector=Sx+Sy+|states={}|flat_states={flat}|bytes={}|sha256={}|workers={workers}|ms={}|json=0",
                reps.len(),
                bytes.len(),
                sha256_hex(&bytes),
                t0.elapsed().as_millis()
            );
        }
        "build" => {
            if a.len() < 8 {
                die("usage_build");
            }
            let pa = std::fs::read(&a[4]).unwrap_or_else(|_| die("read_passa"));
            let n = pa.len() / 16;
            let mut keys = Vec::with_capacity(n);
            let mut wm = Vec::with_capacity(n);
            for c in pa.chunks_exact(16) {
                keys.push(u64::from_le_bytes(c[0..8].try_into().unwrap_or([0; 8])));
                wm.push((u32::from_le_bytes(c[8..12].try_into().unwrap_or([0; 4])), u32::from_le_bytes(c[12..16].try_into().unwrap_or([0; 4]))));
            }
            if keys.windows(2).any(|p| p[0] >= p[1]) {
                die("passa_not_sorted");
            }
            // keys into the room file: one 8-byte key per room, first n rooms
            let mut kf = std::fs::OpenOptions::new().read(true).write(true).open(&a[5]).unwrap_or_else(|_| die("open_keys_rooms"));
            let room_bytes = kf.metadata().map(|m| m.len()).unwrap_or(0);
            if room_bytes < 8 * n as u64 {
                die("keys_rooms_too_small");
            }
            let kb: Vec<u8> = keys.iter().flat_map(|k| k.to_le_bytes()).collect();
            kf.write_all(&kb).unwrap_or_else(|_| die("write_keys_rooms"));
            kf.flush().unwrap_or_else(|_| die("flush_keys_rooms"));
            let keys_sha = sha256_hex(&kb);
            let offset: u64 = a[7].parse().unwrap_or_else(|_| die("bad_offset"));
            if offset % 1_048_576 != 0 {
                die("offset_not_1MiB_aligned");
            }
            let mut dev = std::fs::OpenOptions::new().read(true).write(true).open(&a[6]).unwrap_or_else(|_| die("open_dev"));
            dev.seek(SeekFrom::Start(offset + 4096)).unwrap_or_else(|_| die("seek_dev"));
            const MIB: usize = 1_048_576;
            let mut pend: Vec<u8> = Vec::with_capacity(64 * MIB);
            let mut written: u64 = 4096;
            let mut chunk_shas: Vec<u8> = Vec::new();
            let (mut rooms, mut entries) = (0u64, 0u64);
            let mut sa: u64 = 0; // W-self-adjointness: sum of H(i,j,w_i z) over i<j minus over i>j
            let mix = |i: u64, j: u64, v: i64| -> u64 {
                let mut x = i.wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ j.rotate_left(29) ^ (v as u64).wrapping_mul(0xBF58_476D_1CE4_E5B9);
                x ^= x >> 31;
                x.wrapping_mul(0x94D0_49BB_1331_11EB)
            };
            let chunk = 200_000usize;
            let mut last_report = std::time::Instant::now();
            let mut i0 = 0usize;
            while i0 < n {
                let i1 = (i0 + chunk).min(n);
                let rows = rows_chunk(&ctx, &keys, i0, i1, workers);
                for (d, r) in rows.iter().enumerate() {
                    let i = i0 + d;
                    let (w, m) = wm[i];
                    let cnt = u16::try_from(r.len()).unwrap_or_else(|_| die("row_too_long"));
                    pend.extend_from_slice(&w.to_le_bytes());
                    pend.extend_from_slice(&u16::try_from(m).unwrap_or_else(|_| die("mag_u16")).to_le_bytes());
                    pend.extend_from_slice(&cnt.to_le_bytes());
                    rooms += 1;
                    for &(j, z) in r {
                        pend.extend_from_slice(&j.to_le_bytes());
                        pend.extend_from_slice(&i32::try_from(z).unwrap_or_else(|_| die("coef_i32")).to_le_bytes());
                        rooms += 1;
                        entries += 1;
                        let (iu, ju) = (i as u64, u64::from(j));
                        let v = i64::from(w) * z;
                        match iu.cmp(&ju) {
                            std::cmp::Ordering::Less => sa = sa.wrapping_add(mix(iu, ju, v)),
                            std::cmp::Ordering::Greater => sa = sa.wrapping_sub(mix(ju, iu, v)),
                            std::cmp::Ordering::Equal => {}
                        }
                    }
                }
                let full = (pend.len() / (16 * MIB)) * (16 * MIB);
                if full > 0 {
                    for c in pend[..full].chunks(16 * MIB) {
                        chunk_shas.extend_from_slice(sha256_hex(c).as_bytes());
                    }
                    dev.write_all(&pend[..full]).unwrap_or_else(|_| die("write_dev"));
                    written += full as u64;
                    pend.drain(..full);
                }
                i0 = i1;
                if last_report.elapsed().as_secs() >= 60 {
                    last_report = std::time::Instant::now();
                    eprintln!("YMROOM_PROGRESS|rows={i0}/{n}|rooms={rooms}|bytes={written}|ms={}|json=0", t0.elapsed().as_millis());
                }
            }
            // tail: pad to 1 MiB
            let pad = (MIB - (pend.len() + 4096) % MIB) % MIB;
            pend.resize(pend.len() + pad, 0);
            for c in pend.chunks(16 * MIB) {
                chunk_shas.extend_from_slice(sha256_hex(c).as_bytes());
            }
            dev.write_all(&pend).unwrap_or_else(|_| die("write_dev_tail"));
            written += pend.len() as u64;
            let payload_merkle = sha256_hex(&chunk_shas);
            let hdr = format!(
                "YMROOMHDR|L={lx}x{ly}|sector=Sx+Sy+|n={n}|nl={nl}|rooms={rooms}|entries={entries}|payload_bytes={}|stream_bytes={written}|chunk=16MiB|payload_merkle={payload_merkle}|keys_sha256={keys_sha}|w_self_adjoint={}|json=0\n",
                written - 4096,
                if sa == 0 { "PASS" } else { "FAIL" }
            );
            let mut blk = hdr.clone().into_bytes();
            blk.resize(4096, 0);
            dev.seek(SeekFrom::Start(offset)).unwrap_or_else(|_| die("seek_hdr"));
            dev.write_all(&blk).unwrap_or_else(|_| die("write_hdr"));
            dev.flush().unwrap_or_else(|_| die("flush_dev"));
            // read the header back (wrap-around / lost-write tripwire)
            let mut back = vec![0u8; 4096];
            dev.seek(SeekFrom::Start(offset)).unwrap_or_else(|_| die("seek_back"));
            dev.read_exact(&mut back).unwrap_or_else(|_| die("read_back"));
            print!("{hdr}");
            println!(
                "YMROOM_BUILD|dev={}|offset={offset}|header_readback={}|ms={}|json=0",
                a[6],
                if back == blk { "EXACT" } else { "MISMATCH" },
                t0.elapsed().as_millis()
            );
            if sa != 0 || back != blk {
                std::process::exit(2);
            }
        }
        _ => die("unknown_mode"),
    }
}
