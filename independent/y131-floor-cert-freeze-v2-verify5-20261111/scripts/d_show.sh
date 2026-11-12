V=/root/floor-v5-verify
cat $V/out/D13.start $V/out/D13.exit $V/out/D13.sampler
grep -E '^(STEP|DECISION|CERTROW|LIMIT|PREREQ|PUBLISH|INVOKE)' $V/out/D13.stdout.txt | grep -E 'm0=13|PUBLISH|LIMIT' | cut -c1-300
grep -E '^(PEAK|MEM)' $V/out/D13/log/*m13* 2>/dev/null | cut -c1-200 | head
tail -1 $V/out/D13.stdout.txt | cut -c1-500
