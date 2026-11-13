set -u
cd /root/floor-v2-verify
rm -rf clone
git clone -q --no-hardlinks --no-checkout /root/floor-v2/repo clone
cd clone && git checkout -q --detach cfc57befadcb61fb36b992af841941adaecd3fd0 && git log -1 --format=%H && git status --short | head
git cat-file -p c8e8a135c9291129f28f1fcaa018fa29a7cc96fe | od -c | head -2
