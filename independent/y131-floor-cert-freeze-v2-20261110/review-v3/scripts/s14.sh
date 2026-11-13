cd /root/floor-v2/repo
for c in e74d8a46 cfc57bef 3b91d1a0; do for p in independent/y131-floor-cert-freeze-20261110/final/tools/lint_hbp.py independent/y131-floor-cert-freeze-v2-20261110/final/tools/lint_hbp.py; do h=$(git show $c:$p 2>/dev/null | sha256sum | cut -c1-16); echo "$c $p $h"; done; done
for p in work/design/gate_required.sh work/design/py/cert_gate.py work/design/py/indep_verify.py work/design/peak_rss.py work/design/rs/src/main.rs; do a=$(git show cfc57bef:independent/y131-floor-cert-freeze-v2-20261110/$p | sha256sum|cut -c1-16); b=$(git show 3b91d1a0:independent/y131-floor-cert-freeze-v2-20261110/$p | sha256sum|cut -c1-16); echo "$p cfc=$a head=$b"; done
git diff cfc57bef 3b91d1a0 --stat -- independent/y131-floor-cert-freeze-v2-20261110/work | tail -1
