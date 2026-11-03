@echo off
start "" /belownormal /b /wait "C:\tmp\opus55\allpairs-review-20261103\bin\fuzz.exe" %1 %2 %3 %4 > NUL 2> "C:\tmp\opus55\allpairs-review-20261103\out\%5.err"
echo exit=%errorlevel% >> "C:\tmp\opus55\allpairs-review-20261103\out\%5.err"
