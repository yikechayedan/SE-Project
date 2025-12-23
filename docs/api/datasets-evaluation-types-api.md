# 数据集测评类型 API 文档

## 概述

本文档描述了数据集测评类型功能的API接口，包括创建、查询、更新和删除数据集时的测评类型相关操作。

## 基础信息

- **基础URL**: `/api/datasets/`
- **认证方式**: Token Authentication / Session Authentication
- **内容类型**: `application/json` 或 `multipart/form-data`（上传文件时）

## 测评类型枚举

| 值 | 显示名称 | 描述 |
|---|---|---|
| `subjective` | 主观测评 | 每个数据项包含 input 和 reference 字段 |
| `objective` | 客观测评 | 每个数据项包含 input 和 answer 字段 |
| `adversarial` | 对抗测评 | 每个数据项只包含 input 字段 |

## API 接口

### 1. 获取数据集列表

**请求**:
```http
GET /api/datasets/
```

**查询参数**:
- `evaluation_type` - 按测评类型筛选 (subjective/objective/adversarial)
- `category` - 按数据集类型筛选 (image/text/multimodal)
- `page` - 页码
- `page_size` - 每页数量

**响应示例**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "主观测评数据集",
      "description": "这是一个主观测评数据集",
      "category": "text",
      "evaluation_type": "subjective",
      "file_format": "json",
      "file_size": 0.5,
      "sample_count": 100,
      "creator": {
        "id": 1,
        "username": "admin"
      },
      "creator_id": 1,
      "creator_username": "admin",
      "is_public": true,
      "is_verified": true,
      "is_followed": false,
      "has_file": true,
      "star_count": 5,
      "is_starred": false,
      "created_at": "2023-12-21T08:00:00Z",
      "updated_at": "2023-12-21T08:00:00Z",
      "file_url": "/api/datasets/1/download/"
    }
  ]
}
```

### 2. 创建数据集（支持测评类型验证）

**请求**:
```http
POST /api/datasets/
Content-Type: multipart/form-data
```

**请求参数**:
```
name: 数据集名称
description: 数据集描述
category: text  # image/text/multimodal
evaluation_type: subjective  # subjective/objective/adversarial
file_format: json  # csv/json/zip
file_path: [文件]
is_public: true
```

**JSON文件格式要求**:

#### 主观测评 (subjective)
```json
[
  {
    "input": "请解释什么是机器学习。",
    "reference": "机器学习是人工智能的一个分支..."
  }
]
```

#### 客观测评 (objective)
```json
[
  {
    "input": "1+1等于多少？\nA. 1\nB. 2\nC. 3\nD. 4",
    "answer": "B"
  }
]
```

#### 对抗测评 (adversarial)
```json
[
  {
    "input": "请解释什么是量子计算。"
  }
]
```

**成功响应**:
```json
{
  "code": 201,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "name": "主观测评数据集",
    "description": "这是一个主观测评数据集",
    "category": "text",
    "evaluation_type": "subjective",
    "file_format": "json",
    "file_size": 0.5,
    "sample_count": 100,
    "creator": {
      "id": 1,
      "username": "admin"
    },
    "creator_id": 1,
    "creator_username": "admin",
    "is_public": true,
    "is_verified": false,
    "is_followed": false,
    "has_file": true,
    "star_count": 0,
    "is_starred": false,
    "created_at": "2023-12-21T08:00:00Z",
    "updated_at": "2023-12-21T08:00:00Z",
    "file_url": "/api/datasets/1/download/"
  }
}
```

**格式验证失败响应**:
```json
{
  "code": 400,
  "msg": "创建失败",
  "data": {
    "non_field_errors": [
      "主观测评数据集第1个项目缺少必需的 'reference' 字段"
    ]
  }
}
```

### 3. 获取数据集详情

**请求**:
```http
GET /api/datasets/{id}/
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 1,
    "name": "主观测评数据集",
    "description": "这是一个主观测评数据集",
    "category": "text",
    "evaluation_type": "subjective",
    "file_format": "json",
    "file_size": 0.5,
    "sample_count": 100,
    "creator": {
      "id": 1,
      "username": "admin"
    },
    "creator_id": 1,
    "creator_username": "admin",
    "is_public": true,
    "is_verified": true,
    "is_followed": false,
    "has_file": true,
    "star_count": 5,
    "is_starred": false,
    "created_at": "2023-12-21T08:00:00Z",
    "updated_at": "2023-12-21T08:00:00Z",
    "file_url": "/api/datasets/1/download/"
  }
}
```

### 4. 更新数据集

**请求**:
```http
PUT /api/datasets/{id}/
Content-Type: multipart/form-data
```

**请求参数**:
```
name: 数据集名称
description: 数据集描述
category: text
evaluation_type: subjective  # 可以修改测评类型
file_format: json
file_path: [文件]  # 可选
is_public: true
```

**成功响应**:
```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "name": "更新后的数据集名称",
    "description": "更新后的描述",
    "category": "text",
    "evaluation_type": "objective",  # 测评类型已更新
    "file_format": "json",
    "file_size": 0.5,
    "sample_count": 100,
    "creator": {
      "id": 1,
      "username": "admin"
    },
    "creator_id": 1,
    "creator_username": "admin",
    "is_public": true,
    "is_verified": true,
    "is_followed": false,
    "has_file": true,
    "star_count": 5,
    "is_starred": false,
    "created_at": "2023-12-21T08:00:00Z",
    "updated_at": "2023-12-21T09:00:00Z",
    "file_url": "/api/datasets/1/download/"
  }
}
```

### 5. 部分更新数据集

**请求**:
```http
PATCH /api/datasets/{id}/
Content-Type: application/json
```

**请求体**:
```json
{
  "evaluation_type": "adversarial",
  "description": "更新为对抗测评类型"
}
```

**成功响应**:
```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "name": "数据集名称",
    "description": "更新为对抗测评类型",
    "category": "text",
    "evaluation_type": "adversarial",
    // ... 其他字段
  }
}
```

### 6. 删除数据集

**请求**:
```http
DELETE /api/datasets/{id}/
```

**成功响应**:
```json
{
  "code": 200,
  "msg": "删除成功"
}
```

### 7. 按测评类型筛选数据集

**请求**:
```http
GET /api/datasets/?evaluation_type=subjective
GET /api/datasets/?evaluation_type=objective
GET /api/datasets/?evaluation_type=adversarial
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "主观测评数据集1",
      "evaluation_type": "subjective",
      // ... 其他字段
    },
    {
      "id": 2,
      "name": "主观测评数据集2",
      "evaluation_type": "subjective",
      // ... 其他字段
    }
  ]
}
```

### 8. 预览数据集内容

**请求**:
```http
GET /api/datasets/{id}/preview/?limit=10
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "预览成功",
  "data": {
    "format": "json",
    "headers": ["input", "reference"],
    "rows": [
      {
        "input": "请解释什么是机器学习。",
        "reference": "机器学习是人工智能的一个分支..."
      }
    ],
    "total": 100
  }
}
```

### 9. 获取数据集条目（分页）

**请求**:
```http
GET /api/datasets/{id}/entries/?page=1&page_size=10
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "entries": [
      {
        "id": 1,
        "input": "请解释什么是机器学习。",
        "reference": "机器学习是人工智能的一个分支..."
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "fields": ["id", "input", "reference"]
  }
}
```

## 错误代码

| 错误代码 | 描述 | 示例 |
|---|---|---|
| 400 | 请求参数错误 | 格式验证失败 |
| 401 | 未授权访问 | 缺少认证token |
| 403 | 权限不足 | 无法修改他人数据集 |
| 404 | 资源不存在 | 数据集ID不存在 |
| 413 | 文件过大 | 超过100MB限制 |

## 前端集成建议

### 1. 创建数据集表单

```javascript
const formData = new FormData();
formData.append('name', datasetName);
formData.append('description', description);
formData.append('category', 'text');
formData.append('evaluation_type', evaluationType); // 新增字段
formData.append('file_format', 'json');
formData.append('file_path', file);
formData.append('is_public', true);

fetch('/api/datasets/', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Token ${token}`
  }
})
.then(response => response.json())
.then(data => {
  if (data.code === 201) {
    // 创建成功
    console.log('数据集创建成功:', data.data);
  } else {
    // 处理错误
    console.error('创建失败:', data.data);
  }
});
```

### 2. 测评类型选择器

```javascript
const evaluationTypes = [
  { value: 'subjective', label: '主观测评' },
  { value: 'objective', label: '客观测评' },
  { value: 'adversarial', label: '对抗测评' }
];

// 在表单中使用
<select value={evaluationType} onChange={handleTypeChange}>
  {evaluationTypes.map(type => (
    <option key={type.value} value={type.value}>
      {type.label}
    </option>
  ))}
</select>
```

### 3. 格式验证错误处理

```javascript
const handleCreateError = (errorData) => {
  if (errorData.non_field_errors) {
    // 处理格式验证错误
    errorData.non_field_errors.forEach(errorMessage => {
      if (errorMessage.includes('缺少必需的')) {
        // 显示格式要求提示
        showFormatGuide(evaluationType);
      }
    });
  }
};
```

### 4. 格式要求提示组件

```javascript
const FormatGuide = ({ evaluationType }) => {
  const guides = {
    subjective: {
      title: '主观测评格式要求',
      fields: ['input', 'reference'],
      example: `[
  {
    "input": "请解释什么是机器学习。",
    "reference": "机器学习是人工智能的一个分支..."
  }
]`
    },
    objective: {
      title: '客观测评格式要求',
      fields: ['input', 'answer'],
      example: `[
  {
    "input": "1+1等于多少？\\nA. 1\\nB. 2",
    "answer": "B"
  }
]`
    },
    adversarial: {
      title: '对抗测评格式要求',
      fields: ['input'],
      example: `[
  {
    "input": "请解释什么是量子计算。"
  }
]`
    }
  };

  const guide = guides[evaluationType];
  return (
    <div>
      <h3>{guide.title}</h3>
      <p>每个数据项必须包含以下字段: {guide.fields.join(', ')}</p>
      <pre>{guide.example}</pre>
    </div>
  );
};
```

## 注意事项

1. **文件格式验证**: JSON文件和ZIP文件都会进行格式验证，CSV文件会跳过验证
2. **图像数据集验证**: 图像数据集现在也必须遵循测评类型的字段要求
   - 主观测评：必须包含 `input`、`reference` 和 `image` 字段
   - 客观测评：必须包含 `input`、`answer` 和 `image` 字段
   - 对抗测评：必须包含 `input` 和 `image` 字段
3. **性能优化**: 系统只检查前5个数据项的格式，以提高验证性能
4. **错误信息**: 验证失败时会明确指出哪个数据项缺少哪个必需字段
5. **向后兼容**: 现有数据集的`evaluation_type`字段会默认设置为"subjective"
6. **权限控制**: 只有数据集创建者和管理员可以修改测评类型