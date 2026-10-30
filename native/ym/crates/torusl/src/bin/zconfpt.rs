//! zconf: S3 confining phase, static-charge potential and string tension to O(r^2) (see PREREG.md).
//! Rust 1.81, std only, exact integer and rational arithmetic, json=0.

const PERM: [[usize; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
const TRANS: [usize; 3] = [1, 2, 5];

fn gcd(a: i128, b: i128) -> i128 {
    if b == 0 {
        a.abs()
    } else {
        gcd(b, a % b)
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
struct Q {
    n: i128,
    d: i128,
}

impl Q {
    fn new(n: i128, d: i128) -> Q {
        let g = gcd(n, d).max(1);
        let s = if d < 0 { -1 } else { 1 };
        Q { n: s * n / g, d: s * d / g }
    }
    fn add(self, o: Q) -> Q {
        Q::new(self.n * o.d + o.n * self.d, self.d * o.d)
    }
    fn sub(self, o: Q) -> Q {
        Q::new(self.n * o.d - o.n * self.d, self.d * o.d)
    }
    fn mul(self, o: Q) -> Q {
        Q::new(self.n * o.n, self.d * o.d)
    }
    fn div(self, o: Q) -> Q {
        Q::new(self.n * o.d, self.d * o.n)
    }
    fn show(self) -> String {
        format!("{}/{}", self.n, self.d)
    }
}

struct Group {
    mul: [[usize; 6]; 6],
    inv: [usize; 6],
}

fn group() -> Group {
    let mut mul = [[0usize; 6]; 6];
    for (a, pa) in PERM.iter().enumerate() {
        for (b, pb) in PERM.iter().enumerate() {
            let p = [pa[pb[0]], pa[pb[1]], pa[pb[2]]];
            mul[a][b] = PERM.iter().position(|&q| q == p).unwrap_or(0);
        }
    }
    let mut inv = [0usize; 6];
    for (a, ia) in inv.iter_mut().enumerate() {
        *ia = (0..6).find(|&b| mul[a][b] == 0).unwrap_or(0);
    }
    Group { mul, inv }
}

/// characters: irrep 0 = trivial, 1 = sign, 2 = std (2-dimensional)
fn chi(r: usize, g: usize) -> i128 {
    match r {
        0 => 1,
        1 => {
            if TRANS.contains(&g) {
                -1
            } else {
                1
            }
        }
        _ => match g {
            0 => 2,
            3 | 4 => -1,
            _ => 0,
        },
    }
}

const DIM: [i128; 3] = [1, 1, 2];

/// electric eigenvalue of a link in irrep r: 3 - (sum over transpositions of chi_r(t)) / dim r
fn e_link(r: usize) -> Q {
    let s: i128 = TRANS.iter().map(|&t| chi(r, t)).sum();
    Q::new(3, 1).sub(Q::new(s, DIM[r]))
}

fn tuple(i: usize) -> [usize; 4] {
    [i % 6, (i / 6) % 6, (i / 36) % 6, i / 216]
}

fn index(u: [usize; 4]) -> usize {
    u[0] + 6 * u[1] + 36 * u[2] + 216 * u[3]
}

/// Second-order plaquette shift. string = whether link u1 carries the std string.
/// gfun(h) = sum over u of F(u, h u) (integer), with F given; returns s_p as an exact rational.
fn shift(gfun: &[i128], norm: i128, string: bool) -> Q {
    let ground = if string { [2usize, 0, 0, 0] } else { [0usize; 4] };
    let e0 = ground.iter().fold(Q::new(0, 1), |a, &r| a.add(e_link(r)));
    let mut s = Q::new(0, 1);
    for asg in 0..81usize {
        let rr = [asg % 3, (asg / 3) % 3, (asg / 9) % 3, asg / 27];
        if rr == ground {
            continue;
        }
        let er = rr.iter().fold(Q::new(0, 1), |a, &r| a.add(e_link(r)));
        // <f, P_R f> = (prod dim / 6^4) * sum_g prod chi_r(g_e) * (1/6^4) sum_u F(u, g^-1 u)
        // gfun is indexed by h = g^-1 per link; chi is a class function with chi(g) = chi(g^-1) for S3
        let mut tot = 0i128;
        for (h, gh) in gfun.iter().enumerate() {
            let hv = tuple(h);
            let w: i128 = (0..4).map(|e| chi(rr[e], hv[e])).product();
            tot += w * gh;
        }
        if tot == 0 {
            continue;
        }
        let pd: i128 = rr.iter().map(|&r| DIM[r]).product();
        let val = Q::new(pd * tot, 1296 * 1296);
        let de = er.sub(e0);
        s = s.sub(val.div(Q::new(norm, 1).mul(de)));
    }
    s
}

/// Method A: group table and characters.
fn method_a(g: &Group) -> (Q, Q) {
    let up = |u: [usize; 4]| g.mul[g.mul[g.mul[u[0]][u[1]]][g.inv[u[2]]]][g.inv[u[3]]];
    let mut gv = vec![0i128; 1296];
    let mut gs = vec![0i128; 1296];
    for (h, (gvh, gsh)) in gv.iter_mut().zip(gs.iter_mut()).enumerate() {
        let hv = tuple(h);
        for ui in 0..1296usize {
            let u = tuple(ui);
            let u2 = [g.mul[hv[0]][u[0]], g.mul[hv[1]][u[1]], g.mul[hv[2]][u[2]], g.mul[hv[3]][u[3]]];
            let f = chi(2, up(u)) * chi(2, up(u2));
            *gvh += f;
            *gsh += f * chi(2, g.mul[u[0]][g.inv[u2[0]]]);
        }
    }
    (shift(&gv, 1, false), shift(&gs, 2, true))
}

type M3 = [[i128; 3]; 3];

fn mm(a: &M3, b: &M3) -> M3 {
    let mut c = [[0i128; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            c[i][j] = (0..3).map(|k| a[i][k] * b[k][j]).sum();
        }
    }
    c
}

fn tr(a: &M3) -> i128 {
    a[0][0] + a[1][1] + a[2][2]
}

fn transpose(a: &M3) -> M3 {
    [[a[0][0], a[1][0], a[2][0]], [a[0][1], a[1][1], a[2][1]], [a[0][2], a[1][2], a[2][2]]]
}

fn det(a: &M3) -> i128 {
    a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
}

/// Method B: explicit integer permutation matrices; std = image of 3*Pi = 3I - J, so 3 chi_std(M) = tr((3I - J) M).
fn method_b() -> (Q, Q, bool) {
    let pm: Vec<M3> = PERM
        .iter()
        .map(|p| {
            let mut m = [[0i128; 3]; 3];
            for j in 0..3 {
                m[p[j]][j] = 1;
            }
            m
        })
        .collect();
    let find = |m: &M3| pm.iter().position(|q| q == m).unwrap_or(usize::MAX);
    let three_pi: M3 = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]];
    let chi3 = |m: &M3| tr(&mm(&three_pi, m)); // 3 chi_std
    // characters from matrices, for the projector weights
    let chim = |r: usize, g: usize| -> i128 {
        match r {
            0 => 1,
            1 => det(&pm[g]),
            _ => tr(&pm[g]) - 1,
        }
    };
    let mut agree = true;
    for (g, _) in pm.iter().enumerate() {
        for r in 0..3 {
            agree &= chim(r, g) == chi(r, g);
        }
    }
    let upm = |u: [usize; 4]| mm(&mm(&mm(&pm[u[0]], &pm[u[1]]), &transpose(&pm[u[2]])), &transpose(&pm[u[3]]));
    let mut gv = vec![0i128; 1296];
    let mut gs = vec![0i128; 1296];
    for h in 0..1296usize {
        let hv = tuple(h);
        for ui in 0..1296usize {
            let u = tuple(ui);
            let u2i = [
                find(&mm(&pm[hv[0]], &pm[u[0]])),
                find(&mm(&pm[hv[1]], &pm[u[1]])),
                find(&mm(&pm[hv[2]], &pm[u[2]])),
                find(&mm(&pm[hv[3]], &pm[u[3]])),
            ];
            let f9 = chi3(&upm(u)) * chi3(&upm(u2i)); // 9 F
            gv[h] += f9;
            // K = sum_ab D(u1)_ab D(u1')_ab = tr(Pi Pm(u1) Pm(u1')^T) ; 3K = tr((3I - J) Pm(u1) Pm(u1')^T)
            gs[h] += f9 * chi3(&mm(&pm[u[0]], &transpose(&pm[u2i[0]])));
        }
    }
    // undo the scale factors exactly: gv = 9 * (method A sum), gs = 27 * (method A sum)
    let ok = gv.iter().all(|x| x % 9 == 0) && gs.iter().all(|x| x % 27 == 0);
    let gv: Vec<i128> = gv.iter().map(|x| x / 9).collect();
    let gs: Vec<i128> = gs.iter().map(|x| x / 27).collect();
    let _ = index([0, 0, 0, 0]);
    (shift(&gv, 1, false), shift(&gs, 2, true), agree && ok)
}

fn main() {
    let g = group();
    let pf = |b: bool| if b { "PASS" } else { "FAIL" };
    // F1
    let e: Vec<Q> = (0..3).map(e_link).collect();
    let f1 = e[0] == Q::new(0, 1) && e[1] == Q::new(6, 1) && e[2] == Q::new(3, 1);
    println!("ZCONF_LINK|E_trivial={}|E_sign={}|E_std={}|json=0", e[0].show(), e[1].show(), e[2].show());
    // F2: minimal Gauss-law string on a path of d links (fusion multiplicities from characters)
    let fuse = |a: usize, b: usize, c: usize| (0..6).map(|x| chi(a, x) * chi(b, x) * chi(c, x)).sum::<i128>() / 6;
    let mut f2 = true;
    for d in 1..=6usize {
        let mut best: Option<Q> = None;
        for asg in 0..3usize.pow(d as u32) {
            let rr: Vec<usize> = (0..d).map(|i| (asg / 3usize.pow(i as u32)) % 3).collect();
            // vertex 0: charge std with rr[0]; interior vertices rr[i], rr[i+1]; last: rr[d-1] with charge std
            let mut ok = fuse(2, rr[0], 0) > 0 && fuse(rr[d - 1], 2, 0) > 0;
            for i in 0..d - 1 {
                ok &= fuse(rr[i], rr[i + 1], 0) > 0;
            }
            if ok {
                let en = rr.iter().fold(Q::new(0, 1), |a, &r| a.add(e_link(r)));
                if best.map_or(true, |b| en.n * b.d < b.n * en.d) {
                    best = Some(en);
                }
            }
        }
        let v = best.unwrap_or(Q::new(-1, 1));
        f2 &= v == Q::new(3 * d as i128, 1);
        println!("ZCONF_V0|d={d}|V_d_0={}|json=0", v.show());
    }
    // F3, F4
    let (va, sa) = method_a(&g);
    let (vb, sb, chars_ok) = method_b();
    let kappa = Q::new(2, 1).mul(sa.sub(va));
    println!("ZCONF_SHIFT|method=A|s_vac={}|s_str={}|json=0", va.show(), sa.show());
    println!("ZCONF_SHIFT|method=B|s_vac={}|s_str={}|characters_match={}|json=0", vb.show(), sb.show(), i64::from(chars_ok));
    println!("ZCONF_KAPPA|kappa={}|sigma_r=3+kappa*r^2|V_d_r=3d+kappa*d*r^2+O(r^3)|json=0", kappa.show());
    let f3 = kappa.n < 0;
    let f4 = va == vb && sa == sb && chars_ok;
    // F5: sigma at sample couplings, and the zero of the second-order string tension
    for (n, d) in [(1i128, 27i128), (1, 9), (1, 3), (1, 1)] {
        let r2 = Q::new(n * n, d * d);
        let sig = Q::new(3, 1).add(kappa.mul(r2));
        println!("ZCONF_SIGMA|r={n}/{d}|sigma={}|json=0", sig.show());
    }
    let rz2 = Q::new(-3, 1).div(kappa);
    println!("ZCONF_ZERO|r_squared_where_second_order_sigma_is_0={}|json=0", rz2.show());
    println!("ZCONF_RESULT|F1={}|F2={}|F3={}|F4={}|json=0", pf(f1), pf(f2), pf(f3), pf(f4));
}
