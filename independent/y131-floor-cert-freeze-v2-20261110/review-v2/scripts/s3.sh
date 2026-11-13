F=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/src/main.rs
sed -n '225,245p;262,280p;300,320p;365,380p;530,560p;590,615p;710,722p;880,900p;1155,1182p;2040,2060p' $F | cat -n | head -0
for r in 225,245 262,280 300,320 365,380 532,552 590,615 712,722 884,900 1159,1180 2044,2058; do echo "=== $r"; sed -n "${r}p" $F; done
echo ===; grep -nE '^const|^    const|const E:|const NL|const NK|const V:|struct Rat|fn mk_rat|impl Rat' $F | head -30
