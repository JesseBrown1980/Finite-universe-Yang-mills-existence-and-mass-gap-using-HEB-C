#!/usr/bin/env python3
"""Independent Chebyshev factor audit by 2x2 integer matrix exponentiation.

Does not import the source verifier, use its polynomial coefficient builder,
or build any Q graph. The acceptance scope is scalar factor verification
against pinned whole-Q operator endpoints, not an independent YM source proof.
"""
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
B=1000000000
UNIT=1000000000000
EXPECTED=(
    (69909875505,7905087124,1056945906,639127784,408485),
    (69949729820,7940519358,1063411525,643298996,413834),
)
SOURCE_SHA="91bd1e80cbfcfb76198966aa177d097ecfbe8143"
CENTRE_SHA="3a147c8a750dae490882702307f8ec795a3c1f51"
TRANSFER_SHA="a03d3e6ab5d9340518443e7d1b66c1ca25c2214d"


def need(t,why):
    if not t:
        raise SystemExit("Y137_CHEB_AUDIT_REFUSE|reason="+why+"|json=0")


def blobsha(data):
    return hashlib.sha1(("blob "+str(len(data))+"\0").encode()+data).hexdigest()


def matmul(a,b):
    return ((a[0][0]*b[0][0]+a[0][1]*b[1][0],
             a[0][0]*b[0][1]+a[0][1]*b[1][1]),
            (a[1][0]*b[0][0]+a[1][1]*b[1][0],
             a[1][0]*b[0][1]+a[1][1]*b[1][1]))


def matpow(a,n):
    need(n>=0,"bad_matrix_power")
    p=((1,0),(0,1))
    while n:
        if n%2:
            p=matmul(p,a)
        a=matmul(a,a)
        n//=2
    return p


def integer_power(a,n):
    need(n>=0,"bad_integer_power")
    v=1
    while n:
        if n%2:
            v*=a
        a*=a
        n//=2
    return v


def upper(n,d):
    need(n>=0 and d>0,"invalid_quotient")
    return (n+d-1)//d


def factor(g,h,n):
    need(0<g<h and n>=1,"uncertified_operator_interval")
    s=g+h
    d=h-g
    # Matrix-power representation of the Chebyshev normalizer recurrence;
    # logically separate from the source's polynomial-coefficient expansion.
    transition=((2*s,-d*d),(1,0))
    block=matpow(transition,n-1)
    k=block[0][0]*s+block[0][1]
    need(k>0,"nonpositive_chebyshev_denominator")
    numer=integer_power(d,n)
    return numer,k


def fields(line):
    f=line.split("|")
    d={}
    for entry in f[1:]:
        need("=" in entry,"malformed_receipt_row")
        k,v=entry.split("=",1)
        need(k not in d,"duplicate_receipt_key")
        d[k]=v
    return f[0],d


def inspect(records,expected):
    points=[x for x in records if x[0]=="Y137_CHEB_POINT"]
    need(len(points)==2,"expected_two_samples")
    for i,(z,n11,n15,n16,g16) in enumerate(expected):
        got=points[i][1]
        need(int(got["sample_num"])==z,"sample_energy_changed")
        g=94068200000-z
        h=468000000000-z
        need(int(got["full_Q_lower_num"])==g and
             int(got["full_Q_upper_num"])==h,
             "spectral_interval_not_authorized")
        for n,want in ((11,n11),(15,n15),(16,n16)):
            v,k=factor(g,h,n)
            actual=upper(v*UNIT,k)
            need(actual==want and
                 int(got["degree"+str(n)+"_norm_ratio_ceil_per_trillion"])==want,
                 "norm_fraction_mismatch")
        v,k=factor(g,h,16)
        val=upper(v*v*UNIT,k*k)
        need(val==g16 and
             int(got["degree16_Gram_ratio_ceil_per_trillion"])==g16,
             "PSD_Gram_ratio_mismatch")
        need(1550*v<k and 1000*v<k,
             "not_a_strict_1550fold_contraction")
        need(got["corrected_Schur_matrix"]=="NOT_COMPUTED" and
             got["actual_first_Wilson_weight"]=="HOLD",
             "false_physical_conclusion")
    need(records[-1][0]=="Y137_CHEB_VERDICT" and
         records[-1][1]["actual_new_trial_Schur_or_Wilson"]=="NOT_COMPUTED" and
         records[-1][1]["issue_137"]=="OPEN","bad_theorem_scope")
    return len(points)


def main():
    for path,sha in (
        ("independent/finite_s3_3x4_r9_first_gap.py",SOURCE_SHA),
        ("independent/y137-centered-schur-transfer-20261113/RESULT-CENTERED-PROJECTOR.hbp",CENTRE_SHA),
        ("independent/y137-combined-W-transfer-20261113/RESULT-COMBINED-FULL-W.hbp",TRANSFER_SHA)):
        data=ROOT.joinpath(path).read_bytes()
        need(blobsha(data)==sha,"source_pin_"+path)
    data=HERE.joinpath("RESULT-CHEB.hbp").read_text(encoding="utf-8")
    rows=[fields(line) for line in data.splitlines() if line.strip()]
    need(len(rows)==5 and
         [x[0] for x in rows]==[
            "Y137_CHEB_FREEZE","Y137_CHEB_TOY",
            "Y137_CHEB_POINT","Y137_CHEB_POINT","Y137_CHEB_VERDICT"],
         "receipt_shape")
    count=inspect(rows,EXPECTED)
    changed=[(x[0],dict(x[1])) for x in rows]
    changed[2][1]["degree16_norm_ratio_ceil_per_trillion"]="639127785"
    caught=False
    try:
        inspect(changed,EXPECTED)
    except SystemExit:
        caught=True
    need(caught,"changed_ceiling_negative_control_not_rejected")
    need(not 1000*(468000000000-69909875505-
                    (94068200000-69909875505)) <
             factor(94068200000-69909875505,
                    468000000000-69909875505,1)[1],
         "incorrect_degree_one_claim_accepted")
    print("Y137_CHEB_INDEPENDENT_AUDIT|samples="+str(count)+
          "|method=2x2_integer_matrix_power_not_source_polynomial"+
          "|all_norm_and_Gram_ratios=PASS"+
          "|modified_ratio_negative_control=REJECTED"+
          "|actual_first_Wilson_weight=HOLD|json=0",flush=True)


if __name__=="__main__":
    main()
