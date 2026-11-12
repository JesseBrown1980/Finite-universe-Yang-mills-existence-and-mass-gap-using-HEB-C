//! ym-residual-rooms V0. See SPEC-AND-PREDICTION.hbp (written before this file).
//! Integer only. std only. The room store is opened read-only and never written.
//!
//!   ym-residual-rooms <store_dir> <seed16_hex> <leaf_file> <block_out> <ticks>
//!
//! Output: HBP rows on stdout (json=0).
#![forbid(unsafe_code)]

// The canonical ternary kernel, reused via #[path] (never copied).
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
#[allow(dead_code)]
mod tribit;
use tribit::Zero;

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{Read, Seek, SeekFrom, Write};
use std::process::exit;

// ---- the room law of ROOMS-MAKE.hbp / host8-rooms main.rs (same constants, same mix)
const SECTORS: u64 = 375;
const RPS: u64 = 100_000_000;
const TOTAL: u64 = SECTORS * RPS;
const CENTRE: u64 = TOTAL / 2;
const H27: u64 = 3_812_798_742_493;
const M1: u64 = 0xbf58_476d_1ce4_e5b9;
const M2: u64 = 0x94d0_49bb_1331_11eb;

const fn modinv(c: u64) -> u64 {
    let mut x = c;
    let mut i = 0;
    while i < 6 {
        x = x.wrapping_mul(2u64.wrapping_sub(c.wrapping_mul(x)));
        i += 1;
    }
    x
}
const M1I: u64 = modinv(M1);
const M2I: u64 = modinv(M2);

fn mix(mut z: u64) -> u64 {
    z = (z ^ (z >> 30)).wrapping_mul(M1);
    z = (z ^ (z >> 27)).wrapping_mul(M2);
    z ^ (z >> 31)
}

fn unmix(mut z: u64) -> u64 {
    z ^= (z >> 31) ^ (z >> 62);
    z = z.wrapping_mul(M2I);
    z ^= (z >> 27) ^ (z >> 54);
    z = z.wrapping_mul(M1I);
    z ^= (z >> 30) ^ (z >> 60);
    z
}

// ---- the block: 3^9 rooms centred on the ground room
const BLOCK: usize = 19_683;
const HALF: u64 = 9_841;
const SIDE: i32 = 27;
const GROUPS: usize = 729;
const REST: u8 = 13;

/// Block index (0..19683) -> (X, Y, Z), each in 0..27 (balanced value plus 13).
fn coords(idx: usize) -> (i32, i32, i32) {
    let mut d = [0i32; 9];
    let mut v = idx;
    for slot in &mut d {
        *slot = i32::try_from(v % 3).unwrap_or(0);
        v /= 3;
    }
    (
        d[0] + 3 * d[3] + 9 * d[6],
        d[1] + 3 * d[4] + 9 * d[7],
        d[2] + 3 * d[5] + 9 * d[8],
    )
}

fn index_of(x: i32, y: i32, z: i32) -> usize {
    let dig = |c: i32, k: u32| usize::try_from((c / 3i32.pow(k)) % 3).unwrap_or(0);
    dig(x, 0)
        + 3 * dig(y, 0)
        + 9 * dig(z, 0)
        + 27 * dig(x, 1)
        + 81 * dig(y, 1)
        + 243 * dig(z, 1)
        + 729 * dig(x, 2)
        + 2187 * dig(y, 2)
        + 6561 * dig(z, 2)
}

fn group_of(x: i32, y: i32, z: i32) -> usize {
    usize::try_from((x / 3) + 9 * (y / 3) + 81 * (z / 3)).unwrap_or(0)
}

#[derive(Clone, Copy)]
struct Func {
    x: i32,
    y: i32,
    z: i32,
    heading: u8,
    rho: u128,
    top: u128, // 27^(L-1)
}

#[derive(Default, Clone, Copy)]
struct Stats {
    group_events: u64,
    triple_births: u64,
    life_sum: u64,
    life_max: u64,
    life_ge3: u64,
    occ_max: u64,
    moving_end: u64,
}

fn digits27(mut v: u128) -> (u32, u128) {
    let mut l = 1u32;
    let mut top = 1u128;
    while v >= 27 {
        v /= 27;
        l += 1;
        top *= 27;
    }
    (l, top)
}

fn simulate(rooms: &[[u8; 27]], start: &[Func], ticks: u32) -> Stats {
    let mut f: Vec<Func> = start.to_vec();
    let mut st = Stats::default();
    let mut alive: BTreeMap<(u16, u16, u16), u32> = BTreeMap::new();
    let close = |st: &mut Stats, life: u64| {
        st.life_sum += life;
        if life > st.life_max {
            st.life_max = life;
        }
        if life >= 3 {
            st.life_ge3 += 1;
        }
    };
    for t in 0..=ticks {
        // who shares a group now
        let mut by_group: BTreeMap<usize, Vec<u16>> = BTreeMap::new();
        for (i, w) in f.iter().enumerate() {
            by_group
                .entry(group_of(w.x, w.y, w.z))
                .or_default()
                .push(u16::try_from(i).unwrap_or(u16::MAX));
        }
        let mut now: BTreeSet<(u16, u16, u16)> = BTreeSet::new();
        for ids in by_group.values() {
            let n = ids.len();
            if n as u64 > st.occ_max {
                st.occ_max = n as u64;
            }
            if n >= 3 {
                st.group_events += 1;
                if n > 160 {
                    println!("ABORT|reason=a_group_holds_{n}_functions_the_triple_count_is_out_of_budget|json=0");
                    exit(3);
                }
                for a in 0..n {
                    for b in a + 1..n {
                        for c in b + 1..n {
                            now.insert((ids[a], ids[b], ids[c]));
                        }
                    }
                }
            }
        }
        let ended: Vec<(u16, u16, u16)> = alive
            .keys()
            .filter(|k| !now.contains(k))
            .copied()
            .collect();
        for k in ended {
            if let Some(s) = alive.remove(&k) {
                close(&mut st, u64::from(t - s));
            }
        }
        for k in &now {
            if !alive.contains_key(k) {
                alive.insert(*k, t);
                st.triple_births += 1;
            }
        }
        if t == ticks {
            break;
        }
        // one tick: the function bound to the room runs on the room's 27 trits
        for w in &mut f {
            let room = &rooms[index_of(w.x, w.y, w.z)];
            let i = u8::try_from(w.rho % 27).unwrap_or(0);
            match Zero::from_digit(room[usize::from(i)]) {
                Zero::Nil => {}
                Zero::Pos => w.heading = i,
                Zero::Neg => w.heading = REST,
            }
            let h = i32::from(w.heading);
            w.x = (w.x + (h % 3) - 1).rem_euclid(SIDE);
            w.y = (w.y + ((h / 3) % 3) - 1).rem_euclid(SIDE);
            w.z = (w.z + (h / 9) - 1).rem_euclid(SIDE);
            w.rho = w.rho / 27 + (w.rho % 27) * w.top;
        }
    }
    for s in alive.values() {
        close(&mut st, u64::from(ticks + 1 - s));
    }
    st.moving_end = f.iter().filter(|w| w.heading != REST).count() as u64;
    st
}

fn row(tag: &str, name: &str, s: &Stats) {
    println!(
        "{tag}|run={name}|group_events={}|triple_births={}|lifetime_sum={}|lifetime_max={}|lifetimes_ge3={}|max_group_occupancy={}|functions_moving_at_end={}|json=0",
        s.group_events, s.triple_births, s.life_sum, s.life_max, s.life_ge3, s.occ_max, s.moving_end
    );
}

fn verdict(null: &str, name: &str, real: u64, runs: &[u64]) {
    let lo = runs.iter().copied().min().unwrap_or(0);
    let hi = runs.iter().copied().max().unwrap_or(0);
    let below = runs.iter().filter(|v| **v < real).count();
    let v = if real < lo || real > hi { "OUTSIDE" } else { "INSIDE" };
    println!(
        "VERDICT|null={null}|statistic={name}|real={real}|null_min={lo}|null_max={hi}|null_runs_below_real={below}|of={}|result={v}|json=0",
        runs.len()
    );
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() != 6 {
        eprintln!("usage: ym-residual-rooms <store_dir> <seed16_hex> <leaf_file> <block_out> <ticks>");
        exit(2);
    }
    let seed = u64::from_str_radix(&a[2], 16).unwrap_or_else(|_| exit(2));
    let ticks: u32 = a[5].parse().unwrap_or_else(|_| exit(2));

    // ---- one positioned read of the block, then every stub must decode to its own room
    let first = CENTRE - HALF;
    let sector = first / RPS;
    assert_eq!(sector, (CENTRE + HALF) / RPS);
    let path = format!("{}/sector-{sector:03}.rooms", a[1]);
    let mut file = File::open(&path).unwrap_or_else(|e| {
        println!("ABORT|reason=cannot_open_{path}_{e}|json=0");
        exit(1)
    });
    let mut buf = vec![0u8; BLOCK * 8];
    file.seek(SeekFrom::Start((first % RPS) * 8)).unwrap_or_else(|_| exit(1));
    file.read_exact(&mut buf).unwrap_or_else(|_| exit(1));
    File::create(&a[4])
        .and_then(|mut o| o.write_all(&buf))
        .unwrap_or_else(|_| exit(1));
    let mut rooms: Vec<[u8; 27]> = Vec::with_capacity(BLOCK);
    let mut bad = 0u64;
    let mut census = [0u64; 3];
    for (idx, c) in buf.chunks_exact(8).enumerate() {
        let stub = u64::from_le_bytes([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]]);
        let n = first + idx as u64;
        let word = unmix(stub) ^ seed;
        if i128::from(word) - i128::from(H27) + i128::from(CENTRE) != i128::from(n) {
            bad += 1;
        }
        let mut t = [0u8; 27];
        let mut v = stub;
        for slot in &mut t {
            *slot = u8::try_from(v % 3).unwrap_or(0);
            census[usize::from(*slot)] += 1;
            v /= 3;
        }
        rooms.push(t);
    }
    println!(
        "BLOCKREAD|path={path}|first_room={first}|rooms={BLOCK}|bytes={}|stubs_not_decoding_to_their_own_room={bad}|trit_census_neg_nil_pos={}_{}_{}|ground_room_stub={:016x}|mix_of_ground_word={:016x}|json=0",
        BLOCK * 8,
        census[0],
        census[1],
        census[2],
        u64::from_le_bytes([
            buf[HALF as usize * 8],
            buf[HALF as usize * 8 + 1],
            buf[HALF as usize * 8 + 2],
            buf[HALF as usize * 8 + 3],
            buf[HALF as usize * 8 + 4],
            buf[HALF as usize * 8 + 5],
            buf[HALF as usize * 8 + 6],
            buf[HALF as usize * 8 + 7]
        ]),
        mix(H27 ^ seed)
    );
    if bad != 0 {
        println!("ABORT|reason=block_not_authenticated|json=0");
        exit(1);
    }
    // geometry self-check: index_of(coords(i)) == i, and 729 omega rooms
    let mut omega = 0u32;
    for i in 0..BLOCK {
        let (x, y, z) = coords(i);
        assert_eq!(index_of(x, y, z), i);
        if x % 3 == 1 && y % 3 == 1 && z % 3 == 1 {
            omega += 1;
        }
    }
    println!("GEOMETRY|rooms={BLOCK}|groups={GROUPS}|omega_rooms={omega}|index_roundtrip=EXACT|json=0");

    // ---- the leaves
    let text = std::fs::read_to_string(&a[3]).unwrap_or_else(|_| exit(1));
    let mut start: Vec<Func> = Vec::new();
    for line in text.lines() {
        if !line.starts_with("LEAF|") {
            continue;
        }
        let get = |k: &str| -> u128 {
            line.split('|')
                .find_map(|w| w.strip_prefix(k).and_then(|r| r.strip_prefix('=')))
                .and_then(|v| v.parse::<u128>().ok())
                .unwrap_or_else(|| {
                    println!("ABORT|reason=leaf_field_{k}_unreadable|json=0");
                    exit(1)
                })
        };
        let (key, m, slack) = (get("key"), get("M"), get("slack"));
        let (x, y, z) = coords(usize::try_from(key % BLOCK as u128).unwrap_or(0));
        let (_, top) = digits27(slack);
        start.push(Func {
            x,
            y,
            z,
            heading: u8::try_from(m % 27).unwrap_or(0),
            rho: slack,
            top,
        });
    }
    let nf = start.len();
    let distinct: BTreeSet<(i32, i32, i32)> = start.iter().map(|w| (w.x, w.y, w.z)).collect();
    println!(
        "FUNCTIONS|count={nf}|distinct_start_rooms={}|ticks={ticks}|json=0",
        distinct.len()
    );

    let real = simulate(&rooms, &start, ticks);
    row("REAL", "leaves", &real);

    let mut na: Vec<Stats> = Vec::new();
    let mut nb: Vec<Stats> = Vec::new();
    for k in 0..27u64 {
        // null A: same digit count, pseudo-random base-27 digits
        let mut fa = start.clone();
        for (i, w) in fa.iter_mut().enumerate() {
            let (l, _) = digits27(w.top);
            let mut v: u128 = 0;
            for j in 0..l {
                let r = mix((0xA5A5_0000 + k) ^ ((i as u64) << 20) ^ u64::from(j));
                v = v * 27 + u128::from(r % 27);
            }
            w.rho = v;
        }
        let s = simulate(&rooms, &fa, ticks);
        row("NULL_A", &format!("seed_{k}"), &s);
        na.push(s);
        // null B: the real residuals permuted among the functions (Fisher-Yates on a mix stream)
        let mut perm: Vec<usize> = (0..nf).collect();
        for i in (1..nf).rev() {
            let r = mix((0xB6B6_0000 + k) ^ ((i as u64) << 20));
            perm.swap(i, usize::try_from(r % (i as u64 + 1)).unwrap_or(0));
        }
        let mut fb = start.clone();
        for (i, w) in fb.iter_mut().enumerate() {
            w.rho = start[perm[i]].rho;
            w.top = start[perm[i]].top;
        }
        let s = simulate(&rooms, &fb, ticks);
        row("NULL_B", &format!("seed_{k}"), &s);
        nb.push(s);
    }
    for (name, runs) in [("A_random_digits", &na), ("B_permuted_residuals", &nb)] {
        verdict(name, "group_events", real.group_events, &runs.iter().map(|s| s.group_events).collect::<Vec<_>>());
        verdict(name, "triple_births", real.triple_births, &runs.iter().map(|s| s.triple_births).collect::<Vec<_>>());
        verdict(name, "lifetime_sum", real.life_sum, &runs.iter().map(|s| s.life_sum).collect::<Vec<_>>());
        verdict(name, "lifetime_max", real.life_max, &runs.iter().map(|s| s.life_max).collect::<Vec<_>>());
        verdict(name, "lifetimes_ge3", real.life_ge3, &runs.iter().map(|s| s.life_ge3).collect::<Vec<_>>());
    }
    println!("END|float_used=0|room_writes=0|json=0");
}
