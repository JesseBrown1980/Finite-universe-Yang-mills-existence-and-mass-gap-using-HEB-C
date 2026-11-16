//! Issue #137 B7: exact signed 320-bit moment accumulator with runtime bounds.
//! Based on Stage A independently tested five-limb Wide implementation.
use std::io::BufRead;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Wide([u64; 5]);

impl Wide {
    const ZERO: Wide = Wide([0; 5]);

    /// a * b * w for a, b below 2^128 and w below 2^64, as a nonnegative 320-bit value
    fn product(a: u128, b: u128, w: u64) -> Wide {
        let (a0, a1) = (a as u64, (a >> 64) as u64);
        let (b0, b1) = (b as u64, (b >> 64) as u64);
        // a*b as four limbs
        let p00 = u128::from(a0) * u128::from(b0);
        let p01 = u128::from(a0) * u128::from(b1);
        let p10 = u128::from(a1) * u128::from(b0);
        let p11 = u128::from(a1) * u128::from(b1);
        let l0 = p00 as u64;
        let mid = (p00 >> 64) + u128::from(p01 as u64) + u128::from(p10 as u64);
        let l1 = mid as u64;
        let hi = (mid >> 64) + (p01 >> 64) + (p10 >> 64) + u128::from(p11 as u64);
        let l2 = hi as u64;
        let l3 = ((hi >> 64) + (p11 >> 64)) as u64;
        // times w
        let mut out = [0u64; 5];
        let mut carry = 0u128;
        for (o, l) in out.iter_mut().zip([l0, l1, l2, l3]) {
            let t = u128::from(l) * u128::from(w) + carry;
            *o = t as u64;
            carry = t >> 64;
        }
        out[4] = carry as u64;
        Wide(out)
    }

    fn add(&mut self, o: &Wide) {
        let mut carry = 0u128;
        for (s, &x) in self.0.iter_mut().zip(&o.0) {
            let t = u128::from(*s) + u128::from(x) + carry;
            *s = t as u64;
            carry = t >> 64;
        }
    }

    fn sub(&mut self, o: &Wide) {
        let mut borrow = 0i128;
        for (s, &x) in self.0.iter_mut().zip(&o.0) {
            let t = i128::from(*s) - i128::from(x) - borrow;
            *s = t as u64;
            borrow = i128::from(t < 0);
        }
    }

    fn negative(&self) -> bool {
        self.0[4] >> 63 == 1
    }

    /// decimal text of the signed value
    fn decimal(&self) -> String {
        let mut mag = *self;
        let neg = self.negative();
        if neg {
            let mut z = Wide::ZERO;
            z.sub(self);
            mag = z;
        }
        let mut digits: Vec<u8> = Vec::new();
        let mut limbs = mag.0;
        while limbs.iter().any(|&l| l != 0) {
            let mut rem = 0u128;
            for l in limbs.iter_mut().rev() {
                let cur = (rem << 64) | u128::from(*l);
                *l = (cur / 1_000_000_000_000_000_000) as u64;
                rem = cur % 1_000_000_000_000_000_000;
            }
            let mut r = rem as u64;
            for _ in 0..18 {
                digits.push(b'0' + (r % 10) as u8);
                r /= 10;
            }
        }
        while digits.len() > 1 && digits.last() == Some(&b'0') {
            digits.pop();
        }
        if digits.is_empty() {
            digits.push(b'0');
        }
        digits.reverse();
        let s = String::from_utf8(digits).unwrap_or_default();
        if neg {
            format!("-{s}")
        } else {
            s
        }
    }
}


const Q5_AMP_LIMIT: u128 = 1u128 << 112;
const WEIGHT_COEFF_LIMIT: u64 = 1u64 << 46;
const MAX_TERMS: u64 = 1u64 << 31;
const MAGNITUDE_TOP_LIMIT: u64 = 1u64 << 48;

fn need(ok: bool, error: &str) -> Result<(), String> {
    if ok { Ok(()) } else { Err(error.to_string()) }
}

impl Wide {
    fn raw_checked_add(&mut self, rhs: &Wide) -> Result<(), String> {
        let a = self.negative();
        let b = rhs.negative();
        let mut out = *self;
        out.add(rhs);
        need(a != b || out.negative() == a, "signed_320_bit_overflow")?;
        *self = out;
        Ok(())
    }

    fn abs_lt_2pow304(&self) -> bool {
        let mut mag = *self;
        if self.negative() {
            let mut zero = Wide::ZERO;
            zero.sub(self);
            mag = zero;
        }
        mag.0[4] < MAGNITUDE_TOP_LIMIT
    }
}

#[derive(Clone, Copy)]
struct CheckedMoment {
    total: Wide,
    terms: u64,
}

impl CheckedMoment {
    fn zero() -> Self {
        Self { total: Wide::ZERO, terms: 0 }
    }

    /// Enforces the full production source and term bound *before* mutation.
    /// Caller supplies the complete signed integer coefficient, including
    /// orbit weight 6*w and diagonal or electric edge factor b.
    fn add_term(&mut self, a: u128, b: u128, signed_coefficient: i64)
        -> Result<(), String> {
        need(a < Q5_AMP_LIMIT && b < Q5_AMP_LIMIT,
             "physical_Q5_amplitude_exceeds_2pow112")?;
        let abs_weight = signed_coefficient.unsigned_abs();
        need(abs_weight < WEIGHT_COEFF_LIMIT,
             "operator_times_weight_coefficient_exceeds_2pow46")?;
        need(self.terms < MAX_TERMS, "accumulated_terms_exceed_2pow31")?;
        let mut term = Wide::product(a, b, abs_weight);
        if signed_coefficient < 0 {
            let mut neg = Wide::ZERO;
            neg.sub(&term);
            term = neg;
        }
        let mut candidate = self.total;
        candidate.raw_checked_add(&term)?;
        need(candidate.abs_lt_2pow304(), "partial_sum_exceeds_2pow304")?;
        self.total = candidate;
        self.terms += 1;
        Ok(())
    }
}

fn selftest() -> Result<(), String> {
    let one = Wide::product(1, 1, 1);
    let mut max_signed = Wide([u64::MAX; 5]);
    max_signed.0[4] = 0x7fff_ffff_ffff_ffff;
    need(max_signed.raw_checked_add(&one).is_err(),
         "signed_320_positive_overflow_accepted")?;
    let min_signed = Wide([0, 0, 0, 0, 0x8000_0000_0000_0000]);
    let mut neg_one = Wide::ZERO;
    neg_one.sub(&one);
    let mut underflow = min_signed;
    need(underflow.raw_checked_add(&neg_one).is_err(),
         "signed_320_negative_overflow_accepted")?;

    let at_304 = Wide([u64::MAX, u64::MAX, u64::MAX, u64::MAX,
                       (1u64 << 48) - 1]);
    let mut high = CheckedMoment { total: at_304, terms: 0 };
    need(high.add_term(1, 1, 1).is_err(),
         "positive_304_magnitude_violation_accepted")?;
    let mut minus_high = Wide::ZERO;
    minus_high.sub(&at_304);
    let mut low = CheckedMoment { total: minus_high, terms: 0 };
    need(low.add_term(1, 1, -1).is_err(),
         "negative_304_magnitude_violation_accepted")?;
    let mut cancel = at_304;
    cancel.raw_checked_add(&minus_high)?;
    need(cancel == Wide::ZERO && cancel.abs_lt_2pow304(),
         "near_boundary_cancellation")?;

    let mut bad_a = CheckedMoment::zero();
    need(bad_a.add_term(Q5_AMP_LIMIT, 1, 1).is_err(),
         "oversized_Q5_amplitude_accepted")?;
    need(bad_a.add_term(1, 1, WEIGHT_COEFF_LIMIT as i64).is_err(),
         "oversized_weighted_coefficient_accepted")?;
    let mut max_terms = CheckedMoment {
        total: Wide::ZERO, terms: MAX_TERMS,
    };
    need(max_terms.add_term(1, 1, 1).is_err(),
         "overlarge_term_count_accepted")?;

    let mut sample = CheckedMoment::zero();
    let a = (1u128 << 112) - 1;
    let b = (1u128 << 112) - 3;
    let coef = (1i64 << 45) - 1;
    sample.add_term(a, b, coef)?;
    let expected = sample.total.decimal();
    sample.add_term(a, b, -coef)?;
    need(sample.total == Wide::ZERO && sample.terms == 2,
         "wide_signed_product_cancellation")?;
    println!("Y137_B7_TOY|signed_320_overflow=REFUSED|signed_320_underflow=REFUSED|positive_2pow304=REFUSED|negative_2pow304=REFUSED|near_boundary_cancellation=PASS|bad_amplitude=REFUSED|bad_coefficient=REFUSED|overlarge_term_count=REFUSED|large_signed_product=PASS|positive_example={expected}|actual_mu3=NOT_COMPUTED|json=0");
    Ok(())
}

fn evaluate() -> Result<(), String> {
    let mut sum = CheckedMoment::zero();
    for line in std::io::stdin().lock().lines() {
        let s = line.map_err(|x| x.to_string())?;
        if s.trim().is_empty() {
            continue;
        }
        let values: Vec<&str> = s.split_whitespace().collect();
        need(values.len() == 3, "invalid_term_field_count")?;
        let a = values[0].parse::<u128>().map_err(|x| x.to_string())?;
        let b = values[1].parse::<u128>().map_err(|x| x.to_string())?;
        let weight = values[2].parse::<i64>().map_err(|x| x.to_string())?;
        sum.add_term(a, b, weight)?;
    }
    let mut negative = Wide::ZERO;
    negative.sub(&sum.total);
    println!("Y137_B7_EVAL|terms={}|sum={}|negative_sum={}|bounded_signed_320=PASS|json=0",
             sum.terms, sum.total.decimal(), negative.decimal());
    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let result = match args.as_slice() {
        [_, mode] if mode == "--selftest" => selftest(),
        [_, mode] if mode == "--evaluate" => evaluate(),
        _ => Err("usage: b7_checked --selftest | --evaluate".to_string()),
    };
    if let Err(why) = result {
        eprintln!("Y137_B7_REFUSE|reason={why}|json=0");
        std::process::exit(1);
    }
}
