//! Native HEB-C: exact finite non-Abelian gauge diagnostics and virtual address dispatch.
//! This is a finite S3 lattice model, NOT a continuum quantum Yang-Mills proof.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

// Original Clasy X3 transition lattice, byte-identical to upstream.
#[path = "../vendor/constellation_lattice/trit.rs"]
pub mod trit;
#[path = "../vendor/constellation_lattice/oscillator.rs"]
pub mod constellation_oscillator;
pub mod constellation_gate;

pub mod hamiltonian;
pub mod torus2;
pub mod torus2_bounds;
pub mod torus2_inertia;
pub mod torus2_independent;
pub mod shadow_residual;
pub mod rime_gear;
pub mod double_plaquette;
pub mod clasy_portal;

pub const VIRTUAL_KERNELS: u64 = 23_000_000_000;
pub const COPRIME_STRIDE: u64 = 1_000_003;
const TRANS: [u8; 3] = [1, 2, 5];

// Each index is a permutation of three elements; S3 is non-Abelian.
pub const PERM: [[u8; 3]; 6] = [
    [0, 1, 2], // identity
    [0, 2, 1], // swap 1 and 2
    [1, 0, 2], // swap 0 and 1
    [1, 2, 0], // cycle
    [2, 0, 1], // inverse cycle
    [2, 1, 0], // swap 0 and 2
];

pub fn mul(a: u8, b: u8) -> u8 {
    assert!(a < 6 && b < 6);
    let p = PERM[a as usize];
    let q = PERM[b as usize];
    let target = [p[q[0] as usize], p[q[1] as usize], p[q[2] as usize]];
    PERM.iter().position(|x| *x == target).expect("S3 closure") as u8
}

pub fn inv(a: u8) -> u8 {
    (0..6).find(|&b| mul(a, b) == 0 && mul(b, a) == 0)
        .expect("S3 inverse")
}

pub fn character(a: u8) -> i64 {
    // Character of the real 2D irreducible representation of S3.
    if a == 0 { 2 } else if a == 3 || a == 4 { -1 } else { 0 }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Lattice {
    pub side: usize,
    pub x: Vec<u8>,
    pub y: Vec<u8>,
}

impl Lattice {
    pub fn new(side: usize, mut seed: u64) -> Self {
        assert!((2..=512).contains(&side), "side must be 2..512");
        let n = side * side;
        let mut x = Vec::with_capacity(n);
        let mut y = Vec::with_capacity(n);
        for _ in 0..n {
            x.push((splitmix64(&mut seed) % 6) as u8);
            y.push((splitmix64(&mut seed) % 6) as u8);
        }
        Self { side, x, y }
    }

    pub fn identity(side: usize) -> Self {
        let n = side * side;
        Self { side, x: vec![0; n], y: vec![0; n] }
    }

    fn index(&self, x: usize, y: usize) -> usize {
        (x % self.side) * self.side + (y % self.side)
    }

    pub fn plaquette(&self, x: usize, y: usize) -> u8 {
        // U_x(n) U_y(n+x) U_x(n+y)^-1 U_y(n)^-1
        let a = self.index(x, y);
        let right = self.index(x + 1, y);
        let up = self.index(x, y + 1);
        mul(mul(mul(self.x[a], self.y[right]), inv(self.x[up])), inv(self.y[a]))
    }

    pub fn action(&self) -> u64 {
        let mut sum = 0;
        for x in 0..self.side {
            for y in 0..self.side {
                let c = character(self.plaquette(x, y));
                sum += (2 - c) as u64;
            }
        }
        sum
    }

    pub fn transformed(&self, gauge: &[u8]) -> Self {
        assert_eq!(gauge.len(), self.x.len());
        assert!(gauge.iter().all(|&v| v < 6));
        let mut out = self.clone();
        for x in 0..self.side {
            for y in 0..self.side {
                let a = self.index(x, y);
                let right = self.index(x + 1, y);
                let up = self.index(x, y + 1);
                out.x[a] = mul(mul(gauge[a], self.x[a]), inv(gauge[right]));
                out.y[a] = mul(mul(gauge[a], self.y[a]), inv(gauge[up]));
            }
        }
        out
    }

    pub fn advance(&mut self) {
        // Toy gauge-equivariant deterministic link update.
        // P(n) transforms by conjugation at n, so P(n)*U_x(n) transforms as a link.
        // NOT a unitary Hamiltonian evolution; no invertibility claim.
        let mut next_x = self.x.clone();
        for x in 0..self.side {
            for y in 0..self.side {
                let a = self.index(x, y);
                next_x[a] = mul(self.plaquette(x, y), self.x[a]);
            }
        }
        self.x = next_x;
    }

    pub fn bytes(&self) -> Vec<u8> {
        let mut result = Vec::with_capacity(self.x.len() * 2);
        for (&x, &y) in self.x.iter().zip(&self.y) {
            result.push(x);
            result.push(y);
        }
        result
    }
}


/// Encode one S3 link as two balanced Q-trits. Six of the nine pairs are valid.
/// This is a discrete data representation, not a coherent quantum qutrit.
pub fn link_qtrits(g: u8) -> [i8; 2] {
    assert!(g < 6);
    [(g % 3) as i8 - 1, (g / 3) as i8 - 1]
}

pub fn qtrits_link(q: [i8; 2]) -> Option<u8> {
    if q.iter().any(|&x| !(-1..=1).contains(&x)) { return None; }
    let n = (q[0] + 1) + 3 * (q[1] + 1);
    if n < 6 { Some(n as u8) } else { None }
}

/// Lazily allocated, version-bound content-addressed final-state cache.
/// No independent physical state is created for unrequested virtual coordinates.
/// Replaying with receipts must still recompute per-step states unless those
/// complete state snapshots have also been stored and authenticated.
#[derive(Default)]
pub struct KernelCache {
    states: std::collections::HashMap<[u8; 32], ([u8; 32], Vec<u8>)>,
    pub hits: u64,
    pub misses: u64,
    pub rejected: u64,
}

impl KernelCache {
    pub fn new() -> Self { Self::default() }
    pub fn active_states(&self) -> usize { self.states.len() }

    pub fn state_after(&mut self, side: usize, seed: u64, steps: u64) -> Vec<u8> {
        let mut lattice = Lattice::new(side, seed);
        let source = lattice.bytes();
        let mut input = b"HEBC-S3-GAUGE-EQUIVARIANT-TOY-V1".to_vec();
        input.extend_from_slice(&(side as u64).to_le_bytes());
        input.extend_from_slice(&seed.to_le_bytes());
        input.extend_from_slice(&steps.to_le_bytes());
        input.extend_from_slice(&sha256(&source));
        let key = sha256(&input);
        if let Some((digest, value)) = self.states.get(&key) {
            if sha256(value) == *digest {
                self.hits += 1;
                return value.clone();
            }
            self.rejected += 1;
            self.states.remove(&key);
        }
        self.misses += 1;
        for _ in 0..steps { lattice.advance(); }
        let bytes = lattice.bytes();
        self.states.insert(key, (sha256(&bytes), bytes.clone()));
        bytes
    }
}

pub fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9e37_79b9_7f4a_7c15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

pub fn address(ordinal: u64) -> u64 {
    (((ordinal % VIRTUAL_KERNELS) as u128 * COPRIME_STRIDE as u128)
        % VIRTUAL_KERNELS as u128) as u64
}

pub fn virtual_qtrit(ordinal: u64) -> i8 {
    match address(ordinal) % 3 {
        0 => -1,
        1 => 0,
        _ => 1,
    }
}

pub fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

pub fn laplacian(v: &[i64; 6]) -> [i64; 6] {
    // Central S3 Cayley Laplacian, generated by all three transpositions.
    let mut out = [0; 6];
    for g in 0..6u8 {
        let mut z = 3 * v[g as usize];
        for &t in &TRANS {
            z -= v[mul(t, g) as usize];
        }
        out[g as usize] = z;
    }
    out
}

pub fn gap_certificate() -> bool {
    // K_3,3 Cayley graph: complete even-to-odd connectivity.
    // Six linearly independent *integer* eigenvectors.
    let eig: [([i64; 6], i64); 6] = [
        ([1, 1, 1, 1, 1, 1], 0),
        ([1, -1, -1, 1, 1, -1], 6),
        ([1, 0, 0, -1, 0, 0], 3),
        ([1, 0, 0, 0, -1, 0], 3),
        ([0, 1, -1, 0, 0, 0], 3),
        ([0, 1, 0, 0, 0, -1], 3),
    ];
    eig.iter().all(|(v, lambda)| {
        let out = laplacian(v);
        (0..6).all(|i| out[i] == lambda * v[i])
    })
}

// SHA-256 in pure Rust; no external dependencies, network, float or unsafe.
pub fn sha256(input: &[u8]) -> [u8; 32] {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f,
        0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut data = input.to_vec();
    let bit_len = (input.len() as u64).wrapping_mul(8);
    data.push(0x80);
    while data.len() % 64 != 56 { data.push(0); }
    data.extend_from_slice(&bit_len.to_be_bytes());
    for chunk in data.chunks_exact(64) {
        let mut w = [0u32; 64];
        for (i, v) in w.iter_mut().take(16).enumerate() {
            let s = i * 4;
            *v = u32::from_be_bytes([chunk[s], chunk[s+1], chunk[s+2], chunk[s+3]]);
        }
        for i in 16..64 {
            let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3);
            let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }
        let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh] = h;
        for i in 0..64 {
            let ch = (e & f) ^ ((!e) & g);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let t2 = s0.wrapping_add(maj);
            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        let vars = [a, b, c, d, e, f, g, hh];
        for (out, v) in h.iter_mut().zip(vars) { *out = out.wrapping_add(v); }
    }
    let mut out = [0u8; 32];
    for (i, word) in h.iter().enumerate() {
        out[i*4..i*4+4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

pub fn hex(bytes: &[u8]) -> String {
    const HEX: &[u8] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for &b in bytes {
        out.push(HEX[(b >> 4) as usize] as char);
        out.push(HEX[(b & 0x0f) as usize] as char);
    }
    out
}

pub fn field<'a>(record: &'a str, key: &str) -> Option<&'a str> {
    record.split('|').find_map(|f| f.split_once('='))
        .and_then(|_| record.split('|').find_map(|item| {
            let (k, v) = item.split_once('=')?;
            if k == key { Some(v) } else { None }
        }))
}

pub struct Ledger {
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    prev: [u8; 32],
}

impl Default for Ledger {
    fn default() -> Self { Self::new() }
}

impl Ledger {
    pub fn new() -> Self { Self { hbp: Vec::new(), hbi: Vec::new(), prev: [0;32] } }

    pub fn append(&mut self, tick: u64, side: usize, action: u64, state: &[u8], source: &[u8]) {
        let input_sha = hex(&sha256(source));
        let state_sha = hex(&sha256(state));
        let sh = &input_sha[..16];
        let body = format!(
            "HBP|schema=HEBC-S3-V1|tick={tick}|side={side}|action={action}|source_sha={input_sha}|sh={sh}|state_sha={state_sha}|prev={}",
            hex(&self.prev)
        );
        let record_sha = sha256(body.as_bytes());
        let mut pair = Vec::with_capacity(64);
        pair.extend_from_slice(&self.prev);
        pair.extend_from_slice(&record_sha);
        let chain = sha256(&pair);
        let offset = self.hbp.len();
        let line = format!("{body}|record_sha={}|chain={}|json=0\n", hex(&record_sha), hex(&chain));
        self.hbp.extend_from_slice(line.as_bytes());
        self.hbi.extend_from_slice(format!(
            "HBI|tick={tick}|offset={offset}|length={}|record_sha={}|chain={}|json=0\n",
            line.len(), hex(&record_sha), hex(&chain)
        ).as_bytes());
        self.prev = chain;
    }

    pub fn anchor(&self) -> String {
        format!(
            "ANCHOR|schema=HEBC-S3-V1|hbp_sha={}|hbi_sha={}|chain={}|json=0\n",
            hex(&sha256(&self.hbp)), hex(&sha256(&self.hbi)), hex(&self.prev)
        )
    }
}

pub fn verify_ledger(hbp: &[u8], hbi: &[u8], anchor: &str) -> Result<usize, String> {
    if !anchor.ends_with('\n') || !anchor.starts_with("ANCHOR|") {
        return Err("anchor format".into());
    }
    let a = anchor.trim_end();
    if field(a, "hbp_sha") != Some(hex(&sha256(hbp)).as_str()) ||
       field(a, "hbi_sha") != Some(hex(&sha256(hbi)).as_str()) {
        return Err("root file sha mismatch".into());
    }
    let rows: Vec<&[u8]> = hbp.split_inclusive(|&b| b == b'\n').collect();
    let idx: Vec<&[u8]> = hbi.split_inclusive(|&b| b == b'\n').collect();
    if rows.is_empty() || rows.len() != idx.len() { return Err("row count".into()); }
    let mut offset = 0usize;
    let mut prev = [0u8; 32];
    for (expected, (rb, ib)) in rows.iter().zip(idx.iter()).enumerate() {
        if !rb.ends_with(b"\n") || !ib.ends_with(b"\n") {
            return Err("missing newline".into());
        }
        let row = std::str::from_utf8(rb).map_err(|_| "HBP utf8")?.trim_end();
        let index = std::str::from_utf8(ib).map_err(|_| "HBI utf8")?.trim_end();
        if !row.starts_with("HBP|") || !index.starts_with("HBI|") {
            return Err("record type".into());
        }
        let tick = (expected + 1).to_string();
        if field(row, "tick") != Some(tick.as_str()) ||
           field(index, "tick") != Some(tick.as_str()) ||
           field(index, "offset") != Some(offset.to_string().as_str()) ||
           field(index, "length") != Some(rb.len().to_string().as_str()) {
            return Err("index position".into());
        }
        let (body, _) = row.split_once("|record_sha=").ok_or("record digest missing")?;
        let rec = sha256(body.as_bytes());
        let rec_hex = hex(&rec);
        if field(row, "record_sha") != Some(rec_hex.as_str()) ||
           field(index, "record_sha") != Some(rec_hex.as_str()) ||
           field(row, "prev") != Some(hex(&prev).as_str()) {
            return Err("record sha or previous hash".into());
        }
        if field(row, "json") != Some("0") || field(index, "json") != Some("0") {
            return Err("noncanonical json marker".into());
        }
        let mut pair = Vec::with_capacity(64);
        pair.extend_from_slice(&prev);
        pair.extend_from_slice(&rec);
        let next = sha256(&pair);
        let next_hex = hex(&next);
        if field(row, "chain") != Some(next_hex.as_str()) ||
           field(index, "chain") != Some(next_hex.as_str()) {
            return Err("chain link".into());
        }
        prev = next;
        offset += rb.len();
    }
    if field(a, "chain") != Some(hex(&prev).as_str()) {
        return Err("anchor chain mismatch".into());
    }
    Ok(rows.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn group_laws() {
        for a in 0..6u8 {
            assert_eq!(mul(a, inv(a)), 0);
            assert_eq!(mul(inv(a), a), 0);
            for b in 0..6 {
                assert_eq!(mul(a, b), mul(a, b));
                for c in 0..6 { assert_eq!(mul(mul(a,b),c), mul(a,mul(b,c))); }
            }
        }
        assert_ne!(mul(1, 2), mul(2, 1));
    }

    #[test]
    fn gauge_invariance_and_equivariance() {
        for side in 2..=5 {
            for seed in 0..12u64 {
                let lattice = Lattice::new(side, seed + 400);
                let mut s = seed ^ 0x12_34_56_78;
                let g: Vec<u8> = (0..side * side)
                    .map(|_| (splitmix64(&mut s) % 6) as u8).collect();
                let transformed = lattice.transformed(&g);
                assert_eq!(lattice.action(), transformed.action());
                for x in 0..side {
                    for y in 0..side {
                        let i = lattice.index(x,y);
                        assert_eq!(
                            transformed.plaquette(x,y),
                            mul(mul(g[i], lattice.plaquette(x,y)), inv(g[i]))
                        );
                    }
                }
                let mut a = lattice;
                let mut b = transformed;
                a.advance();
                b.advance();
                assert_eq!(a.transformed(&g), b);
                assert_eq!(a.action(), b.action());
            }
        }
    }

    #[test]
    fn trivial_and_pure_gauge_zero_action() {
        let lattice = Lattice::identity(4);
        assert_eq!(lattice.action(), 0);
        let gauge = vec![1,2,3,4,5,0,2,1,4,3,5,0,3,2,1,4];
        assert_eq!(lattice.transformed(&gauge).action(), 0);
    }

    #[test]
    fn exact_graph_gap_three() {
        assert!(gap_certificate());
        let basis: [i64; 6] = [1, 0, 0, 0, 0, 0];
        assert_eq!(laplacian(&basis), [3,-1,-1,0,0,-1]);
    }

    #[test]
    fn sha_vectors() {
        assert_eq!(hex(&sha256(b"")), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
        assert_eq!(hex(&sha256(b"abc")), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }

    #[test]
    fn virtual_address_injection() {
        assert_eq!(gcd(VIRTUAL_KERNELS, COPRIME_STRIDE), 1);
        assert_eq!(address(0), 0);
        assert_eq!(address(VIRTUAL_KERNELS), 0);
        let mut seen = std::collections::HashSet::new();
        for i in 0..65_536 { assert!(seen.insert(address(i))); }
        assert!((-1..=1).contains(&virtual_qtrit(42)));
    }

    #[test]
    fn ledger_roundtrip_and_corruption_rejection() {
        let mut l = Lattice::new(3, 55);
        let source = l.bytes();
        let mut ledger = Ledger::new();
        for tick in 1..=27 {
            l.advance();
            ledger.append(tick, l.side, l.action(), &l.bytes(), &source);
        }
        let anchor = ledger.anchor();
        assert_eq!(verify_ledger(&ledger.hbp, &ledger.hbi, &anchor), Ok(27));
        let mut corrupted = ledger.hbp.clone();
        let loc = corrupted.iter().position(|&b| b == b'5').unwrap();
        corrupted[loc] = b'6';
        assert!(verify_ledger(&corrupted, &ledger.hbi, &anchor).is_err());
        let mut tampered = ledger.hbi.clone();
        tampered[5] = b'X';
        assert!(verify_ledger(&ledger.hbp, &tampered, &anchor).is_err());
    }

    #[test]
    fn deterministic_replay() {
        let mut a = Lattice::new(4, 123);
        let mut b = Lattice::new(4, 123);
        for _ in 0..243 {
            a.advance();
            b.advance();
            assert_eq!(a.bytes(), b.bytes());
        }
        assert_eq!(sha256(&a.bytes()), sha256(&b.bytes()));
    }
    #[test]
    fn qtrit_link_canonical_encoding() {
        for g in 0..6u8 {
            let q = link_qtrits(g);
            assert!(q.iter().all(|&v| (-1..=1).contains(&v)));
            assert_eq!(qtrits_link(q), Some(g));
        }
        assert_eq!(qtrits_link([1,1]), None);
        assert_eq!(qtrits_link([2,0]), None);
    }

    #[test]
    fn lazy_cache_misses_then_verifies_and_hits() {
        let mut cache = KernelCache::new();
        assert_eq!(cache.active_states(), 0);
        let a = cache.state_after(4, 1234, 243);
        let b = cache.state_after(4, 1234, 243);
        assert_eq!(a, b);
        assert_eq!(cache.hits, 1);
        assert_eq!(cache.misses, 1);
        assert_eq!(cache.rejected, 0);
        assert_eq!(cache.active_states(), 1);
        let different = cache.state_after(4, 1234, 244);
        assert_eq!(cache.misses, 2);
        assert_eq!(cache.active_states(), 2);
        assert_ne!(a, different);
    }

    #[test]
    fn gauge_invariance_scaled_lattice_sizes() {
        for side in [2, 3, 4, 8, 16, 32, 64, 128, 256, 512] {
            let mut l = Lattice::new(side, 0x494e5445474552 ^ side as u64);
            let mut rng = 0x47617567654c6177 ^ side as u64;
            let gauge: Vec<u8> = (0..side * side)
                .map(|_| (splitmix64(&mut rng) % 6) as u8).collect();
            let mut g = l.transformed(&gauge);
            assert_eq!(l.action(), g.action(), "side={side}");
            // Exact equivariance under repeated sequential gauge-covariant updates.
            let ticks = if side <= 16 { 27 } else if side <= 64 { 9 } else if side <= 256 { 3 } else { 1 };
            for _ in 0..ticks {
                l.advance();
                g.advance();
                assert_eq!(l.transformed(&gauge), g, "side={side}");
                assert_eq!(l.action(), g.action(), "side={side}");
            }
            assert_eq!(l.bytes().len(), 2 * side * side);
        }
    }

    #[test]
    fn very_large_logical_namespace_does_not_allocate_states() {
        let mut cache = KernelCache::new();
        assert_eq!(cache.active_states(), 0);
        for n in [0, 1, 81, 243, 9_999_999, 22_999_999_999] {
            let q = virtual_qtrit(n);
            assert!((-1..=1).contains(&q));
            assert!(address(n) < VIRTUAL_KERNELS);
        }
        assert_eq!(cache.active_states(), 0);
        let state = cache.state_after(16, 7, 9);
        assert_eq!(state.len(), 512);
        assert_eq!(cache.active_states(), 1);
    }

}
