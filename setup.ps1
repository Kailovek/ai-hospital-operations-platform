param([switch]$Full)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    python -m venv (Join-Path $ProjectRoot ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Pip installation failed." }
if ($Full) {
    & $VenvPython -m pip install -e ".[dev,full]"
} else {
    & $VenvPython -m pip install -e ".[dev]"
}
if ($LASTEXITCODE -ne 0) { throw "Project dependency installation failed." }

Write-Host "Environment ready. Demo mode does not download model weights."
