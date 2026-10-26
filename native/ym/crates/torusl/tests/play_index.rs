//! Index certificate for the play primitive (small lattices, exhaustive).
use torusl::play::{chi, play_row, Address, Ctx};
use torusl::{Lat, G};

const SECTORS: [(i64, i64); 4] = [(1, 1), (1, -1), (-1, 1), (-1, -1)];

fn keys_of(ctx: &Ctx, lat: &Lat, sx: i64, sy: i64) -> Vec<u64> {
    let mut s = ctx.scratch();
    let total = 6u64.pow(u32::try_from(lat.free.len()).unwrap());
    (0..total)
        .filter(|&id| {
            let q = ctx.decode(id);
            lat.canonical(ctx.g, &q) as u64 == id && ctx.representative(id, sx, sy, &mut s).is_some()
        })
        .collect()
}

/// Every image of every gauge orbit maps to its representative with the
/// predicted character coefficient; character-odd orbits are rejected exactly.
#[test]
fn orbit_consistency_2x2_and_2x3() {
    let g = G::new();
    for (lx, ly) in [(2, 2), (2, 3)] {
        let lat = Lat::new(lx, ly);
        let ctx = Ctx::new(&g, &lat);
        let mut s = ctx.scratch();
        let total = 6u64.pow(u32::try_from(lat.free.len()).unwrap());
        for &(sx, sy) in &SECTORS {
            let addr = Address::checked(keys_of(&ctx, &lat, sx, sy), total).unwrap();
            for id in 0..total {
                let q = ctx.decode(id);
                if lat.canonical(&g, &q) as u64 != id {
                    continue;
                }
                let raw = lat.representative(&q);
                let (rep, sign0) = ctx.canon(&raw, sx, sy, &mut s);
                let mut img = raw.clone();
                for o in 0..ctx.ops.dest.len() {
                    ctx.apply(o, &raw, &mut img);
                    let (r2, sg) = ctx.canon(&img, sx, sy, &mut s);
                    assert_eq!(r2, rep, "image maps to the same representative");
                    if sign0 == 0 {
                        assert_eq!(sg, 0, "character-odd orbit rejected for every image");
                    } else {
                        assert_eq!(sg, sign0 * chi(ctx.ops.point[o], sx, sy), "coefficient = chi(g) relative to the orbit");
                    }
                }
                // membership: addressed exactly when the orbit is in the sector
                assert_eq!(addr.find(rep).is_some(), sign0 != 0);
            }
        }
    }
}

#[test]
fn boundary_and_absent_keys() {
    let g = G::new();
    let lat = Lat::new(2, 3);
    let ctx = Ctx::new(&g, &lat);
    let total = 6u64.pow(u32::try_from(lat.free.len()).unwrap());
    let keys = keys_of(&ctx, &lat, 1, 1);
    let addr = Address::checked(keys.clone(), total).unwrap();
    assert_eq!(addr.find(keys[0]), Some(0));
    assert_eq!(addr.find(*keys.last().unwrap()), Some(keys.len() - 1));
    for (i, &k) in keys.iter().enumerate() {
        assert_eq!(addr.find(k), Some(i));
    }
    // absent keys: gaps between representatives and beyond the ends
    let mut absent = 0;
    for w in keys.windows(2) {
        if w[1] > w[0] + 1 {
            assert_eq!(addr.find(w[0] + 1), None);
            absent += 1;
        }
    }
    assert!(absent > 0);
    assert_eq!(addr.find(total - 1), keys.binary_search(&(total - 1)).ok());
}

#[test]
fn corrupt_address_files_fail_closed() {
    let g = G::new();
    let lat = Lat::new(2, 2);
    let ctx = Ctx::new(&g, &lat);
    let mut s = ctx.scratch();
    let total = 6u64.pow(u32::try_from(lat.free.len()).unwrap());
    let keys = keys_of(&ctx, &lat, 1, 1);
    // duplicate key
    let mut dup = keys.clone();
    dup.insert(5, dup[5]);
    assert!(Address::checked(dup, total).is_err());
    // unsorted
    let mut uns = keys.clone();
    uns.swap(3, 4);
    assert!(Address::checked(uns, total).is_err());
    // key outside the space
    let mut out = keys.clone();
    out.push(total);
    assert!(Address::checked(out, total).is_err());
    // incomplete file: a removed representative makes some row fail
    let mut missing = keys.clone();
    missing.remove(missing.len() / 2);
    let addr = Address::checked(missing, total).unwrap();
    assert!((0..addr.keys.len()).any(|i| play_row(&ctx, &addr, i, 1, 1, &mut s).is_err()));
    // wrong-sector file: the (1,-1) keys played as sector (1,1)
    let wrong = Address::checked(keys_of(&ctx, &lat, 1, -1), total).unwrap();
    assert!((0..wrong.keys.len()).any(|i| play_row(&ctx, &wrong, i, 1, 1, &mut s).is_err()));
    // the complete, correct file plays every row
    let good = Address::checked(keys, total).unwrap();
    assert!((0..good.keys.len()).all(|i| play_row(&ctx, &good, i, 1, 1, &mut s).is_ok()));
}
