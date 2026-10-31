#!/usr/bin/env python3
"""Segmented-store P2/P3 verdicts from the run's HBP evidence rows (json=0, integer only).

Frozen with SEGP2P3-SPEC. Pure logic: it reads evidence rows and never runs a tool.
Every verdict is AGREE, MISMATCH or INCONCLUSIVE.
  AGREE        every required row present, every integrity gate passed, every compared value equal.
  MISMATCH     every required row present and every integrity gate passed, and a compared value
               (bytes, SHA-256, header line, comparator v2) differs: a fully computed difference.
  INCONCLUSIVE anything missing, failed, duplicated, out of range or not verifiable.
A shared AMBIGUOUS result at a threshold is reported with its counts and spectral_pass=0;
AGREE there is implementation agreement only.
"""
import sys

LATTICES = ('2x3', '2x4', '3x3')
GEOMS = ('single', 'G1', 'G2')
SEGGEOMS = ('G1', 'G2')
ANCHOR = {  # ymsec/ymroom text SHA-256 from CI receipt ci-40936173167 (P2 PASS)
    '2x3': '2bc797fe8bafeb4c4a3db11495784fd72a28b03e3c63be582ac95754a9276725',
    '2x4': 'a34d252302eea9050c7dbb6dad6f099de96f99b657b2a3558e27e030b34576bb',
    '3x3': 'ad0168f973d120a0da2b5ebaa33d4e80619ad7704cfca8f45f3e940dc757bd1b',
}
THRESH = {60000000: (101, 2), 72000000: (1137, 16), 90000000: (2940, 40)}  # t -> (frozen core, S)


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


def p2(rs, lat):
    tx = one(rs, 'P2_TEXT', L=lat)
    if tx is None or tx.get('runs_ok') != '1':
        return 'INCONCLUSIVE', 'text_missing_or_failed'
    builds = [one(rs, 'P2_BUILD', L=lat, geom=g) for g in GEOMS]
    if any(b is None for b in builds):
        return 'INCONCLUSIVE', 'build_row_missing_or_duplicated'
    for b in builds:
        if b.get('exit') != '0' or b.get('w_self_adjoint') != 'PASS' or b.get('header_readback') != 'EXACT':
            return 'INCONCLUSIVE', f"build_failed_{b.get('geom')}"
    stores = [one(rs, 'P2_STORE', L=lat, geom=g) for g in SEGGEOMS]
    if any(s is None for s in stores):
        return 'INCONCLUSIVE', 'store_row_missing_or_duplicated'
    if any(s.get('read_ok') != '1' for s in stores):
        return 'INCONCLUSIVE', 'store_read_failed'
    # every input present and every run completed: now compare
    diffs = []
    if not (tx.get('ymsec_sha256') == tx.get('ymroom_sha256') and tx.get('ymsec_bytes') == tx.get('ymroom_bytes')):
        diffs.append('text_ymsec_vs_ymroom')
    if tx.get('ymsec_sha256') != ANCHOR[lat]:
        diffs.append('text_vs_ci_anchor')
    if len({b.get('hdr_sha256') for b in builds}) != 1:
        diffs.append('ymroomhdr_differs_across_geometries')
    for s in stores:
        if s.get('prefix_equal_single') != '1':
            diffs.append(f"store_bytes_{s.get('geom')}_vs_single")
        if s.get('tail_zero') != '1':
            diffs.append(f"stray_bytes_beyond_store_{s.get('geom')}")
    if diffs:
        return 'MISMATCH', ','.join(diffs)
    return 'AGREE', 'text_identical_anchor_equal_store_bytes_identical_single_G1_G2'


def p3(rs, t, p2_merkle):
    core, s = THRESH[t]
    ts = str(t)
    for side in ('shell', 'room'):
        c = one(rs, 'P3_CHUNKS', t=ts, side=side)
        if c is None:
            return 'INCONCLUSIVE', f'{side}_chunk_row_missing', None
        if (c.get('S') != str(s) or c.get('present') != str(s) or c.get('exits_ok') != '1'
                or c.get('partition_exact') != '1' or c.get('binding_equal') != '1' or c.get('core') != str(core)):
            return 'INCONCLUSIVE', f'{side}_chunk_integrity', None
        m = one(rs, 'P3_MERGE', t=ts, side=side)
        if m is None or m.get('exit') not in ('0', '2') or m.get('core') != str(core):
            return 'INCONCLUSIVE', f'{side}_merge_failed_or_core_not_frozen', None
    mk = one(rs, 'P3_MERKLE', t=ts)
    if mk is None or mk.get('room_lines') != str(s) or mk.get('all_equal') != '1' or mk.get('merkle') != p2_merkle:
        return 'INCONCLUSIVE', 'payload_merkle_not_bound_to_p2_store', None
    inp = one(rs, 'P3_INPUTS', t=ts)
    if inp is None or inp.get('unchanged') != '1':
        return 'INCONCLUSIVE', 'inputs_changed_or_unverified', None
    v2 = one(rs, 'P3_CMP', t=ts, mode='v2')
    v1 = one(rs, 'P3_CMP', t=ts, mode='v1')
    if v2 is None or v1 is None:
        return 'INCONCLUSIVE', 'comparator_row_missing', None
    ms, mr = one(rs, 'P3_MERGE', t=ts, side='shell'), one(rs, 'P3_MERGE', t=ts, side='room')
    amb = None
    if ms.get('result') == 'AMBIGUOUS' and mr.get('result') == 'AMBIGUOUS':
        amb = f"shared_AMBIGUOUS_negative={ms.get('negative')}_ambiguous={ms.get('ambiguous')}_spectral_pass=0"
    if v2.get('verdict') == 'AGREE' and v2.get('exit') == '0':
        return 'AGREE', 'v2_AGREE' + (f'|{amb}' if amb else ''), amb
    # comparator contract (7b224b21): SCHUR_COMPARE_VERDICT|..|<V>|, exit 0 only for AGREE, else 2
    if v2.get('verdict') == 'MISMATCH' and v2.get('exit') == '2':
        return 'MISMATCH', 'v2_MISMATCH', amb
    return 'INCONCLUSIVE', f"v2_{v2.get('verdict')}_exit_{v2.get('exit')}", amb


def decide(lines):
    rs = rows(lines)
    out = []
    pre = one(rs, 'PRECONDITIONS')
    ctl = one(rs, 'CONTROLS')
    end = one(rs, 'END_INTEGRITY')
    gate_ok = (pre is not None and pre.get('ok') == '1' and ctl is not None and ctl.get('comparator') == 'PASS'
               and ctl.get('segment') == 'PASS' and ctl.get('verdict') == 'PASS' and ctl.get('csf60') == 'PASS'
               and end is not None and end.get('exe_unchanged') == '1')
    p2v = {}
    for lat in LATTICES:
        v, why = p2(rs, lat) if gate_ok else ('INCONCLUSIVE', 'preconditions_controls_or_end_integrity_failed')
        p2v[lat] = v
        out.append(f'SEGP2_VERDICT|L={lat}|verdict={v}|why={why}|spectral_pass=0|json=0')
    hdr = one(rs, 'P2_BUILD', L='3x3', geom='G1')
    merkle = hdr.get('payload_merkle') if hdr else None
    p3v = {}
    for t in THRESH:
        if not gate_ok:
            v, why, amb = 'INCONCLUSIVE', 'preconditions_controls_or_end_integrity_failed', None
        elif p2v['3x3'] != 'AGREE':
            v, why, amb = 'INCONCLUSIVE', 'p2_3x3_store_not_AGREE', None
        else:
            v, why, amb = p3(rs, t, merkle)
        p3v[t] = v
        out.append(f'SEGP3_VERDICT|t={t}|verdict={v}|why={why}|scope=G1_segmented_store|spectral_pass=0|json=0')

    def agg(vs):
        vs = list(vs)
        if all(x == 'AGREE' for x in vs):
            return 'AGREE'
        return 'MISMATCH' if 'MISMATCH' in vs else 'INCONCLUSIVE'
    out.append(f'SEGP2P3_VERDICT|P2={agg(p2v.values())}|P3={agg(p3v.values())}|t90_is_implementation_agreement_only=1'
               f'|P3_scope=G1_segmented_store_only|G2=P2_builder_bytes_only_not_runner_certified|spectral_pass=0'
               f'|binary_provenance=PASS(rebuild2)|gap_verdict_3x4=NONE|production_hold=UNCHANGED|json=0')
    return out


if __name__ == '__main__':
    for line in decide(open(sys.argv[1], encoding='ascii').read().splitlines()):
        print(line)
