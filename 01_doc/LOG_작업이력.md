# 작업 이력 (Work Log)

**최종 수정일**: 2025-12-29
**현재 상태**: Week 7 Day 2 완료 - PACS 인프라 구축 및 OHIF Viewer 통합 (DICOM 시각화)

> [!NOTE]
> 시스템 아키텍처, 사용자 역할(RBAC), 상세 모듈 설계 등 기술 참조 정보는 **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)**를 참조하십시오. 이 문서는 일자별 작업 진행 상황과 변경 이력만을 기록합니다.

---

## 📈 주차별 요약

- **Week 1**: 프로젝트 초기 설정, UC1(인증/권한), UC9(감사 로그 기본) 완료
- **Week 2**: UC2(EMR) OpenEMR 연동, UC7(알림 레이아웃), React 초기 설정 완료
- **Week 3**: UC5(RIS) Orthanc 연동, UC6(AI) Queue 인프라, React 대시보드 완성
- **Week 4**: 데이터 정합성(Locking), 멱등성(Idempotency), AI R&R 정의, OCS 고도화 완료
- **Week 5**: OCS/LIS 워크플로우 심화, 실시간 알림 강화(UC07), 감사 로그 뷰어(UC09) 완료
- **Week 6**: AI 모듈 통합(UC06) 비동기 워크플로우 및 진단 마스터 데이터 확장 완료
- **Week 7**: Phase 1 문서(25~27번) 실제 코드 구현 및 PACS 인프라 구축 완료

---

## 📅 상세 작업 로그

### Week 7 (2025-12-29)
- **2025-12-29 Day 2**:
  - [x] **PACS 인프라 구축 (UC05 - RIS 시각화 완성)**:
    - **NIfTI → DICOM 변환**: 12개 Brain MRI 파일 변환 (sub-0004, sub-0005 각 6개 시퀀스)
      - 시퀀스: T1w, T2w, FLAIR, SWI, ce-T1w, DWI
      - 총 1,860개 DICOM 인스턴스 생성 (각 155 슬라이스)
      - `scripts/convert_nifti_to_dicom.py` 구현 및 100% 성공률 업로드
    - **Orthanc PACS 서버**: Docker 기반 구축 및 DICOM-Web 활성화
      - 포트: 8042 (HTTP/REST API), 4242 (DICOM 프로토콜)
      - DICOM-Web 표준 지원: QIDO-RS, WADO-RS, STOW-RS
      - `orthanc.json` 설정: 인증 비활성화, 타임아웃 60초, 인스턴스 덮어쓰기 허용
      - 데이터 검증: 2명 환자, 12개 Study, ~1,860개 Instance 확인
    - **OHIF Viewer 통합**: 웹 기반 DICOM 뷰어 배포
      - Docker 컨테이너 배포 (`ohif/viewer:latest`)
      - `ohif-config.js`: Orthanc PACS 데이터 소스 설정
      - Nginx 역방향 프록시 (포트 3000) 통한 서비스 제공
    - **Nginx 프록시 구성**: CORS, MIME 타입, 라우팅 통합 관리
      - CORS 헤더 추가 (Access-Control-Allow-Origin: *)
      - JavaScript 모듈(.mjs) MIME 타입 설정 (`application/javascript`)
      - polyfill.io 보안 차단 (CDN 보안 이슈 대응)
      - 라우팅: `/` → OHIF, `/pacs/*` → Orthanc
    - **Django RIS API 통합**: Orthanc 클라이언트 구현
      - `ris/clients/orthanc_client.py`: 10개 메서드 구현
      - Health check, Studies 조회, Study 상세 정보, DICOM 메타데이터 추출
      - Study 검색 (PatientName, PatientID, StudyDate), DICOM 인스턴스 다운로드
    - **시스템 아키텍처**:
      ```
      브라우저 (localhost:8000)
          ↓
      [Nginx 역방향 프록시]
          ↓
      [Django Server:8000]
          ↓ (Proxy/Client)
          ├─→ [Orthanc PACS:8042] ← [Flask AI Server]
          └─→ [OHIF Viewer]
      ```
  - [x] **문서화**:
    - `프로젝트_구성_및_문제_보고서.md` 생성: 9개 섹션 포괄 문서
    - 시스템 구성, 데이터 현황, 접속 방법, 문제 및 해결책, 검증 체크리스트 포함
    - `REF_CLAUDE_CONTEXT.md` UC05 섹션 업데이트 (PACS 인프라 상세 정보)
  - [x] **알려진 이슈**:
    - OHIF Viewer "No matching results" 표시 (브라우저에서 DICOM-Web API 미호출)
    - 원인 추정: 브라우저 캐시, OHIF 설정 인식 실패, JavaScript 초기화 오류
    - 인프라 검증 완료: Orthanc API 정상 응답, CORS 헤더 존재, MIME 타입 수정됨
    - 상세 트러블슈팅: `프로젝트_구성_및_문제_보고서.md` 참조

- **2025-12-29 Day 1**:
  - [x] **에러 핸들링 구현 (Phase 1)**:
    - `utils/exceptions.py` 생성: 7개 커스텀 Exception 클래스 구현 (CDSSException 기본 + 6개 특화)
    - `utils/exception_handlers.py` 생성: DRF 전역 예외 처리 핸들러 구현
    - `settings.py`에 커스텀 Exception Handler 등록
    - `acct/services.py` AuthService.login()에 AuthenticationFailedException 적용 (샘플)
    - 표준 에러 응답 형식 (`error.code`, `error.message`, `error.timestamp`) 적용
  - [x] **Swagger 자동문서화 구현 (Phase 1)**:
    - `drf-spectacular` 패키지 설치 (v0.29.0)
    - `settings.py`에 SPECTACULAR_SETTINGS 추가 (제목, 설명, 태그, 인증 스키마)
    - `urls.py`에 Swagger UI, ReDoc, Schema 엔드포인트 추가
    - `acct/views.py` 주요 API 3개에 `@extend_schema` 적용 (login, logout, me)
    - Swagger 접속 URL: `http://localhost:8000/api/docs/`
  - [x] **데이터 검증 강화 (Phase 1)**:
    - `emr/serializers.py` PatientCreateSerializer에 5개 필드 검증 메서드 추가
    - `validate_phone()`: 한국 전화번호 형식 검증
    - `validate_email()`: 이메일 형식 검증
    - `validate_gender()`: 성별 허용 값 검증 (M, F, O)
    - `validate_blood_type()`: 혈액형 허용 값 검증 (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - `validate()`: 객체 수준 검증 (필수 필드, 생년월일 미래 날짜 체크)
  - [x] **통합 테스트**:
    - `python manage.py check` 통과 (0 issues)
    - 서버 정상 실행 확인
    - `requirements.txt` 업데이트 (drf-spectacular 포함)

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
