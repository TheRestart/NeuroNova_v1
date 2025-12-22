# CDSS (Clinical Decision Support System) 프로젝트

## 프로젝트 개요

**프로젝트명**: CDSS - Clinical Decision Support System (임상 의사결정 지원 시스템)
**개발 기간**: 16주 (4개월)
**개발 방식**: AI 협업 개발 (Claude AI + 사용자)
**아키텍처**: Django Backend + React/Flutter Frontend + 외부 시스템 통합

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
- **Flask + GPU**: AI 추론 서버 (MRI 종양 분석, Omics 분석)
- **RabbitMQ**: AI Job Queue

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
00_UML/                        # UML 설계 파일
01_doc/                          # 프로젝트 문서 및 스크립트
├── 01_권한7.txt                 # ...
├── ... (기타 문서)
├── GIT_SETUP_GUIDE.md           # Git 설정 가이드
└── ...
02_back_end/                     # 백엔드 서버 (Django + OpenEMR)
├── 01_django_server/            # Django 메인 서버
└── 02_openemr_server/           # OpenEMR Docker 구성
03_front_end_react/              # React 클라이언트 저장소
└── 01_react_client/             # React 웹 애플리케이션
04_front_end_flutter/            # Flutter 클라이언트 저장소
└── (Flutter App)                # Flutter 모바일 애플리케이션
README.md                        # [이 파일] 프로젝트 개요
```

### 📄 주요 문서 설명

| 문서 | 목적 | 대상 |
|---|---|---|
| **README.md** | 프로젝트 전체 개요 | 모든 사용자 |
| **CLAUDE_CONTEXT.md** | Claude AI 빠른 온보딩 | Claude AI |
| **업무계획서.md** | 기술 스택별 업무 분류 | 개발팀 |
| **02_세부 계획서.md** | 인프라 구성 상세 | DevOps 팀 |
| **03_개발_작업_순서.md** | Claude 1달 작업 계획 | Claude AI + 사용자 |
| **04_수정_지침서.md** | 수정 요청 템플릿 | 사용자 |
| **05_기술스택_상세.md** | 기술 스택 상세 설명 | 개발팀 |
| **06_환경설정_가이드.md** | 가상환경 및 의존성 관리 | 개발팀 (필수) |
| **07_일일_체크리스트.md** | 일일 개발 체크리스트 | 개발팀 |
| **08_API_명세서.md** | REST API 명세서 | 개발팀, QA |
| **09_데이터베이스_스키마.md** | DB 스키마 및 ERD | Database 팀 |
| **10_테스트_시나리오.md** | 테스트 시나리오 | QA/Test 팀 |
| **11_배포_가이드.md** | Docker 배포 가이드 | DevOps 팀 |

---

## 개발 일정 (16주)

### Phase 1: 기반 구축 (Week 1-4)
- Django 프로젝트 초기 설정
- UC1 (인증/권한) 7개 역할 구현
- UC2 (EMR Proxy), UC9 (Audit), UC7 (Alert) 기본 구현
- React 프로젝트 초기 설정, 로그인 화면
- MySQL 스키마 구축

**마일스톤**: 기본 인증 + 환자 조회 기능 완성

### Phase 2: 핵심 기능 개발 (Week 5-10)
- UC5 (RIS) - Orthanc 연동, DICOM Viewer
- UC6 (AI) - RabbitMQ 큐, Flask AI 서버
- UC3 (OCS), UC4 (LIS), UC8 (FHIR) 기본 구현
- React 역할별 화면 구현

**마일스톤**: 영상 조회 + AI 분석 + 처방 입력 완성

### Phase 3: 고급 기능 및 통합 (Week 11-14)
- UC5 판독문 서명, UC6 AI 비동기 폴링
- UC8 FHIR 리소스 변환 완성
- Flutter 모바일 앱 개발 (Patient 전용)
- 전체 통합 테스트

**마일스톤**: 전체 UC 기능 완성

### Phase 4: 최적화 및 배포 (Week 15-16)
- 성능 테스트 및 최적화
- 보안 감사
- Docker 배포, Prometheus 모니터링 구축
- Flutter App Store/Google Play 배포

**마일스톤**: 프로덕션 배포

---

## 빠른 시작 (Quick Start)

### 1. 프로젝트 클론 및 환경 설정 (개발자)

```bash
# 프로젝트 클론
git clone <repository-url>
cd UML

# Backend 환경 설정
cd 02_back_end/01_django_server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # .env 파일 수정 필요

# Frontend 환경 설정
cd ../../03_front_end_react/01_react_client
npm install
cp .env.example .env  # .env 파일 수정 필요
```

**중요**: [06_환경설정_가이드.md](06_환경설정_가이드.md) 참조

### 2. Claude AI에게 작업 요청 시

```
[03_개발_작업_순서.md]를 읽고 Week X의 작업을 시작해줘.
```

### 3. 수정 요청 시

```
[04_수정_지침서.md]의 [수정 템플릿]을 참고해서
UC1의 JWT 토큰 만료 시간을 30분으로 변경해줘.
```

### 4. 새로운 Claude 인스턴스 시작 시

```
[CLAUDE_CONTEXT.md]를 먼저 읽고 프로젝트를 이해한 후,
[03_개발_작업_순서.md]에서 현재 진행 상황을 확인해줘.
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

## 팀 구성

| 팀 | 인원 | 주요 역할 |
|---|---|---|
| Frontend | 3-4명 | React (2명), Flutter (1명), UI/UX (1명) |
| Backend | 4-5명 | Django (3명), DevOps (1명), 시니어 (1명) |
| Database | 1-2명 | DBA (1명), 데이터 엔지니어 (1명) |
| AI | 2명 | AI 엔지니어 (1명), MLOps (1명) |
| Integration | 2명 | 외부 시스템 연동 전문가 |
| DevOps | 1-2명 | Docker, CI/CD, 모니터링 |
| QA/Test | 2명 | 기능 테스트, E2E 자동화 |

**총 인원**: 14-18명

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
- [CLAUDE_CONTEXT.md](01_doc/CLAUDE_CONTEXT.md): Claude AI 온보딩
- [업무계획서.md](01_doc/업무계획서.md): 전체 업무 계획
- [02_세부 계획서.md](01_doc/02_세부 계획서.md): 인프라 상세
- [03_개발_작업_순서.md](01_doc/03_개발_작업_순서.md): 1달 작업 계획
- [04_수정_지침서.md](01_doc/04_수정_지침서.md): 수정 요청 가이드
- [05_기술스택_상세.md](01_doc/05_기술스택_상세.md): 기술 스택 상세
- [06_환경설정_가이드.md](01_doc/06_환경설정_가이드.md): 환경 설정
- [07_일일_체크리스트.md](01_doc/07_일일_체크리스트.md): 일일 체크리스트
- [08_API_명세서.md](01_doc/08_API_명세서.md): API 명세서
- [09_데이터베이스_스키마.md](01_doc/09_데이터베이스_스키마.md): DB 스키마
- [10_테스트_시나리오.md](01_doc/10_테스트_시나리오.md): 테스트 시나리오
- [11_배포_가이드.md](01_doc/11_배포_가이드.md): 배포 가이드

---

**Last Updated**: 2025-12-19
**Version**: 1.0
**Author**: Claude AI + Project Team
