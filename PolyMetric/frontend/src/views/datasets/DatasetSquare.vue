<template>
  <div class="dataset-square">
    <div class="hero">
      <div class="hero-left">
        <div class="title-row">
          <div class="badge">数据集广场</div>
          <h2>评测数据集榜单</h2>
        </div>
        <p class="subtitle">优先展示高质量、已审核、被关注的数据集，像榜单一样浏览。</p>
        <div class="hero-stats">
          <div class="stat-card">
            <div class="label">已收录</div>
            <div class="value">{{ filteredDatasets.length }}</div>
            <div class="hint">数据集数量</div>
          </div>
          <div class="stat-card">
            <div class="label">已审核</div>
            <div class="value">{{ verifiedCount }}</div>
            <div class="hint">通过审核</div>
          </div>
          <div class="stat-card">
            <div class="label">已关注</div>
            <div class="value">{{ followedCount }}</div>
            <div class="hint">你的关注</div>
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
                <el-tag size="small" effect="plain">{{ formatFileSize(item.file_size) }}</el-tag>
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
          placeholder="搜索数据集名称..."
          :prefix-icon="Search"
          clearable
          @input="handleLocalFilter"
          @clear="handleLocalFilter"
          class="filter-input"
        />
        <el-select
          v-model="categoryFilter"
          placeholder="选择分类"
          clearable
          @change="handleLocalFilter"
          class="filter-select"
        >
          <el-option label="全部分类" value="" />
          <el-option label="图像" value="image" />
          <el-option label="文本" value="text" />
          <el-option label="多模态" value="multimodal" />
        </el-select>
        <el-button :icon="Refresh" @click="resetFilter">重置</el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else>
      <el-empty v-if="filteredDatasets.length === 0" description="暂无数据集" />

      <div v-else class="board-list">
        <div
          v-for="item in paginatedRankedDatasets"
          :key="item.id"
          class="board-row"
          :class="{ 'top-row': item._rank <= 3 }"
        >
          <div class="rank">
            <span>#{{ item._rank }}</span>
          </div>
          <div class="meta">
            <div class="name-line">
              <el-icon><Folder /></el-icon>
              <span class="name">{{ item.name }}</span>
              <el-tag size="small" :type="getCategoryType(item.category)">{{ getCategoryLabel(item.category) }}</el-tag>
            </div>
            <div class="meta-sub">
              <span>上传者: 
                <UserPopover :user-id="item.creator_id" :username="item.creator_username" v-if="item.creator_id" />
                <span v-else>{{ item.creator_username || '未知' }}</span>
              </span>
              <span class="dot" />
              <span>{{ formatFileSize(item.file_size) }}</span>
            </div>
          </div>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">审核状态</div>
              <div class="metric-value" :class="{ on: item.is_verified }">{{ item.is_verified ? '已审核' : '待审核' }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">最近更新</div>
              <div class="metric-value">{{ formatDate(item.updated_at) }}</div>
            </div>
          </div>
          <div class="actions">
            <el-button type="primary" size="small" @click="showDetail(item)">详情</el-button>
            <el-button type="success" size="small" :icon="Download" @click="handleDownload(item)">下载</el-button>
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
            :total="filteredDatasets.length"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 数据集详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      :title="currentDataset?.name" 
      width="900px"
      :close-on-click-modal="false"
      class="dataset-detail-dialog"
    >
      <div v-if="detailLoading" class="dialog-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载详情中...</span>
      </div>
      
      <div class="detail-content" v-else-if="datasetDetail">
        <!-- 基本信息区域 -->
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="基本信息" name="info">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="数据集名称">{{ datasetDetail.name }}</el-descriptions-item>
              <el-descriptions-item label="上传者">
                <UserPopover :user-id="datasetDetail.creator_id" :username="datasetDetail.creator_username" v-if="datasetDetail.creator_id" />
                <span v-else>{{ datasetDetail.creator_username || '未知' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="分类">
                <el-tag :type="getCategoryType(datasetDetail.category)" size="small">
                  {{ getCategoryLabel(datasetDetail.category) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="文件格式">{{ datasetDetail.file_format || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(datasetDetail.file_size) }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="datasetDetail.is_verified ? 'success' : 'warning'" size="small">
                  {{ datasetDetail.is_verified ? '已审核' : '待审核' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(datasetDetail.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(datasetDetail.updated_at) }}</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">
                {{ datasetDetail.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>
        </el-collapse>

        <!-- 数据条目预览区域 -->
        <div class="entries-section">
          <div class="entries-header">
            <h4>
              <el-icon><Document /></el-icon>
              数据条目预览
              <span class="entries-total" v-if="entriesTotal > 0">（共 {{ entriesTotal }} 条）</span>
            </h4>
            <el-button 
              size="small" 
              :icon="Refresh" 
              @click="fetchDatasetEntries(1)"
              :loading="entriesLoading"
            >
              刷新
            </el-button>
          </div>

          <div v-if="entriesLoading" class="entries-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载数据条目中...</span>
          </div>

          <div v-else-if="datasetEntries.length > 0" class="entries-container">
            <el-table 
              :data="datasetEntries" 
              border 
              stripe 
              size="small"
              max-height="350"
              style="width: 100%;"
            >
              <el-table-column 
                v-for="field in entryFields" 
                :key="field"
                :prop="field"
                :label="field"
                :min-width="getFieldWidth(field)"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <span class="cell-content">{{ formatCellValue(row[field]) }}</span>
                </template>
              </el-table-column>
            </el-table>

            <div class="entries-pagination">
              <el-pagination
                v-model:current-page="entriesCurrentPage"
                :page-size="entriesPageSize"
                :total="entriesTotal"
                :background="true"
                layout="prev, pager, next, jumper"
                @current-change="handleEntriesPageChange"
                small
              />
            </div>
          </div>

          <el-empty v-else description="暂无数据条目或不支持预览该格式" :image-size="80" />
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          :type="datasetDetail?.is_followed ? 'warning' : 'info'" 
          :icon="datasetDetail?.is_followed ? StarFilled : Star"
          @click="handleToggleFollowInDialog"
          :loading="dialogFollowLoading"
        >
          {{ datasetDetail?.is_followed ? '取消关注' : '关注' }}
        </el-button>
        <el-button type="success" :icon="Download" @click="handleDownload(currentDataset)">
          下载数据集
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Folder, Download, Loading, Star, StarFilled, Document, User } from '@element-plus/icons-vue'
import UserPopover from '@/components/common/UserPopover.vue'
import { getAllDatasets, getDatasetDetail, downloadDataset, followDataset, unfollowDataset, getDatasetEntries } from '@/api/datasets'

// 状态
const loading = ref(false)
const allDatasets = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(5)

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const dialogFollowLoading = ref(false)
const currentDataset = ref(null)
const datasetDetail = ref(null)
const activeCollapse = ref(['info'])  // 默认展开基本信息

// 数据条目相关状态
const entriesLoading = ref(false)
const datasetEntries = ref([])
const entryFields = ref([])  // 动态字段列表
const entriesCurrentPage = ref(1)
const entriesPageSize = ref(10)
const entriesTotal = ref(0)

// 本地筛选后的数据集
const filteredDatasets = computed(() => {
  let result = allDatasets.value
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    result = result.filter(item => item.name.toLowerCase().includes(keyword))
  }
  if (categoryFilter.value) {
    result = result.filter(item => item.category === categoryFilter.value)
  }
  return result
})

// 榜单派生数据
const verifiedCount = computed(() => filteredDatasets.value.filter(item => item.is_verified).length)
const followedCount = computed(() => filteredDatasets.value.filter(item => item.is_followed).length)
const rankedDatasets = computed(() => filteredDatasets.value.map((item, idx) => ({ ...item, _rank: idx + 1 })))
const paginatedRankedDatasets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rankedDatasets.value.slice(start, end)
})
const rankedTop3 = computed(() => rankedDatasets.value.slice(0, 3))

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

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '未知'
  return typeof size === 'number' ? `${size.toFixed(2)} MB` : size
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
    'image': '图像',
    'text': '文本',
    'multimodal': '多模态'
  }
  return labels[category] || category || '未分类'
}

const getCategoryType = (category) => {
  const types = {
    'image': 'primary',
    'text': 'success',
    'multimodal': 'warning'
  }
  return types[category] || ''
}

// 根据字段名获取列宽度
const getFieldWidth = (field) => {
  const fieldLower = field.toLowerCase()
  // 长文本字段给更多宽度
  if (fieldLower.includes('content') || fieldLower.includes('text') || 
      fieldLower.includes('answer') || fieldLower.includes('question') ||
      fieldLower.includes('description') || fieldLower.includes('prompt')) {
    return 200
  }
  // ID 和短字段
  if (fieldLower === 'id' || fieldLower.includes('_id')) {
    return 60
  }
  // 默认宽度
  return 120
}

// 格式化单元格值
const formatCellValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  if (typeof value === 'boolean') return value ? '是' : '否'
  return String(value)
}

// 从后端获取所有数据集（带关注状态）
const fetchAllDatasets = async () => {
  loading.value = true
  try {
    const res = await getAllDatasets()
    // 后端返回格式: { code: 200, msg: "查询成功", data: [...] }
    let datasets = []
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasets = res.data.data
    } else if (Array.isArray(res.data)) {
      datasets = res.data
    }
    // 为每个数据集添加 followLoading 状态
    allDatasets.value = datasets.map(item => ({
      ...item,
      is_followed: item.is_followed || false,
      followLoading: false
    }))
  } catch (error) {
    console.error('获取数据集列表失败:', error)
    ElMessage.error('获取数据集列表失败')
    allDatasets.value = []
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
  fetchAllDatasets()
}

// 切换关注状态（列表中）
const handleToggleFollow = async (row) => {
  // 从原始数组中找到对应的数据集对象
  const originalItem = allDatasets.value.find(d => d.id === row.id)
  if (!originalItem) return
  
  originalItem.followLoading = true
  try {
    if (originalItem.is_followed) {
      // 取消关注
      const res = await unfollowDataset(originalItem.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        originalItem.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      // 添加关注
      const res = await followDataset(originalItem.id)
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
  if (!datasetDetail.value) return
  
  dialogFollowLoading.value = true
  try {
    if (datasetDetail.value.is_followed) {
      const res = await unfollowDataset(datasetDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        datasetDetail.value.is_followed = false
        // 同步更新列表中的状态
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
        if (item) item.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      const res = await followDataset(datasetDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        datasetDetail.value.is_followed = true
        // 同步更新列表中的状态
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
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

// 获取数据集条目（分页）
const fetchDatasetEntries = async (page = 1) => {
  if (!currentDataset.value) return
  
  entriesLoading.value = true
  entriesCurrentPage.value = page
  
  try {
    const res = await getDatasetEntries(currentDataset.value.id, {
      page: page,
      page_size: entriesPageSize.value
    })
    
    // 后端返回格式: { code: 200, msg: "查询成功", data: { entries: [...], total: 100, fields: [...] } }
    if (res.data?.code === 200 && res.data.data) {
      const { entries, total, fields } = res.data.data
      datasetEntries.value = entries || []
      entriesTotal.value = total || 0
      // 如果后端返回了字段列表则使用，否则从第一条数据中提取
      if (fields && fields.length > 0) {
        entryFields.value = fields
      } else if (entries && entries.length > 0) {
        entryFields.value = Object.keys(entries[0])
      } else {
        entryFields.value = []
      }
    } else {
      datasetEntries.value = []
      entriesTotal.value = 0
      entryFields.value = []
    }
  } catch (error) {
    console.error('获取数据条目失败:', error)
    // 不显示错误提示，可能是格式不支持
    datasetEntries.value = []
    entriesTotal.value = 0
    entryFields.value = []
  } finally {
    entriesLoading.value = false
  }
}

// 处理条目分页变化
const handleEntriesPageChange = (page) => {
  fetchDatasetEntries(page)
}

// 显示详情
const showDetail = async (row) => {
  currentDataset.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  datasetDetail.value = null
  
  // 重置条目状态
  datasetEntries.value = []
  entryFields.value = []
  entriesTotal.value = 0
  entriesCurrentPage.value = 1
  
  try {
    const res = await getDatasetDetail(row.id)
    // 后端返回格式: { code: 200, msg: "查询成功", data: {...} }
    if (res.data?.code === 200 && res.data.data) {
      datasetDetail.value = {
        ...res.data.data,
        is_followed: row.is_followed // 从列表中继承关注状态
      }
    } else {
      datasetDetail.value = row
    }
    
    // 加载数据条目
    fetchDatasetEntries(1)
  } catch (error) {
    console.error('获取数据集详情失败:', error)
    ElMessage.error('获取详情失败')
    datasetDetail.value = row
  } finally {
    detailLoading.value = false
  }
}

// 下载数据集 - 调用 GET /api/datasets/{id}/download/
const handleDownload = async (dataset) => {
  if (!dataset) return
  
  try {
    ElMessage.info('开始下载...')
    const res = await downloadDataset(dataset.id)
    
    // 检查是否返回了错误信息
    if (res.data?.type === 'application/json') {
      const reader = new FileReader()
      reader.onload = () => {
        const errorData = JSON.parse(reader.result)
        ElMessage.error(errorData.msg || '下载失败')
      }
      reader.readAsText(res.data)
      return
    }
    
    // 创建 Blob 并触发下载
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${dataset.name}.${dataset.file_format || 'zip'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('无权限下载该数据集')
    } else {
      ElMessage.error('下载失败，请稍后重试')
    }
  }
}

onMounted(() => {
  fetchAllDatasets()
})
</script>

<style scoped>
.dataset-square {
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
  background: radial-gradient(circle, rgba(35, 134, 54, 0.15), transparent 70%);
  pointer-events: none;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  background: rgba(35, 134, 54, 0.15);
  border: 1px solid rgba(35, 134, 54, 0.4);
  color: var(--success-color);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  letter-spacing: 1px;
}

.hero-left h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(35, 134, 54, 0.3);
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
  transition: border-color 0.2s;
}

.stat-card:hover {
  border-color: var(--success-color);
}

.stat-card .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-card .value {
  font-size: 22px;
  font-weight: 700;
  margin: 6px 0 2px;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

.stat-card .hint {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.8;
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
  color: var(--success-color);
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
  grid-template-columns: 80px 1.3fr 1fr 260px;
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
  border-color: var(--success-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.board-row.top-row {
  background: linear-gradient(90deg, rgba(35, 134, 54, 0.05) 0%, var(--bg-secondary) 100%);
  border-color: rgba(35, 134, 54, 0.3);
}

.rank span {
  font-size: 20px;
  font-weight: 800;
  color: var(--success-color);
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

/* 数据条目区域 */
.entries-section {
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  background: var(--bg-body);
}

.entries-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.entries-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-size: 15px;
}

.entries-total {
  color: var(--text-secondary);
  font-weight: normal;
  font-size: 13px;
}

.entries-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--text-secondary);
}

.entries-container {
  background: var(--bg-secondary);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.entries-pagination {
  display: flex;
  justify-content: center;
  padding: 15px 0 5px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.cell-content {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

/* Table Dark Theme Overrides for Entries */
:deep(.el-table) {
  --el-table-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-secondary);
  --el-table-header-bg-color: var(--bg-body);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  --el-table-row-hover-bg-color: var(--bg-hover);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
}

:deep(.el-table th) {
  background-color: var(--bg-body) !important;
  color: var(--text-secondary) !important;
  border-bottom: 1px solid var(--border-color) !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-color) !important;
}

/* Collapse Dark Overrides */
:deep(.el-collapse) {
  border-color: var(--border-color);
}
:deep(.el-collapse-item__header) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-color: var(--border-color);
}
:deep(.el-collapse-item__content) {
  background-color: var(--bg-body);
  color: var(--text-secondary);
  padding-bottom: 10px;
}
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

