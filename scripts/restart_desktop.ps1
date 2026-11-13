$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$pidPath = Join-Path $env:APPDATA "yumeVNGame\desktop.pid"
if (Test-Path -LiteralPath $pidPath) {
  $pidText = (Get-Content -LiteralPath $pidPath -Raw).Trim()
  if ($pidText -match "^\d+$") {
    $proc = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
    if ($proc) {
      Write-Host "[restart] stopping desktop pid $($proc.Id)" -ForegroundColor Yellow
      Stop-Process -Id $proc.Id -Force
    }
  }
  Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Milliseconds 700
$python = (Get-Command python).Source
Write-Host "[restart] launching source desktop app..." -ForegroundColor Green
Start-Process -FilePath $python -ArgumentList "desktop.py" -WorkingDirectory $root -WindowStyle Normal

