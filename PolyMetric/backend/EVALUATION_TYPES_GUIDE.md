# 数据集测评类型功能指南

## 概述

数据集现在支持三种测评类型：主观测评、客观测评和对抗测评。用户上传数据集时，系统会根据选择的测评类型验证数据集格式，确保符合标准。

## 测评类型

### 1. 主观测评 (subjective)

**格式要求**：每个数据项必须包含 `input` 和 `reference` 字段

**示例格式**：
```json
[
  {
    "input": "请简要解释什么是操作系统。",
    "reference": "操作系统是管理计算机硬件与软件资源的系统软件。"
  },
  {
    "input": "什么是机器学习？",
    "reference": "机器学习是让计算机从数据中自动学习规律的方法。"
  }
]
```

### 2. 客观测评 (objective)

**格式要求**：每个数据项必须包含 `input` 和 `answer` 字段

**示例格式**：
```json
[
  {
    "input": "Lichens are symbiotic organisms made of green algae and fungi. What do the green algae supply to the fungi in this symbiotic relationship?\nA. carbon dioxide\nB. food\nC. protection\nD. water",
    "answer": "B"
  },
  {
    "input": "When a switch is used in an electrical circuit, the switch can\nA. cause the charge to build.\nB. increase and decrease the voltage.\nC. cause the current to change direction.\nD. stop and start the flow of current.",
    "answer": "D"
  }
]
```

### 3. 对抗测评 (adversarial)

**格式要求**：每个数据项只需包含 `input` 字段

**示例格式**：
```json
[
  {
    "input": "请简要解释什么是 Transformer 模型。"
  },
  {
    "input": "如果你是产品经理，如何评价一个大模型的好坏？"
  }
]
```

## 使用方法

### 1. 通过API上传数据集

```http
POST /api/datasets/
Content-Type: multipart/form-data

name: 测试数据集
description: 这是一个测试数据集
category: text
evaluation_type: subjective  # 选择测评类型
file_format: json
file_path: [上传的JSON文件]
is_public: true
```

### 2. 验证规则

- 系统会自动验证上传的JSON文件格式是否符合选择的测评类型
- 如果格式不符合要求，系统会返回详细的错误信息
- 非JSON文件（如CSV、ZIP）会跳过格式验证

### 3. 错误示例

如果上传格式错误的数据集，系统会返回如下错误：

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

## 示例文件

系统提供了三种测评类型的示例文件，位于 `apps/datasets/examples/` 目录：

- `subjective_test_5.json` - 主观测评示例
- `object(1).json` - 客观测评示例
- `adversarial_test.json` - 对抗测评示例

## 技术实现

### 数据库变更

在 `Dataset` 模型中新增了 `evaluation_type` 字段：

```python
evaluation_type = models.CharField(
    max_length=20,
    verbose_name="测评类型",
    choices=[
        ("subjective", "主观测评"),
        ("objective", "客观测评"),
        ("adversarial", "对抗测评")
    ],
    default="subjective"
)
```

### 验证逻辑

在 `DatasetSerializer` 中实现了 `validate_dataset_format` 方法，用于验证数据集格式：

- 主观测评：验证 `input` 和 `reference` 字段
- 客观测评：验证 `input` 和 `answer` 字段
- 对抗测评：验证 `input` 字段

### API变更

- 新增 `evaluation_type` 字段支持
- 更新过滤器，支持按测评类型筛选数据集
- 在创建和更新数据集时自动验证格式

## 注意事项

1. 所有数据项必须是对象格式（字典）
2. 数据集必须是非空数组
3. 系统只检查前5个数据项的格式，以提高性能
4. 如果上传的是非JSON文件，系统会跳过格式验证
5. 错误信息会明确指出哪个数据项缺少哪个必需字段