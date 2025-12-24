# CDSS UML 프로젝트 - Claude 컨텍스트 문서

> **목적**: 이 문서는 Claude AI가 프로젝트를 빠르게 이해하고 작업을 이어서 수행할 수 있도록 작성되었습니다.

**문서 작성일**: 2025-12-16
**최종 업데이트**: 2025-12-24
**프로젝트 위치**: `d:\1222\NeuroNova_v1`
**프로젝트 타입**: 임상 의사결정 지원 시스템(CDSS) - Django 백엔드 구현 중심

---

## ⚡ 중요: 프로젝트 R&R (역할 분담)

### 현재 담당자(나)의 역할: AI 코어 모델 개발

**책임 범위:**
- ✅ AI 모델 개발 (MRI 종양 분석, Omics 분석)
- ✅ 데이터 전처리 파이프라인
- ✅ 추론 로직 구현 (독립 Python 모듈)

**제외 사항 (타 팀원 담당):**
- ❌ Backend Serving (Flask API)
- ❌ Web Frontend (React)
- ❌ Mobile App (Flutter)

**개발 전략:**
- 독립 실행 가능한 Python 모듈 개발
- Interface Specification 문서 작성 필수
- 타 팀 코드 의존 금지

**관련 문서:**
- [17_프로젝트_RR_역할분담.md](17_프로젝트_RR_역할분담.md)
- [18_AI_개발_가이드.md](18_AI_개발_가이드.md)

---

## 1. 프로젝트 개요

### 1.1 시스템 설명
- **시스템명**: CDSS (Clinical Decision Support System)
- **아키텍처**: Django 기반 마이크로서비스 + 외부 시스템 통합
- **설계 방법론**: UML 기반 상세 설계
- **주요 통합 시스템**:
  - OpenEMR (전자의무기록)
  - Orthanc (DICOM 서버)
  - HAPI FHIR (의료정보 교환)
  - AI 모델 서버

### 1.2 Use Case 구성 (9개 모듈)

| UC | 모듈명 | 설명 | 핵심 기능 |
|---|---|---|---|
| UC1 | ACCT | Accounts/Auth | JWT 인증, RBAC 권한, MFA |
| UC2 | EMR | EMR Proxy | OpenEMR 데이터 Pull, 캐싱 |
| UC3 | OCS | Order Communication System | 처방 전달 |
| UC4 | LIS | Lab Information System | 임상병리 검사 |
| UC5 | RIS | Radiology Information System | 영상 검사 오더, DICOM 연동 |
| UC6 | AI | AI Orchestration | AI 모델 호출, 결과 관리 |
| UC7 | ALERT | Timeline/Alert Core | 이벤트 타임라인, 알림 |
| UC8 | FHIR | FHIR Gateway | FHIR 리소스 변환, 동기화 |
| UC9 | AUDIT | Audit/Admin | 감사 로그, 보안 이벤트 |

---

## 2. 디렉토리 구조 및 파일 맵

```
c:\Users\302-28\Downloads\UML\
├── 이용법.md                    # 사용자용 가이드
├── CLAUDE_CONTEXT.md            # [이 파일] Claude용 컨텍스트
└── UML/
    ├── CDSS System 상세설계.mdj  # StarUML 전체 설계 (시스템 다이어그램)
    │
    ├── usecase/                 # Use Case Diagrams (액터-시스템 상호작용)
    │   ├── UC1-Accounts-Auth.puml
    │   ├── UC2-EMR-Proxy.puml
    │   └── ... (UC3~UC9)
    │
    ├── sequence/                # Sequence Diagrams (시간순 메시지 흐름)
    │   ├── 1. ACCT/
    │   │   ├── SD-ACCT-01.puml  # 로그인 성공
    │   │   ├── SD-ACCT-02.puml  # 로그인 실패
    │   │   └── ... (01~05)
    │   ├── 2. EMR/              # SD-EMR-01~05
    │   ├── 5. RIS/              # SD-RIS-01~14 (가장 복잡)
    │   └── ... (3~9)
    │
    ├── class/                   # Class Diagrams (클래스 구조 및 관계)
    │   ├── 1. UC01 (ACCT)/
    │   │   ├── uc01_01_class_main.puml      # [진입점] 전체 통합
    │   │   ├── uc01_02_domain.puml          # 도메인 엔티티
    │   │   ├── uc01_03_dtos.puml            # API Request/Response
    │   │   ├── uc01_04_clients.puml         # 외부 시스템 클라이언트
    │   │   ├── uc01_05_repositories.puml    # 데이터 접근 계층
    │   │   ├── uc01_06_services.puml        # 비즈니스 로직
    │   │   └── uc01_07_controllers.puml     # API 엔드포인트
    │   └── ... (2~9 동일 구조)
    │
    └── db/                      # ERD (Entity-Relationship Diagrams)
        ├── CDSS_DB.mmd          # Django CDSS 메인 DB
        ├── CDSS_DB.png/svg      # 렌더링된 이미지
        ├── HAPI_DB.mmd          # HAPI FHIR 서버 DB
        ├── OpenEMR_DB.mmd       # OpenEMR DB
        ├── Orthanc_DB.mmd       # Orthanc DICOM DB
        └── IntegrationERD.mmd   # 전체 통합 ERD
```

---

## 3. 아키텍처 패턴 이해

### 3.1 레이어 아키텍처 (공통)

모든 UC는 동일한 7-Layer 구조를 따릅니다:

```
┌─────────────────────────────────────┐
│  7. Controllers (API Endpoints)     │  ← REST API 진입점
├─────────────────────────────────────┤
│  6. Services (Business Logic)       │  ← 핵심 비즈니스 로직
├─────────────────────────────────────┤
│  5. Repositories (Data Access)      │  ← ORM/DB 추상화
├─────────────────────────────────────┤
│  4. Clients (External Systems)      │  ← 외부 API 호출
├─────────────────────────────────────┤
│  3. DTOs (Data Transfer Objects)    │  ← API 계약
├─────────────────────────────────────┤
│  2. Domain (Entities)                │  ← 도메인 모델
├─────────────────────────────────────┤
│  1. Main (Integration)               │  ← 레이어 간 연결
└─────────────────────────────────────┘
```

**의존성 흐름**: Controller → Service → Repository/Client
**도메인 모델**: 모든 레이어에서 참조 가능

### 3.2 파일 읽기 순서 (UC 분석 시)

1. **`uc0X_01_class_main.puml`** ← 먼저 읽기 (전체 구조 파악)
2. `uc0X_02_domain.puml` (데이터 모델)
3. `uc0X_06_services.puml` (핵심 로직)
4. `uc0X_07_controllers.puml` (API 인터페이스)
5. 나머지 레이어 (필요 시)

---

## 4. UC별 상세 분석

### 4.1 UC01 (ACCT) - 인증/권한 시스템 ✅ 구현 완료

#### 핵심 컴포넌트
```
AuthController (views.py)
  ├─→ AuthService (로그인/로그아웃)
  │     ├─→ UserService (사용자 관리)
  │     ├─→ JWT (djangorestframework-simplejwt)
  │     └─→ Django Auth (비밀번호 검증)
  │
  ├─→ login() - POST /api/acct/login/
  ├─→ logout() - POST /api/acct/logout/
  ├─→ me() - GET /api/acct/me/
  └─→ UserViewSet
        ├─→ register() - POST /api/acct/users/register/
        └─→ CRUD (Admin only)

Permission Classes (permissions.py)
  ├─→ IsAdmin, IsDoctor, IsRIB, IsLab, IsNurse
  ├─→ IsDoctorOrRIB, IsDoctorOrNurse
  ├─→ IsSelfOrAdmin (Patient용)
  └─→ IsAdminOrReadOnly, IsStaffRole
```

**구현 상태:**
- ✅ Custom User 모델 (AUTH_USER_MODEL = 'acct.User')
- ✅ JWT 토큰 인증 (Access + Refresh)
- ✅ 7개 역할 시스템 (admin, doctor, rib, lab, nurse, patient, external)
- ✅ Service 레이어 패턴
- ✅ 10개 Permission 클래스

#### 도메인 모델 (실제 구현: acct/models.py)
```python
User (AbstractBaseUser, PermissionsMixin)
  - user_id: UUID (PK)
  - username: String (unique)
  - email: EmailField (unique)
  - role: String (choices: admin, doctor, rib, lab, nurse, patient, external)
  - full_name: String
  - department: String
  - license_number: String
  - is_active: Boolean
  - is_staff: Boolean
  - is_superuser: Boolean
  - created_at: DateTime
  - last_login: DateTime

JWT Token (djangorestframework-simplejwt)
  - Access Token: 1시간 (설정 가능)
  - Refresh Token: 7일 (설정 가능)
  - Token Rotation: 활성화
  - Blacklist: 활성화 (로그아웃 시)
```

**UML 설계와의 차이점:**
- ✅ User 모델은 Django AbstractBaseUser 기반으로 단순화
- ✅ Role은 User 모델의 CharField로 구현 (별도 테이블 없음)
- ⏳ Permission은 Django의 기본 Permission 시스템 활용 가능
- ⏳ RefreshToken은 simplejwt의 token_blacklist 앱으로 관리

#### 주요 흐름 (SD-ACCT-01: 로그인 성공)
```
User → UI: ID/PW 입력
UI → AuthController: POST /auth/login
AuthController → AuthService: login()
  AuthService → UserRepository: 사용자 조회
  AuthService → PasswordService: 비밀번호 검증
  AuthService → AccessPolicyService: role/permission 로딩
  AuthService → JwtService: 액세스 토큰 발급
  AuthService → RefreshTokenService: 리프레시 토큰 발급
  AuthService → AuditClient: log_event(LOGIN_SUCCESS)
AuthController → UI: 200 OK (tokens, profile)
```

#### 핵심 설계 의도
- **Stateless JWT**: 세션 없이 JWT로 인증
- **Token Rotation**: 리프레시 토큰 재발급 시 이전 토큰 무효화
- **Login Defense**: 로그인 실패 횟수 추적 → 계정 잠금
- **RBAC**: Role-Based Access Control (역할 기반 권한)

---

### 4.2 UC02 (EMR) - OpenEMR 프록시 ✅ 구현 완료

#### 핵심 컴포넌트 (실제 구현)
```
EMRController (views.py) - OpenEMR 연동 API
  └─→ EMRService (services.py)
        └─→ OpenEMRClient (openemr_client.py) - 외부 API

EMR CRUD ViewSets (viewsets.py) - 내부 CRUD API
  ├─→ PatientCacheViewSet
  │     └─→ PatientService (services.py)
  │           └─→ PatientRepository (repositories.py)
  ├─→ EncounterViewSet
  │     └─→ EncounterService (services.py)
  │           └─→ EncounterRepository (repositories.py)
  ├─→ OrderViewSet
  │     └─→ OrderService (services.py)
  │           └─→ OrderRepository (repositories.py)
  └─→ OrderItemViewSet
        └─→ OrderItemRepository (repositories.py)

Models (models.py)
  ├─→ PatientCache (환자 기본 정보 캐시)
  │     - patient_id: P-YYYY-NNNNNN (PK, 자동 생성)
  │     - family_name, given_name, birth_date, gender
  │     - phone, email, address
  │     - emergency_contact (JSON), allergies (JSON)
  │     - openemr_patient_id (외부 동기화)
  ├─→ Encounter (진료 기록)
  │     - encounter_id: E-YYYY-NNNNNN (PK, 자동 생성)
  │     - patient (FK), doctor_id (FK → acct.User)
  │     - encounter_type, department, chief_complaint
  │     - diagnosis, status, encounter_date
  ├─→ Order (처방 주문)
  │     - order_id: O-YYYY-NNNNNN (PK, 자동 생성)
  │     - patient (FK), encounter (FK, nullable)
  │     - ordered_by (FK → acct.User), order_type, urgency, status
  └─→ OrderItem (처방 항목)
        - item_id: OI-ORDERID-NNN (PK, 자동 생성)
        - order (FK), drug_code, drug_name, dosage, frequency
        - duration, route, instructions
```

**구현 상태:**
- ✅ Service/Repository 레이어 패턴 완성 (3-layer)
- ✅ OpenEMRClient 외부 API 통합
- ✅ MySQL 캐싱 구조
- ✅ OCS (Order Communication System) 모델 포함
- ✅ JSON 필드 활용 (allergies, emergency_contact)
- ✅ DRF ViewSets를 통한 REST API CRUD 엔드포인트 (4개)
- ✅ 자동 ID 생성 정책 (Service 레이어에서 처리)
- ✅ Transaction 보장 (Order + OrderItem 동시 생성)
- ✅ 테스트 UI (emr_crud_test.html) - 예시입력 버튼 포함
- ✅ OrderItem 개별 CRUD 지원 (PATCH, DELETE)
- ✅ Custom User 모델 FK 연결 (doctor_id, ordered_by)
- ✅ **데이터 충돌 방지 전략** (2025-12-24)
  - **낙관적 락**: `version` 필드 기반 동시성 제어 (PatientCache, Encounter, Order, OrderItem)
  - **비관적 락**: `select_for_update()` 기반 로우 잠금 (서비스 레이어 적용)
  - **멱등성 보장**: `IdempotencyMiddleware` (`X-Idempotency-Key` 헤더 기반 응답 캐싱)
  - **DB 격리 수준**: MySQL `READ COMMITTED` 설정으로 성능/정합성 균형 최적화

#### API 엔드포인트

**OpenEMR 연동 API:**
- GET /api/emr/health/ - OpenEMR 연결 상태 확인
- POST /api/emr/auth/ - OpenEMR 인증
- GET /api/emr/openemr/patients/ - OpenEMR 환자 목록
- GET /api/emr/openemr/patients/search/ - OpenEMR 환자 검색
- GET /api/emr/openemr/patients/{id}/ - OpenEMR 환자 상세

**CRUD API (DRF Router):**
- GET /api/emr/patients/ - 환자 목록
- POST /api/emr/patients/ - 환자 생성 (ID 자동 생성)
- GET /api/emr/patients/{id}/ - 환자 상세
- PUT/PATCH /api/emr/patients/{id}/ - 환자 수정
- DELETE /api/emr/patients/{id}/ - 환자 삭제
- GET /api/emr/patients/search/?q={query} - 환자 검색

- GET /api/emr/encounters/ - 진료 기록 목록
- POST /api/emr/encounters/ - 진료 기록 생성 (ID 자동 생성)
- GET /api/emr/encounters/{id}/ - 진료 기록 상세
- PUT/PATCH /api/emr/encounters/{id}/ - 진료 기록 수정
- DELETE /api/emr/encounters/{id}/ - 진료 기록 삭제
- GET /api/emr/encounters/by_patient/?patient_id={id} - 환자별 진료 기록

- GET /api/emr/orders/ - 처방 목록
- POST /api/emr/orders/ - 처방 생성 (ID 자동 생성, 항목 포함)
- GET /api/emr/orders/{id}/ - 처방 상세
- PUT/PATCH /api/emr/orders/{id}/ - 처방 수정
- DELETE /api/emr/orders/{id}/ - 처방 삭제
- POST /api/emr/orders/{id}/execute/ - 처방 실행
- GET /api/emr/orders/by_patient/?patient_id={id} - 환자별 처방 목록

- GET /api/emr/order-items/ - 처방 항목 목록
- POST /api/emr/order-items/ - 처방 항목 생성
- GET /api/emr/order-items/{id}/ - 처방 항목 상세
- PATCH /api/emr/order-items/{id}/ - 처방 항목 수정
- DELETE /api/emr/order-items/{id}/ - 처방 항목 삭제

**테스트 UI:**
- GET /api/emr/comprehensive-test/ - **종합 테스트 대시보드** (⭐ 최신, 추천)
  - 6개 탭: Overview, OpenEMR Integration, Patient CRUD, Encounter CRUD, Order/OCS, Write-Through
  - Write-Through 패턴 테스트 통합
  - 실시간 통계 대시보드
- GET /api/emr/test-dashboard/ - 통합 테스트 대시보드 (순차적 CRUD 시나리오)
- GET /api/emr/test-ui/ - 레거시 OpenEMR 테스트 UI

#### 설계 패턴
- **Pull-Based**: Django가 OpenEMR에서 데이터를 가져옴 (Push 없음)
- **Cache-Aside**: 조회 시 캐시 먼저 확인 → 없으면 EMR에서 Pull → 캐시 저장
- **Parallel Dual-Write**: 데이터 생성/수정 시 OpenEMR DB와 Django DB에 독립적으로 병렬 전달 (2025-12-24 변경)
**설계 철학:**
- **Distributed Persistence**: OpenEMR(원본)과 Django DB(캐시/비즈니스)를 독립적인 저장 시스템으로 취급
- **Parallel Delivery**: 요청이 들어오면 두 시스템에 병렬적으로(Concurrency) 데이터를 전달하여 최신성 동기화
- **High Visibility**: API 응답 시 각 DB(테이블별) 저장 성공 여부를 독립적으로 반환하여 투명성 확보
- **Concurrency Control**: 
  - **Optimistic Locking**: 업데이트 시 `version` 필드 증가 및 필터링
  - **Pessimistic Locking**: `atomic` 트랜잭션 내 `select_for_update` 사용
- **Idempotency**: `X-Idempotency-Key` 헤더 기반 응답 캐싱 및 중복 요청 차단

**데이터 흐름:**
```
사용자 → Django API → [1] OpenEMR DB (Insert) & [2] Django DB (Insert) -- 병렬/독립 전달
                           ↓ 각 DB별 결과 취합 (persistence_status)
                       성공/실패 상태를 포함한 구조화된 응답 반환
```
- **Aggregate View**: 환자 요약 카드 생성 시 여러 소스 집계
  - Radiology Orders (UC5)
  - Lab Results (UC4)
  - AI Results (UC6)
  - Timeline Events (UC7)

#### 주요 흐름 (SD-EMR-01: 환자 검색)
```
Doctor → UI: 이름/ID 입력
UI → EMRController: GET /patients?query=...
EMRController → PatientProxyService:
  PatientProxyService → OpenEMRClient: REST /patients/search
  PatientProxyService → PatientCacheRepository: cache upsert
EMRController → UI: patient list DTO
```

---

### 4.3 UC05 (RIS) - 영상의학 (가장 복잡)

#### 핵심 컴포넌트
```
RadiologyController
  └─→ RadiologyService
        ├─→ RadiologyOrderRepository (오더 관리)
        ├─→ RadiologyStudyRepository (검사 관리)
        ├─→ OrthancClient (DICOM 서버)
        ├─→ AIClient (AI 모델 호출)
        └─→ TimelineClient (이벤트 발행)
```

#### 워크플로우 (14개 Sequence Diagram)
1. **오더 생성** (SD-RIS-01)
2. **DICOM 업로드** (SD-RIS-02) - Orthanc로 전송
3. **Study 생성** (SD-RIS-03) - DICOM 메타데이터 파싱
4. **AI 자동 트리거** (SD-RIS-04) - 특정 Modality 시 AI 호출
5. **AI 결과 수신** (SD-RIS-05)
6. **판독문 작성** (SD-RIS-06~08)
7. **판독문 서명** (SD-RIS-09)
8. **DICOM Viewer** (SD-RIS-10~11) - Orthanc API 프록시
9. **Study 상태 관리** (SD-RIS-12~14)

#### 외부 시스템 통합
- **Orthanc**: DICOM 저장소 (C-STORE, WADO-RS)
- **AI Server**: REST API로 모델 호출
- **FHIR**: ImagingStudy 리소스로 변환

---

### 4.4 UC06 (AI) - AI 오케스트레이션

#### 핵심 컴포넌트
```
AIJobController
  └─→ AIOrchestrationService
        ├─→ AIJobRepository (작업 큐)
        ├─→ AIModelClient (외부 AI 서버)
        ├─→ AIResultRepository (결과 저장)
        └─→ AIPollingService (비동기 폴링)
```

#### 비동기 처리 패턴
```
1. AI Job 제출 → 즉시 job_id 반환
2. Background Worker가 주기적으로 AI 서버 폴링
3. 결과 준비되면 DB에 저장 + Timeline 이벤트 발행
4. UI는 WebSocket으로 실시간 알림 수신
```

#### AI 결과 구조
```
AI_RESULTS
  - result_id
  - ai_job_id (FK)
  - tumor_class (분류 결과)
  - metrics_json (정확도, 신뢰도 등)

AI_ARTIFACTS (결과 파일)
  - artifact_id
  - result_id (FK)
  - kind (HEATMAP, SEGMENTATION, RAW)
  - storage_uri (S3/MinIO)
  - checksum
```

---

### 4.5 UC08 (FHIR) - 의료정보 교환 ✅ 구축 완료

#### 핵심 컴포넌트
```
FHIRController
  └─→ FHIRServiceAdapter (HAPI FHIR 연동)
        ├─→ HAPI FHIR Server (Docker, Port 8080)
        └─→ REST API (requests)
```

#### 아키텍처 변경사항 (2025-12-23)
- **HAPI FHIR Server**: 기존 OpenEMR 내장 FHIR 대신, 별도의 HAPI FHIR JPA Server를 구축하여 **메인 FHIR 게이트웨이**로 사용.
- **설정**: `FHIR_SERVER_URL = 'http://localhost:8080/fhir'`

#### 동기화 전략
- **OpenEMR First**: 데이터 생성 시 OpenEMR에 먼저 저장.
- **HAPI Sync**: 주요 리소스(Patient, Encounter)는 HAPI FHIR 서버로 동기화 (구현 예정).

---

### 4.6 UC09 (AUDIT) - 감사/보안

#### 핵심 컴포넌트
```
AuditController
  └─→ AuditService
        ├─→ AuditLogRepository (모든 액션 기록)
        └─→ SecurityEventRepository (보안 이벤트)
```

#### 로깅 대상
```
AUDIT_LOGS (일반 감사)
  - LOGIN, LOGOUT
  - PATIENT_VIEW, PATIENT_EDIT
  - ORDER_CREATE, REPORT_SIGN
  - ROLE_ASSIGN

SECURITY_EVENTS (보안)
  - LOGIN_FAILED (5회 이상)
  - UNAUTHORIZED_ACCESS
  - PERMISSION_DENIED
  - TOKEN_REVOKED
```

#### 모든 UC에서 AuditClient 호출
```python
# 예시: UC01 로그인 시
audit_client.log_event(
    action="LOGIN_SUCCESS",
    actor_user_id=user.user_id,
    ip=request.ip,
    target_type="USER",
    target_id=user.user_id
)
```

---

## 5. 데이터베이스 스키마 (ERD)

### 5.1 CDSS_DB.mmd (메인 DB)

#### 주요 테이블 그룹

**1. Accounts (UC01)**
```
ACCT_USERS
  ├─ ACCT_USER_ROLES ─┤
  │                    │
ACCT_ROLES             │
  ├─ ACCT_ROLE_PERMS ─┤
  │                    │
ACCT_PERMISSIONS       │

ACCT_USERS
  ├─ ACCT_REFRESH_TOKENS
  └─ ACCT_MFA_SECRETS
```

**2. EMR Cache (UC02)**
```
EMR_PATIENT_CACHE
  ├─ EMR_ENCOUNTER_CACHE
  ├─ EMR_ID_MAP (외부 ID 매핑)
  └─ EMR_SYNC_JOBS (동기화 작업)
```

**3. Radiology (UC05)**
```
RADIOLOGY_ORDERS
  ├─ RADIOLOGY_STUDIES
  │    ├─ RADIOLOGY_SERIES
  │    └─ RADIOLOGY_REPORTS
  └─ (환자 FK: cdss_patient_id → EMR_PATIENT_CACHE)
```

**4. AI (UC06)**
```
RADIOLOGY_STUDIES
  └─ AI_JOBS
       ├─ AI_JOB_POLLING
       └─ AI_RESULTS
            └─ AI_ARTIFACTS
```

**5. Timeline & Alerts (UC07) - Implemented**
```
TIMELINE_EVENTS (시스템 이벤트)
  └─ USER_NOTIFICATIONS (Alert 모델 - MySQL)
       ├─ user_id (FK)
       ├─ message, type, metadata
       └─ is_read
```
- **Redis Channel Layer**: 실시간 전송 (WebSocket)

**6. FHIR (UC08)**
```
FHIR_RESOURCE_MAP (CDSS ↔ FHIR 매핑)
  ├─ cdss_ref_type, cdss_ref_id
  └─ fhir_id (HAPI 서버의 리소스 ID)

FHIR_TX_QUEUE (전송 큐)
  - resource_type
  - payload_json
  - status, retry_count
```

**7. Audit (UC09)**
```
AUDIT_LOGS
  └─ actor_user_id (FK: ACCT_USERS)

SECURITY_EVENTS
  └─ actor_user_id (FK: ACCT_USERS)
```

### 5.2 외부 시스템 DB

**OpenEMR_DB.mmd**
- 읽기 전용 (Django는 조회만)
- 주요 테이블: `patient_data`, `form_encounter`, `procedure_order`

**Orthanc_DB.mmd**
- DICOM 메타데이터 저장
- 주요 테이블: `Studies`, `Series`, `Instances`

**HAPI_DB.mmd**
- FHIR 리소스 저장
- 주요 테이블: `HFJ_RESOURCE`, `HFJ_RES_VER`

---

## 6. 파일 형식 및 도구

### 6.1 PlantUML (.puml)
- **사용처**: Usecase, Sequence, Class Diagram
- **미리보기**: VSCode에서 `Alt+D`
- **문법 예시**:
  ```plantuml
  @startuml
  class User {
    +userId: UUID
    +username: String
  }
  User "1" o-- "0..*" UserRole
  @enduml
  ```

### 6.2 Mermaid (.mmd)
- **사용처**: ERD
- **미리보기**: VSCode `Ctrl+Shift+V` 또는 mermaid.live
- **문법 예시**:
  ```mermaid
  erDiagram
    ACCT_USERS ||--o{ ACCT_USER_ROLES : has
    ACCT_USERS {
      string user_id PK
      string username
    }
  ```

### 6.3 StarUML (.mdj)
- **사용처**: 전체 시스템 아키텍처
- **도구**: StarUML 7.0 (독립 실행형 GUI)

---

## 7. 작업 시나리오별 가이드

### 7.1 새로운 UC 추가 시

1. **폴더 생성**:
   ```
   /usecase/UC10-NewModule.puml
   /sequence/10. NEWMODULE/SD-NEWMODULE-01.puml
   /class/10. UC10 (NEWMODULE)/
   ```

2. **Class Diagram 7개 파일 생성**:
   - `uc10_01_class_main.puml` (다른 UC 복사 후 수정)
   - `uc10_02_domain.puml`
   - `uc10_03_dtos.puml`
   - `uc10_04_clients.puml`
   - `uc10_05_repositories.puml`
   - `uc10_06_services.puml`
   - `uc10_07_controllers.puml`

3. **ERD 수정**:
   - `db/CDSS_DB.mmd`에 새 테이블 추가
   - `db/IntegrationERD.mmd`에 관계 추가

### 7.2 기존 UC 수정 시

**예시: UC01에 MFA 기능 추가**

1. **Domain 수정**:
   - `uc01_02_domain.puml`에 `MFASecret` 클래스 추가

2. **Service 추가**:
   - `uc01_06_services.puml`에 `MFAService` 추가

3. **Controller 수정**:
   - `uc01_07_controllers.puml`에 `/mfa/setup` 엔드포인트 추가

4. **Main 연결**:
   - `uc01_01_class_main.puml`에 의존성 추가:
     ```plantuml
     AuthController --> MFAService
     MFAService --> MFASecretRepository
     ```

5. **Sequence 추가**:
   - `sequence/1. ACCT/SD-ACCT-06.puml` 생성 (MFA 설정 흐름)

6. **ERD 수정**:
   - `db/CDSS_DB.mmd`에 `ACCT_MFA_SECRETS` 테이블 확인/수정

### 7.3 API 엔드포인트 추가 시

**예시: 환자 알레르기 조회 API 추가 (UC02)**

1. **DTO 추가**:
   ```plantuml
   # uc02_3_dtos.puml
   class AllergyDTO {
     +allergyId: UUID
     +patientId: UUID
     +allergen: String
     +severity: String
   }
   ```

2. **Service 메서드 추가**:
   ```plantuml
   # uc02_6_services.puml
   class PatientProxyService {
     +getAllergies(patientId: UUID): List<AllergyDTO>
   }
   ```

3. **Controller 엔드포인트 추가**:
   ```plantuml
   # uc02_7_controllers.puml
   class PatientController {
     +GET /patients/{id}/allergies
   }
   ```

4. **Main 연결**:
   ```plantuml
   # uc02_1_class_main.puml
   PatientController --> PatientProxyService
   ```

5. **Sequence 추가**:
   - `SD-EMR-06.puml` 생성 (알레르기 조회 흐름)

### 7.4 외부 시스템 통합 시

**예시: 새로운 AI 모델 서버 추가**

1. **Client 추가**:
   ```plantuml
   # uc06_4_clients.puml
   interface NewAIClient <<Interface>> {
     +submitJob(studyId: UUID): String
     +getResult(jobId: String): AIResultDTO
   }
   ```

2. **Service 수정**:
   ```plantuml
   # uc06_6_services.puml
   AIOrchestrationService --> NewAIClient
   ```

3. **설정 문서 작성**:
   - `/docs/integrations/new-ai-model.md` (연동 가이드)

---

## 8. 중요한 설계 원칙

### 8.1 일관성 유지
- 모든 UC는 **동일한 7-Layer 구조** 사용
- 파일 명명 규칙 엄격히 준수:
  - `uc[번호]_[레이어]_*.puml`
  - `SD-[모듈명]-[번호].puml`

### 8.2 관심사 분리
- **Domain**: 비즈니스 로직 없음 (순수 데이터 구조)
- **Service**: 비즈니스 로직만 (HTTP/DB 직접 접근 금지)
- **Controller**: 요청 파싱 + 응답 직렬화만
- **Repository**: SQL/ORM만 (비즈니스 로직 금지)

### 8.3 외부 시스템 추상화
- 모든 외부 API는 **Client 인터페이스**로 추상화
- 테스트 시 Mock 객체로 교체 가능
- 예: `OpenEMRClient`, `OrthancClient`, `AIClient`

### 8.4 감사 추적
- **모든 중요한 액션**은 `AuditClient.log_event()` 호출
- 개인정보 조회/수정은 필수 로깅

### 8.5 보안
- **JWT**: 짧은 만료 시간 (15분)
- **Refresh Token**: 긴 만료 시간 (7일) + Rotation
- **RBAC**: 최소 권한 원칙
- **Login Defense**: 5회 실패 시 15분 잠금
- **CRUD Reliability**:
  - **Optimistic Locking**: `version` 필드 기반 충돌 감지 (PatientCache, Encounter, Order, OrderItem 적용)
  - **Pessimistic Locking**: 수정 시 `select_for_update()`를 통한 강력한 정합성 보장
  - **Idempotency**: `X-Idempotency-Key` 헤더 기반 중복 요청 방지 미들웨어
  - **Atomicity**: 서비스 레이어 내 `transaction.atomic()`을 통한 원자성 보장

---

## 9. 자주 사용하는 UML 패턴

### 9.1 PlantUML 관계 표기법
```plantuml
' 연관 (Association)
ClassA --> ClassB

' 의존 (Dependency)
ClassA ..> ClassB

' 집합 (Aggregation)
ClassA o-- ClassB

' 합성 (Composition)
ClassA *-- ClassB

' 상속 (Inheritance)
ClassA --|> ClassB

' 구현 (Realization)
ClassA ..|> InterfaceB

' 다중성
ClassA "1" --> "0..*" ClassB
```

### 9.2 Sequence Diagram 패턴
```plantuml
' 그룹
group 로그인 인증
  actor -> controller: request
end group

' 조건
alt 성공
  service -> db: insert
else 실패
  service -> log: error
end

' 반복
loop 3회 재시도
  client -> api: request
end
```

---

## 10. 트러블슈팅

### 10.1 PlantUML 미리보기 안 됨
- Java JRE 설치 확인
- VSCode PlantUML 확장 설치 확인
- 파일 인코딩 UTF-8 확인

### 10.2 !include 경로 오류
- `uc0X_01_class_main.puml`과 다른 파일이 **같은 디렉토리**에 있어야 함
- 상대 경로 사용: `!include uc01_02_domain.puml`

### 10.3 Mermaid 렌더링 실패
- Mermaid Preview 확장 설치
- 또는 https://mermaid.live 사용

### 10.4 다이어그램이 너무 복잡함
- `hide empty members` 사용 (빈 클래스 숨김)
- `left to right direction` 사용 (가로 배치)
- 개별 레이어 파일만 열어보기

---

## 11. 다음 작업 시 체크리스트

새로운 Claude 인스턴스가 작업을 시작할 때:

- [ ] `이용법.md` 읽기 (사용자 관점)
- [ ] `CLAUDE_CONTEXT.md` 읽기 (이 문서)
- [ ] 작업 대상 UC의 `uc0X_01_class_main.puml` 읽기
- [ ] 관련 Sequence Diagram 읽기
- [ ] `db/CDSS_DB.mmd` 또는 `IntegrationERD.mmd` 읽기
- [ ] 기존 패턴 준수하며 작업 수행
- [ ] 수정 후 관련된 3개 다이어그램(Usecase, Sequence, Class) 일관성 확인

---

## 12. 추가 참고 자료

### 12.1 외부 문서 (프로젝트에 없음 - 필요 시 참고)
- PlantUML 공식 문서: https://plantuml.com/ko/
- Mermaid 공식 문서: https://mermaid.js.org/
- Django REST Framework: https://www.django-rest-framework.org/
- FHIR R4 Spec: https://hl7.org/fhir/R4/

### 12.2 주요 용어 사전
- **CDSS**: Clinical Decision Support System (임상 의사결정 지원 시스템)
- **EMR**: Electronic Medical Record (전자의무기록)
- **RIS**: Radiology Information System (영상의학정보시스템)
- **LIS**: Laboratory Information System (임상병리정보시스템)
- **OCS**: Order Communication System (처방전달시스템)
- **FHIR**: Fast Healthcare Interoperability Resources (의료정보 교환 표준)
- **DICOM**: Digital Imaging and Communications in Medicine (의료영상 표준)
- **JWT**: JSON Web Token (인증 토큰)
- **RBAC**: Role-Based Access Control (역할 기반 접근 제어)

---

## 13. 업무 계획서

### 13.1 업무계획서.md
프로젝트 개발을 위한 상세 업무 계획서가 작성되었습니다.
- **파일 위치**: `업무계획서.md`
- **작성일**: 2025-12-19

### 13.2 주요 내용
**기술 스택별 업무 분류**
- Frontend - React Web (의료진용 데스크톱)
- Frontend - Flutter Mobile (모바일 앱)
- Backend - Django REST API (9개 UC 모듈)
- Database - MySQL/MariaDB
- 외부 시스템 통합 (OpenEMR, Orthanc, HAPI FHIR)

**상용 서버 확인 사항 (중요)**

OpenEMR, Orthanc, HAPI FHIR는 외부 상용 서버를 사용합니다.
개발 시작 전 반드시 확인해야 할 사항:

1. **OpenEMR (전자의무기록)**
   - API 엔드포인트 URL 및 인증 정보
   - 읽기 전용 DB 계정 (선택)
   - IP Whitelist 등록
   - 환자 ID 체계 및 데이터 규격

2. **Orthanc (DICOM 서버)**
   - DICOMweb API URL 및 인증
   - DICOM AE Title 설정
   - 지원 Modality 목록 확인
   - DICOM 태그 구조

3. **HAPI FHIR (의료정보 교환)**
   - FHIR Server URL 및 버전 (R4 권장)
   - OAuth 2.0 인증 정보
   - 지원 리소스 타입 확인
   - Subscription/Webhook 설정

**팀 구성**
- Frontend Team: 3-4명
- Backend Team: 4-5명
- Database Team: 1-2명
- Integration Team: 2명
- QA/Test Team: 2명

**개발 일정**
- Phase 1: 기반 구축 (Week 1-4)
- Phase 2: 핵심 기능 개발 (Week 5-10)
- Phase 3: 고급 기능 및 통합 (Week 11-14)
- Phase 4: 최적화 및 배포 준비 (Week 15-16)

---

## 변경 이력

| 날짜 | 작성자 | 변경 내용 |
|---|---|---|
| 2025-12-16 | Claude (초기 인스턴스) | 문서 최초 작성 |
| 2025-12-19 | Claude | 업무계획서 작성 및 CLAUDE_CONTEXT.md 업데이트<br>- 기술 스택별 업무 분류 추가<br>- 상용 서버 확인 사항 정리<br>- 팀 구성 및 개발 일정 추가 |
| 2025-12-23 (오전) | Claude | 프로젝트 현황 반영 업데이트<br>- UC01 (ACCT) 구현 완료 반영<br>- UC02 (EMR) Service/Repository 레이어 구조 추가<br>- Custom User 모델 적용 상태 업데이트<br>- MySQL 데이터베이스 전환 완료 반영 |
| 2025-12-23 (오후) | Claude | EMR CRUD 기능 완성 업데이트<br>- EMR CRUD ViewSets 전체 구현 완료<br>- Patient/Encounter/Order 자동 ID 생성 정책 추가<br>- DRF Router 기반 REST API 엔드포인트 전체 구성<br>- Service/Repository 3-layer 패턴 완성<br>- 테스트 UI (emr_crud_test.html) 구현<br>- 테스트 사용자 7개 역할 생성<br>- Transaction 보장 로직 추가 |
| 2025-12-23 (저녁) | Claude | 프로젝트 전체 검토 및 문서 업데이트<br>- OrderItem 개별 CRUD API 추가 (ViewSet 구현)<br>- Custom User FK 연결 확인 (doctor_id, ordered_by)<br>- 테스트 대시보드 추가 (통합 테스트 UI)<br>- REF_CLAUDE_CONTEXT.md 최신화<br>- LOG_작업이력.md 최신화 |
| 2025-12-23 (심야) | Claude | Write-Through 패턴 구현 및 종합 테스트 대시보드 완성<br>- FHIR Service Adapter 구현 (fhir_adapter.py)<br>- PatientCacheViewSet에 Write-Through 패턴 적용<br>- Write-Through 패턴 유닛 테스트 완료 (7개 테스트 Pass)<br>- 16_Write_Through_패턴_가이드.md 문서 작성<br>- 종합 테스트 대시보드 구현 (comprehensive_test.html)<br>- 6개 탭 통합 테스트 UI 완성<br>- 15_테스트_페이지_가이드.md 업데이트<br>- REF_CLAUDE_CONTEXT.md 설계 패턴 추가 |
| 2025-12-24 (오전) | Claude | 프로젝트 현황 재검토 및 문서 최신화<br>- 실제 프로젝트 위치 확인 (d:\1222\NeuroNova_v1)<br>- 현재 구현 상태 정확히 반영<br>- 테스트 파일 위치 업데이트 (templates/emr/comprehensive_test.html)<br>- FHIR Adapter 구현 상태 확인<br>- Write-Through 패턴 적용 확인 |
| 2025-12-24 (오후) | Claude | AI 코어 개발 R&R 정의 및 문서 작성<br>- 17_프로젝트_RR_역할분담.md 생성<br>- 18_AI_개발_가이드.md 생성<br>- Interface Specification 템플릿 생성<br>- AI 개발자 역할 명확화 (Backend/Frontend 제외)<br>- 독립 모듈 개발 전략 수립 |

---

**이 문서는 Claude AI가 프로젝트를 빠르게 온보딩하기 위해 작성되었습니다.**
**사용자용 가이드는 `이용법.md`를 참조하세요.**
**개발 업무 계획은 `업무계획서.md`를 참조하세요.**
