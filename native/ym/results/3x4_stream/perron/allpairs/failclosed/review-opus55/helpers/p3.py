p="C:/tmp/opus55/allpairs-review-20261103/fuzz/harness_tail.rs"
s=open(p,encoding="utf-8").read()
a="""                if u64::from(j) == h {
                    t.diag += 1;
                    has_diag = true;
                } else if u64::from(j) > h {
                    t.upper += 1;
                    upper.insert((h as u32, j), v64);
                } else {
                    t.lower += 1;
                    lower.push((j, h as u32, v64));
                }"""
b="""                match u64::from(j).cmp(&h) {
                    std::cmp::Ordering::Equal => {
                        t.diag += 1;
                        has_diag = true;
                    }
                    std::cmp::Ordering::Greater => {
                        t.upper += 1;
                        upper.insert((h as u32, j), v64);
                    }
                    std::cmp::Ordering::Less => {
                        t.lower += 1;
                        lower.push((j, h as u32, v64));
                    }
                }"""
assert a in s; s=s.replace(a,b)
a="""    fn one_case(file: &[u8], cap: usize, cap2: usize, tmp: &str, sha: &Sha256, tally: &mut Tally, seed: u64, iter: u64, shown: &mut u32) {"""
b="""    #[allow(clippy::too_many_arguments)]
    fn one_case(file: &[u8], cap: usize, cap2: usize, tmp: &str, sha: &Sha256, tally: &mut Tally, seed: u64, iter: u64, shown: &mut u32) {"""
assert a in s; s=s.replace(a,b)
open(p,"w",encoding="utf-8",newline="\n").write(s)
