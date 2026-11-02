#!/usr/bin/env bash
# Builds ymcheck (./checker) and ymgen, runs every control, writes CONTROLS.hbp.
# Exit status 0 only if every control matched its expectation.
set -u -o pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GO="${GO:-go}"
FUZZ="${FUZZ:-200}"
cd "$ROOT"
"$GO" build -trimpath -o checker ./cmd/ymcheck || exit 1
"$GO" build -trimpath -o ymgen ./cmd/ymgen || exit 1
W="$ROOT/work"
rm -rf "$W"
mkdir -p "$W"
cd "$W"
OUT="$ROOT/CONTROLS.hbp"
NMATCH=0
NMISS=0
{
	echo "CONTROLS|tool=ymcheck|source=cmd/ymcheck/main.go|source_sha256=$(sha256sum ../cmd/ymcheck/main.go | cut -d' ' -f1)|go=$("$GO" version | cut -d' ' -f3)|json=0"
	echo "# Every command runs in work/ (relative to this file) with ../checker = ymcheck and ../ymgen = generator/reference."
	echo "# 'fail' means: exit status 2 and stdout exactly one line FAIL|reason=<prefix>...|json=0, with no CERT and no STORE row."
	echo "# 'pass' means: exit status 0, CERT row(s) and one STORE row with merkle=PASS, row_sums_zero=PASS, w_symmetry=PASS."
} >"$OUT"

record() { # id name command expected actual ok stdout
	local v=MISMATCH
	if [ "$6" = 1 ]; then
		v=MATCH
		NMATCH=$((NMATCH + 1))
	else
		NMISS=$((NMISS + 1))
	fi
	{
		echo
		echo "CONTROL|id=$1|verdict=$v|json=0"
		echo "  name:     $2"
		echo "  command:  $3"
		echo "  expected: $4"
		echo "  actual:   $5"
		printf '%s\n' "$7" | sed -n '1,6p' | cut -c1-400 | sed 's/^/  stdout:   /'
	} >>"$OUT"
	echo "$v $1 $2" >&2
}

run() {
	STDOUT="$(bash -c "$1" 2>/dev/null)"
	RC=$?
}

strip() { sed -E 's/\|secs=[0-9]+//; s/\|max_num_bits=[0-9]+//'; }
certs() { grep '^CERT|' | strip; }
field() { sed -nE "s/.*\|$1=([^|]*)\|.*/\1/p" | head -n1; }

expect_fail() { # id name command reason-prefix
	run "$3"
	local lines nres ok=0
	lines=$(printf '%s' "$STDOUT" | grep -c '')
	nres=$(printf '%s\n' "$STDOUT" | grep -cE '^(CERT|STORE)\|')
	if [ "$RC" = 2 ] && [ "$lines" = 1 ] && [ "$nres" = 0 ] && [[ "$STDOUT" =~ ^FAIL\|reason=($4) ]] && [[ "$STDOUT" == *"|json=0" ]]; then ok=1; fi
	record "$1" "$2" "$3" "fail, reason matching ^(${4:-<any>})" "exit=$RC lines=$lines cert_or_store_rows=$nres" $ok "$STDOUT"
}

expect_pass() { # id name command [extra-shell-test [expected-text]]
	run "$3"
	local ok=0
	if [ "$RC" = 0 ] && ! grep -q '^FAIL' <<<"$STDOUT" && grep -q '^CERT|' <<<"$STDOUT" &&
		grep -qE '^STORE\|.*\|merkle=PASS\|.*\|row_sums_zero=PASS\|w_symmetry=PASS\|' <<<"$STDOUT"; then ok=1; fi
	if [ $ok = 1 ] && [ -n "${4:-}" ]; then eval "$4" || ok=0; fi
	record "$1" "$2" "$3" "pass${5:+; $5}" "exit=$RC${4:+; extra test: $4 -> $([ $ok = 1 ] && echo true || echo false)}" $ok "$STDOUT"
}

compare_ref() { # id name store d...
	local id=$1 name=$2 store=$3
	shift 3
	local c1="../checker $* < $store" c2="../ymgen ref -store $store $*"
	run "$c1"
	local o1="$STDOUT" r1=$RC
	run "$c2"
	local o2="$STDOUT" r2=$RC ok=0
	if [ $r1 = 0 ] && [ $r2 = 0 ] && [ "$(strip <<<"$o1")" = "$(strip <<<"$o2")" ]; then ok=1; fi
	record "$id" "$name" "$c1   VERSUS   $c2" "both pass; identical CERT and STORE rows (ignoring secs and the reference's max_num_bits)" \
		"exit=$r1/$r2 identical=$([ $ok = 1 ] && echo yes || echo no); reference max_num_bits=$(field max_num_bits <<<"$o2")" $ok "$o1"
}

# ---------------------------------------------------------------------------
# A. Build-level controls.
run "cd .. && $GO vet ./..."
record A01 "go vet" "$GO vet ./..." "exit 0" "exit=$RC" $([ $RC = 0 ] && echo 1 || echo 0) "$STDOUT"
run "cd .. && $GO test -count=1 ./cmd/ymcheck"
record A02 "unit tests: int128/int256/floor-division/compare vs math/big, splitter under random chunking" "$GO test -count=1 ./cmd/ymcheck" "exit 0" "exit=$RC" $([ $RC = 0 ] && echo 1 || echo 0) "$STDOUT"
run "cd .. && grep -rniE 'float|complex64|complex128' --include='*.go' . ; true"
record A03 "no floating point anywhere in the Go sources" "grep -rniE 'float|complex64|complex128' --include='*.go' ." "no matches" "matches=$(printf '%s' "$STDOUT" | grep -c '')" $([ -z "$STDOUT" ] && echo 1 || echo 0) "$STDOUT"

# ---------------------------------------------------------------------------
# B. Correct stores.
../ymgen random -rows 300 -flat 20 -deg 3 -wmax 7 -magmax 6 -cmax 4 -seed 1 -dup -zeros -out s300.bin 2>/dev/null
../ymgen dvec -store s300.bin -mode perron -out dp.bin
../ymgen dvec -store s300.bin -mode random -max 1000000 -seed 3 -out dr.bin
../ymgen dvec -store s300.bin -mode big -seed 4 -out db.bin
HDR=$(head -c 4096 s300.bin | tr -d '\000' | head -n1)
PB=$(field payload_bytes <<<"$HDR|")
MK=$(field payload_merkle <<<"$HDR|")
GEN300="../ymgen random -rows 300 -flat 20 -deg 3 -wmax 7 -magmax 6 -cmax 4 -seed 1 -dup -zeros"

expect_pass B01 "correct 300-row store (20 flat, weights 1..7, duplicate and zero entries), Perron-type d" "../checker dp.bin < s300.bin"
compare_ref B02 "fast checker equals big-int reference: Perron d, random d, d near 2^62 (128-bit products)" s300.bin dp.bin dr.bin db.bin
MINROW=$(../checker dp.bin <s300.bin | grep '^CERT' | field row)
BASECERT=$(../checker dp.bin <s300.bin | certs)

# B03: tiny stores, exact smallest eigenvalue.
for s in 1 2 3 4 5 6 7 8; do
	../ymgen random -rows 6 -flat 1 -deg 2 -wmax 7 -seed $s -out t$s.bin
	../ymgen dvec -store t$s.bin -mode perron -out tp$s.bin
	../ymgen dvec -store t$s.bin -mode random -max 1000 -seed $((s + 100)) -out tr$s.bin
	run "../checker tp$s.bin tr$s.bin < t$s.bin"
	o="$STDOUT"
	tp=$(grep "d=tp$s.bin" <<<"$o" | field t_cert)
	tr=$(grep "d=tr$s.bin" <<<"$o" | field t_cert)
	e=$(../ymgen eigen -store t$s.bin)
	tf=$(field t_floor <<<"$e")
	ok=0
	if [ $RC = 0 ] && [ -n "$tp" ] && [ -n "$tf" ] && [ "$tp" -le "$tf" ] && [ "$tr" -le "$tf" ] &&
		grep -q 'psd_at_t_floor=true|psd_at_t_floor_plus_1=false' <<<"$e"; then ok=1; fi
	record B03.$s "tiny store seed $s (6 rows, 1 flat, 5 non-flat, weights 1..7): certified value <= exact floor(1e6*lambda_min(H'))" \
		"../checker tp$s.bin tr$s.bin < t$s.bin ; ../ymgen eigen -store t$s.bin" \
		"pass; t_cert(Perron d) <= t_floor and t_cert(random d) <= t_floor; W(1e6 H' - t I) PSD at t_floor, not at t_floor+1" \
		"t_cert(Perron d)=$tp t_cert(random d)=$tr t_floor=$tf" $ok "$o
$e"
done

../ymgen random -rows 300 -flat 20 -deg 3 -wmax 7 -magmax 6 -cmax 4 -seed 1 -dup -zeros -hdr-spaces -out s300sp.bin 2>/dev/null
expect_pass B04 "header line padded with spaces to byte 4095 instead of NULs after the newline" "../checker dp.bin < s300sp.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ]' "same CERT row as B01"
for pad in 0 1 1000000; do
	$GEN300 -pad $pad -out s300pad$pad.bin 2>/dev/null
	expect_pass B05.$pad "zero padding of $pad bytes after the payload" "../checker dp.bin < s300pad$pad.bin" \
		'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && [ "$(field padding_bytes <<<"$STDOUT")" = '"$pad"' ]' "same CERT row as B01, padding_bytes=$pad"
done

# B06: multi-leaf stores (rows straddle 16 MiB leaf boundaries).
../ymgen random -rows 90000 -flat 900 -deg 30 -seed 11 -target-payload 50331648 -out m3.bin
../ymgen random -rows 50000 -flat 500 -deg 30 -seed 12 -dup -target-payload 33554440 -out m2.bin
for m in m3 m2; do
	../ymgen dvec -store $m.bin -mode perron -iters 40 -out $m-dp.bin
	../ymgen dvec -store $m.bin -mode big -seed 5 -out $m-db.bin
done
compare_ref B06.1 "3 full leaves (payload exactly 3*16 MiB), fast vs big-int reference" m3.bin m3-dp.bin m3-db.bin
compare_ref B06.2 "payload 2*16 MiB + 8 bytes (last leaf is 8 bytes, last row straddles), fast vs reference" m2.bin m2-dp.bin m2-db.bin
for m in m3 m2; do
	pbm=$(head -c 4096 $m.bin | tr -d '\000' | head -n1 | sed -nE 's/.*\|payload_bytes=([0-9]+)\|.*/\1/p')
	mkm=$(head -c 4096 $m.bin | tr -d '\000' | head -n1 | sed -nE 's/.*\|payload_merkle=([0-9a-f]+)\|.*/\1/p')
	cu=$(tail -c +4097 $m.bin | head -c "$pbm" | split -b 16777216 --filter='sha256sum' | cut -c1-64 | tr -d '\n' | sha256sum | cut -c1-64)
	record B06.$m.merkle "merkle recomputed with coreutils (split -b 16777216 | sha256sum) equals header and checker" \
		"tail -c +4097 $m.bin | head -c $pbm | split -b 16777216 --filter=sha256sum | cut -c1-64 | tr -d '\\n' | sha256sum" \
		"$mkm" "$cu" $([ "$cu" = "$mkm" ] && echo 1 || echo 0) ""
done
REF3=$(../checker m3-dp.bin m3-db.bin <m3.bin | strip)
for wk in 1 2 7; do
	expect_pass B07.$wk "worker count $wk gives identical output" "../checker -workers $wk -hashers 1 m3-dp.bin m3-db.bin < m3.bin" \
		'[ "$(strip <<<"$STDOUT")" = "$REF3" ]' "output identical to the default worker count"
done
split -n 34 -d -a 2 m3.bin sector-
expect_pass B08 "store split into 34 sector files and concatenated through a pipe (CI form)" "cat sector-* | ../checker m3-dp.bin m3-db.bin" \
	'[ "$(strip <<<"$STDOUT")" = "$REF3" ]' "identical to reading the single file"

# B09: two d files in one pass versus two separate runs.
run "../checker dp.bin db.bin < s300.bin"
both=$(certs <<<"$STDOUT")
sep="$(../checker dp.bin <s300.bin | certs)
$(../checker db.bin <s300.bin | certs)"
record B09 "two d files in one pass give the same CERT rows as two separate runs" \
	"../checker dp.bin db.bin < s300.bin   VERSUS   ../checker dp.bin < s300.bin ; ../checker db.bin < s300.bin" \
	"identical CERT rows" "identical=$([ "$both" = "$sep" ] && echo yes || echo no)" $([ "$both" = "$sep" ] && [ $RC = 0 ] && echo 1 || echo 0) "$STDOUT"

# B10: negative numerator, floor toward minus infinity.
printf '1 1 : 0:1 1:-1\n1 1 : 0:-1 1:1\n' >neg.txt
../ymgen text -in neg.txt -out neg.bin
../ymgen dlist -vals 3,50 -out neg-d.bin
../ymgen dlist -vals 1,1 -out neg-d1.bin
expect_pass B10 "negative numerator: row 0 numerator = 9e6*1*3 + 1e6*(3-50) = -20000000, d=3 -> floor = -6666667 (truncation would give -6666666)" \
	"../checker neg-d.bin < neg.bin" '[ "$(grep ^CERT <<<"$STDOUT" | field t_cert)" = -6666667 ] && [ "$(grep ^CERT <<<"$STDOUT" | field row)" = 0 ]' "t_cert=-6666667 row=0 mag=1"
compare_ref B10.ref "negative numerator, big-int reference agrees" neg.bin neg-d.bin
run "../checker neg-d1.bin < neg.bin; ../ymgen eigen -store neg.bin"
record B10.eig "same 2x2 store with d=(1,1): H' = 9I + [[1,-1],[-1,1]], eigenvalues 9 and 11" "../checker neg-d1.bin < neg.bin; ../ymgen eigen -store neg.bin" \
	"t_cert = t_floor = 9000000" "t_cert=$(grep ^CERT <<<"$STDOUT" | field t_cert) t_floor=$(field t_floor <<<"$STDOUT")" \
	$([ "$(grep ^CERT <<<"$STDOUT" | field t_cert)" = 9000000 ] && [ "$(field t_floor <<<"$STDOUT")" = 9000000 ] && echo 1 || echo 0) "$STDOUT"

# B11: near the 128-bit limit (exact) and over it (fail closed).
printf '1 1 : 0:2147483647*30000 1:-2147483647*30000\n1 1 : 1:2147483647*30000 0:-2147483647*30000\n' >ovf.txt
../ymgen text -in ovf.txt -out ovf.bin
../ymgen dlist -vals 1,2305843009213693952 -out ovf-d61.bin
../ymgen dlist -vals 1,4611686018427387904 -out ovf-d62.bin
compare_ref B11 "numerator just under 2^127 (d = 1, 2^61; 30000 duplicate diagonal entries): exact, equals reference" ovf.bin ovf-d61.bin

# B12: differential fuzz against the big-int reference, including defects.
fz_total=0 fz_pass=0 fz_fail=0 fz_bad=0 fz_list=""
for i in $(seq 1 "$FUZZ"); do
	rows=$((1 + RANDOM % 400))
	flat=$((RANDOM % (rows / 3 + 1)))
	deg=$((1 + RANDOM % 6))
	wmax=$((1 + RANDOM % 2000))
	cmax=$((1 + RANDOM % 2000))
	mm=$((1 + RANDOM % 65535))
	opts=""
	[ $((RANDOM % 3)) = 0 ] && opts="$opts -dup"
	[ $((RANDOM % 3)) = 0 ] && opts="$opts -zeros"
	[ $((RANDOM % 4)) = 0 ] && opts="$opts -hdr-spaces"
	defect=""
	case $((RANDOM % 8)) in 0) defect=posoff ;; 1) defect=rowsum ;; 2) defect=asym ;; 3) defect=colrange ;; esac
	../ymgen random -rows $rows -flat $flat -deg $deg -wmax $wmax -cmax $cmax -magmax $mm -seed $((1000 + i)) $opts ${defect:+-defect $defect} -out fz.bin 2>/dev/null || continue
	case $((RANDOM % 5)) in
	0) ../ymgen dvec -store fz.bin -mode perron -iters 200 -out fzd.bin 2>/dev/null || ../ymgen dvec -store fz.bin -mode random -seed $i -out fzd.bin ;;
	1) ../ymgen dvec -store fz.bin -mode big -seed $i -out fzd.bin ;;
	2) ../ymgen dvec -store fz.bin -mode random -max 1000 -seed $i -out fzd.bin ;;
	3) ../ymgen dvec -store fz.bin -mode random -max 4611686018427387904 -seed $i -out fzd.bin ;;
	4) ../ymgen dvec -store fz.bin -mode const -out fzd.bin ;;
	esac
	../ymgen dvec -store fz.bin -mode random -max 9223372036854775807 -seed $((i + 7)) -out fzd2.bin
	case $((RANDOM % 10)) in
	0) ../ymgen dset -in fzd.bin -out fzd.bin -h $((RANDOM % rows)) -v -$((RANDOM % 3)) ;;
	1) ../ymgen dset -in fzd2.bin -out fzd2.bin -h $((RANDOM % rows)) -v $((RANDOM % 3)) ;;
	esac
	o1=$(../checker -workers $((1 + RANDOM % 4)) fzd.bin fzd2.bin <fz.bin 2>/dev/null)
	r1=$?
	o2=$(../ymgen ref -store fz.bin fzd.bin fzd2.bin 2>/dev/null)
	r2=$?
	fz_total=$((fz_total + 1))
	good=0
	if [ $r1 = 0 ] && [ $r2 = 0 ] && [ "$(strip <<<"$o1")" = "$(strip <<<"$o2")" ]; then
		good=1
		fz_pass=$((fz_pass + 1))
	elif [ $r1 = 2 ] && [ $r2 = 2 ] && [ "$(printf '%s' "$o1" | grep -c '')" = 1 ] && [[ "$o1" == FAIL\|reason=* ]]; then
		good=1
		fz_fail=$((fz_fail + 1))
	fi
	if [ $good = 0 ]; then
		fz_bad=$((fz_bad + 1))
		fz_list="$fz_list seed=$((1000 + i)):$r1/$r2"
		cp fz.bin "fuzz-mismatch-$i.bin"
	fi
done
record B12 "differential fuzz: $fz_total random stores (1..400 rows, weights and couplings up to 2000, mag up to 65535, d up to 2^63-1, random defects and bad d entries) vs the big-int reference" \
	"controls.sh section B12 (../checker fzd.bin fzd2.bin < fz.bin  VERSUS  ../ymgen ref -store fz.bin fzd.bin fzd2.bin)" \
	"every case: both pass with identical rows, or both fail (exit 2, one FAIL line)" \
	"total=$fz_total both_pass_identical=$fz_pass both_fail=$fz_fail disagreements=$fz_bad$fz_list" $([ $fz_bad = 0 ] && echo 1 || echo 0) ""

# ---------------------------------------------------------------------------
# C. The owner's two controls.
offs=$(../ymgen dump -store s300.bin)
O_CNT=$(awk '$1=="R" && $2==10 {print $6+6}' <<<"$offs")
O_W=$(awk '$1=="R" && $2==7 {print $6}' <<<"$offs")
O_J=$(awk '$1=="E" && $4!=$2 && $5<0 {print $6; exit}' <<<"$offs")
O_ZOFF=$(awk '$1=="E" && $4!=$2 && $5<0 {print $7; exit}' <<<"$offs")
O_ZDIAG=$(awk '$1=="E" && $4==$2 && $2>20 {print $7+3; exit}' <<<"$offs")
O_MAG=$(awk -v m="$MINROW" '$1=="R" && $4>=1 && $4<=15 && $2!=m && $2>50 {print $6+4; exit}' <<<"$offs")
O_LAST=$((4096 + PB - 1))
for spec in "first:4096:1" "cnt:$O_CNT:1" "w:$O_W:1" "j:$O_J:1" "z_offdiag:$O_ZOFF:1" "z_diag_high_byte:$O_ZDIAG:128" "mag:$O_MAG:16" "last:$O_LAST:1" "mid:$((4096 + PB / 2)):4"; do
	IFS=: read -r nm off x <<<"$spec"
	../ymgen flip -in s300.bin -out flip-$nm.bin -offset $off -xor $x
	expect_fail C01.$nm "owner control: one flipped payload byte ($nm field, stream offset $off, xor $x), original header" \
		"../checker dp.bin < flip-$nm.bin" ""
done
../ymgen remerkle -in flip-mag.bin -out flip-mag-remerkled.bin
expect_pass C01.mag.remerkled "same mag-byte flip with the header merkle recomputed: every other check passes, so in C01.mag only the merkle caught it" \
	"../checker dp.bin < flip-mag-remerkled.bin" '[ "$(certs <<<"$STDOUT")" = "$BASECERT" ]' "same CERT row as B01 (the flipped row is not the minimum)"
expect_fail C01.mag.reason "the mag-byte flip with the original header fails on the merkle" "../checker dp.bin < flip-mag.bin" "merkle_mismatch"
../ymgen zpair -in s300.bin -out zpair.bin 2>/dev/null
expect_fail C01.zpair "four z values changed consistently (z_hj-1, z_hh+1, z_jh-1, z_jj+1; equal weights): signs, row sums and W-symmetry still hold, original header" \
	"../checker dp.bin < zpair.bin" "merkle_mismatch"
../ymgen remerkle -in zpair.bin -out zpair-remerkled.bin
expect_pass C01.zpair.remerkled "the same z change with the merkle recomputed passes every other check (so only the merkle caught C01.zpair)" \
	"../checker dp.bin < zpair-remerkled.bin"

NF=$(awk '$1=="R" && $4>0 && $2>100 {print $2; exit}' <<<"$offs")
FL=$(awk '$1=="R" && $4==0 {print $2; exit}' <<<"$offs")
for v in 0 -1 -9223372036854775808; do
	../ymgen dset -in dp.bin -out dbad$v.bin -h $NF -v $v
	expect_fail C02.$v "owner control: d with one nonpositive non-flat entry (row $NF set to $v)" "../checker dbad$v.bin < s300.bin" "nonflat_row_d_nonpositive"
done
expect_fail C02.second "good d first, bad d second: no value printed for either" "../checker dp.bin dbad0.bin < s300.bin" "nonflat_row_d_nonpositive"

# ---------------------------------------------------------------------------
# D. Every other FAIL condition.
mkraw() { $GEN300 -hdr-raw "$1" -out "$2" 2>/dev/null; }
mkraw "XMROOMHDR|n=300|payload_bytes=$PB|payload_merkle=$MK|" hp1.bin
mkraw "YMROOMHDR|payload_bytes=$PB|payload_merkle=$MK|" hp2.bin
mkraw "YMROOMHDR|n=300|n=300|payload_bytes=$PB|payload_merkle=$MK|" hp3.bin
mkraw "YMROOMHDR|n=3x0|payload_bytes=$PB|payload_merkle=$MK|" hp4.bin
mkraw "YMROOMHDR|n=300|payload_bytes=$PB|payload_merkle=$(tr a-f A-F <<<"$MK")|" hp5.bin
mkraw "YMROOMHDR|n=300|payload_merkle=$MK|" hp6.bin
mkraw "YMROOMHDR|n=300|payload_bytes=$PB|payload_merkle=$MK|" hp7.bin
../ymgen flip -in s300sp.bin -out hp8.bin -offset 4095 -xor 42
../ymgen flip -in s300.bin -out hp9.bin -offset 4000 -xor 65
expect_fail D01.1 "parse error: header does not start with YMROOMHDR|" "../checker dp.bin < hp1.bin" "header_parse:missing_YMROOMHDR_prefix"
expect_fail D01.2 "parse error: header has no n" "../checker dp.bin < hp2.bin" "header_parse:missing_n"
expect_fail D01.3 "parse error: duplicate n" "../checker dp.bin < hp3.bin" "header_parse:duplicate_key"
expect_fail D01.4 "parse error: n is not a decimal integer" "../checker dp.bin < hp4.bin" "header_parse:bad_n"
expect_fail D01.5 "parse error: merkle not lowercase hex" "../checker dp.bin < hp5.bin" "header_parse:payload_merkle_not_64"
expect_fail D01.6 "parse error: no payload_bytes" "../checker dp.bin < hp6.bin" "header_parse:missing_payload_bytes"
expect_pass D01.7 "minimal valid header line (only the three required keys) still passes" "../checker dp.bin < hp7.bin" '[ "$(certs <<<"$STDOUT")" = "$BASECERT" ]' "same CERT row as B01"
expect_fail D01.8 "parse error: no newline in the first 4096 bytes" "../checker dp.bin < hp8.bin" "header_parse:no_newline"
expect_fail D01.9 "parse error: stray non-padding byte after the header line" "../checker dp.bin < hp9.bin" "header_parse:unexpected_byte"
mkraw "YMROOMHDR|lattice=3×4|n=300|payload_bytes=$PB|payload_merkle=$MK|note=Größe" hp10.bin
$GEN300 -hdr-nulnl -out hp11.bin 2>/dev/null
../ymgen flip -in hp7.bin -out hp12.bin -offset 3 -xor 79
expect_pass D01.10 "header text with UTF-8 bytes in unrelated fields still passes" "../checker dp.bin < hp10.bin" '[ "$(certs <<<"$STDOUT")" = "$BASECERT" ]' "same CERT row as B01"
expect_pass D01.11 "header text padded with NULs and the newline at byte 4095 still passes" "../checker dp.bin < hp11.bin" '[ "$(certs <<<"$STDOUT")" = "$BASECERT" ]' "same CERT row as B01"
expect_fail D01.12 "parse error: NUL byte inside the header text" "../checker dp.bin < hp12.bin" "header_parse:nul_inside_header_text"

head -c $((4096 + PB - 100)) s300.bin >short1.bin
head -c 100 s300.bin >short2.bin
expect_fail D02.1 "short stream: cut 100 bytes before the end of the payload" "../checker dp.bin < short1.bin" "short_stream"
expect_fail D02.2 "short stream: only 100 header bytes" "../checker dp.bin < short2.bin" "short_stream:header"
expect_fail D02.3 "short stream: empty input" "../checker dp.bin < /dev/null" "short_stream:header"

{
	cat s300.bin
	printf '\001'
} >long1.bin
$GEN300 -hdr-pb $((PB + 8)) -out long2.bin 2>/dev/null
$GEN300 -hdr-pb $((PB - 8)) -out short3.bin 2>/dev/null
expect_fail D03.1 "long stream: a nonzero byte appended after the zero padding" "../checker dp.bin < long1.bin" "nonzero_padding"
expect_fail D03.2 "long stream: header payload_bytes 8 larger than the rows (8 extra payload bytes after row n-1)" "../checker dp.bin < long2.bin" "payload_has_bytes_after_row_n"
expect_fail D03.3 "header payload_bytes 8 smaller than the rows (last row runs past the payload)" "../checker dp.bin < short3.bin" "payload_ends_inside_row"

$GEN300 -hdr-n 299 -out cnt1.bin 2>/dev/null
$GEN300 -hdr-n 301 -out cnt2.bin 2>/dev/null
../ymgen dresize -in dp.bin -out dp299.bin -delta -8
../ymgen dresize -in dp.bin -out dp301.bin -delta 8
expect_fail D04.1 "count mismatch: header n=299 but the payload holds 300 rows" "../checker dp299.bin < cnt1.bin" "payload_has_bytes_after_row_n|column_out_of_range"
expect_fail D04.2 "count mismatch: header n=301 but the payload holds 300 rows" "../checker dp301.bin < cnt2.bin" "payload_ends_before_row_n"

$GEN300 -defect colrange -out colr.bin 2>/dev/null
expect_fail D05 "column out of range (j = n), merkle consistent" "../checker dp.bin < colr.bin" "column_out_of_range"

for v in 1 -1; do
	../ymgen dset -in dp.bin -out dflat$v.bin -h $FL -v $v
	expect_fail D06.$v "flat row $FL with d = $v" "../checker dflat$v.bin < s300.bin" "flat_row_d_nonzero"
done

$GEN300 -defect posoff -out posoff.bin 2>/dev/null
expect_fail D07 "positive off-diagonal entry (coupling -1 on one edge; rows still sum to 0, W*Z still symmetric, merkle consistent)" "../checker dp.bin < posoff.bin" "positive_offdiagonal"

../ymgen flip -in s300.bin -out pad1.bin -offset $((4096 + PB + 10)) -xor 1
expect_fail D08 "nonzero padding byte" "../checker dp.bin < pad1.bin" "nonzero_padding"

$GEN300 -hdr-merkle 0000000000000000000000000000000000000000000000000000000000000000 -out mk1.bin 2>/dev/null
expect_fail D09.1 "merkle mismatch: header payload_merkle replaced" "../checker dp.bin < mk1.bin" "merkle_mismatch"
expect_fail D09.2 "merkle pin: -expect-merkle differs from the header" "../checker -expect-merkle ${MK%?}0 dp.bin < s300.bin" "header_pin_mismatch"
expect_fail D09.3 "n pin: -expect-n differs from the header" "../checker -expect-n 301 dp.bin < s300.bin" "header_pin_mismatch"
expect_pass D09.4 "all three pins equal to the header values" "../checker -expect-n 300 -expect-payload-bytes $PB -expect-merkle $MK dp.bin < s300.bin"

$GEN300 -defect rowsum -out rowsum.bin 2>/dev/null
expect_fail D10 "row sum not 0 (one diagonal +1; W*Z still symmetric, merkle consistent)" "../checker dp.bin < rowsum.bin" "row_sum_nonzero"

$GEN300 -defect asym -out asym.bin 2>/dev/null
expect_fail D11 "W-symmetry identity fails (one weight changed; rows sum to 0, signs fine, merkle consistent)" "../checker dp.bin < asym.bin" "w_symmetry_mismatch"

run "../ymgen ref -store ovf.bin ovf-d62.bin"
refbits=$(field max_num_bits <<<"$STDOUT")
expect_fail D12 "arithmetic overflow: numerator magnitude >= 2^127 (d = 1, 2^62); exact value has $refbits bits per the big-int reference" "../checker ovf-d62.bin < ovf.bin" "arithmetic_overflow"

for delta in -8 8 -1 1; do
	../ymgen dresize -in dp.bin -out dlen$delta.bin -delta $delta
	expect_fail D13.$delta "d file length 8n$([ $delta -gt 0 ] && echo +)$delta bytes" "../checker dlen$delta.bin < s300.bin" "d_length_not_8n"
done
expect_fail D14.1 "no d file argument" "../checker < s300.bin" "usage"
expect_fail D14.2 "d file does not exist" "../checker missing.bin < s300.bin" "d_open_error"

printf '1 0 : 0:0\n2 0 : 1:0\n' >allflat.txt
../ymgen text -in allflat.txt -out allflat.bin
../ymgen dlist -vals 0,0 -out allflat-d.bin
expect_fail D15 "no non-flat rows (no ratio exists)" "../checker allflat-d.bin < allflat.bin" "no_nonflat_rows"

# Large intermediate files are removed to save disk; CONTROLS.hbp is the record.
find "$W" -type f -size +1M -delete

# ---------------------------------------------------------------------------
{
	echo
	echo "SUMMARY|controls=$((NMATCH + NMISS))|match=$NMATCH|mismatch=$NMISS|json=0"
} >>"$OUT"
echo "controls=$((NMATCH + NMISS)) match=$NMATCH mismatch=$NMISS" >&2
[ $NMISS = 0 ]
