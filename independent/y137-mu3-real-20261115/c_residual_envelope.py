#!/usr/bin/env python3
"""#137 independent exact source envelope for signed physical V1=X R.

Do not infer actual V1 entries or third moment. Establish a strict sufficient
global source bound from exact *full* original R_K3 and R_Q4 magnitudes:
  |R| < 2^78 and max_i (|D_i|+72b)<2^39 => |V1|<2^117.
Both historical frozen sample U/G source fingerprints are verified when
src.build_inputs() runs. Q5 positive V1 is independently <2^112 by the
accepted packed 82-bit width and b<2^30.

No geometry, source content, or energies are changed.
"""
import hashlib
import os
import sys

ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
PREV_ARGV=sys.argv[:]
sys.argv=sys.argv[:1]
import mu1_shard as src
sys.argv=PREV_ARGV

Z=(69909875505,69949729820)
B=1000000000
SUPPORT=(155378,1985218,18598040)
MR=1<<78
MV=1<<117

def require(ok,why):
    if not ok:
        print("Y137_C_R_ENVELOPE_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)

def toy():
    n=sum(SUPPORT)
    require(n==20738636 and n<1<<25,"support_count")
    for z in Z:
        maxD=max(abs(B*72-z),abs(B*(72+9*36)-z))
        require(maxD+72*B<1<<39,"original_operator_row_bound")
    require(78+39==117 and 117+156+25+6==304,
            "conservative_integer_exponents")
    require(B<1<<30 and 82+30==112,"Q5_physical_lane_width")
    print("Y137_C_R_ENVELOPE_TOY|supported_total=20738636"+
          "|row_operator_limit_bits=39|R_limit_bits=78"+
          "|V1_sufficient_limit_bits=117|partial_sum_limit_bits=304"+
          "|Q5_physical_bound_bits=112|real_source_max=NOT_COMPUTED"+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0")

def real():
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    require(ball["n"]==SUPPORT[0] and ball["nf"]==SUPPORT[1] and
            len(items)==2 and len(ex["code4"])==SUPPORT[1],
            "original_K3_Q4_count")
    require(tuple(row[0] for row,_,_,_ in items)==Z,
            "frozen_two_energy_numerators")
    dmax=[]
    for z in Z:
        a=max(abs(B*72-z),abs(B*396-z))+72*B
        require(a<1<<39,"operator_row_larger_than_2pow39")
        dmax.append(a)
    for index,(row,record,rs,positive_q4) in enumerate(items):
        require(len(rs)==SUPPORT[0] and len(positive_q4)==SUPPORT[1],
                "frozen_R_support_count")
        digest=hashlib.sha256()
        inner_max=0
        q4_max=0
        neg_inner=0
        neg_q4=0
        for v in rs:
            require(len(v)==8,"inner_R_width")
            for n in v:
                inner_max=max(inner_max,abs(n))
                neg_inner+=int(n<0)
                digest.update(str(n).encode("ascii")+b",")
            digest.update(b";")
        for f in range(SUPPORT[1]):
            digits=src.unpack(positive_q4[f],width,mask)
            require(len(digits)==8,"Q4_R_packed_source_width")
            for p in digits:
                require(p>=0,"Q4_R_positive_record_sign")
                q4_max=max(q4_max,p)
                neg_q4+=int(p>0)  # true source has R_Q4=-positive p
                digest.update(str(-p).encode("ascii")+b",")
            digest.update(b";")
        actual_max=max(inner_max,q4_max)
        # This sufficient test is a genuine full support gate, rather than
        # an extrapolation from the 216 signed source preflight rows.
        source_limit=actual_max<MR
        inferred_upper=actual_max*dmax[index]
        need_v1=inferred_upper<MV
        require(source_limit==need_v1 or not source_limit,
                "inconsistent_sufficient_bound")
        label="PASS" if source_limit and need_v1 else "HOLD_SHARPER_SOURCE_BOUND"
        print("Y137_C_R_ENVELOPE|sample_num="+str(row[0])+
              "|K3_rows="+str(SUPPORT[0])+"|Q4_rows="+str(SUPPORT[1])+
              "|K3_max_abs_R="+str(inner_max)+
              "|Q4_max_abs_R="+str(q4_max)+
              "|max_abs_R="+str(actual_max)+
              "|max_R_bit_length="+str(actual_max.bit_length())+
              "|actual_operator_row_abs_upper="+str(dmax[index])+
              "|derived_V1_abs_upper="+str(inferred_upper)+
              "|derived_V1_bound_bits="+str(inferred_upper.bit_length())+
              "|K3_negative_R_entries="+str(neg_inner)+
              "|Q4_negative_R_entries="+str(neg_q4)+
              "|full_signed_R_sha256="+digest.hexdigest()+
              "|original_U_sha256="+str(row[4])+
              "|original_G_sha256="+str(row[5])+
              "|authentic_full_R_K3_Q4=REBUILT"+
              "|V1_under_2pow117="+label+
              "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",
              flush=True)
        require(source_limit and need_v1,
                "global_signed_residual_bound_requires_sharper_certificate")
    print("Y137_C_R_ENVELOPE_VERDICT|sample_count=2"+
          "|all_K3_Q4_residuals=EXACT"+
          "|complete_source_rows=2140596"+
          "|Q5_source_82bit_verified_by_B1_B2=1"+
          "|global_physical_V1_under_2pow117=PROVED_FROM_R_ENVELOPE"+
          "|row_and_pair_absolute_sum_under_2pow304=CONDITIONAL_GRAPH_JOIN"+
          "|full_physical_V1_spools=PENDING"+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",flush=True)

def main(args):
    if args==["toy"]:
        toy()
    elif args==["real"]:
        real()
    else:
        raise SystemExit("usage: c_residual_envelope.py toy|real")

if __name__=="__main__":
    main(sys.argv[1:])
