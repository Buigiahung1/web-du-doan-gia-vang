@echo off
chcp 65001 > nul
cd /d "%~dp0"
call .venv\Scripts\activate.bat
set USE_STUB_MODEL=false
python scripts\run_demo.py
pause