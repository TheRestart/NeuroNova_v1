# API 자동문서화 가이드 (API Auto-Documentation Guide)

**최종 수정일**: 2025-12-28
**목적**: Swagger/OpenAPI를 통한 API 자동 문서화 설정 및 사용 가이드

---

## 📋 목차

1. [개요](#1-개요)
2. [drf-spectacular 설치 및 설정](#2-drf-spectacular-설치-및-설정)
3. [Swagger UI 활용](#3-swagger-ui-활용)
4. [API 문서화 주석 작성법](#4-api-문서화-주석-작성법)
5. [스키마 커스터마이징](#5-스키마-커스터마이징)
6. [프론트엔드 팀 공유 방법](#6-프론트엔드-팀-공유-방법)

---

## 1. 개요

### 1.1 왜 자동문서화가 필요한가?

- **수동 문서 작성의 문제점**:
  - 코드와 문서의 불일치 (코드는 변경했는데 문서는 업데이트 안 함)
  - 시간 소모적 (API 하나 추가할 때마다 문서 수정)
  - 휴먼 에러 (오타, 누락)

- **자동문서화의 장점**:
  - 코드가 곧 문서 (Code as Documentation)
  - 실시간 API 테스트 가능 (Swagger UI)
  - 프론트엔드 팀과의 협업 효율성 증가
  - OpenAPI 3.0 표준 준수

### 1.2 사용 도구

- **drf-spectacular**: Django REST Framework용 OpenAPI 3.0 자동 생성 라이브러리
- **Swagger UI**: 대화형 API 문서 인터페이스
- **ReDoc**: 깔끔한 정적 API 문서 (선택)

---

## 2. drf-spectacular 설치 및 설정

### 2.1 패키지 설치

```bash
pip install drf-spectacular
```

`requirements.txt` 업데이트:
```txt
drf-spectacular==0.27.0
```

### 2.2 settings.py 설정

```python
# cdss_backend/settings.py

INSTALLED_APPS = [
    # ... 기존 앱들
    'rest_framework',
    'drf_spectacular',  # 추가
    # ...
]

REST_FRAMEWORK = {
    # ... 기존 설정
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # 추가
}

# drf-spectacular 설정
SPECTACULAR_SETTINGS = {
    'TITLE': 'NeuroNova CDSS API',
    'DESCRIPTION': 'Clinical Decision Support System API Documentation\n\n'
                   '## 인증\n'
                   'JWT 토큰 기반 인증을 사용합니다.\n'
                   '1. `/api/acct/login/` 엔드포인트로 로그인\n'
                   '2. 응답으로 받은 `access` 토큰을 복사\n'
                   '3. 우측 상단 "Authorize" 버튼 클릭\n'
                   '4. `Bearer <access_token>` 형식으로 입력\n\n'
                   '## 사용자 역할\n'
                   '- Admin: 시스템 관리자\n'
                   '- Doctor: 의사\n'
                   '- RIB: 영상의학과 의사\n'
                   '- Lab: 임상병리사\n'
                   '- Nurse: 간호사\n'
                   '- Patient: 환자\n'
                   '- External: 외부 시스템',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,  # Request/Response 스키마 분리
    'SCHEMA_PATH_PREFIX': r'/api',

    # 보안 스키마 정의
    'SECURITY': [
        {
            'bearerAuth': []
        }
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },

    # 태그 정렬 및 그룹화
    'TAGS': [
        {'name': 'acct', 'description': '인증/권한 (Authentication & Authorization)'},
        {'name': 'emr', 'description': 'EMR 관리 (Electronic Medical Records)'},
        {'name': 'ocs', 'description': '처방 관리 (Order Communication System)'},
        {'name': 'lis', 'description': '검사 관리 (Laboratory Information System)'},
        {'name': 'ris', 'description': '영상 관리 (Radiology Information System)'},
        {'name': 'ai', 'description': 'AI 분석 (AI Job Management)'},
        {'name': 'alert', 'description': '알림 (Notification System)'},
        {'name': 'audit', 'description': '감사 로그 (Audit Logs)'},
    ],

    # 에러 응답 예시 추가
    'ENUM_NAME_OVERRIDES': {
        'ValidationErrorEnum': 'drf_spectacular.types.ValidationErrorEnum',
    },
}
```

### 2.3 urls.py 설정

```python
# cdss_backend/urls.py
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,      # OpenAPI 스키마 JSON/YAML
    SpectacularSwaggerView,  # Swagger UI
    SpectacularRedocView,    # ReDoc UI
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API 엔드포인트
    path('api/acct/', include('acct.urls')),
    path('api/emr/', include('emr.urls')),
    path('api/ocs/', include('ocs.urls')),
    # ... 기타 API

    # API 문서화 엔드포인트
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### 2.4 접속 URL

서버 실행 후 다음 URL로 접속:

- **Swagger UI** (대화형): http://localhost:8000/api/docs/
- **ReDoc** (정적): http://localhost:8000/api/redoc/
- **OpenAPI Schema** (JSON): http://localhost:8000/api/schema/

---

## 3. Swagger UI 활용

### 3.1 Swagger UI 화면 구성

```
┌─────────────────────────────────────────────────┐
│  NeuroNova CDSS API v1.0.0        [Authorize]  │
├─────────────────────────────────────────────────┤
│  Servers: http://localhost:8000                 │
├─────────────────────────────────────────────────┤
│  ▼ acct - 인증/권한                             │
│    POST /api/acct/login/          로그인        │
│    POST /api/acct/register/       회원가입      │
│    POST /api/acct/logout/         로그아웃      │
│    GET  /api/acct/me/             내 정보 조회  │
│                                                  │
│  ▼ emr - EMR 관리                               │
│    GET  /api/emr/patients/        환자 목록     │
│    POST /api/emr/patients/        환자 등록     │
│    GET  /api/emr/patients/{id}/   환자 상세     │
│    ...                                           │
└─────────────────────────────────────────────────┘
```

### 3.2 인증 설정 방법

1. **로그인 API 테스트**:
   - `POST /api/acct/login/` 펼치기
   - "Try it out" 클릭
   - Request Body에 테스트 계정 입력:
     ```json
     {
       "username": "doctor1",
       "password": "password123"
     }
     ```
   - "Execute" 클릭
   - 응답에서 `access` 토큰 복사

2. **Authorize 설정**:
   - 우측 상단 "Authorize" 버튼 클릭
   - `bearerAuth` 입력란에 다음 형식으로 입력:
     ```
     Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```
   - "Authorize" 클릭
   - 이후 모든 API 요청에 자동으로 토큰이 포함됨

### 3.3 API 테스트 방법

1. 테스트할 API 엔드포인트 펼치기
2. "Try it out" 클릭
3. 파라미터 입력 (Path, Query, Body)
4. "Execute" 클릭
5. 응답 확인 (Status Code, Response Body)

---

## 4. API 문서화 주석 작성법

### 4.1 ViewSet 문서화

```python
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, status

@extend_schema_view(
    list=extend_schema(
        summary="환자 목록 조회",
        description="등록된 모든 환자의 목록을 조회합니다. 페이지네이션이 적용됩니다.",
        tags=['emr'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='환자 이름 또는 SSN으로 검색',
                required=False,
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='페이지 번호 (기본값: 1)',
                required=False,
            ),
        ],
        responses={
            200: PatientSerializer(many=True),
            401: OpenApiExample(
                'Unauthorized',
                value={
                    'error': {
                        'code': 'ERR_001',
                        'message': '인증에 실패했습니다.',
                        'timestamp': '2025-12-28T10:30:00Z'
                    }
                }
            ),
        }
    ),
    retrieve=extend_schema(
        summary="환자 상세 조회",
        description="특정 환자의 상세 정보를 조회합니다.",
        tags=['emr'],
        responses={
            200: PatientSerializer,
            404: OpenApiExample(
                'Not Found',
                value={
                    'error': {
                        'code': 'ERR_201',
                        'message': '요청한 환자 정보를 찾을 수 없습니다.',
                        'timestamp': '2025-12-28T10:30:00Z'
                    }
                }
            ),
        }
    ),
    create=extend_schema(
        summary="환자 등록",
        description="새로운 환자를 등록합니다. OpenEMR과 Django DB에 병렬로 저장됩니다.",
        tags=['emr'],
        request=PatientSerializer,
        responses={
            201: PatientSerializer,
            400: OpenApiExample(
                'Validation Error',
                value={
                    'error': {
                        'code': 'ERR_101',
                        'message': '입력값이 올바르지 않습니다.',
                        'field': 'ssn',
                        'detail': '주민등록번호 형식이 올바르지 않습니다.',
                        'timestamp': '2025-12-28T10:30:00Z'
                    }
                }
            ),
        }
    ),
    update=extend_schema(
        summary="환자 정보 수정",
        description="환자 정보를 수정합니다.",
        tags=['emr'],
    ),
    partial_update=extend_schema(
        summary="환자 정보 부분 수정",
        description="환자 정보의 일부 필드만 수정합니다.",
        tags=['emr'],
    ),
    destroy=extend_schema(
        summary="환자 삭제",
        description="환자 정보를 삭제합니다.",
        tags=['emr'],
        responses={
            204: None,
            404: OpenApiExample(
                'Not Found',
                value={
                    'error': {
                        'code': 'ERR_201',
                        'message': '요청한 환자 정보를 찾을 수 없습니다.',
                        'timestamp': '2025-12-28T10:30:00Z'
                    }
                }
            ),
        }
    ),
)
class PatientViewSet(viewsets.ModelViewSet):
    """
    환자 관리 API

    환자 정보의 CRUD 기능을 제공합니다.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsDoctorOrRIB]
```

### 4.2 APIView 문서화

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class LoginAPIView(APIView):
    """
    로그인 API

    사용자 인증 후 JWT 토큰을 발급합니다.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="로그인",
        description="사용자 인증 후 JWT Access Token과 Refresh Token을 발급합니다.",
        tags=['acct'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': '사용자 아이디',
                        'example': 'doctor1'
                    },
                    'password': {
                        'type': 'string',
                        'description': '비밀번호',
                        'example': 'password123',
                        'format': 'password'
                    },
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'access': {'type': 'string', 'description': 'JWT Access Token'},
                    'refresh': {'type': 'string', 'description': 'JWT Refresh Token'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'role': {'type': 'string', 'enum': ['Admin', 'Doctor', 'RIB', 'Lab', 'Nurse', 'Patient', 'External']},
                        }
                    }
                },
                'example': {
                    'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'user': {
                        'id': 1,
                        'username': 'doctor1',
                        'role': 'Doctor'
                    }
                }
            },
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    'error': {
                        'code': 'ERR_001',
                        'message': '인증에 실패했습니다. 아이디 또는 비밀번호를 확인해주세요.',
                        'timestamp': '2025-12-28T10:30:00Z'
                    }
                }
            ),
        }
    )
    def post(self, request):
        # 로그인 로직
        pass
```

### 4.3 Serializer 문서화

```python
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

class PatientSerializer(serializers.ModelSerializer):
    """환자 정보 Serializer"""

    ssn = serializers.CharField(
        max_length=13,
        help_text="주민등록번호 (13자리, 하이픈 없이)",
        required=True
    )

    birth_date = serializers.DateField(
        help_text="생년월일 (YYYY-MM-DD 형식)",
        required=True
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_age(self, obj):
        """나이 계산 (읽기 전용)"""
        from datetime import date
        today = date.today()
        return today.year - obj.birth_date.year

    class Meta:
        model = Patient
        fields = ['id', 'name', 'ssn', 'birth_date', 'gender', 'phone', 'address', 'age']
        read_only_fields = ['id', 'age']
        examples = {
            'application/json': {
                'name': '홍길동',
                'ssn': '9001011234567',
                'birth_date': '1990-01-01',
                'gender': 'M',
                'phone': '010-1234-5678',
                'address': '서울시 강남구'
            }
        }
```

### 4.4 에러 응답 문서화

```python
from drf_spectacular.utils import OpenApiResponse

# 공통 에러 응답 정의
ERROR_RESPONSES = {
    401: OpenApiResponse(
        description='인증 실패',
        examples={
            'application/json': {
                'error': {
                    'code': 'ERR_001',
                    'message': '인증에 실패했습니다.',
                    'timestamp': '2025-12-28T10:30:00Z'
                }
            }
        }
    ),
    403: OpenApiResponse(
        description='권한 없음',
        examples={
            'application/json': {
                'error': {
                    'code': 'ERR_002',
                    'message': '해당 작업을 수행할 권한이 없습니다.',
                    'timestamp': '2025-12-28T10:30:00Z'
                }
            }
        }
    ),
    404: OpenApiResponse(
        description='리소스 없음',
        examples={
            'application/json': {
                'error': {
                    'code': 'ERR_201',
                    'message': '요청한 리소스를 찾을 수 없습니다.',
                    'timestamp': '2025-12-28T10:30:00Z'
                }
            }
        }
    ),
}

# 사용 예시
@extend_schema(
    summary="환자 조회",
    responses={
        200: PatientSerializer,
        **ERROR_RESPONSES  # 공통 에러 응답 적용
    }
)
def retrieve(self, request, pk=None):
    pass
```

---

## 5. 스키마 커스터마이징

### 5.1 커스텀 필터 문서화

```python
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

class PatientFilter(filters.FilterSet):
    """환자 필터"""
    name = filters.CharFilter(lookup_expr='icontains', help_text='환자 이름 (부분 일치)')
    gender = filters.ChoiceFilter(choices=[('M', 'Male'), ('F', 'Female')], help_text='성별')
    min_age = filters.NumberFilter(field_name='birth_date', lookup_expr='lte', help_text='최소 나이')

    class Meta:
        model = Patient
        fields = ['name', 'gender', 'min_age']

# ViewSet에서 사용
@extend_schema(
    parameters=[
        OpenApiParameter('name', description='환자 이름 검색', required=False),
        OpenApiParameter('gender', description='성별 필터 (M/F)', required=False, enum=['M', 'F']),
        OpenApiParameter('min_age', description='최소 나이', required=False, type=int),
    ]
)
class PatientViewSet(viewsets.ModelViewSet):
    filterset_class = PatientFilter
    # ...
```

### 5.2 페이지네이션 문서화

```python
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema

class StandardResultsSetPagination(PageNumberPagination):
    """
    표준 페이지네이션

    - page_size: 한 페이지당 항목 수 (기본값: 20)
    - max_page_size: 최대 페이지 크기 (100)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ViewSet에서 사용
@extend_schema(
    parameters=[
        OpenApiParameter('page', description='페이지 번호', required=False, type=int),
        OpenApiParameter('page_size', description='페이지 크기 (기본값: 20, 최대: 100)', required=False, type=int),
    ]
)
class PatientViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    # ...
```

### 5.3 버전 관리

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}

# urls.py
urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/v2/', include('api.v2.urls')),
]

# drf-spectacular 설정
SPECTACULAR_SETTINGS = {
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}
```

---

## 6. 프론트엔드 팀 공유 방법

### 6.1 OpenAPI Schema 파일 생성

스키마 파일을 JSON/YAML 형식으로 Export:

```bash
# JSON 형식
python manage.py spectacular --file schema.json

# YAML 형식
python manage.py spectacular --format openapi-yaml --file schema.yaml
```

생성된 파일을 프론트엔드 팀에 공유:
- Git 저장소에 커밋: `api_schema/schema.json`
- 또는 Swagger UI URL 공유: `http://localhost:8000/api/docs/`

### 6.2 TypeScript 타입 자동 생성

프론트엔드 팀이 OpenAPI 스키마에서 TypeScript 타입을 자동 생성할 수 있습니다:

```bash
# openapi-typescript 설치
npm install -D openapi-typescript

# 타입 생성
npx openapi-typescript http://localhost:8000/api/schema/ --output src/types/api.d.ts
```

생성된 타입 사용 예시:
```typescript
import type { components } from './types/api';

type Patient = components['schemas']['Patient'];
type PatientList = components['schemas']['PaginatedPatientList'];

const patient: Patient = {
  id: 1,
  name: '홍길동',
  ssn: '9001011234567',
  // TypeScript가 자동 완성 및 타입 체크
};
```

### 6.3 Postman Collection 생성

Swagger UI에서 Postman Collection으로 Export 가능:

1. Swagger UI 접속 (`http://localhost:8000/api/docs/`)
2. 우측 상단 "..." 메뉴 → "Export" → "Postman Collection v2.1"
3. `neuronova_cdss.postman_collection.json` 파일 다운로드
4. Postman에서 Import

### 6.4 실시간 협업 워크플로우

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Backend    │────▶│ Django      │────▶│  Swagger    │
│  Developer  │     │ Server      │     │  UI         │
│  (당신)     │     │ (localhost) │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               │ http://localhost:8000/api/docs/
                                               │
┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│  Frontend   │────▶│  TypeScript │◀────│  OpenAPI    │
│  Developer  │     │  Types      │     │  Schema     │
│  (팀원)     │     │             │     │  (JSON)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

**워크플로우**:
1. Backend: API 개발 및 `@extend_schema` 주석 작성
2. Backend: 서버 실행 (`python manage.py runserver`)
3. Frontend: Swagger UI 접속하여 API 명세 확인
4. Frontend: "Try it out"으로 실시간 테스트
5. Frontend: OpenAPI 스키마로 TypeScript 타입 자동 생성
6. 양측: 변경사항 발생 시 즉시 반영 (새로고침만 하면 됨)

### 6.5 환경별 서버 설정

```python
# settings.py
SPECTACULAR_SETTINGS = {
    # ... 기존 설정
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Local Development'},
        {'url': 'https://dev.neuronova.com', 'description': 'Development Server'},
        {'url': 'https://api.neuronova.com', 'description': 'Production Server'},
    ],
}
```

Swagger UI에서 서버 선택 가능:
```
┌─────────────────────────────────────┐
│ Servers: [http://localhost:8000  ▼]│
│          - Local Development        │
│          - Development Server       │
│          - Production Server        │
└─────────────────────────────────────┘
```

---

## 📚 체크리스트

### API 개발 시 체크리스트

- [ ] ViewSet/APIView에 `@extend_schema` 데코레이터 추가
- [ ] `summary`, `description`, `tags` 작성
- [ ] Request 파라미터 문서화 (`parameters`, `request`)
- [ ] Response 스키마 정의 (`responses`)
- [ ] 에러 응답 예시 추가 (400, 401, 403, 404 등)
- [ ] Serializer에 `help_text` 추가
- [ ] 테스트: Swagger UI에서 "Try it out" 실행
- [ ] 스키마 파일 Export 및 Git 커밋 (`schema.json`)
- [ ] 프론트엔드 팀에 변경사항 공지

---

## 📚 참고 문서

- **[08_API_명세서.md](08_API_명세서.md)** - 전체 API 명세 (수동 작성 버전)
- **[25_에러_핸들링_가이드.md](25_에러_핸들링_가이드.md)** - 에러 응답 형식
- **drf-spectacular 공식 문서**: https://drf-spectacular.readthedocs.io/
- **OpenAPI 3.0 Specification**: https://spec.openapis.org/oas/v3.0.0

---

**문서 버전**: 1.0
**작성일**: 2025-12-28
**대상 독자**: Backend 개발자, Frontend 개발자
