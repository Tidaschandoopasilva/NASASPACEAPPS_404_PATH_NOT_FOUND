@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto failed
if exist "wheelhouse\*.whl" (
  .venv\Scripts\python.exe -m pip install --no-index --find-links wheelhouse -r requirements-desktop.txt
) else (
  .venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
)
if errorlevel 1 goto failed
echo Setup complete. Open start_desktop.bat.
pause
exit /b 0
:failed
echo Desktop setup failed. See README_DESKTOP.md for prerequisites.
pause
exit /b 1
