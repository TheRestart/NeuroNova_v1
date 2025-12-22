"""
EMR Models
OpenEMR 데이터를 캐시하는 모델
"""
from django.db import models
from django.conf import settings


class Patient(models.Model):
    """
    환자 정보 (OpenEMR 캐시)
    """
    openemr_patient_id = models.CharField(max_length=100, unique=True, help_text='OpenEMR 환자 ID')

    # 기본 정보
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    # 생년월일 및 성별
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    # 연락처
    phone_home = models.CharField(max_length=50, blank=True, null=True)
    phone_mobile = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # 주소
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # 동기화 정보
    last_synced_at = models.DateTimeField(auto_now=True, help_text='OpenEMR 마지막 동기화 시간')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'emr_patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['openemr_patient_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth']),
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.openemr_patient_id})'

    @property
    def full_name(self):
        """전체 이름"""
        if self.middle_name:
            return f'{self.first_name} {self.middle_name} {self.last_name}'
        return f'{self.first_name} {self.last_name}'


class Encounter(models.Model):
    """
    진료 기록 (OpenEMR 캐시)
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    openemr_encounter_id = models.CharField(max_length=100, unique=True, help_text='OpenEMR 진료 ID')

    # 진료 정보
    encounter_date = models.DateTimeField()
    encounter_type = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    # 담당 의사
    provider_name = models.CharField(max_length=200, blank=True, null=True)

    # 진단 및 처방
    diagnosis = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)

    # 동기화 정보
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'emr_encounters'
        ordering = ['-encounter_date']
        indexes = [
            models.Index(fields=['patient', 'encounter_date']),
            models.Index(fields=['openemr_encounter_id']),
        ]

    def __str__(self):
        return f'Encounter {self.openemr_encounter_id} - {self.patient.full_name} ({self.encounter_date})'
