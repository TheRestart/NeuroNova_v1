# 16. Write-Through 패턴 가이드

**문서 작성일**: 2025-12-23
**작성자**: Claude AI
**버전**: 1.0

---

## 📋 개요

CDSS 시스템의 **환자 프로필 수정** 기능은 **Write-Through 패턴**을 사용하여 데이터 일관성을 보장합니다.

### 핵심 원칙

**Single Source of Truth: OpenEMR (FHIR Server)**
- OpenEMR이 환자 정보의 **유일한 원본(Master)**입니다.
- Django DB는 성능을 위한 **Read Cache(읽기 캐시)**입니다.

**Write-Through 전략**
```
사용자 → Django API → FHIR 서버 (먼저 업데이트) → 성공 시 → Django DB 업데이트
                          ↓ 실패 시
                      Django DB 수정 없이 에러 반환
```

---

## 🏗️ 아키텍처

### 데이터 수정 흐름

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 클라이언트가 환자 프로필 수정 요청 (PATCH)                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Django ViewSet이 요청 수신 및 검증                        │
│    - Serializer 유효성 검사                                  │
│    - OpenEMR Patient ID 확인                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FHIR Adapter를 통해 FHIR 서버에 업데이트 요청 (선행)      │
│    - FHIRServiceAdapter.update_patient() 호출                │
└─────────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┴────────────────┐
         ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│  FHIR 서버 성공  │              │  FHIR 서버 실패  │
│  (200 OK)        │              │  (400/503)       │
└──────────────────┘              └──────────────────┘
         ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ 4A. Django DB    │              │ 4B. Django DB    │
│     업데이트     │              │     수정 없음    │
│                  │              │                  │
│ 5A. 200 OK 응답  │              │ 5B. 400/503 응답 │
└──────────────────┘              └──────────────────┘
```

### 컴포넌트 구조

```
emr/
├── viewsets.py                    # PatientCacheViewSet
│   └── partial_update()           # PATCH 메서드 (Write-Through 구현)
│
├── fhir_adapter.py                # FHIR Service Adapter
│   └── FHIRServiceAdapter
│       ├── update_patient()       # FHIR 서버 업데이트
│       ├── _get_patient_resource()
│       ├── _merge_patient_data()
│       └── _parse_error_response()
│
├── models.py                      # PatientCache
│   └── openemr_patient_id         # FHIR 서버 리소스 ID
│
└── test_write_through.py          # Write-Through 패턴 테스트
```

---

## 💡 주요 시나리오

### 시나리오 1: FHIR 서버 업데이트 성공

```python
# Given: 환자 정보 수정 요청
PATCH /api/emr/patients/P-2025-000001/
{
    "phone": "010-9999-8888",
    "email": "newemail@example.com"
}

# 처리 흐름:
1. FHIRServiceAdapter.update_patient() 호출
2. FHIR 서버가 200 OK + 업데이트된 리소스 반환
3. Django DB 업데이트 (perform_update)
4. last_synced_at 갱신
5. 200 OK 응답
```

**결과:**
- ✅ FHIR 서버 업데이트됨
- ✅ Django DB 업데이트됨
- ✅ 데이터 일관성 보장

---

### 시나리오 2: FHIR 서버 거절 (유효성 검사 실패)

```python
# Given: 잘못된 형식의 전화번호
PATCH /api/emr/patients/P-2025-000001/
{
    "phone": "invalid-phone"
}

# 처리 흐름:
1. FHIRServiceAdapter.update_patient() 호출
2. FHIR 서버가 400 Bad Request 반환
   - OperationOutcome: "Invalid phone format"
3. Django DB 수정 없음
4. 400 Bad Request 응답
```

**결과:**
- ❌ FHIR 서버 업데이트 거절
- ❌ Django DB 수정 없음
- ✅ 기존 데이터 유지

**응답 예시:**
```json
{
    "error": "Invalid phone format",
    "detail": "FHIR server rejected the update"
}
```

---

### 시나리오 3: FHIR 서버 통신 장애

```python
# Given: FHIR 서버 다운 또는 네트워크 장애
PATCH /api/emr/patients/P-2025-000001/
{
    "phone": "010-9999-8888"
}

# 처리 흐름:
1. FHIRServiceAdapter.update_patient() 호출
2. Exception 발생 (ConnectionError, Timeout 등)
3. Django DB 수정 없음
4. 503 Service Unavailable 응답
```

**결과:**
- ❌ FHIR 서버 통신 실패
- ❌ Django DB 수정 없음
- ⚠️ 사용자에게 재시도 안내

**응답 예시:**
```json
{
    "error": "FHIR server communication failed",
    "detail": "Connection timeout"
}
```

---

### 시나리오 4: OpenEMR과 동기화되지 않은 환자

```python
# Given: openemr_patient_id가 None인 환자
PATCH /api/emr/patients/P-2025-000002/
{
    "phone": "010-1234-5678"
}

# 처리 흐름:
1. openemr_patient_id 확인 → None
2. FHIR Adapter 호출 스킵
3. Django DB만 업데이트
4. 200 OK 응답
```

**결과:**
- ⏭️ FHIR 서버 호출 스킵
- ✅ Django DB만 업데이트
- ℹ️ 로그에 경고 메시지 기록

---

## 🧪 테스트

### 테스트 실행

```bash
# 전체 Write-Through 테스트 실행
cd NeuroNova_02_back_end/01_django_server
./venv/Scripts/python manage.py test emr.test_write_through -v 2

# 특정 테스트만 실행
./venv/Scripts/python manage.py test emr.test_write_through.PatientWriteThroughTestCase.test_update_success_with_emr_sync
```

### 테스트 케이스

| 테스트 케이스 | 설명 | 검증 항목 |
|---|---|---|
| `test_update_success_with_emr_sync` | FHIR 서버 성공 | ✅ Django DB 업데이트됨<br>✅ 200 OK 응답 |
| `test_update_fail_when_emr_rejects` | FHIR 서버 거절 | ❌ Django DB 수정 없음<br>✅ 400 에러 응답 |
| `test_update_fail_on_emr_exception` | FHIR 서버 장애 | ❌ Django DB 수정 없음<br>✅ 503 에러 응답 |
| `test_update_patient_without_openemr_id` | 동기화 안된 환자 | ⏭️ FHIR 호출 스킵<br>✅ Django DB만 업데이트 |

**테스트 결과 (2025-12-23):**
```
Ran 7 tests in 0.152s
OK (✅ 모든 테스트 통과)
```

---

## 🔧 개발 가이드

### FHIR Adapter 사용법

```python
from emr.fhir_adapter import FHIRServiceAdapter

# Adapter 인스턴스 생성
fhir_adapter = FHIRServiceAdapter()

# 환자 정보 업데이트
success, result = fhir_adapter.update_patient(
    patient_id='fhir-patient-123',
    update_data={
        'phone': '010-1234-5678',
        'email': 'patient@example.com',
        'address': '서울시 강남구...'
    }
)

if success:
    # 성공: result는 업데이트된 FHIR Patient 리소스
    print(f"Updated: {result['id']}")
else:
    # 실패: result는 에러 메시지
    print(f"Error: {result['error']}")
```

### ViewSet 커스터마이징

```python
class PatientCacheViewSet(viewsets.ModelViewSet):
    def partial_update(self, request, *args, **kwargs):
        # 1. 환자 조회
        patient = self.get_object()

        # 2. Serializer 검증
        serializer = self.get_serializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 3. OpenEMR Patient ID 확인
        if not patient.openemr_patient_id:
            # 동기화 안된 환자는 Django DB만 업데이트
            self.perform_update(serializer)
            return Response(serializer.data)

        # 4. FHIR Adapter 호출 (Write-Through)
        fhir_adapter = FHIRServiceAdapter()
        try:
            success, result = fhir_adapter.update_patient(...)

            if success:
                # Case A: FHIR 서버 성공 → Django DB 업데이트
                self.perform_update(serializer)
                return Response(serializer.data, status=200)
            else:
                # Case B: FHIR 서버 거절 → Django DB 수정 없음
                return Response({...}, status=400)

        except Exception as e:
            # Case C: FHIR 서버 장애 → Django DB 수정 없음
            return Response({...}, status=503)
```

---

## 🎯 환자가 직접 프로필 수정하는 경우

### Patient Role의 프로필 수정

환자(Patient Role)가 직접 자신의 프로필 정보를 수정할 때도 동일한 Write-Through 패턴을 따릅니다.

#### 권한 체크

```python
from acct.permissions import IsSelfOrAdmin

class PatientCacheViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['partial_update', 'update']:
            # 환자는 본인 데이터만 수정 가능
            return [IsSelfOrAdmin()]
        return super().get_permissions()
```

#### 프로필 수정 API

```python
# Patient가 본인 프로필 수정
PATCH /api/emr/patients/P-2025-000001/
Authorization: Bearer <patient-jwt-token>
{
    "phone": "010-5555-6666",
    "email": "myemail@example.com",
    "address": "경기도 성남시..."
}
```

**처리 흐름:**
1. JWT 토큰으로 환자 인증
2. `IsSelfOrAdmin` 권한 체크 (본인 확인)
3. FHIR Adapter를 통해 OpenEMR 업데이트 (선행)
4. OpenEMR 성공 시 Django DB 업데이트
5. 200 OK 응답

**보안:**
- ✅ 환자는 본인의 `patient_id`와 일치하는 데이터만 수정 가능
- ✅ 다른 환자의 데이터 수정 시도 시 403 Forbidden
- ✅ Read-Only 필드(patient_id, created_at 등)는 무시됨

---

## ⚠️ 주의사항

### 1. FHIR 서버 필수

Write-Through 패턴은 **FHIR 서버가 가동 중**이어야 합니다.
- 개발 환경: OpenEMR Docker 실행 필요
- 프로덕션: HAPI FHIR 서버 또는 OpenEMR 연동

### 2. 성능 고려

FHIR 서버 호출로 인해 응답 시간이 증가할 수 있습니다.
- 평균 응답 시간: ~200-500ms (FHIR 서버 포함)
- 캐시 전략: Read는 Django DB에서 빠르게 조회

### 3. 동기화 대상 필드

현재 FHIR 동기화 대상 필드:
- `phone` (전화번호)
- `email` (이메일)
- `address` (주소)

기타 필드는 Django DB만 업데이트됩니다.

### 4. 에러 핸들링

- **400 Bad Request**: 사용자에게 입력값 수정 요청
- **503 Service Unavailable**: 사용자에게 잠시 후 재시도 안내
- **500 Internal Server Error**: 시스템 관리자에게 알림

---

## 📊 모니터링

### 로그 확인

```bash
# Django 로그 확인
tail -f logs/django.log | grep "FHIR"

# 성공 로그
FHIR update success for patient P-2025-000001

# 실패 로그
FHIR validation failed for patient P-2025-000001: Invalid phone format
FHIR server error for patient P-2025-000001: Connection timeout
```

### 메트릭

추천 모니터링 메트릭:
- FHIR 서버 응답 시간 (avg, p95, p99)
- FHIR 서버 성공률 (%)
- FHIR 서버 오류율 (400, 503)
- Django DB 업데이트 성공률 (%)

---

## 📚 참고 자료

- [08_API_명세서.md](08_API_명세서.md) - EMR CRUD API
- [12_보안_아키텍처_정책.md](12_보안_아키텍처_정책.md) - 권한 체계
- [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md) - UC02 EMR 아키텍처

---

**최종 수정일**: 2025-12-23
**작성자**: Claude AI
**버전**: 1.0
