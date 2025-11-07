@echo off
REM Bug-Be-Gone Setup Script for Windows
REM Run this after extracting Bug-Be-Gone-export.tar.gz

echo ========================================================================
echo Bug-Be-Gone - Windows Push Setup
echo ========================================================================
echo.

REM Check if we're in the right directory
if not exist "README.md" (
    echo ERROR: README.md not found!
    echo Please run this script from inside the Bug-Be-Gone directory.
    pause
    exit /b 1
)

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git for Windows: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] Disabling GPG signing...
git config commit.gpgsign false

echo [2/6] Initializing git repository...
git init

echo [3/6] Adding all files...
git add .

echo [4/6] Creating initial commit...
git commit -m "Initial release: Bug-Be-Gone v1.0 - 31+ error types, 3 modes, self-improving"

echo [5/6] Adding GitHub remote...
git remote add origin https://github.com/Ninja1232123/Bug-Be-Gone.git

echo [6/6] Renaming branch to main...
git branch -M main

echo.
echo ========================================================================
echo READY TO PUSH!
echo ========================================================================
echo.
echo Next step: Push to GitHub
echo.
echo Run this command:
echo     git push -u origin main
echo.
echo You'll be prompted for:
echo     Username: Ninja1232123
echo     Password: [Your GitHub Personal Access Token]
echo.
echo Get token: https://github.com/settings/tokens
echo     Scopes needed: repo
echo.
echo ========================================================================
pause
