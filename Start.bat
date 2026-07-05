@echo off
title WMV Video File Corrector
echo Starting WMV Video File Corrector...
echo.
cd /d "%~dp0"
start "" http://127.0.0.1:5000
python app.py
pause
