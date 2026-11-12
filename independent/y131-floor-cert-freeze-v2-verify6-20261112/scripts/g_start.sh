cp /mnt/c/tmp/opus55/floor-v2-verify6/scripts/g_runs.sh /root/floor-v6-verify/g_runs.sh
systemd-run --unit=floor-v6-g --collect bash /root/floor-v6-verify/g_runs.sh; sleep 2; systemctl is-active floor-v6-g
