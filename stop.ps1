$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".hospital-api.pid"

if (-not (Test-Path -LiteralPath $PidFile)) {
    Write-Host "Hospital API is not running (PID file not found)."
    exit 0
}

$ServerPid = [int](Get-Content -LiteralPath $PidFile -Raw)
$Process = Get-Process -Id $ServerPid -ErrorAction SilentlyContinue
if ($null -ne $Process) {
    Stop-Process -Id $ServerPid
    $null = $Process.WaitForExit(10000)
}
Remove-Item -LiteralPath $PidFile -Force
Write-Host "Hospital API stopped."
