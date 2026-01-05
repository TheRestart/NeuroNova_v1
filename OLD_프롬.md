# Claude AI 작업 프롬프트 (v2.0)
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
asdagr@DESKTOP-FL5CDM6:/mnt/d/1222/NeuroNova_v1$ cd NeuroNova_03_front_end_react/00_test_client
PORT=3001 npm start
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
