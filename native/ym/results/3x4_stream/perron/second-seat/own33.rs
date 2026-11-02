// C1 on 3x3: own proposals for the Perron vector of H', own exact evaluation. Integer only: i128 vectors, exact Barta floors, exact Rayleigh numerator and denominator.
// Own reader of the store format. Nothing from the tools. No proposal step decides anything: only `eval` rows do, and they are exact.
//   own33 DEV cheb JB A_MILLI B_MILLI STEPS OUT      Chebyshev filter from the uniform vector, printing exact rows now and then.
//   own33 DEV polish JB IN T_MILLI EPS_BITS SWEEPS OUT   Gauss-Seidel on (H'-t) x = in + eps, from the start in * scale.
//   own33 DEV eval JB IN                              exact rows only
use std::io::Read;

struct S { n: usize, keep: Vec<u32>, w: Vec<u32>, m: Vec<u16>, ptr: Vec<u32>, col: Vec<u32>, val: Vec<i32>, diag: Vec<i64> }

fn load(p: &str) -> S {
    let mut b = Vec::new();
    std::fs::File::open(p).unwrap().read_to_end(&mut b).unwrap();
    let nl = b.iter().position(|&c| c == b'\n').unwrap();
    let line = String::from_utf8_lossy(&b[..nl]).to_string();
    let get = |k: &str| line.split('|').find_map(|kv| kv.strip_prefix(k)).unwrap().parse::<usize>().unwrap();
    let n = get("n=");
    let data = &b[4096..];
    // First walk: flats.
    let mut pos = 0usize;
    let mut starts = Vec::with_capacity(n);
    let mut flat = vec![false; n];
    for h in 0..n {
        starts.push(pos);
        let mag = u16::from_le_bytes([data[pos + 4], data[pos + 5]]);
        let cnt = u16::from_le_bytes([data[pos + 6], data[pos + 7]]) as usize;
        flat[h] = mag == 0;
        pos += 8 + 8 * cnt;
    }
    let mut map = vec![u32::MAX; n];
    let mut keep = Vec::new();
    for h in 0..n { if !flat[h] { map[h] = keep.len() as u32; keep.push(h as u32); } }
    let k = keep.len();
    let (mut w, mut m, mut ptr, mut col, mut val, mut diag) = (Vec::with_capacity(k), Vec::with_capacity(k), Vec::with_capacity(k + 1), Vec::new(), Vec::new(), Vec::with_capacity(k));
    ptr.push(0u32);
    let (mut pos_off, mut sum_bad) = (0u64, 0u64);
    for &h in &keep {
        let p = starts[h as usize];
        let wt = u32::from_le_bytes([data[p], data[p + 1], data[p + 2], data[p + 3]]);
        let mag = u16::from_le_bytes([data[p + 4], data[p + 5]]);
        let cnt = u16::from_le_bytes([data[p + 6], data[p + 7]]) as usize;
        let mut d = 0i64;
        let mut rs = 0i64;
        for e in data[p + 8..p + 8 + 8 * cnt].chunks_exact(8) {
            let j = u32::from_le_bytes([e[0], e[1], e[2], e[3]]);
            let z = i32::from_le_bytes([e[4], e[5], e[6], e[7]]);
            rs += i64::from(z);
            if j == h { d = i64::from(z); continue; }
            if z > 0 { pos_off += 1; }
            if map[j as usize] != u32::MAX && z != 0 { col.push(map[j as usize]); val.push(z); }
        }
        if rs != 0 { sum_bad += 1; }
        w.push(wt); m.push(mag); diag.push(d); ptr.push(col.len() as u32);
    }
    println!("LOAD|n={n}|nonflat={k}|entries_kept={}|pos_off={pos_off}|row_sum_bad={sum_bad}|json=0", col.len());
    S { n: k, keep, w, m, ptr, col, val, diag }
}

fn matvec(s: &S, jb: i128, x: &[i128], out: &mut [i128]) {
    let u = 1_000_000i128;
    let v = 1000 * jb;
    for h in 0..s.n {
        let mut t = (u * i128::from(s.diag[h]) + v * i128::from(s.m[h])) * x[h];
        let mut off = 0i128;
        for e in s.ptr[h] as usize..s.ptr[h + 1] as usize {
            off += i128::from(s.val[e]) * x[s.col[e] as usize];
        }
        t += u * off;
        out[h] = t;
    }
}

fn mul_u(a: u128, b: u128) -> (u128, u128) {
    let mk = u128::from(u64::MAX);
    let (a0, a1, b0, b1) = (a & mk, a >> 64, b & mk, b >> 64);
    let (p00, p01, p10, p11) = (a0 * b0, a0 * b1, a1 * b0, a1 * b1);
    let mid = (p00 >> 64) + (p01 & mk) + (p10 & mk);
    ((p11 + (p01 >> 64) + (p10 >> 64) + (mid >> 64)), (p00 & mk) | (mid << 64))
}

#[derive(Default, Clone, Copy)]
struct W256 { hi: i128, lo: u128 }
impl W256 {
    fn add_mul(&mut self, a: i128, b: i128) {
        let neg = (a < 0) != (b < 0);
        let (h, l) = mul_u(a.unsigned_abs(), b.unsigned_abs());
        if neg {
            let (lo, br) = self.lo.overflowing_sub(l);
            self.lo = lo;
            self.hi -= h as i128 + i128::from(br);
        } else {
            let (lo, c) = self.lo.overflowing_add(l);
            self.lo = lo;
            self.hi += h as i128 + i128::from(c);
        }
    }
    fn show(&self) -> String { format!("{}:{}", self.hi, self.lo) }
}

fn eval(s: &S, jb: i128, x: &[i128], tag: &str) -> Option<i128> {
    let mut y = vec![0i128; s.n];
    matvec(s, jb, x, &mut y);
    let (mut a, mut g) = (W256::default(), W256::default());
    let mut np = 0u64;
    let mut best: Option<(i128, usize)> = None;
    let (mut mn, mut mx) = (i128::MAX, i128::MIN);
    for h in 0..s.n {
        let wx = i128::from(s.w[h]) * x[h];
        a.add_mul(wx, y[h]);
        g.add_mul(wx, x[h]);
        if x[h] <= 0 { np += 1; continue; }
        mn = mn.min(x[h]); mx = mx.max(x[h]);
        let q = y[h].div_euclid(x[h]);
        if best.map_or(true, |b| q < b.0) { best = Some((q, h)); }
    }
    let row = best.map_or(0, |b| s.keep[b.1]);
    let mag = best.map_or(0, |b| s.m[b.1]);
    println!("EVAL|{tag}|barta_floor={}|row={row}|M={mag}|nonpositive={np}|x_min={mn}|x_max={mx}|ray_num={}|ray_den={}|json=0", best.map_or(0, |b| b.0), a.show(), g.show());
    best.map(|b| b.0)
}

fn ray_quick(s: &S, jb: i128, x: &[i128]) -> i128 {
    // Progress only: drop bits so that an i128 sum holds.
    let mx = x.iter().map(|v| v.unsigned_abs()).max().unwrap_or(1).max(1);
    let bits = 128 - mx.leading_zeros() as i32;
    let sh = (bits - 28).max(0) as u32;
    let z: Vec<i128> = x.iter().map(|v| v >> sh).collect();
    let mut y = vec![0i128; s.n];
    matvec(s, jb, &z, &mut y);
    let (mut a, mut g) = (0i128, 0i128);
    for h in 0..s.n {
        let w = i128::from(s.w[h]);
        a += w * z[h] * y[h];
        g += w * z[h] * z[h];
    }
    a / g.max(1)
}

fn save(p: &str, x: &[i128]) {
    let mut b = Vec::with_capacity(x.len() * 16);
    for v in x { b.extend_from_slice(&v.to_le_bytes()); }
    std::fs::write(p, b).unwrap();
}
fn load_x(p: &str) -> Vec<i128> {
    std::fs::read(p).unwrap().chunks_exact(16).map(|c| { let mut t = [0u8; 16]; t.copy_from_slice(c); i128::from_le_bytes(t) }).collect()
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let s = load(&a[1]);
    let jb: i128 = a[3].parse().unwrap();
    let t0 = std::time::Instant::now();
    match a[2].as_str() {
        "cheb" => {
            let (lo_cut, hi_end): (i128, i128) = (a[4].parse().unwrap(), a[5].parse().unwrap());
            let steps: usize = a[6].parse().unwrap();
            let c = (lo_cut + hi_end) / 2;
            let e = (hi_end - lo_cut) / 2;
            let mut xm: Vec<i128> = vec![1i128 << 80; s.n];
            let mut x = xm.clone();
            let mut y = vec![0i128; s.n];
            // x_1 = A' x_0, A' = (c - H) / e
            matvec(&s, jb, &x, &mut y);
            for h in 0..s.n { x[h] = (c * xm[h] - y[h]) / e; }
            let half = e / 2;
            for k in 2..=steps {
                matvec(&s, jb, &x, &mut y);
                let mut big = 0u128;
                for h in 0..s.n {
                    let nx = (c * x[h] - y[h]) / half - xm[h];
                    xm[h] = x[h];
                    x[h] = nx;
                    big = big.max(nx.unsigned_abs());
                }
                if big >> 94 != 0 {
                    for h in 0..s.n { x[h] >>= 24; xm[h] >>= 24; }
                }
                if k % 100 == 0 || k == steps {
                    println!("CHEB|step={k}|ray_quick={}|secs={}|json=0", ray_quick(&s, jb, &x), t0.elapsed().as_secs());
                }
            }
            eval(&s, jb, &x, "cheb");
            save(&a[7], &x);
        }
        "polish" => {
            let inp = load_x(&a[4]);
            let t: i128 = a[5].parse().unwrap();
            let eps = 1i128 << a[6].parse::<u32>().unwrap();
            let sweeps: usize = a[7].parse().unwrap();
            let start_div: i128 = a[9].parse().unwrap();
            // b = in + eps; start x = b / start_div, with start_div the level minus t, the Perron part of the solution.
            let b: Vec<i128> = inp.iter().map(|&v| v.max(0) + eps).collect();
            let mut x: Vec<i128> = b.iter().map(|&v| v / start_div).collect();
            let u = 1_000_000i128;
            let vv = 1000 * jb;
            for sw in 1..=sweeps {
                let mut biggest = 0i128;
                for h in 0..s.n {
                    let diag = u * i128::from(s.diag[h]) + vv * i128::from(s.m[h]) - t;
                    let mut off = 0i128;
                    for e in s.ptr[h] as usize..s.ptr[h + 1] as usize {
                        off += i128::from(s.val[e]) * x[s.col[e] as usize];
                    }
                    let nx = (b[h] - u * off) / diag;
                    biggest = biggest.max((nx - x[h]).abs());
                    x[h] = nx;
                }
                if sw % 20 == 0 || sw == sweeps {
                    println!("POLISH|sweep={sw}|biggest_change={biggest}|secs={}|json=0", t0.elapsed().as_secs());
                    eval(&s, jb, &x, "polish");
                }
            }
            save(&a[8], &x);
        }
        "eval" => {
            let x = load_x(&a[4]);
            eval(&s, jb, &x, "eval");
        }
        _ => panic!("mode"),
    }
    let _ = s.keep.len();
}
