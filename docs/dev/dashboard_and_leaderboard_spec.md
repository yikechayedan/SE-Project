# 仪表盘与排行榜功能后端设计规范

## 1. 概述
本文档详细描述了为了支持首页（LoggedHome）的"实时统计仪表盘"和"动态能力排行榜"功能，后端需要实现的 API 接口、数据模型变更及业务逻辑。

## 2. 核心需求
1.  **全站统计**：提供模型数、数据集数、任务数、用户数（含在线/活跃）的实时统计。
2.  **多维度排行榜**：支持按"综合"、"语言理解"、"推理能力"、"代码能力"、"知识问答"、"安全合规"等维度对模型进行排序。
3.  **动态更新**：当新的评测任务完成时，自动更新模型的各项能力得分和排名。
4.  **趋势追踪**：记录排名的升降趋势。

---

## 3. 数据库建模 (Models)

为了解耦"模型基础信息"与"评测得分"，建议采用独立的评分表，而不是在 `My_Model` 表中无限扩展字段。

### 3.1 新增/修改模型

#### A. 维度定义 (可选，或硬编码)
如果维度相对固定，可以硬编码；如果需要动态扩展，建议新建表。这里推荐**枚举硬编码 + 评分表**的轻量级方案。

#### B. 模型得分表 (`ModelScore`)
记录每个模型在各个维度下的得分。建议放在 `apps/rankings/models.py`。

```python
class ModelScore(models.Model):
    DIMENSION_CHOICES = [
        ('overall', '综合评测'),
        ('language', '语言理解'),
        ('reasoning', '推理能力'),
        ('code', '代码能力'),
        ('knowledge', '知识问答'),
        ('safety', '安全合规'),
    ]

    model = models.ForeignKey('models.My_Model', on_delete=models.CASCADE, related_name='scores')
    dimension = models.CharField(max_length=20, choices=DIMENSION_CHOICES, db_index=True)
    score = models.FloatField(default=0.0, help_text="当前得分 (0-100)")
    
    # 用于计算趋势
    previous_score = models.FloatField(default=0.0, help_text="上周期得分")
    previous_rank = models.IntegerField(default=0, help_text="上周期排名")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('model', 'dimension')
        indexes = [
            models.Index(fields=['dimension', '-score']), # 加速排序查询
        ]
```

#### C. 评测任务关联 (`EvaluationTask` Update)
当 `EvaluationTask` 完成时，需要触发得分更新逻辑。

---

## 4. API 接口设计

### 4.1 全站统计接口

*   **URL**: `/api/system/dashboard/stats/`
*   **Method**: `GET`
*   **Description**: 获取首页顶部的四个统计卡片数据。

**响应体 (Response JSON)**:
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "model_count": 42,        // 真实模型总数
        "dataset_count": 15,      // 真实数据集总数
        "task_count": 128,        // 累计评测任务数
        "user_count": 305,        // 总注册用户
        "online_user_count": 12,  // 在线用户数 (需 Redis 或 Session 统计支持)
        "active_user_count": 45   // 近24小时活跃用户
    }
}
```

### 4.2 排行榜接口

*   **URL**: `/api/rankings/leaderboard/`
*   **Method**: `GET`
*   **Description**: 获取排序后的模型列表。

**请求参数 (Query Params)**:
*   `dimension`: string (默认 `overall`) - 排序维度，如 `language`, `code`。
*   `limit`: int (默认 `10`) - 返回数量。

**响应体 (Response JSON)**:
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "dimension": "code",
        "dimension_display": "代码能力",
        "results": [
            {
                "id": 101,
                "name": "DeepSeek Coder",
                "company": "DeepSeek",
                "avatar_url": "...",
                "scores": {
                    "overall": 88.5,
                    "language": 85.0,
                    "reasoning": 92.1,
                    "code": 95.5,    // 当前维度的分数会高亮
                    "knowledge": 80.0,
                    "safety": 90.0
                },
                "main_score": 95.5,  // 当前排序依据的分数
                "trend": 1,          // 1: 上升, 0: 持平, -1: 下降
                "star_count": 1024,  // 点赞数
                "is_followed": true
            },
            // ... 更多模型
        ]
    }
}
```

---

## 5. 业务逻辑实现建议 (Service Layer)

### 5.1 得分计算逻辑
不要在每次 API 请求时实时计算所有 Dataset 的平均分。应该采用**事件驱动**或**定时任务**：

1.  **触发时机**：当一个 `EvaluationTask` 状态变为 `completed`。
2.  **计算步骤**：
    *   读取该 Task 对应的 `dataset` 的 `category` (映射到 dimension)。
    *   读取 Task 的 `result` 分数。
    *   更新 `ModelScore` 表中对应 `(model, dimension)` 的记录。
    *   重新计算 `overall` 维度（加权平均）。

### 5.2 趋势 (Trend) 计算
建议每天凌晨运行 Celery 定时任务：
1.  将当前的 Rank 存入 `previous_rank`。
2.  对比当前实时 Rank 和 `previous_rank`，得出 trend (1, 0, -1)。

### 5.3 在线用户统计
如果使用 Django 的默认 Session：
*   查询 `django_session` 表中 `expire_date > now()` 的数量（粗略估计）。
*   或者使用 Redis 记录带有过期时间的 User ID Set。

