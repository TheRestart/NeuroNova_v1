from .models import AuditLog


class AuditClient:
    """
    감사 로그 클라이언트
    다른 앱에서 이 클라이언트를 사용하여 감사 로그를 기록
    """

    @staticmethod
    def log_event(user, action, resource_type, resource_id=None, request=None, details=None):
        """
        감사 이벤트 기록

        Args:
            user: User 객체 (None 가능)
            action: 액션 타입 (LOGIN, LOGOUT, CREATE, READ, UPDATE, DELETE 등)
            resource_type: 리소스 타입 (User, Patient, Order 등)
            resource_id: 리소스 ID (선택)
            request: Django Request 객체 (선택, IP/User-Agent 추출용)
            details: 추가 상세 정보 (dict, 선택)

        Returns:
            AuditLog 객체
        """
        ip_address = '127.0.0.1'
        user_agent = None

        if request:
            # X-Forwarded-For 헤더 확인 (프록시 환경)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

            user_agent = request.META.get('HTTP_USER_AGENT', '')

        audit_log = AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )

        return audit_log

    @staticmethod
    def log_login_success(user, request=None):
        """로그인 성공 로그"""
        return AuditClient.log_event(
            user=user,
            action='LOGIN',
            resource_type='User',
            resource_id=user.id,
            request=request,
            details={'status': 'success'}
        )

    @staticmethod
    def log_login_failed(username, request=None):
        """로그인 실패 로그"""
        return AuditClient.log_event(
            user=None,
            action='LOGIN_FAILED',
            resource_type='User',
            request=request,
            details={'username': username, 'status': 'failed'}
        )

    @staticmethod
    def log_logout(user, request=None):
        """로그아웃 로그"""
        return AuditClient.log_event(
            user=user,
            action='LOGOUT',
            resource_type='User',
            resource_id=user.id,
            request=request
        )

    @staticmethod
    def log_permission_denied(user, resource_type, resource_id=None, request=None):
        """권한 거부 로그"""
        return AuditClient.log_event(
            user=user,
            action='PERMISSION_DENIED',
            resource_type=resource_type,
            resource_id=resource_id,
            request=request
        )

    @staticmethod
    def log_resource_access(user, action, resource_type, resource_id, request=None, details=None):
        """리소스 접근 로그 (일반)"""
        return AuditClient.log_event(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request=request,
            details=details
        )
