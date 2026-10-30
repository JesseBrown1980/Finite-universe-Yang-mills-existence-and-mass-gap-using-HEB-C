#!/usr/bin/env python3
"""Segmented-store P2/P3 verdicts from the run's HBP evidence rows (json=0, integer only).

Frozen with SEGP2P3-SPEC (revision 2). Usage: segp2p3_verdict.py EVIDENCE.hbp RUN_DIR
It reads the evidence rows and, to bind comparator claims to retained bytes, re-hashes and
parses the comparator stdout files named by the rows (paths relative to RUN_DIR). It never
runs a tool. Every verdict is AGREE, MISMATCH or INCONCLUSIVE:
  AGREE        every required row present exactly once and well-formed, every integrity gate
               passed, every compared value equal.
  MISMATCH     the same completeness and integrity, and a compared value differs.
  INCONCLUSIVE anything missing, duplicated, malformed, failed, unreadable or unbound.
Completeness is checked before any comparison, so incomplete evidence is never a MISMATCH.
Aggregates give INCONCLUSIVE precedence over MISMATCH. Every verdict row carries
spectral_pass=0; P3 is scoped to the G1 segmented store.
"""
import hashlib
import os
import re
import sys

LATTICES = ('2x3', '2x4', '3x3')
GEOMS = ('single', 'G1', 'G2')
SEGGEOMS = ('G1', 'G2')
SEGLEN = {'G1': '40000000', 'G2': '1048583'}
G3 = '16411'
ANCHOR = {  # ymsec/ymroom text SHA-256 from CI receipt ci-40936173167 (P2 PASS)
    '2x3': '2bc797fe8bafeb4c4a3db11495784fd72a28b03e3c63be582ac95754a9276725',
    '2x4': 'a34d252302eea9050c7dbb6dad6f099de96f99b657b2a3558e27e030b34576bb',
    '3x3': 'ad0168f973d120a0da2b5ebaa33d4e80619ad7704cfca8f45f3e940dc757bd1b',
}
THRESH = {60000000: (101, 2), 72000000: (1137, 16), 90000000: (2940, 40)}  # t -> (frozen core, S)
KWANT = {'K0': '0', 'K1': '1', 'K2': '1', 'K3': '1', 'K4': '1', 'K5': '1'}
CTL_TOTALS = {
    'comparator': 'STREAM_EQUIV_TOTAL|cases=60|ok=60|result=PASS|json=0',
    'verdict': 'SEGP2P3_CONTROLS_TOTAL|cases=35|ok=35|result=PASS|json=0',
}
VERDICTS = ('AGREE', 'MISMATCH', 'INCONCLUSIVE')
HEX = re.compile(r'^[0-9a-f]{64}$')
INT = re.compile(r'^(0|[1-9][0-9]*)$')


def hx(v):
    return v is not None and bool(HEX.match(v))


def nat(v):
    return v is not None and bool(INT.match(v))


def rows(lines):
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln or '|' not in ln:
            continue
        tag, *kv = ln.split('|')
        d = {}
        for x in kv:
            if '=' in x:
                k, v = x.split('=', 1)
                d[k] = v
        out.append((tag, d))
    return out


def pick(rs, tag, **want):
    return [d for t, d in rs if t == tag and all(d.get(k) == v for k, v in want.items())]


def one(rs, tag, **want):
    m = pick(rs, tag, **want)
    return m[0] if len(m) == 1 else None  # missing or duplicated -> None


class Bad(Exception):
    """Incomplete, malformed or unbound evidence: always INCONCLUSIVE."""


def need(cond, why):
    if not cond:
        raise Bad(why)


def gates(rs, root):
    """Preconditions, every control in detail, and end integrity. Raises Bad on any gap."""
    pre = one(rs, 'PRECONDITIONS')
    need(pre is not None and pre.get('ok') == '1', 'preconditions')
    for kind, line in CTL_TOTALS.items():
        c = one(rs, 'CONTROL_TOTAL', kind=kind)
        need(c is not None and c.get('line') == line.replace('|', ';'), f'control_total_{kind}')
    st = one(rs, 'SEG_CONTROL_STORE', L='2x3', geom='G3')
    need(st is not None and st.get('seglen') == G3 and st.get('build_exit') == '0'
         and st.get('prefix_equal_single') == '1' and nat(st.get('files')) and int(st['files']) >= 6,
         'seg_control_store')
    need(not pick(rs, 'SEG_CONTROL', case='setup'), 'seg_control_setup_failed')
    need(len(pick(rs, 'SEG_CONTROL')) == len(KWANT), 'seg_control_count')
    for k, w in KWANT.items():
        c = one(rs, 'SEG_CONTROL', case=k)
        need(c is not None and nat(c.get('exit')) and c.get('want_detected') == w
             and c.get('detected') == w and c.get('ok') == '1', f'seg_control_{k}')
    cs = one(rs, 'CSF60')
    need(cs is not None and cs.get('scol_bytes_identical') == '1' and cs.get('result') == 'PASS', 'csf60')
    need(cmp_bound({'verdict': cs.get('v2_verdict'), 'exit': cs.get('v2_exit'), 'stdout_file': cs.get('stdout_file'),
                    'stdout_sha256': cs.get('stdout_sha256')}, root) == 'AGREE', 'csf60_v2_not_AGREE')
    summ = one(rs, 'CONTROLS')
    need(summ is not None and all(summ.get(k) == 'PASS' for k in ('comparator', 'segment', 'verdict', 'csf60')),
         'controls_summary')
    end = one(rs, 'END_INTEGRITY')
    need(end is not None and end.get('exe_unchanged') == '1' and end.get('spec_unchanged') == '1', 'end_integrity')


def p2(rs, lat):
    """Returns (verdict, why). Completeness first; only then compare."""
    try:
        tx = one(rs, 'P2_TEXT', L=lat)
        need(tx is not None and tx.get('runs_ok') == '1', 'text_missing_or_failed')
        need(hx(tx.get('ymsec_sha256')) and hx(tx.get('ymroom_sha256')) and nat(tx.get('ymsec_bytes'))
             and nat(tx.get('ymroom_bytes')), 'text_fields_malformed')
        builds = [one(rs, 'P2_BUILD', L=lat, geom=g) for g in GEOMS]
        need(all(b is not None for b in builds), 'build_row_missing_or_duplicated')
        for b in builds:
            need(b.get('exit') == '0' and b.get('w_self_adjoint') == 'PASS' and b.get('header_readback') == 'EXACT',
                 f"build_failed_{b.get('geom')}")
            need(hx(b.get('hdr_sha256')) and hx(b.get('payload_merkle')), f"build_fields_malformed_{b.get('geom')}")
        sg = one(rs, 'P2_SINGLE', L=lat)
        need(sg is not None and nat(sg.get('bytes')) and int(sg['bytes']) > 4096 and hx(sg.get('store_sha256')),
             'single_store_row_missing_or_malformed')
        stores = [one(rs, 'P2_STORE', L=lat, geom=g) for g in SEGGEOMS]
        need(all(s is not None for s in stores), 'store_row_missing_or_duplicated')
        for s in stores:
            need(s.get('read_ok') == '1', f"store_read_failed_{s.get('geom')}")
            need(s.get('seglen') == SEGLEN[s.get('geom')] and nat(s.get('files'))
                 and s.get('prefix_equal_single') in ('0', '1') and s.get('tail_zero') in ('0', '1'),
                 f"store_fields_malformed_{s.get('geom')}")
    except Bad as e:
        return 'INCONCLUSIVE', str(e)
    diffs = []
    if not (tx['ymsec_sha256'] == tx['ymroom_sha256'] and tx['ymsec_bytes'] == tx['ymroom_bytes']):
        diffs.append('text_ymsec_vs_ymroom')
    if tx['ymsec_sha256'] != ANCHOR[lat]:
        diffs.append('text_vs_ci_anchor')
    if len({b['hdr_sha256'] for b in builds}) != 1 or len({b['payload_merkle'] for b in builds}) != 1:
        diffs.append('ymroomhdr_differs_across_geometries')
    for s in stores:
        if s['prefix_equal_single'] != '1':
            diffs.append(f"store_bytes_{s['geom']}_vs_single")
        if s['tail_zero'] != '1':
            diffs.append(f"stray_bytes_beyond_store_{s['geom']}")
    if diffs:
        return 'MISMATCH', ','.join(diffs)
    return 'AGREE', 'text_identical_anchor_equal_store_bytes_identical_single_G1_G2'


def cmp_bound(row, root):
    """Re-hash and parse the retained comparator stdout; the row must match it exactly."""
    need(row is not None, 'comparator_row_missing')
    need(row.get('verdict') in VERDICTS and row.get('exit') in ('0', '2'), 'comparator_row_malformed')
    need((row['verdict'] == 'AGREE') == (row['exit'] == '0'), 'comparator_exit_contract')
    rel = row.get('stdout_file', '')
    need(rel and not os.path.isabs(rel) and '..' not in rel.replace('\\', '/').split('/'), 'comparator_stdout_path')
    path = os.path.join(root, rel)
    need(os.path.isfile(path), 'comparator_stdout_missing')
    data = open(path, 'rb').read()
    need(hx(row.get('stdout_sha256')) and hashlib.sha256(data).hexdigest() == row['stdout_sha256'],
         'comparator_stdout_hash')
    lines = [x for x in data.decode('ascii', 'replace').replace('\r', '').split('\n') if x]
    vl = [x for x in lines if x.startswith('SCHUR_COMPARE_VERDICT|')]
    cl = [x for x in lines if x.startswith('SCHUR_COMPARE|')]
    need(len(vl) == 1 and len(cl) == 1, 'comparator_stdout_shape')
    need(vl[0] == f"SCHUR_COMPARE_VERDICT|thresholds=1|{row['verdict']}|json=0", 'comparator_stdout_verdict')
    need(f"|verdict={row['verdict']}|" in cl[0], 'comparator_stdout_record_verdict')
    return row['verdict']


def p3(rs, t, p2_merkle, root):
    core, s = THRESH[t]
    ts = str(t)
    amb = None
    try:
        merges = {}
        for side in ('shell', 'room'):
            c = one(rs, 'P3_CHUNKS', t=ts, side=side)
            need(c is not None, f'{side}_chunk_row_missing')
            need(c.get('S') == str(s) and c.get('present') == str(s) and c.get('exits_ok') == '1'
                 and c.get('partition_exact') == '1' and c.get('binding_equal') == '1' and c.get('core') == str(core),
                 f'{side}_chunk_integrity')
            m = one(rs, 'P3_MERGE', t=ts, side=side)
            need(m is not None and m.get('exit') in ('0', '2') and m.get('core') == str(core),
                 f'{side}_merge_failed_or_core_not_frozen')
            need(m.get('result') in ('PASS', 'FAIL', 'AMBIGUOUS') and nat(m.get('negative')) and nat(m.get('ambiguous')),
                 f'{side}_merge_fields_malformed')
            merges[side] = m
        mk = one(rs, 'P3_MERKLE', t=ts)
        need(mk is not None and mk.get('room_lines') == str(s) and mk.get('all_equal') == '1'
             and hx(p2_merkle) and mk.get('merkle') == p2_merkle, 'payload_merkle_not_bound_to_p2_store')
        inp = one(rs, 'P3_INPUTS', t=ts)
        need(inp is not None and inp.get('unchanged') == '1', 'inputs_changed_or_unverified')
        v2 = cmp_bound(one(rs, 'P3_CMP', t=ts, mode='v2'), root)
        cmp_bound(one(rs, 'P3_CMP', t=ts, mode='v1'), root)  # v1: reported verbatim, must be bound
    except Bad as e:
        return 'INCONCLUSIVE', str(e), None
    ms, mr = merges['shell'], merges['room']
    if ms['result'] == 'AMBIGUOUS' and mr['result'] == 'AMBIGUOUS':
        amb = f"shared_AMBIGUOUS_negative={ms['negative']}_ambiguous={ms['ambiguous']}_spectral_pass=0"
    if v2 == 'AGREE':
        return 'AGREE', 'v2_AGREE' + (f'|{amb}' if amb else ''), amb
    if v2 == 'MISMATCH':
        return 'MISMATCH', 'v2_MISMATCH', amb
    return 'INCONCLUSIVE', 'v2_INCONCLUSIVE', amb


def agg(vs):
    vs = list(vs)
    if 'INCONCLUSIVE' in vs:
        return 'INCONCLUSIVE'  # incomplete evidence takes precedence over a mismatch
    if 'MISMATCH' in vs:
        return 'MISMATCH'
    return 'AGREE'


def decide(lines, root):
    rs = rows(lines)
    out = []
    try:
        gates(rs, root)
        gate_why = None
    except Bad as e:
        gate_why = 'gate:' + str(e)
    p2v = {}
    for lat in LATTICES:
        v, why = p2(rs, lat) if gate_why is None else ('INCONCLUSIVE', gate_why)
        p2v[lat] = v
        out.append(f'SEGP2_VERDICT|L={lat}|verdict={v}|why={why}|spectral_pass=0|json=0')
    hdr = one(rs, 'P2_BUILD', L='3x3', geom='G1')
    merkle = hdr.get('payload_merkle') if hdr else None
    p3v = {}
    for t in THRESH:
        if gate_why is not None:
            v, why = 'INCONCLUSIVE', gate_why
        elif p2v['3x3'] != 'AGREE':
            v, why = 'INCONCLUSIVE', 'p2_3x3_store_not_AGREE'
        else:
            v, why, _ = p3(rs, t, merkle, root)
        p3v[t] = v
        out.append(f'SEGP3_VERDICT|t={t}|verdict={v}|why={why}|scope=G1_segmented_store|spectral_pass=0|json=0')
    out.append(f'SEGP2P3_VERDICT|P2={agg(p2v.values())}|P3={agg(p3v.values())}|t90_is_implementation_agreement_only=1'
               f'|P3_scope=G1_segmented_store_only|G2=P2_builder_bytes_only_not_runner_certified|spectral_pass=0'
               f'|binary_provenance=PASS(rebuild2)|gap_verdict_3x4=NONE|production_hold=UNCHANGED|json=0')
    return out


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: segp2p3_verdict.py EVIDENCE.hbp RUN_DIR')
    text = open(sys.argv[1], 'rb').read().decode('ascii', 'replace')
    sys.stdout.write(''.join(x + '\n' for x in decide(text.splitlines(), sys.argv[2])))
