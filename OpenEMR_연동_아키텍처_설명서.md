# OpenEMR 연동 아키텍처 설명서 (Direct DB Access)

## 1. 개요
본 문서는 NeuroNova 시스템이 OpenEMR(Electronic Medical Record)과 데이터를 연동하는 방식을 기술합니다.
기존의 **수동 SQL 실행(Manual SQL Execution)** 방식을 **Django ORM 자동 라우팅(Database Router)** 방식으로 고도화하여, 코드의 안정성과 유지보수성을 높였습니다.

### 핵심 특징
- **OAuth2 미사용**: API 계층을 거치지 않고 데이터베이스(MariaDB)에 직접 연결합니다.
- **ORM 기반**: 복잡한 SQL 쿼리 문자열 대신 Django의 객체 지향 문법(`objects.create`, `filter` 등)을 사용합니다.
- **자동 라우팅**: `OpenEMRRouter`가 OpenEMR 관련 모델에 대한 쿼리를 자동으로 식별하여 `openemr` DB 연결로 보냅니다.

---

## 2. 시스템 구성 요소

### 2.1 Database Router (`emr/router.py`)
Django의 다중 데이터베이스 기능을 활용하기 위한 라우터 클래스입니다.
- **역할**: `app_label`이 `openemr_db`인 모델의 읽기(Read)/쓰기(Write) 요청을 가로채어 `openemr` 데이터베이스 설정으로 연결합니다.
- **설정**: `settings.py`의 `DATABASE_ROUTERS` 리스트에 등록되어 작동합니다.

### 2.2 OpenEMR Models (`emr/openemr_models.py`)
OpenEMR의 레거시 데이터베이스 테이블과 1:1로 매핑되는 Django 모델입니다.
- **Managed = False**: Django가 이 테이블들을 생성하거나 변경(Migration)하지 않도록 설정했습니다. (기존 스키마 유지)
- **주요 모델**:
    - `PatientData`: 환자 정보 (`patient_data` 테이블)
    - `Encounter`: 진료 기록 (`encounters` 테이블)
    - `Form`: 진료 폼 메타데이터 (`forms` 테이블)
    - `Prescription`: 처방 내역 (`prescriptions` 테이블)

### 2.3 Repositories (`emr/repositories.py`)
비즈니스 로직과 데이터 접근 계층을 분리하는 저장소 패턴 구현체입니다.
- **기존**: `cursor.execute("INSERT INTO ...")` 형태의 Raw SQL 사용.
- **변경 후**: 
  ```python
  # 예시: 환자 생성
  OpenEMRPatientData.objects.create(
      pid=new_pid,
      fname=data['given_name'],
      lname=data['family_name'],
      ...
  )
  ```
- **장점**: SQL Injection 방지, 타입 안정성 확보, 가독성 향상.

---

## 3. 데이터 흐름 (Data Flow)

### 환자 등록 (Patient Creation)
1. **Frontend/API**: 환자 등록 요청 (`POST /api/emr/patients/`)
2. **Service Layer**: `PatientService`가 비즈니스 로직 수행
3. **Repository**: `OpenEMRPatientRepository.create_patient_in_openemr()` 호출
4. **ORM & Router**: 
    - `OpenEMRPatientData` 모델 감지
    - `OpenEMRRouter`가 `openemr` DB 커넥션 선택
5. **Database**: OpenEMR MariaDB의 `patient_data` 테이블에 `INSERT` 수행

### 처방 전송 (Order Creation)
1. **Frontend/API**: 처방 생성 요청 (`POST /api/emr/orders/`)
2. **Service Layer**: `OrderService`가 처방 생성 로직 수행
3. **Repository**: 
    - 로컬 DB에 저장 (`OrderRepository`)
    - OpenEMR DB에 처방 전송 (`OpenEMROrderRepository`)
4. **ORM & Router**: `OpenEMRPrescription` 모델을 통해 `openemr` DB의 `prescriptions` 테이블에 저장

---

## 4. 설정 및 환경 변수
`.env` 파일 또는 환경 변수에서 다음 접속 정보가 정확해야 합니다.

```env
# OpenEMR Database Connection
OPENEMR_DB_NAME=openemr
OPENEMR_DB_USER=openemr
OPENEMR_DB_PASSWORD=xxxxxx
OPENEMR_DB_HOST=localhost
OPENEMR_DB_PORT=3306 (또는 외부 포트)
```
