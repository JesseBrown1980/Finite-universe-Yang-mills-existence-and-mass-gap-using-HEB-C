// Every row of the 3x3 store rebuilt from the definition of H by my own code, compared in full. Also exact W-symmetry on all pairs. Integer only.
// usage: own33_rebuild DEV PASSA THREADS
use std::io::Read;

const LX: usize = 3;
const LY: usize = 3;
const V: usize = LX * LY;
const NL: usize = 2 * V;

fn site(x: i32, y: i32) -> usize { (x.rem_euclid(LX as i32) as usize) * LY + y.rem_euclid(LY as i32) as usize }
fn xl(x: i32, y: i32) -> usize { site(x, y) }
fn yl(x: i32, y: i32) -> usize { V + site(x, y) }

struct G {
    mul: [[u8; 6]; 6], inv: [u8; 6], cost: [u8; 6], conj: [[u8; 6]; 6], tr: [u8; 3],
    free: Vec<usize>, steps: Vec<(usize, usize, usize)>, ends: [(usize, usize); NL], ops: Vec<[(u8, bool); NL]>, plaq: Vec<[usize; 4]>,
}

fn setup() -> G {
    let p: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
    let idx = |q: [u8; 3]| p.iter().position(|r| *r == q).unwrap() as u8;
    let mut mul = [[0u8; 6]; 6];
    for a in 0..6 { for b in 0..6 {
        mul[a][b] = idx([p[a][p[b][0] as usize], p[a][p[b][1] as usize], p[a][p[b][2] as usize]]);
    } }
    let mut inv = [0u8; 6];
    for a in 0..6 { for b in 0..6 { if mul[a][b] == 0 { inv[a] = b as u8; } } }
    let mut cost = [0u8; 6];
    let mut tr = Vec::new();
    for a in 0..6 {
        let fixed = (0..3).filter(|&k| p[a][k] == k as u8).count() as i32;
        cost[a] = (2 - (fixed - 1)) as u8;
        if fixed == 1 { tr.push(a as u8); }
    }
    let mut conj = [[0u8; 6]; 6];
    for c in 0..6 { for v in 0..6 { conj[c][v] = mul[mul[c][v] as usize][inv[c] as usize]; } }
    let mut ends = [(0usize, 0usize); NL];
    for x in 0..LX as i32 { for y in 0..LY as i32 {
        ends[xl(x, y)] = (site(x, y), site(x + 1, y));
        ends[yl(x, y)] = (site(x, y), site(x, y + 1));
    } }
    let mut in_tree = [false; NL];
    let mut steps = Vec::new();
    for y in 0..LY as i32 - 1 { in_tree[yl(0, y)] = true; steps.push((site(0, y), site(0, y + 1), yl(0, y))); }
    for x in 0..LX as i32 - 1 { for y in 0..LY as i32 { in_tree[xl(x, y)] = true; steps.push((site(x, y), site(x + 1, y), xl(x, y))); } }
    let free: Vec<usize> = (0..NL).filter(|&l| !in_tree[l]).collect();
    let mut ops = Vec::new();
    for fx in [false, true] { for fy in [false, true] { for tx in 0..LX as i32 { for ty in 0..LY as i32 {
        let mut d = [(0u8, false); NL];
        for x in 0..LX as i32 { for y in 0..LY as i32 {
            let (px, py) = (if fx { -x } else { x }, if fy { -y } else { y });
            d[xl(x, y)] = (xl(if fx { px - 1 } else { px } + tx, py + ty) as u8, fx);
            d[yl(x, y)] = (yl(px + tx, if fy { py - 1 } else { py } + ty) as u8, fy);
        } }
        ops.push(d);
    } } } }
    let mut plaq = Vec::new();
    for x in 0..LX as i32 { for y in 0..LY as i32 { plaq.push([xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)]); } }
    G { mul, inv, cost, conj, tr: [tr[0], tr[1], tr[2]], free, steps, ends, ops, plaq }
}

impl G {
    fn gauge_digits(&self, u: &[u8; NL], q: &mut [u8; 10]) {
        let mut h = [0u8; V];
        for &(t, hd, l) in &self.steps { h[hd] = self.mul[h[t] as usize][u[l] as usize]; }
        for (k, &l) in self.free.iter().enumerate() {
            let (a, b) = self.ends[l];
            q[k] = self.mul[self.mul[h[a] as usize][u[l] as usize] as usize][self.inv[h[b] as usize] as usize];
        }
    }
    fn canon(&self, u: &[u8; NL], collect: Option<&mut Vec<u64>>) -> u64 {
        let mut best = u64::MAX;
        let mut out = [0u8; NL];
        let mut q = [0u8; 10];
        let mut sink = collect;
        for op in &self.ops {
            for l in 0..NL { let (d, i) = op[l]; out[d as usize] = if i { self.inv[u[l] as usize] } else { u[l] }; }
            self.gauge_digits(&out, &mut q);
            for c in &self.conj {
                let mut code = 0u64;
                for k in (0..10).rev() { code = code * 6 + u64::from(c[q[k] as usize]); }
                if code < best { best = code; }
                if let Some(v) = sink.as_deref_mut() { v.push(code); }
            }
        }
        best
    }
    fn magnetic(&self, u: &[u8; NL]) -> u32 {
        let mut m = 0;
        for p in &self.plaq {
            let z = self.mul[self.mul[self.mul[u[p[0]] as usize][u[p[1]] as usize] as usize][self.inv[u[p[2]] as usize] as usize] as usize][self.inv[u[p[3]] as usize] as usize];
            m += u32::from(self.cost[z as usize]);
        }
        m
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let mut b = Vec::new();
    std::fs::File::open(&a[1]).unwrap().read_to_end(&mut b).unwrap();
    let nl = b.iter().position(|&c| c == b'\n').unwrap();
    let line = String::from_utf8_lossy(&b[..nl]).to_string();
    let n: usize = line.split('|').find_map(|kv| kv.strip_prefix("n=")).unwrap().parse().unwrap();
    let data = &b[4096..];
    let mut pa = Vec::new();
    std::fs::File::open(&a[2]).unwrap().read_to_end(&mut pa).unwrap();
    assert_eq!(pa.len(), 16 * n);
    let keys: Vec<u64> = (0..n).map(|h| u64::from_le_bytes(pa[16 * h..16 * h + 8].try_into().unwrap())).collect();
    assert!(keys.windows(2).all(|w| w[0] < w[1]));
    let mut starts = Vec::with_capacity(n + 1);
    let mut pos = 0usize;
    let (mut max_cnt, mut max_abs_sum, mut max_diag, mut not_ascending) = (0usize, 0i64, 0i64, 0u64);
    let mut weights = vec![0u32; n];
    for h in 0..n {
        starts.push(pos);
        weights[h] = u32::from_le_bytes(data[pos..pos + 4].try_into().unwrap());
        let cnt = u16::from_le_bytes(data[pos + 6..pos + 8].try_into().unwrap()) as usize;
        max_cnt = max_cnt.max(cnt);
        let mut s = 0i64;
        let mut prev = -1i64;
        for e in data[pos + 8..pos + 8 + 8 * cnt].chunks_exact(8) {
            let j = u32::from_le_bytes(e[0..4].try_into().unwrap());
            let z = i32::from_le_bytes(e[4..8].try_into().unwrap());
            s += i64::from(z.abs());
            if i64::from(j) <= prev { not_ascending += 1; }
            prev = i64::from(j);
            if j as usize == h { max_diag = max_diag.max(i64::from(z)); }
        }
        max_abs_sum = max_abs_sum.max(s);
        pos += 8 + 8 * cnt;
    }
    starts.push(pos);
    // Exact W-symmetry, every entry against its mirror.
    let entry = |h: usize, j: usize| -> i32 {
        let cnt = (starts[h + 1] - starts[h] - 8) / 8;
        let body = &data[starts[h] + 8..starts[h + 1]];
        let (mut lo, mut hi) = (0usize, cnt);
        while lo < hi {
            let mid = (lo + hi) / 2;
            let col = u32::from_le_bytes(body[8 * mid..8 * mid + 4].try_into().unwrap()) as usize;
            if col == j { return i32::from_le_bytes(body[8 * mid + 4..8 * mid + 8].try_into().unwrap()); }
            if col < j { lo = mid + 1; } else { hi = mid; }
        }
        0
    };
    let mut bad_pairs = 0u64;
    let mut pairs = 0u64;
    for h in 0..n {
        for e in data[starts[h] + 8..starts[h + 1]].chunks_exact(8) {
            let j = u32::from_le_bytes(e[0..4].try_into().unwrap()) as usize;
            let z = i32::from_le_bytes(e[4..8].try_into().unwrap());
            pairs += 1;
            if i64::from(weights[h]) * i64::from(z) != i64::from(weights[j]) * i64::from(entry(j, h)) { bad_pairs += 1; }
        }
    }
    println!("OWN33_STRUCT|n={n}|entries={pairs}|W_symmetry_bad_entries={bad_pairs}|max_cnt={max_cnt}|max_sum_abs_z={max_abs_sum}|max_diag={max_diag}|not_ascending={not_ascending}|json=0");
    let g = setup();
    println!("OWN33_GROUP|free_links={}|ops={}|json=0", g.free.len(), g.ops.len());
    let threads: usize = a[3].parse().unwrap();
    let t0 = std::time::Instant::now();
    let (keysr, gr, datar, startsr, par) = (&keys, &g, data, &starts, &pa);
    let res: Vec<(u64, u64, u64, u64, u64)> = std::thread::scope(|sc| {
        let hs: Vec<_> = (0..threads).map(|t| sc.spawn(move || {
            let (mut bad_w, mut bad_m, mut bad_e, mut bad_key, mut done) = (0u64, 0u64, 0u64, 0u64, 0u64);
            let mut codes = Vec::with_capacity(216);
            let mut hit: Vec<(u32, i32)> = Vec::with_capacity(60);
            for h in (t..n).step_by(threads) {
                let mut key = keysr[h];
                let mut u = [0u8; NL];
                for &l in &gr.free { u[l] = (key % 6) as u8; key /= 6; }
                codes.clear();
                let c = gr.canon(&u, Some(&mut codes));
                if c != keysr[h] { bad_key += 1; }
                codes.sort_unstable();
                codes.dedup();
                let w_store = u32::from_le_bytes(datar[startsr[h]..startsr[h] + 4].try_into().unwrap());
                let m_store = u32::from(u16::from_le_bytes(datar[startsr[h] + 4..startsr[h] + 6].try_into().unwrap()));
                let w_pa = u32::from_le_bytes(par[16 * h + 8..16 * h + 12].try_into().unwrap());
                let m_pa = u32::from_le_bytes(par[16 * h + 12..16 * h + 16].try_into().unwrap());
                if codes.len() as u32 != w_store || w_store != w_pa { bad_w += 1; }
                let m = gr.magnetic(&u);
                if m != m_store || m != m_pa { bad_m += 1; }
                hit.clear();
                let mut back = 0i32;
                for l in 0..NL {
                    let old = u[l];
                    for &tau in &gr.tr {
                        u[l] = gr.mul[tau as usize][old as usize];
                        let kk = gr.canon(&u, None);
                        match keysr.binary_search(&kk) {
                            Ok(j) if j == h => back += 1,
                            Ok(j) => hit.push((j as u32, -1)),
                            Err(_) => { bad_e += 1; }
                        }
                    }
                    u[l] = old;
                }
                hit.push((h as u32, (3 * NL) as i32 - back));
                hit.sort_unstable_by_key(|x| x.0);
                // merge
                let mut merged: Vec<(u32, i32)> = Vec::with_capacity(hit.len());
                for &(j, z) in hit.iter() {
                    if let Some(last) = merged.last_mut() { if last.0 == j { last.1 += z; continue; } }
                    merged.push((j, z));
                }
                let body = &datar[startsr[h] + 8..startsr[h + 1]];
                let stored: Vec<(u32, i32)> = body.chunks_exact(8).map(|e| (u32::from_le_bytes(e[0..4].try_into().unwrap()), i32::from_le_bytes(e[4..8].try_into().unwrap()))).filter(|e| e.1 != 0).collect();
                let mine: Vec<(u32, i32)> = merged.into_iter().filter(|e| e.1 != 0).collect();
                if stored != mine { bad_e += 1; }
                done += 1;
            }
            (done, bad_key, bad_w, bad_m, bad_e)
        })).collect();
        hs.into_iter().map(|h| h.join().unwrap()).collect()
    });
    let sum = res.iter().fold((0, 0, 0, 0, 0), |a, b| (a.0 + b.0, a.1 + b.1, a.2 + b.2, a.3 + b.3, a.4 + b.4));
    println!("OWN33_REBUILD|rows_rebuilt={}|canonical_key_mismatch={}|weight_mismatch={}|M_mismatch={}|entries_mismatch={}|secs={}|json=0", sum.0, sum.1, sum.2, sum.3, sum.4, t0.elapsed().as_secs());
}
