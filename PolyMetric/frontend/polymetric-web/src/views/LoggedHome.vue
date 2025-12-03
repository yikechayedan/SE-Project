<template>
  <div class="logged-home">
    <!-- 顶部欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="banner-text">
          <h1>
            <el-icon><TrophyBase /></el-icon>
            PolyMetric 大模型评测榜单
          </h1>
          <p class="banner-desc">
            多维度、多场景的大语言模型综合能力评估平台
          </p>
        </div>
        <div class="banner-actions">
          <el-button type="primary" size="large" round :icon="Aim" @click="showEvalDialog = true">
            发起评测
          </el-button>
          <el-button size="large" round :icon="QuestionFilled" @click="showTutorial = true">
            使用指南
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon :size="28"><Box /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.modelCount }}</span>
          <span class="stat-label">已评测模型</span>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <el-icon :size="28"><Folder /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.datasetCount }}</span>
          <span class="stat-label">评测数据集</span>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <el-icon :size="28"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.taskCount }}</span>
          <span class="stat-label">评测任务</span>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <el-icon :size="28"><User /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.userCount }}</span>
          <span class="stat-label">活跃用户</span>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：排行榜 -->
      <div class="leaderboard-section">
        <el-card class="leaderboard-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon class="header-icon"><TrophyBase /></el-icon>
                <span>综合能力排行榜</span>
              </div>
              <div class="header-right">
                <el-select v-model="selectedDataset" placeholder="选择数据集" size="small" style="width: 140px;">
                  <el-option label="综合评测" value="comprehensive" />
                  <el-option label="语言理解" value="language" />
                  <el-option label="数学推理" value="math" />
                  <el-option label="代码能力" value="code" />
                  <el-option label="多模态" value="multimodal" />
                </el-select>
                <el-button :icon="Refresh" circle size="small" @click="refreshRankings" :loading="rankingLoading" />
              </div>
            </div>
          </template>

          <el-table 
            :data="rankings" 
            style="width: 100%;"
            :row-class-name="tableRowClassName"
            v-loading="rankingLoading"
          >
            <el-table-column label="排名" width="80" align="center">
              <template #default="{ row, $index }">
                <div class="rank-cell">
                  <el-icon v-if="$index === 0" class="rank-icon gold"><Medal /></el-icon>
                  <el-icon v-else-if="$index === 1" class="rank-icon silver"><Medal /></el-icon>
                  <el-icon v-else-if="$index === 2" class="rank-icon bronze"><Medal /></el-icon>
                  <span v-else class="rank-number">{{ $index + 1 }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="模型" min-width="180">
              <template #default="{ row }">
                <div class="model-cell">
                  <el-avatar :size="32" :style="{ background: row.color }">
                    {{ row.name.charAt(0) }}
                  </el-avatar>
                  <div class="model-info">
                    <span class="model-name">{{ row.name }}</span>
                    <span class="model-company">{{ row.company }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="综合得分" width="120" align="center">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.overallScore" 
                  :stroke-width="8"
                  :color="getScoreColor(row.overallScore)"
                  :format="() => row.overallScore.toFixed(1)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="languageScore" label="语言理解" width="90" align="center">
              <template #default="{ row }">
                <span :style="{ color: getScoreColor(row.languageScore) }">{{ row.languageScore.toFixed(1) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="reasoningScore" label="推理能力" width="90" align="center">
              <template #default="{ row }">
                <span :style="{ color: getScoreColor(row.reasoningScore) }">{{ row.reasoningScore.toFixed(1) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="codeScore" label="代码能力" width="90" align="center">
              <template #default="{ row }">
                <span :style="{ color: getScoreColor(row.codeScore) }">{{ row.codeScore.toFixed(1) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="趋势" width="80" align="center">
              <template #default="{ row }">
                <el-icon v-if="row.trend > 0" class="trend-up"><Top /></el-icon>
                <el-icon v-else-if="row.trend < 0" class="trend-down"><Bottom /></el-icon>
                <span v-else class="trend-stable">-</span>
              </template>
            </el-table-column>
          </el-table>

          <div class="leaderboard-footer">
            <el-text type="info" size="small">
              <el-icon><InfoFilled /></el-icon>
              数据更新时间：{{ lastUpdated }}
            </el-text>
            <el-button type="primary" link @click="$router.push('/models')">
              查看更多模型 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧：快捷入口和最新动态 -->
      <div class="side-section">
        <!-- 快捷入口 -->
        <el-card class="quick-actions-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Grid /></el-icon>
              <span>快捷入口</span>
            </div>
          </template>
          <div class="quick-grid">
            <div class="quick-item" @click="$router.push('/models')">
              <div class="quick-icon" style="background: #e8f4ff;">
                <el-icon :size="24" color="#409eff"><Box /></el-icon>
              </div>
              <span>模型广场</span>
            </div>
            <div class="quick-item" @click="$router.push('/datasets')">
              <div class="quick-icon" style="background: #e8fff0;">
                <el-icon :size="24" color="#67c23a"><Folder /></el-icon>
              </div>
              <span>数据集</span>
            </div>
            <div class="quick-item" @click="showEvalDialog = true">
              <div class="quick-icon" style="background: #fff0e8;">
                <el-icon :size="24" color="#e6a23c"><Aim /></el-icon>
              </div>
              <span>发起评测</span>
            </div>
            <div class="quick-item" @click="$router.push('/profile')">
              <div class="quick-icon" style="background: #f0e8ff;">
                <el-icon :size="24" color="#9b59b6"><User /></el-icon>
              </div>
              <span>个人中心</span>
            </div>
          </div>
        </el-card>

        <!-- 评测维度雷达图 -->
        <el-card class="radar-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><DataAnalysis /></el-icon>
              <span>评测维度说明</span>
            </div>
          </template>
          <div class="dimension-list">
            <div class="dimension-item">
              <div class="dimension-dot" style="background: #409eff;"></div>
              <span class="dimension-name">语言理解</span>
              <span class="dimension-desc">文本理解、阅读理解、语义分析</span>
            </div>
            <div class="dimension-item">
              <div class="dimension-dot" style="background: #67c23a;"></div>
              <span class="dimension-name">推理能力</span>
              <span class="dimension-desc">逻辑推理、数学计算、因果分析</span>
            </div>
            <div class="dimension-item">
              <div class="dimension-dot" style="background: #e6a23c;"></div>
              <span class="dimension-name">代码能力</span>
              <span class="dimension-desc">代码生成、代码理解、调试修复</span>
            </div>
            <div class="dimension-item">
              <div class="dimension-dot" style="background: #f56c6c;"></div>
              <span class="dimension-name">知识问答</span>
              <span class="dimension-desc">常识知识、专业知识、事实核查</span>
            </div>
            <div class="dimension-item">
              <div class="dimension-dot" style="background: #9b59b6;"></div>
              <span class="dimension-name">安全合规</span>
              <span class="dimension-desc">内容安全、伦理对齐、隐私保护</span>
            </div>
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card class="activity-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Bell /></el-icon>
              <span>最近动态</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item 
              v-for="(activity, index) in recentActivities" 
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
              placement="top"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>

    <!-- 使用教程弹窗 -->
    <el-dialog v-model="showTutorial" title="PolyMetric 使用指南" :draggable="true" width="650px">
      <div class="tutorial-content">
        <el-steps :active="tutorialStep" finish-status="success" align-center>
          <el-step title="浏览模型" />
          <el-step title="选择数据集" />
          <el-step title="发起评测" />
          <el-step title="查看结果" />
        </el-steps>
        <div class="tutorial-body">
          <div v-if="tutorialStep === 0">
            <el-icon :size="48" color="#409eff"><Box /></el-icon>
            <h3>第一步：浏览模型广场</h3>
            <p>在模型广场中，您可以浏览和搜索各类大语言模型，查看模型详情和历史评测成绩。支持按类型筛选：文本生成、图像生成、多模态、代码生成等。</p>
          </div>
          <div v-else-if="tutorialStep === 1">
            <el-icon :size="48" color="#67c23a"><Folder /></el-icon>
            <h3>第二步：选择评测数据集</h3>
            <p>在数据集广场中，选择适合您评测需求的数据集。您也可以上传自定义数据集，支持 CSV、JSON、ZIP 格式。</p>
          </div>
          <div v-else-if="tutorialStep === 2">
            <el-icon :size="48" color="#e6a23c"><Aim /></el-icon>
            <h3>第三步：创建评测任务</h3>
            <p>点击"发起评测"按钮，选择要评测的模型和数据集，配置评测参数后提交。系统将自动执行评测并生成结果。</p>
          </div>
          <div v-else>
            <el-icon :size="48" color="#9b59b6"><TrophyBase /></el-icon>
            <h3>第四步：查看评测结果</h3>
            <p>评测完成后，您可以在任务列表中查看详细结果。模型成绩将自动更新到排行榜，与其他模型进行对比。</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="tutorialStep = Math.max(0, tutorialStep - 1)" :disabled="tutorialStep === 0">上一步</el-button>
        <el-button v-if="tutorialStep < 3" type="primary" @click="tutorialStep++">下一步</el-button>
        <el-button v-else type="success" @click="showTutorial = false; tutorialStep = 0">开始使用</el-button>
      </template>
    </el-dialog>

    <!-- 评测弹窗 -->
    <EvalDialog v-model:showDialog="showEvalDialog" @close="showEvalDialog = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  TrophyBase, Aim, QuestionFilled, Box, Folder, Document, User, 
  Refresh, Medal, Top, Bottom, InfoFilled, ArrowRight, Grid,
  DataAnalysis, Bell
} from '@element-plus/icons-vue'
import EvalDialog from '../components/common/EvalDialog.vue'
import { getAllDatasets } from '@/api/datasets'

// 状态
const showTutorial = ref(false)
const tutorialStep = ref(0)
const showEvalDialog = ref(false)
const selectedDataset = ref('comprehensive')
const rankingLoading = ref(false)

// 统计数据
const stats = ref({
  modelCount: 0,
  datasetCount: 0,
  taskCount: 0,
  userCount: 0
})

// 获取真实数据集数量
const fetchStats = async () => {
  try {
    const res = await getAllDatasets()
    let datasets = []
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasets = res.data.data
    } else if (Array.isArray(res.data)) {
      datasets = res.data
    }
    stats.value.datasetCount = datasets.length
    // 其他数据暂时使用模拟值（等待后端 API）
    stats.value.modelCount = 12
    stats.value.taskCount = 156
    stats.value.userCount = 89
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用默认值
    stats.value = { modelCount: 12, datasetCount: 8, taskCount: 156, userCount: 89 }
  }
}

// 排行榜数据（模拟数据，等待后端 API 实现）
const rankings = ref([
  { 
    name: 'GPT-4o', company: 'OpenAI', color: '#10a37f',
    overallScore: 92.5, languageScore: 94.2, reasoningScore: 91.8, codeScore: 93.1, trend: 0
  },
  { 
    name: 'Claude 3.5 Sonnet', company: 'Anthropic', color: '#d97757',
    overallScore: 91.2, languageScore: 93.5, reasoningScore: 90.1, codeScore: 91.8, trend: 1
  },
  { 
    name: 'Gemini 1.5 Pro', company: 'Google', color: '#4285f4',
    overallScore: 89.8, languageScore: 91.2, reasoningScore: 88.5, codeScore: 90.2, trend: 1
  },
  { 
    name: '文心一言 4.0', company: '百度', color: '#2932e1',
    overallScore: 87.3, languageScore: 89.1, reasoningScore: 85.6, codeScore: 86.9, trend: 0
  },
  { 
    name: '通义千问 2.5', company: '阿里云', color: '#ff6a00',
    overallScore: 86.5, languageScore: 88.3, reasoningScore: 84.2, codeScore: 87.1, trend: -1
  },
  { 
    name: 'GLM-4', company: '智谱AI', color: '#1e50a2',
    overallScore: 85.2, languageScore: 87.1, reasoningScore: 83.5, codeScore: 85.8, trend: 1
  },
  { 
    name: 'Llama 3.1 405B', company: 'Meta', color: '#0866ff',
    overallScore: 84.8, languageScore: 86.5, reasoningScore: 82.9, codeScore: 85.2, trend: 0
  },
  { 
    name: 'Mistral Large 2', company: 'Mistral AI', color: '#f54e42',
    overallScore: 83.6, languageScore: 85.2, reasoningScore: 81.8, codeScore: 84.1, trend: -1
  }
])

// 最近活动
const recentActivities = ref([
  { content: 'GPT-4o 完成了新一轮综合评测', time: '10 分钟前', type: 'primary' },
  { content: '新增数据集「中文逻辑推理v2」', time: '1 小时前', type: 'success' },
  { content: 'Claude 3.5 排名上升 1 位', time: '3 小时前', type: 'warning' },
  { content: '系统完成 23 个模型的批量评测', time: '昨天', type: 'info' }
])

// 最后更新时间
const lastUpdated = computed(() => {
  const now = new Date()
  return now.toLocaleString('zh-CN', { 
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' 
  })
})

// 刷新排行榜
const refreshRankings = () => {
  rankingLoading.value = true
  setTimeout(() => {
    rankingLoading.value = false
    ElMessage.success('排行榜已更新')
  }, 800)
}

// 表格行样式
const tableRowClassName = ({ rowIndex }) => {
  if (rowIndex < 3) return 'top-rank-row'
  return ''
}

// 根据分数获取颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.logged-home {
  padding: 0;
  background: #f5f7fa;
  min-height: 100%;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px 40px;
  color: white;
  margin: -20px -20px 20px -20px;
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.banner-text h1 {
  font-size: 28px;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.banner-desc {
  margin: 0;
  opacity: 0.9;
  font-size: 15px;
}

.banner-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  gap: 16px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;
  padding: 0 20px 20px;
}

/* 排行榜 */
.leaderboard-section {
  min-width: 0;
}

.leaderboard-card {
  background: white;
  border-radius: 12px;
}

.leaderboard-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.leaderboard-card :deep(.el-card__body) {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-icon {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 排名单元格 */
.rank-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.rank-icon {
  font-size: 24px;
}

.rank-icon.gold { color: #ffd700; }
.rank-icon.silver { color: #c0c0c0; }
.rank-icon.bronze { color: #cd7f32; }

.rank-number {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
}

/* 模型单元格 */
.model-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-info {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: 600;
  color: #303133;
}

.model-company {
  font-size: 12px;
  color: #909399;
}

/* 趋势图标 */
.trend-up { color: #67c23a; font-size: 18px; }
.trend-down { color: #f56c6c; font-size: 18px; }
.trend-stable { color: #909399; }

/* 表格行样式 */
:deep(.top-rank-row) {
  background-color: #fafafa;
}

.leaderboard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid #ebeef5;
}

/* 右侧区域 */
.side-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 快捷入口 */
.quick-actions-card :deep(.el-card__body) {
  padding: 16px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-item:hover {
  background: #f0f2f5;
  transform: translateY(-2px);
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-item span {
  font-size: 13px;
  color: #606266;
}

/* 评测维度 */
.dimension-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dimension-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.dimension-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.dimension-name {
  font-weight: 500;
  color: #303133;
  min-width: 60px;
}

.dimension-desc {
  font-size: 12px;
  color: #909399;
}

/* 活动卡片 */
.activity-card :deep(.el-card__body) {
  padding: 16px 20px;
}

/* 教程弹窗 */
.tutorial-content {
  padding: 10px 0;
}

.tutorial-body {
  text-align: center;
  padding: 30px 20px;
}

.tutorial-body h3 {
  margin: 16px 0 12px;
  color: #303133;
}

.tutorial-body p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* 响应式 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .side-section {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
  
  .activity-card {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .banner-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .side-section {
    grid-template-columns: 1fr;
  }
  
  .activity-card {
    grid-column: span 1;
  }
}
</style>
