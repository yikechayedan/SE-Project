#!/bin/bash
# ================================
# SE-Project 文件结构重构脚本
# ================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  SE-Project 文件结构重构"
echo "=========================================="
echo ""

# 检查 Git 状态
if [ -d .git ]; then
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${YELLOW}警告: 有未提交的更改${NC}"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "重构已取消"
            exit 1
        fi
    fi
fi

echo "步骤 1/7: 创建新目录结构..."
mkdir -p docs/api docs/dev docs/deployment
mkdir -p tests/fixtures tests/integration  
mkdir -p scripts
echo -e "${GREEN}✓ 目录创建完成${NC}"

echo ""
echo "步骤 2/7: 移动 API 文档..."
[ -f PolyMetric/dataset-api.txt ] && mv PolyMetric/dataset-api.txt docs/api/datasets-api.md
[ -f PolyMetric/models_api.md ] && mv PolyMetric/models_api.md docs/api/models-api.md
[ -f PolyMetric/tasks-api.txt ] && mv PolyMetric/tasks-api.txt docs/api/tasks-api.md
[ -f PolyMetric/need_api.txt ] && mv PolyMetric/need_api.txt docs/api/requirements.md
echo -e "${GREEN}✓ API 文档移动完成${NC}"

echo ""
echo "步骤 3/7: 移动开发文档..."
[ -f PolyMetric/git_specification.pdf ] && mv PolyMetric/git_specification.pdf docs/dev/
[ -f PolyMetric/会议文档.txt ] && mv PolyMetric/会议文档.txt docs/dev/meeting-notes.md
[ -f PolyMetric/backendstart.txt ] && mv PolyMetric/backendstart.txt docs/dev/backend-startup.md
echo -e "${GREEN}✓ 开发文档移动完成${NC}"

echo ""
echo "步骤 4/7: 移动测试数据..."
[ -f book.json ] && mv book.json tests/fixtures/
[ -f test_dataset.json ] && mv test_dataset.json tests/fixtures/
echo -e "${GREEN}✓ 测试数据移动完成${NC}"

echo ""
echo "步骤 5/7: 删除冗余文件..."
[ -f PolyMetric/frontend/package.json ] && rm PolyMetric/frontend/package.json && echo "  - 删除 frontend/package.json"
[ -f PolyMetric/frontend/package-lock.json ] && rm PolyMetric/frontend/package-lock.json && echo "  - 删除 frontend/package-lock.json"
[ -f PolyMetric/frontend/README.md ] && rm PolyMetric/frontend/README.md && echo "  - 删除 README.md"
echo -e "${GREEN}✓ 冗余文件清理完成${NC}"

echo ""
echo "步骤 6/7: 创建 .gitignore（如果不存在）..."
if [ ! -f .gitignore ]; then
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/
*.log

# Django
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
*.log

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local

# Test
.coverage
htmlcov/
.pytest_cache/

# Logs
logs/
*.log
GITIGNORE
    echo -e "${GREEN}✓ .gitignore 创建完成${NC}"
else
    echo -e "${YELLOW}  .gitignore 已存在，跳过${NC}"
fi

echo ""
echo "步骤 7/7: 创建前端 README..."
cat > PolyMetric/frontend/README.md << 'FRONTEND_README'
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
FRONTEND_README
echo -e "${GREEN}✓ 前端 README 创建完成${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}  重构完成！${NC}"
echo "=========================================="
echo ""
echo "重构摘要:"
echo "  ✓ 创建了 docs/ 目录结构"
echo "  ✓ 创建了 tests/ 目录结构"
echo "  ✓ 创建了 scripts/ 目录"
echo "  ✓ 移动了 API 文档到 docs/api/"
echo "  ✓ 移动了开发文档到 docs/dev/"
echo "  ✓ 移动了测试数据到 tests/fixtures/"
echo "  ✓ 删除了冗余的 package.json"
echo "  ✓ 创建了 .gitignore 和前端 README"
echo ""
echo "下一步:"
echo "  1. 查看新的目录结构"
echo "  2. 测试前后端是否正常运行"
echo "  3. 提交更改: git add . && git commit -m 'refactor: 优化项目文件结构'"
echo ""

