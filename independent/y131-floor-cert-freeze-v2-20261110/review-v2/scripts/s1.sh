set -u
export PATH="$HOME/.cargo/bin:$PATH"
R=/root/floor-v2/repo
C=cfc57befadcb61fb36b992af841941adaecd3fd0
V1=independent/y131-floor-cert-freeze-20261110
V2=independent/y131-floor-cert-freeze-v2-20261110
cd $R
git log -1 --format='%H|%P|%an|%ae|%cn|%ce' $C
git log -1 --format=%B $C | cat -A | tail -5
echo "--- branch"; git branch --contains $C
echo "--- v1 diff lines"; git diff e74d8a46 $C -- $V1 | wc -l
echo "--- files outside v2"; git diff --name-only e74d8a46 $C | grep -v "^$V2/" | wc -l
echo "--- files in v2"; git diff --name-only e74d8a46 $C | wc -l
echo "--- status"; git status --short | head
mkdir -p /root/floor-v2-verify/arch
rm -rf /root/floor-v2-verify/arch/*
git archive $C $V2 $V1 | tar -x -C /root/floor-v2-verify/arch
cd /root/floor-v2-verify/arch/$V2
echo "--- CR files"; grep -rlI $'\r' . | wc -l
echo "--- pin check"; sha256sum -c FREEZE-PIN.sha256 2>&1 | grep -vc ': OK$'; wc -l FREEZE-PIN.sha256
find . -type f | wc -l
ls -R | head -80
