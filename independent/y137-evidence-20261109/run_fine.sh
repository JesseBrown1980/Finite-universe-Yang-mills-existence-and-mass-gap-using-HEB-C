#!/usr/bin/env bash
cd /mnt/c/tmp/opus55/ym137-fable5-20261109
G=$(seq -s, 69930 2 69990)
for s in 4 8 16; do python3 -I -B sector_split.py $s $G 1000 > run-fine-steps$s.out 2>&1; echo "steps=$s rc=$?"; done
