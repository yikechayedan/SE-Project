from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

from .models import User


# ------------------------------
# 自定义表单：用于后台修改用户
# ------------------------------
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone', 'avatar', 'bio',
            'is_active', 'is_staff', 'is_superuser', 'groups'
        )

    def validate_unique(self):
        """
        覆盖默认唯一性校验 —— 修复 Django Admin 错误绑定 avatar 的问题
        并且使用 add_error() 将错误显示到表单，而不是抛出异常导致页面崩溃
        """
        super(UserChangeForm, self).validate_unique()

        # 校验邮箱唯一
        email = self.cleaned_data.get("email")
        if email and User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            self.add_error("email", "该邮箱已被其他用户使用")

        # 校验手机号唯一
        phone = self.cleaned_data.get("phone")
        if phone and User.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            self.add_error("phone", "该手机号已被其他用户使用")




# ------------------------------
# 自定义表单：用于后台新建用户
# ------------------------------
class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password("defaultpassword123")  # 后台添加用户默认密码
        if commit:
            user.save()
        return user


# ------------------------------
# 自定义 UserAdmin（必须覆盖 BaseUserAdmin）
# ------------------------------
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm       # 编辑用户
    add_form = UserCreationForm # 添加用户

    list_display = ('id', 'username', 'email', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # 后台表单排版
    fieldsets = (
        ('基本信息', {'fields': ('username', 'password')}),
        ('个人资料', {'fields': ('email', 'phone', 'avatar', 'bio')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('时间信息', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('新增用户', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone'),
        }),
    )

    search_fields = ('username', 'email', 'phone')
    ordering = ('id',)


admin.site.register(User, UserAdmin)
