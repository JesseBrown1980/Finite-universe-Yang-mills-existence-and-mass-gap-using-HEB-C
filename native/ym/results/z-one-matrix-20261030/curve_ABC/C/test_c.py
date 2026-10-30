#!/usr/bin/env python3
"""Compare the externally inspected, pinned GitHub evidence. No live API access."""
from pathlib import Path
from datetime import datetime
f = Path(__file__).with_name('EVIDENCE.hbp')
lines = f.read_text(encoding='ascii').splitlines()
def find(tag,field,value):
    a=[]
    for row in lines:
        pieces=row.split('|')
        if pieces[0]!=tag: continue
        d=dict(x.split('=',1) for x in pieces[1:] if '=' in x)
        if d.get(field)==value:a.append(d)
    assert len(a)==1
    return a[0]
early=find('C_COMMIT','role','first_substantive_dictionary')
later=find('C_COMMIT','role','first_committed_verses_in_reviewed_history')
t0=datetime.fromisoformat(early['created_utc'].replace('Z','+00:00'))
t1=datetime.fromisoformat(later['created_utc'].replace('Z','+00:00'))
delta=int((t1-t0).total_seconds())
assert delta == 3327
for fname in ['README.md','index.html']:
    old=[
        dict(x.split('=',1) for x in row.split('|')[1:] if '=' in x)
        for row in lines if row.startswith('C_BLOB|') and f'|path={fname}|' in row
    ]
    assert len(old)==2
    assert old[0]['f_from']==old[0]['m_intelligence']=='1'
    assert old[0]['father']==old[0]['mother']==old[0]['verses_section']=='0'
    assert old[1]['father']==old[1]['mother']==old[1]['verses_section']=='1'
out=(f'C_VERDICT|commit_order=PASS|first_letters_commit={early["sha"]}|'
     f'first_verses_commit={later["sha"]}|interval_seconds={delta}|'
     'spoken_order=INCONCLUSIVE|replay_mode=pinned_externally_retrieved_metadata|json=0\n')
Path(__file__).with_name('RESULT.hbp').write_text(out,encoding='ascii')
print(out.strip())
