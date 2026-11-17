#!/usr/bin/env python3
"""Read-only binding-candidate overlay on the unchanged 96-pixel Big Bang pilot."""
import os
import sys
from hashlib import sha256

HERE=os.path.dirname(os.path.abspath(__file__))
PARENT=os.path.abspath(os.path.join(HERE,'..','y137-finite-bigbang-mtp-20261117'))
sys.path.insert(0,PARENT)
import pilot as original
sys.path.insert(0,HERE)
import derive_binding as micro

SLICES=(1,3,6,12,18,24,36,48)
DIRECTIONS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def emit(tag,**values):
    print(tag+'|'+'|'.join(str(k)+'='+str(v) for k,v in values.items())+'|json=0')

def candidate_counts(pixels):
    cells={p.pos for p in pixels}
    free_dirs={c:sum(int(original.add(c,d) not in cells) for d in DIRECTIONS)
               for c in cells}
    result={'overlap':0,'adjacent':0,'bind':0,'separate':0,'tie':0,'cross_sector':0}
    for i,p in enumerate(pixels):
        for j in range(i+1,len(pixels)):
            q=pixels[j]
            d=original.dist(p.pos,q.pos)
            if d>1:
                continue
            if d==0:
                result['overlap']+=1
            else:
                result['adjacent']+=1
            result['cross_sector']+=int(p.sector!=q.sector)
            g=max(1,min(6,free_dirs[p.pos],free_dirs[q.pos]))
            E=min(24,(p.temp+q.temp)//2)
            label=micro.gate(24,E,g)
            result[{'BIND_FAVORED':'bind','SEPARATE_FAVORED':'separate',
                    'EQUAL':'tie'}[label]]+=1
    assert result['bind']+result['separate']+result['tie']==result['overlap']+result['adjacent']
    return result

def main():
    pixels=original.seed()
    radius=original.START_R
    reservoir=0
    totals={'err_injected':0,'err_corrected':0,'err_escaped':0,'expansion':0}
    source_key=original.h(original.snapshot_key(pixels,0,radius,reservoir,0))
    emit('OVERLAY_SOURCE',original_physical_pixels=len(pixels),
         initial_source_sha256=source_key,bath_modes_per_pair=24,
         overlap_criterion='MANHATTAN_DISTANCE_ZERO_OR_ONE',
         source_dynamics_modified='NO',status='PASS')
    frames=[]
    for t in range(48):
        pixels,radius,reservoir,receipt=original.step_slice(pixels,t,radius,reservoir,0,True)
        for key in totals:
            totals[key]+=receipt[key]
        if t+1 in SLICES:
            val=candidate_counts(pixels)
            frames.append((t+1,val['bind'],val['separate'],val['tie'],val['overlap'],val['adjacent']))
            emit('OVERLAY_SLICE',t=t+1,active_address_cells=(2*radius+1)**3,
                 physical_pixels=len(pixels),overlap_pairs=val['overlap'],
                 adjacent_pairs=val['adjacent'],
                 binding_preferred_pairs=val['bind'],
                 separation_preferred_pairs=val['separate'],
                 equal_preference_pairs=val['tie'],
                 cross_sector_pairs=val['cross_sector'],
                 original_source_state_sha256=receipt['result'])
    assert (radius,reservoir)==(6,1728)
    assert (totals['err_injected'],totals['err_corrected'],totals['err_escaped'])==(84,77,7)
    assert totals['expansion']==2072
    emit('OVERLAY_FINAL',evaluated_slices=len(frames),
         archived_original_signature='96_PIXELS_48_TICKS_R6_84_77_7',
         derived_binding_inequality='R_MINUS_E_GT_G_TIMES_E_PLUS_ONE',
         source_dynamics_modified='NO',binding_is_merely_candidate_readout='YES',
         spontaneous_Big_Loop='NOT_DERIVED',
         original_S3_Hamiltonian='UNMODIFIED',original_Wilson_first_weight='HOLD',
         sha256=sha256(repr(frames).encode('ascii')).hexdigest(),status='PASS')

if __name__=='__main__':
    main()
