for i in $(seq 1 56); do grep -q '^PREREQ' /root/floor-v2-verify/reh/F13/log/run.log 2>/dev/null && break; sleep 3; done
ps -o etimes=,rss=,args= -C python3 | grep rows-only | cut -c1-40; grep -E '^PREREQ|FLOOR_RUN' /root/floor-v2-verify/reh/F13/log/run.log | cut -c1-200
