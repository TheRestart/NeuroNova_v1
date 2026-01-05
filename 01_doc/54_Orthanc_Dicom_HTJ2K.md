# Orthanc DICOM HTJ2K 지원 및 변환 가이드

## 1. 개요
본 문서는 NeuroNova 시스템에서 **HTJ2K (High-Throughput JPEG 2000)** 형식의 DICOM 파일을 지원하고, 기존 및 신규 DICOM 데이터를 효율적으로 변환/저장하기 위한 아키텍처와 사용법을 설명합니다.

> [!NOTE]
> **Windows 환경 제약에 따른 Fallback**: 현재 Windows Server 환경에서는 ImageCodecs의 HTJ2K(Part 15) 코덱을 완벽하게 지원하지 않는 경우가 있습니다. 이 경우 시스템은 자동으로 **JPEG 2000 Lossless (Part 1, Transfer Syntax 1.2.840.10008.1.2.4.90)** 방식으로 안전하게 Fallback하여 저장합니다. 이는 HTJ2K와 유사한 압축 효율을 제공하며, 대부분의 PACS/Viewer와 호환됩니다.

## 2. 아키텍처
Orthanc 자체는 DICOM 파일을 있는 그대로 저장합니다. 따라서 HTJ2K 저장을 위해서는 **Orthanc 저장 전** 또는 **저장 후**에 변환 프로세스가 필요합니다.

### 데이터 흐름
1. **업로드 (Upload)**:
   - 사용자가 `POST /api/ris/upload/dicom/` 엔드포인트로 DICOM 파일 전송
   - **Django Backend**에서 메모리 상에서 HTJ2K/J2K로 변환 (`dicom_converter.py`)
   - 변환된 데이터를 Orthanc에 저장
2. **일괄 변환 (Batch Conversion)**:
   - 관리자가 `manage.py` 커맨드 실행
   - Orthanc에서 원본 다운로드 -> 변환 -> 신규 인스턴스 업로드 -> 원본 삭제

## 3. 기능 및 사용법

### 3.1. 자동 변환 업로드 API
신규 DICOM 파일을 업로드할 때 자동으로 압축하여 저장합니다.

*   **Endpoint**: `POST /api/ris/upload/dicom/`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data`
*   **Body**: `file` (Binary DICOM file)

**Python 예시**:
```python
import requests

url = "http://localhost:8000/api/ris/upload/dicom/"
files = {'file': open('study.dcm', 'rb')}
# 인증 헤더 필요 시 추가
response = requests.post(url, files=files)

if response.status_code == 201:
    print("성공:", response.json())
else:
    print("실패:", response.text)
```

### 3.2. 기존 데이터 일괄 변환 명령어
이미 Orthanc에 저장된 공부(Study)들을 압축 포맷으로 변환합니다.

**명령어 위치**: `NeuroNova_02_back_end/02_django_server`

```bash
# 특정 Study만 변환
python manage.py convert_to_htj2k --study <StudyInstanceUID>

# 전체 Study 변환
python manage.py convert_to_htj2k --all

# 시뮬레이션 (Dry Run) - 실제 변환 없이 로그만 출력
python manage.py convert_to_htj2k --all --dry-run
```

## 4. 기술 명세 (Technical Specs)

### 4.1. 변환 로직 (`ris/utils/dicom_converter.py`)
*   **라이브러리**: `pydicom`, `imagecodecs` (또는 `openjphpy`)
*   **프로세스**:
    1. DICOM 로드 및 Pixel Data 추출
    2. `imagecodecs`를 통해 인코딩 시도 (`jph` -> `jpeg2k` 순서로 시도)
    3. `TransferSyntaxUID` 업데이트
        *   HTJ2K Lossless: `1.2.840.10008.1.2.4.201`
        *   JPEG 2000 Lossless (Fallback): `1.2.840.10008.1.2.4.90`
    4. DICOM Encapsulation 및 메타데이터 업데이트 (`PixelData` 교체)

### 4.2. 의존성 (Dependencies)
*   `imagecodecs`: 핵심 코덱 라이브러리
*   `pydicom`: DICOM 파싱 및 조작
*   `pylibjpeg-openjpeg` (Optional): 디코딩 지원

## 5. 트러블슈팅

### 5.1. "UID mismatch" 경고
로그에 `Warning: Fallback to JPEG 2000 Lossless`가 뜨는 경우:
*   **원인**: 서버 환경에 HTJ2K 전용 인코더(`openjph`)가 없거나 호환되지 않음.
*   **해결**: JPEG 2000 Lossless로 자동 저장되므로 기능상 문제는 없습니다. 리눅스 환경으로 배포 시 `imagecodecs`의 전체 빌드를 사용하면 해결될 수 있습니다.

### 5.2. Orthanc 업로드 실패
*   Orthanc 서버(`http://localhost:8042`)가 켜져 있는지 확인하십시오.
*   Django 로그에서 `OrthancClient` 연결 오류를 확인하십시오.
