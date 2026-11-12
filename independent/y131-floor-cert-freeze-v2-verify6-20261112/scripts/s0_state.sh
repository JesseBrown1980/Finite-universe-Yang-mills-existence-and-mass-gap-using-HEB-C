V=/root/floor-v6-verify; cd $V/repoE || exit 9
echo "HEAD=$(git rev-parse HEAD) parent=$(git rev-parse HEAD^) branch=$(git rev-parse --abbrev-ref HEAD)"
echo "porcelain_all=$(git status --porcelain | wc -l)"; git status --porcelain | head
echo "remote=$(git ls-remote origin refs/heads/local-opus55-floor-cert-freeze-v2-20261110)"
ls $V; findmnt -t nsfs; echo nsfs_done; grep -c floor-run /proc/1/mountinfo
ls -la /Cargo.toml; grep -c workspace /Cargo.toml
git diff --stat HEAD^ HEAD | tail -30
systemctl list-units --all 'floor-*' --no-pager | head
