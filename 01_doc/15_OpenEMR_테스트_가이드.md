# OpenEMR 유닛테스트 가이드

## 문서 정보
- **작성일**: 2025-12-22
- **대상 모듈**: EMR (OpenEMR 연동)
- **테스트 파일**: `NeuroNova_02_back_end/01_django_server/emr/tests.py`
- **테스트 대상**: OpenEMR FHIR API 연동 및 Django REST API

---

## 목차
1. [개요](#개요)
2. [테스트 환경 설정](#테스트-환경-설정)
3. [테스트 구조](#테스트-구조)
4. [테스트 실행 방법](#테스트-실행-방법)
5. [테스트 케이스 상세 설명](#테스트-케이스-상세-설명)
6. [트러블슈팅](#트러블슈팅)

---

## 개요

### 목적
- OpenEMR FHIR API 연동 기능의 정상 작동 검증
- Django REST API 엔드포인트의 응답 검증
- 예외 상황 및 오류 처리 로직 검증

### 테스트 범위
- **OpenEMRClient 클래스**: OpenEMR API 통신 클라이언트
- **Django Views**: REST API 엔드포인트
- **통합 테스트**: 전체 워크플로우

### 테스트 전략
- **Unit Test**: Mock을 사용한 독립적인 단위 테스트
- **Integration Test**: 실제 서버와의 통합 테스트 (선택적)
- **Test Coverage**: 16개 테스트 케이스, 100% 통과

---

## 테스트 환경 설정

### 1. 필수 패키지 설치

```bash
cd NeuroNova_02_back_end/01_django_server
./venv/Scripts/activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 필수 패키지
pip install django djangorestframework django-cors-headers
pip install requests
pip install pika  # RabbitMQ 클라이언트 (AI 모듈 의존성)
```

### 2. 환경 변수 설정

```bash
# .env 파일 또는 settings.py에서 설정
OPENEMR_BASE_URL=http://localhost:80
```

### 3. Django 테스트 데이터베이스

Django는 테스트 실행 시 자동으로 인메모리 데이터베이스를 생성합니다.
별도의 데이터베이스 설정이 필요 없습니다.

---

## 테스트 구조

### 테스트 클래스 구성

```
emr/tests.py
├── OpenEMRClientTestCase (9 tests)
│   ├── OpenEMRClient 클래스의 모든 메서드 테스트
│   └── Mock을 사용한 외부 API 격리
│
├── EMRViewsTestCase (6 tests)
│   ├── Django REST API 엔드포인트 테스트
│   └── Mock을 사용한 클라이언트 격리
│
└── EMRIntegrationTestCase (1 test)
    └── 전체 워크플로우 통합 테스트
```

### 테스트 파일 구조

```python
# emr/tests.py
from django.test import TestCase, Client
from unittest.mock import patch, Mock
import json
import requests
from .openemr_client import OpenEMRClient

# 3개의 TestCase 클래스
# - OpenEMRClientTestCase: 클라이언트 단위 테스트
# - EMRViewsTestCase: API 엔드포인트 테스트
# - EMRIntegrationTestCase: 통합 테스트
```

---

## 테스트 실행 방법

### 1. 전체 테스트 실행

```bash
cd NeuroNova_02_back_end/01_django_server
./venv/Scripts/python manage.py test emr.tests -v 2
```

**예상 출력:**
```
Found 16 test(s).
...
Ran 16 tests in 0.130s
OK
```

### 2. 특정 테스트 클래스만 실행

#### OpenEMRClient 테스트만 실행
```bash
./venv/Scripts/python manage.py test emr.tests.OpenEMRClientTestCase -v 2
```

#### EMR Views 테스트만 실행
```bash
./venv/Scripts/python manage.py test emr.tests.EMRViewsTestCase -v 2
```

#### 통합 테스트만 실행
```bash
./venv/Scripts/python manage.py test emr.tests.EMRIntegrationTestCase -v 2
```

### 3. 특정 테스트 메서드만 실행

```bash
./venv/Scripts/python manage.py test emr.tests.OpenEMRClientTestCase.test_health_check_success -v 2
```

### 4. 테스트 커버리지 확인 (선택)

```bash
# coverage 패키지 설치
pip install coverage

# 커버리지 측정
coverage run --source='emr' manage.py test emr.tests
coverage report
coverage html  # HTML 리포트 생성
```

---

## 테스트 케이스 상세 설명

### OpenEMRClientTestCase (9개 테스트)

#### 1. Health Check 테스트

##### test_health_check_success
- **목적**: OpenEMR 서버 상태 확인 성공 케이스
- **검증 항목**:
  - HTTP 200 응답 시 `status: "healthy"` 반환
  - `status_code` 필드 포함
- **Mock 설정**:
  ```python
  mock_response.status_code = 200
  ```

##### test_health_check_failure
- **목적**: OpenEMR 서버 연결 실패 케이스
- **검증 항목**:
  - 연결 실패 시 `status: "error"` 반환
  - 에러 메시지 포함
- **Mock 설정**:
  ```python
  mock_get.side_effect = requests.RequestException("Connection failed")
  ```

#### 2. 인증 테스트

##### test_authenticate_success
- **목적**: OpenEMR API 인증 성공 케이스
- **검증 항목**:
  - `success: True` 반환
  - `access_token` 발급
- **Mock 설정**:
  ```python
  mock_response.status_code = 200
  mock_response.json.return_value = {
      "access_token": "test_token_12345",
      "token_type": "Bearer",
      "expires_in": 3600
  }
  ```

##### test_authenticate_failure
- **목적**: 잘못된 인증 정보로 인증 실패
- **검증 항목**:
  - `success: False` 반환
  - HTTP 401 응답 처리
- **Mock 설정**:
  ```python
  mock_response.status_code = 401
  ```

#### 3. 환자 목록 조회 테스트

##### test_get_patients_success
- **목적**: 환자 목록 조회 성공
- **검증 항목**:
  - FHIR Bundle 형식 파싱
  - 환자 리소스 추출
  - 환자 데이터 필드 검증 (id, name, birthDate, gender)
- **Mock 설정**:
  ```python
  mock_response.json.return_value = {
      "resourceType": "Bundle",
      "entry": [
          {"resource": {"id": "1", "name": [{"given": ["John"], "family": "Doe"}]}},
          {"resource": {"id": "2", "name": [{"given": ["Jane"], "family": "Smith"}]}}
      ]
  }
  ```

##### test_get_patients_no_token
- **목적**: 토큰 없이 환자 목록 조회 시도
- **검증 항목**:
  - HTTP 401 응답 시 빈 리스트 반환
  - 예외 발생 없이 안전하게 처리
- **Mock 설정**:
  ```python
  self.client.token = None
  mock_response.status_code = 401
  ```

#### 4. 환자 검색 테스트

##### test_search_patients_by_name
- **목적**: 이름으로 환자 검색
- **검증 항목**:
  - `given`, `family` 파라미터로 검색
  - FHIR 검색 결과 파싱
- **Mock 설정**:
  ```python
  # given="John", family="Doe"로 검색
  mock_response.json.return_value = {
      "resourceType": "Bundle",
      "entry": [{"resource": {...}}]
  }
  ```

#### 5. 특정 환자 조회 테스트

##### test_get_patient_by_id
- **목적**: 환자 ID로 특정 환자 조회
- **검증 항목**:
  - 환자 상세 정보 반환
  - telecom, address 등 추가 필드 검증
- **Mock 설정**:
  ```python
  mock_response.json.return_value = {
      "id": "1",
      "name": [...],
      "telecom": [{"system": "phone", "value": "555-1234"}],
      "address": [{"text": "123 Main St"}]
  }
  ```

##### test_get_patient_not_found
- **목적**: 존재하지 않는 환자 조회
- **검증 항목**:
  - HTTP 404 응답 시 `None` 반환
  - 예외 발생 없이 처리
- **Mock 설정**:
  ```python
  mock_response.status_code = 404
  ```

---

### EMRViewsTestCase (6개 테스트)

#### 1. Health Check Endpoint

##### test_health_check_endpoint
- **URL**: `GET /api/emr/health/`
- **검증 항목**:
  - HTTP 200 응답
  - JSON 응답에 `status` 필드 포함
- **Mock 설정**:
  ```python
  @patch('emr.views.client')
  mock_client.health_check.return_value = {"status": "healthy"}
  ```

#### 2. 인증 Endpoint

##### test_authenticate_endpoint
- **URL**: `POST /api/emr/auth/`
- **검증 항목**:
  - HTTP 200 응답
  - `success: True` 및 `token` 반환
- **Mock 설정**:
  ```python
  mock_client.authenticate.return_value = {
      "success": True,
      "token": "test_token"
  }
  ```

#### 3. 환자 목록 Endpoint

##### test_list_patients_endpoint
- **URL**: `GET /api/emr/patients/?limit=10`
- **검증 항목**:
  - HTTP 200 응답
  - `count` 및 `results` 필드 포함
  - 환자 데이터 배열
- **Mock 설정**:
  ```python
  mock_client.get_patients.return_value = [
      {"id": "1", "name": [...]},
      {"id": "2", "name": [...]}
  ]
  ```

#### 4. 환자 검색 Endpoint

##### test_search_patients_endpoint
- **URL**: `GET /api/emr/patients/search/?given=John&family=Doe`
- **검증 항목**:
  - HTTP 200 응답
  - 검색 결과 반환
- **Mock 설정**:
  ```python
  mock_client.search_patients.return_value = [{"id": "1", ...}]
  ```

#### 5. 특정 환자 조회 Endpoint

##### test_get_patient_endpoint
- **URL**: `GET /api/emr/patients/1/`
- **검증 항목**:
  - HTTP 200 응답
  - 환자 상세 정보 반환
- **Mock 설정**:
  ```python
  mock_client.get_patient.return_value = {
      "id": "1",
      "name": [...],
      "gender": "male"
  }
  ```

##### test_get_patient_not_found
- **URL**: `GET /api/emr/patients/999/`
- **검증 항목**:
  - HTTP 404 응답
  - `error` 메시지 포함
- **Mock 설정**:
  ```python
  mock_client.get_patient.return_value = None
  ```

---

### EMRIntegrationTestCase (1개 테스트)

##### test_end_to_end_workflow
- **목적**: 전체 워크플로우 통합 테스트
- **시나리오**:
  1. Health check 확인
  2. 인증 시도
  3. 환자 목록 조회
- **특징**:
  - 실제 OpenEMR 서버가 필요 (선택적)
  - 서버가 없으면 적절한 HTTP 상태 코드로 처리
  - 개발 환경에서는 Mock 테스트 우선 사용

---

## 테스트 결과 예시

### 성공적인 테스트 실행

```bash
$ ./venv/Scripts/python manage.py test emr.tests -v 2

Found 16 test(s).
Operations to perform:
  Synchronize unmigrated apps: corsheaders, messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, emr, sessions
System check identified no issues (0 silenced).

Creating test database for alias 'default'...

test_authenticate_endpoint (emr.tests.EMRViewsTestCase.test_authenticate_endpoint) ... ok
test_authenticate_failure (emr.tests.OpenEMRClientTestCase.test_authenticate_failure) ... ok
test_authenticate_success (emr.tests.OpenEMRClientTestCase.test_authenticate_success) ... ok
test_end_to_end_workflow (emr.tests.EMRIntegrationTestCase.test_end_to_end_workflow) ... ok
test_get_patient_by_id (emr.tests.OpenEMRClientTestCase.test_get_patient_by_id) ... ok
test_get_patient_endpoint (emr.tests.EMRViewsTestCase.test_get_patient_endpoint) ... ok
test_get_patient_not_found (emr.tests.EMRViewsTestCase.test_get_patient_not_found) ... ok
test_get_patient_not_found (emr.tests.OpenEMRClientTestCase.test_get_patient_not_found) ... ok
test_get_patients_no_token (emr.tests.OpenEMRClientTestCase.test_get_patients_no_token) ... ok
test_get_patients_success (emr.tests.OpenEMRClientTestCase.test_get_patients_success) ... ok
test_health_check_endpoint (emr.tests.EMRViewsTestCase.test_health_check_endpoint) ... ok
test_health_check_failure (emr.tests.OpenEMRClientTestCase.test_health_check_failure) ... ok
test_health_check_success (emr.tests.OpenEMRClientTestCase.test_health_check_success) ... ok
test_list_patients_endpoint (emr.tests.EMRViewsTestCase.test_list_patients_endpoint) ... ok
test_search_patients_by_name (emr.tests.OpenEMRClientTestCase.test_search_patients_by_name) ... ok
test_search_patients_endpoint (emr.tests.EMRViewsTestCase.test_search_patients_endpoint) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.130s

OK

Destroying test database for alias 'default'...
```

---

## 트러블슈팅

### 1. ModuleNotFoundError: No module named 'pika'

**문제**: RabbitMQ 클라이언트 패키지 누락

**해결**:
```bash
./venv/Scripts/pip install pika
```

### 2. ImportError: cannot import name 'xyz' from 'emr'

**문제**: 순환 참조 또는 잘못된 import

**해결**:
- `emr/urls.py`, `emr/views.py` 파일의 import 구문 확인
- 필요 없는 import 제거

### 3. Test database creation failed

**문제**: 데이터베이스 권한 문제

**해결**:
```bash
# SQLite 사용 시 파일 권한 확인
# settings.py의 DATABASES 설정 확인
```

### 4. CORS 에러

**문제**: 테스트 중 CORS 관련 에러

**해결**:
```python
# settings.py
INSTALLED_APPS = [
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경
```

### 5. Mock이 제대로 작동하지 않음

**문제**: `@patch` 데코레이터 경로 오류

**해결**:
```python
# 올바른 경로 사용
@patch('emr.views.client')  # emr/views.py의 client 변수
@patch('requests.Session.get')  # requests 라이브러리의 Session.get
```

### 6. 실제 OpenEMR 서버 연결 에러

**문제**: 통합 테스트 실행 시 서버 없음

**해결**:
```bash
# Docker로 OpenEMR 서버 실행
cd NeuroNova_02_back_end/02_openemr_server
docker-compose up -d

# 또는 통합 테스트 스킵
./venv/Scripts/python manage.py test emr.tests.OpenEMRClientTestCase
./venv/Scripts/python manage.py test emr.tests.EMRViewsTestCase
```

---

## 베스트 프랙티스

### 1. Mock 사용 원칙
- 외부 API 호출은 항상 Mock 사용
- 실제 네트워크 요청 지양
- 빠른 테스트 실행 보장

### 2. 테스트 격리
- 각 테스트는 독립적으로 실행 가능
- `setUp()` 메서드로 초기화
- 공유 상태 사용 금지

### 3. 명확한 테스트 이름
- `test_[기능]_[상황]` 형식 사용
- 예: `test_get_patient_not_found`

### 4. Assertion 명확성
```python
# Good
self.assertEqual(result["status"], "healthy")
self.assertTrue(result["success"])
self.assertIsNotNone(patient)

# Avoid
self.assertTrue(result["status"] == "healthy")
```

### 5. 테스트 주석
```python
def test_health_check_success(self):
    """서버 상태 확인 성공 테스트"""
    # Mock 응답 설정
    mock_response = Mock()
    mock_response.status_code = 200

    # 메서드 실행
    result = self.client.health_check()

    # 검증
    self.assertEqual(result["status"], "healthy")
```

---

## 추가 테스트 확장

### 1. RIS 모듈 테스트 추가
```bash
./venv/Scripts/python manage.py test ris.tests
```

### 2. AI 모듈 테스트 추가
```bash
./venv/Scripts/python manage.py test ai.tests
```

### 3. 통합 테스트 시나리오
- EMR + RIS 연동 테스트
- RIS + AI 큐 연동 테스트
- 전체 워크플로우 E2E 테스트

---

## 참고 자료

### 관련 파일
- [openemr_client.py](../NeuroNova_02_back_end/01_django_server/emr/openemr_client.py) - OpenEMR API 클라이언트
- [views.py](../NeuroNova_02_back_end/01_django_server/emr/views.py) - Django REST API Views
- [tests.py](../NeuroNova_02_back_end/01_django_server/emr/tests.py) - 테스트 코드
- [urls.py](../NeuroNova_02_back_end/01_django_server/emr/urls.py) - URL 라우팅

### Django 테스트 공식 문서
- https://docs.djangoproject.com/en/5.0/topics/testing/

### OpenEMR FHIR API 문서
- https://www.open-emr.org/wiki/index.php/OpenEMR_API

### Python unittest.mock 문서
- https://docs.python.org/3/library/unittest.mock.html

---

## 체크리스트

테스트 실행 전 확인사항:

- [ ] 가상환경 활성화
- [ ] 필수 패키지 설치 (django, djangorestframework, pika, requests)
- [ ] settings.py의 INSTALLED_APPS에 'emr' 포함
- [ ] URL 라우팅 설정 완료
- [ ] 테스트 데이터베이스 생성 권한 확인

테스트 실행 후 확인사항:

- [ ] 모든 테스트 통과 (16/16)
- [ ] 에러 메시지 없음
- [ ] 테스트 데이터베이스 자동 삭제 확인
- [ ] 로그 메시지 검토

---

**문서 버전**: 1.0
**최종 수정일**: 2025-12-22
**작성자**: NeuroNova Development Team
