from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    UserInfoView,
    ChangePasswordView,
    LogoutView,
    AdminUserListView,
    AdminUserDeleteView
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
]
