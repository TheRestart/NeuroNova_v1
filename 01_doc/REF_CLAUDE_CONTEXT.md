# CDSS UML 프로젝트 - Claude 컨텍스트 문서

> **목적**: 이 문서는 Claude AI가 프로젝트를 빠르게 이해하고 작업을 이어서 수행할 수 있도록 작성되었습니다.

**문서 작성일**: 2025-12-16
**최종 업데이트**: 2025-12-30 (Phase 2 완료, GCP 배포 준비 완료)
**프로젝트 위치**:
- **원본 PC**: `d:\1222\NeuroNova_v1` (기본)
- **임시 PC**: `c:\Users\gksqu\Downloads\git_hub\NeuroNova_v1` (현재, 데이터 일부 누락)
**프로젝트 타입**: 임상 의사결정 지원 시스템(CDSS) - HTJ2K 기반 고성능 의료 영상 아키텍처 v2.1
**최신 변경**:
- Phase 2 완료: 테스트 전략, 로깅 전략, 성능 최적화 문서화
- GCP 배포 가이드 완성 (12_GCP_배포_가이드.md)
- 아키텍처 v2.1: Secure Proxy Pattern, Multi-SPA 빌드 전략
- 문서 재구성 완료 (50개 → 44개)

---

## ⚡ 중요: 프로젝트 R&R (역할 분담)

### 현재 담당자(User)의 역할: Django Backend API 개발

**책임 범위:**
- ✅ Django Backend API 개발 (핵심)
- ✅ API 문서 작성 (Swagger/OpenAPI)
- ✅ 데이터 무결성 정책 구현
- ✅ 에러 핸들링 표준화
- ✅ 테스트 전략 수립

**제외 사항 (타 팀원 담당):**
- ❌ Frontend (React) - 타 팀원
- ❌ AI 코어 모델 개발 - 타 팀원
- ❌ 보안 작업 (우선순위 낮음 - 개발 중 오작동 우려)

**작업 우선순위:**
1. API 문서화 (Swagger)
2. 에러 핸들링 표준화
3. 데이터 검증 정책 구현
4. 테스트 전략
5. 로깅 및 성능 최적화

**관련 문서:**
- [25_에러_핸들링_가이드.md](25_에러_핸들링_가이드.md)
- [26_API_자동문서화_가이드.md](26_API_자동문서화_가이드.md)
- [27_데이터_검증_정책.md](27_데이터_검증_정책.md)

---

## 1. 프로젝트 개요

### 1.1 시스템 설명
- **시스템명**: CDSS (Clinical Decision Support System)
- **아키텍처**: Django 기반 마이크로서비스 + 외부 시스템 통합
- **설계 방법론**: UML 기반 상세 설계
- **주요 통합 시스템**:
  - OpenEMR (전자의무기록)
  - Orthanc (DICOM 서버)
  - HAPI FHIR (의료정보 교환)
  - AI 모델 서버

### 1.2 Use Case 구성 (9개 모듈)

| UC | 모듈명 | 설명 | 핵심 기능 |
|---|---|---|---|
| UC1 | ACCT | Accounts/Auth | JWT 인증, RBAC 권한, MFA |
| UC2 | EMR | EMR Proxy | OpenEMR 데이터 Pull, 캐싱 |
| UC3 | OCS | Order Communication System | 처방 전달 |
| UC04 | LIS | Lab Information System | 임상병리 검사 결과 및 이상치 알림 | ✅ 완료 |
| UC05 | RIS | Radiology Information System | 영상 검사 오더, DICOM 연동 (OHIF Proxy) | ✅ 완료 |
| UC06 | AI | AI Orchestration | AI 모델 호출, 결과 관리, 검토 프로세스 | ✅ 완료 |
| UC07 | ALERT | Timeline/Alert Core | 이벤트 타임라인, 실시간 알림 (Channels) | ✅ 완료 |
| UC08 | FHIR | FHIR Gateway | HAPI FHIR 연동 및 리소스 변환 | ✅ 완료 |
| UC09 | AUDIT | Audit/Admin | 전수 감사 로그 및 로그 뷰어 | ✅ 완료 |

---

## 2. 디렉토리 구조 및 파일 맵

```
c:\Users\gksqu\Downloads\git_hub\NeuroNova_v1/
├── 00_UML/                          # UML 설계 파일 (PlantUML)
├── 01_doc/                          # 📚 모든 문서 (44개)
│   ├── REF_CLAUDE_ONBOARDING_QUICK.md # 🔥 빠른 온보딩 (이 문서)
│   ├── REF_CLAUDE_CONTEXT.md        # 🔥 상세 참조 (1300줄+)
│   ├── LOG_작업이력.md               # 🔥 Week 1~7 작업 기록
│   ├── 00_업무계획서.md              # 전체 계획
│   ├── 08_API_명세서.md              # API 명세
│   ├── 12_GCP_배포_가이드.md          # 🆕 GCP VM + Docker 배포
│   ├── 25_에러_핸들링_가이드.md      # 에러 응답 표준
│   ├── 26_API_자동문서화_가이드.md   # Swagger 설정
│   ├── 27_데이터_검증_정책.md        # 데이터 검증 규칙
│   ├── 28_테스트_전략_가이드.md      # 테스트 전략
│   ├── 29_로깅_전략_문서.md          # 로깅 전략
│   ├── 30_성능_최적화_가이드.md      # 성능 최적화
│   └── ... (기타 31개 문서)
├── NeuroNova_02_back_end/
│   ├── 01_ai_core/                  # AI 코어 모듈 (FastAPI)
│   ├── 02_django_server/            # 🔥 Django 프로젝트 루트
│   │   ├── cdss_backend/            # Django 설정
│   │   ├── acct/                    # UC01: 인증/권한
│   │   ├── emr/                     # UC02: EMR (OpenEMR 연동)
│   │   ├── ocs/                     # UC03: 처방 (Order)
│   │   ├── lis/                     # UC04: 검사
│   │   ├── ris/                     # UC05: 영상 (Orthanc)
│   │   ├── ai/                      # UC06: AI Job
│   │   ├── alert/                   # UC07: 알림
│   │   ├── fhir/                    # UC08: FHIR
│   │   ├── audit/                   # UC09: 감사 로그
│   │   └── utils/                   # 공통 유틸리티
│   ├── 03_openemr_server/           # OpenEMR Docker 설정
│   ├── 04_ohif_viewer/              # OHIF Viewer Docker 설정
│   ├── 05_orthanc_pacs/             # Orthanc PACS Docker 설정
│   ├── 06_hapi_fhir/                # HAPI FHIR Server Docker 설정
│   └── 07_redis/                    # Redis Docker 설정
├── NeuroNova_03_front_end_react/
│   └── 00_test_client/              # 🆕 임시 API 테스트 클라이언트
└── NeuroNova_04_front_end_flutter/  # Flutter 모바일 앱 (타 팀원)
```

---

## 3. 개발 품질 관리 정책 (2025-12-28 추가)

### 3.1 에러 핸들링 전략

**표준 에러 응답 형식** ([25_에러_핸들링_가이드.md](25_에러_핸들링_가이드.md) 참조):
```json
{
  "error": {
    "code": "ERR_XXX",
    "message": "사용자 친화적 에러 메시지",
    "detail": "개발자용 상세 정보 (선택)",
    "field": "field_name (유효성 검증 실패 시)",
    "timestamp": "2025-12-28T10:30:00Z"
  }
}
```

**에러 코드 체계**:
- `ERR_001~099`: 인증/권한
- `ERR_101~199`: 유효성 검증
- `ERR_201~299`: 리소스 없음
- `ERR_301~399`: 충돌/락킹
- `ERR_401~499`: 비즈니스 로직
- `ERR_501~599`: 외부 시스템
- `ERR_500`: 서버 내부 오류

**구현 방법**:
- 커스텀 Exception 클래스 (`utils/exceptions.py`)
- 커스텀 Exception Handler (`utils/exception_handlers.py`)
- DRF 설정: `EXCEPTION_HANDLER = 'utils.exception_handlers.custom_exception_handler'`

### 3.2 API 자동문서화

**도구**: drf-spectacular (OpenAPI 3.0)

**접속 URL**:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

**문서화 방법** ([26_API_자동문서화_가이드.md](26_API_자동문서화_가이드.md) 참조):
```python
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="환자 목록 조회",
        description="등록된 모든 환자의 목록을 조회합니다.",
        tags=['emr'],
        responses={200: PatientSerializer(many=True)}
    )
)
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
```

**프론트엔드 협업**:
- OpenAPI Schema Export: `python manage.py spectacular --file schema.json`
- TypeScript 타입 자동 생성: `npx openapi-typescript schema.json --output api.d.ts`
- Postman Collection Export 지원

### 3.3 데이터 검증 정책

**검증 계층** ([27_데이터_검증_정책.md](27_데이터_검증_정책.md) 참조):

```
1. Serializer 검증 (형식, 타입, 필수값)
   ↓
2. 커스텀 필드 검증 (validate_<field_name>)
   ↓
3. 객체 수준 검증 (validate() - 다중 필드 관계)
   ↓
4. 비즈니스 로직 검증 (Service Layer)
```

**주요 원칙**:
- **Defensive Programming**: "절대 사용자 입력을 신뢰하지 마라"
- **Fail Fast**: 잘못된 데이터는 가능한 빨리 거부
- **검증 vs 변환**: 변환은 최소화하고, 검증을 우선시

**데이터 무결성 보장**:
- DB Constraints (UNIQUE, CHECK, FK)
- Transaction 관리 (`@transaction.atomic`)
- 낙관적/비관적 락킹 (동시성 제어)
- 병렬 데이터 전달 무결성 (Parallel Dual-Write)

**외부 시스템 연동 검증**:
- HTTP 상태 코드 검증
- 응답 데이터 형식 검증 (JSON 파싱)
- 필수 필드 존재 여부 확인
- 타임아웃 설정 (OpenEMR: 10초, Orthanc: 60초)

### 3.4 로깅 및 모니터링 (Phase 2)
- **표준화된 로깅**: `logs/` 디렉토리에 `app.log`, `access.log`, `error.log` 분할 관리.
- **액세스 로그**: `AccessLogMiddleware`를 통해 모든 요청의 IP, 유저, 수행 시간 기록.
- **개인정보 마스킹**: SSN, 전화번호, 이메일 등 민감 정보 자동 마스킹 (`utils/logging.py`).
- **테스트 환경**: `pytest-django`, `pytest-cov` 기반의 유닛/통합 테스트 체계 구축.

### 3.5 성능 최적화 정책 (Phase 2)
- **캐싱**: Redis 기반의 API 결과 캐싱 (`django-redis`).
- **ORM 최적화**: `select_related` 및 `prefetch_related` 필수 적용으로 N+1 문제 원천 차단.
- **비동기 처리**: AI 분석 등 무거운 작업은 RabbitMQ/Celery 연동.

---

## 4. 아키텍처 패턴 (v2.1 - Microservices for Medical CDSS & PACS)

**시스템 타입**: Microservices Architecture
**Gateway**: Nginx (Reverse Proxy with X-Accel-Redirect) behind Cloudflare
**Main Backend**: Django REST Framework (Secure Proxy & Auth Delegate)
**App Layer**: Multi-SPA (React Main + Custom OHIF Viewer, separated builds)
**AI/Computation**: FastAPI (AI Core), Celery (Image Processing Factory)

### 4.1 아키텍처 다이어그램 (v2.1)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ingress Layer (v2.1)                         │
│  Internet → Cloudflare (HTTPS/WAF) → Nginx :80 (Secure Proxy)  │
│              Routes:                                            │
│              - / → React Main SPA (/var/www/react-main)         │
│              - /api/* → Django :8000 (Smart Proxy)              │
│              - /pacs-viewer/ → Custom OHIF (/var/www/ohif-dist) │
│              - /internal-orthanc/* → Orthanc :8042 (INTERNAL)   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Application Layer (Multi-SPA)                      │
│  ┌──────────────┬──────────────┬─────────────────────────────┐  │
│  │  React Main  │  Django API  │ Custom OHIF (Separate Build)│  │
│  │  (UI)        │  :8000       │ - HTJ2K WASM Decoder        │  │
│  │              │  JWT Auth    │ - AI Result Panel           │  │
│  │              │  Proxy       │ - Django Proxy 경유         │  │
│  └──────────────┴──────────────┴─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Data & Integration Layer                           │
│  ┌─────────┬─────────┬──────────┬─────────────┐                │
│  │  MySQL  │  Redis  │ Orthanc  │ HAPI FHIR/  │                │
│  │  :3306  │  :6379  │  :8042   │  OpenEMR    │                │
│  │  (DB)   │ (Cache) │  (PACS)  │  :8080      │                │
│  │         │ (Broker)│ (HTJ2K)  │  (EMR)      │                │
│  │         │         │**INTERNAL**│**INTERNAL**│                │
│  └─────────┴─────────┴──────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│           AI & Async Processing Layer                           │
│  ┌──────────────────────┬────────────────────────────────────┐  │
│  │  FastAPI (AI Core)   │  Celery Workers (Factory)          │  │
│  │  - HTJ2K Decoding    │  - Raw DICOM → HTJ2K Conversion    │  │
│  │  - AI Inference      │  - AI Trigger                      │  │
│  │                      │  - FHIR Sync                       │  │
│  └──────────────────────┴────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 핵심 워크플로우 (v2.1)

**1. HTJ2K 파이프라인 (속도 최적화)**:
- **Upload**: 사용자 Raw DICOM 업로드 → Django → **Celery (HTJ2K 변환)** → Orthanc 저장
- **Viewing (Secure)**: OHIF Viewer → Django Proxy (JWT 검증) → Nginx (X-Accel-Redirect) → Orthanc (Internal) → **WASM 디코딩** (초고속 로딩)

**2. AI 분석 (비동기)**:
- Celery 트리거 → FastAPI (Orthanc에서 HTJ2K 조회 → pylibjpeg 디코딩 → 추론) → 결과 저장

**3. 데이터 흐름**:
- **User Request**: Internet -> Cloudflare -> Nginx -> Django
- **EMR Sync**: Django/Celery -> HAPI FHIR/OpenEMR (동기/주기)

**동기 vs 비동기**:
- **동기**: Django ↔ MySQL, Redis, Orthanc, HAPI FHIR (HTTP 직접 호출)
- **비동기**: Celery (이미지 변환, AI 추론, 데이터 동기화)

### 4.3 보안 아키텍처 (v2.1 Enhanced)

- **외부 노출**: Nginx만 (React, OHIF, Django API)
- **Secure Proxy**: Django가 JWT 검증 후 X-Accel-Redirect로 Nginx에 전송 위임
- **내부 전용**: Orthanc, MySQL, Redis, HAPI FHIR, OpenEMR (외부 직접 접속 차단)

### 4.4 데이터 조회 및 캐싱 전략 (Fallback)
1. **MySQL (Cache Layer)**: 로컬 DB 우선 조회.
2. **FHIR Server (Standard Layer)**: 상호운용성 서버 조회 및 Write-Back 캐싱.
3. **OpenEMR (Source of Truth)**: 원천 시스템 조회, FHIR 변환 및 동기화.

---

## 4.5 Redis/Celery 아키텍처 (2025-12-29 업데이트)

### 배경 및 의사결정

**문제**: 초기 아키텍처에서는 Django와 Celery를 별도의 Docker 컨테이너로 분리하여 실행했습니다. 이 구조는 다음과 같은 환경 불일치 문제를 발생시켰습니다:

- Docker Celery 컨테이너는 독립적인 Python 환경을 가짐
- Django는 로컬 가상환경(venv)에서 실행
- 코드는 볼륨 마운트로 공유되지만, Python 패키지 환경은 공유되지 않음
- MySQL 연결 시 socket vs TCP 연결 문제 발생
- 종속성 버전 불일치 가능성

**해결 방안**: Django와 Celery를 **동일한 로컬 가상환경(venv)**에서 실행하도록 아키텍처를 변경했습니다. Redis만 Docker 컨테이너로 유지합니다.

### 현재 구성 (개발 환경)

**Docker:**
- **Redis**: Django 캐시 및 Celery 브로커 (포트 6379)
  - 이미지: `redis:7-alpine`
  - 명령어: `redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru`
  - 네트워크: `neuronova_network`

**로컬 가상환경 (d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\venv):**
- **Django Server**: `venv\Scripts\python manage.py runserver`
- **Celery Worker**: `venv\Scripts\celery -A cdss_backend worker -l info --concurrency=4`
- **Celery Beat**: `venv\Scripts\celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- **Flower**: `venv\Scripts\celery -A cdss_backend flower --port=5555` (선택사항)

### 폴더 구조

```
NeuroNova_02_back_end/
├── 02_django_server/           # Django + Celery (로컬 venv)
│   ├── venv/                   # 공유 Python 가상환경
│   ├── manage.py
│   ├── cdss_backend/           # Django 프로젝트 설정
│   │   ├── celery.py           # Celery 설정
│   │   └── settings.py
│   ├── acct/, emr/, ocs/, lis/, ris/, ai/, alert/, fhir/, audit/  # Django 앱
│   └── requirements.txt
│
├── 01_ai_core/                 # AI 코어 모듈 (FastAPI)
├── 03_openemr_server/          # OpenEMR Docker 설정
├── 04_ohif_viewer/             # OHIF Viewer Docker 설정
├── 05_orthanc_pacs/            # Orthanc PACS Docker 설정
├── 06_hapi_fhir/               # HAPI FHIR Server Docker 설정
├── 07_redis/                   # Redis (Docker)
│   ├── docker-compose.yml
│   └── README.md
└── ... (기타 백엔드 서비스)
```

**참고**:
- `07_redis/` 폴더는 이전에 `07_redis_celery/`였으나, Celery가 로컬 venv로 이동하면서 폴더명을 변경했습니다.
- `02_django_server/`는 이전에 `01_django_server/`였으나, 디렉토리 리넘버링으로 변경되었습니다.

### 실행 방법

**원본 PC 경로**: `d:\1222\NeuroNova_v1`
**임시 PC 경로**: `c:\Users\gksqu\Downloads\git_hub\NeuroNova_v1` (현재)

#### 1. Redis 시작 (Docker)

```bash
cd NeuroNova_02_back_end\07_redis
docker-compose up -d
```

#### 2. Django 및 Celery 시작 (로컬 venv)

```bash
cd NeuroNova_02_back_end\02_django_server

# Django 서버 (메인 터미널)
venv\Scripts\python manage.py runserver

# Celery Worker (새 터미널)
venv\Scripts\celery -A cdss_backend worker -l info --concurrency=4

# Celery Beat (새 터미널)
venv\Scripts\celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Flower - 선택사항 (새 터미널)
venv\Scripts\celery -A cdss_backend flower --port=5555
```

### Celery 태스크 기능

1. **AI Job Processing**: AI 분석 요청 큐잉 및 처리
2. **FHIR Sync**: 의료 데이터 표준 변환 및 HAPI FHIR 서버 동기화
3. **Periodic Tasks**: 오래된 데이터 정리, 재시도 로직 실행

### 모니터링

**Celery Flower**를 통해 작업 상태를 모니터링할 수 있습니다:
- URL: http://localhost:5555
- 기능: 태스크 성공/실패 확인, 워커 상태 모니터링, 재시도 관리

### 패키지 버전

```python
# requirements.txt
Django==5.1.6                    # django-celery-beat 호환성 (5.1.x 요구)
redis==4.6.0                     # celery[redis] 호환성 (<5.0.0 요구)
celery[redis]==5.3.4
django-celery-beat==2.7.0        # 동적 스케줄 관리
django-redis==5.4.0              # Django 캐시 백엔드
flower==2.0.1                    # Celery 모니터링
```

**버전 제약 사항**:
- `django-celery-beat 2.7.0`은 Django 5.2 미만 요구 → Django 5.1.6 사용
- `celery[redis] 5.3.4`는 redis<5.0.0 요구 → redis 4.6.0 사용

### 아키텍처 변경 이력

**변경 전 (2025-12-28 이전):**
```
Docker:
- Redis (브로커)
- Celery Worker
- Celery Beat
- Flower

로컬:
- Django Server (venv)
```

**변경 후 (2025-12-29):**
```
Docker:
- Redis (브로커)

로컬 venv:
- Django Server
- Celery Worker
- Celery Beat
- Flower
```

**변경 사유**: Django와 Celery가 동일한 Python 환경을 공유하여 환경 일관성 확보, MySQL 연결 문제 해결, 종속성 버전 충돌 방지.

---

## 5. 기존 설계 패턴 (Layered Architecture)

### 5.1 레이어 아키텍처 (공통)

모든 UC는 동일한 7-Layer 구조를 따릅니다:

```
┌─────────────────────────────────────┐
│  7. Controllers (API Endpoints)     │  ← REST API 진입점
├─────────────────────────────────────┤
│  6. Services (Business Logic)       │  ← 핵심 비즈니스 로직
├─────────────────────────────────────┤
│  5. Repositories (Data Access)      │  ← ORM/DB 추상화
├─────────────────────────────────────┤
│  4. Clients (External Systems)      │  ← 외부 API 호출
├─────────────────────────────────────┤
│  3. DTOs (Data Transfer Objects)    │  ← API 계약
├─────────────────────────────────────┤
│  2. Domain (Entities)                │  ← 도메인 모델
├─────────────────────────────────────┤
│  1. Main (Integration)               │  ← 레이어 간 연결
└─────────────────────────────────────┘
```

**의존성 흐름**: Controller → Service → Repository/Client
**도메인 모델**: 모든 레이어에서 참조 가능

### 4.2 파일 읽기 순서 (UC 분석 시)

1. **`uc0X_01_class_main.puml`** ← 먼저 읽기 (전체 구조 파악)
2. `uc0X_02_domain.puml` (데이터 모델)
3. `uc0X_06_services.puml` (핵심 로직)
4. `uc0X_07_controllers.puml` (API 인터페이스)
5. 나머지 레이어 (필요 시)

---

## 5. UC별 상세 분석

### 5.1 UC01 (ACCT) - 인증/권한 시스템 ✅ 구현 완료

#### 핵심 컴포넌트
```
AuthController (views.py)
  ├─→ AuthService (로그인/로그아웃)
  │     ├─→ UserService (사용자 관리)
  │     ├─→ JWT (djangorestframework-simplejwt)
  │     └─→ Django Auth (비밀번호 검증)
  │
  ├─→ login() - POST /api/acct/login/
  ├─→ logout() - POST /api/acct/logout/
  ├─→ me() - GET /api/acct/me/
  └─→ UserViewSet
        ├─→ register() - POST /api/acct/users/register/
        └─→ CRUD (Admin only)

Permission Classes (permissions.py)
  ├─→ IsAdmin, IsDoctor, IsRIB, IsLab, IsNurse
  ├─→ IsDoctorOrRIB, IsDoctorOrNurse
  ├─→ IsSelfOrAdmin (Patient용)
  └─→ IsAdminOrReadOnly, IsStaffRole
```

**구현 상태:**
- ✅ Custom User 모델 (AUTH_USER_MODEL = 'acct.User')
- ✅ JWT 토큰 인증 (Access + Refresh)
- ✅ 7개 역할 시스템 (admin, doctor, rib, lab, nurse, patient, external)
- ✅ Service 레이어 패턴
- ✅ 10개 Permission 클래스

**회원가입 정책 (2025-12-28 업데이트):**
- **Patient**: 자가 회원가입 가능 (`POST /acct/register/` - AllowAny)
- **의료진** (Doctor, RIB, Lab, Nurse, External): Admin이 계정 생성 후 ID/PW 공지
  - 보안 강화 및 내부 인력 관리 목적
  - Admin 전용 계정 생성 API 사용 (IsAdmin 권한 필요)
- **API**: 모든 역할의 회원가입 API 구현되어 있음 (정책 변경 대비)

#### 도메인 모델 (실제 구현: acct/models.py)
```python
User (AbstractBaseUser, PermissionsMixin)
  - user_id: UUID (PK)
  - username: String (unique)
  - email: EmailField (unique)
  - role: String (choices: admin, doctor, rib, lab, nurse, patient, external)
  - full_name: String
  - department: String
  - license_number: String
  - is_active: Boolean
  - is_staff: Boolean
  - is_superuser: Boolean
  - created_at: DateTime
  - last_login: DateTime

JWT Token (djangorestframework-simplejwt)
  - Access Token: 1시간 (설정 가능)
  - Refresh Token: 7일 (설정 가능)
  - Token Rotation: 활성화
  - Blacklist: 활성화 (로그아웃 시)
```

**UML 설계와의 차이점:**
- ✅ User 모델은 Django AbstractBaseUser 기반으로 단순화
- ✅ Role은 User 모델의 CharField로 구현 (별도 테이블 없음)
- ⏳ Permission은 Django의 기본 Permission 시스템 활용 가능
- ⏳ RefreshToken은 simplejwt의 token_blacklist 앱으로 관리

#### 주요 흐름 (SD-ACCT-01: 로그인 성공)
```
User → UI: ID/PW 입력
UI → AuthController: POST /auth/login
AuthController → AuthService: login()
  AuthService → UserRepository: 사용자 조회
  AuthService → PasswordService: 비밀번호 검증
  AuthService → AccessPolicyService: role/permission 로딩
  AuthService → JwtService: 액세스 토큰 발급
  AuthService → RefreshTokenService: 리프레시 토큰 발급
  AuthService → AuditClient: log_event(LOGIN_SUCCESS)
AuthController → UI: 200 OK (tokens, profile)
```

#### 핵심 설계 의도
- **Stateless JWT**: 세션 없이 JWT로 인증
- **Token Rotation**: 리프레시 토큰 재발급 시 이전 토큰 무효화
- **Login Defense**: 로그인 실패 횟수 추적 → 계정 잠금
- **RBAC**: Role-Based Access Control (역할 기반 권한)

---

### 5.2 UC02 (EMR) - OpenEMR 프록시 ✅ 구현 완료

#### 핵심 컴포넌트 (실제 구현)
```
EMRController (views.py) - OpenEMR 연동 API
  └─→ EMRService (services.py)
        └─→ OpenEMRClient (openemr_client.py) - 외부 API

EMR CRUD ViewSets (viewsets.py) - 내부 CRUD API
  ├─→ PatientCacheViewSet
  │     └─→ PatientService (services.py)
  │           └─→ PatientRepository (repositories.py)
  ├─→ EncounterViewSet
  │     └─→ EncounterService (services.py)
  │           └─→ EncounterRepository (repositories.py)
  ├─→ OrderViewSet
  │     └─→ OrderService (services.py)
  │           └─→ OrderRepository (repositories.py)
  └─→ OrderItemViewSet
        └─→ OrderItemRepository (repositories.py)

Models (models.py)
  ├─→ PatientCache (환자 기본 정보 캐시)
  │     - patient_id: P-YYYY-NNNNNN (PK, 자동 생성)
  │     - family_name, given_name, birth_date, gender
  │     - phone, email, address
  │     - emergency_contact (JSON), allergies (JSON)
  │     - openemr_patient_id (외부 동기화)
  ├─→ Encounter (진료 기록)
  │     - encounter_id: E-YYYY-NNNNNN (PK, 자동 생성)
  │     - patient (FK), doctor_id (FK → acct.User)
  │     - encounter_type, department, chief_complaint
  │     - diagnosis, status, encounter_date
  ├─→ Order (처방 주문)
  │     - order_id: O-YYYY-NNNNNN (PK, 자동 생성)
  │     - patient (FK), encounter (FK, nullable)
  │     - ordered_by (FK → acct.User), order_type, urgency, status
  └─→ OrderItem (처방 항목)
        - item_id: OI-ORDERID-NNN (PK, 자동 생성)
        - order (FK), drug_code, drug_name, dosage, frequency
        - duration, route, instructions
```

**구현 상태:**
- ✅ Service/Repository 레이어 패턴 완성 (3-layer)
- ✅ OpenEMRClient 외부 API 통합
- ✅ MySQL 캐싱 구조
- ✅ OCS (Order Communication System) 모델 포함
- ✅ JSON 필드 활용 (allergies, emergency_contact)
- ✅ DRF ViewSets를 통한 REST API CRUD 엔드포인트 (4개)
- ✅ 자동 ID 생성 정책 (Service 레이어에서 처리)
- ✅ Transaction 보장 (Order + OrderItem 동시 생성)
- ✅ 테스트 UI (emr_crud_test.html) - 예시입력 버튼 포함
- ✅ OrderItem 개별 CRUD 지원 (PATCH, DELETE)
- ✅ Custom User 모델 FK 연결 (doctor_id, ordered_by)
- ✅ **데이터 충돌 방지 전략** (2025-12-24)
  - **낙관적 락**: `version` 필드 기반 동시성 제어 (PatientCache, Encounter, Order, OrderItem)
  - **비관적 락**: `select_for_update()` 기반 로우 잠금 (서비스 레이어 적용)
  - **멱등성 보장**: `IdempotencyMiddleware` (`X-Idempotency-Key` 헤더 기반 응답 캐싱)
  - **DB 격리 수준**: MySQL `READ COMMITTED` 설정으로 성능/정합성 균형 최적화

#### API 엔드포인트

**OpenEMR 연동 API:**
- GET /api/emr/health/ - OpenEMR 연결 상태 확인
- POST /api/emr/auth/ - OpenEMR 인증
- GET /api/emr/openemr/patients/ - OpenEMR 환자 목록
- GET /api/emr/openemr/patients/search/ - OpenEMR 환자 검색
- GET /api/emr/openemr/patients/{id}/ - OpenEMR 환자 상세

**CRUD API (DRF Router):**
- GET /api/emr/patients/ - 환자 목록
- POST /api/emr/patients/ - 환자 생성 (ID 자동 생성)
- GET /api/emr/patients/{id}/ - 환자 상세
- PUT/PATCH /api/emr/patients/{id}/ - 환자 수정
- DELETE /api/emr/patients/{id}/ - 환자 삭제
- GET /api/emr/patients/search/?q={query} - 환자 검색

- GET /api/emr/encounters/ - 진료 기록 목록
- POST /api/emr/encounters/ - 진료 기록 생성 (ID 자동 생성)
- GET /api/emr/encounters/{id}/ - 진료 기록 상세
- PUT/PATCH /api/emr/encounters/{id}/ - 진료 기록 수정
- DELETE /api/emr/encounters/{id}/ - 진료 기록 삭제
- GET /api/emr/encounters/by_patient/?patient_id={id} - 환자별 진료 기록

- GET /api/emr/orders/ - 처방 목록
- POST /api/emr/orders/ - 처방 생성 (ID 자동 생성, 항목 포함)
- GET /api/emr/orders/{id}/ - 처방 상세
- PUT/PATCH /api/emr/orders/{id}/ - 처방 수정
- DELETE /api/emr/orders/{id}/ - 처방 삭제
- POST /api/emr/orders/{id}/execute/ - 처방 실행
- GET /api/emr/orders/by_patient/?patient_id={id} - 환자별 처방 목록

- GET /api/emr/order-items/ - 처방 항목 목록
- POST /api/emr/order-items/ - 처방 항목 생성
- GET /api/emr/order-items/{id}/ - 처방 항목 상세
- PATCH /api/emr/order-items/{id}/ - 처방 항목 수정
- DELETE /api/emr/order-items/{id}/ - 처방 항목 삭제

**테스트 UI:**
- GET /api/emr/comprehensive-test/ - **종합 테스트 대시보드** (⭐ 최신, 추천)
  - 6개 탭: Overview, OpenEMR Integration, Patient CRUD, Encounter CRUD, Order/OCS, Write-Through
  - Write-Through 패턴 테스트 통합
  - 실시간 통계 대시보드
- GET /api/emr/test-dashboard/ - 통합 테스트 대시보드 (순차적 CRUD 시나리오)
- GET /api/emr/test-ui/ - 레거시 OpenEMR 테스트 UI

#### 설계 패턴
- **Pull-Based**: Django가 OpenEMR에서 데이터를 가져옴 (Push 없음)
- **Cache-Aside**: 조회 시 캐시 먼저 확인 → 없으면 EMR에서 Pull → 캐시 저장
- **Parallel Dual-Write**: 데이터 생성/수정 시 OpenEMR DB와 Django DB에 독립적으로 병렬 전달 (2025-12-24 변경)
**설계 철학:**
- **Distributed Persistence**: OpenEMR(원본)과 Django DB(캐시/비즈니스)를 독립적인 저장 시스템으로 취급
- **Parallel Delivery**: 요청이 들어오면 두 시스템에 병렬적으로(Concurrency) 데이터를 전달하여 최신성 동기화
- **High Visibility**: API 응답 시 각 DB(테이블별) 저장 성공 여부를 독립적으로 반환하여 투명성 확보
- **Concurrency Control**: 
  - **Optimistic Locking**: 업데이트 시 `version` 필드 증가 및 필터링
  - **Pessimistic Locking**: `atomic` 트랜잭션 내 `select_for_update` 사용
- **Idempotency**: `X-Idempotency-Key` 헤더 기반 응답 캐싱 및 중복 요청 차단

**데이터 흐름:**
```
사용자 → Django API → [1] OpenEMR DB (Insert) & [2] Django DB (Insert) -- 병렬/독립 전달
                           ↓ 각 DB별 결과 취합 (persistence_status)
                       성공/실패 상태를 포함한 구조화된 응답 반환
```
- **Aggregate View**: 환자 요약 카드 생성 시 여러 소스 집계
  - Radiology Orders (UC5)
  - Lab Results (UC4)
  - AI Results (UC6)
  - Timeline Events (UC7)

#### 주요 흐름 (SD-EMR-01: 환자 검색)
```
Doctor → UI: 이름/ID 입력
UI → EMRController: GET /patients?query=...
EMRController → PatientProxyService:
  PatientProxyService → OpenEMRClient: REST /patients/search
  PatientProxyService → PatientCacheRepository: cache upsert
EMRController → UI: patient list DTO
```

---

### 5.3 UC05 (RIS) - 영상의학 ✅ PACS 인프라 구축 완료 (2025-12-29)

#### 핵심 컴포넌트
```
RadiologyController (ris/views.py)
  └─→ RadiologyService (ris/services.py)
        ├─→ RadiologyOrderRepository (오더 관리)
        ├─→ RadiologyStudyRepository (검사 관리)
        ├─→ OrthancClient (ris/clients/orthanc_client.py) ✅ 구현 완료
        ├─→ AIClient (AI 모델 호출)
        └─→ TimelineClient (이벤트 발행)
```

#### 구현 상태

**PACS 인프라 (2025-12-29 완성)**:
- ✅ **Orthanc PACS 서버**: Docker 기반 구축 (포트 8042, DICOM 포트 4242)
  - DICOM-Web API 활성화 (QIDO-RS, WADO-RS, STOW-RS)
  - 12개 Study, 약 1,860개 DICOM 인스턴스 저장 (Brain MRI)
  - 2명의 환자 데이터 (sub-0004, sub-0005)
- ✅ **OHIF Viewer**: 웹 기반 DICOM 뷰어 (포트 3000)
  - Nginx 리버스 프록시 통한 접근
  - CORS 처리 완료
  - JavaScript 모듈(.mjs) MIME 타입 수정 완료
- ✅ **Nginx 프록시**: CORS, MIME 타입, 라우팅 처리
  - `/pacs/dicom-web/*` → Orthanc PACS 프록시
  - polyfill.io 보안 차단 처리
- ✅ **NIfTI → DICOM 변환**: Python 스크립트 구현
  - `scripts/convert_nifti_to_dicom.py`
  - 3D MRI 볼륨 → 2D 슬라이스 자동 변환
  - 155 슬라이스/Study, 100% 변환 성공률

**Django API (RIS 모듈)**:
- ✅ OrthancClient 구현 (`ris/clients/orthanc_client.py`)
  - `health_check()`: Orthanc 연결 상태 확인
  - `get_studies()`: Study 목록 조회 (페이지네이션)
  - `get_study()`: Study 상세 정보
  - `search_studies()`: DICOM Query/Retrieve
  - `download_dicom_instance()`: DICOM 파일 다운로드
- ✅ RIS ViewSets 구현 (`ris/views.py`)
  - `RadiologyOrderViewSet`: 영상 검사 오더 CRUD
  - `RadiologyStudyViewSet`: DICOM Study 관리
  - `RadiologyReportViewSet`: 판독문 작성 및 서명
- ✅ 테스트 API 엔드포인트
  - `GET /api/ris/test/patients/`: Orthanc 환자 목록 (페이지네이션)
  - `GET /api/ris/test/studies/`: Orthanc Study 목록 (페이지네이션)

**DICOM 데이터 현황**:
```
환자 ID: sub-0004, sub-0005
Study 개수: 각 6개 (총 12개)
Modality: MR (Magnetic Resonance)
시퀀스: T1w, T2w, FLAIR, SWI, ce-T1w 등
슬라이스: 155개/Study
Instance 총계: 약 1,860개
```

**아키텍처**:
```
사용자 브라우저
  ↓ http://localhost:8000
Nginx 리버스 프록시 (포트 8000)
  ↓
Django API Server (포트 8000)
  ├─→ OHIF Viewer (Proxy)
  └─→ Orthanc PACS (REST API)
        ↑ (Flask-Orthanc 연결)
  [Flask AI Server] (서버간 유일한 별도 연결)
```

**문서**:
- ✅ `프로젝트_구성_및_문제_보고서.md`: 시스템 아키텍처 및 문제 해결 가이드
- ✅ `OHIF_문제분석_보고서.md`: OHIF Viewer 문제 분석 및 해결 방안
- ✅ `scripts/README_DICOM_UPLOAD.md`: DICOM 업로드 가이드

**접속 정보**:
- Orthanc Web UI: `http://localhost:8042/app/explorer.html`
- OHIF Viewer: `http://localhost:3000` (Nginx 프록시)
- Django RIS API: `http://localhost:8000/api/ris/`

#### 워크플로우 (14개 Sequence Diagram)
1. **오더 생성** (SD-RIS-01)
2. **DICOM 업로드** (SD-RIS-02) - ✅ Orthanc로 전송 구현
3. **Study 생성** (SD-RIS-03) - ✅ DICOM 메타데이터 파싱 구현
4. **AI 자동 트리거** (SD-RIS-04) - 특정 Modality 시 AI 호출
5. **AI 결과 수신** (SD-RIS-05)
6. **판독문 작성** (SD-RIS-06~08) - ✅ RadiologyReportViewSet 구현
7. **판독문 서명** (SD-RIS-09) - ✅ sign() API 구현
8. **DICOM Viewer** (SD-RIS-10~11) - ✅ OHIF Viewer 구축 (문제 해결 중)
9. **Study 상태 관리** (SD-RIS-12~14)

#### 외부 시스템 통합
- **Orthanc PACS** (v1.12.10): ✅ 구축 완료
  - DICOM-Web 프로토콜 (QIDO-RS, WADO-RS, STOW-RS)
  - REST API (`http://localhost:8042`)
  - Docker Volume 영구 저장
- **OHIF Viewer** (최신): ✅ 구축 완료 (일부 디버깅 필요)
  - Web-based DICOM 뷰어
  - DICOMweb 표준 준수
- **AI Server**: REST API로 모델 호출 (구현 예정)
- **FHIR**: ImagingStudy 리소스로 변환 (구현 예정)

#### 알려진 문제 및 해결 필요사항
1. **OHIF Viewer API 호출 부재**:
   - 원인: `.env` 설정(`ORTHANC_API_URL`)이 Docker 내부 주소(`orthanc:8042`)로 설정되어 Host Django에서 접근 불가
   - 해결: `ORTHANC_API_URL` 및 `FHIR_SERVER_URL`을 `localhost`로 변경하여 Host-Docker 통신 복구 완료 (2025-12-29)

---

### 5.4 UC06 (AI) - AI 오케스트레이션

#### 핵심 컴포넌트
```
AIJobController
  └─→ AIOrchestrationService
        ├─→ AIJobRepository (작업 큐)
        ├─→ AIModelClient (외부 AI 서버)
        ├─→ AIResultRepository (결과 저장)
        └─→ AIPollingService (비동기 폴링)
```

#### 비동기 처리 및 검토 패턴 ✅ 구현 완료
1. **AI Job 제출**: `AIJobService.submit_ai_job` 호출 → RabbitMQ 큐 등록 → `job_id` 반환
2. **AI 서버 처리**: Flask Worker가 큐에서 타스크를 가져와 분석 수행
3. **분석 결과 콜백**: AI 서버가 `POST /api/ai/callback/` 호출 → Django에서 상태를 `COMPLETED`로 업데이트
4. **의료진 알림**: 결과 수신 즉시 `AlertService`가 'doctor' 역할군에게 WebSocket 실시간 알림 발송
5. **의료진 검토**: 의사가 `review()` API를 통해 수동 승인(`APPROVED`) 또는 반려(`REJECTED`) 처리
6. **감사 추적**: 제출, 수신, 검토의 전 과정이 `AuditService`에 의해 기록됨

#### 도메인 모델 (ai/models.py)
```python
AIJob
  - job_id: UUID (PK)
  - study_id: UUID (RIS 연동)
  - status: PENDING, QUEUED, PROCESSING, COMPLETED, FAILED
  - result_data: JSON (AI 분석 원본 결과)
  - review_status: PENDING, APPROVED, REJECTED
  - reviewed_by: FK (acct.User)
  - review_comment: Text (의료진 소견)
```
AI_ARTIFACTS (결과 파일)
  - artifact_id
  - result_id (FK)
  - kind (HEATMAP, SEGMENTATION, RAW)
  - storage_uri (S3/MinIO)
  - checksum
```

---

### 5.5 UC08 (FHIR) - 의료정보 교환 ✅ 구축 완료

#### 핵심 컴포넌트
```
FHIRController
  └─→ FHIRServiceAdapter (HAPI FHIR 연동)
        ├─→ HAPI FHIR Server (Docker, Port 8080)
        └─→ REST API (requests)
```

#### 아키텍처 변경사항 (2025-12-23)
- **HAPI FHIR Server**: 기존 OpenEMR 내장 FHIR 대신, 별도의 HAPI FHIR JPA Server를 구축하여 **메인 FHIR 게이트웨이**로 사용.
- **설정**: `FHIR_SERVER_URL = 'http://localhost:8080/fhir'`

#### 동기화 전략
- **OpenEMR First**: 데이터 생성 시 OpenEMR에 먼저 저장.
- **HAPI Sync**: 9개 리소스(Patient, Encounter, Observation, DiagnosticReport 등) 동기화 및 Celery 기반 재시도 로직 구현 완료.

---

### 5.6 UC09 (AUDIT) - 감사/보안 ✅ 구현 완료

#### 핵심 컴포넌트
- **AuditService (`audit/services.py`)**: 비즈니스 액션 기록을 위한 싱글톤 성격의 서비스.
- **AuditMiddleware (`audit/middleware.py`)**: HTTP 요청/응답 레벨에서의 자동 감사 로깅.
- **AuditLogViewer (UI)**: `/api/audit/viewer/` 환경에서 필터링 기능을 갖춘 관리자 전용 뷰어.

#### 로깅 및 모니터링 대상
- **일반 감사**: LOGIN, LOGOUT, PATIENT_VIEW/EDIT, ORDER_CREATE, REPORT_SIGN
- **AI/PACS**: AI_REQUEST, AI_CALLBACK, AI_REVIEW
- **보안 이벤트**: LOGIN_FAILED, UNAUTHORIZED_ACCESS

#### 모든 UC에서 AuditClient 호출
```python
# 예시: UC01 로그인 시
audit_client.log_event(
    action="LOGIN_SUCCESS",
    actor_user_id=user.user_id,
    ip=request.ip,
    target_type="USER",
    target_id=user.user_id
)
```

---

## 6. 데이터베이스 스키마 (ERD)

### 6.1 CDSS_DB.mmd (메인 DB)

#### 주요 테이블 그룹

**1. Accounts (UC01)**
```
ACCT_USERS
  ├─ ACCT_USER_ROLES ─┤
  │                    │
ACCT_ROLES             │
  ├─ ACCT_ROLE_PERMS ─┤
  │                    │
ACCT_PERMISSIONS       │

ACCT_USERS
  ├─ ACCT_REFRESH_TOKENS
  └─ ACCT_MFA_SECRETS
```

**2. EMR Cache (UC02)**
```
EMR_PATIENT_CACHE
  ├─ EMR_ENCOUNTER_CACHE
  ├─ EMR_ID_MAP (외부 ID 매핑)
  └─ EMR_SYNC_JOBS (동기화 작업)
```

**3. Radiology (UC05)**
```
RADIOLOGY_ORDERS
  ├─ RADIOLOGY_STUDIES
  │    ├─ RADIOLOGY_SERIES
  │    └─ RADIOLOGY_REPORTS
  └─ (환자 FK: cdss_patient_id → EMR_PATIENT_CACHE)
```

**4. AI (UC06)**
```
RADIOLOGY_STUDIES
  └─ AI_JOBS
       ├─ AI_JOB_POLLING
       └─ AI_RESULTS
            └─ AI_ARTIFACTS
```

**5. Timeline & Alerts (UC07) - Implemented**
```
TIMELINE_EVENTS (시스템 이벤트)
  └─ USER_NOTIFICATIONS (Alert 모델 - MySQL)
       ├─ user_id (FK)
       ├─ message, type, metadata
       └─ is_read
```
- **Redis Channel Layer**: 실시간 전송 (WebSocket)

**6. FHIR (UC08)**
```
FHIR_RESOURCE_MAP (CDSS ↔ FHIR 매핑)
  ├─ cdss_ref_type, cdss_ref_id
  └─ fhir_id (HAPI 서버의 리소스 ID)

FHIR_TX_QUEUE (전송 큐)
  - resource_type
  - payload_json
  - status, retry_count
```

**7. Audit (UC09)**
```
AUDIT_LOGS
  └─ actor_user_id (FK: ACCT_USERS)

SECURITY_EVENTS
  └─ actor_user_id (FK: ACCT_USERS)
```

### 6.2 외부 시스템 DB

**OpenEMR_DB.mmd**
- 읽기 전용 (Django는 조회만)
- 주요 테이블: `patient_data`, `form_encounter`, `procedure_order`

**Orthanc_DB.mmd**
- DICOM 메타데이터 저장
- 주요 테이블: `Studies`, `Series`, `Instances`

**HAPI_DB.mmd**
- FHIR 리소스 저장
- 주요 테이블: `HFJ_RESOURCE`, `HFJ_RES_VER`

---

## 7. 파일 형식 및 도구

### 7.1 PlantUML (.puml)
- **사용처**: Usecase, Sequence, Class Diagram
- **미리보기**: VSCode에서 `Alt+D`
- **문법 예시**:
  ```plantuml
  @startuml
  class User {
    +userId: UUID
    +username: String
  }
  User "1" o-- "0..*" UserRole
  @enduml
  ```

### 7.2 Mermaid (.mmd)
- **사용처**: ERD
- **미리보기**: VSCode `Ctrl+Shift+V` 또는 mermaid.live
- **문법 예시**:
  ```mermaid
  erDiagram
    ACCT_USERS ||--o{ ACCT_USER_ROLES : has
    ACCT_USERS {
      string user_id PK
      string username
    }
  ```

### 7.3 StarUML (.mdj)
- **사용처**: 전체 시스템 아키텍처
- **도구**: StarUML 7.0 (독립 실행형 GUI)

---

## 8. 작업 시나리오별 가이드

### 8.1 새로운 UC 추가 시

1. **폴더 생성**:
   ```
   /usecase/UC10-NewModule.puml
   /sequence/10. NEWMODULE/SD-NEWMODULE-01.puml
   /class/10. UC10 (NEWMODULE)/
   ```

2. **Class Diagram 7개 파일 생성**:
   - `uc10_01_class_main.puml` (다른 UC 복사 후 수정)
   - `uc10_02_domain.puml`
   - `uc10_03_dtos.puml`
   - `uc10_04_clients.puml`
   - `uc10_05_repositories.puml`
   - `uc10_06_services.puml`
   - `uc10_07_controllers.puml`

3. **ERD 수정**:
   - `db/CDSS_DB.mmd`에 새 테이블 추가
   - `db/IntegrationERD.mmd`에 관계 추가

### 8.2 기존 UC 수정 시

**예시: UC01에 MFA 기능 추가**

1. **Domain 수정**:
   - `uc01_02_domain.puml`에 `MFASecret` 클래스 추가

2. **Service 추가**:
   - `uc01_06_services.puml`에 `MFAService` 추가

3. **Controller 수정**:
   - `uc01_07_controllers.puml`에 `/mfa/setup` 엔드포인트 추가

4. **Main 연결**:
   - `uc01_01_class_main.puml`에 의존성 추가:
     ```plantuml
     AuthController --> MFAService
     MFAService --> MFASecretRepository
     ```

5. **Sequence 추가**:
   - `sequence/1. ACCT/SD-ACCT-06.puml` 생성 (MFA 설정 흐름)

6. **ERD 수정**:
   - `db/CDSS_DB.mmd`에 `ACCT_MFA_SECRETS` 테이블 확인/수정

### 8.3 API 엔드포인트 추가 시

**예시: 환자 알레르기 조회 API 추가 (UC02)**

1. **DTO 추가**:
   ```plantuml
   # uc02_3_dtos.puml
   class AllergyDTO {
     +allergyId: UUID
     +patientId: UUID
     +allergen: String
     +severity: String
   }
   ```

2. **Service 메서드 추가**:
   ```plantuml
   # uc02_6_services.puml
   class PatientProxyService {
     +getAllergies(patientId: UUID): List<AllergyDTO>
   }
   ```

3. **Controller 엔드포인트 추가**:
   ```plantuml
   # uc02_7_controllers.puml
   class PatientController {
     +GET /patients/{id}/allergies
   }
   ```

4. **Main 연결**:
   ```plantuml
   # uc02_1_class_main.puml
   PatientController --> PatientProxyService
   ```

5. **Sequence 추가**:
   - `SD-EMR-06.puml` 생성 (알레르기 조회 흐름)

### 8.4 외부 시스템 통합 시

**예시: 새로운 AI 모델 서버 추가**

1. **Client 추가**:
   ```plantuml
   # uc06_4_clients.puml
   interface NewAIClient <<Interface>> {
     +submitJob(studyId: UUID): String
     +getResult(jobId: String): AIResultDTO
   }
   ```

2. **Service 수정**:
   ```plantuml
   # uc06_6_services.puml
   AIOrchestrationService --> NewAIClient
   ```

3. **설정 문서 작성**:
   - `/docs/integrations/new-ai-model.md` (연동 가이드)

---

## 9. 중요한 설계 원칙

### 9.1 일관성 유지
- 모든 UC는 **동일한 7-Layer 구조** 사용
- 파일 명명 규칙 엄격히 준수:
  - `uc[번호]_[레이어]_*.puml`
  - `SD-[모듈명]-[번호].puml`

### 9.2 관심사 분리
- **Domain**: 비즈니스 로직 없음 (순수 데이터 구조)
- **Service**: 비즈니스 로직만 (HTTP/DB 직접 접근 금지)
- **Controller**: 요청 파싱 + 응답 직렬화만
- **Repository**: SQL/ORM만 (비즈니스 로직 금지)

### 9.3 외부 시스템 추상화
- 모든 외부 API는 **Client 인터페이스**로 추상화
- 테스트 시 Mock 객체로 교체 가능
- 예: `OpenEMRClient`, `OrthancClient`, `AIClient`

### 9.4 감사 추적
- **모든 중요한 액션**은 `AuditClient.log_event()` 호출
- 개인정보 조회/수정은 필수 로깅

### 9.5 보안
- **JWT**: 짧은 만료 시간 (15분)
- **Refresh Token**: 긴 만료 시간 (7일) + Rotation
- **RBAC**: 최소 권한 원칙
- **Login Defense**: 5회 실패 시 15분 잠금
- **CRUD Reliability**:
  - **Optimistic Locking**: `version` 필드 기반 충돌 감지 (PatientCache, Encounter, Order, OrderItem 적용)
  - **Pessimistic Locking**: 수정 시 `select_for_update()`를 통한 강력한 정합성 보장
  - **Idempotency**: `X-Idempotency-Key` 헤더 기반 중복 요청 방지 미들웨어
  - **Atomicity**: 서비스 레이어 내 `transaction.atomic()`을 통한 원자성 보장

---

## 10. 자주 사용하는 UML 패턴

### 10.1 PlantUML 관계 표기법
```plantuml
' 연관 (Association)
ClassA --> ClassB

' 의존 (Dependency)
ClassA ..> ClassB

' 집합 (Aggregation)
ClassA o-- ClassB

' 합성 (Composition)
ClassA *-- ClassB

' 상속 (Inheritance)
ClassA --|> ClassB

' 구현 (Realization)
ClassA ..|> InterfaceB

' 다중성
ClassA "1" --> "0..*" ClassB
```

### 10.2 Sequence Diagram 패턴
```plantuml
' 그룹
group 로그인 인증
  actor -> controller: request
end group

' 조건
alt 성공
  service -> db: insert
else 실패
  service -> log: error
end

' 반복
loop 3회 재시도
  client -> api: request
end
```

---

## 10. 트러블슈팅

### 10.1 PlantUML 미리보기 안 됨
- Java JRE 설치 확인
- VSCode PlantUML 확장 설치 확인
- 파일 인코딩 UTF-8 확인

### 10.2 !include 경로 오류
- `uc0X_01_class_main.puml`과 다른 파일이 **같은 디렉토리**에 있어야 함
- 상대 경로 사용: `!include uc01_02_domain.puml`

### 10.3 Mermaid 렌더링 실패
- Mermaid Preview 확장 설치
- 또는 https://mermaid.live 사용

### 10.4 다이어그램이 너무 복잡함
- `hide empty members` 사용 (빈 클래스 숨김)
- `left to right direction` 사용 (가로 배치)
- 개별 레이어 파일만 열어보기

---

## 11. 다음 작업 시 체크리스트

새로운 Claude 인스턴스가 작업을 시작할 때:

- [ ] `이용법.md` 읽기 (사용자 관점)
- [ ] `CLAUDE_CONTEXT.md` 읽기 (이 문서)
- [ ] 작업 대상 UC의 `uc0X_01_class_main.puml` 읽기
- [ ] 관련 Sequence Diagram 읽기
- [ ] `db/CDSS_DB.mmd` 또는 `IntegrationERD.mmd` 읽기
- [ ] 기존 패턴 준수하며 작업 수행
- [ ] 수정 후 관련된 3개 다이어그램(Usecase, Sequence, Class) 일관성 확인

---

## 12. 추가 참고 자료

### 12.1 외부 문서 (프로젝트에 없음 - 필요 시 참고)
- PlantUML 공식 문서: https://plantuml.com/ko/
- Mermaid 공식 문서: https://mermaid.js.org/
- Django REST Framework: https://www.django-rest-framework.org/
- FHIR R4 Spec: https://hl7.org/fhir/R4/

### 12.2 주요 용어 사전
- **CDSS**: Clinical Decision Support System (임상 의사결정 지원 시스템)
- **EMR**: Electronic Medical Record (전자의무기록)
- **RIS**: Radiology Information System (영상의학정보시스템)
- **LIS**: Laboratory Information System (임상병리정보시스템)
- **OCS**: Order Communication System (처방전달시스템)
- **FHIR**: Fast Healthcare Interoperability Resources (의료정보 교환 표준)
- **DICOM**: Digital Imaging and Communications in Medicine (의료영상 표준)
- **JWT**: JSON Web Token (인증 토큰)
- **RBAC**: Role-Based Access Control (역할 기반 접근 제어)

---

## 13. 업무 계획서

### 13.1 업무계획서.md
프로젝트 개발을 위한 상세 업무 계획서가 작성되었습니다.
- **파일 위치**: `업무계획서.md`
- **작성일**: 2025-12-19

### 13.2 주요 내용
**기술 스택별 업무 분류**
- Frontend - React Web (의료진용 데스크톱)
- Frontend - Flutter Mobile (모바일 앱)
- Backend - Django REST API (9개 UC 모듈)
- Database - MySQL/MariaDB
- 외부 시스템 통합 (OpenEMR, Orthanc, HAPI FHIR)

**상용 서버 확인 사항 (중요)**

OpenEMR, Orthanc, HAPI FHIR는 외부 상용 서버를 사용합니다.
개발 시작 전 반드시 확인해야 할 사항:

1. **OpenEMR (전자의무기록)**
   - API 엔드포인트 URL 및 인증 정보
   - 읽기 전용 DB 계정 (선택)
   - IP Whitelist 등록
   - 환자 ID 체계 및 데이터 규격

2. **Orthanc (DICOM 서버)**
   - DICOMweb API URL 및 인증
   - DICOM AE Title 설정
   - 지원 Modality 목록 확인
   - DICOM 태그 구조

3. **HAPI FHIR (의료정보 교환)**
   - FHIR Server URL 및 버전 (R4 권장)
   - OAuth 2.0 인증 정보
   - 지원 리소스 타입 확인
   - Subscription/Webhook 설정

**팀 구성**
- Frontend Team: 3-4명
- Backend Team: 4-5명
- Database Team: 1-2명
- Integration Team: 2명
- QA/Test Team: 2명

**개발 일정**
- Phase 1: 기반 구축 (Week 1-4)
- Phase 2: 핵심 기능 개발 (Week 5-10)
- Phase 3: 고급 기능 및 통합 (Week 11-14)
- Phase 4: 최적화 및 배포 준비 (Week 15-16)

---

## 변경 이력

| 날짜 | 작성자 | 변경 내용 |
|---|---|---|
| 2025-12-16 | Claude (초기 인스턴스) | 문서 최초 작성 |
| 2025-12-19 | Claude | 업무계획서 작성 및 CLAUDE_CONTEXT.md 업데이트<br>- 기술 스택별 업무 분류 추가<br>- 상용 서버 확인 사항 정리<br>- 팀 구성 및 개발 일정 추가 |
| 2025-12-23 (오전) | Claude | 프로젝트 현황 반영 업데이트<br>- UC01 (ACCT) 구현 완료 반영<br>- UC02 (EMR) Service/Repository 레이어 구조 추가<br>- Custom User 모델 적용 상태 업데이트<br>- MySQL 데이터베이스 전환 완료 반영 |
| 2025-12-23 (오후) | Claude | EMR CRUD 기능 완성 업데이트<br>- EMR CRUD ViewSets 전체 구현 완료<br>- Patient/Encounter/Order 자동 ID 생성 정책 추가<br>- DRF Router 기반 REST API 엔드포인트 전체 구성<br>- Service/Repository 3-layer 패턴 완성<br>- 테스트 UI (emr_crud_test.html) 구현<br>- 테스트 사용자 7개 역할 생성<br>- Transaction 보장 로직 추가 |
| 2025-12-23 (저녁) | Claude | 프로젝트 전체 검토 및 문서 업데이트<br>- OrderItem 개별 CRUD API 추가 (ViewSet 구현)<br>- Custom User FK 연결 확인 (doctor_id, ordered_by)<br>- 테스트 대시보드 추가 (통합 테스트 UI)<br>- REF_CLAUDE_CONTEXT.md 최신화<br>- LOG_작업이력.md 최신화 |
| 2025-12-23 (심야) | Claude | Write-Through 패턴 구현 및 종합 테스트 대시보드 완성<br>- FHIR Service Adapter 구현 (fhir_adapter.py)<br>- PatientCacheViewSet에 Write-Through 패턴 적용<br>- Write-Through 패턴 유닛 테스트 완료 (7개 테스트 Pass)<br>- 16_Write_Through_패턴_가이드.md 문서 작성<br>- 종합 테스트 대시보드 구현 (comprehensive_test.html)<br>- 6개 탭 통합 테스트 UI 완성<br>- 15_테스트_페이지_가이드.md 업데이트<br>- REF_CLAUDE_CONTEXT.md 설계 패턴 추가 |
| 2025-12-24 (오전) | Claude | 프로젝트 현황 재검토 및 문서 최신화<br>- 실제 프로젝트 위치 확인 (d:\1222\NeuroNova_v1)<br>- 현재 구현 상태 정확히 반영<br>- 테스트 파일 위치 업데이트 (templates/emr/comprehensive_test.html)<br>- FHIR Adapter 구현 상태 확인<br>- Write-Through 패턴 적용 확인 |
| 2025-12-24 (오후) | Claude | AI 코어 개발 R&R 정의 및 문서 작성<br>- 17_프로젝트_RR_역할분담.md 생성<br>- 18_AI_개발_가이드.md 생성<br>- Interface Specification 템플릿 생성<br>- AI 개발자 역할 명확화 (Backend/Frontend 제외)<br>- 독립 모듈 개발 전략 수립 |
| 2025-12-28 | Claude | API 품질 관리 문서 추가 및 REF_CLAUDE_CONTEXT.md 업데이트<br>- **섹션 3 추가**: 개발 품질 관리 정책 (에러 핸들링, API 자동문서화, 데이터 검증)<br>- 25_에러_핸들링_가이드.md 생성 (표준 에러 응답 형식, 에러 코드 체계)<br>- 26_API_자동문서화_가이드.md 생성 (drf-spectacular, Swagger UI, TypeScript 타입 생성)<br>- 27_데이터_검증_정책.md 생성 (4단계 검증 계층, 데이터 무결성 보장)<br>- 섹션 번호 재조정 (기존 3~9 → 4~10)<br>- README.md 업데이트 (API 품질 관리 문서 추가) |
| 2025-12-29 | Claude | **아키텍처 오해 수정**: Nginx → Django 단일 연결 및 Django 허브 구조 반영<br>- Orthanc/OHIF 직접 연결 가이드 삭제<br>- Flask AI-Orthanc 유일한 서버간 연결 명시 |
| 2025-12-30 | Claude | **Phase 2 완료 및 아키텍처 v2.1 업데이트**<br>- **프로젝트 위치 업데이트**: 원본 PC(`d:\1222\NeuroNova_v1`) + 임시 PC(`c:\Users\gksqu\Downloads\git_hub\NeuroNova_v1`) 명시<br>- **아키텍처 v2.1 반영**: Secure Proxy Pattern, Multi-SPA 빌드 전략, HTJ2K 파이프라인<br>- **디렉토리 구조 업데이트**: 리넘버링 완료 (`01_django_server` → `02_django_server`)<br>- **Phase 2 완료 사항 반영**: 테스트 전략, 로깅 전략, 성능 최적화 문서화<br>- **GCP 배포 가이드 완성**: 12_GCP_배포_가이드.md (1,300줄+)<br>- **React 테스트 클라이언트 구현**: 00_test_client (9개 UC 테스트 페이지)<br>- **문서 재구성 완료**: 50개 → 44개 (논리적 그룹화, 중복 제거)<br>- **담당자 역할 업데이트**: AI 코어 개발 → Django Backend API 개발 |

---

**이 문서는 Claude AI가 프로젝트를 빠르게 온보딩하기 위해 작성되었습니다.**
**사용자용 가이드는 `이용법.md`를 참조하세요.**
**개발 업무 계획은 `업무계획서.md`를 참조하세요.**
