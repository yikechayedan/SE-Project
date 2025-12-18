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
          <el-button type="primary" size="large" round :icon="Aim" @click="goToEvaluation">
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
          <span class="stat-label">模型总数</span>
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
          <span class="stat-label">
            用户总数
            <el-tag size="small" type="success" effect="plain" class="online-tag">
              {{ stats.onlineUserCount }} 在线
            </el-tag>
          </span>
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
            <div class="quick-item" @click="goToEvaluation">
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

        <!-- 最新动态 -->
        <el-card class="activity-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Bell /></el-icon>
              <span>最新动态</span>
            </div>
          </template>
          <el-timeline v-if="recentActivities.length > 0">
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
          <el-empty v-else description="暂无动态" :image-size="60" />
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

    <!-- 评测弹窗（保留作为备用） -->
    <EvalDialog v-model:showDialog="showEvalDialog" @close="showEvalDialog = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  TrophyBase, Aim, QuestionFilled, Box, Folder, Document, User, 
  Refresh, Medal, Top, Bottom, InfoFilled, ArrowRight, Grid,
  DataAnalysis, Bell
} from '@element-plus/icons-vue'
import EvalDialog from '../components/common/EvalDialog.vue'
import { getAllDatasets } from '@/api/datasets'
import { getAllModels } from '@/api/models'
import { getEvaluationTasks } from '@/api/tasks'
// import { getDashboardStats } from '@/api/system' // Removed as per instruction to not change backend

const router = useRouter()

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
  userCount: '-', // Placeholder until backend API is available
  onlineUserCount: 0
})

// 导航到评测页面
const goToEvaluation = () => {
  router.push('/evaluation')
}

// 获取真实统计数据
const fetchStats = async () => {
  try {
    // 并行获取所有统计数据
    const [modelsRes, datasetsRes, tasksRes] = await Promise.all([
      getAllModels().catch(() => null),
      getAllDatasets().catch(() => null),
      getEvaluationTasks().catch(() => null)
    ])
    
    // 处理模型数量
    if (modelsRes) {
      let models = []
      if (modelsRes.data?.code === 200 && Array.isArray(modelsRes.data.data)) {
        models = modelsRes.data.data
      } else if (Array.isArray(modelsRes.data)) {
        models = modelsRes.data
      }
      stats.value.modelCount = models.length
    }
    
    // 处理数据集数量
    if (datasetsRes) {
      let datasets = []
      if (datasetsRes.data?.code === 200 && Array.isArray(datasetsRes.data.data)) {
        datasets = datasetsRes.data.data
      } else if (Array.isArray(datasetsRes.data)) {
        datasets = datasetsRes.data
      }
      stats.value.datasetCount = datasets.length
    }
    
    // 处理任务数量
    if (tasksRes) {
      let tasks = []
      if (tasksRes.data?.code === 200 && Array.isArray(tasksRes.data.data)) {
        tasks = tasksRes.data.data
      } else if (Array.isArray(tasksRes.data)) {
        tasks = tasksRes.data
      } else if (tasksRes.data?.results && Array.isArray(tasksRes.data.results)) {
        tasks = tasksRes.data.results
      }
      stats.value.taskCount = tasks.length
    }
    
    // Note: User count and online user count require new backend APIs.
    // Keeping placeholders for now.
    
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取最新动态（从评测任务、数据集、模型中汇总）
const fetchRecentActivities = async () => {
  try {
    const activities = []
    
    // 获取最新的评测任务
    const tasksRes = await getEvaluationTasks().catch(() => null)
    if (tasksRes) {
      let tasks = []
      if (tasksRes.data?.code === 200 && Array.isArray(tasksRes.data.data)) {
        tasks = tasksRes.data.data
      } else if (Array.isArray(tasksRes.data)) {
        tasks = tasksRes.data
      } else if (tasksRes.data?.results && Array.isArray(tasksRes.data.results)) {
        tasks = tasksRes.data.results
      }
      
      // 取最新的几个任务
      tasks.slice(0, 3).forEach(task => {
        const statusText = task.status === 'completed' ? '完成' : 
                          task.status === 'running' ? '进行中' : 
                          task.status === 'failed' ? '失败' : '等待中'
        activities.push({
          content: `评测任务「${task.name || task.model_name || '未命名'}」${statusText}`,
          time: formatTime(task.created_at || task.updated_at),
          type: task.status === 'completed' ? 'success' : 
                task.status === 'failed' ? 'danger' : 'primary',
          timestamp: new Date(task.created_at || task.updated_at || Date.now()).getTime()
        })
      })
    }
    
    // 获取最新的数据集
    const datasetsRes = await getAllDatasets().catch(() => null)
    if (datasetsRes) {
      let datasets = []
      if (datasetsRes.data?.code === 200 && Array.isArray(datasetsRes.data.data)) {
        datasets = datasetsRes.data.data
      } else if (Array.isArray(datasetsRes.data)) {
        datasets = datasetsRes.data
      }
      
      // 取最新的几个数据集
      datasets.slice(0, 2).forEach(ds => {
        activities.push({
          content: `新增数据集「${ds.name || '未命名数据集'}」`,
          time: formatTime(ds.created_at || ds.upload_time),
          type: 'success',
          timestamp: new Date(ds.created_at || ds.upload_time || Date.now()).getTime()
        })
      })
    }
    
    // 获取最新的模型
    const modelsRes = await getAllModels().catch(() => null)
    if (modelsRes) {
      let models = []
      if (modelsRes.data?.code === 200 && Array.isArray(modelsRes.data.data)) {
        models = modelsRes.data.data
      } else if (Array.isArray(modelsRes.data)) {
        models = modelsRes.data
      }
      
      // 取最新的几个模型
      models.slice(0, 2).forEach(model => {
        activities.push({
          content: `新模型「${model.name}」已添加 (${model.company || '未知厂商'})`,
          time: formatTime(model.created_at),
          type: 'primary',
          timestamp: new Date(model.created_at || Date.now()).getTime()
        })
      })
    }
    
    // 按时间排序，取最新的 5 条
    activities.sort((a, b) => b.timestamp - a.timestamp)
    recentActivities.value = activities.slice(0, 5)
    
    // 如果没有真实数据，显示默认提示
    if (recentActivities.value.length === 0) {
      recentActivities.value = [
        { content: '欢迎使用 PolyMetric 大模型评测平台', time: '刚刚', type: 'primary' }
      ]
    }
    
  } catch (error) {
    console.error('获取最新动态失败:', error)
    recentActivities.value = [
      { content: '欢迎使用 PolyMetric 大模型评测平台', time: '刚刚', type: 'primary' }
    ]
  }
}

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return '刚刚'
  
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
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

// 最近活动（动态获取）
const recentActivities = ref([])

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
  fetchRecentActivities()
})
</script>

<style scoped>
.logged-home {
  padding: 0;
  background: transparent;
  min-height: 100%;
}

/* 欢迎横幅 */
.welcome-banner {
  background: var(--header-gradient);
  padding: 30px 40px;
  color: var(--text-primary);
  margin: -20px -20px 20px -20px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 100%;
  background: radial-gradient(circle at center, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.banner-text h1 {
  font-size: 28px;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
}

.banner-desc {
  margin: 0;
  opacity: 0.8;
  font-size: 15px;
  color: var(--text-secondary);
}

.banner-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  font-family: 'Inter', sans-serif;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.online-tag {
  border-radius: 10px;
  padding: 0 8px;
  height: 18px;
  line-height: 16px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
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
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.leaderboard-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.leaderboard-card :deep(.el-card__body) {
  padding: 0;
  background: var(--bg-body);
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
  color: var(--text-primary);
}

.header-icon {
  color: var(--accent-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Table Styles */
:deep(.el-table) {
  --el-table-bg-color: var(--bg-body);
  --el-table-tr-bg-color: var(--bg-body);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  --el-table-row-hover-bg-color: var(--bg-hover);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
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

.rank-icon.gold { color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
.rank-icon.silver { color: #c0c0c0; text-shadow: 0 0 10px rgba(192, 192, 192, 0.3); }
.rank-icon.bronze { color: #cd7f32; text-shadow: 0 0 10px rgba(205, 127, 50, 0.3); }

.rank-number {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  font-family: 'Share Tech Mono', monospace;
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
  color: var(--text-primary);
}

.model-company {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 趋势图标 */
.trend-up { color: var(--success-color); font-size: 18px; }
.trend-down { color: var(--danger-color); font-size: 18px; }
.trend-stable { color: var(--text-secondary); }

/* 表格行样式 */
:deep(.top-rank-row) {
  background-color: rgba(64, 158, 255, 0.05) !important;
}

:deep(.top-rank-row:hover) {
  background-color: rgba(64, 158, 255, 0.1) !important;
}

.leaderboard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 0 0 12px 12px;
}

/* 右侧区域 */
.side-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 快捷入口 */
.quick-actions-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.quick-actions-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}

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
  background: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-item:hover {
  background: var(--bg-hover);
  border-color: var(--accent-color);
  transform: translateY(-2px);
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary) !important; /* Override inline style */
}

.quick-item span {
  font-size: 13px;
  color: var(--text-secondary);
}

.quick-item:hover span {
  color: var(--text-primary);
}

/* 评测维度 */
.radar-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.radar-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}

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
  box-shadow: 0 0 5px currentColor;
}

.dimension-name {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 60px;
}

.dimension-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 活动卡片 */
.activity-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.activity-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}

.activity-card :deep(.el-card__body) {
  padding: 16px 20px;
}

:deep(.el-timeline-item__content) {
  color: var(--text-primary);
}

:deep(.el-timeline-item__timestamp) {
  color: var(--text-secondary);
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
  color: var(--text-primary);
}

.tutorial-body p {
  color: var(--text-secondary);
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
