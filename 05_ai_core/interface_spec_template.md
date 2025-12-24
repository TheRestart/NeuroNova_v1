# Interface Specification: [모델명]

**문서 작성일**: YYYY-MM-DD
**작성자**: AI 개발자 이름
**모델 버전**: v1.0
**대상**: Backend Serving 팀, Integration 팀

---

## 📋 목차

1. [개요](#개요)
2. [Input Data Specification](#input-data-specification)
3. [Output Data Specification](#output-data-specification)
4. [Dependency List](#dependency-list)
5. [Function Signature](#function-signature)
6. [Error Handling](#error-handling)
7. [Performance Metrics](#performance-metrics)
8. [Usage Examples](#usage-examples)

---

## 개요

### 모델 설명
- **목적**: [모델이 수행하는 작업 설명]
- **입력**: [입력 데이터 요약]
- **출력**: [출력 데이터 요약]

### 주요 특징
- 특징 1
- 특징 2
- 특징 3

---

## Input Data Specification

### 데이터 타입
- **Primary Type**: NumPy Array / PyTorch Tensor / JSON
- **Data Format**: [구체적인 형식]

### 텐서 형태 (Shape)

```python
Input Shape: (batch_size, channels, height, width, depth)
```

**상세:**
- `batch_size`: 배치 크기 (기본값: 1)
- `channels`: 채널 수 (예: 1 for Grayscale, 3 for RGB)
- `height`: 높이 (픽셀)
- `width`: 너비 (픽셀)
- `depth`: 깊이 (3D 이미지의 경우)

### 데이터 타입 및 범위

```python
dtype: np.float32
value_range: [0.0, 1.0]  # 정규화된 값
```

### 전처리 필수 조건

다음 전처리가 완료된 데이터를 입력으로 받습니다:

1. **DICOM → NumPy 변환**
   - DICOM 파일을 NumPy Array로 변환
   - Pixel Spacing 메타데이터 추출

2. **Resampling**
   - Target Spacing: 1mm x 1mm x 1mm
   - Interpolation: Linear

3. **Normalization**
   - HU Window: [-1000, 3000]
   - Normalization: (value - min) / (max - min)

4. **Resize/Crop**
   - Target Size: 256 x 256 x 128
   - Method: Center Crop 또는 Zero Padding

### 예시 코드

```python
import numpy as np
from pathlib import Path

# DICOM 파일 경로
dicom_dir = Path("/path/to/dicom/series")

# 전처리 (사용자가 직접 구현)
from your_module.preprocessing import preprocess_mri

input_tensor = preprocess_mri(dicom_dir)

# 결과 확인
print(f"Shape: {input_tensor.shape}")  # (1, 1, 256, 256, 128)
print(f"Dtype: {input_tensor.dtype}")  # float32
print(f"Range: [{input_tensor.min():.2f}, {input_tensor.max():.2f}]")  # [0.0, 1.0]
```

---

## Output Data Specification

### 데이터 타입
- **Primary Type**: Python Dictionary (JSON-serializable)

### 출력 구조

```json
{
    "prediction": {
        "class": "string",
        "confidence": 0.0-1.0,
        "probabilities": {
            "class_1": 0.0-1.0,
            "class_2": 0.0-1.0,
            "class_3": 0.0-1.0
        },
        "bounding_box": {  // 선택적 (세그멘테이션/검출 모델)
            "x_min": 0,
            "y_min": 0,
            "x_max": 256,
            "y_max": 256
        }
    },
    "metadata": {
        "model_name": "string",
        "model_version": "string",
        "inference_time_ms": 0,
        "timestamp": "ISO 8601 format",
        "device": "cuda:0 or cpu"
    },
    "artifacts": {  // 선택적 (추가 산출물)
        "heatmap_url": "string (S3 URL)",
        "segmentation_mask_url": "string (S3 URL)"
    }
}
```

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `prediction.class` | string | Y | 예측된 클래스 이름 |
| `prediction.confidence` | float | Y | 예측 신뢰도 (0.0 ~ 1.0) |
| `prediction.probabilities` | dict | Y | 각 클래스별 확률 |
| `metadata.model_name` | string | Y | 모델 이름 |
| `metadata.model_version` | string | Y | 모델 버전 (v1.0 등) |
| `metadata.inference_time_ms` | int | Y | 추론 소요 시간 (밀리초) |
| `metadata.timestamp` | string | Y | ISO 8601 형식 타임스탬프 |

### 예시 출력

```json
{
    "prediction": {
        "class": "glioblastoma",
        "confidence": 0.92,
        "probabilities": {
            "glioblastoma": 0.92,
            "meningioma": 0.05,
            "pituitary_adenoma": 0.03
        }
    },
    "metadata": {
        "model_name": "TumorClassifier",
        "model_version": "v1.0",
        "inference_time_ms": 234,
        "timestamp": "2025-12-24T10:30:00Z",
        "device": "cuda:0"
    }
}
```

---

## Dependency List

### Python 버전
- **Required**: Python 3.10+
- **Recommended**: Python 3.11

### 프레임워크

```txt
# Deep Learning
torch==2.0.1
torchvision==0.15.2

# Medical Imaging
pydicom==2.3.1
SimpleITK==2.2.1
nibabel==5.1.0

# Data Processing
numpy==1.24.3
```

### CUDA (GPU 사용 시)
- **CUDA**: 11.8+
- **cuDNN**: 8.6+
- **GPU Memory**: 최소 4GB (권장 8GB)

### 설치 방법

```bash
# CPU 버전
pip install -r requirements.txt

# GPU 버전 (CUDA 11.8)
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 \
    --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

---

## Function Signature

### 주요 함수

```python
def predict(
    input_data: Union[np.ndarray, Path, str],
    model_path: Union[str, Path] = "./models/model_v1.pth",
    device: str = "cuda",
    return_artifacts: bool = False
) -> Dict[str, Any]:
    """
    [모델명] 추론 함수

    Args:
        input_data: 입력 데이터
            - np.ndarray: 전처리된 텐서 (1, 1, H, W, D)
            - Path/str: DICOM 시리즈 디렉토리 경로
        model_path: 학습된 모델 파일 경로 (.pth)
        device: 추론 디바이스 ('cuda' 또는 'cpu')
        return_artifacts: 추가 산출물 반환 여부 (heatmap, mask 등)

    Returns:
        result: 예측 결과 딕셔너리 (Output Spec 참조)

    Raises:
        ValueError: input_data 형태가 잘못된 경우
        FileNotFoundError: model_path가 존재하지 않는 경우
        RuntimeError: GPU 메모리 부족 등 추론 실패
        ModelLoadError: 모델 로드 실패

    Example:
        >>> from your_module import predict
        >>> result = predict("/path/to/dicom", device="cuda")
        >>> print(result["prediction"]["class"])
        "glioblastoma"
    """
    pass
```

### 클래스 기반 API (선택)

```python
from your_module import InferenceEngine

# 엔진 초기화
engine = InferenceEngine(
    model_path="./models/model_v1.pth",
    device="cuda"
)

# 추론 실행
result = engine.predict("/path/to/dicom")
```

---

## Error Handling

### Exception 종류

| Exception | 설명 | 해결 방법 |
|-----------|------|----------|
| `ValueError` | 입력 데이터 형태 오류 | input_data 형태 확인 (Shape, dtype) |
| `FileNotFoundError` | 모델 파일 없음 | model_path 경로 확인 |
| `RuntimeError` | GPU 메모리 부족 | batch_size 줄이기 또는 CPU 사용 |
| `ModelLoadError` | 모델 로드 실패 | 모델 파일 호환성 확인 |

### 에러 메시지 예시

```python
# ValueError
ValueError: Expected input shape (1, 1, 256, 256, 128), got (1, 3, 256, 256, 128)

# FileNotFoundError
FileNotFoundError: Model file not found at ./models/model_v1.pth

# RuntimeError
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 8.00 GiB total capacity)
```

### 예외 처리 예시

```python
try:
    result = predict(dicom_dir, device="cuda")
except ValueError as e:
    print(f"입력 데이터 오류: {e}")
except FileNotFoundError as e:
    print(f"모델 파일 없음: {e}")
except RuntimeError as e:
    print(f"추론 실패 (GPU 메모리 부족 가능성): {e}")
    # CPU로 재시도
    result = predict(dicom_dir, device="cpu")
```

---

## Performance Metrics

### 추론 속도

| 환경 | 평균 시간 | 표준편차 |
|------|----------|----------|
| GPU (NVIDIA RTX 3090) | 250ms | ±30ms |
| GPU (NVIDIA T4) | 500ms | ±50ms |
| CPU (Intel i9-12900K) | 2.5s | ±0.3s |

### 메모리 사용량

| 환경 | 메모리 |
|------|--------|
| GPU VRAM | 2.0 GB |
| CPU RAM | 4.0 GB |

### 모델 정확도 (Test Set)

| 지표 | 값 |
|------|-----|
| Accuracy | 92.5% |
| Precision | 91.8% |
| Recall | 92.1% |
| F1 Score | 0.91 |
| AUC-ROC | 0.95 |

### 클래스별 성능

| 클래스 | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| glioblastoma | 0.94 | 0.93 | 0.94 |
| meningioma | 0.90 | 0.91 | 0.91 |
| pituitary_adenoma | 0.91 | 0.92 | 0.92 |

---

## Usage Examples

### 예시 1: 기본 사용

```python
from pathlib import Path
from your_module import predict

# DICOM 시리즈 경로
dicom_dir = Path("/data/patient_001/mri_study")

# 추론 실행
result = predict(dicom_dir, device="cuda")

# 결과 출력
print(f"Predicted Class: {result['prediction']['class']}")
print(f"Confidence: {result['prediction']['confidence']:.2%}")
```

### 예시 2: 전처리된 텐서 직접 입력

```python
import numpy as np
from your_module import predict

# 이미 전처리된 NumPy 텐서
preprocessed_tensor = np.load("preprocessed.npy")  # Shape: (1, 1, 256, 256, 128)

# 추론 실행
result = predict(preprocessed_tensor, device="cpu")
```

### 예시 3: 배치 처리

```python
from pathlib import Path
from your_module import InferenceEngine

# 엔진 초기화 (한 번만)
engine = InferenceEngine(model_path="./models/model_v1.pth", device="cuda")

# 여러 환자 처리
patient_dirs = [
    Path("/data/patient_001/mri_study"),
    Path("/data/patient_002/mri_study"),
    Path("/data/patient_003/mri_study"),
]

results = []
for dicom_dir in patient_dirs:
    result = engine.predict(dicom_dir)
    results.append(result)

# 결과 저장
import json
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### 예시 4: Flask 서버 통합 (Backend 팀 참고용)

```python
from flask import Flask, request, jsonify
from your_module import InferenceEngine

app = Flask(__name__)
engine = InferenceEngine(model_path="./models/model_v1.pth", device="cuda")

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """AI 추론 API"""
    try:
        data = request.json
        dicom_dir = data["dicom_dir"]

        result = engine.predict(dicom_dir)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

---

## 📌 체크리스트 (통합 전)

Backend Serving 팀이 이 모듈을 사용하기 전에 확인할 사항:

- [ ] Python 3.10+ 환경 구축
- [ ] requirements.txt로 의존성 설치
- [ ] 학습된 모델 파일 다운로드 (`model_v1.pth`)
- [ ] GPU 환경 확인 (CUDA 11.8+)
- [ ] Input Spec에 맞게 데이터 전처리
- [ ] 함수 호출 테스트 (`predict()`)
- [ ] Output Spec 형식 확인
- [ ] 에러 핸들링 구현
- [ ] 성능 측정 (추론 시간, 메모리)

---

## 📞 연락처

문의 사항이 있으면 AI 개발팀에 연락하세요:
- **담당자**: [이름]
- **이메일**: [이메일]
- **Slack**: #ai-development

---

**최종 수정일**: YYYY-MM-DD
**작성자**: [이름]
**버전**: 1.0
