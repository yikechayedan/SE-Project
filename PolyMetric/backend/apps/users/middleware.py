from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()


class UpdateLastLoginMiddleware:
    """
    更新用户最后登录时间的中间件
    
    这个中间件会在每个已认证用户的请求中检查并更新用户的最后登录时间，
    但为了性能考虑，只有当用户的最后登录时间超过一定时间间隔（如5分钟）时才更新。
    
    支持 Session 认证和 SimpleJWT 认证。
    """
    
    # 更新间隔：5分钟
    UPDATE_INTERVAL = timedelta(minutes=5)
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 尝试获取用户
        user = getattr(request, 'user', None)
        
        # 如果标准中间件未认证用户（例如使用JWT时），尝试手动进行JWT认证
        if not user or not user.is_authenticated:
            try:
                jwt_auth = JWTAuthentication()
                # authenticate 返回 (user, token) 或 None
                auth_result = jwt_auth.authenticate(request)
                if auth_result:
                    user, _ = auth_result
                    # 可选：将认证后的用户赋值给 request，供后续使用
                    request.user = user
            except Exception:
                # 忽略认证错误（如 Token 无效/过期），交由后续 DRF 视图处理
                pass
        
        # 处理请求前的逻辑：如果用户已认证，检查并更新最后登录时间
        if user and user.is_authenticated:
            # 检查是否需要更新最后登录时间
            now = timezone.now()
            
            # 如果用户没有last_login或者last_login超过更新间隔，则更新
            if (not user.last_login or 
                now - user.last_login > self.UPDATE_INTERVAL):
                
                # 使用update()方法而不是save()来避免触发其他信号和更新updated_at字段
                User.objects.filter(id=user.id).update(last_login=now)
                
                # 同时更新user对象
                user.last_login = now
        
        # 处理请求
        response = self.get_response(request)
        
        return response