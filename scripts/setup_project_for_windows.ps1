param(
    [switch]$CpuTorch # Force CPU-only torch build (recommended on most Windows laptops)
)

$ErrorActionPreference = "Stop"

function Assert-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Error "Команда '$name' не найдена. Установите её и повторите."
    }
}

Assert-Command "python"

# Проверяем версию Python
python - <<'PY'
import sys
major, minor = sys.version_info[:2]
if (major, minor) < (3, 10):
    raise SystemExit("Нужен Python 3.10+ (текущая версия: %s)" % sys.version)
PY

$venvPath = Join-Path $PWD ".venv"
$python = Join-Path $venvPath "Scripts\python.exe"
$pip = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host "Создаю виртуальное окружение в $venvPath"
    python -m venv $venvPath
}

Write-Host "Обновляю pip/wheel..."
& $python -m pip install --upgrade pip wheel

# PyTorch: CPU-колесо для Windows (CUDA добавляйте вручную при необходимости)
if ($CpuTorch) {
    Write-Host "Ставлю torch (CPU-only) для Windows..."
    & $pip install --upgrade --index-url https://download.pytorch.org/whl/cpu torch
}

Write-Host "Ставлю зависимости из requirements.txt..."
& $pip install -r requirements.txt

# Подготовка директорий data/logs
& $python - <<'PY'
from app.config import AppConfig
cfg = AppConfig.from_env()
cfg.prepare_directories()
print("Готовы каталоги:", cfg.data_dir, cfg.log_dir)
PY

Write-Host ""
Write-Host "Готово! Запуск: .\scripts\run_windows.ps1"
