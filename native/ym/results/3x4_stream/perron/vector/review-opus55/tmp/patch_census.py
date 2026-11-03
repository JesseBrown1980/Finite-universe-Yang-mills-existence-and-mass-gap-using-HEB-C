p='census.rs'; s=open(p,encoding='utf-8').read()
s=s.replace("""//!   census LX LY R_NUM R_DEN GFILE THREADS
""","""//!   census LX LY R_NUM R_DEN GFILE THREADS [conj]
//! With `conj`, the first free link runs only over one element of each conjugacy class, with its class size as a multiplicity. Conjugation is a bijection that keeps every signature.
""")
s=s.replace("""    #[inline]
    fn add(&mut self, key: u64) {
        let mask""","""    #[inline]
    fn add(&mut self, key: u64, mult: u64) {
        let mask""")
s=s.replace("""                self.vals[i] += 1;
                return;""","""                self.vals[i] += mult;
                return;""")
s=s.replace("""                self.vals[i] = 1;
                self.used += 1;""","""                self.vals[i] = mult;
                self.used += 1;""")
s=s.replace("""    leaves: u64,
    frame_checks: u64,""","""    leaves: u64,
    mult: u64,
    flat_weighted: u64,
    frame_checks: u64,""")
s=s.replace("""        self.leaves += 1;
        let mut key""","""        self.leaves += self.mult;
        let mut key""")
s=s.replace("""        self.table.add(key + 1);
        if self.a == 0 && self.b == 0 {
            self.flats.push(self.u.clone());
        }
        if self.leaves & 0xF_FFFF == 0 {""","""        self.table.add(key + 1, self.mult);
        if self.a == 0 && self.b == 0 {
            self.flat_weighted += self.mult;
            self.flats.push(self.u.clone());
        }
        self.tick += 1;
        if self.tick & 0xF_FFFF == 0 {""")
s=s.replace("""    frame_checks: u64,
    frame_bad: u64,
}

impl Work""","""    tick: u64,
    frame_checks: u64,
    frame_bad: u64,
}

impl Work""")
s=s.replace("""type WorkerOut = (Table, Vec<Vec<El>>, u64, u64, u64);""","""type WorkerOut = (Table, Vec<Vec<El>>, u64, u64, u64, u64);""")
s=s.replace("""    let threads: usize = args[6].parse().expect("threads");
""","""    let threads: usize = args[6].parse().expect("threads");
    let conj_mode = args.get(7).is_some_and(|x| x == "conj");
""")
s=s.replace("""    let tasks = 36usize;
""","""    let tasks = if conj_mode { 18usize } else { 36usize };
""")
s=s.replace("""                    leaves: 0,
                    frame_checks: 0,""","""                    leaves: 0,
                    mult: 1,
                    flat_weighted: 0,
                    tick: 0,
                    frame_checks: 0,""")
s=s.replace("""                    w.set(free[0], (task / 6) as u8);
                    w.set(free[1], (task % 6) as u8);""","""                    if conj_mode {
                        // Identity, a 3-cycle, a transposition, each standing for its class.
                        let (first, mult) = [(0u8, 1u64), (1, 2), (3, 3)][task / 6];
                        assert_eq!(g.class[first as usize], [0u8, 2, 1][task / 6]);
                        w.mult = mult;
                        w.set(free[0], first);
                    } else {
                        w.set(free[0], (task / 6) as u8);
                    }
                    w.set(free[1], (task % 6) as u8);""")
s=s.replace("""                (w.table, w.flats, w.leaves, w.frame_checks, w.frame_bad)""","""                (w.table, w.flats, w.leaves, w.frame_checks, w.frame_bad, w.flat_weighted)""")
s=s.replace("""    let (mut leaves, mut fc, mut fb) = (0u64, 0u64, 0u64);
    for (table, fl, lv, c, b) in results {""","""    let (mut leaves, mut fc, mut fb, mut fw) = (0u64, 0u64, 0u64, 0u64);
    for (table, fl, lv, c, b, w) in results {""")
s=s.replace("""        fb += b;
    }""","""        fb += b;
        fw += w;
    }""")
s=s.replace("""flat_gauge_fixed={}|flat_classes={}|frame_audits={fc}|frame_bad={fb}|seconds={}|json=0", merged.len(), flats.len(), classes.len(), start.elapsed().as_secs());""","""flat_gauge_fixed={fw}|flat_classes={}|frame_audits={fc}|frame_bad={fb}|seconds={}|json=0", merged.len(), classes.len(), start.elapsed().as_secs());""")
open(p,'w',encoding='utf-8',newline='\n').write(s)
