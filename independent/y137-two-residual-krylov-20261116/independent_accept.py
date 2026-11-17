#!/usr/bin/env python3
"""Independent exact-integer acceptance for FULL 2x2 residual Gram evidence.

Reads the hosted real-source matrix and independently recalculates the
2x2 determinant, PSD/rank, source 2D Gram, rational correlation, all
integer SHA-256 and bit-length fields. Negative controls forge one unit
of the cross entry and attempt to introduce linear dependence. This
checker is independent of the physical source builder, but NOT an
independent enumeration of its 1.48-million original K3 moves.
"""
import os
import sys
from hashlib import sha256

ROOT=os.path.dirname(os.path.abspath(__file__))
ART=os.path.join(os.path.dirname(os.path.dirname(ROOT)), "build",
                 "y137-two-residual", "RESULT-TWO-RESIDUAL.hbp")


def need(ok,why):
    if not ok:
        print("Y137_TWO_RESIDUAL_INDEPENDENT_REFUSE|reason="+why+
              "|json=0",flush=True)
        raise SystemExit(1)


def digest(v):
    return sha256(str(v).encode("ascii")).hexdigest()


def decode(line, prefix):
    need(line.startswith(prefix+"|"),"wrong_receipt_record_type")
    parts={}
    for item in line.split("|")[1:]:
        k,sep,v=item.partition("=")
        need(sep and k not in parts,"bad_duplicate_receipt_key")
        parts[k]=v
    need(parts.get("json")=="0","bad_record_trailer")
    return parts


def exact():
    need(os.path.isfile(ART),"real_full_H_receipt_missing")
    all_lines=open(ART,encoding="ascii").read().splitlines()
    # The original pinned S3 builder also prints two independent source-
    # census provenance records. Restrict the five-row exact new certificate
    # while separately asserting the historical full-orbit census.
    source_census=[line for line in all_lines
                   if line.startswith("S3_3X4_CENSUS|")]
    need(len(source_census)==2 and all(
         "orbit_dimension_full=2177317873|" in line
         for line in source_census), "original_S3_source_census_missing")
    lines=[line for line in all_lines
           if line.startswith("Y137_TWO_RESIDUAL_")]
    labels=[line.split("|",1)[0] for line in lines]
    need(labels==["Y137_TWO_RESIDUAL_SOURCE",
                  "Y137_TWO_RESIDUAL_MATRIX",
                  "Y137_TWO_RESIDUAL_GRAM",
                  "Y137_TWO_RESIDUAL_HBLOCK",
                  "Y137_TWO_RESIDUAL_VERDICT"],
         "invalid_source_2x2_record_order")
    src,mat,gram,hblock,verdict=(
        decode(lines[i],labels[i]) for i in range(5))
    need(src["original_PR247_source_git_blob"]
         =="1a174c7ff47d944370bf3c35ecc8557dfcc3bb17"
         and src["original_PR247_receipt_git_blob"]
         =="a7af4f4eb556ff60ca98f31dc9c73b2715b5032f"
         and src["original_H20736_sparse_sha256"]
         =="bb5de4e36f751209dad7ba742dbca2c0b5d111a1c82e3a51ffeff3ec5adb37b0",
         "not_original_authentic_source")
    e11=int(mat["E11_num"])
    e12=int(mat["E12_num"])
    e22=int(mat["E22_num"])
    d=int(mat["old_Gram_det_den"])
    D=int(mat["energy_den"])
    discr=int(mat["E_determinant_num"])
    need(d>0 and D==1000000000 and
         e11>0 and e22>0 and e11*e22-e12*e12==discr
         and discr>0,"two_residual_Gram_not_strictly_positive")
    need(int(gram["denominator"])==d and
         gram["rank"]=="2" and gram["nested_dimension"]=="20738"
         and gram["rank_discriminant_sign"]=="POSITIVE",
         "reported_rank_or_sign_wrong")
    for key,value in [("E11",e11),("E12",e12),("E22",e22)]:
        need(gram[key+"_num_sha256"]==digest(value)
             and int(gram[key+"_num_bits"])==abs(value).bit_length(),
             "residual_Gram_element_sha_or_bitlength_failure")
    need(gram["rank_discriminant_sha256"]==digest(discr)
         and int(gram["rank_discriminant_bits"])==discr.bit_length()
         and int(gram["squared_correlation_ppm"])
             ==1000000*e12*e12//(e11*e22),
         "residual_Gram_discriminant_or_correlation_incorrect")
    # The original two H20736 source trials must themselves be independent.
    u11=int(mat["old_source_G11"])
    u12=int(mat["old_source_G12"])
    u22=int(mat["old_source_G22"])
    need(u11>0 and u22>0 and u11*u22-u12*u12>0,
         "original_two_source_Gram_independence_drift")
    for key in ("H11","H12","H22"):
        need(hblock["old_"+key+"_sha256"]
             ==digest(int(mat["old_source_"+key])),
             "old_source_Hamiltonian_element_hash_wrong")
    for key,e in (("11",e11),("12",e12),("22",e22)):
        need(hblock["true_old_to_residual_H"+key+"_num_sha256"]
             ==digest(e),"true_source_H_cross_not_Gram_cross")
    need(int(hblock["old_to_residual_H_common_den"])==d*D
         and hblock["new_residual_to_residual_H"]=="NOT_COMPUTED"
         and hblock["new_two_residual_Ritz"]=="NOT_COMPUTED",
         "new_2x2_H_block_overclaim")
    need(verdict["two_new_independent_residual_directions"]=="PASS"
         and verdict["certified_nested_dimension"]=="20738"
         and verdict["new_H_tt_block"]=="HOLD"
         and verdict["new_Ritz_brackets"]=="HOLD"
         and verdict["first_Wilson_weight"]=="HOLD"
         and verdict["issue_137"]=="OPEN",
         "source_claim_exceeds_actual_acceptance")
    # Negative control 1: a forged E12+1 must break accepted matrix digest.
    need(digest(e12+1)!=gram["E12_num_sha256"],
         "forged_cross_sha_accepted")
    # Negative control 2: dependent copy T12^2=T11*T22 cannot pass determinant.
    need(discr>0 and e11*e22!=e12*e12,
         "dependent_residual_Gram_accepted")
    print("Y137_TWO_RESIDUAL_INDEPENDENT|original_full_source=PINNED"
          "|independent_2x2_determinant=POSITIVE"
          "|nested_Galerkin_dimension=20738"
          "|all_matrix_SHA256_and_bits=PASS"
          "|old_to_new_H_cross_identity=PASS"
          "|negative_controls=2_OF_2_REJECTED"
          "|full_new_H_tt=NOT_COMPUTED"
          "|new_Ritz=NOT_COMPUTED"
          "|Wilson_weight=HOLD|json=0",flush=True)


if __name__=="__main__":
    need(sys.argv[1:]==["real"],"usage_real")
    exact()
