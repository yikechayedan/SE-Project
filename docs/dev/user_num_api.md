  基于当前项目的后端代码（Django + SimpleJWT），以下是在线人数统计接口的实现思路和API文档。

  1. 核心实现思路

  目前 User 模型继承自 AbstractUser，自带一个 last_login（最后登录时间）字段。

  实现方案：基于“时间窗口”推算
  我们定义：如果在过去 15 分钟内有“登录”或“活跃”记录，就视为在线。

  方案 A：最简方案（当前代码直接可用）
  利用现有的 last_login 字段。
   * 逻辑：在线人数 = 数据库中 last_login 时间在 (当前时间 - 15分钟) 之后的用户数量。
   * 优点：不需要修改数据库模型，不需要加 Redis，不需要写中间件。
   * 缺点：last_login 默认只在用户获取 Token（登录）时更新。如果用户登录后一直用同一个 Token 操作了 1 个小时，last_login 还是 1 小时前的，他会被算作“离线”。
   * 适用性：作为初期的近似统计足够了。

  ---

  2. API 接口文档

    需要将这份文档交给后端开发人员，让他们照此实现（推荐先用 方案 A 快速上线）。

  接口信息
   * 名称: 获取用户统计数据
   * URL: /api/users/stats/
   * 方法: GET
   * 权限: 建议开放 (AllowAny) 或 仅登录用户 (IsAuthenticated)

  请求参数
  无

  响应体 (Response Body)

   1 {
   2     "code": 200,
   3     "msg": "success",
   4     "data": {
   5         "total_users": 128,       // 数据库总用户数
   6         "online_users": 15        // 过去 15 分钟内的活跃/登录用户数
   7     }
   8 }

  ---

  3. 后端代码实现参考（Python / Django）

  后端开发人员只需要在 apps/users/views.py 中添加如下代码：

    1 from rest_framework.decorators import api_view, permission_classes
    2 from rest_framework.permissions import AllowAny
    3 from rest_framework.response import Response
    4 from django.contrib.auth import get_user_model
    5 from django.utils import timezone
    6 from datetime import timedelta
    7 
    8 User = get_user_model()
    9 
   10 @api_view(['GET'])
   11 @permission_classes([AllowAny])
   12 def user_stats(request):
   13     """
   14     统计用户总数和近期活跃用户数
   15     """
   16     # 1. 统计总数
   17     total_count = User.objects.count()
   18     
   19     # 2. 统计在线（近似值）：过去 15 分钟内有过登录行为的用户
   20     # 注意：这依赖于 last_login 字段。
   21     # 如果想统计"活跃"，需要在中间件中频繁更新 last_login 或使用 Redis。
   22     time_threshold = timezone.now() - timedelta(minutes=15)
   23     online_count = User.objects.filter(last_login__gte=time_threshold).count()
   24 
   25     # 兜底：如果当前有人调用这个接口，说明至少有1人在线
   26     if online_count == 0 and request.user.is_authenticated:
   27         online_count = 1
   28 
   29     return Response({
   30         "code": 200,
   31         "msg": "success",
   32         "data": {
   33             "total_users": total_count,
   34             "online_users": online_count
   35         }
   36     })

  并在 apps/users/urls.py 中注册：

   1 path('stats/', views.user_stats, name='user_stats'),