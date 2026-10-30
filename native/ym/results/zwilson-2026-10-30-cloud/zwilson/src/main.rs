//! zwilson driver: certified spatial Wilson loops of the S3 vacuum on the open 2 x 4 ladder, every
//! computation a job of the HEB-C HTTP-0 backend (hebc_ym_http0 serve) over HTTP/1.1. See PREREG.md.
//! Rust 1.81, integer arithmetic only (i128 and big integers), json=0.
//! usage: zwilson PORT
use num_bigint::BigInt;
use num_traits::{Signed, Zero};
use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::TcpStream;

const JE: i128 = 270_000_000_000_000;
const UNIT: i128 = 1000 * JE; // T units per J_E
const LAM: i128 = 2_700_000; // lambda = 10^-8
const M_FLOOR: i128 = 270_000_000_000; // 10^-6 J_E
const NP: i128 = 3;
const RS: [(i128, i128); 4] = [(1, 27), (1, 9), (1, 3), (1, 1)];
const LOOPS: [usize; 3] = [1, 2, 3];
const ORDER: usize = 4;

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

/// exact rational with big integers, positive denominator
#[derive(Clone, Debug)]
struct Q {
    n: BigInt,
    d: BigInt,
}

fn q(n: i128, d: i128) -> Q {
    Q { n: BigInt::from(n), d: BigInt::from(d) }
}

impl Q {
    fn parse(s: &str) -> Option<Q> {
        let (a, b) = s.split_once('/')?;
        Some(Q { n: a.parse().ok()?, d: b.parse().ok()? })
    }
    fn mul(&self, o: &Q) -> Q {
        Q { n: &self.n * &o.n, d: &self.d * &o.d }
    }
    fn div(&self, o: &Q) -> Q {
        let (n, d) = (&self.n * &o.d, &self.d * &o.n);
        if d.is_negative() {
            Q { n: -n, d: -d }
        } else {
            Q { n, d }
        }
    }
    fn sub(&self, o: &Q) -> Q {
        Q { n: &self.n * &o.d - &o.n * &self.d, d: &self.d * &o.d }
    }
    fn add(&self, o: &Q) -> Q {
        Q { n: &self.n * &o.d + &o.n * &self.d, d: &self.d * &o.d }
    }
    fn lt(&self, o: &Q) -> bool {
        &self.n * &o.d < &o.n * &self.d
    }
    fn abs(&self) -> Q {
        Q { n: self.n.abs(), d: self.d.clone() }
    }
    fn pow(&self, k: usize) -> Q {
        (0..k).fold(q(1, 1), |a, _| a.mul(self))
    }
    /// 15 significant decimals of the value, rounded toward minus infinity (display only)
    fn dec(&self) -> String {
        let s = BigInt::from(10).pow(15);
        let v = num_integer::Integer::div_floor(&(&self.n * &s), &self.d);
        let neg = v.is_negative();
        let a = v.abs();
        let (ip, fp) = (num_integer::Integer::div_floor(&a, &s), num_integer::Integer::mod_floor(&a, &s));
        format!("{}{}.{:0>15}", if neg { "-" } else { "" }, ip, fp.to_string())
    }
}

struct Client {
    port: u16,
    out: Vec<String>,
    cache: BTreeMap<String, Option<i64>>,
}

impl Client {
    fn job(&mut self, spec: &str) -> Result<(String, String), String> {
        let (code, body) = http(self.port, "POST", &format!("/job/{spec}"))?;
        if code != 200 {
            return Err(body.trim().replace('|', "/"));
        }
        let hs = field(body.trim(), "hbp_sha256=").unwrap_or("").to_string();
        let (_, shard) = http(self.port, "GET", &format!("/shard/{spec}"))?;
        Ok((hs, shard))
    }
    fn matrix(&mut self, x1: usize, jb: i128, lam: i128) -> bool {
        let spec = format!("wilsonmat/2/4/0/{x1}/{jb}/{lam}");
        if self.cache.contains_key(&spec) {
            return self.cache[&spec].is_some();
        }
        let r = self.job(&spec);
        let ok = matches!(&r, Ok((_, s)) if s.contains("w_self_adjoint=PASS"));
        match &r {
            Ok((hs, shard)) => {
                let cm = shard.lines().find(|l| l.starts_with("CONF_MATRIX|")).unwrap_or("CONF_MATRIX|missing");
                self.out.push(format!("MATRIX|spec={spec}|ok={}|states={}|w_self_adjoint={}|hbp_sha256={hs}|json=0", u8::from(ok), field(cm, "states=").unwrap_or("-"), field(cm, "w_self_adjoint=").unwrap_or("-")));
            }
            Err(e) => self.out.push(format!("MATRIX|spec={spec}|result=INCONCLUSIVE|reason={e}|json=0")),
        }
        self.cache.insert(spec, if ok { Some(1) } else { None });
        ok
    }
    fn count(&mut self, x1: usize, jb: i128, lam: i128, t: i128) -> Option<i64> {
        let spec = format!("wilsoncount/2/4/0/{x1}/{jb}/{lam}/{JE}/{t}");
        if let Some(v) = self.cache.get(&spec) {
            return *v;
        }
        let v = match self.job(&spec) {
            Ok((hs, shard)) => {
                let line = shard.lines().find(|l| l.starts_with("STURM-RS|")).unwrap_or("");
                match (field(line, "status="), field(line, "negative=").and_then(|v| v.parse::<i64>().ok())) {
                    (Some("COMPLETE"), Some(n)) => {
                        self.out.push(format!("COUNT|spec={spec}|negative={n}|hbp_sha256={hs}|json=0"));
                        Some(n)
                    }
                    _ => {
                        self.out.push(format!("COUNT|spec={spec}|result=INCONCLUSIVE|reason=uncertain|json=0"));
                        None
                    }
                }
            }
            Err(e) => {
                self.out.push(format!("COUNT|spec={spec}|result=INCONCLUSIVE|reason={e}|json=0"));
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
    /// bisect a certified bracket (count(lo) = 0, count(hi) >= 1) to width <= 1, verify both ends
    fn bisect(&mut self, x1: usize, jb: i128, lam: i128, mut lo: i128, mut hi: i128) -> Option<(i128, i128)> {
        while hi - lo > 1 {
            let mid = lo + (hi - lo) / 2;
            if self.count(x1, jb, lam, mid)? == 0 {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        let a = self.verify(&format!("wilsoncount/2/4/0/{x1}/{jb}/{lam}/{JE}/{lo}"));
        let b = self.verify(&format!("wilsoncount/2/4/0/{x1}/{jb}/{lam}/{JE}/{hi}"));
        if a && b {
            Some((lo, hi))
        } else {
            None
        }
    }
}

fn main() {
    let port: u16 = std::env::args().nth(1).and_then(|p| p.parse().ok()).unwrap_or(0);
    let mut c = Client { port, out: Vec::new(), cache: BTreeMap::new() };
    c.out.push(format!("ZWILSON|geometry=L2_open_2x4|loops=1x1,1x2,1x3|JE={JE}|lambda=LAM/JE={LAM}/{JE}|r=1/27,1/9,1/3,1|json=0"));

    // W1: exact series, two methods
    let mut series: BTreeMap<(usize, usize), Vec<Q>> = BTreeMap::new(); // (method, loop) -> c_k
    let mut series_ok = true;
    for method in 0..2usize {
        let spec = format!("wilsonseries/2/4/{method}/{ORDER}");
        match c.job(&spec) {
            Ok((hs, shard)) => {
                for l in shard.lines() {
                    if l.starts_with("WSERIES_BASIS|") {
                        series_ok &= l.contains("e_w_self_adjoint=PASS") && l.contains("orthogonality=PASS");
                    }
                    if let (Some(lp), Some(cs)) = (field(l, "loop=1x"), field(l, "c_k=")) {
                        let v: Option<Vec<Q>> = cs.split(',').map(Q::parse).collect();
                        if let (Ok(a), Some(v)) = (lp.parse::<usize>(), v) {
                            series.insert((method, a), v);
                        }
                    }
                    if l.starts_with("WSERIES") {
                        c.out.push(l.to_string());
                    }
                }
                let ver = c.verify(&spec);
                series_ok &= ver;
                c.out.push(format!("SERIES_JOB|spec={spec}|hbp_sha256={hs}|verify={}|json=0", if ver { "PASS" } else { "FAIL" }));
            }
            Err(e) => {
                series_ok = false;
                c.out.push(format!("SERIES_JOB|spec={spec}|result=INCONCLUSIVE|reason={e}|json=0"));
            }
        }
    }
    let mut w1 = series_ok;
    let mut lead: BTreeMap<usize, Q> = BTreeMap::new();
    for &a in &LOOPS {
        let (Some(sa), Some(sb)) = (series.get(&(0, a)), series.get(&(1, a))) else {
            w1 = false;
            continue;
        };
        let same = sa.len() == sb.len() && sa.iter().zip(sb).all(|(x, y)| &x.n * &y.d == &y.n * &x.d);
        let below_zero = (0..a).all(|k| sa[k].n.is_zero());
        let lead_pos = sa[a].n.is_positive();
        w1 &= same && below_zero && lead_pos;
        if a == 1 {
            w1 &= &sa[1].n * BigInt::from(6) == sa[1].d;
        }
        lead.insert(a, sa[a].clone());
        c.out.push(format!("SERIES_CHECK|loop=1x{a}|methods_identical={}|zero_below_order_A={}|leading_positive={}|c_AA={}/{}|json=0", u8::from(same), u8::from(below_zero), u8::from(lead_pos), sa[a].n, sa[a].d));
    }

    // certified values
    let mut wv: BTreeMap<(usize, usize), (Q, Q)> = BTreeMap::new(); // (loop, r index) -> [lo, hi]
    let mut w2 = true;
    let mut inconclusive: Vec<String> = Vec::new();
    for (ri, &(rn, rd)) in RS.iter().enumerate() {
        let jb = JE * rn / rd;
        // E0(0)
        let second = -1000 * NP * jb * jb / (12 * JE);
        let pred = 2000 * NP * jb + second;
        let mut m = (10 * second.abs()).max(M_FLOOR);
        let e0 = (|| -> Option<(i128, i128)> {
            if !c.matrix(1, jb, 0) {
                return None;
            }
            for _ in 0..=20 {
                let (lo, hi) = (pred - m, pred + m);
                if c.count(1, jb, 0, lo)? == 0 && c.count(1, jb, 0, hi)? >= 1 {
                    return c.bisect(1, jb, 0, lo, hi);
                }
                m *= 2;
            }
            None
        })();
        let Some((l0, u0)) = e0 else {
            w2 = false;
            inconclusive.push(format!("E0:r={rn}/{rd}"));
            continue;
        };
        c.out.push(format!("ENERGY0|r={rn}/{rd}|T_lo={l0}|T_hi={u0}|E0_lo={}|json=0", q(l0, UNIT).dec()));
        for &a in &LOOPS {
            let mut ends = Vec::new();
            for lam in [LAM, -LAM] {
                let got = (|| -> Option<(i128, i128)> {
                    if !c.matrix(a, jb, lam) {
                        return None;
                    }
                    let (lo, hi) = (l0 - 2000 * LAM - 1, u0 + 2000 * LAM + 1);
                    if c.count(a, jb, lam, lo)? == 0 && c.count(a, jb, lam, hi)? >= 1 {
                        c.bisect(a, jb, lam, lo, hi)
                    } else {
                        None
                    }
                })();
                ends.push(got);
            }
            let (Some((lp, _)), Some((lm, _))) = (ends[0], ends[1]) else {
                w2 = false;
                inconclusive.push(format!("1x{a}:r={rn}/{rd}"));
                continue;
            };
            // <W> in [(L+ - U0)/(1000 LAM), (U0 - L-)/(1000 LAM)]
            let (lo, hi) = (q(lp - u0, 1000 * LAM), q(u0 - lm, 1000 * LAM));
            let width_ok = (u0 - lm - (lp - u0)) * 1_000_000_000 <= 4 * 1000 * LAM;
            let pos = lp - u0 > 0;
            w2 &= width_ok && pos;
            c.out.push(format!(
                "WILSON|loop=1x{a}|r={rn}/{rd}|W_lo={}/{}|W_hi={}/{}|W_lo_dec={}|W_hi_dec={}|width_T={}|width_le_4e-9={}|positive={}|json=0",
                lo.n,
                lo.d,
                hi.n,
                hi.d,
                lo.dec(),
                hi.dec(),
                u0 - lm - (lp - u0),
                u8::from(width_ok),
                u8::from(pos)
            ));
            wv.insert((a, ri), (lo, hi));
        }
    }

    // W3, W4, two-term comparison
    let rq = |ri: usize| q(RS[ri].0, RS[ri].1);
    let mut w3 = true;
    let mut w4 = true;
    for &a in &LOOPS {
        let (Some(ca), Some(full)) = (lead.get(&a), series.get(&(0, a))) else {
            w3 = false;
            w4 = false;
            continue;
        };
        let ratio = |ri: usize| -> Option<(Q, Q)> {
            let (lo, hi) = wv.get(&(a, ri))?;
            let p = ca.mul(&rq(ri).pow(a));
            Some((lo.div(&p), hi.div(&p)))
        };
        let (Some((r27l, r27h)), Some((r9l, r9h))) = (ratio(0), ratio(1)) else {
            w3 = false;
            w4 = false;
            continue;
        };
        let ok3 = !r27l.lt(&q(4, 5)) && !q(5, 4).lt(&r27h);
        w3 &= ok3;
        let one = q(1, 1);
        let maxd = |l: &Q, h: &Q| -> Q {
            let (a1, b1) = (l.sub(&one).abs(), h.sub(&one).abs());
            if a1.lt(&b1) {
                b1
            } else {
                a1
            }
        };
        let mind = |l: &Q, h: &Q| -> Q {
            if !one.lt(l) && !h.lt(&one) {
                q(0, 1)
            } else {
                let (a1, b1) = (l.sub(&one).abs(), h.sub(&one).abs());
                if a1.lt(&b1) {
                    a1
                } else {
                    b1
                }
            }
        };
        let ok4 = maxd(&r27l, &r27h).lt(&mind(&r9l, &r9h));
        w4 &= ok4;
        c.out.push(format!("LEADING|loop=1x{a}|ratio_r=1/27=[{},{}]|ratio_r=1/9=[{},{}]|within_0.8_1.25={}|converging={}|json=0", r27l.dec(), r27h.dec(), r9l.dec(), r9h.dec(), u8::from(ok3), u8::from(ok4)));
        for (ri, &(rn, rd)) in RS.iter().enumerate() {
            let r = rq(ri);
            let one_term = ca.mul(&r.pow(a));
            let two_term = one_term.add(&full[a + 1].mul(&r.pow(a + 1)));
            if let Some((lo, hi)) = wv.get(&(a, ri)) {
                let inside2 = !lo.lt(&q(0, 1)) && !two_term.lt(lo) && !hi.lt(&two_term);
                c.out.push(format!("SERIES_COMPARE|loop=1x{a}|r={rn}/{rd}|one_term={}|two_term={}|two_term_inside={}|json=0", one_term.dec(), two_term.dec(), u8::from(inside2)));
            }
        }
    }
    // W5 area law
    let mut w5 = true;
    for w in LOOPS.windows(2) {
        let (a, b) = (w[0], w[1]);
        for (ri, &(rn, rd)) in RS.iter().enumerate() {
            let (Some((al, ah)), Some((bl, bh))) = (wv.get(&(a, ri)), wv.get(&(b, ri))) else {
                w5 = false;
                continue;
            };
            let dec = bh.lt(al);
            w5 &= dec;
            let mut line = format!("AREA|loops=1x{b}/1x{a}|r={rn}/{rd}|ratio=[{},{}]|decreasing={}", bl.div(ah).dec(), bh.div(al).dec(), u8::from(dec));
            if ri == 0 {
                if let (Some(ca), Some(cb)) = (lead.get(&a), lead.get(&b)) {
                    let pred = cb.div(ca).mul(&rq(0));
                    let (lo, hi) = (bl.div(ah).div(&pred), bh.div(al).div(&pred));
                    let ok = !lo.lt(&q(4, 5)) && !q(5, 4).lt(&hi);
                    w5 &= ok;
                    line.push_str(&format!("|predicted_ratio={}|within_0.8_1.25={}", pred.dec(), u8::from(ok)));
                } else {
                    w5 = false;
                }
            }
            c.out.push(format!("{line}|json=0"));
        }
    }
    let inc = !inconclusive.is_empty();
    let v = |b: bool| if inc { "INCONCLUSIVE" } else if b { "PASS" } else { "FAIL" };
    c.out.push(format!(
        "ZWILSON_RESULT|W1={}|W2={}|W3={}|W4={}|W5={}|inconclusive={}|json=0",
        if w1 { "PASS" } else { "FAIL" },
        v(w2),
        v(w3),
        v(w4),
        v(w5),
        if inc { inconclusive.join(",") } else { "none".into() }
    ));
    for l in &c.out {
        println!("{l}");
    }
}
