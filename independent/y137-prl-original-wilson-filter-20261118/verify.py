#!/usr/bin/env python3
"""Independent integer receipt algebra; does not import moment_filter or S3 builders."""
import hashlib
import sys


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha(x):
    return hashlib.sha256(str(x).encode('ascii')).hexdigest()


def parse(data):
    rows = {}
    for line in data.splitlines():
        if line.startswith('Y137_PRL_FILTER_REFUSE|'):
            continue
        parts = line.split('|')
        key = parts[0]
        if key in ('Y137_QDUAL_GRAPH', 'Y137_QDUAL_TRIAL'):
            continue
        need(key in ('Y137_PRL_FILTER_TOY', 'Y137_PRL_SOURCE',
                     'Y137_PRL_MOMENTS', 'Y137_PRL_FILTER_VERDICT'),
             'unrecognized_row')
        need(key not in rows, 'duplicate_row')
        fields = {}
        for part in parts[1:]:
            name, sep, value = part.partition('=')
            need(sep and name and name not in fields, 'malformed_field')
            fields[name] = value
        need(fields.pop('json', None) == '0', 'noncanonical_end')
        rows[key] = fields
    need(set(rows) == {'Y137_PRL_FILTER_TOY', 'Y137_PRL_SOURCE',
                       'Y137_PRL_MOMENTS', 'Y137_PRL_FILTER_VERDICT'},
         'incomplete_record')
    return rows


def verify(data):
    rows = parse(data)
    t = rows['Y137_PRL_FILTER_TOY']
    need(t == {'physical_H2': 'PASS', 'tampered_moment': 'REJECTED',
               'high_energy_dark_control': 'PASS',
               'first_Wilson_weight': 'HOLD'}, 'toy_bad')
    src = rows['Y137_PRL_SOURCE']
    need(src == {'source': 'ORIGINAL_S3_3X4_SEVEN_LOOP_WILSON',
                 'first_shell': '8_FLATS_PLUS_155378_K3',
                 'shell4': '1985218',
                 'source_kind': 'TRUE_H_ON_FIXED_TRIAL',
                 'operator_cap': '468',
                 'source_sha256': sha('b9881651c51a278757bc0fef15de583277330da3'),
                 'original_spectral_weight': 'HOLD'}, 'source_scope')
    record = rows['Y137_PRL_MOMENTS']
    need(set(record) == {'m0', 'm1', 'm2', 't1', 't2', 'shell4_norm2',
                         'm0_sha256', 'm1_sha256', 'm2_sha256', 't2_sha256',
                         'mean_energy_ppm', 'once_filtered_energy_ppm'},
         'moment_fields')
    for key in ('m0', 'm1', 'm2', 't1', 't2', 'shell4_norm2',
                'mean_energy_ppm', 'once_filtered_energy_ppm'):
        need(record[key].isdigit() and str(int(record[key])) == record[key],
             'noncanonical_integer_' + key)
    m0, m1, m2, t1, t2 = (int(record[k]) for k in ('m0', 'm1', 'm2', 't1', 't2'))
    sh4 = int(record['shell4_norm2'])
    need(m0 > 0 and sh4 > 0, 'source_norm_and_shell4')
    need(0 <= m1 <= 468*m0, 'energy_support')
    need(m1*m1 <= m0*m2 <= 468*m0*m1, 'H2_Cauchy_and_ceiling')
    need(t1 == 468*m0-m1 and t2 == 468*468*m0-936*m1+m2,
         'filter_moments')
    need(0 <= t1 and 0 <= t2 <= 468*t1 and m0*t2 >= t1*t1,
         'T_Cauchy_and_ceiling')
    for val in ('m0', 'm1', 'm2', 't2'):
        need(record[val + '_sha256'] == sha(int(record[val])), 'digest_' + val)
    need(int(record['mean_energy_ppm']) == m1*1000000//m0,
         'mean_energy')
    need(t1 > 0 and int(record['once_filtered_energy_ppm']) ==
         (468*t1-t2)*1000000//t1, 'filtered_mean_energy')
    need(m1*t1 >= 0 and m1*1000000//m0 >= (468*t1-t2)*1000000//t1,
         'filter_is_low_pass')
    verdict = rows['Y137_PRL_FILTER_VERDICT']
    need(verdict == {'original_H_moments': 'EXACT_K3_TO_K4',
                     'weighted_Cauchy': 'PASS',
                     'shell4_omission': 'REJECTED_BY_FULL_ACTION',
                     'source_trial': 'NOT_TRUE_PSI1',
                     'actual_Wilson_weight': 'HOLD',
                     'next_gate': 'TRUE_GROUND_PROJECTOR_AND_E3_TAIL'},
         'verdict_scope')
    return (m0, m1, m2)


def selftest(data):
    verify(data)
    for old, new in (
        ('|actual_Wilson_weight=HOLD|', '|actual_Wilson_weight=PASS|'),
        ('|source_trial=NOT_TRUE_PSI1|', '|source_trial=TRUE_PSI1|'),
        ('|shell4=1985218|', '|shell4=0|'),
        ('|operator_cap=468|', '|operator_cap=469|'),
        ('|m2_sha256=', '|m2_sha256=bad'),
    ):
        altered = data.replace(old, new, 1)
        need(altered != data, 'tamper_fixture_not_found')
        try:
            verify(altered)
        except ValueError:
            pass
        else:
            raise AssertionError('adversarial_receipt_was_accepted')
    print('Y137_PRL_REPLAY|original_moments=PASS|tamper_controls=5_REJECTED|wilson_weight=HOLD|json=0')


if __name__ == '__main__':
    need(len(sys.argv) == 2, 'usage_verify_RESULT_HBP')
    with open(sys.argv[1], encoding='ascii') as f:
        selftest(f.read())
