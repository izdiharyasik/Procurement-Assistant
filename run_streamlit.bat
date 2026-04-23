@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :err

python -m pip install --upgrade pip
if errorlevel 1 goto :err
python -m pip install -r requirements.txt
if errorlevel 1 goto :err

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env from .env.example. Edit it before running AI-powered workflows.
)

for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
  set "k=%%A"
  set "v=%%B"
  if not "!k!"=="" if /I not "!k:~0,1!"=="#" set "!k!=!v!"
)

streamlit run streamlit_app.py
exit /b %errorlevel%

:err
echo Setup failed. Check the error output above.
exit /b 1
