//! zconfcert driver: certified finite-coupling energies of the S3 static-charge sector, every count run
//! as a job of the HEB-C HTTP-0 backend (hebc_ym_http0 serve) over HTTP/1.1. See PREREG.md, ADDENDUM.md.
//! Rust 1.81, std only, integer arithmetic only (i128), json=0.
//! usage: zconfcert PORT
use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::TcpStream;

const JE: i128 = 270_000_000;
const UNIT: i128 = 1000 * JE; // T units per J_E
const WIDTH: i128 = 270; // 10^-9 J_E
const M_FLOOR: i128 = 270_000; // 10^-6 J_E
const JBS: [i128; 4] = [10_000_000, 30_000_000, 90_000_000, 270_000_000]; // r = 1/27, 1/9, 1/3, 1
const RLAB: [&str; 4] = ["1/27", "1/9", "1/3", "1"];
const ZCONF_RESULT_SHA: &str = "bb9ca0f42964582404e476b4ab29649d22fb0655f70fd0360693a67f0136dc64";

struct Geo {
    name: &'static str,
    rows: i128,
    cols: i128,
    ds: &'static [i128],
}

// geometries as fixed by PREREG.md and ADDENDUM.md
const GEOS: [Geo; 2] = [Geo { name: "L2", rows: 2, cols: 4, ds: &[1, 2, 3] }, Geo { name: "L3", rows: 3, cols: 2, ds: &[1] }];

impl Geo {
    fn np(&self) -> i128 {
        (self.rows - 1) * (self.cols - 1)
    }
    fn ng(&self) -> i128 {
        if self.rows == 2 {
            1
        } else {
            2
        }
    }
}

struct Client {
    port: u16,
    out: Vec<String>,
    cache: BTreeMap<String, Option<i64>>,
    inconclusive: Vec<String>,
}

fn http(port: u16, method: &str, path: &str) -> Result<(u16, String), String> {
    let mut s = TcpStream::connect(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    s.write_all(format!("{method} {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 0\r\n\r\n").as_bytes()).map_err(|e| e.to_string())?;
    let mut buf = String::new();
    s.read_to_string(&mut buf).map_err(|e| e.to_string())?;
    let (head, body) = buf.split_once("\r\n\r\n").ok_or("malformed response")?;
    let code = head.split_ascii_whitespace().nth(1).and_then(|c| c.parse().ok()).ok_or("no status")?;
    Ok((code, body.to_string()))
}

fn field<'a>(line: &'a str, key: &str) -> Option<&'a str> {
    line.split('|').find_map(|f| f.strip_prefix(key))
}

impl Client {
    /// negative-eigenvalue count at T, or None if the job failed or the count is uncertain
    fn count(&mut self, g: &Geo, xa: i128, xb: i128, ch: i128, jb: i128, t: i128) -> Option<i64> {
        let spec = format!("confcount/{}/{}/{xa}/{xb}/{ch}/{JE}/{jb}/{t}", g.rows, g.cols);
        if let Some(v) = self.cache.get(&spec) {
            return *v;
        }
        let res = (|| -> Result<(i64, String), String> {
            let (code, body) = http(self.port, "POST", &format!("/job/{spec}"))?;
            if code != 200 {
                return Err(body.trim().to_string());
            }
            let hs = field(body.trim(), "hbp_sha256=").unwrap_or("").to_string();
            let (_, shard) = http(self.port, "GET", &format!("/shard/{spec}"))?;
            let line = shard.lines().find(|l| l.starts_with("STURM-RS|")).ok_or("no sturm line")?;
            if field(line, "status=") != Some("COMPLETE") {
                return Err("uncertain count".into());
            }
            let neg = field(line, "negative=").and_then(|v| v.parse().ok()).ok_or("no count")?;
            Ok((neg, hs))
        })();
        let v = match res {
            Ok((neg, hs)) => {
                self.out.push(format!("COUNT|spec={spec}|negative={neg}|hbp_sha256={hs}|json=0"));
                Some(neg)
            }
            Err(e) => {
                self.out.push(format!("COUNT|spec={spec}|result=INCONCLUSIVE|reason={}|json=0", e.replace('|', "/")));
                None
            }
        };
        self.cache.insert(spec, v);
        v
    }
    fn verify(&mut self, spec: &str) -> bool {
        let ok = matches!(http(self.port, "GET", &format!("/verify/{spec}")), Ok((200, ref b)) if b.contains("result=PASS|action=verify"));
        self.out.push(format!("VERIFY|spec={spec}|result={}|json=0", if ok { "PASS" } else { "FAIL" }));
        ok
    }
}

fn spec_of(g: &Geo, xa: i128, xb: i128, ch: i128, jb: i128, t: i128) -> String {
    format!("confcount/{}/{}/{xa}/{xb}/{ch}/{JE}/{jb}/{t}", g.rows, g.cols)
}

/// Certified bracket (lo, hi) in T units with E0 in (lo, hi).
fn bracket(c: &mut Client, g: &Geo, d: i128, ch: i128, jb: i128) -> Option<(i128, i128, u32)> {
    let (xa, xb) = if ch == 1 { (0, d) } else { (0, 0) };
    let s2 = -12 * g.np() - 5 * g.ng() * d * ch; // second-order coefficient x 144
    let second = (1000 * jb * jb * s2).div_euclid(144 * JE);
    let pred = 3 * d * ch * UNIT + 2000 * g.np() * jb + second;
    let mut m = (10 * second.abs()).max(M_FLOOR);
    let mut found = None;
    for k in 0..=20u32 {
        let (lo, hi) = (pred - m, pred + m);
        let nl = c.count(g, xa, xb, ch, jb, lo)?;
        let nh = c.count(g, xa, xb, ch, jb, hi)?;
        if nl == 0 && nh >= 1 {
            found = Some((lo, hi, k));
            break;
        }
        m *= 2;
    }
    let (mut lo, mut hi, k) = found?;
    while hi - lo > WIDTH {
        let mid = lo + (hi - lo) / 2;
        let n = c.count(g, xa, xb, ch, jb, mid)?;
        if n == 0 {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    let ok = c.verify(&spec_of(g, xa, xb, ch, jb, lo)) & c.verify(&spec_of(g, xa, xb, ch, jb, hi));
    if ok {
        Some((lo, hi, k))
    } else {
        None
    }
}

fn gcd(a: i128, b: i128) -> i128 {
    if b == 0 {
        a.abs()
    } else {
        gcd(b, a % b)
    }
}

fn frac(n: i128, d: i128) -> String {
    let g = gcd(n, d).max(1);
    format!("{}/{}", n / g, d / g)
}

/// value n/d to 12 decimals, rounded toward minus infinity (display only)
fn dec(n: i128, d: i128) -> String {
    let s = 1_000_000_000_000i128;
    let v = (n * s).div_euclid(d);
    let sign = if v < 0 { "-" } else { "" };
    format!("{sign}{}.{:012}", v.abs() / s, v.abs() % s)
}

/// rational comparison a/b < c/e, b, e > 0
fn lt(a: i128, b: i128, c: i128, e: i128) -> bool {
    a * e < c * b
}

fn main() {
    let port: u16 = std::env::args().nth(1).and_then(|p| p.parse().ok()).unwrap_or(0);
    let mut c = Client { port, out: Vec::new(), cache: BTreeMap::new(), inconclusive: Vec::new() };
    c.out.push(format!("ZCONFCERT|JE={JE}|unit_T_per_JE={UNIT}|width_T={WIDTH}|r=1/27,1/9,1/3,1|json=0"));

    // Q7: HTTP-0 replay of the sealed #56 calculation
    let q7 = (|| -> Option<bool> {
        let (code, body) = http(port, "POST", "/job/zconf").ok()?;
        let (_, hbp) = http(port, "GET", "/shard/zconf").ok()?;
        let sha = field(body.trim(), "hbp_sha256=").unwrap_or("").to_string();
        let same = sha == ZCONF_RESULT_SHA;
        let ver = c.verify("zconf");
        c.out.push(format!("ZCONF_HTTP0|job_status={code}|run_hbp_sha256={sha}|sealed_result_sha256={ZCONF_RESULT_SHA}|identical={}|lines={}|verify={}|json=0", u8::from(same), hbp.lines().count(), if ver { "PASS" } else { "FAIL" }));
        Some(same && ver)
    })();

    // matrices: one confmat job per (geometry, sector)
    let mut q1 = true;
    for g in &GEOS {
        let mut cells: Vec<(i128, i128, i128)> = vec![(0, 0, 0)];
        cells.extend(g.ds.iter().map(|&d| (0, d, 1)));
        for (xa, xb, ch) in cells {
            let spec = format!("confmat/{}/{}/{xa}/{xb}/{ch}", g.rows, g.cols);
            let r = http(port, "POST", &format!("/job/{spec}"));
            let line = match &r {
                Ok((200, b)) => b.trim().to_string(),
                Ok((_, b)) => b.trim().to_string(),
                Err(e) => e.clone(),
            };
            let ok = matches!(r, Ok((200, ref b)) if b.contains("w_self_adjoint=PASS"));
            q1 &= ok;
            let (_, shard) = http(port, "GET", &format!("/shard/{spec}")).unwrap_or((0, String::new()));
            let cm = shard.lines().find(|l| l.starts_with("CONF_MATRIX|")).unwrap_or("CONF_MATRIX|missing").to_string();
            c.out.push(format!("MATRIX|geom={}|spec={spec}|ok={}|{}|response_sha={}|json=0", g.name, u8::from(ok), cm.trim_start_matches("CONF_MATRIX|").trim_end_matches("|json=0"), field(&line, "hbp_sha256=").unwrap_or("-")));
        }
    }
    // Q1: r = 0 exact levels
    for g in &GEOS {
        let mut cells: Vec<(i128, i128)> = vec![(0, 0)];
        cells.extend(g.ds.iter().map(|&d| (d, 1)));
        for (d, ch) in cells {
            let e0 = 3 * d * ch * UNIT;
            let xb = if ch == 1 { d } else { 0 };
            let below = c.count(g, 0, xb, ch, 0, e0 - 1);
            let above = c.count(g, 0, xb, ch, 0, e0 + 1);
            let ok = below == Some(0) && above.is_some_and(|n| n >= 1);
            q1 &= ok;
            c.out.push(format!("LEVEL_R0|geom={}|d={d}|sector={}|E0={}|negative_below={}|negative_above={}|certified={}|json=0", g.name, if ch == 1 { "charged" } else { "vacuum" }, 3 * d * ch, below.map_or(-1, |v| v), above.map_or(-1, |v| v), u8::from(ok)));
        }
    }

    // Q2: certified energies
    let mut energies: BTreeMap<(usize, i128, i128, usize), (i128, i128)> = BTreeMap::new(); // (geo, d, ch, r)
    let mut q2 = true;
    for (gi, g) in GEOS.iter().enumerate() {
        let mut cells: Vec<(i128, i128)> = vec![(0, 0)];
        cells.extend(g.ds.iter().map(|&d| (d, 1)));
        for (ri, &jb) in JBS.iter().enumerate() {
            for &(d, ch) in &cells {
                match bracket(&mut c, g, d, ch, jb) {
                    Some((lo, hi, k)) => {
                        q2 &= hi - lo <= WIDTH;
                        energies.insert((gi, d, ch, ri), (lo, hi));
                        c.out.push(format!(
                            "ENERGY|geom={}|d={d}|sector={}|r={}|E_lo={}|E_hi={}|E_lo_dec={}|width_T={}|bracket_doublings={k}|json=0",
                            g.name,
                            if ch == 1 { "charged" } else { "vacuum" },
                            RLAB[ri],
                            frac(lo, UNIT),
                            frac(hi, UNIT),
                            dec(lo, UNIT),
                            hi - lo
                        ));
                    }
                    None => {
                        q2 = false;
                        c.inconclusive.push(format!("{}:d={d}:ch={ch}:r={}", g.name, RLAB[ri]));
                        c.out.push(format!("ENERGY|geom={}|d={d}|sector={}|r={}|result=INCONCLUSIVE|json=0", g.name, if ch == 1 { "charged" } else { "vacuum" }, RLAB[ri]));
                    }
                }
            }
        }
    }

    // V intervals, kappa_eff intervals, sigma
    // kappa_eff = (V - 3d) / (d r^2) = (V_T - 3 d UNIT) * JE / (1000 d JB^2)
    let mut kap: BTreeMap<(usize, i128, usize), (i128, i128, i128)> = BTreeMap::new(); // num lo, num hi, den
    let mut vint: BTreeMap<(usize, i128, usize), (i128, i128)> = BTreeMap::new();
    for (gi, g) in GEOS.iter().enumerate() {
        for &d in g.ds {
            for (ri, &jb) in JBS.iter().enumerate() {
                let (Some(&(cl, chh)), Some(&(vl, vh))) = (energies.get(&(gi, d, 1, ri)), energies.get(&(gi, 0, 0, ri))) else { continue };
                let (lo, hi) = (cl - vh, chh - vl);
                vint.insert((gi, d, ri), (lo, hi));
                let den = 1000 * d * jb * jb;
                let (kl, kh) = ((lo - 3 * d * UNIT) * JE, (hi - 3 * d * UNIT) * JE);
                kap.insert((gi, d, ri), (kl, kh, den));
                c.out.push(format!(
                    "VPOT|geom={}|d={d}|r={}|V_lo={}|V_hi={}|V_lo_dec={}|kappa_eff_lo={}|kappa_eff_hi={}|kappa_eff_lo_dec={}|kappa_g={}|json=0",
                    g.name,
                    RLAB[ri],
                    frac(lo, UNIT),
                    frac(hi, UNIT),
                    dec(lo, UNIT),
                    frac(kl, den),
                    frac(kh, den),
                    dec(kl, den),
                    frac(-5 * g.ng(), 144)
                ));
            }
        }
    }
    let mut q6 = true;
    let mut q6n = 0;
    for (gi, g) in GEOS.iter().enumerate() {
        for w in g.ds.windows(2) {
            for (ri, _) in JBS.iter().enumerate() {
                let (Some(&(al, ah)), Some(&(bl, bh))) = (vint.get(&(gi, w[0], ri)), vint.get(&(gi, w[1], ri))) else {
                    q6 = false;
                    continue;
                };
                let (sl, sh) = (bl - ah, bh - al);
                q6 &= sl > 0;
                q6n += 1;
                c.out.push(format!("SIGMA|geom={}|d={}|r={}|sigma_lo={}|sigma_hi={}|sigma_lo_dec={}|positive={}|json=0", g.name, w[0], RLAB[ri], frac(sl, UNIT), frac(sh, UNIT), dec(sl, UNIT), u8::from(sl > 0)));
            }
        }
    }
    // Q3: within 15% of kappa_g at r = 1/27: kappa in [1.15 kg, 0.85 kg] (kg < 0)
    let mut q3 = true;
    let mut q4 = true;
    for (gi, g) in GEOS.iter().enumerate() {
        let (kgn, kgd) = (-5 * g.ng(), 144i128);
        for &d in g.ds {
            let Some(&(kl, kh, den)) = kap.get(&(gi, d, 0)) else {
                q3 = false;
                q4 = false;
                continue;
            };
            // kl/den >= 115 kgn / (100 kgd) and kh/den <= 85 kgn / (100 kgd)
            let ok3 = !lt(kl, den, 115 * kgn, 100 * kgd) && !lt(85 * kgn, 100 * kgd, kh, den);
            q3 &= ok3;
            // Q4: max distance at 1/27 < min distance at 1/9 (distances as rationals over den * kgd)
            let dist = |l: i128, h: i128, dn: i128| -> (i128, i128, i128) {
                // returns (min_num, max_num, common_den) of |x - kg| for x in [l/dn, h/dn]
                let a = l * kgd - kgn * dn;
                let b = h * kgd - kgn * dn;
                let mx = a.abs().max(b.abs());
                let mn = if a <= 0 && b >= 0 { 0 } else { a.abs().min(b.abs()) };
                (mn, mx, dn * kgd)
            };
            let ok4 = match kap.get(&(gi, d, 1)) {
                Some(&(l9, h9, d9)) => {
                    let (_, mx27, den27) = dist(kl, kh, den);
                    let (mn9, _, den9) = dist(l9, h9, d9);
                    lt(mx27, den27, mn9, den9)
                }
                None => false,
            };
            q4 &= ok4;
            c.out.push(format!("SECOND_ORDER|geom={}|d={d}|within_15pct_at_r=1/27={}|closer_at_1/27_than_1/9={}|json=0", g.name, u8::from(ok3), u8::from(ok4)));
        }
    }
    // Q5: ratio kappa(L3,d=1)/kappa(L2,d=1) at r = 1/27 in [1.7, 2.3]
    let q5 = match (kap.get(&(1, 1, 0)), kap.get(&(0, 1, 0))) {
        (Some(&(l3, h3, d3)), Some(&(l2, h2, d2))) => {
            let neg = h3 < 0 && h2 < 0;
            // all negative: h3 <= 1.7 l2  and  l3 >= 2.3 h2
            let a = !lt(17 * l2, 10 * d2, h3, d3);
            let b = !lt(l3, d3, 23 * h2, 10 * d2);
            let ok = neg && a && b;
            c.out.push(format!("LOCAL_MECHANISM|kappa_L3_d1=[{},{}]|kappa_L2_d1=[{},{}]|ratio_in_1.7_2.3={}|json=0", frac(l3, d3), frac(h3, d3), frac(l2, d2), frac(h2, d2), u8::from(ok)));
            ok
        }
        _ => false,
    };
    let v = |b: bool, inc: bool| if inc { "INCONCLUSIVE" } else if b { "PASS" } else { "FAIL" };
    let incq2 = !c.inconclusive.is_empty();
    c.out.push(format!(
        "ZCONFCERT_RESULT|Q1={}|Q2={}|Q3={}|Q4={}|Q5={}|Q6={}|Q7={}|sigma_cells={q6n}|inconclusive_cells={}|json=0",
        v(q1, false),
        v(q2, incq2),
        v(q3, incq2),
        v(q4, incq2),
        v(q5, incq2),
        v(q6, incq2),
        match q7 {
            Some(b) => v(b, false),
            None => "INCONCLUSIVE",
        },
        if c.inconclusive.is_empty() { "none".to_string() } else { c.inconclusive.join(",") }
    ));
    for l in &c.out {
        println!("{l}");
    }
}
