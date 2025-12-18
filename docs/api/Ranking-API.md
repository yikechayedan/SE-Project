API R1：更新模型排名（管理员）

POST /api/rankings/update/
权限：管理员（IsAdminUser）

📌 说明
根据指定数据集的评测结果，
自动计算该数据集下所有模型的最新排名，并记录历史变化。

Request Body
{
  "dataset_id": 1
}

Response（成功）
{
  "success": true,
  "message": "Updated rankings for dataset MMLU",
  "dataset": "MMLU",
  "total_models": 5
}

Response（失败）
{
  "error": "No evaluation results found for dataset MMLU"
}

API R2：获取指定数据集的模型排行榜（Top Models）

GET /api/rankings/top/
权限：无需登录

Query Params
参数	类型	说明
dataset_id	int	数据集 ID（必填）
limit	int	返回数量，默认 10
示例请求
GET /api/rankings/top/?dataset_id=1&limit=10

Response
{
  "code": 200,
  "data": [
    {
      "rank": 1,
      "model_id": 3,
      "model_name": "DeepSeek-V3-250324",
      "company": "DeepSeek",
      "score": 0.87,
      "previous_rank": 2,
      "rank_change": 1
    },
    {
      "rank": 2,
      "model_id": 5,
      "model_name": "GLM-4-Plus",
      "company": "Zhipu",
      "score": 0.83,
      "previous_rank": 1,
      "rank_change": -1
    }
  ]
}

字段说明
字段	说明
rank	当前排名
previous_rank	上一次排名
rank_change	排名变化（正数表示上升）
score	评测得分
API R3：获取模型排名历史

GET /api/rankings/history/{model_id}/
权限：无需登录

Query Params（可选）
参数	说明
dataset_id	指定数据集，只返回该数据集下的历史
示例请求
GET /api/rankings/history/3/?dataset_id=1

Response
{
  "code": 200,
  "data": [
    {
      "rank": 1,
      "score": 0.87,
      "dataset_name": "MMLU",
      "recorded_at": "2025-12-12T10:30:00"
    },
    {
      "rank": 2,
      "score": 0.82,
      "dataset_name": "MMLU",
      "recorded_at": "2025-12-10T09:15:00"
    }
  ]