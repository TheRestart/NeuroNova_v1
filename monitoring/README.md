# NeuroNova CDSS Monitoring Stack

## 개요

Prometheus + Grafana + Alertmanager를 사용한 시스템 모니터링 및 알림

## 접속 정보

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`

- **Prometheus**: http://localhost:9090
  - 메트릭 수집 및 쿼리

- **Alertmanager**: http://localhost:9093
  - 알림 관리

## 주요 기능

### 1. 시계열 데이터 수집 (Prometheus)
- Django 응답 시간, RPS, 에러율
- Redis 메모리 사용량, 히트율
- MySQL 커넥션 수, 쿼리 성능
- Celery 큐 길이, 작업 성공/실패율
- 시스템 리소스 (CPU, Memory, Disk, Network)

### 2. 대시보드 시각화 (Grafana)
- **시스템 상태 대시보드**: RPS, 에러율, 응답 시간
- **리소스 모니터링**: CPU, Memory, Disk 사용량
- **AI 작업 모니터링**: GPU 사용량 (확장 가능)
- **데이터베이스 모니터링**: 커넥션, 슬로우 쿼리

### 3. 알림 시스템 (Alertmanager)
- **CODE BLUE**: 시스템 다운, DB 연결 끊김 등 치명적 장애
- **CRITICAL**: 높은 에러율, 응답 지연
- **WARNING**: 리소스 부족, 큐 백업

## 알림 채널 설정

`monitoring/alertmanager/alertmanager.yml` 파일에서 설정:

```yaml
# Email 알림
email_configs:
  - to: 'oncall@neuronova.com'

# Slack 알림
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'
    channel: '#alerts'

# SMS 알림 (Webhook)
webhook_configs:
  - url: 'http://sms-gateway:8080/send'
```

## Django Metrics 활성화

1. django-prometheus 설치:
```bash
pip install django-prometheus
```

2. settings.py 설정:
```python
INSTALLED_APPS = [
    'django_prometheus',
    ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

3. urls.py 설정:
```python
from django.urls import path, include

urlpatterns = [
    path('metrics/', include('django_prometheus.urls')),
    ...
]
```

## 커스텀 대시보드 추가

`monitoring/grafana/dashboards/` 디렉토리에 JSON 파일 추가

## 트러블슈팅

### Prometheus가 타겟을 찾지 못함
- 서비스 이름 확인 (`docker-compose.dev.yml`의 service 이름과 일치해야 함)
- 네트워크 연결 확인

### Grafana에서 데이터가 보이지 않음
- Prometheus 데이터 소스 연결 확인
- 메트릭이 실제로 수집되는지 Prometheus UI에서 확인 (http://localhost:9090)

### 알림이 전송되지 않음
- Alertmanager 로그 확인: `docker logs neuronova-alertmanager-dev`
- SMTP 설정 확인 (Gmail의 경우 앱 비밀번호 사용)
