# CDSS Backend - Week 1 Implementation

임상 의사결정 지원 시스템(Clinical Decision Support System) Django Backend

## 완료된 작업 (Week 1)

### ✅ UC01 (ACCT) - 인증/권한 시스템
- [x] 7개 역할 정의 (Admin, Doctor, RIB, Lab, Nurse, Patient, External)
- [x] Custom User 모델 구현
- [x] 역할 기반 권한 클래스 (RBAC)
- [x] 로그인/회원가입/로그아웃 API
- [x] JWT Token 인증

### ✅ UC09 (AUDIT) - 감사 로그 시스템
- [x] AuditLog 모델 구현
- [x] AuditClient 유틸리티
- [x] 로그인/로그아웃 자동 로깅
- [x] 권한 거부 이벤트 로깅

## 디렉토리 구조

```
cdss-backend/
├── cdss_backend/          # Django 프로젝트 설정
│   ├── settings.py        # 설정 파일 (MySQL, CORS, REST Framework)
│   └── urls.py            # 메인 URL 라우팅
├── acct/                  # UC01: 인증/권한 앱
│   ├── models.py          # User 모델 (7개 역할)
│   ├── permissions.py     # 역할 기반 권한 클래스
│   ├── serializers.py     # API 직렬화
│   ├── views.py           # 로그인/회원가입/로그아웃 API
│   └── urls.py            # acct URL 라우팅
├── audit/                 # UC09: 감사 로그 앱
│   ├── models.py          # AuditLog 모델
│   ├── client.py          # AuditClient 유틸리티
│   └── admin.py           # Django Admin 설정
├── emr/                   # UC02: EMR Proxy (Week 2)
├── alert/                 # UC07: 알림 시스템 (Week 2)
├── requirements.txt       # Python 패키지 의존성
├── .env.example           # 환경 변수 템플릿
├── .env                   # 환경 변수 (Git 제외)
├── setup_database.sql     # MySQL 데이터베이스 설정
└── create_test_users.py   # 테스트 사용자 생성 스크립트
```

## 설치 및 실행

### 1. 가상환경 설정

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 보안 모드 설정 (중요!)

**개발 중에는 보안을 비활성화하여 빠르게 테스트할 수 있습니다.**

`.env` 파일 확인:
```env
# 개발 모드 (기본값): 인증/권한 우회
ENABLE_SECURITY=False

# 프로덕션 모드: 인증/권한 필수
# ENABLE_SECURITY=True
```

**개발 모드 (ENABLE_SECURITY=False):**
- ✅ 토큰 없이 모든 API 접근 가능
- ✅ 권한 검증 우회 (빠른 테스트)
- ✅ 감사 로그 부분 기록

**프로덕션 모드 (ENABLE_SECURITY=True):**
- 🔒 Token 인증 필수
- 🔒 역할 기반 권한 검증
- 🔒 전체 감사 로그 기록

**상세 가이드:** [개발모드_가이드.md](개발모드_가이드.md)

---

### 4. 데이터베이스 설정

#### 옵션 A: MySQL (권장)

1. MySQL 설치 (8.0+)
2. 데이터베이스 생성:

```bash
mysql -u root -p < setup_database.sql
```

3. `.env` 파일 설정:

```env
DB_NAME=cdss_db
DB_USER=cdss_user
DB_PASSWORD=cdss_password
DB_HOST=localhost
DB_PORT=3306
```

#### 옵션 B: SQLite (개발/테스트용)

`settings.py`에서 DATABASES 설정을 임시로 변경:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 4. 마이그레이션 실행

```bash
python manage.py migrate
```

### 5. 테스트 사용자 생성

```bash
python manage.py shell < create_test_users.py
```

생성되는 사용자:
- admin1 / admin123 (Admin)
- doctor1 / doctor123 (Doctor)
- rib1 / rib123 (RIB - 방사선과)
- lab1 / lab123 (Lab - 검사실)
- nurse1 / nurse123 (Nurse)
- patient1 / patient123 (Patient)
- external1 / external123 (External)

### 6. 서버 실행

```bash
python manage.py runserver
```

서버 주소: `http://localhost:8000`

## API 엔드포인트

### 인증 (UC01 - ACCT)

| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/api/acct/login/` | 로그인 | AllowAny |
| POST | `/api/acct/register/` | 회원가입 | AllowAny |
| POST | `/api/acct/logout/` | 로그아웃 | IsAuthenticated |
| GET | `/api/acct/me/` | 현재 사용자 정보 | IsAuthenticated |

### 로그인 예시

```bash
curl -X POST http://localhost:8000/api/acct/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor1",
    "password": "doctor123"
  }'
```

응답:
```json
{
  "token": "your_auth_token_here",
  "user": {
    "id": 2,
    "username": "doctor1",
    "email": "doctor@hospital.com",
    "role": "doctor",
    "employee_id": "D001",
    "department": "Neurosurgery"
  }
}
```

### 인증된 요청 예시

```bash
curl -X GET http://localhost:8000/api/acct/me/ \
  -H "Authorization: Token your_auth_token_here"
```

## 7개 역할별 권한

| 역할 | 설명 | 권한 클래스 |
|------|------|-------------|
| Admin | 시스템 관리자 | `IsAdmin` |
| Doctor | 의사 (처방, 진단) | `IsDoctor`, `IsDoctorOrRIB`, `IsDoctorOrNurse` |
| RIB | 방사선과 | `IsRIB`, `IsDoctorOrRIB` |
| Lab | 검사실 | `IsLab` |
| Nurse | 간호사 | `IsNurse`, `IsDoctorOrNurse` |
| Patient | 환자 | `IsSelfOrAdmin` (본인 데이터만 접근) |
| External | 외부 기관 | (추후 정의) |

## 감사 로그 (UC09)

모든 중요한 액션은 자동으로 감사 로그에 기록됩니다:

- 로그인 성공/실패
- 로그아웃
- 회원가입
- 권한 거부

### Django Admin에서 감사 로그 확인

```bash
python manage.py createsuperuser
```

`http://localhost:8000/admin` 접속 후 "Audit logs" 메뉴에서 확인

## 보안 아키텍처 (중요)

### Django 중앙 인증 정책

⚠️ **핵심 원칙: 모든 외부 시스템 접근은 Django를 경유해야 합니다**

**잘못된 구조 ❌:**
```
Client → Nginx → HAPI FHIR (직접 연결) ← 보안 위험!
```

**올바른 구조 ✅:**
```
Client → Nginx → Django (인증/권한 검증) → HAPI FHIR
                    ↓
                감사 로그 기록
```

**보안 원칙:**
1. **Nginx는 Django API만 노출** - 외부 시스템(OpenEMR, Orthanc, HAPI FHIR) 직접 노출 금지
2. **Django에서 인증/권한 검증** - Token 인증 + 역할 기반 권한(RBAC)
3. **감사 로그 필수** - 모든 외부 시스템 접근 기록
4. **Client 클래스 사용** - Django 내부에서만 외부 시스템 호출

**Week 2-3 구현 예정:**
```python
# emr/views.py (Week 2)
@api_view(['GET'])
@permission_classes([IsDoctorOrNurse])  # 권한 검증
def get_patient(request, patient_id):
    client = OpenEMRClient()  # Django 내부에서만 호출
    data = client.get_patient(patient_id)
    AuditClient.log_event(...)  # 감사 로그
    return Response(data)
```

---

## 다음 작업 (Week 2)

- [ ] UC02 (EMR) - OpenEMR 프록시 구현
  - [ ] OpenEMRClient 클래스 (Django 중앙 인증 준수)
  - [ ] 환자 조회 API (`/api/emr/patients/`)
  - [ ] 캐싱 로직
- [ ] UC07 (ALERT) - 알림 시스템 구현
- [ ] React 프론트엔드 초기 설정
- [ ] 로그인 화면 구현

## 문제 해결

### MySQL 연결 오류

```
(1045, "Access denied for user 'cdss_user'@'localhost'")
```

해결:
1. MySQL이 설치되어 있는지 확인
2. `setup_database.sql` 스크립트 실행
3. `.env` 파일의 DB 정보 확인

### 마이그레이션 오류

```bash
python manage.py migrate --run-syncdb
```

### 가상환경 활성화 오류 (Windows PowerShell)

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 프로젝트 정보

- **Django**: 4.2
- **Python**: 3.8+
- **Database**: MySQL 8.0+ (SQLite3 for development)
- **작성일**: 2025-12-22
- **프로젝트 위치**: `c:\Users\302-28\Downloads\UML\cdss-backend`
