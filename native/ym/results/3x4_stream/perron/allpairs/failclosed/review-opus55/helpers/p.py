p="C:/tmp/opus55/allpairs-review-20261103/reader/src/main.rs"
s=open(p,encoding="utf-8").read()
a="""        for i in 0..64 {
            let bs1 = v[4]"""
b="""        for (wi, ki) in w.iter().zip(self.t.k.iter()) {
            let bs1 = v[4]"""
assert a in s
s=s.replace(a,b)
a2=".wrapping_add(self.t.k[i]).wrapping_add(w[i]);"
assert a2 in s
s=s.replace(a2,".wrapping_add(*ki).wrapping_add(*wi);")
a3="""        assert_eq!(w.start, vec![0, 2, 3, 5]);
        assert_eq!(w.upper, vec![5, 1, 9, 5]);"""
assert a3 in s
s=s.replace(a3,"""        // Row 3 alone overfills its window, so the empty row 4 closes it, as in allpairs' admit.
        assert_eq!(w.start, vec![0, 2, 3, 4]);
        assert_eq!(w.upper, vec![5, 1, 9, 5]);""")
open(p,"w",encoding="utf-8",newline="\n").write(s)
