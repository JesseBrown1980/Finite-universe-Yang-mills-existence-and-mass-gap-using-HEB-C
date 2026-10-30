//! Minimal exact signed big integer (base 2^32 limbs), std only: add, sub, mul, exact division
//! (binary long division), comparison and sign. Enough for fraction-free Bareiss elimination.
use std::cmp::Ordering;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Big {
    neg: bool,
    mag: Vec<u32>, // little-endian, no trailing zeros; empty = 0
}

fn trim(v: &mut Vec<u32>) {
    while v.last() == Some(&0) {
        v.pop();
    }
}

fn cmp_mag(a: &[u32], b: &[u32]) -> Ordering {
    if a.len() != b.len() {
        return a.len().cmp(&b.len());
    }
    for i in (0..a.len()).rev() {
        if a[i] != b[i] {
            return a[i].cmp(&b[i]);
        }
    }
    Ordering::Equal
}

fn add_mag(a: &[u32], b: &[u32]) -> Vec<u32> {
    let mut out = Vec::with_capacity(a.len().max(b.len()) + 1);
    let mut carry = 0u64;
    for i in 0..a.len().max(b.len()) {
        let s = carry + *a.get(i).unwrap_or(&0) as u64 + *b.get(i).unwrap_or(&0) as u64;
        out.push(s as u32);
        carry = s >> 32;
    }
    if carry > 0 {
        out.push(carry as u32);
    }
    out
}

/// a - b with |a| >= |b|
fn sub_mag(a: &[u32], b: &[u32]) -> Vec<u32> {
    let mut out = Vec::with_capacity(a.len());
    let mut borrow = 0i64;
    for (i, &ai) in a.iter().enumerate() {
        let mut d = ai as i64 - borrow - *b.get(i).unwrap_or(&0) as i64;
        if d < 0 {
            d += 1 << 32;
            borrow = 1;
        } else {
            borrow = 0;
        }
        out.push(d as u32);
    }
    trim(&mut out);
    out
}

fn mul_mag(a: &[u32], b: &[u32]) -> Vec<u32> {
    if a.is_empty() || b.is_empty() {
        return Vec::new();
    }
    let mut out = vec![0u32; a.len() + b.len()];
    for (i, &x) in a.iter().enumerate() {
        let mut carry = 0u64;
        for (j, &y) in b.iter().enumerate() {
            let cur = out[i + j] as u64 + x as u64 * y as u64 + carry;
            out[i + j] = cur as u32;
            carry = cur >> 32;
        }
        let mut k = i + b.len();
        while carry > 0 {
            let cur = out[k] as u64 + carry;
            out[k] = cur as u32;
            carry = cur >> 32;
            k += 1;
        }
    }
    trim(&mut out);
    out
}

fn bits(a: &[u32]) -> usize {
    match a.last() {
        None => 0,
        Some(&top) => 32 * (a.len() - 1) + (32 - top.leading_zeros() as usize),
    }
}

fn shl1_or(a: &mut Vec<u32>, bit: u32) {
    let mut carry = bit;
    for x in a.iter_mut() {
        let nc = *x >> 31;
        *x = (*x << 1) | carry;
        carry = nc;
    }
    if carry > 0 {
        a.push(carry);
    }
}

/// quotient magnitude of a / b (b != 0), binary long division
fn div_mag(a: &[u32], b: &[u32]) -> (Vec<u32>, Vec<u32>) {
    let mut q = vec![0u32; a.len()];
    let mut r: Vec<u32> = Vec::new();
    for i in (0..bits(a)).rev() {
        let bit = (a[i / 32] >> (i % 32)) & 1;
        shl1_or(&mut r, bit);
        trim(&mut r);
        if cmp_mag(&r, b) != Ordering::Less {
            r = sub_mag(&r, b);
            q[i / 32] |= 1 << (i % 32);
        }
    }
    trim(&mut q);
    (q, r)
}

impl Big {
    pub fn from_i128(v: i128) -> Big {
        let neg = v < 0;
        let mut u = v.unsigned_abs();
        let mut mag = Vec::new();
        while u > 0 {
            mag.push(u as u32);
            u >>= 32;
        }
        Big { neg, mag }
    }
    pub fn signum(&self) -> i32 {
        if self.mag.is_empty() {
            0
        } else if self.neg {
            -1
        } else {
            1
        }
    }
    pub fn add(&self, o: &Big) -> Big {
        if self.neg == o.neg {
            return Big { neg: self.neg, mag: add_mag(&self.mag, &o.mag) }.norm();
        }
        match cmp_mag(&self.mag, &o.mag) {
            Ordering::Less => Big { neg: o.neg, mag: sub_mag(&o.mag, &self.mag) }.norm(),
            _ => Big { neg: self.neg, mag: sub_mag(&self.mag, &o.mag) }.norm(),
        }
    }
    pub fn sub(&self, o: &Big) -> Big {
        self.add(&Big { neg: !o.neg, mag: o.mag.clone() })
    }
    pub fn mul(&self, o: &Big) -> Big {
        Big { neg: self.neg != o.neg, mag: mul_mag(&self.mag, &o.mag) }.norm()
    }
    /// exact division; returns None if the remainder is not zero or the divisor is zero
    pub fn div_exact(&self, o: &Big) -> Option<Big> {
        if o.mag.is_empty() {
            return None;
        }
        let (q, r) = div_mag(&self.mag, &o.mag);
        if !r.is_empty() {
            return None;
        }
        Some(Big { neg: self.neg != o.neg, mag: q }.norm())
    }
    fn norm(mut self) -> Big {
        trim(&mut self.mag);
        if self.mag.is_empty() {
            self.neg = false;
        }
        self
    }
}
