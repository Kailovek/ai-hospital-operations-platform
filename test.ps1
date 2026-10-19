$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "Virtual environment not found. Run .\setup.ps1 first."
}

Push-Location $ProjectRoot
try {
    & $VenvPython -m ruff check .
    if ($LASTEXITCODE -ne 0) { throw "Ruff checks failed." }
    & $VenvPython -m pytest
    if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
} finally {
    Pop-Location
}
