@echo off
chcp 936 >nul
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=gbk

rem ---- 自提权；带 elevated 参数进来就直接干活 ----
if "%~1"=="elevated" goto run
net session >nul 2>&1 && goto run
echo 还原 Claude Desktop 的程序文件需要管理员权限，正在请求提权……
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList 'elevated' -Verb RunAs"
exit /b

:run
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

echo ============================================================
echo  卸载补充汉化（还原到第 2 步之前的状态）
echo ============================================================
echo.
echo  注意：这里只撤销「第 2 步」的补充汉化。
echo  要连上游汉化包一起去掉，请再运行 upstream\install-windows.bat，
echo  在里面选卸载选项。
echo.
pause

"%PY%" "%~dp0apply.py" --uninstall
echo.
pause
