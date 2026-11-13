cd /root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
cp final/tools/run_floor.sh final/tools/floor_eval.py /mnt/c/tmp/opus55/floor-v2-final/
wc -l final/tools/*; ls final final/link
cd /root/floor-v2/repo; git diff cfc57bef 3b91d1a0 -- independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py > /mnt/c/tmp/opus55/floor-v2-final/tools.diff
wc -l /mnt/c/tmp/opus55/floor-v2-final/tools.diff
