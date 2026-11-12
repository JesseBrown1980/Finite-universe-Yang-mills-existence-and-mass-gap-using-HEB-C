V=/root/floor-v5-verify; cd $V/repoC; git status --porcelain; cat .gitignore 2>/dev/null | head; grep -E '^(error|warning)' $V/clippy.txt | sort | uniq -c; grep -A12 '^error' $V/clippy.txt | head -60
ls ~/.cargo/config* /root/.cargo 2>&1 | head; env | grep -i -E 'cargo|rust|clippy'
