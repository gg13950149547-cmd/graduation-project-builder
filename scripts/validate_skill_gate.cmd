@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%validate_skill_gate.py"

if defined VIRTUAL_ENV if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
  "%VIRTUAL_ENV%\Scripts\python.exe" "%PY_SCRIPT%" %*
  exit /b !errorlevel!
)

for /f "delims=" %%I in ('dir /b /ad /o-n "%LocalAppData%\Programs\Python\Python*" 2^>nul') do (
  if exist "%LocalAppData%\Programs\Python\%%~I\python.exe" (
    "%LocalAppData%\Programs\Python\%%~I\python.exe" "%PY_SCRIPT%" %*
    exit /b !errorlevel!
  )
)

for /f "delims=" %%I in ('where python 2^>nul') do (
  echo %%~fI | findstr /i /v "\\WindowsApps\\" >nul && (
    "%%~fI" "%PY_SCRIPT%" %*
    exit /b !errorlevel!
  )
)

echo No usable Python executable found outside WindowsApps stub. 1>&2
exit /b 9009
