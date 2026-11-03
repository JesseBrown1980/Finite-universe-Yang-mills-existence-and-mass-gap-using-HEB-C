p='census.rs'; s=open(p,encoding='utf-8').read()
s=s.replace("use review::{adj_limit, micro,","use review::{adj_limit, ceil_two_root, micro,")
s=s.replace("""    let conj_mode = args.get(7).is_some_and(|x| x == "conj");
""","""    let conj_mode = args.iter().any(|x| x == "conj");
    let planar = args.iter().any(|x| x == "planar");
""")
s=s.replace("""    let (ul, uy) = (lx as u32, ly as u32);
    let p = (lx * ly) as u32;""","""    let (ul, uy) = (lx as u32, ly as u32);
    let p = (lx * ly) as u32;
    let limit = |s: u32| if planar { 2 * s - ceil_two_root(s) } else { adj_limit(s, ul, uy) };""")
s=s.replace("""            && tt <= adj_limit(a, ul, uy)
            && cc <= adj_limit(b, ul, uy)
            && tt + tc + cc <= adj_limit(a + b, ul, uy);""","""            && tt <= limit(a)
            && cc <= limit(b)
            && tt + tc + cc <= limit(a + b);""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
p='classes.rs'; s=open(p,encoding='utf-8').read()
s=s.replace("use review::{adj_limit, micro,","use review::{adj_limit, ceil_two_root, micro,")
s=s.replace("""    let (ul, uy) = (lx as u32, ly as u32);
    let mut outside = 0u64;""","""    let (ul, uy) = (lx as u32, ly as u32);
    let planar = args.iter().any(|x| x == "planar");
    let limit = |s: u32| if planar { 2 * s - ceil_two_root(s) } else { adj_limit(s, ul, uy) };
    let mut outside = 0u64;""")
s=s.replace("""tt as u32 <= adj_limit(a, ul, uy) && cc as u32 <= adj_limit(b, ul, uy) && (tt + tc + cc) as u32 <= adj_limit(a + b, ul, uy);""","""tt as u32 <= limit(a) && cc as u32 <= limit(b) && (tt + tc + cc) as u32 <= limit(a + b);""")
s=s.replace("""    if args.get(7).is_some_and(|x| x == "dump") {""","""    if args.iter().any(|x| x == "dump") {""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
