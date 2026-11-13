for f in B4 B4b B6; do echo "$f $(grep -o 'reason=[a-zA-Z_.]*' /root/floor-v5-verify/out/B/$f.out | tail -1)"; done
wc -l < /root/floor-v5-verify/neg/C.hbp
