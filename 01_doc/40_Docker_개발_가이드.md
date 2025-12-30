# NeuroNova CDSS - Docker 개발 환경 가이드 v2.1

**작성일**: 2025-12-30
**아키텍처**: v2.1 (Secure Proxy Pattern + Multi-SPA)
**대상**: 로컬 개발 환경

---

## 📋 목차

1. [개요](#개요)
2. [사전 준비](#사전-준비)
3. [빠른 시작](#빠른-시작)
4. [상세 설정](#상세-설정)
5. [서비스 접속](#서비스-접속)
6. [개발 워크플로우](#개발-워크플로우)
7. [트러블슈팅](#트러블슈팅)

---

## 🎯 개요

### 아키텍처 v2.1 핵심 특징

이 Docker 구성은 **아키텍처 v2.1**을 완벽히 구현합니다:

- ✅ **Secure Proxy Pattern**: Django JWT 검증 + Nginx X-Accel-Redirect
- ✅ **Multi-SPA Strategy**: React Main + OHIF Viewer 분리 빌드
- ✅ **Internal Routing**: Orthanc 외부 직접 접속 차단
- ✅ **HTJ2K Pipeline**: Celery 이미지 변환 공장
- ✅ **Hot Reload**: Django 소스 코드 변경 시 자동 재시작

### 서비스 구성

```
┌─────────────────────────────────────────────────────┐
│  Ingress Layer                                      │
│  - Nginx (Port 80) - Reverse Proxy                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Application Layer                                  │
│  - Django API (Port 8000)                          │
│  - Celery Worker (비동기 작업)                      │
│  - Celery Beat (스케줄러)                          │
│  - Flower (Port 5555) - 모니터링                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Data Layer                                         │
│  - CDSS MySQL (Port 3306)                          │
│  - Redis (Port 6379)                               │
│  - Orthanc PACS (Port 8042, 4242)                  │
│  - OpenEMR + MySQL (Port 8081, 3307)               │
│  - HAPI FHIR (Port 8080)                           │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ 사전 준비

### 1. 필수 소프트웨어 설치

- **Docker Desktop** (Windows/Mac) 또는 **Docker Engine** (Linux)
  - 버전: 20.10 이상
  - Docker Compose v2 포함
- **Git** (소스 코드 관리)

### 2. 시스템 요구사항

- **메모리**: 최소 8GB (권장 16GB)
- **디스크 공간**: 최소 20GB
- **포트**: 80, 3306, 3307, 4242, 5555, 6379, 8000, 8042, 8080, 8081, 15672 사용 가능

### 3. Docker 설정 확인

Windows/Mac의 경우 Docker Desktop 리소스 설정:

```
Settings → Resources
- CPUs: 4 이상
- Memory: 8GB 이상
- Disk: 60GB 이상
```

---

## 🚀 빠른 시작

### Step 1: 환경변수 설정

```bash
# 1. .env.example을 .env로 복사
cp .env.example .env

# 2. .env 파일을 열어 비밀번호 변경
# 다음 값들을 반드시 변경하세요:
# - DJANGO_SECRET_KEY
# - DB_PASSWORD
# - DB_ROOT_PASSWORD
# - OPENEMR_DB_PASSWORD
# - ORTHANC_PASSWORD
```

**중요**: `.env` 파일은 절대 Git에 커밋하지 마세요! (`.gitignore`에 이미 추가됨)

### Step 2: Docker 네트워크 생성

```bash
# neuronova_network 생성 (최초 1회만)
docker network create neuronova_network
```

### Step 3: 전체 스택 실행

```bash
# 모든 서비스 빌드 및 실행
docker compose -f docker-compose.dev.yml up -d --build

# 로그 확인 (실시간)
docker compose -f docker-compose.dev.yml logs -f

# 특정 서비스만 로그 확인
docker compose -f docker-compose.dev.yml logs -f django
```

### Step 4: Django 초기 설정

```bash
# Django 마이그레이션 (자동 실행되지만 확인용)
docker compose -f docker-compose.dev.yml exec django python manage.py migrate

# 슈퍼유저 생성
docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser

# 테스트 데이터 시딩 (선택사항)
docker compose -f docker-compose.dev.yml exec django python manage.py seed_test_data
```

### Step 5: 접속 확인

브라우저에서 다음 주소로 접속:

- **Nginx Gateway**: http://localhost
- **Django Admin**: http://localhost/api/admin/
- **Django API Docs**: http://localhost/api/swagger/
- **Flower (Celery)**: http://localhost/flower/
- **Orthanc (직접 접속 - 개발용)**: http://localhost/orthanc-direct/

---

## ⚙️ 상세 설정

### 프론트엔드 빌드 (Multi-SPA)

#### React Main App

```bash
# 1. React 앱 디렉토리로 이동
cd NeuroNova_03_front_end_react/00_test_client

# 2. 의존성 설치
npm install

# 3. 빌드
npm run build

# 4. 빌드 결과물을 static 폴더로 복사
cp -r build/* ../../static/react-main/

# 5. Nginx 재시작
docker compose -f docker-compose.dev.yml restart nginx
```

#### Custom OHIF Viewer

```bash
# 1. OHIF 디렉토리로 이동
cd NeuroNova_02_back_end/04_ohif_viewer

# 2. 의존성 설치
yarn install

# 3. 빌드
yarn run build

# 4. 빌드 결과물을 static 폴더로 복사
cp -r dist/* ../../static/ohif-dist/

# 5. Nginx 재시작
docker compose -f ../../docker-compose.dev.yml restart nginx
```

### Nginx 설정 수정

Nginx 설정 파일 위치:

- **메인 설정**: `nginx/nginx.dev.conf`
- **사이트 설정**: `nginx/conf.d/neuronova.conf`

설정 변경 후 적용:

```bash
# Nginx 설정 테스트
docker compose -f docker-compose.dev.yml exec nginx nginx -t

# Nginx 재시작
docker compose -f docker-compose.dev.yml restart nginx
```

### Django 소스 코드 핫 리로드

Django 컨테이너는 소스 코드를 볼륨 마운트하여 **자동 리로드**됩니다:

```yaml
# docker-compose.dev.yml 에서
volumes:
  - ./NeuroNova_02_back_end/02_django_server:/app
```

**사용법**:
1. `NeuroNova_02_back_end/02_django_server` 폴더의 Python 파일 수정
2. Django가 자동으로 변경 감지 및 재시작
3. 로그 확인: `docker compose -f docker-compose.dev.yml logs -f django`

### Celery 작업 모니터링

**Flower UI**: http://localhost/flower/

- 실시간 작업 상태 확인
- Worker 상태 모니터링
- 큐 길이 확인

**CLI로 확인**:

```bash
# Celery Worker 상태
docker compose -f docker-compose.dev.yml exec celery-worker celery -A cdss_backend inspect active

# 등록된 Task 목록
docker compose -f docker-compose.dev.yml exec celery-worker celery -A cdss_backend inspect registered
```

---

## 🌐 서비스 접속

### 외부 접속 포트 (Nginx를 통한 통합 접근)

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Main React SPA** | http://localhost/ | 메인 대시보드 (빌드 후) |
| **OHIF Viewer** | http://localhost/pacs-viewer/ | DICOM 뷰어 (빌드 후) |
| **Django API** | http://localhost/api/ | REST API 엔드포인트 |
| **Django Admin** | http://localhost/api/admin/ | 관리자 페이지 |
| **API Docs (Swagger)** | http://localhost/api/swagger/ | API 문서 |
| **Flower** | http://localhost/flower/ | Celery 모니터링 |

### 개발/디버깅용 직접 접속

| 서비스 | 포트 | URL | 용도 |
|--------|------|-----|------|
| Django | 8000 | http://localhost:8000 | 직접 API 호출 |
| MySQL (CDSS) | 3306 | localhost:3306 | DB 클라이언트 연결 |
| MySQL (OpenEMR) | 3307 | localhost:3307 | DB 클라이언트 연결 |
| Redis | 6379 | localhost:6379 | Redis CLI 연결 |
| Orthanc HTTP | 8042 | http://localhost:8042 | PACS UI (개발용) |
| Orthanc DICOM | 4242 | localhost:4242 | DICOM C-STORE |
| OpenEMR | 8081 | http://localhost:8081 | EMR 시스템 |
| HAPI FHIR | 8080 | http://localhost:8080/fhir | FHIR API |
| Flower | 5555 | http://localhost:5555 | Celery 모니터링 직접 |

### DB 접속 정보

**CDSS MySQL**:
```
Host: localhost
Port: 3306
Database: cdss_db
Username: cdss_user
Password: (your .env DB_PASSWORD)
```

**OpenEMR MySQL**:
```
Host: localhost
Port: 3307
Database: openemr
Username: openemr
Password: (your .env OPENEMR_DB_PASSWORD)
```

**Redis**:
```bash
# Redis CLI 접속
docker compose -f docker-compose.dev.yml exec redis redis-cli

# 또는 로컬에서
redis-cli -h localhost -p 6379
```

---

## 💻 개발 워크플로우

### 시나리오 1: Django API 개발

```bash
# 1. Django 코드 수정
# NeuroNova_02_back_end/02_django_server/apps/*/views.py

# 2. 자동 리로드 확인 (로그)
docker compose -f docker-compose.dev.yml logs -f django

# 3. API 테스트
curl http://localhost/api/your-endpoint/

# 4. DB 마이그레이션이 필요한 경우
docker compose -f docker-compose.dev.yml exec django python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec django python manage.py migrate
```

### 시나리오 2: Celery 비동기 작업 개발

```bash
# 1. Task 정의 (예: apps/pacs/tasks.py)
@shared_task
def convert_dicom_to_htj2k(study_id):
    # HTJ2K 변환 로직
    pass

# 2. Celery Worker 재시작
docker compose -f docker-compose.dev.yml restart celery-worker

# 3. Task 트리거 (Django 코드 또는 Shell)
docker compose -f docker-compose.dev.yml exec django python manage.py shell
>>> from apps.pacs.tasks import convert_dicom_to_htj2k
>>> convert_dicom_to_htj2k.delay('study-123')

# 4. Flower에서 작업 상태 확인
# http://localhost/flower/
```

### 시나리오 3: Nginx 라우팅 테스트

```bash
# 1. Nginx 설정 수정
# nginx/conf.d/neuronova.conf

# 2. 설정 검증
docker compose -f docker-compose.dev.yml exec nginx nginx -t

# 3. Nginx 재시작
docker compose -f docker-compose.dev.yml restart nginx

# 4. 라우팅 테스트
curl -I http://localhost/api/health/
curl -I http://localhost/pacs-viewer/
```

### 시나리오 4: Secure Proxy Pattern 테스트

**목표**: Django가 JWT 검증 후 Nginx에게 Orthanc 접근 위임

```python
# Django View 예시 (apps/pacs/views.py)
from django.http import HttpResponse

def secure_dicom_proxy(request, study_id):
    # 1. JWT 인증 확인
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    # 2. X-Accel-Redirect 헤더 반환
    response = HttpResponse(status=200)
    response['X-Accel-Redirect'] = f'/internal-orthanc/studies/{study_id}'
    response['Content-Type'] = 'application/dicom'
    return response
```

**테스트**:

```bash
# 1. JWT 토큰 획득
TOKEN=$(curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' | jq -r '.access')

# 2. Secure Proxy를 통해 DICOM 데이터 요청
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost/api/pacs/studies/study-123/
```

---

## 🐛 트러블슈팅

### 1. 컨테이너가 시작되지 않음

```bash
# 모든 컨테이너 상태 확인
docker compose -f docker-compose.dev.yml ps

# 특정 서비스 로그 확인
docker compose -f docker-compose.dev.yml logs django

# 컨테이너 재시작
docker compose -f docker-compose.dev.yml restart django
```

### 2. 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인 (Windows)
netstat -ano | findstr :8000

# 포트 사용 중인 프로세스 확인 (Linux/Mac)
lsof -i :8000

# .env 파일에서 포트 변경
# 예: DB_HOST_PORT=3307 → 3308
```

### 3. DB 연결 실패

```bash
# MySQL 컨테이너 상태 확인
docker compose -f docker-compose.dev.yml exec cdss-mysql mysqladmin ping

# DB 로그 확인
docker compose -f docker-compose.dev.yml logs cdss-mysql

# Health check 상태 확인
docker inspect neuronova-cdss-mysql-dev | grep -A 10 Health
```

### 4. Nginx 502 Bad Gateway

**원인**: Django 컨테이너가 정상 동작하지 않음

```bash
# Django 컨테이너 상태 확인
docker compose -f docker-compose.dev.yml ps django

# Django 로그 확인
docker compose -f docker-compose.dev.yml logs django

# Django 재시작
docker compose -f docker-compose.dev.yml restart django
```

### 5. 프론트엔드가 표시되지 않음

**원인**: 빌드 파일이 복사되지 않았거나 Nginx 설정 오류

```bash
# 1. static 폴더 확인
ls -la static/react-main/
ls -la static/ohif-dist/

# 2. Placeholder 파일만 있는 경우 → 빌드 필요
# 위의 "프론트엔드 빌드" 섹션 참조

# 3. Nginx 설정 검증
docker compose -f docker-compose.dev.yml exec nginx nginx -t

# 4. Nginx 로그 확인
docker compose -f docker-compose.dev.yml logs nginx
```

### 6. Celery 작업이 실행되지 않음

```bash
# 1. Redis 연결 확인
docker compose -f docker-compose.dev.yml exec redis redis-cli ping

# 2. Celery Worker 상태 확인
docker compose -f docker-compose.dev.yml logs celery-worker

# 3. Worker 재시작
docker compose -f docker-compose.dev.yml restart celery-worker

# 4. Flower에서 확인
# http://localhost/flower/
```

### 7. X-Accel-Redirect가 작동하지 않음

**증상**: OHIF Viewer에서 이미지를 불러오지 못함

```bash
# 1. Django에서 X-Accel-Redirect 헤더 반환 확인
docker compose -f docker-compose.dev.yml logs django | grep "X-Accel"

# 2. Nginx 설정 확인
docker compose -f docker-compose.dev.yml exec nginx cat /etc/nginx/conf.d/neuronova.conf | grep "internal-orthanc"

# 3. Orthanc 접근 가능 여부 확인
docker compose -f docker-compose.dev.yml exec nginx wget -O- http://orthanc:8042/system
```

### 8. 전체 초기화 (Clean Slate)

```bash
# 1. 모든 컨테이너 중지 및 제거
docker compose -f docker-compose.dev.yml down

# 2. 볼륨까지 삭제 (데이터 완전 삭제)
docker compose -f docker-compose.dev.yml down -v

# 3. 네트워크 재생성
docker network create neuronova_network

# 4. 처음부터 다시 시작
docker compose -f docker-compose.dev.yml up -d --build
```

---

## 📚 추가 참고 자료

- **아키텍처 상세**: [01_doc/06_시스템_아키텍처_v2.md](01_doc/06_시스템_아키텍처_v2.md)
- **배포 가이드**: [01_doc/08_배포_와_운영_요약.md](01_doc/08_배포_와_운영_요약.md)
- **API 명세**: [01_doc/10_API_명세서.md](01_doc/10_API_명세서.md)
- **빠른 온보딩**: [01_doc/REF_CLAUDE_ONBOARDING_QUICK.md](01_doc/REF_CLAUDE_ONBOARDING_QUICK.md)

---

## 🔧 유용한 명령어 모음

```bash
# === 전체 스택 관리 ===
# 시작
docker compose -f docker-compose.dev.yml up -d

# 중지
docker compose -f docker-compose.dev.yml stop

# 중지 및 제거
docker compose -f docker-compose.dev.yml down

# 재시작
docker compose -f docker-compose.dev.yml restart

# 빌드 및 시작 (코드 변경 후)
docker compose -f docker-compose.dev.yml up -d --build

# === 로그 확인 ===
# 전체 로그
docker compose -f docker-compose.dev.yml logs -f

# 특정 서비스
docker compose -f docker-compose.dev.yml logs -f django celery-worker

# === 컨테이너 접속 ===
# Django Shell
docker compose -f docker-compose.dev.yml exec django python manage.py shell

# Bash 접속
docker compose -f docker-compose.dev.yml exec django bash

# === DB 관리 ===
# 마이그레이션
docker compose -f docker-compose.dev.yml exec django python manage.py migrate

# 마이그레이션 파일 생성
docker compose -f docker-compose.dev.yml exec django python manage.py makemigrations

# MySQL CLI
docker compose -f docker-compose.dev.yml exec cdss-mysql mysql -u cdss_user -p cdss_db

# === 리소스 정리 ===
# 사용하지 않는 이미지 삭제
docker image prune -a

# 사용하지 않는 볼륨 삭제
docker volume prune

# 전체 시스템 정리
docker system prune -a --volumes
```

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-30
**작성자**: NeuroNova Development Team
**Architecture**: v2.1 - Secure Proxy Pattern + Multi-SPA
