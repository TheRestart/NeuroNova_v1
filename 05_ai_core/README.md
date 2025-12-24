# NeuroNova AI Core

**모듈 소유자**: AI 코어 개발팀 (타 팀원)
**현재 담당자**: Django Backend 개발자 (본인)
**상태**: 타 팀원 영역 - 수정 금지
**최종 수정일**: 2025-12-24

---

## ⚠️ 중요: 역할 분담

이 디렉토리(`05_ai_core/`)는 **AI 코어 개발팀의 영역**입니다.

### Django Backend 개발자 (본인)의 책임 범위

**✅ 담당:**
- Django REST API 개발 (UC01~UC09)
- 데이터 충돌 없는 CRUD 구현
- Transaction 관리 및 동시성 제어
- OpenEMR, Orthanc, FHIR 연동

**❌ 제외 (타 팀원 담당):**
- AI 모델 개발 (PyTorch, MONAI)
- DICOM 전처리 파이프라인
- Flask AI Serving
- 이 디렉토리의 코드 수정

---

## 📋 AI Core 개요

NeuroNova AI Core는 **Flask 기반 AI 추론 서버**로, MONAI 프레임워크를 사용한 의료 영상 분석 모듈입니다.

**주요 기능:**
- MRI 종양 분류 (3D CNN)
- 종양 세그멘테이션 (U-Net 3D)
- DICOM 전처리 파이프라인

**기술 스택:**
- Flask 3.0 + MONAI 1.3 + PyTorch 2.0
- GPU/CPU 추론 지원

---

## 🔗 통합 정보 (Django Backend 개발자용)

### Interface Specification

AI 모듈과 Django Backend의 통합은 **Week 13 (통합 단계)**에 진행됩니다.

**통합 구조:**
```
Django API → RabbitMQ Queue → Flask AI Server → AI Model
                                      ↓
                                  추론 결과
                                      ↓
                              Django DB 저장
```

**현재 상태:**
- ✅ RabbitMQ Queue 인프라 준비 완료 (UC06)
- ⏸️ Flask AI Server 통합 대기 (타 팀원)
- ⏸️ AI 모델 개발 대기 (타 팀원)

### API 연동 예정 (Week 13)

**Django → AI 연동 흐름:**
1. Django API: `POST /api/ai/submit/` - AI Job 제출
2. RabbitMQ: `ai_jobs` 큐에 메시지 추가
3. Flask AI Server: 큐에서 메시지 수신, 추론 실행
4. Flask AI Server: 결과를 Django API로 전송
5. Django API: `AIJob` 모델 업데이트 (status: COMPLETED)

**참고 문서:**
- [interface_spec_template.md](interface_spec_template.md) - AI 모듈 인터페이스 규격
- [../01_doc/17_프로젝트_RR_역할분담.md](../01_doc/17_프로젝트_RR_역할분담.md) - R&R 정의

---

## 📁 디렉토리 구조 (참고용)

```
05_ai_core/
├── models/                      # AI 모델 정의 (타 팀원)
├── preprocessing/               # 전처리 파이프라인 (타 팀원)
├── inference/                   # 추론 로직 (타 팀원)
├── tests/                       # 단위 테스트 (타 팀원)
├── interface_spec_template.md   # Interface Specification 템플릿
└── README.md                    # [이 파일]
```

---

## 🚫 주의 사항

### Django Backend 개발자는 이 디렉토리를 수정하지 마세요

**이유:**
1. **역할 분리**: AI 모델 개발은 AI 코어 팀의 책임
2. **독립 개발**: 각 팀은 자신의 영역에만 집중
3. **통합 시점**: Week 13에 Interface Specification으로 통합

**필요한 작업:**
- Django Backend 작업은 `NeuroNova_02_back_end/01_django_server/` 디렉토리에서 진행
- AI 연동은 `ai/` 앱 (UC06)에서 RabbitMQ Queue로 처리

---

## 📞 문의

**AI 코어 개발 관련 문의:**
- AI 코어 개발팀 (타 팀원)

**Django Backend 개발 관련 문의:**
- [17_프로젝트_RR_역할분담.md](../01_doc/17_프로젝트_RR_역할분담.md) 참조

---

**Last Updated**: 2025-12-24
**Version**: 2.0 (Django Backend 개발자용 안내)
**Author**: Project Team
