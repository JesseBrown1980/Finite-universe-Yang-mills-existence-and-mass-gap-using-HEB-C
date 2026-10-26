//! Play, don't build: sector rows generated on demand from a frozen address
//! file (the kernel-pump principle applied to the zero-momentum sectors).
//!
//! The address file of a sector is the sorted list of its representative keys
//! (least key of each G-orbit whose stabiliser is chi-trivial), u64 little
//! endian. A bucket index over the top bits of the key gives the position of
//! any key in O(1) expected time. Row i of the sector operator is generated
//! from key i alone: 3 transpositions on every link, each target
//! canonicalised under G (translations x C2v) and located by address.
//! Integer-only, Rust 1.81.

use crate::{Lat, G, TRANS};

pub struct Ops {
    pub dest: Vec<Vec<(usize, bool)>>,
    pub point: Vec<u8>,
}

pub fn build_ops(lat: &Lat) -> Ops {
    let (lx, ly, n) = (lat.lx, lat.ly, lat.n);
    let mut dest = Vec::new();
    let mut point = Vec::new();
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
                point.push(p);
            }
        }
    }
    Ops { dest, point }
}

pub fn chi(p: u8, sx: i64, sy: i64) -> i64 {
    match p {
        0 => 1,
        1 => sx,
        2 => sy,
        _ => sx * sy,
    }
}

pub struct Ctx<'a> {
    pub g: &'a G,
    pub lat: &'a Lat,
    pub ops: Ops,
    pub pow6: Vec<u64>,
    pub conj: [[u8; 6]; 6],
}

pub struct Scratch {
    h: Vec<u8>,
    q: Vec<u8>,
    a: Vec<u8>,
    b: Vec<u8>,
}

impl<'a> Ctx<'a> {
    pub fn new(g: &'a G, lat: &'a Lat) -> Ctx<'a> {
        let mut conj = [[0u8; 6]; 6];
        for c in 0..6u8 {
            for x in 0..6u8 {
                conj[c as usize][x as usize] = g.m(g.m(c, x), g.i(c));
            }
        }
        let k = lat.free.len();
        Ctx { g, lat, ops: build_ops(lat), pow6: (0..k).map(|i| 6u64.pow(u32::try_from(i).unwrap_or(0))).collect(), conj }
    }
    pub fn scratch(&self) -> Scratch {
        let nl = 2 * self.lat.n;
        Scratch { h: vec![0; self.lat.n], q: vec![0; self.lat.free.len()], a: vec![0; nl], b: vec![0; nl] }
    }
    /// gauge fix along the tree, then least conjugate of the free tuple
    pub fn key(&self, links: &[u8], s: &mut Scratch) -> u64 {
        let (g, lat) = (self.g, self.lat);
        s.h[0] = 0;
        for &e in &lat.tree {
            let (t, hd) = lat.edges[e];
            s.h[hd] = g.m(s.h[t], links[e]);
        }
        for (i, &e) in lat.free.iter().enumerate() {
            let (t, hd) = lat.edges[e];
            s.q[i] = g.m(g.m(s.h[t], links[e]), g.i(s.h[hd]));
        }
        let mut best = u64::MAX;
        for row in &self.conj {
            let mut id = 0u64;
            for (i, &v) in s.q.iter().enumerate() {
                id += u64::from(row[v as usize]) * self.pow6[i];
            }
            best = best.min(id);
        }
        best
    }
    pub fn apply(&self, op: usize, u: &[u8], out: &mut [u8]) {
        for (l, &(d, inv)) in self.ops.dest[op].iter().enumerate() {
            out[d] = if inv { self.g.i(u[l]) } else { u[l] };
        }
    }
    pub fn decode(&self, key: u64) -> Vec<u8> {
        let mut rest = key;
        (0..self.lat.free.len())
            .map(|_| {
                let v = (rest % 6) as u8;
                rest /= 6;
                v
            })
            .collect()
    }
    /// least key over G of a configuration and the character of the minimising
    /// op in sector (sx, sy); sign 0 when two minimising ops disagree
    pub fn canon(&self, links: &[u8], sx: i64, sy: i64, s: &mut Scratch) -> (u64, i64) {
        let mut best = u64::MAX;
        let mut sgn = 0i64;
        let mut buf = std::mem::take(&mut s.b);
        for o in 0..self.ops.dest.len() {
            self.apply(o, links, &mut buf);
            let kk = self.key(&buf, s);
            let c = chi(self.ops.point[o], sx, sy);
            match kk.cmp(&best) {
                std::cmp::Ordering::Less => {
                    best = kk;
                    sgn = c;
                }
                std::cmp::Ordering::Equal => {
                    if sgn != c {
                        sgn = 0;
                    }
                }
                std::cmp::Ordering::Greater => {}
            }
        }
        s.b = buf;
        (best, sgn)
    }
    /// Is `key` a sector representative? (least key of its G-orbit, chi
    /// trivial on its stabiliser). Returns the G-orbit size when it is.
    pub fn representative(&self, key: u64, sx: i64, sy: i64, s: &mut Scratch) -> Option<i64> {
        let raw = self.lat.representative(&self.decode(key));
        let mut buf = std::mem::take(&mut s.a);
        let mut stab = 0i64;
        let mut ok = true;
        for o in 0..self.ops.dest.len() {
            self.apply(o, &raw, &mut buf);
            let kk = self.key(&buf, s);
            if kk < key {
                ok = false;
                break;
            }
            if kk == key {
                stab += 1;
                if chi(self.ops.point[o], sx, sy) != 1 {
                    ok = false;
                    break;
                }
            }
        }
        s.a = buf;
        let gsize = i64::try_from(self.ops.dest.len()).unwrap_or(1);
        if ok {
            Some(gsize / stab.max(1))
        } else {
            None
        }
    }
}

/// Frozen address file with an O(1) bucket index over the top key bits.
pub struct Address {
    pub keys: Vec<u64>,
    shift: u32,
    start: Vec<u32>,
}

impl Address {
    /// Validated address file: keys strictly increasing (sorted, unique) and
    /// below the configuration space. Anything else is refused.
    pub fn checked(keys: Vec<u64>, space: u64) -> Result<Address, String> {
        if let Some(i) = keys.windows(2).position(|w| w[0] >= w[1]) {
            return Err(format!("address_not_strictly_increasing_at_{}", i + 1));
        }
        if keys.last().is_some_and(|&k| k >= space) {
            return Err("address_key_outside_space".into());
        }
        Ok(Address::new(keys, space))
    }
    pub fn new(keys: Vec<u64>, space: u64) -> Address {
        let n = keys.len().max(1);
        // about one key per bucket: 2^b buckets with 2^b >= n
        let mut b = 0u32;
        while (1usize << b) < n {
            b += 1;
        }
        let bits = 64 - space.leading_zeros();
        let shift = bits.saturating_sub(b);
        let nb = 1usize << b;
        let mut start = vec![0u32; nb + 1];
        for &k in &keys {
            start[usize::try_from(k >> shift).unwrap_or(0).min(nb - 1) + 1] += 1;
        }
        for i in 0..nb {
            start[i + 1] += start[i];
        }
        Address { keys, shift, start }
    }
    /// Position of `key`. The bucket only narrows the search; the binary search
    /// inside it compares the stored key exactly (worst case O(log n)).
    pub fn find(&self, key: u64) -> Option<usize> {
        let nb = self.start.len() - 1;
        let bk = usize::try_from(key >> self.shift).unwrap_or(0).min(nb - 1);
        let (a, b) = (self.start[bk] as usize, self.start[bk + 1] as usize);
        let pos = self.keys[a..b].binary_search(&key).ok().map(|i| a + i)?;
        (self.keys[pos] == key).then_some(pos)
    }
}

/// One generated row of the sector operator (ymsec convention): electric
/// entries (column, coefficient) with the diagonal 3 nl included, the
/// magnetic diagonal and the weight.
/// Electric entries (column, coefficient), magnetic diagonal, weight.
pub type PlayedRow = (Vec<(usize, i64)>, i64, i64);

/// A row whose key is not a representative of this sector, or a signed target
/// missing from the address file, is an error (wrong-sector or incomplete file).
pub fn play_row(ctx: &Ctx, addr: &Address, i: usize, sx: i64, sy: i64, s: &mut Scratch) -> Result<PlayedRow, String> {
    let (g, lat) = (ctx.g, ctx.lat);
    let key = addr.keys[i];
    let orbit = ctx.representative(key, sx, sy, s).ok_or(format!("key_{key}_not_a_sector_representative"))?;
    let q = ctx.decode(key);
    let raw = lat.representative(&q);
    let nl = 2 * lat.n;
    let mut row: std::collections::BTreeMap<usize, i64> = std::collections::BTreeMap::new();
    *row.entry(i).or_insert(0) += 3 * i64::try_from(nl).unwrap_or(0);
    let mut w = raw.clone();
    for l in 0..nl {
        for &t in &TRANS {
            w.copy_from_slice(&raw);
            w[l] = g.m(t, w[l]);
            let (kk, sg) = ctx.canon(&w, sx, sy, s);
            if sg == 0 {
                continue;
            }
            // a signed target lies in the sector, so its least key must be addressed
            let j = addr.find(kk).ok_or(format!("target_key_{kk}_missing_from_address_file"))?;
            *row.entry(j).or_insert(0) -= sg;
        }
    }
    row.retain(|_, v| *v != 0);
    let weight = orbit * lat.weight(g, &q);
    Ok((row.into_iter().collect(), lat.magnetic(g, &raw), weight))
}
