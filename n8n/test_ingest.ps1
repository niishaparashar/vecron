param(
    [string]$ApiBaseUrl = "http://localhost:8000",
    [string]$IngestionKey = $env:N8N_INGESTION_KEY,
    [string]$PayloadPath = ".\sample_opportunities_payload.json"
)

if (-not $IngestionKey) {
    Write-Error "Missing ingestion key. Pass -IngestionKey or set N8N_INGESTION_KEY."
    exit 1
}

if (-not (Test-Path $PayloadPath)) {
    Write-Error "Payload file not found: $PayloadPath"
    exit 1
}

$headers = @{
    "X-Ingestion-Key" = $IngestionKey
    "Content-Type" = "application/json"
}

$url = "$ApiBaseUrl/admin/opportunities/ingest"
$body = Get-Content -Raw $PayloadPath

try {
    $response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body
    Write-Output "Ingestion success"
    Write-Output ("received={0} inserted={1} updated={2}" -f $response.received, $response.inserted, $response.updated)
    Write-Output ("csv_path={0}" -f $response.csv_path)
}
catch {
    Write-Error ("Ingestion failed: {0}" -f $_.Exception.Message)
    exit 1
}
