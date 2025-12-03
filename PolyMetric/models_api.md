## 一、数据库设计

### 1. Model 模型（大模型信息表）

```python
# apps/models/models.py

from django.db import models

class Model(models.Model):
    """大模型信息"""
    name = models.CharField(max_length=100, verbose_name='模型名称')
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name='所属公司')
    category = models.CharField(
        max_length=20,
        choices=[
            ('text', '文本生成'),
            ('image', '图像生成'),
            ('multimodal', '多模态'),
            ('code', '代码生成'),
        ],
        default='text',
        verbose_name='类型'
    )
    parameter_size = models.CharField(max_length=50, blank=True, null=True, verbose_name='参数量')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name='版本')
    release_date = models.DateField(blank=True, null=True, verbose_name='发布日期')
    official_url = models.URLField(blank=True, null=True, verbose_name='官方链接')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'models_model'
        verbose_name = '大模型'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ModelFollow(models.Model):
    """模型关注关系"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='followed_models',
        verbose_name='用户'
    )
    model = models.ForeignKey(
        'Model',
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='模型'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        db_table = 'models_modelfollow'
        verbose_name = '模型关注'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'model')  # 防止重复关注
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 关注 {self.model.name}"
```

---

## 二、API 接口定义

### 1. 获取模型列表（带关注状态）

**请求**
```
GET /api/models/?with_follow=true
Authorization: Bearer <token>  (可选，未登录时 is_followed 恒为 false)
```

**可选查询参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| with_follow | string | "true" 时返回 is_followed 字段 |


**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "GPT-4",
      "company": "OpenAI",
      "category": "text",
      "parameter_size": "1.8T",
      "description": "最先进的大语言模型",
      "version": "4.0",
      "release_date": "2023-03-14",
      "official_url": "https://openai.com/gpt-4",
      "is_followed": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z"
    },
    {
      "id": 2,
      "name": "Claude 3",
      "company": "Anthropic",
      "category": "text",
      "parameter_size": "未知",
      "description": "安全可控的AI助手",
      "version": "3.0",
      "release_date": "2024-03-04",
      "official_url": "https://anthropic.com/claude",
      "is_followed": false,
      "created_at": "2024-01-12T10:00:00Z",
      "updated_at": "2024-01-12T10:00:00Z"
    }
  ]
}
```

---

### 2. 获取模型详情

**请求**
```
GET /api/models/{id}/
Authorization: Bearer <token>  (可选)
```

**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 1,
    "name": "GPT-4",
    "company": "OpenAI",
    "category": "text",
    "parameter_size": "1.8T",
    "description": "最先进的大语言模型，具有强大的推理和创造能力",
    "version": "4.0",
    "release_date": "2023-03-14",
    "official_url": "https://openai.com/gpt-4",
    "created_at": "2024-01-10T08:00:00Z",
    "updated_at": "2024-01-10T08:00:00Z"
  }
}
```

**响应 - 模型不存在（404 Not Found）**
```json
{
  "code": 404,
  "msg": "模型不存在",
  "data": null
}
```

---

### 3. 关注模型

**请求**
```
POST /api/models/{id}/follow/
Authorization: Bearer <token>
```

**响应 - 成功（201 Created）**
```json
{
  "code": 201,
  "msg": "关注成功",
  "data": {
    "id": 1,
    "model_id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**响应 - 已关注（200 OK）**
```json
{
  "code": 200,
  "msg": "已关注该模型",
  "data": null
}
```

**响应 - 未登录（401 Unauthorized）**
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

---

### 4. 取消关注模型

**请求**
```
DELETE /api/models/{id}/follow/
Authorization: Bearer <token>
```

**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "已取消关注",
  "data": null
}
```

**响应 - 未关注（404 Not Found）**
```json
{
  "code": 404,
  "msg": "未关注该模型",
  "data": null
}
```

---

### 5. 获取当前用户关注的模型列表

**请求**
```
GET /api/models/followed/
Authorization: Bearer <token>
```

**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "GPT-4",
      "company": "OpenAI",
      "category": "text",
      "parameter_size": "1.8T",
      "description": "最先进的大语言模型",
      "version": "4.0",
      "release_date": "2023-03-14",
      "official_url": "https://openai.com/gpt-4",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z",
      "followed_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

> 
## 前端已完成的对接

### 1. API 调用（src/api/models.js）
```javascript
// 获取所有模型（带关注状态）
export function getAllModels(params = {}) {
  return request.get("/api/models/", { 
    params: { ...params, with_follow: true } 
  })
}

// 获取模型详情
export function getModelDetail(id) {
  return request.get("/api/models/" + id + "/")
}

// 关注模型
export function followModel(id) {
  return request.post("/api/models/" + id + "/follow/")
}

// 取消关注模型
export function unfollowModel(id) {
  return request.delete("/api/models/" + id + "/follow/")
}

// 获取用户关注的模型列表
export function getFollowedModels() {
  return request.get("/api/models/followed/")
}
```