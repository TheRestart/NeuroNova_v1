# CDSS UML 프로젝트 - Claude 컨텍스트 문서

> **목적**: 이 문서는 Claude AI가 프로젝트를 빠르게 이해하고 작업을 이어서 수행할 수 있도록 작성되었습니다.

**문서 작성일**: 2025-12-16
**프로젝트 위치**: `c:\Users\302-28\Downloads\UML`
**프로젝트 타입**: 임상 의사결정 지원 시스템(CDSS) UML 설계 문서

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

### 4.1 UC01 (ACCT) - 인증/권한 시스템

#### 핵심 컴포넌트
```
AuthController
  ├─→ AuthService (로그인/로그아웃)
  │     ├─→ UserRepository
  │     ├─→ PasswordService (bcrypt)
  │     ├─→ LoginDefenseService (무차별 대입 방어)
  │     ├─→ JwtService (액세스 토큰)
  │     ├─→ RefreshTokenService (리프레시 토큰)
  │     └─→ AuditClient (로그인 이벤트 기록)
  │
  ├─→ MeController (내 프로필)
  │     ├─→ JwtService
  │     └─→ AccessPolicyService (권한 체크)
  │
  └─→ RoleAdminController (역할 관리)
        ├─→ RoleRepository
        ├─→ PermissionRepository
        └─→ UserRoleRepository
```

#### 도메인 모델 (uc01_02_domain.puml)
```
User (사용자)
  - userId: UUID
  - username: String
  - passwordHash: String
  - status: UserStatus (ACTIVE, LOCKED, DISABLED)
  - failedLoginCount: int
  - lockedUntil: DateTime

Role (역할)
  - roleKey: String
  - name: String
  - enabled: bool

Permission (권한)
  - permKey: String
  - description: String

UserRole (사용자-역할 매핑)
  - userId: UUID (FK)
  - roleKey: String (FK)

RolePermission (역할-권한 매핑)
  - roleKey: String (FK)
  - permKey: String (FK)

RefreshToken (리프레시 토큰)
  - tokenId: UUID
  - userId: UUID (FK)
  - tokenHash: String
  - status: RefreshTokenStatus (ACTIVE, REVOKED, EXPIRED)
  - expiresAt: DateTime
  - rotatedFrom: UUID (토큰 로테이션)
```

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

### 4.2 UC02 (EMR) - OpenEMR 프록시

#### 핵심 컴포넌트
```
PatientController
  └─→ PatientProxyService
        ├─→ OpenEMRClient (외부 API)
        ├─→ PatientCacheRepository (캐싱)
        └─→ EncounterCacheRepository
```

#### 설계 패턴
- **Pull-Based**: Django가 OpenEMR에서 데이터를 가져옴 (Push 없음)
- **Cache-Aside**: 조회 시 캐시 먼저 확인 → 없으면 EMR에서 Pull → 캐시 저장
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

### 4.5 UC08 (FHIR) - 의료정보 교환

#### 핵심 컴포넌트
```
FHIRController
  └─→ FHIRTransformService
        ├─→ FHIRResourceMapRepository (리소스 매핑)
        ├─→ HAPIClient (HAPI FHIR 서버)
        └─→ FHIRTxQueueRepository (전송 큐)
```

#### CDSS → FHIR 매핑
```
CDSS Entity          → FHIR Resource
─────────────────────────────────────
EMR_PATIENT_CACHE    → Patient
RADIOLOGY_ORDERS     → ServiceRequest
RADIOLOGY_STUDIES    → ImagingStudy
AI_RESULTS           → DiagnosticReport
TIMELINE_EVENTS      → AuditEvent
```

#### 동기화 전략
- **Change Data Capture**: CDSS DB 변경 감지 → FHIR_TX_QUEUE 삽입
- **Retry Logic**: 전송 실패 시 exponential backoff 재시도
- **Idempotent**: 동일 리소스 중복 전송 방지 (FHIR_RESOURCE_MAP으로 추적)

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

**5. Timeline & Alerts (UC07)**
```
TIMELINE_EVENTS
  └─ USER_NOTIFICATIONS
       └─ (사용자 FK: user_id → ACCT_USERS)
```

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

---

**이 문서는 Claude AI가 프로젝트를 빠르게 온보딩하기 위해 작성되었습니다.**
**사용자용 가이드는 `이용법.md`를 참조하세요.**
**개발 업무 계획은 `업무계획서.md`를 참조하세요.**
