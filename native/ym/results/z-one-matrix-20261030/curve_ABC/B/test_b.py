#!/usr/bin/env python3
"""Independent integer model B; statements frozen in ../PREREG.hbp first."""
from pathlib import Path

def sign_rotation(delta):
    return {0: 1, 1: 1, 2: -1}[delta]

def j_level(vector, n, level, asym=True):
    m = 3 ** n
    a = 3 ** (level - 1)
    out = [0] * m
    for src, v in enumerate(vector):
        if not v:
            continue
        digit = (src // a) % 3
        for new_digit in range(3):
            dest = src + (new_digit - digit) * a
            coeff = sign_rotation((new_digit - digit) % 3) if asym else 1
            out[dest] += v * coeff
    return out

def j_first(n, src, asym=True):
    m = 3 ** n
    state = [0] * m
    state[src] = 1
    first = [-1] * m
    first[src] = 0
    block_ok = True
    for level in range(1, n + 1):
        state = j_level(state, n, level, asym)
        size = 3 ** level
        for i, x in enumerate(state):
            block_ok &= (x != 0) == (i // size == src // size)
            if x and first[i] == -1:
                first[i] = level
    return state, first, block_ok

def top_diff(x, y, n):
    answer = 0
    for l in range(1, n + 1):
        if x % 3 != y % 3:
            answer = l
        x //= 3
        y //= 3
    return answer

def ring_r_first(n, src):
    m = 3 ** n
    reach = {src}
    first = [-1] * m
    first[src] = 0
    for tick in range(1, (m // 2) + 2):
        reach = {z for x in reach for z in ((x - 1) % m, (x + 1) % m)}
        for z in reach:
            if first[z] == -1:
                first[z] = tick
    return first

def main():
    out = ["B_MODEL|asym=I+R-R2|baseline=I+R+R2|r=R+Rinverse|n=1..5|signed=1|json=0"]
    # The three by three matrix is columns=inputs, rows=outputs
    ja = [[sum(sign_rotation((row - col) % 3) for k in [0]) for col in range(3)] for row in range(3)]
    js = [[1] * 3 for _ in range(3)]
    r = [[int((row-col)%3 in (1,2)) for col in range(3)] for row in range(3)]
    r_sym = all(r[i][j] == r[j][i] for i in range(3) for j in range(3))
    asym = any(ja[i][j] != ja[j][i] for i in range(3) for j in range(3))
    support = all(sum(ja[i][j] != 0 for i in range(3)) == 3 for j in range(3))
    assert r_sym and asym and support and all(x==1 for row in js for x in row)
    out.append(f"B_MATRIX|r_symmetric={int(r_sym)}|j_asymmetric={int(asym)}|j_support3={int(support)}|j_signed_rows={';'.join(','.join(map(str,row)) for row in ja)}|json=0")
    all_five = True
    baseline_all_plus = True
    signed_all_plus = True
    for n in range(1,6):
        m = 3**n
        local_ok = True
        per_source_all = True
        block_ok = True
        jmax = 0
        for src in range(m):
            state, first, bok = j_first(n, src, True)
            bstate, bfirst, bbok = j_first(n, src, False)
            assert bbok and bfirst == first
            local_ok &= all(first[i] == top_diff(src, i, n) for i in range(m))
            block_ok &= bok
            per_source_all &= all(z != 0 for z in state)
            signed_all_plus &= all(z == 1 for z in state)
            baseline_all_plus &= all(z == 1 for z in bstate)
            jmax = max(jmax, max(first))
        r_first = ring_r_first(n,0)
        rmax = max(r_first)
        q6 = n == 1 or (ring_r_first(n, 3**(n-1)-1)[3**(n-1)] == 1 and j_first(n,3**(n-1)-1)[1][3**(n-1)] == n)
        good = all([local_ok,block_ok,per_source_all,q6,jmax==n,rmax==(m-1)//2])
        all_five &= good
        out.append(f"B_LEVEL|N={n}|sites={m}|j_max={jmax}|r_max={rmax}|single_source_support_all={int(per_source_all)}|block_prefix_exact={int(block_ok)}|top_digit_first_tick={int(local_ok)}|Q6_same={int(q6)}|predictions_preserved={int(good)}|json=0")
    # Two positive source pulses in distinct input positions cancel at target 0.
    c = j_level([1,1,0],1,1,True)
    cancellation = c[0] == 0
    assert cancellation
    assert baseline_all_plus and not signed_all_plus and all_five
    out.append(f"B_SUPERPOSITION|input=1,1,0|output={','.join(map(str,c))}|target0_cancels={int(cancellation)}|single_source_only_reach_scope=1|json=0")
    out.append(f"B_VERDICT|r_symmetric={int(r_sym)}|j_asymmetric={int(asym)}|j_support3={int(support)}|Q1_Q2_Q3_Q4_Q6_preserved={int(all_five)}|Q5_original_equal_all_ones={int(signed_all_plus)}|Q5_changed={int(not signed_all_plus)}|signed_superposition_cancels={int(cancellation)}|overall_prediction=PASS|json=0")
    Path(__file__).with_name("RESULT.hbp").write_text("\n".join(out)+"\n",encoding="ascii")
    print(out[-1])
if __name__=="__main__": main()
