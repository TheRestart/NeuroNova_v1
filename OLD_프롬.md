# Claude AI 작업 프롬프트 (v2.0)

> **목적**: 이 문서는 Claude AI에게 작업을 지시할 때 사용하는 **최적화된 프롬프트 템플릿** 모음입니다.
> **최신화**: 2026-01-02 (문서 경량화 및 React 통합 반영)


프롬프트 제목: [NeuroNova 아키텍처 문서 정밀 점검 및 시각화]

1. 역할: 너는 숙련된 소프트웨어 아키텍트이자 기술 문서 작성 전문가야. 
2. 작업 목표: 제공된 문서의 기술적 오류를 점검하고, 전체 서비스 구조를 한눈에 파악할 수 있도록 재정리해줘. 
3. 정검 대상 : doc의 문서 전부 
4. 점검 항목:
서비스 간(Django, FastAPI, Celery, Orthanc) 데이터 흐름의 모순 확인.
HTJ2K 변환 및 WASM 디코딩 과정의 기술적 누락 점검.
MSA 설계 원칙에 어긋나는 의존성 유무 확인. 4. 출력 형식:
오류 리스트: 발견된 오류나 개선 제안을 번호 순으로 한 줄씩 정리.
구조 요약: 'A -> B (내용) -> C' 형태의 텍스트 흐름도 사용.
시각화: 흐름을 명확히 하기 위해 Mermaid graph TD 코드를 포함해줘. 5. 제약 사항: 전문 용어는 유지하되, 전체적인 구조는 비전공자도 이해할 수 있도록 명확한 화살표와 레이블을 사용할 것.

===
NeuroNova_03_front_end_react\00_test_client
기능에 에러가 있다. 

장고에서 환자와 orthance 다이콤 데이터의 메핑 기능이 있어야 
장고에서 orthance 호출도 되고 FHIR 데이터 매핑연동이 될텐데 
맵핑 기능을 구현하라 

그외 에러사항을 찾고 보고하라 
===

@01_doc/REF_CLAUDE_ONBOARDING_QUICK.md 
@01_doc/REF_프롬프트_프론트엔드_인수인계.md
@작업_계획_요약.md

위 3개 문서를 읽고 맥락을 이해후 프론트엔드 고도화 작업을 즉시 시작








===
임시 배포전 정검 문서 : 
01_doc\초기_데이터_시딩_가이드.md
01_doc\12_GCP_배포_가이드.md (.env 같이 따로 옮겨야하는 파일 정리 필요)
NeuroNova_03_front_end_react\00_test_client\사용방법_설명문서.md
docker-compose.dev.yml
===
배포전에 깔끔하게 불필요한 파일을 정리하라



NeuroNova_03_front_end_react\00_test_client\FRONTEND_WORK_LOG.md
NeuroNova_03_front_end_react\00_test_client\LOG_테스트클라이언트_정밀점검_20260102.md

위 2개 문서를 보니 아직 개선해야하는 문제가 많아보인다. 
특히 'http://localhost:3001/monitoring' 은 심각하다

---

## 🚀 1. 빠른 온보딩 (Quick Start)

토큰 절약을 위해 가장 핵심적인 문서만 읽고 즉시 작업을 시작할 때 사용합니다.

**[프롬프트]:**
```text
@01_doc/REF_CLAUDE_ONBOARDING_QUICK.md @01_doc/LOG_작업이력.md @작업_계획_요약.md

위 3개 파일을 읽고 현재 프로젝트 상태(Phase 2 완료, React 통합)를 파악한 뒤,
[작업_계획_요약.md]의 '다음 단계'에 있는 [작업명]을 수행하기 위한 계획을 수립해줘.
```

---

## 🛠️ 2. 상세 문제 해결 (Deep Dive)

복잡한 문제나 아키텍처 이해가 필요할 때 사용합니다.

**[프롬프트]:**
```text
@01_doc/REF_CLAUDE_CONTEXT.md @01_doc/LOG_작업이력.md @01_doc/OLD_오류정리_antigra_1230.md

위 문서들을 참조하여 현재 발생한 [오류 내용]에 대한 원인을 분석하고,
기존 아키텍처 규칙(Layered Architecture)을 준수하며 해결 방안을 제시해줘.
```

---

## 💻 3. 실행 환경 정보 (Context)

Claude가 실행 명령어를 제안할 때 참조해야 할 환경 설정입니다.

```json
{
  "environment": {
    "os": "Windows 11 + WSL Ubuntu-22.04 LTS",
    "frontend": {
      "stack": "React 18 + OHIF Viewer v3",
      "path": "NeuroNova_03_front_end_react/00_test_client",
      "command": "PORT=3001 npm start",
      "url": "http://localhost:3001"
    },
    "backend": {
      "stack": "Django 4.2 + DRF",
      "path": "NeuroNova_02_back_end/02_django_server",
      "command": "python manage.py runserver",
      "url": "http://localhost:8000/api (Direct) or http://localhost/api (Nginx)"
    }
  }
}
```

---

## 📝 4. 문서 업데이트 요청

작업 완료 후 문서를 현행화할 때 사용합니다.

**[프롬프트]:**
```text
작업이 완료되었으니 문서를 업데이트해줘.

1. [LOG_작업이력.md]: 오늘 날짜로 작업 내용(해결된 버그, 구현 기능) 추가
2. [작업_계획_요약.md]: 완료된 항목 체크([x]) 및 다음 할 일 갱신
3. (필요 시) [01_doc/REF_CLAUDE_ONBOARDING_QUICK.md]: 변경된 아키텍처나 주요 정책 반영
```

---

## ⚡ 5. 작업 원칙 (System Prompts)

Claude가 코드를 작성할 때 항상 준수해야 할 규칙입니다.

1. **가독성 & 재사용성**: "코드는 한 번 작성되지만 수백 번 읽힌다."
2. **이모지 금지**: 코드 파일(.py, .js) 내부에는 절대 이모지를 사용하지 않는다. (인코딩 오류 방지)
3. **절대 경로 사용**: 파일 경로를 언급할 때는 항상 프로젝트 루트 기준 상대 경로 또는 절대 경로를 사용한다.
4. **적극적 질문**: 모호한 요구사항은 가정하지 말고 반드시 먼저 질문한다.
