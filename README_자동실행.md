# NeuroNova CDSS - 자동 실행 가이드

**최종 수정일**: 2026-01-02
**목적**: 시스템 재시작 후에도 모든 서비스가 자동으로 정상 작동하도록 설정

---

## 🚀 빠른 시작

### Option 1: 통합 자동 시작 스크립트 (권장)

```bash
# 루트 디렉토리에서 실행
d:\1222\NeuroNova_v1\start-all-services.bat
```

**기능**:
- ✅ Docker Desktop 자동 시작 (실행 중이 아닐 경우)
- ✅ Docker Compose로 전체 스택 시작 (14개 컨테이너)
- ✅ 서비스 초기화 대기 (30초)
- ✅ React 클라이언트 선택적 시작
- ✅ 접속 URL 및 로그 명령어 안내

---

### Option 2: 개별 서비스 시작

#### 1. Docker 서비스 시작

```bash
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. React 클라이언트 시작

```bash
cd d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client
start-react.bat
```

---

## 🔧 시작 프로그램 등록 (Windows)

### 방법: 시스템 부팅 시 자동 시작

1. **Win + R** 키 누르기
2. `shell:startup` 입력 후 **Enter**
3. 시작 프로그램 폴더가 열림
4. `d:\1222\NeuroNova_v1\start-all-services.bat` 파일의 **바로가기** 생성
5. 바로가기를 시작 프로그램 폴더에 붙여넣기

**결과**: 다음 부팅 시 자동으로 NeuroNova 서비스 시작

---

## 📋 서비스 상태 확인

### Docker 컨테이너 상태

```bash
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml ps
```

**예상 출력**:
```
NAME                          STATUS                      PORTS
neuronova-django-dev          Up 10 minutes (healthy)     0.0.0.0:8000->8000/tcp
neuronova-celery-worker-dev   Up 10 minutes (healthy)
neuronova-celery-beat-dev     Up 10 minutes (healthy)
neuronova-flower-dev          Up 10 minutes               0.0.0.0:5555->5555/tcp
neuronova-redis-dev           Up 10 minutes (healthy)     0.0.0.0:6379->6379/tcp
...
```

### 서비스 접속 URL

| 서비스 | URL | 계정 | 설명 |
|--------|-----|------|------|
| **Django API** | http://localhost/api | - | REST API (Nginx 경유) |
| **Swagger UI** | http://localhost/api/docs/ | - | API 문서 |
| **React Client** | http://localhost:3001 | doctor/doctor123 | 개발 자동 로그인 |
| **Grafana** | http://localhost:3000 | admin/admin123 | 시스템 모니터링 |
| **OpenEMR** | http://localhost:8081 | admin/pass | EMR 시스템 |
| **Orthanc PACS** | http://localhost:8042 | orthanc/orthanc | DICOM 서버 |
| **Flower** | http://localhost:5555 | - | Celery 모니터링 |

---

## 🛠️ 문제 해결

### 문제 1: Docker Desktop이 시작되지 않음

**증상**:
```
ERROR: Cannot connect to the Docker daemon
```

**해결**:
1. Docker Desktop 수동 시작
2. 작업 표시줄에서 Docker 아이콘 확인 (초록색 = 정상)
3. 30초 대기 후 다시 시도

---

### 문제 2: 포트 충돌 (포트 이미 사용 중)

**증상**:
```
ERROR: for django  Cannot start service django: Ports are not available
```

**해결**:
```bash
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F

# 또는 Docker Compose 중지 후 재시작
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

---

### 문제 3: React 시작 실패 (WSL 문제)

**증상**:
```
ERROR: WSL이 설치되어 있지 않습니다
```

**해결**:
```bash
# WSL 설치 (PowerShell 관리자 권한)
wsl --install -d Ubuntu-22.04

# 설치 후 재부팅
# Ubuntu 사용자 계정 생성
# 다시 start-react.bat 실행
```

---

### 문제 4: 일부 컨테이너가 Unhealthy

**증상**:
```
neuronova-django-dev  Up 5 minutes (unhealthy)
```

**해결**:
```bash
# 로그 확인
docker-compose -f docker-compose.dev.yml logs django

# 컨테이너 재시작
docker-compose -f docker-compose.dev.yml restart django

# 데이터베이스 마이그레이션 확인
docker exec neuronova-django-dev python manage.py migrate
```

---

## 📝 서비스 중지

### 전체 중지

```bash
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml down
```

### 특정 서비스만 중지

```bash
# Django만 중지
docker-compose -f docker-compose.dev.yml stop django

# React 중지 (WSL 창에서 Ctrl+C)
```

---

## 🔍 로그 확인

### 전체 로그 (실시간)

```bash
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml logs -f
```

### 특정 서비스 로그

```bash
# Django 로그
docker-compose -f docker-compose.dev.yml logs -f django

# Celery Worker 로그
docker-compose -f docker-compose.dev.yml logs -f celery-worker

# Nginx 로그
docker-compose -f docker-compose.dev.yml logs -f nginx
```

---

## ✅ 동작 확인 체크리스트

시스템이 정상 작동하는지 확인하십시오:

### Docker 서비스
- [ ] `docker ps`로 14개 컨테이너 실행 확인
- [ ] `docker-compose ps`로 모든 서비스 healthy 확인
- [ ] Grafana 접속 (http://localhost:3000)
- [ ] Swagger UI 접속 (http://localhost/api/docs/)

### React 클라이언트
- [ ] http://localhost:3001 접속
- [ ] 자동 로그인 (doctor 계정)
- [ ] 대시보드 정상 표시
- [ ] UC02 (EMR) 환자 목록 조회 성공
- [ ] UC05 (RIS) Orthanc 환자 목록 조회 성공

### API 테스트
- [ ] 로그인 API: `curl http://localhost/api/acct/login/ -X POST ...`
- [ ] 환자 목록 API: `curl http://localhost/api/emr/patients/`
- [ ] Swagger에서 API 테스트 실행

---

## 🎯 전원 켜자마자 작동 시나리오

### 시나리오: 컴퓨터 전원 ON → NeuroNova 자동 시작

1. **부팅** (Windows 시작)
2. **시작 프로그램 실행** (`start-all-services.bat` 바로가기)
3. **Docker Desktop 자동 시작** (60초 대기)
4. **Docker Compose 실행** (14개 컨테이너)
5. **서비스 초기화 대기** (30초)
6. **React 클라이언트 선택** (Y/N)
7. **완료!**

**예상 소요 시간**: 약 3~5분 (컴퓨터 사양에 따라)

---

## 📚 관련 문서

### 설정 가이드
- [REF_CLAUDE_ONBOARDING_QUICK.md](01_doc/REF_CLAUDE_ONBOARDING_QUICK.md) - 빠른 온보딩
- [12_GCP_배포_가이드.md](01_doc/12_GCP_배포_가이드.md) - 배포 가이드
- [40_Docker_개발_가이드.md](01_doc/40_Docker_개발_가이드.md) - Docker 상세 가이드

### React 가이드
- [NeuroNova_03_front_end_react/00_test_client/사용방법_설명문서.md](NeuroNova_03_front_end_react/00_test_client/사용방법_설명문서.md)
- [NeuroNova_03_front_end_react/00_test_client/FRONTEND_WORK_LOG.md](NeuroNova_03_front_end_react/00_test_client/FRONTEND_WORK_LOG.md)

### 문제 해결
- [51_OpenEMR_인증_문제_해결_보고서.md](01_doc/51_OpenEMR_인증_문제_해결_보고서.md)
- [50_OpenEMR_OAuth2_설정_가이드.md](01_doc/50_OpenEMR_OAuth2_설정_가이드.md)

---

## 💡 팁

### 개발 효율성 팁

1. **VSCode에서 터미널 2개 사용**:
   - 터미널 1: Docker 로그 (`docker-compose logs -f`)
   - 터미널 2: React WSL (`wsl` → `npm start`)

2. **브라우저 북마크 폴더 생성**:
   - 폴더명: "NeuroNova Dev"
   - 포함: Grafana, Swagger, React, Orthanc, OpenEMR

3. **Git 커밋 전 체크**:
   ```bash
   # 테스트 실행
   docker exec neuronova-django-dev python manage.py test

   # 코드 린트
   docker exec neuronova-django-dev flake8 --max-line-length=120
   ```

---

**문서 버전**: 1.0
**최종 업데이트**: 2026-01-02
**작성자**: NeuroNova Development Team
