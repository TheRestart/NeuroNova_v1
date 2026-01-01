# CDSS 오류 정리 및 해결 내역 (2025-12-30)

이 문서는 개발 과정에서 발생한 주요 오류와 해결 방안을 300자 내외로 정리한 기록입니다.

---

### 1. 포트 충돌 (React Test Client vs OHIF)
**현상:** 리액트 테스트 클라이언트와 OHIF Viewer가 모두 3000 포트를 사용하여 서버 실행 시 충돌 발생.
**원인:** 두 프론트엔드 프로젝트의 기본 포트 설정이 동일함.
**해결:** 테스트 클라이언트의 `package.json`에서 `PORT=3001`을 명시하여 포트를 분리함. 이제 테스트 클라이언트는 3001 포트에서 원활히 동작함.

### 2. WSL -> Windows 호스트 프록시 연결 실패
**현상:** WSL 환경에서 `npm start` 실행 시 `localhost:8000`으로의 API 프록시가 `ECONNREFUSED` 에러로 실패.
**원인:** WSL 내부에서 `localhost`는 WSL 자신을 가리키며, Windows 호스트의 Django 서버에 도달하지 못함.
**해결:** Windows 호스트의 WSL 어댑터 IP(`172.29.64.1`)를 확인하고, `package.json`의 proxy 설정을 해당 IP로 변경하여 해결함. (이후 로컬호스트로 해결됨)

### 3. API 서비스 명칭 불일치 (Frontend vs Backend)
**현상:** 테스트 클라이언트의 각 UC 페이지에서 API 호출 시 함수가 존재하지 않는다는 런타임 에러 발생.
**원인:** `apiClient.js`의 서비스 함수명(예: `getRadiologyOrders`)과 각 페이지의 호출명(예: `getImagingStudies`)이 일치하지 않음.
**해결:** `apiClient.js`의 최신 정의에 맞춰 모든 UC 테스트 페이지(UC01~UC09)의 호출부와 파라미터를 전수 수정함.

### 4. Django 서버 외부 접속 거부
**현상:** 프록시 IP 설정 후에도 WSL에서 Django 서버로의 연결이 여전히 거부됨.
**원인:** Django `runserver`가 기본값인 `127.0.0.1`로 실행되어 외부(WSL 포함) 인터페이스의 루프백 요청을 수락하지 않음.
**해결:** 서버 실행 시 `0.0.0.0:8000`을 명시하여 모든 인터페이스에서 접속 가능하도록 변경함.

### 5. API 엔드포인트 경로 불일치 (404 Not Found)
**현상:** UC03 OCS와 UC05 RIS에서 처방/오더 관련 API 호출 시 404 에러 발생.
**원인:** 백엔드 라우터 설정과 프론트엔드 `apiClient.js`에 정의된 경로가 서로 다름 (예: `radiology-orders` vs `orders`).
**해결:** 백엔드 `urls.py`를 전수 조사하여 OCS 처방은 `emr/orders/`로, RIS 오더는 `ris/orders/`로 `apiClient.js`의 경로를 수정하여 해결함.

---

## 2025-12-30 정적 분석 및 개선 작업 (서버 미기동)

### 6. 환경 변수 검증 로직 부재 (잠재적 프로덕션 이슈)
**현상:** settings.py에서 환경 변수를 os.getenv()로 읽어오지만, 프로덕션 환경에서 필수 변수 누락 시 런타임에 문제 발생 가능.
**원인:** 필수 환경 변수(SECRET_KEY, DB 연결 정보 등)에 대한 검증 로직이 없어 서버 기동 후에야 문제 발견.
**해결:** settings.py에 require_env() 함수를 추가하여 DEBUG=False(프로덕션)일 때 필수 환경 변수 미설정 시 즉시 EnvironmentError 발생하도록 개선. .env.example도 업데이트하여 필수 변수를 명시함.

### 7. 마스터 데이터 시딩 스크립트 통합 작업 완료
**현상:** 진단/약물/검사 마스터 데이터를 각각 별도로 관리하여 데이터 업로드 시 여러 스크립트를 순차 실행해야 하는 번거로움.
**원인:** 기존에는 add_diagnosis_data.py만 있고 약물/검사 마스터 데이터는 없었음.
**해결:** data/ 디렉토리에 medication_master.json(30개), lab_test_master.json(50개) 생성. ocs/management/commands/seed_master_data.py를 작성하여 `python manage.py seed_master_data` 한 번으로 모든 마스터 데이터를 시딩할 수 있도록 통합함. --diagnosis-only, --medication-only, --labtest-only, --force 옵션 지원.

---

## 2025-12-31 트러블슈팅

### 8. create_test_users.py 비밀번호 해싱 버그 (치명적)
**현상:** `python manage.py create_test_users`로 생성된 계정으로 로그인 불가 (401 에러).
**원인:** `create_user` 함수 호출 시 비밀번호 인자가 누락되어, Django가 사용할 수 없는 비밀번호로 설정함.
**해결:** `create_user`에 `password` 인자를 명시적으로 전달하도록 수정하고, 특수문자 처리를 위해 raw string을 사용하려 했으나, 최종적으로 특수문자를 제거한 단순 비밀번호(`admin123`)로 변경하여 문제를 원천 해결함.
- **데이터 초기화**: `python manage.py create_test_users`를 재실행하여 백엔드 데이터를 갱신했습니다.

### 10. API URL 경로 불일치 (Login 404 Not Found)
**현상:** 로그인 시도 시 `POST http://localhost:8000/acct/login/` 요청이 404 (Not Found) 반환.
**원인:** 백엔드 API는 `/api/` 접두사를 사용하지만(`http://localhost:8000/api/acct/login/`), 프론트엔드 환경 변수 `REACT_APP_API_URL`이 `http://localhost:8000`으로 설정되어 있어 `/api`가 누락됨.
**해결:** `.env` 파일의 `REACT_APP_API_URL`을 `http://localhost:8000/api`로 수정하고 서버를 재시작하여 해결함.

### 9. 빠른 로그인(Quick Login) 작동 실패 (해결됨)
**현상:** 로그인 페이지의 역할별 빠른 로그인 버튼 클릭 시 로그인이 실패하고 에러 메시지가 표시됨.
**원인:** 백엔드의 테스트 유저 생성 스크립트와 프론트엔드 `LoginPage.js`의 하드코딩된 비밀번호가 서로 달랐으며, 특수문자 처리 문제도 복합적으로 작용함.
**해결:** 백엔드(`create_test_users.py`)와 프론트엔드(`LoginPage.js`)의 비밀번호를 단순한 형태(`username` + `123`)로 통일하고, Docker 컨테이너에서 사용자 데이터를 재생성하여 해결함.

### 11. Django 포트 접근 불가 (Connection Refused)
**현상:** React 클라이언트에서 http://localhost:8000/api 호출 시 연결 실패.
**원인:** Docker 환경에서 Django 컨테이너(8000)는 외부 노출 없이 Nginx(80)만을 통하도록 설정됨.
**해결:** API 호출 주소를 Nginx 프록시로 http://localhost/api로 변경하여 해결함.

---

## 2026-01-01 긴급 버그 수정

### 12. React 무한 새로고침 (Infinite Refresh) 현상 (치명적)
**현상:** React 앱 실행 시 페이지가 무한으로 새로고침되어 정상적으로 사용 불가능.
**원인:** `devAutoLogin.js`의 자동 로그인 로직에서 로그인 성공 후 `window.location.reload()`를 호출하여 페이지를 강제로 리로드함. 리로드 시 `App.js`의 `useEffect`가 다시 실행되고 `devAutoLogin()`이 재호출되어 무한 루프 발생. 22-24번 라인의 토큰 체크로는 비동기 로그인 완료 전에 통과하여 방지 불가.
**해결:**
1. `devAutoLogin.js:50-52` - `window.location.reload()` 완전 제거
2. `App.js:25-65` - localStorage 변경을 100ms 간격으로 감지하여 자동 로그인 완료 시 React 상태를 자동 업데이트하도록 개선 (5초 후 interval 자동 정리)
**영향:** 개발 자동 로그인 기능이 페이지 리로드 없이 원활하게 작동하며, 무한 새로고침 문제 완전 해결.
**수정 파일:**
- `NeuroNova_03_front_end_react/00_test_client/src/utils/devAutoLogin.js`
- `NeuroNova_03_front_end_react/00_test_client/src/App.js`
