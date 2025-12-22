from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """감사 로그 관리자 설정"""
    list_display = ('timestamp', 'user', 'action', 'resource_type', 'resource_id', 'ip_address')
    list_filter = ('action', 'resource_type', 'timestamp')
    search_fields = ('user__username', 'resource_type', 'resource_id', 'ip_address')
    readonly_fields = ('user', 'action', 'resource_type', 'resource_id', 'ip_address', 'user_agent', 'timestamp', 'details')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        """감사 로그는 수동으로 추가할 수 없음"""
        return False

    def has_change_permission(self, request, obj=None):
        """감사 로그는 수정할 수 없음"""
        return False

    def has_delete_permission(self, request, obj=None):
        """감사 로그는 삭제할 수 없음 (Admin만 가능하도록 추후 수정 가능)"""
        return request.user.is_superuser
