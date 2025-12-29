# Redis & Celery 통합 가이드

**작성일**: 2025-12-29
**대상**: 개발자, DevOps 엔지니어
**목적**: NeuroNova CDSS의 Redis/Celery 아키텍처 이해 및 배포 가이드

---

## 📋 목차

1. [개요](#1-개요)
2. [아키텍처 결정 배경](#2-아키텍처-결정-배경)
3. [Redis 상세 설명](#3-redis-상세-설명)
4. [Celery 상세 설명](#4-celery-상세-설명)
5. [통합 아키텍처](#5-통합-아키텍처)
6. [배포 구성](#6-배포-구성)
7. [설정 및 환경변수](#7-설정-및-환경변수)
8. [실행 방법](#8-실행-방법)
9. [모니터링](#9-모니터링)
10. [트러블슈팅](#10-트러블슈팅)
11. [성능 최적화](#11-성능-최적화)

---

## 1. 개요

### 1.1 시스템 구성

NeuroNova CDSS는 **Redis**와 **Celery**를 사용하여 비동기 작업 처리 및 캐싱을 구현합니다.

```
┌─────────────────────────────────────────────────────────┐
│                    NeuroNova CDSS                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                 │
│  │   Django     │◄────►│    Redis     │                 │
│  │   Server     │      │   (Docker)   │                 │
│  │  (로컬 venv)  │      │              │                 │
│  └──────┬───────┘      └──────┬───────┘                 │
│         │                     │                         │
│         │                     │ (브로커)                 │
│         │                     │                         │
│  ┌──────▼───────┐      ┌──────▼───────┐                 │
│  │   Celery     │      │   Celery     │                 │
│  │   Worker     │      │    Beat      │                 │
│  │  (로컬 venv)  │      │  (로컬 venv)  │                 │
│  └──────────────┘      └──────────────┘                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 주요 역할

| 컴포넌트 | 역할 | 배포 위치 |
|---------|------|----------|
| **Redis** | 메시지 브로커 + 캐시 저장소 | Docker 컨테이너 |
| **Celery Worker** | 비동기 작업 처리 | 로컬 venv |
| **Celery Beat** | 주기적 작업 스케줄러 | 로컬 venv |
| **Django** | 메인 애플리케이션 서버 | 로컬 venv |
| **Flower** | Celery 모니터링 (선택) | 로컬 venv |

---

## 2. 아키텍처 결정 배경

### 2.1 초기 아키텍처의 문제점

**변경 전 (2025-12-28):**
```
Docker:
├── Redis (브로커)
├── Celery Worker
├── Celery Beat
└── Flower

로컬:
└── Django Server (venv)
```

**문제점:**
1. **환경 불일치**: Docker Celery와 로컬 Django가 별도의 Python 환경 사용
2. **볼륨 마운트 한계**: 코드는 공유되지만 Python 패키지는 공유되지 않음
3. **DB 연결 문제**: MySQL socket vs TCP 연결 문제 (`OperationalError: 2002`)
4. **버전 충돌**: Django/Celery 간 패키지 버전 불일치 가능성
5. **디버깅 어려움**: 컨테이너 로그 확인 및 환경 재현 복잡

### 2.2 개선된 아키텍처

**변경 후 (2025-12-29):**
```
Docker:
└── Redis (브로커)

로컬 venv:
├── Django Server
├── Celery Worker
├── Celery Beat
└── Flower
```

**장점:**
1. ✅ **환경 일관성**: Django와 Celery가 동일한 Python 환경 공유
2. ✅ **DB 연결 안정성**: Socket/TCP 연결 문제 원천 차단
3. ✅ **버전 통일**: 단일 `requirements.txt` 관리
4. ✅ **디버깅 용이**: 로컬에서 직접 로그 확인 및 디버깅
5. ✅ **개발 편의성**: 코드 변경 시 즉시 반영 (hot reload)

### 2.3 Redis를 Docker로 분리한 이유

Redis만 Docker에 유지한 이유:
- **상태 비저장**: Redis는 상태를 메모리에 저장하며 Python 환경과 무관
- **포트 격리**: 6379 포트를 Docker 네트워크로 관리
- **데이터 영속성**: Docker 볼륨으로 데이터 보존
- **확장성**: 추가 Redis 노드 배포 시 Docker Compose로 쉽게 관리

---

## 3. Redis 상세 설명

### 3.1 Redis란?

**Redis** (Remote Dictionary Server)는 인메모리 데이터 구조 저장소입니다.

**주요 특징:**
- **인메모리 저장**: 매우 빠른 읽기/쓰기 (< 1ms)
- **다양한 자료구조**: String, Hash, List, Set, Sorted Set 지원
- **영속성**: RDB/AOF를 통한 디스크 저장
- **Pub/Sub**: 메시지 브로커 기능
- **원자적 연산**: 트랜잭션 지원

### 3.2 NeuroNova에서의 Redis 역할

#### 역할 1: Celery 메시지 브로커

```
Django → Redis Queue → Celery Worker
```

**동작 방식:**
1. Django에서 Celery 태스크 호출: `task.delay(args)`
2. Redis에 작업 메시지 큐잉: `celery` 큐에 저장
3. Celery Worker가 Redis에서 메시지 polling
4. Worker가 작업 수행 후 결과를 Redis에 저장
5. Django가 결과 조회 가능

**Redis 큐 구조:**
```
Redis Keys:
├── celery (기본 큐)
├── celery-task-meta-{task_id} (결과 저장)
└── _kombu.binding.celery (라우팅 정보)
```

#### 역할 2: Django 캐시 백엔드

```python
# Django에서 캐시 사용
from django.core.cache import cache

# 저장
cache.set('orthanc_url:study:123', jwt_data, timeout=3000)

# 조회
cached_data = cache.get('orthanc_url:study:123')
```

**캐시 사용 사례:**
- **Orthanc JWT URL**: 1시간 JWT를 50분간 캐싱 (10분 안전 마진)
- **FHIR OAuth 토큰**: 24시간 토큰을 90% 시간(21.6시간) 캐싱
- **API 응답 캐싱**: 자주 조회되는 환자/검사 정보

### 3.3 Redis 설정 (Docker)

**위치**: `d:\1222\NeuroNova_v1\NeuroNova_02_back_end\07_redis\docker-compose.yml`

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - neuronova_network

volumes:
  redis_data:
    driver: local

networks:
  neuronova_network:
    external: true
```

**주요 설정 해석:**

| 설정 | 값 | 의미 |
|-----|-----|-----|
| `image` | `redis:7-alpine` | Redis 7.x, 경량 Alpine Linux 기반 |
| `appendonly` | `yes` | AOF 영속성 활성화 (데이터 손실 방지) |
| `maxmemory` | `256mb` | 최대 메모리 사용량 제한 |
| `maxmemory-policy` | `allkeys-lru` | 메모리 부족 시 LRU 알고리즘으로 키 삭제 |
| `healthcheck` | `redis-cli ping` | 10초마다 헬스 체크 |
| `restart` | `unless-stopped` | 컨테이너 자동 재시작 |

**LRU (Least Recently Used) 정책:**
- 가장 오래 사용되지 않은 키부터 삭제
- 캐시 히트율 극대화
- 중요한 데이터(최근 사용)는 메모리에 유지

### 3.4 Redis 데이터 구조

**캐시 키 네이밍 규칙:**

```
orthanc_url:study:{study_uid}        # Orthanc JWT URL 캐시
orthanc_url:instance:{instance_uid}  # Orthanc Instance URL 캐시
fhir_oauth:token                     # FHIR OAuth 토큰
fhir_resource_map:{resource_type}    # FHIR 리소스 매핑
celery-task-meta-{task_id}           # Celery 작업 결과
```

**캐시 값 예시:**

```json
// Key: orthanc_url:study:1.2.840.113619.2.1.1.1
{
  "url": "http://orthanc:8042/dicom-web/studies/1.2.840.113619.2.1.1.1",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-12-29T13:00:00Z"
}

// TTL: 3000초 (50분)
```

---

## 4. Celery 상세 설명

### 4.1 Celery란?

**Celery**는 분산 태스크 큐 시스템입니다.

**주요 특징:**
- **비동기 실행**: 무거운 작업을 백그라운드에서 처리
- **분산 처리**: 여러 워커로 작업 분산
- **스케줄링**: Celery Beat를 통한 주기적 작업
- **재시도 로직**: 실패 시 자동 재시도
- **모니터링**: Flower를 통한 실시간 모니터링

### 4.2 NeuroNova에서의 Celery 역할

#### 역할 1: AI Job Processing (비동기 작업)

```python
# ai/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def process_ai_job(self, job_id):
    """
    AI 분석 작업 비동기 처리
    - MRI 종양 분석
    - 뇌 MRI 세그멘테이션
    - 결과 저장 및 리뷰어 알림
    """
    try:
        job = AIJob.objects.get(job_id=job_id)
        job.status = 'processing'
        job.save()

        # AI 모델 호출 (시간 소요: 10~60초)
        result = ai_inference_client.analyze(job.input_data)

        job.status = 'completed'
        job.result_data = result
        job.save()

        # 리뷰어에게 알림 전송
        send_notification(job.reviewer, f"AI 분석 완료: {job.job_id}")

    except Exception as exc:
        # 재시도 (최대 3회, 5분 간격)
        raise self.retry(exc=exc, countdown=300)
```

**호출 방법:**

```python
# Django View에서 비동기 호출
from ai.tasks import process_ai_job

def create_ai_job(request):
    job = AIJob.objects.create(...)

    # 비동기 실행 (즉시 반환)
    process_ai_job.delay(job.job_id)

    return JsonResponse({"status": "queued", "job_id": job.job_id})
```

#### 역할 2: FHIR Sync (주기적 동기화)

```python
# fhir/tasks.py
from celery import shared_task

@shared_task
def sync_fhir_resource(resource_type, resource_id):
    """
    FHIR 리소스 동기화 (HAPI FHIR 서버)
    - Patient, Encounter, Observation 등
    - OAuth 2.0 인증
    - 실패 시 자동 재시도
    """
    fhir_client = FHIRClient()
    resource_data = convert_to_fhir(resource_type, resource_id)

    response = fhir_client.create_or_update(resource_type, resource_data)

    # 동기화 상태 업데이트
    FHIRSyncQueue.objects.filter(
        resource_type=resource_type,
        resource_id=resource_id
    ).update(status='completed', synced_at=datetime.now())
```

#### 역할 3: Periodic Tasks (주기 작업)

```python
# fhir/tasks.py
from celery import shared_task
from celery.schedules import crontab

@shared_task
def cleanup_old_sync_queue():
    """
    오래된 동기화 큐 정리
    - 완료된 작업: 30일 후 삭제
    - 실패한 작업: 90일 후 삭제
    """
    from datetime import datetime, timedelta

    # 30일 이전 완료 작업 삭제
    FHIRSyncQueue.objects.filter(
        status='completed',
        synced_at__lt=datetime.now() - timedelta(days=30)
    ).delete()

    # 90일 이전 실패 작업 삭제
    FHIRSyncQueue.objects.filter(
        status='failed',
        updated_at__lt=datetime.now() - timedelta(days=90)
    ).delete()
```

**스케줄 설정 (Celery Beat):**

```python
# cdss_backend/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'process-pending-ai-jobs': {
        'task': 'ai.tasks.process_pending_ai_jobs',
        'schedule': 180.0,  # 3분마다
    },
    'process-fhir-sync-queue': {
        'task': 'fhir.tasks.process_fhir_sync_queue',
        'schedule': 300.0,  # 5분마다
    },
    'cleanup-old-sync-queue': {
        'task': 'fhir.tasks.cleanup_old_sync_queue',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
}
```

### 4.3 Celery 설정

**위치**: `d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\cdss_backend\celery.py`

```python
# cdss_backend/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdss_backend.settings')

# Celery 앱 생성
app = Celery('cdss_backend')

# Django settings.py에서 설정 로드 (CELERY_ 접두사)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 tasks.py 자동 검색
app.autodiscover_tasks()

# Celery Beat 스케줄 설정
app.conf.beat_schedule = {
    'process-pending-ai-jobs': {
        'task': 'ai.tasks.process_pending_ai_jobs',
        'schedule': 180.0,  # 3분
    },
    'process-fhir-sync-queue': {
        'task': 'fhir.tasks.process_fhir_sync_queue',
        'schedule': 300.0,  # 5분
    },
    'cleanup-old-sync-queue': {
        'task': 'fhir.tasks.cleanup_old_sync_queue',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
    'cleanup-old-ai-jobs': {
        'task': 'ai.tasks.cleanup_old_ai_jobs',
        'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
    },
}

# Celery 설정
app.conf.update(
    # 작업 결과 백엔드 (Redis)
    result_backend='redis://localhost:6379/0',

    # 브로커 URL
    broker_url='redis://localhost:6379/0',

    # 작업 결과 만료 시간 (1시간)
    result_expires=3600,

    # 작업 직렬화 형식
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # 시간대
    timezone='Asia/Seoul',
    enable_utc=True,

    # Worker 설정
    worker_prefetch_multiplier=4,  # 한 번에 가져올 작업 수
    worker_max_tasks_per_child=1000,  # Worker 재시작 전 최대 작업 수
)
```

### 4.4 Celery Worker 구성

**Worker 설정:**

```bash
# Worker 실행 (4개 동시 처리)
celery -A cdss_backend worker -l info --concurrency=4
```

**옵션 설명:**

| 옵션 | 값 | 의미 |
|-----|-----|-----|
| `-A` | `cdss_backend` | Celery 앱 이름 |
| `worker` | - | Worker 모드로 실행 |
| `-l` | `info` | 로그 레벨 (debug/info/warning/error) |
| `--concurrency` | `4` | 동시 처리 프로세스 수 |

**동시성 모드:**

```bash
# Prefork (기본, 다중 프로세스)
celery -A cdss_backend worker -l info --concurrency=4

# Threading (다중 스레드)
celery -A cdss_backend worker -l info --concurrency=4 --pool=threads

# Eventlet (비동기 I/O)
celery -A cdss_backend worker -l info --concurrency=1000 --pool=eventlet
```

**권장 설정:**
- **CPU 집약적 작업** (AI 분석): Prefork (기본)
- **I/O 집약적 작업** (API 호출): Threading 또는 Eventlet

### 4.5 Celery Beat 구성

**Beat 실행:**

```bash
# Celery Beat 실행 (주기 작업 스케줄러)
celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Django Celery Beat:**
- **DatabaseScheduler**: Django Admin에서 스케줄 관리 가능
- **동적 스케줄 변경**: 서버 재시작 없이 스케줄 수정
- **여러 Beat 인스턴스**: 분산 환경에서 하나만 활성화 (락 메커니즘)

**Django Admin에서 스케줄 관리:**

```
http://localhost:8000/admin/django_celery_beat/
├── Periodic Tasks (주기 작업)
├── Intervals (간격 설정)
├── Crontabs (cron 표현식)
└── Solar Events (일출/일몰 기반)
```

---

## 5. 통합 아키텍처

### 5.1 전체 데이터 흐름

```
┌────────────────────────────────────────────────────────────────┐
│                      사용자 요청                                 │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   Nginx (Reverse Proxy) │
        └────────────┬─────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   Django REST API       │
        │   (로컬 venv)            │
        └────┬───────────────┬────┘
             │               │
             │ (즉시 반환)    │ (비동기 처리)
             │               │
             ↓               ↓
    ┌────────────┐   ┌──────────────┐
    │  Response  │   │ Redis Queue  │
    │  (200 OK)  │   │  (Docker)    │
    └────────────┘   └──────┬───────┘
                            │
                            ↓ (polling)
                   ┌─────────────────┐
                   │ Celery Worker   │
                   │  (로컬 venv)     │
                   └────┬────────────┘
                        │
                        ↓ (작업 수행)
               ┌─────────────────────┐
               │  AI Core / FHIR     │
               │  External Services  │
               └─────────────────────┘
```

### 5.2 비동기 작업 시나리오

**시나리오 1: AI 분석 요청**

```
1. 사용자 → Django API: POST /api/ai/jobs/
2. Django → Redis: 작업 큐잉 (process_ai_job.delay(job_id))
3. Django → 사용자: {"status": "queued", "job_id": "abc123"}
4. Celery Worker → Redis: 작업 polling
5. Celery Worker → AI Core: AI 추론 요청 (10~60초 소요)
6. AI Core → Celery Worker: 분석 결과
7. Celery Worker → Django DB: 결과 저장 및 상태 업데이트
8. Celery Worker → Alert Service: 리뷰어에게 알림 전송
```

**시나리오 2: FHIR 동기화 (주기 작업)**

```
1. Celery Beat (매 5분): process_fhir_sync_queue.delay()
2. Celery Worker → Django DB: pending 상태 큐 조회
3. Celery Worker → Redis: OAuth 토큰 캐시 확인
4. Celery Worker → FHIR Server: 리소스 전송 (Patient, Encounter 등)
5. FHIR Server → Celery Worker: 응답 (201 Created)
6. Celery Worker → Django DB: 동기화 상태 업데이트 (completed)
```

### 5.3 캐싱 전략

**3-Tier 캐싱:**

```
┌─────────────────────────────────────────┐
│  Tier 1: Redis Cache (초고속)            │
│  - TTL: 수분 ~ 수십분                     │
│  - 용도: API 응답, JWT URL, OAuth 토큰    │
└────────────────┬────────────────────────┘
                 │ (캐시 미스)
                 ↓
┌─────────────────────────────────────────┐
│  Tier 2: MySQL Cache Layer (중속)        │
│  - TTL: 영구 (수동 무효화)                 │
│  - 용도: Patient, Encounter 복사본        │
└────────────────┬────────────────────────┘
                 │ (없음)
                 ↓
┌─────────────────────────────────────────┐
│  Tier 3: Source of Truth (저속)          │
│  - OpenEMR, HAPI FHIR, Orthanc           │
│  - 용도: 원본 데이터 조회                   │
└─────────────────────────────────────────┘
```

---

## 6. 배포 구성

### 6.1 개발 환경 (현재)

**폴더 구조:**

```
d:\1222\NeuroNova_v1\NeuroNova_02_back_end\
├── 01_django_server/              # Django + Celery (로컬 venv)
│   ├── venv/                       # Python 가상환경
│   │   └── Scripts/
│   │       ├── python.exe
│   │       ├── celery.exe
│   │       └── flower.exe
│   ├── manage.py
│   ├── cdss_backend/               # Django 설정
│   │   ├── __init__.py             # Celery 초기화
│   │   ├── celery.py               # Celery 설정
│   │   └── settings.py             # Django 설정
│   ├── ai/                         # AI 앱
│   │   └── tasks.py                # AI 태스크
│   ├── fhir/                       # FHIR 앱
│   │   └── tasks.py                # FHIR 태스크
│   └── requirements.txt            # Python 패키지
│
└── 07_redis/                       # Redis (Docker)
    ├── docker-compose.yml
    └── README.md
```

**배포 구성:**

| 컴포넌트 | 실행 위치 | 명령어 |
|---------|---------|--------|
| Redis | Docker | `docker-compose up -d` |
| Django | 로컬 venv | `venv\Scripts\python manage.py runserver` |
| Celery Worker | 로컬 venv | `venv\Scripts\celery -A cdss_backend worker -l info --concurrency=4` |
| Celery Beat | 로컬 venv | `venv\Scripts\celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` |
| Flower | 로컬 venv | `venv\Scripts\celery -A cdss_backend flower --port=5555` |

### 6.2 프로덕션 환경 (권장)

**옵션 1: 모두 Docker로 배포**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    # ... (동일)

  django:
    build: ./01_django_server
    command: gunicorn cdss_backend.wsgi:application --bind 0.0.0.0:8000
    depends_on:
      - redis

  celery_worker:
    build: ./01_django_server
    command: celery -A cdss_backend worker -l info --concurrency=4
    depends_on:
      - redis
      - django

  celery_beat:
    build: ./01_django_server
    command: celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    depends_on:
      - redis
      - django

  flower:
    build: ./01_django_server
    command: celery -A cdss_backend flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
      - celery_worker
```

**옵션 2: Kubernetes 배포**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 3  # Worker 3개
  template:
    spec:
      containers:
      - name: celery-worker
        image: neuronova/django:latest
        command: ["celery", "-A", "cdss_backend", "worker", "-l", "info", "--concurrency=4"]
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-beat
spec:
  replicas: 1  # Beat는 1개만
  template:
    spec:
      containers:
      - name: celery-beat
        image: neuronova/django:latest
        command: ["celery", "-A", "cdss_backend", "beat", "-l", "info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
```

### 6.3 스케일링 전략

**수평 확장 (Horizontal Scaling):**

```bash
# Worker 수 증가
celery -A cdss_backend worker -l info --concurrency=8  # 8개 프로세스

# 여러 Worker 인스턴스 실행 (분산)
# Server 1
celery -A cdss_backend worker -n worker1@%h -l info --concurrency=4

# Server 2
celery -A cdss_backend worker -n worker2@%h -l info --concurrency=4

# Server 3
celery -A cdss_backend worker -n worker3@%h -l info --concurrency=4
```

**큐 분리 (Queue Isolation):**

```python
# cdss_backend/celery.py
app.conf.task_routes = {
    'ai.tasks.process_ai_job': {'queue': 'ai'},
    'fhir.tasks.sync_fhir_resource': {'queue': 'fhir'},
}
```

```bash
# AI 전용 Worker
celery -A cdss_backend worker -Q ai -l info --concurrency=4

# FHIR 전용 Worker
celery -A cdss_backend worker -Q fhir -l info --concurrency=2
```

---

## 7. 설정 및 환경변수

### 7.1 Django Settings

**위치**: `d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\cdss_backend\settings.py`

```python
# settings.py

# Redis 설정
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Celery 설정
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

# Django Cache (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'cdss',
        'TIMEOUT': 300,  # 기본 5분
    }
}
```

### 7.2 환경변수 (.env)

**위치**: `d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\.env`

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Orthanc JWT
ORTHANC_JWT_LIFETIME_HOURS=1

# FHIR OAuth
FHIR_OAUTH_TOKEN_URL=https://hapi.fhir.org/oauth/token
FHIR_OAUTH_CLIENT_ID=your_client_id
FHIR_OAUTH_CLIENT_SECRET=your_client_secret
```

### 7.3 requirements.txt

**위치**: `d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\requirements.txt`

```txt
# Django
Django==5.1.6

# Redis
redis==4.6.0
django-redis==5.4.0

# Celery
celery[redis]==5.3.4
django-celery-beat==2.7.0
flower==2.0.1

# 기타
requests==2.32.5
python-dotenv==1.2.1
```

**버전 제약:**
- `django-celery-beat 2.7.0`: Django < 5.2 요구 → Django 5.1.6 사용
- `celery[redis] 5.3.4`: redis < 5.0.0 요구 → redis 4.6.0 사용

---

## 8. 실행 방법

### 8.1 개발 환경 실행

**Step 1: Redis 시작 (Docker)**

```powershell
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\07_redis
docker-compose up -d
```

**Step 2: Django 서버 시작 (Terminal 1)**

```powershell
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server
venv\Scripts\activate
python manage.py runserver
```

**Step 3: Celery Worker 시작 (Terminal 2)**

```powershell
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server
venv\Scripts\activate
celery -A cdss_backend worker -l info --concurrency=4
```

**Step 4: Celery Beat 시작 (Terminal 3)**

```powershell
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server
venv\Scripts\activate
celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Step 5 (선택): Flower 시작 (Terminal 4)**

```powershell
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server
venv\Scripts\activate
celery -A cdss_backend flower --port=5555
```

### 8.2 상태 확인

```powershell
# Redis 상태
docker ps | findstr redis

# Redis 연결 테스트
docker exec redis redis-cli ping
# 응답: PONG

# Celery Worker 상태
celery -A cdss_backend inspect active

# Celery Beat 스케줄 확인
celery -A cdss_backend inspect scheduled
```

### 8.3 중지 방법

```powershell
# Django 서버 중지 (Ctrl+C)

# Celery Worker 중지 (Ctrl+C)

# Celery Beat 중지 (Ctrl+C)

# Flower 중지 (Ctrl+C)

# Redis 중지
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\07_redis
docker-compose down
```

---

## 9. 모니터링

### 9.1 Flower (Celery 모니터링)

**접속**: http://localhost:5555

**주요 기능:**
- **Workers**: 활성 워커 상태, CPU/메모리 사용률
- **Tasks**: 실행 중/완료/실패한 작업 목록
- **Broker**: Redis 큐 상태 (pending, active, reserved)
- **Graph**: 시간별 작업 처리량 그래프
- **Logs**: 실시간 작업 로그

**Flower 스크린샷 (예시):**

```
┌──────────────────────────────────────────────────┐
│ Flower - Celery Monitoring                       │
├──────────────────────────────────────────────────┤
│ Workers                                          │
│ ├── worker1@localhost  [Active]                  │
│ │   ├── Concurrency: 4                           │
│ │   ├── CPU: 25%                                 │
│ │   ├── Memory: 512MB                            │
│ │   └── Tasks: 150 processed                     │
│                                                  │
│ Tasks (Last 1 Hour)                              │
│ ├── Succeeded: 120                               │
│ ├── Failed: 5                                    │
│ ├── Retrying: 2                                  │
│ └── Active: 3                                    │
│     ├── ai.tasks.process_ai_job (job_123)       │
│     ├── fhir.tasks.sync_fhir_resource (Patient)  │
│     └── fhir.tasks.sync_fhir_resource (Encounter)│
└──────────────────────────────────────────────────┘
```

### 9.2 Redis 모니터링

**Redis CLI 사용:**

```bash
# Redis에 접속
docker exec -it redis redis-cli

# 현재 키 개수 확인
127.0.0.1:6379> DBSIZE
(integer) 1523

# 메모리 사용량 확인
127.0.0.1:6379> INFO memory
# used_memory_human:128.45M
# maxmemory_human:256.00M

# 특정 패턴 키 조회
127.0.0.1:6379> KEYS orthanc_url:*
1) "orthanc_url:study:1.2.840.113619.2.1.1.1"
2) "orthanc_url:study:1.2.840.113619.2.1.1.2"

# TTL 확인
127.0.0.1:6379> TTL orthanc_url:study:1.2.840.113619.2.1.1.1
(integer) 2850  # 2850초 남음 (약 47분)

# Celery 큐 길이 확인
127.0.0.1:6379> LLEN celery
(integer) 5  # 5개 작업 대기 중
```

**Redis Monitor (실시간 명령어 추적):**

```bash
docker exec -it redis redis-cli MONITOR
```

### 9.3 Django Celery Beat Admin

**접속**: http://localhost:8000/admin/django_celery_beat/

**주기 작업 관리:**

```
┌──────────────────────────────────────────────────┐
│ Django Admin - Periodic Tasks                    │
├──────────────────────────────────────────────────┤
│ Task                        | Interval | Enabled │
├─────────────────────────────┼──────────┼─────────┤
│ process-pending-ai-jobs     │ 3 min    │ ✓       │
│ process-fhir-sync-queue     │ 5 min    │ ✓       │
│ cleanup-old-sync-queue      │ Daily 2AM│ ✓       │
│ cleanup-old-ai-jobs         │ Daily 3AM│ ✓       │
└──────────────────────────────────────────────────┘
```

**동적 스케줄 변경 (서버 재시작 불필요):**
1. Admin에서 "Add Periodic Task" 클릭
2. Task 선택: `fhir.tasks.process_fhir_sync_queue`
3. Interval 설정: 10분
4. Save → 즉시 적용

---

## 10. 트러블슈팅

### 10.1 Redis 연결 실패

**증상:**

```
celery.exceptions.OperationalError: Error 111 connecting to localhost:6379. Connection refused.
```

**원인:**
- Redis 컨테이너가 실행되지 않음
- 잘못된 REDIS_HOST 설정

**해결:**

```powershell
# Redis 상태 확인
docker ps | findstr redis

# Redis가 없으면 시작
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\07_redis
docker-compose up -d

# 연결 테스트
docker exec redis redis-cli ping
```

### 10.2 Celery Worker가 작업을 처리하지 않음

**증상:**
- Django에서 `task.delay()` 호출 후 작업이 처리되지 않음
- Flower에서 "No workers online" 표시

**원인:**
- Celery Worker가 실행되지 않음
- 잘못된 브로커 URL

**해결:**

```powershell
# Worker 상태 확인
celery -A cdss_backend inspect active

# Worker 재시작
celery -A cdss_backend worker -l info --concurrency=4

# 브로커 URL 확인 (.env 파일)
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 10.3 Celery Beat 스케줄이 실행되지 않음

**증상:**
- 주기 작업이 예정 시간에 실행되지 않음

**원인:**
- Celery Beat가 실행되지 않음
- DatabaseScheduler 마이그레이션 누락

**해결:**

```powershell
# Beat 상태 확인
celery -A cdss_backend inspect scheduled

# 마이그레이션 확인
python manage.py migrate django_celery_beat

# Beat 재시작
celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 10.4 메모리 부족 (Redis OOM)

**증상:**

```
Redis: OOM command not allowed when used memory > 'maxmemory'
```

**원인:**
- Redis maxmemory 초과 (256MB)

**해결:**

```yaml
# docker-compose.yml 수정
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

```powershell
# Redis 재시작
docker-compose down
docker-compose up -d

# 메모리 확인
docker exec redis redis-cli INFO memory
```

### 10.5 Django와 Celery 환경 불일치

**증상:**
- Celery에서 `ModuleNotFoundError: No module named 'xxx'`
- Django에서는 정상 작동

**원인:**
- Docker Celery와 로컬 Django의 Python 환경 불일치

**해결 (현재 아키텍처):**
- ✅ 이미 해결됨: Celery를 로컬 venv로 이동하여 Django와 동일 환경 공유

**확인 방법:**

```powershell
# Django Python 환경
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server
venv\Scripts\python -c "import sys; print(sys.executable)"
# 출력: d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server\venv\Scripts\python.exe

# Celery Python 환경
venv\Scripts\celery -A cdss_backend worker -l info
# 같은 venv 사용 확인
```

---

## 11. 성능 최적화

### 11.1 Redis 최적화

**메모리 최적화:**

```bash
# RDB 스냅샷 비활성화 (AOF만 사용)
redis-server --save "" --appendonly yes

# 압축 활성화
redis-server --rdbcompression yes

# LRU 샘플 증가 (정확도 향상)
redis-server --maxmemory-samples 10
```

**네트워크 최적화:**

```python
# Django settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,  # 연결 풀 크기
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
    }
}
```

### 11.2 Celery 최적화

**Worker 튜닝:**

```bash
# CPU 집약적 작업 (AI 분석)
celery -A cdss_backend worker -Q ai \
  -l info \
  --concurrency=4 \
  --pool=prefork \
  --max-tasks-per-child=100  # 메모리 누수 방지

# I/O 집약적 작업 (API 호출)
celery -A cdss_backend worker -Q fhir \
  -l info \
  --concurrency=1000 \
  --pool=eventlet
```

**재시도 전략:**

```python
# ai/tasks.py
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5분
    retry_backoff=True,  # 지수 백오프
    retry_backoff_max=3600,  # 최대 1시간
    retry_jitter=True,  # 랜덤 지터
)
def process_ai_job(self, job_id):
    try:
        # AI 처리
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
```

**우선순위 큐:**

```python
# cdss_backend/celery.py
from kombu import Queue

app.conf.task_queues = (
    Queue('high_priority', routing_key='high'),
    Queue('default', routing_key='default'),
    Queue('low_priority', routing_key='low'),
)

app.conf.task_routes = {
    'ai.tasks.urgent_ai_job': {'queue': 'high_priority'},
    'ai.tasks.process_ai_job': {'queue': 'default'},
    'fhir.tasks.cleanup_old_sync_queue': {'queue': 'low_priority'},
}
```

### 11.3 캐시 최적화

**캐시 워밍 (Pre-warming):**

```python
# ris/tasks.py
@shared_task
def warm_orthanc_cache():
    """최근 7일간 조회된 Study의 JWT URL 미리 로드"""
    from datetime import datetime, timedelta
    from ris.models import RadiologyStudy

    recent_studies = RadiologyStudy.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).values_list('study_instance_uid', flat=True)

    for study_uid in recent_studies:
        # JWT URL 생성 및 캐싱
        OrthancClient().get_study_url_with_jwt(study_uid)
```

**캐시 무효화 (Invalidation):**

```python
# ris/models.py
from django.db.models.signals import post_save
from django.core.cache import cache

@receiver(post_save, sender=RadiologyStudy)
def invalidate_study_cache(sender, instance, **kwargs):
    """Study 업데이트 시 캐시 무효화"""
    cache_key = f"orthanc_url:study:{instance.study_instance_uid}"
    cache.delete(cache_key)
```

### 11.4 모니터링 메트릭

**수집해야 할 메트릭:**

```python
# metrics.py
import time
from celery.signals import task_prerun, task_postrun, task_failure

# 작업 수행 시간 측정
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    task.start_time = time.time()

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, **kwargs):
    duration = time.time() - task.start_time
    logger.info(f"Task {task.name} completed in {duration:.2f}s")

# 실패율 측정
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    logger.error(f"Task {sender.name} failed: {exception}")
```

**성능 목표:**

| 메트릭 | 목표 |
|-------|------|
| Redis 캐시 적중률 | > 85% |
| Celery Worker 처리량 | > 100 tasks/min |
| 평균 작업 대기 시간 | < 10초 |
| 평균 작업 수행 시간 | < 30초 (AI 제외) |
| Redis 메모리 사용률 | < 80% |

---

## 12. 참고 자료

### 12.1 공식 문서

- **Redis**: https://redis.io/documentation
- **Celery**: https://docs.celeryproject.org/
- **Django Celery Beat**: https://django-celery-beat.readthedocs.io/
- **Flower**: https://flower.readthedocs.io/

### 12.2 관련 NeuroNova 문서

- [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md) - 섹션 4.5: Redis/Celery 아키텍처
- [REF_CLAUDE_ONBOARDING_QUICK.md](REF_CLAUDE_ONBOARDING_QUICK.md) - 섹션 8: 빠른 시작
- [07_redis/README.md](../NeuroNova_02_back_end/07_redis/README.md) - Redis 실행 가이드
- [11_배포_가이드.md](11_배포_가이드.md) - 전체 배포 가이드
- [13_FHIR_통합_가이드.md](13_FHIR_통합_가이드.md) - FHIR 동기화 작업

### 12.3 Best Practices

1. **환경 일관성**: Django와 Celery는 동일한 Python 환경에서 실행
2. **큐 분리**: AI, FHIR, 정리 작업을 별도 큐로 분리
3. **재시도 전략**: 지수 백오프 + 랜덤 지터로 재시도
4. **캐싱 전략**: 적절한 TTL 설정 (JWT 50분, OAuth 21.6시간)
5. **모니터링**: Flower + Redis CLI로 실시간 모니터링

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-29
**작성자**: NeuroNova Development Team
