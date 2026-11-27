@echo off
chcp 65001 > nul
title GOLD AI - Khoi dong he thong
echo =========================================================================
echo       AURUM QUANT - HE THONG THEO DOI VA DU BAO GIA VANG
echo =========================================================================
echo.
echo Dang khoi tao moi truong va co so du lieu SQLite Demo...

cd /d "%~dp0"
set PYTHONPATH=backend;.
set USE_STUB_MODEL=false

:: Mo trinh duyet sau 2 giay
start "" cmd /c "timeout /t 2 /nobreak > nul & start http://127.0.0.1:8000/"


:: Chay FastAPI Backend
python scripts/run_demo.py

pause
