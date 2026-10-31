#!/usr/bin/env python3
"""Synthetic controls for segp2p3_verdict.py: pure logic, no tool is run. HBP out, json=0."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import segp2p3_verdict as V  # noqa: E402

M = 'ab' * 32  # stand-in 3x3 payload_merkle


def clean():
    r = ['PRECONDITIONS|ok=1', 'CONTROLS|comparator=PASS|segment=PASS|verdict=PASS|csf60=PASS',
         'END_INTEGRITY|exe_unchanged=1']
    for lat in V.LATTICES:
        a = V.ANCHOR[lat]
        r.append(f'P2_TEXT|L={lat}|runs_ok=1|ymsec_sha256={a}|ymsec_bytes=9|ymroom_sha256={a}|ymroom_bytes=9')
        for g in V.GEOMS:
            r.append(f'P2_BUILD|L={lat}|geom={g}|exit=0|w_self_adjoint=PASS|header_readback=EXACT|hdr_sha256=h{lat}|payload_merkle={M}')
        for g in V.SEGGEOMS:
            r.append(f'P2_STORE|L={lat}|geom={g}|read_ok=1|prefix_equal_single=1|tail_zero=1')
    for t, (core, s) in V.THRESH.items():
        res, neg, amb = ('AMBIGUOUS', 37, 9) if t == 90000000 else ('PASS', 7, 0)
        for side in ('shell', 'room'):
            r.append(f'P3_CHUNKS|t={t}|side={side}|S={s}|present={s}|exits_ok=1|partition_exact=1|binding_equal=1|core={core}')
            r.append(f'P3_MERGE|t={t}|side={side}|exit={2 if res == "AMBIGUOUS" else 0}|core={core}|result={res}|negative={neg}|ambiguous={amb}')
        r.append(f'P3_MERKLE|t={t}|room_lines={s}|all_equal=1|merkle={M}')
        r.append(f'P3_INPUTS|t={t}|unchanged=1')
        r.append(f'P3_CMP|t={t}|mode=v2|verdict=AGREE|exit=0')
        r.append(f'P3_CMP|t={t}|mode=v1|verdict=MISMATCH|exit=2')
    return r


def edit(r, prefix, old, new):
    return [x.replace(old, new) if x.startswith(prefix) else x for x in r]


def drop(r, prefix):
    return [x for x in r if not x.startswith(prefix)]


T90 = 'P3_CMP|t=90000000|mode=v2'
CASES = [
    ('clean', clean(), 'AGREE', 'AGREE'),
    ('t90_shared_ambiguous_labelled', clean(), 'AGREE', 'AGREE'),
    ('text_ymroom_differs', edit(clean(), 'P2_TEXT|L=2x4', 'ymroom_bytes=9', 'ymroom_bytes=8'), 'MISMATCH', 'AGREE'),
    ('text_not_ci_anchor', edit(clean(), 'P2_TEXT|L=2x3', V.ANCHOR['2x3'], 'f' * 64), 'MISMATCH', 'AGREE'),
    ('seg_store_bytes_differ_3x3', edit(clean(), 'P2_STORE|L=3x3|geom=G2', 'prefix_equal_single=1', 'prefix_equal_single=0'), 'MISMATCH', 'INCONCLUSIVE'),
    ('stray_write_beyond_store', edit(clean(), 'P2_STORE|L=2x3|geom=G1', 'tail_zero=1', 'tail_zero=0'), 'MISMATCH', 'AGREE'),
    ('hdr_differs_across_geoms', edit(clean(), 'P2_BUILD|L=2x4|geom=G2', 'hdr_sha256=h2x4', 'hdr_sha256=zz'), 'MISMATCH', 'AGREE'),
    ('build_readback_not_exact', edit(clean(), 'P2_BUILD|L=2x3|geom=G1', 'header_readback=EXACT', 'header_readback=MISMATCH'), 'INCONCLUSIVE', 'AGREE'),
    ('build_row_duplicated', clean() + ['P2_BUILD|L=2x4|geom=G1|exit=0|w_self_adjoint=PASS|header_readback=EXACT|hdr_sha256=h2x4'], 'INCONCLUSIVE', 'AGREE'),
    ('store_row_missing', drop(clean(), 'P2_STORE|L=2x4|geom=G1'), 'INCONCLUSIVE', 'AGREE'),
    ('v2_mismatch', edit(clean(), 'P3_CMP|t=72000000|mode=v2', 'verdict=AGREE|exit=0', 'verdict=MISMATCH|exit=2'), 'AGREE', 'MISMATCH'),
    ('v2_inconclusive', edit(clean(), T90, 'verdict=AGREE|exit=0', 'verdict=INCONCLUSIVE|exit=2'), 'AGREE', 'INCONCLUSIVE'),
    ('v2_agree_but_exit2', edit(clean(), T90, 'exit=0', 'exit=2'), 'AGREE', 'INCONCLUSIVE'),
    ('chunk_missing', edit(clean(), 'P3_CHUNKS|t=90000000|side=room', 'present=40', 'present=39'), 'AGREE', 'INCONCLUSIVE'),
    ('partition_gap', edit(clean(), 'P3_CHUNKS|t=60000000|side=shell', 'partition_exact=1', 'partition_exact=0'), 'AGREE', 'INCONCLUSIVE'),
    ('merged_core_not_frozen', edit(clean(), 'P3_MERGE|t=72000000|side=room', 'core=1137', 'core=1136'), 'AGREE', 'INCONCLUSIVE'),
    ('payload_merkle_not_p2', edit(clean(), 'P3_MERKLE|t=60000000', f'merkle={M}', 'merkle=' + 'cd' * 32), 'AGREE', 'INCONCLUSIVE'),
    ('room_merkles_inconsistent', edit(clean(), 'P3_MERKLE|t=90000000', 'all_equal=1', 'all_equal=0'), 'AGREE', 'INCONCLUSIVE'),
    ('input_changed', edit(clean(), 'P3_INPUTS|t=72000000', 'unchanged=1', 'unchanged=0'), 'AGREE', 'INCONCLUSIVE'),
    ('exe_changed_at_end', edit(clean(), 'END_INTEGRITY', 'exe_unchanged=1', 'exe_unchanged=0'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('segment_control_failed', edit(clean(), 'CONTROLS', 'segment=PASS', 'segment=FAIL'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('preconditions_failed', edit(clean(), 'PRECONDITIONS', 'ok=1', 'ok=0'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('comparator_row_missing', drop(clean(), 'P3_CMP|t=60000000|mode=v1'), 'AGREE', 'INCONCLUSIVE'),
    ('never_spectral_pass_and_G1_scope', clean(), 'AGREE', 'AGREE'),
]


def main():
    ok = 0
    for name, r, w2, w3 in CASES:
        out = V.decide(r)
        tot = out[-1]
        g2 = tot.split('|P2=')[1].split('|')[0]
        g3 = tot.split('|P3=')[1].split('|')[0]
        good = g2 == w2 and g3 == w3
        if name == 't90_shared_ambiguous_labelled':
            line = [x for x in out if x.startswith('SEGP3_VERDICT|t=90000000|')][0]
            good = good and 'shared_AMBIGUOUS_negative=37_ambiguous=9_spectral_pass=0' in line
        if name == 'never_spectral_pass_and_G1_scope':
            vrows = [x for x in out if '_VERDICT|' in x]
            good = good and len(vrows) == 7 and all('|spectral_pass=0|' in x for x in vrows)
            good = good and all('|scope=G1_segmented_store|' in x for x in out if x.startswith('SEGP3_VERDICT|'))
            good = good and '|P3_scope=G1_segmented_store_only|G2=P2_builder_bytes_only_not_runner_certified|' in tot
            good = good and not any('spectral_pass=1' in x or 'PASS|spectral' in x for x in out)
        ok += good
        print(f'SEGP2P3_CONTROL|case={name}|want_P2={w2}|got_P2={g2}|want_P3={w3}|got_P3={g3}|ok={int(good)}|json=0')
    print(f'SEGP2P3_CONTROLS_TOTAL|cases={len(CASES)}|ok={ok}|result={"PASS" if ok == len(CASES) else "FAIL"}|json=0')
    return 0 if ok == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())
