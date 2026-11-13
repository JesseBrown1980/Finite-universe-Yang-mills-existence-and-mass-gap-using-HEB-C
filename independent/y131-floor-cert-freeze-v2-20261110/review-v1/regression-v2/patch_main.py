import sys
p = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/src/main.rs"
s = open(p, "rb").read().decode("utf-8")
assert "\r" not in s
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, count, old[:80])
    s = s.replace(old, new)

# header note
rep("// written file with the same row hash before any gamma is quoted (design/gate_required.sh). SHA-256 is std-only, below.\n",
    "// written file with the same row hash before any gamma is quoted (design/gate_required.sh). SHA-256 is std-only, below.\n"
    "// V2 (2026-11-10, operational review of the freeze e74d8a46): `rowhash` creates its --dir when it is absent; the 22\n"
    "// clippy 1.81 findings are rewritten with the same integer results (regression receipts in review-v1/ and the record).\n")
# 1 hex / format_collect
rep("    b.iter().map(|x| format!(\"{:02x}\", x)).collect()\n",
    "    let mut s = String::with_capacity(2 * b.len());\n    for x in b.iter() {\n        write!(s, \"{:02x}\", x).unwrap();\n    }\n    s\n")
# 2 dst loop
rep("                    for k in 0..NL {\n                        let (d, iv) = dst[k];\n",
    "                    for (k, &(d, iv)) in dst.iter().enumerate() {\n")
# 3 encode
rep("        for j in 0..NK {\n            k = k * 6 + z[j] as u64;\n        }\n",
    "        for &zj in z.iter() {\n            k = k * 6 + zj as u64;\n        }\n")
# 4 from_key rename
rep("from_key(", "links_of_key(", 3)
# 5 letters
rep("        for j in 0..NK {\n            let (s0, t0) = self.kst[j];\n            let x = self.val(s, u, self.kept[j]);\n            z[j] = self.mul",
    "        for (j, zj) in z.iter_mut().enumerate() {\n            let (s0, t0) = self.kst[j];\n            let x = self.val(s, u, self.kept[j]);\n            *zj = self.mul")
# 6 apply
rep("        for d in 0..NL {\n            o[d] = self.val(s, u, d);\n        }\n",
    "        for (d, od) in o.iter_mut().enumerate() {\n            *od = self.val(s, u, d);\n        }\n")
# 7 pdone
rep("        for p in 0..V {\n            if !pdone[p] && tab.plq[p].iter().all(|&(l, _)| assigned[l]) {\n                pdone[p] = true;\n",
    "        for (p, pd) in pdone.iter_mut().enumerate() {\n            if !*pd && tab.plq[p].iter().all(|&(l, _)| assigned[l]) {\n                *pd = true;\n")
# 8 dfs
rep("    fn dfs(tab: &Tab, order: &[usize; NK], done_at: &[Vec<usize>], lev: usize, u: &mut [u8; NL], msum: i64, m0: i64, out: &mut Vec<u64>) {\n",
    "    struct Dfs<'a> {\n        tab: &'a Tab,\n        order: &'a [usize; NK],\n        done_at: &'a [Vec<usize>],\n        m0: i64,\n    }\n"
    "    fn dfs(cx: &Dfs, lev: usize, u: &mut [u8; NL], msum: i64, out: &mut Vec<u64>) {\n        let (tab, order, done_at, m0) = (cx.tab, cx.order, cx.done_at, cx.m0);\n")
rep("                dfs(tab, order, done_at, lev + 1, u, m, m0, out);\n", "                dfs(cx, lev + 1, u, m, out);\n")
rep("                            dfs(tab, order, done_at, 3, &mut u, m, m0, &mut out);\n",
    "                            dfs(&Dfs { tab, order, done_at, m0 }, 3, &mut u, m, &mut out);\n")
rep("                        for lev in 0..3 {\n                            for &p in done_at[lev].iter() {\n",
    "                        for at in done_at.iter().take(3) {\n                            for &p in at.iter() {\n")
# 9 mem
rep("        if l.starts_with(\"VmHWM:\") {\n            return l[6..].trim().replace(' ', \"\");\n",
    "        if let Some(rest) = l.strip_prefix(\"VmHWM:\") {\n            return rest.trim().replace(' ', \"\");\n")
# 10 plaquette_costs
rep("    for p in 0..V {\n        pc[p] = tab.pcost(u, p);\n        m += pc[p];\n    }\n",
    "    for (p, c) in pc.iter_mut().enumerate() {\n        *c = tab.pcost(u, p);\n        m += *c;\n    }\n")
# 11 col
rep("        for p in 0..V {\n            col[p] = c % 3;\n            c /= 3;\n        }\n",
    "        for cp in col.iter_mut() {\n            *cp = c % 3;\n            c /= 3;\n        }\n")
# 12 nonminimal bool
rep("        if !(tn * o.cap_d < o.cap_n * td) {\n", "        if tn * o.cap_d >= o.cap_n * td {\n")
# 13 fmat removal, fmat_x signature: t as one Rat (tn/td)
rep("fn fmat(rows: &[Row], f: &[i128], r: Rat, tn: i128, td: i128, threads: usize) -> FMat {\n    fmat_x(rows, f, r, tn, td, threads, false, true)\n}\n", "")
rep("fn fmat_x(rows: &[Row], f: &[i128], r: Rat, tn: i128, td: i128, threads: usize, flip: bool, strict: bool) -> FMat {\n",
    "// t = tn/td is passed as one Rat (n = tn, d = td)\nfn fmat_x(rows: &[Row], f: &[i128], r: Rat, t: Rat, threads: usize, flip: bool, strict: bool) -> FMat {\n    let (tn, td) = (t.n, t.d);\n")
# 14 gs_eigen
rep("fn gs_eigen(fm: &FMat, v: &mut Vec<i128>, outer: usize, verbose: bool) -> i128 {", "fn gs_eigen(fm: &FMat, v: &mut [i128], outer: usize, verbose: bool) -> i128 {")
rep("    for a in 0..n {\n        for &(j, w) in fm.ent[a].iter() {\n            if j as usize == a {\n                selfw[a] += w;\n            }\n        }\n    }\n",
    "    for (a, sw) in selfw.iter_mut().enumerate() {\n        for &(j, w) in fm.ent[a].iter() {\n            if j as usize == a {\n                *sw += w;\n            }\n        }\n    }\n")
rep("let margin = ((hi - lo) / 4).max(E / 50).min(20 * E);", "let margin = ((hi - lo) / 4).clamp(E / 50, 20 * E);")
# 15 certify: Problem + Solve
rep("fn certify(rows: &[Row], f: &[i128], r: Rat, td: i128, tcap: i128, o: Opts, sweeps: usize, threads: usize, verbose: bool, tag: &str, strict: bool) -> (i128, Vec<i64>) {\n    let strict = strict && o.gates && !o.flip;\n",
    "// the data of one certificate problem (rows, f, r and the t denominator td) and the solver settings of one certify call\n"
    "#[derive(Clone, Copy)]\nstruct Problem<'a> {\n    rows: &'a [Row],\n    f: &'a [i128],\n    r: Rat,\n    td: i128,\n}\n"
    "#[derive(Clone, Copy)]\nstruct Solve<'a> {\n    sweeps: usize,\n    threads: usize,\n    verbose: bool,\n    tag: &'a str,\n    strict: bool,\n}\n"
    "fn certify(pb: Problem, tcap: i128, o: Opts, sv: Solve) -> (i128, Vec<i64>) {\n"
    "    let Problem { rows, f, r, td } = pb;\n    let Solve { sweeps, threads, verbose, tag, strict } = sv;\n"
    "    let strict = strict && o.gates && !o.flip;\n")
rep("        let fm = fmat_x(rows, f, r, tn, td, threads, o.flip, strict);\n", "        let fm = fmat_x(rows, f, r, Rat { n: tn, d: td }, threads, o.flip, strict);\n")
rep("certify(&b.rows, &f, r, td, tcap, o, sweeps, threads, args.iter().any(|a| a == \"--verbose\"), \"honest\", true);",
    "certify(Problem { rows: &b.rows, f: &f, r, td }, tcap, o, Solve { sweeps, threads, verbose: args.iter().any(|a| a == \"--verbose\"), tag: \"honest\", strict: true });")
rep("certify(rows, f, r, td, tcap, bare, sweeps, threads, false, name, false);",
    "certify(Problem { rows, f, r, td }, tcap, bare, Solve { sweeps, threads, verbose: false, tag: name, strict: false });")
rep("certify(&b.rows, &f2, r, td, tcap, bare, sweeps, threads, false, \"P3a\", false);",
    "certify(Problem { rows: &b.rows, f: &f2, r, td }, tcap, bare, Solve { sweeps, threads, verbose: false, tag: \"P3a\", strict: false });")
rep("certify(&b.rows, f, r, td, tcap_over, over, sweeps, threads, false, \"P4c\", false);",
    "certify(Problem { rows: &b.rows, f, r, td }, tcap_over, over, Solve { sweeps, threads, verbose: false, tag: \"P4c\", strict: false });")
rep("certify(&b.rows, f, r, td, tcap_low, under, sweeps, threads, false, \"P4d\", false);",
    "certify(Problem { rows: &b.rows, f, r, td }, tcap_low, under, Solve { sweeps, threads, verbose: false, tag: \"P4d\", strict: false });")
# 16 write_cert
rep("fn write_cert(path: &str, m0: i64, r: Rat, tn: i128, td: i128, f: &[i128], cap: (i128, i128), rowhash: &str, keyshash: &str, freeze: &Option<(String, String)>, rows: &[Row], v: &[i64]) -> String {\n",
    "struct CertOut<'a> {\n    path: &'a str,\n    m0: i64,\n    r: Rat,\n    tn: i128,\n    td: i128,\n    f: &'a [i128],\n    cap: (i128, i128),\n    rowhash: &'a str,\n    keyshash: &'a str,\n    freeze: &'a Option<(String, String)>,\n    rows: &'a [Row],\n    v: &'a [i64],\n}\n"
    "fn write_cert(c: &CertOut) -> String {\n    let CertOut { path, m0, r, tn, td, f, cap, rowhash, keyshash, freeze, rows, v } = *c;\n")
rep("write_cert(&p, m0, r, lo, td, &f, (dn, dd), &b.rowhash, &b.keyshash, &freeze, &b.rows, &vi);",
    "write_cert(&CertOut { path: &p, m0, r, tn: lo, td, f: &f, cap: (dn, dd), rowhash: &b.rowhash, keyshash: &b.keyshash, freeze: &freeze, rows: &b.rows, v: &vi });")
rep("write_cert(&path, m0, r, tf, td, ff, cap, &rh, &b.keyshash, &None, &b.rows, vf);",
    "write_cert(&CertOut { path: &path, m0, r, tn: tf, td, f: ff, cap, rowhash: &rh, keyshash: &b.keyshash, freeze: &None, rows: &b.rows, v: vf });")
# 17 redundant closure
rep(".split(',').map(|x| parse_rat(x)).collect();", ".split(',').map(parse_rat).collect();")
# 18 max_t
rep("fn max_t(rows: &[Row], v: &[i64], f: &[i128], r: Rat, td: i128, o: Opts, lo0: i128, hi0: i128) -> Option<i128> {\n",
    "fn max_t(pb: Problem, v: &[i64], o: Opts, lo0: i128, hi0: i128) -> Option<i128> {\n    let Problem { rows, f, r, td } = pb;\n")
rep("max_t(&b.rows, v, f, r, td, o_flip, tn - 20 * td, tcap)", "max_t(Problem { rows: &b.rows, f, r, td }, v, o_flip, tn - 20 * td, tcap)")
# E1: rowhash creates its --dir
rep("fn rowhash_only(args: &[String]) {\n    let tab = tables();\n",
    "// V2: an absent --dir is created here, before the keys file is written; `cert` creates no directory (it reuses the\n// directory that `rowhash` wrote, or an existing one, as in FIX-1)\nfn rowhash_only(args: &[String]) {\n    std::fs::create_dir_all(arg(args, \"--dir\", \".\")).unwrap();\n    let tab = tables();\n")
open(p, "wb").write(s.encode("utf-8"))
print("patched", len(s))
