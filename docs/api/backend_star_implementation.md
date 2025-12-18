# 后端点赞功能 (Star) 最终实施方案

## 1. 核心设计原则

*   **通用性**: 使用 `ContentType` 实现一个通用的点赞表 (`UserStar`)，同时支持模型 (`My_Model`) 和数据集 (`Dataset`)，以及未来可能的其他资源。
*   **数据一致性**: 利用数据库唯一约束防止重复点赞。
*   **接口规范**: 统一使用 RESTful 风格，集成到现有的 `ViewSet` 中。

---

## 2. 数据库建模

建议在 `users` app 下（或新建 `interactions` app）创建模型：

```python
# apps/users/models.py (或其他位置)
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class UserStar(models.Model):
    """
    通用用户点赞表
    支持对任意模型（Model, Dataset, Article...）进行点赞
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='stars',
        verbose_name='用户'
    )
    
    # 通用外键配置
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        verbose_name = '用户点赞'
        verbose_name_plural = verbose_name
        # 核心约束：一个用户对同一个对象只能点赞一次
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            # 优化查询：按对象类型和ID查找（用于统计总数）
            models.Index(fields=["content_type", "object_id"]),
            # 优化查询：按用户查找（用于"我的点赞"）
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} starred {self.content_type} {self.object_id}"
```

---

## 3. 序列化器 (Serializers) 修改

需要在 `My_Model` 和 `Dataset` 的序列化器中动态添加 `star_count` 和 `is_starred` 字段。

**示例：修改 `apps/models/serializers.py`**

```python
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar # 假设放在这里

class ModelListSerializer(serializers.ModelSerializer):
    # ... 原有字段 ...
    
    # 1. 统计总数
    star_count = serializers.SerializerMethodField()
    # 2. 当前用户状态
    is_starred = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        # 简单实现：实时查询（数据量大时建议增加冗余字段或缓存）
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_is_starred(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(user=user, content_type=ct, object_id=obj.id).exists()
        
    class Meta:
        model = My_Model
        fields = [..., 'star_count', 'is_starred']
```
*(Dataset 序列化器同理修改)*

---

## 4. 视图层 (Views) 实现

编写一个通用的 Mixin 或者直接在各自的 `ViewSet` 中添加 `action`。以下是在 `ModelViewSet` 中的实现范例（`DatasetViewSet` 逻辑完全一致，只需更换 QuerySet）。

**文件：`apps/models/views.py`**

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar

class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    # ... 原有代码 ...

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def star(self, request, pk=None):
        """
        点赞/取消点赞接口
        POST   /api/models/{id}/star/ -> 点赞
        DELETE /api/models/{id}/star/ -> 取消点赞
        """
        obj = self.get_object() # 获取具体的模型实例
        content_type = ContentType.objects.get_for_model(obj)
        user = request.user

        # ====== 1. 点赞逻辑 (POST) ======
        if request.method == 'POST':
            # get_or_create 自动处理去重
            _, created = UserStar.objects.get_or_create(
                user=user,
                content_type=content_type,
                object_id=obj.id
            )
            msg = "点赞成功" if created else "已点赞"
            status_code = 201 if created else 200

        # ====== 2. 取消点赞逻辑 (DELETE) ======
        elif request.method == 'DELETE':
            deleted_count, _ = UserStar.objects.filter(
                user=user,
                content_type=content_type,
                object_id=obj.id
            ).delete()
            msg = "已取消点赞" if deleted_count > 0 else "未曾点赞"
            status_code = 200

        # ====== 3. 返回最新统计数据 ======
        # 前端需要这两个字段来更新 UI
        current_count = UserStar.objects.filter(
            content_type=content_type, 
            object_id=obj.id
        ).count()
        
        # 判断当前状态（POST肯定是True, DELETE肯定是False）
        is_starred = True if request.method == 'POST' else False

        return Response({
            "code": status_code,
            "msg": msg,
            "data": {
                "star_count": current_count,
                "is_starred": is_starred
            }
        })
```

---

## 5. API 接口汇总

| 资源类型 | 动作 | 方法 | URL | 权限 |
| :--- | :--- | :--- | :--- | :--- |
| **模型** | 点赞 | POST | `/api/models/{id}/star/` | 登录 |
| **模型** | 取消 | DELETE | `/api/models/{id}/star/` | 登录 |
| **数据集** | 点赞 | POST | `/api/datasets/{id}/star/` | 登录 |
| **数据集** | 取消 | DELETE | `/api/datasets/{id}/star/` | 登录 |

**请求体:** 空 (`{}`)
**响应体:**
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "star_count": 105,
        "is_starred": true
    }
}
```
