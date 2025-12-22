from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User 모델 관리자 설정"""
    list_display = ('username', 'email', 'role', 'employee_id', 'department', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'employee_id', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('CDSS 정보', {'fields': ('role', 'employee_id', 'department', 'phone')}),
        ('타임스탬프', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('CDSS 정보', {'fields': ('role', 'employee_id', 'department', 'phone')}),
    )
