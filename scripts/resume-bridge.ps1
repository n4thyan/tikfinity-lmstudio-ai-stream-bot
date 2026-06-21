$ErrorActionPreference = "Stop"
$pauseFile = "config\PAUSE_STREAM.txt"

if (Test-Path $pauseFile) {
    Remove-Item $pauseFile
    Write-Host "Bridge pause file removed. Chat replies can resume." -ForegroundColor Green
} else {
    Write-Host "No pause file found. Bridge is already live." -ForegroundColor Green
}
