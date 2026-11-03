//! prodvec: tests a Perron vector with few parameters on an S3 room store.
//!
//! A row's lump is (a, b): a plaquettes whose holonomy is a transposition and b whose holonomy is a 3-cycle, so M = 2a + 3b.
//! Here d depends on a row through its lump alone. Two forms:
//!   lump     one free value per lump
//!   product  d = eps^a eta^b, two numbers
//!
//! `census` reads every row once and keeps what the ratio of `perroncert check` needs for any such d: the lump, the diagonal,
//! and how many moves lead into each lump. `fit` maximizes the minimum ratio over those signatures, and `write` puts the vector
//! in the format of `perroncert check`, which then decides the value on every row with no help from this tool.
//!
//!   prodvec census DEV OFFSET PASSA LX LY TABLE
//!   prodvec fit TABLE JE JB lump|product G_OUT
//!   prodvec write PASSA LX LY G_IN D_OUT
//!
//! PASSA holds 16 bytes per row: key u64, weight u32, M u32. Integer only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

#[allow(dead_code)]
#[path = "../../../torusl/src/segio.rs"]
mod segio;
#[allow(dead_code)]
#[path = "../../../torusl/src/sha.rs"]
mod sha;
#[allow(dead_code)]
#[path = "../../../torusl/src/roomio.rs"]
mod roomio;

use std::collections::{BTreeMap, HashMap};
use std::io::Write;

/// g values live in fixed point with this many bits, the largest in [2^(TOP-1), 2^TOP).
const TOP: u32 = 90;
/// eps and eta of the product form, in fixed point.
const PARAM_BITS: u32 = 30;
/// The largest d written.
const D_TOP: u32 = 60;
const SWEEPS: usize = 2000;
const NO_LUMP: u16 = u16::MAX;

/// The lump id of every row, and the (a, b) of every id.
type Lumps = (Vec<u16>, Vec<(u8, u8)>);

struct Lattice {
    nl: usize,
    free: Vec<usize>,
    plaq: Vec<[usize; 4]>,
    mul: [[u8; 6]; 6],
    inv: [u8; 6],
    cost: [u8; 6],
}

impl Lattice {
    /// The comb gauge of `ymroom`: free links in ascending link order, each a base-6 digit of the key, lowest first.
    fn new(lx: usize, ly: usize) -> Lattice {
        let v = lx * ly;
        let nl = 2 * v;
        let site = |x: usize, y: usize| (x % lx) * ly + y % ly;
        let xl = |x: usize, y: usize| site(x, y);
        let yl = |x: usize, y: usize| v + site(x, y);
        const P: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
        let mut mul = [[0u8; 6]; 6];
        let mut inv = [0u8; 6];
        let mut cost = [0u8; 6];
        for (a, pa) in P.iter().enumerate() {
            for (b, pb) in P.iter().enumerate() {
                let t = [pa[pb[0] as usize], pa[pb[1] as usize], pa[pb[2] as usize]];
                mul[a][b] = P.iter().position(|q| *q == t).map_or(255, |i| i as u8);
                if mul[a][b] == 0 {
                    inv[a] = b as u8;
                }
            }
            cost[a] = (0..3).filter(|&k| pa[k] != k as u8).count() as u8;
        }
        let mut tree = vec![false; nl];
        for y in 0..ly - 1 {
            tree[yl(0, y)] = true;
        }
        for x in 0..lx - 1 {
            for y in 0..ly {
                tree[xl(x, y)] = true;
            }
        }
        let free = (0..nl).filter(|&l| !tree[l]).collect();
        let mut plaq = Vec::with_capacity(v);
        for x in 0..lx {
            for y in 0..ly {
                plaq.push([xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)]);
            }
        }
        Lattice { nl, free, plaq, mul, inv, cost }
    }

    fn lump(&self, mut key: u64) -> (u8, u8) {
        let mut u = vec![0u8; self.nl];
        for &l in &self.free {
            u[l] = (key % 6) as u8;
            key /= 6;
        }
        let (mut a, mut b) = (0u8, 0u8);
        for p in &self.plaq {
            let z = self.mul[self.mul[self.mul[u[p[0]] as usize][u[p[1]] as usize] as usize][self.inv[u[p[2]] as usize] as usize] as usize][self.inv[u[p[3]] as usize] as usize];
            match self.cost[z as usize] {
                2 => a += 1,
                3 => b += 1,
                _ => {}
            }
        }
        (a, b)
    }
}

/// Reads the lump of every row, fails if 2a + 3b differs from the stored M.
fn read_lumps(path: &str, lat: &Lattice) -> Result<Lumps, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("read {path}: {e}"))?;
    if bytes.len() % 16 != 0 {
        return Err("PASSA is not 16 bytes per row".into());
    }
    let mut ids: BTreeMap<(u8, u8), u16> = BTreeMap::new();
    let mut lump = Vec::with_capacity(bytes.len() / 16);
    for r in bytes.chunks_exact(16) {
        let key = u64::from_le_bytes([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]]);
        let m = u32::from_le_bytes([r[12], r[13], r[14], r[15]]);
        let (a, b) = lat.lump(key);
        if 2 * u32::from(a) + 3 * u32::from(b) != m {
            return Err(format!("row {}: a={a} b={b} gives another M than {m}", lump.len()));
        }
        let next = ids.len() as u16;
        lump.push(*ids.entry((a, b)).or_insert(next));
    }
    let mut names = vec![(0u8, 0u8); ids.len()];
    for (k, v) in &ids {
        names[*v as usize] = *k;
    }
    Ok((lump, names))
}

fn census(a: &[String]) -> Result<String, String> {
    let (spec, off, passa, lx, ly, out) = (&a[2], num::<u64>(&a[3])?, &a[4], num::<usize>(&a[5])?, num::<usize>(&a[6])?, &a[7]);
    let lat = Lattice::new(lx, ly);
    let (lump, names) = read_lumps(passa, &lat)?;
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    if hdr.n != lump.len() {
        return Err(format!("store has {} rows, PASSA {}", hdr.n, lump.len()));
    }
    let flat = names.iter().position(|n| *n == (0, 0)).map_or(NO_LUMP, |i| i as u16);
    let mut rows_of = vec![0u64; names.len()];
    let mut table: HashMap<Vec<u16>, (u64, u32)> = HashMap::new();
    let mut count = vec![0u16; names.len()];
    let mut touched: Vec<u16> = Vec::new();
    let mut key: Vec<u16> = Vec::new();
    let (mut bad_sign, mut no_diag, mut bad_mag) = (0u64, 0u64, 0u64);
    roomio::stream(&mut dev, off, &hdr, |h, row| {
        let id = lump[h];
        rows_of[id as usize] += 1;
        let (na, nb) = names[id as usize];
        bad_mag += u64::from(u32::from(row.mag) != 2 * u32::from(na) + 3 * u32::from(nb));
        if id == flat {
            return;
        }
        let (mut diag, mut to_flat, mut has_diag) = (0u16, 0u16, false);
        touched.clear();
        for (j, z) in row.entries() {
            if j == h {
                diag = z.max(0) as u16;
                has_diag = true;
                continue;
            }
            bad_sign += u64::from(z >= 0);
            let moves = (-z).max(0) as u16;
            let t = lump[j];
            if t == flat {
                to_flat += moves;
            } else {
                if count[t as usize] == 0 {
                    touched.push(t);
                }
                count[t as usize] += moves;
            }
        }
        no_diag += u64::from(!has_diag);
        touched.sort_unstable();
        key.clear();
        key.extend_from_slice(&[id, diag, to_flat]);
        for &t in &touched {
            key.push(t);
            key.push(count[t as usize]);
            count[t as usize] = 0;
        }
        if let Some(e) = table.get_mut(key.as_slice()) {
            e.0 += 1;
        } else {
            table.insert(key.clone(), (1, h as u32));
        }
    })?;
    if bad_sign > 0 || no_diag > 0 || bad_mag > 0 {
        return Err(format!("the rows break the form this tool assumes: positive off-diagonal {bad_sign}, no diagonal {no_diag}, M against the lump {bad_mag}"));
    }
    let mut f = std::io::BufWriter::new(std::fs::File::create(out).map_err(|e| e.to_string())?);
    for (i, (na, nb)) in names.iter().enumerate() {
        writeln!(f, "LUMP|id={i}|a={na}|b={nb}|rows={}|json=0", rows_of[i]).map_err(|e| e.to_string())?;
    }
    let mut sorted: Vec<(&Vec<u16>, &(u64, u32))> = table.iter().collect();
    sorted.sort();
    for (k, v) in &sorted {
        let n: Vec<String> = k[3..].chunks_exact(2).map(|p| format!("{}:{}", p[0], p[1])).collect();
        writeln!(f, "SIG|lump={}|diag={}|flat={}|rows={}|row={}|n={}|json=0", k[0], k[1], k[2], v.0, v.1, n.join(",")).map_err(|e| e.to_string())?;
    }
    f.flush().map_err(|e| e.to_string())?;
    let a_odd: u64 = names.iter().zip(&rows_of).filter(|(n, _)| n.0 % 2 == 1).map(|(_, r)| *r).sum();
    Ok(format!(
        "PRODVEC_CENSUS|L={}|n={}|rows_read={}|lumps={}|signatures={}|rows_with_a_odd={a_odd}|merkle=PASS|table_sha256={}|json=0",
        hdr.lattice,
        hdr.n,
        rows_of.iter().sum::<u64>(),
        names.len(),
        sorted.len(),
        sha::sha256_hex(&std::fs::read(out).map_err(|e| e.to_string())?)
    ))
}

fn num<T: std::str::FromStr>(s: &str) -> Result<T, String> {
    s.parse().map_err(|_| format!("bad number {s}"))
}

struct Sig {
    lump: usize,
    /// (JB M + JE diag) * 1000: the ratio with no neighbours, in the units of perroncert's t_milli.
    base: i128,
    rows: u64,
    row: u32,
    near: Vec<(u16, u16)>,
    /// Moves into the row's own lump.
    own: u16,
}

struct Table {
    names: Vec<(u8, u8)>,
    sigs: Vec<Sig>,
    /// Signatures of each lump, and the lumps in ascending M.
    of: Vec<Vec<usize>>,
    order: Vec<usize>,
    unit: u128,
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

fn read_table(path: &str, je: i128, jb: i128) -> Result<Table, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let mut names = Vec::new();
    let mut sigs = Vec::new();
    for line in text.lines() {
        let need = |k: &str| field(line, k).ok_or_else(|| format!("no {k} in {line}"));
        if line.starts_with("LUMP|") {
            names.push((num::<u8>(need("a=")?)?, num::<u8>(need("b=")?)?));
        } else if line.starts_with("SIG|") {
            let lump: usize = num(need("lump=")?)?;
            let diag: i128 = num(need("diag=")?)?;
            let (na, nb) = names[lump];
            let m = 2 * i128::from(na) + 3 * i128::from(nb);
            let mut near = Vec::new();
            let mut own = 0u16;
            let list = need("n=")?;
            if !list.is_empty() {
                for p in list.split(',') {
                    let (i, c) = p.split_once(':').ok_or("bad neighbour")?;
                    let (i, c): (u16, u16) = (num(i)?, num(c)?);
                    if i as usize == lump {
                        own = c;
                    } else {
                        near.push((i, c));
                    }
                }
            }
            sigs.push(Sig { lump, base: 1000 * (jb * m + je * diag), rows: num(need("rows=")?)?, row: num(need("row=")?)?, near, own });
        }
    }
    let mut of = vec![Vec::new(); names.len()];
    for (i, s) in sigs.iter().enumerate() {
        of[s.lump].push(i);
    }
    let mut order: Vec<usize> = (0..names.len()).filter(|&i| !of[i].is_empty()).collect();
    order.sort_by_key(|&i| (2 * u32::from(names[i].0) + 3 * u32::from(names[i].1), names[i]));
    let unit = u128::try_from(1000 * je).map_err(|_| "bad JE")?;
    Ok(Table { names, sigs, of, order, unit })
}

impl Table {
    /// min over the signatures of the ratio of `perroncert check` for this g, rounded down, and its signature.
    fn t_of(&self, g: &[u128]) -> (i128, usize) {
        let mut best = (i128::MAX, 0usize);
        for (i, s) in self.sigs.iter().enumerate() {
            let own = u128::from(s.own) * g[s.lump];
            let sum: u128 = s.near.iter().map(|&(k, c)| u128::from(c) * g[k as usize]).sum::<u128>() + own;
            let t = s.base - ((self.unit * sum).div_ceil(g[s.lump]) as i128);
            if t < best.0 {
                best = (t, i);
            }
        }
        best
    }

    /// One Gauss-Seidel sweep of g_L = max over its signatures of (moves out of the lump, weighted by g) / (its diagonal less t).
    /// None when a denominator is not positive, so that no g of this form reaches t.
    fn sweep(&self, g: &mut [u128], t: i128) -> Option<u128> {
        let mut change = 0u128;
        for &l in &self.order {
            let mut top = 0u128;
            for &i in &self.of[l] {
                let s = &self.sigs[i];
                let den = s.base - i128::from(s.own) * self.unit as i128 - t;
                if den <= 0 {
                    return None;
                }
                let sum: u128 = s.near.iter().map(|&(k, c)| u128::from(c) * g[k as usize]).sum();
                top = top.max(self.unit * sum / den as u128);
            }
            let new = top.max(1);
            change = change.max(new.abs_diff(g[l]) >> 24);
            g[l] = new;
        }
        // Only the lumps with a value set the scale. The flat lump stays at 1.
        let top = self.order.iter().map(|&l| g[l]).max().unwrap_or(1).max(1);
        let bits = 128 - top.leading_zeros();
        for &l in &self.order {
            g[l] = if bits > TOP { g[l] >> (bits - TOP) } else { g[l] << (TOP - bits) }.max(1);
        }
        Some(change)
    }

    fn fit_lump(&self) -> (Vec<u128>, i128, usize) {
        // The flat lump has no signature and no value, so it must not set the scale.
        let g: Vec<u128> = self.of.iter().map(|sigs| if sigs.is_empty() { 1 } else { 1u128 << (TOP - 1) }).collect();
        let (mut lo, mut hi) = (0i128, self.sigs.iter().map(|s| s.base).min().unwrap_or(0));
        let mut best = (g.clone(), i128::MIN, 0usize);
        while hi - lo > 100 {
            let t = (lo + hi) / 2;
            let mut trial = best.0.clone();
            let mut feasible = true;
            let mut sweeps = 0;
            for _ in 0..SWEEPS {
                sweeps += 1;
                match self.sweep(&mut trial, t) {
                    None => {
                        feasible = false;
                        break;
                    }
                    Some(0) => break,
                    Some(_) => {}
                }
            }
            let (got, at) = if feasible { self.t_of(&trial) } else { (i128::MIN, 0) };
            println!("PRODVEC_BISECT|t_tried={t}|feasible_form={feasible}|sweeps={sweeps}|t_reached={got}|json=0");
            if got > best.1 {
                best = (trial, got, at);
            }
            // A sweep leaves every lump tight at t when g exists, and rounding down takes one or two units. When no g reaches t, the shortfall is larger.
            if got + 2 >= t {
                lo = t;
            } else {
                hi = t;
            }
        }
        best
    }

    fn product(&self, eps: u128, eta: u128) -> Vec<u128> {
        let mut g: Vec<u128> = self
            .names
            .iter()
            .map(|&(na, nb)| {
                let mut v = 1u128 << (TOP - 1);
                for _ in 0..na {
                    v = (v * eps) >> PARAM_BITS;
                }
                for _ in 0..nb {
                    v = (v * eta) >> PARAM_BITS;
                }
                v.max(1)
            })
            .collect();
        normalize(&mut g);
        g
    }

    fn fit_product(&self) -> (Vec<u128>, i128, usize, u128, u128) {
        // Concave in the logarithms of eps and eta, so a descent over eight directions with a shrinking step has no other optimum to stop at.
        let (mut eps, mut eta) = (1u128 << (PARAM_BITS - 2), 1u128 << (PARAM_BITS - 3));
        let mut g = self.product(eps, eta);
        let (mut t, mut at) = self.t_of(&g);
        for shift in 2..=22u32 {
            loop {
                let mut moved = false;
                for (de, dn) in [(1i32, 0i32), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)] {
                    let step = |v: u128, d: i32| match d {
                        1 => v + (v >> shift),
                        -1 => v - (v >> shift),
                        _ => v,
                    };
                    let (e2, n2) = (step(eps, de), step(eta, dn));
                    let g2 = self.product(e2, n2);
                    let (t2, at2) = self.t_of(&g2);
                    if t2 > t {
                        (eps, eta, g, t, at) = (e2, n2, g2, t2, at2);
                        moved = true;
                    }
                }
                if !moved {
                    break;
                }
            }
        }
        (g, t, at, eps, eta)
    }
}

fn normalize(g: &mut [u128]) {
    let top = g.iter().copied().max().unwrap_or(1).max(1);
    let bits = 128 - top.leading_zeros();
    for v in g.iter_mut() {
        *v = if bits > TOP { *v >> (bits - TOP) } else { *v << (TOP - bits) };
        *v = (*v).max(1);
    }
}

fn fit(a: &[String]) -> Result<String, String> {
    let (path, je, jb, form, out) = (&a[2], num::<i128>(&a[3])?, num::<i128>(&a[4])?, a[5].as_str(), &a[6]);
    let tb = read_table(path, je, jb)?;
    let (g, t, at, extra) = match form {
        "lump" => {
            let (g, t, at) = tb.fit_lump();
            (g, t, at, String::new())
        }
        "product" => {
            let (g, t, at, eps, eta) = tb.fit_product();
            (g, t, at, format!("eps_q30={eps}|eta_q30={eta}|"))
        }
        _ => return Err("form must be lump or product".into()),
    };
    let s = &tb.sigs[at];
    let (ta, tb_b) = tb.names[s.lump];
    let mut f = std::io::BufWriter::new(std::fs::File::create(out).map_err(|e| e.to_string())?);
    for (i, (na, nb)) in tb.names.iter().enumerate() {
        writeln!(f, "G|id={i}|a={na}|b={nb}|g={}|json=0", g[i]).map_err(|e| e.to_string())?;
    }
    f.flush().map_err(|e| e.to_string())?;
    let refg = tb.names.iter().position(|n| *n == (0, 1)).map_or(1, |i| g[i]);
    for &l in tb.order.iter().take(14) {
        let (na, nb) = tb.names[l];
        println!("PRODVEC_G|a={na}|b={nb}|M={}|g_over_g_of_one_3_cycle_ppm={}|json=0", 2 * u32::from(na) + 3 * u32::from(nb), g[l] * 1_000_000 / refg);
    }
    Ok(format!(
        "PRODVEC_FIT|form={form}|JE={je}|JB={jb}|t_on_the_table_milli={t}|{extra}tight_a={ta}|tight_b={tb_b}|tight_rows={}|tight_row={}|signatures={}|lumps={}|json=0",
        s.rows,
        s.row,
        tb.sigs.len(),
        tb.names.len()
    ))
}

fn write_d(a: &[String]) -> Result<String, String> {
    let (passa, lx, ly, gin, out) = (&a[2], num::<usize>(&a[3])?, num::<usize>(&a[4])?, &a[5], &a[6]);
    let lat = Lattice::new(lx, ly);
    let (lump, names) = read_lumps(passa, &lat)?;
    let text = std::fs::read_to_string(gin).map_err(|e| e.to_string())?;
    let mut by: HashMap<(u8, u8), u128> = HashMap::new();
    for line in text.lines() {
        let need = |k: &str| field(line, k).ok_or_else(|| format!("no {k}"));
        by.insert((num(need("a=")?)?, num(need("b=")?)?), num(need("g=")?)?);
    }
    let top = by.values().copied().max().ok_or("no g")?;
    let bits = 128 - top.leading_zeros();
    let shift = bits.saturating_sub(D_TOP);
    let value: Vec<i64> = names.iter().map(|n| if *n == (0, 0) { Ok(0) } else { by.get(n).map(|g| ((g >> shift).max(1)) as i64).ok_or("lump with no g") }).collect::<Result<_, _>>()?;
    let mut bytes = Vec::with_capacity(lump.len() * 8);
    for &id in &lump {
        bytes.extend_from_slice(&value[id as usize].to_le_bytes());
    }
    std::fs::write(out, &bytes).map_err(|e| e.to_string())?;
    Ok(format!("PRODVEC_WRITE|rows={}|parameters={}|d_max={}|d_sha256={}|json=0", lump.len(), names.len(), value.iter().max().copied().unwrap_or(0), sha::sha256_hex(&bytes)))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let r = match (a.get(1).map(String::as_str), a.len()) {
        (Some("census"), 8) => census(&a),
        (Some("fit"), 7) => fit(&a),
        (Some("write"), 7) => write_d(&a),
        _ => Err("usage: prodvec census DEV OFFSET PASSA LX LY TABLE | fit TABLE JE JB lump|product G_OUT | write PASSA LX LY G_IN D_OUT".into()),
    };
    match r {
        Ok(line) => println!("{line}"),
        Err(e) => {
            println!("PRODVEC_ERROR|{}|json=0", e.replace('|', "/"));
            std::process::exit(2);
        }
    }
}
