# 系统动态模块 (System Events)

## 功能概述

系统动态模块实现了一个事件驱动的日志系统，用于记录和展示系统中的重要活动，如数据集上传、模型收录、排名变化和评测完成等。

## 核心组件

### 1. SystemEvent 模型
- **位置**: `apps/system/models.py`
- **功能**: 存储系统事件的所有信息
- **字段**:
  - `event_type`: 事件类型 (数据集上传、模型收录、排名上升、评测完成)
  - `actor_id`: 触发事件的用户ID
  - `actor_name`: 触发者名称
  - `target_id`: 目标对象ID
  - `target_name`: 目标对象名称
  - `target_extra`: 额外信息 (如公司名称、排名变化)
  - `message`: 展示消息
  - `created_at`: 创建时间

### 2. 信号处理器 (Signals)
- **位置**: `apps/system/signals.py`
- **功能**: 监听业务模型的变化，自动创建系统事件
- **监听的事件**:
  - 数据集创建 (Dataset.post_save)
  - 模型创建 (My_Model.post_save)

### 3. 服务函数 (Services)
- **位置**: `apps/system/services.py`
- **功能**: 提供手动记录系统事件的工具函数
- **主要函数**:
  - `log_rank_change()`: 记录排名变化
  - `log_task_complete()`: 记录任务完成

### 4. API 接口
- **位置**: `apps/system/views.py`
- **端点**: `/api/system/news/`
- **方法**: GET
- **功能**: 返回格式化的系统动态列表

## 使用方法

### 1. 获取系统动态
```http
GET /api/system/news/
```

响应示例:
```json
{
  "code": 200,
  "data": [
    {
      "id": 105,
      "content": "Google 的模型 Gemini 1.5 Pro 排名飙升，上升了 2 位！",
      "time": "2023-12-18T10:00:00Z",
      "type": "warning",
      "icon": "Top"
    },
    {
      "id": 104,
      "content": "用户 wang-ty22 上传了新数据集「C-Eval Valid」",
      "time": "2023-12-18T09:30:00Z",
      "type": "success",
      "icon": "Folder"
    }
  ]
}
```

### 2. 手动记录系统事件
```python
from apps.system.services import log_rank_change, log_task_complete

# 记录排名变化
log_rank_change(model_obj, old_rank=5, new_rank=3)

# 记录任务完成
log_task_complete(task_obj, user_obj)
```

## 事件类型与前端映射

| 事件类型 | 前端类型 | 图标 | 颜色 |
|---------|---------|------|------|
| dataset_upload | success | Folder | 绿色 |
| model_add | primary | Box | 蓝色 |
| rank_up | warning | Top | 金色/橙色 |
| task_complete | info | CheckCircle | 灰色 |

## 管理界面

系统事件可以在Django管理后台中查看和管理:
- 路径: `/admin/system/systemevent/`
- 功能: 查看列表、筛选、搜索
- 限制: 禁止手动添加和修改事件

## 测试

运行测试:
```bash
python manage.py test apps.system.tests
```

测试覆盖:
- API接口测试
- 信号处理器测试
- 数据格式验证

## 扩展指南

### 添加新的事件类型
1. 在 `SystemEvent.EVENT_TYPES` 中添加新选项
2. 在 `SystemEventSerializer.get_type()` 中添加映射
3. 在 `SystemEventSerializer.get_icon()` 中添加图标
4. 创建相应的信号处理器或服务函数

### 自定义消息格式
可以在信号处理器或服务函数中自定义消息内容，支持动态变量和格式化。