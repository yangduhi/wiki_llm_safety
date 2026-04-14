[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "git-sync-status",
        "git-sync-safe",
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

function Ensure-Venv {
    if (-not (Test-Path $VenvPython)) {
        throw "Virtual environment not found at .venv. Run .\\scripts\\bootstrap.ps1 first."
    }
}

function Invoke-HarnessScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptName
    )

    Ensure-Venv
    $ScriptPath = Join-Path $HarnessScripts $ScriptName
    Write-Host "Running $ScriptName"
    & $VenvPython $ScriptPath --project-root $RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "$ScriptName failed with exit code $LASTEXITCODE."
    }
}

function Get-BranchName {
    $branch = (& git branch --show-current 2>$null).Trim()
    if (-not $branch) {
        return $null
    }
    return $branch
}

function Get-UpstreamRef {
    $upstream = (& git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>$null).Trim()
    if (-not $upstream) {
        return $null
    }
    return $upstream
}

function Get-AheadBehind {
    param(
        [Parameter(Mandatory = $true)]
        [string]$UpstreamRef
    )

    $counts = (& git rev-list --left-right --count "HEAD...$UpstreamRef" 2>$null).Trim()
    if (-not $counts) {
        return @{
            ahead = 0
            behind = 0
        }
    }

    $parts = $counts -split "\s+"
    return @{
        ahead = [int]$parts[0]
        behind = [int]$parts[1]
    }
}

function Get-DirtyFiles {
    $statusLines = & git status --porcelain=v1 2>$null
    $files = @()
    foreach ($line in $statusLines) {
        if ($line.Length -ge 4) {
            $files += $line.Substring(3)
        }
    }
    return $files
}

function Get-SyncSnapshot {
    $branch = Get-BranchName
    $upstream = Get-UpstreamRef
    $dirtyFiles = Get-DirtyFiles
    $ahead = 0
    $behind = 0
    $status = "no-upstream"
    $canFastForward = $false

    if (-not $branch) {
        $status = "detached-head"
    }
    elseif ($upstream) {
        $counts = Get-AheadBehind -UpstreamRef $upstream
        $ahead = $counts.ahead
        $behind = $counts.behind

        if ($dirtyFiles.Count -gt 0) {
            $status = "dirty"
        }
        elseif ($ahead -gt 0 -and $behind -gt 0) {
            $status = "diverged"
        }
        elseif ($ahead -gt 0) {
            $status = "ahead"
        }
        elseif ($behind -gt 0) {
            $status = "behind"
            $canFastForward = $true
        }
        else {
            $status = "up-to-date"
        }
    }
    elseif ($dirtyFiles.Count -gt 0) {
        $status = "dirty"
    }

    return @{
        branch = $branch
        upstream = $upstream
        dirty_files = $dirtyFiles
        ahead = $ahead
        behind = $behind
        status = $status
        can_fast_forward = $canFastForward
    }
}

function Write-SyncSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Snapshot
    )

    $branchLabel = if ($Snapshot.branch) { $Snapshot.branch } else { "(detached HEAD)" }
    $upstreamLabel = if ($Snapshot.upstream) { $Snapshot.upstream } else { "(none)" }

    Write-Host "Current branch: $branchLabel"
    Write-Host "Upstream: $upstreamLabel"
    Write-Host "Working tree: $(if ($Snapshot.dirty_files.Count -eq 0) { 'clean' } else { 'dirty' })"
    Write-Host "Ahead/behind: ahead=$($Snapshot.ahead) behind=$($Snapshot.behind)"
    Write-Host "Status: $($Snapshot.status)"

    if ($Snapshot.dirty_files.Count -gt 0) {
        Write-Host "Blocking files:"
        foreach ($path in $Snapshot.dirty_files | Select-Object -First 20) {
            Write-Host "  - $path"
        }
        if ($Snapshot.dirty_files.Count -gt 20) {
            Write-Host "  - ... and $($Snapshot.dirty_files.Count - 20) more"
        }
    }
}

function Invoke-GitSyncStatus {
    $upstream = Get-UpstreamRef
    if ($upstream) {
        $remote = ($upstream -split "/")[0]
        & git fetch $remote --prune | Out-Null
    }
    else {
        & git fetch origin --prune 2>$null | Out-Null
    }

    Write-SyncSnapshot -Snapshot (Get-SyncSnapshot)
}

function Invoke-GitSyncSafe {
    $upstream = Get-UpstreamRef
    if ($upstream) {
        $remote = ($upstream -split "/")[0]
        & git fetch $remote --prune | Out-Null
    }
    else {
        & git fetch origin --prune 2>$null | Out-Null
    }

    $snapshot = Get-SyncSnapshot
    Write-SyncSnapshot -Snapshot $snapshot

    switch ($snapshot.status) {
        "up-to-date" {
            Write-Host "Git sync skipped: already up to date."
            return
        }
        "behind" {
            Write-Host "Applying fast-forward update from $($snapshot.upstream)"
            & git merge --ff-only $snapshot.upstream
            if ($LASTEXITCODE -ne 0) {
                throw "git merge --ff-only failed."
            }
            Write-Host "Git sync complete."
            return
        }
        "dirty" {
            Write-Host "Git sync skipped: working tree has local changes."
            return
        }
        "ahead" {
            Write-Host "Git sync skipped: local branch has commits that are not on upstream."
            return
        }
        "diverged" {
            Write-Host "Git sync skipped: local branch and upstream have diverged."
            return
        }
        "no-upstream" {
            Write-Host "Git sync skipped: current branch does not track an upstream branch."
            return
        }
        "detached-head" {
            Write-Host "Git sync skipped: repository is in detached HEAD state."
            return
        }
        default {
            Write-Host "Git sync skipped: unsupported status '$($snapshot.status)'."
            return
        }
    }
}

switch ($Command) {
    "git-sync-status" { Invoke-GitSyncStatus }
    "git-sync-safe" { Invoke-GitSyncSafe }
    "frontmatter" { Invoke-HarnessScript "check_frontmatter.py" }
    "links" { Invoke-HarnessScript "check_wikilinks.py" }
    "provenance" { Invoke-HarnessScript "check_provenance.py" }
    "boundaries" { Invoke-HarnessScript "check_layer_boundaries.py" }
    "note-ids" { Invoke-HarnessScript "check_note_ids.py" }
    "raw-immutability" { Invoke-HarnessScript "check_raw_immutability.py" }
    "design-package" { Invoke-HarnessScript "check_design_package.py" }
    "schema-validate" {
        Ensure-Venv
        & $VenvPython -m wiki_obsidian.cli schema-validate | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "schema-validate failed with exit code $LASTEXITCODE."
        }
    }
    "dashboard-refresh" {
        Ensure-Venv
        & $VenvPython -m wiki_obsidian.cli dashboard-refresh | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "dashboard-refresh failed with exit code $LASTEXITCODE."
        }
    }
    "source-audit" {
        Ensure-Venv
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
