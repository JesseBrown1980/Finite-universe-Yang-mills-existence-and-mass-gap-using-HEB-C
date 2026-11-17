#!/usr/bin/env python3
"""#137 controlled exact original S3 QOQ Jacobi depth comparison.

Imports the source-authenticated whole-Q 8x8 effective-Wilson interval
calculator from Stage P (#273), changes ONLY the source Jacobi step count,
then recomputes all 64 matrix entries, complete shell4 residual Gram and
the accepted full physical energy window radii. Comparing the emitted
max_radius_per_trillion to the already accepted 20-step receipt tests
whether this specific source numerical refinement actually helps.

Each depth runs on its own GitHub Actions job; the physical first Wilson
weight and true flat eigendirection remain HOLD at every depth.
"""
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-eight-wilson-full-q-interval-20261117"))
import physical_wilson_matrix as stage_p

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ("40","60"):
        raise SystemExit("Y137_QOQ_DEPTH_REFUSE|allowed_steps=40,60|json=0")
    steps=int(sys.argv[1])
    original_steps=stage_p.source.ITER
    if original_steps!=20:
        raise SystemExit("Y137_QOQ_DEPTH_REFUSE|old_source_iteration_changed|json=0")
    stage_p.source.ITER=steps
    print("Y137_QOQ_DEPTH_FREEZE|parent_step=20|depth="+str(steps)+
          "|source_model=ORIGINAL_S3_FULL_Q|original_Wilson=SEVEN_LOOPS|json=0",flush=True)
    stage_p.run()
    print("Y137_QOQ_DEPTH_SCOPE|source_residual=FULL_SHELL4_INCLUDED"
          "|actual_true_flat_projectors=NOT_CERTIFIED"
          "|actual_Wilson_weight=HOLD|json=0",flush=True)

if __name__=="__main__":
    main()
