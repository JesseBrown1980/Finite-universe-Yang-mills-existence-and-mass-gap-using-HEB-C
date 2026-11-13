set -u
# Prepare (no launch): fresh clone of the freeze commit, pin check, state of the host.
B=/root/floor-r9
[ -e $B ] && { echo "PREP|$B exists, refusing"; exit 9; }
mkdir -p $B && cd $B || exit 7
git clone -q --branch local-opus55-floor-cert-freeze-v2-20261110 https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git repo || exit 6
cd repo
echo "PREP|head=$(git rev-parse HEAD)|want=c8dbcdbf990114292313cbc410a745a14ba0b778|status_lines=$(git status --short | wc -l)"
F=independent/y131-floor-cert-freeze-v2-20261110
cd $F
echo "PREP|pins_ok=$(sha256sum -c FREEZE-PIN.sha256 2>/dev/null | grep -c ': OK$')|pins_bad=$(sha256sum -c FREEZE-PIN.sha256 2>/dev/null | grep -vc ': OK$')"
echo "PREP|record=$(sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)"
echo "PREP|launcher=$(sha256sum final/tools/run_floor.sh | cut -d' ' -f1)"
echo "PREP|run9_exists=$([ -e work/run9 ] && echo 1 || echo 0)|parent_cargo=$(ls /Cargo.toml /root/Cargo.toml $B/Cargo.toml 2>/dev/null | tr '\n' ',')"
echo "PREP|nsfs=$(findmnt -t nsfs | wc -l)|floor_mounts=$(grep -c floor-run /proc/1/mountinfo)|procs=$(pgrep -cf 'floorcert|run_floor|recheck_floor')"
free -m | sed -n 2p; uptime; df -h /root | tail -1; rustup toolchain list 2>/dev/null | head -5; /root/.cargo/bin/rustup toolchain list | head -5
