#!/usr/bin/env python3
# d2-feshbach-r9 step 4: evaluate the rigorous-lower-bound inequality chain with the MEASURED inputs
# (exact rationals parsed from the printed exact-rational roundings; residuals rounded UP by 1e-12).
# Writes rigor.rows. json=0.
import sys
from fractions import Fraction as Fr
from math import isqrt
HERE = '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9'


def parse(path, tag, filt=None):
    out = []
    for l in open(path):
        if l.startswith(tag + '|'):
            kv = dict(x.split('=', 1) for x in l.strip().split('|')[1:] if '=' in x)
            if filt is None or all(kv.get(k) == v for k, v in filt.items()):
                out.append(kv)
    return out


def F(s):
    if '/' in s:
        a, b = s.split('/'); return Fr(int(a), int(b))
    return Fr(s)


def dec(x, d=7):
    x = Fr(x); s = '-' if x < 0 else ''; x = abs(x)
    q = (x.numerator * 10 ** d * 2 + x.denominator) // (2 * x.denominator)
    return '%s%d.%0*d' % (s, q // 10 ** d, d, q % 10 ** d)


def sqrt_up(x, d=12):
    v = isqrt(x.numerator * 10 ** (2 * d) // x.denominator) + 1
    return Fr(v, 10 ** d)


rows = []
def emit(label, **kv):
    rows.append(label + '|' + '|'.join('%s=%s' % kv_ for kv_ in [(k, v) for k, v in kv.items()]) + '|json=0')
    print(rows[-1])


ONORM = Fr(21, 2)              # ||O - 7/2|| : O_sum in [-7, 14] on every orbit
GAMMA_FLOOR = Fr(94070673, 10 ** 6)
k2lev = {r['which']: r for r in parse(HERE + '/run-s64.rows', 'FE_LEVEL')}
k2amp = parse(HERE + '/run-s64.rows', 'FE_AMP')[0]
bounds = {(r['level'], r['form']): r for r in parse(HERE + '/lower-s32.rows', 'FL_BOUND')}
amp = abs(F(k2amp['amp']))
need = amp / ONORM
emit('RIGOR_TARGET', amp_estimate=k2amp['amp'], O_shift='7/2', O_shift_norm='21/2',
     required_eta1_plus_eta2_below=dec(need, 7),
     chain='T>=|<psi2h,(O-7/2)psi1h>|-(21/2)(eta1+eta2),eta_i=||phi_i-psi_ih||_W<=sqrt2*sin(theta_i)',
     tag='NAMED_INEQUALITY_MEASURED_INPUTS')
# ---- chain A: Davis-Kahan / Kato-Temple on the full H with certified windows
E1_hi = F(bounds[('E1_even', 'Ue')]['bound']); E1_lo = F(bounds[('E1_even', 'Le')]['bound'])
E2_hi = F(bounds[('E2_even', 'Ue')]['bound']); E2_lo = F(bounds[('E2_even', 'Le')]['bound'])
E3_lo = F(bounds[('E3_even', 'Le')]['bound']); Eo_lo = F(bounds[('E1_odd', 'Lo')]['bound'])
rho1 = F(k2lev['E1_even']['rayleigh']); rho2 = F(k2lev['E2_even']['rayleigh'])
eps1 = F(k2lev['E1_even']['rel_res_at_rho']) + Fr(1, 10 ** 12)
eps2 = F(k2lev['E2_even']['rel_res_at_rho']) + Fr(1, 10 ** 12)
d1 = E2_lo - rho1
d2 = min(rho2 - E1_hi, E3_lo - rho2)
emit('RIGOR_WINDOWS_K2', E1='[%s,%s]' % (dec(E1_lo), dec(E1_hi)), E2_even='[%s,%s]' % (dec(E2_lo), dec(E2_hi)),
     E3_even_lower=dec(E3_lo), E1_odd_lower=dec(Eo_lo),
     E2_even_isolated_from_E3_even=int(E3_lo > E2_hi), E2_is_even_certified=int(Eo_lo > E2_hi),
     note='lower_ends_CONDITIONAL_on_Perron_floor;upper_ends_unconditional_minmax', tag='MEASURED')
emit('RIGOR_CHAIN_A_K2', eps1=dec(eps1, 9), eps2=dec(eps2, 9), delta1=dec(d1, 9), delta2=dec(d2, 9),
     sin1_bound=(dec(eps1 / d1, 4) if d1 > 0 else 'inapplicable'),
     sin2_bound=(dec(eps2 / d2, 4) if d2 > 0 else 'inapplicable_no_isolation'),
     verdict='VACUOUS', tag='MEASURED')
# ---- chain B: Feshbach-resolvent Q-tail bound
z1 = F(k2lev['E1_even']['z_used']); z2 = F(k2lev['E2_even']['z_used'])
rz1 = sqrt_up(F(k2lev['E1_even']['rel_res2_at_z'])); rz2 = sqrt_up(F(k2lev['E2_even']['rel_res2_at_z']))
g1 = GAMMA_FLOOR - z1; g2 = GAMMA_FLOOR - z2
eq1 = rz1 / g1; eq2 = rz2 / g2
emit('RIGOR_CHAIN_B_K2', gamma1=dec(g1), gamma2=dec(g2), qtail1=dec(eq1, 6), qtail2=dec(eq2, 6),
     first_order_qtail_term=dec(ONORM * (eq1 + eq2), 6), second_order_cross_term=dec(ONORM * eq1 * eq2, 6),
     isotropic_Delta_size_rel=dec(rz1 * rz1 / g1, 6),
     verdict='VACUOUS_first_order;second_order_cross_term_below_amp_but_flat_vector_term_unbounded', tag='MEASURED')
# ---- K3 (if present)
try:
    k3lev = {r['which']: r for r in parse(HERE + '/k3-amp.rows', 'K3_LEVEL', {'steps': '20'})}
    k3amp = parse(HERE + '/k3-amp.rows', 'K3_AMP', {'steps': '20'})[0]
    z1 = F(k3lev['E1_even']['z_used']); z2 = F(k3lev['E2_even']['z_used'])
    e1 = F(k3lev['E1_even']['rel_res_at_rho']) + Fr(1, 10 ** 12)
    e2 = F(k3lev['E2_even']['rel_res_at_rho']) + Fr(1, 10 ** 12)
    g1 = GAMMA_FLOOR - z1; g2 = GAMMA_FLOOR - z2
    # K3 windows: upper ends from the K3 U-form root brackets (k3-amp-roots.rows / k3-amp.rows),
    # lower ends E3_even / E1_odd from the K3 sandwich; E2_even lower end still the K2 value.
    kb = {r['level']: r for r in parse(HERE + '/k3-lower.rows', 'K3L_BOUND')}
    E1_hi3 = F(k3lev['E1_even']['z_hi']); E2_hi3 = F(k3lev['E2_even']['z_hi'])
    E3_lo3 = F(kb['E3_even']['lower_bound']); Eo_lo3 = F(kb['E1_odd']['lower_bound'])
    r1 = F(k3lev['E1_even']['rayleigh']); r2 = F(k3lev['E2_even']['rayleigh'])
    dd1 = E2_lo - r1
    dd2 = min(r2 - E1_hi3, E3_lo3 - r2)
    emit('RIGOR_WINDOWS_K3', E1_upper=dec(E1_hi3, 9), E2_even='[%s,%s]' % (dec(E2_lo), dec(E2_hi3, 9)),
         E3_even_lower=dec(E3_lo3), E1_odd_lower=dec(Eo_lo3),
         E2_even_isolated_from_E3_even=int(E3_lo3 > E2_hi3), E2_is_even_certified=int(Eo_lo3 > E2_hi3),
         note='E2_even_lower_from_K2;lower_ends_CONDITIONAL_on_Perron_floor;upper_ends_unconditional_minmax', tag='MEASURED')
    emit('RIGOR_CHAIN_A_K3', eps1=dec(e1, 9), eps2=dec(e2, 9), delta1=dec(dd1, 9), delta2=dec(dd2, 9),
         sin1_bound=(dec(e1 / dd1, 4) if dd1 > 0 else 'inapplicable'),
         sin2_bound=(dec(e2 / dd2, 4) if dd2 > 0 else 'inapplicable'),
         verdict=('VACUOUS' if (dd1 <= 0 or dd2 <= 0 or e1 / dd1 >= 1 or e2 / dd2 >= 1 or
                                ONORM * 2 * (e1 / dd1 + e2 / dd2) >= abs(F(k3amp['amp']))) else 'NONVACUOUS'),
         tag='MEASURED')
    emit('RIGOR_CHAIN_B_K3', amp_estimate=k3amp['amp'], gamma1=dec(g1), gamma2=dec(g2),
         qtail1=dec(e1 / g1, 6), qtail2=dec(e2 / g2, 6),
         first_order_qtail_term=dec(ONORM * (e1 / g1 + e2 / g2), 6),
         second_order_cross_term=dec(ONORM * e1 * e2 / (g1 * g2), 6),
         isotropic_Delta_size_rel=dec(e1 * e1 / g1, 6),
         required_eta1_plus_eta2_below=dec(abs(F(k3amp['amp'])) / ONORM, 6), tag='MEASURED')
except (FileNotFoundError, IndexError, KeyError) as ex:
    emit('RIGOR_CHAIN_B_K3', missing=1, ok=0, reason=type(ex).__name__)
try:
    for r in parse(HERE + '/k3-lower.rows', 'K3L_TEST'):
        emit('RIGOR_ORDER_K3', z=r['z'], odd_level_below_z_possible=r['odd_level_below_z_possible'],
             even_levels_below_z_at_most=r['even_levels_below_z_at_most'],
             E2_is_even_certified=int(r['odd_level_below_z_possible'] == '0'),
             E2_even_isolated_from_E3_even=int(r['even_levels_below_z_at_most'] == '2'),
             note='z=K2_unconditional_upper_bound_of_E2_even;lower_counts_CONDITIONAL_on_Perron_floor', tag='MEASURED')
    for r in parse(HERE + '/k3-lower.rows', 'K3L_BOUND'):
        emit('RIGOR_BOUND_K3', **{k: v for k, v in r.items() if k != 'json'})
except FileNotFoundError:
    emit('RIGOR_ORDER_K3', missing=1, ok=0)
# ---- summary rows (exact-rational arithmetic on the printed measured values)
amps = []
for s in ('4', '8', '16', '32', '64', '128'):
    a_ = parse(HERE + '/run-s%s.rows' % s, 'FE_AMP')[0]
    amps.append('s%s:%s' % (s, a_['amp']))
emit('FE_SUMMARY', item='K2_amp_vs_jacobi_steps', values=','.join(amps),
     scale15_s64=parse(HERE + '/run-s64-scale15.rows', 'FE_AMP')[0]['amp'], tag='ESTIMATE')
LO = Fr(5, 144)
try:
    a2 = abs(F(k2amp['amp'])); a3 = abs(F(k3amp['amp']))
    emit('FE_SUMMARY', item='K_truncation_and_leading_order', amp_K2=k2amp['amp'], amp_K3=k3amp['amp'],
         rel_change_K2_to_K3=dec((a3 - a2) / a2, 6), amp_leading_order='5/144', amp_LO_dec=dec(LO, 9),
         ratio_K2_over_LO=dec(a2 / LO, 6), ratio_K3_over_LO=dec(a3 / LO, 6),
         amp2_K2=k2amp['amp2'], amp2_K3=k3amp['amp2'], amp2_LO='25/20736', tag='ESTIMATE')
    emit('FE_SUMMARY', item='first_gap_rayleigh', K2=dec(rho2 - rho1, 12),
         K3=dec(F(k3lev['E2_even']['rayleigh']) - F(k3lev['E1_even']['rayleigh']), 12),
         leading_order='3/81', tag='ESTIMATE')
except NameError:
    pass
emit('FE_SUMMARY', item='first_state_weight_fraction_K2', amp2_over_connected_var=k2amp['first_state_weight_over_var'],
     var1=k2amp['var1'], leading_order='all_var_9_goes_to_C1_zero_mode_(2,0,-1)_on_flats_0_1_2;E2_gets_0_at_r_infinity',
     tag='ESTIMATE')
open(HERE + '/rigor.rows', 'w').write('\n'.join(rows) + '\n')
