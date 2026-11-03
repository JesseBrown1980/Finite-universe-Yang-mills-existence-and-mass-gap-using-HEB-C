//! Compression of H = JE*E + JB*M onto the flat (M = 0) basis states of one sector.
//! Reports, exactly from the exchange file: the number of flat states, the
//! electric diagonal z_ii on each, and every matrix entry coupling two flat
//! states. If there is no flat-flat coupling, the compression onto the flat
//! one-hot vectors (mutually W-orthogonal, also across sectors) is diagonal with
//! entries JE*z_ii, independent of JB. Courant-Fischer over the span of the
//! eight flat states (seven in (+,+), one in (-,-)) then gives, for every r,
//! E_8(r) <= JE * max z_ii over those eight states.
//! Integer-only.
//! usage: flatcomp MATRIX                json=0
//!        flatcomp --room DEV OFFSET     the same FLATCOMP row, read from a `ymroom build` stream.
//!          DEV is a path or a seg: spec. The stream's merkle is checked against its header, and a
//!          mismatch prints no FLATCOMP row. A second row gives the store's identity.
#![deny(clippy::float_arithmetic)]

#[allow(dead_code)]
#[path = "../../../torusl/src/segio.rs"]
mod segio;
#[allow(dead_code)]
#[path = "../../../torusl/src/sha.rs"]
mod sha;
#[path = "../../../torusl/src/roomio.rs"]
mod roomio;

struct RoomFlat {
    row: String,
    store: String,
}

/// Flat rows are kept as read, because the row a coupling points to may come later in the stream.
fn room_report(spec: &str, off: u64) -> Result<RoomFlat, String> {
    let t0 = std::time::Instant::now();
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    let mut flats: Vec<(usize, u32, i64, Vec<usize>)> = Vec::new();
    roomio::stream(&mut dev, off, &hdr, |h, row| {
        if row.mag == 0 {
            let mut diag = 0i64;
            let mut targets = Vec::new();
            for (j, z) in row.entries() {
                if j == h {
                    diag += i64::from(z);
                } else if z != 0 {
                    targets.push(j);
                }
            }
            flats.push((h, row.w, diag, targets));
        }
    })?;
    let is_flat = |j: usize| flats.iter().any(|f| f.0 == j);
    let count = |upper: bool| flats.iter().map(|f| f.3.iter().filter(|&&j| (j > f.0) == upper && is_flat(j)).count()).sum::<usize>();
    let (ff_upper, ff_lower) = (count(true), count(false));
    if ff_upper != ff_lower {
        return Err(format!("flat couplings not symmetric: upper {ff_upper} lower {ff_lower}"));
    }
    let join = |v: Vec<String>| v.join(",");
    let dmax = flats.iter().map(|f| f.2).max().unwrap_or(0);
    Ok(RoomFlat {
        row: format!(
            "FLATCOMP|matrix=room|n={}|flat_states={}|flat_electric_diag=[{}]|flat_diag_max={dmax}|flat_flat_couplings={ff_upper}|json=0",
            hdr.n,
            flats.len(),
            join(flats.iter().map(|f| f.2.to_string()).collect())
        ),
        store: format!(
            "FLATCOMP_STORE|L={}|sector={}|n={}|payload_bytes={}|payload_merkle={}|merkle=PASS|flat_rows={}|flat_weights={}|ms={}|json=0",
            hdr.lattice,
            hdr.sector,
            hdr.n,
            hdr.payload,
            hdr.merkle,
            join(flats.iter().map(|f| f.0.to_string()).collect()),
            join(flats.iter().map(|f| f.1.to_string()).collect()),
            t0.elapsed().as_millis()
        ),
    })
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() >= 4 && a[1] == "--room" {
        match a[3].parse::<u64>().map_err(|_| "bad OFFSET".to_string()).and_then(|off| room_report(&a[2], off)) {
            Ok(r) => {
                println!("{}", r.store);
                println!("{}", r.row);
            }
            Err(e) => {
                println!("FLATCOMP_ERROR|{e}|json=0");
                std::process::exit(2);
            }
        }
        return;
    }
    if a.len() < 2 {
        eprintln!("usage: flatcomp MATRIX | flatcomp --room DEV OFFSET");
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

#[cfg(test)]
mod tests {
    use super::*;

    fn temp(name: &str) -> std::path::PathBuf {
        std::env::temp_dir().join(format!("flatcomp-test-{}-{name}", std::process::id()))
    }

    #[test]
    fn room_mode_reads_the_flat_rows() {
        let p = temp("flat");
        let rows = vec![(1, 0, vec![(0, 54), (1, -1)]), (6, 3, vec![(0, -6), (1, 50), (2, -2)]), (2, 0, vec![(1, -1), (2, 72)])];
        roomio::write_test_stream(&p, &rows);
        let r = room_report(p.to_str().unwrap(), 0).unwrap();
        assert_eq!(r.row, "FLATCOMP|matrix=room|n=3|flat_states=2|flat_electric_diag=[54,72]|flat_diag_max=72|flat_flat_couplings=0|json=0");
        assert!(r.store.contains("|merkle=PASS|flat_rows=0,2|flat_weights=1,2|"));
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_flat_flat_coupling_is_counted_once() {
        let p = temp("coupled");
        let rows = vec![(1, 0, vec![(0, 54), (2, -1)]), (1, 3, vec![(1, 50)]), (1, 0, vec![(0, -1), (2, 54)])];
        roomio::write_test_stream(&p, &rows);
        assert!(room_report(p.to_str().unwrap(), 0).unwrap().row.ends_with("|flat_flat_couplings=1|json=0"));
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_one_sided_coupling_is_an_error() {
        let p = temp("onesided");
        let rows = vec![(1, 0, vec![(0, 54), (1, -1)]), (1, 0, vec![(1, 54)])];
        roomio::write_test_stream(&p, &rows);
        assert!(room_report(p.to_str().unwrap(), 0).is_err());
        std::fs::remove_file(p).unwrap();
    }

    #[test]
    fn a_changed_byte_fails_closed() {
        let p = temp("corrupt");
        let rows = vec![(1, 0, vec![(0, 54)]), (1, 3, vec![(1, 50)])];
        roomio::write_test_stream(&p, &rows);
        let mut b = std::fs::read(&p).unwrap();
        let last = b.len() - 1;
        b[last] ^= 1;
        std::fs::write(&p, b).unwrap();
        let e = room_report(p.to_str().unwrap(), 0).err().unwrap();
        assert!(e.contains("merkle mismatch"), "{e}");
        std::fs::remove_file(p).unwrap();
    }
}
