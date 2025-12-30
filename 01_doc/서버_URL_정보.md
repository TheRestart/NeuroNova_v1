# NeuroNova CDSS 서버 및 페이지 URL 정보

**작성일**: 2025-12-30
**버전**: 1.0
**목적**: 모든 서버와 웹 페이지의 접속 URL 한눈에 보기

---

## 목차

1. [Django Backend 서버](#1-django-backend-서버)
2. [React 테스트 클라이언트](#2-react-테스트-클라이언트)
3. [외부 시스템 (Docker)](#3-외부-시스템-docker)
4. [모니터링 도구](#4-모니터링-도구)
5. [개발 도구](#5-개발-도구)
6. [빠른 접속 체크리스트](#6-빠른-접속-체크리스트)

---

## 1. Django Backend 서버

### 1.1 메인 API 서버
**URL**: http://localhost:8000

**실행 방법**:
```bash
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\python manage.py runserver
```

### 1.2 API 문서화

| 서비스 | URL | 설명 |
|--------|-----|------|
| Swagger UI | http://localhost:8000/api/docs/ | 대화형 API 문서 (추천) |
| ReDoc | http://localhost:8000/api/redoc/ | 읽기 전용 API 문서 |
| Django Admin | http://localhost:8000/admin/ | 관리자 페이지 |

**관리자 계정**:
- 사용자명: `admin`
- 비밀번호: `admin123!@#`

### 1.3 주요 API 엔드포인트

| UC | 엔드포인트 | 설명 |
|----|-----------|------|
| UC01 | http://localhost:8000/api/acct/ | 인증/권한 |
| UC02 | http://localhost:8000/api/emr/ | EMR (전자의무기록) |
| UC03 | http://localhost:8000/api/ocs/ | 처방전달시스템 |
| UC04 | http://localhost:8000/api/lis/ | 검체검사시스템 |
| UC05 | http://localhost:8000/api/ris/ | 영상검사시스템 |
| UC06 | http://localhost:8000/api/ai/ | AI 추론 |
| UC07 | http://localhost:8000/api/alert/ | 알림 관리 |
| UC08 | http://localhost:8000/api/fhir/ | FHIR 표준 |
| UC09 | http://localhost:8000/api/audit/ | 감사 로그 |

---

## 2. React 테스트 클라이언트

### 2.1 메인 페이지
**URL**: http://localhost:3000

**실행 방법 (WSL 권장)**:
```bash
# WSL에서
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client
npm install  # 최초 1회만
npm start
```

**실행 방법 (Windows)**:
```powershell
cd NeuroNova_03_front_end_react\00_test_client
npm install  # 최초 1회만
npm start
```

### 2.2 테스트 페이지

| 페이지 | URL | 설명 |
|--------|-----|------|
| 로그인 | http://localhost:3000/ | 로그인 페이지 (빠른 로그인 버튼) |
| 대시보드 | http://localhost:3000/dashboard | UC 테스트 페이지 목록 |
| UC01 테스트 | http://localhost:3000/uc01 | 인증/권한 테스트 |
| UC02 테스트 | http://localhost:3000/uc02 | EMR 테스트 |
| UC03 테스트 | http://localhost:3000/uc03 | OCS 테스트 |
| UC04 테스트 | http://localhost:3000/uc04 | LIS 테스트 |
| UC05 테스트 | http://localhost:3000/uc05 | RIS 테스트 |
| UC06 테스트 | http://localhost:3000/uc06 | AI 테스트 |
| UC07 테스트 | http://localhost:3000/uc07 | 알림 테스트 |
| UC08 테스트 | http://localhost:3000/uc08 | FHIR 테스트 |
| UC09 테스트 | http://localhost:3000/uc09 | 감사 로그 테스트 |

### 2.3 테스트 계정

| 역할 | 사용자명 | 비밀번호 |
|------|----------|----------|
| 관리자 | `admin` | `admin123!@#` |
| 의사 | `doctor` | `doctor123!@#` |
| 간호사 | `nurse` | `nurse123!@#` |
| 환자 | `patient` | `patient123!@#` |
| 방사선사 | `radiologist` | `rib123!@#` |
| 검사실 기사 | `labtech` | `lab123!@#` |

---

## 3. 외부 시스템 (Docker)

### 3.1 Orthanc PACS (DICOM 서버)

**URL**: http://localhost:8042

**실행 방법**:
```bash
cd NeuroNova_02_back_end/05_orthanc_pacs
docker-compose up -d
```

**주요 페이지**:
- **웹 인터페이스**: http://localhost:8042/app/explorer.html
- **DICOMweb API**: http://localhost:8042/dicom-web/
- **System API**: http://localhost:8042/system

**인증**: 기본적으로 인증 비활성화 (개발 환경)

### 3.2 OpenEMR (외부 EMR 시스템)

**URL**: http://localhost:8080 (설정에 따라 다름)

**실행 방법**:
```bash
cd NeuroNova_02_back_end/03_openemr_server
docker-compose up -d
```

**기본 계정**:
- 사용자명: `admin`
- 비밀번호: `pass` (설정에 따라 다름)

### 3.3 HAPI FHIR Server

**URL**: http://localhost:8080/fhir

**실행 방법**:
```bash
cd NeuroNova_02_back_end/06_hapi_fhir
docker-compose up -d
```

**주요 엔드포인트**:
- **메타데이터**: http://localhost:8080/fhir/metadata
- **Patient 검색**: http://localhost:8080/fhir/Patient
- **Observation 검색**: http://localhost:8080/fhir/Observation

### 3.4 OHIF Viewer (의료 영상 뷰어)

**URL**: http://localhost:3000 (Orthanc 연동)

**실행 방법**:
```bash
cd NeuroNova_02_back_end/04_ohif_viewer
docker-compose up -d
```

**주의**: React 테스트 클라이언트와 포트 충돌 가능 (둘 다 3000번 포트 사용)

### 3.5 Redis (캐시 + Celery 브로커)

**URL**: redis://localhost:6379

**실행 방법**:
```bash
cd NeuroNova_02_back_end/07_redis
docker-compose up -d
```

**연결 테스트**:
```bash
redis-cli ping
# 응답: PONG
```

---

## 4. 모니터링 도구

### 4.1 Flower (Celery 모니터링)

**URL**: http://localhost:5555

**실행 방법**:
```bash
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\celery -A cdss_backend flower --port=5555
```

**기능**:
- Celery Worker 상태 모니터링
- Task 실행 이력 확인
- 실패한 Task 재시도

### 4.2 Docker 컨테이너 상태

**명령어**:
```bash
# 모든 컨테이너 상태 확인
docker ps

# 특정 컨테이너 로그 확인
docker logs <container_name>

# 컨테이너 재시작
docker restart <container_name>
```

---

## 5. 개발 도구

### 5.1 Django Shell

**실행 방법**:
```bash
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\python manage.py shell
```

**주요 명령어**:
```python
# 사용자 조회
from acct.models import User
users = User.objects.all()

# 환자 조회
from emr.models import Patient
patients = Patient.objects.all()
```

### 5.2 Django Migrations

**명령어**:
```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 마이그레이션 상태 확인
python manage.py showmigrations
```

### 5.3 테스트 실행

**명령어**:
```bash
# 전체 테스트
python manage.py test

# 특정 앱 테스트
python manage.py test emr

# 특정 테스트 케이스
python manage.py test emr.tests.test_models
```

---

## 6. 빠른 접속 체크리스트

### 개발 시작 시 실행 순서

**Step 1: Docker 서비스 시작**
```bash
# Terminal 1: Redis
cd NeuroNova_02_back_end/07_redis
docker-compose up -d

# Terminal 2: Orthanc PACS
cd NeuroNova_02_back_end/05_orthanc_pacs
docker-compose up -d
```

**Step 2: Django Backend 시작**
```bash
# Terminal 3: Django Server
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\python manage.py runserver

# Terminal 4: Celery Worker
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\celery -A cdss_backend worker -l info --concurrency=4

# Terminal 5: Celery Beat (선택)
cd NeuroNova_02_back_end/02_django_server
venv\Scripts\celery -A cdss_backend beat -l info
```

**Step 3: React 테스트 클라이언트 (선택)**
```bash
# Terminal 6: React (WSL)
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client
npm start
```

### 필수 접속 URL

| 서비스 | URL | 상태 확인 |
|--------|-----|----------|
| Django API | http://localhost:8000/api/docs/ | Swagger UI 표시 |
| React Client | http://localhost:3000 | 로그인 페이지 표시 |
| Orthanc PACS | http://localhost:8042/system | JSON 응답 |
| Redis | `redis-cli ping` | PONG 응답 |

### 문제 해결

**Django 서버가 시작되지 않는 경우**:
```bash
# 포트 사용 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

**React 앱이 시작되지 않는 경우**:
```bash
# WSL에서
rm -rf node_modules package-lock.json
npm install
npm start
```

**Docker 컨테이너가 시작되지 않는 경우**:
```bash
# 컨테이너 중지 및 제거
docker-compose down

# 이미지 재빌드
docker-compose build --no-cache

# 다시 시작
docker-compose up -d
```

---

## 부록: 포트 사용 요약

| 포트 | 서비스 | 설명 |
|------|--------|------|
| 3000 | React Test Client | 테스트 클라이언트 (또는 OHIF Viewer) |
| 5555 | Flower | Celery 모니터링 |
| 6379 | Redis | 캐시 + 메시지 브로커 |
| 8000 | Django | API 서버 |
| 8042 | Orthanc | DICOM PACS 서버 |
| 8080 | OpenEMR / HAPI FHIR | 외부 시스템 |

**주의**: OHIF Viewer와 React Test Client는 모두 3000번 포트를 사용하므로 동시 실행 불가

---

**문서 버전**: 1.0
**작성일**: 2025-12-30
**작성자**: NeuroNova Development Team
