

지금부터 능동적으로 문제를 해결하고
4개 문서를 업데이트 하시오
01_doc/REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md, 작업_계획_요약.md, OLD_오류정리_antigra_1230.md


# [작업 지시서] NeuroNova React 클라이언트 정상화 및 고도화

## 1. 개요

* **대상**: `NeuroNova_03_front_end_react\00_test_client` (React 테스트 클라이언트)
* **목표**: 타겟 디렉토리 내 발생 오류를 분석 및 수정하여, 최종적으로 백엔드와 정상 통신이 가능한 **'정상 작동'** 상태로 복구하고, **전문적인 화면의 구성으로 부가적인 기능을 배치**한다.

## 2. 작업 원칙 (Constraints)

* **세션 관리**: 작업 도중 토큰 제한으로 세션이 종료될 경우, '이어서 작업하시오'라는 명령에 따라 중단된 지점부터 즉시 재개한다.
* **순차적 진행**: 한 번에 모든 파일을 수정하지 않고, 핵심 파일부터 순차적으로 수정한다.
* **문서 업데이트**: 각 단계 완료 시 `LOG_작업이력.md`와 `작업_계획_요약.md`를 최신 상태로 유지한다.

## 3. 단계별 프로세스 (Step-by-Step)

### 1단계: [진단] (Diagnosis)

* **목표**: 현재 코드와 오류 로그를 바탕으로 원인을 분석한다.
* **액션**: 해결을 위한 단계별 계획을 수립하여 먼저 출력한다.
* **주의**: 이 단계에서는 아직 코드를 작성하거나 수정하지 않는다.

### 2단계: [실행] (Execution)

* **목표**: 승인된 계획에 따라 코드를 수정하고 기능을 고도화한다.
* **액션**:
1. 핵심 오류 수정 (기능 정상화)
2. 전문적인 UI 레이아웃 구성 및 부가 기능 구현 (화면 고도화)



### 3단계: [기록] (Documentation)

* **목표**: 작업 진행 상황을 문서화한다.
* **액션**: 각 단계 종료 시 다음 문서를 업데이트하고 코드 블록으로 출력한다.
* **필수 업데이트**: `LOG_작업이력.md`, `작업_계획_요약.md`
* **필요 시 업데이트**: `01_doc/REF_CLAUDE_ONBOARDING_QUICK.md`, `OLD_오류정리_antigra_1230.md`



---

## 4. 실행 환경 및 상세 지침 (2026 Context)

**사전 작업**: `01_doc/REF_CLAUDE_ONBOARDING_QUICK.md`와 `01_doc\LOG_작업이력.md`를 읽고 현재 프로젝트 상황을 파악한다.

### 환경 설정 (Environment)

```json
{
  "environment": {
    "os": "Windows 11 (WSL Ubuntu-22.04 LTS)",
    "frontend": "React (Port 3000 recommended)",
    "backend": "Django (Port 8000), Nginx (Port 80)",
    "command": "npm run dev (must be executed in Ubuntu-22.04 LTS)"
  }
}

```

### 상세 작업 지시 (Instructions)

```json
{
  "tasks": [
    "WSL (Ubuntu-22.04) 환경에서 'npm run dev'를 사용하여 React 개발 서버를 구동하십시오.",
    "다음 순서로 작업을 진행하십시오:",
    "1. [진단]: 현재 'CDSS API 테스트 클라이언트'의 각 UC 메뉴(UC01~UC09)를 순회하며 기능 작동 여부를 전수 점검하십시오.",
    "2. [분석]: 브라우저 콘솔 및 네트워크 탭을 분석하여 4xx/5xx 에러나 의도치 않은 동작을 파악하십시오.",
    "3. [수정]: 발견된 오류의 원인을 분석하고 'step-by-step' 계획을 수립하여 코드를 수정하십시오.",
    "4. [검증]: 수정 후 재테스트를 통해 백엔드와의 정상 통신을 확인하십시오.",
    "5. [고도화]: 기능 정상화가 완료되면, 전문적인 화면 구성(Dashboard Layout 등)을 적용하고 필요한 부가 기능을 배치하여 UI/UX를 개선하십시오."
  ],
  "constraints": [
    "토큰 제한으로 세션 종료 시 '이어서 작업하시오'라고 입력하면 중단된 지점부터 즉시 재개하십시오.",
    "문서 업데이트: 각 단계 완료 시 'LOG_작업이력.md'와 '작업_계획_요약.md'를 최신 상태로 유지하십시오."
  ]
}

```



---

## 4. 실행 환경 및 추가 지침 (2026 Context)

**사전 작업**: `01_doc/REF_CLAUDE_ONBOARDING_QUICK.md`와 `01_doc\LOG_작업이력.md`를 읽고 현재 프로젝트 상황을 파악한다.

### 환경 설정 (Environment)

```json
{
  "environment": {
    "os": "Windows 11 (WSL Ubuntu-22.04 LTS)",
    "frontend": "React (Port 3000 recommended)",
    "backend": "Django (Port 8000), Nginx (Port 80)",
    "command": "npm run dev (must be executed in Ubuntu-22.04 LTS)"
  }
}

```

### 상세 작업 지시 (Instructions)

```json
{
  "tasks": [
    "WSL (Ubuntu-22.04) 환경에서 'npm run dev'를 사용하여 React 개발 서버를 구동하십시오.",
    "다음 순서로 작업을 진행하십시오:",
    "1. [진단]: 현재 'CDSS API 테스트 클라이언트'의 각 UC 메뉴(UC01~UC09)를 순회하며 기능 작동 여부를 전수 점검하십시오.",
    "2. [분석]: 브라우저 콘솔 및 네트워크 탭을 분석하여 4xx/5xx 에러나 의도치 않은 동작을 파악하십시오.",
    "3. [수정]: 발견된 오류에 대해 원인을 분석하고 'step-by-step' 계획을 수립한 후 코드를 수정하십시오.",
    "4. [검증]: 수정 후 재테스트를 통해 정상 작동을 확인하고 기록하십시오."
  ],
  "constraints": [
    "토큰 제한으로 세션 종료 시 '이어서 작업하시오'라고 입력하면 중단된 지점부터 즉시 재개하십시오.",
    "문서 업데이트: 각 단계 완료 시 'LOG_작업이력.md'와 '작업_계획_요약.md'를 최신 상태로 유지하십시오."
  ]
}

```





===


=== Claude AI 온보딩 방법 

🎯 **빠른 온보딩** (권장 - 토큰 80% 절약):
1. **REF_CLAUDE_ONBOARDING_QUICK.md** 읽기 (5분) ← 핵심만 요약
2. **LOG_작업이력.md** 읽기 (현재 진행 상황)
3. 필요 시 개별 문서 참조

📚 **상세 온보딩** (필요 시):
1. **REF_CLAUDE_CONTEXT.md** 전체 읽기 (1000줄+) ← 모든 상세 내용
2. **LOG_작업이력.md** 읽기
3. 개별 UC 분석 (필요 시)

---

=== Claude에게 작업 시작 요청 시 프롬프트 예시:

**빠른 온보딩**:
"01_doc/REF_CLAUDE_ONBOARDING_QUICK.md와 01_doc\LOG_작업이력.md를 읽고 현재 프로젝트 상황을 파악해줘"

01_doc/REF_CLAUDE_ONBOARDING_QUICK.md와 01_doc\LOG_작업이력.md를 읽고 현재 프로젝트 상황을 파악후



orthance, ohir 을 중심으로 
실제 서비스가 어떻게 동작하는지 설명하라




**상세 온보딩**:
            "01_doc/REF_CLAUDE_CONTEXT.md와 LOG_작업이력.md를 읽고 전체 시스템을 이해해줘"

**문서 업데이트 요청**:
(빠르게)
핵심 2개 문서를 업데이트 하시오 
01_doc/REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md


현제 문제를 정리하고 
4개 문서를 업데이트 하시오 
01_doc/REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md, 
작업_계획_요약.md, OLD_오류정리_antigra_1230.md






(정밀)
핵심 3개 문서를 업데이트 하시오 
01_doc/REF_CLAUDE_CONTEXT.md, 01_doc/REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md



+ 모듈 설치시 requirement.txt 업데이트 필요
+ npm run dev 를 실행할때는 Ubuntu-22.04 LTS를 사용하시오

==프롬 새로 작성 
코드 작성시 가장 고려해야하는 것은 코드의 '가독성'과 '재사용성'이다. 



==
'오류정리_antigra_1230.md'를 생성하고 

지금부터 
오류가 발생할때마다. 
발생한 오류들을 300자 내외로 정리해서 
업데이트하시오 
