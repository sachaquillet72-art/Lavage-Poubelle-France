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

# Check git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "Git is not installed or not on PATH. Please install Git (https://git-scm.com/download/win) and restart PowerShell." -ForegroundColor Red
    exit 1
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

# Ask remote URL
$remoteUrl = Read-Host "Enter your GitHub repo URL (HTTPS) e.g. https://github.com/username/repo.git"
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
} else {
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
} else {
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
} catch {
    Write-Host "Push failed. If it's due to upstream protection, run the commands manually or set the remote branch." -ForegroundColor Red
}

Write-Host "Done. If push succeeded, tell me 'c'est poussé' and I'll verify Streamlit Cloud." -ForegroundColor Cyan
