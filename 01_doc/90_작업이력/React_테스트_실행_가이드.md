# React 테스트 클라이언트 실행 가이드

**작성일**: 2025-12-31
**작성자**: Claude (NeuroNova 배포 준비)

---

## 🎯 목적

배포 전 Django 백엔드 API를 검증하기 위한 **2가지 테스트 방법** 제공:

1. **방법 1**: 브라우저 전용 HTML 테스트 페이지 (즉시 실행 가능)
2. **방법 2**: React 개발 서버 (WSL Ubuntu-22.04 필요)

---

## ⚡ 방법 1: HTML API 테스트 페이지 (권장)

### 장점
- ✅ **즉시 실행 가능** (Node.js 불필요)
- ✅ **모든 UC01-UC09 API 테스트** 가능
- ✅ **시각적 결과** 확인
- ✅ **JWT 토큰 자동 관리**

### 실행 방법

#### 1단계: 파일 열기
```bash
# Windows 탐색기에서 파일 열기
d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client\public\api_test.html
```

**또는**

브라우저에서 직접 접속:
```
file:///d:/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client/public/api_test.html
```

#### 2단계: API 테스트 순서

1. **"로그인 테스트"** 버튼 클릭
   - 계정: `doctor` / `doctor123`
   - JWT Access/Refresh 토큰 발급 확인

2. **각 UC별 테스트 버튼 클릭**
   - UC02: 환자 목록 조회
   - UC03: 오더 목록/생성
   - UC04: 검사 목록/결과
   - UC05: 영상 검사 목록
   - UC06: AI Jobs (500 에러 예상 - 정상)
   - UC09: 감사 로그

3. **결과 확인**
   - 초록색 테두리: 성공 (200 OK)
   - 빨간색 테두리: 에러
   - JSON 응답 데이터 실시간 표시

---

## 🐧 방법 2: React 개발 서버 실행

### 사전 요구사항
- WSL Ubuntu-22.04 LTS
- Node.js v20.19.6
- npm 10.8.2

### 실행 방법

#### 1단계: WSL Ubuntu-22.04 터미널 열기

**PowerShell 또는 CMD에서**:
```powershell
wsl -d Ubuntu-22.04
```

**또는 Windows Terminal에서**:
- 새 탭 → "Ubuntu-22.04" 선택

#### 2단계: 프로젝트 디렉토리 이동
```bash
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client
```

#### 3단계: 환경 확인
```bash
# Node.js 버전 확인 (v20.19.6 이상)
node --version

# npm 버전 확인 (10.8.2 이상)
npm --version

# node_modules 존재 확인
ls -la node_modules | head -5
```

#### 4단계: React 개발 서버 실행
```bash
# PORT 3001로 실행 (기본 3000 포트와 충돌 방지)
PORT=3001 npm start

# 또는
npm run dev
```

#### 5단계: 브라우저 접속
```
http://localhost:3001
```

#### 6단계: 자동 로그인 확인

`.env.local` 설정에 따라:
```bash
REACT_APP_DEV_AUTO_LOGIN=true
REACT_APP_DEV_MOCK_USER=doctor
```

**자동으로 `doctor` 계정으로 로그인됨** → 바로 서비스 테스트 가능

---

## 📊 테스트 체크리스트

### UC01: 인증 (Authentication)
- [ ] 로그인 성공 (doctor/doctor123)
- [ ] JWT Access Token 발급 확인
- [ ] JWT Refresh Token 발급 확인
- [ ] 사용자 정보 반환 확인 (role: doctor)

### UC02: EMR (Electronic Medical Records)
- [ ] 환자 목록 조회 (5명: P20250001~P20250005)
- [ ] 환자 상세 조회 (P20250001)
- [ ] 환자 데이터 정합성 확인

### UC03: OCS (Order Communication System)
- [ ] 오더 목록 조회
- [ ] 신규 오더 생성
- [ ] 오더 상태 확인

### UC04: LIS (Laboratory Information System)
- [ ] 검사 항목 목록 조회
- [ ] 검사 결과 조회
- [ ] 검사 데이터 정합성 확인

### UC05: RIS (Radiology Information System)
- [ ] 영상 검사 목록 조회
- [ ] DICOMweb 연결 테스트
- [ ] Orthanc PACS 통신 확인

### UC06: AI Jobs (알려진 이슈)
- [ ] **500 에러 발생 확인** (예상됨)
- [ ] 에러 메시지: "Invalid field name(s) given in select_related"
- [ ] 배포 범위 외 (FastAPI 팀 담당)

### UC09: 감사 로그 (Audit Log)
- [ ] 감사 로그 목록 조회
- [ ] 로그 데이터 확인

---

## 🔧 문제 해결

### 문제 1: "npm: command not found"

**원인**: Git Bash에서 실행했거나 Node.js 미설치

**해결**:
```bash
# WSL Ubuntu-22.04에서 실행
wsl -d Ubuntu-22.04

# Node.js 설치 확인
node --version
```

### 문제 2: "EADDRINUSE: address already in use"

**원인**: 포트 3001이 이미 사용 중

**해결**:
```bash
# 포트 사용 중인 프로세스 종료
lsof -ti:3001 | xargs kill -9

# 또는 다른 포트 사용
PORT=3002 npm start
```

### 문제 3: API 연결 실패 (Network Error)

**원인**: Django 컨테이너 미실행 또는 Nginx 중지

**해결**:
```bash
# Docker 컨테이너 상태 확인
docker ps --format "table {{.Names}}\t{{.Status}}"

# Django API 직접 테스트
curl http://localhost/api/acct/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor","password":"doctor123"}'
```

### 문제 4: 자동 로그인 안됨

**원인**: `.env.local` 설정 오류

**해결**:
```bash
# .env.local 확인
cat /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client/.env.local

# 필수 설정:
# REACT_APP_DEV_AUTO_LOGIN=true
# REACT_APP_DEV_MOCK_USER=doctor
# REACT_APP_API_URL=http://localhost/api
```

---

## 📝 테스트 결과 기록

### 테스트 일시
- **날짜**: _____________
- **시간**: _____________
- **테스터**: _____________

### 테스트 환경
- **OS**: Windows 11 / WSL Ubuntu-22.04
- **브라우저**: Chrome / Firefox / Edge
- **Node.js**: v_____________ (React 서버 사용 시)

### 테스트 결과 요약

| UC | API 엔드포인트 | 상태 | 비고 |
|----|---------------|------|------|
| UC01 | /api/acct/login/ | ⬜ PASS / ⬜ FAIL |  |
| UC02 | /api/emr/patients/ | ⬜ PASS / ⬜ FAIL |  |
| UC03 | /api/ocs/orders/ | ⬜ PASS / ⬜ FAIL |  |
| UC04 | /api/lis/lab-tests/ | ⬜ PASS / ⬜ FAIL |  |
| UC05 | /api/ris/studies/ | ⬜ PASS / ⬜ FAIL |  |
| UC06 | /api/ai/jobs/ | ⬜ 500 ERROR (예상) |  |
| UC09 | /api/audit/logs/ | ⬜ PASS / ⬜ FAIL |  |

### 발견된 이슈

1. **이슈 1**: _______________________________________________
   - 재현 방법: _______________________________________________
   - 에러 메시지: _______________________________________________

2. **이슈 2**: _______________________________________________
   - 재현 방법: _______________________________________________
   - 에러 메시지: _______________________________________________

---

## ✅ 배포 전 최종 확인

### 인프라 상태
- [ ] Docker 14개 컨테이너 실행 중
- [ ] Nginx (포트 80) 정상 응답
- [ ] Django (내부 8000) healthy 상태
- [ ] MySQL 연결 정상

### API 테스트
- [ ] UC01-UC05 모두 PASS (200 OK)
- [ ] UC09 PASS (200 OK)
- [ ] UC06 500 Error 확인 (배포 범위 외)

### 샘플 데이터
- [ ] 사용자 13명 (7 roles + 6 patients)
- [ ] 환자 5명 (P20250001~P20250005)
- [ ] 검사 결과 데이터 확인

### 문서 업데이트
- [ ] LOG_작업이력.md 업데이트
- [ ] 36_다음_작업_계획.md 업데이트
- [ ] 배포전_테스트_결과_1231.md 업데이트
- [ ] OLD_오류정리_antigra_1230.md 업데이트

---

## 🚀 다음 단계

### 즉시 실행
1. **HTML API 테스트 페이지 열기** (권장)
   - 파일: `d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client\public\api_test.html`
   - 브라우저에서 열기

2. **모든 API 테스트 수행**
   - 로그인 → UC02~UC05, UC09 순서대로 테스트

3. **테스트 결과 기록**
   - 위 체크리스트 작성

### 선택 사항
- React 개발 서버 실행 (WSL Ubuntu-22.04)
- 브라우저 UI 테스트

### GCP 배포 준비 (2일 후)
- 참조 문서: [배포_빠른_시작_가이드.md](배포_빠른_시작_가이드.md)

---

## 📌 참고 문서

- [배포전_테스트_결과_1231.md](배포전_테스트_결과_1231.md) - 이전 테스트 결과
- [배포_빠른_시작_가이드.md](배포_빠른_시작_가이드.md) - GCP VM 배포 가이드
- [README_배포전_작업_완료.md](README_배포전_작업_완료.md) - 작업 완료 요약
- [REF_CLAUDE_ONBOARDING_QUICK.md](../REF_CLAUDE_ONBOARDING_QUICK.md) - 시스템 참조

---

**문의사항**: 추가 지원이 필요하면 작업 이력 문서 참조 또는 새로운 이슈 생성
