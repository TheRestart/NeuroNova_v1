# Week 1 작업 완료 보고서

**프로젝트**: CDSS (Clinical Decision Support System)
**작업 기간**: Week 1
**작업 완료일**: 2025-12-22
**위치**: `c:\Users\302-28\Downloads\UML\cdss-backend`

---

## ✅ 완료 항목

### 1. Django 프로젝트 초기 설정
- [x] Django 4.2 프로젝트 생성 (`cdss_backend`)
- [x] 가상환경 설정 및 패키지 설치
- [x] 4개 Django 앱 생성:
  - `acct` (UC01: 인증/권한)
  - `audit` (UC09: 감사 로그)
  - `emr` (UC02: EMR Proxy - 구조만)
  - `alert` (UC07: 알림 - 구조만)
- [x] `requirements.txt` 생성

### 2. Settings.py 구성
- [x] MySQL 데이터베이스 연동 설정
- [x] CORS 설정 (React 연동 준비)
- [x] REST Framework 설정
- [x] Custom User 모델 설정 (`AUTH_USER_MODEL = 'acct.User'`)
- [x] 외부 시스템 연동 준비 (OpenEMR, Orthanc, HAPI FHIR)
- [x] `.env.example` 환경 변수 템플릿 생성

### 3. UC01 (ACCT) - 인증/권한 시스템 구현 ⭐
- [x] **User 모델**:
  - AbstractUser 확장
  - 7개 역할 정의 (Admin, Doctor, RIB, Lab, Nurse, Patient, External)
  - 추가 필드: `role`, `employee_id`, `department`, `phone`
  - 역할별 헬퍼 메서드 (`is_admin`, `is_doctor` 등)

- [x] **권한 클래스** (`acct/permissions.py`):
  - `IsAdmin` - Admin만 접근
  - `IsDoctor` - Doctor만 접근
  - `IsRIB` - 방사선과만 접근
  - `IsLab` - 검사실만 접근
  - `IsNurse` - 간호사만 접근
  - `IsDoctorOrRIB` - Doctor 또는 RIB 접근
  - `IsDoctorOrNurse` - Doctor 또는 Nurse 접근
  - `IsSelfOrAdmin` - 본인 또는 Admin 접근 (Patient용)
  - `IsAdminOrReadOnly` - Admin은 쓰기, 나머지는 읽기만
  - `IsStaffRole` - 의료진 역할만 접근

- [x] **API 엔드포인트**:
  - `POST /api/acct/login/` - 로그인
  - `POST /api/acct/register/` - 회원가입
  - `POST /api/acct/logout/` - 로그아웃
  - `GET /api/acct/me/` - 현재 사용자 정보

- [x] **Serializers**:
  - `UserSerializer` - 사용자 정보
  - `UserCreateSerializer` - 회원가입 (비밀번호 검증)
  - `LoginSerializer` - 로그인 요청
  - `LoginResponseSerializer` - 로그인 응답

- [x] Django Admin 통합

### 4. UC09 (AUDIT) - 감사 로그 시스템 구현 ⭐
- [x] **AuditLog 모델**:
  - 필드: `user`, `action`, `resource_type`, `resource_id`, `ip_address`, `user_agent`, `timestamp`, `details`
  - 액션 타입: CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, LOGIN_FAILED, PERMISSION_DENIED, UNAUTHORIZED_ACCESS
  - 데이터베이스 인덱스: `user+timestamp`, `resource_type+timestamp`, `action+timestamp`

- [x] **AuditClient** (`audit/client.py`):
  - `log_event()` - 일반 이벤트 로깅
  - `log_login_success()` - 로그인 성공
  - `log_login_failed()` - 로그인 실패
  - `log_logout()` - 로그아웃
  - `log_permission_denied()` - 권한 거부
  - `log_resource_access()` - 리소스 접근
  - IP 주소 및 User-Agent 자동 추출

- [x] **로그인 API와 통합**:
  - 로그인 성공 시 자동 로그
  - 로그인 실패 시 자동 로그
  - 로그아웃 시 자동 로그
  - 권한 거부 시 자동 로그

- [x] Django Admin 통합 (읽기 전용, Superuser만 삭제 가능)

### 5. 데이터베이스 설정
- [x] `setup_database.sql` - MySQL 초기 설정 스크립트
- [x] Django 마이그레이션 파일 생성:
  - `acct/migrations/0001_initial.py` (User 모델)
  - `audit/migrations/0001_initial.py` (AuditLog 모델 + 인덱스)

### 6. 테스트 및 문서화
- [x] `create_test_users.py` - 7개 역할별 테스트 사용자 생성 스크립트
- [x] `README.md` - 백엔드 설치 및 사용 가이드
- [x] `WEEK1_COMPLETION_SUMMARY.md` - 이 문서

---

## 📁 생성된 파일 목록

```
cdss-backend/
├── cdss_backend/
│   ├── settings.py         ✅ 구성 완료
│   └── urls.py             ✅ acct 라우팅 추가
├── acct/
│   ├── models.py           ✅ User 모델 (7개 역할)
│   ├── permissions.py      ✅ 10개 권한 클래스
│   ├── serializers.py      ✅ 4개 Serializer
│   ├── views.py            ✅ 4개 API 엔드포인트
│   ├── urls.py             ✅ URL 라우팅
│   ├── admin.py            ✅ Admin 설정
│   └── migrations/
│       └── 0001_initial.py ✅ User 마이그레이션
├── audit/
│   ├── models.py           ✅ AuditLog 모델
│   ├── client.py           ✅ AuditClient
│   ├── admin.py            ✅ Admin 설정
│   └── migrations/
│       └── 0001_initial.py ✅ AuditLog 마이그레이션
├── emr/                    (Week 2)
├── alert/                  (Week 2)
├── requirements.txt        ✅ 의존성 목록
├── .env.example            ✅ 환경 변수 템플릿
├── .env                    ✅ 환경 변수
├── setup_database.sql      ✅ MySQL 설정 스크립트
├── create_test_users.py    ✅ 테스트 사용자 생성
├── README.md               ✅ 설치/사용 가이드
└── WEEK1_COMPLETION_SUMMARY.md ✅ 이 문서
```

---

## 🧪 테스트 사용자

`create_test_users.py` 스크립트로 생성된 7개 역할별 사용자:

| 역할 | Username | Password | 이메일 | 직원번호 | 부서 |
|------|----------|----------|--------|----------|------|
| Admin | admin1 | admin123 | admin@hospital.com | A001 | IT |
| Doctor | doctor1 | doctor123 | doctor@hospital.com | D001 | Neurosurgery |
| RIB | rib1 | rib123 | rib@hospital.com | R001 | Radiology |
| Lab | lab1 | lab123 | lab@hospital.com | L001 | Laboratory |
| Nurse | nurse1 | nurse123 | nurse@hospital.com | N001 | Emergency |
| Patient | patient1 | patient123 | patient@example.com | - | - |
| External | external1 | external123 | external@partner.com | - | External Partner |

---

## 🔗 API 엔드포인트 테스트

### 1. 로그인 테스트

```bash
curl -X POST http://localhost:8000/api/acct/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor1",
    "password": "doctor123"
  }'
```

**응답 예시**:
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0...",
  "user": {
    "id": 2,
    "username": "doctor1",
    "email": "doctor@hospital.com",
    "role": "doctor",
    "employee_id": "D001",
    "department": "Neurosurgery",
    "first_name": "의사",
    "last_name": "이",
    "is_active": true,
    "created_at": "2025-12-22T00:00:00Z"
  }
}
```

### 2. 현재 사용자 정보 조회

```bash
curl -X GET http://localhost:8000/api/acct/me/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0..."
```

### 3. 로그아웃

```bash
curl -X POST http://localhost:8000/api/acct/logout/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0..."
```

---

## 📊 감사 로그 확인

Django Admin을 통해 감사 로그 확인:

1. Superuser 생성:
   ```bash
   python manage.py createsuperuser
   ```

2. `http://localhost:8000/admin` 접속

3. "Audit logs" 메뉴에서 로그 확인

**기록되는 이벤트**:
- LOGIN (로그인 성공)
- LOGIN_FAILED (로그인 실패)
- LOGOUT (로그아웃)
- CREATE (사용자 생성)
- PERMISSION_DENIED (권한 거부)

---

## 🚀 다음 작업 (Week 2)

### Day 8-10: UC2 (EMR) - OpenEMR 프록시 구현
- [ ] `emr/models.py` - Patient/Encounter 캐시 모델
- [ ] `emr/client.py` - OpenEMR API 클라이언트
- [ ] `emr/views.py` - 환자 조회 API
- [ ] OpenEMR 연동 테스트

### Day 11-12: UC7 (ALERT) - 알림 시스템
- [ ] `alert/models.py` - Alert 모델
- [ ] `alert/views.py` - 알림 API
- [ ] WebSocket 준비 (Django Channels)

### Day 13-14: React 프론트엔드 초기 설정
- [ ] React + TypeScript 프로젝트 생성
- [ ] Tailwind CSS 설정
- [ ] Zustand 상태 관리
- [ ] 로그인 화면 구현
- [ ] 역할별 대시보드 라우팅

---

## 📝 주요 기술 스택

| 항목 | 기술 | 버전 |
|------|------|------|
| Framework | Django | 4.2 |
| API | Django REST Framework | 3.16.1 |
| Database | MySQL (or SQLite) | 8.0+ |
| Authentication | Token Authentication | - |
| CORS | django-cors-headers | 4.9.0 |
| Environment | python-dotenv | 1.2.1 |
| Python | Python | 3.13.5 |

---

## 🔧 사용된 디자인 패턴

1. **Repository Pattern**: 데이터 접근 로직 분리
2. **Serializer Pattern**: API 데이터 변환
3. **Middleware Pattern**: 인증 및 CORS 처리
4. **Singleton Pattern**: AuditClient (static methods)
5. **Strategy Pattern**: 역할별 권한 클래스

---

## 💡 중요 결정 사항

1. **Custom User 모델 사용**: Django의 AbstractUser 확장하여 7개 역할 지원
2. **Token 인증**: JWT 대신 DRF Token Authentication 사용 (간단함, Week 1에 적합)
3. **감사 로그 자동화**: AuditClient를 통해 일관된 로깅
4. **역할 기반 권한**: 각 역할별로 독립적인 Permission 클래스 생성
5. **환경 변수**: .env 파일로 민감한 설정 분리

---

## ⚠️ 알려진 이슈 및 주의사항

1. **MySQL 연결 필요**:
   - 현재 설정은 MySQL을 기본으로 함
   - 개발/테스트 시 SQLite로 임시 전환 가능
   - `setup_database.sql` 스크립트로 데이터베이스 초기화 필요

2. **외부 시스템 연동 미완료**:
   - OpenEMR, Orthanc, HAPI FHIR는 Week 2 이후 작업
   - `.env` 파일에 URL만 준비됨

3. **프론트엔드 미구현**:
   - API만 구현됨
   - React 프론트엔드는 Week 2 Day 13-14 작업

4. **테스트 코드 미작성**:
   - Unit Test는 Week 4에 작성 예정

---

## 📞 문의 및 지원

문제 발생 시 확인 사항:
1. 가상환경 활성화 확인: `venv\Scripts\activate`
2. 패키지 설치 확인: `pip install -r requirements.txt`
3. 마이그레이션 실행 확인: `python manage.py migrate`
4. 환경 변수 설정 확인: `.env` 파일 존재 여부

---

**작업 완료**: Week 1의 모든 목표를 성공적으로 달성했습니다! 🎉

다음 Week 2 작업을 진행하시려면 [03_개발_작업_순서.md](../../03_개발_작업_순서.md)의 Week 2 섹션을 참고하세요.
