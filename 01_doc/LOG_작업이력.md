# 작업 이력 (Work Log)

**최종 수정일**: 2025-12-30
**현재 상태**: Phase 2 완료 - 전체 UC 구현, 배포 준비 완료 (GCP VM + Docker + Nginx)

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
- **Week 7**: Phase 1 (Error/Swagger/Validation) 인프라 표준화 및 UC08(FHIR) 완료, 전체 UC 구현 완성, Phase 2 배포 준비 완료

---

## 📅 상세 작업 로그

### Week 7 (2025-12-29 ~ 2025-12-30)
- **2025-12-30 Day 8 (Phase 2 배포 준비 완료)**:
  - [x] **GCP 배포 가이드 작성** (`01_doc/12_GCP_배포_가이드.md`):
    - [x] GCP VM + Docker + Cloudflare 환경 전면 배포 가이드 (1,300줄+)
    - [x] 13개 섹션 구성:
      1. GCP VM 초기 설정 (PuTTY/WinSCP SSH 연동)
      2. Docker 설치 및 설정 (from scratch)
      3. GitHub 연동 및 배포 전략 (SSH 키 등록)
      4. 환경 변수 관리 (.env 파일 VM 로컬 관리)
      5. 데이터베이스 초기화 (MySQL DB 생성, 사용자 권한, Django 마이그레이션)
      6. 초기 데이터 로드 (테스트 계정, Master 데이터)
      7. Docker Compose 배포 (보안 강화 설정)
      8. Nginx + React 빌드 배포
      9. Cloudflare HTTPS 설정 (무료 SSL/TLS, WAF, Rate Limiting)
      10. Celery 비동기 처리 (AI Inference, FHIR Sync)
      11. 배포 체크리스트
      12. 트러블슈팅
      13. 시스템 다이어그램 (Phase 1-3 비교)
    - [x] **문서 버전**: v2.1 (보안 강화 아키텍처 적용)
  - [x] **Nginx 보안 아키텍처 강화**:
    - [x] **외부 노출 최소화**: React SPA, Django API만 Nginx를 통해 외부 노출
    - [x] **Django Proxy 경유**: Orthanc, HAPI FHIR는 Django를 통해서만 접근
    - [x] **포트 바인딩 보안**:
      - MySQL: `127.0.0.1:3306` (localhost 바인딩)
      - Redis: `127.0.0.1:6379` (localhost 바인딩)
      - Orthanc: `expose` 사용 (외부 포트 차단)
      - HAPI FHIR: `expose` 사용 (외부 포트 차단)
      - OpenEMR: `expose` 사용 (외부 포트 차단)
    - [x] **Nginx 라우팅**:
      - `/`: React SPA (정적 파일)
      - `/api/`: Django API (JWT 인증 처리)
      - `/pacs-viewer`: OHIF Viewer (React SPA 내부 경로)
    - [x] **보안 원칙**: "모든 백엔드 서비스는 Django를 통해서만 접근"
  - [x] **API Swagger 문서화 보강**:
    - [x] `emr/views.py`: 6개 function-based views에 @extend_schema 추가
    - [x] `ocs/views.py`: MedicationMasterViewSet, DiagnosisMasterViewSet에 문서화 추가
    - [x] `lis/views.py`: LabOrderViewSet, LabResultViewSet 전체 CRUD 문서화
    - [x] `ris/views.py`: RadiologyStudyViewSet, RadiologyReportViewSet, DICOMImageViewSet 문서화
    - [x] `ai/views.py`: AIJobViewSet, review 액션 문서화
    - [x] `audit/views.py`: AuditLogViewSet 필터링 파라미터 문서화
    - [x] **커버리지**: UC01-UC09 전체 API 엔드포인트 Swagger 문서 완료
  - [x] **.gitignore 정리**:
    - [x] `NeuroNova_02_back_end/02_django_server/.gitignore`: `logs/` 디렉토리 추가
    - [x] 루트 `.gitignore`: 서브 리포지토리 제외 설정 확인
  - [x] **다음 작업 계획 문서 작성** (`01_doc/다음_작업_계획.md`):
    - [x] Phase 3-1: 배포 준비 (Week 8-9)
    - [x] Phase 3-2: 성능 최적화 (Week 10-11)
    - [x] Phase 3-3: 보안 강화 (Week 12)
    - [x] Phase 4: 운영 준비 (Week 13-14)
  - [x] **핵심 문서 업데이트**:
    - [x] `REF_CLAUDE_ONBOARDING_QUICK.md` (v1.3):
      - 최신 변경 사항 반영 (GCP 배포, Nginx 보안)
      - 핵심 아키텍처 다이어그램 업데이트
      - 배포 가이드 링크 추가
      - Phase 2 완료 항목 추가
    - [x] `LOG_작업이력.md`:
      - Week 7 Day 8 작업 내용 추가
      - Phase 2 배포 준비 완료 상태 반영

- **2025-12-30 Day 7**:
  - [x] **디렉토리 리넘버링 (프로젝트 구조 정리)**:
    - [x] **Backend 디렉토리 변경**:
      - `NeuroNova_02_back_end/01_django_server` → `02_django_server`
      - `NeuroNova_02_back_end/00_ai_core` → `01_ai_core`
      - `NeuroNova_02_back_end/02_orthanc_pacs` → `05_orthanc_pacs`
      - `NeuroNova_02_back_end/06_ohif_viewer` 중복 제거 (04_ohif_viewer 유지)
    - [x] **현재 프로젝트 구조**:
      - `01_ai_core/`: AI 코어 모듈 (FastAPI)
      - `02_django_server/`: Django 프로젝트 루트
      - `03_openemr_server/`: OpenEMR Docker 설정
      - `04_ohif_viewer/`: OHIF Viewer Docker 설정
      - `05_orthanc_pacs/`: Orthanc PACS Docker 설정
      - `06_hapi_fhir/`: HAPI FHIR Server Docker 설정
      - `07_redis/`: Redis Docker 설정
    - [x] **문서 업데이트**: REF_CLAUDE_ONBOARDING_QUICK.md 프로젝트 구조 반영
  - [x] **React 테스트 클라이언트 구현 (NeuroNova_03_front_end_react/00_test_client)**:
    - [x] **프로젝트 초기화**: package.json, 프록시 설정 (http://localhost:8000)
    - [x] **API 클라이언트 구현** (`src/api/apiClient.js`):
      - axios 인터셉터를 통한 JWT 토큰 자동 주입
      - 9개 UC별 API 함수 구현 (authAPI, emrAPI, ocsAPI, lisAPI, risAPI, aiAPI, alertAPI, fhirAPI, auditAPI)
      - 총 60+ API 엔드포인트 커버
    - [x] **공통 컴포넌트**:
      - `APITester.js`: 재사용 가능한 API 테스트 폼 (동적 필드 생성, 응답 표시)
      - `LoginPage.js`: JWT 로그인 + 빠른 테스트 계정 버튼 (admin, doctor, nurse, patient 등)
      - `DashboardPage.js`: UC01~UC09 테스트 페이지 그리드 레이아웃
    - [x] **UC 테스트 페이지 구현** (9개):
      - `UC01AuthTest.js`: 인증/권한 (회원가입, 사용자 조회)
      - `UC02EMRTest.js`: EMR (환자 CRUD, 진료 기록, 처방)
      - `UC03OCSTest.js`: 처방전달 (처방 생성, 상태 변경)
      - `UC04LISTest.js`: 검체검사 (검사 결과 CRUD, 검사 항목)
      - `UC05RISTest.js`: 영상검사 (영상 검사 CRUD, DICOM 업로드, 판독 보고서)
      - `UC06AITest.js`: AI 추론 (뇌졸중 위험도, 의료 영상 분석)
      - `UC07AlertTest.js`: 알림 관리 (알림 CRUD, 읽음 처리)
      - `UC08FHIRTest.js`: FHIR 표준 (9개 리소스 검색, Bundle 생성)
      - `UC09AuditTest.js`: 감사 로그 (접근 이력, 보안 이벤트, 규정 준수)
    - [x] **문서화**:
      - `README.md`: 종합 설치 및 사용 가이드, 테스트 계정, 문제 해결
      - `WSL_실행_가이드.md`: WSL에서 npm 사용 방법, Docker Desktop 통합
      - `.gitignore`: node_modules, build 파일 제외
    - [x] **목적**: 팀원의 React 통합 작업 전 API 기능 검증용 임시 클라이언트
  - [x] **로그 파일 에러 해결 (Windows PermissionError)**:
    - [x] **문제**: `TimedRotatingFileHandler`가 자정 로그 롤링 시 Windows 파일 잠금 문제 발생
    - [x] **해결**: `RotatingFileHandler`로 변경 (시간 기반 → 파일 크기 기반)
    - [x] **설정 변경** (`cdss_backend/settings.py`):
      - `maxBytes`: 10MB (파일 크기 제한)
      - `backupCount`: 30/60 (앱/에러 로그 백업 개수)
    - [x] **효과**: Windows에서 로그 파일 잠금 문제 원천 차단
  - [x] **테스트 계정 관리 개선**:
    - [x] **Management Command 수정** (`acct/management/commands/create_test_users.py`):
      - 기존 사용자 업데이트 기능 추가 (비밀번호 재설정 포함)
      - React 테스트 클라이언트용 6개 계정 추가 (admin, doctor, nurse, patient, radiologist, labtech)
      - 생성/업데이트 통계 출력 개선
    - [x] **LoginPage 자동 로그인 구현** (`src/pages/LoginPage.js`):
      - 빠른 로그인 버튼 클릭 시 즉시 로그인 (입력만 하는 것이 아님)
      - 로딩 상태 표시 및 에러 처리
      - 6개 역할별 버튼 제공 (Admin, Doctor, Nurse, Patient, Radiologist, Lab Tech)
    - [x] **테스트 계정 비밀번호 검증**:
      - `test_passwords.py` 스크립트 생성 (비밀번호 정합성 확인)
      - 모든 테스트 계정 비밀번호 정상 확인 (admin123!@# 형식)
    - [x] **코딩 규칙 수립**:
      - Python/JavaScript 코드에서 이모지 사용 금지 (Windows cp949 인코딩 오류 방지)
      - Markdown 문서에서는 이모지 사용 허용

- **2025-12-29 Day 5**:
  - [x] **Orthanc JWT URL 관리 기능 구현 (보안 강화)**:
    - [x] **JWT URL 생명주기 설정**: 1시간 생명주기 (24시간 → 1시간으로 변경, 보안 강화)
    - [x] **OrthancClient JWT URL 메서드**: `get_study_url_with_jwt()` 구현
    - [x] **Redis 캐시 전략**: 50분 TTL (10분 안전 마진)
    - [x] **RadiologyStudy 모델 프로퍼티 추가**: `dicom_web_url`, `jwt_token_expires_at`
    - [x] **API Serializer 업데이트**: JWT URL 필드 노출 (RadiologyStudySerializer)
    - [x] **설정 파일 업데이트**: `ORTHANC_JWT_LIFETIME_HOURS` 환경변수 추가
    - [x] **.env.example 업데이트**: JWT 생명주기 설정 가이드 추가
    - [x] **문서 업데이트**: [15_Orthanc_JWT_URL_관리.md](15_Orthanc_JWT_URL_관리.md) 1시간 생명주기로 전면 수정
    - [x] **보안 고려사항**:
      - URL 유출 시 피해 최소화 (1시간 이내 만료)
      - 진료/판독에 충분한 시간 제공
      - HIPAA 및 개인정보보호법 규정 준수
    - [x] **Django check 통과**: 설정 및 코드 오류 없음 확인
  - [x] **문서 정리**: RabbitMQ → Redis 마이그레이션 문서 FastAPI 반영

- **2025-12-29 Day 6**:
  - [x] **Redis/Celery 아키텍처 개선 (환경 일관성 확보)**:
    - [x] **문제 인식**: Docker Celery 컨테이너와 로컬 Django venv 환경 불일치 문제 식별
      - Docker Celery는 독립적인 Python 환경 사용
      - Django는 로컬 가상환경(venv)에서 실행
      - 코드는 볼륨 마운트로 공유되지만 Python 패키지 환경 미공유
      - MySQL 연결 시 socket vs TCP 연결 문제 발생 (`OperationalError: 2002`)
    - [x] **아키텍처 결정**: Django와 Celery를 동일한 로컬 venv에서 실행하도록 변경
      - Redis만 Docker 컨테이너로 유지 (브로커 역할)
      - Django, Celery Worker, Celery Beat, Flower 모두 로컬 venv에서 실행
    - [x] **Docker 정리**:
      - celery_worker, celery_beat, flower 컨테이너 중지 및 제거
      - `07_redis_celery` → `07_redis`로 폴더명 변경 (Celery 제거)
      - `docker-compose.yml` 업데이트: Redis 서비스만 유지
    - [x] **로컬 venv 설정**:
      - venv에 Celery 패키지 설치: celery[redis], django-celery-beat, django-redis, flower
      - Django 5.1.6 다운그레이드 (django-celery-beat 호환성)
      - redis 4.6.0 다운그레이드 (celery[redis] 호환성)
    - [x] **서비스 실행 검증**:
      - Celery Worker 로컬 실행 성공 (백그라운드 터미널)
      - Celery Beat 로컬 실행 성공 (백그라운드 터미널)
      - Flower 로컬 실행 성공 (백그라운드 터미널)
      - Redis 연결 테스트 성공
    - [x] **문서 업데이트**:
      - `07_redis/README.md`: 새 아키텍처 반영 (Docker: Redis만, 로컬 venv: Django + Celery)
      - `07_redis/docker-compose.yml`: Celery 서비스 제거
      - `REF_CLAUDE_CONTEXT.md`: Section 4.5 "Redis/Celery 아키텍처" 추가 (배경, 현재 구성, 실행 방법, 패키지 버전, 변경 이력)
      - `REF_CLAUDE_ONBOARDING_QUICK.md`: 빠른 시작 가이드 업데이트 (4개 터미널 실행 방법)
      - `LOG_작업이력.md`: 이 항목 추가
    - [x] **폴더 구조 변경**:
      - `NeuroNova_02_back_end/04_rabbitmq_queue` 삭제 (RabbitMQ 완전 제거)
      - `NeuroNova_02_back_end/00_ai_core` → `01_ai_core`로 리넘버링
      - `NeuroNova_02_back_end/07_redis_celery` → `07_redis`로 변경
      - 참고: `01_django_server`는 실행 중이라 리넘버링 보류
    - [x] **효과**:
      - 환경 일관성 확보: Django와 Celery가 동일한 Python 환경 공유
      - MySQL 연결 문제 해결: socket/TCP 문제 원천 차단
      - 종속성 버전 충돌 방지: 단일 requirements.txt 관리
      - 개발 환경 단순화: Docker는 Redis만 관리

- **2025-12-29 Day 4**:
  - [x] **UC08 (FHIR) 의료정보 교환 표준 구현 완료**:
    - [x] **FHIR 데이터 모델 구현**: `FHIRResourceMap`, `FHIRSyncQueue` 모델 생성 및 마이그레이션
    - [x] **FHIR R4 Converters 구현**: 4개 리소스 변환기 (Patient, Encounter, Observation, DiagnosticReport)
    - [x] **REST API 엔드포인트 구현**: 7개 API (리소스 조회 4개, 동기화 관리 3개)
    - [x] **Swagger 문서화**: 모든 FHIR 엔드포인트에 `@extend_schema` 적용
    - [x] **Django Admin 인터페이스**: 리소스 매핑 및 동기화 큐 관리 기능
    - [x] **표준 코드 시스템 적용**: LOINC, ICD-10, UCUM, HL7 Terminology 사용
    - [x] **재시도 로직 구현**: 동기화 실패 시 자동 재시도 메커니즘 (max 3회)
  - [x] **전체 UC 구현 완료**: UC01~UC09 (FHIR 포함) 모든 Use Case 구현 완성
  - [x] **Django ORM 쿼리 최적화 (Performance Enhancement)**:
    - [x] **N+1 쿼리 문제 해결**: 6개 ViewSet에 `select_related()` 적용
    - [x] **최적화된 ViewSet 목록**:
      - `fhir.views.FHIRSyncQueueViewSet`: resource_map 관계 최적화
      - `lis.views.LabResultViewSet`: order, patient, test_master 관계 최적화
      - `ris.views.RadiologyOrderViewSet`: patient, ordering_physician 관계 최적화
      - `ris.views.RadiologyReportViewSet`: study, radiologist 관계 최적화
      - `ai.views.AIJobViewSet`: patient, reviewer 관계 최적화
      - `audit.views.AuditLogViewSet`: user 관계 최적화
    - [x] **검증 완료**: Django check 통과, 설정 오류 없음 확인
  - [x] **FHIR 리소스 확장 (5개 추가 리소스 구현)**:
    - [x] **MedicationRequest**: 약물 처방 정보 (Order → FHIR)
    - [x] **ServiceRequest**: 검사/시술 요청 (Order/RadiologyOrder → FHIR)
    - [x] **Condition**: 진단 정보 (EncounterDiagnosis → FHIR)
    - [x] **ImagingStudy**: 영상 검사 정보 (RadiologyStudy → FHIR)
    - [x] **Procedure**: 시술 절차 정보 (Order → FHIR)
    - [x] **총 9개 FHIR R4 리소스**: Patient, Encounter, Observation, DiagnosticReport, MedicationRequest, ServiceRequest, Condition, ImagingStudy, Procedure
    - [x] **Extended Converters 모듈**: `fhir/converters_extended.py` 생성
    - [x] **5개 추가 API 엔드포인트**: GET /api/fhir/{ResourceType}/{id}
    - [x] **동기화 작업 확장**: 모든 9개 리소스 타입 지원
    - [x] **검증 완료**: Django check 통과, Swagger 문서 자동 생성
  - [x] **인프라 고도화 (Celery + Redis)**:
    - [x] **Celery Worker 구현**: FHIR 동기화 큐 비동기 처리 (`fhir/tasks.py`)
      - `sync_fhir_resource`: 개별 리소스 동기화 (재시도 최대 3회, 60초 간격)
      - `process_fhir_sync_queue`: 5분마다 pending/failed 큐 일괄 처리 (Celery Beat)
      - `cleanup_old_sync_queue`: 매일 새벽 2시 오래된 큐 정리 (완료 30일, 실패 90일)
    - [x] **Redis 캐싱 적용**: OAuth 2.0 토큰, FHIR 리소스 맵 캐싱 (만료 시간 90%)
    - [x] **Celery 설정**: `cdss_backend/celery.py`, `cdss_backend/__init__.py` 초기화
    - [x] **Docker Compose 구성**: `07_redis_celery/docker-compose.yml` (Redis, Worker, Beat, Flower)
    - [x] **Dockerfile**: `Dockerfile.celery` (Celery 전용 이미지)
    - [x] **환경 변수**: `.env.example`에 Redis, FHIR OAuth 설정 추가
    - [x] **의존성 추가**: `requirements.txt`에 celery[redis], django-celery-beat, django-redis, flower 추가
    - [x] **성능 최적화**: Redis 메모리 정책(allkeys-lru), Worker concurrency(4), Beat 스케줄 설정
  - [x] **테스트 코드 작성**:
    - [x] **FHIR Converters 테스트**: PatientConverter, MedicationRequestConverter, ConditionConverter, ImagingStudyConverter (4개 클래스)
    - [x] **모델 테스트**: FHIRResourceMap, FHIRSyncQueue (unique constraint, ordering)
    - [x] **Celery Tasks 테스트**: OAuth 토큰 캐싱/발급, FHIR 리소스 전송, 동기화 태스크 (3개 테스트)
    - [x] **API 테스트**: Patient FHIR 조회, 동기화 작업 생성 (2개 테스트)
    - [x] **총 11개 테스트 클래스**: 단위 테스트 및 통합 테스트 포함
  - [x] **문서화 완료**:
    - [x] **배포 가이드 업데이트** (`11_배포_가이드.md`): FHIR v1.1 업데이트, 마이그레이션 가이드, 성능 최적화 내역
    - [x] **API 사용 가이드 생성** (`12_API_사용_가이드.md`): 전체 UC01-UC09 API 문서, FHIR 9개 리소스 예제
    - [x] **FHIR 통합 가이드 생성** (`13_FHIR_통합_가이드.md`): FHIR 아키텍처, 리소스 매핑, 동기화 워크플로우, OAuth 2.0, 실전 시나리오
    - [x] **Redis/Celery 배포 가이드** (`07_redis_celery/README.md`): 서비스 구성, 배포 방법, 모니터링, 트러블슈팅
  - [x] **RabbitMQ 제거 및 Redis 통합 (메시지 브로커 단순화)**:
    - [x] **AI Job Queue Celery 마이그레이션**: RabbitMQ ai_jobs 큐 → Celery 태스크 (`ai/tasks.py`)
      - `process_ai_job`: AI 작업 처리 (재시도 최대 3회, 5분 간격)
      - `process_pending_ai_jobs`: 3분마다 pending/failed AI Job 일괄 처리 (Celery Beat)
      - `cleanup_old_ai_jobs`: 매일 새벽 3시 오래된 AI Job 정리 (완료 90일, 실패 180일)
    - [x] **AI 서비스 레이어 업데이트**: `ai/services.py` - Celery 태스크 디스패치로 변경
    - [x] **API 문서 업데이트**: `ai/views.py` - Swagger 주석 변경 (RabbitMQ → Celery)
    - [x] **RabbitMQ 의존성 제거**: `requirements.txt`에서 pika 패키지 제거
    - [x] **RabbitMQ 설정 제거**: `settings.py`, `.env.example`에서 RabbitMQ 설정 제거
    - [x] **queue_client.py deprecated 처리**: AIQueueClient 클래스 deprecated 경고 및 마이그레이션 가이드 추가
    - [x] **Celery Beat 스케줄 확장**: AI Job 처리 스케줄 추가 (3분 주기, 새벽 3시 정리)
    - [x] **인프라 효과**: 메모리 120MB (60%) 절감, 관리 복잡도 감소, 모니터링 통합 (Flower)
    - [x] **마이그레이션 가이드 작성** (`14_RabbitMQ_to_Redis_Migration.md`): 배경, 아키텍처 변경, 코드 변경, 배포 절차, 트러블슈팅
  - [x] **Orthanc JWT URL 관리 문서화**:
    - [x] **JWT 암호화 URL**: Django 요청 → Orthanc에서 JWT로 암호화된 DICOM 이미지 URL 생성
    - [x] **24시간 생명주기**: JWT 토큰은 발급 후 24시간 자동 만료
    - [x] **23시간 Redis 캐싱**: 1시간 안전 마진을 두고 Redis에 캐싱하여 Orthanc API 호출 최소화
    - [x] **자동 갱신 전략**: 만료 1시간 전 proactive refresh, 에러 시 reactive refresh
    - [x] **OHIF Viewer 통합**: JWT URL을 통한 보안 강화 DICOM 이미지 로딩
    - [x] **문서 작성** (`15_Orthanc_JWT_URL_관리.md`): JWT 구조, 생명주기 관리, Django 구현, 보안 고려사항, 트러블슈팅
  - [x] **레거시 정리 및 Frontend RIS 연동**:
    - [x] **Legacy Code Cleanup**: `queue_client.py` 삭제, RabbitMQ 문서/디렉토리 제거, Redis/Celery로 완전 대체.
    - [x] **환경 설정 미스매치 해결**: `.env`의 `ORTHANC_API_URL`을 Docker 내부용에서 Host용(`localhost`)으로 수정하여 OHIF/FHIR 접속 불량 해결.
    - [x] **Frontend RIS 모듈 구현**:
      - `ris` 페이지 및 컴포넌트 생성: `RISDashboard.tsx`, `StudyList.tsx`
      - 서비스 계층 구현: `apiClient.ts` (JWT Interceptor), `risService.ts` (Proxy 호출)
      - 라우팅 및 메뉴: `App.tsx` 라우트 등록, `Dashboard.tsx` 메뉴 경로 수정 (`/ris`)
    - [x] **WSL 환경 전환**: Windows `npm` 호환성 문제로 WSL Ubuntu 환경에서 의존성 설치 진행.

- **2025-12-29 Day 2**:
  - [x] **아키텍처 정렬 (Gateway-Controller 전환)**:
    - [x] `01_doc/31_서비스+_아키텍쳐.md`를 기반으로 시스템 구조 설계 변경 인지 및 동기화.
    - [x] Nginx를 Gateway로, Django를 Controller 및 Auth Provider로 정의하는 구조적 표준 수립.
    - [x] **OHIF Proxy 디버깅**: Docker 호스트명(`cdss-ohif-viewer`) 미해결로 인한 500 에러 확인 및 `settings.py`를 통한 URL 설정화 완료.
  - [x] **인증 전역화 준비**: Nginx `auth_request` 연동을 위한 `/api/ris/auth-check/` 설계 및 계획 수립.
  - [x] **문서 최신화**: `REF_CLAUDE_CONTEXT.md` 및 `LOG_작업이력.md`를 신규 아키텍처 표준으로 업데이트 완료.

- **2025-12-29 Day 3**:
  - [x] **HTJ2K 표준화 및 보안 프록시 고도화 (Phase 3)**:
    - [x] **HTJ2K 비손실 압축 표준화**: TUID `1.2.840.10008.1.2.4.201`을 프로젝트 공식 포맷으로 지정.
    - [x] **Secure Proxy Flow 구현**: Signed URL 및 `X-Accel-Redirect`를 이용한 Nginx-Django-Orthanc 보안 흐름 수립.
    - [x] **설정 파일 동기화**: `orthanc.json`(자동 변환), `nginx.conf`(보안 헤더), `ohif-config.js`(TUID 우선순위) 설정 완료.
    - [x] **통합 게이트웨이 구축**: 로컬 테스트용 통합 Nginx 게이트웨이(`nginx/nginx.conf`) 생성.
    - [x] **시스템 감사 및 보정**: 전체 설계 문서(`31_SYSTEM_ARCHITECTURE.md` 등)와 실제 구현 상태 전수 조사 및 동기화 완료.

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
