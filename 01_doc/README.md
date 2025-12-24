# 01_doc - 프로젝트 문서 디렉토리

**최종 수정일**: 2025-12-24 (AI R&R Update)
**현재 상태**: Week 4 완료 - AI 코어 개발 준비 단계

---

## 📚 문서 구조

이 디렉토리는 NeuroNova CDSS 프로젝트의 모든 문서를 포함합니다.

### 🔥 읽는 순서 (권장) - Django Backend 개발자

#### ⚡ 최소 필수 (빠른 시작)
1. **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)** 🔥 - Claude AI 온보딩 (최우선)
2. **[17_프로젝트_RR_역할분담.md](17_프로젝트_RR_역할분담.md)** 🔥 - R&R 정의 및 역할 범위
3. **[LOG_작업이력.md](LOG_작업이력.md)** 🔥 - 현재 진행 상황 (Week 4 완료)
4. **[16_Write_Through_패턴_가이드.md](16_Write_Through_패턴_가이드.md)** 🔥 - Write-Through 패턴

#### 📚 전체 컨텍스트 (처음 참여하는 경우)
1. **[01_프로젝트_개요.md](01_프로젝트_개요.md)** 📌 - 프로젝트 전체 구조 (9개 UC 모듈)
2. 위 최소 필수 문서 (1~4번)
3. **[08_API_명세서.md](08_API_명세서.md)** - Django REST API 명세
4. **[09_데이터베이스_스키마.md](09_데이터베이스_스키마.md)** - DB 스키마

---

## 📁 문서 분류

### 🔥 Django Backend 개발 문서 (Week 4 신규)

| 번호 | 문서명 | 설명 | 중요도 |
|---|---|---|---|
| 17 | [프로젝트_RR_역할분담.md](17_프로젝트_RR_역할분담.md) | R&R 정의, 개발 전략 | 🔥 **필수** |
| 16 | [Write_Through_패턴_가이드.md](16_Write_Through_패턴_가이드.md) | Write-Through 패턴 가이드 | 🔥 **필수** |
| 19 | [CLAUDE_프롬프트_템플릿.md](19_CLAUDE_프롬프트_템플릿.md) | Claude AI 작업 프롬프트 템플릿 (Backend용) | ⭐ **권장** |

### 핵심 문서 (넘버링 01~12)

| 번호 | 문서명 | 설명 | Backend 관련 |
|---|---|---|---|
| 01 | [프로젝트_개요.md](01_프로젝트_개요.md) | 프로젝트 소개, 빠른 시작, Git 구조 | ⭐ 권장 |
| 02 | [세부_계획서.md](02_세부_계획서.md) | 인프라 구성 상세 | - |
| 03 | [개발_작업_순서.md](03_개발_작업_순서.md) | 4주 개발 계획 (Day 1~28) | - |
| 04 | [수정_지침서.md](04_수정_지침서.md) | 수정 요청 템플릿 | - |
| 05 | [기술스택_상세.md](05_기술스택_상세.md) | 기술 스택 설명 | - |
| 06 | [환경설정_가이드.md](06_환경설정_가이드.md) | 가상환경, 의존성, 개발 모드 | 📌 필수 |
| 07 | [일일_체크리스트.md](07_일일_체크리스트.md) | 일일 개발 체크리스트 | - |
| 08 | [API_명세서.md](08_API_명세서.md) | Django REST API 명세 | 🔥 필수 |
| 09 | [데이터베이스_스키마.md](09_데이터베이스_스키마.md) | DB 스키마, ERD | 🔥 필수 |
| 10 | [테스트_시나리오.md](10_테스트_시나리오.md) | 테스트 시나리오 | 📌 참고 |
| 11 | [배포_가이드.md](11_배포_가이드.md) | Docker 배포 가이드 | 📌 참고 |
| 12 | [보안_아키텍처_정책.md](12_보안_아키텍처_정책.md) | 보안 정책 | - |

### 참고 문서 (REF_ 접두사)

| 문서명 | 설명 |
|---|---|
| [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md) | Claude AI 온보딩 가이드 |
| [REF_PROJECT_STRUCTURE.md](REF_PROJECT_STRUCTURE.md) | 디렉토리 구조 설명 |
| [REF_GIT_SETUP_GUIDE.md](REF_GIT_SETUP_GUIDE.md) | Git 설정 가이드 |
| [REF_UML_사용법.md](REF_UML_사용법.md) | UML 다이어그램 사용법 |
| [REF_프롬프트.md](REF_프롬프트.md) | Claude AI 프롬프트 모음 |
| [REF_권한정의.txt](REF_권한정의.txt) | 7개 역할 권한 정의 |

### 작업 로그 (LOG_ 접두사)

| 문서명 | 설명 |
|---|---|
| [LOG_작업이력.md](LOG_작업이력.md) | 주차별 작업 완료 보고서 (Week 1~2) |

### 기타

| 문서명 | 설명 |
|---|---|
| [업무계획서.md](업무계획서.md) | 전체 업무 계획 (방대) |
| [00_문서정리계획.md](00_문서정리계획.md) | 문서 정리 계획서 |

### 보관 파일 (ARCHIVE)

중복되거나 통합된 문서들이 보관되어 있습니다.

---

## 🔍 문서 찾기

### 🔥 AI 코어 개발을 시작하려면
→ **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)** (온보딩 - 최우선)
→ **[17_프로젝트_RR_역할분담.md](17_프로젝트_RR_역할분담.md)** (R&R 이해)
→ **[18_AI_개발_가이드.md](18_AI_개발_가이드.md)** (코드 구현 - Flask + MONAI)
→ **[19_CLAUDE_프롬프트_템플릿.md](19_CLAUDE_프롬프트_템플릿.md)** (프롬프트 템플릿)

### 시작 가이드가 필요하면
→ **[01_프로젝트_개요.md](01_프로젝트_개요.md)**

### 개발 환경 설정이 필요하면
→ **[06_환경설정_가이드.md](06_환경설정_가이드.md)** (Django)
→ **[../05_ai_core/README.md](../05_ai_core/README.md)** (AI 코어)

### API 명세가 필요하면
→ **[08_API_명세서.md](08_API_명세서.md)** (통합 시 참조)

### 작업 진행 상황을 확인하려면
→ **[LOG_작업이력.md](LOG_작업이력.md)**

### Claude AI가 프로젝트를 이해하려면
→ **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)**

### Interface Specification 작성이 필요하면
→ **[../05_ai_core/interface_spec_template.md](../05_ai_core/interface_spec_template.md)**

---

**문서 버전**: 3.0 (AI R&R Update)
**정리 완료일**: 2025-12-24
**현재 단계**: AI 코어 개발 Phase (Week 5-12)
