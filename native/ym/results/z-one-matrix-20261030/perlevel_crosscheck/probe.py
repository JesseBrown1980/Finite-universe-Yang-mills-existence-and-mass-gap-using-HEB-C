#!/usr/bin/env python3
"""Pre-registered three-per-level r/j propagation test; exact integer reference.

The dictionary names r and j; the R+R^2 and J matrix realizations are a
chosen MODEL, not a proven identity with the dictionary's semantics.
No physical dynamics are claimed. Python stdlib only, json=0 HBP output.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path

OUT = Path(__file__).resolve().parent
SIZES = range(1, 6)
I = ((1,0,0),(0,1,0),(0,0,1))
R = ((0,0,1),(1,0,0),(0,1,0))

def mm(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3))
                       for j in range(3)) for i in range(3))

def add(*matrices):
    return tuple(tuple(sum(a[i][j] for a in matrices)
                       for j in range(3)) for i in range(3))

def reduce3(mat):
    return tuple(tuple(a % 3 for a in row) for row in mat)

R2 = mm(R,R)
r = add(R,R2)
J = add(I,R,R2)
ZERO = ((0,0,0),)*3

def axis_step(v: list[int], axis: int, operator) -> list[int]:
    """Apply the 3x3 operator to the *selected* ternary address digit."""
    stride = 3**axis
    z = [0]*len(v)
    for group in range(0,len(v),3*stride):
        for within in range(stride):
            inds = [group+within+j*stride for j in range(3)]
            inp = [v[i] for i in inds]
            for k in range(3):
                z[inds[k]] = sum(operator[k][j]*inp[j] for j in range(3))
    return z

def leaf(i: int, digit: int) -> bytes:
    assert digit in (-1,0,1)
    return sha256(b'RJ-LEAF-v1|'+i.to_bytes(4,'big')+
                  digit.to_bytes(1,'big',signed=True)).digest()

def merkle(values: list[int]) -> bytes:
    nodes = [leaf(i, v) for i,v in enumerate(values)]
    while len(nodes)>1:
        if len(nodes)%2:
            nodes.append(nodes[-1])
        nodes = [sha256(b'RJ-NODE-v1|'+nodes[i]+nodes[i+1]).digest()
                 for i in range(0,len(nodes),2)]
    return nodes[0]

def model_run():
    rows = []
    marks = {}
    def check(pid, cond, detail):
        if not cond:
            marks[pid] = False
        else:
            marks.setdefault(pid, True)
        rows.append(f'RJ_CHECK|id={pid}|detail={detail}|ok={int(bool(cond))}|json=0')

    check('P1', mm(R,R2)==I and R2!=R and J==((1,1,1),)*3 and
          mm(J,R)==J and mm(R,J)==J,
          'R3_I,R2_Rinverse,J_IplusRplusR2,JR_RJ_J')
    e0 = [1,0,0]
    r_once = [sum(row[k]*e0[k] for k in range(3)) for row in r]
    j_once = [sum(row[k]*e0[k] for k in range(3)) for row in J]
    check('P2',r_once == [0,1,1] and j_once == [1,1,1] and J!=R2,
          f'r_impulse_{"".join(map(str,r_once))},j_impulse_{"".join(map(str,j_once))}')
    rows.append('RJ_LOCAL|r_support=2|j_support=3|r_keeps_source=0|j_keeps_source=1|steps=1|json=0')
    for n in SIZES:
        length=3**n
        target = sum(3**i for i in range(n))
        tracked=[]
        for kind,op in [('r',r),('j',J)]:
            v=[0]*length
            v[0]=1
            target_first=None
            for k in range(n+1):
                supp=sum(x!=0 for x in v)
                expected=(2 if kind=='r' else 3)**k
                check('P3', supp == expected,
                      f'levels_{n},operator_{kind},stage_{k},support_{supp},want_{expected}')
                if v[target] and target_first is None:
                    target_first=k
                rows.append(f'RJ_STAGE|levels={n}|operator={kind}|stage={k}|'
                            f'support={supp}|target_nonzero={int(v[target]!=0)}|json=0')
                if k<n:
                    v=axis_step(v,k,op)
            check('P3',target_first==n,
                  f'levels_{n},operator_{kind},target_first_{target_first},want_{n}')
            tracked.append((kind,v,target_first))
        v=[0]*length
        v[0]=1
        for axis in range(n):
            v=axis_step(v,axis,J)
        global_once = [1]*length  # (J tensor ... tensor J) applied once to delta[0]
        check('P4',v==global_once,
              f'levels_{n},global_tensor_J_support_{sum(x!=0 for x in v)},leaves_{length}')
        # Distinguish a global all-to-all operator from a sequence of N local-axis operations.
        probe = [((i*7+5)%3)-1 for i in range(length)]
        staged = probe[:] 
        for axis in range(n):
            staged = axis_step(staged,axis,J)
        direct = [sum(probe)]*length
        check('P4',staged==direct,
              f'levels_{n},global_direct_eq_staged_for_nontrivial_input_{int(staged==direct)}')
        check('P7',(target>n) if n>=2 else target==n,
              f'levels_{n},target_line_distance_{target},hierarchy_steps_{n}')
        rows.append(f'RJ_LEVEL|levels={n}|leaves={length}|target_address_ones={target}|'
                    f'r_reach={2**n}|j_reach={3**n}|r_first_target={n}|j_first_target={n}|'
                    f'line_distance={target}|json=0')
    j2=mm(J,J)
    j3=tuple(tuple(3*J[i][k] for k in range(3)) for i in range(3))
    check('P6',j2==j3 and reduce3(j2)==ZERO and J!=r and J!=R2,
          'J_squared_3J,mod3_zero,J_singular_distinct_from_r_Rinverse')
    rows.append('RJ_MOD3|J_squared_over_Z=3J|J_squared_over_GF3=ZERO|'
                'J_invertible=0|physical_instant_claim=0|json=0')

    n=5
    line_length=3**n
    d=line_length-1
    # Two equiprobable signed messages, 1D c=1 pulse. No sampling assumptions.
    for t in range(d+1):
        states=[]
        for signal in [-1,1]:
            cells=[0]*line_length
            cells[t]=signal
            global_root = merkle(cells)
            local_hash = leaf(d,cells[d])
            with_global = sha256(b'RJ-WITH-GLOBAL-v1|' + local_hash + global_root).digest()
            states.append((cells,global_root,local_hash,with_global))
        global_diff=int(states[0][1]!=states[1][1])
        local_diff=int(states[0][2]!=states[1][2])
        all_diff=int(states[0][3]!=states[1][3])
        check('P5',global_diff==1 and local_diff==int(t==d) and all_diff==1,
              f'line_tick_{t},distance_{d},global_diff_{global_diff},local_diff_{local_diff}')
        if t in (0,1,d-1,d):
            rows.append(f'RJ_LIGHT|tick={t}|distance={d}|root_message_info_millibits={global_diff*1000}|'
                        f'local_message_info_millibits={local_diff*1000}|'
                        f'global_annotation_info_millibits={all_diff*1000}|json=0')
    rows.append('RJ_BOUNDARY|nesting_operator_link=logical_nonlocal_on_1D_line|'
                'not_a_physical_c=1_update=1|global_hash_readability=privileged|json=0')
    for pid in ('P1','P2','P3','P4','P5','P6','P7'):
        rows.append(f'RJ_VERDICT|id={pid}|result={"PASS" if marks.get(pid) else "FAIL"}|json=0')
    overall='PASS' if all(marks.values()) and len(marks)==7 else 'FAIL'
    rows.append(f'RJ_TOTAL|predictions=7|passed={sum(marks.values())}|failed={7-sum(marks.values())}|'
                f'overall={overall}|physical_proof=0|rust_executed=0|json=0')
    return rows

if __name__=='__main__':
    expected=OUT/'PREREG.hbp.sha256'
    line=expected.read_text('ascii').split()[0]
    assert sha256((OUT/'PREREG.hbp').read_bytes()).hexdigest()==line, 'prereg changed'
    lines=model_run()
    (OUT/'RESULT.hbp').write_bytes(('\n'.join(lines)+'\n').encode('ascii'))
    print(lines[-1])
