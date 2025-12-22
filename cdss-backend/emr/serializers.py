"""
EMR Serializers
"""
from rest_framework import serializers
from .models import Patient, Encounter


class PatientSerializer(serializers.ModelSerializer):
    """환자 정보 Serializer"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            'id', 'openemr_patient_id', 'first_name', 'last_name', 'middle_name',
            'full_name', 'date_of_birth', 'gender',
            'phone_home', 'phone_mobile', 'email',
            'street', 'city', 'state', 'postal_code',
            'last_synced_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_synced_at', 'created_at', 'updated_at']


class EncounterSerializer(serializers.ModelSerializer):
    """진료 기록 Serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = Encounter
        fields = [
            'id', 'patient', 'patient_name', 'openemr_encounter_id',
            'encounter_date', 'encounter_type', 'reason',
            'provider_name', 'diagnosis', 'prescription',
            'last_synced_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_synced_at', 'created_at', 'updated_at']


class OpenEMRPatientSerializer(serializers.Serializer):
    """OpenEMR API 응답 Serializer"""
    id = serializers.CharField(required=False)
    fname = serializers.CharField(required=False)
    lname = serializers.CharField(required=False)
    mname = serializers.CharField(required=False, allow_blank=True)
    DOB = serializers.DateField(required=False)
    sex = serializers.CharField(required=False, allow_blank=True)
    phone_home = serializers.CharField(required=False, allow_blank=True)
    phone_cell = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    street = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
