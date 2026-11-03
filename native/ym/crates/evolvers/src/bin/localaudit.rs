//! localaudit: exhaustive tests of the store-free table of results/3x4_stream/perron/vector/local_table.py, from the definition of H.
//!
//!   localaudit adjacency LX LY
//!     Over every set S of plaquettes, the largest number of links with both plaquettes in S, for each |S|, against the bound the table uses.
//!
//!   localaudit enumerate LX LY TABLE G JE JB T_MILLI MCUT THREADS
//!     Every gauge-fixed link configuration with M <= MCUT, by depth-first search that stops as soon as the finished plaquettes pass MCUT. For each one, each of the 3 nl moves is
//!     applied and the two plaquettes holding its link are recomputed from the links. Its row must be in TABLE, and its ratio under the vector G must be at least T_MILLI, in the units of
//!     perroncert's t_milli. Prints the count per lump, so that a control can compare it with a store's weights.
//!
//! Every count is exact. A failure prints its configuration and exits 2. Integer only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::{BTreeMap, HashMap, HashSet};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

const PERMS: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];

fn num<T: std::str::FromStr>(s: &str) -> Result<T, String> {
    s.parse().map_err(|_| format!("bad number {s}"))
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

fn ceil_two_sqrt(n: usize) -> usize {
    let mut v = 0;
    while v * v < 4 * n {
        v += 1;
    }
    v
}

fn adjacency(lx: usize, ly: usize) -> Result<String, String> {
    let p = lx * ly;
    if p > 30 {
        return Err("at most 30 plaquettes".into());
    }
    let at = |x: usize, y: usize| (x % lx) * ly + y % ly;
    let (mut right, mut up) = (vec![0usize; p], vec![0usize; p]);
    for x in 0..lx {
        for y in 0..ly {
            right[at(x, y)] = at(x + 1, y);
            up[at(x, y)] = at(x, y + 1);
        }
    }
    let shift = |mask: u64, to: &[usize]| {
        let mut out = 0u64;
        let mut m = mask;
        while m != 0 {
            let i = m.trailing_zeros() as usize;
            out |= 1u64 << to[i];
            m &= m - 1;
        }
        out
    };
    let mut most = vec![0u32; p + 1];
    for mask in 0..(1u64 << p) {
        let inner = (mask & shift(mask, &right)).count_ones() + (mask & shift(mask, &up)).count_ones();
        let s = mask.count_ones() as usize;
        most[s] = most[s].max(inner);
    }
    let (mut over, mut tight, mut slack_sum) = (0usize, 0usize, 0usize);
    let mut cells = Vec::new();
    for (s, &m) in most.iter().enumerate() {
        let bound = if s == 0 {
            0
        } else if s == p {
            2 * s
        } else {
            2 * s - ceil_two_sqrt(s).min(lx.min(ly)).min(ceil_two_sqrt(p - s))
        };
        over += usize::from(m as usize > bound);
        tight += usize::from(m as usize == bound);
        slack_sum += bound.saturating_sub(m as usize);
        cells.push(format!("{s}:{m}/{bound}"));
    }
    Ok(format!("AUDIT_ADJACENCY|Lx={lx}|Ly={ly}|subsets={}|sizes_over_the_bound={over}|sizes_at_the_bound={tight}|total_slack={slack_sum}|size_most_bound={}|json=0", 1u64 << p, cells.join(",")))
}

struct Lattice {
    nl: usize,
    mul: [[u8; 6]; 6],
    inv: [u8; 6],
    kind: [u8; 6],
    trans: [u8; 3],
    plaq: Vec<[usize; 4]>,
    of_link: Vec<[usize; 2]>,
    /// Free links in search order, and the plaquettes each one finishes.
    order: Vec<usize>,
    finishes: Vec<Vec<usize>>,
}

impl Lattice {
    fn new(lx: usize, ly: usize) -> Lattice {
        let v = lx * ly;
        let nl = 2 * v;
        let site = |x: usize, y: usize| (x % lx) * ly + y % ly;
        let xl = |x: usize, y: usize| site(x, y);
        let yl = |x: usize, y: usize| v + site(x, y);
        let mut mul = [[0u8; 6]; 6];
        let mut inv = [0u8; 6];
        let mut kind = [0u8; 6];
        for (a, pa) in PERMS.iter().enumerate() {
            for (b, pb) in PERMS.iter().enumerate() {
                let t = [pa[pb[0] as usize], pa[pb[1] as usize], pa[pb[2] as usize]];
                mul[a][b] = PERMS.iter().position(|q| *q == t).map_or(255, |i| i as u8);
                if mul[a][b] == 0 {
                    inv[a] = b as u8;
                }
            }
            // 0 for the identity, 1 for a transposition, 2 for a 3-cycle.
            kind[a] = match (0..3).filter(|&k| pa[k] == k as u8).count() {
                3 => 0,
                1 => 1,
                _ => 2,
            };
        }
        let t: Vec<u8> = (0..6u8).filter(|&g| kind[g as usize] == 1).collect();
        let mut plaq = Vec::with_capacity(v);
        for x in 0..lx {
            for y in 0..ly {
                plaq.push([xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)]);
            }
        }
        let mut of_link = vec![[usize::MAX; 2]; nl];
        for (p, links) in plaq.iter().enumerate() {
            for &l in links {
                let slot = usize::from(of_link[l][0] != usize::MAX);
                of_link[l][slot] = p;
            }
        }
        // The comb gauge of ymroom: these links stay at the identity.
        let mut tree = vec![false; nl];
        for y in 0..ly - 1 {
            tree[yl(0, y)] = true;
        }
        for x in 0..lx - 1 {
            for y in 0..ly {
                tree[xl(x, y)] = true;
            }
        }
        // A column of vertical links at a time, so that plaquettes finish early and low M prunes the search.
        let mut order = Vec::new();
        order.push(yl(0, ly - 1));
        for x in 1..lx {
            for y in 0..ly {
                order.push(yl(x, y));
            }
        }
        for y in 0..ly {
            order.push(xl(lx - 1, y));
        }
        assert_eq!(order.len(), v + 1);
        assert!(order.iter().all(|&l| !tree[l]));
        let mut seen = tree;
        let mut finishes = Vec::with_capacity(order.len());
        for &l in &order {
            seen[l] = true;
            finishes.push((0..v).filter(|&p| plaq[p].contains(&l) && plaq[p].iter().all(|&q| seen[q])).collect());
        }
        Lattice { nl, mul, inv, kind, trans: [t[0], t[1], t[2]], plaq, of_link, order, finishes }
    }

    fn holonomy(&self, u: &[u8], p: usize) -> u8 {
        let q = &self.plaq[p];
        self.mul[self.mul[self.mul[u[q[0]] as usize][u[q[1]] as usize] as usize][self.inv[u[q[2]] as usize] as usize] as usize][self.inv[u[q[3]] as usize] as usize]
    }

    fn cost_kind(&self, u: &[u8], p: usize) -> u8 {
        self.kind[self.holonomy(u, p) as usize]
    }
}

struct Audit<'a> {
    lat: &'a Lattice,
    mcut: u32,
    ids: &'a HashMap<(u8, u8), u16>,
    names: &'a [(u8, u8)],
    table: &'a HashSet<Vec<u16>>,
    g: &'a [u128],
    jb: i128,
    je: i128,
    t_milli: i128,
}

#[derive(Default)]
struct Tally {
    configs: u64,
    flats: u64,
    a_odd: u64,
    not_in_table: u64,
    below: u64,
    min_ratio: Option<i128>,
    min_lump: (u8, u8),
    per_lump: BTreeMap<(u8, u8), u64>,
    shown: Vec<String>,
}

const NEAR_MAX: usize = 4096;

/// What one thread keeps between configurations: the rows met so far, a key to build, and a count per lump.
struct Work {
    cache: HashMap<Vec<u16>, (bool, i128)>,
    key: Vec<u16>,
    counts: Vec<u16>,
}

impl Audit<'_> {
    fn visit(&self, u: &mut [u8], t: &mut Tally, w: &mut Work) {
        let lat = self.lat;
        let Work { cache, key, counts } = w;
        let (mut a, mut b) = (0u8, 0u8);
        for p in 0..lat.plaq.len() {
            match lat.cost_kind(u, p) {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        t.configs += 1;
        if a == 0 && b == 0 {
            t.flats += 1;
            return;
        }
        t.a_odd += u64::from(a % 2 == 1);
        *t.per_lump.entry((a, b)).or_insert(0) += 1;
        let mut touched: Vec<u16> = Vec::with_capacity(16);
        let mut flat = 0u16;
        for l in 0..lat.nl {
            let keep = u[l];
            let [p, q] = lat.of_link[l];
            let (kp, kq) = (lat.cost_kind(u, p), lat.cost_kind(u, q));
            for &s in &lat.trans {
                u[l] = lat.mul[s as usize][keep as usize];
                let (np, nq) = (lat.cost_kind(u, p), lat.cost_kind(u, q));
                let count = |k: u8, w: u8| i16::from(k == w);
                let a2 = i16::from(a) + count(np, 1) + count(nq, 1) - count(kp, 1) - count(kq, 1);
                let b2 = i16::from(b) + count(np, 2) + count(nq, 2) - count(kp, 2) - count(kq, 2);
                if a2 == 0 && b2 == 0 {
                    flat += 1;
                } else {
                    let id = self.ids.get(&(a2 as u8, b2 as u8)).copied().unwrap_or(u16::MAX);
                    if id == u16::MAX {
                        t.not_in_table += 1;
                        continue;
                    }
                    if counts[id as usize] == 0 {
                        touched.push(id);
                    }
                    counts[id as usize] += 1;
                }
            }
            u[l] = keep;
        }
        touched.sort_unstable();
        key.clear();
        key.extend_from_slice(&[self.ids[&(a, b)], flat]);
        for &id in &touched {
            key.push(id);
            key.push(counts[id as usize]);
            counts[id as usize] = 0;
        }
        let (known, ratio) = match cache.get(key.as_slice()) {
            Some(v) => *v,
            None => {
                let v = (self.table.contains(key.as_slice()), self.ratio(key.as_slice()));
                cache.insert(key.clone(), v);
                v
            }
        };
        if !known {
            t.not_in_table += 1;
        }
        if ratio < self.t_milli {
            t.below += 1;
        }
        if t.min_ratio.map_or(true, |m| ratio < m) {
            t.min_ratio = Some(ratio);
            t.min_lump = (a, b);
        }
        if (!known || ratio < self.t_milli) && t.shown.len() < 4 {
            let text: Vec<String> = lat.order.iter().map(|&l| u[l].to_string()).collect();
            t.shown.push(format!("AUDIT_FAILURE|a={a}|b={b}|known={known}|ratio={ratio}|free_links={}|json=0", text.join(",")));
        }
    }

    /// The ratio of perroncert check for this row: all 3 nl moves on the diagonal, so 1000 (JB M + JE 3 nl) less 1000 JE sum(c g_k) / g_L, rounded down.
    fn ratio(&self, key: &[u16]) -> i128 {
        let l = key[0] as usize;
        let (a, b) = self.names[l];
        let m = 2 * i128::from(a) + 3 * i128::from(b);
        let unit = 1000 * self.je;
        let sum: u128 = key[2..].chunks_exact(2).map(|p| u128::from(p[1]) * self.g[p[0] as usize]).sum();
        let top = (unit as u128) * sum;
        let moved = top.div_ceil(self.g[l]) as i128;
        1000 * (self.jb * m + self.je * 3 * (self.lat.nl as i128)) - moved
    }

    fn search(&self, depth: usize, m: u32, u: &mut [u8], t: &mut Tally, w: &mut Work) {
        let lat = self.lat;
        if depth == lat.order.len() {
            self.visit(u, t, w);
            return;
        }
        let link = lat.order[depth];
        for v in 0..6u8 {
            u[link] = v;
            let mut m2 = m;
            for &p in &lat.finishes[depth] {
                m2 += match lat.cost_kind(u, p) {
                    1 => 2,
                    2 => 3,
                    _ => 0,
                };
            }
            if m2 <= self.mcut {
                self.search(depth + 1, m2, u, t, w);
            }
        }
        u[link] = 0;
    }
}

fn enumerate(a: &[String]) -> Result<String, String> {
    let (lx, ly, table_path, g_path) = (num::<usize>(&a[2])?, num::<usize>(&a[3])?, &a[4], &a[5]);
    let (je, jb, t_milli, mcut, threads) = (num::<i128>(&a[6])?, num::<i128>(&a[7])?, num::<i128>(&a[8])?, num::<u32>(&a[9])?, num::<usize>(&a[10])?);
    let lat = Lattice::new(lx, ly);
    let text = std::fs::read_to_string(table_path).map_err(|e| e.to_string())?;
    let mut names: Vec<(u8, u8)> = Vec::new();
    let mut table = HashSet::new();
    for line in text.lines() {
        let need = |k: &str| field(line, k).ok_or_else(|| format!("no {k}"));
        if line.starts_with("LUMP|") {
            names.push((num(need("a=")?)?, num(need("b=")?)?));
        } else if line.starts_with("SIG|") {
            let lump: u16 = num(need("lump=")?)?;
            let flat: u16 = num(need("flat=")?)?;
            if num::<i64>(need("diag=")?)? != 3 * lat.nl as i64 {
                return Err("a row with another diagonal".into());
            }
            let mut pairs: Vec<(u16, u16)> = Vec::new();
            let list = need("n=")?;
            if !list.is_empty() {
                for p in list.split(',') {
                    let (i, c) = p.split_once(':').ok_or("bad neighbour")?;
                    pairs.push((num(i)?, num(c)?));
                }
            }
            pairs.sort_unstable();
            let mut key = vec![lump, flat];
            for (i, c) in pairs {
                key.push(i);
                key.push(c);
            }
            table.insert(key);
        }
    }
    if names.len() > NEAR_MAX {
        return Err("too many lumps".into());
    }
    let ids: HashMap<(u8, u8), u16> = names.iter().enumerate().map(|(i, n)| (*n, i as u16)).collect();
    let gtext = std::fs::read_to_string(g_path).map_err(|e| e.to_string())?;
    let mut g = vec![0u128; names.len()];
    for line in gtext.lines() {
        let need = |k: &str| field(line, k).ok_or_else(|| format!("no {k}"));
        let n: (u8, u8) = (num(need("a=")?)?, num(need("b=")?)?);
        let id = *ids.get(&n).ok_or("a lump of G outside the table")? as usize;
        g[id] = num(need("g=")?)?;
    }
    let audit = Audit { lat: &lat, mcut, ids: &ids, names: &names, table: &table, g: &g, jb, je, t_milli };
    // The first two links of the order split the work.
    let jobs: Vec<(u8, u8)> = (0..6u8).flat_map(|p| (0..6u8).map(move |q| (p, q))).collect();
    let next = AtomicUsize::new(0);
    let total = Mutex::new(Tally::default());
    std::thread::scope(|sc| {
        for _ in 0..threads {
            sc.spawn(|| {
                let mut w = Work { cache: HashMap::new(), key: Vec::new(), counts: vec![0u16; names.len()] };
                let mut u = vec![0u8; lat.nl];
                let mut t = Tally::default();
                loop {
                    let i = next.fetch_add(1, Ordering::Relaxed);
                    if i >= jobs.len() {
                        break;
                    }
                    let (p, q) = jobs[i];
                    u.iter_mut().for_each(|v| *v = 0);
                    let mut m = 0u32;
                    for (depth, v) in [(0usize, p), (1usize, q)] {
                        u[lat.order[depth]] = v;
                        for &pl in &lat.finishes[depth] {
                            m += match lat.cost_kind(&u, pl) {
                                1 => 2,
                                2 => 3,
                                _ => 0,
                            };
                        }
                    }
                    if m <= mcut {
                        audit.search(2, m, &mut u, &mut t, &mut w);
                    }
                }
                let mut all = total.lock().unwrap_or_else(std::sync::PoisonError::into_inner);
                all.configs += t.configs;
                all.flats += t.flats;
                all.a_odd += t.a_odd;
                all.not_in_table += t.not_in_table;
                all.below += t.below;
                if let Some(r) = t.min_ratio {
                    if all.min_ratio.map_or(true, |m| r < m) {
                        all.min_ratio = Some(r);
                        all.min_lump = t.min_lump;
                    }
                }
                for (k, v) in t.per_lump {
                    *all.per_lump.entry(k).or_insert(0) += v;
                }
                all.shown.extend(t.shown);
            });
        }
    });
    let t = total.into_inner().unwrap_or_else(std::sync::PoisonError::into_inner);
    for s in t.shown.iter().take(8) {
        println!("{s}");
    }
    let lumps: Vec<String> = t.per_lump.iter().map(|(k, v)| format!("{},{}:{v}", k.0, k.1)).collect();
    println!("AUDIT_LUMPS|Lx={lx}|Ly={ly}|mcut={mcut}|counts={}|json=0", lumps.join(";"));
    let ok = t.not_in_table == 0 && t.below == 0 && t.a_odd == 0;
    let line = format!(
        "AUDIT_ENUMERATE|Lx={lx}|Ly={ly}|mcut={mcut}|JE={je}|JB={jb}|configs={}|flat_configs={}|a_odd={}|not_in_table={}|ratio_below_bound={}|min_ratio_milli={}|min_ratio_lump={},{}|bound_milli={t_milli}|table_rows={}|result={}|json=0",
        t.configs,
        t.flats,
        t.a_odd,
        t.not_in_table,
        t.below,
        t.min_ratio.map_or("-".to_string(), |r| r.to_string()),
        t.min_lump.0,
        t.min_lump.1,
        table.len(),
        if ok { "PASS" } else { "FAIL" }
    );
    if ok {
        Ok(line)
    } else {
        println!("{line}");
        std::process::exit(2);
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let r = match (a.get(1).map(String::as_str), a.len()) {
        (Some("adjacency"), 4) => num::<usize>(&a[2]).and_then(|x| num::<usize>(&a[3]).and_then(|y| adjacency(x, y))),
        (Some("enumerate"), 11) => enumerate(&a),
        _ => Err("usage: localaudit adjacency LX LY | enumerate LX LY TABLE G JE JB T_MILLI MCUT THREADS".to_string()),
    };
    match r {
        Ok(line) => println!("{line}"),
        Err(e) => {
            println!("AUDIT_ERROR|{}|json=0", e.replace('|', "/"));
            std::process::exit(1);
        }
    }
}
