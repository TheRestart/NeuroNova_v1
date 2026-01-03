@echo off
REM ============================================================================
REM NeuroNova CDSS - Deployment Cleanup Script
REM ============================================================================
REM Purpose: Remove unnecessary files before GCP deployment
REM Author: NeuroNova Development Team
REM Date: 2026-01-03
REM ============================================================================

echo ========================================
echo NeuroNova CDSS - Deployment Cleanup
echo ========================================
echo.

REM Navigate to project root
cd /d "%~dp0"

echo [1/9] Removing Python cache files (__pycache__, *.pyc)...
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        echo Deleting: %%i
        rmdir /s /q "%%i" 2>nul
    )
)
del /s /q *.pyc 2>nul
echo ✓ Python cache cleaned
echo.

echo [2/9] Removing test coverage files (.coverage)...
if exist ".coverage" (
    del /q .coverage
    echo ✓ .coverage deleted
) else (
    echo - .coverage not found
)
if exist "NeuroNova_02_back_end\02_django_server\.coverage" (
    del /q "NeuroNova_02_back_end\02_django_server\.coverage"
    echo ✓ Backend .coverage deleted
)
echo.

echo [3/9] Removing log files (*.log)...
del /s /q logs\*.log 2>nul
del /s /q NeuroNova_02_back_end\02_django_server\logs\*.log 2>nul
echo ✓ Log files cleaned
echo.

echo [4/9] Removing development environment files (.env.local)...
if exist "NeuroNova_03_front_end_react\00_test_client\.env.local" (
    del /q "NeuroNova_03_front_end_react\00_test_client\.env.local"
    echo ✓ .env.local deleted (SECURITY RISK REMOVED)
) else (
    echo - .env.local not found
)
echo.

echo [5/9] Removing macOS system files (.DS_Store)...
del /s /q .DS_Store 2>nul
echo ✓ .DS_Store files cleaned
echo.

echo [6/9] Removing Python virtual environment (venv/)...
if exist "venv" (
    echo Deleting venv directory (183MB)...
    rmdir /s /q venv
    echo ✓ venv deleted (reinstall from requirements.txt on deployment)
) else (
    echo - venv directory not found
)
echo.

echo [7/9] Removing deprecated documentation files (OLD_*.md)...
if exist "OLD_프롬.md" (
    del /q "OLD_프롬.md"
    echo ✓ OLD_프롬.md deleted
)
if exist "OLD_작업이력.md" (
    del /q "OLD_작업이력.md"
    echo ✓ OLD_작업이력.md deleted
)
if exist "OLD_업무계획서.md" (
    del /q "OLD_업무계획서.md"
    echo ✓ OLD_업무계획서.md deleted
)
if exist "OLD_README.md" (
    del /q "OLD_README.md"
    echo ✓ OLD_README.md deleted
)
echo.

echo [8/9] Removing old Docker Compose files...
if exist "90_작업이력\docker-compose.OLD.yml" (
    del /q "90_작업이력\docker-compose.OLD.yml"
    echo ✓ docker-compose.OLD.yml deleted
)
if exist "90_작업이력\docker-compose.OLD2.yml" (
    del /q "90_작업이력\docker-compose.OLD2.yml"
    echo ✓ docker-compose.OLD2.yml deleted
)
echo.

echo [9/9] Removing Git cache files (.git/index.lock)...
if exist ".git\index.lock" (
    del /q ".git\index.lock"
    echo ✓ Git lock file removed
) else (
    echo - No Git lock files found
)
echo.

echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Summary of removed files:
echo - Python cache (__pycache__, *.pyc)
echo - Test coverage (.coverage)
echo - Log files (*.log)
echo - Development environment (.env.local)
echo - macOS system files (.DS_Store)
echo - Virtual environment (venv/)
echo - Deprecated docs (OLD_*.md)
echo - Old Docker files (docker-compose.OLD*.yml)
echo.
echo Estimated space saved: ~200MB+
echo.
echo ========================================
echo IMPORTANT: node_modules NOT deleted
echo ========================================
echo To delete node_modules (1.2GB) for deployment:
echo   cd NeuroNova_03_front_end_react\00_test_client
echo   rmdir /s /q node_modules
echo.
echo Reinstall on deployment:
echo   npm install --legacy-peer-deps
echo ========================================
echo.
echo Press any key to exit...
pause >nul
