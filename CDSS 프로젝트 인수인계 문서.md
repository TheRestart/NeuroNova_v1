# CDSS 프로젝트 인수인계 문서 (Quick Start)

**최종 수정일**: 2025-12-24
**작업 단계**: Week 5 - 병렬 데이터 전달 아키텍처 및 문서 최적화 단계

> [!IMPORTANT]
> 프로젝트의 상세한 아키텍처, 데이터 모델링(ERD), 사용자 권한(RBAC) 등 기술 참조 정보는 **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)**를 반드시 먼저 정독하십시오.

---

## 🚀 1. 빠른 시작 가이드 (Onboarding)

### 16.1 필수 개발 환경
- **Backend**: Windows PowerShell (Django 4.2+, Python 3.10+)
- **Frontend**: WSL Ubuntu-22.04 LTS (React npm 환경)
- **Database**: MySQL 8.0 (cdss_db, openemr 두 개의 스키마 사용)
- **Message Broker**: RabbitMQ (AI Queue 용)
- **영상 저장소**: Orthanc PACS

### 16.2 환경 구축 및 실행
```powershell
# 1. 패키지 설치
cd NeuroNova_02_back_end/01_django_server
pip install -r requirements.txt

# 2. 인프라 컨테이너 실행 (Docker Desktop)
cd 03_orthanc_pacs; docker-compose up -d
cd ../04_rabbitmq_queue; docker-compose up -d

# 3. DB 마이그레이션 및 서버 실행
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

---

## 🛡️ 2. 보안 및 개발 모드 설정

### 2.1 ENABLE_SECURITY 토글 (`settings.py`)
- `ENABLE_SECURITY = False` (기본값): 인증 없이 모든 API 접근 가능 (개발/테스트 용)
- `ENABLE_SECURITY = True`: JWT 인증 및 역할별 Permission(10개 클래스) 엄격히 적용

### 2.2 회원가입 정책 (2025-12-28 업데이트)
- **Patient (환자)**: 자가 회원가입 가능 (`POST /api/acct/register/` - AllowAny)
- **의료진** (Doctor, RIB, Lab, Nurse, External): Admin이 계정 생성 후 ID/PW 공지
  - Admin 전용 계정 생성 API 사용 (IsAdmin 권한 필요)
  - 보안 강화 및 내부 인력 관리 목적
- **API**: 모든 역할의 회원가입 API는 구현되어 있음 (정책 변경 대비)

### 2.3 중앙 인증 정책
- 모든 외부 시스템(OpenEMR, Orthanc) 접근은 반드시 Django API를 경유해야 합니다.
- **클라이언트 직접 호출 엄금**.

---

## 📂 3. 프로젝트 핵심 구조 (SSOT 기반)

- **디렉토리 맵**: `REF_CLAUDE_CONTEXT.md#Folder-Map` 참조
- **사용자 역할(RBAC)**: `REF_CLAUDE_CONTEXT.md#RBAC` 참조 (7개 역할)
- **병렬 데이터 전달(Parallel Dual-Write)**: 환자/진료/처방 데이터 생성 시 OpenEMR과 Django DB에 독립적으로 저장되며, 응답 결과는 `persistence_status` 필드로 확인합니다.

---

## 🐛 4. 빈번한 문제 해결 (Troubleshooting)

1. **PowerShell `&&` 에러**: `&&` 대신 `;`를 사용하세요. (예: `cd folder; python manage.py runserver`)
2. **리팩토링 후 DB 오류**: `acct.User` 커스텀 모델을 사용하므로, 초기 마이그레이션이 꼬인 경우 `cdss_db`를 드랍하고 다시 `migrate` 하십시오.
3. **OpenEMR 연동 실패**: `openemr` 컨테이너가 정상 구동 중인지, `settings.py`의 `DATABASES['openemr']` 설정이 올바른지 확인하십시오.
4. **npm 명령어 무반응**: `npm`은 반드시 **WSL(Ubuntu) 터미널**에서 실행해야 합니다.

---

## 📚 주요 문서 위치
- **기술 설계 총괄**: [REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md)
- **작업 진행 기록**: [LOG_작업이력.md](01_doc/LOG_작업이력.md)
- **향후 계획 및 로드맵**: [업무계획서.md](01_doc/업무계획서.md)
