P=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110/work/design/peak_rss.py
mkdir -p /root/floor-v2-verify/pg; cp /bin/sleep /root/floor-v2-verify/pg/zzsleeper
timeout -k 30 2 python3 -I -B $P /root/floor-v2-verify/pg/zzsleeper 20; echo "rc=$?"
python3 -c "import time; time.sleep(1)"
echo "survivors_after_timeout: $(pgrep -x zzsleeper | wc -l)"
pkill -x zzsleeper; true
