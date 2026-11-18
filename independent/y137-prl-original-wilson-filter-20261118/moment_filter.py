#!/usr/bin/env python3
"""Original S3 Wilson low-pass moments: source-authenticated trial, not a true projector."""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, 'y137-direct-projector-moment-20261117'))
ARGS = sys.argv[:]
try:
    sys.argv = sys.argv[:1]
    import wilson_moment as stage_n
finally:
    sys.argv = ARGS

CAP = 468


def need(ok, msg):
    if not ok:
        print('Y137_PRL_FILTER_REFUSE|reason=' + msg + '|json=0', flush=True)
        raise SystemExit(1)


def emit(tag, **fields):
    print(tag + '|' + '|'.join(str(k) + '=' + str(v) for k, v in fields.items()) + '|json=0', flush=True)


def digest(value):
    return hashlib.sha256(str(value).encode('ascii')).hexdigest()


def checks(m0, m1, m2, cap):
    need(m0 > 0 and 0 <= m1 <= cap * m0 and m1 * m1 <= m0 * m2,
         'nonnegative_H_and_Cauchy')
    need(0 <= m2 <= cap * m1, 'H2_le_cap_H')
    t1 = cap * m0 - m1
    t2 = cap * cap * m0 - 2 * cap * m1 + m2
    need(0 <= t1 <= cap * m0, 'filtered_first_in_range')
    need(0 <= t2 <= cap * t1 and m0 * t2 >= t1 * t1,
         'filtered_second_in_range_and_Cauchy')
    return t1, t2


def toy():
    need(checks(1, 2, 5, 4) == (2, 5), 'toy_H2')
    try:
        checks(1, 2, 3, 4)
    except SystemExit:
        pass
    else:
        need(False, 'forged_H2_accepted')
    need(checks(1, 5, 25, 6) == (1, 1), 'dark_channel')
    emit('Y137_PRL_FILTER_TOY', physical_H2='PASS', tampered_moment='REJECTED',
         high_energy_dark_control='PASS', first_Wilson_weight='HOLD')


def original_H_action(ball, p, q):
    """Apply genuine source H through K3 and collect all shell-4 exterior output."""
    wf, wq, n = ball['wf'], ball['wq'], ball['n']
    need(len(p) == 8 and len(q) == n, 'source_support')
    hp = [72 * x for x in p]
    cross = [0] * 8
    hq = [0] * n
    for i in range(n):
        coupling = sum(ball['oc'][h] * q[ball['oj'][h]]
                       for h in range(ball['rs'][i], ball['rs'][i + 1]))
        c = ball['C'][i]
        if c is not None:
            coupling += sum(c[j] * p[j] for j in range(8))
            for j in range(8):
                cross[j] += wq[i] * c[j] * q[i]
        hq[i] = ball['dbase'][i] * q[i] - coupling
    for j in range(8):
        need(cross[j] % wf[j] == 0, 'W_weighted_PQ_reciprocity')
        hp[j] -= cross[j] // wf[j]
    shell4_norm = 0
    for f in range(ball['nf']):
        acc = sum(ball['ewc'][h] * q[ball['esrc'][h]]
                  for h in range(ball['es'][f], ball['es'][f + 1]))
        ww = ball['eW'][f]
        need(acc % ww == 0, 'W_weighted_shell4_reciprocity')
        exterior = -(acc // ww)
        shell4_norm += ww * exterior * exterior
    return hp, hq, shell4_norm


def real():
    need(stage_n.previous.k.SCRIPT_SHA ==
         'f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff',
         'original_K3_graph_source_pin')
    ball, obs = stage_n.previous.build()
    source = stage_n.previous.mod.threshold_ball(
        stage_n.previous.A1, stage_n.previous.DEN,
        stage_n.previous.ITER, stage_n.previous.SCALE,
        ball, stage_n.previous.FLOOR)
    flat = stage_n.previous.even_trial(source['U'], [1, 2, 3, 4, 5, 6, 7])
    trial = stage_n.previous.trial(ball, stage_n.previous.A1, flat)
    p, q = trial['p'], trial['q']
    wf, wq = ball['wf'], ball['wq']
    norm = stage_n.previous.dot_w(p, p, wf) + stage_n.previous.dot_w(q, q, wq)
    need(norm == trial['norm'] and norm > 0, 'source_trial_norm')
    mean = sum(wf[j] * obs[j] * p[j] * p[j] for j in range(8))
    mean += sum(wq[i] * obs[i + 8] * q[i] * q[i] for i in range(ball['n']))
    pp = [(norm * obs[j] - mean) * p[j] for j in range(8)]
    qq = [(norm * obs[i + 8] - mean) * q[i] for i in range(ball['n'])]
    need(sum(wf[j] * p[j] * pp[j] for j in range(8)) +
         sum(wq[i] * q[i] * qq[i] for i in range(ball['n'])) == 0,
         'original_W_centered_trial')
    m0, m1, _, _, _ = stage_n.H_moment(ball, pp, qq)
    hp, hq, shell4 = original_H_action(ball, pp, qq)
    action_m1 = sum(wf[j] * pp[j] * hp[j] for j in range(8))
    action_m1 += sum(wq[i] * qq[i] * hq[i] for i in range(ball['n']))
    need(action_m1 == m1, 'physical_H_bilinear_vs_direct_action')
    m2 = shell4 + sum(wf[j] * hp[j] * hp[j] for j in range(8))
    m2 += sum(wq[i] * hq[i] * hq[i] for i in range(ball['n']))
    t1, t2 = checks(m0, m1, m2, CAP)
    emit('Y137_PRL_SOURCE', source='ORIGINAL_S3_3X4_SEVEN_LOOP_WILSON',
         first_shell='8_FLATS_PLUS_155378_K3', shell4=ball['nf'],
         source_kind='TRUE_H_ON_FIXED_TRIAL',
         operator_cap=CAP, source_sha256=digest(stage_n.SHARE_SHA),
         original_spectral_weight='HOLD')
    emit('Y137_PRL_MOMENTS', m0=m0, m1=m1, m2=m2,
         t1=t1, t2=t2, shell4_norm2=shell4,
         m0_sha256=digest(m0), m1_sha256=digest(m1),
         m2_sha256=digest(m2), t2_sha256=digest(t2),
         mean_energy_ppm=m1 * 1000000 // m0,
         once_filtered_energy_ppm=(CAP * t1 - t2) * 1000000 // t1)
    emit('Y137_PRL_FILTER_VERDICT', original_H_moments='EXACT_K3_TO_K4',
         weighted_Cauchy='PASS', shell4_omission='REJECTED_BY_FULL_ACTION',
         source_trial='NOT_TRUE_PSI1', actual_Wilson_weight='HOLD',
         next_gate='TRUE_GROUND_PROJECTOR_AND_E3_TAIL')


if __name__ == '__main__':
    if sys.argv[1:] == ['toy']:
        toy()
    elif sys.argv[1:] == ['real']:
        toy()
        real()
    else:
        need(False, 'usage_toy_or_real')
