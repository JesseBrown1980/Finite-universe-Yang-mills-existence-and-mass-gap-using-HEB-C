//! Compression of H = JE*E + JB*M onto the flat (M = 0) basis states of one sector.
//! Reports, exactly from the exchange file: the number of flat states, the
//! electric diagonal z_ii on each, and every matrix entry coupling two flat
//! states. If there is no flat-flat coupling, the compression onto the flat
//! one-hot vectors (mutually W-orthogonal, also across sectors) is diagonal with
//! entries JE*z_ii, independent of JB. Courant-Fischer over the span of the
//! eight flat states (seven in (+,+), one in (-,-)) then gives, for every r,
//! E_8(r) <= JE * max z_ii over those eight states.
//! Integer-only. usage: flatcomp MATRIX        json=0
#![deny(clippy::float_arithmetic)]

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 2 {
        eprintln!("usage: flatcomp MATRIX");
        std::process::exit(1);
    }
    let text = std::fs::read_to_string(&a[1]).unwrap_or_default();
    let mut it = text.split_ascii_whitespace().map(|s| s.parse::<i64>().unwrap_or(-1));
    let n = usize::try_from(it.next().unwrap_or(0)).unwrap_or(0);
    let _w: Vec<i64> = (0..n).map(|_| it.next().unwrap_or(0)).collect();
    let mag: Vec<i64> = (0..n).map(|_| it.next().unwrap_or(-1)).collect();
    let flat: Vec<bool> = mag.iter().map(|&m| m == 0).collect();
    let mut diag = vec![0i64; n];
    let mut ff_edges = 0usize;
    while let (Some(i), Some(j), Some(z)) = (it.next(), it.next(), it.next()) {
        let (i, j) = (usize::try_from(i).unwrap_or(0), usize::try_from(j).unwrap_or(0));
        if i == j {
            diag[i] += z;
        } else if z != 0 && flat[i] && flat[j] {
            ff_edges += 1;
        }
    }
    let d: Vec<String> = (0..n).filter(|&k| flat[k]).map(|k| diag[k].to_string()).collect();
    let dmax = (0..n).filter(|&k| flat[k]).map(|k| diag[k]).max().unwrap_or(0);
    let name = a[1].rsplit('/').next().unwrap_or("");
    println!("FLATCOMP|matrix={name}|n={n}|flat_states={}|flat_electric_diag=[{}]|flat_diag_max={dmax}|flat_flat_couplings={ff_edges}|json=0", d.len(), d.join(","));
}
