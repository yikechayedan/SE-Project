# PolyMetric Frontend

基于 Vue 3 + Vite + Element Plus 的前端应用

## 🚀 快速开始

### 安装依赖
\`\`\`bash
npm install
\`\`\`

### 开发模式
\`\`\`bash
npm run dev
\`\`\`

### 生产构建
\`\`\`bash
npm run build
\`\`\`

### 预览生产构建
\`\`\`bash
npm run preview
\`\`\`

## 📁 项目结构

\`\`\`
src/
├── api/              # API 接口定义
├── assets/           # 静态资源
├── components/       # 可复用组件
│   ├── common/       # 通用组件
│   ├── layout/       # 布局组件
│   └── profile/      # 个人资料组件
├── router/           # 路由配置
├── views/            # 页面视图
│   ├── auth/         # 认证相关
│   ├── datasets/     # 数据集
│   ├── evaluation/   # 评测
│   ├── models/       # 模型
│   └── profile/      # 个人中心
├── App.vue           # 根组件
├── main.js           # 入口文件
└── style.css         # 全局样式
\`\`\`

## 🛠️ 技术栈

- Vue 3.5+
- Vite 7+
- Element Plus 2.11+
- Vue Router 4+
- Axios 1.13+

## 📝 开发规范

- 组件使用 Composition API (\`<script setup>\`)
- 使用 ESLint 保持代码风格一致
- 遵循项目的 Git 提交规范

## 🔗 相关文档

- [API 文档](../../../docs/api/)
- [开发指南](../../../docs/dev/development-guide.md)
