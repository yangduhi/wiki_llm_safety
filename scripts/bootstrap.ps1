[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\\python.exe"
$PyprojectFile = Join-Path $RepoRoot "pyproject.toml"
$RequirementsFile = Join-Path $RepoRoot "requirements-dev.txt"

Write-Host "Using repository root: $RepoRoot"

try {
    & py -3.11 --version | Out-Host
}
catch {
    throw "Python 3.11 launcher entry not found. Install Python 3.11 and ensure 'py -3.11' works."
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating Python 3.11 virtual environment at $VenvPath"
    & py -3.11 -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment."
    }
}
else {
    Write-Host "Reusing existing virtual environment at $VenvPath"
}

& $VenvPython -c "import sys; assert sys.version_info[:2] == (3, 11), sys.version"
if ($LASTEXITCODE -ne 0) {
    throw "The existing .venv is not using Python 3.11. Remove .venv and rerun scripts/bootstrap.ps1."
}

Write-Host "Upgrading pip"
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed."
}

if (Test-Path $PyprojectFile) {
    Write-Host "Installing editable project with dev extras"
    & $VenvPython -m pip install -e ".[dev]"
}
elseif (Test-Path $RequirementsFile) {
    Write-Host "Installing requirements from $RequirementsFile"
    & $VenvPython -m pip install -r $RequirementsFile
}
else {
    throw "Neither pyproject.toml nor requirements-dev.txt is available."
}
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed."
}

Write-Host "Capturing raw baseline and refreshing dashboards"
& $VenvPython -m wiki_obsidian.cli source-audit --write-baseline | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "source-audit baseline capture failed."
}

& $VenvPython -m wiki_obsidian.cli dashboard-refresh | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "dashboard-refresh failed."
}

Write-Host "Bootstrap complete."
