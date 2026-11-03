p="C:/tmp/opus55/allpairs-review-20261103/attack/attacks.py"
s=open(p,encoding="utf-8").read()
a='''{"exit": 1, "verdict": "FAIL"}, reader_verdict="None")'''
assert a in s; s=s.replace(a,'''{"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")''')
a='''{"exit": 0, "verdict": "PASS"}, reader_verdict="FAIL", note="reader_counts_raw_tail_only_prints_it_verdict_may_pass")'''
assert a in s; s=s.replace(a,'''{"exit": 0, "verdict": "PASS"}, reader_verdict="PASS", note="reader_prints_the_raw_tail_count_and_does_not_gate_on_it")''')
open(p,"w",encoding="utf-8",newline="\n").write(s)
