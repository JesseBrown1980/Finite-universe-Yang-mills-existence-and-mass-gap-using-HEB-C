# fresh package copies for the attack runs; nothing touches /root/floor-v2/repo
set -u
B=/root/floor-v2-final
H=$B/head/independent/y131-floor-cert-freeze-v2-20261110
mkdir -p $B/tmp $B/runs $B/old
rm -rf $B/pkg; mkdir -p $B/pkg
tar -C $H --exclude=./work/design/rs/target -cf - . | tar -C $B/pkg -xf -
mkdir -p $B/pkg/work/design/rs/target/release; cp -p $H/work/design/rs/target/release/floorcert $B/pkg/work/design/rs/target/release/
rm -rf $B/oldpkg $B/old/x; mkdir -p $B/old/x $B/oldpkg
git -C /root/floor-v2/repo archive cfc57befadcb61fb36b992af841941adaecd3fd0 independent/y131-floor-cert-freeze-v2-20261110 | tar -x -C $B/old/x
tar -C $B/old/x/independent/y131-floor-cert-freeze-v2-20261110 -cf - . | tar -C $B/oldpkg -xf -
mkdir -p $B/oldpkg/work/design/rs/target/release; cp -p $H/work/design/rs/target/release/floorcert $B/oldpkg/work/design/rs/target/release/
cd $B/pkg && sha256sum -c FREEZE-PIN.sha256 2>/dev/null | grep -vc ': OK$'
sha256sum $B/pkg/final/tools/run_floor.sh $B/oldpkg/final/tools/run_floor.sh
