@echo off
setlocal

REM --- Path of this BAT file ---
set SCRIPT_DIR=%~dp0

REM --- PowerShell scripts to execute ---
set PS1_FILE1=%SCRIPT_DIR%bootstrap_all_windows.ps1
set PS1_FILE2=%SCRIPT_DIR%run_windows.ps1

echo === Setting ExecutionPolicy for CurrentUser ===
powershell -NoProfile -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force"
echo ExecutionPolicy set to RemoteSigned

echo === Running first PowerShell script ===
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%PS1_FILE1%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR running %PS1_FILE1%
    exit /b 1
)

echo === Running second PowerShell script ===
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%PS1_FILE2%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR running %PS1_FILE2%
    exit /b 1
)

echo.
echo === All scripts executed successfully ===
endlocal
pause
