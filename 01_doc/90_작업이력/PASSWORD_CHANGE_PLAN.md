# 비밀번호 규칙 변경 계획

**작성일**: 2025-12-31
**목적**: 로그인 인증 문제 해결을 위한 비밀번호 규칙 단순화
**변경 사유**: Python escape sequence 문제 및 로그인 인증 실패 해결

---

## 📋 변경 개요

### 현재 비밀번호 규칙
```
admin / admin123!@#
doctor / doctor123!@#
nurse / nurse123!@#
patient / patient123!@#
radiologist / rib123!@#
labtech / lab123!@#
```

### 신규 비밀번호 규칙 (최종 확정)
```
admin / admin123
doctor / doctor123
nurse / nurse123
patient / patient123
radiologist / radiologist123
labtech / labtech123
```

---

## 🎯 변경 이유

### 1. Python Escape Sequence 문제
- 현재: `!@#` 특수문자 조합이 Python에서 `\!` escape sequence 경고 발생
- 해결: 특수문자 완전 제거 (`*123` 형태)

### 2. 로그인 인증 실패
- 현재: create_test_users.py로 생성된 계정의 비밀번호 검증 실패 (check_password 반환 False)
- 예상: 특수문자 처리 과정에서 비밀번호 해시 불일치 발생
- 해결: 특수문자 완전 제거로 문제 원천 차단

### 3. 가독성 및 입력 편의성
- 현재: `!@#` 조합은 키보드 입력 시 Shift 키 3번 필요
- 개선: `*123` 형태는 Shift 키 불필요, 숫자만 입력

---

## 📝 변경 작업 계획

### Phase 1: 코드 수정 (서버 미기동)

#### 1.1 create_test_users.py 수정
**파일**: `NeuroNova_02_back_end/02_django_server/acct/management/commands/create_test_users.py`

**변경 내용**:
```python
# [이전] 19번 줄
'password': r'admin123!@#',

# [최종 확정]
'password': 'admin123',
```

**적용 범위**: 6개 메인 계정 (admin, doctor, nurse, patient, radiologist, labtech)
- 19번 줄: admin → `admin123`
- 29번 줄: doctor → `doctor123`
- 38번 줄: nurse → `nurse123`
- 47번 줄: patient → `patient123`
- 55번 줄: radiologist → `radiologist123` (rib@123에서 변경)
- 64번 줄: labtech → `labtech123` (lab@123에서 변경)

**참고**:
- raw string (r'...') 접두사 제거 완료
- 특수문자 완전 제거로 escape 문제 해결
- admin1, doctor1 등 numbered 계정은 유지 (기존 `admin123!`, `doctor123!` 등)

---

#### 1.2 문서 업데이트

**변경 대상 문서** (4개):

1. **01_doc/REF_CLAUDE_ONBOARDING_QUICK.md** ✅ 완료
   - 위치: 섹션 Q5 (FAQ), 섹션 8.6 (로그인 테스트)
   - 변경: 모든 비밀번호 `*123!@#` → `*123`

2. **작업_계획_요약.md** ✅ 완료 (비밀번호 언급 없음)
   - 확인 결과: 비밀번호 정보 없음

3. **NeuroNova_03_front_end_react/00_test_client/사용방법_설명문서.md** ✅ 완료
   - 위치: 섹션 4-2 (수동 로그인), 부록 (빠른 참조)
   - 변경: 모든 비밀번호 `*123!@#` → `*123`
   - 특이사항: radiologist `rib123!@#` → `radiologist123`, labtech `lab123!@#` → `labtech123`

4. **NeuroNova_03_front_end_react/00_test_client/README.md**
   - 확인 필요

---

### Phase 2: 데이터베이스 재생성 (서버 기동 후)

#### 2.1 기존 테스트 사용자 삭제
```bash
docker exec neuronova-django-dev python manage.py shell -c "
from acct.models import User
User.objects.filter(username__in=['admin', 'doctor', 'nurse', 'patient', 'radiologist', 'labtech']).delete()
print('Deleted 6 test users')
"
```

#### 2.2 신규 테스트 사용자 생성
```bash
docker exec neuronova-django-dev python manage.py create_test_users
```

#### 2.3 비밀번호 검증
```bash
docker exec neuronova-django-dev python manage.py shell -c "
from acct.models import User
admin = User.objects.get(username='admin')
print('Password check:', admin.check_password('admin@123'))
"
```

**예상 결과**: `Password check: True`

---

### Phase 3: 로그인 테스트

#### 3.1 React 테스트 클라이언트 로그인
1. 브라우저에서 http://localhost:3001 접속
2. 신규 비밀번호로 로그인 시도:
   - Username: `admin`
   - Password: `admin@123`
3. 성공 확인: 대시보드 접근 가능

#### 3.2 Django Admin 로그인
1. 브라우저에서 http://localhost:8000/admin 접속
2. Superuser 로그인 시도:
   - Username: `admin`
   - Password: `admin@123`
3. 성공 확인: Admin 페이지 접근 가능

---

## 📊 변경 영향 범위

### 코드 파일
- [x] `acct/management/commands/create_test_users.py` (6개 라인)

### 문서 파일
- [ ] `01_doc/REF_CLAUDE_ONBOARDING_QUICK.md`
- [ ] `작업_계획_요약.md`
- [ ] `NeuroNova_03_front_end_react/00_test_client/사용방법_설명문서.md`
- [ ] `NeuroNova_03_front_end_react/00_test_client/README.md`

### 데이터베이스
- [ ] 6개 테스트 사용자 재생성 (admin, doctor, nurse, patient, radiologist, labtech)

### 영향 없음
- admin1, doctor1, rib1, lab1, nurse1, patient1, external1 (기존 비밀번호 유지)

---

## ⚠️ 주의사항

### 1. 실행 순서 준수
- **반드시** Phase 1 (코드 수정) → Phase 2 (DB 재생성) → Phase 3 (테스트) 순서로 진행
- Phase 2는 Django 서버 기동 후에만 실행 가능

### 2. 문서 일관성
- 모든 문서에서 비밀번호를 일관되게 `*@123` 형태로 변경
- 누락된 문서가 없는지 grep 검색으로 최종 확인:
  ```bash
  grep -r "admin123!@#" 01_doc/
  grep -r "doctor123!@#" NeuroNova_03_front_end_react/
  ```

### 3. Git 커밋 메시지
```
fix: Simplify test user passwords to resolve authentication issue

- Change password format from `*123!@#` to `*@123`
- Resolve Python escape sequence warnings
- Fix login authentication failures (401 errors)
- Update all documentation with new password format

Affected accounts: admin, doctor, nurse, patient, radiologist, labtech
```

---

## 🔄 롤백 계획

만약 신규 비밀번호로도 로그인 실패 시:

### Option 1: 특수문자 완전 제거
```
admin / admin123
doctor / doctor123
nurse / nurse123
...
```

### Option 2: Django Admin에서 수동 재설정
1. http://localhost:8000/admin 접속 (다른 superuser 계정 사용)
2. Users 테이블에서 해당 사용자 선택
3. "Change password" 버튼으로 비밀번호 직접 재설정

### Option 3: 직접 Shell에서 재설정
```bash
docker exec neuronova-django-dev python manage.py shell
```
```python
from acct.models import User
admin = User.objects.get(username='admin')
admin.set_password('admin@123')
admin.save()
```

---

## ✅ 체크리스트

### Phase 1: 코드 수정
- [x] create_test_users.py 6개 라인 수정 완료
- [x] raw string 접두사 제거 확인
- [x] 비밀번호 특수문자 완전 제거 (admin123, doctor123, ...)

### Phase 1: 문서 업데이트
- [x] REF_CLAUDE_ONBOARDING_QUICK.md 업데이트
- [x] 작업_계획_요약.md 확인 (비밀번호 언급 없음)
- [x] 사용방법_설명문서.md 업데이트 (2곳)
- [x] README.md 업데이트
- [x] LoginPage.js 확인 (이미 업데이트됨)

### Phase 2: 데이터베이스 재생성 (서버 필요)
- [x] 기존 사용자 삭제 ✅ (2025-12-31 완료 - 6개 계정 삭제)
- [x] 신규 사용자 생성 ✅ (2025-12-31 완료 - 13명 생성/업데이트)
- [x] check_password() 검증 ✅ (2025-12-31 완료 - 6개 계정 모두 PASS)

### Phase 3: 로그인 테스트 (서버 필요)
- [ ] React 로그인 테스트 성공 (사용자 확인 대기 중)
- [ ] Django Admin 로그인 테스트 성공 (선택)

### Phase 4: 문서화 (서버 필요)
- [x] OLD_오류정리_antigra_1230.md에 변경 결과 기록 ✅
- [x] LOG_작업이력.md에 변경 이력 추가 ✅

---

**작성자**: Claude AI
**승인 대기**: 작업 시작 전 검토 필요
**예상 소요 시간**: 30분 (코드 수정 10분 + 문서 업데이트 15분 + 테스트 5분)
