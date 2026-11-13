grep -E 'm0=13' /root/floor-v2-verify/reh/F13/log/run.log | sed -E 's/\|argv=.*//' | cut -c1-220
ps -o etimes=,rss=,args= -C python3 | cut -c1-150
grep -h -E '^(ROWHASH_ONLY|PEAK_RSS)' /root/floor-v2-verify/reh/F13/log/m13_rowhash*.txt 2>/dev/null | cut -c1-200
