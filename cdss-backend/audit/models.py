from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    감사 로그 모델
    모든 중요한 사용자 액션을 기록
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name="사용자"
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name="액션"
    )
    resource_type = models.CharField(
        max_length=50,
        verbose_name="리소스 타입"
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="리소스 ID"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="IP 주소"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="발생시각"
    )
    details = models.JSONField(
        blank=True,
        null=True,
        verbose_name="상세정보"
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '감사 로그'
        verbose_name_plural = '감사 로그들'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Unknown"
        return f"[{self.timestamp}] {username} - {self.action} on {self.resource_type}"
