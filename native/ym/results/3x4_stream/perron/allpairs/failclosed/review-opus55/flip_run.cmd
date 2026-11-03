@echo off
start "" /belownormal /b /wait "C:\tmp\opus55\allpairs-review-20261103\bin\fuzz3.exe" %1 %2 %3 > NUL 2> "C:\tmp\opus55\allpairs-review-20261103\out\%4.err"
echo exit=%errorlevel% >> "C:\tmp\opus55\allpairs-review-20261103\out\%4.err"
