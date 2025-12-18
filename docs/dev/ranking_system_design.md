# 排行榜系统设计方案 (Leaderboard System Design) - v2.0

## 1. 核心架构：解耦方案
为了保证系统的可维护性和可扩展性，本项目采用**“维度得分表 (Dimension Score Table)”**方案。

### 为什么不直接在 `My_Model` 表中增加分数？
1.  **属性分离**：`My_Model` 仅存储模型的固有元数据（如名称、版本、厂商）。“得分”是评测产出的动态结果，不应混入主表。
2.  **扩展性**：未来若新增评测维度（如：安全合规、长文本能力、逻辑一致性），只需在得分表中增加数据行，而无需修改数据库结构（Schema）。
3.  **历史追溯**：独立表更方便未来扩展“历史分数”功能。

---

## 2. 数据库建模 (rankings app)

建议在 `apps/rankings/models.py` 中新增 `ModelDimensionScore` 模型，作为排行榜的直接数据源。

### 2.1 维度得分模型 (`ModelDimensionScore`)
该表存储模型在各个特定能力维度上的**聚合分数**。

```python
class ModelDimensionScore(models.Model):
    DIMENSION_CHOICES = [
        ('overall', '综合能力'),
        ('language', '语言理解'),
        ('math', '数学推理'),
        ('code', '代码能力'),
        ('multimodal', '多模态'),
    ]

    model = models.ForeignKey(
        'models.My_Model', 
        on_delete=models.CASCADE, 
        related_name='dimension_scores'
    )
    dimension = models.CharField(
        max_length=20, 
        choices=DIMENSION_CHOICES, 
        db_index=True,
        verbose_name="评测维度"
    )
    score = models.FloatField(default=0.0, verbose_name="得分")
    
    # 用于趋势计算：存储上一次更新时的分数或排名
    previous_score = models.FloatField(default=0.0) 
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rankings_dimension_score'
        unique_together = ('model', 'dimension') # 核心约束
        indexes = [
            models.Index(fields=['dimension', '-score']), # 核心索引：加速“按维度查排行榜”
        ]
```

---

## 3. API 接口规范

### 3.1 获取完整排行榜 (Pivot 视图)
*   **URL**: `/api/rankings/leaderboard/`
*   **Method**: `GET`
*   **说明**: 后端负责将数据库中的行数据转换为对象格式返回，方便前端直接渲染表格。

**响应体 (Response JSON)**:

```json
{
    "code": 200,
    "msg": "success",
    "data": [
        {
            "rank": 1,
            "model_id": 101,
            "name": "GPT-4o",
            "company": "OpenAI",
            "category": "text",
            "star_count": 1205,
            "scores": {
                "overall": 92.5,
                "language": 94.0,
                "math": 91.0,
                "code": 93.5,
                "multimodal": 88.0
            },
            "trends": {
                "overall": "up",      // 相比上一次更新
                "math": "stable"
            }
        },
        {
            "rank": 2,
            "model_id": 105,
            "name": "Claude 3.5",
            "company": "Anthropic",
            "category": "text",
            "star_count": 890,
            "scores": {
                "overall": 91.2,
                "language": 93.5,
                "math": 89.5,
                "code": 91.8,
                "multimodal": 90.2
            },
            "trends": {
                "overall": "down"
            }
        }
    ]
}
```

---

## 4. 逻辑实现逻辑 (Calculation Logic)

### 4.1 分数更新触发时机
每当一个 `EvaluationTask` 状态变为 `completed` 且生成了 `EvaluationSummary` 时，后端应触发计算逻辑：

1.  **确定维度**：根据 `EvaluationTask.dataset` 的标签（Tag）判断该评测属于哪个维度（如 GSM8K 数据集对应 `math` 维度，多模态数据集对应 `multimodal` 维度）。
2.  **重算聚合分**：查询该模型在该维度下的所有评测记录，计算平均分。
3.  **同步综合分**：更新该模型的 `overall` 维度得分（通常是各维度分的加权平均）。
4.  **更新 `ModelDimensionScore`**：执行 `update_or_create`。

---

## 5. 前端视觉特效实现 (UI/UX)
*   **下拉切换**：当用户在下拉框选择特定维度时，前端通过 `:class-name` 动态给 `el-table-column` 添加高亮类。
*   **分数值动效**：高亮显示的分数通过颜色加深和字体加粗处理。
*   **趋势标识**：利用 `trends` 字段，配合 `<el-icon>` 展示上升（`Top`）、下降（`Bottom`）或持平。
