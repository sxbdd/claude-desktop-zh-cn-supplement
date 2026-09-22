@echo off
chcp 936 >nul
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=gbk

rem ---- 自提权；带 elevated 参数进来就直接干活，避免提权判断失误时死循环 ----
if "%~1"=="elevated" goto run
net session >nul 2>&1 && goto run
echo 修改 Claude Desktop 的程序文件需要管理员权限，正在请求提权……
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList 'elevated' -Verb RunAs"
exit /b

:run
set PY=
where python >nul 2>nul && set PY=python
if "%PY%"=="" (where py >nul 2>nul && set PY=py)
if "%PY%"=="" (
    echo.
    echo   没有找到 Python。请先安装 Python 3
    echo   （安装时记得勾选 "Add python.exe to PATH"），然后重试。
    echo.
    pause
    exit /b 1
)

tasklist /fi "imagename eq Claude.exe" /nh 2>nul | "%SystemRoot%\System32\find.exe" /i "Claude.exe" >nul
if not errorlevel 1 (
    echo.
    echo   提示：Claude Desktop 正在运行。建议先从托盘图标完全退出它，
    echo   否则程序文件可能被占用导致写入失败。
    echo.
)

"%PY%" "%~dp0apply.py"
echo.
pause
