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
          <div class="stat-card type-total">
            <div class="label">已收录</div>
            <div class="value">{{ allModels.length }}</div>
            <div class="hint">模型数量</div>
          </div>
          <div class="stat-card type-star">
            <div class="label">总点赞</div>
            <div class="value">{{ totalStars }}</div>
            <div class="hint">全站热度</div>
          </div>
          <div class="stat-card type-followed">
            <div class="label">已关注</div>
            <div class="value">{{ followedCount }}</div>
            <div class="hint">你的关注</div>
          </div>
          <div class="stat-card type-text">
            <div class="label">文本生成</div>
            <div class="value">{{ textModelCount }}</div>
            <div class="hint">Text</div>
          </div>
          <div class="stat-card type-image">
            <div class="label">生成图像</div>
            <div class="value">{{ imageModelCount }}</div>
            <div class="hint">Image</div>
          </div>
          <div class="stat-card type-multi">
            <div class="label">多模态识别</div>
            <div class="value">{{ multiModelCount }}</div>
            <div class="hint">Multi</div>
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
                <span class="mini-star"><el-icon><StarFilled /></el-icon>{{ item.star_count }}</span>
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
          <el-option label="生成图像" value="image" />
          <el-option label="多模态识别" value="multimodal" />
        </el-select>
        <el-select
          v-model="companyFilter"
          placeholder="选择机构"
          clearable
          filterable
          @change="handleLocalFilter"
          class="filter-select"
        >
          <el-option label="全部机构" value="" />
          <el-option 
            v-for="comp in availableCompanies" 
            :key="comp" 
            :label="comp" 
            :value="comp" 
          />
        </el-select>
        <el-checkbox v-model="onlyFollowed" label="仅看已关注" border />
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
              <div class="metric-label">点赞热度</div>
              <div class="metric-value star-val">
                <el-icon><StarFilled /></el-icon>
                <span>{{ item.star_count }}</span>
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">最近更新</div>
              <div class="metric-value">{{ formatDate(item.updated_at) }}</div>
            </div>
          </div>
          <div class="actions">
            <el-button type="primary" size="small" @click="showDetail(item)">详情</el-button>
            <el-button
              type="primary"
              plain
              size="small"
              :icon="ChatDotRound"
              @click="handleShowComments(item)"
            >
              评论
            </el-button>
            <el-button
              :type="item.is_starred ? 'danger' : 'default'"
              size="small"
              :icon="item.is_starred ? StarFilled : Star"
              @click="handleToggleStar(item)"
              :loading="item.starLoading"
              class="star-btn"
            >
              {{ item.is_starred ? '已点赞' : '点赞' }}
            </el-button>
            <el-button
              :type="item.is_followed ? 'warning' : 'info'"
              size="small"
              :icon="item.is_followed ? Opportunity : Star"
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

  <!-- 评论组件 -->
  <CommentSection
    v-model="showCommentDialog"
    target-type="model"
    :target-id="currentCommentModelId"
  />

    <!-- 模型详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      :title="currentModel?.name" 
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="detailLoading" class="dialog-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载详情中...</span>
      </div>
      
      <div class="detail-content" v-else-if="modelDetail">
        <div class="detail-header-stats">
           <div class="d-stat">
              <span class="label">热度</span>
              <span class="value"><el-icon><StarFilled /></el-icon> {{ modelDetail.star_count }}</span>
           </div>
        </div>
        <el-descriptions :column="2" border size="default">
          <el-descriptions-item label="模型名称">{{ modelDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="公司/组织">{{ modelDetail.company || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :type="getCategoryType(modelDetail.category)" size="small">
              {{ getCategoryLabel(modelDetail.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本">{{ modelDetail.version || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="参数量">{{ modelDetail.parameters || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="发布日期">{{ formatDate(modelDetail.release_date) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(modelDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(modelDetail.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ modelDetail.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          :type="modelDetail?.is_starred ? 'danger' : 'default'" 
          :icon="modelDetail?.is_starred ? StarFilled : Star"
          @click="handleToggleStarInDialog"
          :loading="dialogStarLoading"
        >
          {{ modelDetail?.is_starred ? '取消点赞' : '点赞' }}
        </el-button>
        <el-button 
          :type="modelDetail?.is_followed ? 'warning' : 'info'" 
          :icon="modelDetail?.is_followed ? Opportunity : Star"
          @click="handleToggleFollowInDialog"
          :loading="dialogFollowLoading"
        >
          {{ modelDetail?.is_followed ? '取消关注' : '关注' }}
        </el-button>
      </template>
    </el-dialog>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Box, Loading, Star, StarFilled, Opportunity, ChatDotRound } from '@element-plus/icons-vue'
import { getAllModels, getModelDetail, followModel, unfollowModel, starModel, unstarModel } from '@/api/models'
import CommentSection from '@/components/common/CommentSection.vue'

// 状态
const loading = ref(false)
const allModels = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const companyFilter = ref('')
const onlyFollowed = ref(false)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(5)

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const dialogFollowLoading = ref(false)
const dialogStarLoading = ref(false)
const currentModel = ref(null)
const modelDetail = ref(null)

// 评论弹窗
const showCommentDialog = ref(false)
const currentCommentModelId = ref(null)

// 显示评论
const handleShowComments = (row) => {
  currentCommentModelId.value = row.id
  showCommentDialog.value = true
}

// 提取所有公司
const availableCompanies = computed(() => {
  const companies = new Set(allModels.value.map(m => m.company).filter(Boolean))
  return Array.from(companies).sort()
})

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
  if (companyFilter.value) {
    result = result.filter(item => item.company === companyFilter.value)
  }
  if (onlyFollowed.value) {
    result = result.filter(item => item.is_followed)
  }
  return result
})

// 榜单派生数据
const followedCount = computed(() => allModels.value.filter(item => item.is_followed).length)
const totalStars = computed(() => allModels.value.reduce((acc, m) => acc + (m.star_count || 0), 0))

// 各类型数量统计 (基于所有模型)
const textModelCount = computed(() => allModels.value.filter(m => m.category === 'text').length)
const imageModelCount = computed(() => allModels.value.filter(m => m.category === 'image').length)
const multiModelCount = computed(() => allModels.value.filter(m => m.category === 'multimodal').length)

const rankedModels = computed(() => filteredModels.value.map((item, idx) => ({ ...item, _rank: idx + 1 })))
const paginatedRankedModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rankedModels.value.slice(start, end)
})

// Top 3 逻辑：按点赞量降序取前三
const rankedTop3 = computed(() => {
  const sortedByStars = [...allModels.value].sort((a, b) => (b.star_count || 0) - (a.star_count || 0))
  return sortedByStars.slice(0, 3).map((item, idx) => ({ ...item, _rank: idx + 1 }))
})

// 监听筛选条件变化，重置到第一页
watch([searchQuery, categoryFilter, companyFilter, onlyFollowed], () => {
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
    'image': '生成图像',
    'multimodal': '多模态识别'
  }
  return labels[category] || category || '未分类'
}

const getCategoryType = (category) => {
  const types = {
    'text': 'primary',
    'image': 'success',
    'multimodal': 'warning'
  }
  return types[category] || ''
}

// 参数量解析辅助函数
const parseParamValue = (str) => {
  if (!str) return 0
  const s = str.toString().toUpperCase()
  let mult = 1
  if (s.includes('B')) mult = 1e9
  else if (s.includes('M')) mult = 1e6
  else if (s.includes('K')) mult = 1e3
  
  // 处理 8x7B 这种情况
  if (s.includes('X')) {
    const parts = s.split('X')
    if (parts.length >= 2) {
      const a = parseFloat(parts[0])
      const b = parseFloat(parts[1])
      if (!isNaN(a) && !isNaN(b)) {
        return a * b * mult // 假设单位在最后
      }
    }
  }
  
  const num = parseFloat(s)
  return isNaN(num) ? 0 : num * mult
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
    
    // 预处理数据
    models = models.map(item => ({
      ...item,
      is_followed: item.is_followed || false,
      is_starred: item.is_starred || false,
      star_count: item.star_count || 0,
      followLoading: false,
      starLoading: false
    }))

    // 默认排序：
    // 1. 关注的模型在前
    // 2. 点赞量高的在前
    // 3. 参数量大的模型在前
    // 4. 更新时间较早的原则 (Ascending date)
    models.sort((a, b) => {
      // 1. Followed
      if (a.is_followed !== b.is_followed) {
        return a.is_followed ? -1 : 1
      }
      
      // 2. Star Count (High to Low)
      const starsA = a.star_count || 0
      const starsB = b.star_count || 0
      if (starsA !== starsB) {
        return starsB - starsA
      }
      
      // 3. Parameters (Large first)
      const paramA = parseParamValue(a.parameter_size)
      const paramB = parseParamValue(b.parameter_size)
      if (Math.abs(paramA - paramB) > 1e3) { // Use a small epsilon or just check inequality
         return paramB - paramA
      }
      
      // 4. Updated At (Earlier first -> Ascending)
      // "较早" means older date (smaller timestamp)
      const dateA = new Date(a.updated_at || 0).getTime()
      const dateB = new Date(b.updated_at || 0).getTime()
      return dateA - dateB
    })

    allModels.value = models
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
  companyFilter.value = ''
  onlyFollowed.value = false
  currentPage.value = 1
  fetchAllModels()
}

// 切换点赞状态
const handleToggleStar = async (row) => {
  const originalItem = allModels.value.find(m => m.id === row.id)
  if (!originalItem) return
  
  originalItem.starLoading = true
  try {
    if (originalItem.is_starred) {
      const res = await unstarModel(originalItem.id)
      if (res.data?.code === 200) {
        originalItem.is_starred = false
        // 后端应返回更新后的数量，如果没返回则前端估算
        originalItem.star_count = res.data.data?.star_count ?? (originalItem.star_count - 1)
        ElMessage.success('已取消点赞')
      }
    } else {
      const res = await starModel(originalItem.id)
      if (res.data?.code === 201 || res.data?.code === 200) {
        originalItem.is_starred = true
        originalItem.star_count = res.data.data?.star_count ?? (originalItem.star_count + 1)
        ElMessage.success('感谢点赞！')
      }
    }
  } catch (error) {
    if (error.response?.status === 401) ElMessage.warning('请先登录')
    else ElMessage.error('操作失败')
  } finally {
    originalItem.starLoading = false
  }
}

const handleToggleStarInDialog = async () => {
  if (!modelDetail.value) return
  dialogStarLoading.value = true
  try {
    if (modelDetail.value.is_starred) {
      const res = await unstarModel(modelDetail.value.id)
      if (res.data?.code === 200) {
        modelDetail.value.is_starred = false
        modelDetail.value.star_count = res.data.data?.star_count ?? (modelDetail.value.star_count - 1)
        const item = allModels.value.find(m => m.id === modelDetail.value.id)
        if (item) {
          item.is_starred = false
          item.star_count = modelDetail.value.star_count
        }
        ElMessage.success('已取消点赞')
      }
    } else {
      const res = await starModel(modelDetail.value.id)
      if (res.data?.code === 201 || res.data?.code === 200) {
        modelDetail.value.is_starred = true
        modelDetail.value.star_count = res.data.data?.star_count ?? (modelDetail.value.star_count + 1)
        const item = allModels.value.find(m => m.id === modelDetail.value.id)
        if (item) {
          item.is_starred = true
          item.star_count = modelDetail.value.star_count
        }
        ElMessage.success('感谢点赞！')
      }
    }
  } catch (error) {
    if (error.response?.status === 401) ElMessage.warning('请先登录')
    else ElMessage.error('操作失败')
  } finally {
    dialogStarLoading.value = false
  }
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
        is_followed: row.is_followed, // 从列表中继承关注状态
        is_starred: row.is_starred,
        star_count: row.star_count
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
  background: transparent;
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
  background: var(--header-gradient);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
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
  background: radial-gradient(circle, rgba(56, 139, 253, 0.15), transparent 70%);
  pointer-events: none;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  background: rgba(56, 139, 253, 0.15);
  border: 1px solid rgba(56, 139, 253, 0.4);
  color: var(--accent-color);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  letter-spacing: 1px;
}

.hero-left h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(56, 139, 253, 0.3);
}

.subtitle {
  margin: 4px 0 14px;
  color: var(--text-secondary);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-card {
  background: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 10px 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.type-total {
  border-left: 3px solid var(--text-primary);
}
.stat-card.type-star {
  border-left: 3px solid #f56c6c; /* Danger/Red for stars */
}
.stat-card.type-followed {
  border-left: 3px solid #ffc107; /* Gold/Yellow for favorites */
}

/* ... existing styles ... */

.stat-card.type-star:hover { border-color: #f56c6c; background: rgba(245, 108, 108, 0.05); }

/* ... existing styles ... */

.stat-card.type-star .value { color: #f56c6c; }

.mini-star {
  font-size: 12px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
}

.star-val {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f56c6c !important;
}

.star-btn:hover {
  background-color: #f56c6c22 !important;
}

.detail-header-stats {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.d-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.d-stat .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.d-stat .value {
  font-size: 18px;
  font-weight: 700;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}
.stat-card.type-text {
  border-left: 3px solid var(--el-color-primary);
}
.stat-card.type-image {
  border-left: 3px solid var(--el-color-success);
}
.stat-card.type-multi {
  border-left: 3px solid var(--el-color-warning);
}
.stat-card.type-code {
  border-left: 3px solid var(--el-color-info);
}

/* Add subtle colored backgrounds on hover */
.stat-card.type-total:hover { border-color: var(--text-primary); }
.stat-card.type-followed:hover { border-color: #ffc107; background: rgba(255, 193, 7, 0.05); }
.stat-card.type-text:hover { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.stat-card.type-image:hover { border-color: var(--el-color-success); background: var(--el-color-success-light-9); }
.stat-card.type-multi:hover { border-color: var(--el-color-warning); background: var(--el-color-warning-light-9); }
.stat-card.type-code:hover { border-color: var(--el-color-info); background: var(--el-color-info-light-9); }

.stat-card .label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-card .value {
  font-size: 24px;
  font-weight: 800;
  margin: 4px 0 2px;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

/* Colorize values based on type */
.stat-card.type-followed .value { color: #ffc107; }
.stat-card.type-text .value { color: var(--el-color-primary); }
.stat-card.type-image .value { color: var(--el-color-success); }
.stat-card.type-multi .value { color: var(--el-color-warning); }
.stat-card.type-code .value { color: var(--el-color-info); }

.stat-card .hint {
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.7;
}

.hero-right {
  width: 320px;
}

.mini-rank {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 14px;
  height: 100%;
}

.mini-title {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.mini-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.mini-item:last-child {
  border-bottom: none;
}

.mini-rank-num {
  font-weight: 700;
  color: var(--accent-color);
  font-family: 'Share Tech Mono', monospace;
}

.mini-name {
  font-weight: 600;
  color: var(--text-primary);
}

.mini-tags {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.filter-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 14px;
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
  color: var(--text-secondary);
}

.board-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.board-row {
  display: grid;
  grid-template-columns: 80px 1.3fr 1fr 350px;
  gap: 16px;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 14px 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.board-row:hover {
  transform: translateY(-2px);
  border-color: var(--accent-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.board-row.top-row {
  background: linear-gradient(90deg, rgba(56, 139, 253, 0.05) 0%, var(--bg-secondary) 100%);
  border-color: rgba(56, 139, 253, 0.3);
}

.rank span {
  font-size: 20px;
  font-weight: 800;
  color: var(--accent-color);
  font-family: 'Share Tech Mono', monospace;
}

.meta .name-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta .name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.meta-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  margin-top: 6px;
  font-size: 13px;
}

.meta-sub .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-color);
  display: inline-block;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 12px;
}

.metric {
  background: var(--bg-body);
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-value {
  margin-top: 6px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-value.on {
  color: var(--success-color);
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

/* Pagination Dark Mode Override */
:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--accent-color);
  color: #ffffff;
}

:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.dialog-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  color: var(--text-secondary);
}

.detail-content {
  padding: 10px 0;
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
  color: var(--text-primary);
}

/* Descriptions Dark Mode Override */
:deep(.el-descriptions__label) {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

:deep(.el-descriptions__content) {
  background-color: var(--bg-body) !important;
  color: var(--text-primary) !important;
}

:deep(.el-descriptions__cell) {
  border-color: var(--border-color) !important;
}
</style>

