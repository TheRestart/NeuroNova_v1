# OpenEMR OAuth2 Client 등록 절차

**실행 시점**: 최초 1회 (OpenEMR 설치 후)
**소요 시간**: 5분
**브라우저**: Chrome, Firefox, Edge 권장

---

## 🚀 빠른 시작

### 1단계: OpenEMR Admin Panel 접속

1. 브라우저 열기
2. 주소창에 입력: `http://localhost:8081`
3. 로그인 정보 입력:
   - Username: `admin`
   - Password: `pass`
4. [Login] 버튼 클릭

---

### 2단계: API Clients 메뉴 이동

**경로**: Administration → System → API Clients

1. 상단 메뉴에서 **Administration** 클릭
2. 좌측 메뉴에서 **System** 섹션 찾기
3. **API Clients** 클릭

![경로 표시]
```
┌─ Administration (상단 메뉴)
│
├─ System (좌측 메뉴)
│  ├─ Configuration
│  ├─ Settings
│  └─ API Clients ← 클릭
```

---

### 3단계: New Client 등록

#### 3.1 [Register New Client] 클릭

화면 우측 상단의 파란색 버튼을 클릭합니다.

#### 3.2 폼 입력

| 필드명 | 입력 값 | 참고 |
|--------|---------|------|
| Client Name | `NeuroNova CDSS Internal` | 식별용 |
| Client Identifier | `neuronova-cdss-internal` | 반드시 이 값 사용 |
| Client Secret | [Generate] 버튼 클릭 | 자동 생성 |

#### 3.3 Grant Types 선택

**체크 필요**:
- ✅ `client_credentials`

**체크 해제**:
- ❌ `authorization_code`
- ❌ `refresh_token`
- ❌ `password`

#### 3.4 Scopes 선택

**필수 Scopes** (모두 체크):
- ✅ `system/Patient.read`
- ✅ `system/Patient.write`
- ✅ `system/Encounter.read`
- ✅ `system/Encounter.write`
- ✅ `system/Observation.read`
- ✅ `system/Observation.write`

#### 3.5 저장

1. [Save] 버튼 클릭
2. **Client Secret 복사** (화면에 1회만 표시됨)
   ```
   예시: a7f3e9d2c1b8f4e6a9d5c2b7f1e4a8d3
   ```
3. 메모장에 붙여넣기 또는 안전한 곳에 보관

---

### 4단계: Django 환경 변수 설정

#### 4.1 .env 파일 열기

```bash
# PowerShell 또는 CMD에서 실행
cd d:\1222\NeuroNova_v1\NeuroNova_02_back_end\02_django_server
notepad .env
```

#### 4.2 환경 변수 추가

파일 하단에 다음 3줄 추가:

```bash
OPENEMR_FHIR_URL=http://openemr:80/apis/default/fhir
OPENEMR_CLIENT_ID=neuronova-cdss-internal
OPENEMR_CLIENT_SECRET=<3단계에서_복사한_Secret>
```

**예시**:
```bash
OPENEMR_FHIR_URL=http://openemr:80/apis/default/fhir
OPENEMR_CLIENT_ID=neuronova-cdss-internal
OPENEMR_CLIENT_SECRET=a7f3e9d2c1b8f4e6a9d5c2b7f1e4a8d3
```

#### 4.3 저장 및 닫기

- [파일] → [저장] (Ctrl+S)
- 메모장 닫기

---

### 5단계: Django 재시작

```bash
# PowerShell에서 실행
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml restart django

# 로그 확인 (30초 대기)
docker-compose -f docker-compose.dev.yml logs -f django
```

**성공 메시지**:
```
django_1  | System check identified no issues (0 silenced).
django_1  | Starting development server at http://0.0.0.0:8000/
```

---

### 6단계: 인증 테스트

#### 6.1 Django Shell 진입

```bash
docker-compose -f docker-compose.dev.yml exec django python manage.py shell
```

#### 6.2 토큰 발급 테스트

```python
from emr.services.openemr_client import OpenEMRClient

client = OpenEMRClient()
print(f"Client ID: {client.client_id}")
print(f"Secret: {client.client_secret[:10]}..." if client.client_secret else "None")

token = client.get_access_token()
print(f"Token: {token[:30]}..." if token else "FAILED")
```

**예상 출력 (성공)**:
```
Client ID: neuronova-cdss-internal
Secret: a7f3e9d2c1...

INFO: Requesting OpenEMR Token from http://openemr:80/oauth2/default/token
INFO: Access Token retrieved successfully

Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1...
```

**예상 출력 (실패)**:
```
Client ID:
Secret: None

ERROR: Failed to retrieve OpenEMR Access Token

Token: FAILED
```

→ 실패 시 [트러블슈팅](#트러블슈팅) 참조

#### 6.3 Shell 종료

```python
exit()
```

---

## ✅ 완료 체크리스트

설정이 완료되었는지 확인하십시오:

- [ ] OpenEMR Admin Panel 로그인 성공
- [ ] API Clients에 `neuronova-cdss-internal` 등록
- [ ] Client Secret 복사 완료
- [ ] Grant Type: `client_credentials` 체크
- [ ] Scopes: `system/Patient.*`, `system/Encounter.*` 체크
- [ ] `.env` 파일에 `OPENEMR_CLIENT_ID` 추가
- [ ] `.env` 파일에 `OPENEMR_CLIENT_SECRET` 추가
- [ ] Django 컨테이너 재시작 완료
- [ ] Django Shell에서 토큰 발급 성공

---

## 🚨 트러블슈팅

### 문제 1: Admin Panel 접속 안 됨

**증상**: `http://localhost:8081`에 접속 불가

**해결**:
```bash
# OpenEMR 컨테이너 상태 확인
docker ps | grep openemr

# 컨테이너가 없다면 시작
docker-compose -f docker-compose.dev.yml up -d openemr

# 30초 대기 후 재접속
```

---

### 문제 2: Client Secret이 표시 안 됨

**원인**: 이미 저장되었거나 페이지를 새로고침함

**해결**:
1. API Clients 목록에서 `neuronova-cdss-internal` 찾기
2. [Edit] 클릭
3. [Regenerate Secret] 버튼 클릭
4. 새 Secret 복사

---

### 문제 3: Django에서 Client ID가 빈 값

**원인**: 환경 변수 전달 실패

**해결**:
```bash
# .env 파일 내용 확인
cd NeuroNova_02_back_end/02_django_server
cat .env | findstr OPENEMR

# Docker 컨테이너 환경 변수 확인
docker exec neuronova-django-dev env | findstr OPENEMR

# 없다면 컨테이너 재빌드
cd d:\1222\NeuroNova_v1
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

---

### 문제 4: 400 Bad Request (invalid_request)

**원인**: Grant Type이 체크되지 않음

**해결**:
1. OpenEMR Admin Panel → API Clients
2. `neuronova-cdss-internal` 편집
3. **Grant Types** 섹션에서 `client_credentials` 체크
4. [Save]
5. Django 재시작

---

## 📚 추가 문서

- [50_OpenEMR_OAuth2_설정_가이드.md](../01_doc/50_OpenEMR_OAuth2_설정_가이드.md) - 상세 가이드
- [51_OpenEMR_인증_문제_해결_보고서.md](../01_doc/51_OpenEMR_인증_문제_해결_보고서.md) - 문제 분석

---

**작성일**: 2026-01-02
**업데이트**: 필요 시 수시 업데이트
