@echo off
set TEST_DIR=C:\autotest
set BINARY_DIR=\\172.16.0.73\HY5_Binary

if exist Y: subst Y: /d

subst Y: %BINARY_DIR%

REM Get the Latest SVN version
for /f "delims=" %%a in ('dir /b /ad /od "Y:\"') do (
    set "TARGET_BUILD=%%~a"
)

REM Save current tested version for comparision
echo set TESTED_VERSION=%TARGET_BUILD%>GetTestedVersion.bat
set TARGET_BIN=%BINARY_DIR%\%TARGET_BUILD%\RP001\HY5*.bin

echo Target Build for Test is:%TARGET_BUILD% >TestResult.log

REM Clean up test directory and copy target binary
if exist %TEST_DIR%/*.bin del /f /q *.bin
echo Binary for test: %TARGET_BIN%
echo Copying BIOS Image to local harddrive
if exist %TARGET_BIN% (
    echo F|xcopy /y %TARGET_BIN% %TEST_DIR%\RP001.bin
) else (
    echo "No binary found, pribably the latest build failed."
)

REM Run Daily Test Script.

call python dailytest.py