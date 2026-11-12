set -u
V=/root/floor-v5-verify; F=$V/repoC/independent/y131-floor-cert-freeze-v2-20261110
TC=/root/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin
$TC/rustc --version; $TC/cargo --version; nproc
cd $F/work/design/rs
RUSTC=$TC/rustc $TC/cargo build --release --locked -j2 > $V/build.txt 2>&1; echo "build exit=$?"
echo "pinfree_sha=$(sha256sum target/release/floorcert | cut -d' ' -f1) row016=9533e7e902ff565641b34d3bdd0c693ffa0b37baa08575283e00429e2c7fa74f"
RUSTC=$TC/rustc PATH=$TC:$PATH $TC/cargo clippy --release -- -D warnings > $V/clippy.txt 2>&1; echo "clippy exit=$?"; tail -2 $V/clippy.txt
$TC/cargo-clippy --version 2>/dev/null || $TC/clippy-driver --version
cd $V/repoC && echo "status_after=$(git status --porcelain | wc -l)"
