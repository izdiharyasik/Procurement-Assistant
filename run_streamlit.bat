@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul && set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  echo Python was not found on PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/windows/
  echo Then reopen Command Prompt and run this script again.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :err
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :err

python -m pip install --upgrade pip
if errorlevel 1 goto :err
python -m pip install -r requirements.txt
if errorlevel 1 goto :err
python -c "import streamlit" >nul 2>nul
if errorlevel 1 (
  echo Streamlit is not importable in this environment.
  echo Re-run this script and check pip/network output above.
  goto :err
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env from .env.example. Edit it before running AI-powered workflows.
)

for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
  set "k=%%A"
  set "v=%%B"
  if not "!k!"=="" if /I not "!k:~0,1!"=="#" set "!k!=!v!"
)

echo.
echo Starting Streamlit...
echo If your browser shows ERR_CONNECTION_REFUSED, keep this window open and read errors here.
echo Local URL: http://localhost:8501
echo Backup URL: http://127.0.0.1:8501
echo.

python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
exit /b %errorlevel%

:err
echo Setup failed. Check the error output above.
exit /b 1
