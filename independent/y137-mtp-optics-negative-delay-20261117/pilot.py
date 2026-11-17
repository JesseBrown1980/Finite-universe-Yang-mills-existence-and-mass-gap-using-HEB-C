#!/usr/bin/env python3
"""Finite causal MTP correction optics pilot; integer arithmetic only.

Three checked stages share a frozen source: MTP1 local response, MTP3
past/current extrapolation, MTP27 passive gain normalization. This is an
explicit hypothetical correction rule, not a learned network or optical model.
"""
from hashlib import sha256
from math import gcd

PATH_STEPS = 6
INPUT_CENTER = 40
WINDOW = 112
WIDTHS = (3, 8, 16)
DEPTHS = (1, 2, 4)


def emit(tag, **items):
    print(tag + '|' + '|'.join(str(k) + '=' + str(v) for k, v in items.items()) + '|json=0')


def h(x):
    return sha256(repr(x).encode('ascii')).hexdigest()


def reduced(n, d):
    assert d > 0
    g = gcd(abs(n), d)
    return (n // g, d // g)


def ratstr(n, d):
    p, q = reduced(n, d)
    return str(p) + '/' + str(q)


def source(width):
    assert width in WIDTHS
    return tuple(max(0, width-abs(t-INPUT_CENTER)) for t in range(WINDOW))


def respond(x, od, corrected):
    # All read only the source x[t-PATH_STEPS] or its predecessor.
    assert od in DEPTHS
    if corrected:
        # MTP3 extrapolates its current source from local last-frame record;
        # MTP27 enforces a norm-nonincreasing passivity bound.
        current = 2 * od + 1
        prior = -od
        denom = 3 * od + 1
    else:
        # Ordinary local response, no higher-shell extrapolation.
        current = 2
        prior = 1
        denom = 3
    assert abs(current) + abs(prior) <= denom
    result = []
    for tick in range(WINDOW):
        idx = tick - PATH_STEPS
        now = x[idx] if 0 <= idx < len(x) else 0
        before = x[idx-1] if 0 <= idx-1 < len(x) else 0
        result.append(current * now + prior * before)
    return tuple(result), denom, current, prior


def centroid_relative(x, location):
    total = sum(x)
    assert total > 0
    delta = sum((i-location)*x[i] for i in range(len(x)))
    return reduced(delta, total)


def intensity_centroid(y, location):
    weights = tuple(v*v for v in y)
    return centroid_relative(weights, location)


def first_nonzero(x):
    return next(i for i, v in enumerate(x) if v != 0)


def paper_phase_formula_sign():
    # Uploaded February 2025 paper: phi=arctan((omega-omega0)/Gamma).
    # For positive Gamma: -d(phi)/d(omega) at omega=omega0 is -1/Gamma.
    gamma = 3
    return ratstr(-1, gamma)


def weak_value_exact():
    # Two-state pre/post states, each normalized (4,3)/5 and (4,-3)/5.
    pre = (4, 3)
    post = (4, -3)
    assert sum(v*v for v in pre) == 25
    assert sum(v*v for v in post) == 25
    overlap = sum(pre[i]*post[i] for i in range(2))
    projected = pre[1]*post[1]
    assert overlap == 7 and projected == -9
    assert reduced(projected, overlap) == (-9, 7)
    return projected, overlap


def main():
    assert paper_phase_formula_sign() == '-1/3'
    assert weak_value_exact() == (-9, 7)
    emit('MTP_OPTICS_REFERENCE',
         uploaded_pdf='Nonlinear_Temporal_Dynamics_Feb_2025',
         paper_resonant_phase_law='ARCTAN_DETUNING_OVER_LINEWIDTH',
         paper_sign_convention='NEGATIVE_PHASE_DERIVATIVE',
         paper_center_delay_for_gamma_3=paper_phase_formula_sign(),
         paper_prediction_positive_wide_time='NOT_DERIVED_BY_SINGLE_SIGN_LORENTZIAN',
         PRL2026='NEGATIVE_WEAK_VALUE_NARROW_AND_POSITIVE_BROAD',
         measured_narrow_weak_value='-82/100_PLUS_MINUS_31/100_TAU0',
         measured_broad_weak_value='54/100_PLUS_MINUS_28/100_TAU0',
         calibration_to_simulated_slice='NONE',status='SOURCE_GROUNDED')
    emit('MTP_OPTICS_CONTROL',
         pre_post_quantum_weak_value='-9/7',
         pre_and_post_state_norm='1',
         pre_post_weak_value_requires='EXPLICIT_POSTSELECTION',
         baseline_filter_group_delay='1/3',
         generated_by_MTP='NO',status='PASS')
    output = []
    all_narrow_negative = 0
    broad_positive = 0
    earliest_count = 0
    for od in DEPTHS:
        assert od >= 1
        for width in WIDTHS:
            x = source(width)
            frozen = h(('global-frame', x, od, width, PATH_STEPS))
            y0, den0, c0, p0 = respond(x, od, False)
            y, den, current, prior = respond(x, od, True)
            assert den == abs(current) + abs(prior)
            assert (c0, p0, den0) == (2, 1, 3)
            assert frozen == h(('global-frame', x, od, width, PATH_STEPS))
            assert sum(v*v for v in y) <= sum(v*v for v in x) * den * den
            assert sum(v*v for v in y0) <= sum(v*v for v in x) * den0 * den0
            first_input = first_nonzero(x)
            first_output = first_nonzero(y)
            first_baseline = first_nonzero(y0)
            assert first_output == first_baseline == first_input + PATH_STEPS
            earliest_count += 1
            # Signed field-amplitude centroid, not photon-detection weak value.
            r0 = centroid_relative(y0, INPUT_CENTER + PATH_STEPS)
            r1 = centroid_relative(y, INPUT_CENTER + PATH_STEPS)
            iq = intensity_centroid(y, INPUT_CENTER + PATH_STEPS)
            assert r0 == (1, 3)
            assert r1 == reduced(-od, od + 1)
            assert r1[0] < 0
            # Exact baseband analytic group delay from the FIR moment.
            assert reduced(prior, current+prior) == r1
            # The high-frequency (Nyquist) group delay has opposite sign.
            nyquist = reduced(-prior, current-prior)
            assert nyquist[0] > 0
            if width == 3:
                all_narrow_negative += 1
            if width == 16 and r1[0] > 0:
                broad_positive += 1
            # MTP1 uses last-frame local signal as its forecast; the higher
            # shells detect its disagreement with the newly arrived value.
            mismatches = sum(int(x[i] != (x[i-1] if i else 0))
                             for i in range(len(x)))
            assert mismatches > 0
            key = (od, width, x, y0, y)
            emit('MTP_OPTICS_RESULT',optical_density_token=od,
                 pulse_half_width_slices=width,path_length_cells=PATH_STEPS,
                 input_first_tick=first_input,output_first_tick=first_output,
                 MTP1_stale_forecast_mismatches=mismatches,
                 MTP3_revision_receipts=mismatches,
                 MTP27_passive_gain_gate='PASS',
                 baseline_delay=ratstr(*r0),
                 MTP_corrected_group_delay=ratstr(*r1),
                 MTP_corrected_intensity_centroid=ratstr(*iq),
                 Nyquist_group_delay=ratstr(*nyquist),
                 phase_at_zero_negative='YES',
                 normalized_passive='YES',
                 no_output_before_local_arrival='PASS',
                 source_sha256=frozen,
                 result_sha256=h(key),status='PASS')
            output.append((od,width,r0,r1,iq,nyquist))
    # Correction is causal but its simple low-frequency phase sign does NOT
    # reproduce the measured positive broadband weak value.
    assert all_narrow_negative == len(DEPTHS)
    assert broad_positive == 0
    # An unannounced impulse at time 55 cannot influence any output before
    # its *causal* transit time through six link cells.
    impulse = tuple(int(t == 55) for t in range(WINDOW))
    for od in DEPTHS:
        yy, _, _, _ = respond(impulse, od, True)
        assert all(v == 0 for v in yy[:55+PATH_STEPS])
        assert first_nonzero(yy) == 55+PATH_STEPS
    emit('MTP_OPTICS_NEGATIVES',
         phase_sign_narrow='NEGATIVE',
         measured_positive_broad_weak_value_fit='FAIL',
         shared_quantum_postselection_simulated='NO',
         coherent_atom_probe_phase_shift_simulated='NO',
         recorded_past_frames_mutated='NO',
         faster_than_light_message='NO',
         naive_claim_negative_time='REJECTED',status='PASS')
    emit('MTP_OPTICS_FINAL',all_width_depth_cases=len(output),
         first_arrival_causal_checks=earliest_count,
         strict_global_frame_order='PASS',
         MTP1_MTP3_MTP27='DEFINED_DETERMINISTIC_ADAPTERS',
         MTP_corrected_negative_baseband_delay='PASS',
         full_PRL2026_observable_match='HOLD',
         light_matter_quantum_model='NOT_IMPLEMENTED',
         original_S3_Wilson_first_weight='HOLD',
         output_sha256=h(tuple(output)),
         status='EXACT_FIR_PILOT_PASS')

if __name__ == '__main__':
    main()
