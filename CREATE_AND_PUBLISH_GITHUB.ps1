# Team 404 GitHub create + publish (Windows PowerShell 5.1+).
# Requires your own interactive GitHub authentication via the GitHub CLI.
# Will not force push, overwrite an occupied repository or send credentials to ChatGPT.
$ErrorActionPreference = 'Stop'
$repo = 'Tidaschandoopasilva/NASASPACEAPPS_404_PATH_NOT_FOUND'
$repoUrl = "https://github.com/$repo.git"
Set-Location -LiteralPath $PSScriptRoot

function Assert-OK([string]$step) {
    if ($LASTEXITCODE -ne 0) { throw "$step failed (exit code $LASTEXITCODE)." }
}
function Find-Gh {
    $cmd = Get-Command gh -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($path in @(
        "$env:ProgramFiles\GitHub CLI\gh.exe",
        "${env:ProgramFiles(x86)}\GitHub CLI\gh.exe",
        "$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe"
    )) { if ($path -and (Test-Path $path)) { return $path } }
    return $null
}

try {
    Write-Host '=========================================================='
    Write-Host 'TEAM 404 - CREATE GITHUB REPOSITORY AND PUBLISH CODEBASE'
    Write-Host '=========================================================='
    Write-Host "Repository: https://github.com/$repo"
    Write-Host ''
    if (-not (Test-Path -LiteralPath 'README.md')) {
        throw 'README.md not found. Extract the whole GitHub-ready ZIP first, then run the launcher inside the extracted folder.'
    }
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { throw 'Git for Windows is missing. Install Git from https://git-scm.com/download/win and run this launcher again.' }

    $gh = Find-Gh
    if (-not $gh) {
        $winget = Get-Command winget -ErrorAction SilentlyContinue
        if (-not $winget) { throw 'GitHub CLI is missing and winget is unavailable. Install from https://cli.github.com/ and rerun.' }
        Write-Host 'Installing GitHub CLI with Windows Package Manager...'
        & $winget.Source install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
        Assert-OK 'GitHub CLI installation'
        $gh = Find-Gh
        if (-not $gh) { throw 'GitHub CLI installation finished, but gh.exe was not located. Reopen the extracted folder and rerun the launcher.' }
    }

    Write-Host 'Checking GitHub authentication...'
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $gh auth status 2>$null | Out-Null; $signedIn = ($LASTEXITCODE -eq 0) }
    finally { $ErrorActionPreference = $oldPreference }
    if (-not $signedIn) {
        Write-Host 'Sign in to your GitHub account in the browser window that opens.'
        & $gh auth login --hostname github.com --git-protocol https --web
        Assert-OK 'GitHub login'
    }
    & $gh auth setup-git
    Assert-OK 'Git credential setup'

    $login = (& $gh api user --jq .login | Select-Object -First 1).Trim()
    Assert-OK 'Get authenticated account'
    if ($login -ne 'Tidaschandoopasilva') {
        throw "You signed in as '$login', but this package targets Tidaschandoopasilva. No repository was created."
    }
    $id = (& $gh api user --jq .id | Select-Object -First 1).Trim()
    Assert-OK 'Get GitHub account ID'

    if (-not (Test-Path -LiteralPath '.git')) {
        & $git.Source init -b main
        Assert-OK 'Git initialization'
    }
    & $git.Source branch -M main
    Assert-OK 'Set main branch'
    $gitName = & $git.Source config user.name
    if (-not $gitName) { & $git.Source config user.name $login; Assert-OK 'Set Git author name' }
    $gitMail = & $git.Source config user.email
    if (-not $gitMail) {
        & $git.Source config user.email "${id}+${login}@users.noreply.github.com"
        Assert-OK 'Set private Git commit email'
    }

    Write-Host 'Preparing complete project files, including the compiled website...'
    & $git.Source add --all
    Assert-OK 'Stage files'
    if (Test-Path 'apps/web/dist') {
        & $git.Source add --force -- apps/web/dist
        Assert-OK 'Stage built website'
    }
    & $git.Source diff --cached --quiet
    if ($LASTEXITCODE -eq 1) {
        & $git.Source commit -m 'Publish Team 404 Mars Habitat V7 with updated screenshots and installation guides'
        Assert-OK 'Commit project'
    } elseif ($LASTEXITCODE -ne 0) { throw 'Could not inspect staged changes.' }

    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $origin = & $git.Source remote get-url origin 2>$null; $hasOrigin = ($LASTEXITCODE -eq 0) }
    finally { $ErrorActionPreference = $oldPreference }
    if ($hasOrigin) {
        if ($origin.Trim() -ne $repoUrl) { throw "Existing origin '$origin' does not match expected repository '$repoUrl'. No changes pushed." }
    } else {
        & $git.Source remote add origin $repoUrl
        Assert-OK 'Configure GitHub remote'
    }

    Write-Host 'Checking whether target repository exists...'
    $repoExists = $true
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $gh repo view $repo --json name 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { $repoExists = $false }
    } catch { $repoExists = $false }
    finally { $ErrorActionPreference = $oldPreference }
    if (-not $repoExists) {
        Write-Host 'Creating PUBLIC GitHub repository...'
        & $gh repo create $repo --public --description 'NASA Space Apps Challenge - Team 404 Marswalk Planner for Jezero Crater'
        Assert-OK 'Create GitHub repository'
    } else { Write-Host 'Repository already exists; checking whether an initial push is safe...' }

    # An empty repository has no remote refs. An occupied repository needs a normal
    # fast-forward relationship; never force push to bypass history protections.
    Write-Host 'Uploading full codebase to main (no force push)...'
    & $git.Source push --set-upstream origin main
    Assert-OK 'Push to GitHub'
    Write-Host ''
    Write-Host 'SUCCESS. Project published at:' -ForegroundColor Green
    Write-Host "https://github.com/$repo" -ForegroundColor Green
} catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'No forced deletion or overwrite was attempted.'
} finally {
    Write-Host ''
    Read-Host 'Press Enter to close this window'
}
