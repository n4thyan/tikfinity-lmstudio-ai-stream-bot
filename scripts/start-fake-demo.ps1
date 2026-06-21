$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Virtual environment not found. Run .\scripts\windows-setup.ps1 first." -ForegroundColor Red
    exit 1
}

& $python -m src.bridge --demo --fake-llm
