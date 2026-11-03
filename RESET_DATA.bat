@echo off
title EcoServe AI - reset data
echo.
echo  This removes all sales, waste and accounts added while using the app
echo  and restores the original dataset and model results on the next START.
echo  Close the EcoServe AI window first if it is running.
echo.
choice /C YN /M "  Reset the demo data now"
if errorlevel 2 exit /b 0
del /q "%~dp0backend\instance\ecoserve.db" "%~dp0backend\instance\ecoserve.db-wal" "%~dp0backend\instance\ecoserve.db-shm" 2>nul
echo  Done. Double-click START.bat to run EcoServe AI with fresh data.
pause
