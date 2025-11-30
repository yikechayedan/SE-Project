from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, VerifyCodeSerializer, ResetPasswordSerializer,
    AvatarUploadSerializer
)
from .utils import generate_code, save_code, check_code

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

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # 检查邮箱是否存在
        if not User.objects.filter(email=email).exists():
            return Response({"code": 400, "msg": "该邮箱未注册"}, status=400)

        # 生成验证码
        code = generate_code()
        save_code(email, code)

        # 发送邮件
        

        send_mail(
            subject="PolyMetric 密码重置验证码",
            message=f"您的验证码为：{code}，5分钟内有效。",
            from_email=None,  # Django 会自动使用 DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False,  # 邮件失败时显示报错
        )

        return Response({"code": 200, "msg": "验证码已发送到您的邮箱"})
    

class VerifyCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        if not check_code(email, code):
            return Response({"code": 400, "msg": "验证码错误或已过期"}, status=400)

        return Response({"code": 200, "msg": "验证成功"})

class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        password = serializer.validated_data["password"]

        if not check_code(email, code):
            return Response({"code": 400, "msg": "验证码错误或已过期"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"code": 400, "msg": "该邮箱未注册"}, status=400)

        user.set_password(password)
        user.save()

        return Response({"code": 200,"msg": "密码重置成功"}, status=200)


class AvatarUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarUploadSerializer

    # 常见可接受的图片类型
    ALLOWED_TYPES = [
        "image/jpeg", "image/png", "image/gif",
        "image/webp", "image/bmp", "image/x-icon",
        "image/tiff", "image/svg+xml", "image/pjpeg",
        "image/heic", "image/heif"
    ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not request.FILES.get("avatar"):
            return Response({"code": 400, "msg": "请选择要上传的文件"}, status=400)

        file = request.FILES["avatar"]

        # 放宽格式判断
        if file.content_type not in self.ALLOWED_TYPES:
            return Response({
                "code": 400,
                "msg": f"文件格式不支持，仅支持 jpg/png/gif"
            }, status=400)

        # 检查文件大小
        if file.size > 2 * 1024 * 1024:
            return Response({
                "code": 413,
                "msg": "文件过大，最大支持 2MB"
            }, status=413)

        user = request.user
        user.avatar = file
        user.save()

        return Response({
            "code": 200,
            "msg": "头像上传成功",
            "data": {"avatar": request.build_absolute_uri(user.avatar.url)}
        }, status=200)

