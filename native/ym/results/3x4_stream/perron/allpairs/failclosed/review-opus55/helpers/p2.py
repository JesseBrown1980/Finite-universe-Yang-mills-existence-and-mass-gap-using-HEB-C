p="C:/tmp/opus55/allpairs-review-20261103/fuzz/harness_tail.rs"
s=open(p,encoding="utf-8").read()
a="""                        if truth.structure_clean {
                            let want3 = (truth.mismatch, truth.lonely_lower, truth.lonely_upper);"""
b="""                        if truth.not_ascending == 0 {
                            let want3 = (truth.mismatch, truth.lonely_lower, truth.lonely_upper);"""
assert a in s; s=s.replace(a,b)
a="""        match rng.below(18) {
            0 => set(f, "n", "0".into()),"""
b="""        match rng.below(19) {
            18 => {
                set(f, "n", "0".into());
                f.retain(|e| e.0 != "entries" && e.0 != "nl");
            }
            0 => set(f, "n", "0".into()),"""
assert a in s; s=s.replace(a,b)
s=s.replace("disagree_counters_on_clean_rows={}|cap_variant_counters_on_dirty_rows={}|masked_unpaired_on_dirty_rows={}","disagree_counters_on_ascending_rows={}|cap_variant_counters_on_non_ascending_rows={}|masked_unpaired_on_non_ascending_rows={}")
s=s.replace("""                // Counters. Exact when the rows are clean. Across caps they must agree whenever the rows are clean.""","""                // Counters. They must be exact, at both caps, whenever every row's columns ascend strictly.""")
open(p,"w",encoding="utf-8",newline="\n").write(s)
