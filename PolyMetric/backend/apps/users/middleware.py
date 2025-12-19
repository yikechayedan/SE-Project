from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


class UpdateLastLoginMiddleware:
    """
    更新用户最后登录时间的中间件
    
    这个中间件会在每个已认证用户的请求中检查并更新用户的最后登录时间，
    但为了性能考虑，只有当用户的最后登录时间超过一定时间间隔（如5分钟）时才更新。
    """
    
    # 更新间隔：5分钟
    UPDATE_INTERVAL = timedelta(minutes=5)
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 处理请求前的逻辑
        if hasattr(request, 'user') and request.user.is_authenticated:
            # 检查是否需要更新最后登录时间
            now = timezone.now()
            
            # 如果用户没有last_login或者last_login超过更新间隔，则更新
            if (not request.user.last_login or 
                now - request.user.last_login > self.UPDATE_INTERVAL):
                
                # 使用update()方法而不是save()来避免触发其他信号和更新updated_at字段
                User.objects.filter(id=request.user.id).update(last_login=now)
                
                # 同时更新request.user对象，以便在同一请求中使用
                request.user.last_login = now
        
        # 处理请求
        response = self.get_response(request)
        
        # 可以在这里添加响应后的逻辑
        
        return response