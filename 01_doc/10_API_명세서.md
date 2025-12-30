# CDSS API 명세서

**작성일**: 2025-12-19
**버전**: 1.0
**Base URL**: `http://localhost:8000/api` (개발), `https://api.cdss.hospital.com/api` (프로덕션)

---

## 📋 목차

1. [인증 (Authentication)](#1-인증-authentication)
2. [UC1 - ACCT (인증/권한)](#2-uc1---acct-인증권한)
3. [UC2 - EMR (전자의무기록)](#3-uc2---emr-전자의무기록)
4. [UC3 - OCS (처방전달)](#4-uc3---ocs-처방전달)
5. [UC4 - LIS (임상병리)](#5-uc4---lis-임상병리)
6. [UC5 - RIS (영상의학)](#6-uc5---ris-영상의학)
7. [UC6 - AI (AI 오케스트레이션)](#7-uc6---ai-ai-오케스트레이션)
8. [UC7 - ALERT (알림)](#8-uc7---alert-알림)
9. [UC8 - FHIR (의료정보 교환)](#9-uc8---fhir-의료정보-교환)
10. [UC9 - AUDIT (감사 로그)](#10-uc9---audit-감사-로그)
11. [공통 에러 코드](#11-공통-에러-코드)
12. [API 사용 예시](#12-api-사용-예시)

---

## 1. 인증 (Authentication)

### 인증 방식
- **JWT (JSON Web Token)** 기반
- **Access Token**: 30분 유효 (헤더에 포함)
- **Refresh Token**: 7일 유효 (갱신용)

### 헤더 포맷
```http
Authorization: Bearer <access_token>
```

### 역할 (Roles)
- `admin`: 시스템 관리자
- `doctor`: 신경외과 의사
- `rib`: 방사선과
- `lab`: 검사실
- `nurse`: 간호사
- `patient`: 일반 환자
- `external`: 외부 기관

---

## 2. UC1 - ACCT (인증/권한)

### 회원가입 정책

**기본 정책** (현재 운영 방침):
- **환자(Patient)**: 자가 회원가입 가능
- **의료진 및 관리자**: Admin이 계정 생성 후 ID/PW 공지
  - Doctor, RIB, Lab, Nurse, External 역할은 Admin만 생성 가능
  - 보안 강화 및 내부 인력 관리 목적

**API 구현 상태**:
- 모든 역할의 회원가입 API는 구현되어 있음 (정책 변경 대비)
- 프론트엔드에서 Patient만 회원가입 UI 노출
- Admin은 전용 계정 생성 UI 사용

---

### 2.1 회원가입 (Patient 자가 가입 / Admin 계정 생성)

**POST** `/acct/register/`

**설명**:
- **Patient**: 자가 회원가입 (일반 사용자용)
- **의료진**: Admin이 계정 생성 (내부 관리용)

**요청 Body**
```json
{
  "username": "patient001",
  "password": "SecureP@ss123",
  "email": "patient@example.com",
  "role": "patient",
  "firstName": "홍",
  "lastName": "길동",
  "phone": "010-1234-5678"
}
```

**의료진 계정 생성 (Admin만 가능)**
```json
{
  "username": "dr.kim",
  "password": "TempP@ss123",
  "email": "dr.kim@hospital.com",
  "role": "doctor",
  "employeeId": "D-2024-001",
  "department": "신경외과",
  "firstName": "김",
  "lastName": "의사",
  "phone": "010-9999-0000"
}
```

**응답 (201 Created)**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "patient001",
  "email": "patient@example.com",
  "role": "patient",
  "message": "회원가입이 완료되었습니다."
}
```

**에러 응답**
```json
// 403 Forbidden (의료진 계정 생성 시도)
{
  "error": "permission_denied",
  "message": "의료진 계정은 관리자만 생성할 수 있습니다."
}

// 400 Bad Request
{
  "error": "validation_error",
  "message": "이미 존재하는 사용자명입니다."
}
```

**권한**:
- Patient 가입: 인증 불필요 (AllowAny)
- 의료진 계정 생성: Admin 권한 필요 (IsAdmin)

---

### 2.2 로그인

**POST** `/acct/login/`

**설명**: 사용자 인증 후 JWT 토큰 발급

**요청 Body**
```json
{
  "username": "dr.kim",
  "password": "SecureP@ss123"
}
```

**응답 (200 OK)**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "dr.kim",
    "email": "dr.kim@hospital.com",
    "role": "doctor",
    "employeeId": "D-2024-001",
    "department": "신경외과",
    "permissions": [
      "patient.view",
      "patient.edit",
      "order.create",
      "report.sign",
      "ai_result.approve"
    ]
  }
}
```

**에러 응답**
```json
// 401 Unauthorized
{
  "error": "invalid_credentials",
  "message": "아이디 또는 비밀번호가 올바르지 않습니다."
}

// 423 Locked
{
  "error": "account_locked",
  "message": "계정이 잠겼습니다. 관리자에게 문의하세요.",
  "locked_until": "2025-12-19T15:30:00Z"
}
```

---

### 2.3 토큰 갱신

**POST** `/acct/token/refresh/`

**설명**: Refresh Token으로 새로운 Access Token 발급

**요청 Body**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답 (200 OK)**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2.4 로그아웃

**POST** `/acct/logout/`

**설명**: Refresh Token 무효화

**헤더**
```http
Authorization: Bearer <access_token>
```

**요청 Body**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답 (204 No Content)**

---

### 2.5 현재 사용자 정보 조회

**GET** `/acct/me/`

**설명**: 현재 인증된 사용자 정보 조회

**헤더**
```http
Authorization: Bearer <access_token>
```

**응답 (200 OK)**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "dr.kim",
  "email": "dr.kim@hospital.com",
  "role": "doctor",
  "employeeId": "D-2024-001",
  "department": "신경외과",
  "phone": "010-1234-5678",
  "createdAt": "2024-01-15T09:00:00Z",
  "lastLogin": "2025-12-19T14:30:00Z"
}
```

**권한**: 모든 인증된 사용자

---

### 2.6 사용자 목록 조회

**GET** `/acct/users/`

**설명**: 사용자 목록 조회 (관리자 전용)

**Query Parameters**
- `role` (optional): 역할 필터링 (`admin`, `doctor`, `rib`, `lab`, `nurse`, `patient`, `external`)
- `department` (optional): 부서 필터링
- `page` (optional): 페이지 번호 (기본: 1)
- `page_size` (optional): 페이지 크기 (기본: 20)

**응답 (200 OK)**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/acct/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "dr.kim",
      "email": "dr.kim@hospital.com",
      "role": "doctor",
      "department": "신경외과",
      "isActive": true,
      "createdAt": "2024-01-15T09:00:00Z"
    }
  ]
}
```

**권한**: `admin`

---

## 3. UC2 - EMR (전자의무기록)

### 3.1 환자 검색

**GET** `/emr/patients/search/`

**설명**: 환자 검색 (이름, 생년월일, 환자번호)

**Query Parameters**
- `q` (required): 검색어 (이름, 환자번호)
- `birth_date` (optional): 생년월일 (YYYY-MM-DD)
- `page` (optional): 페이지 번호

**응답 (200 OK)**
```json
{
  "count": 5,
  "results": [
    {
      "patientId": "P-2024-001234",
      "familyName": "김",
      "givenName": "철수",
      "birthDate": "1980-05-15",
      "gender": "male",
      "phone": "010-9876-5432",
      "lastVisit": "2025-12-10T14:00:00Z"
    }
  ]
}
```

**권한**: `admin`, `doctor`, `rib`, `lab`, `nurse`

---

### 3.2 환자 상세 조회

**GET** `/emr/patients/{patientId}/`

**설명**: 환자 상세 정보 조회

**Path Parameters**
- `patientId`: 환자 ID (예: `P-2024-001234`)

**응답 (200 OK)**
```json
{
  "patientId": "P-2024-001234",
  "familyName": "김",
  "givenName": "철수",
  "birthDate": "1980-05-15",
  "gender": "male",
  "phone": "010-9876-5432",
  "email": "kim.cs@example.com",
  "address": "서울특별시 강남구 테헤란로 123",
  "emergencyContact": {
    "name": "김영희",
    "relationship": "배우자",
    "phone": "010-1111-2222"
  },
  "allergies": ["페니실린", "땅콩"],
  "bloodType": "A+",
  "lastVisit": "2025-12-10T14:00:00Z",
  "createdAt": "2024-01-15T09:00:00Z"
}
```

**권한**:
- `admin`, `doctor`, `rib`, `lab`, `nurse`: 모든 환자 조회
- `patient`: 본인만 조회

---

### 3.3 환자 진료 기록 조회

**GET** `/emr/patients/{patientId}/encounters/`

**설명**: 환자 진료 기록 (타임라인)

**Query Parameters**
- `from_date` (optional): 시작 날짜 (YYYY-MM-DD)
- `to_date` (optional): 종료 날짜 (YYYY-MM-DD)
- `page` (optional): 페이지 번호

**응답 (200 OK)**
```json
{
  "count": 12,
  "results": [
    {
      "encounterId": "E-2025-005678",
      "date": "2025-12-10T14:00:00Z",
      "type": "외래",
      "department": "신경외과",
      "doctor": {
        "name": "김의사",
        "employeeId": "D-2024-001"
      },
      "chiefComplaint": "두통, 어지러움",
      "diagnosis": "편두통 의심",
      "status": "completed"
    }
  ]
}
```

**권한**:
- `admin`, `doctor`, `nurse`: 모든 환자 조회
- `patient`: 본인만 조회

---

## 4. UC3 - OCS (처방전달)

### 4.1 처방 생성

**POST** `/ocs/orders/`

**설명**: 새로운 처방 생성

**요청 Body**
```json
{
  "patientId": "P-2024-001234",
  "encounterId": "E-2025-005678",
  "orderType": "medication",
  "orderItems": [
    {
      "drugCode": "DRG-001",
      "drugName": "아스피린 100mg",
      "dosage": "1정",
      "frequency": "1일 1회",
      "duration": "7일",
      "route": "경구",
      "instructions": "식후 30분"
    }
  ],
  "urgency": "routine",
  "notes": "혈압 모니터링 필요"
}
```

**응답 (201 Created)**
```json
{
  "orderId": "O-2025-009876",
  "patientId": "P-2024-001234",
  "orderType": "medication",
  "status": "pending",
  "orderedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "orderedAt": "2025-12-19T15:00:00Z",
  "orderItems": [
    {
      "itemId": "OI-001",
      "drugCode": "DRG-001",
      "drugName": "아스피린 100mg",
      "dosage": "1정",
      "frequency": "1일 1회",
      "duration": "7일"
    }
  ]
}
```

**권한**: `admin`, `doctor`

---

### 4.2 처방 조회

**GET** `/ocs/orders/{orderId}/`

**설명**: 처방 상세 조회

**응답 (200 OK)**
```json
{
  "orderId": "O-2025-009876",
  "patientId": "P-2024-001234",
  "orderType": "medication",
  "status": "completed",
  "orderedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "executedBy": {
    "name": "박간호사",
    "employeeId": "N-2024-015"
  },
  "orderedAt": "2025-12-19T15:00:00Z",
  "executedAt": "2025-12-19T16:30:00Z"
}
```

**권한**: `admin`, `doctor`, `nurse`, `patient` (본인만)

---

### 4.3 약물/진단 마스터 조회

**GET** `/ocs/medications/`
**GET** `/ocs/diagnoses/`

**설명**: 표준 코드 정보 조회 및 검색

---

## 5. UC4 - LIS (임상병리)

### 5.1 검사 오더 생성

**POST** `/lis/test-orders/`

**설명**: 검사 오더 생성

**요청 Body**
```json
{
  "patientId": "P-2024-001234",
  "encounterId": "E-2025-005678",
  "testType": "blood",
  "testItems": [
    {
      "testCode": "CBC",
      "testName": "전혈구검사"
    },
    {
      "testCode": "LFT",
      "testName": "간기능검사"
    }
  ],
  "urgency": "stat",
  "notes": "금식 상태 확인"
}
```

**응답 (201 Created)**
```json
{
  "testOrderId": "TO-2025-003456",
  "patientId": "P-2024-001234",
  "status": "pending",
  "orderedAt": "2025-12-19T15:00:00Z",
  "testItems": [
    {
      "testCode": "CBC",
      "testName": "전혈구검사",
      "status": "pending"
    }
  ]
}
```

**권한**: `admin`, `doctor`

---

### 5.2 검사 결과 입력

**POST** `/lis/test-results/`

**설명**: 검사 결과 입력 (검사실 전용)

**요청 Body**
```json
{
  "testOrderId": "TO-2025-003456",
  "testCode": "CBC",
  "results": {
    "WBC": {
      "value": 7500,
      "unit": "/μL",
      "referenceRange": "4000-10000",
      "flag": "normal"
    },
    "RBC": {
      "value": 4.5,
      "unit": "M/μL",
      "referenceRange": "4.0-5.5",
      "flag": "normal"
    },
    "Hemoglobin": {
      "value": 13.2,
      "unit": "g/dL",
      "referenceRange": "12.0-16.0",
      "flag": "normal"
    }
  },
  "performedBy": "L-2024-007",
  "performedAt": "2025-12-19T16:00:00Z",
  "verifiedBy": "L-2024-001"
}
```

**응답 (201 Created)**
```json
{
  "resultId": "TR-2025-001234",
  "testOrderId": "TO-2025-003456",
  "testCode": "CBC",
  "status": "completed",
  "hasAbnormal": false,
  "performedAt": "2025-12-19T16:00:00Z"
}
```

**권한**: `admin`, `lab`

---

## 6. UC5 - RIS (영상의학)

### 6.1 영상 오더 생성

**POST** `/ris/radiology-orders/`

**설명**: 영상 검사 오더 생성

**요청 Body**
```json
{
  "patientId": "P-2024-001234",
  "encounterId": "E-2025-005678",
  "modalityType": "MRI",
  "bodyPart": "Brain",
  "clinicalInfo": "두통, 어지러움, 편두통 의심",
  "urgency": "routine",
  "contrast": true,
  "notes": "조영제 알레르기 확인 완료"
}
```

**응답 (201 Created)**
```json
{
  "orderId": "RO-2025-007890",
  "patientId": "P-2024-001234",
  "modalityType": "MRI",
  "bodyPart": "Brain",
  "status": "scheduled",
  "orderedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "orderedAt": "2025-12-19T15:00:00Z",
  "scheduledAt": "2025-12-20T10:00:00Z"
}
```

**권한**: `admin`, `doctor`

---

### 6.2 스터디 조회

**GET** `/ris/studies/{studyId}/`

**설명**: 영상 스터디 조회

**응답 (200 OK)**
```json
{
  "studyId": "ST-2025-001234",
  "studyInstanceUID": "1.2.840.113619.2.55.1.1234567890.123456",
  "patientId": "P-2024-001234",
  "modalityType": "MRI",
  "bodyPart": "Brain",
  "studyDate": "2025-12-20T10:00:00Z",
  "status": "completed",
  "seriesCount": 8,
  "instanceCount": 240,
  "orthancStudyId": "a1b2c3d4-e5f6-4a5b-8c7d-9e8f7a6b5c4d",
  "wadoUrl": "http://orthanc.hospital.com/wado-rs/studies/a1b2c3d4-e5f6-4a5b-8c7d-9e8f7a6b5c4d"
}
```

**권한**: `admin`, `doctor`, `rib`, `patient` (본인만)

---

### 6.3 판독문 작성

**POST** `/ris/reports/`

**설명**: 판독문 작성 (의사 전용)

**요청 Body**
```json
{
  "studyId": "ST-2025-001234",
  "findings": "뇌 MRI 소견:\n1. 좌측 두정엽에 약 1.5cm 크기의 고강도 신호 병변 관찰\n2. 주변 부종 소견 동반\n3. 중심선 편위 없음",
  "impression": "좌측 두정엽 종양 의심. 추가 조직검사 권고",
  "recommendation": "신경외과 협진, MR Spectroscopy 추가 검사",
  "status": "preliminary"
}
```

**응답 (201 Created)**
```json
{
  "reportId": "RP-2025-005678",
  "studyId": "ST-2025-001234",
  "status": "preliminary",
  "reportedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "reportedAt": "2025-12-20T14:30:00Z"
}
```

**권한**: `admin`, `doctor`

---

### 6.4 판독문 서명

**POST** `/ris/reports/{reportId}/sign/`

**설명**: 판독문 전자서명 (최종 확정)

**요청 Body**
```json
{
  "signature": "digitally_signed_hash_value",
  "password": "doctor_password"
}
```

**응답 (200 OK)**
```json
{
  "reportId": "RP-2025-005678",
  "status": "final",
  "signedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "signedAt": "2025-12-20T15:00:00Z"
}
```

**권한**: `admin`, `doctor`

---

## 7. UC6 - AI (AI 오케스트레이션)

### 7.1 AI 분석 요청

**POST** `/ai/jobs/`

**설명**: AI 분석 작업 생성 (MRI 종양 분석)

**요청 Body**
```json
{
  "studyId": "ST-2025-001234",
  "analysisType": "mri_tumor_detection",
  "parameters": {
    "model": "unet_v2",
    "confidence_threshold": 0.85
  },
  "priority": "high"
}
```

**응답 (202 Accepted)**
```json
{
  "jobId": "AI-2025-001234",
  "studyId": "ST-2025-001234",
  "analysisType": "mri_tumor_detection",
  "status": "queued",
  "queuePosition": 3,
  "estimatedTime": "5-10분",
  "createdAt": "2025-12-20T15:00:00Z"
}
```

**권한**: `admin`, `doctor`

---

### 7.2 AI 작업 상태 조회

**GET** `/ai/jobs/{jobId}/`

**설명**: AI 작업 진행 상태 조회

**응답 (200 OK)**
```json
{
  "jobId": "AI-2025-001234",
  "status": "processing",
  "progress": 65,
  "currentStep": "Segmentation",
  "startedAt": "2025-12-20T15:05:00Z",
  "estimatedCompletion": "2025-12-20T15:12:00Z"
}
```

**상태 값**
- `queued`: 대기 중
- `processing`: 분석 중
- `completed`: 완료
- `failed`: 실패

**권한**: `admin`, `doctor`

---

### 7.3 AI 결과 조회

**GET** `/ai/results/{resultId}/`

**설명**: AI 분석 결과 조회

**응답 (200 OK)**
```json
{
  "resultId": "AR-2025-001234",
  "jobId": "AI-2025-001234",
  "studyId": "ST-2025-001234",
  "analysisType": "mri_tumor_detection",
  "status": "pending_review",
  "findings": {
    "tumor_detected": true,
    "tumor_location": "Left Parietal Lobe",
    "tumor_volume_ml": 12.5,
    "confidence": 0.92,
    "grade_prediction": "Grade II Glioma",
    "grade_confidence": 0.87
  },
  "artifacts": {
    "segmentation_mask": "s3://minio/ai-artifacts/AR-2025-001234/mask.nii.gz",
    "heatmap": "s3://minio/ai-artifacts/AR-2025-001234/heatmap.png",
    "report_pdf": "s3://minio/ai-artifacts/AR-2025-001234/report.pdf"
  },
  "completedAt": "2025-12-20T15:10:00Z",
  "approvedBy": null,
  "approvedAt": null
}
```

**권한**: `admin`, `doctor`

---

### 7.4 AI 결과 승인

**POST** `/ai/results/{resultId}/approve/`

**설명**: 의사가 AI 결과 최종 승인

**요청 Body**
```json
{
  "approved": true,
  "comments": "AI 분석 결과 확인. 조직검사 권고 동의"
}
```

**응답 (200 OK)**
```json
{
  "resultId": "AR-2025-001234",
  "status": "approved",
  "approvedBy": {
    "name": "김의사",
    "employeeId": "D-2024-001"
  },
  "approvedAt": "2025-12-20T16:00:00Z"
}
```

**권한**: `admin`, `doctor`

---

## 8. UC7 - ALERT (알림)

### 8.1 알림 목록 조회

**GET** `/alerts/`

**설명**: 사용자 알림 목록 조회

**Query Parameters**
- `status` (optional): 알림 상태 (`unread`, `read`, `all`)
- `type` (optional): 알림 타입 (`order`, `result`, `ai`, `system`)
- `page` (optional): 페이지 번호

**응답 (200 OK)**
```json
{
  "unreadCount": 5,
  "count": 23,
  "results": [
    {
      "alertId": "AL-2025-001234",
      "type": "ai_result",
      "title": "AI 분석 완료",
      "message": "환자 김철수(P-2024-001234)의 MRI AI 분석이 완료되었습니다.",
      "severity": "info",
      "isRead": false,
      "data": {
        "resultId": "AR-2025-001234",
        "patientId": "P-2024-001234"
      },
      "createdAt": "2025-12-20T15:10:00Z"
    },
    {
      "alertId": "AL-2025-001235",
      "type": "lab_result",
      "title": "이상 검사 결과",
      "message": "환자 이영희(P-2024-005678)의 간기능검사에서 이상 소견이 발견되었습니다.",
      "severity": "warning",
      "isRead": false,
      "data": {
        "testOrderId": "TO-2025-003456",
        "abnormalTests": ["AST", "ALT"]
      },
      "createdAt": "2025-12-20T14:30:00Z"
    }
  ]
}
```

**권한**: 모든 인증된 사용자

---

### 8.2 알림 읽음 처리

**PUT** `/alerts/{alertId}/read/`

**설명**: 알림을 읽음으로 표시

**응답 (200 OK)**
```json
{
  "alertId": "AL-2025-001234",
  "isRead": true,
  "readAt": "2025-12-20T16:00:00Z"
}
```

**권한**: 알림 소유자

---

### 8.3 WebSocket 연결 (실시간 알림)

**WebSocket** `ws://localhost:8000/ws/alerts/`

**설명**: 실시간 알림 수신

**연결 시 헤더**
```
Authorization: Bearer <access_token>
```

**수신 메시지 예시**
```json
{
  "type": "new_alert",
  "alert": {
    "alertId": "AL-2025-001236",
    "type": "order",
    "title": "새 처방",
    "message": "환자 김철수의 새 처방이 등록되었습니다.",
    "severity": "info",
    "createdAt": "2025-12-20T16:15:00Z"
  }
}
```

---

## 9. UC8 - FHIR (의료정보 교환)

### 9.1 FHIR 리소스 조회

**GET** `/fhir/Patient/{patientId}/`

**설명**: FHIR Patient 리소스 조회

**응답 (200 OK)**
```json
{
  "resourceType": "Patient",
  "id": "P-2024-001234",
  "identifier": [
    {
      "system": "http://hospital.com/patient-id",
      "value": "P-2024-001234"
    }
  ],
  "name": [
    {
      "family": "김",
      "given": ["철수"]
    }
  ],
  "gender": "male",
  "birthDate": "1980-05-15",
  "telecom": [
    {
      "system": "phone",
      "value": "010-9876-5432"
    }
  ]
}
```

**권한**: `admin`, `external`

---

### 9.2 FHIR 동기화 작업 생성

**POST** `/fhir/sync/`

**설명**: HAPI FHIR 서버로 데이터 동기화 요청

**요청 Body**
```json
{
  "resourceType": "Patient",
  "resourceId": "P-2024-001234",
  "operation": "create"
}
```

**응답 (202 Accepted)**
```json
{
  "syncJobId": "FS-2025-001234",
  "status": "queued",
  "queuedAt": "2025-12-20T16:00:00Z"
}
```

**권한**: `admin`, `external`

---

## 10. UC9 - AUDIT (감사 로그)

### 10.1 감사 로그 조회

**GET** `/audit/logs/`

**설명**: 감사 로그 조회 (관리자 전용)

**Query Parameters**
- `user_id` (optional): 사용자 ID 필터
- `action` (optional): 액션 타입 (`login`, `create`, `update`, `delete`, `view`)
- `resource_type` (optional): 리소스 타입 (`patient`, `order`, `report`)
- `from_date` (optional): 시작 날짜
- `to_date` (optional): 종료 날짜
- `page` (optional): 페이지 번호

**응답 (200 OK)**
```json
{
  "count": 1234,
  "results": [
    {
      "logId": "AUDIT-2025-001234",
      "actor": {
        "userId": "550e8400-e29b-41d4-a716-446655440000",
        "username": "dr.kim",
        "role": "doctor"
      },
      "action": "update",
      "resourceType": "report",
      "resourceId": "RP-2025-005678",
      "details": {
        "field": "status",
        "oldValue": "preliminary",
        "newValue": "final"
      },
      "ipAddress": "192.168.1.100",
      "userAgent": "Mozilla/5.0...",
      "timestamp": "2025-12-20T15:00:00Z"
    }
  ]
}
```

**권한**: `admin`

---

### 10.2 보안 이벤트 조회

**GET** `/audit/security-events/`

**설명**: 보안 이벤트 조회 (관리자 전용)

**Query Parameters**
- `severity` (optional): 심각도 (`low`, `medium`, `high`, `critical`)
- `event_type` (optional): 이벤트 타입 (`failed_login`, `unauthorized_access`, `data_breach`)

**응답 (200 OK)**
```json
{
  "count": 15,
  "results": [
    {
      "eventId": "SE-2025-001234",
      "eventType": "failed_login",
      "severity": "medium",
      "username": "unknown_user",
      "ipAddress": "203.0.113.42",
      "failedAttempts": 5,
      "timestamp": "2025-12-20T14:00:00Z",
      "blocked": true
    }
  ]
}
```

**권한**: `admin`

---

## 11. 공통 에러 코드

### HTTP 상태 코드

| 코드 | 설명 | 예시 |
|---|---|---|
| `200` | OK | 요청 성공 |
| `201` | Created | 리소스 생성 성공 |
| `204` | No Content | 삭제 성공 (응답 본문 없음) |
| `400` | Bad Request | 잘못된 요청 (유효성 검증 실패) |
| `401` | Unauthorized | 인증 실패 (토큰 없음/만료) |
| `403` | Forbidden | 권한 없음 |
| `404` | Not Found | 리소스 없음 |
| `409` | Conflict | 리소스 충돌 |
| `422` | Unprocessable Entity | 유효성 검증 실패 |
| `423` | Locked | 계정 잠금 |
| `429` | Too Many Requests | Rate Limit 초과 |
| `500` | Internal Server Error | 서버 내부 오류 |
| `503` | Service Unavailable | 서비스 이용 불가 |

---

### 에러 응답 포맷

```json
{
  "error": "error_code",
  "message": "사용자에게 표시할 오류 메시지",
  "details": {
    "field": "username",
    "issue": "이미 존재하는 사용자명입니다."
  },
  "timestamp": "2025-12-20T16:00:00Z"
}
```

---

### 에러 코드 목록

| 에러 코드 | HTTP 상태 | 설명 |
|---|---|---|
| `invalid_credentials` | 401 | 아이디 또는 비밀번호 오류 |
| `token_expired` | 401 | 토큰 만료 |
| `token_invalid` | 401 | 유효하지 않은 토큰 |
| `account_locked` | 423 | 계정 잠금 (무차별 대입 공격 방어) |
| `permission_denied` | 403 | 권한 없음 |
| `resource_not_found` | 404 | 리소스 없음 |
| `validation_error` | 422 | 유효성 검증 실패 |
| `rate_limit_exceeded` | 429 | API 호출 제한 초과 |
| `external_api_error` | 500 | 외부 API 오류 (OpenEMR, Orthanc, FHIR) |
| `ai_job_failed` | 500 | AI 분석 실패 |

---

## 12. API 사용 예시

### 12.1 로그인 후 환자 조회

**TypeScript (React)**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// 1. 로그인
const login = async (username: string, password: string) => {
  const response = await api.post('/acct/login/', { username, password });
  const { access, user } = response.data;

  // 토큰 저장
  localStorage.setItem('token', access);

  // Axios 인터셉터에 토큰 추가
  api.defaults.headers.common['Authorization'] = `Bearer ${access}`;

  return user;
};

// 2. 환자 검색
const searchPatients = async (query: string) => {
  const response = await api.get('/emr/patients/search/', {
    params: { q: query }
  });
  return response.data.results;
};

// 사용 예시
const user = await login('dr.kim', 'SecureP@ss123');
console.log(`로그인 성공: ${user.username} (${user.role})`);

const patients = await searchPatients('김철수');
console.log(`검색 결과: ${patients.length}명`);
```

---

### 12.2 AI 분석 요청 및 폴링

**TypeScript (React)**
```typescript
// AI 분석 요청
const requestAIAnalysis = async (studyId: string) => {
  const response = await api.post('/ai/jobs/', {
    studyId,
    analysisType: 'mri_tumor_detection',
    priority: 'high'
  });
  return response.data.jobId;
};

// AI 작업 상태 폴링
const pollAIJobStatus = async (jobId: string): Promise<any> => {
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/ai/jobs/${jobId}/`);
        const { status } = response.data;

        if (status === 'completed') {
          clearInterval(interval);
          // 결과 조회
          const resultResponse = await api.get(`/ai/results/${response.data.resultId}/`);
          resolve(resultResponse.data);
        } else if (status === 'failed') {
          clearInterval(interval);
          reject(new Error('AI 분석 실패'));
        }

        // 진행 중이면 계속 폴링
      } catch (error) {
        clearInterval(interval);
        reject(error);
      }
    }, 3000); // 3초마다 폴링
  });
};

// 사용 예시
const jobId = await requestAIAnalysis('ST-2025-001234');
console.log(`AI 분석 시작: ${jobId}`);

const result = await pollAIJobStatus(jobId);
console.log(`AI 분석 완료:`, result.findings);
```

---

### 12.3 WebSocket 실시간 알림

**TypeScript (React)**
```typescript
const connectWebSocket = (token: string) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/alerts/?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket 연결됨');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'new_alert') {
      const alert = data.alert;
      console.log(`새 알림: ${alert.title} - ${alert.message}`);

      // Toast 알림 표시
      showToast(alert.title, alert.message, alert.severity);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket 오류:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket 연결 종료');
    // 재연결 로직
    setTimeout(() => connectWebSocket(token), 5000);
  };

  return ws;
};

// 사용 예시
const token = localStorage.getItem('token');
const ws = connectWebSocket(token);
```

---

### 12.4 에러 처리

**TypeScript (Axios Interceptor)**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response } = error;

    if (response?.status === 401) {
      // 토큰 만료 시 Refresh Token으로 재발급
      const refreshToken = localStorage.getItem('refreshToken');

      if (refreshToken) {
        try {
          const { data } = await axios.post('http://localhost:8000/api/acct/token/refresh/', {
            refresh: refreshToken
          });

          // 새 토큰 저장
          localStorage.setItem('token', data.access);
          api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;

          // 원래 요청 재시도
          error.config.headers['Authorization'] = `Bearer ${data.access}`;
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh Token도 만료됨 - 로그아웃
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      } else {
        // Refresh Token 없음 - 로그아웃
        window.location.href = '/login';
      }
    } else if (response?.status === 403) {
      // 권한 없음
      alert('이 작업을 수행할 권한이 없습니다.');
    } else if (response?.status === 429) {
      // Rate Limit 초과
      alert('요청이 너무 많습니다. 잠시 후 다시 시도하세요.');
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## 부록: Pagination

모든 목록 조회 API는 페이지네이션을 지원합니다.

**Query Parameters**
- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지 크기 (기본: 20, 최대: 100)

**응답 포맷**
```json
{
  "count": 1234,
  "next": "http://localhost:8000/api/emr/patients/?page=2",
  "previous": null,
  "results": [...]
}
```

---

**Last Updated**: 2025-12-19
**Version**: 1.0
**Author**: Claude AI
