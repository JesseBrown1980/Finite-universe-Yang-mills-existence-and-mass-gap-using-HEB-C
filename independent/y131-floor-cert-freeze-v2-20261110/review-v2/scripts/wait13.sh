for i in $(seq 1 190); do grep -qE '^PREREQ|kind=rowsonly' /root/floor-v2-verify/reh/F13/log/run.log 2>/dev/null && break; sleep 3; done
grep -E 'kind=rowhash.*m0=13|m0=13\|kind=rowhash|PREREQ|kind=rowsonly' /root/floor-v2-verify/reh/F13/log/run.log | sed -E 's/\|argv=.*//' | cut -c1-200
grep -h -E '^(ROWHASH_ONLY|PEAK_RSS)' /root/floor-v2-verify/reh/F13/log/m13_rowhash*.txt 2>/dev/null | cut -c1-200
