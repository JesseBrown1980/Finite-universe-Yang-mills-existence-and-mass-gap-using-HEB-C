#!/bin/bash
cd /root/gl159/repo/independent/global-lock-20261110/measure
O=/mnt/c/tmp/opus55/gl159-refute/replay
mkdir -p $O
python3 -I gl_measure.py 3x3 27,81,243,729 > $O/levels-3x3.rows 2> $O/levels-3x3.err &
python3 -I gl_measure.py 3x4 27,81 k3plus=1 > $O/levels-3x4-k3plus.rows 2> $O/levels-3x4-k3plus.err &
python3 -I gl_measure.py 3x4 27,81,243,729 > $O/levels-3x4.rows 2> $O/levels-3x4.err &
wait
echo DONE > $O/DONE
