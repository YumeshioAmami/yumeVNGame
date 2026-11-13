$ErrorActionPreference = "SilentlyContinue"
$pidPath = Join-Path $env:APPDATA "yumeVNGame\desktop.pid"
if (Test-Path -LiteralPath $pidPath) {
  $pidText = (Get-Content -LiteralPath $pidPath -Raw).Trim()
  if ($pidText -match "^\d+$") {
    $proc = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
    if ($proc) {
      Stop-Process -Id $proc.Id -Force
      Write-Host "[stop] desktop pid $($proc.Id) stopped"
    }
  }
  Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
}

