from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserFollow
from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, VerifyCodeSerializer, ResetPasswordSerializer,
    AvatarUploadSerializer,
    UserPublicSerializer, UserMeSerializer,
    PrivacySettingSerializer, FollowedUserSerializer,
)
from .utils import generate_code, save_code, check_code

User = get_user_model()

# ========== 保留原有核心视图（已实现） ==========
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # 获取第一个错误信息
            first_error = next(iter(serializer.errors.values()))[0]
            return Response({
                "code": 400,
                "msg": f"注册失败：{first_error}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.save()
        return Response({
            "code": 200,
            "msg": "注册成功",
            "data": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"code": 200, "msg": "退出成功"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"code": 400, "msg": "无效的刷新令牌"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": 400, "msg": "没有提供 refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class AdminUserListView(generics.ListAPIView):
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

        if not User.objects.filter(email=email).exists():
            return Response({"code": 400, "msg": "该邮箱未注册"}, status=400)

        code = generate_code()
        save_code(email, code)

        send_mail(
            subject="PolyMetric 密码重置验证码",
            message=f"您的验证码为：{code}，5分钟内有效。",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
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

        if file.content_type not in self.ALLOWED_TYPES:
            return Response({
                "code": 400,
                "msg": f"文件格式不支持，仅支持 jpg/png/gif"
            }, status=400)

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

# ========== 修复用户公开信息视图（API1） ==========
class UserPublicView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]  # 未登录也可访问

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 序列化时传入request，用于判断is_followed
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# ========== 修复关注/取消关注视图（API2/3） ==========
class UserFollowView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_target_user(self):
        try:
            return User.objects.get(id=self.kwargs['id'])
        except User.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        """关注用户"""
        target_user = self.get_target_user()
        if not target_user:
            return Response({
                "code": 404,
                "msg": "目标用户不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user == target_user:
            return Response({
                "code": 400,
                "msg": "不能关注自己",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if UserFollow.objects.filter(follower=request.user, followed=target_user).exists():
            return Response({
                "code": 400,
                "msg": "已关注该用户",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        UserFollow.objects.create(follower=request.user, followed=target_user)
        return Response({
            "code": 201,
            "msg": "关注成功",
            "data": None
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """取消关注用户"""
        target_user = self.get_target_user()
        if not target_user:
            return Response({
                "code": 404,
                "msg": "目标用户不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow_relation = UserFollow.objects.get(follower=request.user, followed=target_user)
            follow_relation.delete()
            # 修复：将"已取消关注"改为"取消关注成功"，匹配测试用例
            return Response({
                "code": 200,
                "msg": "取消关注成功",  
                "data": None
            }, status=status.HTTP_200_OK)
        except UserFollow.DoesNotExist:
            return Response({
                "code": 400,
                "msg": "未关注该用户",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

# ========== 修复关注用户列表视图（API4） ==========
class FollowedUsersListView(generics.ListAPIView):
    serializer_class = FollowedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 查询当前用户关注的所有用户（关联UserFollow）
        return UserFollow.objects.filter(
            follower=self.request.user
        ).select_related("followed").order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

# ========== 修复隐私设置更新视图（API5） ==========
class PrivacySettingView(generics.UpdateAPIView):
    serializer_class = PrivacySettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # 允许部分更新
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "code": 200,
            "msg": "设置已更新",
            "data": serializer.data
        })

# ========== 修复当前用户信息视图（API6） ==========
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    GET: 获取当前用户信息（返回隐私设置字段）
    PUT/PATCH: 更新当前用户信息（email, phone, bio等）
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        # GET 请求用 UserMeSerializer（包含隐私设置字段）
        # PUT/PATCH 请求用 UserSerializer（用于更新基本资料）
        if self.request.method == 'GET':
            return UserMeSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "msg": "更新成功",
            "data": serializer.data
        })

# ========== 用户统计视图（API7） ==========
@api_view(['GET'])
@permission_classes([AllowAny])
def user_stats(request):
    """
    统计用户总数和近期活跃用户数
    """
    # 1. 统计总数
    total_count = User.objects.count()
    
    # 2. 统计在线（近似值）：过去 15 分钟内有过登录行为的用户
    # 注意：这依赖于 last_login 字段。
    # 如果想统计"活跃"，需要在中间件中频繁更新 last_login 或使用 Redis。
    time_threshold = timezone.now() - timedelta(minutes=15)
    online_count = User.objects.filter(last_login__gte=time_threshold).count()

    # 兜底：如果当前有人调用这个接口，说明至少有1人在线
    if online_count == 0 and request.user.is_authenticated:
        online_count = 1

    return Response({
        "code": 200,
        "msg": "success",
        "data": {
            "total_users": total_count,
            "online_users": online_count
        }
    })
