# Полная автоматизация для Windows без установленного Python.
# Скачивает и ставит Python 3.10 (per-user), затем вызывает setup_windows.ps1.

$ErrorActionPreference = "Stop"

$pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "Python not found. Downloading the 3.10.11 x64 installer..."
    $pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $installer = Join-Path $env:TEMP "python-3.10.11-amd64.exe"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installer

    Write-Host "Installing Python for the current user only..."
    $installDir = Join-Path $env:LocalAppData "Programs\Python\Python310"
    $args = @(
        "/quiet",
        "InstallAllUsers=0",
        "TargetDir=$installDir",
        "Include_pip=1",
        "PrependPath=0",
        "Shortcuts=0"
    )
    Start-Process -FilePath $installer -ArgumentList $args -Wait -NoNewWindow

    # Обновляем путь к только что установленному интерпретатору
    $pythonExe = Join-Path $installDir "python.exe"
    if (-not (Test-Path $pythonExe)) {
        Write-Error "Python not found after install in: $pythonExe"
    }
    $env:PATH = "$installDir;$installDir\Scripts;$env:PATH"
} 
else {
    Write-Host "Found Python: $($pythonCmd.Source)"
}

Write-Host "Running ./setup_project_for_windows.ps1..."
& "$PSScriptRoot\setup_project_for_windows.ps1" @args