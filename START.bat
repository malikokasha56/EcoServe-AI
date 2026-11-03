@echo off
setlocal EnableExtensions
title EcoServe AI
set "PYTHONUNBUFFERED=1"
cd /d "%~dp0backend"

set "VENV=%~dp0backend\.venv"
set "VPY=%VENV%\Scripts\python.exe"

rem Reuse the environment only if it works on this machine (a copied .venv from another PC will not).
if exist "%VPY%" (
    "%VPY%" -c "import flask, flask_sqlalchemy, flask_jwt_extended, flask_bcrypt, flask_cors, waitress" >nul 2>nul
    if not errorlevel 1 goto run
    echo Existing environment is not usable here, rebuilding it...
    rmdir /s /q "%VENV%"
)

echo.
echo  First run: setting up EcoServe AI (one time only, about a minute)...
echo.
call :findpython
if not defined PY (
    echo  Python 3.9 to 3.13 was not found.
    echo  Install Python 3.12 from https://www.python.org/downloads/ and tick "Add python.exe to PATH",
    echo  then double-click START.bat again.
    pause
    exit /b 1
)
echo  Using %PY%
%PY% -m venv "%VENV%"
if errorlevel 1 (
    echo  Could not create the Python environment.
    pause
    exit /b 1
)

rem Install from the bundled wheels first (works offline), fall back to the internet.
"%VPY%" -m pip install --disable-pip-version-check -q --no-index --find-links "%~dp0backend\wheels" -r requirements.txt
if errorlevel 1 (
    echo  Offline install did not cover this Python version, downloading packages instead...
    "%VPY%" -m pip install --disable-pip-version-check -q -r requirements.txt
)
if errorlevel 1 (
    echo  Installing the packages failed. Check the internet connection and try again.
    rmdir /s /q "%VENV%"
    pause
    exit /b 1
)

:run
"%VPY%" run.py %*
echo.
echo  EcoServe AI has stopped.
pause
exit /b 0

:findpython
for %%V in (3.12 3.11 3.13 3.10 3.9) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
    )
)
if not defined PY (
    python -c "import sys; sys.exit(0 if (3, 9) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
    python3 -c "import sys; sys.exit(0 if (3, 9) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>nul && set "PY=python3"
)
exit /b 0
