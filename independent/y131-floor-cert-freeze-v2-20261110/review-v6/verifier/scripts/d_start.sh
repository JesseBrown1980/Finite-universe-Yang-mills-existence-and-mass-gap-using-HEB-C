cp /mnt/c/tmp/opus55/floor-v2-verify5/scripts/d_full.sh /root/floor-v5-verify/d_full.sh
systemd-run --unit=floor-v5-d13 --collect bash /root/floor-v5-verify/d_full.sh; sleep 3; systemctl status floor-v5-d13 --no-pager | head -5
