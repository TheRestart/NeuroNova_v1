# Claude AI 빠른 온보딩 가이드 (Quick Onboarding)

**최종 수정일**: 2026-01-02
**목적**: 최소 토큰으로 프로젝트 핵심만 빠르게 파악
**최신 변경**: v3.0 아키텍처 개선 완료 (2026-01-02)

> **원칙**: 이 문서만 읽으면 즉시 작업 가능. 상세 내용은 필요 시 참조 문서 확인.

---

## 🎯 1. 프로젝트 정체성 (30초 요약)

- **프로젝트명**: NeuroNova CDSS (v2.0)
- **현재 위치**: `d:\1222\NeuroNova_v1`
- **프로젝트 성격**: **연습, 시연, 취업준비용** (포트폴리오 프로젝트)
- **현재 단계**: Week 8 진입 대기, Phase 2 (백엔드 통합 및 안정화) 완료
- **시스템 상태**: **Stable** (UC01~UC05 기능 검증 완료, 데이터 시딩 v3.0 적용)
- **주요 기술**: Django REST + FastAPI (AI) + Custom OHIF (HTJ2K) + Orthanc + Redis/Celery + React
- **배포 환경**: GCP VM + Docker + Nginx + Cloudflare (HTTPS)

---

## 🧑‍💼 2. 내 역할 (R&R)

### 현재 담당자(User)의 역할
- ✅ **Django Backend API 개발** (핵심)
- ✅ **API 문서 작성** (Swagger/OpenAPI)
- ✅ **데이터 무결성 정책 구현**

### 제외 사항 (타 팀원 담당)
- ❌ Frontend (React) - 타 팀원
- ❌ AI 코어 모델 개발 - 타 팀원
- ❌ 보안 작업 (우선순위 낮음 - 개발 중 오작동 우려)

### 작업 우선순위
1. **API 문서화** (Swagger)
2. **에러 핸들링** 표준화
3. **데이터 검증** 정책 구현
4. 테스트 전략
5. 로깅 및 성능 최적화

---

## 📂 3. 프로젝트 구조 (디렉토리)

```
NeuroNova_v1/
├── 00_UML/                          # UML 설계 파일 (PlantUML)
├── 01_doc/                          # 📚 모든 문서 (31개)
│   ├── REF_CLAUDE_ONBOARDING_QUICK.md # 🔥 빠른 온보딩 (이 문서)
│   ├── REF_CLAUDE_CONTEXT.md        # 🔥 상세 참조 (1000줄+)
│   ├── LOG_작업이력.md               # 🔥 Week 1~7 작업 기록
│   ├── 00_업무계획서.md              # 전체 계획
│   ├── 08_API_명세서.md              # API 명세
│   ├── 11_배포_가이드.md              # 배포 가이드 (구버전)
│   ├── 12_GCP_배포_가이드.md          # 🆕 GCP VM + Docker 배포
│   ├── 25_에러_핸들링_가이드.md      # 에러 응답 표준
│   ├── 26_API_자동문서화_가이드.md   # Swagger 설정
│   └── 27_데이터_검증_정책.md        # 데이터 검증 규칙
├── 05_ai_core/                      # AI 코어 모듈
├── NeuroNova_02_back_end/
│   ├── 01_ai_core/                  # AI 코어 모듈 (FastAPI)
│   ├── 02_django_server/            # 🔥 Django 프로젝트 루트
│   │   ├── cdss_backend/            # Django 설정
│   │   ├── acct/                    # UC01: 인증/권한
│   │   ├── emr/                     # UC02: EMR (OpenEMR 연동)
│   │   ├── ocs/                     # UC03: 처방 (Order)
│   │   ├── lis/                     # UC04: 검사
│   │   ├── ris/                     # UC05: 영상 (Orthanc)
│   │   ├── ai/                      # UC06: AI Job
│   │   ├── alert/                   # UC07: 알림
│   │   ├── audit/                   # UC09: 감사 로그
│   │   └── utils/                   # 공통 유틸리티
│   ├── 03_openemr_server/           # OpenEMR Docker 설정
│   ├── 04_ohif_viewer/              # OHIF Viewer Docker 설정
│   ├── 05_orthanc_pacs/             # Orthanc PACS Docker 설정
│   ├── 06_hapi_fhir/                # HAPI FHIR Server Docker 설정
│   └── 07_redis/                    # Redis Docker 설정
├── NeuroNova_03_front_end_react/    # 🔗 Git 서브모듈 (독립 저장소)
│   └── 00_test_client/              # 🆕 React + OHIF Viewer 통합
├── NeuroNova_04_front_end_flutter/  # Flutter 모바일 앱 (타 팀원)
├── .gitmodules                      # Git 서브모듈 설정 파일
└── CDSS 프로젝트 인수인계 문서.md    # 🔥 Quick Start

**Git 서브모듈 구조**:
- NeuroNova_03_front_end_react는 독립적인 Git 저장소로 관리됨
- URL: https://github.com/TheRestart/NeuroNova_03_front_end_react.git
- 프론트엔드와 백엔드를 각각 별도로 커밋/푸시 가능
- 상세: [GIT_서브모듈_관리_가이드.md](GIT_서브모듈_관리_가이드.md)

**주요 Docker 컨테이너** (별도 실행):
- 05_orthanc_pacs: Orthanc PACS (DICOM 서버)
- 07_redis: Redis (캐시 + Celery 브로커)
- 03_openemr_server: OpenEMR (외부 EMR 시스템)
- 06_hapi_fhir: HAPI FHIR Server (FHIR R4 표준)
- 04_ohif_viewer: OHIF Viewer (의료 영상 뷰어)

**로컬 가상환경** (venv - Django와 동일 환경):
- Django Server
- Celery Worker (비동기 작업 처리)
- Celery Beat (주기적 작업 스케줄러)
- Flower (Celery 모니터링 - 선택)

---

## 🏗️ 4. 핵심 아키텍처 (v3.0)

> **상세 아키텍처는 [06_시스템_아키텍처_v3.md](06_시스템_아키텍처_v3.md)를 참조하십시오.**

**핵심 요약 (v3.0 확정)**:
- **Gateway**: Nginx (Reverse Proxy with **X-Accel-Redirect**)
- **Backend**: Django REST Framework (Secure Proxy & Auth Delegate)
- **Frontend**: **Unified React SPA** (단일 빌드, OHIF npm 패키지 통합)
- **DICOM**: Orthanc (Internal) + **HTJ2K 자동 변환 (Orthanc Plugin)**
- **AI**: FastAPI (HTTP REST API) + Celery (Async Processing)
- **FHIR**: **Outbox 패턴** (트랜잭션 일관성 보장)

**데이터 흐름**:
Internet -> Cloudflare -> Nginx -> Django (Auth) -> Proxied Services (Orthanc/OHIF)

**v3.0 주요 변경**:
- Multi-SPA 폐기 → 단일 React 빌드
- HTJ2K Celery 수동 변환 → Orthanc Plugin 자동 변환
- FHIR Write-Through → Outbox 패턴 (비동기 동기화)
- FastAPI 통신 명세 확정 (HTTP REST API + OpenAPI 3.0)


## 🔑 5. 핵심 정책 (즉시 적용)

### 5.1 에러 응답 형식 (표준)

**모든 에러는 이 형식으로 응답**:
```json
{
  "error": {
    "code": "ERR_XXX",
    "message": "사용자 친화적 메시지",
    "detail": "개발자용 상세 정보 (선택)",
    "field": "필드명 (유효성 검증 실패 시)",
    "timestamp": "2025-12-28T10:30:00Z"
  }
}
```

**에러 코드**:
- `ERR_001~099`: 인증/권한
- `ERR_101~199`: 유효성 검증
- `ERR_201~299`: 리소스 없음
- `ERR_301~399`: 충돌/락킹
- `ERR_401~499`: 비즈니스 로직
- `ERR_501~599`: 외부 시스템

> 상세: [25_에러_핸들링_가이드.md](25_에러_핸들링_가이드.md)

### 5.2 데이터 검증 (4단계)

```
1. Serializer 검증 (형식, 타입, 필수값)
   ↓
2. 커스텀 필드 검증 (validate_<field_name>)
   ↓
3. 객체 수준 검증 (validate() - 다중 필드)
   ↓
4. 비즈니스 로직 검증 (Service Layer)
```

**원칙**: "절대 사용자 입력을 신뢰하지 마라" (Defensive Programming)

> 상세: [27_데이터_검증_정책.md](27_데이터_검증_정책.md)

### 5.3 개발 모드 (ENABLE_SECURITY)

`settings.py`:
- `ENABLE_SECURITY = False` (기본): 인증 없이 API 접근 가능 (개발/테스트용)
- `ENABLE_SECURITY = True`: JWT 인증 + 권한 체크 엄격 적용

---

## 👥 6. 사용자 역할 (RBAC)

**7개 역할**:
1. **Admin**: 시스템 관리자
2. **Doctor**: 의사
3. **RIB**: 영상의학과 의사
4. **Lab**: 임상병리사
5. **Nurse**: 간호사
6. **Patient**: 환자
7. **External**: 외부 시스템

**회원가입 정책** (2025-12-28):
- **Patient**: 자가 회원가입 가능 (`AllowAny`)
- **의료진**: Admin이 계정 생성 후 ID/PW 공지 (`IsAdmin` 권한 필요)
- **API**: 모든 역할의 회원가입 API는 구현되어 있음 (정책 변경 대비)

---

## 🗄️ 7. 데이터베이스

**2개 DB 사용**:
1. **cdss_db** (Django ORM) - 메인 DB
   - User, Patient, Encounter, Order, AIJob, Alert, AuditLog 등
2. **openemr** (Read-Only) - OpenEMR 외부 DB
   - patient_data, form_encounter (조회만)

**병렬 데이터 전달 (Parallel Dual-Write)**:
- Patient/Encounter/Order 생성 시 OpenEMR + Django DB에 독립적으로 저장
- 응답: `persistence_status` 필드로 각 저장소 성공/실패 확인

> 상세: [16_Write_Through_패턴_가이드.md](16_Write_Through_패턴_가이드.md)

---

## 🚀 8. 빠른 시작 (서버 실행)

### 8.1 통합 Docker 환경 (권장) ⭐

**전체 스택을 하나의 명령어로 실행**:

```powershell
# 루트 디렉토리에서 실행
cd d:\1222\NeuroNova_v1

# 전체 스택 시작 (14개 컨테이너)
docker-compose -f docker-compose.dev.yml up -d

# 컨테이너 상태 확인
docker-compose -f docker-compose.dev.yml ps

# 로그 확인 (실시간)
docker-compose -f docker-compose.dev.yml logs -f

# 특정 서비스 로그만 확인
docker-compose -f docker-compose.dev.yml logs -f django
docker-compose -f docker-compose.dev.yml logs -f celery-worker

# 전체 스택 종료
docker-compose -f docker-compose.dev.yml down
```

**14개 컨테이너 구성**:
- **Ingress**: nginx (1개)
- **Application**: django, celery-worker, celery-beat, flower, redis (5개)
- **Data**: cdss-mysql, openemr-mysql, orthanc, openemr, hapi-fhir (5개)
- **Observability**: prometheus, grafana, alertmanager (3개)

**주요 접속 URL**:
| 서비스 | URL | 계정 | 비고 |
|--------|-----|------|------|
| Django API | http://localhost/api | - | REST API (Nginx 경유) |
| Swagger UI | http://localhost/api/docs/ | - | API 문서 (Nginx 경유) |
| **Grafana** | http://localhost:3000 | admin/admin123 | 시스템 대시보드 |
| **Prometheus** | http://localhost:9090 | - | 메트릭 조회 |
| **Alertmanager** | http://localhost:9093 | - | 알림 관리 |
| Flower | http://localhost:5555 | - | Celery 모니터링 |
| Orthanc PACS | http://localhost:8042 | orthanc/orthanc | DICOM 서버 |
| OpenEMR | http://localhost:8081 | admin/pass | EMR 시스템 |

**데이터 초기화 (최초 1회)**:
```powershell
# Django 컨테이너에 접속하여 실행
docker-compose -f docker-compose.dev.yml exec django python manage.py create_test_users
docker-compose -f docker-compose.dev.yml exec django python manage.py init_sample_data
docker-compose -f docker-compose.dev.yml exec django python manage.py upload_sample_dicoms --dry-run
```

---

### 8.2 레거시 방식 (Deprecated)

> 더 이상 권장하지 않습니다. 개별 컨테이너 실행 방식은 [LOG_작업이력.md](LOG_작업이력.md)의 과거 기록이나 [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)를 참조하십시오.

---

### 8.3 React 테스트 클라이언트 (WSL 필수)

**CRITICAL**: React는 반드시 **WSL Ubuntu-22.04 LTS** 환경에서 실행해야 합니다.

**Terminal (WSL Ubuntu-22.04):**
```bash
# WSL Ubuntu 진입
wsl -d Ubuntu-22.04

# 프로젝트 디렉토리 이동
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client

# 패키지 설치 (최초 1회, --legacy-peer-deps 필수)
npm install --legacy-peer-deps

# 개발 서버 시작 (포트 3001)
PORT=3001 npm start
```

**접속**: http://localhost:3001

**주요 이슈 해결**:
- OHIF Viewer 3.11.11이 React 16.8.6 요구하나 프로젝트는 React 18.3.1 사용 → `--legacy-peer-deps` 플래그로 해결
- cornerstone-wado-image-loader 4.13.3 버전 없음 → package.json에서 4.13.2로 수정 완료
- WSL에서 localhost:8000 연결 불가 → package.json proxy를 172.29.64.1:8000으로 설정 완료

**상세 가이드**: `NeuroNova_03_front_end_react/00_test_client/사용방법_설명문서.md`

---

## 📝 9. API 개발 체크리스트

새로운 API 개발 시 반드시 확인:

- [ ] `@extend_schema` 데코레이터 추가 (Swagger 문서화)
- [ ] Serializer에 `help_text` 작성
- [ ] 에러 응답 예시 추가 (400, 401, 403, 404)
- [ ] 데이터 검증 4단계 모두 구현
- [ ] 커스텀 Exception 사용 (`utils/exceptions.py`)
- [ ] Service Layer에서 비즈니스 로직 처리
- [ ] 감사 로그 기록 (`AuditClient.log()`)
- [ ] Transaction 관리 (`@transaction.atomic`)

> 상세: [26_API_자동문서화_가이드.md](26_API_자동문서화_가이드.md)

---

## 🔍 10. 상황별 참조 문서

### 프로젝트 전체 이해
→ **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)** (1000줄 상세 참조)

### 현재 진행 상황 확인
→ **[LOG_작업이력.md](LOG_작업이력.md)** (Week 1~7 작업 기록)

### API 명세 확인
→ **[08_API_명세서.md](08_API_명세서.md)** (수동 작성 버전)
→ **http://localhost:8000/api/docs/** (Swagger - 자동 생성)

### 에러 처리 방법
→ **[25_에러_핸들링_가이드.md](25_에러_핸들링_가이드.md)**

### Swagger 설정 방법
→ **[26_API_자동문서화_가이드.md](26_API_자동문서화_가이드.md)**

### 데이터 검증 규칙
→ **[27_데이터_검증_정책.md](27_데이터_검증_정책.md)**

### 동시성 제어 (락킹/멱등성)
→ **[21_락킹_멱등성_개발_가이드.md](21_락킹_멱등성_개발_가이드.md)**

### 외부 시스템 연동
→ **[16_Write_Through_패턴_가이드.md](16_Write_Through_패턴_가이드.md)**

### 레이어 아키텍처 규칙
→ **[24_레이어_아키텍처_가이드.md](24_레이어_아키텍처_가이드.md)**

### 배포 가이드 (GCP)
→ **[12_GCP_배포_가이드.md](12_GCP_배포_가이드.md)** (GCP VM + Docker + Cloudflare)

### v3.0 아키텍처 문서 (신규)
→ **[06_시스템_아키텍처_v3.md](06_시스템_아키텍처_v3.md)** - v3.0 확정 아키텍처
→ **[45_DICOM_뷰잉_시퀀스_다이어그램.md](45_DICOM_뷰잉_시퀀스_다이어그램.md)** - Secure Proxy 패턴
→ **[46_FastAPI_AI_서버_명세서.md](46_FastAPI_AI_서버_명세서.md)** - OpenAPI 3.0 완전 스펙
→ **[47_FHIR_동기화_Outbox_패턴_명세서.md](47_FHIR_동기화_Outbox_패턴_명세서.md)** - Outbox 패턴
→ **[90_작업이력/아키텍처_개선_완료_보고서_20260102.md](90_작업이력/아키텍처_개선_완료_보고서_20260102.md)** - 개선 성과 요약

---

## ⚡ 11. 자주 묻는 질문 (FAQ)

### Q1. Claude AI에게 작업 요청 시작 방법?
A: 다음 순서로 문서 읽기:
1. **이 문서** (REF_CLAUDE_ONBOARDING_QUICK.md) - 5분
2. **[LOG_작업이력.md](LOG_작업이력.md)** - 현재 상황 파악
3. 필요 시 세부 문서 참조

### Q2. API 개발 시 코드 작성 순서?
A: Service → Repository → Controller → Serializer → Tests

### Q3. 에러가 발생하면?
A: 커스텀 Exception 사용 (`utils/exceptions.py`에서 import)

### Q4. OpenEMR 연동이 실패하면?
A: Docker 컨테이너 상태 확인 (`docker ps`), 로그 확인 (`docker logs`)

### Q5. 테스트 계정 비밀번호는?
A:
- `admin` / `admin123`
- `doctor` / `doctor123`
- `nurse` / `nurse123`
- `patient` / `patient123`
- `radiologist` / `radiologist123`
- `labtech` / `labtech123`

생성: `docker exec neuronova-django-dev python manage.py create_test_users`

**비밀번호 규칙 변경 (2025-12-31)**:
- 이전: `*123!@#` → 현재: `*123` (특수문자 완전 제거)
- 변경 이유: Python escape sequence 문제 및 로그인 인증 실패 해결
- 상세: PASSWORD_CHANGE_PLAN.md 참조

### 8.6 로그인 테스트 (계정 정보)

**테스트 계정 목록** (상세: [32_권한_정의_요약.md](32_권한_정의_요약.md#8-테스팅용-임시-계정-test-accounts))

- **Admin**: `admin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Patient**: `patient` / `patient123`

1. http://localhost:3000 접속 (React App)
2. 위 계정으로 로그인 시도
3. 역할별 대시보드 접근 확인

### Q6. React 테스트 클라이언트 사용법?
A:
1. Django 서버 실행 (`python manage.py runserver`)
2. WSL에서 `cd 00_test_client && npm start`
3. http://localhost:3001 접속
4. '예시 입력' 버튼 활용하여 데이터 자동 입력 후 테스트

상세: `NeuroNova_03_front_end_react/00_test_client/README.md`

### Q7. 프론트엔드 팀에게 API 공유 방법?
A: Swagger UI URL 공유 (`http://localhost:8000/api/docs/`)
   또는 OpenAPI Schema 파일 export (`python manage.py spectacular --file schema.json`)

---

## 🚨 12. 코딩 규칙 (CRITICAL)

### 이모지 사용 금지 (코드 파일)
**Windows cp949 인코딩 오류 방지를 위해 필수 준수**

**[금지] Python, JavaScript, TypeScript 코드:**
```python
# [BAD] 이모지 사용 금지
print("User created!")  # UnicodeEncodeError 발생

# [GOOD] 대괄호 텍스트 사용
print("[SUCCESS] User created!")
print("[ERROR] Failed to create user")
print("[INFO] Processing...")
```

**[허용] Markdown 문서 (.md 파일):**
```markdown
## Project Status
- Task 1 완료
- Task 2 진행 중
```

**적용 대상:**
- Python 코드 (.py)
- JavaScript/TypeScript 코드 (.js, .jsx, .ts, .tsx)
- Django templates (.html)
- 설정 파일 (.json, .yaml, .env)

**예외:**
- Markdown 문서 (.md)
- README 파일
- 문서화 파일

---

## 🎯 13. 완료된 Phase (요약)

**Phase 2.5 완료 (2026-01-02)** ⭐ NEW:
- ✅ **v3.0 아키텍처 확정**: Multi-SPA → Unified React SPA
- ✅ **Critical/High 이슈 해결**: 9개 이슈 100% 해결
- ✅ **Secure Proxy 패턴**: X-Accel-Redirect 완전 명세화
- ✅ **백엔드 안정화 (2026-01-02)**: DB 컬럼 불일치 및 RIS 404 에러 완전 해결
- ✅ **V3.0 데이터 시딩**: BRCA1 유전체 변이 등 통합 테스트용 데이터 구축 완료
- ✅ **프론트엔드 최적화**: React Hook 위반 수정 및 예시 데이터 연동 완료

**Phase 3. 프론트엔드 고도화 진입 (진행 중) 🚀**:
- [x] **의사 워크스테이션(Built)**: 프리미엄 디자인 기반 진료 대기 명단 구현 (2026-01-02)
- [x] **런타임 복구**: ResponseTable 전체 리팩토링으로 Hook 위반 이슈 등 완전 해결
- [ ] **통합 진료 차트(Next)**: 환자 카드 클릭 시 EMR+RIS+AI 통합 뷰어 구현 예정
- [ ] **실시간 알림 모듈 통합**: WebSocket 및 Toast 알림 연동
- [ ] **AI 판독 보고서 연동 시각화**: LIS 유전체 정보 및 AI 결과 그래픽 요소 추가

**Phase 1 & 2 완료 (2025-12-31)**:
- ✅ **API 표준화**: 에러 핸들링, Swagger, 데이터 검증 완료
- ✅ **아키텍처**: Redis-only 마이그레이션, Secure Proxy 적용, OHIF v3.0 통합
- ✅ **배포**: React 테스트 클라이언트 Nginx 배포, 무한 새로고침 해결
- ✅ **문서화**: 온보딩 가이드 및 아키텍처 문서 최신화

---

## 🚀 원본 PC 복귀 후 즉시 실행 가이드

### 1단계: React 패키지 설치
```bash
cd NeuroNova_03_front_end_react/00_test_client
npm install
```

### 2단계: 데이터베이스 마이그레이션
```bash
cd NeuroNova_02_back_end/02_django_server
python manage.py makemigrations
python manage.py migrate
python manage.py seed_master_data
```

### 3단계: 서비스 기동
```bash
# Redis
cd NeuroNova_02_back_end/07_redis && docker-compose up -d

# Orthanc PACS
cd ../05_orthanc_pacs && docker-compose up -d

# Django Server
cd ../02_django_server && python manage.py runserver

# React App (OHIF 포함)
cd NeuroNova_03_front_end_react/00_test_client
npm start
```

### 4단계: 기능 검증
1. 브라우저에서 `http://localhost:3000` 접속
2. 로그인 후 UC05: RIS 메뉴 클릭
3. **Orthanc 환자 목록** 확인
4. **"View Study" 버튼**으로 DICOM Viewer 접근
5. Study 메타데이터 표시 확인

---

**문서 버전**: 1.7
**작성일**: 2026-01-02
**최신 업데이트**: v3.0 아키텍처 개선 완료 반영
**토큰 절약**: 이 문서는 REF_CLAUDE_CONTEXT.md (1000줄)의 핵심만 추출 (약 80% 토큰 절약)
**대상 독자**: Claude AI 온보딩용
