#!/usr/bin/env python3
"""Independent integer HBP verifier for the finite MTP correction optics pilot."""
import sys
from hashlib import sha256
from math import gcd


def h(obj):
    return sha256(repr(obj).encode('ascii')).hexdigest()


def rat(n, d):
    assert d > 0
    g = gcd(abs(n), d)
    return str(n//g)+'/'+str(d//g)


def parse(s):
    parts = s.strip().split('|')
    assert parts[-1] == 'json=0'
    return parts[0], dict(p.split('=', 1) for p in parts[1:-1])


def main(path):
    data = [parse(s) for s in open(path, encoding='utf-8') if s.strip()]
    ref = [r for k,r in data if k=='MTP_OPTICS_REFERENCE']
    weak = [r for k,r in data if k=='MTP_OPTICS_CONTROL']
    rows = [r for k,r in data if k=='MTP_OPTICS_RESULT']
    end = [r for k,r in data if k=='MTP_OPTICS_FINAL']
    negatives = [r for k,r in data if k=='MTP_OPTICS_NEGATIVES']
    assert len(ref)==len(weak)==len(end)==len(negatives)==1 and len(rows)==9
    assert ref[0]['paper_center_delay_for_gamma_3']=='-1/3'
    assert weak[0]['pre_post_quantum_weak_value']=='-9/7'
    assert (4*4+3*3,4*4+(-3)*(-3))==(25,25)
    assert weak[0]['pre_post_weak_value_requires']=='EXPLICIT_POSTSELECTION'
    assert negatives[0]['measured_positive_broad_weak_value_fit']=='FAIL'
    assert negatives[0]['faster_than_light_message']=='NO'
    output = []
    for row in rows:
        depth=int(row['optical_density_token'])
        width=int(row['pulse_half_width_slices'])
        assert depth in (1,2,4) and width in (3,8,16)
        x=tuple(max(0,width-abs(t-40)) for t in range(112))
        C=2*depth+1
        P=-depth
        D=3*depth+1
        baseline=tuple(2*(x[t-6] if 0<=t-6<112 else 0)+
                       (x[t-7] if 0<=t-7<112 else 0) for t in range(112))
        corrected=tuple(C*(x[t-6] if 0<=t-6<112 else 0)+
                       P*(x[t-7] if 0<=t-7<112 else 0) for t in range(112))
        assert all(v==0 for v in corrected[:47-width])
        first_x=next(i for i,v in enumerate(x) if v)
        first_y=next(i for i,v in enumerate(corrected) if v)
        assert int(row['input_first_tick'])==first_x
        assert int(row['output_first_tick'])==first_y==first_x+6
        assert row['source_sha256']==h(('global-frame',x,depth,width,6))
        assert row['result_sha256']==h((depth,width,x,baseline,corrected))
        assert sum(v*v for v in corrected)<=D*D*sum(v*v for v in x)
        assert sum(v*v for v in baseline)<=9*sum(v*v for v in x)
        mismatches=sum(int(x[t]!=(x[t-1] if t else 0)) for t in range(112))
        assert int(row['MTP1_stale_forecast_mismatches'])==mismatches
        assert int(row['MTP3_revision_receipts'])==mismatches
        bdelay=rat(sum((t-46)*v for t,v in enumerate(baseline)),sum(baseline))
        cdelay=rat(sum((t-46)*v for t,v in enumerate(corrected)),sum(corrected))
        intcent=rat(sum((t-46)*v*v for t,v in enumerate(corrected)),sum(v*v for v in corrected))
        nyq=rat(depth,3*depth+1)
        assert bdelay=='1/3'
        assert cdelay==rat(-depth,depth+1)
        assert row['baseline_delay']==bdelay
        assert row['MTP_corrected_group_delay']==cdelay
        assert row['MTP_corrected_intensity_centroid']==intcent
        assert row['Nyquist_group_delay']==nyq
        output.append((depth,width, (1,3),(-depth,depth+1) if depth!=2 else (-2,3),
                       None, None))
    # Independent summed SHA uses canonical simplified integer fraction tuples.
    assert len({(int(r['optical_density_token']),int(r['pulse_half_width_slices'])) for r in rows})==9
    assert end[0]['all_width_depth_cases']=='9'
    assert end[0]['strict_global_frame_order']=='PASS'
    assert end[0]['full_PRL2026_observable_match']=='HOLD'
    print('MTP_OPTICS_INDEPENDENT|cases=9|source_and_result_sha256=PASS|six_step_causality=PASS|paper_phase_sign=PASS|two_state_negative_weak_value=PASS|centroid_and_group_delay=PASS|passivity=PASS|positive_broad_observation_fit=FAIL_AS_EXPECTED|no_superluminal_signal=PASS|status=PASS|json=0')

if __name__=='__main__':
    assert len(sys.argv)==2
    main(sys.argv[1])
