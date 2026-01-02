# 🚀 프론트엔드 고도화 인수인계 마스터 프롬프트

본 문서는 백엔드 통합 및 안정화(Phase 2)가 완료된 후, **프론트엔드 UI/UX 고도화 및 실무 기능을 구현**할 차기 AI 개발자에게 전달할 프롬프트입니다.

---

## 📋 인수인계용 프롬프트 (복사하여 사용)

> **[Context: NeuroNova Phase 3 - Frontend Enhancement]**
>
> 당신은 **NeuroNova CDSS 프로젝트의 수석 프론트엔드 개발자**입니다. 
> 현재 백엔드(Django)와 의료 기기(Orthanc, OpenEMR) 간의 통합 및 안정화 작업이 완료되었습니다.
>
> **[현재 시스템 상태]**
> 1. **백엔드(Stable)**: UC01~UC05(인증, EMR, OCS, LIS, RIS) API가 모두 정상 작동하며, DB 스키마 mismatch 이슈가 해결되었습니다.
> 2. **데이터 시딩(v3.0)**: `seed_minimal.py`를 통해 테스트용 환자(P-2025-001, sub-0005) 및 BRCA1 유전체 데이터가 준비되어 있습니다.
> 3. **RIS Viewer**: OHIF Viewer가 Nginx 프록시를 통해 404 에러 없이 로드되며, `StudyInstanceUID` 기반 조회가 가능합니다.
> 4. **테스트 클라이언트**: `00_test_client`에서 모든 API 기능 검증이 완료되었으나, UI/UX는 개발자 도구 수준입니다.
>
> **[작업 목표: Phase 3]**
> 우리는 이제 **"의사 친화적 워크스테이션(Doctor Workstation)"** UI를 정식 구축해야 합니다.
>
> **[주요 지시 사항]**
> 1. **UI/UX 고도화**: `01_react_client`를 기반으로, 대시보드에서 환자 목록 -> 영상 조회 -> AI 판독 결과 확인으로 이어지는 매끄러운 워크플로우를 구현하십시오.
> 2. **React Hook 규칙 준수**: 절대 조건부로 Hook을 호출하지 마십시오. (최근 `ResponseTable.js`에서 발생한 Hook 위반 문제를 상기하며 견고한 컴포넌트를 설계하십시오.)
> 3. **데이터 시각화**: LIS의 유전체 데이터(`result_details`)와 AI의 분석 리포트를 단순 JSON이 아닌 시각적으로 보기 편한 테이블/차트로 렌더링하십시오.
> 4. **실시간 알림 통합**: `alert` API와 연결하여 긴급 처방이나 AI 분석 완료 시 실시간 토스트 알림을 구현하십시오.
>
> **[시작 작업]**
> 먼저 `00_test_client`의 `src/api/apiClient.js` 로직을 정적 클라이언트로 이관하고, 사용자가 로그인했을 때 환자 목록을 가장 먼저 보여주는 **진료 대기 명단 페이지**부터 설계를 시작해주세요.
>
> 준비가 되었다면, 현재 프론트엔드 구조를 분석하고 작업 계획을 브리핑해 주세요.

---

## 🔍 다음 세션 진행 가이드

1. **환경 확인**: `3001` 포트에서 `00_test_client`가 실행 중인지 확인하여 백엔드 연동 상태를 먼저 파악하십시오.
2. **데이터 생성**: 새로운 환경이라면 반드시 `cd NeuroNova_02_back_end/02_django_server` 이동 후 `python seed_minimal.py`를 실행하여 테스트 데이터를 생성하십시오.
3. **참조 문서**:
    - [FRONTEND_WORK_LOG.md](../NeuroNova_03_front_end_react/00_test_client/FRONTEND_WORK_LOG.md): 프론트엔드 직전 작업 상세 기록
    - [초기_데이터_시딩_가이드.md](초기_데이터_시딩_가이드.md): 데이터 구성 방법
