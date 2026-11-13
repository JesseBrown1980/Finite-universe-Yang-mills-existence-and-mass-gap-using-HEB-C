import io
T="C:/tmp/opus55/floor-v2/"
def rd(n): return io.open(T+n,encoding="utf-8",newline="").read().replace("\r\n","\n")
def wr(n,s): io.open(T+n,"w",encoding="utf-8",newline="\n").write(s)
s=rd("gen_notes.py")
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:70]); s=s.replace(a,b)
rep(r'''121 rows. Rows 110-121 disclose the review and everything run\\n"')''', r'''122 rows. Rows 110-122 disclose the review and everything run\\n"')''')
rep(r''''"`review-v2/MODIFIED-ROWS-V1-V2.hbp` account for the 11 modified rows field by field, row 121 puts the two readings of\\n"\n'
 '"rows 006 and 011 at 2 GB before the reviewer.\\n\\n"')''',
 r''''"`review-v2/MODIFIED-ROWS-V1-V2.hbp` account for the 11 modified rows field by field, row 121 puts the two readings of\\n"\n'
 '"rows 006 and 011 at 2 GB before the reviewer, and row 122 records the reviewer\'s ruling on them: a process that completes\\n"\n'
 '"at or over 2 GiB (2,097,152 KiB) gives CERTIFICATE=FAIL with reason RESOURCE_LIMIT_EXCEEDED and no fallback; a timeout or\\n"\n'
 '"a crash may trigger fallback only when the applicable REQUIRED gates have not failed. The launcher runs private, hashed,\\n"\n'
 '"read-only copies of the gate driver, the verifier, the peak wrapper and the evaluator, and a certificate is accepted only\\n"\n'
 '"with the record of a verifier invocation that exited 0 (row 122). `review-v2/rehearsal-v2b/` holds the swap of the gate\\n"\n'
 '"driver as found against the first version 2 commit (X1) and its rejection by this launcher (Y1, Y1b, P1).\\n\\n"')''')
rep(r'''record rows 119-121):\\n"''', r'''record rows 119-122):\\n"''')
rep(r'''"  before every invocation, the evaluator hashes the verifier, the gate driver and the peak wrapper at every step and runs a closing pin check;\\n"''',
 r'''"  before every invocation, the evaluator hashes the verifier, the gate driver and the peak wrapper at every step and runs a closing pin check;\\n"
"  the launcher copies the gate driver, the verifier, the peak wrapper, the evaluator, the record and the binary into a fresh private directory, hashes the\\n"
"  copies against the frozen values and runs only the copies; a certificate needs the record of a verifier invocation with exit 0; a completed process at or\\n"
"  over 2097152 kB gives CERTIFICATE=FAIL, certificate_reason=RESOURCE_LIMIT_EXCEEDED, and no fallback (row 122);\\n"''')
rep(r'''", 121 rows. "')''', r'''", 122 rows. "')''')
rep(r'''record rows 119-121, review-v2/).''', r'''record rows 119-122, review-v2/).''')
wr("gen_notes.py",s)
s=rd("final_b.sh")
rep('NAMES="A1 A2 A3 B1 B2 C1 C2 C3 C4 C5 V1 V2 V3 N9 N13 BA BAm BU BUp E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 LK1 LK2 G1 G2 G3 G4 G5 G6 G7 G8 EV1 EV2 D1"',
    'NAMES="A1 A2 A3 B1 B2 C1 C2 C3 C4 C5 V1 V2 V3 N9 N13 BA BAm BU BUp E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 E10 E11 LK1 LK2 MG G1 G2 G3 G4 G5 G6 G7 G8 EV0 EV1 EV2 EV3 EV4 EV5 X0 X1 X1b Y1 Y1b P1 R1 R2 R3 D1 DX D3"')
rep('for n in $NAMES; do f=$W/rehb/$n/FLOOR-RUN-RECEIPT.hbp; [ -f $f ] && ! grep -q "$ST1" $f',
    'for n in $NAMES; do case $n in X*) continue;; esac; f=$W/rehb/$n/FLOOR-RUN-RECEIPT.hbp; [ -f $f ] && ! grep -q "$ST1" $f')
rep('$T/pins2.sh $T/b1.sh $T/final_b.sh $P/review-v2/generator/', '$T/pins2.sh $T/b1.sh $T/final_b.sh $T/patch_eval.py $T/upd_tail.py $T/upd_reh.py $T/upd_sum.py $T/upd_notes.py $P/review-v2/generator/')
wr("final_b.sh",s)
print("ok")
