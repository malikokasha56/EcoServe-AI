@echo off
setlocal
title EcoServe AI - tests
cd /d "%~dp0backend"
set "VPY=%~dp0backend\.venv\Scripts\python.exe"
if not exist "%VPY%" (
    echo  Run START.bat once first to set up EcoServe AI, then run this file again.
    pause
    exit /b 1
)
"%VPY%" -c "import pytest" >nul 2>nul
if errorlevel 1 (
    echo  Installing the test runner ^(one time only^)...
    "%VPY%" -m pip install --disable-pip-version-check -q --no-index --find-links "%~dp0backend\wheels" -r requirements-dev.txt
    if errorlevel 1 "%VPY%" -m pip install --disable-pip-version-check -q -r requirements-dev.txt
)
rem The evidence tables in docs\testing come from the full run with the ML libraries; keep them as they are.
set "ECOSERVE_NO_EVIDENCE=1"
echo.
echo  Running the EcoServe AI test suite. Machine learning tests are skipped if those libraries are not installed.
echo.
"%VPY%" -m pytest tests -v -p no:cacheprovider -rs
echo.
pause
