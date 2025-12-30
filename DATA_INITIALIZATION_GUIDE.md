# NeuroNova CDSS - 데이터 초기화 가이드

Docker 재설치 후 샘플 데이터를 빠르게 복구하는 방법입니다.

---

## 📦 생성된 스크립트

### 1. Django 데이터 초기화
- **파일**: `acct/management/commands/init_sample_data.py`
- **기능**: 사용자, 환자, 처방, 검사 데이터 생성
- **FHIR**: 자동 동기화 (signals)

### 2. DICOM 업로드
- **파일**: `ris/management/commands/upload_sample_dicoms.py`
- **기능**: sample_dicoms 디렉토리의 DICOM 파일을 Orthanc에 업로드

### 3. FHIR 자동 동기화
- **파일**: `fhir/signals.py`, `fhir/services/fhir_mapper.py`
- **기능**: Django 모델 생성/수정 시 자동으로 FHIR 서버에 동기화

---

## 🚀 빠른 사용법 (3단계)

### 전제 조건

Docker 인프라가 실행 중이어야 합니다:

```bash
# 인프라 시작 (Redis, Orthanc, FHIR, OpenEMR)
docker compose -f docker-compose.infra.yml up -d

# 또는 전체 스택
docker compose -f docker-compose.dev.yml up -d
```

### Step 1: Django 데이터 초기화

```bash
cd NeuroNova_02_back_end/02_django_server

# 데이터 생성
python manage.py init_sample_data

# 또는 기존 데이터 삭제 후 재생성
python manage.py init_sample_data --reset
```

**생성되는 데이터**:
- 👥 **사용자 7명**: admin, doctor1, doctor2, radiologist1, nurse1, tech1, researcher1
- 🏥 **환자 5명**: P20250001 ~ P20250005
- 📋 **의료 기록**: 각 환자별 1건
- 💊 **처방**: 3명 환자에 대해 각 3개 약물
- 🔬 **검사**: 4명 환자에 대해 각 2개 검사

**비밀번호** (모든 사용자):
- admin: `admin123!`
- doctor1, doctor2: `doctor123!`
- radiologist1: `radio123!`
- nurse1: `nurse123!`
- tech1: `tech123!`
- researcher1: `research123!`

### Step 2: DICOM 업로드

```bash
# 모든 DICOM 파일 업로드
python manage.py upload_sample_dicoms

# Dry run (테스트만)
python manage.py upload_sample_dicoms --dry-run

# 특정 환자만
python manage.py upload_sample_dicoms --patient sub-0004
```

**업로드되는 파일**:
- `sample_dicoms/sub-0004/`: Brain MRI 시리즈
- `sample_dicoms/sub-0005/`: Brain MRI 시리즈

### Step 3: FHIR 동기화 확인

FHIR 동기화는 **자동**으로 이루어집니다 (Django signals 사용).

확인 방법:

```bash
# FHIR 서버 접속
curl http://localhost:8080/fhir/Patient

# 또는 브라우저에서
# http://localhost:8080/fhir/Patient
# http://localhost:8080/fhir/MedicationRequest
# http://localhost:8080/fhir/DiagnosticReport
```

---

## 📖 상세 사용법

### 1. Django 데이터 초기화 상세

#### 옵션

```bash
python manage.py init_sample_data [OPTIONS]

Options:
  --reset    기존 데이터 삭제 후 재생성
  --help     도움말 표시
```

#### 생성되는 데이터 상세

**사용자 (7명)**:
| Username | Role | Password | 부서 |
|----------|------|----------|------|
| admin | ADMIN | admin123! | - |
| doctor1 | DOCTOR | doctor123! | Neurology |
| doctor2 | DOCTOR | doctor123! | Neurology |
| radiologist1 | RADIOLOGIST | radio123! | Radiology |
| nurse1 | NURSE | nurse123! | Neurology |
| tech1 | TECHNICIAN | tech123! | Radiology |
| researcher1 | RESEARCHER | research123! | - |

**환자 (5명)**:
| Patient ID | Name | Birth Date | Gender | Diagnosis |
|------------|------|------------|--------|-----------|
| P20250001 | Kim MinJun | 1985-05-15 | M | Brain Tumor - Glioblastoma |
| P20250002 | Lee SeoYun | 1990-08-22 | F | Brain Metastasis |
| P20250003 | Park JiHoon | 1978-03-10 | M | Cerebral Infarction |
| P20250004 | Choi YeJin | 1995-11-30 | F | Intracranial Hemorrhage |
| P20250005 | Jung DoHyun | 1982-07-18 | M | Demyelinating Disease - MS |

**처방 (3명 환자, 각 3개 약물)**:
- Dexamethasone (뇌부종 완화)
- Levetiracetam (발작 예방)
- Mannitol (두개내압 감소)
- Aspirin (항혈소판)
- Ondansetron (구토 방지)

**검사 (4명 환자, 각 2개 검사)**:
- CBC (Complete Blood Count)
- BMP (Basic Metabolic Panel)
- LFT (Liver Function Test)
- COAG (Coagulation Panel)
- TUMOR_MARKER (Tumor Marker Panel)

#### 출력 예시

```
🚀 Starting sample data initialization...
👥 Creating users...
   ✓ User created: admin (ADMIN)
   ✓ User created: doctor1 (DOCTOR)
   ...
🏥 Creating patients...
   ✓ Patient created: P20250001 - Kim MinJun
   ...
📋 Creating medical records...
   ✓ Medical record created for P20250001
   ...
💊 Creating prescriptions...
   ✓ Prescription created for P20250001
   ...
🔬 Creating lab tests...
   ✓ Lab test created: Complete Blood Count for P20250001
   ...

============================================================
📊 Sample Data Summary
============================================================

👥 Users Created: 7
   • ADMIN: admin
   • DOCTOR: doctor1
   ...

🏥 Patients Created: 5
   • P20250001: Kim MinJun
   ...

📋 Medical Records: 5
💊 Prescriptions: 3
🔬 Lab Tests: 8
📝 Lab Results: 32

============================================================
✅ All done! You can now login with the created users.
============================================================
```

---

### 2. DICOM 업로드 상세

#### 옵션

```bash
python manage.py upload_sample_dicoms [OPTIONS]

Options:
  --patient PATIENT_ID   특정 환자만 업로드 (e.g., sub-0004)
  --dry-run              테스트 모드 (실제 업로드 안 함)
  --path PATH            DICOM 디렉토리 경로 (기본: sample_dicoms)
  --help                 도움말 표시
```

#### 사용 예시

```bash
# 1. Dry run으로 먼저 테스트
python manage.py upload_sample_dicoms --dry-run

# 2. 모든 DICOM 업로드
python manage.py upload_sample_dicoms

# 3. 특정 환자만
python manage.py upload_sample_dicoms --patient sub-0004

# 4. 다른 경로에서 업로드
python manage.py upload_sample_dicoms --path /path/to/dicoms
```

#### 출력 예시

```
🔍 Scanning DICOM files in: d:\1222\NeuroNova_v1\sample_dicoms
📡 Orthanc URL: http://localhost:8042
   Scanning sub-0004...
   Scanning sub-0005...
📁 Found 245 DICOM files

   ✓ Uploaded: 10/245 - slice_009.dcm (ID: 5a8c9d2e...)
   ✓ Uploaded: 20/245 - slice_019.dcm (ID: 7b3f1a5c...)
   ...

============================================================
📊 UPLOAD SUMMARY
============================================================

✅ Successfully uploaded: 245 files

📈 Orthanc Statistics:
   • Total Studies: 2
   • Total Series: 4
   • Total Instances: 245
   • Disk Size: 128.5 MB

🌐 View in Orthanc: http://localhost:8042/app/explorer.html
============================================================
```

---

### 3. FHIR 자동 동기화 상세

#### 작동 방식

Django signals를 사용하여 모델 저장 시 자동으로 FHIR에 동기화합니다.

```python
# 환자 생성/수정 → FHIR Patient
patient = Patient.objects.create(...)
# → FHIR Patient 자동 생성
# → patient.fhir_id에 FHIR ID 저장

# 처방 생성/수정 → FHIR MedicationRequest
prescription = Prescription.objects.create(...)
# → FHIR MedicationRequest 자동 생성

# 검사 생성/수정 → FHIR DiagnosticReport + Observation
lab_test = LabTest.objects.create(...)
# → FHIR DiagnosticReport 자동 생성
# → 각 LabResult → FHIR Observation 생성
```

#### Signal 파일 위치

- **Signals**: `fhir/signals.py`
- **Mappers**: `fhir/services/fhir_mapper.py`
- **Client**: `fhir/services/fhir_client.py`
- **앱 활성화**: `fhir/apps.py` (ready() 메서드)

#### 수동 동기화 (필요 시)

기존 데이터를 FHIR에 일괄 동기화:

```python
from fhir.signals import bulk_sync_to_fhir

# 모든 환자 동기화
bulk_sync_to_fhir('Patient')

# 모든 처방 동기화
bulk_sync_to_fhir('Prescription')

# 모든 검사 동기화
bulk_sync_to_fhir('LabTest')

# 모든 데이터 동기화
bulk_sync_to_fhir()
```

#### FHIR 리소스 매핑

| Django Model | FHIR Resource |
|--------------|---------------|
| Patient | Patient |
| Prescription | MedicationRequest |
| LabTest | DiagnosticReport |
| LabResult | Observation |

#### FHIR ID 저장

각 모델에 `fhir_id` 필드가 있어야 합니다 (migration 필요할 수 있음):

```python
# models.py에 추가
class Patient(models.Model):
    # ... 기존 필드들
    fhir_id = models.CharField(max_length=64, blank=True, null=True, unique=True)

class Prescription(models.Model):
    # ... 기존 필드들
    fhir_id = models.CharField(max_length=64, blank=True, null=True, unique=True)

class LabTest(models.Model):
    # ... 기존 필드들
    fhir_id = models.CharField(max_length=64, blank=True, null=True, unique=True)

class LabResult(models.Model):
    # ... 기존 필드들
    fhir_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
```

---

## 🔧 문제 해결

### 1. FHIR 동기화 실패

**증상**: FHIR ID가 저장되지 않음

**확인**:
```bash
# FHIR 서버 실행 확인
curl http://localhost:8080/fhir/metadata

# Django 로그 확인
# logs/django.log 또는 콘솔 출력
```

**해결**:
- HAPI FHIR 컨테이너가 실행 중인지 확인
- `.env`에서 `FHIR_SERVER_URL` 확인
- `fhir_id` 필드가 모델에 있는지 확인 (migration 필요)

### 2. DICOM 업로드 실패

**증상**: Connection refused 에러

**확인**:
```bash
# Orthanc 실행 확인
curl http://localhost:8042/system

# Docker 상태
docker ps | grep orthanc
```

**해결**:
- Orthanc 컨테이너가 실행 중인지 확인
- `.env`에서 `ORTHANC_API_URL` 확인 (http://localhost:8042)
- 방화벽에서 8042 포트 허용 확인

### 3. sample_dicoms 경로 오류

**증상**: DICOM directory not found

**확인**:
```bash
# 경로 확인
ls sample_dicoms/

# 프로젝트 루트에서 실행했는지 확인
pwd
```

**해결**:
- `sample_dicoms` 디렉토리가 프로젝트 루트에 있는지 확인
- `--path` 옵션으로 정확한 경로 지정

### 4. 사용자 생성 실패 - Role not found

**증상**: Role DOCTOR not found

**확인**:
```bash
# Django shell
python manage.py shell

>>> from acct.models import Role
>>> Role.objects.all()
```

**해결**:
```bash
# Role 초기 데이터 로드 (fixtures 사용)
python manage.py loaddata acct/fixtures/roles.json

# 또는 수동 생성
python manage.py shell
>>> from acct.models import Role
>>> Role.objects.create(name='ADMIN', description='System Administrator')
>>> Role.objects.create(name='DOCTOR', description='Doctor')
# ... 나머지 Role들
```

---

## 📝 완전 초기화 시나리오

Docker를 완전히 삭제하고 재설치한 경우:

```bash
# 1. Docker 인프라 시작
docker compose -f docker-compose.infra.yml up -d

# 2. Django 마이그레이션
cd NeuroNova_02_back_end/02_django_server
python manage.py migrate

# 3. Role 초기 데이터 (필요 시)
python manage.py loaddata acct/fixtures/roles.json

# 4. 샘플 데이터 생성
python manage.py init_sample_data

# 5. DICOM 업로드
python manage.py upload_sample_dicoms

# 6. FHIR 확인
curl http://localhost:8080/fhir/Patient

# 7. Orthanc 확인
curl http://localhost:8042/statistics

# 완료!
```

**예상 시간**: 5-10분 (DICOM 업로드 시간 포함)

---

## 📚 참고

- **Django Management Commands**: [Django Docs](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- **FHIR R4 Spec**: [HL7 FHIR](https://hl7.org/fhir/R4/)
- **Orthanc API**: [Orthanc Book](https://book.orthanc-server.com/users/rest.html)

---

**마지막 업데이트**: 2025-12-30
**버전**: v2.1
