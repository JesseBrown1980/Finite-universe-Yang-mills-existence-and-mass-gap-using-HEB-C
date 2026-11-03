p = 'C:/tmp/opus55/vector-review-20261103/review/src/bin/ritz.rs'
s = open(p, encoding='utf-8').read()
old = """fn hybrid(t: &Torus, g: &Group, c: &Canon, md: &Model, r: i64, cut: u32, targets: &[i128], sweeps: usize, threads: usize, start_psi: &[i64]) {"""
assert old in s
s = s.replace(old, """fn hybrid(t: &Torus, g: &Group, c: &Canon, md: &Model, r: i64, cut: u32, targets: &[i128], sweeps: usize, threads: usize, start_psi: &[i64], dump: &str) {""")
old = """        if cert > best {
            best = cert;
        }
"""
assert old in s
s = s.replace(old, """        if cert > best {
            best = cert;
            let mut text = String::new();
            for (i, pi) in psi.iter().enumerate() {
                text.push_str(&format!("P|{}|{}\\n", md.keys[i], pi));
            }
            for &li in &order {
                text.push_str(&format!("G|{}|{}|{}\\n", lumps[li].0, lumps[li].1, gval[li]));
            }
            std::fs::write(dump, text).expect("write hybrid vector");
        }
""")
old = """        hybrid(&t, &g, &canon, &md, r, cut, &targets, hs, threads, &psi);"""
assert old in s
s = s.replace(old, """        hybrid(&t, &g, &canon, &md, r, cut, &targets, hs, threads, &psi, &format!("{prefix}.hybrid"));""")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print("patched2")
