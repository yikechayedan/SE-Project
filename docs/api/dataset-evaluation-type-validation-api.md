# 数据集格式与评测类型匹配验证 API

## 概述

为了确保数据一致性，系统现在会验证评测任务的 `method` 与数据集的 `evaluation_type` 是否匹配。当两者不匹配时，系统会拒绝创建或更新评测任务，并返回明确的错误信息。

## 评测类型对应关系

| 评测任务类型 (method) | 数据集类型 (evaluation_type) | 描述 |
|----------------------|---------------------------|------|
| subjective | subjective | 主观测评 |
| objective | objective | 客观测评 |
| adversarial | adversarial | 对抗评测 |

## API 接口变化

### 1. 创建评测任务

**接口**: `POST /api/tasks/evaluation-tasks/`

**请求体示例**:
```json
{
  "name": "评测任务名称",
  "description": "评测任务描述",
  "dataset": 1,  // 数据集ID
  "method": "subjective",  // 评测类型
  "myModel": 1  // 模型ID
}
```

**成功响应** (当数据集与评测类型匹配时):
```json
{
  "id": 1,
  "name": "评测任务名称",
  "description": "评测任务描述",
  "dataset": 1,
  "dataset_name": "数据集名称",
  "method": "subjective",
  "myModel": 1,
  "myModel_name": "模型名称",
  "status": "pending",
  "created_at": "2023-12-22T09:00:00Z",
  "updated_at": "2023-12-22T09:00:00Z"
}
```

**错误响应** (当数据集与评测类型不匹配时):
```json
{
  "dataset_format_error": [
    "数据集格式错误：当前数据集为客观评测格式，但创建的评测任务为主观评测类型，两者不匹配。请选择正确的评测类型或使用匹配的数据集。"
  ]
}
```

### 2. 更新评测任务

**接口**: `PATCH /api/tasks/evaluation-tasks/{id}/`

**请求体示例**:
```json
{
  "dataset": 2,  // 更换数据集
  "method": "objective"  // 更换评测类型
}
```

**错误响应** (当更新后的数据集与评测类型不匹配时):
```json
{
  "dataset_format_error": [
    "数据集格式错误：当前数据集为主观测评格式，但创建的评测任务为客观评测类型，两者不匹配。请选择正确的评测类型或使用匹配的数据集。"
  ]
}
```

## 前端处理建议

### 1. 创建任务时的验证

```javascript
// 创建评测任务
async function createEvaluationTask(taskData) {
  try {
    const response = await fetch('/api/tasks/evaluation-tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(taskData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      
      // 处理数据集格式错误
      if (errorData.dataset_format_error) {
        // 显示错误提示
        showErrorToast(errorData.dataset_format_error[0]);
        
        // 可选：高亮显示相关字段
        highlightField('dataset');
        highlightField('method');
        
        return;
      }
      
      // 处理其他错误
      handleOtherErrors(errorData);
      return;
    }
    
    const task = await response.json();
    showSuccessToast('评测任务创建成功');
    return task;
    
  } catch (error) {
    console.error('创建评测任务失败:', error);
    showErrorToast('创建评测任务失败，请重试');
  }
}
```

### 2. 更新任务时的验证

```javascript
// 更新评测任务
async function updateEvaluationTask(taskId, updateData) {
  try {
    const response = await fetch(`/api/tasks/evaluation-tasks/${taskId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updateData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      
      // 处理数据集格式错误
      if (errorData.dataset_format_error) {
        showErrorToast(errorData.dataset_format_error[0]);
        return;
      }
      
      handleOtherErrors(errorData);
      return;
    }
    
    const task = await response.json();
    showSuccessToast('评测任务更新成功');
    return task;
    
  } catch (error) {
    console.error('更新评测任务失败:', error);
    showErrorToast('更新评测任务失败，请重试');
  }
}
```

### 3. UI 组件建议

#### 数据集选择组件
```jsx
function DatasetSelector({ value, onChange, method }) {
  const [datasets, setDatasets] = useState([]);
  const [filteredDatasets, setFilteredDatasets] = useState([]);
  
  useEffect(() => {
    // 获取所有数据集
    fetchDatasets().then(setDatasets);
  }, []);
  
  useEffect(() => {
    // 根据评测类型过滤数据集
    if (method && datasets.length > 0) {
      const filtered = datasets.filter(dataset => 
        dataset.evaluation_type === method
      );
      setFilteredDatasets(filtered);
    } else {
      setFilteredDatasets(datasets);
    }
  }, [method, datasets]);
  
  return (
    <Select
      value={value}
      onChange={onChange}
      options={filteredDatasets.map(dataset => ({
        value: dataset.id,
        label: `${dataset.name} (${dataset.evaluation_type})`,
        evaluationType: dataset.evaluation_type
      }))}
      placeholder="请选择数据集"
    />
  );
}
```

#### 评测类型选择组件
```jsx
function EvaluationTypeSelector({ value, onChange, dataset }) {
  const options = [
    { value: 'subjective', label: '主观评测' },
    { value: 'objective', label: '客观评测' },
    { value: 'adversarial', label: '对抗评测' }
  ];
  
  const handleChange = (newValue) => {
    // 如果已选择数据集，检查是否匹配
    if (dataset && dataset.evaluation_type !== newValue) {
      const typeMap = {
        subjective: '主观评测',
        objective: '客观评测',
        adversarial: '对抗评测'
      };
      
      const datasetType = typeMap[dataset.evaluation_type];
      const taskType = typeMap[newValue];
      
      if (window.confirm(
        `当前数据集为${datasetType}格式，但您选择的评测类型为${taskType}，两者不匹配。\n\n` +
        `是否继续？创建任务时系统会显示错误信息。`
      )) {
        onChange(newValue);
      }
    } else {
      onChange(newValue);
    }
  };
  
  return (
    <Select
      value={value}
      onChange={handleChange}
      options={options}
      placeholder="请选择评测类型"
    />
  );
}
```

## 错误信息处理

### 错误类型
- `dataset_format_error`: 数据集格式与评测类型不匹配

### 错误信息格式
```
数据集格式错误：当前数据集为[数据集类型]格式，但创建的评测任务为[评测类型]类型，两者不匹配。请选择正确的评测类型或使用匹配的数据集。
```

### 前端错误处理最佳实践

1. **即时反馈**: 在用户选择数据集和评测类型时，实时检查是否匹配
2. **清晰提示**: 使用 Toast 或 Modal 显示明确的错误信息
3. **视觉引导**: 高亮显示需要修改的字段
4. **预防性提示**: 在用户选择不匹配的组合时，提前给出警告
5. **智能过滤**: 根据已选择的评测类型，自动过滤匹配的数据集

## 测试用例

前端开发人员可以使用以下测试用例验证功能：

1. **正常流程测试**:
   - 选择主观评测数据集 + 主观测评任务 → 应该成功
   - 选择客观评测数据集 + 客观测评任务 → 应该成功
   - 选择对抗评测数据集 + 对抗评测任务 → 应该成功

2. **错误流程测试**:
   - 选择主观评测数据集 + 客观测评任务 → 应该显示错误
   - 选择客观评测数据集 + 主观测评任务 → 应该显示错误
   - 选择主观评测数据集 + 对抗评测任务 → 应该显示错误

3. **更新测试**:
   - 创建匹配的任务后，更新为不匹配的数据集 → 应该显示错误
   - 创建匹配的任务后，更新为不匹配的评测类型 → 应该显示错误

## 注意事项

1. 验证在服务器端进行，前端验证仅用于提升用户体验
2. 错误信息支持中文，前端需要正确处理 UTF-8 编码
3. 建议在用户界面中显示数据集的 `evaluation_type` 信息，帮助用户正确选择
4. 考虑在数据集列表中添加类型标识，方便用户识别