# 배포 전 테스트 계획 (Pre-Deployment Test Plan)

**작성일**: 2025-12-31
**목표**: 2일 후 임시 배포 (GCP VM)
**범위**: Django + MySQL + Orthanc + Redis (FastAPI, React 제외)
**작업자**: Claude AI (단독)

---

## 📋 테스트 개요

### 배포 범위
- ✅ Django 백엔드 (UC01-UC09)
- ✅ MySQL 데이터베이스 (CDSS + OpenEMR)
- ✅ Orthanc PACS
- ✅ Redis (Celery Backend)
- ✅ Celery Workers (비동기 작업)
- ❌ FastAPI AI 서버 (타 팀원 담당 - 제외)
- ❌ React 프론트엔드 (타 팀원 담당 - 제외)

### 테스트 전략
1. **서버 상태 점검** (Phase 1)
2. **비어있는 파일 검색** (Phase 2)
3. **핵심 API 테스트** (Phase 3)
4. **데이터베이스 무결성 확인** (Phase 4)
5. **배포 전 체크리스트 완료** (Phase 5)

---

## 📅 Phase 1: 서버 상태 점검 (30분)

### 1.1 Docker 컨테이너 상태

**목표**: 모든 필수 컨테이너가 healthy 상태인지 확인

**체크리스트**:
- [x] Django (neuronova-django-dev) - ✅ healthy
- [x] MySQL CDSS (neuronova-cdss-mysql-dev) - ✅ healthy
- [x] MySQL OpenEMR (neuronova-openemr-mysql-dev) - ✅ healthy
- [x] Orthanc PACS (neuronova-orthanc-dev) - ✅ healthy
- [x] Redis (neuronova-redis-dev) - ✅ healthy
- [x] Celery Worker (neuronova-celery-worker-dev) - ✅ running
- [x] Celery Beat (neuronova-celery-beat-dev) - ✅ running
- [x] Flower (neuronova-celery-flower-dev) - ✅ running
- [ ] Nginx (neuronova-nginx-dev) - ⚠️ unhealthy (조사 필요)
- [ ] HAPI FHIR (neuronova-hapi-fhir-dev) - ⚠️ unhealthy (실행은 정상)
- [x] Prometheus (neuronova-prometheus-dev) - ✅ healthy
- [x] Grafana (neuronova-grafana-dev) - ✅ healthy
- [x] Alertmanager (neuronova-alertmanager-dev) - ✅ healthy
- [ ] OpenEMR (neuronova-openemr-dev) - ✅ healthy

**명령어**:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
docker ps --filter "health=unhealthy"
```

---

### 1.2 포트 점유 확인

**목표**: 필수 포트가 올바르게 열려있는지 확인

| 서비스 | 포트 | 용도 | 상태 |
|--------|------|------|------|
| Nginx | 80 | 웹 서버 | [ ] |
| Grafana | 3000 | 모니터링 | [x] |
| Django | 8000 | API 서버 | [x] |
| OpenEMR | 8081 | EMR 웹 | [x] |
| Orthanc | 8042 | PACS 웹 | [x] |
| HAPI FHIR | 8080 | FHIR 서버 | [x] |
| Prometheus | 9090 | 메트릭 수집 | [x] |
| Alertmanager | 9093 | 알림 관리 | [x] |
| MySQL CDSS | 3306 | CDSS DB | [x] |
| MySQL OpenEMR | 3307 | OpenEMR DB | [x] |
| Orthanc DICOM | 4242 | DICOM 전송 | [x] |
| Flower | 5555 | Celery 모니터링 | [x] |
| Redis | 6379 | 캐시/Queue | [x] |

**명령어**:
```bash
netstat -tulpn | grep LISTEN | grep -E "80|3000|8000|8042|8080|9090|3306|6379"
```

---

### 1.3 서비스 응답 테스트

**목표**: 각 서비스가 HTTP 요청에 정상 응답하는지 확인

```bash
# Django API
curl -I http://localhost:8000/admin/

# Orthanc PACS
curl -I http://localhost:8042/app/explorer.html

# Grafana
curl -I http://localhost:3000/login

# Prometheus
curl -I http://localhost:9090/graph

# HAPI FHIR
curl -I http://localhost:8080/fhir/metadata
```

**예상 응답**: HTTP 200 또는 302 (Redirect)

---

## 📂 Phase 2: 비어있는 파일 검색 (1시간)

### 2.1 Django 앱 파일 검색

**목표**: 비어있는 Python 파일 찾기 (0 bytes 또는 주석만 있는 파일)

**검색 경로**:
```bash
# 빈 파일 (0 bytes)
find NeuroNova_02_back_end/02_django_server -name "*.py" -size 0

# 10줄 미만 파일 (TODO만 있거나 거의 비어있음)
find NeuroNova_02_back_end/02_django_server -name "*.py" -exec sh -c 'wc -l "$1" | awk "{if (\$1 < 10) print \$1, \$2}"' _ {} \;

# __init__.py 제외
find NeuroNova_02_back_end/02_django_server -name "*.py" ! -name "__init__.py" -size -100c
```

**확인 대상**:
- [ ] acct/ (인증/권한)
- [ ] emr/ (환자 관리)
- [ ] ocs/ (처방)
- [ ] lis/ (검사실)
- [ ] ris/ (영상의학)
- [ ] ai/ (AI 작업)
- [ ] fhir/ (FHIR 연동)
- [ ] audit/ (감사 로그)

---

### 2.2 설정 파일 검증

**목표**: 필수 설정 파일이 비어있지 않은지 확인

**체크리스트**:
- [ ] `.env` (Django 환경변수)
- [ ] `.env.docker` (Docker 환경변수)
- [ ] `docker-compose.dev.yml`
- [ ] `requirements.txt`
- [ ] `settings.py`
- [ ] `urls.py` (각 앱)

**명령어**:
```bash
# 설정 파일 크기 확인
ls -lh NeuroNova_02_back_end/02_django_server/.env
ls -lh NeuroNova_02_back_end/02_django_server/requirements.txt
```

---

### 2.3 마스터 데이터 확인

**목표**: 진단/약물/검사 마스터 데이터가 DB에 있는지 확인

```bash
# Django shell로 확인
docker exec neuronova-django-dev python manage.py shell -c "
from ocs.models import Diagnosis, Medication
from lis.models import LabTestMaster

print('Diagnosis:', Diagnosis.objects.count())
print('Medication:', Medication.objects.count())
print('LabTestMaster:', LabTestMaster.objects.count())
"
```

**예상 결과**:
- Diagnosis: 100개 이상
- Medication: 30개 이상
- LabTestMaster: 50개 이상

---

## 🧪 Phase 3: 핵심 API 테스트 (2시간)

### 3.1 인증 API (UC01)

**테스트 시나리오**:
```bash
# 1. 로그인 (JWT 토큰 발급)
curl -X POST http://localhost:8000/api/acct/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "doctor", "password": "doctor123"}'

# 예상 응답: {"access": "...", "refresh": "..."}

# 2. 토큰 갱신
curl -X POST http://localhost:8000/api/acct/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "REFRESH_TOKEN_HERE"}'

# 3. 사용자 프로필 조회
curl -X GET http://localhost:8000/api/acct/me/ \
  -H "Authorization: Bearer ACCESS_TOKEN_HERE"
```

**체크리스트**:
- [ ] 로그인 성공 (200 OK)
- [ ] 토큰 발급 확인
- [ ] 잘못된 비밀번호 거부 (401 Unauthorized)
- [ ] 토큰으로 인증된 API 호출 성공

---

### 3.2 환자 관리 API (UC02)

**테스트 시나리오**:
```bash
# 1. 환자 목록 조회
curl -X GET http://localhost:8000/api/emr/patients/ \
  -H "Authorization: Bearer TOKEN"

# 2. 환자 생성
curl -X POST http://localhost:8000/api/emr/patients/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST001",
    "name": "테스트환자",
    "date_of_birth": "1990-01-01",
    "gender": "M"
  }'

# 3. 환자 상세 조회
curl -X GET http://localhost:8000/api/emr/patients/TEST001/ \
  -H "Authorization: Bearer TOKEN"
```

**체크리스트**:
- [ ] 환자 목록 조회 성공
- [ ] 환자 생성 성공 (201 Created)
- [ ] 생성된 환자 조회 성공
- [ ] 중복 환자 ID 거부 (400 Bad Request)

---

### 3.3 처방 API (UC03)

**테스트 시나리오**:
```bash
# 1. 처방 생성
curl -X POST http://localhost:8000/api/ocs/prescriptions/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST001",
    "medication_code": "M001",
    "dosage": "1일 3회, 1회 1정",
    "days": 7
  }'

# 2. 처방 목록 조회
curl -X GET http://localhost:8000/api/ocs/prescriptions/?patient_id=TEST001 \
  -H "Authorization: Bearer TOKEN"
```

**체크리스트**:
- [ ] 처방 생성 성공
- [ ] 처방 목록 조회 성공
- [ ] 약물 마스터 데이터 연동 확인

---

### 3.4 Orthanc PACS API (UC05)

**테스트 시나리오**:
```bash
# 1. Orthanc 시스템 정보
curl http://localhost:8042/system

# 2. 환자 목록
curl http://localhost:8042/patients

# 3. DICOM 업로드 (샘플 파일 있을 경우)
# curl -X POST http://localhost:8042/instances \
#   --data-binary @sample.dcm \
#   -H "Content-Type: application/dicom"
```

**체크리스트**:
- [ ] Orthanc 시스템 정보 조회 성공
- [ ] 환자 목록 조회 (비어있어도 OK)
- [ ] DICOM 업로드 기능 확인 (선택)

---

## 🗄️ Phase 4: 데이터베이스 무결성 확인 (1시간)

### 4.1 CDSS 데이터베이스

**테스트 쿼리**:
```bash
docker exec neuronova-cdss-mysql-dev mysql -u cdss_user -pcdss_password cdss_db -e "
SELECT
  (SELECT COUNT(*) FROM acct_user) AS users,
  (SELECT COUNT(*) FROM emr_patient) AS patients,
  (SELECT COUNT(*) FROM ocs_prescription) AS prescriptions,
  (SELECT COUNT(*) FROM lis_laborder) AS lab_orders,
  (SELECT COUNT(*) FROM ris_radiologyorder) AS ris_orders;
"
```

**예상 결과**:
- users: 13명 이상 (테스트 계정)
- patients: 5명 이상 (샘플 데이터)
- prescriptions: 0개 이상
- lab_orders: 0개 이상
- ris_orders: 0개 이상

**체크리스트**:
- [ ] 테이블 존재 확인
- [ ] 테스트 사용자 데이터 확인
- [ ] 외래 키 제약조건 정상

---

### 4.2 마이그레이션 상태

**명령어**:
```bash
docker exec neuronova-django-dev python manage.py showmigrations
```

**체크리스트**:
- [ ] 모든 마이그레이션 [X] 적용됨
- [ ] 미적용 마이그레이션 없음

---

## ✅ Phase 5: 배포 전 체크리스트 (30분)

### 5.1 보안 설정

**프로덕션 체크리스트**:
- [ ] `DEBUG=False` (.env 파일)
- [ ] `ENABLE_SECURITY=True` (.env 파일)
- [ ] `SECRET_KEY` 환경변수 설정
- [ ] `ALLOWED_HOSTS` 설정 (34.71.151.117, 도메인)
- [ ] CORS 설정 (화이트리스트)
- [ ] 테스트 계정 비밀번호 변경 또는 비활성화
- [ ] JWT 토큰 만료 시간 단축 (1h, 7d)

**참조**: [13_배포전_보안_체크리스트.md](../13_배포전_보안_체크리스트.md)

---

### 5.2 Docker 이미지 최적화

**체크리스트**:
- [ ] Django 이미지 빌드 성공
- [ ] 불필요한 패키지 제거
- [ ] `.dockerignore` 설정
- [ ] 이미지 크기 확인 (< 1GB 권장)

**명령어**:
```bash
docker images | grep neuronova
```

---

### 5.3 로그 설정

**체크리스트**:
- [ ] Django 로그 레벨 설정 (INFO)
- [ ] 민감 정보 마스킹 확인
- [ ] 로그 파일 위치 확인
- [ ] 로그 로테이션 설정

---

### 5.4 백업 전략

**체크리스트**:
- [ ] 데이터베이스 백업 스크립트 작성
- [ ] 백업 테스트 (복원 가능 여부)
- [ ] 백업 보관 위치 설정 (GCP Storage)

**명령어**:
```bash
# 백업 생성
docker exec neuronova-cdss-mysql-dev mysqldump -u root -pcdss_root_password cdss_db > backup_$(date +%Y%m%d).sql

# 백업 테스트 (별도 DB에 복원)
# docker exec -i neuronova-cdss-mysql-dev mysql -u root -p test_db < backup_20251231.sql
```

---

## 🚨 알려진 이슈 및 해결 방안

### Issue 1: Nginx unhealthy
**상태**: 조사 중
**영향**: 낮음 (Django는 8000 포트로 직접 접근 가능)
**해결 방안**: Nginx 로그 확인 후 수정

### Issue 2: HAPI FHIR unhealthy
**상태**: 실행은 정상, health check 실패
**영향**: 낮음 (FHIR API는 정상 동작)
**해결 방안**: Health check 엔드포인트 확인

### Issue 3: React 프론트엔드 없음
**상태**: 타 팀원 담당
**영향**: 높음 (사용자 UI 없음)
**임시 해결**: Django Admin, Swagger UI, Postman 사용

### Issue 4: FastAPI AI 서버 없음
**상태**: 타 팀원 담당
**영향**: 중간 (UC06 AI 기능 미작동)
**임시 해결**: AI 기능 제외 배포

---

## 📊 테스트 결과 요약

### 성공 기준
- [ ] 모든 필수 컨테이너 healthy
- [ ] 핵심 API 10개 이상 테스트 성공
- [ ] 데이터베이스 무결성 확인
- [ ] 보안 체크리스트 80% 이상 완료
- [ ] 알려진 이슈 문서화 완료

### 실패 시 조치
1. 로그 수집 및 분석
2. 트러블슈팅 문서 작성
3. 배포 일정 재조정 협의

---

## 📝 다음 단계

### 배포 당일 (D-Day)
1. GCP VM 접속 확인
2. Docker Compose 배포
3. 데이터베이스 마이그레이션
4. 샘플 데이터 시딩
5. Smoke Test (기본 기능 확인)
6. 모니터링 설정 (Prometheus + Grafana)

### 배포 후 (D+1)
1. 로그 모니터링 (24시간)
2. 성능 측정 (응답 시간, TPS)
3. 버그 리포트 수집
4. 핫픽스 준비

---

**작성**: Claude AI
**최종 업데이트**: 2025-12-31
**예상 소요 시간**: 5-6시간 (Phase 1-5)
**다음 문서**: [배포 전 체크리스트 실행 결과](PRE_DEPLOYMENT_TEST_RESULTS.md)
