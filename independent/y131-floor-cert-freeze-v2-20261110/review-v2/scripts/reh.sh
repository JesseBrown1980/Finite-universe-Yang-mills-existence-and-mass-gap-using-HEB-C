# usage: reh.sh NAME args...   (test mode only; refuses if args lack --test-r)
set -u
export PATH="$HOME/.cargo/bin:$PATH"
N=$1; shift
case " $* " in *" --test-r "*) ;; *) echo "REFUSING: no --test-r"; exit 9;; esac
PK=/root/floor-v2-verify/clone/independent/y131-floor-cert-freeze-v2-20261110
O=/root/floor-v2-verify/reh/$N
mkdir -p /root/floor-v2-verify/reh; rm -rf $O
t0=$(date +%s)
bash $PK/final/tools/run_floor.sh "$@" --test-out $O > /root/floor-v2-verify/reh/$N.stdout 2>&1; rc=$?
echo "NAME=$N rc=$rc secs=$(( $(date +%s) - t0 ))"
grep -E '^(DECISION|STEP|INJECTED|NOTE\|rerun)' /root/floor-v2-verify/reh/$N.stdout | cut -c1-260
tail -1 /root/floor-v2-verify/reh/$N.stdout | sed -E 's/\|files=.*//' 
grep -E '^ACCEPTED' $O/FLOOR-RUN-RECEIPT.hbp 2>/dev/null | tr '\n' ' '; echo
