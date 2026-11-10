git -C /root/floor-v2-verify/clone status --short | grep -v '^??'; echo "clean_check_done"
bash /mnt/c/tmp/opus55/floor-v2-verify/scripts/reh.sh F13 --test-r 12 --test-m0 7,8,13 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-hang 3:cert --test-census
grep -E '^(PREREQ|INVOKE\|seq=[0-9]+\|m0=13)' /root/floor-v2-verify/reh/F13.stdout | sed -E 's/\|argv=.*//' | cut -c1-220
grep -h -E '^(MEM|VERDICT)' /root/floor-v2-verify/reh/F13/log/m13_rowsonly.txt | cut -c1-200
grep -h -E '^(ROWHASH_ONLY|PEAK_RSS|GATE\|symmetry)' /root/floor-v2-verify/reh/F13/log/m13_rowhash.txt | cut -c1-220
