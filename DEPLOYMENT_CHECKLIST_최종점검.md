# 🚀 NeuroNova CDSS 배포 전 최종 점검 리스트

**작성일**: 2026-01-03
**점검자**: AI Assistant
**배포 환경**: GCP VM + Docker Compose

---

## ✅ 1. 보안 설정 (CRITICAL)

### 1.1 환경 변수 (.env 파일)

**⚠️ 프로덕션 환경에서 반드시 변경해야 할 항목**

| 항목 | 현재 상태 | 프로덕션 필수 변경 | 위험도 |
|------|-----------|-------------------|--------|
| `DJANGO_SECRET_KEY` | `django-insecure-change-this-in-production-...` | ✅ 필수 변경 | 🔴 CRITICAL |
| `DEBUG` | `True` | ✅ `False`로 변경 | 🔴 CRITICAL |
| `ENABLE_SECURITY` | `False` | ✅ `True`로 변경 | 🔴 CRITICAL |
| `DB_PASSWORD` | `cdss_password` | ✅ 강력한 비밀번호로 변경 | 🔴 CRITICAL |
| `DB_ROOT_PASSWORD` | `cdss_root_pass` | ✅ 강력한 비밀번호로 변경 | 🔴 CRITICAL |
| `ORTHANC_PASSWORD` | `orthanc123` | ✅ 강력한 비밀번호로 변경 | 🟡 HIGH |
| `OPENEMR_CLIENT_SECRET` | `8fa14ca8...` | ⚠️ OAuth2 사용 시 변경 | 🟡 HIGH |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | ✅ `False`로 변경 | 🟡 HIGH |
| `ALLOWED_HOSTS` | `*` | ✅ 실제 도메인으로 제한 | 🟡 HIGH |

**보안 강화 명령어**:
```bash
# Django SECRET_KEY 생성
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 강력한 비밀번호 생성 (32자)
openssl rand -base64 32
```

### 1.2 프론트엔드 보안

| 항목 | 현재 상태 | 프로덕션 조치 | 상태 |
|------|-----------|--------------|------|
| `devAutoLogin.js` | 조건부 로딩 | ✅ `NODE_ENV=production` 시 자동 제외 | ✅ 완료 |
| `LoginPage Quick Login` | `process.env.NODE_ENV` 체크 | ✅ 프로덕션에서 자동 비활성화 | ✅ 완료 |
| `REACT_APP_DEV_AUTO_LOGIN` | `.env`에서 설정 | ⚠️ 프로덕션 `.env`에서 `false` 설정 | ⚠️ 확인 필요 |

### 1.3 Docker 보안

| 항목 | 점검 사항 | 상태 |
|------|-----------|------|
| **포트 노출** | 불필요한 외부 포트 노출 최소화 | ⚠️ 점검 필요 |
| **Volume 권한** | `/var/run/docker.sock` 마운트 제거 | ✅ 확인됨 |
| **컨테이너 격리** | User namespace 설정 | ⚠️ 고려 필요 |
| **이미지 보안** | 최신 베이스 이미지 사용 | ✅ 확인됨 |

---

## ✅ 2. Docker 구성 점검

### 2.1 Docker Compose 파일

**파일**: `docker-compose.dev.yml`

| 서비스 | 컨테이너 | 포트 | Health Check | 상태 |
|--------|----------|------|--------------|------|
| nginx | neuronova-nginx-dev | 80:80 | ✅ | ✅ 정상 |
| django | neuronova-django-dev | 내부 8000 | ✅ | ✅ 정상 |
| celery-worker | neuronova-celery-worker-dev | - | ✅ | ✅ 정상 |
| celery-beat | neuronova-celery-beat-dev | - | ❌ | ⚠️ 없음 |
| flower | neuronova-flower-dev | 5555:5555 | ❌ | ⚠️ 없음 |
| cdss-mysql | neuronova-cdss-mysql | 3306:3306 | ✅ | ✅ 정상 |
| redis | neuronova-redis | 6379:6379 | ✅ | ✅ 정상 |
| orthanc | neuronova-orthanc | 8042:8042, 4242:4242 | ✅ | ✅ 정상 |
| openemr | neuronova-openemr | 8081:80, 4443:443 | ✅ | ✅ 정상 |
| openemr-mysql | neuronova-openemr-mysql | 3307:3306 | ✅ | ✅ 정상 |
| hapi-fhir | neuronova-hapi-fhir | 8080:8080 | ✅ | ✅ 정상 |
| prometheus | neuronova-prometheus | 9090:9090 | ✅ | ✅ 정상 |
| grafana | neuronova-grafana | 3002:3000 | ✅ | ✅ 정상 |
| alertmanager | neuronova-alertmanager | 9093:9093 | ✅ | ✅ 정상 |

**총 14개 컨테이너**

### 2.2 외부 노출 포트 (프로덕션에서 조정 필요)

**현재 외부 노출 포트**:
- `80` (Nginx) - ✅ 필수
- `3306` (CDSS MySQL) - 🔴 **위험: 프로덕션에서 내부 전용으로 변경**
- `3307` (OpenEMR MySQL) - 🔴 **위험: 프로덕션에서 내부 전용으로 변경**
- `6379` (Redis) - 🔴 **위험: 프로덕션에서 내부 전용으로 변경**
- `8042` (Orthanc) - 🟡 **선택: 필요시에만 노출**
- `8080` (HAPI FHIR) - 🟡 **선택: 필요시에만 노출**
- `8081` (OpenEMR) - 🟡 **선택: 필요시에만 노출**
- `5555` (Flower) - 🟡 **개발 전용: 프로덕션에서 제거 권장**
- `9090` (Prometheus) - 🟡 **개발 전용: 프로덕션에서 제거 권장**
- `3002` (Grafana) - 🟡 **선택: 필요시에만 노출**
- `9093` (Alertmanager) - 🟡 **개발 전용: 프로덕션에서 제거 권장**

**권장 프로덕션 설정**:
```yaml
# docker-compose.prod.yml에서 포트 매핑 수정
services:
  cdss-mysql:
    ports:
      - "127.0.0.1:3306:3306"  # localhost만 접근 가능

  redis:
    expose:
      - "6379"  # 외부 포트 매핑 제거, 내부 네트워크만
```

---

## ✅ 3. 프론트엔드 빌드 준비

### 3.1 React 앱 빌드 상태

**경로**: `NeuroNova_03_front_end_react/00_test_client`

| 항목 | 점검 사항 | 상태 |
|------|-----------|------|
| `package.json` | 의존성 최신 상태 | ✅ 확인 필요 |
| `.env.production` | 프로덕션 환경 변수 설정 | ⚠️ 생성 필요 |
| `build/` 디렉토리 | 빌드 결과물 존재 | ⚠️ 빌드 필요 |
| `node_modules/` | 용량 (1.2GB) | ⚠️ 배포 시 제외 |

**프로덕션 빌드 명령어**:
```bash
cd NeuroNova_03_front_end_react/00_test_client

# 프로덕션 환경 변수 파일 생성
cp .env.example .env.production

# .env.production 수정
# REACT_APP_API_URL=https://yourdomain.com/api
# REACT_APP_OHIF_VIEWER_ROOT=https://yourdomain.com:8042
# REACT_APP_DEV_AUTO_LOGIN=false
# NODE_ENV=production

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# 빌드 결과물 확인
ls -lh build/
```

### 3.2 배포 전 파일 정리

**자동 정리 스크립트**: `cleanup-for-deployment.bat`

```bash
# Windows에서 실행
cleanup-for-deployment.bat

# 또는 수동 삭제
rm -rf NeuroNova_03_front_end_react/00_test_client/node_modules
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf NeuroNova_02_back_end/02_django_server/venv
rm -f NeuroNova_02_back_end/02_django_server/.env.local
rm -f logs/*.log
```

**삭제 대상**:
- ✅ `__pycache__/` (모든 위치)
- ✅ `*.pyc` 파일
- ✅ `venv/` (183MB)
- ✅ `node_modules/` (1.2GB, 선택)
- ✅ `.env.local`
- ✅ `.DS_Store`
- ✅ `logs/*.log`

**예상 절약 용량**: ~1.5GB

---

## ✅ 4. 백엔드 마이그레이션 및 시딩

### 4.1 데이터베이스 마이그레이션

**경로**: `NeuroNova_02_back_end/02_django_server`

| 항목 | 명령어 | 상태 |
|------|--------|------|
| 마이그레이션 파일 생성 | `python manage.py makemigrations` | ✅ 필요 시 |
| 마이그레이션 적용 | `python manage.py migrate` | ✅ 자동 실행 (docker-compose) |
| 마이그레이션 확인 | `python manage.py showmigrations` | ⚠️ 수동 확인 필요 |

### 4.2 데이터 시딩

**시딩 스크립트**:
- `seed_minimal.py` - 최소 테스트 데이터 (관리자 + 5명 환자)
- `seed_full_system_test_data.py` - 전체 시스템 테스트 데이터

```bash
# Docker 컨테이너 내부에서 실행
docker exec -it neuronova-django-dev bash

# 시딩 실행
python manage.py shell < scripts/seed_minimal.py

# 또는 전체 시딩
python manage.py shell < scripts/seed_full_system_test_data.py
```

### 4.3 Static 파일 수집

```bash
# Docker 컨테이너 내부
python manage.py collectstatic --noinput

# 결과 확인
ls -lh /app/staticfiles/
```

---

## ✅ 5. 배포 문서 검토

### 5.1 필수 문서

| 문서 | 경로 | 최신 업데이트 | 상태 |
|------|------|--------------|------|
| **배포 가이드** | `01_doc/12_GCP_배포_가이드.md` | 2026-01-03 | ✅ 최신 |
| **시딩 가이드** | `01_doc/초기_데이터_시딩_가이드.md` | 2026-01-02 | ✅ 최신 |
| **작업 이력** | `01_doc/LOG_작업이력.md` | 2026-01-03 Day 19-4 | ✅ 최신 |
| **API 문서** | `01_doc/12_API_사용_가이드.md` | 2025-12-29 | ✅ 최신 |
| **FHIR 통합 가이드** | `01_doc/13_FHIR_통합_가이드.md` | 2025-12-29 | ✅ 최신 |
| **OpenEMR OAuth2** | `01_doc/50_OpenEMR_OAuth2_설정_가이드.md` | 2025-12-28 | ✅ 최신 |

### 5.2 README 파일

| 파일 | 용도 | 상태 |
|------|------|------|
| `README.md` (루트) | 프로젝트 개요 | ⚠️ 업데이트 필요 |
| `README_자동실행.md` | Windows 자동 시작 | ✅ 최신 |
| `NeuroNova_02_back_end/README.md` | 백엔드 설명 | ⚠️ 업데이트 권장 |
| `NeuroNova_03_front_end_react/README.md` | 프론트엔드 설명 | ⚠️ 업데이트 권장 |

---

## ✅ 6. 프로덕션 배포 단계별 체크리스트

### Phase 1: 사전 준비 (로컬)

- [ ] 1.1. Git 저장소 최신 상태 확인 (`git status`)
- [ ] 1.2. 모든 변경사항 커밋 및 푸시
- [ ] 1.3. `.env.example` 파일 최신화
- [ ] 1.4. `cleanup-for-deployment.bat` 실행
- [ ] 1.5. React 프로덕션 빌드 생성
- [ ] 1.6. 배포 파일 압축 (선택)

### Phase 2: GCP VM 준비

- [ ] 2.1. GCP VM 접속 (PuTTY 또는 SSH)
- [ ] 2.2. Docker 및 Docker Compose 설치 확인
- [ ] 2.3. 방화벽 규칙 확인 (80, 443 포트)
- [ ] 2.4. 고정 IP 주소 확인 (`34.71.151.117`)
- [ ] 2.5. Git 저장소 클론 또는 업데이트

### Phase 3: 환경 설정

- [ ] 3.1. `.env` 파일 생성 (WinSCP로 전송 또는 수동 생성)
- [ ] 3.2. **CRITICAL** 보안 변수 변경:
  - [ ] `DJANGO_SECRET_KEY` 변경
  - [ ] `DEBUG=False` 설정
  - [ ] `ENABLE_SECURITY=True` 설정
  - [ ] `DB_PASSWORD` 변경
  - [ ] `DB_ROOT_PASSWORD` 변경
  - [ ] `ORTHANC_PASSWORD` 변경
  - [ ] `ALLOWED_HOSTS` 도메인 지정
  - [ ] `CORS_ALLOW_ALL_ORIGINS=False` 설정
- [ ] 3.3. React `.env.production` 설정 확인

### Phase 4: Docker 배포

- [ ] 4.1. Docker 이미지 빌드
  ```bash
  docker-compose -f docker-compose.dev.yml build
  ```
- [ ] 4.2. 볼륨 초기화 (필요 시)
  ```bash
  docker-compose -f docker-compose.dev.yml down -v
  ```
- [ ] 4.3. 서비스 시작
  ```bash
  docker-compose -f docker-compose.dev.yml up -d
  ```
- [ ] 4.4. 컨테이너 상태 확인
  ```bash
  docker-compose -f docker-compose.dev.yml ps
  ```
- [ ] 4.5. 로그 확인
  ```bash
  docker-compose -f docker-compose.dev.yml logs -f django
  ```

### Phase 5: 데이터베이스 초기화

- [ ] 5.1. 마이그레이션 확인
  ```bash
  docker exec -it neuronova-django-dev python manage.py showmigrations
  ```
- [ ] 5.2. Static 파일 수집 확인
  ```bash
  docker exec -it neuronova-django-dev ls /app/staticfiles/
  ```
- [ ] 5.3. 테스트 데이터 시딩
  ```bash
  docker exec -it neuronova-django-dev python manage.py shell < scripts/seed_minimal.py
  ```
- [ ] 5.4. 관리자 계정 생성 (필요 시)
  ```bash
  docker exec -it neuronova-django-dev python manage.py create_test_users
  ```

### Phase 6: 검증 및 테스트

- [ ] 6.1. Health Check 확인
  ```bash
  curl http://localhost/api/acct/login/
  ```
- [ ] 6.2. Nginx 접속 확인
  ```bash
  curl http://localhost/
  ```
- [ ] 6.3. Django API 확인
  ```bash
  curl http://localhost/api/
  ```
- [ ] 6.4. Orthanc PACS 확인
  ```bash
  curl http://localhost:8042/
  ```
- [ ] 6.5. 브라우저 접속 테스트
  - [ ] React 앱 로딩 확인
  - [ ] 로그인 기능 확인
  - [ ] API 통신 확인
  - [ ] DICOM Viewer 확인

### Phase 7: 모니터링 설정

- [ ] 7.1. Grafana 접속 확인 (`http://VM_IP:3002`)
- [ ] 7.2. Prometheus 메트릭 수집 확인 (`http://VM_IP:9090`)
- [ ] 7.3. Flower Celery 모니터링 확인 (`http://VM_IP:5555`)
- [ ] 7.4. 알림 설정 (Alertmanager)

### Phase 8: HTTPS 설정 (Cloudflare)

- [ ] 8.1. Cloudflare DNS 레코드 추가
  - Type: `A`
  - Name: `@` 또는 `cdss`
  - Content: `34.71.151.117`
  - Proxy: `Proxied` (오렌지 구름)
- [ ] 8.2. SSL/TLS 설정: `Full` 모드
- [ ] 8.3. HTTPS 리다이렉트 활성화
- [ ] 8.4. HTTPS 접속 확인

### Phase 9: 백업 및 복구 계획

- [ ] 9.1. 데이터베이스 백업 스크립트 설정
- [ ] 9.2. Volume 백업 확인
- [ ] 9.3. 복구 절차 문서화
- [ ] 9.4. 정기 백업 스케줄 설정 (Cron)

### Phase 10: 최종 점검

- [ ] 10.1. 보안 점검 완료 확인
- [ ] 10.2. 성능 테스트 실행
- [ ] 10.3. 로그 모니터링 확인
- [ ] 10.4. 배포 문서 업데이트
- [ ] 10.5. 팀원 공유 및 교육

---

## ⚠️ 7. 알려진 이슈 및 주의사항

### 7.1 Frontend 이슈 (0103_문제.md 참조)

**해결 완료 (Day 19-4)**:
- ✅ P-007: LoginPage 비밀번호 하드코딩 → 프로덕션 자동 비활성화
- ✅ P-001/P-017: Mock health check → 실제 API 연동
- ✅ P-003: Pagination 미적용 → 20개씩 페이징
- ✅ P-032: OHIF Viewer URL → Orthanc Explorer 2 연동
- ✅ P-013: 비밀번호 로깅 → 로깅 제거
- ✅ P-004: 환자 컨텍스트 유실 → URL 파라미터 추가
- ✅ P-008, P-006, P-014, P-015, P-016, P-019, P-029, P-030, P-031 수정 완료

**남은 이슈 (Medium/Low, 총 23건)**:
- P-002, P-005: UI/UX 개선 (우선순위 낮음)
- P-010 ~ P-030: 개선 사항 (배포 후 점진적 수정 가능)

### 7.2 Backend 이슈

**OpenEMR 연동**:
- ⚠️ `SKIP_OPENEMR_INTEGRATION=True` 설정 시 Mock 데이터 사용
- OAuth2 클라이언트 등록 필요 시 `50_OpenEMR_OAuth2_설정_가이드.md` 참조

**FHIR 동기화**:
- ✅ Celery Worker 구현 완료 (Day 19-1)
- ⚠️ HAPI FHIR 서버 OAuth2 토큰 설정 필요 시 환경 변수 추가

### 7.3 성능 고려사항

**예상 리소스 사용량**:
- **메모리**: ~10GB (14개 컨테이너)
- **디스크**: ~20GB (초기), DICOM 데이터 증가에 따라 확장
- **CPU**: 평균 20-30%, 피크 시 60-80%

**권장 모니터링 지표**:
- Django 응답 시간 < 500ms
- Celery Task 처리율 > 90%
- MySQL 연결 풀 사용률 < 70%
- Redis 메모리 사용률 < 80%

---

## ✅ 8. 긴급 상황 대응

### 8.1 서비스 중단 시

```bash
# 모든 서비스 중지
docker-compose -f docker-compose.dev.yml down

# 로그 확인
docker-compose -f docker-compose.dev.yml logs --tail=100 [service-name]

# 특정 서비스 재시작
docker-compose -f docker-compose.dev.yml restart django

# 서비스 재시작
docker-compose -f docker-compose.dev.yml up -d
```

### 8.2 데이터베이스 복구

```bash
# MySQL 백업
docker exec neuronova-cdss-mysql mysqldump -u root -p cdss_db > backup_$(date +%Y%m%d).sql

# MySQL 복원
docker exec -i neuronova-cdss-mysql mysql -u root -p cdss_db < backup_YYYYMMDD.sql
```

### 8.3 롤백 절차

```bash
# 이전 Git 커밋으로 복원
git log --oneline
git checkout [commit-hash]

# Docker 이미지 재빌드
docker-compose -f docker-compose.dev.yml build

# 서비스 재시작
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📊 9. 배포 후 확인 사항

### 9.1 기능 테스트

- [ ] 로그인/로그아웃
- [ ] 환자 목록 조회
- [ ] 진료 기록 생성
- [ ] 처방 생성
- [ ] 검사 결과 조회
- [ ] DICOM 이미지 조회 (OHIF Viewer)
- [ ] AI 분석 요청 (Celery Task)
- [ ] FHIR 동기화 (Celery Beat)

### 9.2 성능 테스트

```bash
# Apache Bench 간단 테스트
ab -n 1000 -c 10 http://your-domain/api/acct/login/

# 결과 확인
# - Requests per second
# - Time per request
# - Transfer rate
```

### 9.3 보안 스캔 (권장)

```bash
# Docker 이미지 취약점 스캔
docker scan neuronova-django-dev

# Nikto 웹 서버 스캔
nikto -h http://your-domain
```

---

## 🎯 최종 체크

**배포 준비 완료 기준**:

- [x] 모든 CRITICAL 보안 항목 변경 완료
- [ ] 프로덕션 `.env` 파일 생성 및 검증
- [ ] React 프로덕션 빌드 완료
- [ ] Docker Compose 파일 프로덕션 버전 준비
- [ ] 데이터베이스 백업 계획 수립
- [ ] 모니터링 대시보드 설정
- [ ] 배포 문서 팀원 공유

**배포 승인 조건**:
1. ✅ 보안 점검 완료
2. ⚠️ 프로덕션 환경 변수 설정 완료
3. ⚠️ 백업 및 복구 계획 수립
4. ✅ 배포 문서 최신화
5. ⚠️ 배포 후 모니터링 계획 수립

---

**작성자**: Claude (AI Assistant)
**검토 필요**: Human Developer
**다음 단계**: 프로덕션 환경 변수 설정 → Docker 빌드 → 배포 실행
