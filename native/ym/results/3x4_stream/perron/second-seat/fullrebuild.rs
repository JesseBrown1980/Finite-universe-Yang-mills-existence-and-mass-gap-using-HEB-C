// Every row of a sector store rebuilt from the definition of H by separately written code (second seat), compared in full. Integer only, no float, json=0.
// H = J_E E + J_B M on gauge orbits. E: for each link and each of the three transpositions, one move; a row holds -1 per move into another row's orbit, and its diagonal is
// 3 nl minus the moves that return to its own orbit. M = sum over plaquettes of (2 - chi(U_p)), chi = fixed points - 1. Weight = number of distinct codes over conjugation and lattice symmetry.
// Key of a state: gauge-fix to the comb tree, free links in ascending link order as base-6 digits, least over global conjugation and lattice symmetry. Digits name 012 021 102 120 201 210.
//
// usage: fullrebuild DEV PASSA LX LY THREADS
//   DEV is a path, or first:count:seglen:prefix for <prefix>NNN.rooms. PASSA: 16 bytes per row: key u64, weight u32, M u32.
// Read-only. Memory: 8 bytes per row for the keys, plus at most 32 batches of 8 MiB. Prints FULLREBUILD_PROGRESS rows, then one FULLREBUILD row. Exit 2 on any mismatch.
use std::io::Read;
use std::sync::atomic::{AtomicU64, Ordering::Relaxed};
use std::sync::{mpsc, Arc, Mutex};

const MAXL: usize = 32;
const MAXV: usize = 16;
const LEAF: usize = 16 * 1048576;

struct G {
    lx: i32, ly: i32, v: usize, nl: usize,
    mul: [[u8; 6]; 6], inv: [u8; 6], cost: [u8; 6], conj: [[u8; 6]; 6], tr: [u8; 3],
    free: Vec<usize>, steps: Vec<(usize, usize, usize)>, ends: Vec<(usize, usize)>, ops: Vec<Vec<(u8, bool)>>, plaq: Vec<[usize; 4]>,
}

impl G {
    fn new(lx: i32, ly: i32) -> G {
        let v = (lx * ly) as usize;
        let nl = 2 * v;
        assert!(nl <= MAXL && v <= MAXV);
        let site = |x: i32, y: i32| (x.rem_euclid(lx) as usize) * ly as usize + y.rem_euclid(ly) as usize;
        let xl = |x: i32, y: i32| site(x, y);
        let yl = |x: i32, y: i32| v + site(x, y);
        let p: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
        let idx = |q: [u8; 3]| p.iter().position(|r| *r == q).unwrap() as u8;
        let mut mul = [[0u8; 6]; 6];
        for a in 0..6 { for b in 0..6 { mul[a][b] = idx([p[a][p[b][0] as usize], p[a][p[b][1] as usize], p[a][p[b][2] as usize]]); } }
        let mut inv = [0u8; 6];
        for a in 0..6 { for b in 0..6 { if mul[a][b] == 0 { inv[a] = b as u8; } } }
        let (mut cost, mut tr) = ([0u8; 6], Vec::new());
        for a in 0..6 {
            let fixed = (0..3).filter(|&k| p[a][k] == k as u8).count() as i32;
            cost[a] = (3 - fixed) as u8;
            if fixed == 1 { tr.push(a as u8); }
        }
        let mut conj = [[0u8; 6]; 6];
        for c in 0..6 { for w in 0..6 { conj[c][w] = mul[mul[c][w] as usize][inv[c] as usize]; } }
        let mut ends = vec![(0usize, 0usize); nl];
        for x in 0..lx { for y in 0..ly { ends[xl(x, y)] = (site(x, y), site(x + 1, y)); ends[yl(x, y)] = (site(x, y), site(x, y + 1)); } }
        let mut in_tree = vec![false; nl];
        let mut steps = Vec::new();
        for y in 0..ly - 1 { in_tree[yl(0, y)] = true; steps.push((site(0, y), site(0, y + 1), yl(0, y))); }
        for x in 0..lx - 1 { for y in 0..ly { in_tree[xl(x, y)] = true; steps.push((site(x, y), site(x + 1, y), xl(x, y))); } }
        let free: Vec<usize> = (0..nl).filter(|&l| !in_tree[l]).collect();
        let mut ops = Vec::new();
        for fx in [false, true] { for fy in [false, true] { for tx in 0..lx { for ty in 0..ly {
            let mut d = vec![(0u8, false); nl];
            for x in 0..lx { for y in 0..ly {
                let (px, py) = (if fx { -x } else { x }, if fy { -y } else { y });
                d[xl(x, y)] = (xl(if fx { px - 1 } else { px } + tx, py + ty) as u8, fx);
                d[yl(x, y)] = (yl(px + tx, if fy { py - 1 } else { py } + ty) as u8, fy);
            } }
            ops.push(d);
        } } } }
        let mut plaq = Vec::new();
        for x in 0..lx { for y in 0..ly { plaq.push([xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)]); } }
        G { lx, ly, v, nl, mul, inv, cost, conj, tr: [tr[0], tr[1], tr[2]], free, steps, ends, ops, plaq }
    }
    #[inline]
    fn canon(&self, u: &[u8; MAXL], mut sink: Option<&mut Vec<u64>>) -> u64 {
        let mut best = u64::MAX;
        let mut out = [0u8; MAXL];
        let mut h = [0u8; MAXV];
        let mut q = [0u8; MAXL];
        let nf = self.free.len();
        for op in &self.ops {
            for l in 0..self.nl { let (d, i) = op[l]; out[d as usize] = if i { self.inv[u[l] as usize] } else { u[l] }; }
            for &(t, hd, l) in &self.steps { h[hd] = self.mul[h[t] as usize][out[l] as usize]; }
            for (k, &l) in self.free.iter().enumerate() {
                let (a, b) = self.ends[l];
                q[k] = self.mul[self.mul[h[a] as usize][out[l] as usize] as usize][self.inv[h[b] as usize] as usize];
            }
            for c in &self.conj {
                let mut code = 0u64;
                for k in (0..nf).rev() { code = code * 6 + u64::from(c[q[k] as usize]); }
                if code < best { best = code; }
                if let Some(v) = sink.as_deref_mut() { v.push(code); }
            }
        }
        best
    }
    fn magnetic(&self, u: &[u8; MAXL]) -> u32 {
        let mut m = 0;
        for p in &self.plaq {
            let z = self.mul[self.mul[self.mul[u[p[0]] as usize][u[p[1]] as usize] as usize][self.inv[u[p[2]] as usize] as usize] as usize][self.inv[u[p[3]] as usize] as usize];
            m += u32::from(self.cost[z as usize]);
        }
        m
    }
}

// Own SHA-256 for the merkle.
const K: [u32; 64] = [
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
fn sha_hex(data: &[u8]) -> String {
    let mut h: [u32; 8] = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    let block = |h: &mut [u32; 8], b: &[u8]| {
        let mut w = [0u32; 64];
        for i in 0..16 { w[i] = u32::from_be_bytes([b[4*i], b[4*i+1], b[4*i+2], b[4*i+3]]); }
        for i in 16..64 {
            let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3);
            let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }
        let mut v = *h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let mj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(mj);
            v[7] = v[6]; v[6] = v[5]; v[5] = v[4]; v[4] = v[3].wrapping_add(t1); v[3] = v[2]; v[2] = v[1]; v[1] = v[0]; v[0] = t1.wrapping_add(t2);
        }
        for i in 0..8 { h[i] = h[i].wrapping_add(v[i]); }
    };
    let n = data.len() / 64;
    for c in data[..n * 64].chunks_exact(64) { block(&mut h, c); }
    let mut tail = data[n * 64..].to_vec();
    tail.push(0x80);
    while tail.len() % 64 != 56 { tail.push(0); }
    tail.extend_from_slice(&((data.len() as u64) * 8).to_be_bytes());
    for c in tail.chunks_exact(64) { block(&mut h, c); }
    h.iter().map(|x| format!("{x:08x}")).collect()
}

struct Stream { names: Vec<String>, seg: Option<u64>, k: usize, pos: u64, f: std::fs::File }
impl Stream {
    fn open(spec: &str) -> Stream {
        let parts: Vec<&str> = spec.splitn(4, ':').collect();
        if parts.len() == 4 && parts[0].chars().all(|c| c.is_ascii_digit()) {
            let (first, count, seg): (usize, usize, u64) = (parts[0].parse().unwrap(), parts[1].parse().unwrap(), parts[2].parse().unwrap());
            let names: Vec<String> = (0..count).map(|i| format!("{}{:03}.rooms", parts[3], first + i)).collect();
            let f = std::fs::File::open(&names[0]).unwrap();
            Stream { names, seg: Some(seg), k: 0, pos: 0, f }
        } else {
            Stream { names: vec![spec.to_string()], seg: None, k: 0, pos: 0, f: std::fs::File::open(spec).unwrap() }
        }
    }
    fn read_exact(&mut self, mut out: &mut [u8]) -> bool {
        while !out.is_empty() {
            let want = match self.seg { Some(s) => (out.len() as u64).min(s - self.pos) as usize, None => out.len() };
            let n = if want == 0 { 0 } else { self.f.read(&mut out[..want]).unwrap() };
            if n == 0 {
                if self.k + 1 >= self.names.len() { return false; }
                self.k += 1;
                self.pos = 0;
                self.f = std::fs::File::open(&self.names[self.k]).unwrap();
                continue;
            }
            self.pos += n as u64;
            let (_, rest) = out.split_at_mut(n);
            out = rest;
        }
        true
    }
}

fn check_batch(g: &G, keys: &[u64], first: usize, bytes: &[u8], stat: &[AtomicU64; 5]) {
    let mut codes: Vec<u64> = Vec::with_capacity(4 * (g.lx * g.ly) as usize * 6);
    let mut hit: Vec<(u32, i32)> = Vec::with_capacity(3 * g.nl + 1);
    let mut p = 0usize;
    let mut h = first;
    let nl3 = (3 * g.nl) as i32;
    while p < bytes.len() {
        let w_store = u32::from_le_bytes(bytes[p..p + 4].try_into().unwrap());
        let m_store = u32::from(u16::from_le_bytes(bytes[p + 4..p + 6].try_into().unwrap()));
        let cnt = u16::from_le_bytes(bytes[p + 6..p + 8].try_into().unwrap()) as usize;
        let body = &bytes[p + 8..p + 8 + 8 * cnt];
        let mut key = keys[h];
        let mut u = [0u8; MAXL];
        for &l in &g.free { u[l] = (key % 6) as u8; key /= 6; }
        codes.clear();
        if g.canon(&u, Some(&mut codes)) != keys[h] { stat[1].fetch_add(1, Relaxed); }
        codes.sort_unstable();
        codes.dedup();
        if codes.len() as u32 != w_store { stat[2].fetch_add(1, Relaxed); }
        if g.magnetic(&u) != m_store { stat[3].fetch_add(1, Relaxed); }
        hit.clear();
        let mut back = 0i32;
        let mut lost = 0u64;
        for l in 0..g.nl {
            let old = u[l];
            for &tau in &g.tr {
                u[l] = g.mul[tau as usize][old as usize];
                match keys.binary_search(&g.canon(&u, None)) {
                    Ok(j) if j == h => back += 1,
                    Ok(j) => hit.push((j as u32, -1)),
                    Err(_) => lost += 1,
                }
            }
            u[l] = old;
        }
        hit.push((h as u32, nl3 - back));
        hit.sort_unstable_by_key(|x| x.0);
        let mut same = lost == 0;
        let mut it = body.chunks_exact(8).map(|e| (u32::from_le_bytes(e[0..4].try_into().unwrap()), i32::from_le_bytes(e[4..8].try_into().unwrap()))).filter(|e| e.1 != 0);
        let mut i = 0usize;
        while i < hit.len() && same {
            let (j, mut z) = hit[i];
            i += 1;
            while i < hit.len() && hit[i].0 == j { z += hit[i].1; i += 1; }
            if z == 0 { continue; }
            if it.next() != Some((j, z)) { same = false; }
        }
        if same && it.next().is_some() { same = false; }
        if !same { stat[4].fetch_add(1, Relaxed); }
        stat[0].fetch_add(1, Relaxed);
        p += 8 + 8 * cnt;
        h += 1;
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (dev, passa, lx, ly, threads): (&str, &str, i32, i32, usize) = (&a[1], &a[2], a[3].parse().unwrap(), a[4].parse().unwrap(), a[5].parse().unwrap());
    let t0 = std::time::Instant::now();
    let g = Arc::new(G::new(lx, ly));
    let mut s = Stream::open(dev);
    let mut head = vec![0u8; 4096];
    assert!(s.read_exact(&mut head));
    let end = head.iter().position(|&c| c == b'\n').unwrap();
    let line = String::from_utf8_lossy(&head[..end]).to_string();
    let num = |k: &str| line.split('|').find_map(|kv| kv.strip_prefix(k)).unwrap().parse::<u64>().unwrap();
    let (n, payload) = (num("n=") as usize, num("payload_bytes="));
    let merkle = line.split('|').find_map(|kv| kv.strip_prefix("payload_merkle=")).unwrap().to_string();
    // Keys only: stream the key table so the peak stays at 8 bytes per row.
    let mut keys: Vec<u64> = Vec::with_capacity(n);
    {
        let mut f = std::io::BufReader::with_capacity(1 << 20, std::fs::File::open(passa).unwrap());
        let mut b = [0u8; 16];
        for _ in 0..n {
            f.read_exact(&mut b).unwrap();
            keys.push(u64::from_le_bytes(b[0..8].try_into().unwrap()));
        }
    }
    assert!(keys.windows(2).all(|w| w[0] < w[1]), "keys not ascending");
    let keys = Arc::new(keys);
    let stat: Arc<[AtomicU64; 5]> = Arc::new(Default::default());
    let (tx, rx) = mpsc::sync_channel::<(usize, Vec<u8>)>(32);
    let rx = Arc::new(Mutex::new(rx));
    let hs: Vec<_> = (0..threads).map(|_| {
        let (g, keys, stat, rx) = (g.clone(), keys.clone(), stat.clone(), rx.clone());
        std::thread::spawn(move || loop {
            let msg = rx.lock().unwrap().recv();
            match msg { Ok((first, bytes)) => check_batch(&g, &keys, first, &bytes, &stat), Err(_) => break }
        })
    }).collect();
    // Reader: 16 MiB leaves for the merkle; whole rows cut into batches for the workers.
    let mut left = payload;
    let mut shas = String::new();
    let mut carry: Vec<u8> = Vec::new();
    let mut h = 0usize;
    let mut next_report = 1u64 << 20;
    while left > 0 {
        let take = left.min(LEAF as u64) as usize;
        let mut buf = vec![0u8; take];
        assert!(s.read_exact(&mut buf), "short read");
        left -= take as u64;
        shas.push_str(&sha_hex(&buf));
        carry.extend_from_slice(&buf);
        let mut p = 0usize;
        let first = h;
        while h < n && p + 8 <= carry.len() {
            let cnt = u16::from_le_bytes(carry[p + 6..p + 8].try_into().unwrap()) as usize;
            if p + 8 + 8 * cnt > carry.len() { break; }
            p += 8 + 8 * cnt;
            h += 1;
        }
        // cut this run of rows into pieces of about 8 MiB so the workers share it
        let mut q = 0usize;
        let mut hq = first;
        while q < p {
            let mut r = q;
            let mut hr = hq;
            while r < p && r - q < 8 * 1048576 {
                let cnt = u16::from_le_bytes(carry[r + 6..r + 8].try_into().unwrap()) as usize;
                r += 8 + 8 * cnt;
                hr += 1;
            }
            tx.send((hq, carry[q..r].to_vec())).unwrap();
            q = r;
            hq = hr;
        }
        carry.drain(..p);
        if h == n { if carry.iter().any(|&c| c != 0) { println!("FULLREBUILD_FAIL|reason=nonzero_padding|json=0"); std::process::exit(2); } carry.clear(); }
        let done = stat[0].load(Relaxed);
        if done >= next_report {
            println!("FULLREBUILD_PROGRESS|rows_done={done}|of={n}|bad_key={}|bad_w={}|bad_M={}|bad_entries={}|secs={}|json=0", stat[1].load(Relaxed), stat[2].load(Relaxed), stat[3].load(Relaxed), stat[4].load(Relaxed), t0.elapsed().as_secs());
            next_report = done + (1 << 22);
        }
    }
    drop(tx);
    for t in hs { t.join().unwrap(); }
    let ok_merkle = sha_hex(shas.as_bytes()) == merkle;
    let v: Vec<u64> = stat.iter().map(|x| x.load(Relaxed)).collect();
    println!(
        "FULLREBUILD|L={lx}x{ly}|V={}|nl={}|n={n}|rows_rebuilt={}|rows_read={h}|canonical_key_mismatch={}|weight_mismatch={}|M_mismatch={}|entries_mismatch={}|merkle={}|secs={}|json=0",
        g.v, g.nl, v[0], v[1], v[2], v[3], v[4], if ok_merkle { "PASS" } else { "FAIL" }, t0.elapsed().as_secs()
    );
    if v[1] + v[2] + v[3] + v[4] > 0 || !ok_merkle || h != n || v[0] != n as u64 { std::process::exit(2); }
}
