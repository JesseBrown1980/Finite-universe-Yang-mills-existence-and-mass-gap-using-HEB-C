pgrep -a -x floorcert; echo "---"
S=/mnt/c/tmp/opus55/floor-v2-verify/scripts/reh.sh
bash $S A2 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 100/1
head -3 /root/floor-v2-verify/reh/A2/log/pincheck_1.txt; grep -E 'id=034|id=114|id=115|RESULT' /root/floor-v2-verify/reh/A2/log/pincheck_1.txt | cut -c1-200
