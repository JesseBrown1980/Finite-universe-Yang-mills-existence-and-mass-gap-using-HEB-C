#!/usr/bin/env python3
"""Exact finite six-pyramid seed/cooling/MTP/Hilbert-address Big-Loop pilot.

This is a deterministic RULE DEMONSTRATION, not measured cosmological physics.
All positions/counters/thermal energy are integers; no continuous spacetime.
Original 3x4 S3 Hamiltonian and accepted Wilson sources are not modified.
"""
from hashlib import sha256
from collections import Counter, namedtuple
from math import gcd

SECTORS = ((0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1))
N = 96
TMAX = 18
RMAX = 48
START_R = 2
HOT = 11
WARM = 5
CORE_CELL_CAP = 12
CORESHELL = 2
CORE_TRIGGER = 72


def emit(tag, **kw):
    print(tag + '|' + '|'.join(str(k) + '=' + str(v) for k, v in kw.items()) + '|json=0')


def h(obj):
    return sha256(repr(obj).encode('ascii')).hexdigest()


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def dist(a, b):
    return sum(abs(a[i] - b[i]) for i in range(3))


def radial(a):
    return sum(abs(x) for x in a)


def sector_of(a):
    if a == (0, 0, 0):
        return -1
    axis = max(range(3), key=lambda i: (abs(a[i]), -i))
    return 2 * axis + (0 if a[axis] > 0 else 1)


def step_at_axis(axis, sign):
    v = [0, 0, 0]
    v[axis] = sign
    return tuple(v)


Pixel = namedtuple('Pixel', 'pid pos sector temp clock errors residual locked', defaults=(0,0,0,False))


def snapshot_key(ps, t, radius, vacuum, epoch):
    return (t, radius, vacuum, epoch, tuple((p.pid, p.pos, p.sector,
          p.temp, p.clock, p.errors, p.residual, int(p.locked)) for p in ps))


def seed():
    ps = tuple(Pixel(i, (0, 0, 0), i % 6, TMAX) for i in range(N))
    assert all(p.pos == (0, 0, 0) and p.temp == TMAX for p in ps)
    assert Counter(p.sector for p in ps) == Counter({i: N // 6 for i in range(6)})
    return ps


def desired_delta(p, t, ps):
    axis, sign = SECTORS[p.sector]
    if p.temp >= HOT:
        # Two primary-axis strides and one sideways stride per ternary phase.
        mode = (t + p.pid // 6) % 3
        if mode < 2:
            return step_at_axis(axis, sign)
        side = (axis + 1 + (p.pid // 6) % 2) % 3
        sideways = 1 if (p.pid // 12) % 2 == 0 else -1
        # Never reverse radially while hot.
        if p.pos[side] != 0 and (p.pos[side] > 0) != (sideways > 0):
            sideways = -sideways
        return step_at_axis(side, sideways)
    if p.temp >= WARM:
        return step_at_axis(axis, sign) if t % 2 == 0 else (0, 0, 0)
    # Global catalog has all pixels; lower temperature enables attraction
    # toward the common centroid. It is a proposed hypothesis, not gravity.
    sx = [sum(other.pos[i] for other in ps) for i in range(3)]
    target = tuple((sx[i] - p.pos[i]) // (len(ps) - 1) for i in range(3))
    diffs = [target[i] - p.pos[i] for i in range(3)]
    ix = max(range(3), key=lambda i: (abs(diffs[i]), -i))
    if diffs[ix] == 0:
        return (0, 0, 0)
    return step_at_axis(ix, 1 if diffs[ix] > 0 else -1)


def within(p, R):
    return all(-R <= z <= R for z in p.pos)


def step_slice(ps, t, R, vacuum, epoch, inject_errors):
    """All shell agents read the same IMMUTABLE source, commit one new slice."""
    assert len(ps) == N and all(within(p, R) for p in ps)
    assert sum(p.temp for p in ps) + vacuum == N*TMAX
    before = h(snapshot_key(ps, t, R, vacuum, epoch))
    occupancy = Counter(p.pos for p in ps)
    moves = []
    err_injected = 0
    corrected = 0
    escaped = 0
    for p in ps:
        delta = desired_delta(p, t, ps)
        assert radial(delta) in (0, 1)
        corruption = inject_errors and delta != (0, 0, 0) and (p.pid*17 + t*31 + p.sector) % 47 == 0
        if corruption:
            err_injected += 1
            intended = delta
            delta = tuple(-x for x in delta)
            # MTP3 validates the immediate prediction; MTP27 independently
            # validates shell context. Some planted errors escape both checks.
            detect3 = (p.pid+t) % 3 != 0
            detect27 = (p.pid+t) % 5 != 0
            if detect3 or detect27:
                corrected += 1
                # At maximum/high temperature, a caught error falls back
                # to the legal outward move: no sub-c pause at the hot gate.
                delta = intended if p.temp >= HOT else (0, 0, 0)
            else:
                escaped += 1
        moves.append((p, delta, int(corruption), int(corruption and delta == (0, 0, 0))))
    # Atomic conflict resolution: no destination oversubscribed in cold locked phase.
    destinations = Counter()
    accepted = []
    braking = 0
    for p, delta, is_err, paused in moves:
        v = add(p.pos, delta)
        if p.temp <= 2 and occupancy[v] + destinations[v] >= CORE_CELL_CAP and v != p.pos:
            v = p.pos
            delta = (0, 0, 0)
            braking += 1
        destinations[v] += 1
        assert dist(p.pos, v) <= 1
        if p.temp >= HOT:
            assert dist(p.pos, v) == 1
        accepted.append((p, v, delta, is_err, paused))
    needed_R = max(max(abs(z) for z in v) for _, v, _, _, _ in accepted)
    new_R = max(R, needed_R)
    assert new_R <= RMAX
    expansion = (2*new_R+1)**3-(2*R+1)**3
    next_ps=[]
    cooling_total=0
    for p, v, delta, is_err, paused in accepted:
        # Cooling increases with radial separation; heat transfers into a
        # counted vacuum reservoir rather than vanishing from the ledger.
        cool = 1 + (radial(v) // 6)
        newtemp = max(0, p.temp-cool)
        cooling_total += p.temp-newtemp
        newclock = p.clock + int(not paused)
        newresidual = p.residual + int(is_err and not paused)
        next_ps.append(p._replace( pos=v, temp=newtemp, clock=newclock,
                               errors=p.errors+is_err, residual=newresidual,
                               locked=(newtemp == 0 and occupancy[v] >= CORE_CELL_CAP)))
    next_ps = tuple(next_ps)
    newvac=vacuum+cooling_total
    assert sum(p.temp for p in next_ps)+newvac == N*TMAX
    assert all(within(p,new_R) for p in next_ps)
    after=h(snapshot_key(next_ps,t+1,new_R,newvac,epoch))
    return next_ps,new_R,newvac,{
        'source':before,'result':after,'expansion':expansion,
        'err_injected':err_injected,'err_corrected':corrected,
        'err_escaped':escaped,'brakes':braking,
        'moved':sum(int(old.pos!=new.pos) for old,new in zip(ps,next_ps)),
        'core_count':sum(int(radial(p.pos)<=CORESHELL) for p in next_ps),
        'vacuum':newvac,'cooling':cooling_total,
    }


def isometry_toy():
    # Exact 2-component amplitudes 3/5 and 4/5; append one vacuum trit.
    before = {1:(3,5),4:(4,5)}
    after = {k*3:v for k,v in before.items()}
    assert len(after)==len(before)
    assert 3*3+4*4 == 25
    assert set(after)=={3,12} and set(before)=={1,4}
    return h((tuple(sorted(before.items())),tuple(sorted(after.items()))))


def test_regions():
    counts = Counter(sector_of((i,j,k)) for i in range(-2,3)
                     for j in range(-2,3) for k in range(-2,3) if (i,j,k)!=(0,0,0))
    assert len(counts)==6 and sum(counts.values())==124
    for axis in range(3):
        assert sector_of(step_at_axis(axis,1))==2*axis
        assert sector_of(step_at_axis(axis,-1))==2*axis+1
    for s in range(0,6,2):
        assert SECTORS[s][0]==SECTORS[s+1][0]
        assert SECTORS[s][1]==-SECTORS[s+1][1]
    return counts


def main():
    counts=test_regions()
    assert 3200*8 == 2560*10 # tuple byte/glyph bit equivalence
    assert N == 6*16
    iso=isometry_toy()
    emit('BANG_INIT',pixels=N,initial_temp=TMAX,seed_xyz='0:0:0',
         six_pyramids='PLUS_MINUS_X_Y_Z',samples_in_cube=sum(counts.values()),
         active_R=START_R,max_R=RMAX,capacity_cells=(2*START_R+1)**3,
         signed_baryon_channels='THREE_OPPOSITE_PAIRS_HYPOTHESIS',
         tuple_equivalence='3200_BYTES_TO_2560_BASE1024_SYMBOLS',
         hilbert_injection_isometric='EXACT_TOY_PASS',isometry_sha256=iso,
         original_S3_Wilson='HOLD')
    ps=seed()
    R=START_R
    vacuum=0
    totals=Counter()
    max_core=0
    record=[]
    for tick in range(48):
        ps,R,vacuum,rec=step_slice(ps,tick,R,vacuum,0,True)
        max_core=max(max_core,sum(int(radial(p.pos)<=CORESHELL and p.temp<=2) for p in ps))
        for field in ['err_injected','err_corrected','err_escaped','brakes','moved','expansion']:
            totals[field]+=rec[field]
        record.append((tick,rec))
        if tick in (0,2,5,9,15,23,35,47) or rec['expansion']:
            phases=Counter('HOT' if p.temp>=HOT else 'WARM' if p.temp>=WARM else 'COLD' for p in ps)
            emit('BANG_SLICE',t=tick+1,R=R,active_cells=(2*R+1)**3,
                 extra_vacuum_cells=rec['expansion'],
                 hot=phases['HOT'],warm=phases['WARM'],cold=phases['COLD'],
                 core_count=rec['core_count'],moving=rec['moved'],
                 err_injected=rec['err_injected'],err_corrected=rec['err_corrected'],
                 err_escaped=rec['err_escaped'],vacuum_energy=vacuum,
                 source_sha256=rec['source'],result_sha256=rec['result'])
    assert all(p.clock <= 48 for p in ps)
    assert sum(p.temp for p in ps)+vacuum==N*TMAX
    assert sum(p.errors for p in ps)==totals['err_injected']
    ratios=[(s,min(p.clock for p in ps if p.sector==s),
               max(p.clock for p in ps if p.sector==s),
               sum(p.errors for p in ps if p.sector==s)) for s in range(6)]
    assert totals['expansion'] == (2*R+1)**3-(2*START_R+1)**3
    emit('BANG_MAIN',ticks=48,final_R=R,active_cells=(2*R+1)**3,
         added_addressed_vacuum_cells=totals['expansion'],
         physical_pixels=N,errors_planted=totals['err_injected'],
         errors_corrected=totals['err_corrected'],errors_escaped=totals['err_escaped'],
         motor_brakes=totals['brakes'],max_cold_core_count=max_core,
         six_sector_local_clock_spans=repr(ratios).replace(' ','') ,
         total_energy=N*TMAX,final_vacuum_energy=vacuum,
         norm_preserving_embed='PROVED_BY_INJECTION_IN_TOY',
         per_pixel_max_speed='C_EQ_1_PASS',
         end_sha256=h(snapshot_key(ps,48,R,vacuum,0)))
    # Separate controllable Big Loop threshold test: cold dense center is
    # supplied as a preset. Collapse/reheat is never claimed to arise from
    # the cooling run unless it actually meets CORE_TRIGGER.
    core=tuple(p._replace(pos=(0,0,0),temp=0,clock=0,errors=0,
                       residual=0,locked=True) for p in seed())
    reserve=N*TMAX
    assert sum(p.temp for p in core)+reserve==N*TMAX
    count_core=sum(int(radial(p.pos)<=CORESHELL) for p in core)
    assert count_core>=CORE_TRIGGER
    # Big Loop: state recompile (table-level) uses previously banked energy.
    # No particle jumps; the next slice alone implements c=1 outward steps.
    reheat_needed=N*TMAX-sum(p.temp for p in core)
    assert reserve>=reheat_needed
    reserve-=reheat_needed
    loop=tuple(p._replace(temp=TMAX,locked=False) for p in core)
    assert h(tuple(p.pos for p in loop))==h(tuple(p.pos for p in core))
    assert sum(p.temp for p in loop)+reserve==N*TMAX
    loop,R2,res2,rc=step_slice(loop,0,START_R,reserve,1,False)
    assert sum(p.temp for p in loop)+res2==N*TMAX
    assert all(radial(p.pos)<=1 for p in loop)
    emit('BANG_LOOP',source='PRESET_DENSE_COLD_CORE',trigger=count_core,
         required_min=CORE_TRIGGER,zero_teleport='PASS',reheated_pixel_count=N,
         energy_reused_from_vacuum=N*TMAX,
         first_new_slice_moved=rc['moved'],c_eq_1='PASS',
         energy_ledger='EXACT',result_sha256=rc['result'],
         spontaneous_global_recollapse='NOT_DERIVED')
    # Counterexample to naive SHA inversion: there are 2^257 possible
    # 257-bit states and only 2^256 SHA-256 strings; not injective.
    assert 2**257>2**256
    emit('BANG_COMPLEXITY',one_global_state='FINITE',
         forward_hash='REPLAYABLE_FROM_FULL_STATE_AND_RULE',
         digest_to_arbitrary_state='NONINJECTIVE_FOR_257_BIT_STATE',
         P_equals_NP='NOT_IMPLIED',full_quantum_dynamics='NOT_PROVED',
         S3_original_gap='UNCHANGED',S3_Wilson_first_weight='HOLD',
         continuum='OPEN',status='EXACT_INTEGER_MODEL_PASS')

if __name__=='__main__':
    main()

