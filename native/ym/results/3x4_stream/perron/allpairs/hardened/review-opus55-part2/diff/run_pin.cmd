@echo off
set TMP=C:\tmp\opus55\allpairs-review-20261103\diff\tmp
set TEMP=C:\tmp\opus55\allpairs-review-20261103\diff\tmp
start "" /belownormal /b /wait "C:\tmp\opus55\allpairs-review-20261103\bin\fuzz-pin.exe" %1 %2 %3 %4 > NUL 2> "C:\tmp\opus55\allpairs-review-20261103\diff\out\%5.err"
echo exit=%errorlevel% >> "C:\tmp\opus55\allpairs-review-20261103\diff\out\%5.err"
