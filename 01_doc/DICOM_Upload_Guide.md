# DICOM Upload with Patient Assignment Guide

**작성일**: 2026-01-05
**최종 수정**: 2026-01-05
**작성자**: Claude AI

---

## 📋 목차

1. [개요](#-1-개요)
2. [시스템 아키텍처](#-2-시스템-아키텍처)
3. [Backend API 명세](#-3-backend-api-명세)
4. [Frontend 사용 방법](#-4-frontend-사용-방법)
5. [환자 지정 로직](#-5-환자-지정-로직)
6. [테스트 방법](#-6-테스트-방법)
7. [트러블슈팅](#-7-트러블슈팅)

---

## 🎯 1. 개요

### 목적
이미 준비된 DICOM 파일을 Orthanc PACS에 업로드하면서 특정 환자에게 매핑하는 기능입니다.

### 주요 기능
- ✅ DICOM 파일 업로드 (Multi-part form data)
- ✅ HTJ2K/J2K 자동 변환 (압축)
- ✅ 환자 선택 (EMR 환자 목록에서)
- ✅ DICOM 메타데이터 자동 업데이트 (Patient ID, Name, Birth Date, Gender)
- ✅ Orthanc PACS 자동 업로드
- ✅ 업로드 성공 시 Study List 자동 새로고침

### 워크플로우
```
[사용자]
  → [DICOM 파일 선택]
  → [환자 선택 (선택사항)]
  → [업로드 버튼 클릭]
  → [Backend] DICOM 메타데이터 업데이트
  → [Backend] HTJ2K 변환
  → [Backend] Orthanc 업로드
  → [Frontend] Study List 갱신
```

---

## 🏗️ 2. 시스템 아키텍처

### Backend (Django)

#### 파일 구조
```
NeuroNova_02_back_end/02_django_server/ris/
├── views.py                    # DicomUploadView (업로드 + 변환 + Orthanc 전송)
├── views_patient_upload.py     # get_patients_for_upload (환자 목록 조회)
├── urls.py                     # URL 라우팅
├── utils/
│   └── dicom_converter.py      # HTJ2KConverter (압축 변환)
└── clients/
    └── orthanc_client.py       # OrthancClient (Orthanc API 통신)
```

#### API 엔드포인트
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ris/upload/dicom/` | DICOM 파일 업로드 + 환자 지정 |
| `GET` | `/api/ris/patients/` | 환자 목록 조회 (검색 지원) |

---

### Frontend (React)

#### 파일 구조
```
NeuroNova_03_front_end_react/01_react_client/src/
├── services/
│   └── risService.ts           # API 호출 함수
├── components/ris/
│   ├── DicomUploader.tsx       # 업로드 모달 컴포넌트
│   └── StudyList.tsx           # Study 목록 테이블
└── pages/ris/
    └── RISDashboard.tsx        # RIS 대시보드 (통합)
```

---

## 🔧 3. Backend API 명세

### 3.1 DICOM 파일 업로드 API

#### Request
```http
POST /api/ris/upload/dicom/
Content-Type: multipart/form-data

FormData:
  - file: <DICOM Binary File>
  - patient_id: <Patient ID> (Optional)
```

#### Response (Success)
```json
{
  "success": true,
  "message": "Uploaded and converted successfully",
  "patient_id": "P-2024-001234",
  "orthanc_response": {
    "ID": "e8b3a7c2-12345678",
    "ParentPatient": "patient-id-hash",
    "ParentSeries": "series-id-hash",
    "ParentStudy": "study-id-hash",
    "Status": "Success"
  }
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "Conversion failed: invalid DICOM format"
}
```

#### 처리 단계
1. **파일 검증**: DICOM 형식 확인
2. **환자 정보 매핑** (patient_id가 제공된 경우):
   - EMR에서 환자 정보 조회
   - DICOM 태그 업데이트 (PatientID, PatientName, PatientBirthDate, PatientSex)
3. **HTJ2K 변환**: 압축 (Fallback: JPEG2000 Lossless)
4. **Orthanc 업로드**: POST /instances
5. **임시 파일 정리**

---

### 3.2 환자 목록 조회 API

#### Request
```http
GET /api/ris/patients/?search=Hong
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | 환자 ID/이름 검색 (부분 일치) |
| `limit` | int | No | 반환 개수 (기본값: 50) |

#### Response
```json
{
  "success": true,
  "patients": [
    {
      "patient_id": "P-2024-001234",
      "name": "Hong^Gildong",
      "birth_date": "1980-01-15",
      "gender": "male"
    }
  ],
  "total": 1
}
```

---

## 💻 4. Frontend 사용 방법

### 4.1 RIS Dashboard 접근

1. React 애플리케이션 실행:
   ```bash
   cd NeuroNova_03_front_end_react/01_react_client
   npm start
   ```

2. 브라우저에서 RIS Dashboard 접속:
   ```
   http://localhost:3001/ris
   ```

---

### 4.2 DICOM 파일 업로드

#### Step 1: 업로드 버튼 클릭
- RIS Dashboard 우측 상단의 **"Upload DICOM"** 버튼 클릭
- 모달 창이 열립니다

#### Step 2: DICOM 파일 선택
- "Select DICOM File" 섹션에서 파일 선택
- `.dcm` 또는 `.dicom` 확장자만 허용
- 선택된 파일명과 크기가 표시됩니다

#### Step 3: 환자 지정 (선택사항)
두 가지 옵션:
1. **환자 지정 안 함**: 드롭다운에서 "No patient selected" 선택
   - DICOM 파일의 기존 메타데이터 사용
2. **환자 지정**: 드롭다운에서 환자 선택
   - EMR 환자 정보로 DICOM 메타데이터 덮어쓰기
   - 검색 기능으로 환자 필터링 가능

#### Step 4: 업로드
- **"Upload"** 버튼 클릭
- 진행 상황 표시: "Uploading..."
- 성공 시: 녹색 성공 메시지 표시 + Study List 자동 갱신
- 실패 시: 빨간색 에러 메시지 표시

---

### 4.3 UI 스크린샷 설명

```
┌───────────────────────────────────────────────────┐
│  Upload DICOM File                           [X]  │
├───────────────────────────────────────────────────┤
│  Select DICOM File                                │
│  [Choose File] brain_scan.dcm                     │
│  Selected: brain_scan.dcm (2048.50 KB)            │
│                                                    │
│  Assign to Patient (Optional)                     │
│  [Search patient...                           ]   │
│  [Select Patient ▼                             ]  │
│    -- No patient selected (use existing...)       │
│    P-2024-001234 - Hong^Gildong (1980-01-15)     │
│    P-2024-001235 - Kim^Cheolsu (1975-05-20)      │
│                                                    │
│  [Success] Uploaded and converted successfully!   │
│                                                    │
│                              [Cancel]  [Upload]   │
└───────────────────────────────────────────────────┘
```

---

## 🔑 5. 환자 지정 로직

### 5.1 Backend 환자 매핑 코드

[ris/views.py:616-638](../NeuroNova_02_back_end/02_django_server/ris/views.py#L616-L638)

```python
# If patient_id provided, update DICOM metadata before conversion
if patient_id:
    try:
        ds = pydicom.dcmread(tmp_path)

        # Update Patient ID and Name
        ds.PatientID = patient_id

        # Try to get patient name from EMR
        from emr.models import PatientCache
        try:
            patient = PatientCache.objects.get(patient_id=patient_id)
            ds.PatientName = f"{patient.family_name}^{patient.given_name}"
            ds.PatientBirthDate = patient.birth_date.strftime('%Y%m%d')
            ds.PatientSex = patient.gender[0].upper() if patient.gender else 'O'
        except PatientCache.DoesNotExist:
            ds.PatientName = patient_id

        # Save updated DICOM
        ds.save_as(tmp_path)
        logger.info(f"[DICOM Upload] Updated metadata with patient_id: {patient_id}")
    except Exception as e:
        logger.warning(f"[DICOM Upload] Failed to update patient metadata: {e}")
```

### 5.2 업데이트되는 DICOM 태그

| DICOM Tag | Name | Value Source |
|-----------|------|--------------|
| `(0010,0020)` | PatientID | `patient_id` 파라미터 |
| `(0010,0010)` | PatientName | EMR: `family_name^given_name` |
| `(0010,0030)` | PatientBirthDate | EMR: `birth_date` (YYYYMMDD 형식) |
| `(0010,0040)` | PatientSex | EMR: `gender` 첫 글자 대문자 (M/F/O) |

---

## 🧪 6. 테스트 방법

### 6.1 사전 준비

1. **Django 서버 실행**:
   ```bash
   cd NeuroNova_02_back_end/02_django_server
   python manage.py runserver
   ```

2. **Orthanc PACS 실행**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d orthanc
   ```

3. **React 클라이언트 실행** (WSL):
   ```bash
   cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/01_react_client
   npm start
   ```

4. **테스트 환자 생성**:
   ```bash
   python manage.py create_test_users
   python manage.py seed_master_data
   ```

---

### 6.2 테스트 시나리오

#### Scenario 1: 환자 지정 없이 업로드

1. RIS Dashboard (`http://localhost:3001/ris`) 접속
2. "Upload DICOM" 버튼 클릭
3. DICOM 파일 선택 (예: `sample.dcm`)
4. 환자 드롭다운에서 "No patient selected" 선택
5. "Upload" 버튼 클릭
6. **기대 결과**:
   - 성공 메시지 표시
   - Study List에 새 Study 추가 (기존 DICOM 메타데이터 사용)

#### Scenario 2: 환자 지정하여 업로드

1. RIS Dashboard 접속
2. "Upload DICOM" 버튼 클릭
3. DICOM 파일 선택
4. 검색창에 "Hong" 입력
5. 드롭다운에서 "P-2024-001234 - Hong^Gildong" 선택
6. "Upload" 버튼 클릭
7. **기대 결과**:
   - 성공 메시지 표시 (patient_id 포함)
   - Study List에 새 Study 추가
   - PatientName이 "Hong^Gildong"으로 업데이트됨

#### Scenario 3: 잘못된 파일 형식

1. RIS Dashboard 접속
2. "Upload DICOM" 버튼 클릭
3. JPEG 파일 선택 (예: `image.jpg`)
4. **기대 결과**:
   - 경고 메시지: "Please select a DICOM file (.dcm or .dicom)"
   - 파일 선택 취소됨

---

### 6.3 Orthanc 확인

1. Orthanc 웹 UI 접속:
   ```
   http://localhost:8042/app/explorer.html
   ```

2. "All studies" 클릭

3. 업로드된 Study 확인:
   - Patient Name
   - Patient ID
   - Study Date
   - Series Count

4. Study 클릭 → "Preview" 버튼 → DICOM 이미지 확인

---

## 🛠️ 7. 트러블슈팅

### 문제 1: "Conversion failed: invalid DICOM format"

**원인**: DICOM 형식이 아닌 파일 업로드

**해결 방법**:
- pydicom으로 파일 검증:
  ```bash
  python -c "import pydicom; ds = pydicom.dcmread('file.dcm'); print('Valid DICOM')"
  ```
- 올바른 DICOM 파일 사용

---

### 문제 2: "PatientCache matching query does not exist"

**원인**: 선택한 환자 ID가 EMR에 존재하지 않음

**해결 방법**:
- Django Admin에서 환자 생성:
  ```
  http://localhost:8000/admin/emr/patientcache/
  ```
- 또는 환자 지정 없이 업로드

---

### 문제 3: "Orthanc upload failed (status 400)"

**원인**:
- Orthanc가 실행되지 않음
- DICOM 파일이 손상됨

**해결 방법**:
1. Orthanc 상태 확인:
   ```bash
   docker ps | grep orthanc
   ```
2. Orthanc 로그 확인:
   ```bash
   docker logs neuronova-orthanc-dev
   ```
3. Health Check API 호출:
   ```bash
   curl http://localhost:8000/api/ris/health/
   ```

---

### 문제 4: "Failed to load patients"

**원인**: Backend API 오류 또는 네트워크 문제

**해결 방법**:
1. Django 서버 로그 확인:
   ```bash
   python manage.py runserver
   ```
2. 브라우저 개발자 도구 (F12) → Network 탭 → API 응답 확인
3. `/api/ris/patients/` 직접 호출:
   ```bash
   curl http://localhost:8000/api/ris/patients/
   ```

---

### 문제 5: HTJ2K 변환 실패 (Fallback to J2K)

**원인**: `imagecodecs.jph_encode` 함수 없음 (OpenJPH 미설치)

**해결 방법**:
- **정상 동작**: JPEG2000 Lossless로 자동 Fallback
- HTJ2K 필요 시 `imagecodecs` 재설치:
  ```bash
  pip uninstall imagecodecs
  pip install imagecodecs
  ```
- 로그 확인:
  ```
  [DICOM Upload] HTJ2K Conversion failed: ...
  ```

---

## 📊 로그 확인

### Backend 로그
```bash
# Django 서버 콘솔
[INFO] [DICOM Upload] Updated metadata with patient_id: P-2024-001234
[INFO] [DICOM Upload] HTJ2K Conversion successful
[INFO] [DICOM Upload] Orthanc upload successful: e8b3a7c2-12345678
```

### Frontend 로그 (Browser Console)
```javascript
[DicomUploader] Upload successful:
{
  success: true,
  message: "Uploaded and converted successfully",
  patient_id: "P-2024-001234",
  orthanc_response: {...}
}
```

---

## 🎉 완료!

DICOM 업로드 시스템이 정상적으로 구현되었습니다.

**다음 단계**:
- [ ] 배치 업로드 기능 추가 (여러 파일 동시 업로드)
- [ ] 업로드 진행률 표시 (Progress Bar)
- [ ] 업로드 히스토리 로그 저장
- [ ] NIfTI → DICOM 변환 후 업로드 통합

---

**문서 버전**: 1.0
**마지막 업데이트**: 2026-01-05
