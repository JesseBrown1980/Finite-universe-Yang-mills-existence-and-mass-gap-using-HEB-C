p='ritz.rs'; s=open(p,encoding='utf-8').read()
s=s.replace("use review::{cost_of_class, El, Group, Rng, Torus, ID};","use review::{adj_limit, cost_of_class, micro, ratio_from_definition, El, Group, Rng, Torus, Vector, ID, NPAT, RULE};")
s=s.replace("""const PSI_TOP: i64 = 1 << 36;
""","""/// Exhaustive low-M audit on real orbits: every state of the model, every move recomputed from the definition, checked against the rule and the constraints, with the exact ratio of a vector.
fn audit_low_m(t: &Torus, g: &Group, c: &Canon, md: &Model, path: &str, r: i128) {
    let v = Vector::load(path);
    let mut u = vec![0u8; t.nl];
    let (mut low, mut at, mut low_n) = (i128::MAX, (0u32, 0u32), [0u32; NPAT]);
    let (mut outside, mut rule_bad, mut odd, mut m_bad, mut configs) = (0u64, 0u64, 0u64, 0u64, 0u64);
    let (ul, uy) = (t.lx as u32, t.ly as u32);
    for i in 0..md.keys.len() {
        c.decode(md.keys[i], &mut u);
        configs += u64::from(md.weight[i]);
        let (num, den, (a, b), hist) = ratio_from_definition(t, g, &mut u, &v, r, 1);
        if 2 * a + 3 * b != u32::from(md.m[i]) {
            m_bad += 1;
        }
        if a % 2 != 0 {
            odd += 1;
        }
        let n = t.counts(g, &u);
        let mut predicted: HashMap<(u32, u32), u32> = HashMap::new();
        for (pat, count) in n.iter().enumerate() {
            if *count != 0 {
                for &(da, db, m) in RULE[pat] {
                    *predicted.entry((a.wrapping_add_signed(da), b.wrapping_add_signed(db))).or_insert(0) += m * *count;
                }
            }
        }
        if predicted != hist {
            rule_bad += 1;
        }
        let (tt, cc, inner) = (n[3] + n[4], n[6], n[3] + n[4] + n[5] + n[6]);
        if 4 * a != n[1] + n[5] + 2 * tt || 4 * b != n[2] + n[5] + 2 * cc || tt > adj_limit(a, ul, uy) || cc > adj_limit(b, ul, uy) || inner > adj_limit(a + b, ul, uy) {
            outside += 1;
        }
        let m = micro(num, den);
        if m < low {
            low = m;
            at = (a, b);
            low_n = n;
        }
    }
    println!("LOWM_AUDIT|Lx={}|Ly={}|r={r}|mcut_states={}|configs={configs}|m_bad={m_bad}|a_odd={odd}|rule_bad={rule_bad}|outside={outside}|min_ratio_micro={low}|at_a={}|at_b={}|n={low_n:?}|file={path}|json=0", t.lx, t.ly, md.keys.len(), at.0, at.1);
}

const PSI_TOP: i64 = 1 << 36;
""")
s=s.replace("""    if sabotage == "unit_weight" {
        md.weight.fill(1);
    }""","""    if let Some(path) = args.iter().find_map(|x| x.strip_prefix("audit=")) {
        audit_low_m(&t, &g, &canon, &md, path, i128::from(r));
    }
    if sabotage == "unit_weight" {
        md.weight.fill(1);
    }""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
