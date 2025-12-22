from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 직렬화"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'employee_id', 'department', 'phone',
            'first_name', 'last_name', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """사용자 생성 직렬화 (비밀번호 포함)"""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'role', 'employee_id', 'department', 'phone',
            'first_name', 'last_name'
        ]

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """로그인 요청 직렬화"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class LoginResponseSerializer(serializers.Serializer):
    """로그인 응답 직렬화"""
    token = serializers.CharField()
    user = UserSerializer()
