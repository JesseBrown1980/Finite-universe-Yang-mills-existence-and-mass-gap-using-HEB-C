p='classes.rs'; s=open(p,encoding='utf-8').read()
s=s.replace("""    for ((a, b), (m, n)) in &per {
        println!("CLASSMIN|a={a}|b={b}|micro={m}|n={n:?}|json=0");
    }
""","""    for ((a, b), (m, n)) in &per {
        println!("CLASSMIN|a={a}|b={b}|micro={m}|n={n:?}|json=0");
    }
    if args.get(7).is_some_and(|x| x == "dump") {
        for key in &w.seen {
            println!("CSIG|{key}|json=0");
        }
    }
""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
