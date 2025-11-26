param(
    [switch]$CpuTorch # Force CPU-only torch build (recommended on most Windows laptops)
)

$ErrorActionPreference = "Stop"

function Assert-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Error "Comand '$name' not found. Install it then try again.."
    }
}

Assert-Command "py"

# ------------------------------
# Проверка версии Python
# ------------------------------
py -c "
import sys
major, minor = sys.version_info[:2]
if (major, minor) < (3, 10):
    raise SystemExit('Нужен Python 3.10+ (текущая версия: %s)' % sys.version)
"

# ------------------------------
# Пути окружения
# ------------------------------
$venvPath = Join-Path $PWD ".venv"
$python = Join-Path $venvPath "Scripts\python.exe"
$pip = Join-Path $venvPath "Scripts\pip.exe"

# ------------------------------
# Создание виртуального окружения
# ------------------------------
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating venv in: $venvPath"
    py -m venv $venvPath
}

# ------------------------------
# Обновление pip/wheel
# ------------------------------
Write-Host "Upgrading pip/wheel..."
& $python -m pip install --upgrade pip wheel

# ------------------------------
# Установка CPU PyTorch (опционально)
# ------------------------------
if ($CpuTorch) {
    Write-Host "Downloading torch (CPU-only) for Windows..."
    & $pip install --upgrade --index-url https://download.pytorch.org/whl/cpu torch
}

# ------------------------------
# Установка зависимостей
# ------------------------------
Write-Host "Installing dependencies from requirements.txt..."
& $pip install -r requirements.txt

# ------------------------------
# Подготовка директорий с помощью AppConfig
# ------------------------------
& $python -c "
from app.config import AppConfig
cfg = AppConfig.from_env()
cfg.prepare_directories()
print('Directories ready:', cfg.data_dir, cfg.log_dir)
"

Write-Host ""
Write-Host "Ready! Run by using: ./run_windows.ps1"
