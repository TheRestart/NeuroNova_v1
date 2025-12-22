"""
OpenEMR API Client
Django 중앙 인증 정책 준수: 이 클래스는 Django 내부에서만 사용

보안 정책:
- OpenEMR 인증은 Django가 대신 처리
- OpenEMR은 신뢰된 내부 데이터 소스로 취급
- 모든 보안 검증은 Django에서 수행
"""
import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class OpenEMRClient:
    """
    OpenEMR REST API 클라이언트 (인증 단순화 버전)

    보안 정책:
    - 이 클래스는 Django 내부에서만 사용 (직접 노출 금지)
    - OpenEMR 인증은 제거 (Django가 모든 보안 담당)
    - OpenEMR을 내부 데이터베이스처럼 취급
    """

    def __init__(self):
        self.base_url = settings.OPENEMR_BASE_URL.rstrip('/')
        self.session = requests.Session()

        # Basic headers (인증 헤더 제거)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

        logger.info(f"OpenEMRClient initialized with base_url: {self.base_url}")

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        환자 정보 조회 (인증 불필요)

        Args:
            patient_id: OpenEMR 환자 ID

        Returns:
            환자 정보 (dict)
        """
        try:
            url = f'{self.base_url}/apis/default/api/patient/{patient_id}'
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Retrieved patient: {patient_id}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get patient {patient_id}: {str(e)}")
            return None

    def search_patients(self,
                       fname: Optional[str] = None,
                       lname: Optional[str] = None,
                       dob: Optional[str] = None,
                       limit: int = 20) -> List[Dict]:
        """
        환자 검색 (인증 불필요)

        Args:
            fname: 이름
            lname: 성
            dob: 생년월일 (YYYY-MM-DD)
            limit: 결과 제한

        Returns:
            환자 목록
        """
        try:
            url = f'{self.base_url}/apis/default/api/patient'

            params = {}
            if fname:
                params['fname'] = fname
            if lname:
                params['lname'] = lname
            if dob:
                params['dob'] = dob
            params['_limit'] = limit

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            patients = data.get('data', []) if isinstance(data, dict) else data

            logger.info(f"Found {len(patients)} patients")
            return patients

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search patients: {str(e)}")
            return []

    def get_encounters(self, patient_id: str) -> List[Dict]:
        """
        환자 진료 기록 조회 (인증 불필요)

        Args:
            patient_id: OpenEMR 환자 ID

        Returns:
            진료 기록 목록
        """
        try:
            url = f'{self.base_url}/apis/default/api/encounter'
            params = {'patient': patient_id}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            encounters = data.get('data', []) if isinstance(data, dict) else data

            logger.info(f"Retrieved {len(encounters)} encounters for patient {patient_id}")
            return encounters

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get encounters for patient {patient_id}: {str(e)}")
            return []

    def get_vitals(self, patient_id: str) -> List[Dict]:
        """
        환자 바이탈 사인 조회 (인증 불필요)

        Args:
            patient_id: OpenEMR 환자 ID

        Returns:
            바이탈 사인 목록
        """
        try:
            url = f'{self.base_url}/apis/default/api/vital'
            params = {'patient': patient_id}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            vitals = data.get('data', []) if isinstance(data, dict) else data

            logger.info(f"Retrieved {len(vitals)} vitals for patient {patient_id}")
            return vitals

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get vitals for patient {patient_id}: {str(e)}")
            return []

    def health_check(self) -> bool:
        """
        OpenEMR 서버 연결 확인

        Returns:
            연결 성공 여부
        """
        try:
            url = f'{self.base_url}/'
            response = self.session.get(url, timeout=5)
            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenEMR health check failed: {str(e)}")
            return False
