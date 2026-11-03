
/// A lower bound outside the claim: d is the actual vector on every orbit with M <= cut and one value per lump above it.
/// Rows at M <= cut are exact. Rows above it are the signature rows of my table, with a move into a lump at M <= cut bounded by the largest d in that lump.
/// So the minimum ratio is a rigorous lower bound on lambda_1(H') when the model holds every non-flat orbit with M <= cut, which py_lump_counts.py checks.
#[allow(clippy::too_many_arguments, clippy::too_many_lines)]
fn hybrid(t: &Torus, g: &Group, c: &Canon, md: &Model, r: i64, cut: u32, targets: &[i128], sweeps: usize, threads: usize, start_psi: &[i64]) {
    const U: i128 = 1_000_000;
    const TOP_BITS: u32 = 90;
    type Row = (u32, Vec<(u32, u32)>);
    let p = t.sites as u32;
    let mut lumps: Vec<(u32, u32)> = Vec::new();
    for a in (0..=p).step_by(2) {
        for b in 0..=(p - a) {
            lumps.push((a, b));
        }
    }
    let idx: HashMap<(u32, u32), usize> = lumps.iter().enumerate().map(|(i, l)| (*l, i)).collect();
    let cost = |l: (u32, u32)| 2 * l.0 + 3 * l.1;
    let n = md.keys.len();
    // The lump of each state and its moves past the cut, per lump.
    let mut state_lump = vec![0u32; n];
    let mut out_offs: Vec<u32> = vec![0];
    let mut out_list: Vec<(u32, u32)> = Vec::new();
    let mut u = vec![0u8; t.nl];
    for (i, sl) in state_lump.iter_mut().enumerate() {
        c.decode(md.keys[i], &mut u);
        let mut cls = vec![0u8; t.sites];
        let (mut a, mut b) = (0u32, 0u32);
        for (q, x) in cls.iter_mut().enumerate() {
            *x = g.class[t.hol(g, &u, q) as usize];
            match *x {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        *sl = idx[&(a, b)] as u32;
        let mut tally: HashMap<u32, u32> = HashMap::new();
        for l in 0..t.nl {
            let keep = u[l];
            let [p0, p1] = t.link_plaq[l];
            for &e in &g.trans {
                u[l] = g.m(e, keep);
                let (mut a2, mut b2) = (a, b);
                for q in [p0, p1] {
                    match cls[q] {
                        1 => a2 -= 1,
                        2 => b2 -= 1,
                        _ => {}
                    }
                    match g.class[t.hol(g, &u, q) as usize] {
                        1 => a2 += 1,
                        2 => b2 += 1,
                        _ => {}
                    }
                }
                if cost((a2, b2)) > cut {
                    *tally.entry(idx[&(a2, b2)] as u32).or_insert(0) += 1;
                }
            }
            u[l] = keep;
        }
        out_list.extend(tally);
        out_offs.push(out_list.len() as u32);
    }
    // Signature rows of the lumps past the cut.
    let (ul, uy) = (t.lx as u32, t.ly as u32);
    let nl = t.nl as i64;
    let mut rows: Vec<Vec<Row>> = vec![Vec::new(); lumps.len()];
    for (li, &(a, b)) in lumps.iter().enumerate() {
        if cost((a, b)) <= cut {
            continue;
        }
        let (la, lb, li2) = (adj_limit(a, ul, uy), adj_limit(b, ul, uy), adj_limit(a + b, ul, uy));
        let mut seen: std::collections::HashSet<Row> = std::collections::HashSet::new();
        for tt in 0..=la {
            for tc in 0..=(4 * a - 2 * tt).min(4 * b) {
                let mut cc = 0u32;
                while 2 * cc + tc <= 4 * b && cc <= lb && tt + tc + cc <= li2 {
                    let et = 4 * a - 2 * tt - tc;
                    let ec = 4 * b - tc - 2 * cc;
                    let ee = nl - i64::from(et) - i64::from(ec) - i64::from(tt) - i64::from(tc) - i64::from(cc);
                    if ee >= 0 {
                        for tts in 0..=tt {
                            let counts = [ee as u32, et, ec, tts, tt - tts, tc, cc];
                            let mut near: HashMap<u32, u32> = HashMap::new();
                            let mut own = 0u32;
                            for (pat, count) in counts.iter().enumerate() {
                                if *count != 0 {
                                    for &(da, db, m) in RULE[pat] {
                                        let tgt = (a.wrapping_add_signed(da), b.wrapping_add_signed(db));
                                        if tgt == (a, b) {
                                            own += m * *count;
                                        } else if tgt != (0, 0) {
                                            *near.entry(idx[&tgt] as u32).or_insert(0) += m * *count;
                                        }
                                    }
                                }
                            }
                            let mut list: Vec<(u32, u32)> = near.into_iter().collect();
                            list.sort_unstable();
                            if seen.insert((own, list.clone())) {
                                rows[li].push((own, list));
                            }
                        }
                    }
                    cc += 1;
                }
            }
        }
    }
    let diag_of = |l: (u32, u32)| i128::from(r) * i128::from(cost(l)) + 3 * i128::from(nl);
    let mut order: Vec<usize> = (0..lumps.len()).filter(|i| cost(lumps[*i]) > cut).collect();
    order.sort_by_key(|i| cost(lumps[*i]));
    println!("HYBRID_SETUP|states={n}|rows_past_cut={}|lumps_past_cut={}|json=0", rows.iter().map(Vec::len).sum::<usize>(), order.len());
    let mut psi: Vec<i128> = start_psi.iter().map(|x| (i128::from(*x) + 1) << 50).collect();
    let mut gval: Vec<i128> = lumps
        .iter()
        .map(|l| {
            let m = cost(*l);
            if m <= cut {
                0
            } else {
                let drop = 2 * (m - cut);
                ((1i128 << 70) >> drop.min(60)).max(1)
            }
        })
        .collect();
    let mut dbar = vec![0i128; lumps.len()];
    let mut next = vec![0i128; n];
    let chunk = n.div_ceil(threads);
    let mut best = i128::MIN;
    let fill = |dbar: &mut Vec<i128>, psi: &[i128], gval: &[i128]| {
        dbar.fill(0);
        for (i, v) in psi.iter().enumerate() {
            let l = state_lump[i] as usize;
            if *v > dbar[l] {
                dbar[l] = *v;
            }
        }
        for &li in &order {
            dbar[li] = gval[li];
        }
    };
    for &target in targets {
        for _ in 0..sweeps {
            fill(&mut dbar, &psi, &gval);
            let (psi_ref, dbar_ref, out_offs_ref, out_list_ref) = (&psi, &dbar, &out_offs, &out_list);
            std::thread::scope(|scope| {
                for (tn, out) in next.chunks_mut(chunk).enumerate() {
                    scope.spawn(move || {
                        let base = tn * chunk;
                        for (j, slot) in out.iter_mut().enumerate() {
                            let i = base + j;
                            let mut s: i128 = 0;
                            for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                                s += psi_ref[q as usize];
                            }
                            for &(l, m) in &out_list_ref[out_offs_ref[i] as usize..out_offs_ref[i + 1] as usize] {
                                s += i128::from(m) * dbar_ref[l as usize];
                            }
                            let d = (i128::from(r) * i128::from(md.m[i]) + 3 * i128::from(nl)) * U - target;
                            *slot = (psi_ref[i] + s * U / d) / 2;
                        }
                    });
                }
            });
            std::mem::swap(&mut psi, &mut next);
            fill(&mut dbar, &psi, &gval);
            for &li in &order {
                let dl = diag_of(lumps[li]);
                let mut top: i128 = 0;
                for (own, near) in &rows[li] {
                    let mut s: i128 = 0;
                    for &(l, m) in near {
                        s += i128::from(m) * dbar[l as usize];
                    }
                    let den = (dl - i128::from(*own)) * U - target;
                    assert!(den > 0, "a row past the cut leaves no room at this target");
                    top = top.max(s * U / den);
                }
                let new = ((gval[li] + top) / 2).max(1);
                gval[li] = new;
                dbar[li] = new;
            }
            let high = psi.iter().copied().max().unwrap_or(1).max(gval.iter().copied().max().unwrap_or(1));
            let bits = 128 - high.leading_zeros();
            if bits > TOP_BITS {
                let sh = bits - TOP_BITS;
                for x in &mut psi {
                    *x >>= sh;
                }
                for x in &mut gval {
                    if *x > 0 {
                        *x = (*x >> sh).max(1);
                    }
                }
            } else if bits < TOP_BITS {
                let sh = TOP_BITS - bits;
                for x in &mut psi {
                    *x <<= sh;
                }
                for x in &mut gval {
                    *x <<= sh;
                }
            }
        }
        // The exact value of this d.
        fill(&mut dbar, &psi, &gval);
        let mut min_a = i128::MAX;
        let mut zero = 0u64;
        for (i, pi) in psi.iter().enumerate() {
            if *pi <= 0 {
                zero += 1;
                continue;
            }
            let mut s: i128 = 0;
            for &q in &md.adj[md.offs[i] as usize..md.offs[i + 1] as usize] {
                s += psi[q as usize];
            }
            for &(l, m) in &out_list[out_offs[i] as usize..out_offs[i + 1] as usize] {
                s += i128::from(m) * dbar[l as usize];
            }
            let dg = i128::from(r) * i128::from(md.m[i]) + 3 * i128::from(nl);
            let v = dg * U - (s * U + *pi - 1) / *pi;
            min_a = min_a.min(v);
        }
        let mut min_b = i128::MAX;
        for &li in &order {
            let dl = diag_of(lumps[li]);
            for (own, near) in &rows[li] {
                let mut s: i128 = 0;
                for &(l, m) in near {
                    s += i128::from(m) * dbar[l as usize];
                }
                let v = (dl - i128::from(*own)) * U - (s * U + gval[li] - 1) / gval[li];
                min_b = min_b.min(v);
            }
        }
        let cert = if zero == 0 { min_a.min(min_b) } else { i128::MIN };
        if cert > best {
            best = cert;
        }
        println!("HYBRID|Lx={}|Ly={}|r={r}|mcut={cut}|target_micro={target}|cert_micro={cert}|min_exact_rows={min_a}|min_table_rows={min_b}|psi_zero={zero}|json=0", t.lx, t.ly);
    }
    println!("HYBRID_BEST|Lx={}|Ly={}|r={r}|mcut={cut}|cert_micro={best}|json=0", t.lx, t.ly);
}

const PSI_TOP: i64 = 1 << 36;
