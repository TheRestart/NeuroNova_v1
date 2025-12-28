# Claude AI 작업 프롬프트 템플릿

**문서 작성일**: 2025-12-24
**작성자**: Project Team
**버전**: 2.0 (Django Backend 개발자용)
**대상**: Claude AI + 사용자

---

## 📋 개요

이 문서는 Claude AI에게 작업을 요청할 때 사용하는 **표준 프롬프트 템플릿**입니다.
현재 프로젝트 단계(Week 4 완료, Backend CRUD 고도화)에 최적화되어 있습니다.

---

## 🔥 Phase 2: Django Backend CRUD 고도화 (Week 5-12)

### ⚡ 핵심 컨텍스트

**현재 상태**: Week 4 완료 - Backend Infrastructure 구축 완료
**담당 역할**: Django Backend 개발 (데이터 충돌 없는 CRUD)
**작업 디렉토리**: `NeuroNova_02_back_end/01_django_server/`
**개발 스택**: Django 4.2 + DRF + MySQL + Write-Through 패턴

---

## 1️⃣ 새로운 Claude 세션 시작 (첫 실행)

### 프롬프트 템플릿 A: 최소 필수 (빠른 시작)

```markdown
다음 **필수 문서만** 읽고 Django Backend 개발을 시작하시오:

1. [REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md) - Claude AI 온보딩
2. [17_프로젝트_RR_역할분담.md](01_doc/17_프로젝트_RR_역할분담.md) - R&R 정의
3. [LOG_작업이력.md](01_doc/LOG_작업이력.md) - 현재 진행 상황

현재 상태 확인:
- Week 4 완료, Django Backend CRUD 고도화 시작
- 담당: 데이터 충돌 없는 CRUD 구현, Transaction 관리
- 제외: AI 모델, Flask AI Serving, React UI, Flutter App

확인 후 작업 상태를 요약하시오.
```

### 프롬프트 템플릿 B: 전체 컨텍스트 (처음 참여하는 경우)

```markdown
다음 문서를 **순서대로** 읽고 프로젝트를 이해하시오:

1. [01_프로젝트_개요.md](01_doc/01_프로젝트_개요.md) - 프로젝트 전체 구조 (선택)
2. [REF_CLAUDE_CONTEXT.md](01_doc/REF_CLAUDE_CONTEXT.md) - Claude AI 온보딩
3. [17_프로젝트_RR_역할분담.md](01_doc/17_프로젝트_RR_역할분담.md) - R&R 정의
4. [LOG_작업이력.md](01_doc/LOG_작업이력.md) - 현재 진행 상황
5. [16_Write_Through_패턴_가이드.md](01_doc/16_Write_Through_패턴_가이드.md) - Write-Through 패턴

문서를 읽은 후:
- 9개 UC 모듈 중 Backend Infrastructure(UC01, UC02, UC05, UC06)의 역할 이해
- Django + DRF 기반 개발 환경 확인
- Week 4 완료 상태 파악

확인 후 작업 상태를 요약하시오.
```

### 예상 응답
Claude가 문서를 읽고 현재 상태(Week 4 완료, Django Backend CRUD 고도화)를 파악한 후 요약을 제공합니다.

---

## 2️⃣ 데이터 충돌 방지 패턴 구현

### 프롬프트 템플릿

```markdown
Django Backend에서 데이터 충돌 없는 CRUD를 구현하시오.

작업 디렉토리: NeuroNova_02_back_end/01_django_server/

작업 순서:
1. Optimistic Locking 구현 (version 필드 추가)
2. Pessimistic Locking 구현 (select_for_update() 활용)
3. Transaction Isolation Level 설정
4. Idempotency 보장 (멱등성 패턴)
5. Race Condition 시나리오 테스트
6. 동시성 테스트 작성 (pytest)

완료 후 LOG_작업이력.md에 작업 내용을 추가하시오.
```

---

## 3️⃣ Optimistic Locking 구현

### 프롬프트 템플릿

```markdown
Django 모델에 Optimistic Locking 패턴을 구현하시오.

대상 모델: PatientCache, Encounter, Order

구현 내용:
1. 모델에 `version` 필드 추가 (PositiveIntegerField, default=0)
2. ViewSet의 update 메서드에서 version 검증
3. version 불일치 시 409 Conflict 반환
4. 성공 시 version 자동 증가

예시 코드:
```python
class PatientCache(models.Model):
    ...
    version = models.PositiveIntegerField(default=0)

    class Meta:
        ...

# ViewSet
def update(self, request, *args, **kwargs):
    instance = self.get_object()
    request_version = request.data.get('version')

    if instance.version != request_version:
        return Response(
            {"error": "Data has been modified by another user"},
            status=status.HTTP_409_CONFLICT
        )

    # Update logic
    instance.version += 1
    instance.save()
    ...
```

테스트 케이스:
- test_optimistic_locking_success: version 일치 시 업데이트 성공
- test_optimistic_locking_conflict: version 불일치 시 409 반환

완료 후 LOG_작업이력.md 업데이트
```

---

## 4️⃣ Pessimistic Locking 구현

### 프롬프트 템플릿

```markdown
Django의 select_for_update()를 사용한 Pessimistic Locking을 구현하시오.

대상: Order 생성 시 재고 차감 (동시성 제어)

구현 내용:
```python
from django.db import transaction

@transaction.atomic
def create_order(self, request, *args, **kwargs):
    # Pessimistic Lock으로 재고 조회
    inventory = Inventory.objects.select_for_update().get(product_id=product_id)

    if inventory.stock < quantity:
        return Response({"error": "Insufficient stock"}, status=400)

    # 재고 차감
    inventory.stock -= quantity
    inventory.save()

    # 주문 생성
    order = Order.objects.create(...)
    return Response(OrderSerializer(order).data, status=201)
```

테스트 케이스:
- test_pessimistic_locking_no_race_condition: 동시 요청 시 재고 정합성 보장
- test_pessimistic_locking_timeout: 잠금 대기 시간 초과 시 에러

완료 후 LOG_작업이력.md 업데이트
```

---

## 5️⃣ Transaction Isolation Level 설정

### 프롬프트 템플릿

```markdown
Django에서 Transaction Isolation Level을 설정하시오.

파일: settings.py

설정 내용:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'isolation_level': 'repeatable read',  # MySQL 기본값
        },
    }
}
```

테스트 시나리오:
1. READ UNCOMMITTED: Dirty Read 발생 확인
2. READ COMMITTED: Non-Repeatable Read 발생 확인
3. REPEATABLE READ: Phantom Read 발생 확인 (MySQL은 방지)
4. SERIALIZABLE: 최고 격리 수준, 동시성 저하

문서 작성:
- 01_doc/20_Transaction_Isolation_가이드.md
- 각 격리 수준의 동작 방식 및 테스트 결과

완료 후 LOG_작업이력.md 업데이트
```

---

## 6️⃣ 동시성 테스트 작성

### 프롬프트 템플릿

```markdown
Django CRUD의 동시성 시나리오를 테스트하시오.

파일: emr/tests/test_concurrency.py

테스트 케이스:
```python
from threading import Thread
from django.test import TestCase

class ConcurrencyTestCase(TestCase):
    def test_race_condition_optimistic_locking(self):
        """두 사용자가 동시에 같은 환자 정보를 수정할 때 한 명만 성공"""
        patient = PatientCache.objects.create(...)

        def update_patient():
            # PATCH /api/emr/patients/{id}/
            ...

        t1 = Thread(target=update_patient)
        t2 = Thread(target=update_patient)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # 검증: 한 명은 200 OK, 한 명은 409 Conflict

    def test_race_condition_pessimistic_locking(self):
        """재고 차감 시 Race Condition 방지"""
        ...

    def test_idempotency(self):
        """같은 요청을 여러 번 전송해도 결과가 동일"""
        ...
```

pytest 실행:
```bash
pytest emr/tests/test_concurrency.py -v
```

모든 테스트가 통과하는지 확인하시오.
```

---

## 7️⃣ 작업 이어서 진행

### 프롬프트 템플릿

```markdown
[LOG_작업이력.md]를 읽고 마지막 작업 상태를 확인한 후,
중단된 작업을 이어서 진행하시오.

완료 후 LOG_작업이력.md 업데이트
```

---

## 8️⃣ 문서 업데이트만 필요한 경우

### 프롬프트 템플릿

```markdown
오늘 작업 내용:
- [작업 1: 예) Optimistic Locking 구현 완료]
- [작업 2: 예) Pessimistic Locking 구현 완료]
- [작업 3: 예) 동시성 테스트 통과]

위 작업을 바탕으로 다음 문서를 업데이트하시오:
1. LOG_작업이력.md (Week X 작업 추가)
2. REF_CLAUDE_CONTEXT.md (필요 시)

변경된 파일 목록과 다음 작업 계획을 요약하시오.
```

---

## 9️⃣ 디버깅 및 문제 해결

### 프롬프트 템플릿

```markdown
다음 오류를 해결하시오:

오류 내용:
[오류 메시지 복사]

관련 파일:
- [파일 경로]

발생 위치:
- [함수/클래스명]

해결 방법을 찾고 코드를 수정한 후,
테스트를 실행하여 문제가 해결되었는지 확인하시오.
```

---

## 🔟 일일 작업 완료 보고

### 프롬프트 템플릿

```markdown
금일 작업 완료.

작업 내용:
- [작업 1]
- [작업 2]
- [작업 3]

변경된 파일:
- [파일 경로 1]
- [파일 경로 2]

다음 작업 계획:
- [다음 작업 1]
- [다음 작업 2]

LOG_작업이력.md에 Week X 작업 내용을 추가하고,
작업 요약을 제공하시오.
```

---

## 📌 자주 사용하는 프롬프트 단축키

### 🔹 빠른 시작
```
[REF_CLAUDE_CONTEXT.md], [LOG_작업이력.md]를 읽고 작업을 시작하시오.
```

### 🔹 작업 이어서
```
[LOG_작업이력.md]에서 마지막 작업 확인 후 이어서 진행
```

### 🔹 문서 업데이트
```
금일 작업: [요약]
LOG_작업이력.md 업데이트
```

### 🔹 테스트 실행
```
pytest emr/tests/ -v 실행 후 결과 보고
```

### 🔹 Django 서버 실행
```
Django 서버 실행 테스트:
cd NeuroNova_02_back_end/01_django_server
python manage.py runserver 0.0.0.0:8000
```

---

## 🎯 Django Concurrency 관련 참고 자료

### Django 공식 문서
- [Django Database Transactions](https://docs.djangoproject.com/en/4.2/topics/db/transactions/)
- [select_for_update()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update)
- [Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)

### 동시성 패턴
- Optimistic Locking: version 필드 활용
- Pessimistic Locking: select_for_update() 활용
- Idempotency: 멱등성 보장 (Idempotency Key)

---

## 💡 프롬프트 작성 팁

### ✅ DO (권장)
- 문서 읽는 순서를 명확히 지정
- 구체적인 작업 목록 제공
- 파일 경로와 구현 내용 명시
- 완료 후 액션(테스트, 문서 업데이트) 명시

### ❌ DON'T (비권장)
- 모호한 지시 ("적절히 구현해줘")
- 순서 없는 작업 나열
- 파일 경로 생략
- 완료 조건 불명확

---

## 📞 참고 문서

- [17_프로젝트_RR_역할분담.md](17_프로젝트_RR_역할분담.md): R&R 정의
- [16_Write_Through_패턴_가이드.md](16_Write_Through_패턴_가이드.md): Write-Through 패턴
- [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md): Claude AI 온보딩
- [LOG_작업이력.md](LOG_작업이력.md): 작업 이력

---

**최종 수정일**: 2025-12-24
**작성자**: Project Team
**버전**: 2.0 (Django Backend 개발자용)
