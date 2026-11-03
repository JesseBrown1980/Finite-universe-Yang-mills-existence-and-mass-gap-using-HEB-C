#!/bin/bash
# Read-only runs on the 3x4 (+,+) store. Operator direction: "go on all three, I agree, yes" (2026-11-01).
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
DEV="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
L=$RD/P0BALL.log
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "P0_START|at=$(stamp)|flatcomp_sha256=$(sha256sum $RD/flatcomp.exe | cut -c1-64)|roomball_sha256=$(sha256sum $RD/roomball.exe | cut -c1-64)|json=0" >> $L
t0=$(date +%s)
$RD/flatcomp.exe --room "$DEV" 0 > $RD/P0-3x4.out 2> $RD/P0-3x4.err
echo "P0_RUN|exit=$?|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
cat $RD/P0-3x4.out >> $L
mkdir -p $RD/m34
t0=$(date +%s)
$RD/roomball.exe "$DEV" 0 5 "D:/ym-3x4-room-run/p0-ball/m34/m" > $RD/ROOMBALL-3x4.out 2> $RD/ROOMBALL-3x4.err
echo "BALL_RUN|exit=$?|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
cat $RD/ROOMBALL-3x4.out >> $L
(cd $RD/m34 && sha256sum m.K*) >> $L
echo "DONE|at=$(stamp)|json=0" >> $L
