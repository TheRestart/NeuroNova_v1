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
**현상:** React 로그인 시 모든 테스트 계정이 401 Unauthorized 에러 발생. Django 로그에서 "ERR_001 - 인증에 실패했습니다" 반환.
**원인:** create_test_users.py 162-164번 줄에서 `password = user_data.pop('password')` 후 `User.objects.create_user(**user_data)` 호출 시 password가 전달되지 않음. create_user()가 password 없이 호출되어 사용 불가능한 비밀번호 설정.
**해결:** create_user() 호출 시 password를 명시적으로 전달하도록 수정. 비밀번호를 단순화(`admin123`, `doctor123` 등)하여 특수문자 처리 문제 제거. 13명 테스트 사용자 재생성 후 check_password() 검증 완료.

### 9. React API 접근 경로 문제 (Docker 네트워크)
**현상:** React에서 `http://localhost:8000/api`로 호출하지만 Django 컨테이너 포트 8000이 호스트에 노출되지 않아 연결 실패. `django.contrib.auth.authenticate()`는 정상 작동하지만 HTTP 요청이 Django에 도달하지 못함.
**원인:** Docker Compose 설정에서 django 컨테이너는 내부 네트워크만 사용하고 포트를 호스트에 매핑하지 않음. Nginx가 Reverse Proxy로 포트 80에서 Django로 프록시하는 구조.
**해결:** `.env.local` 파일에서 `REACT_APP_API_URL`을 `http://localhost/api`로 변경하여 Nginx (포트 80) 경유하도록 수정. DICOM URL도 `http://localhost/api/ris/dicom-web`로 변경. curl 테스트 결과 로그인 API 정상 작동 확인 (JWT 토큰 발급 성공).

### 10. 빠른 로그인(Quick Login) 작동 실패
**현상:** 로그인 페이지의 역할별 빠른 로그인 버튼 클릭 시 아무 반응이 없거나 로그인이 실패함.
**원인:** (분석 결과) 빠른 로그인 핸들러에서 호출하는 `authAPI.login` 함수의 매개변수 전달 방식이나, 하드코딩된 비밀번호가 백엔드 데이터와 불일치할 가능성.
**해결:** (진행 중) `LoginPage.js`의 `handleQuickLogin` 함수를 분석하고, 백엔드에 설정된 올바른 자격증명으로 수정할 예정.

### 11. React ���� ���ΰ�ħ (Infinite Refresh) ����
**����:** React �� ���� �� http://localhost ���� ��, �α��� �� ��ú���� �̵��ϸ� ������ �������� ���ΰ�ħ�ǰų� Ư�� ���(/dashboard)���� ���ΰ�ħ(F5) �� 404 ���� �߻�.
**���� ����:** SPA(Single Page Application)�� ��� ��� ��û�� index.html�� ������ �ϴµ�, Nginx ������ 	ry_files Fallback�� �����Ǿ��ų�, React useEffect ���� devAutoLogin�� ���� ���� ��ū ������ �浹�Ͽ� ���� �����̷�Ʈ �߻�.
**�ذ�:** (���� ��) Nginx ������ 	ry_files  / /index.html; �߰� �� React Auth ���� ���� ����.
