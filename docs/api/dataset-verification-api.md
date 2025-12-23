# 数据集审核和能力分析API文档

## 概述

本文档描述了数据集审核和能力分析相关的API接口，包括数据集上传、审核状态查询和能力分析状态查询。

## API接口

### 1. 数据集上传

**端点**：`POST /api/datasets/`

**描述**：上传新的数据集

**请求参数**：
```json
{
  "name": "数据集名称",
  "description": "数据集描述",
  "category": "image|text|multimodal",
  "evaluation_type": "subjective|objective|adversarial",
  "file_format": "csv|json|zip",
  "file_path": "文件对象",
  "is_public": true
}
```

**响应示例**：
```json
{
  "code": 201,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "name": "数据集名称",
    "capability_tag": "processing",
    "capability_dimension": "other",
    "is_verified": false,
    "created_at": "2023-12-23T14:00:00Z"
  }
}
```

**说明**：
- 上传成功后，数据集状态默认为"审核中"(`is_verified: false`)
- 如果文件格式正确，能力标签设置为"processing"状态
- 如果文件格式错误，能力标签设置为"other"状态

---

### 2. 数据集审核

**端点**：`POST /api/datasets/{id}/verify/`

**描述**：管理员审核数据集

**权限**：管理员权限

**请求参数**：
```json
{
  "is_verified": true
}
```

**响应示例**：
```json
{
  "code": 200,
  "msg": "数据集审核通过"
}
```

**说明**：
- 只有管理员可以调用此接口
- 审核通过后，如果数据集文件存在且格式正确，会自动触发能力分析
- 审核不通过时，设置 `is_verified` 为 `false`

---

### 3. 查询数据集状态

**端点**：`GET /api/datasets/{id}/capability_status/`

**描述**：查询数据集审核和能力分析状态

**响应示例**：
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "dataset_id": 1,
    "capability_tag": "processing",
    "capability_dimension": "other",
    "is_processing": true,
    "is_verified": false,
    "has_file": true
  }
}
```

**状态说明**：

#### 审核状态 (`is_verified`)
- `false`：数据集正在审核中，等待管理员审核
- `true`：数据集已通过审核

#### 能力分析状态 (`capability_tag`)
- `processing`：正在分析能力维度
- `no_file`：文件缺失，无法进行能力分析
- `no_samples`：无有效样本，无法进行能力分析
- `analysis_failed`：分析失败，请检查数据集格式或稍后重试
- `language/reasoning/coding`：分析成功，已确定能力类型
- `other`：默认状态，通常用于无法分类的数据集

---

## 前端集成示例

### 1. 数据集上传后轮询

```javascript
function onDatasetUploaded(datasetId) {
  // 显示审核中的UI状态
  updateUI({
    status: 'pending_verification',
    message: '数据集已上传，等待管理员审核...',
    type: 'info'
  });
  
  // 开始轮询
  pollDatasetCapabilityStatus(datasetId, (result) => {
    if (!result.data.is_verified) {
      // 未审核，显示等待审核状态
      updateUI({
        status: 'pending_verification',
        message: '数据集正在审核中，请耐心等待...',
        type: 'info'
      });
    } else {
      // 已审核，检查能力分析状态
      switch (result.data.capability_tag) {
        case 'processing':
          updateUI({
            status: 'processing',
            message: '数据集已审核通过，正在分析能力维度...',
            type: 'info'
          });
          break;
          
        case 'no_file':
        case 'no_samples':
        case 'analysis_failed':
          // 处理错误状态
          updateUI({
            status: 'error',
            message: '能力分析失败，请检查数据集格式或稍后重试',
            type: 'error'
          });
          break;
          
        default:
          // 分析完成
          updateUI({
            status: 'completed',
            message: `数据集审核完成，能力分析结果: ${result.data.capability_tag}`,
            type: 'success'
          });
          showNotification('数据集已完全就绪', 'success');
          break;
      }
    }
  });
}
```

### 2. 轮询函数实现

```javascript
async function pollDatasetCapabilityStatus(datasetId, callback) {
  let attempts = 0;
  const maxAttempts = 30;
  
  const poll = async () => {
    attempts++;
    
    try {
      const response = await fetch(`/api/datasets/${datasetId}/capability_status/`);
      const result = await response.json();
      
      if (result.code === 200) {
        const { capability_tag, capability_dimension, is_processing, is_verified } = result.data;
        
        callback({
          success: true,
          data: result.data,
          isCompleted: !is_processing && is_verified
        });
        
        // 如果处理完成，停止轮询
        if (!is_processing && is_verified) {
          return;
        }
      } else {
        callback({ success: false, error: result.msg });
      }
    } catch (error) {
      callback({ success: false, error: error.message });
    }
    
    if (attempts < maxAttempts) {
      setTimeout(poll, 2000); // 每2秒轮询一次
    }
  };
  
  poll();
}
```

## 错误处理

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|---------|------|---------|
| 400 | 请求参数错误 | 检查请求参数是否正确 |
| 401 | 未授权 | 检查用户登录状态 |
| 403 | 权限不足 | 确认用户有相应权限 |
| 404 | 数据集不存在 | 检查数据集ID是否正确 |
| 413 | 文件格式错误 | 检查文件格式是否符合要求 |
| 500 | 服务器内部错误 | 稍后重试或联系技术支持 |

### 错误状态处理

1. **文件格式错误**：
   - 前端显示："文件格式不符合要求，请检查文件格式"
   - 用户操作：重新上传正确格式的文件

2. **审核未通过**：
   - 前端显示："数据集审核未通过，请联系管理员"
   - 用户操作：查看审核意见并修改后重新上传

3. **能力分析失败**：
   - 前端显示："能力分析失败，请检查数据集格式或稍后重试"
   - 用户操作：查看数据集描述中的详细错误信息

## 最佳实践

1. **错误处理**：始终检查API响应的`code`字段
2. **状态管理**：根据不同的状态显示相应的UI提示
3. **用户体验**：提供清晰的错误信息和处理建议
4. **性能优化**：合理设置轮询间隔，避免过多请求
5. **安全考虑**：在前端隐藏敏感信息，如详细错误堆栈

## 注意事项

1. **文件大小限制**：上传文件大小不超过100MB
2. **支持格式**：CSV、JSON、ZIP格式
3. **审核流程**：只有管理员审核通过的数据集才能进行能力分析
4. **异步处理**：能力分析在后台异步进行，不阻塞用户操作