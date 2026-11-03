//! Vacuum-ball compression of one symmetry sector, read from a `ymroom build` stream.
//!
//! `ball` works on the whole gauge-orbit space. This does the same inside a sector: the seeds are
//! the sector's flat rows (mag = 0), and a breadth-first search over the rows' nonzero off-diagonal
//! entries collects every state within K moves. H is then restricted to that index set. Distinct
//! sector states are W-orthogonal, so this is a principal compression and is still W-self-adjoint.
//! By Cauchy interlacing its k-th eigenvalue is >= the sector's k-th eigenvalue, and so a count
//! N_ball(t) of levels below t is a LOWER bound on the sector's N(t). Nothing here gives a lower
//! bound on an eigenvalue.
//!
//! Writes the standard exchange format, so `flatcomp`, `cluster` and `shellschur` read it unchanged:
//! one file per radius, OUT_PREFIX.K1 to OUT_PREFIX.K<K>, all from one search. Passes over the
//! stream: K + 1. The first pass finds the seeds and their neighbours.
//!
//! usage: roomball DEV OFFSET K OUT_PREFIX     K from 1 to 8
//! Output: one ROOMBALL line per radius, json=0. Integer-only, Rust 1.81.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

#[allow(dead_code)]
#[path = "../../../torusl/src/segio.rs"]
mod segio;
#[allow(dead_code)]
#[path = "../../../torusl/src/sha.rs"]
mod sha;
#[path = "../../../torusl/src/roomio.rs"]
mod roomio;

use std::io::Write;

const UNSEEN: u8 = u8::MAX;

/// One radius being written in the last pass. Entries go to a side file, because the weights and
/// magnetic numbers have to come first in the exchange format.
struct Radius {
    k: u8,
    /// Index in this ball, by index in the largest ball. u32::MAX if outside this ball.
    table: Vec<u32>,
    states: usize,
    nnz: u64,
    leaving: u64,
    out: String,
    side: String,
    entries: std::io::BufWriter<std::fs::File>,
}

fn build(spec: &str, off: u64, k_max: u8, out: &str) -> Result<Vec<String>, String> {
    let t0 = std::time::Instant::now();
    let mut dev = segio::open(spec, false).map_err(|e| format!("open {spec}: {e}"))?;
    let hdr = roomio::read_hdr(&mut dev, off)?;
    let n = hdr.n;
    let mut dist = vec![UNSEEN; n];

    // First pass: seeds, and their rows, kept because a neighbour's index may already have gone by.
    let mut seed_rows: Vec<Vec<usize>> = Vec::new();
    roomio::stream(&mut dev, off, &hdr, |h, row| {
        if row.mag == 0 {
            dist[h] = 0;
            seed_rows.push(row.entries().filter(|&(j, z)| j != h && z != 0).map(|(j, _)| j).collect());
        }
    })?;
    let seeds = seed_rows.len();
    if seeds == 0 {
        return Err("no flat rows".into());
    }
    let mut shells = vec![seeds, 0];
    for &j in seed_rows.iter().flatten() {
        if dist[j] == UNSEEN {
            dist[j] = 1;
            shells[1] += 1;
        }
    }
    let mut passes = 1usize;
    // One pass per later shell. Only rows at distance d are expanded, and the states they add are at
    // d + 1, so the order of the rows does not matter.
    for d in 1..k_max {
        let mut grown = 0usize;
        roomio::stream(&mut dev, off, &hdr, |h, row| {
            if dist[h] == d {
                for (j, z) in row.entries() {
                    if j != h && z != 0 && dist[j] == UNSEEN {
                        dist[j] = d + 1;
                        grown += 1;
                    }
                }
            }
        })?;
        passes += 1;
        shells.push(grown);
    }

    // Last pass: write the principal submatrix of every radius.
    let mut rank = vec![u32::MAX; n];
    let mut member_dist: Vec<u8> = Vec::new();
    for (h, &d) in dist.iter().enumerate() {
        if d != UNSEEN {
            rank[h] = u32::try_from(member_dist.len()).map_err(|_| "ball too large")?;
            member_dist.push(d);
        }
    }
    let mut radii: Vec<Radius> = Vec::new();
    for k in 1..=k_max {
        let mut table = vec![u32::MAX; member_dist.len()];
        let mut states = 0usize;
        for (slot, &d) in table.iter_mut().zip(&member_dist) {
            if d <= k {
                *slot = u32::try_from(states).map_err(|_| "ball too large")?;
                states += 1;
            }
        }
        let out = format!("{out}.K{k}");
        let side = format!("{out}.entries");
        let file = std::fs::File::create(&side).map_err(|e| format!("create {side}: {e}"))?;
        radii.push(Radius { k, table, states, nnz: 0, leaving: 0, out, side, entries: std::io::BufWriter::with_capacity(1 << 20, file) });
    }
    let (mut weights, mut mags) = (vec![0u32; member_dist.len()], vec![0u16; member_dist.len()]);
    let mut write_err: Option<String> = None;
    roomio::stream(&mut dev, off, &hdr, |h, row| {
        if rank[h] == u32::MAX {
            return;
        }
        let at = rank[h] as usize;
        weights[at] = row.w;
        mags[at] = row.mag;
        for rd in radii.iter_mut().filter(|rd| member_dist[at] <= rd.k) {
            let i = rd.table[at];
            for (j, z) in row.entries() {
                if z == 0 {
                    continue;
                }
                let t = if rank[j] == u32::MAX { u32::MAX } else { rd.table[rank[j] as usize] };
                if t == u32::MAX {
                    rd.leaving += 1;
                    continue;
                }
                rd.nnz += 1;
                if t >= i {
                    if let Err(e) = writeln!(rd.entries, "{i} {t} {z}") {
                        write_err.get_or_insert(format!("write entries: {e}"));
                    }
                }
            }
        }
    })?;
    passes += 1;
    if let Some(e) = write_err {
        return Err(e);
    }

    let mut summaries = Vec::new();
    for rd in radii {
        let Radius { k, states, nnz, leaving, out, side, mut entries, .. } = rd;
        entries.flush().map_err(|e| format!("flush {side}: {e}"))?;
        drop(entries);
        let mut w = std::io::BufWriter::with_capacity(1 << 20, std::fs::File::create(&out).map_err(|e| format!("create {out}: {e}"))?);
        let wt: Vec<String> = weights.iter().zip(&member_dist).filter(|(_, d)| **d <= k).map(|(v, _)| v.to_string()).collect();
        let mg: Vec<String> = mags.iter().zip(&member_dist).filter(|(_, d)| **d <= k).map(|(v, _)| v.to_string()).collect();
        let werr = |e: std::io::Error| format!("write {out}: {e}");
        writeln!(w, "{states}").map_err(werr)?;
        writeln!(w, "{}", wt.join(" ")).map_err(werr)?;
        writeln!(w, "{}", mg.join(" ")).map_err(werr)?;
        let mut er = std::fs::File::open(&side).map_err(|e| format!("reopen {side}: {e}"))?;
        std::io::copy(&mut er, &mut w).map_err(werr)?;
        w.flush().map_err(werr)?;
        drop(er);
        std::fs::remove_file(&side).map_err(|e| format!("remove {side}: {e}"))?;
        let shell_text = shells[..=usize::from(k)].iter().map(usize::to_string).collect::<Vec<_>>().join(",");
        summaries.push(format!(
            "ROOMBALL|L={}|sector={}|K={k}|seeds={seeds}|shells={shell_text}|states={states}|nnz={nnz}|entries_leaving_ball={leaving}|merkle=PASS|passes={passes}|ms={}|kind=COMPRESSION_UPPER_BOUNDS|json=0",
            hdr.lattice,
            hdr.sector,
            t0.elapsed().as_millis()
        ));
    }
    Ok(summaries)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        eprintln!("usage: roomball DEV OFFSET K OUT_PREFIX");
        std::process::exit(1);
    }
    let parsed = a[2].parse::<u64>().ok().zip(a[3].parse::<u8>().ok().filter(|k| (1..=8).contains(k)));
    let Some((off, k)) = parsed else {
        println!("ROOMBALL|error=bad_arguments|json=0");
        std::process::exit(1);
    };
    match build(&a[1], off, k, &a[4]) {
        Ok(rows) => rows.iter().for_each(|s| println!("{s}")),
        Err(e) => {
            println!("ROOMBALL|error={e}|json=0");
            std::process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp(name: &str) -> String {
        std::env::temp_dir().join(format!("roomball-test-{}-{name}", std::process::id())).to_str().unwrap().to_string()
    }

    /// A chain 0 - 1 - 2 - 3 - 4 with one flat end, weights chosen so the entries are W-self-adjoint.
    fn chain() -> Vec<roomio::TestRow> {
        vec![
            (1, 0, vec![(0, 54), (1, -2)]),
            (2, 3, vec![(0, -1), (1, 50), (2, -1)]),
            (2, 4, vec![(1, -1), (2, 51), (3, -1)]),
            (2, 5, vec![(2, -1), (3, 52), (4, -1)]),
            (2, 6, vec![(3, -1), (4, 53)]),
        ]
    }

    #[test]
    fn each_radius_is_the_exact_principal_submatrix() {
        let dev = temp("chain");
        roomio::write_test_stream(std::path::Path::new(&dev), &chain());
        let out = temp("chain-out");
        let rows = build(&dev, 0, 2, &out).unwrap();
        assert_eq!(rows.len(), 2);
        assert!(rows[0].contains("|K=1|seeds=1|shells=1,1|states=2|nnz=4|entries_leaving_ball=1|merkle=PASS|passes=3|"), "{}", rows[0]);
        assert!(rows[1].contains("|K=2|seeds=1|shells=1,1,1|states=3|nnz=7|entries_leaving_ball=1|merkle=PASS|passes=3|"), "{}", rows[1]);
        assert_eq!(std::fs::read_to_string(format!("{out}.K1")).unwrap(), "2\n1 2\n0 3\n0 0 54\n0 1 -2\n1 1 50\n");
        assert_eq!(std::fs::read_to_string(format!("{out}.K2")).unwrap(), "3\n1 2 2\n0 3 4\n0 0 54\n0 1 -2\n1 1 50\n1 2 -1\n2 2 51\n");
        for k in 1..=2 {
            assert!(!std::path::Path::new(&format!("{out}.K{k}.entries")).exists());
            std::fs::remove_file(format!("{out}.K{k}")).unwrap();
        }
        std::fs::remove_file(dev).unwrap();
    }

    #[test]
    fn a_ball_past_the_whole_sector_is_the_whole_sector() {
        let dev = temp("whole");
        roomio::write_test_stream(std::path::Path::new(&dev), &chain());
        let out = temp("whole-out");
        let rows = build(&dev, 0, 6, &out).unwrap();
        assert!(rows[5].contains("|shells=1,1,1,1,1,0,0|states=5|nnz=13|entries_leaving_ball=0|"), "{}", rows[5]);
        for k in 1..=6 {
            std::fs::remove_file(format!("{out}.K{k}")).unwrap();
        }
        std::fs::remove_file(dev).unwrap();
    }

    #[test]
    fn a_seed_after_its_neighbours_still_reaches_them() {
        let dev = temp("seeds");
        let rows: Vec<roomio::TestRow> = vec![(1, 3, vec![(0, 50), (2, -1)]), (1, 4, vec![(1, 51)]), (1, 0, vec![(0, -1), (2, 54)])];
        roomio::write_test_stream(std::path::Path::new(&dev), &rows);
        let out = temp("seeds-out");
        let got = build(&dev, 0, 1, &out).unwrap();
        assert!(got[0].contains("|seeds=1|shells=1,1|states=2|nnz=4|entries_leaving_ball=0|"), "{}", got[0]);
        assert_eq!(std::fs::read_to_string(format!("{out}.K1")).unwrap(), "2\n1 1\n3 0\n0 0 50\n0 1 -1\n1 1 54\n");
        std::fs::remove_file(format!("{out}.K1")).unwrap();
        std::fs::remove_file(dev).unwrap();
    }

    #[test]
    fn a_sector_with_no_flat_row_is_an_error() {
        let dev = temp("noflat");
        roomio::write_test_stream(std::path::Path::new(&dev), &[(1, 3, vec![(0, 50)])]);
        assert!(build(&dev, 0, 1, &temp("noflat-out")).is_err());
        std::fs::remove_file(dev).unwrap();
    }
}
