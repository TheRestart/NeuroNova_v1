"""
EMR Unit Tests
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .clients.openemr_client import OpenEMRClient
from .models import Patient, Encounter


class OpenEMRClientTest(TestCase):
    """OpenEMRClient 단위 테스트"""

    def setUp(self):
        self.client = OpenEMRClient()

    @patch('emr.clients.openemr_client.requests.Session')
    def test_health_check_success(self, mock_session):
        """Health check 성공 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        result = self.client.health_check()
        self.assertTrue(result)

    @patch('emr.clients.openemr_client.requests.Session')
    def test_health_check_failure(self, mock_session):
        """Health check 실패 테스트"""
        mock_session.return_value.get.side_effect = Exception("Connection error")

        result = self.client.health_check()
        self.assertFalse(result)

    @patch('emr.clients.openemr_client.requests.Session')
    def test_authenticate_success(self, mock_session):
        """OpenEMR 인증 성공 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'token': 'test_token_123'}
        mock_session.return_value.post.return_value = mock_response

        token = self.client.authenticate('admin', 'pass')
        self.assertEqual(token, 'test_token_123')

    @patch('emr.clients.openemr_client.requests.Session')
    def test_get_patient_success(self, mock_session):
        """환자 정보 조회 성공 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': '1',
            'fname': 'John',
            'lname': 'Doe'
        }
        mock_session.return_value.get.return_value = mock_response

        patient = self.client.get_patient('1')
        self.assertIsNotNone(patient)
        self.assertEqual(patient['fname'], 'John')
        self.assertEqual(patient['lname'], 'Doe')


class EMRViewsTest(TestCase):
    """EMR Views 단위 테스트"""

    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        """Health check 엔드포인트 테스트"""
        response = self.client.get(reverse('emr:health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    @patch('emr.views.OpenEMRClient')
    def test_search_patients_endpoint(self, mock_client_class):
        """환자 검색 엔드포인트 테스트"""
        mock_client = MagicMock()
        mock_client.search_patients.return_value = [
            {'id': '1', 'fname': 'John', 'lname': 'Doe'}
        ]
        mock_client_class.return_value = mock_client

        response = self.client.get(reverse('emr:search_patients'), {
            'fname': 'John',
            'lname': 'Doe'
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertTrue(len(data['results']) > 0)

    @patch('emr.views.OpenEMRClient')
    def test_get_patient_detail_endpoint(self, mock_client_class):
        """환자 상세 조회 엔드포인트 테스트"""
        mock_client = MagicMock()
        mock_client.get_patient.return_value = {
            'id': '1',
            'fname': 'John',
            'lname': 'Doe'
        }
        mock_client_class.return_value = mock_client

        response = self.client.get(reverse('emr:patient_detail', args=['1']))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('fname', data)

    @patch('emr.views.OpenEMRClient')
    def test_get_patient_detail_not_found(self, mock_client_class):
        """존재하지 않는 환자 조회 테스트"""
        mock_client = MagicMock()
        mock_client.get_patient.return_value = None
        mock_client_class.return_value = mock_client

        response = self.client.get(reverse('emr:patient_detail', args=['999']))

        self.assertEqual(response.status_code, 404)


class PatientModelTest(TestCase):
    """Patient 모델 테스트"""

    def test_create_patient(self):
        """환자 생성 테스트"""
        patient = Patient.objects.create(
            openemr_patient_id='test-patient-001',
            first_name='Jane',
            last_name='Smith',
            date_of_birth='1990-01-15',
            gender='Female'
        )

        self.assertEqual(patient.openemr_patient_id, 'test-patient-001')
        self.assertEqual(patient.first_name, 'Jane')
        self.assertEqual(patient.full_name, 'Jane Smith')

    def test_patient_full_name_with_middle_name(self):
        """중간 이름 포함 전체 이름 테스트"""
        patient = Patient.objects.create(
            openemr_patient_id='test-patient-002',
            first_name='John',
            middle_name='William',
            last_name='Doe'
        )

        self.assertEqual(patient.full_name, 'John William Doe')

    def test_patient_str_representation(self):
        """Patient 모델 문자열 표현 테스트"""
        patient = Patient.objects.create(
            openemr_patient_id='test-patient-003',
            first_name='Alice',
            last_name='Johnson'
        )

        self.assertEqual(str(patient), 'Johnson Alice (test-patient-003)')


class EncounterModelTest(TestCase):
    """Encounter 모델 테스트"""

    def setUp(self):
        self.patient = Patient.objects.create(
            openemr_patient_id='test-patient-001',
            first_name='John',
            last_name='Doe'
        )

    def test_create_encounter(self):
        """진료 기록 생성 테스트"""
        encounter = Encounter.objects.create(
            patient=self.patient,
            openemr_encounter_id='encounter-001',
            encounter_date='2025-12-22 10:00:00',
            encounter_type='Office Visit',
            provider_name='Dr. Smith'
        )

        self.assertEqual(encounter.patient, self.patient)
        self.assertEqual(encounter.openemr_encounter_id, 'encounter-001')
        self.assertEqual(encounter.provider_name, 'Dr. Smith')

    def test_encounter_patient_relationship(self):
        """Encounter와 Patient 관계 테스트"""
        Encounter.objects.create(
            patient=self.patient,
            openemr_encounter_id='encounter-001',
            encounter_date='2025-12-22 10:00:00'
        )
        Encounter.objects.create(
            patient=self.patient,
            openemr_encounter_id='encounter-002',
            encounter_date='2025-12-21 14:00:00'
        )

        # Patient의 encounters 역참조 테스트
        self.assertEqual(self.patient.encounters.count(), 2)

    def test_encounter_str_representation(self):
        """Encounter 모델 문자열 표현 테스트"""
        encounter = Encounter.objects.create(
            patient=self.patient,
            openemr_encounter_id='encounter-001',
            encounter_date='2025-12-22 10:00:00'
        )

        expected_str = f'Encounter encounter-001 - John Doe (2025-12-22 10:00:00+00:00)'
        self.assertIn('encounter-001', str(encounter))
        self.assertIn('John Doe', str(encounter))


class IntegrationTest(TestCase):
    """통합 테스트"""

    def test_cached_patients_endpoint(self):
        """캐시된 환자 목록 엔드포인트 테스트"""
        # 테스트 데이터 생성
        Patient.objects.create(
            openemr_patient_id='patient-001',
            first_name='John',
            last_name='Doe'
        )
        Patient.objects.create(
            openemr_patient_id='patient-002',
            first_name='Jane',
            last_name='Smith'
        )

        client = Client()
        response = client.get(reverse('emr:cached_patients'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)

    def test_cached_encounters_endpoint(self):
        """캐시된 진료 기록 엔드포인트 테스트"""
        # 테스트 데이터 생성
        patient = Patient.objects.create(
            openemr_patient_id='patient-001',
            first_name='John',
            last_name='Doe'
        )
        Encounter.objects.create(
            patient=patient,
            openemr_encounter_id='encounter-001',
            encounter_date='2025-12-22 10:00:00'
        )

        client = Client()
        response = client.get(reverse('emr:cached_encounters'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
