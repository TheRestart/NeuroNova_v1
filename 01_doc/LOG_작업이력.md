# 작업 이력 (Work Log)

**최종 수정일**: 2025-12-24
**현재 상태**: Week 5 진행 중 - 병렬 데이터 전달 아키텍처(Parallel Dual-Write) 적용 완료

> [!NOTE]
> 시스템 아키텍처, 사용자 역할(RBAC), 상세 모듈 설계 등 기술 참조 정보는 **[REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md)**를 참조하십시오. 이 문서는 일자별 작업 진행 상황과 변경 이력만을 기록합니다.

---

## 📈 주차별 요약

- **Week 1**: 프로젝트 초기 설정, UC1(인증/권한), UC9(감사 로그 기본) 완료
- **Week 2**: UC2(EMR) OpenEMR 연동, UC7(알림 레이아웃), React 초기 설정 완료
- **Week 3**: UC5(RIS) Orthanc 연동, UC6(AI) Queue 인프라, React 대시보드 완성
- **Week 4**: 데이터 정합성(Locking), 멱등성(Idempotency), AI R&R 정의, OCS 고도화 완료
- **Week 5**: Parallel Dual-Write 아키텍처 리팩토링 및 문서 최적화 (진행 중)

---

## 📅 상세 작업 로그

### Week 5 (2025-12-24 ~)
- **2025-12-24**:
  - [x] **Parallel Dual-Write 리팩토링**: `Patient`, `Encounter`, `Order` 서비스를 병렬 데이터 전달 구조로 변경
  - [x] **상태 보고 고도화**: API 응답에 테이블별 저장 성공 여부(`persistence_status`) 및 한글 메시지 적용
  - [x] **문서 최적화**: `REF_CLAUDE_CONTEXT.md`를 SSOT로 설정하고 `LOG_작업이력`, `업무계획서`, `인수인계 문서` 중복 제거

### Week 4
- **2025-12-24**:
  - [x] 낙관적/비관적 락킹 전략 구현 (`version` 필드 및 `select_for_update`)
  - [x] 멱등성 미들웨어(`IdempotencyMiddleware`) 및 `X-Idempotency-Key` 적용
  - [x] AI 코어 개발 R&R 및 인터페이스 규격 정의
- **2025-12-23**:
  - [x] OCS(처방) 고도화: `OrderItem` CRUD 및 ID 생성 버그 수정
  - [x] Write-Through 패턴 적용 (FHIR Adapter 연동)
  - [x] 종합 테스트 대시보드(`/api/emr/comprehensive-test/`) 구축

### Week 3
- [x] Orthanc PACS (UC5) 연동 클라이언트 및 모델 구현
- [x] RabbitMQ (UC6) AI Queue 인프라 구축
- [x] React 역할별 대시보드 및 JWT 인증 연동 완성

### Week 2
- [x] OpenEMR (UC2) REST API 연동 및 Patient/Encounter 모델 구현
- [x] EMR 테스트 UI 및 유닛 테스트 환경 구축

### Week 1
- [x] Django 프로젝트 및 MySQL 초기 환경 설정
- [x] 7개 사용자 역할(RBAC) 커스텀 User 모델 구현
- [x] JWT 기반 인증 시스템 구축
