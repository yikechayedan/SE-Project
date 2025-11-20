from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from rest_framework.permissions import AllowAny
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    用户注册
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        #return Response({"code": 200, "msg": "注册成功", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({
            "code": 200,
            "msg": "注册成功",
            "data": UserSerializer(user).data  # 不返回密码
        }, status=status.HTTP_201_CREATED)

class UserInfoView(generics.RetrieveUpdateAPIView):
    """
    获取当前用户信息（GET）/ 修改用户信息（PUT）
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

class ChangePasswordView(generics.UpdateAPIView):
    """
    修改密码
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, *args, **kwargs):
        # 旧密码校验、密码修改
        return super().update(request, *args, **kwargs)

class LogoutView(generics.GenericAPIView):
    """
    注销登录（使 refresh token 无效）
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # 刷新令牌加入黑名单
                return Response({"code": 200, "msg": "退出成功"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"code": 400, "msg": "无效的刷新令牌"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": 400, "msg": "没有提供 refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class AdminUserListView(generics.ListAPIView):
    """
    管理员查看所有用户
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        return Response({
            "code": 400,
            "msg": str(exc)
        }, status=response.status_code)

class AdminUserDeleteView(generics.DestroyAPIView):
    """
    管理员删除用户
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        return Response({
            "code": 400,
            "msg": str(exc)
        }, status=response.status_code)
