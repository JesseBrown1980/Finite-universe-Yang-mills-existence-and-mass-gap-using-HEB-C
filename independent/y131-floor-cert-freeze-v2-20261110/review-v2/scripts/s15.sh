set -u
W=/mnt/c/tmp/opus55/floor-v2-verify/winrepo
rm -rf /mnt/c/tmp/opus55/floor-v2-verify/wincheck $W
git clone -q --no-checkout /root/floor-v2-verify/clone $W
cd $W && git -c core.autocrlf=false checkout -q --detach cfc57befadcb61fb36b992af841941adaecd3fd0 && git log -1 --format=%H
