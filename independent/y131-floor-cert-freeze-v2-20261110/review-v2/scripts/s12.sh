cd /root/floor-v2/repo
for b in aad156872fb10213a5afd36e9a0347d99ff151d0 c8e8a135c9291129f28f1fcaa018fa29a7cc96fe e69de29bb2d1d6434b8b29ae775ad8c2e48c5391; do
  echo "== $b"; git rev-list --all --objects | grep "^$b" | head -5
  git log --all --format='%h %s' --find-object=$b | head -3
done
A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110/review-v1/E3-PROVENANCE.hbp
grep -E '345f71973e0982dc|8221ac66be71558c|e3b0c44298fc1c14' $A | cut -c1-300
