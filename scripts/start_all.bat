@echo off
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo Run scripts\setup.bat first.
  pause
  exit /b 1
)
set "PYTHON=%CD%\.venv\Scripts\python.exe"
echo Open http://localhost:5173 after Vite starts.
npm run dev
