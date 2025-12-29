# CDSS 프로젝트 인수인계 문서 (Quick Start)

**최종 수정일**: 2025-12-29
**작업 단계**: Week 7 - Phase 1 문서 구현 및 PACS 인프라 구축 완료

> [!IMPORTANT]
> 프로젝트의 상세한 아키텍처, 데이터 모델링(ERD), 사용자 권한(RBAC) 등 기술 참조 정보는 **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)**를 반드시 먼저 정독하십시오.

---

## 🚀 1. 빠른 시작 가이드 (Onboarding)

### 16.1 필수 개발 환경
- **Backend**: Windows PowerShell (Django 4.2+, Python 3.10+)
- **Frontend**: WSL Ubuntu-22.04 LTS (React npm 환경)
- **Database**: MySQL 8.0 (cdss_db, openemr 두 개의 스키마 사용)
- **Message Broker**: RabbitMQ (AI Queue 용)
- **영상 저장소**: Orthanc PACS (포트 8042, DICOM 포트 4242)
- **영상 뷰어**: OHIF Viewer (Nginx 포트 3000을 통해 제공)

### 16.2 환경 구축 및 실행
```powershell
# 1. 패키지 설치
cd NeuroNova_02_back_end/01_django_server
pip install -r requirements.txt

# 2. 인프라 컨테이너 실행 (Docker Desktop 필수)
cd ../03_orthanc_pacs
docker-compose up -d  # Orthanc PACS + OHIF Viewer + Nginx 통합 시작

cd ../04_rabbitmq_queue
docker-compose up -d  # RabbitMQ 메시지 브로커 시작

# 3. DB 마이그레이션 및 Django 서버 실행
cd ../01_django_server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 16.3 주요 접속 URL
- **Django API**: `http://localhost:8000/api/`
- **Swagger 문서**: `http://localhost:8000/api/docs/`
- **OHIF Viewer**: `http://localhost:3000/` (DICOM 영상 시각화)
- **Orthanc Web UI**: `http://localhost:8042/` (PACS 관리자 인터페이스)
- **RabbitMQ Management**: `http://localhost:15672/` (guest/guest)

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

### 4.1 일반 문제
1. **PowerShell `&&` 에러**: `&&` 대신 `;`를 사용하세요. (예: `cd folder; python manage.py runserver`)
2. **리팩토링 후 DB 오류**: `acct.User` 커스텀 모델을 사용하므로, 초기 마이그레이션이 꼬인 경우 `cdss_db`를 드랍하고 다시 `migrate` 하십시오.
3. **OpenEMR 연동 실패**: `openemr` 컨테이너가 정상 구동 중인지, `settings.py`의 `DATABASES['openemr']` 설정이 올바른지 확인하십시오.
4. **npm 명령어 무반응**: `npm`은 반드시 **WSL(Ubuntu) 터미널**에서 실행해야 합니다.

### 4.2 PACS/OHIF 관련 문제 (2025-12-29 추가)
1. **OHIF Viewer "No matching results"**:
   - **증상**: OHIF가 로드되지만 환자 목록이 표시되지 않음
   - **원인**: 브라우저 캐시, OHIF 설정 미인식, JavaScript 초기화 오류
   - **해결책**:
     - 브라우저 강력 새로고침 (Ctrl+Shift+R)
     - 브라우저 개발자 도구 → Console 탭에서 JavaScript 에러 확인
     - 브라우저 개발자 도구 → Network 탭에서 `/pacs/dicom-web/studies` 요청 확인
     - `docker restart cdss-ohif-viewer cdss-nginx` 실행
   - **검증**: `curl http://localhost/pacs/dicom-web/studies` 실행 시 JSON 응답 확인

2. **Orthanc 연결 실패**:
   - **증상**: Django RIS API에서 Orthanc 접근 불가
   - **해결책**:
     - `docker ps`로 `cdss-orthanc` 컨테이너 실행 확인
     - `curl http://localhost:8042/system` 응답 확인
     - `settings.py`의 `ORTHANC_API_URL` 설정 검증

3. **Docker 포트 충돌**:
   - **증상**: `port is already allocated` 에러
   - **해결책**:
     - OpenEMR이 포트 80을 사용 중이므로 Nginx는 포트 3000 사용
     - `netstat -ano | findstr :3000` (Windows) 또는 `lsof -i :3000` (Linux)로 포트 사용 확인

4. **DICOM 업로드 실패**:
   - **증상**: NIfTI → DICOM 변환 후 업로드 실패
   - **해결책**:
     - Orthanc 로그 확인: `docker logs cdss-orthanc`
     - `orthanc.json`의 `OverwriteInstances: true` 설정 확인
     - DICOM 파일 형식 검증 (dcmtk의 `dcmdump` 사용)

---

## 📚 주요 문서 위치
- **기술 설계 총괄**: [REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md)
- **작업 진행 기록**: [LOG_작업이력.md](01_doc/LOG_작업이력.md)
- **PACS 시스템 상세**: [프로젝트_구성_및_문제_보고서.md](NeuroNova_02_back_end/03_orthanc_pacs/프로젝트_구성_및_문제_보고서.md)

---

## 🏗️ 5. PACS 인프라 아키텍처 (2025-12-29 추가)

### 5.1 시스템 구성
```
┌─────────────────────────────────────────────────────────────┐
│                        브라우저 클라이언트                        │
│  - http://localhost:3000 (OHIF Viewer)                      │
│  - http://localhost:8000/api (Django API)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │     Nginx 역방향 프록시 (포트 3000)     │
        │  - CORS 헤더 추가                    │
        │  - MIME 타입 설정 (.mjs)             │
        │  - 라우팅: / → OHIF, /pacs → Orthanc│
        └───────────┬─────────────────┬────────┘
                    │                 │
        ┌───────────▼──────┐   ┌─────▼────────────┐
        │  OHIF Viewer     │   │ Orthanc PACS     │
        │  (Docker)        │   │ (포트 8042)      │
        │                  │   │ DICOM-Web API    │
        └──────────────────┘   └─────▲────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Django RIS API     │
                          │  (포트 8000)        │
                          │  OrthancClient      │
                          └─────────────────────┘
```

### 5.2 데이터 현황 (2025-12-29 기준)
- **환자 수**: 2명 (sub-0004, sub-0005)
- **Study 수**: 12개 (각 환자당 6개 MRI 시퀀스)
- **DICOM Instance 수**: 약 1,860개 (각 155 슬라이스)
- **MRI 시퀀스**: T1w, T2w, FLAIR, SWI, ce-T1w, DWI

### 5.3 주요 컴포넌트
1. **Orthanc PACS**: DICOM 저장소 및 DICOM-Web 서버
   - 포트: 8042 (HTTP/REST), 4242 (DICOM C-STORE)
   - 기능: QIDO-RS, WADO-RS, STOW-RS
   - 인증: 비활성화 (개발 환경)

2. **OHIF Viewer**: 웹 기반 DICOM 뷰어
   - 포트: Nginx 3000을 통해 제공
   - 데이터 소스: Orthanc PACS (`http://localhost/pacs/`)

3. **Nginx**: 역방향 프록시
   - CORS 처리, JavaScript 모듈 MIME 타입 설정
   - 보안 강화 (polyfill.io 차단)

4. **Django RIS API**: 백엔드 워크플로우 통합
   - `OrthancClient`: 10개 메서드 (health check, studies 조회, 검색, 다운로드 등)
   - 엔드포인트: `/api/ris/orthanc/`

### 5.4 알려진 제한사항
- OHIF Viewer가 DICOM-Web API 호출을 하지 않는 문제 (브라우저 캐시 관련 추정)
- 해결 방법: 브라우저 강력 새로고침, 개발자 도구 Console/Network 탭 확인
- 상세 트러블슈팅: `프로젝트_구성_및_문제_보고서.md` 참조
