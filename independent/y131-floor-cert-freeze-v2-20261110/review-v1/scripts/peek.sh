#!/bin/bash
S=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor/work/verify_opus55/smoke/cert_m7_r12_1_f4-3-2-1.txt
head -3 $S | cut -c1-700; wc -l $S; grep -v '^#' $S | sort -k3 -n | tail -2
