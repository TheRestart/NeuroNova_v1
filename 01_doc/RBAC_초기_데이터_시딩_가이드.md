# NeuroNova RBAC & Menus - 초기 데이터 시딩 가이드

**최종 수정일**: 2026-01-05
**버전**: 1.0
**목적**: RBAC (Role-Based Access Control) 및 동적 메뉴 시스템의 초기 데이터를 시딩하는 단계별 가이드

---

## 📋 목차

1. [개요](#개요)
2. [시스템 구성 요소](#시스템-구성-요소)
3. [사전 준비](#사전-준비)
4. [단계별 시딩 절차](#단계별-시딩-절차)
5. [데이터 구조 상세](#데이터-구조-상세)
6. [검증 및 확인](#검증-및-확인)
7. [트러블슈팅](#트러블슈팅)
8. [확장 가이드](#확장-가이드)

---

## 🎯 개요

### 목적
RBAC 시스템의 초기 데이터(Role, Permission, Menu, Test Users)를 자동으로 생성하여 즉시 테스트 가능한 환경을 구축합니다.

### 생성되는 데이터
- **7개 역할(Role)**: DOCTOR, NURSE, ADMIN, PATIENT, LAB_TECH, RAD_TECH, INSTITUTION
- **2개 권한(Permission)**: VIEW_DASHBOARD, VIEW_PATIENT_LIST
- **2개 메뉴(Menu)**: 대시보드, 환자 목록
- **9개 메뉴 라벨(MenuLabel)**: 역할별 메뉴 텍스트
- **13개 Role-Permission 매핑**
- **2개 Menu-Permission 매핑**
- **4개 테스트 사용자**: doctor1, nurse1, admin1, patient1

---

## 🏗️ 시스템 구성 요소

### Backend (Django)
```
rbac/
  ├── models.py              # Role, Permission, UserRole, RolePermission
  └── management/
      └── commands/
          └── seed_rbac_data.py  # 시딩 스크립트

menus/
  ├── models.py              # Menu, MenuLabel, MenuPermission
  └── management/
      └── commands/
          └── (empty)        # 메뉴 시딩은 rbac 스크립트에 포함
```

### Frontend (React)
```
src/
  ├── types/
  │   ├── menu.ts           # MenuNode, MenuResponse
  │   └── rbac.ts           # Permission, Role
  ├── services/
  │   ├── menuService.ts    # GET /api/menus/my/
  │   ├── rbacService.ts    # GET /api/rbac/permissions/me/
  │   └── permissionSocket.ts  # WebSocket 연결
  ├── stores/
  │   └── authStore.ts      # menus, permissions 상태 관리
  └── components/
      ├── Sidebar.tsx       # 동적 메뉴 렌더링
      └── ProtectedRoute.tsx  # 권한 기반 라우팅
```

---

## ✅ 사전 준비

### 1. 마이그레이션 실행 확인
RBAC 및 Menus 앱의 마이그레이션이 적용되어 있어야 합니다.

```powershell
# 1-1. 마이그레이션 상태 확인
cd NeuroNova_02_back_end/02_django_server
python manage.py showmigrations rbac menus
```

**기대 출력**:
```
rbac
 [ ] 0001_initial      # 체크되지 않음
menus
 [ ] 0001_initial
 [ ] 0002_initial
```

```powershell
# 1-2. 마이그레이션 실행
python manage.py migrate rbac
python manage.py migrate menus
```

**성공 출력**:
```
Running migrations:
  Applying rbac.0001_initial... OK
  Applying menus.0001_initial... OK
  Applying menus.0002_initial... OK
```

### 2. Django 서버 설정 확인
`settings.py`에 앱이 등록되어 있는지 확인합니다.

```python
INSTALLED_APPS = [
    ...
    "rbac",   # Role-Based Access Control
    "menus",  # Menu Management
    ...
]
```

### 3. URL 라우팅 확인
`cdss_backend/urls.py`에 API 엔드포인트가 등록되어 있는지 확인합니다.

```python
urlpatterns = [
    ...
    path("api/rbac/", include("rbac.urls")),
    path("api/menus/", include("menus.urls")),
    ...
]
```

---

## 🚀 단계별 시딩 절차

### Step 1: 초기 데이터 시딩 실행

**명령어**:
```powershell
cd NeuroNova_02_back_end/02_django_server
python manage.py seed_rbac_data
```

**출력 예시**:
```
======================================================================
[START] RBAC & Menus 초기 데이터 시딩
======================================================================

[STEP 1/7] 권한(Permission) 생성 중...
  [생성] VIEW_DASHBOARD: 대시보드 조회
  [생성] VIEW_PATIENT_LIST: 환자 목록 조회
✓ 2개 권한(Permission) 생성 완료

[STEP 2/7] 역할(Role) 생성 중...
  [생성] DOCTOR: 의사
  [생성] NURSE: 간호사
  [생성] ADMIN: 관리자
  [생성] PATIENT: 환자
  [생성] LAB_TECH: 검사실 기사
  [생성] RAD_TECH: 영상의학 기사
  [생성] INSTITUTION: 기관
✓ 7개 역할(Role) 생성 완료

[STEP 3/7] 메뉴(Menu) 생성 중...
  [생성] DASHBOARD: /dashboard
  [생성] PATIENT_LIST: /patients
✓ 2개 메뉴(Menu) 생성 완료

[STEP 4/7] 메뉴 라벨 생성 중...
  [생성] DASHBOARD [DEFAULT]: 대시보드
  [생성] DASHBOARD [DOCTOR]: 진료 대시보드
  [생성] DASHBOARD [NURSE]: 간호 대시보드
  [생성] DASHBOARD [ADMIN]: 관리자 대시보드
  [생성] PATIENT_LIST [DEFAULT]: 환자 목록
  [생성] PATIENT_LIST [DOCTOR]: 환자 목록
  [생성] PATIENT_LIST [NURSE]: 담당 환자
  [생성] PATIENT_LIST [ADMIN]: 전체 환자
  [생성] PATIENT_LIST [PATIENT]: 내 정보
✓ 9개 메뉴 라벨 생성 완료

[STEP 5/7] Role-Permission 매핑 중...
  [생성] ADMIN → VIEW_DASHBOARD
  [생성] ADMIN → VIEW_PATIENT_LIST
  [생성] DOCTOR → VIEW_DASHBOARD
  [생성] DOCTOR → VIEW_PATIENT_LIST
  [생성] NURSE → VIEW_DASHBOARD
  [생성] NURSE → VIEW_PATIENT_LIST
  [생성] PATIENT → VIEW_DASHBOARD
  [생성] LAB_TECH → VIEW_DASHBOARD
  [생성] RAD_TECH → VIEW_DASHBOARD
  [생성] INSTITUTION → VIEW_DASHBOARD
✓ 10개 Role-Permission 매핑 완료

[STEP 6/7] Menu-Permission 매핑 중...
  [생성] DASHBOARD → VIEW_DASHBOARD
  [생성] PATIENT_LIST → VIEW_PATIENT_LIST
✓ 2개 Menu-Permission 매핑 완료

[STEP 7/7] 테스트 사용자 생성 중...
  [생성] doctor1 (DOCTOR): 김의사
  [생성] nurse1 (NURSE): 이간호사
  [생성] admin1 (ADMIN): 관리자
  [생성] patient1 (PATIENT): 박환자
✓ 4개 테스트 사용자 생성 완료

======================================================================
[DONE] RBAC 데이터 시딩 완료
======================================================================

[NEXT STEP] React 앱에서 로그인 테스트:
  - doctor1 / password123
  - nurse1 / password123
  - admin1 / password123
  - patient1 / password123
```

### Step 2: 기존 데이터 삭제 후 재시딩 (선택)

기존 데이터를 삭제하고 처음부터 다시 생성하려면 `--clear` 옵션을 사용합니다.

```powershell
python manage.py seed_rbac_data --clear
```

**출력**:
```
[CLEAR] 기존 데이터 삭제 중...
✓ 기존 데이터 삭제 완료

[STEP 1/7] 권한(Permission) 생성 중...
...
```

⚠️ **주의**: `--clear` 옵션은 **모든 RBAC 관련 데이터를 삭제**하므로 프로덕션 환경에서는 사용하지 마세요.

---

## 📦 데이터 구조 상세

### 1. 역할(Role)

| 코드 | 이름 | 설명 | 권한 |
|------|------|------|------|
| **DOCTOR** | 의사 | 진단, 처방, 환자 기록 조회/수정 | VIEW_DASHBOARD, VIEW_PATIENT_LIST |
| **NURSE** | 간호사 | 환자 케어, 처방 확인, 기록 조회 | VIEW_DASHBOARD, VIEW_PATIENT_LIST |
| **ADMIN** | 관리자 | 전체 시스템 관리 및 모든 권한 | VIEW_DASHBOARD, VIEW_PATIENT_LIST |
| **PATIENT** | 환자 | 본인 기록 조회 권한만 | VIEW_DASHBOARD |
| **LAB_TECH** | 검사실 기사 | 검사 결과 입력 및 조회 | VIEW_DASHBOARD |
| **RAD_TECH** | 영상의학 기사 | 영상 검사 촬영 및 조회 | VIEW_DASHBOARD |
| **INSTITUTION** | 기관 | 외부 기관 연동 | VIEW_DASHBOARD |

### 2. 권한(Permission)

| 코드 | 이름 | 설명 |
|------|------|------|
| **VIEW_DASHBOARD** | 대시보드 조회 | 메인 대시보드 페이지 접근 권한 |
| **VIEW_PATIENT_LIST** | 환자 목록 조회 | 환자 목록 페이지 접근 권한 |

### 3. 메뉴(Menu)

| ID | 경로 | 아이콘 | 부모 | Breadcrumb Only |
|----|------|--------|------|-----------------|
| **DASHBOARD** | /dashboard | 📊 | - | false |
| **PATIENT_LIST** | /patients | 👥 | - | false |

### 4. 메뉴 라벨(MenuLabel)

역할에 따라 다른 메뉴 텍스트를 표시합니다.

| 메뉴 | 역할 | 라벨 텍스트 |
|------|------|-------------|
| DASHBOARD | DEFAULT | 대시보드 |
| DASHBOARD | DOCTOR | 진료 대시보드 |
| DASHBOARD | NURSE | 간호 대시보드 |
| DASHBOARD | ADMIN | 관리자 대시보드 |
| PATIENT_LIST | DEFAULT | 환자 목록 |
| PATIENT_LIST | DOCTOR | 환자 목록 |
| PATIENT_LIST | NURSE | 담당 환자 |
| PATIENT_LIST | ADMIN | 전체 환자 |
| PATIENT_LIST | PATIENT | 내 정보 |

### 5. 테스트 사용자

| Username | Password | Email | Role | Full Name | Department |
|----------|----------|-------|------|-----------|------------|
| doctor1 | password123 | doctor1@neuronova.com | DOCTOR | 김의사 | 진료의학과 |
| nurse1 | password123 | nurse1@neuronova.com | NURSE | 이간호사 | 간호부 |
| admin1 | password123 | admin1@neuronova.com | ADMIN | 관리자 | 시스템관리팀 |
| patient1 | password123 | patient1@neuronova.com | PATIENT | 박환자 | - |

---

## 🔍 검증 및 확인

### 1. Django Admin에서 확인

```powershell
# Django Admin 접속
http://localhost:8000/admin/

# 확인 항목:
# - rbac/Role: 7개 역할
# - rbac/Permission: 2개 권한
# - menus/Menu: 2개 메뉴
# - menus/MenuLabel: 9개 라벨
# - acct/User: 4개 테스트 사용자
```

### 2. API 엔드포인트 테스트

#### 2-1. 로그인
```bash
curl -X POST http://localhost:8000/api/acct/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "doctor1", "password": "password123"}'
```

**응답 예시**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "doctor1",
    "email": "doctor1@neuronova.com",
    "role": "doctor"
  }
}
```

#### 2-2. 내 권한 조회
```bash
curl -X GET http://localhost:8000/api/rbac/permissions/me/ \
  -H "Authorization: Bearer <TOKEN>"
```

**응답 예시** (DOCTOR):
```json
{
  "permissions": [
    "VIEW_DASHBOARD",
    "VIEW_PATIENT_LIST"
  ]
}
```

#### 2-3. 내 메뉴 조회
```bash
curl -X GET http://localhost:8000/api/menus/my/ \
  -H "Authorization: Bearer <TOKEN>"
```

**응답 예시** (DOCTOR):
```json
{
  "menus": [
    {
      "id": "DASHBOARD",
      "path": "/dashboard",
      "icon": "📊",
      "breadcrumbOnly": false,
      "labels": {
        "DEFAULT": "대시보드",
        "DOCTOR": "진료 대시보드"
      },
      "children": []
    },
    {
      "id": "PATIENT_LIST",
      "path": "/patients",
      "icon": "👥",
      "breadcrumbOnly": false,
      "labels": {
        "DEFAULT": "환자 목록",
        "DOCTOR": "환자 목록"
      },
      "children": []
    }
  ]
}
```

### 3. React 앱에서 확인

#### 3-1. 로그인 테스트
```
1. React 앱 실행: npm start
2. 로그인 페이지 접속: http://localhost:3000/login
3. doctor1 / password123 로그인
4. 대시보드 페이지로 리다이렉트 확인
5. Sidebar에 "진료 대시보드", "환자 목록" 메뉴 표시 확인
```

#### 3-2. 역할별 메뉴 라벨 확인
```
# DOCTOR로 로그인
→ "진료 대시보드", "환자 목록"

# NURSE로 로그인
→ "간호 대시보드", "담당 환자"

# PATIENT로 로그인
→ "대시보드", "내 정보" (환자 목록 숨김)
```

#### 3-3. 권한 기반 라우팅 테스트
```
1. PATIENT 계정으로 로그인
2. 직접 /patients 페이지로 이동 시도
3. → 403 Forbidden 페이지로 리다이렉트 확인
```

---

## 🔧 트러블슈팅

### 문제 1: 시딩 스크립트 실행 시 "No such table" 에러
**증상**:
```
django.db.utils.OperationalError: no such table: rbac_role
```

**원인**: 마이그레이션이 적용되지 않음

**해결**:
```powershell
python manage.py migrate rbac
python manage.py migrate menus
```

---

### 문제 2: "UNIQUE constraint failed" 에러
**증상**:
```
django.db.utils.IntegrityError: UNIQUE constraint failed: rbac_role.code
```

**원인**: 이미 데이터가 존재하는 상태에서 재시딩 시도

**해결**:
```powershell
# --clear 옵션으로 기존 데이터 삭제 후 재시딩
python manage.py seed_rbac_data --clear
```

---

### 문제 3: React에서 메뉴가 표시되지 않음
**증상**: Sidebar가 비어있음

**원인**:
1. 백엔드 API 호출 실패
2. 사용자에게 할당된 권한이 없음
3. WebSocket 연결 실패

**해결**:
```javascript
// 1. 브라우저 개발자 도구 → Console 확인
// 네트워크 에러 확인

// 2. API 응답 확인
GET /api/menus/my/
GET /api/rbac/permissions/me/

// 3. authStore 상태 확인
console.log(useAuthStore.getState().menus)
console.log(useAuthStore.getState().permissions)
```

---

### 문제 4: 테스트 사용자 로그인 실패
**증상**: "Invalid credentials" 에러

**원인**: 비밀번호가 제대로 설정되지 않음

**해결**:
```powershell
# Django shell에서 비밀번호 재설정
python manage.py shell

>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='doctor1')
>>> user.set_password('password123')
>>> user.save()
>>> exit()
```

---

## 📚 확장 가이드

### 1. 새로운 역할 추가

**시나리오**: "PHARMACIST (약사)" 역할 추가

**Step 1**: `seed_rbac_data.py` 수정
```python
roles_data = [
    ...
    ('PHARMACIST', '약사', '처방 조제 및 복약 지도 권한'),
]
```

**Step 2**: 권한 할당
```python
role_perm_map = {
    ...
    'PHARMACIST': ['VIEW_DASHBOARD', 'VIEW_PRESCRIPTION'],
}
```

**Step 3**: 재시딩
```powershell
python manage.py seed_rbac_data --clear
```

---

### 2. 새로운 메뉴 추가

**시나리오**: "처방 목록" 메뉴 추가

**Step 1**: Permission 생성
```python
permissions_data = [
    ...
    ('VIEW_PRESCRIPTION_LIST', '처방 목록 조회'),
]
```

**Step 2**: Menu 생성
```python
menus_data = [
    ...
    ('PRESCRIPTION_LIST', '/prescriptions', '💊', None, False),
]
```

**Step 3**: MenuLabel 생성
```python
labels_data = [
    ...
    ('PRESCRIPTION_LIST', 'DEFAULT', '처방 목록'),
    ('PRESCRIPTION_LIST', 'DOCTOR', '내 처방'),
    ('PRESCRIPTION_LIST', 'PHARMACIST', '조제 대기'),
]
```

**Step 4**: Menu-Permission 매핑
```python
menu_perm_map = {
    ...
    'PRESCRIPTION_LIST': ['VIEW_PRESCRIPTION_LIST'],
}
```

**Step 5**: 재시딩
```powershell
python manage.py seed_rbac_data --clear
```

---

### 3. 계층 구조 메뉴 추가

**시나리오**: "설정" 그룹 메뉴 아래에 "프로필 설정", "알림 설정" 하위 메뉴 추가

**Step 1**: 부모 메뉴 생성
```python
menus_data = [
    ...
    # 부모 메뉴 (path 없음)
    ('SETTINGS', None, '⚙️', None, False),
    # 자식 메뉴
    ('SETTINGS_PROFILE', '/settings/profile', None, 'SETTINGS', False),
    ('SETTINGS_NOTIFICATION', '/settings/notifications', None, 'SETTINGS', False),
]
```

**Step 2**: 메뉴 생성 로직 수정 (parent 처리)
```python
def _create_menus(self):
    menus = {}

    # 1차: 부모 메뉴 먼저 생성
    for menu_id, path, icon, parent_id, breadcrumb_only in menus_data:
        if parent_id is None:
            menu, created = Menu.objects.get_or_create(
                id=menu_id,
                defaults={'path': path, 'icon': icon, 'breadcrumbOnly': breadcrumb_only}
            )
            menus[menu_id] = menu

    # 2차: 자식 메뉴 생성
    for menu_id, path, icon, parent_id, breadcrumb_only in menus_data:
        if parent_id is not None:
            parent = menus.get(parent_id)
            menu, created = Menu.objects.get_or_create(
                id=menu_id,
                defaults={'path': path, 'icon': icon, 'parent': parent, 'breadcrumbOnly': breadcrumb_only}
            )
            menus[menu_id] = menu

    return menus
```

---

### 4. 작업 수준 권한 추가

**시나리오**: "환자 생성", "환자 수정", "환자 삭제" 권한 추가

**Step 1**: Permission 추가
```python
permissions_data = [
    ...
    # 메뉴 접근 수준
    ('VIEW_PATIENT_LIST', '환자 목록 조회'),

    # 작업 수준 (확장)
    ('CREATE_PATIENT', '환자 생성'),
    ('UPDATE_PATIENT', '환자 수정'),
    ('DELETE_PATIENT', '환자 삭제'),
]
```

**Step 2**: Role-Permission 매핑
```python
role_perm_map = {
    'ADMIN': [
        'VIEW_PATIENT_LIST',
        'CREATE_PATIENT',
        'UPDATE_PATIENT',
        'DELETE_PATIENT'
    ],
    'DOCTOR': [
        'VIEW_PATIENT_LIST',
        'CREATE_PATIENT',
        'UPDATE_PATIENT'
    ],
    'NURSE': [
        'VIEW_PATIENT_LIST'
    ],
}
```

**Step 3**: React에서 버튼 조건부 렌더링
```tsx
import { useAuthStore } from './stores/authStore';

const PatientListPage = () => {
  const { checkPermission } = useAuthStore();

  return (
    <div>
      <h1>환자 목록</h1>

      {checkPermission('CREATE_PATIENT') && (
        <button>환자 생성</button>
      )}

      {checkPermission('UPDATE_PATIENT') && (
        <button>환자 수정</button>
      )}

      {checkPermission('DELETE_PATIENT') && (
        <button>환자 삭제</button>
      )}
    </div>
  );
};
```

---

## 📝 체크리스트

### 초기 설정 완료 체크리스트
- [ ] rbac, menus 앱이 INSTALLED_APPS에 등록됨
- [ ] rbac, menus 마이그레이션 실행 완료
- [ ] URL 라우팅 설정 완료 (`/api/rbac/`, `/api/menus/`)
- [ ] WebSocket 라우팅 설정 완료 (`/ws/permissions/`)

### 시딩 완료 체크리스트
- [ ] `python manage.py seed_rbac_data` 실행 성공
- [ ] Django Admin에서 7개 Role 확인
- [ ] Django Admin에서 2개 Permission 확인
- [ ] Django Admin에서 2개 Menu 확인
- [ ] Django Admin에서 9개 MenuLabel 확인
- [ ] Django Admin에서 4개 테스트 사용자 확인

### Frontend 통합 확인 체크리스트
- [ ] doctor1으로 로그인 성공
- [ ] Sidebar에 "진료 대시보드", "환자 목록" 메뉴 표시
- [ ] nurse1으로 로그인 시 "간호 대시보드", "담당 환자" 표시
- [ ] patient1으로 로그인 시 "환자 목록" 메뉴 숨김
- [ ] patient1으로 `/patients` 접근 시 403 페이지 표시
- [ ] WebSocket 연결 성공 (브라우저 Console 확인)

---

## 🔗 관련 문서

- [RBAC_INTEGRATION.md](../NeuroNova_03_front_end_react/01_react_client/RBAC_INTEGRATION.md): React 통합 가이드
- [brain_tumor_dev_통합_완료_보고서_20260105.md](brain_tumor_dev_통합_완료_보고서_20260105.md): Backend 통합 완료 보고서
- [brain_tumor_dev_React_통합_완료_20260105.md](brain_tumor_dev_React_통합_완료_20260105.md): Frontend 통합 완료 보고서
- [REF_CLAUDE_CONTEXT.md](REF_CLAUDE_CONTEXT.md#-rbac--menus-시스템-2026-01-05-통합): RBAC 시스템 아키텍처

---

**이 문서는 중간에 다른 담당자가 이어서 작업할 수 있도록 단계별로 상세히 작성되었습니다.**
**문의사항이 있으면 프로젝트 관리자에게 문의하세요.**
