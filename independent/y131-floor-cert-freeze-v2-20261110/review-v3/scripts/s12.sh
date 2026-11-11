rm -rf /mnt/c/tmp/opus55/floor-v2-final/winrepo /mnt/c/tmp/opus55/floor-v2-final/winclone
git clone -q --no-checkout /root/floor-v2/repo /mnt/c/tmp/opus55/floor-v2-final/winclone && cd /mnt/c/tmp/opus55/floor-v2-final/winclone && git -c core.autocrlf=false checkout -q --detach 3b91d1a047d7485693c754ece8c7c18f43fbf326 && git rev-parse HEAD && git status --porcelain | wc -l
