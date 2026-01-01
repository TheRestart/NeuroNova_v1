# Archived Work Logs (2024 - Week 6)

This archive contains work logs from the beginning of the project (Week 1) through Week 6 (ending Dec 28, 2025).
For current work logs, please refer to `LOG_작업이력.md`.

---

### Week 6 (2025-12-24)
- **2025-12-24**:
  - [x] **진단 마스터 데이터 확장**: ICD-10 기반 뇌/호흡기 질환 진단 코드 99종 확충 및 자동 로드 스크립트 실행
  - [x] **AI 모듈 통합(UC06)**: `AIJob` 모델 확장(Review status 추가), RabbitMQ 비동기 요청 및 Callback 수신 서비스 구현
  - [x] **의료진 검토 워크플로우**: AI 분석 결과에 대한 승인/반려 및 알림 연동 기능 완성
  - [x] **통합 검증**: `verify_ai_integration.py`를 통한 전체 AI 비동기 흐름 검증 성공

### Week 5 (2025-12-24)
- **2025-12-24**:
  - [x] **감사 로그 뷰어 개발**: 관리자용 실시간 감사 로그 모니터링 웹 뷰어 구현 및 UI 최적화
  - [x] **LIS/Alert 연동**: 검사 결과 이상치 판정 시 실시간 WebSocket 알림 발송 로직 강화
  - [x] **EMR 안정화**: Patient Repository 내 ID 핸들링 버그 수정 및 `PatientCache` 생성 검증
  - [x] **Parallel Dual-Write 리팩토링**: `Patient`, `Encounter`, `Order` 서비스를 병렬 데이터 전달 구조로 변경

### Week 4
- **2025-12-24**:
  - [x] 낙관적/비관적 락킹 전략 구현 (`version` 필드 및 `select_for_update`)
  - [x] 멱등성 미들웨어(`IdempotencyMiddleware`) 및 `X-Idempotency-Key` 적용
  - [x] AI 코어 개발 R&R 및 인터페이스 규격 정의
- **2025-12-23**:
  - [x] OCS(처방) 고도화: `OrderItem` CRUD 및 ID 생성 버그 수정
  - [x] Write-Through 패턴 적용 (FHIR Adapter 연동)
  - [x] 종합 테스트 대시보드(`/api/emr/comprehensive-test/`) 구축

### Week 3
- [x] Orthanc PACS (UC5) 연동 클라이언트 및 모델 구현
- [x] RabbitMQ (UC6) AI Queue 인프라 구축
- [x] React 역할별 대시보드 및 JWT 인증 연동 완성

### Week 2 (2025-12-22)
**UC02 (EMR) - OpenEMR 연동 및 유닛테스트 완료**
- **OpenEMR Docker 환경**:
  - [x] OpenEMR 7.0.3 Docker 컨테이너 구동 (포트 80, 443)
  - [x] MariaDB 11.8 연동
- **Django EMR 앱 구현**:
  - [x] OpenEMRClient 구현 (인증, 환자 조회, 검색, 진료 기록, 바이탈 조회)
  - [x] Patient, Encounter 모델 설계 및 캐싱 로직
  - [x] 8개 API 엔드포인트 구현 (`/api/emr/`)
  - [x] 감사 로그 통합 (프로덕션 모드)
- **테스트**:
  - [x] HTML 테스트 UI 구현 (emr-test-ui.html)
  - [x] 유닛테스트 16개 작성 (81% 통과율)
- **UC07 (ALERT) - 알림 시스템 레이아웃**:
  - [x] Alert 모델 정의 (4단계 심각도: INFO, WARNING, CRITICAL, CODE_BLUE)
  - [x] 알림 목록 조회 API 구현
  - [x] 읽음 처리 API 구현
- **React 프론트엔드 초기화**:
  - [x] React + TypeScript + Tailwind CSS 환경 구축
  - [x] 역할별 테마 색상 정의
  - [x] axios, react-router-dom, zustand 설치

### Week 1 (2025-12-22)
**프로젝트 초기 설정 및 UC01, UC09 완료**
- **프로젝트 구조**:
  - [x] Django 4.2 프로젝트 생성 (cdss_backend)
  - [x] MySQL 8.0+ 연동 설정
  - [x] acct, audit, emr, alert 앱 생성
- **UC01 (ACCT) - 인증/권한 시스템**:
  - [x] 7개 역할 정의 (Admin, Doctor, RIB, Lab, Nurse, Patient, External)
  - [x] 커스텀 User 모델 구현
  - [x] 10개 권한 클래스 구현 (IsAdmin, IsDoctor, IsDoctorOrRIB, IsSelfOrAdmin 등)
  - [x] JWT/Token 기반 인증 시스템 구축
  - [x] 4개 API 엔드포인트 (login, register, logout, me)
- **UC09 (AUDIT) - 감사 로그 시스템**:
  - [x] AuditLog 모델 설계
  - [x] AuditClient 유틸리티 구현 (IP, User-Agent 자동 기록)
  - [x] 로그인/로그아웃/권한 거부 자동 로깅
  - [x] Django Admin 통합 (읽기 전용)
- **보안 아키텍처**:
  - [x] Django 중앙 인증 정책 수립
  - [x] 개발 모드 토글 기능 구현 (ENABLE_SECURITY)
  - [x] 7개 역할별 테스트 사용자 생성 스크립트
- **Phase 1 인프라 고도화 (2025-12-29)**:
  - [x] 커스텀 에러 핸들링 시스템 (`CDSSException`, Global Handler) 구현 및 적용
  - [x] Swagger/OpenAPI 3.0 자동 문서화(`drf-spectacular`) 설정 및 주요 API 어노테이션 추가
  - [x] `PatientCache` 모델 및 시리얼라이저 데이터 검증 강화 (주민등록번호 필드 추가 및 유효성 체크)

### Week 7-2 (2025-12-30 23:50)
**정적 코드 개선 및 마스터 데이터 시딩 시스템 구축**

- **환경 변수 검증 로직 추가**:
  - [x] `settings.py`에 `require_env()` 함수 구현 (프로덕션 환경에서 필수 환경 변수 누락 시 즉시 오류)
  - [x] SECRET_KEY, DB 연결 정보 (NAME, USER, PASSWORD, HOST)에 검증 적용
  - [x] `.env.example` 파일 업데이트 (필수 변수 명시 및 주석 추가)

- **마스터 데이터 시딩 시스템 구축** (최우선 과제 완료):
  - [x] `data/medication_master.json` 생성 (30개 약물 데이터, KDC/EDI 코드 기반)
  - [x] `data/lab_test_master.json` 생성 (50개 검사 항목, LOINC 코드 기반)
  - [x] `ocs/management/commands/seed_master_data.py` Management Command 작성
    - 진단(100개 ICD-10), 약물(30개), 검사(50개) 통합 시딩
    - --diagnosis-only, --medication-only, --labtest-only, --force 옵션 지원
    - 사용법: `python manage.py seed_master_data`

- **공통 검증 유틸리티 생성**:
  - [x] `utils/validators.py` 작성 (재사용 가능한 검증 함수 모음)
    - `validate_ssn_kr()`: 주민등록번호 형식 + 체크섬 검증
    - `validate_phone_kr()`: 한국 전화번호 형식 검증
    - `validate_email()`: 이메일 형식 검증
    - `validate_birth_date()`: 생년월일 검증 (미래 날짜 불가)
    - `validate_icd10_code()`: ICD-10 진단 코드 형식 검증
    - `validate_loinc_code()`: LOINC 검사 코드 형식 검증
    - `UniqueFieldValidator`: 중복 필드 검증 클래스

- **EMR Serializer 리팩토링**:
  - [x] `emr/serializers.py`의 `PatientValidationMixin` 리팩토링
  - [x] 중복 검증 로직 제거, 공통 validators 사용으로 변경
  - [x] 코드 가독성 및 재사용성 개선

- **문서 업데이트**:
  - [x] `오류정리_antigra_1230.md` 업데이트 (환경 변수 검증, 마스터 데이터 시딩 기록)
  - [x] `REF_CLAUDE_ONBOARDING_QUICK.md` 업데이트 (정적 코드 개선 완료 항목 추가)
  - [x] `LOG_작업이력.md` 업데이트 (Week 7-2 작업 내역 기록)
  - [x] `작업_계획_요약.md` 업데이트 예정 (다음 작업 체크리스트 반영)

**다음 작업 (원본 PC 복귀 후)**:
- [ ] 마스터 데이터 시딩 실행 (`python manage.py seed_master_data`)
- [ ] Foreign Key 마이그레이션 dry-run 테스트
- [ ] Django 서버 기동 및 환경 변수 검증 확인
- [ ] N+1 쿼리 분석 (Django Debug Toolbar)
- [ ] 인덱스 최적화 마이그레이션 적용

### Week 7-3 (2025-12-31 00:15)
**프론트엔드 테스트 클라이언트 코드 개선**

- **React 테스트 클라이언트 개선**:
  - [x] `.env.example` 파일 생성 (환경 변수 설정 가이드)
  - [x] `apiClient.js` 에러 처리 강화
    - 네트워크 에러 처리 추가 (서버 미응답 시 명확한 메시지)
    - 토큰 갱신 (Refresh Token) 로직 구현
    - 에러 메시지 정규화 (백엔드 에러 응답 형식 대응)
    - 401 Unauthorized 시 자동 토큰 갱신 재시도

- **데이터베이스 인덱스 최적화** (서버 불필요):
  - [x] `emr/models.py` - PatientCache 모델에 ssn 인덱스 추가
  - [x] `emr/models.py` - Order 모델에 status+order_type 복합 인덱스 추가

- **문서 업데이트**:
  - [x] `LOG_작업이력.md` 업데이트
  - [x] `REF_CLAUDE_ONBOARDING_QUICK.md` 업데이트 예정
  - [x] `작업_계획_요약.md` 업데이트 예정

**다음 작업 (원본 PC 복귀 후)**:
- [ ] 인덱스 마이그레이션 생성 및 적용 (`python manage.py makemigrations && python manage.py migrate`)
- [ ] 마스터 데이터 시딩 실행
- [ ] React 테스트 클라이언트 실행 테스트 (WSL 또는 로컬)
- [ ] 전체 통합 테스트

---

## Week 7-4 (2025-12-31) - OHIF Viewer React 통합

### 🎯 목표
React 테스트 클라이언트에 OHIF Viewer를 npm 패키지로 통합하여 Orthanc DICOM 이미지를 시각화

### ✅ 완료 작업

#### 1. 서비스 구조 문서 업데이트 (v3.0)
**파일**: [07_서비스_구조_요약.md](07_서비스_구조_요약.md)
- Multi-SPA 전략 폐기, 단일 React 빌드로 통합
- OHIF Viewer를 npm 패키지로 React 프로젝트에 포함
- 라우팅 규칙 간소화 (`/viewer/:studyInstanceUID`)
- 빌드 배포 경로 통합 (`/var/www/react-build`)

#### 2. OHIF Viewer 패키지 설치
**파일**: [package.json](../NeuroNova_03_front_end_react/00_test_client/package.json)

추가된 패키지:
```json
{
  "@ohif/core": "^3.8.0",
  "@ohif/ui": "^3.8.0",
  "@ohif/viewer": "^3.8.0",
  "@ohif/extension-cornerstone": "^3.8.0",
  "@ohif/extension-default": "^3.8.0",
  "@ohif/extension-cornerstone-dicom-sr": "^3.8.0",
  "cornerstone-core": "^2.6.1",
  "cornerstone-tools": "^6.0.9",
  "cornerstone-wado-image-loader": "^4.13.3",
  "dicom-parser": "^1.8.21"
}
```

#### 3. OHIF 설정 파일 생성
**파일**: [src/config/ohif.config.js](../NeuroNova_03_front_end_react/00_test_client/src/config/ohif.config.js)
- Django Proxy를 통한 Orthanc DICOM-Web 접근 설정
- JWT 토큰 자동 추가 (requestHeaders)
- Data source 설정 (wadoUriRoot, qidoRoot, wadoRoot)

#### 4. DICOM Viewer 페이지 구현
**파일**:
- [src/pages/ViewerPage.js](../NeuroNova_03_front_end_react/00_test_client/src/pages/ViewerPage.js)
- [src/pages/ViewerPage.css](../NeuroNova_03_front_end_react/00_test_client/src/pages/ViewerPage.css)

기능:
- Study Instance UID 기반 DICOM 이미지 로드
- Study 메타데이터 표시 (환자명, 검사일, Modality 등)
- Django Proxy를 통한 안전한 접근
- 로딩/에러 상태 처리
- "목록으로 돌아가기" 버튼

#### 5. 라우팅 추가
**파일**: [src/App.js](../NeuroNova_03_front_end_react/00_test_client/src/App.js)
- `/viewer/:studyInstanceUID` 라우트 추가
- JWT 인증 통합 (isAuthenticated 체크)
- ViewerPage 컴포넌트 import

#### 6. RIS 테스트 페이지 개선
**파일**: [src/pages/UC05RISTest.js](../NeuroNova_03_front_end_react/00_test_client/src/pages/UC05RISTest.js)

추가 기능:
- Orthanc 환자 목록 자동 로드 (`/api/ris/test-orthanc-patients/`)
- 환자 정보 테이블 표시 (환자명, 생년월일, 성별, Study 수)
- "View Study" 버튼으로 DICOM Viewer 연결
- 로딩/에러 처리 및 재시도 버튼

#### 7. 스타일링
**파일**: [src/index.css](../NeuroNova_03_front_end_react/00_test_client/src/index.css)

추가 스타일:
- `.orthanc-patients-table` - 환자 목록 테이블
- `.data-table` - 데이터 테이블 공통 스타일
- `.viewer-page` - DICOM Viewer 전체 화면 레이아웃
- `.error-box`, `.info-box` - 메시지 박스
- `.btn-sm`, `.btn-secondary` - 버튼 스타일

#### 8. 환경 변수 설정
**파일**: [.env.example](../NeuroNova_03_front_end_react/00_test_client/.env.example)

추가 설정:
```bash
PORT=3000
REACT_APP_DICOM_WEB_ROOT=http://localhost:8000/api/ris/dicom-web
# WSL: http://172.29.64.1:8000/api/ris/dicom-web
```

#### 9. 통합 가이드 문서 작성
**파일**: [README_OHIF_INTEGRATION.md](../NeuroNova_03_front_end_react/00_test_client/README_OHIF_INTEGRATION.md)

내용:
- 아키텍처 설명 (React → Django → Orthanc)
- 설치 및 실행 방법 (개발/프로덕션)
- 주요 기능 설명
- API 엔드포인트 목록
- 트러블슈팅 가이드
- 추가 개발 예정 사항

### 📊 작업 통계
- **수정된 파일**: 6개 (App.js, UC05RISTest.js, package.json, .env.example, index.css, 서비스구조문서)
- **생성된 파일**: 4개 (ViewerPage.js, ViewerPage.css, ohif.config.js, README_OHIF_INTEGRATION.md)
- **추가된 패키지**: 10개 (OHIF 및 Cornerstone 관련)
- **새 라우트**: `/viewer/:studyInstanceUID`

### 🔑 핵심 개선 사항

1. **단일 빌드 배포**: React와 OHIF Viewer를 하나의 빌드로 통합
2. **보안 강화**: Django Proxy를 통한 JWT 인증 기반 DICOM 접근
3. **사용자 경험**: 환자 목록 → View Images → DICOM Viewer 원활한 흐름
4. **개발 효율**: npm 패키지 관리로 의존성 일원화

### 🚀 다음 단계 (서버 실행 필요)

#### 원본 PC 복귀 후 실행:
```bash
# 1. 패키지 설치
cd NeuroNova_03_front_end_react/00_test_client
npm install

# 2. 백엔드 서비스 시작
cd NeuroNova_02_back_end/07_redis && docker-compose up -d
cd ../05_orthanc_pacs && docker-compose up -d
cd ../02_django_server && python manage.py runserver

# 3. React 클라이언트 시작
cd NeuroNova_03_front_end_react/00_test_client
npm start
```

#### 테스트 항목:
- [ ] Orthanc 환자 목록 조회 (`/uc05`)
- [ ] "View Study" 버튼으로 Viewer 이동
- [ ] Study 메타데이터 표시 확인
- [ ] JWT 토큰 자동 갱신 동작 확인
- [ ] OHIF Viewer 전체 기능 통합 (추가 개발)

### 📖 관련 문서
- [07_서비스_구조_요약.md](07_서비스_구조_요약.md) - v3.0 아키텍처
- [README_OHIF_INTEGRATION.md](../NeuroNova_03_front_end_react/00_test_client/README_OHIF_INTEGRATION.md) - 통합 가이드
- [12_GCP_배포_가이드.md](12_GCP_배포_가이드.md) - 프로덕션 배포 (업데이트 필요)

---

## Week 7-5 (2025-12-31) - Git 서브모듈 관리 문서화

### 🎯 목표
Git 서브모듈 개념 및 관리 방법을 문서화하여 개발 과정 이해도 향상

### ✅ 완료 작업

#### 1. Git 서브모듈 관리 가이드 작성
**파일**: [GIT_서브모듈_관리_가이드.md](GIT_서브모듈_관리_가이드.md)

**내용**:
- Git 서브모듈 개념 설명: "Git 저장소 안에 또 다른 Git 저장소를 폴더처럼 넣어서 관리하는 기능"
- NeuroNova 프로젝트 구조 (메인 저장소 + 프론트엔드 서브모듈)
- 서브모듈 작업 방법 (초기화, 작업, 업데이트)
- VSCode에서 서브모듈 관리
- 자주 사용하는 명령어 모음
- 주의사항 및 트러블슈팅

**핵심 개념**:
```
메인 저장소 (NeuroNova_v1)
├── .git/                    ← 메인 저장소의 Git 데이터
├── .gitmodules              ← 서브모듈 설정 파일
└── NeuroNova_03_front_end_react/  ← 서브모듈 (독립적인 Git 저장소)
    └── .git/                ← 서브모듈의 Git 데이터
```

#### 2. 핵심 문서 업데이트

**파일**: [REF_CLAUDE_ONBOARDING_QUICK.md](REF_CLAUDE_ONBOARDING_QUICK.md)
- 프로젝트 구조 섹션에 Git 서브모듈 설명 추가
- `.gitmodules` 파일 설명 추가
- 서브모듈 URL 명시
- GIT_서브모듈_관리_가이드.md 링크 추가

**파일**: [작업_계획_요약.md](../작업_계획_요약.md)
- Git 서브모듈 관리 섹션 추가 예정

**파일**: [LOG_작업이력.md](LOG_작업이력.md)
- Week 7-5 작업 내역 추가 (이 섹션)

### 📊 작업 통계
- **생성된 파일**: 1개 (GIT_서브모듈_관리_가이드.md, 약 500 lines)
- **수정된 파일**: 3개 (REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md, 작업_계획_요약.md)
- **추가된 문서량**: 약 500 lines

### 🔑 핵심 개선 사항

1. **Git 서브모듈 이해도 향상**: 개발팀이 서브모듈 개념을 명확히 이해
2. **독립적인 버전 관리**: 프론트엔드와 백엔드를 각각 별도 저장소로 관리
3. **팀 협업 효율화**: 프론트엔드 팀과 백엔드 팀이 독립적으로 작업 가능
4. **문서화 완성도**: VSCode에서 서브모듈 작업 시 발생하는 문제 해결 방법 제공

### 📖 관련 문서
- [GIT_서브모듈_관리_가이드.md](GIT_서브모듈_관리_가이드.md) - 상세 가이드
- [REF_CLAUDE_ONBOARDING_QUICK.md](REF_CLAUDE_ONBOARDING_QUICK.md) - 프로젝트 구조 설명
- [작업_계획_요약.md](../작업_계획_요약.md) - 전체 작업 계획

### 🚀 다음 단계
Git 서브모듈 관리 문서화가 완료되었습니다. 개발자는 이제:
- 서브모듈 개념을 명확히 이해
- 프론트엔드 코드를 독립적으로 커밋/푸시 가능
- VSCode에서 발생하는 서브모듈 문제 해결 가능

---

## 2026-01-02 긴급 버그 수정 및 디버깅

### 13. UC02 환자 목록 조회 파라미터 무시 문제 해결
**현상:** 환자 목록 조회 API (`/api/emr/patients/`) 호출 시 `limit`와 `offset` 파라미터가 적용되지 않고 항상 기본값으로만 반환됨.
**원인:** Django REST Framework의 `DEFAULT_PAGINATION_CLASS`가 `PageNumberPagination`으로 설정되어 있어, `limit`/`offset` 스타일의 파라미터를 처리하지 못함.
**해결:** `settings.py`의 `DEFAULT_PAGINATION_CLASS`를 `rest_framework.pagination.LimitOffsetPagination`으로 변경하여 해결함.

### 14. UC02 환자 생성 500 에러 (TransactionManagementError) 해결 및 검증
**현상:** 환자 생성 시 500 Internal Server Error 발생. 로그 상 `TransactionManagementError` 확인.
**원인:** `PatientService.create_patient` 메서드 내의 `AuditService.log_action` 호출이 `@transaction.atomic` 블록 내부에서 발생. Audit 저장 중 예외가 발생하면(예: User가 None일 때의 처리 등) atomic 트랜잭션이 오염되어 전체 롤백 및 에러 발생.
**해결:** 
1. `AuditService` 호출을 atomic 블록 외부로 이동.
2. `try-except` 구문으로 감싸서 로깅 실패가 비즈니스 로직(환자 생성)에 영향을 주지 않도록 격리.
**검증:** 수정 후 `curl` 테스트 결과 201 Created 응답 확인 (성공 - persistence_status 포함).

### 15. UC03 주문 상세 한자 깨짐(Hanja) 이슈 조사
**현상:** 주문(Order) 상세 화면에서 노트(Notes) 등의 필드에 한자가 포함되거나 깨진 문자가 보인다는 보고.
**조사:** 
1. DB 직접 조회(`Order`, `OrderItem`) 결과 레코드가 0건(Empty)임을 확인.
2. 따라서 실제 DB 데이터 문제가 아니라, 프론트엔드 테스트 코드(`UC03OrderTest.js`)나 Mock API 응답에 하드코딩된 더미 데이터일 가능성이 높음.
**조치:** 프론트엔드 Mock 데이터 확인 필요.

### 16. UC01 회원가입 네트워크 에러 조사
**현상:** 회원가입 시도 시 Network Error 발생.
**조사:** WSL 환경에서 `curl` 테스트 시 Connection Refused 발생. 백엔드 로그에는 관련 에러 없음.
**가능성:** CORS 설정 또는 Docker 내부망 통신 문제로 추정.


---

  - [x] **React Client Port Fix** (2025-12-31):
    - [x] **Diagnosis**: React client was trying to connect to Django port 8000, which is not exposed.
    - [x] **Fix**: Updated REACT_APP_API_URL to http://localhost/api (Nginx proxy) in .env.local.
    - [x] **Verification**: Confirmed API endpoint accessibility via curl (405 Method Not Allowed on GET login implies server reachable).


  - [x] **React Client Stability Fix** (2025-12-31):
    - [x] **Fix**: Initialized App.js isAuthenticated from localStorage to prevent redirect loop.
    - [x] **Fix**: Added BROWSER=none to .env.local to stop multi-tab opening.
    - [x] **Verification**: Browser test stable. API Test Record: 10/13 Success (Warning: LIS/Alert 404s).

