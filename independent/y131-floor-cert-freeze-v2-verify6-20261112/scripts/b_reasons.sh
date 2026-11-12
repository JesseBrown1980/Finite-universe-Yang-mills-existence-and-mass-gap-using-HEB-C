for f in B0 B1 B2 B3 B3b B4 B4b B5 B6 B6b B7; do echo "REASON|case=$f|rc=$(cat /root/floor-v6-verify/out/B/$f.rc 2>/dev/null)|$(grep -o 'reason=[a-zA-Z_.0-9]*' /root/floor-v6-verify/out/B/$f.out | grep -v 'reason=EVERY' | tail -1)|stop=$(grep -oE '(NOT_STARTED|early_stop|prelude)[^|]*' /root/floor-v6-verify/out/B/$f.out | tail -1 | cut -c1-120)|json=0"; done
echo "findmnt_nsfs=[$(findmnt -t nsfs)]"; echo "nsd_mounts=$(grep -c floor-v6-verify/nsd /proc/self/mountinfo)"; echo "host_floor_run=$(grep -c floor-run /proc/1/mountinfo)"
pgrep -af '[n]senter|[u]nshare|[r]un_floor' | head
