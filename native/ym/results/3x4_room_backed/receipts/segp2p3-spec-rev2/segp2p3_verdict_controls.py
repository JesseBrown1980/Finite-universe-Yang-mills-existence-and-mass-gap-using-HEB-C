#!/usr/bin/env python3
"""Synthetic controls for segp2p3_verdict.py (revision 2): pure logic, no tool is run.
Comparator stdout files are written to a temporary run directory (CRLF, as Windows Python
writes them) so binding, hashing and tamper cases are exercised against real bytes. HBP, json=0."""
import hashlib
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import segp2p3_verdict as V  # noqa: E402

M = 'ab' * 32  # stand-in 3x3 payload_merkle
H = 'cd' * 32  # stand-in header line hash
S2 = 'ef' * 32  # stand-in single-store hash


def cmpfile(root, rel, verdict):
    body = (f'SCHUR_COMPARE|shell=s.hbp|room=r.hbp|scol_records=1|verdict={verdict}|x|json=0\r\n'
            f'SCHUR_COMPARE_VERDICT|thresholds=1|{verdict}|json=0\r\n').encode()
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(body)
    return hashlib.sha256(body).hexdigest()


def clean(root, v2=None, v1='MISMATCH'):
    v2 = v2 or {}
    r = ['PRECONDITIONS|ok=1',
         'CONTROL_TOTAL|kind=comparator|line=' + V.CTL_TOTALS['comparator'].replace('|', ';'),
         'CONTROL_TOTAL|kind=verdict|line=' + V.CTL_TOTALS['verdict'].replace('|', ';'),
         'SEG_CONTROL_STORE|L=2x3|geom=G3|seglen=16411|files=31|build_exit=0|prefix_equal_single=1']
    for k, w in V.KWANT.items():
        r.append(f'SEG_CONTROL|case={k}|exit={0 if w == "0" else 1}|detected={w}|want_detected={w}|ok=1')
    h = cmpfile(root, 'csf60/cmp.out', 'AGREE')
    r.append(f'CSF60|v2_exit=0|v2_verdict=AGREE|stdout_file=csf60/cmp.out|stdout_sha256={h}|scol_bytes_identical=1|result=PASS')
    r += ['CONTROLS|comparator=PASS|segment=PASS|verdict=PASS|csf60=PASS', 'END_INTEGRITY|exe_unchanged=1|spec_unchanged=1']
    for lat in V.LATTICES:
        a = V.ANCHOR[lat]
        r.append(f'P2_TEXT|L={lat}|runs_ok=1|ymsec_sha256={a}|ymsec_bytes=9|ymroom_sha256={a}|ymroom_bytes=9')
        for g in V.GEOMS:
            r.append(f'P2_BUILD|L={lat}|geom={g}|exit=0|w_self_adjoint=PASS|header_readback=EXACT|hdr_sha256={H}|payload_merkle={M}')
        r.append(f'P2_SINGLE|L={lat}|bytes=500000|store_sha256={S2}')
        for g in V.SEGGEOMS:
            r.append(f'P2_STORE|L={lat}|geom={g}|read_ok=1|files=3|seglen={V.SEGLEN[g]}|prefix_equal_single=1|tail_zero=1')
    for t, (core, s) in V.THRESH.items():
        res, neg, amb = ('AMBIGUOUS', 37, 9) if t == 90000000 else ('PASS', 7, 0)
        for side in ('shell', 'room'):
            r.append(f'P3_CHUNKS|t={t}|side={side}|S={s}|present={s}|exits_ok=1|partition_exact=1|binding_equal=1|core={core}')
            r.append(f'P3_MERGE|t={t}|side={side}|exit={2 if res == "AMBIGUOUS" else 0}|core={core}|result={res}|negative={neg}|ambiguous={amb}')
        r.append(f'P3_MERKLE|t={t}|room_lines={s}|all_equal=1|merkle={M}')
        r.append(f'P3_INPUTS|t={t}|unchanged=1')
        for mode, v in (('v2', v2.get(t, 'AGREE')), ('v1', v1)):
            rel = f'p3/t{t}/cmp-{mode}.out'
            h = cmpfile(root, rel, v)
            r.append(f'P3_CMP|t={t}|mode={mode}|verdict={v}|exit={0 if v == "AGREE" else 2}|stdout_file={rel}|stdout_sha256={h}')
    return r


def edit(r, prefix, old, new):
    return [x.replace(old, new) if x.startswith(prefix) else x for x in r]


def drop(r, prefix):
    return [x for x in r if not x.startswith(prefix)]


def tamper(root, rel):
    p = os.path.join(root, rel)
    open(p, 'ab').write(b'X')


T90 = 'P3_CMP|t=90000000|mode=v2'

# each case: name -> (builder(root) returning rows, want P2, want P3)
CASES = [
    ('clean', lambda d: clean(d), 'AGREE', 'AGREE'),
    ('t90_shared_ambiguous_labelled', lambda d: clean(d), 'AGREE', 'AGREE'),
    ('never_spectral_pass_and_G1_scope', lambda d: clean(d), 'AGREE', 'AGREE'),
    ('text_ymroom_differs', lambda d: edit(clean(d), 'P2_TEXT|L=2x4', 'ymroom_bytes=9', 'ymroom_bytes=8'), 'MISMATCH', 'AGREE'),
    ('text_not_ci_anchor', lambda d: edit(clean(d), 'P2_TEXT|L=2x3', V.ANCHOR['2x3'], 'f' * 64), 'MISMATCH', 'AGREE'),
    ('seg_store_bytes_differ_3x3', lambda d: edit(clean(d), 'P2_STORE|L=3x3|geom=G2', 'prefix_equal_single=1', 'prefix_equal_single=0'), 'MISMATCH', 'INCONCLUSIVE'),
    ('stray_write_beyond_store', lambda d: edit(clean(d), 'P2_STORE|L=2x3|geom=G1', 'tail_zero=1', 'tail_zero=0'), 'MISMATCH', 'AGREE'),
    ('hdr_differs_across_geoms', lambda d: edit(clean(d), 'P2_BUILD|L=2x4|geom=G2', f'hdr_sha256={H}', 'hdr_sha256=' + '0' * 64), 'MISMATCH', 'AGREE'),
    ('build_readback_not_exact', lambda d: edit(clean(d), 'P2_BUILD|L=2x3|geom=G1', 'header_readback=EXACT', 'header_readback=MISMATCH'), 'INCONCLUSIVE', 'AGREE'),
    ('build_row_duplicated', lambda d: clean(d) + [f'P2_BUILD|L=2x4|geom=G1|exit=0|w_self_adjoint=PASS|header_readback=EXACT|hdr_sha256={H}|payload_merkle={M}'], 'INCONCLUSIVE', 'AGREE'),
    ('store_row_missing', lambda d: drop(clean(d), 'P2_STORE|L=2x4|geom=G1'), 'INCONCLUSIVE', 'AGREE'),
    ('p2_single_missing', lambda d: drop(clean(d), 'P2_SINGLE|L=2x4'), 'INCONCLUSIVE', 'AGREE'),
    ('p2_hash_field_empty_not_mismatch', lambda d: edit(clean(d), 'P2_TEXT|L=2x3', f'ymroom_sha256={V.ANCHOR["2x3"]}', 'ymroom_sha256='), 'INCONCLUSIVE', 'AGREE'),
    ('store_read_failed_not_mismatch', lambda d: edit(edit(clean(d), 'P2_STORE|L=2x4|geom=G2', 'read_ok=1', 'read_ok=0'), 'P2_STORE|L=2x4|geom=G2', 'prefix_equal_single=1', 'prefix_equal_single=0'), 'INCONCLUSIVE', 'AGREE'),
    ('mismatch_plus_inconclusive_gives_inconclusive', lambda d: edit(drop(clean(d), 'P2_SINGLE|L=2x3'), 'P2_TEXT|L=2x4', 'ymroom_bytes=9', 'ymroom_bytes=8'), 'INCONCLUSIVE', 'AGREE'),
    ('v2_mismatch', lambda d: clean(d, v2={72000000: 'MISMATCH'}), 'AGREE', 'MISMATCH'),
    ('v2_inconclusive', lambda d: clean(d, v2={90000000: 'INCONCLUSIVE'}), 'AGREE', 'INCONCLUSIVE'),
    ('v2_row_claims_agree_exit2', lambda d: edit(clean(d), T90, '|exit=0|', '|exit=2|'), 'AGREE', 'INCONCLUSIVE'),
    ('v2_row_claims_agree_stdout_mismatch', lambda d: (lambda r: (cmpfile(d, 'p3/t72000000/cmp-v2.out', 'MISMATCH'), r)[1])(clean(d)), 'AGREE', 'INCONCLUSIVE'),
    ('v2_stdout_tampered', lambda d: (lambda r: (tamper(d, 'p3/t60000000/cmp-v2.out'), r)[1])(clean(d)), 'AGREE', 'INCONCLUSIVE'),
    ('v1_stdout_missing', lambda d: (lambda r: (os.remove(os.path.join(d, 'p3/t90000000/cmp-v1.out')), r)[1])(clean(d)), 'AGREE', 'INCONCLUSIVE'),
    ('comparator_row_missing', lambda d: drop(clean(d), 'P3_CMP|t=60000000|mode=v1'), 'AGREE', 'INCONCLUSIVE'),
    ('chunk_missing', lambda d: edit(clean(d), 'P3_CHUNKS|t=90000000|side=room', 'present=40', 'present=39'), 'AGREE', 'INCONCLUSIVE'),
    ('partition_gap', lambda d: edit(clean(d), 'P3_CHUNKS|t=60000000|side=shell', 'partition_exact=1', 'partition_exact=0'), 'AGREE', 'INCONCLUSIVE'),
    ('merged_core_not_frozen', lambda d: edit(clean(d), 'P3_MERGE|t=72000000|side=room', 'core=1137', 'core=1136'), 'AGREE', 'INCONCLUSIVE'),
    ('payload_merkle_not_p2', lambda d: edit(clean(d), 'P3_MERKLE|t=60000000', f'merkle={M}', 'merkle=' + '9' * 64), 'AGREE', 'INCONCLUSIVE'),
    ('input_changed', lambda d: edit(clean(d), 'P3_INPUTS|t=72000000', 'unchanged=1', 'unchanged=0'), 'AGREE', 'INCONCLUSIVE'),
    ('end_exe_changed', lambda d: edit(clean(d), 'END_INTEGRITY', 'exe_unchanged=1', 'exe_unchanged=0'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('end_spec_changed', lambda d: edit(clean(d), 'END_INTEGRITY', 'spec_unchanged=1', 'spec_unchanged=0'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('seg_K3_not_detected_summary_still_pass', lambda d: edit(clean(d), 'SEG_CONTROL|case=K3', 'detected=1|want', 'detected=0|want'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('seg_K5_row_missing', lambda d: drop(clean(d), 'SEG_CONTROL|case=K5'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('seg_control_store_too_few_files', lambda d: edit(clean(d), 'SEG_CONTROL_STORE', 'files=31', 'files=5'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('csf60_stdout_tampered', lambda d: (lambda r: (tamper(d, 'csf60/cmp.out'), r)[1])(clean(d)), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('control_total_wrong', lambda d: edit(clean(d), 'CONTROL_TOTAL|kind=comparator', 'ok=60', 'ok=59'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
    ('preconditions_failed', lambda d: edit(clean(d), 'PRECONDITIONS', 'ok=1', 'ok=0'), 'INCONCLUSIVE', 'INCONCLUSIVE'),
]


def main():
    ok = 0
    for name, build, w2, w3 in CASES:
        d = tempfile.mkdtemp(prefix='segp2p3ctl-')
        try:
            out = V.decide(build(d), d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
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
            good = good and not any('spectral_pass=1' in x for x in out)
        ok += good
        print(f'SEGP2P3_CONTROL|case={name}|want_P2={w2}|got_P2={g2}|want_P3={w3}|got_P3={g3}|ok={int(good)}|json=0')
    print(f'SEGP2P3_CONTROLS_TOTAL|cases={len(CASES)}|ok={ok}|result={"PASS" if ok == len(CASES) else "FAIL"}|json=0')
    return 0 if ok == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())
