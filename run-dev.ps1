param(
    [int]$Port = 8006,
    [string]$Host = "127.0.0.1"
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$env:PORT = "$Port"

if (-not $env:SESSION_SECRET) {
    Write-Warning "SESSION_SECRET is not set in this shell. OAuth sessions will not survive reloads reliably until you set it."
}

if (-not $env:GOOGLE_CLIENT_ID -or -not $env:GOOGLE_CLIENT_SECRET) {
    Write-Warning "Google OAuth env vars are not set in this shell. Google login will fail until they are set."
}

Write-Host "Starting Vecron on http://$Host`:$Port with auto-reload..."
python -m uvicorn app.main:app --host $Host --port $Port --reload --reload-dir app --reload-dir frontend --reload-dir db --reload-dir recommender --reload-dir evaluation
