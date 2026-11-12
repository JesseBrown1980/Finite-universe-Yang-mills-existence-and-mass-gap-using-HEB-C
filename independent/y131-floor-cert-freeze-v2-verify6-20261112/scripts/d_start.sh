cp /mnt/c/tmp/opus55/floor-v2-verify6/scripts/d_full.sh /root/floor-v6-verify/d_full.sh
systemd-run --unit=floor-v6-d13 --collect bash /root/floor-v6-verify/d_full.sh; sleep 3; systemctl status floor-v6-d13 --no-pager | head -5
