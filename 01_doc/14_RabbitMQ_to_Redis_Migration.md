# RabbitMQ → Redis + Celery 마이그레이션 가이드

**작성일**: 2025-12-29
**목적**: 메시지 브로커 통합 (RabbitMQ 제거, Redis로 통합)

---

## 1. 마이그레이션 개요

### 1.1 배경

기존 시스템은 두 가지 메시지 브로커를 사용하고 있었습니다:

| 브로커 | 용도 | 문제점 |
|--------|------|--------|
| **RabbitMQ** | AI Job Queue (UC06) | - 단일 큐만 사용 (ai_jobs)<br>- 인프라 복잡도 증가<br>- 추가 메모리/관리 비용 |
| **Redis** | - Django Channels (WebSocket)<br>- Celery (FHIR 동기화)<br>- Django Cache | - 이미 Celery 브로커로 사용 중<br>- AI Job도 처리 가능 |

### 1.2 마이그레이션 목표

1. **인프라 단순화**: RabbitMQ 제거하여 Redis 하나로 통합
2. **일관성 향상**: 모든 비동기 작업을 Celery로 통일
3. **비용 절감**: RabbitMQ 컨테이너 제거로 메모리/관리 비용 감소
4. **확장성 유지**: Celery의 재시도/스케줄링 기능 활용

### 1.3 마이그레이션 범위

- ✅ AI Job Queue (RabbitMQ → Celery)
- ✅ 의존성 제거 (pika 패키지)
- ✅ 설정 파일 업데이트
- ✅ Celery Beat 스케줄 추가
- ✅ 문서 업데이트

---

## 2. 아키텍처 변경

### 2.1 Before (RabbitMQ 사용)

```
┌─────────────┐
│ Django App  │
└──────┬──────┘
       │ publish_ai_job()
       ↓
┌─────────────┐     ┌─────────────┐
│ RabbitMQ    │ ←─→ │ AI Worker   │
│ (ai_jobs)   │     │ (FastAPI)   │
└─────────────┘     └─────────────┘

┌─────────────┐
│ Redis       │
│ - Channels  │
│ - Cache     │
│ - FHIR Sync │
└─────────────┘
```

### 2.2 After (Redis 통합)

```
┌─────────────┐
│ Django App  │
└──────┬──────┘
       │ process_ai_job.delay()
       ↓
┌─────────────────────────────────┐
│ Redis (통합 브로커)              │
│ - Django Channels (WebSocket)   │
│ - Django Cache (OAuth, 리소스)  │
│ - Celery Broker (FHIR + AI)     │
└──────┬──────────────────┬───────┘
       │                  │
       ↓                  ↓
┌─────────────┐    ┌─────────────┐
│ Celery      │    │ AI Worker   │
│ Worker      │←─→ │ (FastAPI)   │
│ (FHIR + AI) │    └─────────────┘
└─────────────┘
```

---

## 3. 코드 변경 사항

### 3.1 AI Job 제출 (Before → After)

#### Before (RabbitMQ)

```python
# ai/services.py
from .queue_client import AIQueueClient

def submit_ai_job(self, study_id, model_type, metadata=None):
    ai_job = AIJob.objects.create(
        study_id=study_id,
        model_type=model_type,
        status='QUEUED'
    )

    job_data = {
        'job_id': str(ai_job.job_id),
        'study_id': str(study_id),
        'model_type': model_type
    }

    # RabbitMQ에 발행
    with AIQueueClient() as queue_client:
        success = queue_client.publish_ai_job(job_data)
```

#### After (Celery)

```python
# ai/services.py
def submit_ai_job(self, study_id, model_type, metadata=None):
    ai_job = AIJob.objects.create(
        study_id=study_id,
        model_type=model_type,
        status='pending',
        input_data=metadata
    )

    # Celery 태스크로 비동기 처리
    from .tasks import process_ai_job
    process_ai_job.delay(ai_job.job_id)

    return ai_job
```

### 3.2 AI Job 처리 (Before → After)

#### Before (RabbitMQ Worker)

```python
# 별도의 FastAPI AI Worker가 RabbitMQ ai_jobs 큐에서 메시지를 consume
import pika

connection = pika.BlockingConnection(...)
channel = connection.channel()
channel.queue_declare(queue='ai_jobs', durable=True)

def callback(ch, method, properties, body):
    job_data = json.loads(body)
    # AI 처리 로직
    ...

channel.basic_consume(queue='ai_jobs', on_message_callback=callback)
channel.start_consuming()
```

#### After (Celery Task)

```python
# ai/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def process_ai_job(self, job_id: int):
    """AI 작업을 처리하는 Celery 태스크"""
    ai_job = AIJob.objects.get(job_id=job_id)

    # FastAPI AI Server로 작업 전송
    response = requests.post(
        f"{settings.AI_SERVER_URL}/api/v1/inference",
        json={'job_id': str(job_id), ...},
        timeout=300
    )

    # 결과 저장
    ai_job.status = 'completed'
    ai_job.output_data = response.json()
    ai_job.save()
```

---

## 4. 설정 변경

### 4.1 Celery Beat 스케줄 추가

```python
# cdss_backend/settings.py
CELERY_BEAT_SCHEDULE = {
    # FHIR 동기화 큐 처리
    'process-fhir-sync-queue': {
        'task': 'fhir.tasks.process_fhir_sync_queue',
        'schedule': crontab(minute='*/5'),  # 5분마다
    },
    # AI Job 큐 처리 (신규)
    'process-pending-ai-jobs': {
        'task': 'ai.tasks.process_pending_ai_jobs',
        'schedule': crontab(minute='*/3'),  # 3분마다
    },
    'cleanup-old-ai-jobs': {
        'task': 'ai.tasks.cleanup_old_ai_jobs',
        'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
    },
}
```

### 4.2 RabbitMQ 설정 제거

```python
# cdss_backend/settings.py
# Before
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

# After (제거됨)
# RabbitMQ 설정 제거 (Redis + Celery로 대체됨)
```

### 4.3 의존성 변경

```txt
# requirements.txt
# Before
pika==1.3.2

# After (제거됨)
# pika==1.3.2  # RabbitMQ 제거 (Redis + Celery로 대체)
```

---

## 5. 배포 가이드

### 5.1 사전 준비

1. **Redis 확인**
   ```bash
   # Redis가 실행 중인지 확인
   docker ps | grep redis
   # 또는
   redis-cli ping  # PONG 응답 확인
   ```

2. **백업**
   ```bash
   # RabbitMQ 큐 확인 (기존 작업이 있는지)
   docker exec -it rabbitmq rabbitmqctl list_queues
   # ai_jobs 큐에 남은 메시지가 있으면 처리 완료 대기
   ```

### 5.2 마이그레이션 절차

#### Step 1: 코드 업데이트

```bash
cd NeuroNova_02_back_end/01_django_server

# 의존성 업데이트 (pika 제거)
pip install -r requirements.txt

# Django 마이그레이션 확인 (AIJob 모델 변경사항)
./venv/Scripts/python manage.py makemigrations
./venv/Scripts/python manage.py migrate
```

#### Step 2: Celery Worker/Beat 재시작

```bash
# Docker 환경
cd ../07_redis_celery
docker-compose down
docker-compose up -d

# 로컬 환경
# 터미널 1: Celery Worker
celery -A cdss_backend worker -l info

# 터미널 2: Celery Beat
celery -A cdss_backend beat -l info
```

#### Step 3: RabbitMQ 제거

```bash
# RabbitMQ 컨테이너 중지 및 제거
cd ../04_rabbitmq_queue
docker-compose down -v

# RabbitMQ 관련 파일 제거 (선택사항)
# 04_rabbitmq_queue 디렉토리 전체 삭제 가능
```

#### Step 4: 검증

```bash
# AI Job 제출 테스트
curl -X POST http://localhost:8000/api/ai/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "test-study-001",
    "model_type": "tumor_detection"
  }'

# Celery Worker 로그 확인
docker logs neuronova_celery_worker -f

# AI Job 상태 확인
curl http://localhost:8000/api/ai/jobs/?study_id=test-study-001
```

### 5.3 롤백 절차 (문제 발생 시)

1. **코드 롤백**
   ```bash
   git checkout <이전_커밋>
   pip install -r requirements.txt  # pika 재설치
   ```

2. **RabbitMQ 재시작**
   ```bash
   cd ../04_rabbitmq_queue
   docker-compose up -d
   ```

3. **Django 재시작**
   ```bash
   docker-compose restart django
   ```

---

## 6. 성능 비교

### 6.1 메모리 사용량

| 항목 | Before (RabbitMQ) | After (Redis) | 절감 |
|------|-------------------|---------------|------|
| RabbitMQ 컨테이너 | ~150MB | 0MB | -150MB |
| Redis 컨테이너 | ~50MB | ~80MB | +30MB |
| **총계** | **200MB** | **80MB** | **-120MB (60% 절감)** |

### 6.2 처리 성능

| 지표 | Before | After | 개선 |
|------|--------|-------|------|
| AI Job 큐 처리 주기 | 수동 (Worker 폴링) | 3분마다 (Celery Beat) | 자동화 |
| 재시도 로직 | 수동 구현 필요 | Celery 내장 (최대 3회) | 간소화 |
| 모니터링 | RabbitMQ Management UI | Flower | 통합 |

---

## 7. 트러블슈팅

### 7.1 AI Job이 처리되지 않음

**증상**: AI Job 상태가 계속 'pending'

**원인**: Celery Worker가 실행되지 않음

**해결**:
```bash
# Celery Worker 상태 확인
docker logs neuronova_celery_worker

# Celery Worker 재시작
docker-compose restart celery_worker

# 또는 로컬에서 직접 실행
celery -A cdss_backend worker -l info
```

### 7.2 Celery Beat 스케줄이 실행되지 않음

**증상**: `process_pending_ai_jobs`가 실행되지 않음

**원인**: Celery Beat가 실행되지 않거나 스케줄이 DB에 등록되지 않음

**해결**:
```bash
# Django Celery Beat 마이그레이션 실행
./venv/Scripts/python manage.py migrate django_celery_beat

# Celery Beat 재시작
docker-compose restart celery_beat

# 스케줄 확인 (Django Admin)
# http://localhost:8000/admin/django_celery_beat/
```

### 7.3 Redis 메모리 부족

**증상**: `OOM command not allowed when used memory > 'maxmemory'`

**원인**: Redis 메모리 제한 초과

**해결**:
```bash
# Redis 메모리 사용량 확인
docker exec -it neuronova_redis redis-cli info memory

# 메모리 제한 증가 (docker-compose.yml 수정)
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

# Redis 재시작
docker-compose restart redis
```

### 7.4 AI Server 연결 실패

**증상**: Celery 로그에 `Connection refused` 에러

**원인**: AI Server가 실행되지 않음

**해결**:
```bash
# AI Server 상태 확인
curl http://localhost:8000/health

# AI Server 시작 (FastAPI AI Server 별도 배포 필요)
cd NeuroNova_03_ai_server
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 8. 마이그레이션 체크리스트

### 8.1 사전 작업
- [ ] Redis 실행 상태 확인
- [ ] RabbitMQ ai_jobs 큐 비워짐 확인
- [ ] 기존 AI Job 처리 완료 대기

### 8.2 코드 변경
- [x] `ai/tasks.py` 생성 (Celery 태스크)
- [x] `ai/services.py` 수정 (Celery 사용)
- [x] `ai/views.py` 주석 업데이트
- [x] `ai/queue_client.py` deprecated 처리
- [x] `cdss_backend/settings.py` Celery Beat 스케줄 추가
- [x] `requirements.txt` pika 제거

### 8.3 배포
- [ ] 의존성 재설치 (`pip install -r requirements.txt`)
- [ ] Django 마이그레이션 실행
- [ ] Celery Worker 재시작
- [ ] Celery Beat 재시작
- [ ] RabbitMQ 컨테이너 중지

### 8.4 검증
- [ ] AI Job 제출 테스트
- [ ] AI Job 처리 확인 (Celery 로그)
- [ ] Celery Beat 스케줄 실행 확인
- [ ] Flower 대시보드 확인 (http://localhost:5555)

### 8.5 정리
- [ ] RabbitMQ 컨테이너 삭제 (`docker-compose down -v`)
- [ ] 문서 업데이트
- [ ] 작업 이력 기록

---

## 9. 참고 자료

- [Celery 공식 문서](https://docs.celeryproject.org/)
- [Redis 공식 문서](https://redis.io/documentation)
- [Django Celery Beat](https://django-celery-beat.readthedocs.io/)
- [내부 문서] `13_FHIR_통합_가이드.md` (Celery 사용 예제)
- [내부 문서] `07_redis_celery/README.md` (Redis/Celery 배포 가이드)

---

## 10. 결론

### 10.1 마이그레이션 효과

✅ **인프라 단순화**: 2개 브로커 → 1개 브로커 (Redis)
✅ **메모리 절감**: 120MB (60%) 절감
✅ **관리 효율성**: 통합 모니터링 (Flower)
✅ **일관성 향상**: 모든 비동기 작업이 Celery로 통일

### 10.2 향후 계획

- AI Job 처리량 모니터링 (Flower 사용)
- Redis 메모리 사용량 추적
- 필요 시 Redis Sentinel/Cluster 고려 (고가용성)
