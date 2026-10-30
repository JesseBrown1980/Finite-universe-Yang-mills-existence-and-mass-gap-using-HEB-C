#!/usr/bin/env python3
"""Three independent ternary rotations versus three on a single digit."""
from itertools import product
from pathlib import Path

def main():
    combos = list(product(range(3), repeat=3))
    held = [tuple(a) for a in combos]  # rotate digit i by a_i mod 3, all initially zero
    collapsed = [((sum(a) % 3), 0, 0) for a in combos]
    held_distinct = len(set(held))
    collapsed_distinct = len(set(collapsed))
    start=(0,0,0)
    returns=sum(h==start for h in held)
    triple_plus_held=(1,1,1)
    triple_plus_collapsed=((1+1+1)%3,0,0)
    multiplicities={s: collapsed.count(s) for s in set(collapsed)}
    assert len(combos)==27 and held_distinct==27 and collapsed_distinct==3
    assert returns==1 and all(v==9 for v in multiplicities.values())
    assert triple_plus_held != start and triple_plus_collapsed == start
    lines=[
      "A_MODEL|levels=3|states_per_level=3|turns_per_level=0,1,2|total_combinations=27|start=0,0,0|json=0",
      f"A_HELD|combos=27|distinct={held_distinct}|returns_start={returns}|never_returns_start={int(returns==0)}|json=0",
      f"A_COLLAPSED|combos=27|distinct={collapsed_distinct}|preimages_per_state={','.join(str(v) for v in sorted(multiplicities.values()))}|json=0",
      f"A_TRIPLE_PLUS|held_state={','.join(map(str,triple_plus_held))}|collapsed_state={','.join(map(str,triple_plus_collapsed))}|held_returns_start={int(triple_plus_held==start)}|collapsed_returns_start={int(triple_plus_collapsed==start)}|json=0",
      "A_VERDICT|original_held_27_distinct=PASS|original_held_never_returns_start=FAIL|original_collapsed_only_3=PASS|three_plus_one_same_level_returns=PASS|overall_original=FAIL|qualified_nonzero_triple_plus_holds=PASS|json=0"
    ]
    Path(__file__).with_name("RESULT.hbp").write_text("\n".join(lines)+"\n",encoding="ascii")
    print(lines[-1])
if __name__=="__main__":main()
