cd /root/gl159/repo
for c in ef3f76c 08bef6d 26756c9 32ebe74 b3eeca0; do
  a=$(git show $c:docs/PREDICTION-GLOBAL-LOCK-20261110.hbp | sha256sum | cut -c1-64)
  b=$(git show $c:docs/ERRATUM-GLOBAL-LOCK-20261110.hbp 2>/dev/null | sha256sum | cut -c1-64)
  echo "FROZEN_AT|commit=$c|prediction=$a|erratum=$b"
done
echo "--- zgap2 / GL2 scope: files touched by PR vs base"
git diff --name-only origin/local-opus55-global-lock-20261110...b3eeca0 | grep -iE "zgap|gl2|P1" || echo "no zgap2/GL2 paths touched"
git diff origin/local-opus55-global-lock-20261110...b3eeca0 | grep -iE "^[+-].*zgap2" | head
echo "--- base branch vs main"
git log --oneline origin/main..origin/local-opus55-global-lock-20261110 | head
git ls-tree -r --name-only b3eeca0 | grep -i zgap | head -20
