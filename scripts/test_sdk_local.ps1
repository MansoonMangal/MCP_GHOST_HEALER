# Local SDK verification (Windows PowerShell)
# Run from repository root:  .\scripts\test_sdk_local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Installing Python SDK (editable)" -ForegroundColor Cyan
if (Test-Path ".venv\Scripts\pip.exe") {
    .\.venv\Scripts\pip install -e .
    $Py = ".\.venv\Scripts\python.exe"
    $Ghost = ".\.venv\Scripts\ghost-healer.exe"
} else {
    pip install -e .
    $Py = "python"
    $Ghost = "ghost-healer"
}

Write-Host "==> ghost-healer doctor" -ForegroundColor Cyan
& $Ghost doctor

Write-Host "==> Unit tests" -ForegroundColor Cyan
& $Py -m pytest tests/ -q

Write-Host "==> TS SDK build" -ForegroundColor Cyan
Push-Location sdk\ts
npm install --silent
npm run build
Pop-Location

Write-Host "[OK] Local SDK checks complete." -ForegroundColor Green
Write-Host "Next: deploy Brain on Render, then set GHOST_API_KEY and run verify_slo.py"
