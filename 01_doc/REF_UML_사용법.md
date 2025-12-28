# CDSS 시스템 UML 프로젝트 이용법

## 프로젝트 개요
이 프로젝트는 임상 의사결정 지원 시스템(CDSS)의 상세 설계 문서를 포함하고 있습니다.
총 9개의 Use Case(UC)로 구성되어 있으며, 각 UC별로 Usecase, Sequence, Class Diagram을 제공합니다.

---

## 폴더 구조 및 파일 형식

### 1. 루트 디렉토리 (`/UML`)

#### `CDSS System 상세설계.mdj`
- **파일 형식**: StarUML 프로젝트 파일
- **용도**: 시스템 전체 아키텍처 및 상세 설계
- **사용 도구**: StarUML 7.0 Trial (29일 평가판)
- **사용 방법**:
  1. StarUML 프로그램 설치
  2. `파일 > 열기`에서 `.mdj` 파일 선택
  3. 프로젝트 트리에서 각 다이어그램 확인

---

### 2. `/usecase` 폴더

#### 파일 목록
- `UC1-Accounts-Auth.puml`
- `UC2-EMR-Proxy.puml`
- `UC3-OCS.puml`
- `UC4-LIS.puml`
- `UC5-RIS.puml`
- `UC6-AI-Orchestration.puml`
- `UC7-Timeline-AlertCore.puml`
- `UC8-FHIR.puml`
- `UC9-Audit-Admin.puml`

#### 파일 형식
- **확장자**: `.puml` (PlantUML)
- **내용**: 각 Use Case의 사용자-시스템 상호작용 다이어그램

#### 사용 방법
1. **VSCode에서 보기**:
   - VSCode에서 파일 열기
   - `Alt+D` 키를 눌러 미리보기 창 열기
   - 또는 `Ctrl+Shift+P` → `PlantUML: Preview Current Diagram` 선택

2. **필요한 확장 프로그램**:
   - `PlantUML` (jebbs.plantuml)
   - Java Runtime Environment 필요

3. **내보내기**:
   - `Ctrl+Shift+P` → `PlantUML: Export Current Diagram`
   - PNG, SVG, PDF 등으로 저장 가능

#### Use Case 목록
- **UC1**: Accounts/Auth (계정 및 인증)
- **UC2**: EMR Proxy (전자의무기록)
- **UC3**: OCS (처방전달시스템)
- **UC4**: LIS (임상병리시스템)
- **UC5**: RIS (영상의학시스템)
- **UC6**: AI Orchestration (AI 통합)
- **UC7**: Timeline/Alert Core (타임라인 및 알림)
- **UC8**: FHIR (의료 정보 교환)
- **UC9**: Audit/Admin (감사 및 관리)

---

### 3. `/sequence` 폴더

#### 폴더 구조
```
/sequence
├── 1. ACCT/     (SD-ACCT-01.puml ~ SD-ACCT-05.puml)
├── 2. EMR/      (SD-EMR-01.puml ~ SD-EMR-05.puml)
├── 3. OCS/      (SD-OCS-01.puml ~ SD-OCS-05.puml)
├── 4. LIS/      (SD-LIS-01.puml ~ SD-LIS-05.puml)
├── 5. RIS/      (SD-RIS-01.puml ~ SD-RIS-14.puml)
├── 6. AI/       (SD-AI-01.puml ~ SD-AI-05.puml)
├── 7.ALERT/     (SD-ALERT-01.puml ~ SD-ALERT-03.puml)
├── 8.FHIR/      (SD-FHIR-01.puml ~ SD-FHIR-12.puml)
└── 9.AUDIT/     (SD-AUDIT-01.puml ~ SD-AUDIT-02.puml)
```

#### 파일 형식
- **확장자**: `.puml` (PlantUML)
- **내용**: 시퀀스 다이어그램 (객체 간 메시지 흐름)
- **명명 규칙**: `SD-[모듈명]-[번호].puml`

#### 사용 방법
1. **보기**: Usecase와 동일 (`Alt+D` 또는 Preview 명령)
2. **내용**: 각 시나리오별 시스템 컴포넌트 간 상호작용 흐름
3. **예시**:
   - `SD-ACCT-01.puml`: 로그인 성공 시나리오
   - `SD-RIS-01.puml`: 영상 검사 오더 생성

---

### 4. `/class` 폴더

#### 폴더 구조 (UC별 모듈화)
```
/class
├── 1. UC01 (ACCT)/
│   ├── uc01_01_class_main.puml      (메인 - 전체 연결)
│   ├── uc01_02_domain.puml          (도메인 엔티티)
│   ├── uc01_03_dtos.puml            (데이터 전송 객체)
│   ├── uc01_04_clients.puml         (외부 클라이언트)
│   ├── uc01_05_repositories.puml    (데이터 저장소)
│   ├── uc01_06_services.puml        (비즈니스 로직)
│   └── uc01_07_controllers.puml     (API 컨트롤러)
├── 2. UC02 (EMR)/
├── 3. UC03 (OCS)/
├── 4. UC04 (LIS)/
├── 5. UC05 (RIS)/
├── 6. UC06 (AI)/
├── 7. UC07 (ALERT)/
├── 8. UC08 (FHIR)/
└── 9. UC09 (AUDIT)/
```






















#### 파일 형식
- **확장자**: `.puml` (PlantUML)
- **내용**: 클래스 다이어그램 (클래스 구조 및 관계)

#### 파일 구성 설명

##### 1. `_01_class_main.puml` (메인 파일)
- **역할**: 전체 클래스 다이어그램의 통합 진입점
- **내용**:
  - 다른 6개 파일을 `!include` 문으로 포함
  - 레이어 간 의존성 관계 정의 (Controller → Service → Repository)
  - 도메인 엔티티 간 관계 정의

##### 2. `_02_domain.puml`
- **내용**: 도메인 모델 (엔티티, 값 객체)
- **예시**: User, Role, Permission, RefreshToken 등

##### 3. `_03_dtos.puml`
- **내용**: API 요청/응답 객체
- **예시**: LoginRequest, LoginResponse, UserProfileDTO 등

##### 4. `_04_clients.puml`
- **내용**: 외부 시스템 호출 인터페이스
- **예시**: AuditClient, EmailClient, SMSClient 등

##### 5. `_05_repositories.puml`
- **내용**: 데이터베이스 접근 계층
- **예시**: UserRepository, RoleRepository 등

##### 6. `_06_services.puml`
- **내용**: 비즈니스 로직 계층
- **예시**: AuthService, JwtService, AccessPolicyService 등

##### 7. `_07_controllers.puml`
- **내용**: API 엔드포인트 계층
- **예시**: AuthController, MeController, RoleAdminController 등

















#### 사용 방법

##### 전체 클래스 다이어그램 보기
1. `uc0X_01_class_main.puml` 파일 열기
2. `Alt+D` 또는 `Ctrl+Shift+P` → `PlantUML: Preview`
3. 모든 레이어가 통합된 다이어그램 확인

##### 개별 레이어만 보기
- 특정 `_0X_xxx.puml` 파일을 개별적으로 열어 해당 레이어만 확인 가능

##### 수정 시 주의사항
- 메인 파일(`_01_class_main.puml`)에서 관계 정의
- 개별 파일에서는 클래스 정의만 수정
- `!include` 경로가 상대 경로로 설정되어 있으므로 파일 이동 시 주의

---

### 5. `/db` 폴더

#### 파일 목록
- `CDSS_DB.mmd`, `CDSS_DB.png`, `CDSS_DB.svg`
- `HAPI_DB.mmd`, `HAPI_DB.png`, `HAPI_DB.svg`
- `OpenEMR_DB.mmd`, `OpenEMR_DB.png`, `OpenEMR_DB.svg`
- `Orthanc_DB.mmd`, `Orthanc_DB.png`, `Orthanc_DB.svg`
- `IntegrationERD.mmd`, `IntegrationERD.png`, `IntegrationERD.svg`

#### 파일 형식

##### `.mmd` 파일
- **형식**: Mermaid Diagram (텍스트 기반 ERD)
- **내용**: Entity-Relationship Diagram (ERD)
- **사용 도구**:
  - Mermaid Live Editor (https://mermaid.live)
  - VSCode Mermaid 확장 프로그램
  - Draw.io (Mermaid 플러그인)

##### `.png` / `.svg` 파일
- **형식**: 이미지 파일 (미리 렌더링된 ERD)
- **용도**: 문서 첨부, 프레젠테이션, 빠른 확인
- **차이점**:
  - PNG: 래스터 이미지 (확대 시 품질 저하)
  - SVG: 벡터 이미지 (확대해도 선명)

#### ERD 목록 설명
- **CDSS_DB**: Django CDSS 메인 데이터베이스 스키마
- **HAPI_DB**: HAPI FHIR 서버 데이터베이스
- **OpenEMR_DB**: OpenEMR 전자의무기록 시스템 DB
- **Orthanc_DB**: Orthanc DICOM 서버 DB
- **IntegrationERD**: 전체 시스템 통합 ERD

#### 사용 방법

##### Mermaid 파일 편집 및 미리보기
1. **VSCode 사용**:
   - 확장 프로그램 설치: `Mermaid Preview` (bierner.markdown-mermaid)
   - `.mmd` 파일 열기
   - `Ctrl+Shift+V`: Markdown 미리보기 모드에서 확인

2. **온라인 편집기 사용**:
   - https://mermaid.live 접속
   - `.mmd` 파일 내용 복사/붙여넣기
   - 실시간 미리보기 및 편집
   - PNG/SVG로 내보내기 가능

##### 이미지 파일 보기
- `.png`, `.svg` 파일은 일반 이미지 뷰어로 바로 확인 가능

---

## 빠른 시작 가이드

### 1. 필수 도구 설치

#### VSCode 확장 프로그램
```
- PlantUML (jebbs.plantuml)
- Mermaid Preview (bierner.markdown-mermaid)
```

#### 외부 도구
- **Java JRE**: PlantUML 실행을 위해 필요
- **StarUML 7.0**: `.mdj` 파일 편집용 (선택사항)

### 2. 다이어그램 보기

#### PlantUML (Usecase, Sequence, Class)
```
1. VSCode에서 .puml 파일 열기
2. Alt+D 키 누르기
   또는
   Ctrl+Shift+P → "PlantUML: Preview Current Diagram"
```

#### Mermaid (ERD)
```
1. VSCode에서 .mmd 파일 열기
2. Ctrl+Shift+V (Markdown 미리보기)
   또는
   온라인: https://mermaid.live
```

#### StarUML
```
1. StarUML 실행
2. 파일 > 열기 > "CDSS System 상세설계.mdj" 선택
```

### 3. 다이어그램 내보내기

#### PlantUML 내보내기
```
Ctrl+Shift+P → "PlantUML: Export Current Diagram"
지원 형식: PNG, SVG, PDF, EPS
```

#### Mermaid 내보내기
- 온라인 편집기에서 내보내기 버튼 클릭
- 또는 이미 생성된 `.png`, `.svg` 파일 사용

---

## Use Case별 다이어그램 매핑표

| UC | 모듈명 | Usecase | Sequence | Class | 설명 |
|---|---|---|---|---|---|
| UC1 | ACCT | UC1-Accounts-Auth.puml | SD-ACCT-01~05 | 1. UC01 (ACCT) | 계정/인증 |
| UC2 | EMR | UC2-EMR-Proxy.puml | SD-EMR-01~05 | 2. UC02 (EMR) | 전자의무기록 |
| UC3 | OCS | UC3-OCS.puml | SD-OCS-01~05 | 3. UC03 (OCS) | 처방전달 |
| UC4 | LIS | UC4-LIS.puml | SD-LIS-01~05 | 4. UC04 (LIS) | 임상병리 |
| UC5 | RIS | UC5-RIS.puml | SD-RIS-01~14 | 5. UC05 (RIS) | 영상의학 |
| UC6 | AI | UC6-AI-Orchestration.puml | SD-AI-01~05 | 6. UC06 (AI) | AI 통합 |
| UC7 | ALERT | UC7-Timeline-AlertCore.puml | SD-ALERT-01~03 | 7. UC07 (ALERT) | 타임라인/알림 |
| UC8 | FHIR | UC8-FHIR.puml | SD-FHIR-01~12 | 8. UC08 (FHIR) | FHIR 연동 |
| UC9 | AUDIT | UC9-Audit-Admin.puml | SD-AUDIT-01~02 | 9. UC09 (AUDIT) | 감사/관리 |

---

## 다이어그램 읽는 순서 (권장)

### 신규 개발자 온보딩 시
1. **시스템 전체 구조**: `CDSS System 상세설계.mdj` (StarUML)
2. **데이터 모델**: `/db/IntegrationERD.png` → 개별 ERD
3. **기능 이해**: `/usecase/UC1-Accounts-Auth.puml` (예시)
4. **흐름 파악**: `/sequence/1. ACCT/SD-ACCT-01.puml` (예시)
5. **구현 설계**: `/class/1. UC01 (ACCT)/uc01_01_class_main.puml`

### 특정 기능 개발 시
1. 해당 UC의 Usecase Diagram 확인
2. 관련 Sequence Diagram 확인
3. Class Diagram에서 구현 구조 확인
4. ERD에서 데이터베이스 스키마 확인

---

## 자주 묻는 질문 (FAQ)

### Q1. PlantUML 미리보기가 안 보여요
**A**: Java JRE가 설치되어 있는지 확인하세요. VSCode 설정에서 PlantUML 경로를 수동으로 지정할 수 있습니다.

### Q2. 클래스 다이어그램이 너무 복잡해요
**A**: `uc0X_01_class_main.puml` 대신 개별 레이어 파일(`_02_domain.puml` 등)을 열어보세요.

### Q3. Mermaid 파일이 렌더링되지 않아요
**A**: Mermaid Preview 확장 프로그램을 설치하거나, https://mermaid.live 에서 직접 확인하세요.

### Q4. 다이어그램을 수정하고 싶어요
**A**:
- `.puml` 파일: 텍스트 에디터로 직접 수정 가능
- `.mdj` 파일: StarUML에서 편집
- `.mmd` 파일: 텍스트 에디터 또는 Mermaid Live Editor

### Q5. 다이어그램을 문서에 삽입하고 싶어요
**A**:
- PNG: 일반 문서에 적합
- SVG: 확대/축소가 필요한 경우 (웹, 고품질 인쇄)
- PDF: 최종 보고서용

---

## 추가 리소스

### PlantUML 공식 문서
- https://plantuml.com/ko/

### Mermaid 공식 문서
- https://mermaid.js.org/

### StarUML 사용법
- https://docs.staruml.io/

---

## 프로젝트 유지보수

### 다이어그램 수정 시 체크리스트
- [ ] 관련된 3개 다이어그램(Usecase, Sequence, Class) 모두 일관성 확인
- [ ] 클래스 다이어그램 수정 시 메인 파일과 개별 파일 모두 확인
- [ ] ERD 수정 시 `.mmd` 파일 수정 후 PNG/SVG 재생성
- [ ] 변경사항을 문서에 반영

### 파일 백업 권장사항
- 정기적으로 전체 프로젝트 백업
- Git 버전 관리 사용 권장
- StarUML 파일(`.mdj`)은 병합이 어려우므로 충돌 주의

---

**문서 버전**: 1.0
**최종 수정일**: 2025-12-16
**작성자**: CDSS 개발팀
