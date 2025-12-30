# NeuroNova CDSS - Docker 빠른 시작 가이드

## 🚀 새 PC에서 Docker로 시작하기

이 가이드는 **완전히 깨끗한 PC**에서 NeuroNova CDSS를 Docker로 실행하는 방법입니다.

---

## 📋 사전 준비

### 1. 필수 소프트웨어 설치

- **Docker Desktop** (Windows/Mac) 또는 **Docker Engine** (Linux)
  - 버전: 20.10 이상
  - 다운로드: https://www.docker.com/products/docker-desktop
- **Git** (코드 클론용)
- **최소 시스템 요구사항**:
  - RAM: 8GB 이상
  - 디스크: 20GB 이상 여유 공간
  - CPU: 4코어 이상 권장

### 2. Docker 설치 확인

```bash
docker --version
docker compose version
```

정상 출력 예시:
```
Docker version 24.0.0, build xxxxx
Docker Compose version v2.20.0
```

---

## 🔧 설치 단계 (Step-by-Step)

### Step 1: 저장소 클론

```bash
git clone <repository-url>
cd NeuroNova_v1
```

### Step 2: 환경 변수 설정

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

**중요!** `.env` 파일을 열어서 다음 값들을 **반드시 변경**하세요:

```bash
# .env 파일 수정 (텍스트 에디터 사용)
notepad .env  # Windows
nano .env     # Linux/Mac
```

**필수 변경 항목**:
```env
# Django Secret Key - 새로운 랜덤 문자열로 변경
DJANGO_SECRET_KEY=your-new-secret-key-here-make-it-long-and-random

# Database 비밀번호 변경
DB_PASSWORD=your_secure_password_here
DB_ROOT_PASSWORD=your_root_password_here

# Orthanc 비밀번호 변경
ORTHANC_PASSWORD=your_orthanc_password_here

# OpenEMR 비밀번호 변경
OPENEMR_DB_PASSWORD=your_openemr_password_here
OPENEMR_DB_ROOT_PASSWORD=your_openemr_root_password_here
OPENEMR_OE_PASS=your_admin_password_here
```

### Step 3: Docker 네트워크 생성

```bash
docker network create neuronova_network
```

출력:
```
<network-id>
```

### Step 4: Docker 스택 실행

```bash
# 전체 스택 빌드 및 시작 (최초 실행 시 5-10분 소요)
docker compose -f docker-compose.dev.yml up -d --build
```

진행 상황:
```
[+] Building 120.5s (25/25) FINISHED
[+] Running 11/11
 ✔ Container neuronova-cdss-mysql-dev      Started
 ✔ Container neuronova-redis-dev           Started
 ✔ Container neuronova-orthanc-dev         Started
 ✔ Container neuronova-django-dev          Started
 ✔ Container neuronova-nginx-dev           Started
 ...
```

### Step 5: 서비스 상태 확인

```bash
# 모든 컨테이너 상태 확인
docker compose -f docker-compose.dev.yml ps
```

**정상 출력 예시**:
```
NAME                        STATUS              PORTS
neuronova-nginx-dev         Up (healthy)        0.0.0.0:80->80/tcp
neuronova-django-dev        Up (healthy)
neuronova-orthanc-dev       Up (healthy)        0.0.0.0:8042->8042/tcp
neuronova-redis-dev         Up (healthy)
neuronova-cdss-mysql-dev    Up (healthy)
...
```

### Step 6: Django 초기 설정

```bash
# Django 마이그레이션 실행
docker compose -f docker-compose.dev.yml exec django python manage.py migrate

# Django 관리자 계정 생성
docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser
```

프롬프트에서 입력:
- Username: `admin` (또는 원하는 이름)
- Email: 이메일 주소 입력
- Password: 안전한 비밀번호 입력

---

## ✅ 설치 완료 확인

### 1. 웹 브라우저에서 접속 테스트

| 서비스 | URL | 설명 |
|--------|-----|------|
| **메인 페이지** | http://localhost/ | React Main SPA (placeholder) |
| **Django Admin** | http://localhost/admin/ | Django 관리자 페이지 |
| **API 문서** | http://localhost/api/docs/ | Swagger UI |
| **Flower** | http://localhost:5555/ | Celery 모니터링 |
| **OpenEMR** | http://localhost:8081/ | EMR 시스템 |
| **Orthanc** | http://localhost:8042/ | PACS (개발 전용) |

### 2. API 동작 확인

```bash
# Health check
curl http://localhost/health

# API Schema
curl http://localhost/api/schema/ | head -10
```

정상 출력:
```
OK

openapi: 3.0.3
info:
  title: NeuroNova CDSS API
  version: 1.0.0
```

---

## 🔄 일상적인 사용

### 시작

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 중지

```bash
docker compose -f docker-compose.dev.yml down
```

### 로그 확인

```bash
# 전체 로그
docker compose -f docker-compose.dev.yml logs -f

# 특정 서비스 로그
docker compose -f docker-compose.dev.yml logs -f django
docker compose -f docker-compose.dev.yml logs -f nginx
```

### 재시작

```bash
# 전체 재시작
docker compose -f docker-compose.dev.yml restart

# 특정 서비스만 재시작
docker compose -f docker-compose.dev.yml restart django
```

---

## 🛠️ 문제 해결 (Troubleshooting)

### 문제 1: 포트가 이미 사용 중

**에러**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**해결**:
```bash
# Windows: 포트 사용 프로세스 확인
netstat -ano | findstr :80

# Linux/Mac
lsof -i :80

# 또는 .env 파일에서 포트 변경
```

### 문제 2: Docker 네트워크 충돌

**에러**: `network neuronova_network already exists but has incorrect label`

**해결**:
```bash
# 기존 네트워크 삭제 후 재생성
docker network rm neuronova_network
docker network create neuronova_network

# 스택 재시작
docker compose -f docker-compose.dev.yml up -d
```

### 문제 3: 컨테이너가 계속 재시작됨

**확인**:
```bash
# 로그 확인
docker compose -f docker-compose.dev.yml logs <service-name>

# 예: Django 로그
docker compose -f docker-compose.dev.yml logs django
```

**일반적인 원인**:
- DB 연결 실패 → MySQL이 healthy 상태인지 확인
- 환경 변수 오류 → .env 파일 확인
- 포트 충돌 → 다른 서비스가 같은 포트 사용 중

### 문제 4: 데이터베이스 연결 실패

**해결**:
```bash
# MySQL 상태 확인
docker compose -f docker-compose.dev.yml exec cdss-mysql mysqladmin ping -p

# MySQL 로그 확인
docker compose -f docker-compose.dev.yml logs cdss-mysql

# Django에서 DB 접속 테스트
docker compose -f docker-compose.dev.yml exec django python manage.py dbshell
```

### 문제 5: 완전히 초기화하고 싶을 때

**경고**: 모든 데이터가 삭제됩니다!

```bash
# 1. 컨테이너, 볼륨, 네트워크 모두 삭제
docker compose -f docker-compose.dev.yml down -v

# 2. 네트워크 삭제
docker network rm neuronova_network

# 3. 이미지도 삭제하고 싶다면
docker compose -f docker-compose.dev.yml down --rmi all -v

# 4. 다시 처음부터 시작
docker network create neuronova_network
docker compose -f docker-compose.dev.yml up -d --build
```

---

## 📊 서비스 아키텍처

```
Internet (User)
   ↓
┌─────────────────────────────────────────┐
│  Nginx (Port 80)                        │ ← 진입점
│  - Static Files                         │
│  - Reverse Proxy                        │
│  - Secure Proxy Pattern                 │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  Django + Celery                        │
│  - JWT Auth                             │
│  - Business Logic                       │
│  - HTJ2K Processing                     │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  Data Layer (Internal Only)             │
│  - MySQL (CDSS DB)                      │
│  - Redis (Cache/Broker)                 │
│  - Orthanc (PACS)                       │
│  - OpenEMR / HAPI FHIR                  │
└─────────────────────────────────────────┘
```

---

## 🔐 보안 주의사항

1. **절대로 .env 파일을 Git에 커밋하지 마세요!**
   - `.gitignore`에 이미 추가되어 있음
   - 실수로 커밋했다면: `git rm --cached .env`

2. **프로덕션 환경에서는**:
   - 모든 `CHANGE_ME` 값을 강력한 비밀번호로 변경
   - `DEBUG=False`로 설정
   - `ALLOWED_HOSTS`를 실제 도메인으로 제한
   - HTTPS 사용 (Cloudflare 또는 Let's Encrypt)

3. **포트 노출 최소화**:
   - 프로덕션에서는 Orthanc 포트(8042, 4242)를 외부에 노출하지 말 것
   - Nginx만 80/443 포트 오픈

---

## 📚 추가 문서

- **상세 가이드**: [DOCKER_DEV_GUIDE.md](DOCKER_DEV_GUIDE.md)
- **아키텍처 설명**: [DOCKER_ARCHITECTURE.md](DOCKER_ARCHITECTURE.md)
- **시스템 아키텍처**: [01_doc/06_시스템_아키텍처_v2.md](01_doc/06_시스템_아키텍처_v2.md)
- **빠른 온보딩**: [01_doc/REF_CLAUDE_ONBOARDING_QUICK.md](01_doc/REF_CLAUDE_ONBOARDING_QUICK.md)

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: 첫 실행 시 시간이 얼마나 걸리나요?
A: 이미지 다운로드 + 빌드 합쳐서 5-10분 정도 소요됩니다 (인터넷 속도에 따라 다름).

### Q2: 데이터는 어디에 저장되나요?
A: Docker 볼륨에 저장됩니다. `docker compose down` 해도 데이터는 유지됩니다. 삭제하려면 `-v` 옵션 사용.

### Q3: 개발 중 코드 변경이 바로 반영되나요?
A: Django는 Hot Reload가 활성화되어 있어 코드 변경 시 자동 재시작됩니다.

### Q4: 프로덕션 배포는 어떻게 하나요?
A: [01_doc/12_GCP_배포_가이드.md](01_doc/12_GCP_배포_가이드.md) 참조

### Q5: Windows에서 성능이 느린데요?
A: WSL2 사용을 권장합니다. Docker Desktop 설정에서 WSL2 backend 활성화.

---

**마지막 업데이트**: 2025-12-30
**버전**: v2.1 - Architecture v2.1 (Secure Proxy Pattern + Multi-SPA)
