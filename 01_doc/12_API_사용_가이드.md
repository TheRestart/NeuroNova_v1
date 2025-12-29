# CDSS API 사용 가이드

**작성일**: 2025-12-29
**버전**: 1.1
**Base URL**: `https://api.cdss.hospital.com/api`

---

## 📋 목차

1. [인증 (Authentication)](#1-인증-authentication)
2. [UC01 - 사용자 인증 및 권한](#2-uc01---사용자-인증-및-권한)
3. [UC02 - EMR 데이터 조회 및 동기화](#3-uc02---emr-데이터-조회-및-동기화)
4. [UC03 - 처방전 관리 (OCS)](#4-uc03---처방전-관리-ocs)
5. [UC04 - 검사 결과 관리 (LIS)](#5-uc04---검사-결과-관리-lis)
6. [UC05 - 영상 검사 관리 (RIS)](#6-uc05---영상-검사-관리-ris)
7. [UC06 - AI 분석 요청 및 결과 조회](#7-uc06---ai-분석-요청-및-결과-조회)
8. [UC07 - 실시간 알림](#8-uc07---실시간-알림)
9. [UC08 - FHIR 의료정보 교환](#9-uc08---fhir-의료정보-교환)
10. [UC09 - 감사 로그 조회](#10-uc09---감사-로그-조회)
11. [에러 핸들링](#11-에러-핸들링)
12. [Rate Limiting](#12-rate-limiting)

---

## 1. 인증 (Authentication)

### 1.1 JWT 토큰 기반 인증

모든 API 요청은 JWT Access Token을 사용합니다.

**토큰 발급**
```bash
POST /api/acct/login/
Content-Type: application/json

{
  "username": "dr.kim",
  "password": "Doctor@123"
}
```

**응답**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "dr.kim",
    "role": "Doctor",
    "email": "dr.kim@hospital.com",
    "department": "신경외과"
  }
}
```

**토큰 사용**
```bash
GET /api/emr/patients/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**토큰 갱신**
```bash
POST /api/acct/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. UC01 - 사용자 인증 및 권한

### 2.1 로그인

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/acct/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr.kim",
    "password": "Doctor@123"
  }'
```

**응답 (200 OK)**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "user_id": "uuid-here",
    "username": "dr.kim",
    "role": "Doctor",
    "permissions": ["view_patient", "create_order", "view_image"]
  }
}
```

### 2.2 내 정보 조회

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/acct/me/ \
  -H "Authorization: Bearer {access_token}"
```

### 2.3 로그아웃

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/acct/logout/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "{refresh_token}"
  }'
```

---

## 3. UC02 - EMR 데이터 조회 및 동기화

### 3.1 환자 목록 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/emr/patients/?limit=10&offset=0" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 150,
  "next": "https://api.cdss.hospital.com/api/emr/patients/?limit=10&offset=10",
  "previous": null,
  "results": [
    {
      "patient_id": "P-2025-000001",
      "family_name": "김",
      "given_name": "철수",
      "birth_date": "1980-05-15",
      "gender": "male",
      "phone": "010-1234-5678",
      "email": "kim@example.com"
    }
  ]
}
```

### 3.2 환자 상세 조회

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/emr/patients/P-2025-000001/ \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "patient_id": "P-2025-000001",
  "family_name": "김",
  "given_name": "철수",
  "full_name": "김철수",
  "birth_date": "1980-05-15",
  "gender": "male",
  "phone": "010-1234-5678",
  "email": "kim@example.com",
  "address": "서울시 강남구",
  "allergies": ["페니실린", "땅콩"],
  "blood_type": "A+",
  "emergency_contact": {
    "name": "김영희",
    "relationship": "배우자",
    "phone": "010-8765-4321"
  },
  "created_at": "2025-01-15T09:00:00Z",
  "updated_at": "2025-01-15T09:00:00Z"
}
```

### 3.3 환자 생성 (Write-Through)

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/emr/patients/create/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "family_name": "이",
    "given_name": "영희",
    "birth_date": "1990-03-20",
    "gender": "female",
    "phone": "010-9999-8888",
    "email": "lee@example.com",
    "address": "서울시 서초구",
    "allergies": [],
    "blood_type": "B+"
  }'
```

**응답 (201 Created)**
```json
{
  "patient_id": "P-2025-000002",
  "openemr_patient_id": "openemr-uuid-123",
  "family_name": "이",
  "given_name": "영희",
  "created_at": "2025-01-20T10:00:00Z"
}
```

### 3.4 진료 기록 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/emr/encounters/?patient_id=P-2025-000001" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 5,
  "results": [
    {
      "encounter_id": "E-2025-000123",
      "patient": "P-2025-000001",
      "doctor_id": "uuid-doctor",
      "encounter_type": "outpatient",
      "department": "신경외과",
      "chief_complaint": "두통",
      "diagnosis": "편두통 (Migraine)",
      "status": "completed",
      "encounter_date": "2025-01-15T14:00:00Z"
    }
  ]
}
```

---

## 4. UC03 - 처방전 관리 (OCS)

### 4.1 약물 마스터 검색

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/ocs/medications/?search=타이레놀" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 3,
  "results": [
    {
      "drug_code": "KDC-123456",
      "drug_name": "타이레놀정 500mg",
      "generic_name": "아세트아미노펜",
      "dosage_form": "정제",
      "strength": "500mg",
      "manufacturer": "한국존슨앤존슨"
    }
  ]
}
```

### 4.2 처방 생성

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/emr/orders/create/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-2025-000001",
    "encounter_id": "E-2025-000123",
    "order_type": "medication",
    "urgency": "routine",
    "instructions": "1일 3회, 식후 30분"
  }'
```

**응답 (201 Created)**
```json
{
  "order_id": "O-2025-000456",
  "patient": "P-2025-000001",
  "encounter": "E-2025-000123",
  "order_type": "medication",
  "status": "pending",
  "urgency": "routine",
  "created_at": "2025-01-15T15:00:00Z"
}
```

### 4.3 진단 마스터 검색

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/ocs/diagnoses/?search=편두통" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 5,
  "results": [
    {
      "diag_code": "G43.0",
      "name_ko": "전조가 없는 편두통",
      "name_en": "Migraine without aura",
      "category": "신경계 질환"
    }
  ]
}
```

---

## 5. UC04 - 검사 결과 관리 (LIS)

### 5.1 검사 마스터 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/lis/lab-tests/?search=혈당" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 2,
  "results": [
    {
      "test_code": "LOINC-2345-7",
      "test_name": "공복혈당 (Fasting Blood Glucose)",
      "sample_type": "Blood",
      "method": "Enzymatic",
      "unit": "mg/dL",
      "reference_range": "70-110"
    }
  ]
}
```

### 5.2 검사 결과 등록

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/lis/lab-results/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "O-2025-000456",
    "patient_id": "P-2025-000001",
    "test_code": "LOINC-2345-7",
    "result_value": "95",
    "result_unit": "mg/dL",
    "is_abnormal": false,
    "reported_by": "uuid-technician"
  }'
```

**응답 (201 Created)**
```json
{
  "result_id": "LR-2025-000789",
  "order": "O-2025-000456",
  "patient": "P-2025-000001",
  "test_master": {
    "test_code": "LOINC-2345-7",
    "test_name": "공복혈당 (Fasting Blood Glucose)"
  },
  "result_value": "95",
  "result_unit": "mg/dL",
  "is_abnormal": false,
  "reported_at": "2025-01-16T09:00:00Z"
}
```

### 5.3 환자별 검사 이력 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/lis/lab-results/by_patient/?patient_id=P-2025-000001" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 15,
  "results": [
    {
      "result_id": "LR-2025-000789",
      "test_name": "공복혈당",
      "result_value": "95",
      "result_unit": "mg/dL",
      "is_abnormal": false,
      "reported_at": "2025-01-16T09:00:00Z"
    }
  ]
}
```

---

## 6. UC05 - 영상 검사 관리 (RIS)

### 6.1 영상 검사 오더 생성

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/ris/radiology-orders/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-2025-000001",
    "modality": "CT",
    "body_part": "Brain",
    "clinical_info": "두통 및 어지럼증",
    "priority": "ROUTINE"
  }'
```

**응답 (201 Created)**
```json
{
  "order_id": "uuid-radiology-order",
  "patient_id": "P-2025-000001",
  "modality": "CT",
  "body_part": "Brain",
  "status": "ORDERED",
  "created_at": "2025-01-17T10:00:00Z"
}
```

### 6.2 Orthanc Study 동기화

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/ris/sync-orthanc-studies/ \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "message": "Synced 15 studies from Orthanc",
  "synced_count": 15,
  "total": 150
}
```

### 6.3 Study 목록 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/ris/radiology-studies/?patient_id=P-2025-000001" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 3,
  "results": [
    {
      "study_id": "uuid-study",
      "orthanc_study_id": "orthanc-internal-id",
      "study_instance_uid": "1.2.840.113619...",
      "patient_name": "김철수",
      "patient_id": "P-2025-000001",
      "study_date": "2025-01-17",
      "study_time": "11:30:00",
      "study_description": "Brain CT",
      "modality": "CT",
      "num_series": 5,
      "num_instances": 150
    }
  ]
}
```

### 6.4 OHIF Viewer로 Study 조회

**OHIF URL 생성**
```bash
# StudyInstanceUID를 사용하여 OHIF Viewer 접속
https://cdss.hospital.com/viewer?StudyInstanceUIDs=1.2.840.113619...
```

### 6.5 판독문 작성

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/ris/radiology-reports/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "uuid-study",
    "findings": "뇌실질 내 특이 소견 없음. 뇌실 크기 정상.",
    "impression": "정상 소견 (Normal study)",
    "status": "PRELIMINARY"
  }'
```

**응답 (201 Created)**
```json
{
  "report_id": "uuid-report",
  "study": "uuid-study",
  "radiologist": "uuid-doctor",
  "findings": "뇌실질 내 특이 소견 없음...",
  "impression": "정상 소견",
  "status": "PRELIMINARY",
  "created_at": "2025-01-17T15:00:00Z"
}
```

### 6.6 판독문 서명

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/ris/radiology-reports/{report_id}/sign/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**응답 (200 OK)**
```json
{
  "report_id": "uuid-report",
  "status": "FINAL",
  "signed_at": "2025-01-17T15:30:00Z",
  "signed_by": "uuid-doctor"
}
```

---

## 7. UC06 - AI 분석 요청 및 결과 조회

### 7.1 AI 분석 작업 제출

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/ai/jobs/submit/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "uuid-study",
    "model_type": "tumor_detection",
    "metadata": {
      "priority": "high",
      "requester": "Dr. Kim"
    }
  }'
```

**응답 (201 Created)**
```json
{
  "job_id": 12345,
  "study_id": "uuid-study",
  "patient_id": "P-2025-000001",
  "analysis_type": "tumor_detection",
  "status": "pending",
  "created_at": "2025-01-18T09:00:00Z",
  "queue_position": 3
}
```

### 7.2 AI Job 상태 조회

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/ai/jobs/12345/ \
  -H "Authorization: Bearer {access_token}"
```

**응답 (200 OK)**
```json
{
  "job_id": 12345,
  "status": "completed",
  "result": {
    "summary": "뇌종양 의심 소견 발견",
    "confidence": 87.5,
    "diagnosis_code": "C71.9",
    "diagnosis_name": "Brain tumor, unspecified",
    "findings": [
      {
        "location": "Right frontal lobe",
        "size": "2.3 cm",
        "probability": 0.875
      }
    ],
    "visualization_url": "https://minio.cdss.hospital.com/ai-artifacts/job-12345/overlay.nii.gz"
  },
  "started_at": "2025-01-18T09:01:00Z",
  "completed_at": "2025-01-18T09:05:30Z",
  "review_status": "under_review"
}
```

### 7.3 AI 결과 승인/반려

**요청 (승인)**
```bash
curl -X POST https://api.cdss.hospital.com/api/ai/jobs/12345/review/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APPROVED",
    "comment": "AI 분석 결과 확인 완료. 추가 MRI 검사 권장."
  }'
```

**응답 (200 OK)**
```json
{
  "job_id": 12345,
  "review_status": "approved",
  "reviewed_by": "uuid-doctor",
  "reviewed_at": "2025-01-18T10:00:00Z",
  "review_comment": "AI 분석 결과 확인 완료..."
}
```

---

## 8. UC07 - 실시간 알림

### 8.1 WebSocket 연결

**연결**
```javascript
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`wss://api.cdss.hospital.com/ws/alerts/?token=${token}`);

ws.onopen = () => {
  console.log('WebSocket Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Alert received:', data);
  // {
  //   "alert_id": "uuid",
  //   "type": "AI_RESULT_READY",
  //   "severity": "high",
  //   "message": "AI 분석 완료: 뇌종양 의심",
  //   "data": {
  //     "job_id": 12345,
  //     "patient_id": "P-2025-000001"
  //   },
  //   "timestamp": "2025-01-18T09:05:30Z"
  // }
};

ws.onerror = (error) => {
  console.error('WebSocket Error:', error);
};

ws.onclose = () => {
  console.log('WebSocket Disconnected');
};
```

### 8.2 알림 타입

| 타입 | 설명 | Severity |
|------|------|----------|
| `AI_RESULT_READY` | AI 분석 완료 | high |
| `CRITICAL_LAB_RESULT` | 위험 검사 결과 | critical |
| `NEW_ORDER` | 신규 처방 | medium |
| `REPORT_SIGNED` | 판독문 서명 완료 | low |
| `PATIENT_ADMITTED` | 환자 입원 | medium |

---

## 9. UC08 - FHIR 의료정보 교환

### 9.1 Patient 리소스 조회

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/fhir/Patient/P-2025-000001/ \
  -H "Authorization: Bearer {access_token}"
```

**응답 (200 OK) - FHIR R4 표준**
```json
{
  "resourceType": "Patient",
  "id": "P-2025-000001",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2025-01-15T09:00:00Z"
  },
  "identifier": [
    {
      "system": "https://fhir.hospital.com/identifier/patient",
      "value": "P-2025-000001"
    }
  ],
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "김",
      "given": ["철수"],
      "text": "김철수"
    }
  ],
  "gender": "male",
  "birthDate": "1980-05-15",
  "telecom": [
    {
      "system": "phone",
      "value": "010-1234-5678",
      "use": "mobile"
    }
  ],
  "address": [
    {
      "use": "home",
      "type": "physical",
      "text": "서울시 강남구"
    }
  ]
}
```

### 9.2 Observation 리소스 조회 (검사 결과)

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/fhir/Observation/LR-2025-000789/ \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "resourceType": "Observation",
  "id": "LR-2025-000789",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "LOINC-2345-7",
        "display": "Fasting Blood Glucose"
      }
    ]
  },
  "subject": {
    "reference": "Patient/P-2025-000001"
  },
  "effectiveDateTime": "2025-01-16T09:00:00Z",
  "valueQuantity": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org"
  },
  "referenceRange": [
    {
      "text": "70-110"
    }
  ]
}
```

### 9.3 MedicationRequest 리소스 조회 (약물 처방)

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/fhir/MedicationRequest/O-2025-000456/ \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "resourceType": "MedicationRequest",
  "id": "O-2025-000456",
  "status": "active",
  "intent": "order",
  "priority": "routine",
  "subject": {
    "reference": "Patient/P-2025-000001",
    "display": "김철수"
  },
  "authoredOn": "2025-01-15T15:00:00Z",
  "requester": {
    "reference": "Practitioner/uuid-doctor"
  },
  "medicationCodeableConcept": {
    "text": "1일 3회, 식후 30분"
  },
  "dosageInstruction": [
    {
      "text": "1일 3회, 식후 30분",
      "timing": {
        "repeat": {
          "frequency": 1,
          "period": 1,
          "periodUnit": "d"
        }
      }
    }
  ]
}
```

### 9.4 ImagingStudy 리소스 조회 (영상 검사)

**요청**
```bash
curl -X GET https://api.cdss.hospital.com/api/fhir/ImagingStudy/{study-uuid}/ \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "resourceType": "ImagingStudy",
  "id": "uuid-study",
  "identifier": [
    {
      "system": "https://fhir.hospital.com/identifier/imagingstudy",
      "value": "uuid-study"
    },
    {
      "system": "urn:dicom:uid",
      "value": "urn:oid:1.2.840.113619..."
    }
  ],
  "status": "available",
  "subject": {
    "reference": "Patient/P-2025-000001",
    "display": "김철수"
  },
  "started": "2025-01-17T11:30:00",
  "numberOfSeries": 5,
  "numberOfInstances": 150,
  "modality": [
    {
      "system": "http://dicom.nema.org/resources/ontology/DCM",
      "code": "CT"
    }
  ],
  "description": "Brain CT",
  "endpoint": [
    {
      "reference": "http://orthanc:8042/dicom-web/studies/1.2.840.113619..."
    }
  ]
}
```

### 9.5 FHIR 동기화 작업 생성

**요청**
```bash
curl -X POST https://api.cdss.hospital.com/api/fhir/sync/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "Patient",
    "cdss_id": "P-2025-000001",
    "operation": "create",
    "priority": 5
  }'
```

**응답 (201 Created)**
```json
{
  "queue_id": 123,
  "resource_map": {
    "resource_type": "Patient",
    "cdss_id": "P-2025-000001",
    "fhir_id": "Patient/P-2025-000001"
  },
  "operation": "create",
  "status": "pending",
  "priority": 5,
  "payload": {
    "resourceType": "Patient",
    "id": "P-2025-000001",
    ...
  },
  "created_at": "2025-01-20T10:00:00Z"
}
```

---

## 10. UC09 - 감사 로그 조회

### 10.1 로그 목록 조회

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/audit/logs/?action=CREATE&app=emr" \
  -H "Authorization: Bearer {access_token}"
```

**응답**
```json
{
  "count": 50,
  "results": [
    {
      "log_id": 1001,
      "user": {
        "user_id": "uuid",
        "username": "dr.kim"
      },
      "action": "CREATE",
      "app_label": "emr",
      "model_name": "PatientCache",
      "object_id": "P-2025-000001",
      "change_summary": "환자 등록: 김철수",
      "ip_address": "192.168.1.100",
      "created_at": "2025-01-15T09:00:00Z"
    }
  ]
}
```

### 10.2 로그 검색

**요청**
```bash
curl -X GET "https://api.cdss.hospital.com/api/audit/logs/?search=김철수" \
  -H "Authorization: Bearer {access_token}"
```

---

## 11. 에러 핸들링

### 11.1 표준 에러 응답 형식

```json
{
  "error": {
    "code": "ERR_001",
    "message": "인증에 실패했습니다.",
    "details": "Invalid credentials",
    "timestamp": "2025-01-20T10:00:00Z"
  }
}
```

### 11.2 HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 (검증 실패) |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 429 | Too Many Requests | Rate Limit 초과 |
| 500 | Internal Server Error | 서버 오류 |
| 503 | Service Unavailable | 서비스 일시 중단 |

### 11.3 에러 코드

| 코드 | 설명 |
|------|------|
| ERR_001 | 인증 실패 |
| ERR_002 | 권한 없음 |
| ERR_003 | 유효성 검증 실패 |
| ERR_004 | 리소스 없음 |
| ERR_005 | 중복 리소스 |
| ERR_006 | 외부 시스템 연동 실패 (OpenEMR, Orthanc 등) |
| ERR_007 | AI 분석 실패 |

---

## 12. Rate Limiting

### 12.1 제한 정책

| 역할 | 요청 제한 | 기간 |
|------|----------|------|
| Patient | 100 requests | 1시간 |
| Nurse | 500 requests | 1시간 |
| Doctor | 1000 requests | 1시간 |
| Admin | Unlimited | - |

### 12.2 Rate Limit 헤더

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642684800
```

### 12.3 Rate Limit 초과 응답

```json
{
  "error": {
    "code": "ERR_RATE_LIMIT",
    "message": "요청 횟수 제한을 초과했습니다.",
    "retry_after": 3600,
    "timestamp": "2025-01-20T10:00:00Z"
  }
}
```

---

## 📚 참고 자료

- **Swagger UI**: `https://api.cdss.hospital.com/api/docs/`
- **ReDoc**: `https://api.cdss.hospital.com/api/redoc/`
- **OpenAPI Schema**: `https://api.cdss.hospital.com/api/schema/`

---

**Last Updated**: 2025-12-29
**Version**: 1.1
**Author**: Claude AI
