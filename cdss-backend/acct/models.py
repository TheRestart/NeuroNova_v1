from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """7개 역할 정의 (01_권한7.txt 기반)"""
    ADMIN = 'admin', 'Admin'
    DOCTOR = 'doctor', 'Doctor'
    RIB = 'rib', 'RIB'
    LAB = 'lab', 'Lab'
    NURSE = 'nurse', 'Nurse'
    PATIENT = 'patient', 'Patient'
    EXTERNAL = 'external', 'External'


class User(AbstractUser):
    """
    CDSS 사용자 모델
    Django의 AbstractUser를 확장하여 7개 역할 지원
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
        verbose_name="역할"
    )
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="직원번호"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="부서"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="전화번호"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = 'acct_users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == Role.DOCTOR

    @property
    def is_rib(self):
        return self.role == Role.RIB

    @property
    def is_lab(self):
        return self.role == Role.LAB

    @property
    def is_nurse(self):
        return self.role == Role.NURSE

    @property
    def is_patient(self):
        return self.role == Role.PATIENT

    @property
    def is_external(self):
        return self.role == Role.EXTERNAL
