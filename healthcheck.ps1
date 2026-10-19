param([int]$Port = 8101)

$ErrorActionPreference = "Stop"
$Response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/v1/health" -TimeoutSec 5
$Response | ConvertTo-Json -Depth 5
if ($Response.status -ne "healthy") {
    throw "Hospital API reported status '$($Response.status)'."
}
