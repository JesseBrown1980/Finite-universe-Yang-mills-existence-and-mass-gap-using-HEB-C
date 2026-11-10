for i in $(seq 1 190); do grep -q '^PREREQ' /root/floor-v2-verify/reh/F13/log/run.log 2>/dev/null && break; sleep 3; done
bash /mnt/c/tmp/opus55/floor-v2-verify/scripts/st13.sh | grep -vE '^(ROWHASH_ONLY|PEAK_RSS)'
