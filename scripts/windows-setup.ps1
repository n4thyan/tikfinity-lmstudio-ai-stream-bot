$ErrorActionPreference = "Stop"

Write-Host "Tikfinity LM Studio AI Stream Bot - Windows setup" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host ".env already exists, leaving it untouched" -ForegroundColor Yellow
}

if (-not (Test-Path ".venv")) {
    py -m venv .venv
    Write-Host "Created .venv" -ForegroundColor Green
} else {
    Write-Host ".venv already exists" -ForegroundColor Yellow
}

$python = ".\.venv\Scripts\python.exe"

& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-dev.txt

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next commands:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe -m src.doctor"
Write-Host "  .\.venv\Scripts\python.exe -m src.bridge --test-overlay"
Write-Host "  .\.venv\Scripts\python.exe -m src.bridge --demo --fake-llm"
