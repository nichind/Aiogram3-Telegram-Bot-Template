@echo off

set PYTHON_VERSION=3.11.0
set PYTHON_MSI=python-%PYTHON_VERSION%.msi

echo Checking if python is installed...
python --version > nul 2>&1
if errorlevel 9009 (
    echo Installing python...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/%PYTHON_VERSION%/python-3.11.0-amd64.exe', 'python-3.11.0-amd64.exe')"
    python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    start "" "%~f0"
    exit
)

echo Creating virtual environment...
python -m venv %~dp0.venv
call .\.venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
FOR /F %%i IN (requirements.txt) DO python -m pip install %%i

echo Running main.py...
python main.py

pause

@REM Batch file "install-python-and-requirements-and-run-main.bat" made by nichind (https://github.com/nichind)
@REM Please do not remove this comment. ^-^