[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "frontmatter",
        "links",
        "provenance",
        "boundaries",
        "note-ids",
        "raw-immutability",
        "design-package",
        "schema-validate",
        "dashboard-refresh",
        "source-audit",
        "lint",
        "index",
        "operations-index",
        "verify",
        "search",
        "slides",
        "clip-import"
    )]
    [string]$Command
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $RepoRoot ".venv\\Scripts\\python.exe"
$HarnessScripts = Join-Path $RepoRoot "harness\\scripts"

if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment not found at .venv. Run .\\scripts\\bootstrap.ps1 first."
}

function Invoke-HarnessScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptName
    )

    $ScriptPath = Join-Path $HarnessScripts $ScriptName
    Write-Host "Running $ScriptName"
    & $VenvPython $ScriptPath --project-root $RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "$ScriptName failed with exit code $LASTEXITCODE."
    }
}

switch ($Command) {
    "frontmatter" { Invoke-HarnessScript "check_frontmatter.py" }
    "links" { Invoke-HarnessScript "check_wikilinks.py" }
    "provenance" { Invoke-HarnessScript "check_provenance.py" }
    "boundaries" { Invoke-HarnessScript "check_layer_boundaries.py" }
    "note-ids" { Invoke-HarnessScript "check_note_ids.py" }
    "raw-immutability" { Invoke-HarnessScript "check_raw_immutability.py" }
    "design-package" { Invoke-HarnessScript "check_design_package.py" }
    "schema-validate" {
        & $VenvPython -m wiki_obsidian.cli schema-validate | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "schema-validate failed with exit code $LASTEXITCODE."
        }
    }
    "dashboard-refresh" {
        & $VenvPython -m wiki_obsidian.cli dashboard-refresh | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "dashboard-refresh failed with exit code $LASTEXITCODE."
        }
    }
    "source-audit" {
        & $VenvPython -m wiki_obsidian.cli source-audit | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "source-audit failed with exit code $LASTEXITCODE."
        }
    }
    "lint" {
        Invoke-HarnessScript "check_frontmatter.py"
        Invoke-HarnessScript "check_wikilinks.py"
        Invoke-HarnessScript "check_provenance.py"
        Invoke-HarnessScript "check_layer_boundaries.py"
        Invoke-HarnessScript "check_note_ids.py"
    }
    "index" { Invoke-HarnessScript "build_index.py" }
    "operations-index" { Invoke-HarnessScript "build_operations_index.py" }
    "verify" {
        Invoke-HarnessScript "check_frontmatter.py"
        Invoke-HarnessScript "check_wikilinks.py"
        Invoke-HarnessScript "check_provenance.py"
        Invoke-HarnessScript "check_layer_boundaries.py"
        Invoke-HarnessScript "check_note_ids.py"
        Invoke-HarnessScript "check_raw_immutability.py"
        Invoke-HarnessScript "check_design_package.py"
        & $VenvPython -m wiki_obsidian.cli schema-validate | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "schema-validate failed with exit code $LASTEXITCODE."
        }
        & $VenvPython -m wiki_obsidian.cli dashboard-refresh | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "dashboard-refresh failed with exit code $LASTEXITCODE."
        }
        Invoke-HarnessScript "build_index.py"
        Invoke-HarnessScript "build_operations_index.py"
    }
    "search" {
        $qmd = Get-Command qmd -ErrorAction SilentlyContinue
        if (-not $qmd) {
            Write-Host "qmd CLI is not installed. Install qmd and retry. See configs/tools/tooling.yaml."
            exit 0
        }
        Write-Host "qmd is installed at $($qmd.Source). Use repo-local search workflows from docs/operations/notes/obsidian-toolchain.md."
    }
    "slides" {
        $marp = Get-Command marp -ErrorAction SilentlyContinue
        if (-not $marp) {
            Write-Host "Marp CLI is not installed. Install @marp-team/marp-cli and retry. See configs/tools/tooling.yaml."
            exit 0
        }
        Write-Host "Marp is installed at $($marp.Source). Export materialized overview notes as needed."
    }
    "clip-import" {
        Write-Host "External clipper integration is repo-local only. Drop captured files into raw/collections/web_clipper/ and run source-audit or ingest."
    }
}
