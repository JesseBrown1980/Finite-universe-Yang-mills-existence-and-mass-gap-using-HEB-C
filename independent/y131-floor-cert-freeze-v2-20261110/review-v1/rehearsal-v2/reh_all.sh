#!/bin/bash
# rehearsals at excluded r only (test mode). Never the default mode.
D=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh
O=/root/floor-v2/reh
one() { name=$1; shift; rm -rf $O/$name $O/$name.stdout.txt; mkdir -p $O
  bash $D --test-out $O/$name "$@" > $O/$name.stdout.txt 2>&1; rc=$?
  echo "== $name rc=$rc"; grep -v '^FILE\|^CERTROW\|^INVOKE\|^PINCHECK|' $O/$name.stdout.txt | sed 's/|files=.*//' | cut -c1-700; }
case $1 in
 A1) one A1 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1045/10;;
 A2) one A2 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 100/1;;
 A3) one A3 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 110/1;;
 B1) one B1 --test-r 21/2 --test-m0 6,7 --test-f '4,3,2,1' --test-g0 95/1 --test-plant 1:993765/10000;;
 B2) one B2 --test-r 12 --test-m0 6,7 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-plant 2:1048542/10000;;
 C1) one C1 --test-r 12 --test-m0 7,8 --test-f '4,3,2,1' --test-g0 100/1 --test-crash 1:rowhash;;
 C2) one C2 --test-r 12 --test-m0 7,8 --test-f '4,3,2,1' --test-g0 100/1 --test-hang 1:cert;;
 C3) one C3 --test-r 12 --test-m0 7,8 --test-f '4,3,2,1' --test-g0 100/1 --test-crash 1:cert;;
 N9) one N9 --test-r 19/2 --test-m0 7 --test-f '4,3,2,1';;
 N13) one N13 --test-r 13 --test-m0 7 --test-f '4,3,2,1' --test-g0 100/1;;
 D1) one D1 --test-r 21/2 --test-m0 11 --test-g0 99/1 --test-census;;
esac
