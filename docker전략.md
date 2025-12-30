
### 1. 기존 Docker 정리 (Clean Up)

먼저 현재 실행 중인 컨테이너를 중지하고 삭제합니다. 데이터 볼륨(DB 데이터 등)은 남겨두고 컨테이너만 지우는 것이 안전합니다.

```bash
# 실행 중인 모든 컨테이너 중지 및 삭제
docker compose down

# (선택사항) 만약 기존 네트워크나 캐시까지 싹 지우고 싶다면 아래 명령어 사용
# docker system prune -f

```

---

### 2. `docker-compose.yml` 수정 (Infrastructure Only)

Django 개발에 필수적인 **MySQL, Redis, Orthanc**만 남긴 구성입니다.

* **Django & Celery:** 제외 (로컬에서 `python manage.py ...`로 실행)
* **Nginx & OHIF:** 일단 제외 (Django API 개발에 집중하기 위함. 필요시 Orthanc는 8042포트로 직접 접속 가능)

아래 내용을 프로젝트 루트의 `docker-compose.yml`에 덮어쓰세요.

```yaml
version: '3.8'

services:
  # 1. Database (MySQL)
  db:
    image: mysql:8.0
    container_name: neuronova_db
    restart: always
    environment:
      MYSQL_DATABASE: neuronova_db
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3306:3306"  # 로컬 Django가 접속할 수 있게 포트 개방
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin" ,"ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  # 2. Cache & Broker (Redis)
  redis:
    image: redis:alpine
    container_name: neuronova_redis
    restart: always
    ports:
      - "6379:6379"  # 로컬 Celery/Django가 접속할 수 있게 포트 개방
    volumes:
      - redis_data:/data

  # 3. PACS Server (Orthanc) - HTJ2K/DICOM Storage
  orthanc:
    image: jodogne/orthanc-plugins
    container_name: neuronova_orthanc
    restart: always
    ports:
      - "8042:8042"  # HTTP Port (웹 UI 및 REST API)
      - "4242:4242"  # DICOM Port
    environment:
      ORTHANC_NAME: "NeuroNova_PACS"
      # 필요시 orthanc.json 설정 파일을 마운트하여 사용
      # ORTHANC__REGISTERED_USERS: '{"user": "password"}' 
    volumes:
      - orthanc_storage:/var/lib/orthanc/db

volumes:
  db_data:
  redis_data:
  orthanc_storage:

```

---

### 3. Docker 실행

필요한 인프라 서버들만 백그라운드로 실행합니다.

```bash
docker compose up -d

```

---

### 4. 로컬 Django 설정 변경 (`settings.py`)

이제 Django는 Docker 내부 네트워크(`db`, `redis` 등)가 아닌 **Localhost**를 통해 Docker 컨테이너에 접속해야 합니다. `settings.py`를 다음과 같이 확인하고 수정해주세요.

**1) Database 설정**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'neuronova_db',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',  # 중요: 'db'가 아니라 '127.0.0.1' 또는 'localhost'
        'PORT': '3306',
    }
}

```

**2) Redis/Celery 설정**

```python
# Docker 내부가 아니므로 localhost로 변경
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

```

**3) Orthanc 연결 설정 (코드 내 사용하는 부분이 있다면)**

```python
# 예시 상수
ORTHANC_API_URL = "http://127.0.0.1:8042"

```

---

### 5. 개발 진행 방법 (요약)

이제 환경이 분리되었습니다.

1. **터미널 1 (인프라):** `docker compose up -d` (MySQL, Redis, Orthanc 실행)
2. **터미널 2 (Django):** `python manage.py runserver` (API 서버 개발)
3. **터미널 3 (Celery):** `celery -A config worker -l info` (비동기 작업/이미지 변환 테스트)
