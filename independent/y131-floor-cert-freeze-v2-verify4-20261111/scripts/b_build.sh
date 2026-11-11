set -u
cd /root/floor-v4-verify
echo "nproc=$(nproc)"; free -k | head -2; df -k /root | tail -1; uname -r
TC=/root/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin
$TC/rustc --version; $TC/cargo --version
[ -d repoB ] || git clone -q repo repoB
( cd repoB && git checkout -q 5eecb540431a1b5665605f68ed81bc701719dcd1 && git rev-parse HEAD && git status --porcelain | wc -l )
F=independent/y131-floor-cert-freeze-v2-20261110
for c in repo repoB; do
  ( cd $c/$F/work/design/rs && RUSTC=$TC/rustc $TC/cargo build --release --locked -j2 > /root/floor-v4-verify/build_$c.txt 2>&1; echo "build_$c exit=$?"; sha256sum target/release/floorcert )
done
grep '^PIN|id=016|' repo/$F/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | sed -n 's/.*|value=\([0-9a-f]*\)|.*/row016=\1/p'
( cd repo/$F/work/design/rs && RUSTC=$TC/rustc PATH=$TC:$PATH $TC/cargo clippy --release -- -D warnings > /root/floor-v4-verify/clippy.txt 2>&1; echo "clippy exit=$?"; tail -3 /root/floor-v4-verify/clippy.txt )
( cd repo && git status --porcelain | wc -l; cd ../repoB && git status --porcelain | wc -l )
