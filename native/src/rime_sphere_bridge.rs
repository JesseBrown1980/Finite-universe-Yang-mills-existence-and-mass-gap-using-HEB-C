//! Stage 2J — the RIME sphere bridge.
//!
//! The original sphere pipeline (ASOLARIA-UNIVERSE-SIMULATOR, commit 3f9f42d,
//! `players/rime_prism_pipeline.py`) is vendored byte-identical under
//! `vendor/rime_sphere_source/` and is NOT replaced. This module wraps it:
//! the same 27-point NTT over Z/1000081, a carrier that RETAINS the full
//! coefficient values, the original controls C1–C4, one added control C5,
//! and HBP/HBI/anchor receipts.
//!
//! Implementation distinction pinned here (and tested): in the original
//! script the balanced-ternary triples `bt(k)` label the 27 coordinate
//! POSITIONS. They are identical for every block, so they carry no
//! information about any block. Byte-exact recovery comes from the 27
//! coefficient VALUES. The carrier therefore stores the coefficients; the
//! labels are metadata. C5 measures what labels alone can recover.
//!
//! Integer only. No compression is claimed: each coefficient needs 20 bits,
//! so a 27-byte block (216 bits) is carried in 540 bits.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use crate::{hex, sha256};
use std::collections::HashMap;
use std::path::Path;

pub const P: u64 = 1_000_081;
pub const N: usize = 27;
pub const SOURCE: &str =
    "ASOLARIA-UNIVERSE-SIMULATOR@3f9f42d:players/rime_prism_pipeline.py";
/// The original pipeline's C3 sweep.
pub const C3_KS: [usize; 6] = [3, 9, 18, 24, 26, 27];
/// The original pipeline's C4 random-address control uses the first 100 blocks.
pub const C4_BLOCKS: usize = 100;
const SCHEMA: &str = "hebc.rime.sphere.bridge.v1";
/// Which results are theorems (hold for every input) and which are
/// observations (measured on this input only).
const GUARANTEES: &str = "theorem=C1,C2,C3_k27,C4_wrong_root_byte0,C5_single_label_row_if_blocks,C5_bound_le_max_block_multiplicity|observed=C3_k_lt_27_counts,C4_random_counts,C4_wrong_root_other_bytes,C5_max_exact_value";

pub type Block = [u64; N];

fn modpow(mut base: u64, mut exp: u64, m: u64) -> u64 {
    let mut acc = 1u64;
    base %= m;
    while exp > 0 {
        if exp & 1 == 1 {
            acc = acc * base % m;
        }
        base = base * base % m;
        exp >>= 1;
    }
    acc
}

fn distinct_prime_factors(mut n: u64) -> Vec<u64> {
    let mut out = Vec::new();
    let mut d = 2u64;
    while d * d <= n {
        if n % d == 0 {
            out.push(d);
            while n % d == 0 {
                n /= d;
            }
        }
        d += 1;
    }
    if n > 1 {
        out.push(n);
    }
    out
}

/// Smallest primitive root, the same search as `rime_sphere.primitive_root`.
pub fn primitive_root(p: u64) -> u64 {
    let fac = distinct_prime_factors(p - 1);
    (2..p)
        .find(|&g| fac.iter().all(|&q| modpow(g, (p - 1) / q, p) != 1))
        .unwrap_or(0)
}

/// The "bank": everything the inverse needs besides the coefficients.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Bank {
    pub p: u64,
    pub g: u64,
    pub w: u64,
}

pub fn bank() -> Result<Bank, String> {
    let g = primitive_root(P);
    let w = modpow(g, (P - 1) / N as u64, P);
    // w must have multiplicative order exactly 27 (3^3): w^27 = 1, w^9 != 1.
    if modpow(w, N as u64, P) != 1 || modpow(w, 9, P) == 1 {
        return Err("bank root is not a primitive 27th root of unity".into());
    }
    Ok(Bank { p: P, g, w })
}

pub fn ntt(x: &Block, w: u64) -> Block {
    std::array::from_fn(|k| {
        x.iter().enumerate().fold(0u64, |s, (j, &v)| {
            (s + v * modpow(w, ((j * k) % N) as u64, P)) % P
        })
    })
}

pub fn intt(xf: &Block, w: u64) -> Block {
    let wi = modpow(w, P - 2, P);
    let ninv = modpow(N as u64, P - 2, P);
    std::array::from_fn(|j| {
        let s = xf.iter().enumerate().fold(0u64, |s, (k, &v)| {
            (s + v * modpow(wi, ((j * k) % N) as u64, P)) % P
        });
        ninv * s % P
    })
}

/// The original `bt(k)`: position label -> balanced-ternary (r,g,b) in {-1,0,1}^3.
pub fn label(k: usize) -> [i8; 3] {
    let mut x = k;
    std::array::from_fn(|_| {
        let d = (x % 3) as i8 - 1;
        x /= 3;
        d
    })
}

/// What travels across the bridge: the bank header plus full coefficients.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Carrier {
    pub bank: Bank,
    pub input_len: usize,
    pub input_sha: String,
    pub coeffs: Vec<Block>,
    pub tail: Vec<u8>,
}

fn blocks_of(data: &[u8]) -> Vec<Block> {
    data.chunks_exact(N)
        .map(|c| std::array::from_fn(|i| u64::from(c[i])))
        .collect()
}

pub fn encode(data: &[u8], bank: Bank) -> Carrier {
    let blocks = blocks_of(data);
    let coeffs = blocks.iter().map(|b| ntt(b, bank.w)).collect();
    Carrier {
        bank,
        input_len: data.len(),
        input_sha: hex(&sha256(data)),
        coeffs,
        tail: data[blocks.len() * N..].to_vec(),
    }
}

/// Inverse across the bridge. Fails closed: a coefficient outside Z/p, an
/// inverse value that is not a byte, or a length/sha mismatch is an error.
pub fn decode(c: &Carrier) -> Result<Vec<u8>, String> {
    let mut out = Vec::with_capacity(c.input_len);
    for xf in &c.coeffs {
        if xf.iter().any(|&v| v >= c.bank.p) {
            return Err("coefficient outside Z/p".into());
        }
        for v in intt(xf, c.bank.w) {
            out.push(u8::try_from(v).map_err(|_| "inverse value is not a byte".to_string())?);
        }
    }
    out.extend_from_slice(&c.tail);
    if out.len() != c.input_len || hex(&sha256(&out)) != c.input_sha {
        return Err("decoded bytes do not match the carried input sha".into());
    }
    Ok(out)
}

pub fn render(c: &Carrier) -> String {
    let mut s = format!(
        "RIMECARRIER|schema=hebc.rime.sphere.carrier.v1|p={}|g={}|w={}|N={N}|bytes={}|blocks={}|tail={}|input_sha={}|json=0\n",
        c.bank.p, c.bank.g, c.bank.w, c.input_len, c.coeffs.len(), c.tail.len(), c.input_sha
    );
    for (i, xf) in c.coeffs.iter().enumerate() {
        let row: Vec<String> = xf.iter().map(u64::to_string).collect();
        s.push_str(&format!("B|{i}|{}\n", row.join(",")));
    }
    if !c.tail.is_empty() {
        s.push_str(&format!("T|{}\n", hex(&c.tail)));
    }
    s
}

fn field<'a>(header: &'a str, key: &str) -> Result<&'a str, String> {
    header
        .split('|')
        .find_map(|kv| kv.strip_prefix(key).and_then(|r| r.strip_prefix('=')))
        .ok_or_else(|| format!("carrier header missing {key}"))
}

fn num<T: std::str::FromStr>(s: &str) -> Result<T, String> {
    s.parse::<T>().map_err(|_| format!("bad number {s}"))
}

pub fn parse(text: &str) -> Result<Carrier, String> {
    let mut lines = text.lines();
    let header = lines.next().ok_or("empty carrier")?;
    if !header.starts_with("RIMECARRIER|schema=hebc.rime.sphere.carrier.v1|") {
        return Err("not a RIME sphere carrier".into());
    }
    let bank = Bank {
        p: num(field(header, "p")?)?,
        g: num(field(header, "g")?)?,
        w: num(field(header, "w")?)?,
    };
    if num::<usize>(field(header, "N")?)? != N {
        return Err("carrier N is not 27".into());
    }
    let nblocks: usize = num(field(header, "blocks")?)?;
    let mut coeffs = Vec::with_capacity(nblocks);
    let mut tail = Vec::new();
    for line in lines {
        if let Some(rest) = line.strip_prefix("B|") {
            let (idx, row) = rest.split_once('|').ok_or("bad block row")?;
            if num::<usize>(idx)? != coeffs.len() {
                return Err("block rows out of order".into());
            }
            let vals: Vec<u64> = row.split(',').map(num).collect::<Result<_, _>>()?;
            let block: Block = vals.try_into().map_err(|_| "block row is not 27 coefficients")?;
            coeffs.push(block);
        } else if let Some(h) = line.strip_prefix("T|") {
            if h.len() % 2 != 0 {
                return Err("odd tail hex".into());
            }
            for i in (0..h.len()).step_by(2) {
                tail.push(u8::from_str_radix(&h[i..i + 2], 16).map_err(|_| "bad tail hex")?);
            }
        } else {
            return Err("unknown carrier row".into());
        }
    }
    if coeffs.len() != nblocks || tail.len() != num::<usize>(field(header, "tail")?)? {
        return Err("carrier row counts disagree with header".into());
    }
    Ok(Carrier {
        bank,
        input_len: num(field(header, "bytes")?)?,
        input_sha: field(header, "input_sha")?.to_owned(),
        coeffs,
        tail,
    })
}

/// Measured controls. C1–C4 are the original script's; C5 is new.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Controls {
    pub c1_identity: bool,
    pub c2_carrier_roundtrip: bool,
    /// (k, bytes recovered, bytes total) for the original C3 sweep.
    pub c3: Vec<(usize, usize, usize)>,
    /// (k, whole blocks recovered exactly, blocks total) — block-level C3.
    /// Individual bytes can match by chance; whole-block success requires
    /// equality at all 27 positions, and can occur for structured inputs.
    pub c3_blocks: Vec<(usize, usize, usize)>,
    pub c4_random: (usize, usize),
    pub c4_wrong_root: (usize, usize),
    /// Distinct label rows across complete blocks (1 when blocks exist;
    /// 0 when the input has only a tail or is empty).
    pub c5_label_rows_distinct: usize,
    /// Best any labels-only decoder can do: it must emit one fixed block, so
    /// at most the most-repeated block is exact.
    pub c5_labels_only_max_exact: (usize, usize),
}

/// The original C3 address: keep the first k coefficients, null the rest.
pub fn truncate(xf: &Block, k: usize) -> Block {
    std::array::from_fn(|i| if i < k { xf[i] } else { 0 })
}

fn matches(a: &Block, b: &Block) -> usize {
    a.iter().zip(b).filter(|(x, y)| x == y).count()
}

pub fn controls(data: &[u8], c: &Carrier) -> Controls {
    let blocks = blocks_of(data);
    let w = c.bank.w;
    let total = N * blocks.len();
    let c1_identity = c.coeffs.iter().zip(&blocks).all(|(xf, b)| intt(xf, w) == *b);
    let c2_carrier_roundtrip = parse(&render(c))
        .and_then(|back| decode(&back))
        .is_ok_and(|bytes| bytes == data);
    let (c3, c3_blocks): (Vec<_>, Vec<_>) = C3_KS
        .iter()
        .map(|&k| {
            let per_block: Vec<usize> = c
                .coeffs
                .iter()
                .zip(&blocks)
                .map(|(xf, b)| matches(&intt(&truncate(xf, k), w), b))
                .collect();
            let bytes: usize = per_block.iter().sum();
            let whole = per_block.iter().filter(|&&m| m == N).count();
            ((k, bytes, total), (k, whole, blocks.len()))
        })
        .unzip();
    let used = &blocks[..blocks.len().min(C4_BLOCKS)];
    let rnd: Block = std::array::from_fn(|i| (i as u64 * 2_654_435_761 + 7) % P);
    let rnd_inv = intt(&rnd, w);
    let c4_random = (used.iter().map(|b| matches(&rnd_inv, b)).sum(), N * used.len());
    // Wrong bank: invert with w^2 (also a primitive 27th root) instead of w.
    let w2 = w * w % P;
    let c4_wrong_root = (
        c.coeffs.iter().zip(&blocks).map(|(xf, b)| matches(&intt(xf, w2), b)).sum(),
        total,
    );
    let mut label_rows: Vec<[[i8; 3]; N]> = Vec::new();
    let mut seen: HashMap<Block, usize> = HashMap::new();
    for b in &blocks {
        let row: [[i8; 3]; N] = std::array::from_fn(label);
        if !label_rows.contains(&row) {
            label_rows.push(row);
        }
        *seen.entry(*b).or_insert(0) += 1;
    }
    let best = seen.values().copied().max().unwrap_or(0);
    Controls {
        c1_identity,
        c2_carrier_roundtrip,
        c3,
        c3_blocks,
        c4_random,
        c4_wrong_root,
        c5_label_rows_distinct: label_rows.len(),
        c5_labels_only_max_exact: (best, blocks.len()),
    }
}

fn gcd(a: usize, b: usize) -> usize {
    if b == 0 { a } else { gcd(b, a % b) }
}

/// The cross-language line. `scripts/rime_sphere_carrier.py` computes the
/// same line from the ORIGINAL Python ntt/intt; CI requires equality.
pub fn xcheck_line(ctl: &Controls, c: &Carrier, carrier_sha: &str) -> String {
    let c3: Vec<String> = ctl.c3.iter().map(|(k, m, t)| format!("{k}:{m}/{t}")).collect();
    format!(
        "RIMESPHERE-XCHECK|schema=hebc.rime.sphere.xcheck.v1|w={}|blocks={}|c1={}|c3={}|c4_random={}/{}|carrier_sha={carrier_sha}|json=0\n",
        c.bank.w,
        c.coeffs.len(),
        if ctl.c1_identity { "PASS" } else { "FAIL" },
        c3.join(","),
        ctl.c4_random.0,
        ctl.c4_random.1
    )
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Audit {
    pub carrier: String,
    pub xcheck: String,
    pub hbp: Vec<u8>,
    pub hbi: Vec<u8>,
    pub anchor: String,
    pub measure: String,
}

/// The original pipeline's own fallback input when enwik8 is absent.
pub fn default_input() -> Vec<u8> {
    (0..13_500u32).map(|i| u8::try_from(i * 7 % 251).unwrap_or(0)).collect()
}

pub fn generate(data: &[u8]) -> Result<Audit, String> {
    let bank = bank()?;
    let c = encode(data, bank);
    let carrier = render(&c);
    if decode(&parse(&carrier)?)? != data {
        return Err("bridge did not return the input bytes".into());
    }
    let ctl = controls(data, &c);
    // PASS gates ONLY on mathematical guarantees, which must hold for every
    // input: C1/C2 (the NTT is invertible over Z/p because 27 | p-1), C3 at
    // k=27 (that is C1), wrong-root byte 0 (inverse index 0 is root-free),
    // and C5's label rows being one positional row for nonempty complete
    // blocks (zero for tail-only/empty input). The fraction /
    // random / wrong-root / labels-only RECOVERY COUNTS are observations about
    // this input and are reported, never required: a constant block, for
    // example, recovers from one coefficient (see tests).
    let full = ctl.c3.last().is_some_and(|&(k, m, t)| k == N && m == t)
        && ctl.c3_blocks.last().is_some_and(|&(k, m, t)| k == N && m == t);
    let w2 = c.bank.w * c.bank.w % P;
    let byte0_root_free = c.coeffs.iter().all(|xf| intt(xf, w2)[0] == intt(xf, c.bank.w)[0]);
    let pass = ctl.c1_identity
        && ctl.c2_carrier_roundtrip
        && full
        && byte0_root_free
        && ctl.c5_label_rows_distinct == usize::from(!c.coeffs.is_empty());
    let carrier_sha = hex(&sha256(carrier.as_bytes()));
    let xcheck = xcheck_line(&ctl, &c, &carrier_sha);
    let coeff_bits = (64 - (P - 1).leading_zeros()) as usize;
    let block_bits = coeff_bits * N;
    let source_bits = 8 * N;
    let g = gcd(block_bits, source_bits);
    let c3: Vec<String> = ctl.c3.iter().map(|(k, m, t)| format!("{k}:{m}/{t}")).collect();
    let c3b: Vec<String> = ctl.c3_blocks.iter().map(|(k, m, t)| format!("{k}:{m}/{t}")).collect();
    let c3b = c3b.join(",");
    let sh = &carrier_sha[..16];
    let body = format!(
        "HBP|schema={SCHEMA}|source={SOURCE}|source_transform_retained=1|p={}|g={}|w={}|N={N}|bytes={}|blocks={}|tail={}|labels=POSITION_ONLY|coefficients_carried={N}/{N}|c1={}|c2_carrier_roundtrip={}|c3_bytes={}|c3_blocks={c3b}|{GUARANTEES}|c4_random={}/{}|c4_wrong_root={}/{}|c5_label_rows_distinct={}|c5_labels_only_max_exact_blocks={}/{}|input_sha={}|carrier_sha={carrier_sha}|xcheck_sha={}|sh={sh}|prev={}",
        c.bank.p, c.bank.g, c.bank.w, c.input_len, c.coeffs.len(), c.tail.len(),
        u8::from(ctl.c1_identity), u8::from(ctl.c2_carrier_roundtrip), c3.join(","),
        ctl.c4_random.0, ctl.c4_random.1, ctl.c4_wrong_root.0, ctl.c4_wrong_root.1,
        ctl.c5_label_rows_distinct, ctl.c5_labels_only_max_exact.0, ctl.c5_labels_only_max_exact.1,
        c.input_sha, hex(&sha256(xcheck.as_bytes())), hex(&[0u8; 32])
    );
    let record_sha = sha256(body.as_bytes());
    let mut chain_in = [0u8; 64];
    chain_in[32..].copy_from_slice(&record_sha);
    let chain = sha256(&chain_in);
    let hbp = format!("{body}|record_sha={}|chain={}|json=0\n", hex(&record_sha), hex(&chain)).into_bytes();
    let hbi = format!(
        "HBI|schema={SCHEMA}|record=1|offset=0|len={}|sh={sh}|row_sha={}|chain={}|json=0\n",
        hbp.len(), hex(&sha256(&hbp)), hex(&chain)
    ).into_bytes();
    let anchor = format!(
        "ANCHOR|schema={SCHEMA}|records=1|hbp_sha={}|hbi_sha={}|carrier_sha={carrier_sha}|chain={}|json=0\n",
        hex(&sha256(&hbp)), hex(&sha256(&hbi)), hex(&chain)
    );
    let measure = format!(
        "RIMESPHERE|result={}|source_transform_retained=1|labels=POSITION_ONLY|coefficients_carried={N}/{N}|c1=byte_exact|c2=carrier_roundtrip|c3_bytes={}|c3_blocks={c3b}|{GUARANTEES}|c4_random={}/{}|c4_wrong_root={}/{}|c5_labels_only_max_exact_blocks={}/{}|coeff_bits={coeff_bits}|block_bits={block_bits}|source_block_bits={source_bits}|carry_ratio={}/{}|compression_claimed=0|carrier_sha={carrier_sha}|json=0\n",
        if pass { "PASS" } else { "FAIL" }, c3.join(","),
        ctl.c4_random.0, ctl.c4_random.1, ctl.c4_wrong_root.0, ctl.c4_wrong_root.1,
        ctl.c5_labels_only_max_exact.0, ctl.c5_labels_only_max_exact.1,
        block_bits / g, source_bits / g
    );
    if !pass {
        return Err(format!("controls failed: {measure}"));
    }
    Ok(Audit { carrier, xcheck, hbp, hbi, anchor, measure })
}

pub fn verify(a: &Audit, data: &[u8]) -> Result<(), String> {
    if decode(&parse(&a.carrier)?)? != data {
        return Err("carrier does not decode to the input".into());
    }
    if generate(data)? != *a {
        return Err("RIME sphere bridge receipt replay mismatch".into());
    }
    Ok(())
}

const FILES: [&str; 6] = ["carrier.rime", "xcheck.measure", "run.hbp", "index.hbi", "run.anchor", "run.measure"];

pub fn write(dir: &Path, a: &Audit) -> Result<(), String> {
    std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    let parts: [&[u8]; 6] = [
        a.carrier.as_bytes(), a.xcheck.as_bytes(), &a.hbp, &a.hbi, a.anchor.as_bytes(), a.measure.as_bytes(),
    ];
    for (name, bytes) in FILES.iter().zip(parts) {
        std::fs::write(dir.join(name), bytes).map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn verify_directory(dir: &Path, data: &[u8]) -> Result<(), String> {
    let s = |n: &str| std::fs::read_to_string(dir.join(n)).map_err(|e| format!("{n}: {e}"));
    let a = Audit {
        carrier: s(FILES[0])?,
        xcheck: s(FILES[1])?,
        hbp: std::fs::read(dir.join(FILES[2])).map_err(|e| e.to_string())?,
        hbi: std::fs::read(dir.join(FILES[3])).map_err(|e| e.to_string())?,
        anchor: s(FILES[4])?,
        measure: s(FILES[5])?,
    };
    verify(&a, data)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// sha256 of carrier.rime written by scripts/rime_sphere_carrier.py from
    /// the ORIGINAL Python ntt on the default input (cross-language pin).
    const PYTHON_CARRIER_SHA: &str =
        "6121bb3ff559cf5d309f62821ab166578466edd85fd27c8e35f63ab5262dabde";

    #[test]
    fn bank_matches_original_script() {
        let b = bank().unwrap();
        assert_eq!((b.p, b.g, b.w), (1_000_081, 7, 951_846));
    }

    #[test]
    fn labels_are_positions_not_values() {
        assert_eq!(label(0), [-1, -1, -1]);
        assert_eq!(label(13), [0, 0, 0]);
        assert_eq!(label(26), [1, 1, 1]);
        let all: Vec<[i8; 3]> = (0..N).map(label).collect();
        for (i, a) in all.iter().enumerate() {
            assert!(all[i + 1..].iter().all(|b| b != a), "27 labels are distinct cells");
        }
        // Two different blocks get the same label row: labels carry no block data.
        let d = default_input();
        let c = encode(&d, bank().unwrap());
        assert_ne!(c.coeffs[0], c.coeffs[1]);
        assert_eq!(controls(&d, &c).c5_label_rows_distinct, 1);
    }

    #[test]
    fn rust_carrier_equals_python_original_byte_for_byte() {
        let a = generate(&default_input()).unwrap();
        assert_eq!(hex(&sha256(a.carrier.as_bytes())), PYTHON_CARRIER_SHA);
    }

    #[test]
    fn original_controls_reproduced() {
        let d = default_input();
        let ctl = controls(&d, &encode(&d, bank().unwrap()));
        assert!(ctl.c1_identity && ctl.c2_carrier_roundtrip);
        let exact: Vec<usize> = ctl.c3.iter().map(|&(_, m, _)| m).collect();
        assert_eq!(exact, vec![0, 0, 0, 0, 0, 13_500]);
        let whole: Vec<usize> = ctl.c3_blocks.iter().map(|&(_, m, _)| m).collect();
        assert_eq!(whole, vec![0, 0, 0, 0, 0, 500]);
        assert_eq!(ctl.c4_random, (0, 2_700));
        assert_eq!(ctl.c4_wrong_root, (500, 13_500), "byte 0 of each block, nothing else");
    }

    /// C3 failure below k=27 is an OBSERVATION, not a theorem: a constant
    /// block has X = (27c, 0, ..., 0), so one coefficient recovers it. The
    /// bridge must still PASS, because PASS gates only on guarantees.
    #[test]
    fn c3_fraction_failure_is_observed_not_universal() {
        let flat = vec![42u8; 27 * 4];
        let c = encode(&flat, bank().unwrap());
        assert!(c.coeffs.iter().all(|xf| xf[1..].iter().all(|&v| v == 0)));
        let ctl = controls(&flat, &c);
        assert!(ctl.c3.iter().all(|&(_, m, t)| m == t));
        assert!(ctl.c3_blocks.iter().all(|&(_, m, t)| m == t));
        let m = generate(&flat).unwrap().measure;
        assert!(m.starts_with("RIMESPHERE|result=PASS|"));
        assert!(m.contains("c3_blocks=3:4/4,"));
    }

    /// Bytes and blocks are different measures: chance byte matches are
    /// counted in c3_bytes but never make a whole block.
    #[test]
    fn c3_bytes_and_blocks_are_reported_separately() {
        let data: Vec<u8> = (0..27u32 * 40).map(|i| u8::try_from(i % 3).unwrap()).collect();
        let ctl = controls(&data, &encode(&data, bank().unwrap()));
        for (&(k, bytes, _), &(_, whole, _)) in ctl.c3.iter().zip(&ctl.c3_blocks) {
            assert!(bytes >= whole * N, "k={k}");
        }
        let m = generate(&data).unwrap().measure;
        assert!(m.contains("|c3_bytes=") && m.contains("|c3_blocks=") && m.contains("|theorem=C1,C2,"));
    }

    #[test]
    fn arbitrary_input_with_tail_is_byte_exact() {
        let data: Vec<u8> = (0..1000u32).map(|i| u8::try_from((i * 131 + 17) % 256).unwrap()).collect();
        let a = generate(&data).unwrap();
        assert_eq!(decode(&parse(&a.carrier).unwrap()).unwrap(), data);
        verify(&a, &data).unwrap();
    }

    #[test]
    fn carrier_and_receipt_corruption_fail_closed() {
        let d = default_input();
        let a = generate(&d).unwrap();
        verify(&a, &d).unwrap();
        let mut c = parse(&a.carrier).unwrap();
        c.coeffs[3][5] = (c.coeffs[3][5] + 1) % P;
        assert!(decode(&c).is_err(), "one changed coefficient must not decode");
        let mut c = parse(&a.carrier).unwrap();
        c.bank.w = c.bank.w * c.bank.w % P;
        assert!(decode(&c).is_err(), "wrong bank root must not decode");
        let mut forged = a.clone();
        forged.hbp[100] ^= 1;
        assert!(verify(&forged, &d).is_err());
        let mut forged = a.clone();
        forged.xcheck.push(' ');
        assert!(verify(&forged, &d).is_err());
    }

    /// The carrier includes a tail for inputs shorter than one NTT block.
    /// These valid byte streams have *zero* positional label rows, not one.
    #[test]
    fn empty_and_tail_only_files_roundtrip_and_pass_controls() {
        for data in [
            Vec::<u8>::new(),
            vec![7u8],
            vec![9u8; N - 1],
            vec![42u8; N],
            vec![11u8; N + 1],
        ] {
            let a = generate(&data).expect("bridge must support all lengths");
            let c = parse(&a.carrier).unwrap();
            assert_eq!(decode(&c).unwrap(), data);
            verify(&a, &data).unwrap();
            assert_eq!(c.coeffs.len(), data.len() / N);
            assert_eq!(c.tail.len(), data.len() % N);
            let ctl = controls(&data, &c);
            assert_eq!(ctl.c5_label_rows_distinct, usize::from(data.len() >= N));
            assert!(a.measure.contains("compression_claimed=0"));
        }
    }

    #[test]
    fn carry_cost_is_stated_not_hidden() {
        let m = generate(&default_input()).unwrap().measure;
        assert!(m.contains("coeff_bits=20|block_bits=540|source_block_bits=216|carry_ratio=5/2"));
        assert!(m.contains("compression_claimed=0"));
    }
}
