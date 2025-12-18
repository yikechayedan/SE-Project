API D1：获取数据集列表

GET /api/datasets/
权限：

未登录：仅返回公开数据集

已登录：返回公开数据集 + 自己创建的数据集

Query Params（可选）
参数	说明
category	数据集类型（objective / subjective / adversarial）
creator	创建者用户 ID
Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "MMLU",
      "description": "多学科客观题评测数据集",
      "category": "objective",
      "file_format": "json",
      "sample_count": 115000,
      "creator": {
        "id": 1,
        "username": "shadow"
      },
      "is_public": true,
      "is_verified": true,
      "created_at": "2025-12-01T10:00:00"
    }
  ]
}

API D2：获取数据集详情

GET /api/datasets/{id}/
权限：

公开数据集：所有人可访问

私有数据集：仅创建者可访问

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 1,
    "name": "MMLU",
    "description": "多学科客观题评测数据集",
    "category": "objective",
    "file_format": "json",
    "sample_count": 115000,
    "creator": {
      "id": 1,
      "username": "shadow"
    },
    "is_public": true,
    "is_verified": true,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-05T12:00:00"
  }
}

API D3：上传数据集

POST /api/datasets/
权限：已登录
Content-Type：multipart/form-data

Form Data
字段	类型	说明
file	File	数据集文件（json / csv）
name	string	数据集名称
description	string	数据集描述
category	string	objective / subjective / adversarial
is_public	boolean	是否公开
Response（201）
{
  "code": 201,
  "msg": "数据集上传成功",
  "data": {
    "id": 5,
    "name": "Test Dataset",
    "category": "objective",
    "sample_count": 100,
    "is_public": true
  }
}

API D4：更新数据集信息

PUT / PATCH /api/datasets/{id}/
权限：仅创建者

Request Body（示例）
{
  "description": "更新后的数据集描述",
  "is_public": false
}

API D5：删除数据集

DELETE /api/datasets/{id}/
权限：仅创建者

Response
{
  "code": 200,
  "msg": "数据集已删除"
}

API D6：预览数据集内容（样本）

GET /api/datasets/{id}/preview/
权限：

公开数据集：所有人

私有数据集：创建者

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "total": 115000,
    "preview": [
      {
        "question": "1 + 1 = ?",
        "options": ["1", "2", "3", "4"],
        "answer": "2"
      }
    ]
  }
}


📌 仅返回前若干条样本，用于前端快速预览

API D7：下载数据集文件

GET /api/datasets/{id}/download/
权限：

公开数据集：所有人

私有数据集：创建者

Response

文件流（json / csv）

API D8：关注数据集

POST /api/datasets/{id}/follow/
权限：已登录

Response（201）
{
  "code": 201,
  "msg": "关注成功"
}

API D9：取消关注数据集

DELETE /api/datasets/{id}/follow/
权限：已登录

Response
{
  "code": 200,
  "msg": "取消关注成功"
}

API D10：获取我关注的数据集列表

GET /api/datasets/followed/
权限：已登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "MMLU",
      "category": "objective",
      "sample_count": 115000,
      "followed_at": "2025-12-01T10:00:00"
    }
  ]
}

API D11：管理员审核数据集（可选）

POST /api/datasets/{id}/verify/
权限：管理员

Response
{
  "code": 200,
  "msg": "数据集已通过审核"
}