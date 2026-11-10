set -u
export PATH="$HOME/.cargo/bin:$PATH"
CL=/root/floor-v2-verify/clone; ROOT=$CL/independent/y131-floor-cert-freeze-v2-20261110
cd $ROOT
PREDREL=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
P=$(sha256sum $PREDREL | cut -d' ' -f1)
C=$(git log -1 --format=%H -- "$PREDREL"); echo "line67 C=$C"
PFX=$(git rev-parse --show-prefix); BL=$(git show "$C:$PFX$PREDREL" | sha256sum | cut -d' ' -f1); echo "line70 blob=$BL P=$P equal=$([ "$BL" = "$P" ] && echo 1 || echo 0)"
echo "line72 porcelain_lines=$(git status --porcelain --untracked-files=no -- . | wc -l)"
F=/root/floor-v2-verify/frozen; rm -rf $F; mkdir -p $F
(cd work/design/rs && CARGO_TARGET_DIR=$F/target FLOORCERT_FREEZE_COMMIT=$C FLOORCERT_PREDICTION_SHA256=$P cargo +1.81 build --release --locked -j1) > $F/build.txt 2>&1; echo "frozen_build_rc=$? warnings=$(grep -c '^warning' $F/build.txt)"
echo "work/design/rs/target untouched: $(sha256sum work/design/rs/target/release/floorcert | cut -c1-16)"
sha256sum $F/target/release/floorcert | cut -c1-16
$F/target/release/floorcert selftest > $F/selftest.txt 2>&1; echo "frozen selftest rc=$? sha16=$(sha256sum $F/selftest.txt | cut -c1-16)"
mkdir -p $F/RUN7
$F/target/release/floorcert cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $F/RUN7 --freeze-commit $C --prediction $PREDREL --prediction-sha256 $P > $F/c12.txt 2>&1; echo "frozen cert r12 rc=$? $(grep -E '^(FREEZE|REFUSE)' $F/c12.txt | cut -c1-160) cert=$(sha256sum $F/RUN7/cert_*.txt 2>/dev/null | cut -c1-16)"
head -1 $F/RUN7/cert_*.txt | tr ' ' '\n' | grep -E '^(freeze|pred)=' 
