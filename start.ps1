$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host ""
Write-Host "  yumeVNGame 0.1.0 / source launcher" -ForegroundColor Cyan
Write-Host "  local-first AI visual novel runtime" -ForegroundColor DarkGray
Write-Host ""

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js 20+ is required. Install it, then run this script again."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python 3.10+ is required. Install it, then run this script again."
}

if (-not (Test-Path "node_modules")) {
  Write-Host "[setup] installing frontend dependencies..." -ForegroundColor Yellow
  npm install
}

python -c "import fastapi, uvicorn, pydantic, requests, cryptography" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "[setup] installing backend dependencies..." -ForegroundColor Yellow
  pip install -r requirements.txt
}

Write-Host "[start] launching API + Vite source server..." -ForegroundColor Green
Write-Host "[start] opening http://localhost:5173" -ForegroundColor Green
Start-Job -ScriptBlock {
  Start-Sleep -Seconds 5
  Start-Process "http://localhost:5173"
} | Out-Null

npm run dev

