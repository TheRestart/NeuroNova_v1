# NeuroNova CDSS 배포 가이드 (GCP + Docker)

**작성일**: 2025-12-30
**버전**: 2.3
**최종 수정**: 2026-01-03
**환경**: GCP VM + Docker + Cloudflare + GitHub

**주요 변경 (v2.3)**:
- ✅ FHIR OAuth2 환경 변수 추가 (Celery Worker FHIR Outbox)
- ✅ FHIR_SERVER_URL, FHIR_OAUTH_TOKEN_URL, FHIR_OAUTH_CLIENT_ID/SECRET 추가
- ✅ Day 19 (2026-01-03) Celery Worker 개선 사항 반영

**이전 변경 (v2.2, 2026-01-02)**:
- ✅ OpenEMR Skip 모드 설정 추가
- ✅ .env 파일 전송 체크리스트 추가
- ✅ 별도 전송 필요 파일 목록 정리
- ✅ 자동 시작 스크립트 참조 추가
- ✅ 보안 설정 강화 (비밀번호 정책)

---

## 목차

1. [배포 환경 개요](#1-배포-환경-개요)
2. [GCP VM 초기 설정](#2-gcp-vm-초기-설정)
3. [Docker 설치 및 설정](#3-docker-설치-및-설정)
4. [GitHub 연동 및 배포 전략](#4-github-연동-및-배포-전략)
5. [환경 변수 관리 (.env)](#5-환경-변수-관리-env)
6. [데이터베이스 초기화](#6-데이터베이스-초기화)
7. [Docker Compose 배포](#7-docker-compose-배포)
8. [Nginx + React 빌드 배포](#8-nginx--react-빌드-배포)
9. [Cloudflare HTTPS 설정](#9-cloudflare-https-설정)
10. [비동기 처리 설정 (Celery)](#10-비동기-처리-설정-celery)
11. [배포 체크리스트](#11-배포-체크리스트)
12. [트러블슈팅](#12-트러블슈팅)
13. [시스템 다이어그램](#13-시스템-다이어그램)

---

## 1. 배포 환경 개요

### 1.1 전체 아키텍처

```
                    Internet
                       ↓
         ┌─────────────────────────┐
         │   Cloudflare (무료)      │ ← HTTPS, DNS, DDoS Protection
         │   https://cdss.your.com │
         └─────────────────────────┘
                       ↓ HTTPS
         ┌─────────────────────────┐
         │     GCP VM Instance     │
         │   (Ubuntu 22.04 LTS)    │
         │ IP: 34.71.151.117 (고정)│
         └─────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │    Nginx (Port 80)      │ ← React Build (Static)
         │  - Reverse Proxy        │
         │  - SSL Termination      │
         └─────────────────────────┘
                       ↓
    ┌──────────────┬──────────────┬──────────────┐
    │              │              │              │
┌───────┐    ┌─────────┐   ┌──────────┐   ┌──────────┐
│Django │    │Orthanc  │   │  Redis   │   │  MySQL   │
│ :8000 │    │ :8042   │   │  :6379   │   │  :3306   │
└───────┘    └─────────┘   └──────────┘   └──────────┘
    │              │              │              │
    └──────────────┴──────────────┴──────────────┘
                       ↓
         ┌─────────────────────────┐
         │   Docker Network        │
         │  (cdss-network)         │
         └─────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │   Celery Workers        │ ← AI 추론, FHIR 동기화
         │   - AI Task Worker      │
         │   - FHIR Sync Worker    │
         │   - Beat Scheduler      │
         └─────────────────────────┘
```

### 1.2 GCP VM 요구 사양

**최소 사양 (개발/테스트)**
- **Machine Type**: e2-standard-4 (4 vCPU, 16GB RAM)
- **Boot Disk**: 100GB SSD Persistent Disk
- **OS**: Ubuntu 22.04 LTS
- **Region**: asia-northeast3 (서울)
- **방화벽**: HTTP(80), HTTPS(443), SSH(22) 허용
- **External IP**: 34.71.151.117 (고정 IP 할당됨)

**권장 사양 (운영)**
- **Machine Type**: n2-standard-8 (8 vCPU, 32GB RAM)
- **Boot Disk**: 200GB SSD Persistent Disk
- **Additional Disk**: 500GB Standard Persistent Disk (DICOM 저장용)
- **GPU**: NVIDIA T4 (AI 추론용, 선택사항)
- **External IP**: 34.71.151.117 (고정 IP - 이미 예약됨)

### 1.3 접속 도구

- **SSH 클라이언트**: PuTTY
- **파일 전송**: WinSCP
- **Git**: GitHub Desktop (Windows), git CLI (VM)
- **모니터링**: GCP Console, Portainer (Docker UI)

---

## 2. GCP VM 초기 설정

### 2.1 GCP VM 인스턴스 생성

**고정 외부 IP 주소 (Static External IP)**
- **IP 주소**: `34.71.151.117`
- **이름**: `neuronova-static-ip`
- **Region**: `asia-northeast3` (서울)
- **상태**: ✅ 이미 예약됨

**중요**: VM 재부팅 시에도 이 IP 주소가 유지됩니다.

```bash
# GCP Console에서 수동 생성 또는 gcloud CLI 사용

gcloud compute instances create neuronova-cdss-vm \
  --project=YOUR_PROJECT_ID \
  --zone=asia-northeast3-a \
  --machine-type=e2-standard-4 \
  --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default,address=34.71.151.117 \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --create-disk=auto-delete=yes,boot=yes,device-name=neuronova-cdss-vm,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231213,mode=rw,size=100,type=projects/YOUR_PROJECT_ID/zones/asia-northeast3-a/diskTypes/pd-ssd \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --labels=env=production,app=cdss \
  --reservation-affinity=any
```

**고정 IP 주소 확인**
```bash
# 현재 할당된 IP 확인
gcloud compute addresses describe neuronova-static-ip --region=asia-northeast3

# 출력 예시:
# address: 34.71.151.117
# addressType: EXTERNAL
# status: IN_USE
```

**방화벽 규칙 생성**

```bash
# HTTP 허용
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# HTTPS 허용
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server

# VM에 태그 추가
gcloud compute instances add-tags neuronova-cdss-vm \
  --tags http-server,https-server \
  --zone asia-northeast3-a
```

### 2.2 PuTTY를 통한 SSH 접속 설정

**1. SSH 키 생성 (Windows)**

```bash
# PuTTYgen 실행
1. Type of key: RSA
2. Number of bits: 2048
3. Generate 클릭
4. Key comment: neuronova-cdss-key
5. Save public key: neuronova-cdss-key.pub
6. Save private key: neuronova-cdss-key.ppk
```

**2. GCP에 SSH 공개키 등록**

```bash
# GCP Console > Compute Engine > 메타데이터 > SSH 키 > 추가
# neuronova-cdss-key.pub 내용 복사 붙여넣기
# 형식: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDxxx... your-username
```

**3. PuTTY 세션 설정**

```
Session:
  Host Name: EXTERNAL_IP (GCP VM의 외부 IP)
  Port: 22
  Connection type: SSH
  Saved Sessions: neuronova-cdss-vm

Connection > Data:
  Auto-login username: your-username

Connection > SSH > Auth:
  Private key file: neuronova-cdss-key.ppk

Session > Save
```

### 2.3 WinSCP 파일 전송 설정

#### 2.3.1 WinSCP 연결 설정

```
파일 프로토콜: SFTP
호스트 이름: EXTERNAL_IP
포트 번호: 22
사용자 이름: your-username
비밀번호: (비워둠)

고급 > SSH > 인증 > 개인 키 파일: neuronova-cdss-key.ppk

저장 > 로그인
```

#### 2.3.2 배포 전 파일 정리 (필수)

**⚠️ 중요**: GCP VM에 업로드하기 전에 불필요한 파일을 반드시 정리해야 합니다.

**Windows에서 자동 정리 실행**:
```cmd
cd d:\1222\NeuroNova_v1
cleanup-for-deployment.bat
```

**정리 대상 파일** (cleanup-for-deployment.bat가 자동 삭제):

1. **Python 캐시 및 임시 파일** (필수 삭제):
   - `__pycache__/` 디렉토리 (모든 위치)
   - `*.pyc` 파일 (Python 바이트코드)
   - `.coverage` (테스트 커버리지 캐시)

2. **로그 파일** (필수 삭제):
   - `logs/*.log` (모든 로그 파일)
   - `NeuroNova_02_back_end/02_django_server/logs/*.log`

3. **개발 환경 파일** (필수 삭제 - 보안 위험):
   - `NeuroNova_03_front_end_react/00_test_client/.env.local`
   - `.DS_Store` (macOS 시스템 파일)

4. **Python 가상환경** (필수 삭제 - 183MB):
   - `venv/` 디렉토리 전체
   - **이유**: GCP VM에서 requirements.txt로 재설치

5. **Node.js 의존성** (선택 삭제 - 1.2GB):
   - `NeuroNova_03_front_end_react/00_test_client/node_modules/`
   - **이유**: GCP VM에서 package.json으로 재설치
   - **권장**: 로컬에서 `npm run build` 후 `build/` 디렉토리만 전송

6. **구버전 문서** (선택 삭제):
   - `OLD_프롬.md`
   - `OLD_작업이력.md`
   - `OLD_업무계획서.md`
   - `OLD_README.md`
   - `90_작업이력/docker-compose.OLD*.yml`

**예상 절약 용량**: ~1.5GB (venv 183MB + node_modules 1.2GB + 기타)

#### 2.3.3 전송할 파일 및 디렉토리

**필수 전송 파일**:

```plaintext
NeuroNova_v1/
├── NeuroNova_02_back_end/          # 백엔드 전체 (venv 제외)
│   ├── 01_ai_core/                 # AI 모델 및 서비스
│   ├── 02_django_server/           # Django 프로젝트
│   │   ├── cdss_backend/           # Django 설정
│   │   ├── acct/                   # 인증/권한 앱
│   │   ├── emr/                    # EMR 앱
│   │   ├── ocs/                    # OCS 앱
│   │   ├── lis/                    # LIS 앱
│   │   ├── ris/                    # RIS 앱
│   │   ├── ai/                     # AI 앱
│   │   ├── fhir/                   # FHIR 앱
│   │   ├── audit/                  # 감사 로그 앱
│   │   ├── alert/                  # 알림 앱
│   │   ├── manage.py               # Django 관리 명령
│   │   ├── requirements.txt        # Python 의존성 ✅
│   │   └── .env                    # 환경변수 (수동 작성) ⚠️
│   ├── 05_orthanc_pacs/            # Orthanc PACS 설정
│   ├── 06_hapi_fhir/               # HAPI FHIR 설정
│   └── 07_redis/                   # Redis 설정
│
├── NeuroNova_03_front_end_react/   # 프론트엔드
│   └── 00_test_client/
│       ├── public/                 # 정적 파일
│       ├── src/                    # React 소스코드
│       ├── package.json            # npm 의존성 ✅
│       ├── package-lock.json       # npm 잠금 파일
│       └── .env                    # 환경변수 (수동 작성) ⚠️
│
├── docker-compose.dev.yml          # Docker Compose 설정 ✅
├── nginx/                          # Nginx 설정
│   └── nginx.conf
├── prometheus/                     # 모니터링 설정
│   ├── prometheus.yml
│   └── alert.rules.yml
└── 01_doc/                         # 필수 문서
    ├── 초기_데이터_시딩_가이드.md
    ├── 12_GCP_배포_가이드.md
    └── README_자동실행.md
```

**⚠️ 별도 전송 필요 파일** (보안상 Git 미포함):

1. **`.env` 파일** (Django):
   - 경로: `NeuroNova_02_back_end/02_django_server/.env`
   - **수동 작성 필요** (GCP VM에서 직접 생성)
   - 내용: [4. 환경 변수 설정](#4-환경-변수-설정) 참조

2. **`.env` 파일** (React):
   - 경로: `NeuroNova_03_front_end_react/00_test_client/.env`
   - **수동 작성 필요** (GCP VM에서 직접 생성)
   - 프로덕션용 API URL 설정 필요

**전송하지 말아야 할 파일**:
- ❌ `venv/` (Python 가상환경)
- ❌ `node_modules/` (npm 패키지)
- ❌ `__pycache__/`, `*.pyc` (Python 캐시)
- ❌ `.env.local` (개발 환경변수)
- ❌ `logs/*.log` (로그 파일)
- ❌ `.coverage` (테스트 커버리지)
- ❌ `.DS_Store` (macOS 시스템 파일)
- ❌ `OLD_*.md` (구버전 문서)

#### 2.3.4 WinSCP 전송 절차

1. **로컬에서 정리 스크립트 실행**:
   ```cmd
   cleanup-for-deployment.bat
   ```

2. **WinSCP로 프로젝트 루트 전송**:
   - 왼쪽(로컬): `d:\1222\NeuroNova_v1`
   - 오른쪽(GCP): `/home/your-username/NeuroNova_v1`
   - 전송 방법: 드래그 앤 드롭

3. **전송 완료 후 VM에서 확인**:
   ```bash
   cd ~/NeuroNova_v1
   ls -lh
   du -sh *  # 디렉토리 크기 확인
   ```

4. **VM에서 의존성 재설치** ([4.3 Python 가상환경](#43-python-가상환경) 참조):
   ```bash
   cd NeuroNova_02_back_end/02_django_server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 2.4 시스템 업데이트 및 기본 패키지 설치

```bash
# 패키지 목록 업데이트
sudo apt-get update && sudo apt-get upgrade -y

# 기본 도구 설치
sudo apt-get install -y \
  curl \
  wget \
  git \
  vim \
  htop \
  net-tools \
  ca-certificates \
  gnupg \
  lsb-release \
  software-properties-common

# 시간대 설정 (한국 표준시)
sudo timedatectl set-timezone Asia/Seoul

# 확인
date
# 출력: 2025년 12월 30일 월요일 14:25:33 KST
```

---

## 3. Docker 설치 및 설정

### 3.1 Docker Engine 설치

```bash
# 이전 버전 제거 (있을 경우)
sudo apt-get remove -y docker docker-engine docker.io containerd runc

# Docker 공식 GPG 키 추가
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Docker Repository 추가
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 설치 확인
docker --version
docker compose version
```

### 3.2 Docker 권한 설정

```bash
# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 변경사항 적용 (재로그인 필요)
newgrp docker

# 권한 확인
docker ps
```

### 3.3 Docker 데몬 설정

```bash
# Docker 데몬 설정 파일 생성
sudo vi /etc/docker/daemon.json
```

**daemon.json 내용**

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
```

```bash
# Docker 재시작
sudo systemctl restart docker
sudo systemctl enable docker
```

---

## 4. GitHub 연동 및 배포 전략

### 4.1 GitHub SSH 키 등록

```bash
# SSH 키 생성 (VM에서)
ssh-keygen -t ed25519 -C "your-email@example.com"
# Passphrase: (엔터 - 비밀번호 없음)

# 공개키 확인
cat ~/.ssh/id_ed25519.pub

# GitHub > Settings > SSH and GPG keys > New SSH key
# Title: GCP-NeuroNova-VM
# Key: (위 공개키 붙여넣기)
```

### 4.2 프로젝트 Clone

```bash
# 작업 디렉토리 생성
mkdir -p ~/apps
cd ~/apps

# Git Clone (SSH 사용)
git clone git@github.com:your-username/NeuroNova_v1.git
cd NeuroNova_v1
```

### 4.3 배포 스크립트 작성

```bash
vi ~/apps/NeuroNova_v1/deploy.sh
```

**deploy.sh 내용**

```bash
#!/bin/bash

set -e

echo "[1/6] Pulling latest code from GitHub..."
cd ~/apps/NeuroNova_v1
git pull origin main

echo "[2/6] Stopping running containers..."
cd NeuroNova_02_back_end/02_django_server
docker compose down

echo "[3/6] Building new images..."
docker compose build --no-cache

echo "[4/6] Starting containers..."
docker compose up -d

echo "[5/6] Running database migrations..."
docker compose exec django python manage.py migrate

echo "[6/6] Collecting static files..."
docker compose exec django python manage.py collectstatic --noinput

echo "Deployment completed successfully!"
docker compose ps
```

```bash
chmod +x ~/apps/NeuroNova_v1/deploy.sh
```

---

## 5. 환경 변수 관리 (.env)

### 5.1 별도 전송 필요 파일 체크리스트

**⚠️ 중요**: 다음 파일들은 Git에 포함되지 않으며, WinSCP를 통해 별도로 전송해야 합니다.

#### 필수 전송 파일 목록

| 파일 경로 | 설명 | 전송 필요 | 비고 |
|----------|------|---------|------|
| `NeuroNova_02_back_end/02_django_server/.env` | Django 환경 변수 | ✅ 필수 | .env.example 복사 후 수정 |
| `NeuroNova_03_front_end_react/00_test_client/.env.production` | React 프로덕션 환경 변수 | ✅ 필수 | API URL 설정 |
| `NeuroNova_03_front_end_react/00_test_client/.env.local` | React 개발 환경 변수 | ⚠️ 개발 전용 | 프로덕션에서는 불필요 |

#### 선택적 전송 파일

| 파일 경로 | 설명 | 전송 필요 | 비고 |
|----------|------|---------|------|
| `scripts/Register-OpenEMRClient.ps1` | OpenEMR OAuth2 자동 등록 | 🔧 개발 도구 | Windows 전용, 필요 시 |
| `start-all-services.bat` | 전체 서비스 자동 시작 | 🔧 개발 도구 | Windows 전용, 필요 시 |
| `README_자동실행.md` | 자동 실행 가이드 | 📖 참고 | 문서, 필요 시 |

### 5.2 .env 파일 저장 위치 전략

**.env 파일은 Git에 포함하지 않고, VM에서 직접 관리합니다.**

```
프로젝트 구조:
NeuroNova_v1/
├── .gitignore                    ← .env 포함
├── NeuroNova_02_back_end/
│   └── 02_django_server/
│       ├── .env                  ← VM에서만 존재 (Git 무시)
│       ├── .env.example          ← Git에 포함 (템플릿)
│       └── docker-compose.yml
├── NeuroNova_03_front_end_react/
│   └── 00_test_client/
│       ├── .env.production       ← VM에서만 존재 (Git 무시)
│       ├── .env.local            ← 개발 전용 (Git 무시)
│       └── package.json
```

### 5.3 Django .env 파일 상세 설정

**NeuroNova_02_back_end/02_django_server/.env 템플릿 (프로덕션용)**

```bash
# ============================================
# Django Core Settings
# ============================================
DJANGO_SECRET_KEY=your-secret-key-change-this-in-production-min-50-chars
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,34.71.151.117
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ============================================
# Database (MySQL)
# ============================================
DB_ENGINE=django.db.backends.mysql
DB_HOST=mysql
DB_PORT=3306
DB_NAME=cdss_db
DB_USER=cdss_user
DB_PASSWORD=your-strong-db-password-change-this
DB_ROOT_PASSWORD=your-strong-root-password-change-this

# ============================================
# Redis Cache & Message Broker
# ============================================
REDIS_URL=redis://redis:6379/0

# ============================================
# Celery
# ============================================
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# ============================================
# OpenEMR FHIR API (OAuth2)
# ============================================
# 개발 환경 (Docker 네트워크 내부)
OPENEMR_BASE_URL=http://openemr:80
OPENEMR_FHIR_URL=http://openemr:80/apis/default/fhir
OPENEMR_CLIENT_ID=neuronova-cdss-internal
OPENEMR_CLIENT_SECRET=your-client-secret-from-registration

# OpenEMR Skip 모드 (개발 전용, 프로덕션에서는 False)
# OpenEMR 7.x Docker의 OAuth2 client_credentials 미지원 이슈로 인한 임시 우회
SKIP_OPENEMR_INTEGRATION=True

# ============================================
# Orthanc PACS (DICOM)
# ============================================
ORTHANC_API_URL=http://orthanc:8042
ORTHANC_USERNAME=orthanc
ORTHANC_PASSWORD=orthanc-strong-password-change-this

# ============================================
# HAPI FHIR Server
# ============================================
FHIR_SERVER_URL=http://hapi-fhir:8080/fhir

# FHIR OAuth2 (Celery Worker FHIR Outbox 사용)
# 프로덕션에서는 실제 OAuth2 서버 설정 필요
FHIR_OAUTH_TOKEN_URL=http://hapi-fhir:8080/oauth/token
FHIR_OAUTH_CLIENT_ID=neuronova-fhir-client
FHIR_OAUTH_CLIENT_SECRET=your-fhir-client-secret-change-this

# ============================================
# Security & Authentication
# ============================================
ENABLE_SECURITY=True
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# ============================================
# Grafana & Monitoring
# ============================================
GRAFANA_ADMIN_PASSWORD=admin123

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
```

**환경 변수 설정 가이드**:

| 변수명 | 필수 | 기본값 | 설명 | 프로덕션 권장값 |
|--------|------|--------|------|----------------|
| `DJANGO_SECRET_KEY` | ✅ | - | Django SECRET_KEY (50자 이상) | 랜덤 생성 (아래 참조) |
| `DEBUG` | ✅ | `False` | 디버그 모드 | `False` |
| `ALLOWED_HOSTS` | ✅ | - | 허용 호스트 (쉼표 구분) | `your-domain.com,www.your-domain.com` |
| `CORS_ALLOWED_ORIGINS` | ✅ | - | CORS 허용 오리진 | `https://your-domain.com` |
| `DB_PASSWORD` | ✅ | - | MySQL 비밀번호 (8자 이상) | 강력한 비밀번호 |
| `DB_ROOT_PASSWORD` | ✅ | - | MySQL root 비밀번호 (8자 이상) | 강력한 비밀번호 |
| `OPENEMR_CLIENT_ID` | ⚠️ | - | OpenEMR OAuth2 클라이언트 ID | `neuronova-cdss-internal` (선택) |
| `OPENEMR_CLIENT_SECRET` | ⚠️ | - | OpenEMR OAuth2 시크릿 | 등록 시 발급된 값 (선택) |
| `SKIP_OPENEMR_INTEGRATION` | ✅ | `True` | OpenEMR 연동 Skip 모드 | `True` (개발/테스트), `False` (운영 시 OAuth2 필요) |
| `ORTHANC_PASSWORD` | ✅ | `orthanc` | Orthanc 비밀번호 | 강력한 비밀번호 |
| `ENABLE_SECURITY` | ✅ | `True` | JWT 인증 활성화 | `True` |

**⚠️ 보안 경고**:
- `DEBUG=True`는 절대 프로덕션에서 사용 금지
- 모든 비밀번호는 8자 이상, 영문/숫자/특수문자 조합
- `DJANGO_SECRET_KEY`는 최소 50자 이상
- `.env` 파일은 절대 Git에 커밋하지 말 것

**💡 OpenEMR 연동 관련 설명**:
- `SKIP_OPENEMR_INTEGRATION=True`: OpenEMR API 호출을 Mock으로 대체 (개발/테스트 권장)
- `SKIP_OPENEMR_INTEGRATION=False`: 실제 OpenEMR API 호출 (프로덕션 환경, OAuth2 설정 필수)
- ⚠️ 표시된 `OPENEMR_CLIENT_ID`, `OPENEMR_CLIENT_SECRET`는 `SKIP_OPENEMR_INTEGRATION=False`일 때만 필수
- **테스트 배포 시**: `SKIP_OPENEMR_INTEGRATION=True` 사용 권장 (OAuth2 설정 불필요)
- **프로덕션 배포 시**: OpenEMR 연동이 필요하면 `50_OpenEMR_OAuth2_설정_가이드.md` 참조하여 OAuth2 클라이언트 등록 후 사용

### 5.4 React .env 파일 설정

**NeuroNova_03_front_end_react/00_test_client/.env.production (프로덕션용)**

```bash
# ============================================
# Production Environment (GCP VM)
# ============================================
# API Base URL (Nginx를 통한 접근)
REACT_APP_API_URL=https://your-domain.com/api

# OHIF Viewer Root (Orthanc Explorer 2)
# 프로덕션에서는 도메인 또는 내부 IP 사용
REACT_APP_OHIF_VIEWER_ROOT=https://your-domain.com:8042
# 또는 내부 네트워크: http://10.x.x.x:8042

# DICOMweb Root (Django Proxy 경유)
REACT_APP_DICOM_WEB_ROOT=https://your-domain.com/api/ris/dicom-web

# Monitoring Dashboards
REACT_APP_GRAFANA_URL=https://your-domain.com:3002
REACT_APP_PROMETHEUS_URL=https://your-domain.com:9090

# 자동 로그인 비활성화 (프로덕션 - 보안 필수)
REACT_APP_DEV_AUTO_LOGIN=false

# 브라우저 자동 실행 비활성화
BROWSER=none
```

**NeuroNova_03_front_end_react/00_test_client/.env.local (개발 전용)**

```bash
# ============================================
# Development Environment (로컬)
# ============================================
# 자동 로그인 활성화 (개발 편의)
REACT_APP_DEV_AUTO_LOGIN=true
REACT_APP_DEV_MOCK_USER=doctor

# API Base URL (로컬 Django)
REACT_APP_API_URL=http://localhost/api

# DICOMweb Root
REACT_APP_DICOM_WEB_ROOT=http://localhost/api/ris/dicom-web

# 브라우저 자동 실행 비활성화
BROWSER=none
```

**⚠️ 주의사항**:
- `.env.local`은 개발 전용, 프로덕션 VM에 **전송 금지** (cleanup-for-deployment.bat가 자동 삭제)
- `.env.production`만 GCP VM에 전송 (또는 VM에서 직접 `.env` 파일 생성)
- 프로덕션에서는 `REACT_APP_DEV_AUTO_LOGIN=false` 필수 (보안)
- `REACT_APP_OHIF_VIEWER_ROOT`를 Orthanc Explorer 2 경로로 설정 (`http://localhost:8042`)
- `REACT_APP_GRAFANA_URL`은 포트 3002 사용 (docker-compose에서 3000→3002로 매핑)

### 5.5 실제 .env 파일 생성 및 전송

**Windows 로컬에서 작업**:

```bash
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\02_django_server

# Django SECRET_KEY 생성 (PowerShell)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# .env 파일 수정 (메모장 또는 VSCode)
# - DJANGO_SECRET_KEY: 위에서 생성한 값
# - DB_PASSWORD: 강력한 비밀번호 (예: MySecureDB2026!)
# - DB_ROOT_PASSWORD: 강력한 root 비밀번호
# - ALLOWED_HOSTS: your-domain.com,www.your-domain.com
# - CORS_ALLOWED_ORIGINS: https://your-domain.com
```

**WinSCP를 통한 .env 파일 전송**:

```
1. WinSCP 접속 (GCP VM)

2. 로컬 → 원격 전송:
   로컬: d:\1222\NeuroNova_v1\NeuroNova_02_back_end\02_django_server\.env
   원격: ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env

3. React 환경 변수 전송:
   로컬: d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client\.env.production
   원격: ~/apps/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client/.env.production

4. 권한 확인 (PuTTY SSH):
   cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server
   chmod 600 .env
   ls -la .env
   # 출력: -rw------- 1 your-user your-user ... .env
```

**VM에서 환경 변수 검증**:

```bash
cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server

# .env 파일 존재 확인
ls -la .env

# 필수 변수 확인
grep "DJANGO_SECRET_KEY" .env
grep "DB_PASSWORD" .env
grep "ALLOWED_HOSTS" .env

# Django 설정 검증
docker compose run --rm django python manage.py check

# 예상 출력:
# System check identified no issues (0 silenced).
```

### 5.6 .env 파일 백업 전략

```bash
# .env 파일을 암호화하여 GCP Cloud Storage에 백업

# 1. .env 파일 암호화
gpg --symmetric --cipher-algo AES256 .env
# 출력: .env.gpg 생성

# 2. GCS에 업로드
gsutil cp .env.gpg gs://your-backup-bucket/neuronova-cdss/.env.gpg

# 3. 복원 시
gsutil cp gs://your-backup-bucket/neuronova-cdss/.env.gpg .
gpg --decrypt .env.gpg > .env
```

---

## 6. 데이터베이스 초기화

### 6.1 Docker Compose로 MySQL 시작

```bash
cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server

# MySQL만 먼저 시작
docker compose up -d mysql

# MySQL 준비 대기
docker compose logs -f mysql
# "ready for connections" 메시지 확인
```

### 6.2 데이터베이스 생성 및 권한 설정

```bash
# MySQL 컨테이너 접속
docker compose exec mysql mysql -uroot -p
# Enter password: (docker-compose.yml의 MYSQL_ROOT_PASSWORD)
```

```sql
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS cdss_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- OpenEMR용 데이터베이스
CREATE DATABASE IF NOT EXISTS openemr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 및 권한 부여
CREATE USER IF NOT EXISTS 'cdss_user'@'%' IDENTIFIED BY 'your-db-password';
GRANT ALL PRIVILEGES ON cdss_db.* TO 'cdss_user'@'%';
GRANT SELECT ON openemr.* TO 'cdss_user'@'%';
FLUSH PRIVILEGES;

-- 확인
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'cdss_user';

EXIT;
```

### 6.3 Django 마이그레이션 실행

```bash
# 모든 컨테이너 시작
docker compose up -d

# Django 컨테이너 대기
docker compose logs -f django

# 마이그레이션 적용
docker compose exec django python manage.py migrate
```

### 6.4 초기 데이터 로드

**관리자 계정 생성**

```bash
docker compose exec django python manage.py createsuperuser

# 입력:
# Username: admin
# Email: admin@hospital.com
# Password: (강력한 비밀번호)
```

**테스트 사용자 생성**

```bash
docker compose exec django python manage.py create_test_users

# 출력:
# Created user: admin (admin) - UUID: xxx
# Created user: doctor (doctor) - UUID: xxx
# ...
```

**Master & Test Data 통합 시딩 (v3.0)**

기존의 파편화된 시딩 명령 대신, 정합성이 검증된 v3.0 스크립트 사용을 권장합니다.

```bash
# Django 컨테이너 내부에서 실행
docker compose exec django python seed_minimal.py
# 또는
docker compose exec django python seed_full_system_test_data.py
```

**v3.0 시딩으로 보장되는 사항**:
- RIS `patient_id` 및 Order `ordered_by` 등 실제 DB 컬럼 매핑 완벽 반영
- LIS 유전체 데이터(BRCA1) 예제 포함
- Orthanc 영상 자동 동기화 트리거

---

## 7. Docker Compose 배포

### 7.1 docker-compose.yml 최적화

**NeuroNova_02_back_end/02_django_server/docker-compose.yml**

```yaml
version: '3.8'

networks:
  cdss-network:
    driver: bridge

volumes:
  mysql-data:
  redis-data:
  orthanc-data:
  logs-data:

services:
  mysql:
    image: mysql:8.0
    container_name: cdss-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-rootpassword}
      MYSQL_DATABASE: ${DB_NAME:-cdss_db}
      MYSQL_USER: ${DB_USER:-cdss_user}
      MYSQL_PASSWORD: ${DB_PASSWORD:-cdsspassword}
      TZ: Asia/Seoul
    volumes:
      - mysql-data:/var/lib/mysql
    # 보안: localhost에만 바인딩 (개발/디버깅용)
    ports:
      - "127.0.0.1:3306:3306"
    networks:
      - cdss-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: cdss-redis
    restart: always
    volumes:
      - redis-data:/data
    # 보안: localhost에만 바인딩 (개발/디버깅용)
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - cdss-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  django:
    build:
      context: .
      dockerfile: Dockerfile
    image: neuronova-cdss-django:latest
    container_name: cdss-django
    restart: always
    env_file:
      - .env
    volumes:
      - ./:/app
      - logs-data:/app/logs
    ports:
      - "8000:8000"
    networks:
      - cdss-network
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn cdss_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120"

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    image: neuronova-cdss-django:latest
    container_name: cdss-celery-worker
    restart: always
    env_file:
      - .env
    volumes:
      - ./:/app
      - logs-data:/app/logs
    networks:
      - cdss-network
    depends_on:
      - redis
      - django
    command: celery -A cdss_backend worker -l info --concurrency=4

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    image: neuronova-cdss-django:latest
    container_name: cdss-celery-beat
    restart: always
    env_file:
      - .env
    volumes:
      - ./:/app
      - logs-data:/app/logs
    networks:
      - cdss-network
    depends_on:
      - redis
      - django
    command: celery -A cdss_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

  orthanc:
    image: orthancteam/orthanc:latest
    container_name: cdss-orthanc
    restart: always
    volumes:
      - orthanc-data:/var/lib/orthanc/db
    # 보안: 외부 포트 노출 제거 (Django를 통해서만 접근)
    expose:
      - "8042"
      - "4242"
    networks:
      - cdss-network

  openemr:
    image: openemr/openemr:7.0.3
    container_name: cdss-openemr
    restart: always
    environment:
      MYSQL_HOST: mysql
      MYSQL_ROOT_PASS: ${DB_ROOT_PASSWORD:-rootpassword}
    # 보안: 외부 포트 노출 제거 (Django를 통해서만 접근)
    expose:
      - "80"
    networks:
      - cdss-network
    depends_on:
      mysql:
        condition: service_healthy

  hapi-fhir:
    image: hapiproject/hapi:latest
    container_name: cdss-hapi-fhir
    restart: always
    # 보안: 외부 포트 노출 제거 (Django를 통해서만 접근)
    expose:
      - "8080"
    networks:
      - cdss-network
```

### 7.2 서비스 시작

```bash
cd ~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server

# 이미지 빌드 및 컨테이너 시작
docker compose up -d --build

# 로그 확인
docker compose logs -f

# 서비스 상태 확인
docker compose ps
```

---

## 8. Nginx + React 빌드 배포

### 8.1 React 빌드 (VM에서)

```bash
# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 프로젝트 디렉토리로 이동
cd ~/apps/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client

# 환경 변수 파일 생성
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://your-domain.com
EOF

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build
```

### 8.2 Nginx 아키텍처 설계

현재 NeuroNova CDSS의 Nginx 구조는 다음과 같이 설계됩니다.

**시스템 아키텍처 전체 구조**

```
Internet → Cloudflare (HTTPS/WAF/CDN) → Nginx :80
                                           ↓
                        ┌──────────────────┼──────────────────┐
                        ↓                  ↓                  ↓
                   React SPA          Django API         OHIF Viewer
                   (정적파일)          :8000 (proxy)      (SPA 경로)
                   /                   /api/              /pacs-viewer
                                        ↓
                        ┌───────────────┼───────────────────┐
                        ↓               ↓                   ↓
                     MySQL           Redis              FastAPI
                     :3306           :6379              (AI Core)
                     (DB)            (캐시/Queue)       비동기 only
                                        ↓
                        ┌───────────────┼───────────────┐
                        ↓               ↓               ↓
                   Orthanc         HAPI FHIR        OpenEMR
                   :8042           :8080            (Docker)
                   (DICOM)         (FHIR R4)        동기 호출
                   동기 호출        동기 호출

                                        ↓
                                 Celery Workers
                                 - AI 추론 (비동기)
                                 - FHIR 동기화 (주기)
                                 - 데이터 정리 (주기)
```

**서비스 계층 설명**

**1. 외부 노출 계층 (Nginx)**
- **React SPA** (location /): 프론트엔드 메인 애플리케이션, OHIF Viewer 포함
- **Django API** (location /api/): REST API 엔드포인트, JWT 인증 처리
- **OHIF Viewer** (location /pacs-viewer): 의료영상 뷰어 전용 경로

**2. Django 직접 연결 (동기 처리)**
- **MySQL**: Django ORM 데이터베이스 (cdss_db)
- **Redis**: 캐시 저장소 + Celery 메시지 브로커

**3. Django Proxy 경유 (동기 처리 - HTTP 직접 호출)**
- **Orthanc** (:8042): DICOM 저장소 (Django RIS API → Orthanc, 동기 HTTP 호출)
- **HAPI FHIR** (:8080): FHIR R4 서버 (Django FHIR API → HAPI FHIR, 동기 HTTP 호출)
- **OpenEMR**: EMR 시스템 (Django EMR API → OpenEMR, 동기 HTTP 호출)

**4. 비동기 처리 (Celery Workers - AI만 비동기)**
- **AI 추론 (비동기)**: Django → Redis Queue → Celery Worker → FastAPI
- **FHIR 동기화 (주기)**: Celery Beat → Django → HAPI FHIR (동기 호출)
- **데이터 정리 (주기)**: Celery Beat → 캐시/로그 삭제

**동기 vs 비동기 구분**:
- **동기**: Orthanc, HAPI FHIR, OpenEMR - Django가 직접 HTTP 호출하고 응답 대기
- **비동기**: FastAPI (AI 추론) - Celery Queue를 통한 백그라운드 작업

**왜 이 구조가 최적인가**

**보안 강화**
- Orthanc, HAPI FHIR, OpenEMR이 외부에 직접 노출되지 않음
- Django에서 JWT 인증/인가 일괄 처리
- 민감한 의료 데이터 접근 제어
- MySQL, Redis는 127.0.0.1 바인딩 (로컬 디버깅용)

**단순성 및 유지보수**
- 단일 진입점 (Nginx)으로 모든 서비스 관리
- CORS 문제 없음 (동일 도메인)
- SSL 종료를 Cloudflare에서 처리

**성능**
- Cloudflare CDN을 통한 정적 파일 캐싱
- Redis 캐시로 데이터베이스 부하 감소
- Celery 비동기 처리로 API 응답 속도 개선
- 각 서비스별 독립적인 스케일링 가능

### 8.3 Nginx 설치

```bash
# Nginx 설치
sudo apt-get install -y nginx

# Nginx 시작
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8.4 Nginx 설정 파일 작성

```bash
sudo vi /etc/nginx/sites-available/neuronova-cdss
```

**/etc/nginx/sites-available/neuronova-cdss**

```nginx
upstream django_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Cloudflare 실제 IP 복원
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    # ... (Cloudflare IP 범위 전체)
    real_ip_header CF-Connecting-IP;

    access_log /var/log/nginx/neuronova-access.log;
    error_log /var/log/nginx/neuronova-error.log;

    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript application/xml;

    client_max_body_size 100M;

    # React 정적 파일
    location / {
        root /var/www/neuronova-cdss;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Django API 프록시
    location /api/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Swagger/ReDoc
    location ~ ^/(swagger|redoc|api/schema)/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # OHIF Viewer (React SPA 내부 경로)
    location /pacs-viewer {
        root /var/www/neuronova-cdss;
        try_files $uri /index.html;
    }
}
```

**보안 참고사항**

Orthanc (:8042), HAPI FHIR (:8080), OpenEMR은 Django API를 통해서만 접근합니다.
- Orthanc: Django RIS API (/api/ris/)를 통해 접근
- HAPI FHIR: Django FHIR API (/api/fhir/)를 통해 접근
- OpenEMR: Django EMR API (/api/emr/)를 통해 접근

이러한 서비스들은 Nginx에 직접 노출되지 않으며, Docker 내부 네트워크에서만 통신합니다.

```bash
# Symbolic link 생성
sudo ln -s /etc/nginx/sites-available/neuronova-cdss /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl reload nginx
```

### 8.5 React 빌드 파일 배포

```bash
# 웹 루트 디렉토리 생성
sudo mkdir -p /var/www/neuronova-cdss

# 빌드 파일 복사
sudo cp -r ~/apps/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client/build/* /var/www/neuronova-cdss/

# 권한 설정
sudo chown -R www-data:www-data /var/www/neuronova-cdss
sudo chmod -R 755 /var/www/neuronova-cdss
```

---

## 9. Cloudflare HTTPS 설정

### 9.1 Cloudflare 계정 설정

```
1. Cloudflare 가입 (무료 플랜)
   https://dash.cloudflare.com/sign-up

2. 도메인 추가
   Add a Site → your-domain.com

3. 네임서버 변경
   Cloudflare 제공 네임서버로 도메인 등록업체에서 변경

4. DNS 레코드 추가
   A 레코드 (@):
   - Name: @
   - IPv4: [GCP VM External IP]
   - Proxy: Proxied (주황색 구름)

   A 레코드 (www):
   - Name: www
   - IPv4: [GCP VM External IP]
   - Proxy: Proxied
```

### 9.2 SSL/TLS 설정

```
Cloudflare Dashboard > SSL/TLS

1. Overview
   - 암호화 모드: Flexible

2. Edge Certificates
   - Always Use HTTPS: On
   - Minimum TLS Version: TLS 1.2
   - TLS 1.3: On
   - Automatic HTTPS Rewrites: On
```

### 9.3 WAF 보안 설정

```
Security > WAF

1. Managed Rules
   - Cloudflare Managed Ruleset: On
   - Cloudflare OWASP Core Ruleset: On

2. Rate Limiting
   - Rule: API Rate Limit
   - Match: /api/*
   - Action: Block for 1 minute
   - Rate: 100 requests per 1 minute
```

### 9.4 접속 테스트

```bash
# DNS 전파 확인
nslookup your-domain.com

# HTTPS 접속 테스트
curl -I https://your-domain.com

# 브라우저 접속
https://your-domain.com
https://your-domain.com/api/docs/
```

---

## 10. 비동기 처리 설정 (Celery)

### 10.1 Celery 아키텍처

```
Django Application
        ↓
    (Submit Task)
        ↓
    Redis Broker (Queue)
        ↓
    Celery Workers
        ├─ AI Inference Worker
        ├─ FHIR Sync Worker
        └─ Email Worker
        ↓
    Redis Backend (Results)
```

### 10.2 비동기 태스크 예시

**ai/tasks.py**

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def run_ai_inference(self, study_id, model_type='tumor_detection'):
    from ai.models import AIJob
    from ris.models import RadiologyStudy

    study = RadiologyStudy.objects.get(study_id=study_id)
    ai_job = AIJob.objects.create(
        study_id=study_id,
        patient_id=study.patient_id,
        model_type=model_type,
        status='PROCESSING',
        task_id=self.request.id
    )

    # AI 추론 (외부 AI 서버 호출)
    result = {
        'tumor_detected': True,
        'confidence': 0.92,
        'location': {'x': 120, 'y': 85, 'z': 45}
    }

    ai_job.status = 'COMPLETED'
    ai_job.result = result
    ai_job.save()

    return result
```

**fhir/tasks.py**

```python
from celery import shared_task

@shared_task(bind=True)
def sync_patient_to_fhir(self, patient_id):
    from fhir.services import FHIRSyncService
    from emr.models import PatientCache

    patient = PatientCache.objects.get(patient_id=patient_id)

    service = FHIRSyncService()
    fhir_patient = service.patient_to_fhir(patient)
    service.send_to_hapi(fhir_patient, resource_type='Patient')

    return {'patient_id': patient_id, 'status': 'success'}
```

### 10.3 Celery Worker 모니터링

```bash
# Worker 로그 확인
docker compose logs -f celery-worker

# Beat 로그 확인
docker compose logs -f celery-beat

# Flower 설치 및 실행 (모니터링 UI)
docker compose exec django pip install flower
docker compose exec -d django celery -A cdss_backend flower --port=5555

# 접속: http://EXTERNAL_IP:5555
```

---

## 11. 배포 체크리스트

### 11.1 배포 전 체크리스트

**코드 준비**
- [ ] Git main 브랜치 최신 상태
- [ ] 마이그레이션 파일 커밋
- [ ] requirements.txt 업데이트
- [ ] .env.example 최신 상태

**보안**
- [ ] Django SECRET_KEY 변경 (50자 이상)
- [ ] DEBUG=False 설정
- [ ] ALLOWED_HOSTS 설정
- [ ] 데이터베이스 비밀번호 강력하게 설정
- [ ] .env 파일이 .gitignore에 포함

**인프라**
- [ ] GCP VM 생성 및 방화벽 설정
- [ ] Docker 설치
- [ ] Nginx 설치
- [ ] Cloudflare DNS 설정

### 11.2 배포 후 체크리스트

**기능 테스트**
- [ ] https://your-domain.com 접속 (React)
- [ ] https://your-domain.com/api/docs/ (Swagger)
- [ ] 로그인 테스트
- [ ] API 엔드포인트 테스트 (UC01-UC09)

**성능 확인**
- [ ] API 응답 시간 < 300ms
- [ ] Redis Hit Rate > 80%
- [ ] Celery Worker 정상 동작

**모니터링**
- [ ] Docker 컨테이너 상태 (docker compose ps)
- [ ] Nginx 로그 (/var/log/nginx/)
- [ ] Django 로그 (logs/app.log)

**보안**
- [ ] Cloudflare WAF 활성화
- [ ] Rate Limiting 설정
- [ ] HTTPS 강제 리다이렉트

---

## 12. 트러블슈팅

### Docker 관련

**문제: 컨테이너가 시작되지 않음**

```bash
docker compose logs [service-name]
docker compose down
docker compose up -d --build
```

**문제: Volume 권한 문제**

```bash
sudo chown -R 999:999 ./volumes/mysql-data
```

### Nginx 관련

**문제: 502 Bad Gateway**

```bash
docker compose ps django
docker compose restart django
sudo tail -f /var/log/nginx/neuronova-error.log
```

**문제: 정적 파일 로드 안 됨**

```bash
sudo chown -R www-data:www-data /var/www/neuronova-cdss/
sudo chmod -R 755 /var/www/neuronova-cdss/
sudo systemctl reload nginx
```

### Cloudflare 관련

**문제: Error 521 (Origin Down)**

```bash
sudo systemctl status nginx
sudo systemctl restart nginx
```

---

## 13. 시스템 다이어그램

### Phase 1 - 초기 배포

```
Internet → Cloudflare → GCP VM → Nginx
                                     ↓
                      ┌──────────┬──────────┬──────────┐
                      │ Django   │  MySQL   │  Redis   │
                      │ :8000    │  :3306   │  :6379   │
                      └──────────┴──────────┴──────────┘
```

### Phase 2 - 확장

```
Internet → Cloudflare → GCP VM → Nginx
                                     ↓
      ┌───────────┬───────────┬───────────┬───────────┐
      │ Django    │  MySQL    │  Redis    │ Orthanc   │
      │ :8000     │  :3306    │  :6379    │  :8042    │
      └───────────┴───────────┴───────────┴───────────┘
                       ↓
            ┌─────────────────────┐
            │  Celery Workers     │
            │  - AI Inference     │
            │  - FHIR Sync        │
            └─────────────────────┘
```

### Phase 3 - 운영 최적화 (현재, 보안 강화)

```
                    Internet
                       ↓
         ┌─────────────────────────┐
         │   Cloudflare (무료)      │
         │  - SSL/TLS              │
         │  - WAF                  │
         │  - Rate Limiting        │
         │  - CDN                  │
         └─────────────────────────┘
                       ↓ HTTPS
         ┌─────────────────────────┐
         │  GCP VM (asia-northeast3)│
         │  Ubuntu 22.04 LTS       │
         │  4 vCPU, 16GB RAM       │
         └─────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │   Nginx 1.22.1          │
         │  - Reverse Proxy        │
         │  - Static Serving       │
         │  - Gzip Compression     │
         │                         │
         │  외부 노출 경로:         │
         │  ✓ / (React SPA)        │
         │  ✓ /api/ (Django)       │
         │  ✓ /pacs-viewer (OHIF)  │
         └─────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │  Django API (Gunicorn)  │
         │  :8000 (localhost only) │
         │  4 Workers              │
         │                         │
         │  인증/인가 통합 처리     │
         └─────────────────────────┘
                       ↓
         ┌────────────┬────────────┬────────────┐
         │   MySQL    │   Redis    │  FastAPI   │
         │   :3306    │   :6379    │ (AI 추론)  │
         │   (DB)     │(캐시/Queue)│            │
         │  (local)   │  (local)   │            │
         └────────────┴────────────┴────────────┘
                       ↓
         ┌────────────┬────────────┬────────────┐
         │  Orthanc   │ HAPI FHIR  │  OpenEMR   │
         │   :8042    │   :8080    │  (외부)    │
         │  (DICOM)   │  (FHIR R4) │            │
         │  (expose)  │  (expose)  │  (expose)  │
         └────────────┴────────────┴────────────┘
                       ↓
         ┌─────────────────────────┐
         │  Celery Workers         │
         │  - celery-worker (x4)   │
         │  - celery-beat          │
         │  Tasks:                 │
         │    • AI 추론            │
         │    • FHIR 동기화        │
         │    • 데이터 정리        │
         └─────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │  Docker Network         │
         │  (cdss-network)         │
         └─────────────────────────┘

보안 구조:
- Nginx: React SPA와 Django API만 외부 노출
- Django: 모든 백엔드 서비스의 Gateway, JWT 인증 처리
- MySQL/Redis: 127.0.0.1 바인딩 (로컬 디버깅용)
- Orthanc/HAPI FHIR/OpenEMR: expose만 사용, 외부 포트 차단
- 모든 민감한 서비스는 Django를 통해서만 접근

동기 vs 비동기:
- 동기: Orthanc, HAPI FHIR, OpenEMR (Django HTTP 직접 호출)
- 비동기: FastAPI (AI 추론) - Celery Queue 사용
- 주기 작업: FHIR 동기화, 데이터 정리 (Celery Beat)

배포 특징:
- GitHub 기반 배포
- .env 파일 VM 로컬 관리
- Cloudflare 무료 (HTTPS, WAF, CDN)
- Nginx + React 빌드
- Celery 비동기 처리 (AI만)
- Docker Compose 전체 관리
```

---

**문서 버전**: 2.2
**최종 업데이트**: 2026-01-02
**작성자**: Claude AI & NeuroNova Team

**변경 이력**:
- v2.2 (2026-01-02): .env 파일 관리 강화 및 OpenEMR Skip 모드 추가
  - ✅ 별도 전송 필요 파일 체크리스트 추가 (Django .env, React .env.production)
  - ✅ Django .env 상세 설정 가이드 (환경 변수 설명 테이블)
  - ✅ React .env.production vs .env.local 구분
  - ✅ OpenEMR Skip 모드 설정 (`SKIP_OPENEMR_INTEGRATION=True`)
  - ✅ WinSCP 파일 전송 가이드 추가
  - ✅ .env 파일 검증 스크립트 추가
  - ✅ 보안 경고 강화 (비밀번호 정책, DEBUG=False)
  - 📖 참고: 로컬 개발 환경 자동 시작 - [README_자동실행.md](../README_자동실행.md)

- v2.1 (2025-12-30): 보안 강화 아키텍처 적용
  - Nginx 구조 명확화 (React SPA + Django API만 외부 노출)
  - Orthanc, HAPI FHIR 직접 노출 제거 (Django Proxy 경유)
  - MySQL, Redis localhost 바인딩 추가
  - Docker Compose expose vs ports 보안 설정
  - 시스템 다이어그램 Phase 3 보안 구조 반영

- v2.0 (2025-12-30): GCP VM + Docker + Cloudflare 환경 전면 재작성
  - PuTTY/WinSCP 접속 가이드
  - GitHub 배포 전략
  - .env 파일 관리 전략
  - 데이터베이스 초기화 스크립트
  - Nginx + React 빌드 배포
  - Cloudflare 무료 HTTPS
  - Celery 비동기 처리 (AI, FHIR)
  - 시스템 다이어그램 3단계 비교

---

## 관련 문서

- **로컬 개발 환경**: [README_자동실행.md](../README_자동실행.md) - Windows 개발 환경 자동 시작 가이드
- **빠른 온보딩**: [REF_CLAUDE_ONBOARDING_QUICK.md](REF_CLAUDE_ONBOARDING_QUICK.md)
- **초기 데이터 시딩**: [초기_데이터_시딩_가이드.md](초기_데이터_시딩_가이드.md)
- **OpenEMR 인증 설정**: [50_OpenEMR_OAuth2_설정_가이드.md](50_OpenEMR_OAuth2_설정_가이드.md)
- **OpenEMR 문제 해결**: [51_OpenEMR_인증_문제_해결_보고서.md](51_OpenEMR_인증_문제_해결_보고서.md)
- **Docker 개발 가이드**: [40_Docker_개발_가이드.md](40_Docker_개발_가이드.md)
