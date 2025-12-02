
### 1. 关注数据集

**请求**
```
POST /api/datasets/{id}/follow/
Authorization: Bearer <token>
```

**响应 - 成功（201 Created）**
```json
{
  "code": 201,
  "msg": "关注成功",
  "data": {
    "id": 1,
    "dataset_id": 5,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**响应 - 已关注（200 OK）**
```json
{
  "code": 200,
  "msg": "已关注该数据集",
  "data": null
}
```

**响应 - 失败（401 Unauthorized）**
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

**响应 - 数据集不存在（404 Not Found）**
```json
{
  "code": 404,
  "msg": "数据集不存在",
  "data": null
}
```

---

### 2. 取消关注数据集

**请求**
```
DELETE /api/datasets/{id}/follow/
Authorization: Bearer <token>
```

**响应 - 成功（200 OK / 204 No Content）**
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
  "msg": "未关注该数据集",
  "data": null
}
```

---

### 3. 获取当前用户关注的数据集列表

**请求**
```
GET /api/datasets/followed/
Authorization: Bearer <token>
```

**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 5,
      "name": "ImageNet-1K",
      "description": "大规模图像分类数据集",
      "category": "image",
      "file_format": "zip",
      "file_size": 150.5,
      "creator_id": 2,
      "creator_username": "alice",
      "is_verified": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z",
      "followed_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 8,
      "name": "COCO-2017",
      "description": "目标检测数据集",
      "category": "image",
      "file_format": "zip",
      "file_size": 80.2,
      "creator_id": 3,
      "creator_username": "bob",
      "is_verified": true,
      "created_at": "2024-01-12T09:00:00Z",
      "updated_at": "2024-01-12T09:00:00Z",
      "followed_at": "2024-01-14T15:20:00Z"
    }
  ]
}
```

> **注意**：返回的每个数据集对象应包含 `followed_at` 字段，表示用户关注该数据集的时间。

---

### 4. 获取数据集列表（带关注状态，前端多传了一个with_follow=true参数，在原有接口加上对此的处理）

**请求**
```
GET /api/datasets/?with_follow=true
Authorization: Bearer <token>  (可选，未登录时 is_followed 恒为 false)
```

**响应 - 成功（200 OK）**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 5,
      "name": "ImageNet-1K",
      "description": "大规模图像分类数据集",
      "category": "image",
      "file_format": "zip",
      "file_size": 150.5,
      "creator_id": 2,
      "creator_username": "alice",
      "is_verified": true,
      "is_followed": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z"
    },
    {
      "id": 6,
      "name": "SQUAD-v2",
      "description": "问答数据集",
      "category": "text",
      "file_format": "json",
      "file_size": 12.3,
      "creator_id": 4,
      "creator_username": "carol",
      "is_verified": true,
      "is_followed": false,
      "created_at": "2024-01-11T10:00:00Z",
      "updated_at": "2024-01-11T10:00:00Z"
    }
  ]
}
```

