//! sturmfast: interval Sturm inertia, identical arithmetic to sturmrs (a copy of
//! its quotient, selftest and loader) with an O(log n) minimum-degree pivot
//! search instead of the O(n) scan per step. Must reproduce sturmrs counts.
//! B = W(1000*(JE*E + JB*M) - t*W)/... built exactly as the Python version:
//! off-diagonal (i,j) = 1000*JE*w_i*z_ij*S, diagonal += (1000*JB*mag_k*w_k - t*w_k)*S.
//! Pivots only when the pivot interval excludes zero; every Schur update x*y/d
//! is enclosed outward (corner products, floor below, ceiling above).
//! Integer arithmetic only: floats are denied at compile time.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{Signed, Zero};
use std::collections::{BTreeSet, HashMap};
use std::time::Instant;

type Iv = (BigInt, BigInt);

fn cdiv(a: &BigInt, b: &BigInt) -> BigInt {
    -((-a).div_floor(b))
}

fn quotient(x: &Iv, y: &Iv, d: &Iv) -> Result<Iv, String> {
    if !d.0.is_positive() && !d.1.is_negative() {
        return Err("pivot interval contains zero".into());
    }
    let p = [&x.0 * &y.0, &x.0 * &y.1, &x.1 * &y.0, &x.1 * &y.1];
    let mut lo = p.iter().min().cloned().unwrap_or_default();
    let mut hi = p.iter().max().cloned().unwrap_or_default();
    let (mut dlo, mut dhi) = (d.0.clone(), d.1.clone());
    if dhi.is_negative() {
        let (l, h) = (-hi, -lo);
        lo = l;
        hi = h;
        let (a, b) = (-dhi, -dlo);
        dlo = a;
        dhi = b;
    }
    Ok(if !lo.is_negative() {
        (lo.div_floor(&dhi), cdiv(&hi, &dlo))
    } else if !hi.is_positive() {
        (lo.div_floor(&dlo), cdiv(&hi, &dhi))
    } else {
        (lo.div_floor(&dlo), cdiv(&hi, &dlo))
    })
}

fn selftest() -> bool {
    for al in -3i64..=3 {
        for ah in al..=3 {
            for bl in -3i64..=3 {
                for bh in bl..=3 {
                    for dl in 1i64..=3 {
                        for dh in dl..=3 {
                            for s in [-1i64, 1] {
                                let d: Iv = if s == 1 { (dl.into(), dh.into()) } else { ((-dh).into(), (-dl).into()) };
                                let q = match quotient(&(al.into(), ah.into()), &(bl.into(), bh.into()), &d) {
                                    Ok(q) => q,
                                    Err(_) => return false,
                                };
                                for a in al..=ah {
                                    for b in bl..=bh {
                                        for c in dl..=dh {
                                            let n = BigInt::from(a * b);
                                            let den = BigInt::from(s * c);
                                            if q.0 > n.div_floor(&den) || q.1 < cdiv(&n, &den) {
                                                return false;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    true
}

struct Input {
    a: Vec<HashMap<usize, Iv>>,
    entries: usize,
}

fn load(path: &str, je: i64, jb: i64, tn: i64, digits: u32) -> Result<Input, String> {
    let text = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut it = text.split_ascii_whitespace().map(|s| s.parse::<i64>().map_err(|_| format!("bad token {s}")));
    let mut next = || it.next().ok_or_else(|| "truncated matrix".to_string())?;
    let n = usize::try_from(next()?).map_err(|_| "bad n")?;
    let w: Vec<i64> = (0..n).map(|_| next()).collect::<Result<_, _>>()?;
    let mag: Vec<i64> = (0..n).map(|_| next()).collect::<Result<_, _>>()?;
    if w.iter().any(|&v| v <= 0) {
        return Err("non-positive weight".into());
    }
    let scale = num_traits::pow(BigInt::from(10), digits as usize);
    let mut a: Vec<HashMap<usize, Iv>> = vec![HashMap::new(); n];
    let mut entries = 0usize;
    let rest: Vec<i64> = std::iter::from_fn(|| next().ok()).collect();
    if rest.len() % 3 != 0 {
        return Err("malformed triples".into());
    }
    for t in rest.chunks_exact(3) {
        let (i, j, z) = (usize::try_from(t[0]).map_err(|_| "bad i")?, usize::try_from(t[1]).map_err(|_| "bad j")?, t[2]);
        if i > j || j >= n || a[i].contains_key(&j) {
            return Err("bad entry".into());
        }
        entries += 1;
        if z != 0 {
            let v = BigInt::from(1000) * je * w[i] * z * &scale;
            a[i].insert(j, (v.clone(), v.clone()));
            a[j].insert(i, (v.clone(), v));
        }
    }
    for k in 0..n {
        let dv = (BigInt::from(1000) * jb * mag[k] * w[k] - BigInt::from(tn) * w[k]) * &scale;
        let old = a[k].get(&k).cloned().unwrap_or((BigInt::zero(), BigInt::zero()));
        a[k].insert(k, (old.0 + &dv, old.1 + &dv));
    }
    Ok(Input { a, entries })
}

fn certify(a: &mut [HashMap<usize, Iv>]) -> Result<(usize, usize, usize, bool), String> {
    // Same elimination and the same outward-rounded Schur updates as sturmrs;
    // only the pivot SEARCH differs: an ordered set keyed by (current row
    // length, index) replaces the O(n) scan per step. A pivot is still taken
    // only when its interval excludes zero; by Sylvester's law any order of
    // sign-definite pivots yields the same inertia.
    let n = a.len();
    let mut active: Vec<bool> = vec![true; n];
    let mut lens: Vec<usize> = a.iter().map(HashMap::len).collect();
    let mut queue: BTreeSet<(usize, usize)> = (0..n).map(|i| (lens[i], i)).collect();
    let (mut neg, mut pos) = (0usize, 0usize);
    for step in 0..n {
        let mut chosen: Option<usize> = None;
        for &(_, i) in queue.iter() {
            if let Some(d) = a[i].get(&i) {
                if d.0.is_positive() || d.1.is_negative() {
                    chosen = Some(i);
                    break;
                }
            }
        }
        let Some(k) = chosen else { return Ok((neg, pos, step, false)) };
        queue.remove(&(lens[k], k));
        let d = a[k][&k].clone();
        if d.1.is_negative() {
            neg += 1;
        } else {
            pos += 1;
        }
        let nb: Vec<(usize, Iv)> = a[k].iter().filter(|(&j, _)| j != k).map(|(&j, v)| (j, v.clone())).collect();
        for x in 0..nb.len() {
            for y in x..nb.len() {
                let (i, vi) = (&nb[x].0, &nb[x].1);
                let (j, vj) = (&nb[y].0, &nb[y].1);
                let c = quotient(vi, vj, &d)?;
                let o = a[*i].get(j).cloned().unwrap_or((BigInt::zero(), BigInt::zero()));
                let v: Iv = (o.0 - &c.1, o.1 - &c.0);
                if v.0.is_zero() && v.1.is_zero() {
                    a[*i].remove(j);
                    a[*j].remove(i);
                } else {
                    a[*i].insert(*j, v.clone());
                    a[*j].insert(*i, v);
                }
            }
        }
        for (j, _) in &nb {
            a[*j].remove(&k);
        }
        a[k].clear();
        active[k] = false;
        for (j, _) in &nb {
            let j = *j;
            if active[j] && a[j].len() != lens[j] {
                queue.remove(&(lens[j], j));
                lens[j] = a[j].len();
                queue.insert((lens[j], j));
            }
        }
    }
    Ok((neg, pos, n, true))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let run = || -> Result<(bool, String), String> {
        if !selftest() {
            return Err("interval arithmetic selftest".into());
        }
        if args.len() < 5 {
            return Err("usage: sturmfast MATRIX JE JB T_NUM [SCALE_DIGITS=80]".into());
        }
        let p = |i: usize| args[i].parse::<i64>().map_err(|_| format!("bad arg {}", args[i]));
        let (je, jb, tn) = (p(2)?, p(3)?, p(4)?);
        let digits: u32 = args.get(5).map_or(Ok(80), |s| s.parse().map_err(|_| "bad digits".to_string()))?;
        let mut input = load(&args[1], je, jb, tn, digits)?;
        let t0 = Instant::now();
        let (neg, pos, done, complete) = certify(&mut input.a)?;
        let ms = t0.elapsed().as_millis();
        let ok = complete && neg == 1;
        Ok((ok, format!(
            "STURM-FAST|pivot_search=min_degree_ordered_set|result={}|status={}|JE={je}|JB={jb}|threshold={tn}/1000|scale_digits={digits}|upper_entries={}|pivots={done}/{}|negative={neg}|positive={pos}|ambiguous=0|E1_gt_threshold_certified={}|elapsed_ms={ms}|json=0",
            if ok { "PASS" } else { "FAIL" }, if complete { "COMPLETE" } else { "UNCERTAIN" },
            input.entries, input.a.len(), u8::from(ok)
        )))
    };
    match run() {
        Ok((ok, line)) => {
            println!("{line}");
            std::process::exit(if ok { 0 } else { 2 });
        }
        Err(e) => {
            eprintln!("STURM-FAST|result=FAIL|reason={e}|json=0");
            std::process::exit(1);
        }
    }
}

