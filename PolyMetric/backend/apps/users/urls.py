from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView, UserInfoView, ChangePasswordView,
    LogoutView, AdminUserListView, AdminUserDeleteView,
    ForgotPasswordView, VerifyCodeView, ResetPasswordView,
    AvatarUploadView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),

    # 登录 & 刷新 token
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 用户信息
    path("me/", UserInfoView.as_view(), name="user_info"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # 管理员
    path("admin/users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("admin/users/<int:pk>/", AdminUserDeleteView.as_view(), name="admin_user_delete"),

     # 密码找回接口
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify_code"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),

    # 头像上传
    path("avatar/", AvatarUploadView.as_view(), name="upload_avatar"),
]
