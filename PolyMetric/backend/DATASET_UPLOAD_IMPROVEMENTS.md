# 数据集上传流程改进说明

## 概述

本文档说明了对CSV和ZIP数据集上传流程的改进，主要解决了安全性、可靠性和测试覆盖等问题。

## 主要改进内容

### 1. 架构统一

**问题**：系统中同时存在传统审核机制和自动验证机制，造成代码冗余和维护困难。

**解决方案**：
- 修改 `urls.py`，统一使用自动验证机制 `DatasetViewSetAutoVerify`
- 移除了对传统审核机制的依赖
- 简化了验证流程，提高了系统一致性

**修改文件**：
- `apps/datasets/urls.py`

### 2. ZIP安全性增强

**问题**：ZIP文件缺乏安全性检查，存在路径遍历攻击和ZIP炸弹风险。

**解决方案**：
- 添加 `_validate_zip_security()` 方法进行安全检查
- 防止路径遍历攻击（检查 `../` 和绝对路径）
- 限制单个文件大小（50MB）和总大小（200MB）
- 限制文件数量（1000个）防止ZIP炸弹

**新增安全限制**：
```python
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_TOTAL_SIZE = 200 * 1024 * 1024  # 200MB
MAX_FILE_COUNT = 1000  # 最大文件数量
```

**修改文件**：
- `apps/datasets/serializers_auto_verify.py`

### 3. CSV处理优化

**问题**：编码检测可能失败，字段映射过于宽松。

**解决方案**：
- 使用 `chardet` 库进行智能编码检测
- 改进字段映射逻辑，更严格的必需字段检查
- 提供详细的错误信息，指明具体缺少的字段

**编码检测改进**：
```python
# 使用chardet进行智能编码检测
detected = chardet.detect(content)
encoding = detected['encoding']
confidence = detected['confidence']

# 如果置信度低，尝试常见编码
if confidence is None or confidence < 0.7:
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            text = content.decode(enc)
            encoding = enc
            break
        except:
            continue
```

**字段映射改进**：
- 定义明确的必需字段列表
- 严格检查必需字段是否存在
- 提供具体的行号和字段名错误信息

**修改文件**：
- `apps/datasets/serializers_auto_verify.py`

### 4. 能力分析改进

**问题**：能力分析过度依赖外部AI服务，样本数量固定。

**解决方案**：
- 实现本地兜底机制 `fallback_capability_analysis()`
- 添加动态样本数量计算 `calculate_sample_count()`
- 增强错误处理和重试机制

**动态样本数量**：
```python
def calculate_sample_count(total_samples):
    if total_samples <= 10:
        return total_samples
    elif total_samples <= 100:
        return 10
    elif total_samples <= 1000:
        return 20
    else:
        return 30
```

**本地兜底机制**：
- 基于关键词的简单规则判断
- 编程相关：`code`, `python`, `function`, `algorithm` 等
- 推理相关：`calculate`, `solve`, `prove`, `math` 等
- 默认语言：其他情况

**修改文件**：
- `apps/datasets/services/ai_capability_judge.py`
- `apps/datasets/serializers_auto_verify.py`

### 5. 图片路径验证

**问题**：JSON中引用的图片路径不存在时只给出警告。

**解决方案**：
- 添加 `_validate_image_paths()` 方法严格验证
- 对图像数据集强制检查图片路径存在性
- 提供详细的缺失图片列表

**验证逻辑**：
```python
def _validate_image_paths(self, zip_file, json_data):
    zip_files = set(zip_file.namelist())
    missing_images = []
    
    for item in json_data:
        if 'image' in item:
            image_path = item['image']
            if image_path not in zip_files:
                missing_images.append(image_path)
    
    if missing_images:
        raise serializers.ValidationError(
            f"以下图片文件在ZIP中不存在: {', '.join(missing_images[:5])}"
            f"{'...' if len(missing_images) > 5 else ''}"
        )
```

**修改文件**：
- `apps/datasets/serializers_auto_verify.py`

## 测试覆盖

### 新增测试文件

创建了 `test_auto_verification_improvements.py` 来验证所有改进：

1. **ZIP安全性测试**：
   - 正常ZIP文件验证
   - 路径遍历攻击检测
   - 文件大小限制测试

2. **CSV字段映射测试**：
   - 标准字段名验证
   - 缺少必需字段检测

3. **能力分析测试**：
   - 动态样本数量计算
   - 本地兜底机制验证

4. **图片路径验证测试**：
   - 有效图片路径验证
   - 缺失图片路径检测

### 运行测试

```bash
cd PolyMetric/backend
python test_auto_verification_improvements.py
```

## 使用说明

### 1. 安装依赖

确保安装了新增的依赖：
```bash
pip install chardet
```

### 2. 配置更新

无需额外配置，改进已集成到现有系统中。

### 3. 使用方式

数据集上传方式保持不变，但具有更好的：
- 安全性保护
- 错误提示
- 处理可靠性

## 性能影响

### 改进点
1. **安全性提升**：防止恶意文件上传
2. **可靠性增强**：本地兜底机制
3. **用户体验**：更详细的错误信息
4. **维护性**：统一的验证机制

### 性能开销
1. **编码检测**：轻微增加CPU使用
2. **安全检查**：增加文件扫描时间
3. **动态样本**：根据数据集大小调整

总体影响：**轻微**，收益远大于成本。

## 向后兼容性

### 兼容性说明
- ✅ 现有API接口保持不变
- ✅ 数据库结构无需修改
- ✅ 现有数据集文件继续支持
- ✅ 前端无需修改

### 迁移指南
无需特殊迁移，系统会自动使用新的验证机制。

## 监控建议

### 关键指标
1. **上传成功率**：监控验证失败率
2. **安全拦截**：记录恶意文件尝试
3. **能力分析**：AI服务失败时的兜底使用率
4. **性能指标**：上传处理时间

### 日志记录
系统会自动记录以下事件：
- ZIP安全检查失败
- 编码检测失败
- 图片路径验证失败
- 本地兜底机制触发

## 后续优化建议

### 短期优化
1. 添加更多文件格式支持
2. 优化大文件处理性能
3. 增强错误恢复机制

### 长期规划
1. 实现文件内容扫描
2. 添加病毒检测
3. 支持分布式文件存储

## 总结

本次改进主要解决了数据集上传流程中的安全性和可靠性问题，通过统一验证机制、增强安全检查、优化处理逻辑，显著提升了系统的健壮性和用户体验。所有改进都经过了充分测试，确保向后兼容性和系统稳定性。