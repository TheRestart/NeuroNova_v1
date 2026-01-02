#!/bin/bash

# OpenEMR OAuth2 Client 자동 등록 스크립트
#
# 사용법:
#   bash scripts/register_openemr_client.sh
#
# 요구사항:
#   - OpenEMR 컨테이너 실행 중
#   - OpenEMR 데이터베이스 접근 가능

set -e

echo "========================================"
echo "OpenEMR OAuth2 Client 자동 등록"
echo "========================================"
echo ""

# 설정
CLIENT_NAME="NeuroNova CDSS Internal"
CLIENT_ID="neuronova-cdss-internal"
CLIENT_ROLE_ID=1  # Administrator role
GRANT_TYPES="client_credentials"
SCOPES="system/Patient.read system/Patient.write system/Encounter.read system/Encounter.write system/Observation.read system/Observation.write"

# Client Secret 생성 (32자 랜덤)
CLIENT_SECRET=$(openssl rand -hex 16)

echo "[INFO] Client 정보:"
echo "  - Client Name: $CLIENT_NAME"
echo "  - Client ID: $CLIENT_ID"
echo "  - Client Secret: $CLIENT_SECRET"
echo ""

# OpenEMR MySQL 컨테이너 확인
echo "[1/4] OpenEMR MySQL 컨테이너 확인..."
if ! docker ps | grep -q "neuronova-openemr-mysql-dev"; then
    echo "[ERROR] OpenEMR MySQL 컨테이너가 실행 중이 아닙니다."
    echo "실행: docker-compose -f docker-compose.dev.yml up -d openemr-mysql"
    exit 1
fi
echo "[OK] 컨테이너 실행 중"
echo ""

# 기존 Client 삭제 (있을 경우)
echo "[2/4] 기존 Client 삭제 (있을 경우)..."
docker exec neuronova-openemr-mysql-dev mysql -uroot -proot openemr -e \
    "DELETE FROM oauth_clients WHERE client_id = '$CLIENT_ID';" 2>/dev/null || true
echo "[OK] 완료"
echo ""

# 새 Client 등록
echo "[3/4] OAuth2 Client 등록..."

# Client Secret 해시 생성 (bcrypt)
# OpenEMR은 password_hash() 함수 사용 (PHP)
# Docker에서 PHP 실행하여 해시 생성
CLIENT_SECRET_HASH=$(docker exec neuronova-openemr-dev php -r \
    "echo password_hash('$CLIENT_SECRET', PASSWORD_BCRYPT);")

# SQL 실행
docker exec neuronova-openemr-mysql-dev mysql -uroot -proot openemr <<EOF
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
EOF

if [ $? -eq 0 ]; then
    echo "[OK] Client 등록 완료"
else
    echo "[ERROR] Client 등록 실패"
    exit 1
fi
echo ""

# .env 파일 업데이트
echo "[4/4] Django .env 파일 업데이트..."

ENV_FILE="NeuroNova_02_back_end/02_django_server/.env"

# 기존 OpenEMR 설정 제거
sed -i '/^OPENEMR_CLIENT_ID=/d' $ENV_FILE 2>/dev/null || true
sed -i '/^OPENEMR_CLIENT_SECRET=/d' $ENV_FILE 2>/dev/null || true
sed -i '/^OPENEMR_FHIR_URL=/d' $ENV_FILE 2>/dev/null || true

# 새 설정 추가
cat >> $ENV_FILE <<EOF

# OpenEMR OAuth2 설정 (자동 등록: $(date '+%Y-%m-%d %H:%M:%S'))
OPENEMR_FHIR_URL=http://openemr:80/apis/default/fhir
OPENEMR_CLIENT_ID=$CLIENT_ID
OPENEMR_CLIENT_SECRET=$CLIENT_SECRET
EOF

echo "[OK] .env 파일 업데이트 완료"
echo ""

# 결과 출력
echo "========================================"
echo "등록 완료!"
echo "========================================"
echo ""
echo "Client 정보가 .env 파일에 저장되었습니다:"
echo "  파일: $ENV_FILE"
echo ""
echo "Django를 재시작하십시오:"
echo "  docker-compose -f docker-compose.dev.yml restart django"
echo ""
echo "테스트:"
echo "  python scripts/test_openemr_auth.py"
echo ""
