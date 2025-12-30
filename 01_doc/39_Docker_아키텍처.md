# NeuroNova Docker 아키텍처 설명서

**작성일**: 2025-12-30
**버전**: v2.1
**목적**: Docker 구성의 설계 원리와 구현 방법 설명

---

## 📋 목차

1. [설계 원칙](#설계-원칙)
2. [아키텍처 계층 구조](#아키텍처-계층-구조)
3. [서비스별 상세 설명](#서비스별-상세-설명)
4. [네트워크 설계](#네트워크-설계)
5. [볼륨 관리](#볼륨-관리)
6. [보안 설계](#보안-설계)
7. [성능 최적화](#성능-최적화)
8. [개발 vs 프로덕션](#개발-vs-프로덕션)

---

## 🎯 설계 원칙

### 1. Architecture v2.1 완벽 구현

**핵심 목표**: 문서화된 v2.1 아키텍처를 Docker로 완벽히 재현

```
[06_시스템_아키텍처_v2.md] 문서 → Docker 구성 1:1 매핑
```

**구현된 v2.1 특징**:
- ✅ **Secure Proxy Pattern**: Django JWT 검증 + Nginx X-Accel-Redirect
- ✅ **Multi-SPA Strategy**: React Main + OHIF Viewer 독립 빌드
- ✅ **Internal Routing**: Orthanc 등 내부 서비스 외부 접속 차단
- ✅ **HTJ2K Pipeline**: Celery 기반 이미지 변환 공장

### 2. 개발 환경 최적화

**목표**: 빠른 개발 사이클 + 프로덕션 유사성

- **Hot Reload**: Django/Celery 소스 코드 볼륨 마운트
- **디버깅 편의성**: 개발용 직접 포트 노출
- **로그 가시성**: 실시간 로그 스트리밍
- **재현 가능성**: `.env` 파일로 환경 격리

### 3. 단일 진실의 원천 (Single Source of Truth)

**이전 문제점**:
```
루트/docker-compose.yml
03_openemr_server/docker-compose.yml
04_ohif_viewer/docker-compose.yml  ← 삭제됨
05_orthanc_pacs/docker-compose.yml
06_hapi_fhir/docker-compose.yml
07_redis/docker-compose.yml
```
→ 7개 파일 분산, 중복 정의, 네트워크 불일치

**v2.1 해결책**:
```
docker-compose.dev.yml  ← 하나의 통합 파일
```
→ 모든 서비스 중앙 관리, 네트워크 통합

### 4. 보안 우선 (Security First)

- `.env` 파일 Git 추적 제외
- 내부 서비스 외부 포트 차단
- Nginx를 통한 통합 게이트웨이
- JWT 기반 인증/인가

---

## 🏗️ 아키텍처 계층 구조

### 계층 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Ingress (Gateway)                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ nginx:80                                                │ │
│ │ - Reverse Proxy                                         │ │
│ │ - Static File Server (React, OHIF)                     │ │
│ │ - X-Accel-Redirect Handler                             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Application (Backend)                              │
│ ┌──────────────┬──────────────┬──────────────┬───────────┐  │
│ │ django:8000  │ celery-worker│ celery-beat  │ flower    │  │
│ │ - REST API   │ - HTJ2K 변환 │ - Scheduler  │ - Monitor │  │
│ │ - JWT Auth   │ - AI Tasks   │ - Periodic   │           │  │
│ │ - Proxy      │ - FHIR Sync  │              │           │  │
│ └──────────────┴──────────────┴──────────────┴───────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Data & Integration (Internal Only)                 │
│ ┌─────────┬─────────┬──────────┬───────────┬─────────────┐  │
│ │ MySQL   │ Redis   │ Orthanc  │ OpenEMR   │ HAPI FHIR   │  │
│ │ :3306   │ :6379   │ :8042    │ :8081     │ :8080       │  │
│ │ (CDSS)  │ (Cache) │ (PACS)   │ (EMR)     │ (FHIR)      │  │
│ │         │ (Broker)│ HTJ2K    │ +MariaDB  │             │  │
│ └─────────┴─────────┴──────────┴───────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Observability (Monitoring & Alerting)              │
│ ┌────────────────┬────────────────┬───────────────────────┐  │
│ │ Prometheus     │ Grafana        │ Alertmanager          │  │
│ │ :9090          │ :3000          │ :9093                 │  │
│ │ (Metrics)      │ (Dashboard)    │ (Alert Routing)       │  │
│ │ Time-series DB │ Visualization  │ Code Blue Alerts      │  │
│ └────────────────┴────────────────┴───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 계층별 책임

| 계층 | 역할 | 외부 노출 | 볼륨 | 의존성 |
|------|------|-----------|------|--------|
| **Ingress** | 트래픽 라우팅, 정적 파일 서빙, 보안 프록시 | ✅ Port 80 | 정적 파일 (ro) | django, orthanc |
| **Application** | 비즈니스 로직, 인증, 비동기 작업 | ⚠️ 개발용만 | 소스 코드 (rw) | MySQL, Redis, Orthanc |
| **Data** | 데이터 저장, 의료 표준 연동 | ❌ 내부 전용 | DB/PACS 데이터 | - |
| **Observability** | 시스템 모니터링, 알림, 메트릭 수집 | ⚠️ 개발용만 | 메트릭 데이터 | Prometheus |

---

## 🔧 서비스별 상세 설명

### 1. Nginx (Gateway)

**Docker 설정**:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - ./static/react-main:/var/www/react-main:ro
    - ./static/ohif-dist:/var/www/ohif-dist:ro
  depends_on:
    - django
    - orthanc
```

**핵심 기능**:

1. **Reverse Proxy**
   - `/api/*` → Django API (프록시)
   - `/flower/` → Flower 모니터링

2. **Static File Server**
   - `/` → React Main SPA (`/var/www/react-main`)
   - `/pacs-viewer/` → OHIF Viewer (`/var/www/ohif-dist`)

3. **Secure Proxy (v2.1 핵심)**
   ```nginx
   location /internal-orthanc/ {
       internal;  # 외부 접속 차단!
       proxy_pass http://orthanc:8042/;
   }
   ```
   - Django가 `X-Accel-Redirect` 헤더 반환
   - Nginx가 헤더 인터셉트 → Orthanc 내부 접근
   - 클라이언트에 데이터 스트리밍

**왜 Alpine 이미지?**
- 경량 (5MB vs 130MB)
- 보안 취약점 최소화
- 빠른 빌드/배포

---

### 2. Django (Main API)

**Docker 설정**:
```yaml
django:
  build:
    context: ./NeuroNova_02_back_end/02_django_server
    dockerfile: Dockerfile
  command: >
    sh -c "python manage.py migrate --noinput &&
           python manage.py collectstatic --noinput &&
           python manage.py runserver 0.0.0.0:8000"
  volumes:
    - ./NeuroNova_02_back_end/02_django_server:/app  # Hot Reload
  environment:
    - DB_HOST=cdss-mysql  # Docker 내부 DNS
    - REDIS_HOST=redis
    - ORTHANC_API_URL=http://orthanc:8042
```

**핵심 특징**:

1. **Hot Reload (개발 전용)**
   - 소스 코드 볼륨 마운트 (`/app`)
   - `runserver`가 파일 변경 감지 → 자동 재시작

2. **Multi-Stage Command**
   - `migrate`: DB 스키마 업데이트
   - `collectstatic`: 정적 파일 수집 (Admin UI)
   - `runserver`: 개발 서버 실행

3. **Internal DNS**
   - `cdss-mysql`, `redis`, `orthanc` → Docker 내부 DNS 자동 해석
   - 컨테이너명으로 직접 통신

**Dockerfile 구조**:
```dockerfile
FROM python:3.12-slim
# System dependencies (MySQL client, DICOM libs)
RUN apt-get install -y default-libmysqlclient-dev gcc
# Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Medical imaging libraries
RUN pip install pydicom pillow pylibjpeg
```

---

### 3. Celery Worker (Async Processing Factory)

**Docker 설정**:
```yaml
celery-worker:
  build:
    dockerfile: Dockerfile.celery
  command: celery -A cdss_backend worker -l info --concurrency=4
  volumes:
    - ./NeuroNova_02_back_end/02_django_server:/app
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
```

**핵심 역할**:

1. **HTJ2K 변환 공장**
   ```python
   @shared_task
   def convert_dicom_to_htj2k(dicom_file):
       # Raw DICOM → HTJ2K 압축
       # Orthanc에 저장
   ```

2. **AI 작업 트리거**
   ```python
   @shared_task
   def trigger_ai_analysis(study_id):
       # FastAPI AI 서버 호출
       # 결과 DB 저장
   ```

3. **FHIR 동기화**
   ```python
   @shared_task
   def sync_patient_to_fhir(patient_id):
       # Django DB → HAPI FHIR 전송
   ```

**Concurrency 설정**:
- `--concurrency=4`: 4개 워커 프로세스
- CPU 코어 수에 맞춰 조정 가능
- 이미지 변환은 CPU 집약적 작업

---

### 4. Celery Beat (Scheduler)

**Docker 설정**:
```yaml
celery-beat:
  command: celery -A cdss_backend beat -l info
           --scheduler django_celery_beat.schedulers:DatabaseScheduler
  environment:
    - DB_HOST=cdss-mysql
```

**핵심 역할**:
- **주기적 작업 실행** (Cron 대체)
  - 매일 새벽 FHIR 동기화
  - 1시간마다 캐시 정리
  - 주간 보고서 생성

**DatabaseScheduler 사용 이유**:
- Django Admin에서 스케줄 관리 가능
- 동적 스케줄 변경 (재시작 불필요)
- 멀티 인스턴스 환경 지원

---

### 5. Flower (Celery Monitoring)

**Docker 설정**:
```yaml
flower:
  command: celery -A cdss_backend flower --port=5555
  ports:
    - "5555:5555"  # 개발용 직접 접속
```

**제공 기능**:
- 실시간 작업 상태 모니터링
- Worker 상태 확인
- 작업 실행 히스토리
- 실패한 작업 재시도

**접속**: http://localhost/flower/ (Nginx 경유)

---

### 6. MySQL (CDSS Database)

**Docker 설정**:
```yaml
cdss-mysql:
  image: mysql:8.0
  environment:
    MYSQL_DATABASE: cdss_db
    MYSQL_USER: cdss_user
    MYSQL_PASSWORD: ${DB_PASSWORD}
  ports:
    - "3306:3306"  # 개발: DB 클라이언트 접속용
  volumes:
    - cdss_mysql_data:/var/lib/mysql
  command: --character-set-server=utf8mb4
           --collation-server=utf8mb4_unicode_ci
```

**핵심 특징**:

1. **UTF-8 MB4 설정**
   - 한글, 이모지 완벽 지원
   - 의료 데이터 국제화 대비

2. **Health Check**
   ```yaml
   healthcheck:
     test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
     interval: 10s
     retries: 10
   ```
   - Django 시작 전 DB 준비 완료 확인

3. **볼륨 영속성**
   - 컨테이너 삭제해도 데이터 유지
   - 백업/복구 용이

**프로덕션 주의사항**:
- `ports` 제거 (외부 접속 차단)
- `expose: ["3306"]`만 사용 (내부 통신)

---

### 7. Redis (Cache & Message Broker)

**Docker 설정**:
```yaml
redis:
  image: redis:7-alpine
  command: redis-server
           --appendonly yes
           --maxmemory 512mb
           --maxmemory-policy allkeys-lru
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**이중 역할**:

1. **Application Cache**
   ```python
   # Django settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://redis:6379/0',
       }
   }
   ```

2. **Celery Message Broker**
   ```python
   CELERY_BROKER_URL = 'redis://redis:6379/0'
   CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
   ```

**메모리 관리**:
- `maxmemory 512mb`: 개발 환경 적정 크기
- `allkeys-lru`: 메모리 부족 시 LRU 정책으로 자동 삭제
- 프로덕션: 2GB 이상 권장

**AOF (Append-Only File)**:
- `appendonly yes`: 데이터 영속성 보장
- Redis 재시작 시 복구

---

### 8. Orthanc (PACS Server)

**Docker 설정**:
```yaml
orthanc:
  image: orthancteam/orthanc:latest
  environment:
    - ORTHANC_AUTHENTICATION_ENABLED=false  # 개발용
    - ORTHANC__HTTP_CORS_ENABLED=true
  ports:
    - "8042:8042"  # 개발: 직접 접속용
    - "4242:4242"  # DICOM C-STORE
  volumes:
    - orthanc_data:/var/lib/orthanc/db
    - ./NeuroNova_02_back_end/05_orthanc_pacs/orthanc.json:/etc/orthanc/orthanc.json:ro
```

**v2.1 보안 설계**:

**개발 환경**:
```
외부 → Nginx:80/orthanc-direct/ → Orthanc:8042  (디버깅용)
       Nginx:80/internal-orthanc/ → Orthanc:8042  (Secure Proxy)
```

**프로덕션 환경**:
```
외부 → Nginx:80/internal-orthanc/ → Orthanc:8042 (ONLY)
       포트 8042 외부 노출 차단
```

**HTJ2K 지원**:
- `orthanc.json`에서 플러그인 활성화
- DICOM → HTJ2K 변환 설정
- WASM 디코더 연동

---

### 9. OpenEMR (EMR System)

**Docker 설정**:
```yaml
openemr-mysql:
  image: mariadb:11.8
  environment:
    MYSQL_ROOT_PASSWORD: ${OPENEMR_DB_ROOT_PASSWORD}
  ports:
    - "3307:3306"  # CDSS MySQL과 포트 충돌 방지

openemr:
  image: openemr/openemr:7.0.3
  ports:
    - "8081:80"
    - "4443:443"
  environment:
    MYSQL_HOST: openemr-mysql
    OE_USER: admin
    OE_PASS: ${OPENEMR_OE_PASS}
  depends_on:
    openemr-mysql:
      condition: service_healthy
```

**핵심 특징**:

1. **전용 DB 분리**
   - OpenEMR 자체 MariaDB
   - CDSS MySQL과 독립

2. **Health Check Dependency**
   ```yaml
   depends_on:
     openemr-mysql:
       condition: service_healthy
   ```
   - DB 준비 완료 후 OpenEMR 시작

3. **Write-Through 패턴**
   - Django가 OpenEMR API 호출
   - 동시에 CDSS DB 저장
   - 데이터 일관성 보장

---

### 10. HAPI FHIR (FHIR Server)

**Docker 설정**:
```yaml
hapi-fhir:
  image: hapiproject/hapi:latest
  environment:
    - hapi.fhir.fhir_version=R4
    - hapi.fhir.allow_multiple_delete=true
  ports:
    - "8080:8080"
  volumes:
    - hapi_fhir_data:/data/hapi
```

**핵심 역할**:
- HL7 FHIR R4 표준 지원
- Patient, Observation, DiagnosticReport 리소스
- Django에서 REST API 호출

**FHIR 동기화 플로우**:
```
Django (환자 생성)
  ↓
Celery Task 트리거
  ↓
HAPI FHIR (/fhir/Patient POST)
  ↓
FHIR Resource 생성
```

---

### 11. Prometheus (Metrics Collection)

**Docker 설정**:
```yaml
prometheus:
  image: prom/prometheus:latest
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.enable-lifecycle'
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./monitoring/prometheus/alerts:/etc/prometheus/alerts:ro
    - prometheus_data:/prometheus
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
```

**핵심 역할**:
- **시계열 메트릭 수집** (Pull 방식)
  - Django: HTTP 요청, 응답 시간, 에러율
  - Redis: 메모리 사용량, 히트율
  - MySQL: 커넥션 수, 쿼리 성능
  - Celery: 큐 길이, 작업 성공/실패율
  - 시스템: CPU, Memory, Disk, Network

**Scrape 설정** (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['django:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

**Alert Rules** (`alerts/cdss_alerts.yml`):
```yaml
- alert: DjangoServiceDown
  expr: up{job="django"} == 0
  for: 1m
  labels:
    severity: critical
    code: blue
  annotations:
    summary: "CODE BLUE: Django backend is DOWN"
```

---

### 12. Grafana (Visualization Dashboard)

**Docker 설정**:
```yaml
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin123}
    - GF_SERVER_ROOT_URL=http://localhost:3000
    - GF_INSTALL_PLUGINS=redis-datasource,grafana-clock-panel
  ports:
    - "3000:3000"
  volumes:
    - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    - grafana_data:/var/lib/grafana
  depends_on:
    prometheus:
      condition: service_healthy
```

**핵심 역할**:
- **대시보드 시각화**
  - 시스템 상태 대시보드 (RPS, 에러율, 응답 시간)
  - 리소스 모니터링 (CPU, Memory, Disk)
  - AI 작업 모니터링 (GPU 사용량 - 확장 가능)
  - 데이터베이스 모니터링 (커넥션, 슬로우 쿼리)

**자동 프로비저닝**:
- Prometheus 데이터 소스 자동 연결
- 대시보드 JSON 파일 자동 로드
- 플러그인 자동 설치

**접속 정보**:
- URL: http://localhost:3000
- 기본 계정: admin / admin123

---

### 13. Alertmanager (Alert Routing)

**Docker 설정**:
```yaml
alertmanager:
  image: prom/alertmanager:latest
  command:
    - '--config.file=/etc/alertmanager/alertmanager.yml'
    - '--storage.path=/alertmanager'
  ports:
    - "9093:9093"
  volumes:
    - ./monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
    - alertmanager_data:/alertmanager
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9093/-/healthy"]
```

**핵심 역할**:
- **알림 라우팅 및 전송**
  - **CODE BLUE**: 시스템 다운, DB 연결 끊김 (즉시 알림)
  - **CRITICAL**: 높은 에러율, 응답 지연 (30초 대기)
  - **WARNING**: 리소스 부족, 큐 백업 (5분 대기)

**알림 채널** (`alertmanager.yml`):
```yaml
receivers:
  - name: 'code-blue-team'
    email_configs:
      - to: 'oncall@neuronova.com'
        subject: 'CODE BLUE: {{ .GroupLabels.alertname }}'

    # Slack (설정 시)
    # slack_configs:
    #   - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'

    # SMS (Webhook)
    webhook_configs:
      - url: 'http://sms-gateway:8080/send'
```

**알림 우선순위**:
| 레벨 | 대기 시간 | 반복 간격 | 용도 |
|------|-----------|-----------|------|
| CODE BLUE | 0초 | 5분 | 치명적 장애 |
| CRITICAL | 30초 | 1시간 | 심각한 문제 |
| WARNING | 5분 | 12시간 | 경고 |

---

## 🌐 네트워크 설계

### 네트워크 토폴로지

```yaml
networks:
  neuronova_network:
    driver: bridge
    name: neuronova_network
```

**모든 서비스가 하나의 브리지 네트워크에 연결**:
- 서비스명으로 DNS 자동 해석
- 내부 통신 암호화 없음 (프라이빗 네트워크)
- 외부 접속은 Nginx만

### DNS 해석 예시

```python
# Django settings.py
DATABASES = {
    'default': {
        'HOST': 'cdss-mysql',  # Docker DNS가 자동 해석
    }
}

ORTHANC_API_URL = 'http://orthanc:8042'  # 컨테이너명 = 호스트명
```

### 포트 매핑 전략

| 서비스 | 내부 포트 | 외부 포트 (개발) | 프로덕션 |
|--------|-----------|------------------|----------|
| Nginx | 80 | 80 | 80 (HTTPS는 Cloudflare) |
| Django | 8000 | 8000 | expose만 |
| MySQL | 3306 | 3306 | expose만 |
| Redis | 6379 | 6379 | expose만 |
| Orthanc | 8042 | 8042 | expose만 |
| Flower | 5555 | 5555 | 제거 또는 인증 추가 |

**개발 vs 프로덕션 차이**:
- **개발**: 디버깅을 위해 직접 포트 노출
- **프로덕션**: Nginx만 노출, 나머지 `expose` (내부 통신만)

---

## 💾 볼륨 관리

### 볼륨 종류

**Named Volumes (데이터 영속성)**:
```yaml
volumes:
  # Data Layer
  cdss_mysql_data:      # CDSS 데이터베이스
  openemr_mysql_data:   # OpenEMR 데이터베이스
  redis_data:           # Redis AOF/RDB
  orthanc_data:         # DICOM 이미지
  hapi_fhir_data:       # FHIR 리소스
  openemr_logs:         # OpenEMR 로그
  openemr_sites:        # OpenEMR 사이트 설정

  # Monitoring Layer
  prometheus_data:      # 메트릭 시계열 데이터
  grafana_data:         # 대시보드 및 설정
  alertmanager_data:    # 알림 상태 저장소
```

**Bind Mounts (개발용)**:
```yaml
volumes:
  # Hot Reload
  - ./NeuroNova_02_back_end/02_django_server:/app

  # 설정 파일
  - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf:ro
  - ./NeuroNova_02_back_end/05_orthanc_pacs/orthanc.json:/etc/orthanc/orthanc.json:ro

  # 정적 파일
  - ./static/react-main:/var/www/react-main:ro
  - ./static/ohif-dist:/var/www/ohif-dist:ro
```

### 볼륨 위치

**Linux/Mac**:
```bash
/var/lib/docker/volumes/neuronova_cdss_mysql_data/_data
```

**Windows (WSL2)**:
```bash
\\wsl$\docker-desktop-data\data\docker\volumes\neuronova_cdss_mysql_data\_data
```

### 백업 전략

```bash
# MySQL 백업
docker compose -f docker-compose.dev.yml exec cdss-mysql \
  mysqldump -u root -p cdss_db > backup_$(date +%Y%m%d).sql

# Orthanc 백업 (볼륨 전체)
docker run --rm -v neuronova_orthanc_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/orthanc_backup.tar.gz /data
```

---

## 🔒 보안 설계

### 1. 환경 변수 관리

**`.env` 파일 (Git 제외)**:
```env
DJANGO_SECRET_KEY=CHANGE_ME_production_secret_key
DB_PASSWORD=CHANGE_ME_strong_password
DB_ROOT_PASSWORD=CHANGE_ME_root_password
ORTHANC_PASSWORD=CHANGE_ME_orthanc_password
```

**.gitignore**:
```
.env  # 절대 커밋하지 않음!
```

**`.env.example` (Git 포함)**:
```env
DJANGO_SECRET_KEY=CHANGE_ME_django_secret
DB_PASSWORD=CHANGE_ME_db_password
```

### 2. Network Segmentation

**Layer 구분**:
- **Public**: Nginx만
- **Internal**: Django, Celery, 모든 데이터 서비스

**프로덕션 권장**:
```yaml
# docker-compose.prod.yml
orthanc:
  expose:
    - "8042"  # 외부 포트 제거
  # ports 제거!
```

### 3. Secure Proxy Pattern

**동작 원리**:
```
1. OHIF → Django API 요청 (JWT 토큰 포함)
   GET /api/pacs/studies/123/
   Authorization: Bearer eyJ0eXAi...

2. Django JWT 검증 성공
   return HttpResponse(
       status=200,
       headers={'X-Accel-Redirect': '/internal-orthanc/studies/123/'}
   )

3. Nginx 헤더 인터셉트
   location /internal-orthanc/ {
       internal;  # 외부 차단
       proxy_pass http://orthanc:8042/;
   }

4. Orthanc에서 데이터 조회 → 클라이언트 스트리밍
```

**보안 이점**:
- Orthanc 직접 접속 불가
- 모든 요청이 JWT 검증 통과
- 감사 로그 기록 가능

---

## ⚡ 성능 최적화

### 1. Nginx 설정

```nginx
# Gzip 압축
gzip on;
gzip_comp_level 6;
gzip_types text/plain application/json application/javascript;

# 클라이언트 업로드 크기 (DICOM 대용량)
client_max_body_size 500M;

# Keepalive
keepalive_timeout 65;
upstream django_backend {
    server django:8000;
    keepalive 32;  # 연결 재사용
}
```

### 2. Celery Concurrency

```yaml
celery-worker:
  command: celery -A cdss_backend worker -l info --concurrency=4
```

**조정 가이드**:
- CPU 집약적 (HTJ2K 변환): `--concurrency=CPU 코어 수`
- I/O 집약적 (API 호출): `--concurrency=CPU 코어 수 × 2`

### 3. Redis 메모리 관리

```yaml
redis:
  command: redis-server
           --maxmemory 512mb
           --maxmemory-policy allkeys-lru
```

**정책 선택**:
- `allkeys-lru`: 모든 키 대상 LRU (범용)
- `volatile-lru`: 만료 시간 있는 키만 (캐시 전용)
- `allkeys-lfu`: 접근 빈도 기반 (추천)

### 4. MySQL 튜닝

```yaml
cdss-mysql:
  command:
    - --character-set-server=utf8mb4
    - --collation-server=utf8mb4_unicode_ci
    - --innodb_buffer_pool_size=1G  # 프로덕션 권장
    - --max_connections=200
```

---

## 🔄 개발 vs 프로덕션

### 주요 차이점

| 항목 | 개발 (dev) | 프로덕션 (prod) |
|------|-----------|----------------|
| **파일명** | `docker-compose.dev.yml` | `docker-compose.prod.yml` |
| **Django 실행** | `runserver` (Hot Reload) | `gunicorn` (WSGI) |
| **DEBUG** | `True` | `False` |
| **ENABLE_SECURITY** | `False` | `True` |
| **외부 포트** | 다수 노출 (디버깅용) | Nginx:80만 |
| **볼륨 마운트** | 소스 코드 (rw) | 없음 (이미지 포함) |
| **Nginx** | 개발용 설정 | 프로덕션 최적화 |
| **로그 레벨** | `DEBUG` | `WARNING` |
| **Celery Concurrency** | 2-4 | 8-16 |

### 개발 환경 특징

```yaml
# docker-compose.dev.yml
django:
  command: python manage.py runserver 0.0.0.0:8000
  volumes:
    - ./NeuroNova_02_back_end/02_django_server:/app  # Hot Reload
  environment:
    - DEBUG=True
    - ENABLE_SECURITY=False  # JWT 검증 완화
  ports:
    - "8000:8000"  # 직접 API 호출 가능
```

### 프로덕션 환경 (권장 구성)

```yaml
# docker-compose.prod.yml
django:
  command: gunicorn cdss_backend.wsgi:application
           --bind 0.0.0.0:8000
           --workers 4
           --threads 2
  # volumes 제거 (소스 코드 이미지 포함)
  environment:
    - DEBUG=False
    - ENABLE_SECURITY=True
    - SECRET_KEY=${DJANGO_SECRET_KEY}  # 환경 변수 필수
  expose:
    - "8000"  # 외부 포트 차단
  restart: always

orthanc:
  expose:
    - "8042"  # 외부 포트 차단
  environment:
    - ORTHANC_AUTHENTICATION_ENABLED=true  # 인증 활성화
```

---

## 📊 의존성 그래프

```
nginx
 ├─ depends_on: django (healthy)
 └─ depends_on: orthanc (healthy)

django
 ├─ depends_on: cdss-mysql (healthy)
 ├─ depends_on: redis (healthy)
 └─ depends_on: orthanc (healthy)

celery-worker
 ├─ depends_on: redis (healthy)
 ├─ depends_on: cdss-mysql (healthy)
 └─ depends_on: orthanc (healthy)

celery-beat
 ├─ depends_on: redis (healthy)
 └─ depends_on: cdss-mysql (healthy)

flower
 └─ depends_on: redis (healthy)

openemr
 └─ depends_on: openemr-mysql (healthy)
```

**Health Check 중요성**:
- `depends_on` + `condition: service_healthy`
- 순서대로 시작 보장
- DB 마이그레이션 실패 방지

---

## 🛠️ 유지보수 가이드

### 서비스 추가 방법

1. **docker-compose.dev.yml에 추가**:
```yaml
new-service:
  image: your-image:latest
  container_name: neuronova-new-service
  networks:
    - neuronova_network
  depends_on:
    - redis
```

2. **환경 변수 추가** (`.env`, `.env.example`):
```env
NEW_SERVICE_PORT=9000
NEW_SERVICE_API_KEY=CHANGE_ME
```

3. **Nginx 라우팅** (필요 시):
```nginx
location /new-service/ {
    proxy_pass http://new-service:9000/;
}
```

### 버전 업그레이드

```bash
# 이미지 버전 변경
# docker-compose.dev.yml
mysql:
  image: mysql:8.0 → mysql:8.1

# 재빌드 및 재시작
docker compose -f docker-compose.dev.yml up -d --build mysql

# 로그 확인
docker compose -f docker-compose.dev.yml logs -f mysql
```

---

## 📝 요약

### Docker v2.1의 핵심 가치

1. **아키텍처 문서화 → 코드 변환**
   - [06_시스템_아키텍처_v2.md](01_doc/06_시스템_아키텍처_v2.md) 완벽 구현

2. **단일 진실의 원천**
   - `docker-compose.dev.yml` 하나로 전체 스택 관리

3. **보안 우선**
   - Secure Proxy Pattern
   - Network Segmentation
   - 환경 변수 격리

4. **개발 경험 최적화**
   - Hot Reload
   - 실시간 로그
   - 직접 포트 접속 (디버깅)

5. **프로덕션 준비**
   - Health Checks
   - 볼륨 영속성
   - 확장 가능 구조

---

**총 서비스 수**: 14개 (Nginx + Django/Celery 4개 + Data Layer 5개 + Monitoring 3개)

**문서 버전**: 1.1
**최종 수정**: 2025-12-30
**작성자**: NeuroNova Development Team
**변경 이력**:
- v1.1 (2025-12-30): Observability Layer 추가 (Prometheus, Grafana, Alertmanager)
- v1.0 (2025-12-30): 초기 작성

**다음 읽기**: [DOCKER_DEV_GUIDE.md](DOCKER_DEV_GUIDE.md) - 실습 가이드
