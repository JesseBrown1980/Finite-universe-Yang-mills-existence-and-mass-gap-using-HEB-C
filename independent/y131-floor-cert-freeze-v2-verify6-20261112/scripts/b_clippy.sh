V=/root/floor-v6-verify; cd $V/repoE/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs
/root/.cargo/bin/cargo +1.81 --version; /root/.cargo/bin/cargo +1.81 clippy --version
/root/.cargo/bin/cargo +1.81 clippy --release -- -D warnings > $V/clippy181.txt 2>&1; echo "clippy181 exit=$?"; tail -2 $V/clippy181.txt
echo "pinfree_sha_after=$(sha256sum target/release/floorcert | cut -d' ' -f1)"
