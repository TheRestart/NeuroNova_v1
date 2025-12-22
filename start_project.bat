@echo off
REM ======================================================
REM CDSS Project Startup Script
REM 불필요한 Docker 컨테이너를 정리하고 OpenEMR만 실행
REM ======================================================

echo.
echo ========================================
echo  CDSS Project Startup
echo ========================================
echo.

REM 1. 모든 Docker 컨테이너 정리
echo [1/4] Stopping all Docker containers...
for /f "tokens=*" %%i in ('docker ps -aq 2^>nul') do (
    docker stop %%i >nul 2>&1
)
echo   - All containers stopped

echo.
echo [2/4] Removing stopped containers...
docker container prune -f >nul 2>&1
echo   - Cleanup complete

echo.
echo [3/4] Starting OpenEMR Docker...
cd openemr-docker
docker-compose up -d
cd ..

echo.
echo [4/4] Checking OpenEMR status...
timeout /t 5 /nobreak >nul
docker ps --filter "name=openemr"

echo.
echo ========================================
echo  Project Ready!
echo ========================================
echo.
echo  OpenEMR:  http://localhost:80
echo  Django:   Start manually with:
echo            cd cdss-backend
echo            venv\Scripts\python manage.py runserver
echo.
echo ========================================
echo.

REM Django 서버 자동 시작 옵션
set /p START_DJANGO="Django 서버도 자동 시작하시겠습니까? (y/n): "
if /i "%START_DJANGO%"=="y" (
    echo.
    echo Starting Django server...
    cd cdss-backend
    start cmd /k "venv\Scripts\python manage.py runserver"
    cd ..
    echo Django server started in new window!
    echo.
)

pause
