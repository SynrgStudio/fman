@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing virtual environment. Follow README.md first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" build.py run %*
if errorlevel 1 pause
