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

## 2025-12-31 로그인 인증 문제 해결

### 8. create_test_users.py 비밀번호 해싱 버그 (치명적)
**현상:** `python manage.py create_test_users` 실행 후 생성된 계정으로 로그인 시도 시 401 Unauthorized 에러 발생. Django 로그에 "ERR_001 - 인증에 실패했습니다" 경고.
**원인:**
1. create_test_users.py 162-164번 줄에서 `password = user_data.pop('password')` 후 `User.objects.create_user(**user_data)` 호출 시 password가 없는 상태로 create_user() 실행됨
2. create_user()는 password 없이 호출되면 사용 불가능한 비밀번호로 설정
3. 163번 줄의 `user.set_password(password)` 호출 시도는 password 변수가 이미 pop()으로 제거되어 의미 없음
4. 추가 문제: Python에서 특수문자 `!@#`가 포함된 비밀번호 문자열에 escape sequence 경고 (`SyntaxWarning: invalid escape sequence '\!'`)

**해결:**
1. create_user() 호출 시 password를 명시적으로 전달하도록 수정 (162-172번 줄)
2. 비밀번호 문자열을 raw string (`r'admin123!@#'`)으로 변경하여 escape sequence 문제 해결
3. 기존 사용자 13명 삭제 후 수정된 스크립트로 재생성

**코드 수정:**
```python
# [수정 전] 버그 코드
user = User.objects.create_user(**user_data)  # password 없음!
user.set_password(password)  # password 변수 이미 제거됨
user.save()

# [수정 후] 올바른 코드
user = User.objects.create_user(
    username=user_data['username'],
    email=user_data['email'],
    password=password,  # 명시적으로 전달
    role=user_data['role'],
    full_name=user_data['full_name'],
    # ...
)
```

**비밀번호 문자열 수정:**
```python
# [수정 전]
'password': 'admin123!@#',  # SyntaxWarning 발생

# [수정 후]
'password': r'admin123!@#',  # raw string 사용
```

**검증 시도:**
- `admin.check_password("admin123!@#")` 테스트: False 반환 (여전히 문제)
- Python shell의 -c 옵션에서 특수문자 전달 시 escape 문제 발생
- 비밀번호 해시는 정상 생성됨 (pbkdf2_sha256$870000$...)

**현재 상태 (2025-12-31 09:50):**
- 스크립트 코드 수정 완료 (162-172번 줄, 19-64번 줄)
- 테스트 사용자 13명 재생성 완료
- 비밀번호 검증 실패 지속 (Python shell escape 문제로 추정)
- 추가 검증 필요: Django Admin 또는 실제 브라우저 로그인 테스트

**다음 단계:**
1. 브라우저에서 실제 로그인 테스트 (http://localhost:3001)
2. 실패 시 Django Admin에서 비밀번호 수동 재설정
3. 또는 비밀번호를 단순화 (특수문자 제거: 'admin123' 등)
