// Store-free checks on 3x4: reads the key table and the vector files only, never the room store. Streaming, about 40 MB of RAM.
// Exact integer arithmetic. Own SHA-256, own 256-bit sums. Prints rows for own34_post.py.
use std::fs::File;
use std::io::Read;

struct Sha { h: [u32; 8], buf: Vec<u8>, len: u64 }
const K: [u32; 64] = [
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
impl Sha {
    fn new() -> Sha { Sha { h: [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19], buf: Vec::new(), len: 0 } }
    fn block(h: &mut [u32; 8], b: &[u8]) {
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
    }
    fn update(&mut self, data: &[u8]) {
        self.len += data.len() as u64;
        let mut d = data;
        if !self.buf.is_empty() {
            let need = 64 - self.buf.len();
            let take = need.min(d.len());
            self.buf.extend_from_slice(&d[..take]);
            d = &d[take..];
            if self.buf.len() == 64 { let b = std::mem::take(&mut self.buf); Sha::block(&mut self.h, &b); }
        }
        let n = d.len() / 64;
        for c in d[..n*64].chunks_exact(64) { Sha::block(&mut self.h, c); }
        self.buf.extend_from_slice(&d[n*64..]);
    }
    fn hex(mut self) -> String {
        let bits = self.len * 8;
        let mut pad = vec![0x80u8];
        while (self.buf.len() + pad.len()) % 64 != 56 { pad.push(0); }
        pad.extend_from_slice(&bits.to_be_bytes());
        let mut all = std::mem::take(&mut self.buf);
        all.extend_from_slice(&pad);
        for c in all.chunks_exact(64) { Sha::block(&mut self.h, c); }
        self.h.iter().map(|x| format!("{x:08x}")).collect()
    }
}

#[derive(Clone, Copy, Default)]
struct Big { lo: u128, hi: i128 }
impl Big {
    fn add(&mut self, v: i128) {
        let (l, c) = self.lo.overflowing_add(v as u128);
        self.lo = l;
        self.hi += (c as i128) - ((v < 0) as i128);
    }
    fn show(&self) -> String { format!("{}:{}", self.hi, self.lo) }
}

const CH: usize = 4 * 1048576;
struct Rd { f: File, buf: Vec<u8>, pos: usize, end: usize, sha: Sha }
impl Rd {
    fn open(p: &str) -> Rd { Rd { f: File::open(p).unwrap_or_else(|e| panic!("{p}: {e}")), buf: vec![0u8; CH], pos: 0, end: 0, sha: Sha::new() } }
    fn fill(&mut self) -> bool {
        let keep = self.end - self.pos;
        self.buf.copy_within(self.pos..self.end, 0);
        self.pos = 0; self.end = keep;
        while self.end < CH {
            let n = self.f.read(&mut self.buf[self.end..]).unwrap();
            if n == 0 { break; }
            self.sha.update(&self.buf[self.end..self.end + n]);
            self.end += n;
        }
        self.end > 0
    }
    fn take(&mut self, n: usize) -> Option<&[u8]> {
        if self.end - self.pos < n { self.fill(); if self.end - self.pos < n { return None; } }
        let s = &self.buf[self.pos..self.pos + n];
        self.pos += n;
        Some(s)
    }
    fn i64(&mut self) -> Option<i64> { self.take(8).map(|b| i64::from_le_bytes([b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7]])) }
}

fn main() {
    let r = "D:/ym-3x4-room-run/p0-ball";
    let names = [
        format!("{r}/p34/d93000000.bin"), format!("{r}/p34/d93700000.bin"), format!("{r}/climb34/best.bin"), format!("{r}/jump34/x-93-937.bin"),
        format!("{r}/jump34/d93950000-conv.bin"), format!("{r}/jump34/x3-a.bin"), format!("{r}/jump34/x3-b.bin"),
    ];
    let k = names.len();
    let mut rd: Vec<Rd> = names.iter().map(|p| Rd::open(p)).collect();
    let mut pa = Rd::open("D:/ym-3x4-room-run/passA.bin");
    let mut pa_sha_done = false;
    let _ = &mut pa_sha_done;
    let mut g = vec![Big::default(); k * k];
    let mut m = vec![Big::default(); k * k];
    let mut l = vec![Big::default(); k];
    let mut d_min = vec![i64::MAX; k];
    let mut d_max = vec![i64::MIN; k];
    let mut arg_max = vec![0usize; k];
    let mut nonpos = vec![0u64; k];
    let mut flat_nonzero = vec![0u64; k];
    let mut hist = vec![0u64; 64];
    let mut sum_w: u128 = 0;
    let mut max_w: u64 = 0;
    // reconstruction of x3-a and x3-b; x3-a = (5 d0 - 19 d1 + 14 d2) << m + 316 d2, x3-b the same with d4 and gamma 0.
    let (ta, tb) = (316i128, 0i128);
    let (mut fa, mut fb): (i128, i128) = (0, 0);
    let (mut bad_a, mut bad_b) = (0u64, 0u64);
    // Predictions from the vectors alone at every row, min and at the tightest row. g y = 50000 (-95 d0 + 95 d1) in the common scale.
    let s: i128 = 1_000_000i128 << 30;
    let t_top: i128 = 93_950_000;
    let mut pred_a: Option<(i128, usize, u32)> = None;
    let mut pred_b: Option<(i128, usize, u32)> = None;
    let (mut at_a, mut at_b) = (0i128, 0i128);
    let mut flat_rows: Vec<usize> = Vec::new();
    let tight = 44_742_735usize;
    let mut h = 0usize;
    let mut v = vec![0i64; k];
    let t0 = std::time::Instant::now();
    loop {
        let rec = match pa.take(16) { Some(b) => { let w = u32::from_le_bytes([b[8],b[9],b[10],b[11]]); let mg = u32::from_le_bytes([b[12],b[13],b[14],b[15]]); (w, mg) } None => break };
        let (w, mg) = rec;
        for (i, x) in rd.iter_mut().enumerate() { v[i] = x.i64().expect("vector shorter than the key table"); }
        sum_w += u128::from(w);
        max_w = max_w.max(u64::from(w));
        hist[mg as usize] += 1;
        if mg == 0 {
            flat_rows.push(h);
            for i in 0..k { flat_nonzero[i] += u64::from(v[i] != 0); }
        } else {
            for i in 0..k {
                if v[i] <= 0 { nonpos[i] += 1; }
                d_min[i] = d_min[i].min(v[i]);
                if v[i] > d_max[i] { d_max[i] = v[i]; arg_max[i] = h; }
                l[i].add(i128::from(w) * i128::from(v[i]));
            }
            for a in 0..k {
                let wa = i128::from(w) * i128::from(v[a]);
                for b in a..k {
                    let gv = wa * i128::from(v[b]);
                    g[a * k + b].add(gv);
                    m[a * k + b].add(gv * i128::from(mg));
                }
            }
            let xa = 5 * i128::from(v[0]) - 19 * i128::from(v[1]) + 14 * i128::from(v[2]);
            let xb = 5 * i128::from(v[0]) - 19 * i128::from(v[1]) + 14 * i128::from(v[4]);
            let da = i128::from(v[5]) - ta * i128::from(v[2]);
            let db = i128::from(v[6]) - tb * i128::from(v[4]);
            if xa != 0 { if fa == 0 { fa = da / xa; } if da != fa * xa { bad_a += 1; } } else if da != 0 { bad_a += 1; }
            if xb != 0 { if fb == 0 { fb = db / xb; } if db != fb * xb { bad_b += 1; } } else if db != 0 { bad_b += 1; }
            let y = 50_000 * 95 * (i128::from(v[1]) - i128::from(v[0]));
            let na = y * fa + ta * s;
            let nb = y * fb + tb * s;
            let pa_ = t_top + na.div_euclid(i128::from(v[5]));
            let pb_ = t_top + nb.div_euclid(i128::from(v[6]));
            if pred_a.map_or(true, |q| pa_ < q.0) { pred_a = Some((pa_, h, mg)); }
            if pred_b.map_or(true, |q| pb_ < q.0) { pred_b = Some((pb_, h, mg)); }
            if h == tight { at_a = pa_; at_b = pb_; }
        }
        h += 1;
    }
    println!("OWN34|rows={h}|sum_w={sum_w}|max_w={max_w}|flat_rows={flat_rows:?}|secs={}|json=0", t0.elapsed().as_secs());
    let hs: Vec<String> = hist.iter().enumerate().filter(|(_, c)| **c > 0).map(|(i, c)| format!("M{i}={c}")).collect();
    println!("OWN34_HIST|{}|json=0", hs.join("|"));
    for i in 0..k {
        // drain to the end of each file so that the hash covers it all, and check the lengths.
        let extra = rd[i].i64().is_some();
        while rd[i].fill() && { rd[i].pos = rd[i].end; rd[i].fill() } {}
        let sha = std::mem::replace(&mut rd[i].sha, Sha::new()).hex();
        println!("OWN34_D|i={i}|file={}|sha256={sha}|d_min={}|d_max={}|argmax_row={}|nonpositive={}|flat_nonzero={}|extra_rows={extra}|L={}|json=0", names[i], d_min[i], d_max[i], arg_max[i], nonpos[i], flat_nonzero[i], l[i].show());
    }
    for a in 0..k { for b in a..k {
        println!("OWN34_FORM|a={a}|b={b}|G={}|M={}|json=0", g[a * k + b].show(), m[a * k + b].show());
    } }
    println!("OWN34_REBUILD|x3a_factor={fa}|x3a_bad_rows={bad_a}|x3b_factor={fb}|x3b_bad_rows={bad_b}|json=0");
    println!("OWN34_PREDICT|x3a_min={:?}|x3a_at_tight={at_a}|x3b_min={:?}|x3b_at_tight={at_b}|json=0", pred_a, pred_b);
}
