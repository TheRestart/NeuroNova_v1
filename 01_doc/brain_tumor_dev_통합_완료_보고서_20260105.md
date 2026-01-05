# brain_tumor_dev 코드 통합 완료 보고서

**작업일**: 2026-01-05
**작업자**: Claude (AI Assistant)
**상태**: ✅ Backend Django 통합 완료, React 통합 대기 중

---

## 1. 개요

brain_tumor_dev 프로젝트의 React + Django 코드를 NeuroNova_v1에 통합하여 역할 기반 접근 제어(RBAC) 및 동적 메뉴 시스템을 구현하였습니다.

## 2. 완료된 작업

### 2.1 RBAC 앱 통합

#### 네임스페이스 충돌 해결
- `apps.accounts` → `rbac` 앱으로 이름 변경
- 기존 NeuroNova의 `acct` 앱과 충돌 방지

#### User 모델 설계 변경
- **기존**: `AbstractBaseUser` 상속 (AUTH_USER_MODEL)
- **변경**: `UserProfile` 모델 (acct.User OneToOne 확장)
- **이유**: Django는 하나의 AUTH_USER_MODEL만 허용하므로, 기존 acct.User를 유지하면서 RBAC 기능만 확장

#### 생성된 모델
```python
# rbac/models/
- UserProfile: acct.User와 OneToOne, RBAC 기능 추가
- Role: 역할 모델 (DOCTOR, NURSE, ADMIN 등)
- Permission: 권한 모델 (VIEW_PATIENT, CREATE_ORDER 등)
- UserRole: User-Role M2M through 모델
- RolePermission: Role-Permission M2M through 모델 (Menu FK 포함)
```

#### API 엔드포인트
- `GET /api/rbac/permissions/me/`: 현재 사용자 권한 조회
- `POST /api/rbac/permissions/user/<id>/`: 특정 사용자 권한 업데이트 (관리자용)

#### WebSocket 실시간 알림
- `ws://host/ws/permissions/`: 권한 변경 시 실시간 푸시
- Channels 사용, Redis 백엔드
- UserPermissionConsumer 구현

### 2.2 Menus 앱 통합

#### 생성된 모델
```python
# menus/models.py
- Menu: 메뉴 기본 정보 (path, icon, parent-child 구조)
- MenuLabel: 역할별 메뉴 라벨 (다국어 지원)
- MenuPermission: Menu-Permission 매핑 (접근 제어)
```

#### 주요 기능
- **계층 구조**: parent FK를 통한 무한 depth 메뉴 트리
- **역할별 라벨**: 동일 메뉴도 역할에 따라 다른 이름 표시
  - 예: PATIENT_LIST → DOCTOR: "환자 목록", NURSE: "담당 환자"
- **권한 기반 필터링**: get_user_menus(user) → 접근 가능한 메뉴만 반환
- **부모 메뉴 자동 포함**: 자식 메뉴 접근 시 부모 메뉴도 자동 포함

#### API 엔드포인트
- `GET /api/menus/my/`: 현재 사용자의 메뉴 트리 반환 (JSON)

### 2.3 Django 설정 업데이트

#### INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ...
    "rbac",   # Role-Based Access Control
    "menus",  # Menu Management
]
```

#### URL 패턴
```python
urlpatterns = [
    # ...
    path("api/rbac/", include("rbac.urls")),
    path("api/menus/", include("menus.urls")),
]
```

#### WebSocket 라우팅
```python
# api/routing.py
websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
] + rbac.routing.websocket_urlpatterns  # ws/permissions/ 추가
```

### 2.4 마이그레이션 생성

```bash
$ python manage.py makemigrations rbac menus

Migrations for 'menus':
  menus/migrations/0001_initial.py
    - Create model Menu
    - Create model MenuLabel
    - Create model MenuPermission

Migrations for 'rbac':
  rbac/migrations/0001_initial.py
    - Create model Permission
    - Create model UserProfile
    - Create model Role
    - Create model RolePermission
    - Create model UserRole
```

**상태**: 생성 완료, 실행 대기 중

---

## 3. 아키텍처 설계

### 3.1 RBAC 데이터 흐름

```
[User] ─1:1─> [UserProfile] ─M:M─> [Role] ─M:M─> [Permission]
                     │                 │
                     └─────[UserRole]──┘
                                   │
                            [RolePermission] ─FK─> [Menu]
```

### 3.2 메뉴 접근 제어 흐름

```
1. User 로그인
2. get_user_permissions(user) → Permission 코드 리스트
3. MenuPermission 테이블에서 해당 Permission → Menu ID 매핑
4. 부모 메뉴 재귀적으로 포함 (include_parents)
5. Menu 쿼리셋 조회 (prefetch labels, children)
6. build_menu_tree() → JSON 트리 구조 반환
7. React에서 메뉴 렌더링
```

### 3.3 WebSocket 권한 알림 흐름

```
1. 관리자가 사용자 권한 변경 (POST /api/rbac/permissions/user/<id>/)
2. notify_permission_changed(user_id) 호출
3. Channels channel_layer.group_send(f"user_{user_id}", {...})
4. UserPermissionConsumer.permission_changed() 실행
5. 해당 사용자의 브라우저에 WebSocket 메시지 전송
6. React에서 권한 재조회 및 메뉴 리렌더링
```

---

## 4. 파일 구조

```
NeuroNova_02_back_end/02_django_server/
├── rbac/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py (UserProfile)
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── user_role.py
│   │   └── role_permission.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── permission_service.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py (UserPermissionConsumer)
│   ├── routing.py (WebSocket)
│   ├── urls.py
│   └── views.py
│
├── menus/
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── 0002_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py (Menu, MenuLabel, MenuPermission)
│   ├── services.py (get_user_menus, get_accessible_menus)
│   ├── urls.py
│   ├── utils.py (build_menu_tree)
│   └── views.py
│
├── api/
│   └── routing.py (WebSocket 통합)
│
└── cdss_backend/
    ├── settings.py (INSTALLED_APPS 업데이트)
    ├── urls.py (URL 패턴 추가)
    └── asgi.py (WebSocket 설정)
```

---

## 5. 주요 기술적 결정

### 5.1 AUTH_USER_MODEL 충돌 해결

**문제**: brain_tumor_dev의 User 모델과 NeuroNova의 acct.User 모델이 모두 AUTH_USER_MODEL이 될 수 없음

**해결책**: 
- rbac.UserProfile로 변경 (OneToOne with acct.User)
- 기존 acct.User는 AUTH_USER_MODEL 유지
- brain_tumor_dev 호환성을 위해 User = UserProfile 별칭 제공

### 5.2 Audit 앱 충돌 해결

**문제**: brain_tumor_dev의 audit 앱이 NeuroNova의 기존 audit 앱과 충돌 (AuditService 의존성)

**해결책**:
- 기존 NeuroNova audit 앱 유지 (ai/services.py가 AuditService 사용)
- brain_tumor_dev audit 앱 내용은 통합하지 않음
- RBAC/Menus 앱과 독립적으로 운영

### 5.3 네임스페이스 설계

- `rbac.*`: Role-Based Access Control
- `menus.*`: Menu Management
- `acct.*`: NeuroNova 기존 인증/권한 (유지)
- `audit.*`: NeuroNova 기존 감사 로그 (유지)

---

## 6. 다음 단계

### 6.1 Backend (Django)

- [ ] 마이그레이션 실행:
  ```bash
  python manage.py migrate rbac
  python manage.py migrate menus
  ```

- [ ] Permission/Role 시딩:
  ```python
  # management/commands/seed_rbac_data.py 작성 필요
  - Permission: VIEW_PATIENT, CREATE_ORDER, VIEW_DASHBOARD 등
  - Role: DOCTOR, NURSE, ADMIN, PATIENT
  - Menu: DASHBOARD, PATIENT_LIST, ORDER_CREATE 등
  - MenuLabel: 역할별 라벨 설정
  - MenuPermission: Menu-Permission 매핑
  ```

- [ ] API 테스트:
  ```bash
  # 권한 조회
  curl -H "Authorization: Bearer <token>" http://localhost:8000/api/rbac/permissions/me/
  
  # 메뉴 조회
  curl -H "Authorization: Bearer <token>" http://localhost:8000/api/menus/my/
  ```

### 6.2 Frontend (React)

- [ ] brain_tumor_dev React 코드 통합:
  - `NeuroNova_03_front_end_react/01_react_client/`에 복사
  - 권한 기반 라우팅 컴포넌트 (PrivateRoute, RoleBasedRoute)
  - 동적 메뉴 렌더링 컴포넌트 (Sidebar, MenuTree)
  - WebSocket 권한 알림 Hook (usePermissions)

- [ ] API 클라이언트 설정:
  ```javascript
  // src/api/rbac.js
  export const getMyPermissions = () => api.get('/api/rbac/permissions/me/')
  export const getMyMenus = () => api.get('/api/menus/my/')
  
  // src/hooks/usePermissions.js
  - useEffect로 WebSocket 연결 (ws://host/ws/permissions/)
  - PERMISSION_CHANGED 메시지 수신 시 권한 재조회
  ```

- [ ] 라우팅 통합:
  ```javascript
  // src/App.jsx
  const menuTree = useMenus() // GET /api/menus/my/
  const permissions = usePermissions() // GET /api/rbac/permissions/me/
  
  <Router>
    {menuTree.map(menu => (
      <RoleBasedRoute 
        path={menu.path} 
        requiredPermission={menu.permission}
      />
    ))}
  </Router>
  ```

### 6.3 통합 테스트

- [ ] Backend-Frontend API 통신 검증
- [ ] WebSocket 실시간 권한 알림 동작 확인
- [ ] 역할별 메뉴 렌더링 확인 (DOCTOR vs NURSE)
- [ ] 권한 없는 메뉴 접근 차단 확인

---

## 7. 참고 문서

- [LOG_작업이력.md](../LOG_작업이력.md): 2026-01-05 항목 업데이트 완료
- [작업_계획_요약.md](../../작업_계획_요약.md): 다음 단계 추가 완료
- [brain_tumor_dev 원본](D:\1222\brain_tumor_dev\): 참조용 유지

---

**작성**: Claude AI Assistant
**검토**: 필요 시 사용자 검토 요청
