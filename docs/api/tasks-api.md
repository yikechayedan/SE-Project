二、完整 API 说明（对齐用户接口格式）
1. 新建评测任务
接口：POST /api/tasks/evaluation-tasks/
权限：登录用户
请求示例：
json
{
  "name": "GPT-4V 图像分类评测",
  "description": "使用 COCO 数据集测试 GPT-4V 的图像分类能力",
  "method": "objective"
  "myModel": 1 //使用模型的ID（主观/客观测评必填）
  "dataset": 1  // 关联数据集的 ID（必填）
}
成功返回（201 Created）：
json
{
  "id": 1,
  "name": "GPT-4V 图像分类评测",
  "description": "使用 COCO 数据集测试 GPT-4V 的图像分类能力",
  "creator": 1,
  "creator_username": "testuser",
  "dataset": 1,
  "dataset_name": "COCO 2017",
  "method": "objective",
  "myModel": 1,
  "myModel_name": "GPT-4V",
  "status": "pending", //客观评测：进行中和已完成，主观/对抗评测：待测评和已测评
  "accuracy": null, 
  "score": null,
  "created_at": "2025-11-30T10:00:00Z",
  "updated_at": "2025-11-30T10:00:00Z",
  "time_used": null //评测用时
}
失败返回（400 Bad Request）：
json
{
  "error": "{'name': ['该字段为必填项'], 'myModel': ['该字段为必填项'], 'dataset': ['该字段为必填项']}"
}

2. 查看评测任务列表
接口：GET /api/tasks/evaluation-tasks/
权限：登录用户
成功返回（200 OK）：
json
[
  {
    "id": 1,
    "name": "GPT-4V 图像分类评测",
    "description": "使用 COCO 数据集测试 GPT-4V 的图像分类能力",
    "creator": 1,
    "creator_username": "testuser",
    "dataset": 1,
    "dataset_name": "COCO 2017",
    "method": "objective",
    "myModel": 1,
    "myModel_name": "GPT-4V",
    "status": "pending",
    "accuracy": null,
    "score": null,
    "created_at": "2025-11-30T10:00:00Z",
    "updated_at": "2025-11-30T10:00:00Z",
    "time_used": null
  },
  {
    "id": 2,
    "name": "Gemini 文本生成评测",
    "description": "使用 CNN/Daily Mail 数据集测试生成能力",
    "creator": 1,
    "creator_username": "testuser",
    "dataset": 2,
    "dataset_name": "CNN/Daily Mail",
    "method": "subjective",
    "myModel": 1,
    "myModel_name": "GPT-4V",
    "status": "completed",
    "accuracy": 0.89,
    "score": 89,
    "created_at": "2025-11-29T15:30:00Z",
    "updated_at": "2025-11-29T16:45:00Z"
    "time_used": "PT12S"
  }
]

3. 查看单个评测任务详情
接口：GET /api/tasks/evaluation-tasks/{id}/（替换 {id} 为任务 ID）
权限：任务创建者或管理员
成功返回（200 OK）：
json
{
  "id": 1,
  "name": "GPT-4V 图像分类评测",
  "description": "使用 COCO 数据集测试 GPT-4V 的图像分类能力",
  "creator": 1,
  "creator_username": "testuser",
  "dataset": 1,
  "dataset_name": "COCO 2017",
  "method": "objective",
  "myModel": 1,
  "myModel_name": "GPT-4V",
  "status": "pending",
  "accuracy": null,
  "score": null,
  "created_at": "2025-11-30T10:00:00Z",
  "updated_at": "2025-11-30T10:00:00Z",
  "time_used": null,
  "data":{
    [
      "id": 1,
      "content": "1+1=?",
      "correct_answer": "2",
      "predicted_answer": "2",
      "is_correct": 1
    ]
    [
      "id": 1,
      "content": "逻辑题：鸡兔同笼",
      "correct_answer": "C",
      "predicted_answer": "D",
      "is_correct": 0
    ]
  }
}
权限不足返回（403 Forbidden）：
json
{
  "error": "仅任务创建者或管理员可操作此评测任务"
}

4. 编辑评测任务（全量更新）
接口：PUT /api/tasks/evaluation-tasks/{id}/
权限：任务创建者或管理员
请求示例：
json
{
  "name": "GPT-4V 图像分类评测（V2）",
  "description": "使用 COCO 2017 数据集测试 GPT-4V 的图像分类能力（优化版）",
  "method": "objective"
  "myModel": 1 //可修改
  "dataset": 1  // 可保持原数据集，也可修改为其他数据集ID
}
成功返回（200 OK）：
json
{
  "id": 1,
  "name": "GPT-4V 图像分类评测（V2）",
  "description": "使用 COCO 2017 数据集测试 GPT-4V 的图像分类能力（优化版）",
  "creator": 1,
  "creator_username": "testuser",
  "dataset": 1,
  "dataset_name": "COCO 2017",
  "method": "objective",
  "myModel": 1,
  "myModel_name": "GPT-4V",
  "status": "pending",
  "accuracy": null,
  "score": null,
  "created_at": "2025-11-30T10:00:00Z",
  "updated_at": "2025-11-30T11:20:00Z",
  "time_used": null
}

5. 部分更新评测任务
接口：PATCH /api/tasks/evaluation-tasks/{id}/
权限：任务创建者或管理员
请求示例（仅修改名称）：
json
{
  "name": "GPT-4V 图像分类评测（最终版）"
}
成功返回（200 OK）：
json
{
  "id": 1,
  "name": "GPT-4V 图像分类评测（最终版）",
  "description": "使用 COCO 2017 数据集测试 GPT-4V 的图像分类能力（优化版）",
  "creator": 1,
  "creator_username": "testuser",
  "dataset": 1,
  "dataset_name": "COCO 2017",
  "method": "objective",
  "myModel": 1,
  "myModel_name": "GPT-4V",
  "status": "pending",
  "accuracy": null,
  "score": null,
  "created_at": "2025-11-30T10:00:00Z",
  "updated_at": "2025-11-30T11:30:00Z"
  "time_used": null
}

6. 删除评测任务
接口：DELETE /api/tasks/evaluation-tasks/{id}/
权限：任务创建者或管理员
成功返回：204 No Content（无响应体）
失败返回（403 Forbidden）：
json
{
  "error": "仅任务创建者或管理员可操作此评测任务"
}

7.提交主观评测评分（一题一传）
接口：POST /api/tasks/evaluation-tasks/{id}
权限：登录用户
请求示例（json）：
{
  "method":"subjective"
  "myModel":1
  "dataset":1
  "reviewer":1 //测评者id
  "time_stamp": "2025-11-30T10:00:00Z"
  "itemID": 1 //条目id
  "score": 6
}

成功响应（200 OK）：
失败响应（400）：
{
  "error": "Task or Reviewer ID not found, or all items are completed."
}

8.提交对抗评测评分
接口：POST /api/tasks/evaluation-tasks/{id}
权限：登录用户
请求示例（json）：
{
  "method":"subjective"
  "myModel":1
  "dataset":1
  "reviewer":1 //测评者id
  "time_stamp": "2025-11-30T10:00:00Z"
  "itemID": 1 //条目id
  "preference":"left"
}
成功响应（200 OK）：
失败响应（400）：
{
  "error": "Task or Reviewer ID not found, or all items are completed."
}

9.请求待测条目列表（进入页面时调用，用于恢复测评进度）
接口：GET /api/tasks/get-pending-items?{taskid}&{reviewerid}
成功响应（200 OK）
{
  "task":1
  "reviewer":1
  "pending_count":98
  "pengdingItem_ids":[
    "1",
    "2",
    ...
  ]
}

10.请求主观、对抗评测界面条目展示
接口：GET /api/tasks/get-item-detail
请求格式（JSON）
{
  "task": 1
  "itemID": 1
}

成功响应（200）
{
  "method":"subjective"
  "itemID":1
  "item_content":{
    "input_query": "请用一段话解释量子纠缠，并保持幽默风趣的口吻。"
    "myModel1_response": "量子纠缠就像是一对分手的恋人，无论他们相隔多远，只要你踢一下其中一个（测量它的状态），另一个会立刻尖叫（确定它的状态）...",
    "myModel2_response":null //对抗评测下启用
  }
}
