p = 'C:/tmp/opus55/vector-review-20261103/review/src/bin/ritz.rs'
s = open(p, encoding='utf-8').read()
hyb = open('C:/tmp/opus55/vector-review-20261103/tmp/hybrid_fn.rs', encoding='utf-8').read()
assert "\nconst PSI_TOP: i64 = 1 << 36;\n" in s
s = s.replace("\nconst PSI_TOP: i64 = 1 << 36;\n", hyb, 1)
old = """    let sh = format!("{prefix}.psi");"""
assert old in s
s = s.replace(old, """    if let Some(list) = args.iter().find_map(|x| x.strip_prefix("hybrid=")) {
        let targets: Vec<i128> = list.split(',').map(|x| x.parse().expect("target")).collect();
        let hs: usize = args.iter().find_map(|x| x.strip_prefix("hsweeps=")).map_or(200, |x| x.parse().expect("hsweeps"));
        hybrid(&t, &g, &canon, &md, r, cut, &targets, hs, threads, &psi);
    }
    let sh = format!("{prefix}.psi");""")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print("patched")
