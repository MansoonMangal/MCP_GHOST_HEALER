# Run AI Brain locally (no Docker) for debugging before Render deploy.
# From repo root: .\scripts\run_brain_local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\mcp-server"

if (-not $env:GHOST_API_KEY) {
    $env:GHOST_API_KEY = "local-dev-key"
    Write-Host "Using GHOST_API_KEY=local-dev-key (set your own to override)"
}

if (Test-Path "..\.venv\Scripts\pip.exe") {
    ..\.venv\Scripts\pip install -r requirements.txt -q
    ..\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000
} else {
    pip install -r requirements.txt -q
    uvicorn app.main:app --host 0.0.0.0 --port 8000
}
