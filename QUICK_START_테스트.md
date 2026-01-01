# 무한 새로고침 수정 - 빠른 테스트 가이드

**30초 안에 테스트 시작하기**

---

## 🚀 Windows PowerShell (백엔드)

```powershell
# 1. 프로젝트 루트로 이동
cd d:\1222\NeuroNova_v1

# 2. Docker Compose 전체 스택 시작
docker-compose -f docker-compose.dev.yml up -d

# 3. 상태 확인 (모든 컨테이너가 "Up" 상태여야 함)
docker-compose -f docker-compose.dev.yml ps
```

---

## 🚀 WSL Ubuntu (프론트엔드)

**새 PowerShell 창을 열어서 실행:**

```powershell
# 1. WSL 진입
wsl -d Ubuntu-22.04

# 2. WSL 내부에서 프로젝트 디렉토리 이동
cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client

# 3. React 서버 시작
PORT=3001 npm start
```

**또는 한 줄 명령어:**
```powershell
wsl -d Ubuntu-22.04 -e bash -c "cd /mnt/d/1222/NeuroNova_v1/NeuroNova_03_front_end_react/00_test_client && PORT=3001 npm start"
```

---

## ✅ 테스트 확인 사항

### 브라우저: http://localhost:3001

**1. 무한 새로고침 테스트**
- [ ] 페이지가 1회만 로드됨 ✅
- [ ] 계속 새로고침되지 않음 ✅

**2. 자동 로그인 테스트**
- [ ] 1-2초 후 자동으로 대시보드 이동 ✅
- [ ] 네비게이션 바에 "admin (Admin)" 표시 ✅

**3. 개발자 도구 콘솔 (F12)**
```
[DEV MODE] Auto-login enabled
[DEV MODE] Real admin logged in: {...}
```
- [ ] 위 메시지가 1회만 표시됨 ✅

**4. 페이지 새로고침 (F5)**
- [ ] "Already logged in - skipping auto-login" 메시지 ✅
- [ ] 로그인 상태 유지됨 ✅
- [ ] 무한 새로고침 없음 ✅

---

## ❌ 문제 발생 시

### Django 서버 접속 불가
```powershell
# 컨테이너 로그 확인
docker-compose -f docker-compose.dev.yml logs django

# 테스트 계정 재생성
docker-compose -f docker-compose.dev.yml exec django python manage.py create_test_users
```

### React 서버 시작 실패
```bash
# 캐시 삭제
rm -rf node_modules/.cache

# 서버 재시작
PORT=3001 npm start
```

### API 연결 실패
```bash
# .env.local 확인
cat .env.local | grep API_URL

# 출력: REACT_APP_API_URL=http://localhost/api (정상)
```

---

## 🎉 성공!

모든 체크박스가 ✅ 이면 **무한 새로고침 버그가 완전히 수정**되었습니다!

다음 단계: [TEST_무한새로고침_수정_확인.md](TEST_무한새로고침_수정_확인.md)에서 상세 테스트 진행
