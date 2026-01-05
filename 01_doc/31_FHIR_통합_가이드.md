# FHIR 통합 가이드

**작성일**: 2026-01-05 (Update)
**버전**: 2.0 (Direct DB Access)
**FHIR 버전**: R4 (4.0.1)

---

## 📋 목차

1. [개요 및 아키텍처 변경](#1-개요-및-아키텍처-변경)
2. [시스템 아키텍처 (Direct DB)](#2-시스템-아키텍처-direct-db)
3. [동기화 프로세스](#3-동기화-프로세스)
4. [FHIR 리소스 매핑](#4-fhir-리소스-매핑)
5. [운영 및 모니터링](#5-운영-및-모니터링)

---

## 1. 개요 및 아키텍처 변경

### 1.1 주요 변경 사항
기존의 HTTP API 기반 동기화 방식에서 **Direct Database Access** 방식으로 변경되었습니다. 이는 성능 향상과 트랜잭션 관리의 단순화를 목적으로 합니다.
OpenEMR 및 내부 FHIR 서버와의 통신은 이제 Django의 **Database Router**를 통해 Database 레벨에서 직접 이루어집니다.

### 1.2 적용 범위
- **OpenEMR Legacy Data**: `patient_data`, `encounters` 등 레거시 테이블 직접 접근
- **FHIR Resources**: FHIR 서버 데이터베이스 영역에 대한 직접 접근 (OpenEMR DB 공유)

---

## 2. 시스템 아키텍처 (Direct DB)

```
┌─────────────────────────────────────────────────────────────┐
│                     CDSS 시스템 (Django)                     │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Local DB     │      │ SyncOutbox   │                   │
│  │ (MySQL)      │◄────►│ (Buffer)     │                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                           │
│                        ┌──────▼──────┐                    │
│                        │ Celery Task │                    │
│                        └──────┬──────┘                    │
│                               │ Direct SQL / ORM          │
│                               ▼                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 OpenEMR Database (MariaDB)            │  │
│  │ ┌──────────────┐   ┌──────────────┐  ┌─────────────┐  │  │
│  │ │ patient_data │   │ encounters   │  │ ...         │  │  │
│  │ └──────────────┘   └──────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**특징**:
- **API 레이어 제거**: OpenEMR API나 FHIR API를 호출하지 않고 DB 포트(3306/3307)로 직접 접속합니다.
- **ORM 활용**: `OpenEMRPatientData` 등 Django Model을 통해 쿼리를 추상화했습니다.
- **비동기 처리**: Outbox 패턴을 사용하여 로컬 작업의 응답 속도를 보장합니다.

---

## 3. 동기화 프로세스

### 3.1 트리거 (Service Layer)
사용자의 요청(환자 생성 등)이 들어오면 `PatientService` 등 비즈니스 로직에서 다음을 수행합니다:
1. 로컬 데이터 저장
2. `SyncOutbox` 데이터 생성 (Payload 포함)
3. `transaction.on_commit`으로 Celery Task 호출

### 3.2 실행 (Celery Worker)
Async Task는 다음 단계를 수행합니다:
1. `SyncOutbox` 상태 확인 (Processing)
2. `OpenEMRPatientRepository` 등을 호출하여 원격 DB에 INSERT/UPDATE
3. 성공 시 Outbox 상태 완료 처리

---

## 4. FHIR 리소스 매핑

DB 직접 접근 방식에서도 데이터의 구조적 맵핑은 중요합니다.

### 4.1 Patient
- **Django**: `PatientCache`
- **OpenEMR Table**: `patient_data`
- **매핑**:
    - `patient_id` -> `pubpid`
    - `given_name` -> `fname`
    - `family_name` -> `lname`
    - `birth_date` -> `DOB`

### 4.2 Encounter
- **Django**: `Encounter`
- **OpenEMR Table**: `encounters`, `forms`
- **매핑**:
    - `encounter_id` -> (Logic to generate sequential ID)
    - `date` -> `date`
    - `chief_complaint` -> `reason`

### 4.3 Order/Prescription
- **Django**: `Order`
- **OpenEMR Table**: `prescriptions`
- **매핑**:
    - `drug_name` -> `drug`
    - `dosage` -> `dosage`

---

## 5. 운영 및 모니터링

### 5.1 환경 변수
Direct DB 접근을 위해 정확한 DB 접속 정보가 필수적입니다.
```env
OPENEMR_DB_HOST=localhost
OPENEMR_DB_PORT=3307
OPENEMR_DB_NAME=openemr
OPENEMR_DB_USER=openemr
OPENEMR_DB_PASSWORD=...
```

### 5.2 재시도 정책
- 일시적 DB 접속 장애 시 Celery의 `max_retries` 설정에 따라 지수 백오프(Exponential Backoff) 방식으로 재시도합니다.
- 영구적 오류(데이터 무결성 위반 등)는 `failed` 상태로 남으며 관리자의 개입이 필요할 수 있습니다.
