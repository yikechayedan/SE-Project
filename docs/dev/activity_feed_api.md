# 系统动态板块 (News Feed) 实现方案 V2

## 1. 核心设计理念
为了实现一个实时的、包含历史回溯能力的“系统新闻流”，我们不能仅依赖查询业务表的当前状态。我们需要一个**事件驱动日志系统 (Event-Driven Logging System)**。

该系统包含三个核心部分：
1.  **SystemEvent 模型**：持久化存储每一条新闻动态。
2.  **事件触发器 (Triggers)**：在业务动作发生时（如上传数据集、定时更新排名），自动捕获关键信息（谁、什么模型、什么公司）并写入日志。
3.  **API 接口**：向前端提供格式化好的新闻流数据。

---

## 2. 数据库建模 (SystemEvent)

在 `PolyMetric/backend/apps/users/models.py` 或新建 `apps/system/models.py` 中定义：

```python
from django.db import models

class SystemEvent(models.Model):
    """
    记录系统全局动态，用于首页 News Feed 展示
    """
    EVENT_TYPES = [
        ('dataset_upload', '数据集上传'), # 绿色
        ('model_add', '模型收录'),      # 蓝色
        ('rank_up', '排名上升'),        # 金色/橙色
        ('task_complete', '评测完成'),  # 灰色
    ]

    # 1. 事件元数据
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True, verbose_name="事件类型")
    
    # 2. 触发者 (Actor) - 记录当时的快照，防止用户注销后数据丢失
    actor_id = models.IntegerField(null=True, blank=True, help_text="触发事件的用户ID，系统事件可为空")
    actor_name = models.CharField(max_length=150, default="PolyMetric系统", verbose_name="触发者名称")
    
    # 3. 目标对象 (Target) - 记录当时的对象信息
    target_id = models.IntegerField(null=True, blank=True)
    target_name = models.CharField(max_length=255, verbose_name="目标名称", help_text="如模型名、数据集名")
    target_extra = models.CharField(max_length=255, blank=True, verbose_name="额外信息", help_text="如模型公司、排名变化幅度")

    # 4. 展示文案
    # 建议在写入时生成好，避免读取时反复拼接，也支持历史文案不随对象改名而改变
    message = models.TextField(verbose_name="动态消息内容") 

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "系统动态"
```

---

## 3. 业务逻辑对接 (如何记录)

### 场景 A：用户上传数据集
**机制**：使用 Django Signals 监听 `Dataset` 模型的创建。
**获取字段**：从 `instance` 中获取 `creator.username`, `name`。

```python
# apps/datasets/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Dataset
from apps.system.models import SystemEvent

@receiver(post_save, sender=Dataset)
def log_dataset_upload(sender, instance, created, **kwargs):
    if created and instance.is_public: # 仅记录公开数据集
        SystemEvent.objects.create(
            event_type='dataset_upload',
            actor_id=instance.creator.id,
            actor_name=instance.creator.username,
            target_id=instance.id,
            target_name=instance.name,
            message=f"用户 {instance.creator.username} 上传了新数据集「{instance.name}」"
        )
```

### 场景 B：模型排名上升
**机制**：在定时更新排行榜的 Celery Task 或 Service 函数中手动插入。
**获取字段**：在计算逻辑中，对比 `old_rank` 和 `new_rank`。

```python
# apps/rankings/services.py
def update_leaderboard():
    # ... 计算排名的复杂逻辑 ...
    # 假设：model_obj 是当前模型对象，rank_change 是排名变化量 (+3 表示上升3位)
    
    if rank_change > 0:
        SystemEvent.objects.create(
            event_type='rank_up',
            actor_name="榜单更新",
            target_id=model_obj.id,
            target_name=model_obj.name,
            target_extra=model_obj.company, # 获取公司字段
            message=f"{model_obj.company} 的模型 {model_obj.name} 排名飙升，上升了 {rank_change} 位！"
        )
```

### 场景 C：平台新增模型
**机制**：监听 `Model` 表的创建。
**获取字段**：`name`, `company`。

```python
# apps/models/signals.py
@receiver(post_save, sender=LLMModel)
def log_model_add(sender, instance, created, **kwargs):
    if created:
        SystemEvent.objects.create(
            event_type='model_add',
            actor_name="系统管理员",
            target_id=instance.id,
            target_name=instance.name,
            target_extra=instance.company,
            message=f"平台新收录模型：{instance.name} ({instance.company})"
        )
```

---

## 4. API 接口定义

后端只需提供一个只读接口，返回格式化好的数据。

*   **URL**: `/api/system/news/`
*   **Method**: `GET`

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 105,
      "content": "Google 的模型 Gemini 1.5 Pro 排名飙升，上升了 2 位！",
      "time": "2023-12-18T10:00:00Z",
      "type": "warning", // 对应前端黄色图标
      "icon": "Top"      // 可选：后端指定图标名
    },
    {
      "id": 104,
      "content": "用户 wang-ty22 上传了新数据集「C-Eval Valid」",
      "time": "2023-12-18T09:30:00Z",
      "type": "success", // 对应前端绿色图标
      "icon": "Folder"
    },
    {
      "id": 103,
      "content": "平台新收录模型：Llama-3-70B (Meta)",
      "time": "2023-12-17T15:20:00Z",
      "type": "primary", // 对应前端蓝色图标
      "icon": "Box"
    }
  ]
}
```