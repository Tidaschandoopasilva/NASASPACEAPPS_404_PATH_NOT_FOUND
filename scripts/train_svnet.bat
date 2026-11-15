@echo off
cd /d "%~dp0.."
call .venv\Scripts\activate
set OMP_NUM_THREADS=2
set OPENBLAS_NUM_THREADS=2
python research\generate_dataset.py
if errorlevel 1 exit /b 1
python research\train_svnet.py
if errorlevel 1 exit /b 1
python research\evaluate.py
if errorlevel 1 exit /b 1
python research\report.py
if errorlevel 1 exit /b 1
python -m pytest -q
if errorlevel 1 exit /b 1
call npm run build
