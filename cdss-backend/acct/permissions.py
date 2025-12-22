from rest_framework import permissions
from .models import Role


class IsAdmin(permissions.BasePermission):
    """Admin 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.ADMIN


class IsDoctor(permissions.BasePermission):
    """Doctor 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.DOCTOR


class IsRIB(permissions.BasePermission):
    """RIB (방사선과) 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.RIB


class IsLab(permissions.BasePermission):
    """Lab (검사실) 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.LAB


class IsNurse(permissions.BasePermission):
    """Nurse 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.NURSE


class IsDoctorOrRIB(permissions.BasePermission):
    """Doctor 또는 RIB 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.DOCTOR, Role.RIB]


class IsDoctorOrNurse(permissions.BasePermission):
    """Doctor 또는 Nurse 역할만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.DOCTOR, Role.NURSE]


class IsSelfOrAdmin(permissions.BasePermission):
    """본인 또는 Admin만 접근 가능 (Patient의 자기 데이터 접근용)"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == Role.ADMIN:
            return True
        # Patient는 본인 데이터만 접근
        return obj.id == request.user.id or (hasattr(obj, 'user') and obj.user.id == request.user.id)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin은 모든 권한, 나머지는 읽기만 가능"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == Role.ADMIN


class IsStaffRole(permissions.BasePermission):
    """의료진 역할 (Admin, Doctor, RIB, Lab, Nurse)만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            Role.ADMIN,
            Role.DOCTOR,
            Role.RIB,
            Role.LAB,
            Role.NURSE
        ]
