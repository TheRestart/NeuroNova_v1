# Claude AI 빠른 온보딩 가이드 (Quick Onboarding)

**최종 수정일**: 2025-12-28
**목적**: 최소 토큰으로 프로젝트 핵심만 빠르게 파악

> **원칙**: 이 문서만 읽으면 즉시 작업 가능. 상세 내용은 필요 시 참조 문서 확인.

---

## 🎯 1. 프로젝트 정체성 (30초 요약)

- **프로젝트명**: NeuroNova CDSS (Clinical Decision Support System)
- **현재 위치**: `c:\Users\gksqu\Downloads\git_hub\NeuroNova_v1`
- **프로젝트 성격**: **연습, 시연, 취업준비용** (포트폴리오 프로젝트)
- **현재 단계**: Week 6 완료 - AI 모듈 통합 완료
- **주요 기술**: Django REST Framework + OpenEMR + Orthanc + RabbitMQ

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
│   ├── LOG_작업이력.md               # 🔥 Week 1~6 작업 기록
│   ├── 00_업무계획서.md              # 전체 계획
│   ├── 08_API_명세서.md              # API 명세
│   ├── 25_에러_핸들링_가이드.md      # 🆕 에러 응답 표준
│   ├── 26_API_자동문서화_가이드.md   # 🆕 Swagger 설정
│   └── 27_데이터_검증_정책.md        # 🆕 데이터 검증 규칙
├── 05_ai_core/                      # AI 코어 모듈
├── NeuroNova_02_back_end/
│   └── 01_django_server/            # 🔥 Django 프로젝트 루트
│       ├── cdss_backend/            # Django 설정
│       ├── acct/                    # UC01: 인증/권한
│       ├── emr/                     # UC02: EMR (OpenEMR 연동)
│       ├── ocs/                     # UC03: 처방 (Order)
│       ├── lis/                     # UC04: 검사
│       ├── ris/                     # UC05: 영상 (Orthanc)
│       ├── ai/                      # UC06: AI Job
│       ├── alert/                   # UC07: 알림
│       ├── audit/                   # UC09: 감사 로그
│       └── utils/                   # 공통 유틸리티
├── NeuroNova_03_front_end_react/    # React 프론트엔드 (타 팀원)
├── NeuroNova_04_front_end_flutter/  # Flutter 모바일 앱 (타 팀원)
└── CDSS 프로젝트 인수인계 문서.md    # 🔥 Quick Start

**주요 Docker 컨테이너** (별도 실행):
- Orthanc PACS (DICOM 서버)
- RabbitMQ (AI Queue)
- OpenEMR (외부 EMR 시스템)
```

---

## 🏗️ 4. 핵심 아키텍처 (Gateway-Controller Pattern)

**Nginx는 Django 서버와만 연결되며, Django가 모든 외부 시스템의 허브 역할을 수행합니다.**

```
[Nginx] → [Django REST Framework]
               ↓
    ┌──────────┼──────────┐
    ↓          ↓          ↓
[OpenEMR]  [Orthanc]  [RabbitMQ]
               ↑
        [Flask AI Server] (유일한 서버간 직접 연결)
```

**모든 앱(UC)은 동일한 레이어 구조**:
```
Controller (views.py)     ← REST API 엔드포인트
    ↓
Service (services.py)     ← 비즈니스 로직
    ↓
Repository (repositories.py) ← DB 접근 (Django ORM)
Client (clients/)         ← 외부 시스템 (OpenEMR, Orthanc)
```

> 상세: [24_레이어_아키텍처_가이드.md](24_레이어_아키텍처_가이드.md)

---

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

### 8.1 Backend (Django) - PowerShell

```powershell
cd NeuroNova_02_back_end/01_django_server
./venv/Scripts/activate
python manage.py runserver 0.0.0.0:8000
```

### 8.2 Infrastructure (Docker) - PowerShell

```powershell
# Orthanc PACS
cd 03_orthanc_pacs
docker-compose up -d

# RabbitMQ
cd ../04_rabbitmq_queue
docker-compose up -d
```

### 8.3 API 문서 접속

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/

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
→ **[LOG_작업이력.md](LOG_작업이력.md)** (Week 1~6 작업 기록)

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

### Q5. 프론트엔드 팀에게 API 공유 방법?
A: Swagger UI URL 공유 (`http://localhost:8000/api/docs/`)
   또는 OpenAPI Schema 파일 export (`python manage.py spectacular --file schema.json`)

---

## 🎯 12. 다음 작업 (Phase 2 예정)

Phase 1 완료 (2025-12-28):
- ✅ 25_에러_핸들링_가이드.md
- ✅ 26_API_자동문서화_가이드.md
- ✅ 27_데이터_검증_정책.md

Phase 2 예정 (3-4일):
- [ ] 28_테스트_전략_가이드.md
- [ ] 29_로깅_전략_문서.md
- [ ] 30_성능_최적화_가이드.md

---

**문서 버전**: 1.0
**작성일**: 2025-12-28
**토큰 절약**: 이 문서는 REF_CLAUDE_CONTEXT.md (1000줄)의 핵심만 추출 (약 80% 토큰 절약)
**대상 독자**: Claude AI 온보딩용
