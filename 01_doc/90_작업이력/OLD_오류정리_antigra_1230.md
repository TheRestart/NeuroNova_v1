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
**원인:** `create_user` 함수 호출 시 비밀번호 인자가 누락되어, Django가 사용할 수 없는 비밀번호로 설정함. 나중에 `set_password`를 호출하려 했으나 변수가 이미 pop되어 사라짐.
**해결:** `create_user`에 `password` 인자를 명시적으로 전달하도록 수정하고, 특수문자 처리를 위해 raw string(`r''`)을 사용함.

### 9. 빠른 로그인(Quick Login) 작동 실패
**현상:** 로그인 페이지의 역할별 빠른 로그인 버튼 클릭 시 아무 반응이 없거나 로그인이 실패함.
**원인:** (분석 결과) 빠른 로그인 핸들러에서 호출하는 `authAPI.login` 함수의 매개변수 전달 방식이나, 하드코딩된 비밀번호가 백엔드 데이터와 불일치할 가능성.
**해결:** (진행 중) `LoginPage.js`의 `handleQuickLogin` 함수를 분석하고, 백엔드에 설정된 올바른 자격증명으로 수정할 예정.
