# NeuroNova CDSS - 뇌종양 임상 의사결정 지원 시스템

## 프로젝트 개요

**프로젝트명**: NeuroNova CDSS - Clinical Decision Support System (뇌종양 임상 의사결정 지원 시스템)
**개발 기간**: 16주 (4개월)
**현재 상태**: Week 4 완료 - AI 코어 개발 준비 단계
**개발 방식**: AI 협업 개발 (Claude AI + 사용자)
**아키텍처**: Django Backend + AI Core (PyTorch) + React/Flutter Frontend + 외부 시스템 통합

---

## ⚡ 중요: 프로젝트 R&R (역할 분담)

### 현재 담당 역할: Django Backend 개발

**책임 범위:**
- ✅ Django REST API 개발 (UC01~UC09)
- ✅ 데이터 충돌 없는 CRUD 구현 (Optimistic/Pessimistic Locking)
- ✅ Write-Through 패턴 (OpenEMR, FHIR 동기화)
- ✅ 7-Layer Architecture 구현
- ✅ Transaction 관리 및 동시성 제어
- ✅ MySQL 데이터베이스 설계 및 마이그레이션

**제외 사항 (타 팀원 담당):**
- ❌ AI 모델 개발 (PyTorch, MONAI)
- ❌ DICOM 전처리 파이프라인
- ❌ Flask AI Serving
- ❌ Web Frontend (React)
- ❌ Mobile App (Flutter)

**개발 전략:**
- **안전한 CRUD**: Optimistic Locking (version 필드), Pessimistic Locking (select_for_update)
- **데이터 정합성**: Transaction Isolation Level 관리
- **동시성 테스트**: Race Condition 시나리오 테스트
- **Idempotency**: 멱등성 보장

📖 자세한 내용: [17_프로젝트_RR_역할분담.md](01_doc/17_프로젝트_RR_역할분담.md)

---

## 시스템 구성

### 핵심 기능 (9개 UC 모듈)
1. **UC1 - ACCT**: 인증/권한 관리 (7개 역할 RBAC)
2. **UC2 - EMR**: 전자의무기록 프록시 (OpenEMR 연동)
3. **UC3 - OCS**: 처방전달시스템
4. **UC4 - LIS**: 임상병리정보시스템
5. **UC5 - RIS**: 영상의학정보시스템 (Orthanc PACS 연동)
6. **UC6 - AI**: AI 오케스트레이션 (MRI/Omics 분석)
7. **UC7 - ALERT**: 타임라인/알림
8. **UC8 - FHIR**: 의료정보 교환 (HAPI FHIR 연동)
9. **UC9 - AUDIT**: 감사/보안 로그

### 사용자 역할 (7개)
- **Admin**: 시스템 관리자
- **Doctor**: 신경외과 의사
- **RIB**: 방사선과
- **Lab**: 검사실
- **Nurse**: 간호사
- **Patient**: 일반 환자
- **External**: 외부 기관 (FHIR API)

---

## 기술 스택

### Frontend
- **React Web**: 의료진용 (7개 역할 전체 지원)
  - **TypeScript 5.x**: 타입 안정성, 역할 기반 타입 정의
  - **Tailwind CSS 3.x**: 유틸리티 우선 스타일링, 역할별 테마 색상
  - **Zustand**: 경량 상태 관리, 역할별 스토어 분리
  - **shadcn/ui**: Tailwind 기반 UI 컴포넌트
- **Flutter Mobile**: 환자 전용 앱 (Patient 역할만)

### Backend
- **Django 4.2 LTS**: REST API
- **Celery + RabbitMQ**: 비동기 작업 (AI, FHIR 큐)
- **Django Channels**: WebSocket (실시간 알림)

### Database & Storage
- **MySQL 8.0**: 메인 데이터베이스
- **Redis 7.x**: 캐시 + Session + Channel Layer
- **MinIO**: S3 호환 객체 스토리지 (AI Artifacts)

### AI & ML
- **PyTorch 2.0+**: 딥러닝 프레임워크 (3D CNN, Vision Transformer)
- **Medical Imaging**: pydicom, SimpleITK, nibabel (DICOM 전처리)
- **AI Core**: 독립 Python 모듈 (Flask/React 의존성 없음)
- **Flask + GPU** (통합 예정): AI 추론 서버
- **RabbitMQ** (통합 예정): AI Job Queue

### Infrastructure
- **Docker + Docker Compose**: 컨테이너화
- **Nginx**: Reverse Proxy
- **Cloudflare**: CDN + DDoS + SSL/TLS
- **Prometheus + Grafana**: 모니터링
- **Alertmanager**: Code Blue 알림

### 외부 시스템 (상용)
- **OpenEMR**: 전자의무기록
- **Orthanc**: DICOM PACS 서버
- **HAPI FHIR**: HL7 FHIR 서버

---

## 문서 구조

### 📁 프로젝트 문서
```
00_UML/                          # UML 설계 파일
01_doc/                          # 프로젝트 문서 및 스크립트
├── 01_프로젝트_개요.md           # 프로젝트 전체 개요
├── 17_프로젝트_RR_역할분담.md    # 🔥 [NEW] R&R 정의 및 개발 전략
├── 18_AI_개발_가이드.md          # 🔥 [NEW] AI 코어 개발 가이드
├── REF_CLAUDE_CONTEXT.md        # Claude AI 온보딩 문서
├── LOG_작업이력.md               # 작업 이력 및 현황
└── ... (기타 문서)
NeuroNova_02_back_end/           # 백엔드 서버 (Django + OpenEMR)
├── 01_django_server/            # Django REST API (UC01~UC06 완성)
└── 02_openemr_server/           # OpenEMR Docker 구성
NeuroNova_03_front_end_react/    # React 클라이언트 저장소
└── 01_react_client/             # React 웹 애플리케이션
NeuroNova_04_front_end_flutter/  # Flutter 클라이언트 저장소
└── (Flutter App)                # Flutter 모바일 애플리케이션
05_ai_core/                      # 🔥 [NEW] AI 코어 모듈 (독립)
├── models/                      # AI 모델 정의 (TumorClassifier, Segmentation)
├── preprocessing/               # DICOM 전처리 파이프라인
├── inference/                   # 추론 엔진
├── tests/                       # 단위 테스트 (pytest)
├── interface_spec_template.md   # Interface Specification 템플릿
├── requirements.txt             # AI 전용 의존성
└── README.md                    # AI 코어 사용 가이드
06_trained_models/               # 학습된 모델 파일 (.pth, .h5)
README.md                        # [이 파일] 프로젝트 개요
```

### 📄 주요 문서 설명

| 문서 | 목적 | 대상 |
|---|---|---|
| **README.md** | 프로젝트 전체 개요 | 모든 사용자 |
| **01_프로젝트_개요.md** | 프로젝트 상세 개요 | 개발팀 |
| **17_프로젝트_RR_역할분담.md** | 🔥 [NEW] R&R 정의 및 개발 전략 | 전체 팀 (필수) |
| **18_AI_개발_가이드.md** | 🔥 [NEW] AI 코어 개발 완전 가이드 | AI 개발자 |
| **REF_CLAUDE_CONTEXT.md** | Claude AI 빠른 온보딩 | Claude AI |
| **LOG_작업이력.md** | 작업 이력 및 현황 | 전체 팀 |
| **08_API_명세서.md** | REST API 명세서 | 개발팀, QA |
| **09_데이터베이스_스키마.md** | DB 스키마 및 ERD | Database 팀 |
| **10_테스트_시나리오.md** | 테스트 시나리오 | QA/Test 팀 |
| **11_배포_가이드.md** | Docker 배포 가이드 | DevOps 팀 |

---

## 개발 일정 (16주)

### Phase 1: 기반 구축 (Week 1-4) ✅ **완료**
- ✅ Django 프로젝트 초기 설정
- ✅ UC01 (ACCT): 인증/권한 7개 역할 구현
- ✅ UC02 (EMR): OpenEMR 프록시, Write-Through 패턴
- ✅ UC05 (RIS): Orthanc PACS 연동
- ✅ UC06 (AI): RabbitMQ 큐 기본 구현
- ✅ MySQL 스키마 구축 (7-Layer Architecture)
- ✅ R&R 정의 및 AI 개발 환경 준비

**마일스톤**: 기본 인증 + EMR/PACS 통합 완성 ✅

### Phase 2: Backend CRUD 고도화 (Week 5-12) 🔄 **진행 중**
- 🔄 데이터 충돌 방지 패턴 구현 (Optimistic/Pessimistic Locking)
- 🔄 Transaction Isolation Level 설정 및 테스트
- 🔄 동시성 제어 (Race Condition 시나리오)
- 🔄 Idempotency 보장 (멱등성 패턴)
- 🔄 Django select_for_update() 활용
- ⏸️ UC03 (OCS), UC04 (LIS), UC08 (FHIR) - 타 팀원 담당
- ⏸️ React 역할별 화면 구현 - 타 팀원 담당
- ⏸️ AI 모델 개발 (PyTorch, MONAI) - 타 팀원 담당

**마일스톤**: 안전한 CRUD 구현 완료 + 동시성 테스트 통과

### Phase 3: Interface Specification 작성 및 통합 준비 (Week 13)
- Interface Specification 문서 작성 (AI → Backend)
- requirements.txt, Dockerfile 준비
- AI 모듈 전달 패키지 준비
- ⏸️ UC03/UC04/UC08 FHIR 리소스 변환 완성 - 타 팀원 담당
- ⏸️ Flutter 모바일 앱 개발 (Patient 전용) - 타 팀원 담당

**마일스톤**: AI 코어 모듈 완성 + 통합 준비 완료

### Phase 4: 통합 테스트 및 배포 (Week 14-16)
- AI 모듈 통합 (Django → RabbitMQ → Flask → AI Core)
- 전체 시스템 통합 테스트
- 성능 테스트 및 최적화 (AI 추론 속도)
- ⏸️ Docker 배포, Prometheus 모니터링 구축 - DevOps 담당
- ⏸️ Flutter App Store/Google Play 배포 - 타 팀원 담당

**마일스톤**: 전체 시스템 통합 완료 및 배포

---

## 빠른 시작 (Quick Start)

### 1. Django Backend 환경 설정 (현재 담당자)

```bash
# Backend 환경 설정
cd NeuroNova_02_back_end/01_django_server
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Django 서버 실행
python manage.py runserver 0.0.0.0:8000
```

### 2. Claude AI에게 작업 요청 시

```
[REF_CLAUDE_CONTEXT.md]를 먼저 읽고,
Django Backend에서 데이터 충돌 없는 CRUD를 구현해줘.
Optimistic Locking과 Pessimistic Locking 패턴을 적용해줘.
```

### 3. 새로운 Claude 인스턴스 시작 시

```
[REF_CLAUDE_CONTEXT.md]를 먼저 읽고 프로젝트를 이해한 후,
[LOG_작업이력.md]에서 현재 진행 상황을 확인해줘.
```

---

## 개발 규칙

### 아키텍처 원칙
1. **7-Layer Architecture**: Controller → Service → Repository/Client
2. **RBAC**: 7개 역할 기반 접근 제어
3. **Self Access**: Patient는 본인 데이터만 조회
4. **비동기 처리**: AI, FHIR 작업은 RabbitMQ 큐 사용
5. **감사 로그**: 모든 중요 액션은 `AuditClient.log_event()` 호출

### 코딩 스타일
- **Backend**: Django REST Framework, PEP 8
- **Frontend**: React Hooks, ESLint Airbnb
- **Database**: Snake Case (table_name, column_name)
- **API**: RESTful, URL 복수형 (/api/patients/)

### Git 전략
- **Branch**: main (production), develop (staging), feature/* (기능 개발)
- **Commit**: Conventional Commits (feat:, fix:, docs:, etc.)
- **PR**: 기능 단위 (UC별 또는 화면별)

---

## 팀 구성 및 역할 분담

### 현재 개발 단계: Phase 2 (AI 코어 개발)

| 팀 | 담당 | 현재 작업 | 상태 |
|---|---|---|---|
| **Django Backend** | **현재 담당자** | 데이터 충돌 없는 CRUD 구현 | 🔄 진행 중 |
| AI 코어 | 타 팀원 | PyTorch 모델 개발 | ⏸️ 대기 (타 팀원) |
| Backend Serving | 타 팀원 | Flask AI API 서버 | ⏸️ 대기 (Week 13 통합) |
| Frontend (React) | 타 팀원 | React Web UI | ⏸️ 대기 |
| Frontend (Flutter) | 타 팀원 | Flutter Mobile App | ⏸️ 대기 |
| Backend Infrastructure | **완료** | Django REST API | ✅ Week 4 완료 |

### Django Backend 팀 책임 범위
- **개발**: Django REST API, CRUD 로직, 동시성 제어
- **테스트**: Concurrency 테스트, Transaction 테스트
- **문서화**: API 명세서, DB 스키마
- **제외**: AI 모델, DICOM 전처리, Flask API, React UI, Flutter App (타 팀원 담당)

---

## 외부 시스템 연동 확인 사항

### ⚠️ 개발 시작 전 필수 확인
- [ ] **OpenEMR** API 엔드포인트 URL 및 인증 정보
- [ ] **Orthanc** DICOMweb API URL 및 DICOM AE Title
- [ ] **HAPI FHIR** Server URL 및 OAuth 2.0 인증 정보
- [ ] 방화벽 규칙 및 IP Whitelist 등록
- [ ] 테스트 계정 발급

자세한 사항은 [업무계획서.md - 3장 외부 상용 서버 확인 사항] 참조

---

## 모니터링

### Grafana 대시보드
- **System Overview**: API RPS, 응답 시간, 에러율
- **AI Performance**: GPU 사용량, AI Job 처리 시간
- **FHIR Sync Status**: 동기화 성공률, Queue 깊이

### Alertmanager (Code Blue)
- 5xx 에러율 > 5%
- AI Job Queue Backlog > 100
- DB 연결 풀 80% 이상

접속: `http://grafana.cdss.hospital.com:3000`

---

## 라이선스

**프로젝트 라이선스**: MIT License (또는 병원 내부 사용)

**사용 오픈소스**:
- Django (BSD License)
- React (MIT License)
- Flutter (BSD License)
- RabbitMQ (MPL 2.0)
- Prometheus (Apache 2.0)

---

## 연락처

**프로젝트 관리자**: [이름]
**이메일**: [email@hospital.com]
**Slack**: #cdss-project
**이슈 트래킹**: GitHub Issues (또는 Jira)

---

## 참고 자료

### 외부 문서
- [Django REST Framework](https://www.django-rest-framework.org/)
- [HL7 FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [PlantUML 문법](https://plantuml.com/ko/)
- [Mermaid ERD 문법](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)

### 내부 문서

#### 🔥 필수 문서 (Django Backend 개발)
- [17_프로젝트_RR_역할분담.md](01_doc/17_프로젝트_RR_역할분담.md): R&R 정의 및 개발 전략
- [16_Write_Through_패턴_가이드.md](01_doc/16_Write_Through_패턴_가이드.md): Write-Through 패턴 가이드
- [15_테스트_페이지_가이드.md](01_doc/15_테스트_페이지_가이드.md): 테스트 페이지 사용법

#### 📚 프로젝트 전체 문서
- [REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md): Claude AI 온보딩
- [LOG_작업이력.md](01_doc/LOG_작업이력.md): 작업 이력 및 현황
- [01_프로젝트_개요.md](01_doc/01_프로젝트_개요.md): 프로젝트 전체 개요
- [08_API_명세서.md](01_doc/08_API_명세서.md): Django REST API 명세서
- [09_데이터베이스_스키마.md](01_doc/09_데이터베이스_스키마.md): DB 스키마 및 ERD
- [10_테스트_시나리오.md](01_doc/10_테스트_시나리오.md): 테스트 시나리오
- [11_배포_가이드.md](01_doc/11_배포_가이드.md): Docker 배포 가이드

---

**Last Updated**: 2025-12-24
**Version**: 2.0 (AI R&R Update)
**Author**: Claude AI + Project Team
**Current Status**: Week 4 Complete - AI Core Development Phase Started
