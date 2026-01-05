# 배포용 OpenEMR 연동 가이드

**작성일**: 2026-01-05
**대상**: GCP VM 배포 환경
**문제**: 배포 시 OpenEMR 접속 에러 발생

---

## 📋 핵심 요약

### ✅ 해결책
**OpenEMR OAuth2 설정은 필요 없습니다!**

NeuroNova는 **Direct DB Access 방식**을 사용하므로 OAuth2 없이 OpenEMR과 연동할 수 있습니다.

### 🔑 설정 방법
`.env` 파일에 다음 한 줄만 추가:
```bash
SKIP_OPENEMR_INTEGRATION=True
```

---

## 1. OpenEMR 연동 방식 이해

NeuroNova는 **2가지 OpenEMR 연동 방식**을 지원합니다:

### 방식 비교표

| 항목 | Direct DB Access ⭐ | FHIR API Access |
|------|---------------------|-----------------|
| **방식** | OpenEMR MySQL DB 직접 접근 | OpenEMR FHIR API HTTP 호출 |
| **OAuth2** | ❌ **불필요** | ✅ 필수 |
| **구현** | `OpenEMRPatientRepository` | `OpenEMRClient` |
| **코드 위치** | `emr/repositories.py` | `emr/services/openemr_client.py` |
| **장점** | 빠름, 안정적, 설정 간단 | 표준 준수, 확장성 |
| **단점** | 스키마 의존 | 느림, OAuth2 복잡 |
| **사용 시기** | **권장 (프로덕션)** | 표준 준수 필요 시 |

### 현재 프로젝트 구조

```python
# 방식 1: Direct DB Access (현재 사용 중)
from emr.repositories import OpenEMRPatientRepository

# OpenEMR MySQL DB에 직접 INSERT
OpenEMRPatientRepository.create_patient_in_openemr({
    'patient_id': 'P-2026-000001',
    'given_name': 'John',
    'family_name': 'Doe',
    # ...
})
```

```python
# 방식 2: FHIR API Access (구현되어 있지만 선택사항)
from emr.services.openemr_client import OpenEMRClient

# FHIR API 호출 (OAuth2 필요)
client = OpenEMRClient()
token = client.get_access_token()  # ← OAuth2 인증
patients = client.get_patients()
```

---

## 2. 배포 시 설정 (3단계)

### Step 1: `.env.docker` 파일 확인

**파일 위치**: `NeuroNova_02_back_end/02_django_server/.env.docker`

```bash
# ============================================
# OpenEMR 연동 설정
# ============================================
# Skip 모드: OpenEMR FHIR API 호출 비활성화
# - True: Django가 OpenEMR MySQL DB에 직접 접근 (OAuth2 불필요)
# - False: FHIR API 호출 (OAuth2 필수)
SKIP_OPENEMR_INTEGRATION=True  # ← 이 줄이 있는지 확인!

# OpenEMR MySQL 접속 정보 (Direct DB Access 방식)
OPENEMR_DB_HOST=openemr-mysql
OPENEMR_DB_PORT=3306
OPENEMR_DB_NAME=openemr
OPENEMR_DB_USER=openemr
OPENEMR_DB_PASSWORD=openemr
```

### Step 2: VM에 전송 시 `.env.docker` → `.env`로 이름 변경

**GCP VM에서 실행**:

```bash
cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server

# .env.docker를 .env로 복사 (또는 이름 변경)
cp .env.docker .env

# 또는 nano로 직접 생성
nano .env
# (위 내용 붙여넣기)
```

### Step 3: Docker Compose 실행

```bash
cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server

# 컨테이너 시작
docker compose up -d --build

# 로그 확인
docker compose logs -f django

# OpenEMR 컨테이너 확인
docker compose ps openemr
```

---

## 3. 문제 해결

### 문제 1: "OpenEMR 접속 에러"

**증상**:
```
ERROR: Failed to retrieve OpenEMR Access Token: 401 Unauthorized
```

**원인**: `SKIP_OPENEMR_INTEGRATION` 설정이 없어서 FHIR API를 호출하려 시도

**해결**:
```bash
# .env 파일에 추가
SKIP_OPENEMR_INTEGRATION=True

# Django 재시작
docker compose restart django
```

---

### 문제 2: "OpenEMR MySQL 접속 실패"

**증상**:
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'openemr-mysql'")
```

**원인**: OpenEMR MySQL 컨테이너가 실행 중이 아님

**해결**:
```bash
# OpenEMR 컨테이너 상태 확인
docker compose ps openemr-mysql openemr

# 없으면 시작
docker compose up -d openemr-mysql openemr

# 준비 대기 (최대 3분)
docker compose logs -f openemr

# "apache2 -D FOREGROUND" 메시지가 보이면 준비 완료
```

---

### 문제 3: "환자 등록 시 에러"

**증상**:
```python
persistence_status = {"django": "success", "openemr": "error"}
```

**디버깅**:
```bash
# Django Shell 진입
docker compose exec django python manage.py shell
```

```python
# OpenEMR DB 연결 테스트
from django.db import connections

with connections['openemr'].cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM patient_data")
    count = cursor.fetchone()[0]
    print(f"OpenEMR 환자 수: {count}")

# Direct DB Access 테스트
from emr.repositories import OpenEMRPatientRepository

patient_data = {
    'patient_id': 'P-2026-TEST-001',
    'given_name': 'Test',
    'family_name': 'User',
    'birth_date': '1990-01-01',
    'gender': 'male',
    'phone': '010-1234-5678',
    'email': 'test@example.com',
    'address': '서울시 강남구, 서울, 대한민국'
}

pid = OpenEMRPatientRepository.create_patient_in_openemr(patient_data)
print(f"생성된 OpenEMR PID: {pid}")
```

---

## 4. 확인 체크리스트

배포 완료 후 다음을 확인하세요:

### OpenEMR 연동 설정
- [ ] `.env` 파일에 `SKIP_OPENEMR_INTEGRATION=True` 존재
- [ ] `OPENEMR_DB_HOST=openemr-mysql` (localhost 아님!)
- [ ] `OPENEMR_DB_PORT=3306` (3307 아님!)

### Docker 컨테이너
- [ ] `docker compose ps` 실행 시 8개 컨테이너 모두 "Up" 상태
- [ ] `cdss-mysql` 컨테이너 healthy
- [ ] `cdss-openemr-mysql` 컨테이너 healthy
- [ ] `cdss-openemr` 컨테이너 healthy

### 데이터베이스
- [ ] Django DB 마이그레이션 완료 (`docker compose logs django | grep "Applied"`)
- [ ] OpenEMR DB 접속 가능 (`docker compose exec openemr-mysql mysql -uroot -proot`)

### API 테스트
- [ ] Django API health check: `curl http://localhost:8000/api/acct/health/`
- [ ] 환자 등록 API 정상 동작

---

## 5. FAQ

### Q1. OAuth2 설정이 정말 필요 없나요?

**A**: 네, **필요 없습니다**.

`SKIP_OPENEMR_INTEGRATION=True`로 설정하면 Django가 OpenEMR MySQL DB에 직접 접근하므로 OAuth2가 불필요합니다.

[50_OpenEMR_OAuth2_설정_가이드.md](50_OpenEMR_OAuth2_설정_가이드.md)의 OAuth2 설정은 **FHIR API 방식을 사용할 때만** 필요합니다.

---

### Q2. OpenEMR 컨테이너 없이 배포 가능한가요?

**A**: 아니요, **OpenEMR 컨테이너가 필요합니다**.

`SKIP_OPENEMR_INTEGRATION=True`는 **FHIR API 호출만** Skip하는 것이고, **Direct DB Access는 계속 사용**합니다.

따라서 `openemr-mysql`과 `openemr` 컨테이너 모두 필요합니다.

---

### Q3. 프로덕션에서도 Direct DB Access를 사용해도 되나요?

**A**: 네, **권장합니다**.

**장점**:
- 빠르고 안정적
- OAuth2 설정/관리 불필요
- OpenEMR 버전 업그레이드에 덜 의존적 (DB 스키마는 안정적)

**주의사항**:
- OpenEMR 메이저 업그레이드 시 스키마 변경 확인 필요
- `repositories.py`의 SQL 쿼리 검토 권장

---

### Q4. FHIR API 방식으로 전환하려면?

**A**: 다음 단계를 따르세요:

```bash
# 1. .env 파일 수정
SKIP_OPENEMR_INTEGRATION=False

# 2. OpenEMR OAuth2 Client 등록
# 가이드: 01_doc/50_OpenEMR_OAuth2_설정_가이드.md

# 3. .env에 Client ID/Secret 추가
OPENEMR_CLIENT_ID=neuronova-cdss-internal
OPENEMR_CLIENT_SECRET=your_generated_secret

# 4. Django 재시작
docker compose restart django

# 5. 테스트
docker compose exec django python manage.py shell
from emr.services.openemr_client import OpenEMRClient
client = OpenEMRClient()
token = client.get_access_token()
print(f"Token: {token[:30]}...")
```

---

## 6. 관련 문서

- **배포 가이드**: [12_GCP_배포_가이드.md](12_GCP_배포_가이드.md)
- **OpenEMR OAuth2 설정** (FHIR API 사용 시만): [50_OpenEMR_OAuth2_설정_가이드.md](50_OpenEMR_OAuth2_설정_가이드.md)
- **인증 문제 해결**: [51_OpenEMR_인증_문제_해결_보고서.md](51_OpenEMR_인증_문제_해결_보고서.md)
- **Docker Compose 파일**: [NeuroNova_02_back_end/02_django_server/docker-compose.yml](../../NeuroNova_02_back_end/02_django_server/docker-compose.yml)

---

**문서 버전**: 1.0
**최종 수정일**: 2026-01-05
**작성자**: Claude AI (Sonnet 4.5)
**검토 상태**: Ready for Production
