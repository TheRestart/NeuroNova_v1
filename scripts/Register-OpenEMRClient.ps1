# OpenEMR OAuth2 Client 자동 등록 스크립트 (PowerShell)
#
# 사용법:
#   .\scripts\Register-OpenEMRClient.ps1
#
# 요구사항:
#   - OpenEMR 컨테이너 실행 중
#   - Docker Desktop 실행 중

param(
    [switch]$Force = $false  # 기존 설정 강제 덮어쓰기
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenEMR OAuth2 Client 자동 등록" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 설정
$CLIENT_NAME = "NeuroNova CDSS Internal"
$CLIENT_ID = "neuronova-cdss-internal"
$GRANT_TYPES = "client_credentials"
$SCOPES = "system/Patient.read system/Patient.write system/Encounter.read system/Encounter.write system/Observation.read system/Observation.write"

# Client Secret 생성 (32자 랜덤 hex)
$bytes = New-Object byte[] 16
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$CLIENT_SECRET = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ''

Write-Host "[INFO] Client 정보:" -ForegroundColor Yellow
Write-Host "  - Client Name: $CLIENT_NAME"
Write-Host "  - Client ID: $CLIENT_ID"
Write-Host "  - Client Secret: $CLIENT_SECRET"
Write-Host ""

# Step 1: OpenEMR MySQL 컨테이너 확인
Write-Host "[1/4] OpenEMR MySQL 컨테이너 확인..." -ForegroundColor Green
$container = docker ps --filter "name=neuronova-openemr-mysql-dev" --format "{{.Names}}"
if (-not $container) {
    Write-Host "[ERROR] OpenEMR MySQL 컨테이너가 실행 중이 아닙니다." -ForegroundColor Red
    Write-Host "실행: docker-compose -f docker-compose.dev.yml up -d openemr-mysql"
    exit 1
}
Write-Host "[OK] 컨테이너 실행 중" -ForegroundColor Green
Write-Host ""

# Step 2: 기존 Client 삭제
Write-Host "[2/4] 기존 Client 삭제 (있을 경우)..." -ForegroundColor Green
$deleteQuery = "DELETE FROM oauth_clients WHERE client_id = '$CLIENT_ID';"
docker exec neuronova-openemr-mysql-dev mysql -uroot -proot openemr -e $deleteQuery 2>$null
Write-Host "[OK] 완료" -ForegroundColor Green
Write-Host ""

# Step 3: Client Secret 해시 생성
Write-Host "[3/4] OAuth2 Client 등록..." -ForegroundColor Green

# PHP password_hash() 사용
$hashCommand = "echo password_hash('$CLIENT_SECRET', PASSWORD_BCRYPT);"
$CLIENT_SECRET_HASH = docker exec neuronova-openemr-dev php -r $hashCommand

if (-not $CLIENT_SECRET_HASH) {
    Write-Host "[ERROR] Client Secret 해시 생성 실패" -ForegroundColor Red
    exit 1
}

# SQL 쿼리 작성
$insertQuery = @"
INSERT INTO oauth_clients (
    client_id,
    client_secret,
    client_name,
    grant_types,
    scope,
    user_id,
    redirect_uri,
    is_confidential,
    created_at,
    updated_at
) VALUES (
    '$CLIENT_ID',
    '$CLIENT_SECRET_HASH',
    '$CLIENT_NAME',
    '$GRANT_TYPES',
    '$SCOPES',
    NULL,
    '',
    1,
    NOW(),
    NOW()
);
"@

# SQL 실행
$queryFile = "temp_insert_client.sql"
$insertQuery | Out-File -FilePath $queryFile -Encoding ASCII

try {
    Get-Content $queryFile | docker exec -i neuronova-openemr-mysql-dev mysql -uroot -proot openemr
    Write-Host "[OK] Client 등록 완료" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Client 등록 실패: $_" -ForegroundColor Red
    Remove-Item $queryFile -ErrorAction SilentlyContinue
    exit 1
} finally {
    Remove-Item $queryFile -ErrorAction SilentlyContinue
}
Write-Host ""

# Step 4: .env 파일 업데이트
Write-Host "[4/4] Django .env 파일 업데이트..." -ForegroundColor Green

$ENV_FILE = "NeuroNova_02_back_end\02_django_server\.env"

if (-not (Test-Path $ENV_FILE)) {
    Write-Host "[WARNING] .env 파일이 없습니다. 생성합니다." -ForegroundColor Yellow
    New-Item -Path $ENV_FILE -ItemType File -Force | Out-Null
}

# 기존 OpenEMR 설정 제거
$content = Get-Content $ENV_FILE -ErrorAction SilentlyContinue
$newContent = $content | Where-Object {
    $_ -notmatch '^OPENEMR_CLIENT_ID=' -and
    $_ -notmatch '^OPENEMR_CLIENT_SECRET=' -and
    $_ -notmatch '^OPENEMR_FHIR_URL='
}

# 새 설정 추가
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$openemrConfig = @"

# OpenEMR OAuth2 설정 (자동 등록: $timestamp)
OPENEMR_FHIR_URL=http://openemr:80/apis/default/fhir
OPENEMR_CLIENT_ID=$CLIENT_ID
OPENEMR_CLIENT_SECRET=$CLIENT_SECRET
"@

$newContent += $openemrConfig
$newContent | Out-File -FilePath $ENV_FILE -Encoding UTF8

Write-Host "[OK] .env 파일 업데이트 완료" -ForegroundColor Green
Write-Host ""

# 결과 출력
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "등록 완료!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Client 정보가 .env 파일에 저장되었습니다:" -ForegroundColor Green
Write-Host "  파일: $ENV_FILE"
Write-Host ""
Write-Host "다음 명령어로 Django를 재시작하십시오:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.dev.yml restart django"
Write-Host ""
Write-Host "테스트:" -ForegroundColor Yellow
Write-Host "  python scripts\test_openemr_auth.py"
Write-Host ""
