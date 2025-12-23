# CDSS 프로젝트 인수인계 문서

**작성일**: 2025-12-22  
**프로젝트**: Clinical Decision Support System (임상 의사결정 지원 시스템)  
**프로젝트 위치**: `d:\1222\NeuroNova_v1`

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [완료된 작업](#완료된-작업)
3. [코딩 규칙 및 주의사항](#코딩-규칙-및-주의사항)
4. [다음 작업 (계속 진행해야 할 것)](#다음-작업)
5. [환경 설정 방법](#환경-설정-방법)
6. [트러블슈팅](#트러블슈팅)

---

## 🎯 프로젝트 개요

### 시스템 구성
- **Backend**: Django REST API (Python)
- **Frontend**: React (TypeScript + Tailwind CSS) + Flutter (Patient용)
- **Database**: SQLite (개발용, 추후 MySQL 전환)
- **외부 시스템**: Orthanc (DICOM), RabbitMQ (Queue), OpenEMR (EMR)
- **AI**: Flask AI Server (추후 통합)

### 9개 UC 모듈
1. **UC1 (ACCT)** - 인증/권한 (7개 역할 RBAC) - ⏳ 미구현 
2. **UC2 (EMR)** - OpenEMR 연동 - ✅ 완료
3. **UC3 (OCS)** - 처방전달시스템 - ⏳ 미구현
4. **UC4 (LIS)** - 임상병리정보시스템 - ⏳ 미구현
5. **UC5 (RIS)** - 영상의학 (Orthanc) - ✅ Week 3 완료
6. **UC6 (AI)** - AI Queue - ✅ Week 3 완료 (Flask AI는 추후)
7. **UC7 (ALERT)** - 알림 시스템 - ⏳ 미구현
8. **UC8 (FHIR)** - 의료정보 교환 - ⏳ 미구현
9. **UC9 (AUDIT)** - 감사 로그 - ⏳ 미구현

---

## ✅ 완료된 작업

### Week 1-2: EMR 기본 구현
- **UC2 (EMR)**: OpenEMR Docker 연동 완료
  - `emr/clients/openemr_client.py` - OpenEMR API 클라이언트
  - Patient, Encounter 모델
  - 8개 API 엔드포인트
  - HTML 테스트 UI (`emr-test-ui.html`)

### Week 3: RIS + AI 인프라 (최근 완료)

#### 1. Orthanc PACS 연동 (UC5 - RIS)
- **위치**: `NeuroNova_02_back_end/03_orthanc_pacs/`
- **Docker 설정**: `docker-compose.yml`
- **Django 앱**: `ris/`
  - `clients/orthanc_client.py` - 8개 메서드 (health_check, get_studies 등)
  - `models.py` - RadiologyOrder, RadiologyStudy, RadiologyReport
  - `views.py` - Orthanc 동기화, CRUD API
  - `urls.py` - `/api/ris/` 라우팅

#### 2. RabbitMQ AI Queue (UC6 - AI)
- **위치**: `NeuroNova_02_back_end/04_rabbitmq_queue/`
- **Docker 설정**: `docker-compose.yml`
- **Django 앱**: `ai/`
  - `queue_client.py` - RabbitMQ 클라이언트 (Pika)
  - `models.py` - AIJob (상태 추적)
  - `views.py` - AI Job 제출/조회 API
  - `urls.py` - `/api/ai/` 라우팅

#### 3. React 프론트엔드 초기 설정
- **위치**: `NeuroNova_03_front_end_react/01_react_client/`
- TypeScript + Tailwind CSS 환경
- `types/index.ts` - 타입 정의
- `api/axios.ts` - Axios 인스턴스 (토큰 자동 처리)
- `stores/authStore.ts` - Zustand 인증 스토어
- `components/Login.tsx` - 로그인 페이지
- `components/Dashboard.tsx` - 역할별 대시보드

---

## 🏗️ 시스템 아키텍처

### Backend Layer 구조
`View (Controller)` → `Service (Business Logic)` → `Model (Data)` / `Client (External API)`

- **Views**: 요청/응답 처리, 권한 체크만 담당 (`views.py`)
- **Services**: 비즈니스 로직, 트랜잭션 관리 (`services.py`)
- **Models**: DB 스키마 (`models.py`)
- **Clients**: 외부 시스템(Orthanc, RabbitMQ) 통신 (`clients/`)

### Database
- **Main**: MySQL (`cdss_db`) - Django 메인 DB
- **EMR**: MySQL (`openemr`) - OpenEMR 읽기 전용 (Port 3307)

### 1. 필수 개발 환경
```
- Backend: Windows PowerShell (Django)
- Frontend: WSL Ubuntu-22.04 LTS (React npm)
- Docker: Windows Docker Desktop
```

> **중요**: PowerShell에서는 `&&` 대신 `;`를 사용해야 합니다!
> ```bash
> # 잘못된 예
> cd folder && python manage.py runserver
> 
> # 올바른 예
> cd folder; python manage.py runserver
> ```

### 2. Django 아키텍처 원칙

#### 폴더 구조 규칙
```
NeuroNova_02_back_end/
└── 01_django_server/
    ├── emr/           # UC별 앱
    ├── ris/
    ├── ai/
    ├── 03_orthanc_pacs/     # 외부 서버는 번호 폴더
    ├── 04_rabbitmq_queue/
    └── cdss_backend/  # Django 프로젝트 설정
```

> **주의**: 모든 외부 서버(Orthanc, RabbitMQ 등)는 `01_django_server/` 아래에 `번호_서버이름/` 형식으로 폴더를 만듭니다.

#### Layer 구조 (중요!)
```
Controller (views.py)
    ↓
Service (services.py) - 비즈니스 로직
    ↓
Repository (repositories.py) - DB 접근
    ↓
Client (clients/) - 외부 API 호출
```

**현재 상태**: Week 3까지는 Service/Repository 레이어 없이 View에서 직접 구현했습니다. Week 4부터는 제대로 된 레이어 구조로 리팩토링 필요합니다!

### 3. 보안 토글 (ENABLE_SECURITY)

#### 개발 모드 (현재 설정)
```python
# settings.py
ENABLE_SECURITY = False
```
- 모든 API가 `AllowAny` 권한
- 인증 없이 테스트 가능
- 빠른 개발/디버깅

#### 프로덕션 모드 (배포 시)
```python
ENABLE_SECURITY = True
```
- 역할 기반 권한 체크 활성화
- 모든 API에 `IsAuthenticated` 또는 역할별 Permission 필요
- **주의**: UC1 (ACCT) 앱 구현 완료 후 전환해야 함!

### 4. 외부 시스템 연동 주의사항

#### ✅ 올바른 구조
```
Client (React/Flutter)
    ↓
Django API (/api/ris/, /api/emr/)
    ↓ (인증/권한 체크)
    ↓
Orthanc/OpenEMR/RabbitMQ
```

#### ❌ 잘못된 구조
```
Client → 직접 Orthanc 호출 (보안 위험!)
```

> **중요**: 클라이언트는 절대 외부 시스템에 직접 접근하면 안 됩니다. 반드시 Django를 경유해야 합니다.

### 5. Django Model 작성 시 주의사항

#### ✅ 현재 사용 중인 User 모델
```python
from django.contrib.auth.models import User  # Django 기본 User
```

#### 🔜 추후 변경 예정 (UC1 구현 후)
```python
from acct.models import User  # Custom User (7개 역할)
```

> **주의**: UC1 (ACCT) 앱 구현 후에는 RIS/AI 모델의 User ForeignKey를 모두 변경해야 합니다.

### 6. Migration 주의사항

```bash
# 앱별로 마이그레이션 생성 (권장)
python manage.py makemigrations emr
python manage.py makemigrations ris
python manage.py makemigrations ai

# 전체 마이그레이션 (의존성 꼬일 수 있음)
python manage.py makemigrations  # 주의해서 사용
```

### 7. 환경 변수 관리

#### .env 파일 사용 (추후 구현 필요) (진행함)
현재는 `settings.py`에 하드코딩되어 있지만, 추후 `python-dotenv`로 변경해야 합니다:

```python
# settings.py (추후 수정 예정)
import os
from dotenv import load_dotenv

load_dotenv()

ORTHANC_API_URL = os.getenv('ORTHANC_API_URL', 'http://localhost:8042')
```













---

## 📝 다음 작업 (계속 진행해야 할 것)

### 🔥 긴급 (Week 3 마무리)

#### 1. Python 패키지 설치
```bash
cd NeuroNova_02_back_end/01_django_server
pip install -r requirements.txt
```

**필수 패키지**:
- `pika==1.3.2` (RabbitMQ)
- `pydicom==2.4.3` (DICOM 파싱)

#### 2. Django 마이그레이션 실행
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3. Docker 컨테이너 실행
```bash
# Orthanc
cd 03_orthanc_pacs
docker-compose up -d

# RabbitMQ
cd ../04_rabbitmq_queue
docker-compose up -d
```

#### 4. 기본 테스트
```bash
# Django 서버 실행
python manage.py runserver

# 다른 터미널에서 테스트
curl http://localhost:8000/api/ris/health/
curl http://localhost:8000/api/emr/health/
```

### 🎯 Week 4 작업 (다음 우선순위)

#### 1. UC1 (ACCT) - 인증/권한 시스템 구현
**우선순위**: ⭐⭐⭐⭐⭐ (최우선!)

이유: 다른 모든 UC가 이 모듈에 의존합니다.

**구현 사항**:
- `acct/models.py`
  ```python
  class User(AbstractUser):
      role = models.CharField(choices=ROLE_CHOICES)
      # 7개 역할: admin, doctor, rib, lab, nurse, patient, external
  ```
- JWT 토큰 인증 (`djangorestframework-simplejwt`)
- `/api/acct/login/`, `/api/acct/register/`
- 역할별 Permission 클래스 10개

**완료 후 작업**:
- RIS/AI 모델의 User ForeignKey 변경
- `ENABLE_SECURITY=True`로 전환
- 모든 View에 Permission 적용

#### 2. UC09 (AUDIT) - 감사 로그
**우선순위**: ⭐⭐⭐⭐

현재 RIS views.py에서 `audit.client.AuditClient` 호출 코드를 주석 처리했으므로, 이를 복구해야 합니다.

**구현 사항**:
- `audit/models.py` - AuditLog 모델
- `audit/client.py` - AuditClient 유틸리티
- 모든 중요 액션에 로그 기록 (`LOGIN`, `PATIENT_VIEW`, `REPORT_SIGN` 등)

#### 3. React 프론트엔드 개선
**우선순위**: ⭐⭐⭐

**구현 사항**:
- DICOMViewer 컴포넌트 (Cornerstone.js 사용)
- API 통합 테스트
- 역할별 화면 완성

#### 4. Service/Repository 레이어 리팩토링
**우선순위**: ⭐⭐

현재 View에서 직접 Client/Model을 호출하고 있습니다. 제대로 된 아키텍처로 분리:

```python
# ris/services.py (신규 생성)
class RadiologyService:
    def __init__(self):
        self.orthanc_client = OrthancClient()
        self.study_repo = RadiologyStudyRepository()
    
    def sync_studies(self):
        # 비즈니스 로직
        pass

# ris/views.py (수정)
@api_view(['GET'])
def sync_orthanc_studies(request):
    service = RadiologyService()
    result = service.sync_studies()
    return Response(result)
```

### 📅 Week 5 이후 작업

#### UC3 (OCS) - 처방전달시스템
- Prescription 모델
- Doctor가 처방 생성

#### UC4 (LIS) - 임상병리정보
- LabTest, LabResult 모델
- 검사 오더 및 결과 관리

#### UC7 (ALERT) - 알림 시스템
- Django Channels (WebSocket)
- 실시간 알림

#### UC8 (FHIR) - HAPI FHIR 연동
- FHIR 리소스 변환
- 외부 병원과 데이터 교환

#### Flask AI Server 통합
- 다른 팀원이 구현한 Flask AI Server를 RabbitMQ에 연결
- Worker 프로세스 구현 (큐에서 Job 꺼내서 처리)

---

## 🔧 환경 설정 방법

### 1. 프로젝트 클론 (이미 완료)
```bash
d:\1222\NeuroNova_v1
```

### 2. Python 가상환경 (권장)
```bash
cd NeuroNova_02_back_end/01_django_server
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. React 환경 (WSL Ubuntu)
```bash
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/01_react_client
npm install
```

### 4. Docker Desktop
- Orthanc: http://localhost:8042 (orthanc/orthanc123)
- RabbitMQ: http://localhost:15672 (guest/guest)

### 5. .env 파일 생성 (추후)
```bash
cp .env.example .env
# .env 파일 수정
```

---

















## 🐛 트러블슈팅

### 1. PowerShell에서 `&&` 에러
**증상**: `앰퍼샌드(&) 문자를 사용할 수 없습니다`

**해결**:
```bash
# 잘못됨
cd folder && python manage.py runserver

# 올바름
cd folder; python manage.py runserver
```

### 2. `ModuleNotFoundError: No module named 'acct'`
**원인**: UC1 (ACCT) 앱이 아직 생성되지 않음

**임시 해결**:
```python
# models.py
from django.contrib.auth.models import User  # acct.models.User 대신
```

**영구 해결**: UC1 앱 구현 후 변경

### 3. `ModuleNotFoundError: No module named 'pika'`
**원인**: RabbitMQ 클라이언트 미설치

**해결**:
```bash
pip install pika==1.3.2
```

### 4. Docker 컨테이너 실행 안 됨
**확인 사항**:
```bash
# Docker Desktop 실행 확인
docker ps

# 포트 충돌 확인
netstat -ano | findstr :8042  # Orthanc
netstat -ano | findstr :5672  # RabbitMQ
```

### 5. React npm 명령어 안 됨 (PowerShell)
**원인**: npm은 WSL에서만 실행해야 함

**해결**:
```bash
# WSL Ubuntu 터미널에서 실행
wsl
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/01_react_client
npm start
```

---

## 📚 주요 문서 위치

### 프로젝트 문서
- `README.md` - 프로젝트 전체 개요
- `01_doc/03_개발_작업_순서.md` - 개발 계획 (Week 1-4)
- `01_doc/LOG_작업이력.md` - 작업 이력

---

## 🙋 질문이 있다면?

### 코드 위치 찾기
```bash
# Backend
NeuroNova_02_back_end/01_django_server/
  ├── emr/          # OpenEMR 연동
  ├── ris/          # Orthanc PACS 연동
  ├── ai/           # RabbitMQ AI Queue
  └── cdss_backend/ # Django 설정

# Frontend
NeuroNova_03_front_end_react/01_react_client/
  ├── src/
  │   ├── components/  # Login, Dashboard
  │   ├── stores/      # Zustand (authStore)
  │   ├── api/         # Axios
  │   └── types/       # TypeScript 타입
```

### API 엔드포인트
- `/api/emr/` - OpenEMR 관련
- `/api/ris/` - Orthanc PACS 관련
- `/api/ai/` - AI Job 관련

### 테스트 방법
```bash
# Backend API 테스트
curl http://localhost:8000/api/ris/health/

# RabbitMQ 확인
http://localhost:15672 접속 (guest/guest)

# Orthanc 확인
http://localhost:8042 접속 (orthanc/orthanc123)
```

---

## ✅ 최종 체크리스트 (인수인계 전)

- [ ] `pip install -r requirements.txt` 실행 완료
- [ ] Django 마이그레이션 완료
- [ ] Orthanc Docker 실행 확인
- [ ] RabbitMQ Docker 실행 확인
- [ ] Django 서버 정상 기동 (`python manage.py runserver`)
- [ ] `/api/ris/health/` API 응답 확인
- [ ] `/api/ai/submit/` AI Job 제출 테스트
- [ ] React 프론트엔드 빌드 확인 (WSL에서 `npm start`)

---

**작업을 인수받는 분께**: 궁금한 점이 있으면 이 문서를 먼저 참조하고, 해결되지 않으면 프로젝트 루트의 다른 문서들을 확인해주세요. 행운을 빕니다! 🚀
