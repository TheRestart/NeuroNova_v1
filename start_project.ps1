# ======================================================
# CDSS Project Startup Script (PowerShell)
# 불필요한 Docker 컨테이너를 정리하고 OpenEMR만 실행
# ======================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CDSS Project Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 모든 Docker 컨테이너 정리
Write-Host "[1/4] Stopping all Docker containers..." -ForegroundColor Yellow
$containers = docker ps -aq
if ($containers) {
    docker stop $containers | Out-Null
    Write-Host "  - All containers stopped" -ForegroundColor Green
} else {
    Write-Host "  - No containers running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/4] Removing stopped containers..." -ForegroundColor Yellow
docker container prune -f | Out-Null
Write-Host "  - Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Starting OpenEMR Docker..." -ForegroundColor Yellow
Set-Location openemr-docker
docker-compose up -d
Set-Location ..

Write-Host ""
Write-Host "[4/4] Checking OpenEMR status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
docker ps --filter "name=openemr"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Project Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " OpenEMR:  http://localhost:80" -ForegroundColor White
Write-Host " Django:   Start manually with:" -ForegroundColor White
Write-Host "           cd cdss-backend" -ForegroundColor Gray
Write-Host "           venv\Scripts\python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Django 서버 자동 시작 옵션
$startDjango = Read-Host "Django 서버도 자동 시작하시겠습니까? (y/n)"
if ($startDjango -eq "y" -or $startDjango -eq "Y") {
    Write-Host ""
    Write-Host "Starting Django server..." -ForegroundColor Yellow
    Set-Location cdss-backend
    Start-Process cmd -ArgumentList "/k", "venv\Scripts\python manage.py runserver"
    Set-Location ..
    Write-Host "Django server started in new window!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
