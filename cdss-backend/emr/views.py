"""
EMR Views
Django 중앙 인증 정책 준수: 모든 OpenEMR 접근은 이 API를 통해서만
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

from acct.permissions import IsDoctorOrNurse, IsDoctor, IsStaffRole
from audit.client import AuditClient
from .clients.openemr_client import OpenEMRClient
from .models import Patient, Encounter
from .serializers import PatientSerializer, EncounterSerializer, OpenEMRPatientSerializer

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])  # 개발 모드에서는 권한 우회
def health_check(request):
    """
    OpenEMR 서버 연결 상태 확인

    GET /api/emr/health/
    """
    client = OpenEMRClient()
    is_healthy = client.health_check()

    return Response({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'openemr_url': settings.OPENEMR_BASE_URL,
        'message': 'OpenEMR connection successful' if is_healthy else 'OpenEMR connection failed'
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 프로덕션: IsDoctorOrNurse
def search_patients(request):
    """
    OpenEMR에서 환자 검색

    GET /api/emr/patients/search/?fname=John&lname=Doe
    """
    # 감사 로그 (프로덕션 모드에서만)
    if settings.ENABLE_SECURITY:
        AuditClient.log_event(
            user=request.user,
            action='READ',
            resource_type='Patient',
            resource_id=None,
            request=request,
            details={'action': 'search_patients', 'params': request.GET.dict()}
        )

    # OpenEMR에서 환자 검색
    client = OpenEMRClient()
    fname = request.GET.get('fname')
    lname = request.GET.get('lname')
    dob = request.GET.get('dob')
    limit = int(request.GET.get('limit', 20))

    patients = client.search_patients(
        fname=fname,
        lname=lname,
        dob=dob,
        limit=limit
    )

    # OpenEMR 응답을 직렬화
    serializer = OpenEMRPatientSerializer(patients, many=True)

    return Response({
        'count': len(patients),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 프로덕션: IsDoctorOrNurse
def get_patient_detail(request, patient_id):
    """
    OpenEMR에서 환자 상세 정보 조회

    GET /api/emr/patients/{patient_id}/
    """
    # 감사 로그
    if settings.ENABLE_SECURITY:
        AuditClient.log_event(
            user=request.user,
            action='READ',
            resource_type='Patient',
            resource_id=patient_id,
            request=request
        )

    client = OpenEMRClient()
    patient_data = client.get_patient(patient_id)

    if not patient_data:
        return Response({
            'error': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # OpenEMR 응답을 직렬화
    serializer = OpenEMRPatientSerializer(patient_data)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])  # 프로덕션: IsDoctorOrNurse
def get_patient_encounters(request, patient_id):
    """
    환자 진료 기록 조회

    GET /api/emr/patients/{patient_id}/encounters/
    """
    # 감사 로그
    if settings.ENABLE_SECURITY:
        AuditClient.log_event(
            user=request.user,
            action='READ',
            resource_type='Encounter',
            resource_id=None,
            request=request,
            details={'patient_id': patient_id}
        )

    client = OpenEMRClient()
    encounters = client.get_encounters(patient_id)

    return Response({
        'count': len(encounters),
        'results': encounters
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 프로덕션: IsDoctorOrNurse
def get_patient_vitals(request, patient_id):
    """
    환자 바이탈 사인 조회

    GET /api/emr/patients/{patient_id}/vitals/
    """
    # 감사 로그
    if settings.ENABLE_SECURITY:
        AuditClient.log_event(
            user=request.user,
            action='READ',
            resource_type='Vital',
            resource_id=None,
            request=request,
            details={'patient_id': patient_id}
        )

    client = OpenEMRClient()
    vitals = client.get_vitals(patient_id)

    return Response({
        'count': len(vitals),
        'results': vitals
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cached_patients(request):
    """
    Django DB에 캐시된 환자 목록

    GET /api/emr/cached/patients/
    """
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)

    return Response({
        'count': patients.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cached_encounters(request):
    """
    Django DB에 캐시된 진료 기록 목록

    GET /api/emr/cached/encounters/
    """
    encounters = Encounter.objects.select_related('patient').all()
    serializer = EncounterSerializer(encounters, many=True)

    return Response({
        'count': encounters.count(),
        'results': serializer.data
    })
