# 数据集能力分析异步处理方案

## 问题描述

在原始实现中，当用户上传数据集后，系统会同步调用大模型来判断数据集的能力维度，这会导致请求阻塞，用户体验不佳。

## 解决方案

将大模型调用改为异步处理，使用Celery任务队列在后台处理能力分析，前端通过轮询机制获取处理结果。

## 实现细节

### 1. 异步任务

在 `apps/tasks/tasks.py` 中添加了 `analyze_dataset_capability` 任务：

```python
@shared_task(bind=True)
def analyze_dataset_capability(self, dataset_id):
    """
    异步分析数据集能力维度
    在数据集上传后，通过Celery异步调用大模型判断数据集的能力维度
    """
```

### 2. 数据集序列化器修改

修改 `apps/datasets/serializers.py` 中的 `create` 和 `update` 方法：

- 上传/更新数据集时，不再同步调用大模型
- 设置能力标签为 "processing" 状态
- 触发异步任务进行能力分析

### 3. 状态跟踪

在 `apps/datasets/models.py` 中添加了 "processing" 状态：

```python
CAPABILITY_CHOICES = [
    ('processing', '处理中'),
    ('language', '语言理解'),
    ('math', '数学推理'),
    ('code', '代码能力'),
    ('multimodal', '多模态'),
    ('other', '其他'),
]
```

### 4. API端点

在 `apps/datasets/views.py` 中添加了 `capability_status` 端点：

```python
@action(detail=True, methods=["get"])
def capability_status(self, request, pk=None):
    """查询数据集能力分析状态"""
```

## 使用方法

### 1. 启动Celery Worker

```bash
# 方式1：使用提供的脚本
python start_celery_worker.py

# 方式2：直接使用Celery命令
celery -A PolyMetric.celery worker --loglevel=info --concurrency=2
```

### 2. 前端轮询实现

参考 `frontend_polling_example.js` 中的示例代码：

```javascript
// 上传数据集后，获取数据集ID并开始轮询
function onDatasetUploaded(datasetId) {
  // 显示处理中的UI状态
  updateUI({
    status: 'processing',
    message: '正在分析数据集能力维度，请稍候...'
  });
  
  // 开始轮询
  pollDatasetCapabilityStatus(datasetId, (result) => {
    // 处理轮询结果
    if (result.success && result.isCompleted) {
      // 处理完成，更新UI
      showNotification('数据集能力分析完成', 'success');
    }
  });
}
```

### 3. 测试异步处理

运行测试脚本：

```bash
python test_async_capability.py
```

## 优势

1. **用户体验提升**：上传数据集不再需要等待大模型分析完成
2. **系统稳定性**：避免长时间阻塞导致的请求超时
3. **可扩展性**：可以轻松添加更多的后台处理任务
4. **错误处理**：异步任务失败不会影响用户上传流程

## 注意事项

1. **Celery依赖**：需要确保Redis服务正常运行，Celery Worker已启动
2. **任务监控**：建议使用Flower等工具监控Celery任务状态
3. **错误恢复**：异步任务失败时会设置默认能力标签为"other"
4. **前端兼容**：前端需要处理"processing"状态的显示

## 扩展建议

1. **WebSocket通知**：可以考虑使用WebSocket替代轮询，实时推送处理结果
2. **任务优先级**：可以根据用户等级设置不同的任务优先级
3. **批量处理**：对于大量数据集，可以实现批量分析任务
4. **缓存机制**：对相似数据集的分析结果进行缓存，减少API调用