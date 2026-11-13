cp /mnt/c/tmp/opus55/floor-v2-verify5/scripts/g_runs.sh /root/floor-v5-verify/g_runs.sh
systemd-run --unit=floor-v5-g --collect bash /root/floor-v5-verify/g_runs.sh; sleep 2; systemctl is-active floor-v5-g
