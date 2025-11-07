# Bug-Be-Gone Setup Script for Windows (PowerShell)
# Run this after extracting Bug-Be-Gone-export.tar.gz

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Bug-Be-Gone - Windows Push Setup (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-Not (Test-Path "README.md")) {
    Write-Host "ERROR: README.md not found!" -ForegroundColor Red
    Write-Host "Please run this script from inside the Bug-Be-Gone directory." -ForegroundColor Red
    pause
    exit 1
}

# Check if git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git for Windows: https://git-scm.com/download/win" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[1/6] Disabling GPG signing..." -ForegroundColor Green
git config commit.gpgsign false

Write-Host "[2/6] Initializing git repository..." -ForegroundColor Green
git init

Write-Host "[3/6] Adding all files..." -ForegroundColor Green
git add .

Write-Host "[4/6] Creating initial commit..." -ForegroundColor Green
git commit -m "Initial release: Bug-Be-Gone v1.0 - 31+ error types, 3 modes, self-improving"

Write-Host "[5/6] Adding GitHub remote..." -ForegroundColor Green
git remote add origin https://github.com/Ninja1232123/Bug-Be-Gone.git

Write-Host "[6/6] Renaming branch to main..." -ForegroundColor Green
git branch -M main

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "READY TO PUSH!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Push to GitHub"
Write-Host ""
Write-Host "Run this command:"
Write-Host "    git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "You'll be prompted for:"
Write-Host "    Username: Ninja1232123"
Write-Host "    Password: [Your GitHub Personal Access Token]"
Write-Host ""
Write-Host "Get token: https://github.com/settings/tokens"
Write-Host "    Scopes needed: repo"
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
pause
