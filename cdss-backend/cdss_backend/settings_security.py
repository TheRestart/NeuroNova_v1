"""
보안/권한 설정 토글

개발 중에는 ENABLE_SECURITY = False로 설정하여
인증/권한 검증을 우회할 수 있습니다.

프로덕션 배포 시 반드시 ENABLE_SECURITY = True로 설정!
"""

import os

# ⚠️ 보안 기능 활성화/비활성화 토글
# 개발 중: False (빠른 테스트)
# 프로덕션: True (필수!)
ENABLE_SECURITY = os.getenv('ENABLE_SECURITY', 'False').lower() == 'true'

# 보안 설정
SECURITY_CONFIG = {
    # 인증 필수 여부
    'REQUIRE_AUTHENTICATION': ENABLE_SECURITY,

    # 권한 검증 필수 여부
    'REQUIRE_PERMISSIONS': ENABLE_SECURITY,

    # 감사 로그 기록 여부
    'ENABLE_AUDIT_LOG': ENABLE_SECURITY,

    # Token 만료 시간 (초)
    'TOKEN_EXPIRY_SECONDS': 86400 if not ENABLE_SECURITY else 3600,  # 개발: 24시간, 프로덕션: 1시간
}


def get_permission_classes():
    """
    보안 설정에 따라 권한 클래스 반환

    ENABLE_SECURITY = False: AllowAny (모든 요청 허용)
    ENABLE_SECURITY = True: IsAuthenticated (인증 필수)
    """
    if ENABLE_SECURITY:
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated]
    else:
        from rest_framework.permissions import AllowAny
        return [AllowAny]


def should_check_permission(permission_class):
    """
    권한 검증 여부 확인

    개발 모드에서는 모든 권한 검증 우회
    """
    if not ENABLE_SECURITY:
        return False
    return True


def should_log_audit(action):
    """
    감사 로그 기록 여부 확인

    개발 모드에서는 선택적 로깅
    """
    if not ENABLE_SECURITY:
        # 개발 모드에서는 LOGIN/LOGOUT만 로깅 (디버깅용)
        return action in ['LOGIN', 'LOGOUT']
    return True


# 보안 모드 출력 (서버 시작 시)
def print_security_status():
    """서버 시작 시 보안 모드 출력"""
    if ENABLE_SECURITY:
        print("=" * 50)
        print("🔒 SECURITY MODE: ENABLED")
        print("   - Authentication: REQUIRED")
        print("   - Permissions: ENFORCED")
        print("   - Audit Log: ENABLED")
        print("=" * 50)
    else:
        print("=" * 50)
        print("⚠️  SECURITY MODE: DISABLED (DEVELOPMENT)")
        print("   - Authentication: BYPASSED")
        print("   - Permissions: BYPASSED")
        print("   - Audit Log: PARTIAL")
        print("   ⚠️  DO NOT USE IN PRODUCTION!")
        print("=" * 50)
