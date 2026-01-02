# NeuroNova CDSS - End-to-End 테스트 스크립트

**작성일**: 2026-01-02
**버전**: 1.0
**목적**: UC01~UC09 전체 Use Case End-to-End 자동화 테스트

---

## 📁 파일 구조

```
tests/e2e/
├── README.md                  # 이 파일 (테스트 가이드)
├── test_uc01_auth.py          # UC01: 인증/권한 테스트
├── test_uc02_emr.py           # UC02: EMR (환자/진료기록) 테스트
├── test_uc03_ocs.py           # UC03: OCS (처방전달) 테스트
├── test_uc04_lis.py           # UC04: LIS (검체검사) 테스트 (예정)
├── test_uc05_ris.py           # UC05: RIS + OHIF Viewer 테스트 (예정)
├── test_uc06_ai.py            # UC06: AI 추론 테스트 (예정)
├── test_uc07_alert.py         # UC07: 알림 테스트 (예정)
├── test_uc08_fhir.py          # UC08: FHIR 동기화 테스트 (예정)
├── test_uc09_audit.py         # UC09: 감사 로그 테스트 (예정)
└── test_all_uc.py             # 전체 UC 통합 테스트
```

---

## 🚀 빠른 시작

### 1. 사전 준비

#### 1-1. Docker 환경 실행
```bash
# 루트 디렉토리에서 실행
cd d:\1222\NeuroNova_v1

# 전체 스택 시작 (14개 컨테이너)
docker-compose -f docker-compose.dev.yml up -d

# 컨테이너 상태 확인
docker-compose -f docker-compose.dev.yml ps
```

#### 1-2. 샘플 데이터 준비
```bash
# Django 컨테이너에 접속하여 실행
docker-compose -f docker-compose.dev.yml exec django python manage.py create_test_users
docker-compose -f docker-compose.dev.yml exec django python manage.py init_sample_data
docker-compose -f docker-compose.dev.yml exec django python manage.py seed_master_data
```

#### 1-3. Python 패키지 설치
```bash
cd tests/e2e
pip install requests
```

### 2. 개별 UC 테스트 실행

#### UC01: 인증/권한 테스트
```bash
python test_uc01_auth.py
```

**테스트 시나리오**:
1. Patient 자가 회원가입
2. Admin이 Doctor 계정 생성
3. Patient 로그인 (JWT 토큰 발급)
4. Doctor 로그인
5. Refresh Token으로 Access Token 갱신
6. 현재 사용자 정보 조회
7. 권한 검증 (Patient → Admin API 접근 시도)
8. 로그아웃

#### UC02: EMR 테스트
```bash
python test_uc02_emr.py
```

**테스트 시나리오**:
1. 환자 등록 (OpenEMR + Django DB 병렬 저장)
2. 환자 목록 조회 (Pagination)
3. 환자 상세 조회
4. 환자 검색 (이름, 생년월일)
5. 진료 기록 생성 (Encounter)
6. 진료 기록 조회 (타임라인)
7. 환자 정보 수정
8. Patient 권한 검증 (본인만 조회)

#### UC03: OCS (처방전달) 테스트
```bash
python test_uc03_ocs.py
```

**테스트 시나리오**:
1. 처방 생성 (Doctor)
2. 처방 목록 조회
3. 처방 상세 조회
4. 처방 집행 (Nurse)
5. 처방 취소 (Doctor)

### 3. 전체 UC 통합 테스트 실행

```bash
python test_all_uc.py
```

**실행 순서**:
1. UC01 인증/권한 (8개 테스트)
2. UC02 EMR (8개 테스트)
3. UC03 OCS (5개 테스트)
4. UC04~UC09 (예정)

---

## 📊 테스트 결과 리포트

### 자동 생성 파일

각 테스트 실행 후 JSON 리포트 자동 생성:

- `uc01_test_report_<timestamp>.json` - UC01 결과
- `uc02_test_report_<timestamp>.json` - UC02 결과
- `uc03_test_report_<timestamp>.json` - UC03 결과

### 리포트 형식

```json
[
  {
    "timestamp": "2026-01-02T10:30:00.123456",
    "test_name": "UC01-1: Patient 회원가입",
    "status": "PASS",
    "message": "환자 회원가입 성공: patient_e2e_1234567890",
    "status_code": 201,
    "response_time": 0.456
  }
]
```

### 결과 요약 예시

```
================================================================================
테스트 결과 요약
================================================================================

총 테스트: 21
  - PASS: 18 (85.7%)
  - FAIL: 2 (9.5%)
  - SKIP: 1 (4.8%)

[FAIL] 실패한 테스트:
  - UC02-5: 진료 기록 생성: OpenEMR 연결 실패 (503 Service Unavailable)
  - UC03-4: 처방 집행: Nurse 권한 없음 (403 Forbidden)

[INFO] 상세 리포트 저장: uc02_test_report_1735800000.json
================================================================================
```

---

## 🎯 테스트 시나리오별 성공 기준

### UC01: 인증/권한
- [ ] 회원가입 성공 (Patient, Doctor)
- [ ] 로그인 성공 및 JWT 토큰 발급
- [ ] 토큰 갱신 성공
- [ ] 사용자 정보 조회 성공
- [ ] 권한 검증 정상 (403/401 응답)

### UC02: EMR
- [ ] 환자 등록 성공 (Django + OpenEMR 병렬 저장)
- [ ] 환자 목록/상세 조회 성공
- [ ] 진료 기록 생성 성공
- [ ] 권한 검증 정상 (Patient는 본인만 조회)

### UC03: OCS
- [ ] 처방 생성 성공 (Doctor)
- [ ] 처방 상태 변경 성공 (PENDING → EXECUTING → COMPLETED)
- [ ] 처방 집행 성공 (Nurse)
- [ ] 처방 취소 성공 (Doctor)

---

## 🔧 트러블슈팅

### 문제 1: 연결 오류 (Connection Refused)

**증상**:
```
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionRefusedError(10061, '대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다'))
```

**해결**:
1. Django 서버가 실행 중인지 확인:
   ```bash
   docker-compose -f docker-compose.dev.yml ps django
   ```
2. Nginx 게이트웨이가 실행 중인지 확인:
   ```bash
   docker-compose -f docker-compose.dev.yml ps nginx
   ```
3. 브라우저에서 http://localhost/api/docs/ 접속 확인

### 문제 2: 401 Unauthorized

**증상**:
```
{
  "error": "invalid_credentials",
  "message": "아이디 또는 비밀번호가 올바르지 않습니다."
}
```

**해결**:
1. 테스트 사용자가 생성되었는지 확인:
   ```bash
   docker-compose -f docker-compose.dev.yml exec django python manage.py create_test_users
   ```
2. 비밀번호 확인 (기본값: `admin123`, `doctor123`, `nurse123`, `patient123`)

### 문제 3: 503 Service Unavailable (OpenEMR)

**증상**:
```
{
  "persistence_status": {
    "django": {"success": true},
    "openemr": {"success": false, "error": "Connection timeout"}
  }
}
```

**해결**:
1. OpenEMR 컨테이너 실행 확인 (선택적, 테스트 통과 가능):
   ```bash
   docker-compose -f docker-compose.dev.yml ps openemr
   ```
2. Django만 성공해도 테스트는 PASS 처리됨

### 문제 4: 샘플 데이터 없음

**증상**:
```
[SETUP] 환자가 없습니다 (샘플 데이터 필요)
```

**해결**:
```bash
docker-compose -f docker-compose.dev.yml exec django python manage.py init_sample_data
```

---

## 📝 테스트 확장 가이드

### 새로운 테스트 시나리오 추가

```python
def test_new_scenario(self):
    """시나리오 N: 새로운 테스트"""
    if not self.doctor_token:
        self.log_result("UC0X-N: 테스트명", "SKIP", "토큰이 없어 건너뜀")
        return False

    url = f"{self.base_url}/api/endpoint/"
    headers = {"Authorization": f"Bearer {self.doctor_token}"}

    try:
        response = self.session.post(url, json={}, headers=headers)
        if response.status_code == 201:
            self.log_result("UC0X-N: 테스트명", "PASS", "성공", response)
            return True
        else:
            self.log_result("UC0X-N: 테스트명", "FAIL", f"실패: {response.text}", response)
            return False
    except Exception as e:
        self.log_result("UC0X-N: 테스트명", "FAIL", f"예외 발생: {str(e)}")
        return False
```

### 테스트 클래스 템플릿

```python
class UC0XTEST:
    def __init__(self, base_url="http://localhost/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_result(self, test_name, status, message, response=None):
        # 로깅 로직 (기존 참조)
        pass

    def setup(self):
        # 사전 준비 (로그인, 데이터 생성)
        pass

    def test_scenario_1(self):
        # 테스트 시나리오 1
        pass

    def run_all_tests(self):
        # 전체 테스트 실행
        pass

    def print_summary(self):
        # 결과 요약
        pass
```

---

## 🔗 관련 문서

- [REF_CLAUDE_ONBOARDING_QUICK.md](../../01_doc/REF_CLAUDE_ONBOARDING_QUICK.md) - 프로젝트 온보딩
- [10_API_명세서.md](../../01_doc/10_API_명세서.md) - API 전체 명세
- [LOG_작업이력.md](../../01_doc/LOG_작업이력.md) - 작업 이력
- [작업_계획_요약.md](../../작업_계획_요약.md) - 작업 계획

---

## ✅ 체크리스트

### 테스트 실행 전
- [ ] Docker 환경 실행 (`docker-compose up -d`)
- [ ] 테스트 사용자 생성 (`create_test_users`)
- [ ] 샘플 데이터 생성 (`init_sample_data`, `seed_master_data`)
- [ ] API 서버 정상 확인 (http://localhost/api/docs/)

### 테스트 실행
- [x] UC01: 인증/권한 테스트
- [x] UC02: EMR 테스트
- [x] UC03: OCS 테스트
- [ ] UC04: LIS 테스트
- [ ] UC05: RIS + OHIF Viewer 테스트
- [ ] UC06: AI 추론 테스트
- [ ] UC07: 알림 테스트
- [ ] UC08: FHIR 동기화 테스트
- [ ] UC09: 감사 로그 테스트

### 테스트 완료 후
- [ ] JSON 리포트 확인
- [ ] 실패한 테스트 분석
- [ ] 버그 이슈 등록 (필요 시)
- [ ] 문서 업데이트

---

**작성**: Claude AI
**최종 업데이트**: 2026-01-02
