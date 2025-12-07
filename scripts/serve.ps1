param(
  [string]$Host = "127.0.0.1",
  [int]$Port = 8000,
  [switch]$Open,
  [switch]$Background
)

# Get project root (parent of scripts folder)
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $root

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  Write-Host "Virtual env not found at .\.venv. Please create/activate it first." -ForegroundColor Yellow
  Pop-Location; exit 1
}

. .\.venv\Scripts\Activate.ps1

$uri = "http://$Host:$Port"

if ($Open) {
  try { Start-Process $uri } catch {}
  try { Start-Process "$uri/docs" } catch {}
}

if ($Background) {
  $cmd = "cd `"$root`"; . .\.venv\Scripts\Activate.ps1; uvicorn service.api:app --host $Host --port $Port --reload"
  Start-Process -WindowStyle Hidden powershell -ArgumentList $cmd | Out-Null
  Write-Host "Server started in background at $uri"
  Write-Host "Docs: $uri/docs"
} else {
  Write-Host "Homepage: $uri"
  Write-Host "Docs: $uri/docs"
  uvicorn service.api:app --host $Host --port $Port --reload
}

Pop-Location
