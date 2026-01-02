# NeuroNova CDSS - Clinical Decision Support System

**Version**: v2.1
**Architecture**: Microservices (Secure Proxy Pattern + Multi-SPA)
**Status**: Week 7 완료 - Phase 2 배포 준비 완료

---

## 🏥 프로젝트 소개

NeuroNova CDSS는 **뇌 MRI 영상 분석**을 위한 임상의사결정지원시스템입니다.
HTJ2K 기반 초고속 DICOM 뷰어와 AI 기반 병변 탐지 기능을 제공합니다.

### 핵심 기능

- ✅ **9개 Use Case 구현 완료** (UC01-UC09)
- ✅ **Secure Proxy Pattern**: Django JWT 인증 + Nginx X-Accel-Redirect
- ✅ **HTJ2K Pipeline**: 고속 의료 영상 처리
- ✅ **Multi-SPA**: React Main + Custom OHIF Viewer 분리
- ✅ **AI 분석**: Brain Tumor/Metastasis Segmentation
- ✅ **FHIR R4 통합**: 의료 데이터 표준 준수

---

## 🚀 빠른 시작 (Docker)

### 📌 2가지 실행 방법

NeuroNova는 **개발 환경**과 **완전한 Docker 환경** 2가지 방식을 지원합니다:

#### 방법 1: 개발 환경 (권장 - Django/MySQL 로컬 실행) ⭐

**사용 상황**: Django 개발 중, 로컬 MySQL 사용

```bash
# 1. 저장소 클론
git clone <repository-url>
cd NeuroNova_v1

# 2. 환경변수 설정
cp .env.example .env
# .env 파일 수정: DB_HOST=localhost

# 3. Docker 네트워크 생성
docker network create neuronova_network

# 4. 인프라만 실행 (Redis, Orthanc, OpenEMR, FHIR)
docker compose -f docker-compose.infra.yml up -d

# 5. Django 로컬 실행
cd NeuroNova_02_back_end/02_django_server
python manage.py runserver
```

**접속**:
- Django: http://localhost:8000/
- Orthanc: http://localhost:8042/
- OpenEMR: http://localhost:8081/

#### 방법 2: 완전한 Docker 환경 (새 PC, 배포 테스트)

**사용 상황**: 전체 서비스를 Docker로 실행

```bash
# 1-3. 위와 동일

# 4. 전체 스택 실행
docker compose -f docker-compose.dev.yml up -d --build

# 5. Django 초기 설정
docker compose -f docker-compose.dev.yml exec django python manage.py migrate
docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser
```

**접속**:
- Django API: http://localhost/api/
- Django Admin: http://localhost/admin/
- API Swagger: http://localhost/api/docs/

### 📚 상세 가이드

- **Docker 사용법**: [DOCKER_USAGE_GUIDE.md](DOCKER_USAGE_GUIDE.md) - 2가지 방법 비교
- **빠른 시작**: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - 전체 스택 가이드
- **개발 가이드**: [DOCKER_DEV_GUIDE.md](DOCKER_DEV_GUIDE.md)

---

## 📁 프로젝트 구조

```
NeuroNova_v1/
├── 01_doc/                          # 📚 문서 (44개)
│   ├── REF_CLAUDE_ONBOARDING_QUICK.md  # 빠른 온보딩 (5분)
│   ├── 06_시스템_아키텍처_v2.md          # 아키텍처 v2.1
│   ├── 12_GCP_배포_가이드.md             # 배포 가이드
│   └── LOG_작업이력.md                   # Week 1-7 작업 이력
│
├── NeuroNova_02_back_end/           # 🔧 백엔드
│   ├── 02_django_server/            # Django REST API
│   ├── 03_openemr_server/           # OpenEMR
│   ├── 04_ohif_viewer/              # Custom OHIF v3
│   ├── 05_orthanc_pacs/             # Orthanc PACS
│   ├── 06_hapi_fhir/                # HAPI FHIR Server
│   └── 07_redis/                    # Redis
│
├── NeuroNova_03_front_end_react/    # 🎨 프론트엔드
│   └── 00_test_client/              # React Main SPA
│
├── docker-compose.dev.yml           # 🐳 개발용 Docker 구성
├── nginx/                           # 🌐 Nginx 설정 (v2.1)
│   ├── nginx.dev.conf
│   └── conf.d/neuronova.conf
│
├── static/                          # 정적 파일 (빌드 후)
│   ├── react-main/                  # React 빌드 결과물
│   └── ohif-dist/                   # OHIF 빌드 결과물
│
├── .env.example                     # 환경변수 예제
├── DOCKER_DEV_GUIDE.md              # Docker 개발 가이드
└── README.md                        # 이 파일
```

---

## 🏗️ 아키텍처 v2.1

```
Internet (User)
   ↓
Cloudflare (HTTPS/WAF)
   ↓
┌─────────────────────────────────────────┐
│  Nginx Gateway (Port 80)                │
│  - /          → React Main SPA          │
│  - /api/*     → Django API              │
│  - /pacs-viewer/ → OHIF Viewer          │
│  - /internal-orthanc/* → Orthanc (내부) │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  Django + Celery                        │
│  - JWT Authentication                   │
│  - Business Logic                       │
│  - Async Processing (HTJ2K 변환)        │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  Data Layer (Internal Only)             │
│  - MySQL (CDSS DB)                      │
│  - Redis (Cache/Broker)                 │
│  - Orthanc (PACS - HTJ2K)               │
│  - OpenEMR / HAPI FHIR                  │
└─────────────────────────────────────────┘
```

**핵심 특징**:
- **Secure Proxy**: Orthanc 직접 접속 차단, Django → Nginx → Orthanc 위임
- **Multi-SPA**: 독립 빌드로 의존성 충돌 방지
- **HTJ2K**: 웹 브라우저 고속 DICOM 렌더링

---

## 📖 문서

### 필수 문서 (시작 전 꼭 읽기)

1. **[REF_CLAUDE_ONBOARDING_QUICK.md](01_doc/REF_CLAUDE_ONBOARDING_QUICK.md)** - 5분 빠른 온보딩
2. **[DOCKER_USAGE_GUIDE.md](DOCKER_USAGE_GUIDE.md)** ⭐ - Docker 2가지 사용법
3. **[DATA_INITIALIZATION_GUIDE.md](DATA_INITIALIZATION_GUIDE.md)** ⭐ - 데이터 초기화 (재설치 후)
4. **[06_시스템_아키텍처_v2.md](01_doc/06_시스템_아키텍처_v2.md)** - v2.1 아키텍처 상세
5. **[LOG_작업이력.md](01_doc/LOG_작업이력.md)** - Week 1-7 작업 완료 내역

### 전체 문서 목록

**[01_doc/README.md](01_doc/README.md)** - 44개 문서 전체 목록 및 분류

---

## 🛠️ 기술 스택

### Backend
- **Django REST Framework** 4.2.x - Main API
- **Celery** 5.3.x - 비동기 작업 (HTJ2K 변환, AI)
- **FastAPI** 0.100.x - AI Inference Server
- **MySQL** 8.0 - Main Database
- **Redis** 7.x - Cache & Message Broker

### Frontend
- **React** 18.x - Main Dashboard
- **OHIF Viewer** v3.9.2 - Custom DICOM Viewer
- **HTJ2K WASM Decoder** - 고속 이미지 디코딩

### Infrastructure
- **Nginx** - Reverse Proxy (X-Accel-Redirect)
- **Docker** - Container Orchestration
- **Cloudflare** - HTTPS/WAF/DDoS Protection

### Medical Standards
- **Orthanc** - DICOM PACS Server
- **OpenEMR** 7.0.3 - Electronic Medical Records
- **HAPI FHIR** R4 - FHIR Server
- **DICOM** - Medical Imaging Standard
- **HL7 FHIR** R4 - Healthcare Interoperability

### AI/ML
- **MONAI** - Medical Imaging AI Framework
- **PyTorch** - Deep Learning
- **pydicom** - DICOM Processing

---

## 📊 개발 현황

### ✅ 완료된 항목

- [x] **Week 1-3**: Core Infrastructure (Django, MySQL, Redis, Celery)
- [x] **Week 4**: PACS Integration (Orthanc, HTJ2K Pipeline)
- [x] **Week 5**: EMR Integration (OpenEMR, FHIR)
- [x] **Week 6**: AI Module (Brain Tumor/Metastasis Detection)
- [x] **Week 7**: Phase 1 & 2 완료
  - [x] Error Handling, Swagger, Data Validation
  - [x] Architecture v2.1 (Secure Proxy, Multi-SPA)
  - [x] GCP 배포 준비
  - [x] 전체 문서 재구성 (44개)

### 🎯 Use Case 구현 현황 (9/9 완료)

| UC | 이름 | 상태 | 설명 |
|----|------|------|------|
| UC01 | 인증/인가 | ✅ | JWT 기반 7-Role RBAC |
| UC02 | EMR 연동 | ✅ | OpenEMR 환자 정보 동기화 |
| UC03 | OCS 처방 | ✅ | 처방 생성/조회 |
| UC04 | LIS 검사 | ✅ | 검사 결과 관리 |
| UC05 | RIS/PACS | ✅ | DICOM 업로드/조회/HTJ2K |
| UC06 | AI 분석 | ✅ | Brain Tumor 탐지 |
| UC07 | 알림 | ✅ | Critical Finding Alert |
| UC08 | FHIR 통합 | ✅ | HL7 FHIR R4 |
| UC09 | 감사 로그 | ✅ | Audit Trail |

---

## 🔧 개발 워크플로우

### Django API 개발

```bash
# 1. 소스 코드 수정 (Hot Reload 자동)
# NeuroNova_02_back_end/02_django_server/apps/*/

# 2. 마이그레이션
docker compose -f docker-compose.dev.yml exec django python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec django python manage.py migrate

# 3. 테스트
docker compose -f docker-compose.dev.yml exec django python manage.py test

# 4. API 문서 확인
# http://localhost/api/swagger/
```

### Frontend 개발

```bash
# React Main App
cd NeuroNova_03_front_end_react/00_test_client
npm install
npm start  # 개발 서버 (http://localhost:3001)
npm run build  # 프로덕션 빌드

# OHIF Viewer
cd NeuroNova_02_back_end/04_ohif_viewer
yarn install
yarn start  # 개발 서버
yarn build  # 프로덕션 빌드
```

---

## 🐛 트러블슈팅

### 포트 충돌

```bash
# 사용 중인 포트 확인
netstat -ano | findstr :8000  # Windows
lsof -i :8000                # Linux/Mac

# .env 파일에서 포트 변경
```

### DB 연결 실패

```bash
# MySQL 상태 확인
docker compose -f docker-compose.dev.yml exec cdss-mysql mysqladmin ping

# 로그 확인
docker compose -f docker-compose.dev.yml logs cdss-mysql
```

### Nginx 502 Error

```bash
# Django 컨테이너 상태 확인
docker compose -f docker-compose.dev.yml ps django

# Django 재시작
docker compose -f docker-compose.dev.yml restart django
```

**상세 가이드**: [DOCKER_DEV_GUIDE.md#트러블슈팅](DOCKER_DEV_GUIDE.md#트러블슈팅)

---

## 📝 라이선스

이 프로젝트는 포트폴리오 및 학습 목적으로 개발되었습니다.

---

## 👥 팀

**NeuroNova Development Team**

- Architecture v2.1 설계
- Full-Stack Development
- Medical Imaging Integration

---

## 📮 문의

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**Last Updated**: 2025-12-30
**Version**: v2.1 - Secure Proxy Pattern + Multi-SPA
