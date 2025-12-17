<#
prepare_and_push.ps1
Interactive helper to initialize a git repo, commit changes, and push to GitHub.
Run this in PowerShell from the project folder after installing Git.
#>

function Confirm-Continue {
    param([string]$msg = "Continue?")
    $r = Read-Host "$msg (Y/n)"
    return $r -eq "" -or $r -match "^[Yy]"
}

Write-Host "== Git push helper for Analyse-Villes project ==`n" -ForegroundColor Cyan

# Try to find and add Git/GH to PATH if missing
if (-not (Get-Command git -ErrorAction SilentlyContinue) -or -not (Get-Command gh -ErrorAction SilentlyContinue)) {
    $commonPaths = @(
        "C:\Program Files\Git\cmd",
        "C:\Program Files\Git\bin",
        "C:\Program Files\GitHub CLI",
        "$env:LOCALAPPDATA\Programs\Git\cmd",
        "$env:LOCALAPPDATA\Programs\Git\bin"
    )
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Host "Found Git at $path, adding to PATH..." -ForegroundColor Cyan
            $env:Path += ";$path"
            break
        }
    }
}

# Check git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "WARNING: Git command not found in PATH." -ForegroundColor Yellow
    Write-Host "If you are sure Git is installed, you can proceed, but the script might fail if it can't find 'git.exe'." -ForegroundColor Yellow
    if (-not (Confirm-Continue "Try to proceed anyway?")) {
        Write-Host "Aborting. Please restart your terminal/PC if you just installed Git." -ForegroundColor Red
        exit 1
    }
}

# Configure user.name/email if not set
$uname = git config --global user.name
$uemail = git config --global user.email
if (-not $uname) {
    $name = Read-Host "Enter your name for git commits"
    if ($name) { git config --global user.name "$name" }
}
if (-not $uemail) {
    $email = Read-Host "Enter your email for git commits"
    if ($email) { git config --global user.email "$email" }
}

# Check GitHub CLI (gh)
$useGh = $false
if (Get-Command gh -ErrorAction SilentlyContinue) {
    if (gh auth status) {
        $useGh = $true
    }
    else {
        Write-Host "GitHub CLI is installed but not logged in." -ForegroundColor Yellow
        if (Confirm-Continue "Do you want to log in to GitHub now to create the repo automatically?") {
            gh auth login
            if ($LASTEXITCODE -eq 0) { $useGh = $true }
        }
    }
}

# Get Remote URL (Auto create or manual input)
$remoteUrl = ""
if ($useGh) {
    if (Confirm-Continue "Create new private GitHub repo 'analyse-villes' automatically?") {
        # Create repo and get URL
        try {
            gh repo create analyse-villes --private --source=. --description "Analyse Villes Streamlit App"
            $remoteUrl = gh repo view --json url --jq .url
            Write-Host "Created repository: $remoteUrl" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to create repo automatically. Falling back to manual URL." -ForegroundColor Red
        }
    }
}

if (-not $remoteUrl) {
    $remoteUrl = Read-Host "Enter your GitHub repo URL (HTTPS) e.g. https://github.com/username/repo.git"
}

if (-not $remoteUrl) {
    Write-Host "No remote URL provided. Exiting." -ForegroundColor Yellow
    exit 1
}

# Init repo if needed
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Initialized empty git repository." -ForegroundColor Green
}

# Add files (suggested defaults)
Write-Host "Staging recommended files: fetch_insee.py, cities_insee.csv, app.py, requirements.txt, README.md" -ForegroundColor Cyan
if (Confirm-Continue "Stage these files?") {
    git add fetch_insee.py cities_insee.csv app.py requirements.txt README.md
}
else {
    Write-Host "Staging all changes instead." -ForegroundColor Yellow
    git add -A
}

# Commit
$message = Read-Host "Commit message" -Default "Add INSEE data and cloud-ready updates"
git commit -m "$message"

# Setup remote
$exists = git remote
if ($exists -notmatch "origin") {
    git remote add origin $remoteUrl
    Write-Host "Added remote origin: $remoteUrl" -ForegroundColor Green
}
else {
    Write-Host "Remote named 'origin' already exists." -ForegroundColor Yellow
}

# Push
Write-Host "About to push to branch 'main' on origin. You may be prompted for credentials (use GitHub token or sign-in)." -ForegroundColor Cyan
if (-not (git rev-parse --abbrev-ref HEAD) -or (git rev-parse --abbrev-ref HEAD) -eq '') {
    git branch -M main
}

try {
    git push -u origin main
    Write-Host "Pushed successfully." -ForegroundColor Green
}
catch {
    Write-Host "Push failed. If it's due to upstream protection, run the commands manually or set the remote branch." -ForegroundColor Red
}

Write-Host "Done. If push succeeded, tell me 'c'est poussé' and I'll verify Streamlit Cloud." -ForegroundColor Cyan
