.env 파일 구조 완벽 정리
🎯 현재 존재하는 .env 파일들

NeuroNova_v1/
├── .env                    ← ① Docker Compose용 (컨테이너 설정)
├── .env.example            ← 템플릿 (무시)
│
├── NeuroNova_02_back_end/02_django_server/
│   ├── .env               ← ② Django 로컬 개발용
│   ├── .env.docker        ← ③ Django Docker 환경용 ⭐
│   └── .env.example       ← 템플릿 (무시)
│
└── NeuroNova_03_front_end_react/00_test_client/
    ├── .env               ← ④ React 로컬 개발용
    ├── .env.production    ← ⑤ React 프로덕션 빌드용
    └── .env.example       ← 템플릿 (무시)



각 파일의 역할
① .env (루트)
용도: Docker Compose 전역 설정
내용: 컨테이너 이름, 포트, 네트워크 설정
로드 방식: docker-compose.dev.yml이 자동으로 읽음
예시:

PROJECT_NAME=neuronova
DJANGO_HOST_PORT=8000
MYSQL_HOST_PORT=3306
② .env (Django 폴더) - 로컬 개발용
용도: 로컬 PC에서 Django 직접 실행 시
내용: Django 앱 설정 (SECRET_KEY, DEBUG, DB 연결 등)
로드 방식: settings.py가 읽음 (Line 22-24)
Docker에서는 사용 안 함!

③ .env.docker (Django 폴더) - Docker 환경용 ⭐⭐⭐
용도: Docker 컨테이너에서 Django 실행 시
내용: Django 앱 설정 (Docker 호스트명 사용)

④ .env (React 폴더) - 로컬 개발용
용도: npm start 실행 시
내용: API URL 등
예시: REACT_APP_API_URL=http://localhost:8000

⑤ .env.production (React 폴더) - 프로덕션 빌드용
용도: npm run build 실행 시
내용: 프로덕션 API URL
예시: REACT_APP_API_URL=/api

===
 VM 배포 시 필요한 파일 (2개만!)
✅ 전송할 파일:
로컬 파일	→	VM 경로	용도
NeuroNova_v1/.env	→	~/apps/NeuroNova_v1/.env	Docker Compose 설정
NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env.docker	→	~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env	Django 앱 설정 (이름 변경!)
🔥 중요: .env.docker를 .env로 이름 바꿔야 해요!
이유:
Django settings.py는 .env 파일을 찾음 (Line 22)
.env.docker는 Docker 환경 설정이 들어있음
그래서 .env.docker → .env로 이름 변경해서 전송

 Nginx 컨테이너에서 서빙 하려면 Vm에서 react 빌드해야한다. 

 ===============
 ===============

 VM IP 세션 변수 설정 및 배포 명령어
Windows PowerShell 사용 시:

# ============================================
# VM IP 세션 변수 설정
# ============================================
$VM_IP = "34.46.109.203"
$VM_USER = "rlagksquf1208"

# 변수 확인
Write-Host "VM IP: $VM_IP"
Write-Host "VM User: $VM_USER"

# ============================================
# Step 1: .env 파일 전송 (2개)
# ============================================

# 1-1. 루트 .env 파일 전송
scp d:\1222\NeuroNova_v1\.env ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/

# 1-2. Django .env 파일 전송 (.env.docker → .env로 이름 변경)
scp d:\1222\NeuroNova_v1\NeuroNova_02_back_end\02_django_server\.env.docker ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env

# ============================================
# Step 2: React 빌드 파일 전송
# ============================================

# 2-1. VM에 static/react-main 폴더 생성
ssh ${VM_USER}@${VM_IP} "mkdir -p ~/apps/NeuroNova_v1/static/react-main"

# 2-2. React 빌드 파일 전송
scp -r d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client\build\* ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/static/react-main/

# ============================================
# Step 3: VM에서 확인
# ============================================
ssh ${VM_USER}@${VM_IP}
WSL / Git Bash 사용 시:

# ============================================
# VM IP 세션 변수 설정
# ============================================
export VM_IP="34.46.109.203"
export VM_USER="rlagksquf1208"

# 변수 확인
echo "VM IP: $VM_IP"
echo "VM User: $VM_USER"

# ============================================
# Step 1: .env 파일 전송 (2개)
# ============================================

# 1-1. 루트 .env 파일 전송
scp /mnt/d/1222/NeuroNova_v1/.env ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/

# 1-2. Django .env 파일 전송
scp /mnt/d/1222/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env.docker ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env

# ============================================
# Step 2: React 빌드 파일 전송
# ============================================

# 2-1. VM에 폴더 생성
ssh ${VM_USER}@${VM_IP} "mkdir -p ~/apps/NeuroNova_v1/static/react-main"

# 2-2. React 빌드 파일 전송
scp -r /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client/build/* ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/static/react-main/

# ============================================
# Step 3: VM 접속
# ============================================
ssh ${VM_USER}@${VM_IP}
🚀 VM에서 실행할 명령어
SSH 접속 후:

# ============================================
# 전송된 파일 확인
# ============================================
cd ~/apps/NeuroNova_v1

# .env 파일 확인
echo "=== 루트 .env 확인 ==="
ls -la .env
head -3 .env

echo "=== Django .env 확인 ==="
ls -la NeuroNova_02_back_end/02_django_server/.env
head -3 NeuroNova_02_back_end/02_django_server/.env

echo "=== React 빌드 확인 ==="
ls -la static/react-main/
ls -la static/react-main/index.html

# ============================================
# Docker Compose 실행
# ============================================

# 이미지 빌드 (처음 한 번만)
docker-compose -f docker-compose.dev.yml build

# 컨테이너 시작
docker-compose -f docker-compose.dev.yml up -d

# 상태 확인
docker-compose -f docker-compose.dev.yml ps

# 로그 확인 (실시간)
docker-compose -f docker-compose.dev.yml logs -f
📋 빠른 실행 스크립트 (복사해서 사용)
PowerShell 버전:

$VM_IP = "34.46.109.203"
$VM_USER = "rlagksquf1208"

Write-Host "Step 1: .env 파일 전송 중..." -ForegroundColor Green
scp d:\1222\NeuroNova_v1\.env ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/
scp d:\1222\NeuroNova_v1\NeuroNova_02_back_end\02_django_server\.env.docker ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/NeuroNova_02_back_end/02_django_server/.env

Write-Host "Step 2: React 빌드 전송 중..." -ForegroundColor Green
ssh ${VM_USER}@${VM_IP} "mkdir -p ~/apps/NeuroNova_v1/static/react-main"
scp -r d:\1222\NeuroNova_v1\NeuroNova_03_front_end_react\00_test_client\build\* ${VM_USER}@${VM_IP}:~/apps/NeuroNova_v1/static/react-main/

Write-Host "완료! VM에 접속하세요: ssh ${VM_USER}@${VM_IP}" -ForegroundColor Cyan
지금 어떤 환경 쓰시나요? (PowerShell / WSL / Git Bash) 준비되시면 위 스크립트 복사해서 실행하시면 됩니다! 🚀
