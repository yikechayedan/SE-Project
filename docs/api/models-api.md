API M1：获取模型列表（模型广场）

GET /api/models/
权限：无需登录

Query Params（可选）
参数	说明
category	模型类型（chat / reasoning / vl / embedding / code）
company	模型提供方（DeepSeek / 阿里 / 智谱 等）
Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "DeepSeek-V3-250324",
      "company": "DeepSeek",
      "category": "chat",
      "parameter_size": "≈671B (MoE)",
      "version": "V3",
      "release_date": "2024-03-24",
      "is_followed": false
    }
  ]
}


📌 is_followed：仅在已登录状态下返回，用于前端展示关注状态

API M2：获取模型详情

GET /api/models/{id}/
权限：无需登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 1,
    "name": "DeepSeek-V3-250324",
    "company": "DeepSeek",
    "category": "chat",
    "parameter_size": "≈671B (MoE)",
    "version": "V3",
    "release_date": "2024-03-24",
    "description": "DeepSeek 主力通用大模型，具备较强推理能力",
    "official_url": "https://www.deepseek.com",
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-05T12:00:00"
  }
}

API M3：关注模型

POST /api/models/{id}/follow/
权限：已登录

Response（201）
{
  "code": 201,
  "msg": "关注成功",
  "data": null
}

API M4：取消关注模型

DELETE /api/models/{id}/follow/
权限：已登录

Response
{
  "code": 200,
  "msg": "取消关注成功",
  "data": null
}

API M5：获取我关注的模型列表

GET /api/models/followed/
权限：已登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "DeepSeek-V3-250324",
      "company": "DeepSeek",
      "category": "chat",
      "parameter_size": "≈671B (MoE)",
      "followed_at": "2025-12-01T10:00:00"
    }
  ]
}

API M6：管理员新增模型（仅后台）

POST /api/models/
权限：管理员

📌 说明
普通用户不能新增模型；
平台支持的模型由管理员统一维护，
符合“模型集中管理”的设计原则。

Request Body
{
  "name": "Qwen3-30B-A3B-Instruct-2507",
  "company": "Alibaba",
  "category": "chat",
  "parameter_size": "30B",
  "version": "Qwen3",
  "release_date": "2024-07-01",
  "description": "高性价比指令模型",
  "official_url": "https://modelscope.cn"
}

Response（201）
{
  "code": 201,
  "msg": "模型创建成功",
  "data": {
    "id": 5,
    "name": "Qwen3-30B-A3B-Instruct-2507"
  }
}

API M7：管理员更新模型信息

PUT / PATCH /api/models/{id}/
权限：管理员

API M8：管理员删除模型

DELETE /api/models/{id}/
权限：管理员