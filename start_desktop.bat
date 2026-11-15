@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup_desktop.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe desktop.py %*
if errorlevel 1 pause
