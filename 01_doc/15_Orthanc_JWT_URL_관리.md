# Orthanc JWT URL 관리 가이드

**작성일**: 2025-12-29
**목적**: Orthanc에서 생성된 DICOM 이미지 URL의 JWT 암호화 및 생명주기 관리

---

## 1. 개요

### 1.1 배경

NeuroNova CDSS 시스템에서 Orthanc PACS에 저장된 DICOM 이미지에 접근하기 위해서는 보안이 강화된 URL이 필요합니다. Django가 Orthanc에 요청하면, Orthanc는 **JWT로 암호화된 임시 URL**을 생성하여 반환합니다.

### 1.2 주요 특징

| 항목 | 설명 |
|------|------|
| **암호화 방식** | JWT (JSON Web Token) |
| **생명주기** | 1시간 (보안 강화) |
| **용도** | DICOM 이미지 접근, OHIF Viewer 통합 |
| **생성 주체** | Orthanc PACS |
| **관리 주체** | Django (NeuroNova CDSS) |

---

## 2. JWT URL 구조

### 2.1 URL 형식

```
https://neuronova.com/dicom-web/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}?token={jwt_token}
```

**예시**:
```
http://localhost:8042/dicom-web/studies/1.2.840.113619.2.1.1.1/series/1.2.840.113619.2.1.2.1/instances/1.2.840.113619.2.1.3.1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.2 JWT 토큰 구조

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "study_uid": "1.2.840.113619.2.1.1.1",
    "series_uid": "1.2.840.113619.2.1.2.1",
    "instance_uid": "1.2.840.113619.2.1.3.1",
    "iat": 1703865600,
    "exp": 1703869200
  },
  "signature": "..."
}
```

**Payload 필드**:
- `study_uid`: DICOM Study Instance UID
- `series_uid`: DICOM Series Instance UID
- `instance_uid`: DICOM Instance UID
- `iat` (Issued At): 토큰 발급 시각 (Unix timestamp)
- `exp` (Expiration): 토큰 만료 시각 (Unix timestamp, iat + 1시간)

---

## 3. 생명주기 관리

### 3.1 URL 생성 프로세스

```
┌─────────────┐
│ OHIF Viewer │
└──────┬──────┘
       │ 1. Study 조회 요청
       ↓
┌─────────────┐
│ Django      │
│ (RIS)       │
└──────┬──────┘
       │ 2. Orthanc API 호출
       │    GET /studies/{study_uid}
       ↓
┌─────────────┐
│ Orthanc     │
│ PACS        │
└──────┬──────┘
       │ 3. JWT URL 생성 (1시간 만료)
       │    {
       │      "url": "...",
       │      "token": "eyJ...",
       │      "expires_at": "2025-12-29T13:00:00Z"
       │    }
       ↓
┌─────────────┐
│ Django      │
│ (Cache)     │
└──────┬──────┘
       │ 4. Redis에 캐싱 (50분)
       │    key: "orthanc_url:{study_uid}"
       │    ttl: 3000초 (50분)
       ↓
┌─────────────┐
│ OHIF Viewer │
│ (Display)   │
└─────────────┘
```

### 3.2 캐시 전략 (보안 강화)

**왜 50분인가?**
- JWT 만료: 1시간 (60분)
- 캐시 만료: 50분 (10분 안전 마진)
- 이유:
  - URL 유출 시 피해 최소화 (1시간 이내 만료)
  - 캐시된 URL이 만료되기 전에 새로 발급받아 사용자 경험 저하 방지
  - 진료/판독에 충분한 시간 제공

**Redis 캐시 키 구조**:
```python
# Study URL 캐시
key: f"orthanc_url:study:{study_instance_uid}"
value: {
    "url": "http://orthanc:8042/dicom-web/studies/...",
    "token": "eyJ...",
    "expires_at": "2025-12-29T13:00:00Z"
}
ttl: 3000  # 50분

# Instance URL 캐시
key: f"orthanc_url:instance:{instance_uid}"
value: {
    "url": "http://orthanc:8042/dicom-web/studies/.../instances/...",
    "token": "eyJ...",
    "expires_at": "2025-12-29T13:00:00Z"
}
ttl: 3000  # 50분
```

---

## 4. Django 구현

### 4.1 Orthanc Client (JWT URL 생성)

```python
# ris/clients/orthanc_client.py
import requests
import jwt
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings

class OrthancClient:
    def __init__(self):
        self.base_url = settings.ORTHANC_API_URL
        self.username = settings.ORTHANC_USERNAME
        self.password = settings.ORTHANC_PASSWORD

    def get_study_url_with_jwt(self, study_instance_uid):
        """
        Study에 대한 JWT 암호화 URL 가져오기 (1시간 유효)

        보안 강화:
        - JWT 생명주기: 1시간 (URL 유출 시 피해 최소화)
        - Redis 캐시 TTL: 50분 (10분 안전 마진)

        Args:
            study_instance_uid: DICOM Study Instance UID

        Returns:
            {
                "url": "http://...",
                "token": "eyJ...",
                "expires_at": "2025-12-29T13:00:00Z"
            }
        """
        # Redis 캐시 확인 (50분 TTL)
        cache_key = f"orthanc_url:study:{study_instance_uid}"
        cached_url = cache.get(cache_key)

        if cached_url:
            # 캐시된 URL의 만료 시간 확인
            expires_at = datetime.fromisoformat(cached_url['expires_at'])
            if datetime.now() < expires_at - timedelta(minutes=10):  # 10분 여유
                return cached_url

        # Orthanc에 JWT URL 요청
        response = requests.get(
            f"{self.base_url}/studies/{study_instance_uid}",
            auth=(self.username, self.password),
            params={"jwt": "true"}  # JWT 생성 요청
        )
        response.raise_for_status()

        data = response.json()

        # JWT URL 정보 추출
        jwt_url_data = {
            "url": data.get("url"),
            "token": data.get("token"),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }

        # Redis에 캐싱 (50분 = 3000초)
        cache.set(cache_key, jwt_url_data, timeout=3000)

        return jwt_url_data
```

### 4.2 RadiologyStudy 모델 확장

```python
# ris/models.py
from django.db import models
from django.core.cache import cache
from datetime import datetime, timedelta

class RadiologyStudy(models.Model):
    # ... 기존 필드들 ...

    @property
    def dicom_web_url(self):
        """
        DICOM-Web URL (JWT 토큰 포함, 1시간 유효)

        캐시된 URL이 있으면 반환, 없으면 Orthanc에서 새로 생성
        """
        from .clients.orthanc_client import OrthancClient

        client = OrthancClient()
        jwt_url_data = client.get_study_url_with_jwt(self.study_instance_uid)

        return f"{jwt_url_data['url']}?token={jwt_url_data['token']}"

    @property
    def jwt_token_expires_at(self):
        """JWT 토큰 만료 시각"""
        cache_key = f"orthanc_url:study:{self.study_instance_uid}"
        cached_url = cache.get(cache_key)

        if cached_url:
            return datetime.fromisoformat(cached_url['expires_at'])

        return None
```

### 4.3 API Response에 URL 포함

```python
# ris/serializers.py
from rest_framework import serializers
from .models import RadiologyStudy

class RadiologyStudySerializer(serializers.ModelSerializer):
    dicom_web_url = serializers.ReadOnlyField()
    jwt_token_expires_at = serializers.ReadOnlyField()

    class Meta:
        model = RadiologyStudy
        fields = [
            'study_id', 'study_instance_uid', 'patient_id',
            'dicom_web_url', 'jwt_token_expires_at',  # JWT URL 추가
            # ... 기타 필드들
        ]
```

**API 응답 예시**:
```json
{
  "study_id": 1,
  "study_instance_uid": "1.2.840.113619.2.1.1.1",
  "patient_id": "P001",
  "dicom_web_url": "http://localhost:8042/dicom-web/studies/1.2.840.113619.2.1.1.1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "jwt_token_expires_at": "2025-12-29T13:00:00Z",
  "modality": "CT",
  "study_description": "Brain CT"
}
```

---

## 5. OHIF Viewer 통합

### 5.1 URL 전달

OHIF Viewer는 Django API로부터 JWT 암호화된 URL을 받아 DICOM 이미지를 로드합니다:

```javascript
// OHIF Viewer Configuration
const config = {
  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'neuronova',
      configuration: {
        name: 'NeuroNova PACS',
        wadoUriRoot: 'http://localhost:8000/api/ris/dicom-web',
        qidoRoot: 'http://localhost:8000/api/ris/dicom-web',
        wadoRoot: 'http://localhost:8000/api/ris/dicom-web',
        qidoSupportsIncludeField: false,
        imageRendering: 'wadouri',
        thumbnailRendering: 'wadouri',
        requestOptions: {
          auth: 'include-credentials-and-token'  // JWT 토큰 포함
        }
      }
    }
  ]
};
```

### 5.2 토큰 갱신 전략

**자동 갱신 (Proactive Refresh)**:
```javascript
// OHIF에서 토큰 만료 10분 전에 자동 갱신
const checkTokenExpiry = (expiresAt) => {
  const now = new Date();
  const expires = new Date(expiresAt);
  const minutesUntilExpiry = (expires - now) / (1000 * 60);

  if (minutesUntilExpiry < 10) {
    // 토큰 만료 10분 전 → 새로 요청
    fetchNewStudyUrl(studyInstanceUID);
  }
};
```

**오류 시 재시도 (Reactive Refresh)**:
```javascript
// 401/403 에러 발생 시 URL 재요청
const handleImageLoadError = async (error) => {
  if (error.status === 401 || error.status === 403) {
    console.warn('JWT token expired, fetching new URL...');
    const newUrl = await fetchNewStudyUrl(studyInstanceUID);
    retryImageLoad(newUrl);
  }
};
```

---

## 6. 보안 고려사항

### 6.1 JWT 토큰 보안

1. **HTTPS 필수**: 프로덕션 환경에서는 HTTPS 사용 필수
   - JWT 토큰이 평문으로 전송되므로 암호화 필요

2. **토큰 재사용 방지**: 토큰은 URL 파라미터로 전달되므로 로그에 남지 않도록 주의

3. **IP 화이트리스트**: Orthanc 접근을 특정 IP로 제한

### 6.2 캐시 보안

1. **Redis 암호화**: Redis 데이터 암호화 권장
2. **캐시 키 분리**: 사용자별/역할별로 캐시 키 분리
3. **접근 제어**: Django 미들웨어로 URL 접근 권한 확인

---

## 7. 모니터링 및 로깅

### 7.1 JWT URL 생성 로그

```python
# ris/clients/orthanc_client.py
import logging

logger = logging.getLogger(__name__)

def get_study_url_with_jwt(self, study_instance_uid):
    logger.info(f"Generating JWT URL for study: {study_instance_uid}")

    # ... URL 생성 로직 ...

    logger.info(f"JWT URL generated, expires at: {jwt_url_data['expires_at']}")
    return jwt_url_data
```

### 7.2 토큰 만료 알림

```python
# ris/tasks.py (Celery Beat)
from celery import shared_task
from django.core.cache import cache
from datetime import datetime, timedelta

@shared_task
def check_expiring_jwt_urls():
    """만료 임박 JWT URL 체크 (10분 전)"""
    # Redis에서 모든 orthanc_url 키 조회
    keys = cache.keys("orthanc_url:*")

    expiring_soon = []
    for key in keys:
        url_data = cache.get(key)
        if url_data:
            expires_at = datetime.fromisoformat(url_data['expires_at'])
            if expires_at - datetime.now() < timedelta(minutes=10):
                expiring_soon.append(key)

    if expiring_soon:
        logger.warning(f"{len(expiring_soon)} JWT URLs expiring soon")

    return len(expiring_soon)
```

---

## 8. 트러블슈팅

### 8.1 JWT 토큰 만료 에러

**증상**: OHIF Viewer에서 이미지 로드 실패, 401 Unauthorized

**원인**: JWT 토큰이 1시간 경과하여 만료됨

**해결**:
```python
# 1. 캐시 확인
from django.core.cache import cache

cache_key = f"orthanc_url:study:{study_uid}"
cached_url = cache.get(cache_key)
print(cached_url)  # None이면 만료됨

# 2. 캐시 삭제 후 재생성
cache.delete(cache_key)

# 3. 새 URL 요청
from ris.clients.orthanc_client import OrthancClient
client = OrthancClient()
new_url = client.get_study_url_with_jwt(study_uid)
```

### 8.2 캐시 불일치

**증상**: Redis에 캐시된 URL과 실제 Orthanc URL이 다름

**원인**: Orthanc 재시작 또는 설정 변경

**해결**:
```bash
# Redis 캐시 전체 초기화
docker exec -it neuronova_redis redis-cli FLUSHDB

# 또는 특정 패턴만 삭제
docker exec -it neuronova_redis redis-cli --scan --pattern "orthanc_url:*" | xargs redis-cli DEL
```

---

## 9. 성능 최적화

### 9.1 캐시 적중률 향상

| 지표 | 목표 |
|------|------|
| 캐시 적중률 | > 85% |
| 평균 응답 시간 | < 100ms (캐시 히트), < 500ms (캐시 미스) |
| JWT URL 생성 빈도 | 1시간당 1회 (Study당) |

### 9.2 프리로딩 (선택적)

```python
# ris/tasks.py
@shared_task
def preload_recent_study_urls():
    """최근 7일간 조회된 Study의 JWT URL 미리 로드"""
    from .models import RadiologyStudy
    from datetime import datetime, timedelta

    recent_studies = RadiologyStudy.objects.filter(
        synced_at__gte=datetime.now() - timedelta(days=7)
    ).values_list('study_instance_uid', flat=True)

    for study_uid in recent_studies:
        client = OrthancClient()
        client.get_study_url_with_jwt(study_uid)  # 캐시에 저장
```

---

## 10. 요약

### 10.1 핵심 포인트

✅ **JWT 암호화**: Orthanc에서 생성된 URL은 JWT로 암호화되어 보안 강화
✅ **1시간 생명주기**: JWT 토큰은 1시간 후 자동 만료 (보안 강화)
✅ **50분 캐싱**: Redis에 50분 캐싱하여 10분 안전 마진 확보
✅ **자동 갱신**: 만료 10분 전 또는 에러 시 자동으로 새 URL 생성

### 10.2 Best Practices

1. **항상 캐시 먼저 확인**: Orthanc API 호출 최소화
2. **만료 시간 모니터링**: Celery Beat로 주기적 체크
3. **HTTPS 사용**: 프로덕션 환경에서 필수
4. **로그 기록**: JWT URL 생성/만료 이벤트 추적

---

## 11. 참고 자료

- [JWT 공식 문서](https://jwt.io/)
- [Orthanc Book](https://book.orthanc-server.com/)
- [Django Cache Framework](https://docs.djangoproject.com/en/5.0/topics/cache/)
- [Redis TTL 관리](https://redis.io/commands/ttl/)
