지금부터 능동적으로 문제를 해결하라.
아래 4개 문서를 단일 프로젝트 기준으로 통합 분석하고,
현재 상태에 맞게 모든 문서를 업데이트하라.

대상 문서:
- 01_doc/REF_CLAUDE_ONBOARDING_QUICK.md
- LOG_작업이력.md
- 작업_계획_요약.md
- OLD_오류정리_antigra_1230.md

===
[작업 지시서] NeuroNova React 클라이언트 정상화 및 고도화

대상 디렉토리 : 
NeuroNova_03_front_end_react/00_test_client


목표 : 
React 테스트 클라이언트의 오류를 분석·수정하여
백엔드(Django)와 정상 통신 가능한 상태로 복구
이후 전문적인 UI 레이아웃(Dashboard 등) 적용 및 기능 고도화

작업 원칙 (Constraints) : 
토큰 제한으로 세션이 종료될 경우
→ 사용자가 **「이어서 작업하시오」**라고 입력하면 중단 지점부터 즉시 재개
한 번에 모든 파일을 수정하지 말고 핵심 파일부터 순차적 진행
각 단계 종료 시 문서 상태를 반드시 최신으로 유지

필수: LOG_작업이력.md, 작업_계획_요약.md
필요 시: REF_CLAUDE_ONBOARDING_QUICK.md, OLD_오류정리_antigra_1230.md

단계별 프로세스 : 
프론트 개발 참고 : 01_doc, 
01_doc\21_락킹_멱등성_개발_가이드.md

1단계: 진단 (Diagnosis)
UC01 ~ UC09 전체 기능 점검
브라우저 Console / Network 탭 분석
이 단계에서는 코드 수정 금지
해결을 위한 step-by-step 계획만 먼저 출력

2단계: 실행 (Execution)
승인된 계획에 따라 코드 수정
핵심 오류 해결 → 기능 정상화
이후 UI/UX 고도화 (Dashboard Layout 등)

3단계: 기록 (Documentation)
각 단계 종료 시 작업 내용을 문서화
변경 사항을 문서에 반영하고 전체 내용을 출력
실행 환경 (2026 기준)
{
  "environment": {
    "os": "Windows 11 + WSL Ubuntu-22.04 LTS",
    "frontend": "React (Port 3000)",
    "backend": "Django (Port 8000), Nginx (Port 80)",
    "command": "npm run dev (Ubuntu-22.04 LTS에서 실행)"
  }
}

상세 작업 지침
{
  "tasks": [
    "WSL(Ubuntu-22.04) 환경에서 npm run dev로 React 서버 실행",
    "UC01~UC09 기능 전수 테스트",
    "4xx/5xx 오류 및 비정상 동작 분석",
    "오류 원인별 step-by-step 계획 수립 후 수정",
    "수정 후 재검증",
    "기능 안정화 이후 UI/UX 고도화"
  ]
}



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








**상세 온보딩**:
            "01_doc/REF_CLAUDE_CONTEXT.md와 LOG_작업이력.md를 읽고 전체 시스템을 이해해줘"

**문서 업데이트 요청**:
(빠르게)
핵심 2개 문서를 업데이트 하시오 
01_doc/REF_CLAUDE_ONBOARDING_QUICK.md, LOG_작업이력.md


현제 문제를 정리하고 
4개 문서를 업데이트 하시오 
필수: LOG_작업이력.md, 작업_계획_요약.md
필요 시: REF_CLAUDE_ONBOARDING_QUICK.md, OLD_오류정리_antigra_1230.md





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
