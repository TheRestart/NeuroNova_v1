@echo off
REM NeuroNova 전체 서비스 자동 시작 스크립트
REM
REM 사용법:
REM   1. 더블클릭으로 실행
REM   2. 또는 start-all-services.bat 실행
REM
REM 시작 프로그램 등록:
REM   Win+R → shell:startup → 이 파일의 바로가기 복사

chcp 65001 >nul
echo ========================================
echo NeuroNova 전체 서비스 자동 시작
echo ========================================
echo.

REM Docker Desktop 확인
echo [1/4] Docker Desktop 상태 확인...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Desktop이 실행 중이 아닙니다.
    echo [INFO] Docker Desktop을 시작하는 중... (60초 대기)

    REM Docker Desktop 시작
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    REM Docker가 준비될 때까지 대기 (최대 60초)
    set /a count=0
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Docker Desktop 준비 완료
        goto docker_ready
    )
    set /a count+=1
    if %count% lss 12 goto wait_docker

    echo [ERROR] Docker Desktop 시작 실패 (60초 타임아웃)
    echo [INFO] 수동으로 Docker Desktop을 시작한 후 다시 실행하세요.
    pause
    exit /b 1
)
echo [OK] Docker Desktop 실행 중
:docker_ready
echo.

REM Docker Compose 서비스 시작
echo [2/4] Docker Compose 서비스 시작...
cd /d d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml up -d
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose 시작 실패
    pause
    exit /b 1
)
echo [OK] Docker 컨테이너 시작 완료
echo.

REM 서비스 준비 대기
echo [3/4] 서비스 초기화 대기 (30초)...
timeout /t 30 /nobreak >nul
echo [OK] 대기 완료
echo.

REM React 클라이언트 시작 (선택)
echo [4/4] React 클라이언트 시작 여부 선택...
echo.
echo React를 자동으로 시작하시겠습니까? (Y/N)
choice /c YN /n /m "Y: 예, N: 아니오"

if %errorlevel% equ 1 (
    echo.
    echo [INFO] React 클라이언트를 새 창에서 시작합니다...
    start "React Client" cmd /k "cd /d d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client && start-react.bat"
    echo [OK] React 시작 완료 (별도 창)
) else (
    echo.
    echo [INFO] React 클라이언트를 건너뜁니다.
    echo [INFO] 나중에 시작하려면: cd NeuroNova_03_front_end_react\00_test_client && start-react.bat
)
echo.

REM 결과 출력
echo ========================================
echo 서비스 시작 완료!
echo ========================================
echo.
echo [서비스 상태]
docker-compose -f docker-compose.dev.yml ps
echo.
echo [접속 URL]
echo   - Django API:    http://localhost/api
echo   - Swagger UI:    http://localhost/api/docs/
echo   - Grafana:       http://localhost:3000 (admin/admin123)
echo   - OpenEMR:       http://localhost:8081 (admin/pass)
echo   - Orthanc PACS:  http://localhost:8042 (orthanc/orthanc)
echo   - React Client:  http://localhost:3001
echo.
echo [로그 확인]
echo   docker-compose -f docker-compose.dev.yml logs -f
echo.
echo [종료]
echo   docker-compose -f docker-compose.dev.yml down
echo.
pause
