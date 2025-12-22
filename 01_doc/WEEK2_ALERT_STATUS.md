# Week 2 중간 점검 보고서: Frontend 초기화 및 Alert 모듈

**작성일**: 2025-12-22
**작성자**: Claude AI
**상태**: 진행 중

---

## ✅ 완료 항목

### 1. Alert (UC7) 모듈 구현 (Backend)
- `alert` 앱 생성 및 모델 정의
- **Alert 모델**:
    - 사용자(`user`)와 1:N 관계
    - 심각도(`severity`) 4단계: INFO, WARNING, CRITICAL, CODE_BLUE
    - 읽음 상태(`is_read`) 추적
- **API 구현**:
    - `GET /api/alert/`: 내 알림 목록 조회
    - `POST /api/alert/{id}/mark_as_read/`: 알림 읽음 처리
- **연동 설정**:
    - `cdss_backend/urls.py`에 라우팅 등록 완료
    - 데이터베이스 마이그레이션 적용 완료

### 2. Frontend 프로젝트 초기화
- React + TypeScript 환경 구축 (WSL Ubuntu-22.04 LTS 사용)
- **설치된 패키지**:
    - `axios`: API 통신
    - `react-router-dom`: 라우팅
    - `zustand`: 상태 관리
    - `tailwindcss`, `postcss`, `autoprefixer`: 스타일링
    - `@headlessui/react`, `@heroicons/react`: UI 컴포넌트
- **Tailwind CSS 구성**:
    - 역할별 테마 색상 정의 (Admin, Doctor, Etc.)
    - `src/index.css`에 Tailwind 지시어 추가

---

## 🚧 진행 중인 작업

### 1. Frontend 구조 잡기
- 인증 서비스 (`AuthService`) 구현
- 공통 컴포넌트 (레이아웃, 헤더, 사이드바)
- 페이지별 라우팅 설정

### 2. Alert 연동
- WebSocket을 통한 실시간 알림 (Week 3 예정이나 준비 작업 필요)

---

## ⚠️ 특이 사항 및 해결 내용

1. **WSL 환경 사용**: 
   - `npm` 및 `npx` 명령어가 PowerShell에서 작동하지 않아 WSL(Ubuntu-22.04 LTS) 환경으로 전환하여 실행했습니다.
   - 프로젝트 디렉토리는 Windows 파일 시스템(`c:\Users\302-28\Downloads\UML`)을 WSL 마운트(`/mnt/c/...`)를 통해 접근하여 공유합니다.

2. **Tailwind 초기화**:
   - `npx tailwindcss init` 명령어 오류로 인해 설정 파일(`tailwind.config.js`, `postcss.config.js`)을 직접 생성하여 설정했습니다.

---

## 📅 향후 계획

1. **Frontend 로그인 페이지 구현**:
   - `Login.tsx` 컴포넌트 작성
   - 백엔드 (`/api/acct/login/`) 연동

2. **Dashboard 레이아웃**:
   - 역할(Role)에 따른 동적 메뉴 구성 구현

보고서 작성 완료.
