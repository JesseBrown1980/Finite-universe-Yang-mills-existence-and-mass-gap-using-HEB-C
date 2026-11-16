#!/bin/sh
# #137 stage A, end to end.   sh stage_a.sh GROUP-0.v1 WORKDIR
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SPOOL=$1; W=$2
R=$HERE/rust/target/release/y137_rows
python3 -I -B "$HERE/stage_a_check.py" select "$SPOOL" "$W"
cut -d' ' -f1 "$W/audit128.txt" | "$R" rows > "$W/audit128.rows"
"$R" rows < "$W/random.txt" > "$W/random.rows"
"$R" wide < "$W/wide.txt" > "$W/wide.out"
python3 -I -B "$HERE/stage_a_check.py" compare "$W"
"$R" bench 2000000
