1. 创建数据集
接口: POST /api/datasets/
权限: 需登录（携带 JWT Token）
请求示例（表单提交，支持文件上传）:
json
{
  "name": "猫狗图像分类数据集",
  "description": "包含2000张猫狗标注图片，用于图像分类模型训练",
  "category": "image",  // 可选值：image/text/multimodal
  "file_format": "zip", // 可选值：csv/json/zip
  "is_public": true
}
返回示例:
json
{
  "code": 201,
  "msg": "数据集创建成功",
  "data": {
    "id": 1,
    "name": "猫狗图像分类数据集",
    "description": "包含2000张猫狗标注图片，用于图像分类模型训练",
    "category": "image",
    "file_format": "zip",
    "file_size": 128.5,  // 单位：MB（自动计算）
    "is_public": true,
    "is_verified": false, // 初始未审核
    "creator_id": 1,
    "creator_username": "testuser",
    "file_url": "http://example.com/media/datasets/20251130/猫狗分类数据集.zip",
    "created_at": "2025-11-30T14:23:45Z",
    "updated_at": "2025-11-30T14:23:45Z"
  }
}
2. 获取数据集列表
接口: GET /api/datasets/
权限:
未登录用户：仅返回 is_public=true 且 is_verified=true 的数据集
登录用户：返回自身创建的所有数据集 + 公开已审核数据集
管理员：返回所有数据集（含未审核 / 私有）
查询参数（可选）:
category: 按类型筛选（如 category=image）
search: 搜索名称 / 描述（如 search=分类）
ordering: 排序（如 ordering=-created_at 按创建时间倒序）
返回示例:
json
{
  "code": 200,
  "msg": "数据集列表查询成功",
  "data": [
    {
      "id": 1,
      "name": "猫狗图像分类数据集",
      "description": "包含2000张猫狗标注图片，用于图像分类模型训练",
      "category": "image",
      "file_format": "zip",
      "file_size": 128.5,
      "is_public": true,
      "is_verified": true,
      "creator_id": 1,
      "creator_username": "testuser",
      "created_at": "2025-11-30T14:23:45Z",
      "file_url": "http://example.com/media/datasets/20251130/猫狗分类数据集.zip"
    },
    {
      "id": 2,
      "name": "新闻文本情感分析数据集",
      "description": "5000条新闻文本及情感标签（正面/负面）",
      "category": "text",
      "file_format": "csv",
      "file_size": 8.2,
      "is_public": true,
      "is_verified": true,
      "creator_id": 2,
      "creator_username": "admin",
      "created_at": "2025-11-29T09:15:30Z",
      "file_url": "http://example.com/media/datasets/20251129/新闻情感数据集.csv"
    }
  ]
}
3. 获取数据集详情
接口: GET /api/datasets/{id}/
权限: 同列表接口权限规则
返回示例:
json
{
  "code": 200,
  "msg": "数据集详情查询成功",
  "data": {
    "id": 1,
    "name": "猫狗图像分类数据集",
    "description": "包含2000张猫狗标注图片，用于图像分类模型训练",
    "category": "image",
    "file_format": "zip",
    "file_size": 128.5,
    "is_public": true,
    "is_verified": true,
    "creator_id": 1,
    "creator_username": "testuser",
    "file_url": "http://example.com/media/datasets/20251130/猫狗分类数据集.zip",
    "created_at": "2025-11-30T14:23:45Z",
    "updated_at": "2025-11-30T16:40:22Z"
  }
}
4. 更新数据集信息
接口: PATCH /api/datasets/{id}/
权限: 仅数据集创建者或管理员
请求示例（部分字段更新）:
json
{
  "name": "猫狗图像分类数据集（V2）",
  "description": "包含2500张猫狗标注图片（新增500张），用于图像分类模型训练",
  "is_public": false
}
返回示例:
json
{
  "code": 200,
  "msg": "数据集更新成功",
  "data": {
    "id": 1,
    "name": "猫狗图像分类数据集（V2）",
    "description": "包含2500张猫狗标注图片（新增500张），用于图像分类模型训练",
    "category": "image",
    "file_format": "zip",
    "file_size": 128.5,
    "is_public": false,
    "is_verified": true,
    "creator_id": 1,
    "creator_username": "testuser",
    "file_url": "http://example.com/media/datasets/20251130/猫狗分类数据集.zip",
    "created_at": "2025-11-30T14:23:45Z",
    "updated_at": "2025-11-30T17:05:18Z"
  }
}
5. 删除数据集
接口: DELETE /api/datasets/{id}/
权限: 仅数据集创建者或管理员
返回示例:
json
{
  "code": 200,
  "msg": "数据集删除成功"
}
6. 获取我的数据集
接口: GET /api/datasets/my/
权限: 需登录
返回示例:
json
{
  "code": 200,
  "msg": "我的数据集查询成功",
  "data": [
    {
      "id": 1,
      "name": "猫狗图像分类数据集（V2）",
      "description": "包含2500张猫狗标注图片（新增500张），用于图像分类模型训练",
      "category": "image",
      "file_format": "zip",
      "file_size": 128.5,
      "is_public": false,
      "is_verified": true,
      "created_at": "2025-11-30T14:23:45Z",
      "updated_at": "2025-11-30T17:05:18Z",
      "file_url": "http://example.com/media/datasets/20251130/猫狗分类数据集.zip"
    }
  ]
}
7. 下载数据集
接口: GET /api/datasets/{id}/download/
权限:
公开已审核数据集：所有用户可下载
私有 / 未审核数据集：仅创建者或管理员可下载
返回: 成功返回二进制文件流（触发浏览器下载）；权限不足返回如下：
json
{
  "code": 403,
  "msg": "无权限下载该数据集"
}
8. 审核数据集（管理员）
接口: POST /api/datasets/{id}/verify/
权限: 仅管理员
请求示例:
json
{
  "is_verified": true
}
返回示例:
json
{
  "code": 200,
  "msg": "数据集审核通过",
  "data": {
    "id": 1,
    "name": "猫狗图像分类数据集（V2）",
    "is_verified": true,
    "updated_at": "2025-11-30T18:10:05Z"
  }
}