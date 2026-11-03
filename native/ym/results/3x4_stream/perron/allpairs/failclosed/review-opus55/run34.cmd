@echo off
start "" /belownormal /b /wait "C:\tmp\opus55\allpairs-review-20261103\bin\review-reader.exe" seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- --r %1 --k0 %2 --k1 %3 --cap 470000000 --manifest C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256 > "C:\tmp\opus55\allpairs-review-20261103\out\reader-3x4.out" 2> "C:\tmp\opus55\allpairs-review-20261103\out\reader-3x4.err"
echo exit=%errorlevel% > "C:\tmp\opus55\allpairs-review-20261103\out\reader-3x4.exit"
