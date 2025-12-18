一、评测任务（EvaluationTask）
API T1：创建评测任务

POST /api/tasks/evaluation-tasks/
权限：已登录

Request Body
{
  "dataset": 1,
  "myModel": 2,
  "method": "objective"
}

字段说明
字段	说明
dataset	数据集 ID（来自 /api/datasets/）
myModel	模型 ID（来自 /api/models/）
method	评测类型：objective / subjective / adversarial
Response（201）
{
  "code": 201,
  "msg": "评测任务创建成功",
  "data": {
    "task_id": 10,
    "status": "pending"
  }
}

API T2：获取评测任务列表（我的任务）

GET /api/tasks/evaluation-tasks/
权限：已登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 10,
      "dataset": {
        "id": 1,
        "name": "MMLU"
      },
      "model": {
        "id": 2,
        "name": "DeepSeek-V3-250324"
      },
      "method": "objective",
      "status": "finished",
      "created_at": "2025-12-10T10:00:00"
    }
  ]
}

API T3：获取评测任务详情

GET /api/tasks/evaluation-tasks/{id}/
权限：

创建者

或管理员

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 10,
    "dataset": {
      "id": 1,
      "name": "MMLU"
    },
    "model": {
      "id": 2,
      "name": "DeepSeek-V3-250324"
    },
    "method": "objective",
    "status": "finished",
    "created_at": "2025-12-10T10:00:00",
    "finished_at": "2025-12-10T10:05:00"
  }
}

二、任务执行
API T4：启动评测任务

POST /api/tasks/run-task/
权限：已登录

📌 说明
该接口触发后台评测逻辑（可同步 / Celery 异步），
实际评测过程由系统自动完成。

Request Body
{
  "task_id": 10
}

Response
{
  "code": 200,
  "msg": "任务已开始执行",
  "data": {
    "task_id": 10,
    "status": "running"
  }
}

三、评测条目（EvaluationItem）
API T5：获取评测条目列表

GET /api/tasks/evaluation-items/
权限：创建者

Query Params
参数	说明
task	评测任务 ID
Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 101,
      "content": "1 + 1 = ?",
      "correct_answer": "2",
      "predicted_answer": "2",
      "is_correct": true
    }
  ]
}

API T6：获取单个评测条目详情

POST /api/tasks/get-item-detail/
权限：创建者

Request Body
{
  "task": 10,
  "itemID": 101
}

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 101,
    "content": "1 + 1 = ?",
    "correct_answer": "2",
    "predicted_answer": "2",
    "is_correct": true
  }
}

四、评测结果与汇总（EvaluationSummary）
API T7：获取评测结果汇总

GET /api/tasks/evaluation-summary/{task_id}/
权限：创建者

Response（Objective 示例）
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "task_id": 10,
    "model": "DeepSeek-V3-250324",
    "dataset": "MMLU",
    "method": "objective",
    "total": 100,
    "correct": 87,
    "accuracy": 0.87
  }
}

Subjective 示例
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "task_id": 11,
    "model": "GLM-4-Plus",
    "dataset": "Subjective-Test",
    "average_score": 8.4,
    "summary": "模型整体表现良好，在逻辑与表达方面得分较高"
  }
}

五、Benchmark（多模型评测）
API T8：运行 Benchmark

POST /api/tasks/benchmark/
权限：已登录

Request Body
{
  "dataset_id": 1,
  "model_ids": [1, 2, 3]
}

Response
{
  "code": 200,
  "msg": "Benchmark 已启动",
  "data": [
    {
      "task_id": 20,
      "model": "DeepSeek-V3-250324"
    },
    {
      "task_id": 21,
      "model": "GLM-4-Plus"
    }
  ]
}