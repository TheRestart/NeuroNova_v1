# DICOM 뷰잉 Secure Proxy 패턴 상세 가이드

**작성일**: 2026-01-02
**버전**: v3.0
**목적**: OHIF Viewer ↔ Django ↔ Nginx ↔ Orthanc 데이터 흐름 명확화
**관련 문서**: [06_시스템_아키텍처_v3.md](06_시스템_아키텍처_v3.md)

---

## 📋 목차

1. [Overview](#1-overview)
2. [시퀀스 다이어그램](#2-시퀀스-다이어그램)
3. [구성 요소 상세](#3-구성-요소-상세)
4. [X-Accel-Redirect 동작 원리](#4-x-accel-redirect-동작-원리)
5. [보안 검증](#5-보안-검증)
6. [성능 최적화](#6-성능-최적화)
7. [트러블슈팅](#7-트러블슈팅)

---

## 1. Overview

### 1.1 목표

**Secure Proxy 패턴**을 통해 다음을 달성:
- ✅ **보안**: Orthanc PACS 외부 직접 접근 차단
- ✅ **인증**: Django JWT 검증 통과 사용자만 DICOM 접근
- ✅ **감사**: 모든 DICOM 접근 기록 (AuditLog)
- ✅ **성능**: Nginx Zero-Copy 스트리밍 (Django 메모리 부하 없음)

### 1.2 핵심 원칙

```
원칙 1: OHIF는 Orthanc에 직접 접근 불가
원칙 2: 모든 DICOM 요청은 Django Proxy 경유 필수
원칙 3: Django는 데이터 전송하지 않음 (Nginx 위임)
원칙 4: Nginx만 Orthanc 내부 접근 가능
```

---

## 2. 시퀀스 다이어그램

### 2.1 전체 흐름 (성공 시나리오)

```mermaid
sequenceDiagram
    participant User as 사용자<br/>(의사/방사선과)
    participant Browser as 브라우저
    participant OHIF as OHIF Viewer<br/>(React Component)
    participant Django as Django Proxy<br/>(/api/ris/dicom-web/)
    participant Nginx as Nginx<br/>(Reverse Proxy)
    participant Orthanc as Orthanc PACS<br/>(Internal Only)
    participant MySQL as MySQL<br/>(RIS DB)

    User->>Browser: 1. Study 선택 클릭
    Browser->>OHIF: 2. loadStudy(studyInstanceUID)

    Note over OHIF: OHIF 내부 로직
    OHIF->>OHIF: 3. DICOMweb 클라이언트 초기화<br/>(wadoRoot: /api/ris/dicom-web)

    OHIF->>Django: 4. GET /api/ris/dicom-web/studies/{studyUID}/metadata
    Note over OHIF,Django: Authorization: Bearer JWT_TOKEN<br/>Accept: application/dicom+json

    Note over Django: Django View (dicom_web_proxy)
    Django->>Django: 5. JWT 토큰 검증<br/>(DRF JWTAuthentication)

    alt JWT 유효
        Django->>MySQL: 6. Study 조회<br/>(SELECT * FROM radiology_study)
        MySQL-->>Django: 7. Study 데이터 반환
        Django->>Django: 8. 권한 확인<br/>(user.has_perm 체크)

        alt 권한 OK
            Django->>MySQL: 9. 감사 로그 기록<br/>(INSERT INTO audit_log)
            MySQL-->>Django: 10. OK

            Django->>Nginx: 11. X-Accel-Redirect 헤더 반환
            Note over Django,Nginx: X-Accel-Redirect: /internal-orthanc/dicom-web/...<br/>Content-Type: application/dicom+json<br/>(빈 Body)

            Nginx->>Nginx: 12. 헤더 인터셉트<br/>(internal 디렉티브 확인)
            Nginx->>Orthanc: 13. 내부 프록시 요청<br/>(http://orthanc:8042/dicom-web/...)

            Orthanc->>Orthanc: 14. DICOM 메타데이터 조회<br/>(SQLite DB)
            Orthanc-->>Nginx: 15. JSON 반환<br/>(DICOM 메타데이터)

            Nginx-->>OHIF: 16. JSON 스트리밍<br/>(Zero-Copy)
            OHIF->>OHIF: 17. 메타데이터 파싱<br/>(Series, Instances)

            loop 각 Instance별 이미지 요청
                OHIF->>Django: 18. GET /api/ris/dicom-web/studies/.../instances/.../frames/1
                Django->>Nginx: 19. X-Accel-Redirect
                Nginx->>Orthanc: 20. HTJ2K 이미지 조회
                Orthanc-->>Nginx: 21. HTJ2K 바이너리
                Nginx-->>OHIF: 22. HTJ2K 스트리밍
                OHIF->>OHIF: 23. WASM 디코딩<br/>(openjpeg-wasm)
            end

            OHIF->>Browser: 24. Canvas 렌더링
            Browser->>User: 25. DICOM 이미지 표시

        else 권한 없음
            Django-->>OHIF: 403 Forbidden<br/>{"error": "권한이 없습니다"}
            OHIF-->>User: 에러 메시지 표시
        end
    else JWT 무효
        Django-->>OHIF: 401 Unauthorized<br/>{"error": "인증 실패"}
        OHIF->>Browser: 로그인 페이지로 리다이렉트
    end
```

---

### 2.2 에러 시나리오 (Orthanc 다운)

```mermaid
sequenceDiagram
    participant OHIF as OHIF Viewer
    participant Django as Django Proxy
    participant Nginx as Nginx
    participant Orthanc as Orthanc PACS<br/>(DOWN)

    OHIF->>Django: 1. GET /api/ris/dicom-web/...
    Django->>Django: 2. JWT 검증 OK
    Django->>Nginx: 3. X-Accel-Redirect

    Nginx->>Orthanc: 4. 내부 프록시 요청
    Note over Orthanc: 503 Service Unavailable

    Orthanc--XNginx: 5. Connection Refused
    Nginx-->>OHIF: 6. 502 Bad Gateway

    OHIF->>OHIF: 7. 에러 처리<br/>(재시도 또는 알림)
    OHIF-->>User: 8. "PACS 서버 연결 실패" 메시지
```

---

## 3. 구성 요소 상세

### 3.1 OHIF Viewer 설정

**파일**: `NeuroNova_03_front_end_react/00_test_client/src/config/ohif.config.js`

```javascript
export default {
  routerBasename: '/',
  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'dicomweb',
      configuration: {
        friendlyName: 'NeuroNova PACS',
        name: 'Orthanc',

        // Django Proxy 경로 (v3.0)
        wadoUriRoot: 'http://localhost/api/ris/dicom-web',
        qidoRoot: 'http://localhost/api/ris/dicom-web',
        wadoRoot: 'http://localhost/api/ris/dicom-web',

        // 프로덕션 (Cloudflare)
        // wadoUriRoot: 'https://cdss.hospital.com/api/ris/dicom-web',

        // DICOMweb 설정
        qidoSupportsIncludeField: true,
        imageRendering: 'wadors',  // WADO-RS 사용
        thumbnailRendering: 'wadors',
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: true,

        // 인증 헤더 (Axios Interceptor로 자동 추가)
        // headers: { Authorization: 'Bearer JWT_TOKEN' }
      },
    },
  ],

  // HTJ2K WASM 디코더 설정
  extensions: [
    {
      id: '@ohif/extension-cornerstone',
      configuration: {
        codecs: {
          'image/x-jls': {
            codec: 'openjpeg-wasm',  // HTJ2K 디코더
          },
        },
      },
    },
  ],
};
```

---

### 3.2 Django Proxy View

**파일**: `NeuroNova_02_back_end/02_django_server/ris/views.py`

```python
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import RadiologyStudy
from audit.models import AuditLog
import re


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dicom_web_proxy(request, path):
    """
    DICOM Web Proxy with Secure X-Accel-Redirect

    Path 예시:
    - studies/{studyUID}/metadata
    - studies/{studyUID}/series/{seriesUID}/instances
    - studies/{studyUID}/series/{seriesUID}/instances/{instanceUID}/frames/1

    Security:
    1. JWT 인증 (DRF Middleware 자동 처리)
    2. 환자 접근 권한 확인
    3. 감사 로그 기록
    4. X-Accel-Redirect로 Nginx 위임

    Returns:
        HttpResponse: X-Accel-Redirect 헤더 (빈 Body)
    """
    user = request.user  # JWT로 인증된 사용자

    # 1. StudyInstanceUID 추출
    study_uid = extract_study_uid_from_path(path)
    if not study_uid:
        return Response({'error': 'Invalid path'}, status=400)

    # 2. Study 조회
    try:
        study = RadiologyStudy.objects.select_related('patient').get(
            study_instance_uid=study_uid
        )
    except RadiologyStudy.DoesNotExist:
        return Response({'error': 'Study not found'}, status=404)

    # 3. 권한 확인
    if not can_access_study(user, study):
        # 감사 로그 (실패)
        AuditLog.objects.create(
            user=user,
            action='DICOM_ACCESS_DENIED',
            resource_type='Study',
            resource_id=study_uid,
            ip_address=request.META.get('REMOTE_ADDR'),
            result='FAIL'
        )
        return Response({'error': '권한이 없습니다'}, status=403)

    # 4. 감사 로그 (성공)
    AuditLog.objects.create(
        user=user,
        action='DICOM_ACCESS',
        resource_type='Study',
        resource_id=study_uid,
        ip_address=request.META.get('REMOTE_ADDR'),
        result='SUCCESS'
    )

    # 5. X-Accel-Redirect 헤더 반환
    internal_url = f'/internal-orthanc/dicom-web/{path}'
    response = HttpResponse()
    response['X-Accel-Redirect'] = internal_url
    response['Content-Type'] = request.META.get('HTTP_ACCEPT', 'application/dicom')

    # 캐시 헤더 (선택적)
    response['Cache-Control'] = 'private, max-age=3600'

    return response


def extract_study_uid_from_path(path):
    """
    Path에서 StudyInstanceUID 추출

    예시:
    - studies/1.2.840.../metadata → 1.2.840...
    - studies/1.2.840.../series/... → 1.2.840...
    """
    match = re.match(r'studies/([\d.]+)', path)
    return match.group(1) if match else None


def can_access_study(user, study):
    """
    사용자 권한 확인

    규칙:
    - Admin: 모든 Study 접근 가능
    - Doctor/Radiologist: 본인이 처방하거나 판독한 Study
    - Patient: 본인의 Study만
    - Nurse/Lab: 접근 불가
    """
    if user.role == 'admin':
        return True

    if user.role in ['doctor', 'radiologist']:
        # 처방 의사 또는 판독 의사인지 확인
        return study.ordering_physician == user or study.radiologist == user

    if user.role == 'patient':
        # 본인 환자인지 확인
        return study.patient.user == user

    return False
```

---

### 3.3 Nginx 설정

**파일**: `NeuroNova_02_back_end/02_django_server/nginx/nginx.conf`

```nginx
http {
    # ... (기본 설정 생략)

    upstream django {
        server django:8000;
    }

    upstream orthanc {
        server orthanc:8042;
    }

    server {
        listen 80;
        server_name cdss.hospital.com localhost;

        # 1. React Unified SPA
        location / {
            root /var/www/react-unified/;
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }

        # 2. Django API
        location /api/ {
            proxy_pass http://django/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS (필요 시)
            add_header Access-Control-Allow-Origin $http_origin;
            add_header Access-Control-Allow-Credentials true;
        }

        # 3. Orthanc 내부 전용 (외부 접근 차단)
        location /internal-orthanc/ {
            internal;  # 핵심: Django X-Accel-Redirect만 허용

            # Orthanc 프록시
            rewrite ^/internal-orthanc/(.*)$ /$1 break;
            proxy_pass http://orthanc;

            # 헤더 전달
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # 버퍼링 비활성화 (스트리밍 최적화)
            proxy_request_buffering off;
            proxy_buffering off;
            proxy_http_version 1.1;
            proxy_set_header Connection "";

            # 타임아웃 (대용량 DICOM)
            proxy_connect_timeout 60s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    }
}
```

**핵심 설정 설명**:
- `internal;`: **외부 직접 접근 차단**, Django `X-Accel-Redirect` 헤더만 허용
- `rewrite ^/internal-orthanc/(.*)$ /$1 break;`: `/internal-orthanc/dicom-web/...` → `/dicom-web/...`
- `proxy_buffering off;`: 스트리밍 최적화 (Zero-Copy)

---

## 4. X-Accel-Redirect 동작 원리

### 4.1 개념

**X-Accel-Redirect**는 Nginx의 내부 리다이렉트 기능으로, 애플리케이션 서버(Django)가 파일 전송을 Nginx에 위임할 수 있습니다.

**장점**:
- ✅ **성능**: Django 메모리 부하 없음 (Nginx Zero-Copy)
- ✅ **보안**: 애플리케이션 서버가 인증/인가만 담당
- ✅ **확장성**: Nginx가 대용량 파일 스트리밍 처리

### 4.2 흐름 비교

#### 일반 Proxy (Django가 데이터 전송)

```
OHIF → Django (JWT 검증) → Orthanc (데이터 조회) → Django (메모리 버퍼) → OHIF
```

**문제점**:
- Django가 100MB DICOM을 메모리에 로드 (메모리 부족 위험)
- Python GIL로 인한 성능 저하
- 동시 요청 100개 시 Django 메모리 10GB+ 사용

#### X-Accel-Redirect (Nginx가 데이터 전송)

```
OHIF → Django (JWT 검증, 헤더만 반환) → Nginx (헤더 인터셉트) → Orthanc (데이터 조회) → Nginx (Zero-Copy) → OHIF
```

**개선 효과**:
- Django 메모리 사용 < 10MB (헤더만)
- Nginx sendfile 시스템 콜 (커널 레벨 Zero-Copy)
- 동시 요청 1000개 처리 가능

---

### 4.3 실제 HTTP 흐름

#### Step 1: OHIF → Django

```http
GET /api/ris/dicom-web/studies/1.2.840.../series/1.2.840.../instances/1.2.840.../frames/1 HTTP/1.1
Host: localhost
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: image/jls
```

#### Step 2: Django → Nginx (X-Accel-Redirect 응답)

```http
HTTP/1.1 200 OK
X-Accel-Redirect: /internal-orthanc/dicom-web/studies/1.2.840.../series/1.2.840.../instances/1.2.840.../frames/1
Content-Type: image/jls
Cache-Control: private, max-age=3600
Content-Length: 0

(빈 Body)
```

**핵심**: `Content-Length: 0` (Django는 빈 응답만 전송)

#### Step 3: Nginx → Orthanc (내부 프록시)

```http
GET /dicom-web/studies/1.2.840.../series/1.2.840.../instances/1.2.840.../frames/1 HTTP/1.1
Host: orthanc:8042
Accept: image/jls
```

**주의**: Nginx가 `/internal-orthanc/`를 `/`로 rewrite

#### Step 4: Orthanc → Nginx (HTJ2K 바이너리)

```http
HTTP/1.1 200 OK
Content-Type: image/jls
Content-Length: 5242880

(HTJ2K 바이너리 데이터 5MB)
```

#### Step 5: Nginx → OHIF (최종 응답)

```http
HTTP/1.1 200 OK
Content-Type: image/jls
Content-Length: 5242880
Cache-Control: private, max-age=3600

(HTJ2K 바이너리 데이터 5MB)
```

**핵심**: Nginx가 Orthanc 응답을 그대로 OHIF에 전송 (Zero-Copy)

---

## 5. 보안 검증

### 5.1 외부 직접 접근 차단 테스트

```bash
# 테스트 1: Orthanc 직접 접근 시도 (실패해야 정상)
curl http://localhost/internal-orthanc/dicom-web/studies
# 예상 결과: 404 Not Found (internal 디렉티브로 차단)

# 테스트 2: Django Proxy 경유 (성공)
curl -H "Authorization: Bearer VALID_JWT_TOKEN" \
     http://localhost/api/ris/dicom-web/studies/1.2.840.../metadata
# 예상 결과: 200 OK (JSON 메타데이터)

# 테스트 3: JWT 없이 접근 (실패)
curl http://localhost/api/ris/dicom-web/studies/1.2.840.../metadata
# 예상 결과: 401 Unauthorized
```

---

### 5.2 권한 검증 테스트

```python
# tests/test_dicom_proxy_permissions.py
from django.test import TestCase
from rest_framework.test import APIClient

class DICOMProxyPermissionTest(TestCase):
    def test_patient_cannot_access_other_study(self):
        """환자는 타인의 Study 접근 불가"""
        # Patient A 로그인
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + patient_a_token)

        # Patient B의 Study 접근 시도
        response = client.get(f'/api/ris/dicom-web/studies/{patient_b_study_uid}/metadata')

        # 권한 오류 확인
        self.assertEqual(response.status_code, 403)
        self.assertIn('권한이 없습니다', response.data['error'])

    def test_doctor_can_access_own_prescription(self):
        """의사는 본인이 처방한 Study 접근 가능"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + doctor_token)

        response = client.get(f'/api/ris/dicom-web/studies/{own_study_uid}/metadata')

        # 성공 확인 (X-Accel-Redirect 헤더)
        self.assertEqual(response.status_code, 200)
        self.assertIn('/internal-orthanc/', response['X-Accel-Redirect'])
```

---

## 6. 성능 최적화

### 6.1 Nginx 캐싱 (선택적)

```nginx
# nginx.conf
http {
    # DICOM 메타데이터 캐싱
    proxy_cache_path /var/cache/nginx/dicom
                     levels=1:2
                     keys_zone=dicom_cache:10m
                     max_size=1g
                     inactive=1h;

    server {
        location /internal-orthanc/dicom-web/studies/ {
            internal;
            proxy_pass http://orthanc;

            # 캐싱 활성화 (메타데이터만)
            proxy_cache dicom_cache;
            proxy_cache_valid 200 1h;
            proxy_cache_key "$request_uri";

            # 이미지는 캐싱 안 함 (용량 큼)
            proxy_cache_bypass $http_pragma;
            proxy_cache_revalidate on;
        }
    }
}
```

---

### 6.2 Connection Keep-Alive

```nginx
upstream orthanc {
    server orthanc:8042;
    keepalive 32;  # 연결 풀 유지
}

location /internal-orthanc/ {
    proxy_pass http://orthanc;
    proxy_http_version 1.1;
    proxy_set_header Connection "";  # Keep-Alive 활성화
}
```

---

## 7. 트러블슈팅

### 7.1 "404 Not Found" (외부 직접 접근 시도)

**증상**: 브라우저에서 `http://localhost/internal-orthanc/...` 직접 접근 시 404

**원인**: `internal;` 디렉티브로 외부 접근 차단

**해결**: 정상 동작입니다. Django Proxy 경유 필수.

---

### 7.2 "502 Bad Gateway" (Orthanc 연결 실패)

**증상**: OHIF에서 이미지 로딩 실패, 502 에러

**원인**:
1. Orthanc 컨테이너 다운
2. Nginx → Orthanc 네트워크 문제

**해결**:
```bash
# 1. Orthanc 상태 확인
docker ps | grep orthanc

# 2. Orthanc 재시작
docker restart orthanc

# 3. Nginx 로그 확인
docker logs nginx | grep "internal-orthanc"
```

---

### 7.3 "X-Accel-Redirect 작동 안 함"

**증상**: Django는 200 OK 반환하지만 OHIF가 빈 응답 수신

**원인**: Nginx가 X-Accel-Redirect 헤더를 인식하지 못함

**해결**:
```nginx
# nginx.conf에서 확인
location /internal-orthanc/ {
    internal;  # 이 줄이 있는지 확인
    proxy_pass http://orthanc;
}
```

**검증**:
```bash
# Django 응답 헤더 확인
curl -I -H "Authorization: Bearer TOKEN" \
     http://localhost/api/ris/dicom-web/studies/.../metadata

# X-Accel-Redirect 헤더가 있어야 함
# X-Accel-Redirect: /internal-orthanc/dicom-web/...
```

---

## 📚 참고 자료

- [Nginx X-Accel-Redirect 공식 문서](https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/)
- [DICOMweb WADO-RS 표준](https://www.dicomstandard.org/using/dicomweb)
- [OHIF Viewer 데이터 소스 설정](https://docs.ohif.org/configuration/dataSources)
- [Django HTTP Response 헤더](https://docs.djangoproject.com/en/stable/ref/request-response/#httpresponse-objects)

---

**작성**: NeuroNova Team
**검토**: Security & Architecture Team
**다음 검증**: Penetration Test (2026-01-10)
