@echo off
chcp 936 >nul
setlocal
cd /d "%~dp0"

set PY=
where python >nul 2>nul && set PY=python
if "%PY%"=="" (where py >nul 2>nul && set PY=py)

if "%PY%"=="" (
    echo.
    echo   没有找到 Python。请先安装 Python 3 后重试。
    echo.
    pause
    exit /b 1
)

"%PY%" "%~dp0apply.py"
echo.
pause
