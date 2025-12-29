# FHIR 통합 가이드

**작성일**: 2025-12-29
**버전**: 1.0
**FHIR 버전**: R4 (4.0.1)

---

## 📋 목차

1. [FHIR 개요](#1-fhir-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [지원하는 FHIR 리소스](#3-지원하는-fhir-리소스)
4. [FHIR 서버 설정](#4-fhir-서버-설정)
5. [리소스 변환 (Django → FHIR)](#5-리소스-변환-django--fhir)
6. [동기화 워크플로우](#6-동기화-워크플로우)
7. [OAuth 2.0 인증](#7-oauth-20-인증)
8. [실전 시나리오](#8-실전-시나리오)
9. [트러블슈팅](#9-트러블슈팅)
10. [성능 최적화](#10-성능-최적화)

---

## 1. FHIR 개요

### 1.1 FHIR란?

**FHIR (Fast Healthcare Interoperability Resources)**는 HL7에서 개발한 의료 정보 교환 표준입니다.

**주요 특징**:
- REST API 기반 (HTTP GET/POST/PUT/DELETE)
- JSON/XML 형식 지원
- 모듈화된 리소스 구조
- OAuth 2.0 인증

**CDSS 시스템의 FHIR 사용 목적**:
1. **외부 EMR 시스템과 데이터 교환** (OpenEMR, Epic, Cerner 등)
2. **병원간 환자 정보 공유** (표준 포맷)
3. **AI 분석 결과 전송** (DiagnosticReport)
4. **검사 결과 동기화** (Observation)

---

### 1.2 FHIR R4 vs 이전 버전

| 버전 | 출시일 | 주요 변경사항 |
|------|--------|--------------|
| DSTU2 | 2015 | 초기 안정 버전 |
| STU3 | 2017 | 리소스 구조 개선 |
| **R4** | **2019** | **정식 표준, 대부분의 EHR 지원** |
| R5 | 2023 | 최신 버전 (아직 미지원) |

**CDSS는 R4를 사용합니다** (가장 널리 지원되는 버전)

---

## 2. 시스템 아키텍처

### 2.1 FHIR 통합 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     CDSS 시스템                              │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Django Models│      │ FHIR         │                     │
│  │ (CDSS DB)    │─────>│ Converters   │                     │
│  └──────────────┘      └──────────────┘                     │
│                              │                               │
│                              ▼                               │
│                        ┌──────────────┐                     │
│                        │ FHIR Resource│                     │
│                        │ (JSON)       │                     │
│                        └──────────────┘                     │
│                              │                               │
│                              ▼                               │
│                        ┌──────────────┐                     │
│                        │ Sync Queue   │                     │
│                        │ (비동기)      │                     │
│                        └──────────────┘                     │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
                               │ OAuth 2.0
                               ▼
                    ┌─────────────────────┐
                    │  HAPI FHIR Server   │
                    │  (외부 시스템)       │
                    └─────────────────────┘
                               │
                   ┌───────────┼───────────┐
                   ▼           ▼           ▼
            ┌─────────┐ ┌─────────┐ ┌─────────┐
            │ Epic    │ │ Cerner  │ │ Other   │
            │ EMR     │ │ EMR     │ │ Systems │
            └─────────┘ └─────────┘ └─────────┘
```

---

### 2.2 데이터 흐름

**CDSS → FHIR 서버 (Push)**
```
1. Django Model 생성/수정
2. FHIR Converter가 FHIR Resource로 변환
3. FHIRSyncQueue에 작업 추가
4. Celery Worker가 FHIR 서버로 전송
5. FHIRResourceMap에 ID 매핑 저장
```

**FHIR 서버 → CDSS (Pull)**
```
1. FHIR 서버에서 리소스 조회 (GET)
2. FHIR Resource를 Django Model로 변환
3. CDSS DB에 저장
4. FHIRResourceMap 업데이트
```

---

## 3. 지원하는 FHIR 리소스

### 3.1 전체 리소스 목록 (9개)

| # | 리소스 타입 | Django Model | 용도 | 상태 |
|---|------------|--------------|------|------|
| 1 | **Patient** | PatientCache | 환자 기본 정보 | ✅ 구현 |
| 2 | **Encounter** | Encounter | 진료 기록 | ✅ 구현 |
| 3 | **Observation** | LabResult | 검사 결과 | ✅ 구현 |
| 4 | **DiagnosticReport** | AIJob | AI 분석 결과 | ✅ 구현 |
| 5 | **MedicationRequest** | Order (medication) | 약물 처방 | ✅ 구현 |
| 6 | **ServiceRequest** | Order, RadiologyOrder | 검사/시술 요청 | ✅ 구현 |
| 7 | **Condition** | EncounterDiagnosis | 진단 정보 | ✅ 구현 |
| 8 | **ImagingStudy** | RadiologyStudy | 영상 검사 | ✅ 구현 |
| 9 | **Procedure** | Order (procedure) | 시술 절차 | ✅ 구현 |

---

### 3.2 리소스별 매핑 상세

#### 3.2.1 Patient

**Django Model**: `emr.models.PatientCache`

**FHIR 필드 매핑**:
```json
{
  "resourceType": "Patient",
  "id": "patient_id",
  "name": [{
    "family": "last_name",
    "given": ["first_name"]
  }],
  "gender": "gender (M→male, F→female)",
  "birthDate": "date_of_birth",
  "telecom": ["phone", "email"],
  "address": ["address"]
}
```

**코드 시스템**:
- Identifier: `https://fhir.hospital.com/identifier/patient`

---

#### 3.2.2 Observation (검사 결과)

**Django Model**: `lis.models.LabResult`

**FHIR 필드 매핑**:
```json
{
  "resourceType": "Observation",
  "id": "result_id",
  "status": "final",
  "category": "laboratory",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "test_master.test_code",
      "display": "test_master.test_name"
    }]
  },
  "valueQuantity": {
    "value": "result_value",
    "unit": "result_unit"
  },
  "interpretation": "is_abnormal → H/L/N"
}
```

**코드 시스템**:
- Test Code: LOINC (http://loinc.org)
- Unit: UCUM (http://unitsofmeasure.org)

---

#### 3.2.3 MedicationRequest (약물 처방)

**Django Model**: `emr.models.Order` (order_type='medication')

**FHIR 필드 매핑**:
```json
{
  "resourceType": "MedicationRequest",
  "id": "order_id",
  "status": "active/completed",
  "intent": "order",
  "priority": "routine/urgent/stat",
  "medicationCodeableConcept": {
    "text": "instructions"
  },
  "dosageInstruction": [{
    "text": "instructions"
  }]
}
```

---

#### 3.2.4 ImagingStudy (영상 검사)

**Django Model**: `ris.models.RadiologyStudy`

**FHIR 필드 매핑**:
```json
{
  "resourceType": "ImagingStudy",
  "id": "study_id",
  "identifier": [{
    "system": "urn:dicom:uid",
    "value": "urn:oid:{study_instance_uid}"
  }],
  "status": "available",
  "modality": "CT/MRI/XR",
  "numberOfSeries": "num_series",
  "numberOfInstances": "num_instances",
  "endpoint": [{
    "reference": "WADO-RS URL"
  }]
}
```

**코드 시스템**:
- Modality: DICOM (http://dicom.nema.org/resources/ontology/DCM)

---

## 4. FHIR 서버 설정

### 4.1 HAPI FHIR 서버 설치

**Docker Compose로 설치**:

```yaml
# docker-compose.yml
services:
  hapi-fhir:
    image: hapiproject/hapi:latest
    container_name: cdss-hapi-fhir
    ports:
      - "8080:8080"
    environment:
      - spring.datasource.url=jdbc:postgresql://postgres:5432/hapi
      - spring.datasource.username=hapi
      - spring.datasource.password=SecurePassword123!
      - hapi.fhir.fhir_version=R4
      - hapi.fhir.allow_external_references=true
      - hapi.fhir.allow_multiple_delete=true
      - hapi.fhir.reuse_cached_search_results_millis=60000
    depends_on:
      - postgres
    networks:
      - cdss-network

  postgres:
    image: postgres:14
    container_name: cdss-hapi-postgres
    environment:
      - POSTGRES_DB=hapi
      - POSTGRES_USER=hapi
      - POSTGRES_PASSWORD=SecurePassword123!
    volumes:
      - hapi-data:/var/lib/postgresql/data
    networks:
      - cdss-network

volumes:
  hapi-data:

networks:
  cdss-network:
    driver: bridge
```

**실행**:
```bash
docker compose up -d hapi-fhir postgres

# FHIR 서버 접속 확인
curl http://localhost:8080/fhir/metadata
```

---

### 4.2 Django 설정

**settings.py**:
```python
# FHIR 설정
FHIR_SERVER_URL = os.getenv('FHIR_SERVER_URL', 'http://hapi-fhir:8080/fhir')
FHIR_CLIENT_ID = os.getenv('FHIR_CLIENT_ID', 'cdss-client')
FHIR_CLIENT_SECRET = os.getenv('FHIR_CLIENT_SECRET', 'your-secret')
FHIR_TOKEN_URL = os.getenv('FHIR_TOKEN_URL', 'https://auth.fhir.org/token')
```

**.env**:
```env
FHIR_SERVER_URL=https://fhir.hospital.com/fhir
FHIR_CLIENT_ID=cdss-fhir-client
FHIR_CLIENT_SECRET=your-client-secret-here
FHIR_TOKEN_URL=https://auth.fhir.org/oauth/token
```

---

## 5. 리소스 변환 (Django → FHIR)

### 5.1 Converter 사용법

**기본 4개 리소스**:
```python
from fhir.converters import (
    PatientConverter,
    EncounterConverter,
    ObservationConverter,
    DiagnosticReportConverter
)

# Patient 변환
from emr.models import PatientCache
patient = PatientCache.objects.get(patient_id='P-2025-000001')
fhir_patient = PatientConverter.to_fhir(patient)

# Observation 변환
from lis.models import LabResult
lab_result = LabResult.objects.get(result_id='LR-2025-000789')
fhir_observation = ObservationConverter.to_fhir(lab_result)
```

**추가 5개 리소스**:
```python
from fhir.converters_extended import (
    MedicationRequestConverter,
    ServiceRequestConverter,
    ConditionConverter,
    ImagingStudyConverter,
    ProcedureConverter
)

# MedicationRequest 변환
from emr.models import Order
order = Order.objects.get(order_id='O-2025-000456', order_type='medication')
fhir_medication_request = MedicationRequestConverter.to_fhir(order)

# ImagingStudy 변환
from ris.models import RadiologyStudy
study = RadiologyStudy.objects.get(study_id='uuid-study')
fhir_imaging_study = ImagingStudyConverter.to_fhir(study)
```

---

### 5.2 커스텀 Converter 작성

**새 리소스 타입 추가 시**:

```python
# fhir/converters_custom.py
from typing import Dict
from django.conf import settings
from .converters import FHIRConverter

class AllergyIntoleranceConverter(FHIRConverter):
    """AllergyIntolerance 리소스 컨버터"""

    @staticmethod
    def to_fhir(allergy) -> Dict:
        """Django Allergy 모델 → FHIR AllergyIntolerance Resource"""
        resource = {
            "resourceType": "AllergyIntolerance",
            "id": str(allergy.id),
            "meta": FHIRConverter.get_meta("AllergyIntolerance", allergy.updated_at),
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": "active"
                }]
            },
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": allergy.allergen_code,
                    "display": allergy.allergen_name
                }]
            },
            "patient": {
                "reference": f"Patient/{allergy.patient.patient_id}"
            },
            "reaction": [{
                "manifestation": [{
                    "text": allergy.reaction
                }],
                "severity": allergy.severity  # mild/moderate/severe
            }]
        }
        return resource
```

---

## 6. 동기화 워크플로우

### 6.1 수동 동기화 (API 호출)

**1. 단일 리소스 동기화**:
```bash
curl -X POST https://api.cdss.hospital.com/api/fhir/sync/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "Patient",
    "cdss_id": "P-2025-000001",
    "operation": "create",
    "priority": 5
  }'
```

**2. 대량 동기화 스크립트**:
```python
# scripts/sync_all_patients.py
from fhir.models import FHIRSyncQueue, FHIRResourceMap
from fhir.converters import PatientConverter
from emr.models import PatientCache

# 최근 24시간 내 수정된 환자만 동기화
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)

patients = PatientCache.objects.filter(updated_at__gte=yesterday)

for patient in patients:
    # FHIR 리소스 변환
    fhir_payload = PatientConverter.to_fhir(patient)

    # Resource Map 생성/조회
    resource_map, created = FHIRResourceMap.objects.get_or_create(
        resource_type='Patient',
        cdss_id=patient.patient_id,
        defaults={'fhir_id': f'Patient/{patient.patient_id}'}
    )

    # Sync Queue에 추가
    FHIRSyncQueue.objects.create(
        resource_map=resource_map,
        operation='update' if not created else 'create',
        priority=5,
        payload=fhir_payload
    )

print(f"Synced {patients.count()} patients")
```

**실행**:
```bash
docker exec -it cdss-django-api python scripts/sync_all_patients.py
```

---

### 6.2 자동 동기화 (Signal 기반)

**Django Signals로 자동 동기화**:

```python
# emr/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PatientCache
from fhir.models import FHIRSyncQueue, FHIRResourceMap
from fhir.converters import PatientConverter

@receiver(post_save, sender=PatientCache)
def sync_patient_to_fhir(sender, instance, created, **kwargs):
    """환자 생성/수정 시 자동으로 FHIR 동기화"""

    # FHIR 리소스 변환
    fhir_payload = PatientConverter.to_fhir(instance)

    # Resource Map
    resource_map, _ = FHIRResourceMap.objects.get_or_create(
        resource_type='Patient',
        cdss_id=instance.patient_id,
        defaults={'fhir_id': f'Patient/{instance.patient_id}'}
    )

    # Sync Queue에 추가 (Priority: 생성=10, 수정=5)
    FHIRSyncQueue.objects.create(
        resource_map=resource_map,
        operation='create' if created else 'update',
        priority=10 if created else 5,
        payload=fhir_payload
    )
```

**apps.py에 등록**:
```python
# emr/apps.py
from django.apps import AppConfig

class EmrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emr'

    def ready(self):
        import emr.signals  # Signal 등록
```

---

### 6.3 Celery Worker 구현

**Celery Task 정의**:

```python
# fhir/tasks.py
from celery import shared_task
import requests
from django.conf import settings
from .models import FHIRSyncQueue

@shared_task(bind=True, max_retries=3)
def process_fhir_sync_queue(self, queue_id):
    """FHIR 동기화 큐 처리"""
    try:
        sync_task = FHIRSyncQueue.objects.get(queue_id=queue_id)
        sync_task.mark_as_processing()

        # FHIR 서버 URL 구성
        resource_type = sync_task.resource_map.resource_type
        fhir_id = sync_task.resource_map.fhir_id
        url = f"{settings.FHIR_SERVER_URL}/{fhir_id}"

        # OAuth 2.0 토큰 획득
        token = get_fhir_access_token()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/fhir+json'
        }

        # HTTP 요청 (CREATE/UPDATE)
        if sync_task.operation == 'create':
            response = requests.post(
                f"{settings.FHIR_SERVER_URL}/{resource_type}",
                json=sync_task.payload,
                headers=headers,
                timeout=30
            )
        elif sync_task.operation == 'update':
            response = requests.put(
                url,
                json=sync_task.payload,
                headers=headers,
                timeout=30
            )

        # 응답 처리
        if response.status_code in [200, 201]:
            sync_task.mark_as_completed()
            sync_task.resource_map.last_synced_at = timezone.now()
            sync_task.resource_map.save()
        else:
            raise Exception(f"FHIR Server Error: {response.status_code} - {response.text}")

    except Exception as exc:
        # 재시도 가능한지 확인
        if sync_task.can_retry():
            sync_task.retry_count += 1
            sync_task.save()
            # 재시도 (지수 백오프)
            raise self.retry(exc=exc, countdown=60 * (2 ** sync_task.retry_count))
        else:
            # 최대 재시도 횟수 초과
            sync_task.mark_as_failed(str(exc))

def get_fhir_access_token():
    """OAuth 2.0 Client Credentials Flow로 토큰 획득"""
    response = requests.post(
        settings.FHIR_TOKEN_URL,
        data={
            'grant_type': 'client_credentials',
            'client_id': settings.FHIR_CLIENT_ID,
            'client_secret': settings.FHIR_CLIENT_SECRET,
            'scope': 'system/*.read system/*.write'
        }
    )
    return response.json()['access_token']
```

**Celery Beat 스케줄**:
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'process-fhir-sync-queue': {
        'task': 'fhir.tasks.process_fhir_sync_queue_batch',
        'schedule': crontab(minute='*/5'),  # 5분마다 실행
    },
}
```

---

## 7. OAuth 2.0 인증

### 7.1 Client Credentials Flow

FHIR 서버 접근 시 OAuth 2.0 Client Credentials Grant를 사용합니다.

**흐름**:
```
1. CDSS → Auth Server: POST /oauth/token
   {
     "grant_type": "client_credentials",
     "client_id": "cdss-client",
     "client_secret": "secret",
     "scope": "system/*.read system/*.write"
   }

2. Auth Server → CDSS: 200 OK
   {
     "access_token": "eyJ...",
     "token_type": "Bearer",
     "expires_in": 3600
   }

3. CDSS → FHIR Server: GET /fhir/Patient/123
   Authorization: Bearer eyJ...

4. FHIR Server → CDSS: 200 OK + Patient Resource
```

---

### 7.2 토큰 캐싱

**Redis를 사용한 토큰 캐싱**:

```python
# fhir/auth.py
import requests
from django.core.cache import cache
from django.conf import settings

def get_cached_fhir_token():
    """Redis에서 FHIR 토큰 캐시 조회"""
    token = cache.get('fhir_access_token')

    if not token:
        # 토큰 재발급
        response = requests.post(
            settings.FHIR_TOKEN_URL,
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.FHIR_CLIENT_ID,
                'client_secret': settings.FHIR_CLIENT_SECRET,
                'scope': 'system/*.read system/*.write'
            }
        )
        data = response.json()
        token = data['access_token']
        expires_in = data.get('expires_in', 3600)

        # Redis에 캐시 (만료 10분 전)
        cache.set('fhir_access_token', token, timeout=expires_in - 600)

    return token
```

---

## 8. 실전 시나리오

### 8.1 시나리오 1: 신규 환자 등록

**요구사항**: 신규 환자를 CDSS에 등록하고 FHIR 서버에 동기화

**절차**:
```bash
# 1. CDSS에 환자 생성
curl -X POST https://api.cdss.hospital.com/api/emr/patients/create/ \
  -H "Authorization: Bearer {token}" \
  -d '{
    "family_name": "홍",
    "given_name": "길동",
    "birth_date": "1985-06-15",
    "gender": "male"
  }'

# 응답: {"patient_id": "P-2025-000100"}

# 2. FHIR 동기화 작업 생성 (자동 또는 수동)
curl -X POST https://api.cdss.hospital.com/api/fhir/sync/ \
  -H "Authorization: Bearer {token}" \
  -d '{
    "resource_type": "Patient",
    "cdss_id": "P-2025-000100",
    "operation": "create",
    "priority": 10
  }'

# 3. Celery Worker가 백그라운드에서 처리
# 4. FHIR 서버에 Patient 리소스 생성 완료
```

---

### 8.2 시나리오 2: 검사 결과 전송

**요구사항**: LIS에서 등록된 검사 결과를 FHIR 서버로 전송

**절차**:
```python
# Django Shell
from lis.models import LabResult
from fhir.converters import ObservationConverter
from fhir.models import FHIRSyncQueue, FHIRResourceMap

# 1. 검사 결과 조회
lab_result = LabResult.objects.get(result_id='LR-2025-000789')

# 2. FHIR Observation으로 변환
fhir_observation = ObservationConverter.to_fhir(lab_result)

# 3. Sync Queue에 추가
resource_map, created = FHIRResourceMap.objects.get_or_create(
    resource_type='Observation',
    cdss_id=lab_result.result_id,
    defaults={'fhir_id': f'Observation/{lab_result.result_id}'}
)

FHIRSyncQueue.objects.create(
    resource_map=resource_map,
    operation='create',
    priority=8,  # 검사 결과는 높은 우선순위
    payload=fhir_observation
)

# 4. Celery Worker가 자동 처리
```

---

### 8.3 시나리오 3: AI 분석 결과 공유

**요구사항**: AI 분석 결과를 DiagnosticReport로 변환하여 FHIR 서버에 전송

**절차**:
```python
from ai.models import AIJob
from fhir.converters import DiagnosticReportConverter

# 1. AI Job 조회 (완료된 작업)
ai_job = AIJob.objects.get(job_id=12345, status='completed')

# 2. FHIR DiagnosticReport로 변환
fhir_report = DiagnosticReportConverter.to_fhir(ai_job)

# 3. FHIR 서버로 전송
resource_map, _ = FHIRResourceMap.objects.get_or_create(
    resource_type='DiagnosticReport',
    cdss_id=str(ai_job.job_id),
    defaults={'fhir_id': f'DiagnosticReport/{ai_job.job_id}'}
)

FHIRSyncQueue.objects.create(
    resource_map=resource_map,
    operation='create',
    priority=7,
    payload=fhir_report
)
```

---

## 9. 트러블슈팅

### 9.1 동기화 실패

**증상**: FHIRSyncQueue 상태가 'failed'

**확인 사항**:
```bash
# 1. Sync Queue 조회
docker exec -it cdss-django-api python manage.py shell
from fhir.models import FHIRSyncQueue
failed_tasks = FHIRSyncQueue.objects.filter(status='failed')
for task in failed_tasks:
    print(f"Queue ID: {task.queue_id}")
    print(f"Error: {task.error_message}")
    print(f"Retry Count: {task.retry_count}")

# 2. FHIR 서버 연결 테스트
curl http://hapi-fhir:8080/fhir/metadata

# 3. OAuth 토큰 확인
curl -X POST https://auth.fhir.org/oauth/token \
  -d "grant_type=client_credentials&client_id=cdss-client&client_secret=secret"
```

**해결 방법**:
- FHIR 서버 URL 확인 (`settings.FHIR_SERVER_URL`)
- OAuth 인증 정보 확인 (`FHIR_CLIENT_ID`, `FHIR_CLIENT_SECRET`)
- 네트워크 방화벽 확인
- Celery Worker 재시작: `docker compose restart celery-worker`

---

### 9.2 리소스 변환 오류

**증상**: FHIR Resource JSON 생성 실패

**디버깅**:
```python
from fhir.converters import PatientConverter
from emr.models import PatientCache

patient = PatientCache.objects.get(patient_id='P-2025-000001')

try:
    fhir_resource = PatientConverter.to_fhir(patient)
    print(fhir_resource)
except Exception as e:
    print(f"Conversion Error: {e}")
    import traceback
    traceback.print_exc()
```

**일반적인 원인**:
- 필수 필드 누락 (name, gender, birthDate)
- 날짜 형식 오류 (ISO 8601 필요)
- 코드 시스템 불일치

---

## 10. 성능 최적화

### 10.1 배치 동기화

**대량 리소스 동기화 시**:

```python
# scripts/batch_sync.py
from fhir.models import FHIRSyncQueue
from django.db import transaction

# Pending 상태인 작업 100개씩 배치 처리
pending_tasks = FHIRSyncQueue.objects.filter(
    status='pending'
).order_by('priority', 'created_at')[:100]

with transaction.atomic():
    for task in pending_tasks:
        # Celery Task 비동기 실행
        from fhir.tasks import process_fhir_sync_queue
        process_fhir_sync_queue.delay(task.queue_id)
```

---

### 10.2 압축 전송

**대용량 리소스 압축**:

```python
import gzip
import json

# FHIR Payload 압축
fhir_json = json.dumps(fhir_resource)
compressed_payload = gzip.compress(fhir_json.encode('utf-8'))

# HTTP 요청 시 Content-Encoding 헤더 추가
headers = {
    'Content-Encoding': 'gzip',
    'Content-Type': 'application/fhir+json'
}
```

---

### 10.3 캐싱 전략

**Resource Map 캐싱**:

```python
from django.core.cache import cache

def get_fhir_id_cached(resource_type, cdss_id):
    """Redis에서 FHIR ID 캐시 조회"""
    cache_key = f"fhir_map:{resource_type}:{cdss_id}"
    fhir_id = cache.get(cache_key)

    if not fhir_id:
        from fhir.models import FHIRResourceMap
        try:
            resource_map = FHIRResourceMap.objects.get(
                resource_type=resource_type,
                cdss_id=cdss_id
            )
            fhir_id = resource_map.fhir_id
            # 1시간 캐시
            cache.set(cache_key, fhir_id, timeout=3600)
        except FHIRResourceMap.DoesNotExist:
            return None

    return fhir_id
```

---

## 📚 참고 자료

- **HL7 FHIR 공식 문서**: https://hl7.org/fhir/R4/
- **HAPI FHIR**: https://hapifhir.io/
- **FHIR 리소스 예제**: https://hl7.org/fhir/R4/resourcelist.html
- **LOINC 코드 검색**: https://loinc.org/
- **SNOMED CT**: https://www.snomed.org/

---

**Last Updated**: 2025-12-29
**Version**: 1.0
**Author**: Claude AI
