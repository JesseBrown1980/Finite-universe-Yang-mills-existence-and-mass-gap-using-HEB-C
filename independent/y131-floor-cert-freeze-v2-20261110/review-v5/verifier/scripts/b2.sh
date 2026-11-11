set -u
echo "nproc=$(nproc)"; free -k | head -2; df -k /root | tail -1
ls /root/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin/
ls /root/.cargo/bin 2>/dev/null
cd /root/floor-v4-verify/repo && git status --porcelain
F=independent/y131-floor-cert-freeze-v2-20261110
cd $F/work/design/rs && /root/.cargo/bin/cargo +1.81 clippy --version; /root/.cargo/bin/cargo +1.81 clippy --release -- -D warnings > /root/floor-v4-verify/clippy181.txt 2>&1; echo "clippy181 exit=$?"; tail -3 /root/floor-v4-verify/clippy181.txt
