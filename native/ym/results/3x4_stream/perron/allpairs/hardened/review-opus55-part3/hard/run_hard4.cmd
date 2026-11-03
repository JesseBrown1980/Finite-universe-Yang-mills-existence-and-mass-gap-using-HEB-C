@echo off
set TMP=C:\tmp\opus55\allpairs-review-20261103\hard\tmp
set TEMP=C:\tmp\opus55\allpairs-review-20261103\hard\tmp
start "" /belownormal /b /wait "C:\tmp\opus55\allpairs-review-20261103\bin\fuzz-hard4.exe" %1 %2 %3 %4 > NUL 2> "C:\tmp\opus55\allpairs-review-20261103\hard\out\%5.err"
echo exit=%errorlevel% >> "C:\tmp\opus55\allpairs-review-20261103\hard\out\%5.err"
