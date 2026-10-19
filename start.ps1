param([int]$Port = 8101)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $ProjectRoot ".hospital-api.pid"
$LogFile = Join-Path $ProjectRoot "hospital-api.log"
$ErrorLogFile = Join-Path $ProjectRoot "hospital-api-error.log"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "Virtual environment not found. Run .\setup.ps1 first."
}
if (Test-Path -LiteralPath $PidFile) {
    $ExistingPid = [int](Get-Content -LiteralPath $PidFile -Raw)
    if (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue) {
        throw "Hospital API is already running with PID $ExistingPid."
    }
    Remove-Item -LiteralPath $PidFile -Force
}

$Process = Start-Process -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $Port) `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError $ErrorLogFile `
    -WindowStyle Hidden `
    -PassThru

Set-Content -LiteralPath $PidFile -Value $Process.Id -Encoding ascii
Write-Host "Hospital API started at http://127.0.0.1:$Port (PID $($Process.Id))."
