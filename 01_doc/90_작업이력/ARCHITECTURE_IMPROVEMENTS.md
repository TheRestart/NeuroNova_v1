# 아키텍처 개선 계획

**작성일**: 2025-12-31
**목적**: FHIR-Orthanc 연동 및 GCP 배포 안정성 개선
**우선순위**: High (프로덕션 배포 전 필수)

---

## 📋 개요

프로덕션 배포를 위한 두 가지 핵심 아키텍처 개선:

1. **FHIR-Orthanc 연동**: Orthanc의 DICOM 데이터를 FHIR ImagingStudy로 자동 노출
2. **GCP IP 변경 대응**: VM 재부팅 시 IP 변경 문제 해결 (내부 통신 + 외부 접근)

---

## 🔗 개선 1: FHIR-Orthanc 연동 (orthanc-fhir 플러그인)

### 현재 상황

**문제점**:
- Orthanc는 DICOM 네이티브 저장소이지만 FHIR 표준 미지원
- 외부 시스템(HAPI FHIR, EMR)에서 Orthanc 데이터 조회 불가
- UC09 (FHIR 연동)에서 ImagingStudy 리소스 누락

**현재 아키텍처**:
```
[Orthanc PACS]
    ↓ (DICOMweb API - QIDO/WADO)
[Django RIS]
    ↓ (Custom Converter)
[HAPI FHIR]
```

**한계**:
- Django가 중간 변환 계층 역할 → 성능 오버헤드
- DICOM → FHIR 변환 로직 직접 구현 필요
- 표준 FHIR 클라이언트로 Orthanc 직접 조회 불가

---

### 개선 방안: orthanc-fhir 플러그인

**목표**:
```
[Orthanc PACS + orthanc-fhir Plugin]
    ↓ (FHIR REST API)
[HAPI FHIR] or [Django FHIR Client]
```

**주요 기능**:
- DICOM 계층 구조 → FHIR ImagingStudy 자동 매핑
- FHIR REST API 제공 (`GET /fhir/ImagingStudy`)
- 표준 FHIR 클라이언트 호환

---

### DICOM → FHIR 매핑 구조

| DICOM 계층 | FHIR 리소스 | 매핑 예시 |
|-----------|------------|----------|
| **Patient** | Patient | PatientName → name, PatientID → identifier |
| **Study** | ImagingStudy | StudyInstanceUID → identifier, StudyDate → started |
| **Series** | ImagingStudy.series | SeriesInstanceUID → uid, Modality → modality |
| **Instance** | ImagingStudy.series.instance | SOPInstanceUID → uid |

**예시**:
```json
// DICOM Study
{
  "PatientName": "홍길동",
  "PatientID": "P001",
  "StudyInstanceUID": "1.2.840.113619.2.55.3.123",
  "StudyDate": "20251231",
  "Modality": "CT"
}

// FHIR ImagingStudy (orthanc-fhir 변환)
{
  "resourceType": "ImagingStudy",
  "id": "orthanc-study-123",
  "identifier": [{
    "system": "urn:dicom:uid",
    "value": "1.2.840.113619.2.55.3.123"
  }],
  "status": "available",
  "subject": {
    "reference": "Patient/P001"
  },
  "started": "2025-12-31",
  "series": [{
    "uid": "1.2.840.113619.2.55.3.123.456",
    "modality": {
      "system": "http://dicom.nema.org/resources/ontology/DCM",
      "code": "CT"
    },
    "numberOfInstances": 150
  }]
}
```

---

### 구현 계획

#### Step 1: orthanc-fhir 플러그인 설치

**파일**: `NeuroNova_02_back_end/05_orthanc_pacs/orthanc.json`

**변경 전**:
```json
{
  "Name": "NeuroNova Orthanc PACS",
  "HttpPort": 8042,
  "DicomAet": "NEURONOVA",
  "DicomPort": 4242
}
```

**변경 후**:
```json
{
  "Name": "NeuroNova Orthanc PACS",
  "HttpPort": 8042,
  "DicomAet": "NEURONOVA",
  "DicomPort": 4242,

  // FHIR 플러그인 설정
  "Plugins": [
    "/usr/share/orthanc/plugins-available/libOrthancFHIR.so"
  ],

  "FHIR": {
    "Enabled": true,
    "OrthancServerUrl": "http://localhost:8042",
    "FhirServerUrl": "http://hapi-fhir:8080/fhir"
  }
}
```

**Docker 이미지**:
```dockerfile
# Dockerfile (Orthanc with FHIR plugin)
FROM orthancteam/orthanc:24.11.3

# FHIR 플러그인 설치
RUN apt-get update && \
    apt-get install -y orthanc-fhir && \
    apt-get clean

COPY orthanc.json /etc/orthanc/orthanc.json
```

---

#### Step 2: FHIR API 테스트

**1. Orthanc에 DICOM 업로드**:
```bash
# 샘플 DICOM 업로드
curl -X POST http://localhost:8042/instances \
  --data-binary @sample.dcm
```

**2. FHIR ImagingStudy 조회**:
```bash
# FHIR API로 조회
curl http://localhost:8042/fhir/ImagingStudy

# 응답 예시
{
  "resourceType": "Bundle",
  "type": "searchset",
  "entry": [{
    "resource": {
      "resourceType": "ImagingStudy",
      "id": "study-123",
      "subject": {"reference": "Patient/P001"},
      "started": "2025-12-31"
    }
  }]
}
```

**3. Django에서 FHIR 클라이언트로 조회**:
```python
# ris/views.py
import requests

def get_imaging_studies(request):
    # Orthanc FHIR API 호출
    response = requests.get('http://orthanc:8042/fhir/ImagingStudy')
    imaging_studies = response.json()

    return Response(imaging_studies)
```

---

#### Step 3: HAPI FHIR 연동

**목표**: Orthanc의 FHIR 데이터를 HAPI FHIR에 동기화

**방법 A: FHIR Subscription (권장)**:
```json
// Orthanc에 Subscription 생성
POST http://localhost:8042/fhir/Subscription
{
  "resourceType": "Subscription",
  "status": "active",
  "criteria": "ImagingStudy",
  "channel": {
    "type": "rest-hook",
    "endpoint": "http://hapi-fhir:8080/fhir/ImagingStudy"
  }
}
```

**방법 B: 주기적 동기화 (Celery Beat)**:
```python
# ris/tasks.py
from celery import shared_task
import requests

@shared_task
def sync_orthanc_to_fhir():
    # Orthanc에서 ImagingStudy 가져오기
    orthanc_response = requests.get('http://orthanc:8042/fhir/ImagingStudy')
    studies = orthanc_response.json()['entry']

    # HAPI FHIR에 업로드
    for study in studies:
        requests.post('http://hapi-fhir:8080/fhir/ImagingStudy',
                      json=study['resource'])
```

---

### 예상 효과

| 항목 | 현재 | 개선 후 |
|------|------|---------|
| FHIR 호환성 | ❌ 없음 | ✅ 표준 FHIR API |
| 변환 로직 | Django 직접 구현 필요 | Orthanc 플러그인 자동 처리 |
| 성능 | Django 중간 계층 오버헤드 | 직접 조회 (빠름) |
| 외부 연동 | 커스텀 API 필요 | FHIR 클라이언트 즉시 사용 가능 |

---

## 🌐 개선 2: GCP 배포 IP 변경 대응

### 현재 상황

**문제점**:
- GCP VM 재부팅 시 외부 IP 변경 → 프론트엔드 연결 끊김
- 컨테이너 간 통신에 하드코딩된 IP 사용 → 재배포 시 설정 변경 필요

**현재 설정** (문제 있음):
```javascript
// React apiClient.js
const API_BASE_URL = 'http://34.64.123.45:8000';  // ❌ VM IP 하드코딩

// Django settings.py
ORTHANC_URL = 'http://172.17.0.5:8042'  // ❌ 컨테이너 IP 하드코딩
```

---

### 개선 방안

#### 전략 1: 내부 통신 - Docker Service Discovery

**목표**: 컨테이너 간 통신을 Service Name으로 변경 (IP 사용 금지)

**변경 전** (IP 의존):
```python
# settings.py
ORTHANC_URL = 'http://172.17.0.5:8042'  # ❌ 컨테이너 재시작 시 IP 변경 가능
```

**변경 후** (Service Name):
```python
# settings.py
ORTHANC_URL = os.getenv('ORTHANC_URL', 'http://orthanc:8042')  # ✅ 안정적
```

**Docker Compose** (이미 올바르게 설정됨):
```yaml
# docker-compose.dev.yml
services:
  django:
    environment:
      - ORTHANC_URL=http://orthanc:8042  # Service Name 사용
      - REDIS_URL=redis://redis:6379/0
      - MYSQL_HOST=cdss-mysql
      - HAPI_FHIR_URL=http://hapi-fhir:8080/fhir

  orthanc:
    hostname: orthanc  # DNS 이름 고정
    networks:
      - neuronova-network
```

**Docker 네트워크 내부 DNS**:
- `orthanc` → 자동으로 컨테이너 IP 해석
- IP 변경되어도 Service Name은 유지

---

#### 전략 2: 외부 접근 - GCP 고정 외부 IP

**목표**: VM 재부팅 시에도 동일한 IP 유지

**Step 1: GCP 고정 IP 예약**

✅ **이미 예약된 고정 IP 주소**:
- **IP 주소**: `34.71.151.117`
- **이름**: `neuronova-static-ip`
- **Region**: `asia-northeast3` (서울)
- **상태**: IN_USE

```bash
# 예약된 IP 확인
gcloud compute addresses describe neuronova-static-ip \
  --region=asia-northeast3

# 출력:
# address: 34.71.151.117
# addressType: EXTERNAL
# status: IN_USE
```

**Step 2: VM 인스턴스에 고정 IP 할당**

✅ **이미 할당 완료**: VM 인스턴스에 `34.71.151.117` 할당됨

```bash
# 현재 VM의 IP 확인
gcloud compute instances describe neuronova-cdss-vm \
  --zone=asia-northeast3-a \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

# 출력: 34.71.151.117
```

**결과**:
- ✅ VM 재부팅 후에도 `34.71.151.117` 유지
- DNS에 도메인 연결 가능: `neuronova.example.com` → `34.71.151.117`
- Cloudflare에서 A 레코드 설정 시 이 IP 사용

---

#### 전략 3: 프론트엔드 - Nginx Reverse Proxy

**목표**: React에서 상대 경로(`/api`)로 호출하여 Nginx가 Django로 프록시

**변경 전** (절대 경로 - 문제):
```javascript
// React apiClient.js
const API_BASE_URL = 'http://34.64.123.45:8000';  // ❌ IP 하드코딩

axios.get(`${API_BASE_URL}/api/emr/patients/`);
```

**변경 후** (상대 경로 - 안정적):
```javascript
// React apiClient.js
const API_BASE_URL = '/api';  // ✅ 상대 경로

axios.get(`${API_BASE_URL}/emr/patients/`);  // → /api/emr/patients/
```

**Nginx 설정**:
```nginx
# nginx.conf
server {
    listen 80;
    server_name neuronova.example.com;

    # React 정적 파일
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }

    # Django API 프록시
    location /api/ {
        proxy_pass http://django:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Orthanc DICOMweb 프록시
    location /dicom-web/ {
        proxy_pass http://orthanc:8042/dicom-web/;
        proxy_set_header Host $host;
    }

    # OHIF Viewer
    location /viewer/ {
        proxy_pass http://ohif:3000/;
    }
}
```

**호출 흐름**:
```
[사용자 브라우저]
    ↓ GET http://neuronova.example.com/api/emr/patients/
[Nginx:80]
    ↓ proxy_pass → http://django:8000/api/emr/patients/
[Django:8000]
    ↓ 응답
[Nginx] → [브라우저]
```

---

### 프로덕션 아키텍처 (개선 후)

```
[사용자]
    ↓
[도메인: neuronova.example.com (고정 IP: 34.64.100.200)]
    ↓
[GCP VM - Compute Engine]
    ↓
[Nginx:80/443]
    ├─ /           → React 정적 파일
    ├─ /api/       → Django (Service Name: django:8000)
    ├─ /dicom-web/ → Orthanc (Service Name: orthanc:8042)
    └─ /viewer/    → OHIF (Service Name: ohif:3000)

[Docker 내부 네트워크]
    ├─ django:8000
    │   └─ 환경변수: ORTHANC_URL=http://orthanc:8042
    ├─ orthanc:8042 (+ orthanc-fhir 플러그인)
    ├─ hapi-fhir:8080
    ├─ cdss-mysql:3306
    └─ redis:6379
```

---

## 📝 구현 체크리스트

### Phase 1: FHIR-Orthanc 연동 (3-4일)

- [ ] **orthanc-fhir 플러그인 설치**:
  - [ ] Dockerfile 수정 (orthanc-fhir 패키지 추가)
  - [ ] orthanc.json 설정 업데이트
  - [ ] Docker 이미지 리빌드

- [ ] **FHIR API 테스트**:
  - [ ] DICOM 업로드 후 FHIR ImagingStudy 조회 확인
  - [ ] Patient, Study, Series 매핑 검증
  - [ ] Postman/cURL 테스트 스크립트 작성

- [ ] **Django 연동**:
  - [ ] ris/views.py에서 Orthanc FHIR API 호출
  - [ ] ImagingStudy → RIS Order 매핑 로직
  - [ ] HAPI FHIR 동기화 (Celery Task)

- [ ] **문서화**:
  - [ ] Orthanc FHIR API 사용 가이드
  - [ ] DICOM-FHIR 매핑 테이블
  - [ ] 12_배포_가이드_GCP.md 업데이트

---

### Phase 2: GCP IP 변경 대응 (2-3일)

- [ ] **내부 통신 Service Name 전환**:
  - [ ] settings.py 환경변수 확인 (ORTHANC_URL, REDIS_URL, MYSQL_HOST)
  - [ ] 하드코딩된 IP 검색 및 제거
    ```bash
    grep -r "172\.\|192\.168\." NeuroNova_02_back_end/02_django_server/
    ```

- [ ] **GCP 고정 IP 설정**:
  - [ ] GCP Console에서 고정 IP 예약
  - [ ] VM 인스턴스에 고정 IP 할당
  - [ ] 방화벽 규칙 업데이트 (고정 IP로)
  - [ ] DNS A 레코드 등록 (선택)

- [ ] **Nginx Reverse Proxy 설정**:
  - [ ] nginx.conf 작성 (/, /api/, /dicom-web/, /viewer/)
  - [ ] React API_BASE_URL을 상대 경로로 변경
  - [ ] CORS 설정 제거 (Nginx가 Same-Origin 처리)
  - [ ] HTTPS 리디렉션 설정 (Let's Encrypt)

- [ ] **프로덕션 배포 테스트**:
  - [ ] VM 재부팅 후 서비스 정상 동작 확인
  - [ ] React → Nginx → Django 호출 테스트
  - [ ] Orthanc FHIR API 외부 접근 확인

- [ ] **문서화**:
  - [ ] 12_배포_가이드_GCP.md 업데이트
  - [ ] 고정 IP 설정 가이드
  - [ ] Nginx 설정 가이드

---

## 🎯 예상 효과

### FHIR-Orthanc 연동
- ✅ 표준 FHIR 클라이언트 호환 (SMART on FHIR 앱 연동 가능)
- ✅ DICOM → FHIR 변환 로직 자동화 (개발 공수 절감)
- ✅ 외부 EMR/HIS 시스템과 FHIR 표준으로 연동

### GCP IP 변경 대응
- ✅ VM 재부팅 시에도 안정적 운영 (고정 IP)
- ✅ 컨테이너 재시작 시에도 통신 유지 (Service Name)
- ✅ 프론트엔드 설정 변경 불필요 (상대 경로)
- ✅ 도메인 연결 가능 (고정 IP → DNS)

---

## 📚 참고 자료

### Orthanc FHIR
- Orthanc FHIR Plugin: https://book.orthanc-server.com/plugins/fhir.html
- DICOM-FHIR Mapping: https://www.hl7.org/fhir/imagingstudy.html
- Orthanc REST API: https://api.orthanc-server.com/

### GCP 고정 IP
- GCP Static IP Guide: https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address
- Docker Networking: https://docs.docker.com/network/

### Nginx Reverse Proxy
- Nginx Proxy Guide: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- Let's Encrypt: https://letsencrypt.org/getting-started/

---

**작성**: Claude AI
**최종 업데이트**: 2025-12-31
**우선순위**: High (프로덕션 배포 전 필수)
**예상 소요**: 5-7일 (FHIR 3-4일 + GCP 2-3일)
