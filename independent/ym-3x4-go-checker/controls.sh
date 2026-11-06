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
	echo "# Layout (owner's payload-only decision): header 4096 bytes + payload_bytes; rows first, then zero bytes up to"
	echo "# payload_bytes (inside the merkle); bytes after payload_bytes are room-file bytes, read and counted, never interpreted."
	echo "# Controls marked [CHANGED ...], [EXTENDED ...], [renamed ...] or [NEW] are the ones that decision changed; section E is new."
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
	expect_pass B05.$pad "[STORE field renamed by the payload-only decision: padding_bytes -> after_payload_bytes] $pad zero bytes after header+payload_bytes (room-file bytes, not store)" "../checker dp.bin < s300pad$pad.bin" \
		'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && [ "$(field after_payload_bytes <<<"$STDOUT")" = '"$pad"' ]' "same CERT row as B01, after_payload_bytes=$pad"
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
rm -f sector-*

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
# Extended for the payload-only decision: random zero tails inside payload_bytes,
# random room-file bytes after payload_bytes (zero, nonzero or room-stub words),
# and a nonzero byte poked into the zero tail (with or without re-merkling).
fz_total=0 fz_pass=0 fz_fail=0 fz_bad=0 fz_list="" fz_ztail=0 fz_after=0 fz_poke=0
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
	ztail=0
	[ $((RANDOM % 3)) = 0 ] && ztail=$((1 + RANDOM % 3000))
	after=0
	[ $((RANDOM % 3)) != 0 ] && after=$((RANDOM % 5000))
	fills=(zero nonzero rooms)
	pfill=${fills[$((RANDOM % 3))]}
	../ymgen random -rows $rows -flat $flat -deg $deg -wmax $wmax -cmax $cmax -magmax $mm -seed $((1000 + i)) $opts ${defect:+-defect $defect} \
		-ztail $ztail -pad $after -pad-fill $pfill -pad-seed $i -out fz.bin 2>/dev/null || continue
	[ $ztail -gt 0 ] && fz_ztail=$((fz_ztail + 1))
	[ $after -gt 0 ] && [ $pfill != zero ] && fz_after=$((fz_after + 1))
	if [ $ztail -gt 0 ] && [ $((RANDOM % 4)) = 0 ]; then
		fpb=$(head -c 4096 fz.bin | tr -d '\000' | head -n1 | field payload_bytes)
		../ymgen flip -in fz.bin -out fz.bin -offset $((4096 + fpb - 1 - RANDOM % ztail)) -xor $((1 + RANDOM % 255))
		[ $((RANDOM % 2)) = 0 ] && ../ymgen remerkle -in fz.bin -out fz.bin
		fz_poke=$((fz_poke + 1))
	fi
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
record B12 "[EXTENDED for the payload-only decision] differential fuzz: $fz_total random stores (1..400 rows, weights and couplings up to 2000, mag up to 65535, d up to 2^63-1, random defects and bad d entries; random zero tails inside payload_bytes, random room-file bytes after it, nonzero bytes poked into the zero tail) vs the big-int reference" \
	"controls.sh section B12 (../checker fzd.bin fzd2.bin < fz.bin  VERSUS  ../ymgen ref -store fz.bin fzd.bin fzd2.bin)" \
	"every case: both pass with identical rows, or both fail (exit 2, one FAIL line)" \
	"total=$fz_total both_pass_identical=$fz_pass both_fail=$fz_fail disagreements=$fz_bad with_zero_tail=$fz_ztail with_nonzero_after_payload=$fz_after zero_tail_pokes=$fz_poke$fz_list" $([ $fz_bad = 0 ] && echo 1 || echo 0) ""

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
expect_pass D03.1 "[CHANGED by the payload-only decision; was: fail nonzero_padding] a nonzero byte appended after the 4096 zero bytes that follow payload_bytes: room-file bytes, not store" "../checker dp.bin < long1.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && [ "$(field after_payload_bytes <<<"$STDOUT")" = 4097 ] && [ "$(field payload_zero_tail_bytes <<<"$STDOUT")" = 0 ]' \
	"same CERT row as B01, after_payload_bytes=4097, payload_zero_tail_bytes=0"
expect_fail D03.2 "[CHANGED by the payload-only decision; was: fail payload_has_bytes_after_row_n] header payload_bytes 8 larger than the rows: the 8 payload bytes after row n-1 are zero (an allowed zero tail), but the header merkle covers only the rows" "../checker dp.bin < long2.bin" "merkle_mismatch"
../ymgen remerkle -in long2.bin -out long2-remerkled.bin
expect_pass D03.2.remerkled "[NEW] the D03.2 store with the header merkle recomputed over all payload_bytes: passes with an 8-byte zero tail" "../checker dp.bin < long2-remerkled.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && [ "$(field rows_end_payload_offset <<<"$STDOUT")" = '"$PB"' ] && [ "$(field payload_zero_tail_bytes <<<"$STDOUT")" = 8 ] && [ "$(field after_payload_bytes <<<"$STDOUT")" = 4088 ]' \
	"same CERT row as B01, rows_end_payload_offset=$PB, payload_zero_tail_bytes=8, after_payload_bytes=4088"
expect_fail D03.3 "header payload_bytes 8 smaller than the rows (last row runs past the payload)" "../checker dp.bin < short3.bin" "payload_ends_inside_row"

$GEN300 -hdr-n 299 -out cnt1.bin 2>/dev/null
$GEN300 -hdr-n 301 -out cnt2.bin 2>/dev/null
../ymgen dresize -in dp.bin -out dp299.bin -delta -8
../ymgen dresize -in dp.bin -out dp301.bin -delta 8
expect_fail D04.1 "[reason renamed by the payload-only decision: payload_has_bytes_after_row_n -> payload_zero_tail_nonzero] count mismatch: header n=299 but the payload holds 300 rows (row 299 lies where the zero tail must be)" "../checker dp299.bin < cnt1.bin" "payload_zero_tail_nonzero|column_out_of_range"
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
expect_pass D08 "[CHANGED by the payload-only decision; was: fail nonzero_padding] one nonzero byte 10 bytes after payload_bytes: room-file bytes, not store" "../checker dp.bin < pad1.bin" \
	'[ "$(strip <<<"$STDOUT")" = "$(../checker dp.bin <s300.bin | strip)" ] && [ "$(field after_payload_bytes <<<"$STDOUT")" = 4096 ]' \
	"output identical to the unflipped store B01 (same CERT and STORE rows), after_payload_bytes=4096"

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

# ---------------------------------------------------------------------------
# E. The owner's payload-only layout decision. The store is the 4096-byte header
#    plus payload_bytes: rows first, then zero bytes up to payload_bytes (inside
#    the merkle). Bytes after payload_bytes belong to the room file: read to end
#    of input and counted, never interpreted, never required to be zero.
ZT=742160       # zero-tail length of the real store (rows end 742,160 bytes before payload_bytes)
AFTER=349114368 # room-file bytes after payload_bytes in the real sector-374
ZPB=$((PB + ZT))
$GEN300 -ztail $ZT -pad 0 -out z.bin 2>/dev/null
$GEN300 -ztail 1 -pad 0 -out z1.bin 2>/dev/null
ZMK=$(head -c 4096 z.bin | tr -d '\000' | head -n1 | field payload_merkle)
zfields() { # rows_end_payload_offset payload_zero_tail_bytes after_payload_bytes payload_bytes
	[ "$(field rows_end_payload_offset <<<"$STDOUT")" = "$1" ] && [ "$(field payload_zero_tail_bytes <<<"$STDOUT")" = "$2" ] &&
		[ "$(field after_payload_bytes <<<"$STDOUT")" = "$3" ] && [ "$(grep '^STORE|' <<<"$STDOUT" | field payload_bytes)" = "$4" ]
}

# E01: rows followed by zero bytes inside payload_bytes pass, and the count is reported.
expect_pass E01.1 "rows followed by $ZT zero bytes inside payload_bytes (the real store's zero-tail length), nothing after" "../checker dp.bin < z.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB $ZT 0 $ZPB" \
	"same CERT row as B01; rows_end_payload_offset=$PB payload_zero_tail_bytes=$ZT after_payload_bytes=0 payload_bytes=$ZPB"
expect_pass E01.2 "rows followed by a 1-byte zero tail inside payload_bytes" "../checker dp.bin < z1.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB 1 0 $((PB + 1))" \
	"same CERT row as B01; rows_end_payload_offset=$PB payload_zero_tail_bytes=1 after_payload_bytes=0"
compare_ref E01.3 "zero tail of $ZT bytes: fast checker equals the big-int reference (Perron, random and near-2^62 d)" z.bin dp.bin dr.bin db.bin
cu=$(tail -c +4097 z.bin | head -c $ZPB | split -b 16777216 --filter='sha256sum' | cut -c1-64 | tr -d '\n' | sha256sum | cut -c1-64)
cr=$(tail -c +4097 z.bin | head -c $PB | split -b 16777216 --filter='sha256sum' | cut -c1-64 | tr -d '\n' | sha256sum | cut -c1-64)
record E01.4 "the zero tail is inside the merkle: coreutils merkle over all payload_bytes equals the header; the merkle over the rows only does not" \
	"tail -c +4097 z.bin | head -c $ZPB | split -b 16777216 --filter=sha256sum | cut -c1-64 | tr -d '\\n' | sha256sum   (and the same with head -c $PB)" \
	"$ZMK; rows-only merkle different" "payload_bytes merkle=$cu rows-only merkle=$cr" $([ "$cu" = "$ZMK" ] && [ "$cr" != "$ZMK" ] && echo 1 || echo 0) ""
../ymgen random -rows 50000 -flat 500 -deg 30 -seed 12 -dup -target-payload 33554440 -ztail 16777216 -out m2z.bin 2>/dev/null
expect_pass E01.5 "multi-leaf: rows end 8 bytes into leaf 2, the 16 MiB zero tail runs over the leaf boundary into an 8-byte leaf 3" "../checker m2-dp.bin m2-db.bin < m2z.bin" \
	'zfields 33554440 16777216 4096 50331656' "rows_end_payload_offset=33554440 payload_zero_tail_bytes=16777216 after_payload_bytes=4096 payload_bytes=50331656"
compare_ref E01.5.ref "the same multi-leaf zero-tail store, fast vs big-int reference" m2z.bin m2-dp.bin m2-db.bin
../ymgen random -rows 90000 -flat 900 -deg 30 -seed 11 -target-payload 50331648 -ztail 5 -out m3z.bin
expect_pass E01.6 "multi-leaf: rows end exactly at the end of leaf 2, the zero tail is a 5-byte leaf 3 of its own" "../checker m3-dp.bin m3-db.bin < m3z.bin" \
	'zfields 50331648 5 4096 50331653' "rows_end_payload_offset=50331648 payload_zero_tail_bytes=5 after_payload_bytes=4096"
compare_ref E01.6.ref "the same leaf-aligned zero-tail store, fast vs big-int reference" m3z.bin m3-dp.bin m3-db.bin
rm -f m3z.bin

# E02/E03: one nonzero byte in the zero tail fails, with the merkle recomputed
# (only the zero-tail check can catch it) and with the original merkle.
for spec in "first:$((4096 + PB)):1" "mid:$((4096 + PB + ZT / 2)):128" "last:$((4096 + ZPB - 1)):255"; do
	IFS=: read -r nm off x <<<"$spec"
	../ymgen flip -in z.bin -out zf-$nm.bin -offset $off -xor $x
	../ymgen remerkle -in zf-$nm.bin -out zfr-$nm.bin
	expect_fail E02.$nm "one nonzero byte in the zero tail ($nm tail byte, stream offset $off, xor $x), header merkle recomputed to match" \
		"../checker dp.bin < zfr-$nm.bin" "payload_zero_tail_nonzero"
	expect_fail E03.$nm "the same nonzero zero-tail byte with the original header merkle" "../checker dp.bin < zf-$nm.bin" "payload_zero_tail_nonzero"
done
rmk=$(head -c 4096 zfr-mid.bin | tr -d '\000' | head -n1 | field payload_merkle)
cu=$(tail -c +4097 zfr-mid.bin | head -c $ZPB | split -b 16777216 --filter='sha256sum' | cut -c1-64 | tr -d '\n' | sha256sum | cut -c1-64)
record E02.merkle "the re-merkled E02.mid store really has a matching merkle (coreutils), different from the original, so in E02 only the zero-tail check caught the byte" \
	"tail -c +4097 zfr-mid.bin | head -c $ZPB | split -b 16777216 --filter=sha256sum | cut -c1-64 | tr -d '\\n' | sha256sum" \
	"$rmk (and not $ZMK)" "$cu" $([ "$cu" = "$rmk" ] && [ "$rmk" != "$ZMK" ] && echo 1 || echo 0) ""
off=$((4096 + 50331648))
../ymgen flip -in m2z.bin -out m2zf.bin -offset $off -xor 1
expect_fail E03.leaf3 "multi-leaf: a nonzero byte in leaf 3 (zero tail, a later leaf than the end of the rows), original merkle" "../checker m2-dp.bin < m2zf.bin" "payload_zero_tail_nonzero"
../ymgen remerkle -in m2zf.bin -out m2zf.bin
expect_fail E02.leaf3 "multi-leaf: the same leaf-3 byte with the merkle recomputed" "../checker m2-dp.bin < m2zf.bin" "payload_zero_tail_nonzero"
rm -f m2z.bin m2zf.bin

# E04: random nonzero bytes after payload_bytes (the room-file tail) pass with
# the same rows as without them, and their count is reported.
for spec in "nonzero:1:s300pad1.bin" "nonzero:4096:s300.bin" "nonzero:1000000:s300pad1000000.bin" "rooms:1000000:s300pad1000000.bin"; do
	IFS=: read -r pf pn zstore <<<"$spec"
	$GEN300 -pad $pn -pad-fill $pf -pad-seed 9 -out sa-$pf-$pn.bin 2>/dev/null
	ZREF=$(../checker dp.bin <$zstore | strip)
	nz=$(tail -c $pn sa-$pf-$pn.bin | tr -d '\000' | wc -c)
	expect_pass E04.$pf.$pn "$pn $pf bytes after payload_bytes ($nz of them nonzero): room-file bytes, not store" "../checker dp.bin < sa-$pf-$pn.bin" \
		'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && [ "$(strip <<<"$STDOUT")" = "$ZREF" ] && zfields '"$PB 0 $pn $PB"' && [ $((100 * '"$nz"')) -ge $((99 * '"$pn"')) ]' \
		"same CERT row as B01 and the same STORE row as $zstore (the same length of zero bytes); after_payload_bytes=$pn; at least 99% of those bytes nonzero"
done
$GEN300 -ztail $ZT -pad 1000000 -pad-fill rooms -pad-seed 5 -out zr.bin 2>/dev/null
expect_pass E04.z "the real layout in small: rows, a $ZT-byte zero tail, then 1000000 room-stub bytes after payload_bytes" "../checker dp.bin < zr.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB $ZT 1000000 $ZPB" \
	"same CERT row as B01; rows_end_payload_offset=$PB payload_zero_tail_bytes=$ZT after_payload_bytes=1000000"
compare_ref E04.z.ref "the same store, fast vs big-int reference (the reference also ignores the room-file bytes)" zr.bin dp.bin dr.bin db.bin

# E05: no zero tail and no trailing bytes.
expect_pass E05 "a store with no zero tail and no bytes after payload_bytes" "../checker dp.bin < s300pad0.bin" \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB 0 0 $PB" "same CERT row as B01; rows_end_payload_offset=payload_bytes=$PB, payload_zero_tail_bytes=0, after_payload_bytes=0"

# E06: pipes. The checker reads to end of input, so the writer never gets SIGPIPE.
run 'cat z.bin <(../ymgen fill -bytes '"$AFTER"' -mode rooms -seed 7) | head -c 4096 >/dev/null; echo "pipestatus=${PIPESTATUS[*]}"'
record E06.0 "sanity for E06.1: the pipestatus test can see SIGPIPE: the same writer into a reader that stops after 4096 bytes" \
	'cat z.bin <(../ymgen fill -bytes '"$AFTER"' -mode rooms -seed 7) | head -c 4096 >/dev/null; echo "pipestatus=${PIPESTATUS[*]}"' \
	"pipestatus=141 0 (cat killed by SIGPIPE)" "$STDOUT" $([ "$STDOUT" = "pipestatus=141 0" ] && echo 1 || echo 0) "$STDOUT"
expect_pass E06.1 "cat pipe with the real store's shape: rows, the $ZT-byte zero tail, then $AFTER room-stub bytes after payload_bytes, with the header pins; the writer (cat) must exit 0, not 141 (SIGPIPE)" \
	'cat z.bin <(../ymgen fill -bytes '"$AFTER"' -mode rooms -seed 7) | ../checker -expect-n 300 -expect-payload-bytes '"$ZPB"' -expect-merkle '"$ZMK"' dp.bin; ps="${PIPESTATUS[*]}"; echo "pipestatus=$ps"; [ "$ps" = "0 0" ]' \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB $ZT $AFTER $ZPB"' && grep -qx "pipestatus=0 0" <<<"$STDOUT"' \
	"pipestatus=0 0 (cat, checker); same CERT row as B01; payload_zero_tail_bytes=$ZT after_payload_bytes=$AFTER"
expect_pass E06.2 "the same, with a Go writer streaming the $AFTER bytes itself (writer exit status must be 0)" \
	'{ cat z.bin; ../ymgen fill -bytes '"$AFTER"' -mode rooms -seed 8; } | ../checker dp.bin; ps="${PIPESTATUS[*]}"; echo "pipestatus=$ps"; [ "$ps" = "0 0" ]' \
	'[ "$(certs <<<"$STDOUT")" = "$BASECERT" ] && zfields '"$PB $ZT $AFTER $ZPB"' && grep -qx "pipestatus=0 0" <<<"$STDOUT"' \
	"pipestatus=0 0; same CERT row as B01; after_payload_bytes=$AFTER"
split -n 34 -d -a 2 zr.bin zsector-
expect_pass E06.3 "zero-tail store with room-file bytes, split into 34 sector files and concatenated through a pipe" "cat zsector-* | ../checker dp.bin" \
	'[ "$(strip <<<"$STDOUT")" = "$(../checker dp.bin <zr.bin | strip)" ]' "identical to reading the single file"
expect_fail E06.4 "pipe form still fails closed: E02.mid store (nonzero zero-tail byte, merkle recomputed) followed by $AFTER room-stub bytes" \
	'cat zfr-mid.bin <(../ymgen fill -bytes '"$AFTER"' -mode rooms -seed 7) | ../checker dp.bin' "payload_zero_tail_nonzero"

# Large intermediate files are removed to save disk; CONTROLS.hbp is the record.
find "$W" -type f -size +1M -delete

# ---------------------------------------------------------------------------
{
	echo
	echo "SUMMARY|controls=$((NMATCH + NMISS))|match=$NMATCH|mismatch=$NMISS|json=0"
} >>"$OUT"
echo "controls=$((NMATCH + NMISS)) match=$NMATCH mismatch=$NMISS" >&2
[ $NMISS = 0 ]
