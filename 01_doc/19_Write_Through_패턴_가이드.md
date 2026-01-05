# 19. Write-Through 패턴 가이드 (DEPRECATED)

> **⚠️ 주의**: 본 문서는 **폐기(DEPRECATED)** 되었습니다.
> 현재 NeuroNova CDSS는 **Outbox Pattern**과 **Direct DB Access**를 사용하여 데이터 동기화를 수행합니다.
> 최신 내용은 [47_FHIR_동기화_Outbox_패턴_명세서.md](47_FHIR_동기화_Outbox_패턴_명세서.md)를 참고하십시오.

---

## 🔒 Write-Through (구버전) vs Outbox (신버전)

| 항목 | Write-Through (폐기됨) | Outbox Pattern (현행) |
|------|------------------------|-----------------------|
| **동기화 시점** | 동기 (Synchronous) | **비동기 (Asynchronous)** |
| **성공 보장** | 외부 API 의존 (API 실패 시 롤백) | **Eventual Consistency** (재시도 보장) |
| **연결 방식** | HTTP/OAuth2 API 호출 | **Direct DB Access (SQL)** |
| **목적** | 즉각적인 정합성 | **시스템 안정성 및 성능** |

본 문서는 기록 보관용으로 남겨둡니다.

---

(이하 기존 내용 생략)
