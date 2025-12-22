from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from audit.client import AuditClient
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    LoginResponseSerializer
)
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    로그인 API
    POST /api/acct/login/
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)

    if not user:
        # 로그인 실패 감사 로그
        AuditClient.log_login_failed(username, request)
        return Response(
            {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        AuditClient.log_permission_denied(user, 'User', user.id, request)
        return Response(
            {'error': '비활성화된 계정입니다. 관리자에게 문의하세요.'},
            status=status.HTTP_403_FORBIDDEN
        )

    token, _ = Token.objects.get_or_create(user=user)

    # 로그인 성공 감사 로그
    AuditClient.log_login_success(user, request)

    response_data = {
        'token': token.key,
        'user': UserSerializer(user).data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    회원가입 API
    POST /api/acct/register/
    """
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token = Token.objects.create(user=user)

    # 회원가입 감사 로그
    AuditClient.log_event(
        user=user,
        action='CREATE',
        resource_type='User',
        resource_id=user.id,
        request=request,
        details={'role': user.role}
    )

    response_data = {
        'token': token.key,
        'user': UserSerializer(user).data
    }

    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    로그아웃 API
    POST /api/acct/logout/
    """
    try:
        # 로그아웃 감사 로그
        AuditClient.log_logout(request.user, request)

        request.user.auth_token.delete()
        return Response(
            {'message': '로그아웃 되었습니다.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    현재 로그인한 사용자 정보 조회
    GET /api/acct/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
