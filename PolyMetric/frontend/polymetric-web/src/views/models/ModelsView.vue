<template>
  <div class="model-square">
    <div class="hero">
      <div class="hero-left">
        <div class="title-row">
          <div class="badge">模型广场</div>
          <h2>大模型评测榜单</h2>
        </div>
        <p class="subtitle">按综合能力、类型与关注度发现模型，像榜单一样浏览。</p>
        <div class="hero-stats">
          <div class="stat-card">
            <div class="label">已收录</div>
            <div class="value">{{ filteredModels.length }}</div>
            <div class="hint">模型数量</div>
          </div>
          <div class="stat-card">
            <div class="label">已关注</div>
            <div class="value">{{ followedCount }}</div>
            <div class="hint">你的关注</div>
          </div>
          <div class="stat-card">
            <div class="label">类型覆盖</div>
            <div class="value">{{ categoryCount }}</div>
            <div class="hint">文本/多模态/代码等</div>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="mini-rank" v-if="rankedTop3.length">
          <div class="mini-title">Top 3</div>
          <div class="mini-item" v-for="item in rankedTop3" :key="item.id">
            <span class="mini-rank-num">#{{ item._rank }}</span>
            <div class="mini-info">
              <div class="mini-name">{{ item.name }}</div>
              <div class="mini-tags">
                <el-tag size="small" effect="dark" :type="getCategoryType(item.category)">
                  {{ getCategoryLabel(item.category) }}
                </el-tag>
                <el-tag size="small" effect="plain">{{ item.parameter_size || '参数未知' }}</el-tag>
              </div>
            </div>
            <el-button link type="primary" size="small" @click="showDetail(item)">详情</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索模型名称..."
          :prefix-icon="Search"
          clearable
          @input="handleLocalFilter"
          @clear="handleLocalFilter"
          class="filter-input"
        />
        <el-select
          v-model="categoryFilter"
          placeholder="选择类型"
          clearable
          @change="handleLocalFilter"
          class="filter-select"
        >
          <el-option label="全部类型" value="" />
          <el-option label="文本生成" value="text" />
          <el-option label="图像生成" value="image" />
          <el-option label="多模态" value="multimodal" />
          <el-option label="代码生成" value="code" />
        </el-select>
        <el-button :icon="Refresh" @click="resetFilter">重置</el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else>
      <el-empty v-if="filteredModels.length === 0" description="暂无模型" />

      <div v-else class="board-list">
        <div
          v-for="item in paginatedRankedModels"
          :key="item.id"
          class="board-row"
          :class="{ 'top-row': item._rank <= 3 }"
        >
          <div class="rank">
            <span>#{{ item._rank }}</span>
          </div>
          <div class="meta">
            <div class="name-line">
              <el-icon><Box /></el-icon>
              <span class="name">{{ item.name }}</span>
              <el-tag size="small" :type="getCategoryType(item.category)">{{ getCategoryLabel(item.category) }}</el-tag>
            </div>
            <div class="meta-sub">
              <span>{{ item.company || '未知机构' }}</span>
              <span class="dot" />
              <span>参数: {{ item.parameter_size || '未知' }}</span>
            </div>
          </div>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">关注</div>
              <div class="metric-value" :class="{ on: item.is_followed }">{{ item.is_followed ? '已关注' : '未关注' }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">最近更新</div>
              <div class="metric-value">{{ formatDate(item.updated_at) }}</div>
            </div>
          </div>
          <div class="actions">
            <el-button type="primary" size="small" @click="showDetail(item)">详情</el-button>
            <el-button
              :type="item.is_followed ? 'warning' : 'info'"
              size="small"
              :icon="item.is_followed ? StarFilled : Star"
              @click="handleToggleFollow(item)"
              :loading="item.followLoading"
            >
              {{ item.is_followed ? '已关注' : '关注' }}
            </el-button>
          </div>
        </div>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="filteredModels.length"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Box, Loading, Star, StarFilled } from '@element-plus/icons-vue'
import { getAllModels, getModelDetail, followModel, unfollowModel } from '@/api/models'

// 状态
const loading = ref(false)
const allModels = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(5)

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const dialogFollowLoading = ref(false)
const currentModel = ref(null)
const modelDetail = ref(null)

// 本地筛选后的模型
const filteredModels = computed(() => {
  let result = allModels.value
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    result = result.filter(item =>
      item.name.toLowerCase().includes(keyword) ||
      (item.company && item.company.toLowerCase().includes(keyword))
    )
  }
  if (categoryFilter.value) {
    result = result.filter(item => item.category === categoryFilter.value)
  }
  return result
})

// 榜单派生数据
const followedCount = computed(() => filteredModels.value.filter(item => item.is_followed).length)
const categoryCount = computed(() => {
  const set = new Set(filteredModels.value.map(item => item.category).filter(Boolean))
  return set.size
})
const rankedModels = computed(() => filteredModels.value.map((item, idx) => ({ ...item, _rank: idx + 1 })))
const paginatedRankedModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rankedModels.value.slice(start, end)
})
const rankedTop3 = computed(() => rankedModels.value.slice(0, 3))

// 监听筛选条件变化，重置到第一页
watch([searchQuery, categoryFilter], () => {
  currentPage.value = 1
})

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 切换每页条数时回到第一页
}

// 处理页码变化
const handlePageChange = (val) => {
  currentPage.value = val
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 分类英文转中文
const getCategoryLabel = (category) => {
  const labels = {
    'text': '文本生成',
    'image': '图像生成',
    'multimodal': '多模态',
    'code': '代码生成'
  }
  return labels[category] || category || '未分类'
}

const getCategoryType = (category) => {
  const types = {
    'text': 'primary',
    'image': 'success',
    'multimodal': 'warning',
    'code': 'info'
  }
  return types[category] || ''
}

// 从后端获取所有模型（带关注状态）
const fetchAllModels = async () => {
  loading.value = true
  try {
    const res = await getAllModels()
    // 后端返回格式: { code: 200, msg: "查询成功", data: [...] }
    let models = []
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      models = res.data.data
    } else if (Array.isArray(res.data)) {
      models = res.data
    }
    // 为每个模型添加 followLoading 状态
    allModels.value = models.map(item => ({
      ...item,
      is_followed: item.is_followed || false,
      followLoading: false
    }))
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error('获取模型列表失败')
    allModels.value = []
  } finally {
    loading.value = false
  }
}

// 本地筛选
const handleLocalFilter = () => {
  // 筛选由 computed 自动完成，页码重置由 watch 处理
}

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
  fetchAllModels()
}

// 切换关注状态（列表中）
const handleToggleFollow = async (row) => {
  // 从原始数组中找到对应的模型对象
  const originalItem = allModels.value.find(m => m.id === row.id)
  if (!originalItem) return
  
  originalItem.followLoading = true
  try {
    if (originalItem.is_followed) {
      // 取消关注
      const res = await unfollowModel(originalItem.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        originalItem.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      // 添加关注
      const res = await followModel(originalItem.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        originalItem.is_followed = true
        ElMessage.success('关注成功')
      } else {
        ElMessage.error(res.data?.msg || '关注失败')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    originalItem.followLoading = false
  }
}

// 切换关注状态（弹窗中）
const handleToggleFollowInDialog = async () => {
  if (!modelDetail.value) return
  
  dialogFollowLoading.value = true
  try {
    if (modelDetail.value.is_followed) {
      const res = await unfollowModel(modelDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        modelDetail.value.is_followed = false
        // 同步更新列表中的状态
        const item = allModels.value.find(m => m.id === modelDetail.value.id)
        if (item) item.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      const res = await followModel(modelDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        modelDetail.value.is_followed = true
        // 同步更新列表中的状态
        const item = allModels.value.find(m => m.id === modelDetail.value.id)
        if (item) item.is_followed = true
        ElMessage.success('关注成功')
      } else {
        ElMessage.error(res.data?.msg || '关注失败')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    dialogFollowLoading.value = false
  }
}

// 显示详情
const showDetail = async (row) => {
  currentModel.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  modelDetail.value = null
  
  try {
    const res = await getModelDetail(row.id)
    // 后端返回格式: { code: 200, msg: "查询成功", data: {...} }
    if (res.data?.code === 200 && res.data.data) {
      modelDetail.value = {
        ...res.data.data,
        is_followed: row.is_followed // 从列表中继承关注状态
      }
    } else {
      modelDetail.value = row
    }
  } catch (error) {
    console.error('获取模型详情失败:', error)
    ElMessage.error('获取详情失败')
    modelDetail.value = row
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  fetchAllModels()
})
</script>

<style scoped>
.model-square {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 50%, #f7fbff 100%);
  border-radius: 14px;
  box-shadow: 0 6px 24px rgba(31, 41, 61, 0.08);
  min-height: calc(100vh - 140px);
}

.hero {
  display: flex;
  gap: 18px;
  align-items: stretch;
  margin-bottom: 16px;
}

.hero-left {
  flex: 1;
  background: linear-gradient(120deg, #1f6bff 0%, #5f8bff 60%, #9ec5ff 100%);
  color: #fff;
  border-radius: 14px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
}

.hero-left::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -40px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(255,255,255,0.28), rgba(255,255,255,0));
  transform: rotate(-10deg);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  letter-spacing: 1px;
}

.hero-left h2 {
  margin: 0;
  font-size: 22px;
}

.subtitle {
  margin: 4px 0 14px;
  color: rgba(255,255,255,0.92);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-card {
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 12px;
  padding: 10px 12px;
  backdrop-filter: blur(2px);
}

.stat-card .label {
  font-size: 12px;
  opacity: 0.9;
}

.stat-card .value {
  font-size: 22px;
  font-weight: 700;
  margin: 6px 0 2px;
}

.stat-card .hint {
  font-size: 12px;
  opacity: 0.8;
}

.hero-right {
  width: 320px;
}

.mini-rank {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(18,38,63,0.12);
  padding: 14px;
  height: 100%;
}

.mini-title {
  font-weight: 700;
  margin-bottom: 10px;
  color: #1f2d3d;
}

.mini-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f2f8;
}

.mini-item:last-child {
  border-bottom: none;
}

.mini-rank-num {
  font-weight: 700;
  color: #1f6bff;
}

.mini-name {
  font-weight: 600;
  color: #1f2d3d;
}

.mini-tags {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.filter-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 8px 24px rgba(18, 38, 63, 0.06);
  margin-bottom: 14px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-input,
.filter-select {
  width: 260px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.board-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.board-row {
  display: grid;
  grid-template-columns: 80px 1.3fr 1fr 220px;
  gap: 16px;
  align-items: center;
  background: #ffffff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 8px 22px rgba(18, 38, 63, 0.06);
  border: 1px solid #eef2f9;
}

.board-row.top-row {
  border-color: #d8e6ff;
  box-shadow: 0 10px 28px rgba(31, 107, 255, 0.12);
}

.rank span {
  font-size: 20px;
  font-weight: 800;
  color: #1f6bff;
}

.meta .name-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta .name {
  font-size: 16px;
  font-weight: 700;
  color: #1f2d3d;
}

.meta-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #607086;
  margin-top: 6px;
  font-size: 13px;
}

.meta-sub .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d0d7e2;
  display: inline-block;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 12px;
}

.metric {
  background: #f6f8fb;
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #eef2f9;
}

.metric-label {
  font-size: 12px;
  color: #7a869a;
}

.metric-value {
  margin-top: 6px;
  font-weight: 700;
  color: #1f2d3d;
}

.metric-value.on {
  color: #1f8f4c;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 6px;
  padding: 8px 0 4px;
}

.dialog-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  color: #909399;
}

.detail-content {
  padding: 10px 0;
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>

