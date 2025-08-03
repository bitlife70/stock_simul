@echo off
echo === GitHub Repository Setup ===
echo.
echo 1. First, create the repository on GitHub:
echo    - Go to https://github.com/bitlife70
echo    - Click "New repository"
echo    - Name: stock_simul
echo    - Description: Korean Stock Backtesting Simulation Platform
echo    - Click "Create repository"
echo.
echo 2. Then run the following commands:
echo.
echo git remote add origin https://github.com/bitlife70/stock_simul.git
echo git branch -M main
echo git push -u origin main
echo.
echo Press any key to execute the commands after creating the repository...
pause > nul

echo.
echo === Executing Git Commands ===
git remote add origin https://github.com/bitlife70/stock_simul.git
if %errorlevel% neq 0 (
    echo Error: Failed to add remote origin
    echo Make sure the repository exists on GitHub
    pause
    exit /b 1
)

git branch -M main
if %errorlevel% neq 0 (
    echo Error: Failed to rename branch
    pause
    exit /b 1
)

git push -u origin main
if %errorlevel% neq 0 (
    echo Error: Failed to push to GitHub
    echo Check your credentials and repository permissions
    pause
    exit /b 1
)

echo.
echo === Success! ===
echo Repository has been pushed to GitHub
echo Visit: https://github.com/bitlife70/stock_simul
echo.
pause