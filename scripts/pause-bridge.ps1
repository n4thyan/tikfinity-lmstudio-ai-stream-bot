$ErrorActionPreference = "Stop"
$pauseFile = "config\PAUSE_STREAM.txt"

if (-not (Test-Path "config")) {
    New-Item -ItemType Directory -Path "config" | Out-Null
}

Set-Content -Path $pauseFile -Value "paused" -Encoding UTF8
Write-Host "Bridge pause file created: $pauseFile" -ForegroundColor Yellow
Write-Host "The running bridge will stop processing new chat replies until this file is removed."
