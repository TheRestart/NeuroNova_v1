# FHIR 동기화 Outbox 패턴 명세서

**문서 ID**: 47_FHIR_동기화_Outbox_패턴_명세서
**버전**: v4.0 (Direct DB Access 적용)
**최종 수정일**: 2026-01-05
**상태**: ✅ 확정

---

## 📋 Changelog

### v4.0 (2026-01-05) - Direct DB Access & Outbox Pattern 통합
- ✅ **Direct DB Access 전면 적용**: OpenEMR 및 FHIR 서버(OpenEMR 내장) 동기화 시 HTTP API 대신 **Django Database Router**를 통한 직접 DB 접근 사용.
- ✅ **Outbox Pattern 강제**: Service Layer에서의 Dual-Write(동시 쓰기)를 제거하고, 모든 외부 동기화를 Outbox -> Async Task 흐름으로 일원화.
- ✅ **SyncOutbox 모델 활용**: 기존 `SyncOutbox` 모델을 유지하며, Payload를 직렬화하여 저장.

---

## 1. Outbox 패턴 개요

### 1.1 기본 원리

**Outbox 패턴**은 분산 시스템에서 **트랜잭션 일관성**을 보장하기 위해 사용됩니다.
로컬 데이터베이스 변경과 "외부 시스템 동기화 요청"을 **하나의 트랜잭션**으로 묶어서 처리합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                  Outbox 패턴 동작 흐름 (Direct DB)           │
└─────────────────────────────────────────────────────────────┘

[1단계] Django API 요청 (예: 환자 등록)
   ↓
[2단계] Django Transaction 시작
   ├─ PatientCache 레코드 INSERT (로컬 DB)
   ├─ SyncOutbox 레코드 INSERT (status='pending')
   └─ COMMIT
   ↓
[3단계] Async Task (Celery) 실행
   ├─ SyncOutbox 조회 (status='pending')
   ├─ **Direct DB Access**: OpenEMR DB에 직접 INSERT/UPDATE
   │   (OpenEMRPatientRepository 사용)
   ├─ 성공 시: status='done', last_synced_at 업데이트
   └─ 실패 시: status='failed', 재시도 스케줄링
```

### 1.2 핵심 변경 사항 (vs v3.0)

| 항목 | 기존 (v3.0) | 변경 (v4.0) |
|------|-------------|-------------|
| **동기화 방식** | HTTP REST API (FHIR) | **Direct DB Access (SQL/ORM)** |
| **연결 방식** | `requests` 라이브러리 | `django.db.connections['openemr']` |
| **Trigger** | Django Signals (Implicit) | **Service Layer Explicit Call** |
| **Consistency** | Eventual Consistency | **Strong Eventual Consistency** (DB 직접 제어) |

---

## 2. 구성 요소 상세

### 2.1 Service Layer (`emr/business_services.py`)

서비스 계층은 비즈니스 로직을 수행하고 **SyncOutbox**를 생성합니다. 외부 시스템(OpenEMR)에 직접 쓰기 작업을 수행하지 않습니다.

```python
# 예시: 환자 생성
with transaction.atomic():
    # 1. 로컬 DB 저장
    patient = PatientRepository.create_patient(data)

    # 2. Outbox 저장
    outbox = SyncOutbox.objects.create(
        entity_type='patient',
        entity_id=patient.patient_id,
        operation='create',
        target_system='openemr', # 또는 'fhir'
        payload=serialize(patient),
        status='pending'
    )

    # 3. 비동기 작업 트리거
    transaction.on_commit(lambda: process_sync_outbox.delay(outbox.outbox_id))
```

### 2.2 Async Task (`emr/tasks.py`)

Celery Worker는 Outbox 메시지를 소비하여 실제 OpenEMR 데이터베이스에 반영합니다.

- **`_sync_to_openemr`**: `OpenEMRPatientRepository` 등을 사용하여 `openemr` DB에 직접 쿼리를 수행합니다.
- **`_sync_to_fhir`**: 사용자 요구사항에 따라 `_sync_to_openemr`와 동일한 메커니즘(Direct DB Access)을 사용하여 처리합니다.

### 2.3 Repositories (`emr/repositories.py`)

실제 데이터베이스 접근을 담당합니다.

- **`PatientRepository`**: 로컬 Django Default DB 접근
- **`OpenEMRPatientRepository`**: OpenEMR DB 접근 (`using('openemr')` 또는 Router 활용)

---

## 3. 데이터베이스 스키마 (SyncOutbox)

```python
class SyncOutbox(models.Model):
    outbox_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    entity_type = models.CharField(max_length=20)   # patient, encounter, order
    entity_id = models.CharField(max_length=100)    # P-2025-xxxxxx
    operation = models.CharField(max_length=10)     # create, update, delete
    target_system = models.CharField(max_length=20) # openemr, fhir
    payload = models.JSONField()                    # 동기화 데이터
    status = models.CharField(max_length=20, default='pending') # pending, processing, done, failed
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True)
```

---

## 4. 트러블슈팅 및 모니터링

1.  **동기화 실패 시**:
    *   `SyncOutbox.status`가 `failed`로 기록됩니다.
    *   `retry_count`가 증가하며, Celery 설정에 따라 자동 재시도됩니다.
    *   `retry_failed_outbox` 태스크가 주기적으로 실패한 항목을 재처리합니다.

2.  **데이터 불일치**:
    *   Direct DB Access를 사용하므로 데이터 형식(Type)이나 스키마 제약조건 위반이 발생할 수 있습니다.
    *   `error_message` 필드를 확인하여 원인을 분석해야 합니다.

3.  **DB 연결 오류**:
    *   OpenEMR DB가 중단된 경우, 로컬 트랜잭션은 성공하고 Outbox에 `pending` 상태로 남습니다.
    *   DB 복구 후 자동으로 재처리됩니다.
