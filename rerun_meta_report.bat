@echo off
setlocal enabledelayedexpansion

set "PYTHON_BIN=%PYTHON_BIN%"
if "%PYTHON_BIN%"=="" set "PYTHON_BIN=python"

set "META_NAME=%~1"
if "%META_NAME%"=="" set "META_NAME=SR1"

set "WORK_DIR=%~2"
if "%WORK_DIR%"=="" set "WORK_DIR=all_txt"

set "REPORT_FILE=%~3"
if "%REPORT_FILE%"=="" set "REPORT_FILE=report_doc\%META_NAME%_output.docx"

set "DRY_RUN=%DRY_RUN%"
if "%DRY_RUN%"=="" set "DRY_RUN=0"

if /I "%META_NAME%"=="-h" goto :usage
if /I "%META_NAME%"=="--help" goto :usage

set "SCRIPT_DIR=%~dp0"
set "MPLCONFIGDIR=%WORK_DIR%\.mplconfig"

if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"
for %%I in ("%REPORT_FILE%") do if not exist "%%~dpI" mkdir "%%~dpI"
if not exist "%MPLCONFIGDIR%" mkdir "%MPLCONFIGDIR%"

echo Meta name   : %META_NAME%
echo Work dir    : %WORK_DIR%
echo Report file : %REPORT_FILE%
echo Python      : %PYTHON_BIN%

call :run_cmd "%PYTHON_BIN%" "%SCRIPT_DIR%main.py" -c meta_check -n "%META_NAME%" -data "%WORK_DIR%"
if errorlevel 1 exit /b 1

call :run_cmd "%PYTHON_BIN%" "%SCRIPT_DIR%main.py" -c merge -n "%META_NAME%" -data "%WORK_DIR%" -s "%REPORT_FILE%"
if errorlevel 1 exit /b 1

if "%DRY_RUN%"=="0" (
  if not exist "%REPORT_FILE%" (
    echo Final report was not created: %REPORT_FILE%
    exit /b 1
  )
  for %%I in ("%REPORT_FILE%") do (
    if %%~zI LEQ 0 (
      echo Final report is empty: %REPORT_FILE%
      exit /b 1
    )
  )
)

echo.
echo Final report: %REPORT_FILE%
exit /b 0

:run_cmd
echo.
echo [RUN] %*
if "%DRY_RUN%"=="0" (
  %*
)
exit /b %errorlevel%

:usage
echo Usage:
echo   rerun_meta_report.bat [META_NAME] [WORK_DIR] [REPORT_FILE]
echo.
echo Examples:
echo   rerun_meta_report.bat
echo   rerun_meta_report.bat SR1
echo   rerun_meta_report.bat SR2 all_txt report_doc\SR2_output.docx
echo.
echo Environment variables:
echo   PYTHON_BIN  Python executable, default: python
echo   DRY_RUN     Set to 1 to print commands only
exit /b 0
