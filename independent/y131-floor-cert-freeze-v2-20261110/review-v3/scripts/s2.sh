export PATH="$HOME/.cargo/bin:$PATH"
mkdir -p /root/floor-v2-final
cd /root/floor-v2/repo
H=3b91d1a047d7485693c754ece8c7c18f43fbf326
V2=independent/y131-floor-cert-freeze-v2-20261110
echo "== outside v2 vs e74d8a46"; git diff --name-only e74d8a46 $H | grep -v "^$V2/" | wc -l
echo "== outside v2 vs cfc57bef"; git diff --name-only cfc57bef $H | grep -v "^$V2/" | wc -l
echo "== v1 folder vs e74d"; git diff --name-only e74d8a46 $H -- independent/y131-floor-cert-freeze-20261110 | wc -l
echo "== work/ vs cfc"; git diff --name-only cfc57bef $H -- $V2/work | wc -l
echo "== trailers"; git log -1 --format=%B $H | grep -iE 'co-authored|signed-off|claude-session' | wc -l
git log -1 --format='%an|%ae|%cn|%ce' $H
rm -rf /root/floor-v2-final/head; mkdir -p /root/floor-v2-final/head
git archive $H | tar -x -C /root/floor-v2-final/head
cd /root/floor-v2-final/head/$V2
echo "== CR files"; git -C /root/floor-v2/repo diff --name-only e74d8a46 $H | while read f; do [ -f "/root/floor-v2-final/head/$f" ] && grep -lI $'\r' "/root/floor-v2-final/head/$f"; done | wc -l
ls; cat FREEZE-PIN.txt | head -30
echo "== pin check"; sha256sum -c FREEZE-PIN.sha256 2>&1 | grep -vc ': OK$'; sha256sum -c FREEZE-PIN.sha256 2>&1 | grep -c ': OK$'
sha256sum -c FREEZE-PIN.sha256 2>&1 | grep -v ': OK$' | head
