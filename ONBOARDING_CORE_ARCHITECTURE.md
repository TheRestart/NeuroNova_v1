# NeuroNova CDSS 프로젝트 - 핵심 아키텍처 온보딩

> **목적**: 다른 개발자가 유사한 프로젝트를 시작할 때 참고할 핵심 구조와 데이터 흐름 가이드

**작성일**: 2026-01-05
**프로젝트**: 임상 의사결정 지원 시스템(CDSS) - 의료 영상 기반 AI 분석 플랫폼

---

## 1. 시스템 개요

### 1.1 핵심 특징
- **시스템 타입**: 의료 마이크로서비스 아키�ecture
- **주요 기능**: 의료 영상(DICOM) 관리, AI 기반 분석, 전자의무기록(EMR) 통합
- **아키텍처 패턴**: Django 기반 Layered Architecture + 외부 시스템 통합

### 1.2 핵심 기술 스택
```
Backend: Django REST Framework + FastAPI (AI)
Database: MySQL (메인 DB) + Redis (캐시/브로커)
PACS: Orthanc (DICOM 서버) + HTJ2K (고속 압축)
EMR: OpenEMR + HAPI FHIR (의료정보 표준)
비동기: Celery (이미지 처리, AI 추론)
프론트엔드: React SPA + OHIF Viewer (의료 영상 뷰어)
Gateway: Nginx (Reverse Proxy)
```

---

## 2. 시스템 아키텍처 (v2.1)

### 2.1 전체 구조도

```
┌─────────────────────────────────────────────────────────────────┐
│                    외부 접근 레이어                                │
│  Internet → Cloudflare → Nginx :80 (Reverse Proxy)              │
│              Routes:                                            │
│              - / → React SPA                                    │
│              - /api/* → Django :8000                            │
│              - /internal-orthanc/* → Orthanc :8042 (INTERNAL)  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Django Backend (핵심 비즈니스 로직)                   │
│  - JWT 인증/권한 (RBAC)                                          │
│  - EMR 데이터 프록시                                              │
│  - AI 작업 오케스트레이션                                          │
│  - DICOM 업로드/조회 관리                                         │
│  - FHIR 표준 변환                                                │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              데이터 & 통합 레이어                                 │
│  ┌─────────┬─────────┬────────────┬─────────────┐                │
│  │  MySQL  │  Redis  │   Orthanc  │ HAPI FHIR/  │                │
│  │  :3306  │  :6379  │    :8042   │  OpenEMR    │                │
│  │  (DB)   │ (Cache) │    (PACS)  │  :8080      │                │
│  │         │ (Broker)│   (HTJ2K)  │  (EMR)      │                │
│  │         │         │**INTERNAL**│ **INTERNAL**│                │
│  └─────────┴─────────┴────────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│           AI & 비동기 처리 레이어                                  │
│  ┌──────────────────────┬────────────────────────────────────┐  │
│  │  FastAPI (AI Core)   │  Celery Workers                    │  │
│  │  - HTJ2K 디코딩       │  - DICOM → HTJ2K 변환               │  │
│  │  - AI 추론           │  - AI 작업 트리거                    │  │
│  │                      │  - FHIR 동기화                      │  │
│  └──────────────────────┴────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 보안 설계
- **외부 노출**: Nginx만 (React, Django API)
- **Secure Proxy Pattern**: Django가 JWT 검증 후 Nginx X-Accel-Redirect로 Orthanc 접근 위임
- **내부 전용**: Orthanc, MySQL, Redis, HAPI FHIR, OpenEMR (직접 외부 접속 차단)

---

## 3. 핵심 데이터 흐름

### 3.1 동기 vs 비동기 처리

#### 동기 처리 (HTTP 직접 호출)
```
Django ↔ MySQL (ORM)
Django ↔ Redis (캐싱)
Django ↔ Orthanc (DICOM 조회/메타데이터)
Django ↔ HAPI FHIR (의료정보 표준 조회)
Django ↔ OpenEMR (환자 정보 조회)
```

#### 비동기 처리 (Celery Task Queue)
```
Celery Worker:
  1. DICOM → HTJ2K 이미지 변환
  2. AI 모델 추론 (장시간 작업)
  3. FHIR 서버 동기화 (배치 작업)
  4. 주기적 데이터 정리
```

**아키텍처 결정**:
- Django와 Celery는 **동일한 로컬 가상환경(venv)**에서 실행
- Redis만 Docker 컨테이너로 분리
- 이유: Python 환경 일관성, MySQL 연결 안정성, 종속성 충돌 방지

### 3.2 HTJ2K 파이프라인 (의료 영상 고속 처리)

**HTJ2K**: High-Throughput JPEG 2000 (DICOM 표준 압축 포맷)
- 기존 JPEG 2000 대비 10배 빠른 디코딩 속도
- WASM(WebAssembly) 브라우저 디코딩 지원
- 고화질 유지, 손실/무손실 선택 가능

#### 업로드 흐름
```
사용자 → Django API (DICOM 업로드)
  ↓
Celery Worker (비동기 변환)
  - Raw DICOM → HTJ2K 압축
  - 또는 J2K Fallback (Orthanc 호환성)
  ↓
Orthanc PACS (저장)
```

#### 조회/뷰잉 흐름 (Secure)
```
OHIF Viewer → Django API (JWT 검증)
  ↓
Django (권한 확인 후)
  ↓
Nginx X-Accel-Redirect (내부 전송)
  ↓
Orthanc PACS (DICOM 파일 전송)
  ↓
WASM 디코딩 (브라우저 초고속 렌더링)
```

### 3.3 AI 분석 흐름
```
1. 의사가 영상 검사 오더 생성
   ↓
2. Django가 AI 작업 생성 (Job 상태: PENDING)
   ↓
3. Celery Worker가 작업 수행:
   - Orthanc에서 HTJ2K 조회
   - pylibjpeg 디코딩 → NumPy 배열
   - FastAPI (AI Core) 호출
   ↓
4. AI 결과 저장 (Job 상태: COMPLETED)
   ↓
5. 의사에게 실시간 알림 (WebSocket - Django Channels)
   ↓
6. 의사가 검토 후 승인/거부
```

### 3.4 EMR 데이터 동기화 전략 (Database Router + Outbox)

```
┌────────────────────────────────────────────────────────┐
│  읽기 작업 (Django ORM Auto-Routing)                   │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  1단계: CDSS DB (Cache Layer)          │
│  - Django 로컬 DB 우선 조회            │
│  - 빠른 응답 (< 10ms)                   │
│  - ORM: Patient.objects.using('default')│
└────────────────────────────────────────┘
           ↓ (캐시 미스)
┌────────────────────────────────────────┐
│  2단계: OpenEMR DB (Source of Truth)   │
│  - Django Database Router 자동 라우팅  │
│  - MariaDB 직접 조회 (REST API 불필요)  │
│  - ORM: OpenEMRPatient.objects.all()   │
│    → 자동으로 using='openemr' 적용      │
└────────────────────────────────────────┘
           ↓ (조회 후)
┌────────────────────────────────────────┐
│  Write-Back Caching                    │
│  - OpenEMR 데이터 → CDSS DB에 캐싱      │
│  - 다음 조회 시 1단계에서 빠른 응답      │
└────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  쓰기 작업 (Outbox Pattern - 비동기)                   │
└────────────────────────────────────────────────────────┘

1. API 요청 (환자 생성)
   ↓
2. Django Transaction (CDSS DB)
   - Patient 생성 (default DB)
   - OutboxEvent 생성 (PENDING)
   - 트랜잭션 커밋 → API 즉시 응답
   ↓
3. Celery Worker (비동기)
   - OutboxEvent 폴링 (10초마다)
   - OpenEMR DB에 데이터 동기화 (using='openemr')
   - OutboxEvent 상태 업데이트 (COMPLETED/FAILED)
   ↓
4. FHIR 동기화 (선택사항)
   - FHIR Celery Worker가 별도 처리
   - HAPI FHIR 서버에 리소스 생성
```

**Django ORM 예시:**
```python
# 1. OpenEMR DB 직접 조회 (자동 라우팅)
from openemr_models.models import OpenEMRPatient

# Router가 자동으로 'openemr' DB로 라우팅
patients = OpenEMRPatient.objects.filter(fname__icontains='홍길동')

# 2. CDSS DB 캐시 조회
from emr.models import Patient

# Router가 자동으로 'default' DB로 라우팅
cached_patients = Patient.objects.filter(full_name__icontains='홍길동')

# 3. 데이터 생성 시 Outbox Pattern
@transaction.atomic
def create_patient(patient_data):
    # CDSS DB에 환자 생성
    patient = Patient.objects.create(**patient_data)

    # Outbox 이벤트 생성 (OpenEMR 동기화 예약)
    OutboxEvent.objects.create(
        event_type='PATIENT_CREATED',
        aggregate_id=patient.id,
        payload=patient_data
    )

    # 즉시 응답 (OpenEMR 동기화는 Celery가 비동기 처리)
    return patient
```

**설계 패턴**:
- **Database Router**: Django ORM이 모델에 따라 자동으로 DB 선택
- **Read-Through Caching**: CDSS DB 캐시 미스 시 OpenEMR DB 조회 → 캐싱
- **Outbox Pattern**: 쓰기 작업은 Outbox 테이블에 기록 → Celery 비동기 처리
- **Eventually Consistent**: 즉시 일관성 대신 최종 일관성 보장 (성능 우선)

**장점:**
- **성능**: REST API 오버헤드 없이 직접 DB 접근 (10배 빠름)
- **신뢰성**: Outbox Pattern으로 메시지 유실 방지
- **트랜잭션**: Django ORM 트랜잭션 관리 활용
- **확장성**: OpenEMR 부하 없이 CDSS에서 캐시 조회 가능

---

## 4. 레이어드 아키텍처 패턴

### 4.1 7-Layer 구조 (모든 모듈 공통)

```
┌─────────────────────────────────────┐
│  7. Controllers (API Endpoints)     │  ← REST API 진입점 (views.py)
├─────────────────────────────────────┤
│  6. Services (Business Logic)       │  ← 핵심 비즈니스 로직 (services.py)
├─────────────────────────────────────┤
│  5. Repositories (Data Access)      │  ← ORM 추상화 (repositories.py)
├─────────────────────────────────────┤
│  4. Clients (External Systems)      │  ← 외부 API 호출 (clients/)
├─────────────────────────────────────┤
│  3. DTOs (Data Transfer Objects)    │  ← API 계약 (serializers.py)
├─────────────────────────────────────┤
│  2. Domain (Entities)                │  ← 도메인 모델 (models.py)
├─────────────────────────────────────┤
│  1. Main (Integration)               │  ← 레이어 간 연결
└─────────────────────────────────────┘
```

**의존성 규칙**: Controller → Service → Repository/Client
- 상위 레이어는 하위 레이어만 참조
- 도메인 모델은 모든 레이어에서 참조 가능

### 4.2 예시: 환자 조회 API (Database Router 방식)

```python
# 1. Controller (views.py) - API 엔드포인트
@api_view(['GET'])
def search_patients(request):
    query = request.GET.get('q')
    patients = PatientService.search(query)  # Service 호출
    return Response(PatientSerializer(patients, many=True).data)

# 2. Service (services.py) - 비즈니스 로직
class PatientService:
    @staticmethod
    def search(query):
        # 1. CDSS DB 캐시 조회 (default DB)
        cached_patients = PatientRepository.search_cache(query)
        if cached_patients.exists():
            return cached_patients

        # 2. OpenEMR DB 직접 조회 (Database Router 자동 라우팅)
        openemr_patients = OpenEMRRepository.search(query)

        # 3. CDSS DB에 Write-Back 캐싱
        for openemr_patient in openemr_patients:
            PatientRepository.upsert_from_openemr(openemr_patient)

        # 4. 캐시에서 재조회 (일관성 보장)
        return PatientRepository.search_cache(query)

# 3. Repository (repositories.py) - 데이터 접근

# CDSS DB Repository (default)
class PatientRepository:
    @staticmethod
    def search_cache(query):
        return Patient.objects.filter(  # 자동으로 using='default'
            Q(full_name__icontains=query) | Q(patient_id__icontains=query)
        )

    @staticmethod
    def upsert_from_openemr(openemr_patient):
        """OpenEMR 데이터를 CDSS DB에 캐싱"""
        Patient.objects.update_or_create(
            openemr_pid=openemr_patient.pid,
            defaults={
                'full_name': f"{openemr_patient.fname} {openemr_patient.lname}",
                'birth_date': openemr_patient.DOB,
                'gender': openemr_patient.sex,
                'ssn': openemr_patient.ss,
                'phone': openemr_patient.phone_home,
            }
        )

# OpenEMR DB Repository (openemr)
class OpenEMRRepository:
    @staticmethod
    def search(query):
        # Database Router가 자동으로 'openemr' DB로 라우팅
        from openemr_models.models import PatientData

        return PatientData.objects.filter(  # 자동으로 using='openemr'
            Q(fname__icontains=query) |
            Q(lname__icontains=query) |
            Q(pubpid__icontains=query)
        )

# 4. OpenEMR Models (openemr_models/models.py)
class PatientData(models.Model):
    """OpenEMR의 patient_data 테이블"""
    pid = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    DOB = models.DateField()
    sex = models.CharField(max_length=30)
    ss = models.CharField(max_length=11)  # SSN
    phone_home = models.CharField(max_length=255)

    class Meta:
        app_label = 'openemr_models'  # Router가 이 app_label 기준 라우팅
        db_table = 'patient_data'  # OpenEMR 실제 테이블명
        managed = False  # Django 마이그레이션 비활성화
```

**데이터 흐름:**
```
1. API 요청: GET /api/emr/patients/?q=홍길동
   ↓
2. PatientService.search('홍길동')
   ↓
3. CDSS DB 조회 (default)
   - Patient.objects.filter(...)
   - Router: using='default'
   ↓
4. 캐시 미스 → OpenEMR DB 조회
   - PatientData.objects.filter(...)
   - Router: using='openemr' (자동 라우팅)
   ↓
5. Write-Back Caching
   - Patient.objects.update_or_create(...)
   - OpenEMR 데이터 → CDSS DB 저장
   ↓
6. API 응답
   - PatientSerializer(cached_patients)
```

---

## 5. 외부 시스템 통합

### 5.1 OpenEMR (전자의무기록)
- **역할**: 환자 정보, 진료 기록, 처방 원천 시스템
- **통신**: Django Database Router (MariaDB 직접 접근)
- **읽기**: Django ORM으로 OpenEMR MariaDB 테이블 직접 조회 (using='openemr')
- **쓰기**: Outbox Pattern (Celery + Redis 비동기 업데이트)
- **데이터**: Patient, Encounter, Order, Medication

**Django Database Router 구조:**
```python
# settings.py
DATABASES = {
    'default': {  # CDSS 메인 DB (MySQL)
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cdss_db',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'openemr': {  # OpenEMR DB (MariaDB)
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'openemr',
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'read_default_file': '/path/to/openemr.cnf',
        }
    }
}

DATABASE_ROUTERS = ['emr.routers.OpenEMRRouter']
```

**자동 라우팅 (emr/routers.py):**
```python
class OpenEMRRouter:
    """
    OpenEMR 앱의 모델은 'openemr' DB로 라우팅
    """
    openemr_app_labels = {'openemr_models'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.openemr_app_labels:
            return 'openemr'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.openemr_app_labels:
            return 'openemr'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # OpenEMR 모델끼리만 관계 허용
        if (obj1._meta.app_label in self.openemr_app_labels and
            obj2._meta.app_label in self.openemr_app_labels):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # OpenEMR DB는 Django 마이그레이션 비활성화
        if app_label in self.openemr_app_labels:
            return db == 'openemr'
        return None
```

**Outbox Pattern (비동기 쓰기):**
```python
# 1. Django에서 OpenEMR 데이터 변경 시 Outbox 테이블에 기록
@transaction.atomic
def create_patient(patient_data):
    # CDSS DB에 환자 생성
    patient = Patient.objects.create(**patient_data)

    # Outbox 테이블에 이벤트 기록
    OutboxEvent.objects.create(
        event_type='PATIENT_CREATED',
        aggregate_id=patient.id,
        payload=patient_data,
        status='PENDING'
    )

# 2. Celery가 Outbox 폴링하여 OpenEMR DB에 비동기 업데이트
@periodic_task(run_every=timedelta(seconds=10))
def process_outbox_events():
    events = OutboxEvent.objects.filter(status='PENDING')[:100]

    for event in events:
        try:
            if event.event_type == 'PATIENT_CREATED':
                # OpenEMR DB에 환자 생성
                openemr_patient = OpenEMRPatient(
                    **event.payload
                )
                openemr_patient.save(using='openemr')

            # Outbox 이벤트 완료 처리
            event.status = 'COMPLETED'
            event.save()

        except Exception as e:
            event.status = 'FAILED'
            event.error = str(e)
            event.retry_count += 1
            event.save()
```

**장점:**
- **성능**: REST API 오버헤드 없이 직접 DB 접근 (10배 빠름)
- **트랜잭션**: Django ORM의 트랜잭션 관리 활용
- **OAuth2 불필요**: 같은 네트워크 내 DB 직접 연결
- **비동기 일관성**: Outbox Pattern으로 Eventually Consistent 보장

### 5.2 Orthanc (PACS 서버)
- **역할**: DICOM 의료 영상 저장/조회
- **통신**: REST API + DICOM-Web (QIDO-RS, WADO-RS, STOW-RS)
- **타임아웃**: 60초 (이미지 처리)
- **포트**: 8042 (HTTP), 4242 (DICOM C-STORE)
- **특징**: HTJ2K 압축 지원, 경량 설계

### 5.3 HAPI FHIR (의료정보 표준 서버)
- **역할**: HL7 FHIR 표준 리소스 변환 및 저장
- **통신**: REST API (JSON)
- **리소스**: Patient, Encounter, DiagnosticReport, ImagingStudy
- **용도**: 외부 병원 연동, 데이터 상호운용성

### 5.4 FastAPI (AI Core)
- **역할**: AI 모델 추론 서버
- **통신**: REST API (내부 네트워크)
- **입력**: HTJ2K 디코딩된 NumPy 배열
- **출력**: 분석 결과 (JSON), 신뢰도, 시각화 이미지

---

## 6. 비동기 처리 아키텍처 (Redis/Celery)

### 6.1 전체 구조

**Redis (전역 독립 서버):**
```
Redis :6379 (중앙 브로커 & 캐시)
  - 역할: 모든 서버의 공통 메시지 브로커 및 캐시
  - Docker: redis:7-alpine
  - 메모리: 256MB (LRU 정책)
  - 영속성: AOF (Append-Only File)
  - 네트워크: neuronova_network
```

**Celery (각 서버별 종속 실행):**
```
┌─────────────────────────────────────────────┐
│  Django Server                              │
│  - Django Process (manage.py runserver)     │
│  - Celery Worker (celery -A cdss_backend)   │
│  - Celery Beat (주기적 작업 스케줄러)          │
│  - 태스크: DICOM 변환, EMR 동기화, 정리 작업   │
└─────────────────────────────────────────────┘
                  ↓ 연결
┌─────────────────────────────────────────────┐
│  Redis :6379 (전역 브로커)                   │
└─────────────────────────────────────────────┘
                  ↑ 연결
┌─────────────────────────────────────────────┐
│  FastAPI Server (AI Core)                   │
│  - FastAPI Process (uvicorn)                │
│  - Celery Worker (celery -A ai_core)        │
│  - 태스크: AI 추론, HTJ2K 디코딩, 전처리       │
└─────────────────────────────────────────────┘
                  ↑ 연결
┌─────────────────────────────────────────────┐
│  HAPI FHIR Server                           │
│  - FHIR Server Process (Java)               │
│  - Celery Worker (celery -A fhir_sync)      │
│  - 태스크: FHIR 리소스 변환, 외부 병원 동기화  │
└─────────────────────────────────────────────┘
```

**설계 철학:**
- **Redis 중앙화**: 모든 비동기 작업의 메시지 브로커를 단일 Redis로 통합
- **Celery 분산화**: 각 서버는 자신의 Celery Worker를 독립 운영
- **태스크 격리**: 각 서버의 태스크는 서로 독립적 (Queue 분리 가능)
- **장애 격리**: 한 서버의 Celery 장애가 다른 서버에 영향 없음

### 6.2 Django Celery 태스크 유형

```python
# 1. DICOM → HTJ2K 변환 (Django)
@shared_task(queue='django_tasks')
def convert_dicom_to_htj2k(instance_id):
    orthanc_client.download(instance_id)
    compress_to_htj2k(dicom_file)
    orthanc_client.upload(htj2k_file)

# 2. AI 분석 트리거 (Django → FastAPI Celery로 위임)
@shared_task(queue='django_tasks')
def trigger_ai_analysis(job_id):
    # FastAPI Celery Queue에 작업 전달
    from ai_core.tasks import ai_inference
    ai_inference.apply_async(args=[job_id], queue='fastapi_tasks')

# 3. FHIR 동기화 (Django → FHIR Celery로 위임)
@shared_task(queue='django_tasks')
def sync_to_fhir(patient_id):
    # FHIR Celery Queue에 작업 전달
    from fhir_sync.tasks import convert_and_upload
    convert_and_upload.apply_async(args=[patient_id], queue='fhir_tasks')

# 4. 주기적 정리 (Django Celery Beat)
@periodic_task(run_every=crontab(hour=2, minute=0))
def cleanup_old_logs():
    AuditLog.objects.filter(created_at__lt=90_days_ago).delete()
```

### 6.3 FastAPI Celery 태스크 유형

```python
# FastAPI AI Core (ai_core/tasks.py)

# AI 추론 작업 (GPU 리소스 사용)
@app.task(queue='fastapi_tasks', bind=True)
def ai_inference(self, job_id):
    # Orthanc에서 HTJ2K 조회
    images = orthanc_client.get_study_images(job_id)

    # HTJ2K 디코딩 (pylibjpeg)
    decoded = decode_htj2k(images)

    # AI 모델 추론
    result = ai_model.predict(decoded)

    # Django DB에 결과 저장 (REST API 호출)
    django_api.post(f'/api/ai/jobs/{job_id}/result/', result)

# 이미지 전처리 작업
@app.task(queue='fastapi_tasks')
def preprocess_images(study_id):
    images = orthanc_client.get_study(study_id)
    normalized = normalize_intensity(images)
    cache.set(f'preprocessed:{study_id}', normalized, timeout=3600)
```

### 6.4 FHIR Celery 태스크 유형

```python
# FHIR Server (fhir_sync/tasks.py)

# FHIR 리소스 변환 및 업로드
@app.task(queue='fhir_tasks')
def convert_and_upload(patient_id):
    # Django에서 환자 데이터 조회
    patient_data = django_api.get(f'/api/emr/patients/{patient_id}/')

    # FHIR Patient 리소스 변환
    fhir_patient = convert_to_fhir_patient(patient_data)

    # HAPI FHIR 서버에 업로드
    fhir_server.create_or_update(fhir_patient)

# 외부 병원 동기화 (주기적)
@app.task(queue='fhir_tasks')
def sync_external_hospital(hospital_id):
    # 외부 병원 FHIR 서버에서 데이터 Pull
    external_patients = external_fhir.search_patients(hospital_id)

    # 로컬 FHIR 서버에 저장
    for patient in external_patients:
        fhir_server.create_or_update(patient)

    # Django DB에도 캐싱
    django_api.post('/api/emr/patients/bulk_sync/', external_patients)
```

### 6.5 실행 방법 (개발 환경)

```bash
# 1. Redis 시작 (전역 독립 서버)
cd NeuroNova_02_back_end/07_redis
docker-compose up -d

# 2. Django + Celery
cd ../02_django_server
venv\Scripts\activate

# Django 서버 (터미널 1)
python manage.py runserver

# Django Celery Worker (터미널 2)
celery -A cdss_backend worker -Q django_tasks -l info --concurrency=4

# Django Celery Beat (터미널 3)
celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 3. FastAPI + Celery
cd ../01_ai_core
source venv/bin/activate

# FastAPI 서버 (터미널 4)
uvicorn main:app --host 0.0.0.0 --port 8001

# FastAPI Celery Worker (터미널 5)
celery -A ai_core worker -Q fastapi_tasks -l info --concurrency=2

# 4. FHIR + Celery (선택사항)
cd ../06_hapi_fhir
source venv/bin/activate

# FHIR Celery Worker (터미널 6)
celery -A fhir_sync worker -Q fhir_tasks -l info --concurrency=2

# 5. Flower 모니터링 (선택사항 - 전체 큐 모니터링)
celery -A cdss_backend flower --port=5555 --broker=redis://localhost:6379/0
```

### 6.6 Queue 분리 전략

```python
# settings.py (Django)
CELERY_TASK_ROUTES = {
    # Django 전용 태스크
    'cdss_backend.tasks.*': {'queue': 'django_tasks'},

    # FastAPI AI 태스크 (외부 호출)
    'ai_core.tasks.*': {'queue': 'fastapi_tasks'},

    # FHIR 태스크 (외부 호출)
    'fhir_sync.tasks.*': {'queue': 'fhir_tasks'},
}

# Celery Worker 우선순위 설정
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # 한 번에 하나씩 처리 (AI 무거운 작업 대비)
```

**장점:**
- **리소스 분리**: AI(GPU), Django(CPU), FHIR(I/O)가 각각 독립적 리소스 사용
- **확장성**: 각 서버의 Worker 수를 독립적으로 조정 가능
- **장애 격리**: 한 서버의 Celery 장애가 다른 서버 영향 없음
- **모니터링 용이**: Queue별로 태스크 상태 추적 가능

---

## 7. 인증/권한 시스템 (RBAC)

### 7.1 JWT 토큰 기반 인증

```
사용자 로그인
  ↓
Django (ID/PW 검증)
  ↓
JWT 토큰 발급:
  - Access Token (1시간)
  - Refresh Token (7일)
  ↓
모든 API 요청 시 Header에 포함:
  Authorization: Bearer <access_token>
  ↓
Django Middleware (JWT 검증)
  - 만료 체크
  - 서명 검증
  - 블랙리스트 확인 (로그아웃 시)
```

### 7.2 역할 기반 권한 (7개 Role)

| Role | 설명 | 주요 권한 |
|------|------|---------|
| admin | 시스템 관리자 | 전체 접근, 사용자 관리 |
| doctor | 의사 | 환자 조회, 처방, 판독문 작성 |
| rib | 영상의학과 의사 | DICOM 조회, 판독문 서명 |
| lab | 검사실 | 검사 결과 입력 |
| nurse | 간호사 | 환자 조회, 바이탈 입력 |
| patient | 환자 | 본인 정보만 조회 |
| external | 외부 연동 | API 전용 계정 |

### 7.3 동적 메뉴 시스템 (RBAC + Menus)

```python
# 1. Role과 Permission 연결
Role: "doctor"
  ├─ Permission: "view_patient"
  ├─ Permission: "create_order"
  └─ Permission: "view_dicom"

# 2. Permission과 Menu 연결
Menu: "환자 관리"
  - required_permission: "view_patient"
  - icon: "users"
  - route: "/patients"

# 3. API 응답 (역할별 메뉴)
GET /api/menus/my-menus/
Response:
[
  {
    "label": "환자 관리",
    "icon": "users",
    "route": "/patients",
    "children": [...]
  }
]
```

---

## 8. 개발 품질 관리

### 8.1 에러 핸들링 표준

```json
// 표준 에러 응답 형식
{
  "error": {
    "code": "ERR_201",
    "message": "환자를 찾을 수 없습니다.",
    "detail": "Patient with ID=12345 not found",
    "field": "patient_id",
    "timestamp": "2026-01-05T10:30:00Z"
  }
}
```

**에러 코드 체계:**
- `ERR_001~099`: 인증/권한
- `ERR_101~199`: 유효성 검증
- `ERR_201~299`: 리소스 없음
- `ERR_301~399`: 충돌/락킹
- `ERR_401~499`: 비즈니스 로직
- `ERR_501~599`: 외부 시스템
- `ERR_500`: 서버 내부 오류

### 8.2 데이터 검증 계층

```
1. Serializer 검증 (형식, 타입, 필수값)
   ↓
2. 커스텀 필드 검증 (validate_<field_name>)
   ↓
3. 객체 수준 검증 (validate() - 다중 필드 관계)
   ↓
4. 비즈니스 로직 검증 (Service Layer)
   ↓
5. DB Constraints (UNIQUE, CHECK, FK)
```

**원칙:**
- **Defensive Programming**: 사용자 입력 절대 신뢰 금지
- **Fail Fast**: 잘못된 데이터는 조기 거부
- **트랜잭션 관리**: `@transaction.atomic` 필수

### 8.3 동시성 제어

```python
# 1. 낙관적 락킹 (Optimistic Locking)
class Patient(models.Model):
    version = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            # UPDATE ... WHERE id=? AND version=?
            affected = Patient.objects.filter(
                pk=self.pk, version=self.version
            ).update(version=F('version') + 1, ...)

            if affected == 0:
                raise ConcurrencyError("데이터가 변경되었습니다.")

# 2. 비관적 락킹 (Pessimistic Locking)
from django.db import transaction

with transaction.atomic():
    patient = Patient.objects.select_for_update().get(pk=patient_id)
    patient.status = 'discharged'
    patient.save()
```

### 8.4 API 자동 문서화 (Swagger)

```python
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="환자 목록 조회",
    description="등록된 모든 환자의 목록을 조회합니다.",
    tags=['emr'],
    responses={200: PatientSerializer(many=True)}
)
@api_view(['GET'])
def list_patients(request):
    ...
```

**접속 URL:**
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

---

## 9. 프로젝트 구조

```
NeuroNova_v1/
├── 00_UML/                      # UML 설계 (PlantUML)
├── 01_doc/                      # 문서 (44개)
│   ├── REF_CLAUDE_CONTEXT.md    # 상세 컨텍스트 (1300줄)
│   ├── 08_API_명세서.md
│   ├── 12_GCP_배포_가이드.md
│   └── ...
├── NeuroNova_02_back_end/
│   ├── 01_ai_core/              # FastAPI (AI)
│   ├── 02_django_server/        # Django 메인
│   │   ├── venv/                # Python 가상환경
│   │   ├── cdss_backend/        # Django 설정
│   │   ├── acct/                # 인증/권한
│   │   ├── rbac/                # RBAC 시스템
│   │   ├── menus/               # 동적 메뉴
│   │   ├── emr/                 # OpenEMR 연동
│   │   ├── ris/                 # 영상의학 (Orthanc)
│   │   ├── ai/                  # AI 오케스트레이션
│   │   ├── alert/               # 실시간 알림
│   │   ├── fhir/                # FHIR 변환
│   │   └── audit/               # 감사 로그
│   ├── 03_openemr_server/       # OpenEMR Docker
│   ├── 04_ohif_viewer/          # OHIF Viewer Docker
│   ├── 05_orthanc_pacs/         # Orthanc Docker
│   ├── 06_hapi_fhir/            # HAPI FHIR Docker
│   └── 07_redis/                # Redis Docker
└── NeuroNova_03_front_end_react/ # React SPA
```

---

## 10. 핵심 설계 원칙

### 10.1 관심사 분리 (Separation of Concerns)
- Controller: HTTP 요청/응답만 처리
- Service: 비즈니스 로직 집중
- Repository: 데이터 접근 추상화
- Client: 외부 시스템 통신 캡슐화

### 10.2 외부 시스템 추상화
```python
# ❌ 나쁜 예: Controller에서 직접 호출
def get_patient(request, patient_id):
    response = requests.get(f"{OPENEMR_URL}/patients/{patient_id}")
    return Response(response.json())

# ✅ 좋은 예: Client 레이어 사용
def get_patient(request, patient_id):
    patient = PatientService.get_patient(patient_id)  # Service
    return Response(PatientSerializer(patient).data)

# Service Layer
class PatientService:
    @staticmethod
    def get_patient(patient_id):
        return OpenEMRClient.get_patient(patient_id)  # Client

# Client Layer
class OpenEMRClient:
    @staticmethod
    def get_patient(patient_id):
        try:
            response = requests.get(
                f"{OPENEMR_URL}/patients/{patient_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise ExternalSystemError(f"OpenEMR 연결 실패: {e}")
```

### 10.3 감사 추적 (Audit Trail)
```python
# 모든 중요 이벤트는 AuditLog에 기록
AuditLog.objects.create(
    user=request.user,
    action='CREATE_ORDER',
    resource_type='RadiologyOrder',
    resource_id=order.id,
    ip_address=get_client_ip(request),
    details={'modality': 'CT', 'body_part': 'brain'}
)
```

### 10.4 Idempotency (멱등성)
```python
# 중복 요청 방지 (X-Idempotency-Key)
@idempotent_request
@api_view(['POST'])
def create_order(request):
    key = request.headers.get('X-Idempotency-Key')

    # 캐시 확인
    cached_response = cache.get(f"idempotency:{key}")
    if cached_response:
        return Response(cached_response, status=200)

    # 새 요청 처리
    order = OrderService.create(request.data)
    response_data = OrderSerializer(order).data

    # 캐시 저장 (24시간)
    cache.set(f"idempotency:{key}", response_data, timeout=86400)
    return Response(response_data, status=201)
```

---

## 11. 실행 방법 (개발 환경)

### 11.1 전제 조건
- Python 3.11+
- Docker & Docker Compose
- MySQL 8.0+
- Node.js 18+ (프론트엔드)

### 11.2 백엔드 실행

```bash
# 1. Redis 시작 (Docker)
cd NeuroNova_02_back_end/07_redis
docker-compose up -d

# 2. Django 서버 (로컬 venv)
cd ../02_django_server
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

python manage.py migrate
python manage.py runserver

# 3. Celery Worker (새 터미널)
celery -A cdss_backend worker -l info --concurrency=4

# 4. Celery Beat (새 터미널)
celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 5. Flower 모니터링 (선택)
celery -A cdss_backend flower --port=5555
```

### 11.3 Orthanc PACS 실행

```bash
cd NeuroNova_02_back_end/05_orthanc_pacs
docker-compose up -d

# 접속: http://localhost:8042
# DICOM Port: 4242
```

### 11.4 OpenEMR 실행

```bash
cd NeuroNova_02_back_end/03_openemr_server
docker-compose up -d

# 접속: http://localhost:8080
```

---

## 12. 주요 API 엔드포인트 예시

### 12.1 인증
```
POST /api/acct/login/          # 로그인
POST /api/acct/logout/         # 로그아웃
GET  /api/acct/me/             # 내 정보
POST /api/acct/token/refresh/  # 토큰 갱신
```

### 12.2 환자 관리 (EMR)
```
GET  /api/emr/patients/                    # 환자 목록
GET  /api/emr/patients/{id}/               # 환자 상세
GET  /api/emr/patients/search/?q=홍길동    # 환자 검색
POST /api/emr/patients/sync/{id}/          # OpenEMR 동기화
```

### 12.3 영상의학 (RIS)
```
GET  /api/ris/orders/                      # 영상 검사 오더 목록
POST /api/ris/orders/                      # 오더 생성
POST /api/ris/upload/dicom/                # DICOM 업로드
GET  /api/ris/studies/{id}/                # Study 상세
POST /api/ris/reports/{id}/sign/           # 판독문 서명
```

### 12.4 AI 분석
```
GET  /api/ai/jobs/                         # AI 작업 목록
POST /api/ai/jobs/                         # AI 분석 요청
GET  /api/ai/jobs/{id}/                    # 작업 상태 조회
POST /api/ai/jobs/{id}/review/             # 결과 검토 (승인/거부)
```

### 12.5 RBAC & Menus
```
GET  /api/rbac/roles/                      # 역할 목록
GET  /api/rbac/permissions/                # 권한 목록
GET  /api/menus/my-menus/                  # 내 권한 기반 메뉴
```

---

## 13. 핵심 학습 포인트

### 13.1 의료 시스템 특수성
1. **HL7 FHIR 표준**: 의료정보 상호운용성 필수
2. **DICOM 표준**: 의료 영상 표준 (메타데이터 + 픽셀 데이터)
3. **감사 추적**: 모든 의료 데이터 접근 기록 (법적 요구사항)
4. **개인정보 보호**: PHI(Protected Health Information) 엄격 관리

### 13.2 성능 최적화 전략
1. **HTJ2K 압축**: 기존 대비 10배 빠른 의료 영상 전송
2. **Redis 캐싱**: 반복 조회 성능 향상 (EMR, FHIR)
3. **ORM 최적화**: `select_related`, `prefetch_related` 필수 (N+1 문제 방지)
4. **비동기 처리**: 무거운 작업(AI, 변환)은 Celery로 분리

### 13.3 마이크로서비스 통합
1. **독립성**: 각 시스템(OpenEMR, Orthanc, FHIR)은 독립 실행
2. **통신**: HTTP REST API 기반 느슨한 결합
3. **장애 격리**: 외부 시스템 장애 시 Django는 계속 작동 (Timeout, Fallback)
4. **데이터 일관성**: Eventual Consistency (최종 일관성) 전략

### 13.4 보안 설계
1. **네트워크 격리**: 내부 시스템(Orthanc, MySQL) 직접 노출 차단
2. **Proxy Pattern**: Django가 JWT 검증 후 Nginx에 위임
3. **최소 권한 원칙**: RBAC으로 역할별 최소 권한만 부여
4. **Token Rotation**: Refresh Token 재발급 시 이전 토큰 무효화

---

## 14. 다른 프로젝트 적용 시 고려사항

### 14.1 필수 적용 요소
- ✅ Layered Architecture (7-Layer)
- ✅ 외부 시스템 Client 레이어 분리
- ✅ 동기/비동기 처리 명확한 구분
- ✅ JWT + RBAC 인증/권한
- ✅ 표준화된 에러 응답
- ✅ Swagger API 문서화

### 14.2 선택적 요소 (프로젝트 특성에 따라)
- HTJ2K: 대용량 이미지 처리가 있는 경우
- FHIR: 의료 시스템 또는 외부 연동이 필요한 경우
- Celery: 장시간 작업, 배치 처리가 많은 경우
- Redis: 고성능 캐싱이 필요한 경우

### 14.3 확장 가능 아키텍처
```
현재: Monolithic Django (11개 앱)
  ↓ (트래픽 증가 시)
마이크로서비스 분리:
  - Auth Service (acct, rbac, menus)
  - EMR Service (emr, ocs, lis)
  - Imaging Service (ris, ai)
  - Integration Service (fhir, audit)

각 서비스:
  - 독립 배포 (Docker)
  - 독립 DB (Database per Service)
  - API Gateway (Kong, AWS API Gateway)
```

---

## 15. 참고 문서

- **상세 컨텍스트**: [01_doc/REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md) (1300줄)
- **API 명세**: [01_doc/08_API_명세서.md](01_doc/08_API_명세서.md)
- **배포 가이드**: [01_doc/12_GCP_배포_가이드.md](01_doc/12_GCP_배포_가이드.md)
- **에러 핸들링**: [01_doc/25_에러_핸들링_가이드.md](01_doc/25_에러_핸들링_가이드.md)
- **데이터 검증**: [01_doc/27_데이터_검증_정책.md](01_doc/27_데이터_검증_정책.md)
- **테스트 전략**: [01_doc/28_테스트_전략_가이드.md](01_doc/28_테스트_전략_가이드.md)

---

**작성자**: NeuroNova CDSS 개발팀
**버전**: v2.1 (2026-01-05)
**라이선스**: 프로젝트 내부 문서
