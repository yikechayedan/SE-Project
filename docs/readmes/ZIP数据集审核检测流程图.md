# ZIP数据集审核检测流程图

## 整体流程图

```mermaid
graph TD
    A[用户上传ZIP数据集] --> B{文件格式验证}
    B -->|通过| C[ZIP文件结构验证]
    B -->|失败| D[返回错误信息]
    
    C --> E{查找JSON数据文件}
    E -->|找到| F[提取并解析JSON数据]
    E -->|未找到| G[返回错误: ZIP中未找到JSON文件]
    
    F --> H{测评类型特定验证}
    H -->|通过| I[图片文件验证与统计]
    H -->|失败| D
    
    I --> J[创建数据集记录]
    J --> K[设置初始状态: is_verified=false, capability_tag=processing]
    K --> L[触发异步能力分析任务]
    L --> M[等待管理员审核]
    
    M --> N{验证结果处理}
    N -->|验证通过| O[设置is_verified=true]
    N -->|验证失败| P[保持is_verified=false]
    
    O --> Q{能力分析状态}
    Q -->|processing| R[继续分析中]
    Q -->|no_file| S[标记为文件缺失]
    Q -->|no_samples| T[标记为无有效样本]
    Q -->|analysis_failed| U[标记为分析失败]
    Q -->|language/reasoning/coding| V[分析完成]
    
    R --> W[前端轮询状态]
    S --> W
    T --> W
    U --> W
    V --> X[数据集可用]
    W --> Y{状态检查}
    Y -->|处理完成| X
    Y -->|处理中| W
```

## ZIP文件解析流程

```mermaid
graph TD
    A[开始解析ZIP文件] --> B[读取ZIP文件内容]
    B --> C[扫描文件列表]
    C --> D{查找JSON文件}
    
    D -->|找到多个| E{是否有data.json}
    D -->|只找到一个| F[使用找到的JSON文件]
    D -->|未找到| G[返回错误: 未找到JSON文件]
    
    E -->|有| H[使用data.json]
    E -->|无| I[使用第一个JSON文件]
    
    F --> J[读取JSON文件内容]
    H --> J
    I --> J
    
    J --> K{JSON格式是否有效}
    K -->|有效| L[解析JSON结构]
    K -->|无效| M[返回错误: JSON格式错误]
    
    L --> N{数据结构类型}
    N -->|直接数组| O[使用数组数据]
    N -->|对象包含数组| P[查找数据数组键]
    N -->|测评类型结构| Q[使用测评类型数据]
    N -->|单个对象| R[包装为数组]
    
    P --> S{是否找到数据数组}
    S -->|是| T[使用找到的数组]
    S -->|否| U[返回错误: 无有效数据]
    
    O --> V[返回解析结果]
    Q --> V
    R --> V
    T --> V
```

## 图片处理流程

```mermaid
graph TD
    A[开始处理图片] --> B[扫描ZIP中的图片文件]
    B --> C[识别图片格式]
    C --> D[统计图片数量]
    D --> E[记录图片路径]
    
    E --> F[验证JSON中的图片引用]
    F --> G{图片路径是否存在}
    
    G -->|存在| H[记录图片信息]
    G -->|不存在| I[记录警告信息]
    
    H --> J[设置has_images=true]
    I --> J
    J --> K[更新image_count]
    
    K --> L[图片处理完成]
```

## 测评类型验证流程

```mermaid
graph TD
    A[ZIP测评类型验证] --> B{测评类型}
    B -->|subjective| C[主观测评验证]
    B -->|objective| D[客观测评验证]
    B -->|adversarial| E[对抗测评验证]
    
    C --> F{是否包含input和reference}
    F -->|是| G{是否包含image字段}
    F -->|否| H[返回字段缺失错误]
    
    G -->|是| I[验证字段内容非空]
    G -->|否| J[记录警告但继续]
    
    I --> K{验证是否通过}
    K -->|是| L[验证通过]
    K -->|否| M[返回内容错误]
    
    D --> N{是否包含input和answer}
    N -->|是| O{是否包含image字段}
    N -->|否| H
    
    O -->|是| P[验证字段内容非空]
    O -->|否| J
    
    P --> Q{验证是否通过}
    Q -->|是| L
    Q -->|否| M
    
    E --> R{是否包含input}
    R -->|是| S{是否包含image字段}
    R -->|否| H
    
    S -->|是| T[验证字段内容非空]
    S -->|否| J
    
    T --> U{验证是否通过}
    U -->|是| L
    U -->|否| M
    
    J --> V[继续处理]
    L --> W[验证完成]
    M --> X[返回验证错误]
```

## ZIP特有能力分析流程

```mermaid
graph TD
    A[触发ZIP数据集能力分析] --> B{数据集是否存在}
    B -->|不存在| C[返回错误: 数据集不存在]
    B -->|存在| D{是否已有能力标签且不是processing}
    D -->|是| E[返回已有标签]
    D -->|否| F{数据集是否有文件}
    
    F -->|否| G[设置capability_tag=no_file]
    F -->|是| H[读取ZIP文件]
    
    H --> I{ZIP解析是否成功}
    I -->|失败| J[设置capability_tag=analysis_failed]
    I -->|成功| K[查找JSON文件]
    
    K --> L{是否找到JSON文件}
    L -->|否| M[设置capability_tag=no_samples]
    L -->|是| N[提取JSON数据]
    
    N --> O{JSON解析是否成功}
    O -->|失败| M
    O -->|成功| P[抽取前5条数据]
    
    P --> Q{抽样是否成功}
    Q -->|否| M
    Q -->|是| R[调用AI判断能力维度]
    
    R --> S{AI调用是否成功}
    S -->|失败| T[设置capability_tag=analysis_failed]
    S -->|成功| U{返回结果是否有效}
    U -->|无效| V[使用默认值: language]
    U -->|有效| W[更新capability_tag和能力维度]
    
    G --> X[保存错误信息到描述]
    J --> X
    M --> X
    T --> X
    V --> X
    W --> Y[返回成功信息]
```

## 图片访问流程

```mermaid
graph TD
    A[用户请求图片] --> B[验证数据集存在]
    B -->|不存在| C[返回404错误]
    B -->|存在| D[检查数据集是否有文件]
    
    D -->|无文件| E[返回404错误]
    D -->|有文件| F[检查数据集是否包含图片]
    
    F -->|无图片| G[返回404错误]
    F -->|有图片| H[获取图片文件名参数]
    
    H --> I{文件名参数是否存在}
    I -->|否| J[返回400错误]
    I -->|是| K[打开ZIP文件]
    
    K --> L{图片文件是否存在于ZIP中}
    L -->|不存在| M[返回404错误]
    L -->|存在| N[检查文件是否为图片]
    
    N -->|不是图片| O[返回400错误]
    N -->|是图片| P[提取图片文件]
    
    P --> Q[读取图片二进制数据]
    Q --> R[根据扩展名确定Content-Type]
    R --> S[返回图片响应]
```

## ZIP文件结构示例

```mermaid
graph TD
    A[ZIP文件结构] --> B{结构类型}
    
    B -->|标准结构| C[
        dataset.zip<br/>
        ├── data.json<br/>
        ├── image1.jpg<br/>
        ├── image2.png<br/>
        └── images/<br/>
            ├── image3.jpg<br/>
            └── subdir/<br/>
                └── image4.png
    ]
    
    B -->|多JSON结构| D[
        dataset.zip<br/>
        ├── metadata.json<br/>
        ├── data.json<br/>
        └── images.json<br/>
    ]
    
    B -->|目录结构| E[
        dataset.zip<br/>
        ├── data/<br/>
        │   ├── samples.json<br/>
        │   └── images/<br/>
        │       ├── img1.jpg<br/>
        │       └── img2.png<br/>
        └── config/<br/>
            └── settings.json<br/>
    ]
    
    C --> F[系统会优先使用data.json]
    D --> F
    E --> G[系统会查找data目录下的JSON文件]
```

## 错误处理流程

```mermaid
graph TD
    A[ZIP处理发生错误] --> B{错误类型}
    B -->|ZIP格式错误| C[返回ZIP格式错误信息]
    B -->|JSON解析错误| D[返回JSON格式错误信息]
    B -->|字段验证错误| E[返回字段缺失或格式错误]
    B -->|图片路径错误| F[记录警告但继续处理]
    B -->|能力分析错误| G[记录错误日志]
    B -->|系统错误| H[记录详细错误信息]
    
    C --> I[建议用户检查ZIP文件完整性]
    D --> J[建议用户检查JSON格式]
    E --> K[返回具体字段或格式问题]
    F --> L[在数据集描述中记录警告]
    G --> M{是否可重试}
    H --> M
    
    M -->|是| N[自动重试最多3次]
    M -->|否| O[标记为失败状态]
    
    N --> P{重试是否成功}
    P -->|成功| Q[继续正常流程]
    P -->|失败| R[达到重试上限]
    
    R --> O
    O --> S[更新数据集描述中的错误信息]
    S --> T[通知用户处理失败]