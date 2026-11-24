@echo off
chcp 65001 >nul
title AURUM QUANT - Frontend Server
echo.
echo ============================================
echo   AURUM QUANT - Khoi dong Frontend Server
echo ============================================
echo.
echo Dang khoi dong server tai http://localhost:3000 ...
echo Trinh duyet se tu dong mo.
echo.
cd /d "%~dp0frontend"
python serve.py
pause
