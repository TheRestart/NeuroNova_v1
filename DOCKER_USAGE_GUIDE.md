# NeuroNova CDSS - Docker 사용 가이드

## 📋 Docker Compose 파일 종류

NeuroNova 프로젝트는 **2가지 Docker Compose 구성**을 제공합니다:

### 1. `docker-compose.infra.yml` - 인프라 전용 (개발 중 권장) ⭐

**사용 상황**:
- ✅ Django를 로컬에서 수동으로 실행할 때 (개발 중)
- ✅ MySQL을 컴퓨터에 설치된 프로그램으로 사용할 때
- ✅ 인프라 서비스만 Docker로 실행하고 싶을 때

**포함 서비스**:
- Redis (Cache & Message Broker)
- Orthanc (PACS)
- OpenEMR + OpenEMR MySQL (EMR)
- HAPI FHIR (FHIR Server)

**제외 서비스**:
- ❌ Django (로컬에서 수동 실행)
- ❌ CDSS MySQL (로컬 MySQL 사용)
- ❌ Celery Worker/Beat (Django와 함께 수동 실행)
- ❌ Nginx (개발 시 불필요)

**사용 방법**:
```bash
# 시작
docker compose -f docker-compose.infra.yml up -d

# 중지
docker compose -f docker-compose.infra.yml down

# 로그 확인
docker compose -f docker-compose.infra.yml logs -f
```

---

### 2. `docker-compose.dev.yml` - 전체 스택 (완전한 Docker 환경)

**사용 상황**:
- ✅ 모든 서비스를 Docker로 실행하고 싶을 때
- ✅ 새 PC에서 빠르게 전체 환경을 구축할 때
- ✅ 프로덕션 환경과 유사한 구성으로 테스트할 때
- ✅ CI/CD 파이프라인에서 사용할 때

**포함 서비스**:
- Nginx (Reverse Proxy)
- Django (Backend API)
- CDSS MySQL (Main Database)
- Redis (Cache & Message Broker)
- Orthanc (PACS)
- OpenEMR + OpenEMR MySQL (EMR)
- HAPI FHIR (FHIR Server)
- Celery Worker, Celery Beat, Flower

**사용 방법**:
```bash
# 시작
docker compose -f docker-compose.dev.yml up -d --build

# 중지
docker compose -f docker-compose.dev.yml down

# 로그 확인
docker compose -f docker-compose.dev.yml logs -f
```

---

## 🔧 개발 워크플로우 (infra.yml 사용)

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정 - 로컬 MySQL 설정
# DB_HOST=localhost 또는 127.0.0.1 (Docker 네트워크가 아닌 로컬)
```

### 2. Docker 인프라 시작

```bash
# Docker 네트워크 생성 (최초 1회)
docker network create neuronova_network

# 인프라 서비스 시작
docker compose -f docker-compose.infra.yml up -d

# 상태 확인
docker compose -f docker-compose.infra.yml ps
```

예상 출력:
```
NAME                            STATUS              PORTS
neuronova-redis-infra           Up (healthy)        0.0.0.0:6379->6379/tcp
neuronova-orthanc-infra         Up (healthy)        0.0.0.0:8042->8042/tcp, 0.0.0.0:4242->4242/tcp
neuronova-openemr-infra         Up (healthy)        0.0.0.0:8081->80/tcp
neuronova-openemr-mysql-infra   Up (healthy)        0.0.0.0:3307->3306/tcp
neuronova-hapi-fhir-infra       Up (healthy)        0.0.0.0:8080->8080/tcp
```

### 3. Django 로컬 실행

```bash
cd NeuroNova_02_back_end/02_django_server

# 가상환경 활성화 (선택)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Django 실행
python manage.py runserver 0.0.0.0:8000
```

### 4. Celery 실행 (필요 시)

```bash
# 터미널 1: Celery Worker
celery -A cdss_backend worker -l info --concurrency=4

# 터미널 2: Celery Beat
celery -A cdss_backend beat -l info

# 터미널 3: Flower (모니터링)
celery -A cdss_backend flower --port=5555
```

### 5. 접속 확인

| 서비스 | URL | 비고 |
|--------|-----|------|
| Django API | http://localhost:8000/api/ | 로컬 실행 |
| Django Admin | http://localhost:8000/admin/ | 로컬 실행 |
| Redis | localhost:6379 | Docker |
| Orthanc | http://localhost:8042/ | Docker |
| OpenEMR | http://localhost:8081/ | Docker |
| HAPI FHIR | http://localhost:8080/fhir/ | Docker |
| Flower | http://localhost:5555/ | 로컬 실행 시 |

---

## 🚀 새 PC에서 시작하기 (dev.yml 사용)

완전히 새로운 환경에서 모든 서비스를 Docker로 실행하려면:

```bash
# 1. 저장소 클론
git clone <repository-url>
cd NeuroNova_v1

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에서 비밀번호 변경!

# 3. Docker 네트워크 생성
docker network create neuronova_network

# 4. 전체 스택 실행
docker compose -f docker-compose.dev.yml up -d --build

# 5. Django 초기 설정
docker compose -f docker-compose.dev.yml exec django python manage.py migrate
docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser

# 6. 접속
# http://localhost/api/
# http://localhost/admin/
```

상세한 가이드는 [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)를 참조하세요.

---

## 🔄 전환하기

### infra.yml → dev.yml 전환

```bash
# 1. 인프라 중지
docker compose -f docker-compose.infra.yml down

# 2. 전체 스택 시작
docker compose -f docker-compose.dev.yml up -d --build
```

⚠️ **주의**: 데이터 볼륨 이름이 다르므로 데이터가 초기화됩니다!

### dev.yml → infra.yml 전환

```bash
# 1. 전체 스택 중지
docker compose -f docker-compose.dev.yml down

# 2. 인프라만 시작
docker compose -f docker-compose.infra.yml up -d

# 3. Django 로컬 실행
cd NeuroNova_02_back_end/02_django_server
python manage.py runserver
```

---

## 📊 서비스별 포트 맵핑

### infra.yml 사용 시

| 서비스 | 컨테이너 포트 | 호스트 포트 | 접속 URL |
|--------|--------------|------------|----------|
| Redis | 6379 | 6379 | localhost:6379 |
| Orthanc HTTP | 8042 | 8042 | http://localhost:8042 |
| Orthanc DICOM | 4242 | 4242 | localhost:4242 |
| OpenEMR | 80 | 8081 | http://localhost:8081 |
| OpenEMR MySQL | 3306 | 3307 | localhost:3307 |
| HAPI FHIR | 8080 | 8080 | http://localhost:8080/fhir |

**로컬 실행 (수동)**:
- Django: localhost:8000 (직접 실행)
- MySQL: localhost:3306 (로컬 설치)

### dev.yml 사용 시

위 포트 + 추가:

| 서비스 | 컨테이너 포트 | 호스트 포트 | 접속 URL |
|--------|--------------|------------|----------|
| Nginx | 80 | 80 | http://localhost/ |
| Django | 8000 | - | http://localhost/api/ (Nginx를 통해) |
| CDSS MySQL | 3306 | 3306 | localhost:3306 |
| Flower | 5555 | 5555 | http://localhost:5555/ |

---

## 🛠️ 일반적인 작업

### 로그 확인

```bash
# 전체 로그
docker compose -f docker-compose.infra.yml logs -f

# 특정 서비스
docker compose -f docker-compose.infra.yml logs -f redis
docker compose -f docker-compose.infra.yml logs -f orthanc
```

### 재시작

```bash
# 전체 재시작
docker compose -f docker-compose.infra.yml restart

# 특정 서비스만
docker compose -f docker-compose.infra.yml restart redis
```

### 컨테이너 접속

```bash
# Orthanc 컨테이너 접속
docker compose -f docker-compose.infra.yml exec orthanc sh

# Redis CLI
docker compose -f docker-compose.infra.yml exec redis redis-cli
```

### 완전 초기화

```bash
# 컨테이너, 볼륨, 네트워크 모두 삭제
docker compose -f docker-compose.infra.yml down -v

# 네트워크 재생성
docker network create neuronova_network

# 다시 시작
docker compose -f docker-compose.infra.yml up -d
```

---

## 🔐 환경 변수 설정 (.env)

### infra.yml 사용 시 주의사항

Django와 MySQL을 로컬에서 실행하므로 다음 설정을 확인하세요:

```env
# Django는 Docker가 아닌 로컬에서 실행
# 따라서 서비스명이 아닌 localhost 사용

# MySQL 연결 (로컬 MySQL 사용)
DB_HOST=localhost  # 또는 127.0.0.1
DB_PORT=3306

# Redis 연결 (Docker 사용, 하지만 로컬에서 접속)
REDIS_HOST=localhost  # Docker 포트가 노출되어 있음
REDIS_PORT=6379

# Orthanc 연결 (Docker 사용)
ORTHANC_API_URL=http://localhost:8042

# OpenEMR 연결 (Docker 사용)
OPENEMR_BASE_URL=http://localhost:8081

# FHIR 연결 (Docker 사용)
FHIR_SERVER_URL=http://localhost:8080/fhir
```

### dev.yml 사용 시

Docker 내부 네트워크를 사용하므로 서비스명 사용:

```env
# Docker 서비스명 사용
DB_HOST=cdss-mysql
REDIS_HOST=redis
ORTHANC_API_URL=http://orthanc:8042
```

---

## ❓ FAQ

### Q1: infra.yml과 dev.yml의 주요 차이점은?

| 항목 | infra.yml | dev.yml |
|------|-----------|---------|
| Django | ❌ 로컬 실행 | ✅ Docker |
| MySQL | ❌ 로컬 MySQL | ✅ Docker |
| Celery | ❌ 로컬 실행 | ✅ Docker |
| Nginx | ❌ 없음 | ✅ Docker |
| 인프라 서비스 | ✅ Docker | ✅ Docker |

### Q2: 왜 infra.yml을 사용하나요?

**개발 중에는 infra.yml 사용을 권장**:
- Django 코드 수정 시 즉시 반영 (Docker 재빌드 불필요)
- 디버거 사용 가능 (PyCharm, VS Code 디버깅)
- 로컬 MySQL 기존 데이터 활용
- 빠른 개발 사이클

### Q3: 언제 dev.yml을 사용하나요?

다음 경우에 dev.yml 사용:
- 새 팀원 온보딩 (빠른 환경 구축)
- 프로덕션 환경 테스트
- CI/CD 파이프라인
- 완전히 독립된 환경 필요

### Q4: 두 구성 간 데이터 공유는?

**안됩니다.** 볼륨 이름이 다르므로 데이터가 분리됩니다:
- infra.yml: `neuronova_*_data`
- dev.yml: `neuronova_*_data`

전환 시 데이터 마이그레이션이 필요합니다.

### Q5: 포트 충돌 해결?

```bash
# .env 파일에서 포트 변경
REDIS_HOST_PORT=6380  # 6379 대신
ORTHANC_HOST_PORT_HTTP=8043  # 8042 대신
```

---

## 📚 관련 문서

- **빠른 시작**: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - dev.yml 전체 스택 시작
- **아키텍처**: [DOCKER_ARCHITECTURE.md](DOCKER_ARCHITECTURE.md) - Docker 설계 상세
- **개발 가이드**: [DOCKER_DEV_GUIDE.md](DOCKER_DEV_GUIDE.md) - 개발 워크플로우
- **시스템 아키텍처**: [01_doc/06_시스템_아키텍처_v2.md](01_doc/06_시스템_아키텍처_v2.md)

---

**마지막 업데이트**: 2025-12-30
**버전**: v2.1
