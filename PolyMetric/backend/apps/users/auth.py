from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义JWT序列化器，在验证成功后更新用户的最后登录时间
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 更新用户的最后登录时间
        if self.user:
            self.user.last_login = timezone.now()
            self.user.save(update_fields=['last_login'])
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义JWT认证视图，使用自定义序列化器
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # 如果验证失败，返回标准错误响应
            return Response({
                "code": 401,
                "msg": "用户名或密码错误",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 返回标准格式的响应
        return Response({
            "code": 200,
            "msg": "登录成功",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)