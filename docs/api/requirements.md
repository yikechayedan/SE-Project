# 核心思路：
# 1. 模型/数据集关注已有中间表，只需扩展现有 API 支持查询他人数据
# 2. 新建用户关注用户的中间表
# 3. 数据集 API 需要返回 creator_id 字段


# 在 DatasetSerializer 中添加 creator_id 字段：
```python
# apps/datasets/serializers.py
class DatasetSerializer(serializers.ModelSerializer):
    creator_id = serializers.IntegerField(source='creator.id', read_only=True)
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    # ... 其他字段
```

# GET /api/datasets/ 和 GET /api/datasets/{id}/ 返回的数据需包含:
{
  "id": 1,
  "name": "数据集名称",
  "creator_id": 5,            // 新增！
  "creator_username": "张三",
  // ... 其他字段
}


------------------------------------------
获取关注的模型列表（已有 API 扩展）
------------------------------------------
GET /api/models/followed/
GET /api/models/followed/?user_id=5

# 后端修改：在现有 view 中加个 user_id 参数

```python
# apps/models/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followed_models(request):
    user_id = request.query_params.get('user_id')
    
    if user_id:
        # 查询他人的关注列表
        target_user = User.objects.get(id=user_id)
        # 检查隐私设置
        if target_user != request.user and not target_user.show_followed_models:
            return Response({"code": 200, "msg": "该用户未公开关注的模型", "data": None})
        follows = ModelFollow.objects.filter(user=target_user)
    else:
        # 查询自己的关注列表
        follows = ModelFollow.objects.filter(user=request.user)
    
    # ... 返回关注的模型列表
```


------------------------------------------
获取关注的数据集列表（已有 API 扩展）
------------------------------------------
GET /api/datasets/followed/
GET /api/datasets/followed/?user_id=5

# 同上，在现有 view 中加 user_id 参数支持


------------------------------------------
【新增】User 模型新增隐私字段
------------------------------------------

```python
# apps/users/models.py
class User(AbstractUser):
    # ... 现有字段 ...
    
    # 隐私设置
    show_followed_models = models.BooleanField(default=True, verbose_name="公开关注的模型")
    show_followed_datasets = models.BooleanField(default=True, verbose_name="公开关注的数据集")
```

# 然后迁移：
# python manage.py makemigrations users
# python manage.py migrate


------------------------------------------
【新增】UserFollow 用户关注关系模型
------------------------------------------

```python
# apps/users/models.py
class UserFollow(models.Model):
    """用户关注关系"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        verbose_name='关注者'
    )
    followed = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name='被关注者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} -> {self.followed.username}"
```




API 1: 获取用户公开信息

GET /api/users/{id}/public/

# userId 来源：数据集 API 返回的 creator_id 字段
# 例如：用户点击上传者名字 → row.creator_id = 5 → 调用 /api/users/5/public/

请求头:
{
  "Authorization": "Bearer <access_token>"  (可选)
}

成功响应 (200):
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 5,
    "username": "张三",
    "email": "zhangsan@example.com",
    "avatar": "http://localhost:8000/media/avatars/user5.jpg",
    "bio": "热爱AI和数据科学",
    "is_followed": true,               // 当前登录用户是否已关注（未登录返回 false）
    "show_followed_models": true,      // 是否公开模型关注列表
    "show_followed_datasets": false,   // 是否公开数据集关注列表
    "followers_count": 120,
    "following_count": 45
  }
}



API 2: 关注用户

POST /api/users/{id}/follow/

请求头:
{
  "Authorization": "Bearer <access_token>"  (必填)
}

成功响应 (201):
{
  "code": 201,
  "msg": "关注成功",
  "data": null
}

失败响应 (400):
{
  "code": 400,
  "msg": "不能关注自己" / "已关注该用户",
  "data": null
}



API 3: 取消关注用户

DELETE /api/users/{id}/follow/

请求头:
{
  "Authorization": "Bearer <access_token>"  (必填)
}

成功响应 (200):
{
  "code": 200,
  "msg": "已取消关注",
  "data": null
}


API 4: 获取当前用户关注的用户列表

GET /api/users/followed/

请求头:
{
  "Authorization": "Bearer <access_token>"  (必填)
}

成功响应 (200):
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 5,
      "username": "张三",
      "avatar": "...",
      "bio": "...",
      "show_followed_models": true,
      "show_followed_datasets": true,
      "followed_at": "2025-06-01T10:00:00Z"
    }
  ]
}


API 5: 更新隐私设置

PUT /api/users/privacy/

请求头:
{
  "Authorization": "Bearer <access_token>"  (必填)
}

请求体:
{
  "show_followed_models": true,
  "show_followed_datasets": false
}

成功响应 (200):
{
  "code": 200,
  "msg": "设置已更新",
  "data": {
    "show_followed_models": true,
    "show_followed_datasets": false
  }
}



API 6: /api/users/me/ 返回隐私设置


# 在现有 UserSerializer 中添加这两个字段
GET /api/users/me/ 返回:
{
  "id": 1,
  "username": "...",
  "email": "...",
  "avatar": "...",
  "bio": "...",
  "show_followed_models": true,      // 新增
  "show_followed_datasets": true     // 新增
}




==========================================
首页统计与动态所需 API（2024-12-11 新增）
==========================================

目前首页使用以下现有 API 获取统计数据：
- GET /api/models/        → 模型总数
- GET /api/datasets/      → 数据集总数  
- GET /api/tasks/evaluation-tasks/  → 评测任务总数

【待实现】用户统计 API
------------------------------------------
GET /api/users/stats/

请求头:
{
  "Authorization": "Bearer <access_token>"  (可选)
}

成功响应 (200):
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "total_users": 156,      // 总用户数
    "active_users": 89       // 活跃用户数（7天内有操作）
  }
}


【待实现】平台统计汇总 API（建议合并为一个接口）
------------------------------------------
GET /api/stats/overview/

成功响应 (200):
{
  "code": 200,
  "msg": "查询成功", 
  "data": {
    "model_count": 12,       // 模型总数
    "dataset_count": 8,      // 数据集总数
    "task_count": 156,       // 评测任务总数
    "user_count": 89,        // 活跃用户数
    "completed_tasks": 120   // 已完成评测数
  }
}

说明：这个 API 可以减少前端多次请求，提升首页加载速度


【待实现】最新动态 API（可选，推荐）
------------------------------------------
GET /api/activities/recent/

请求参数:
- limit: 返回条数，默认 10

成功响应 (200):
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "type": "task_completed",      // task_created, task_completed, dataset_added, model_added
      "content": "评测任务「GPT-4 vs Claude」已完成",
      "user": "张三",                // 操作用户（可选）
      "created_at": "2024-12-11T10:30:00Z"
    },
    {
      "type": "dataset_added",
      "content": "新增数据集「中文逻辑推理v2」",
      "user": "李四",
      "created_at": "2024-12-11T09:00:00Z"
    }
  ]
}

说明：目前前端通过分别请求任务、数据集、模型列表来组装动态，
      如果后端实现此 API 可以简化逻辑并支持更丰富的动态类型


==========================================
当前首页实现说明（前端已完成）
==========================================

1. 统计数据获取：
   - 模型总数：调用 getAllModels() → /api/models/
   - 数据集总数：调用 getAllDatasets() → /api/datasets/
   - 任务总数：调用 getEvaluationTasks() → /api/tasks/evaluation-tasks/
   - 用户数：暂时使用估算值（模型+数据集数量）

2. 最新动态：
   - 从任务、数据集、模型列表中各取前几条
   - 按时间排序合并展示
   - 显示相对时间（x分钟前、x小时前等）

3. 发起评测按钮：
   - 点击后跳转到 /evaluation 页面
   - 不再弹出对话框

