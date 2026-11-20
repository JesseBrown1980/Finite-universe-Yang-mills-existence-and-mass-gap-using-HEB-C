#!/usr/bin/env python3
"""Controls for exact conditional projector checker; synthetic only."""
from fractions import Fraction as F
import copy
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_projector as c

def fixture():
    L=[[F(-1 if i==0 else 2) if i==j else F(0) for j in range(8)] for i in range(8)]
    U=[[L[i][j]+(F(1,10000) if i==j else 0) for j in range(8)] for i in range(8)]
    return dict(weights=[1]*8,schur_lower=L,schur_upper=U,
        witness=[1]+[0]*7,sample_energy="0",gamma="100",
        upper_energy="0",window_drift="0",coupling_norm_sq_upper="72",
        envelope_norm_upper="1/1000",projected_residual_upper="1/1000",
        compressed_singular_lower="1",target_sine_upper="1/100")

def reject(a):
    try:c.verify(a)
    except (AssertionError,ValueError,KeyError,ZeroDivisionError,IndexError):return
    raise AssertionError("negative control incorrectly accepted")

def main():
    a=fixture()
    c.need(c.verify(a)["status"]=="CONDITIONAL_NUMERICAL_PASS", "synthetic_positive_control")
    bad=[]
    x=copy.deepcopy(a);x["envelope_norm_upper"]="0";bad.append(x)
    x=copy.deepcopy(a);x["projected_residual_upper"]="0";bad.append(x)
    x=copy.deepcopy(a);x["compressed_singular_lower"]="3";bad.append(x)
    x=copy.deepcopy(a);x["target_sine_upper"]="1/10000000";bad.append(x)
    x=copy.deepcopy(a);x["weights"][0]=0;bad.append(x)
    x=copy.deepcopy(a);x["schur_upper"][0][0]=F(-3);bad.append(x)
    x=copy.deepcopy(a);x["witness"]=[0]*8;bad.append(x)
    x=copy.deepcopy(a);x["gamma"]="0";bad.append(x)
    for x in bad:reject(x)
    print("Y137_PROJECTOR_TOY|synthetic=PASS|negative_controls=8/8_REJECTED|original_E1_E2=NOT_RUN|first_wilson=FORMAL_HOLD")
if __name__=="__main__":main()
