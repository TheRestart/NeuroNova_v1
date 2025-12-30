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
**해결:** Windows 호스트의 WSL 어댑터 IP(`172.29.64.1`)를 확인하고, `package.json`의 proxy 설정을 해당 IP로 변경하여 해결함.

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
