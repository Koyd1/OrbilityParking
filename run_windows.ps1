$ErrorActionPreference = "Stop"
$venvPath = Join-Path $PWD ".venv"
$python = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $python)) {
    # Write-Error "Не найдено виртуальное окружение .venv. Сначала запустите scripts\setup_windows.ps1"
    Write-Error "The virtual environment .venv was not found. Please run scripts\setup_windows.ps1 first."
}

Write-Host "Starting application..."
& $python main.py
