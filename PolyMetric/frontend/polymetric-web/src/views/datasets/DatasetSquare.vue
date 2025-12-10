<template>
  <div class="dataset-square">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><Folder /></el-icon>
        数据集广场
      </h2>
      <p class="subtitle">浏览和发现优质数据集，支持搜索和分类筛选</p>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-bar">
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索数据集名称..." 
        :prefix-icon="Search" 
        clearable
        @input="handleLocalFilter"
        @clear="handleLocalFilter"
        style="width: 300px;"
      />
      <el-select 
        v-model="categoryFilter" 
        placeholder="选择分类" 
        clearable
        @change="handleLocalFilter"
        style="width: 150px; margin-left: 15px;"
      >
        <el-option label="全部分类" value="" />
        <el-option label="图像" value="image" />
        <el-option label="文本" value="text" />
        <el-option label="多模态" value="multimodal" />
      </el-select>
      <el-button :icon="Refresh" @click="resetFilter" style="margin-left: 15px;">重置</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 数据集列表 -->
    <div v-else>
      <el-empty v-if="filteredDatasets.length === 0" description="暂无数据集" />
      
      <template v-else>
        <el-table 
          :data="paginatedDatasets" 
          border 
          stripe
          style="width: 100%;"
        >
          <el-table-column prop="name" label="数据集名称" min-width="180">
            <template #default="{ row }">
              <div class="dataset-name">
                <el-icon><Folder /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="creator_username" label="上传者" width="160">
            <template #default="{ row }">
              <UserPopover :user-id="row.creator_id" :username="row.creator_username" v-if="row.creator_id" />
              <span v-else>{{ row.creator_username || '未知' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="120">
            <template #default="{ row }">
              <el-tag :type="getCategoryType(row.category)" size="small">
                {{ getCategoryLabel(row.category) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="file_size" label="大小" width="100" align="center">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" size="small" @click="showDetail(row)">
                  详情
                </el-button>
                <el-button type="success" size="small" :icon="Download" @click="handleDownload(row)">
                  下载
                </el-button>
                <el-button 
                  :type="row.is_followed ? 'warning' : 'info'" 
                  size="small" 
                  :icon="row.is_followed ? StarFilled : Star"
                  @click="handleToggleFollow(row)"
                  :loading="row.followLoading"
                >
                  {{ row.is_followed ? '已关注' : '关注' }}
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
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
      </template>
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

          <!-- 条目加载状态 -->
          <div v-if="entriesLoading" class="entries-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载数据条目中...</span>
          </div>

          <!-- 条目列表 -->
          <div v-else-if="datasetEntries.length > 0" class="entries-container">
            <!-- 动态表格：根据数据字段自动生成列 -->
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

            <!-- 条目分页 -->
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

          <!-- 无数据 -->
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
    result = result.filter(item => 
      item.name.toLowerCase().includes(keyword)
    )
  }
  
  if (categoryFilter.value) {
    result = result.filter(item => item.category === categoryFilter.value)
  }
  
  return result
})

// 分页后的数据集（当前页显示的数据）
const paginatedDatasets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDatasets.value.slice(start, end)
})

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
  row.followLoading = true
  try {
    if (row.is_followed) {
      // 取消关注
      const res = await unfollowDataset(row.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        row.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      // 添加关注
      const res = await followDataset(row.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        row.is_followed = true
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
    row.followLoading = false
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
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: calc(100vh - 140px);
}

.page-header {
  margin-bottom: 25px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: #303133;
}

.page-header .subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
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

/* 分页容器样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 15px 0;
}

/* 数据条目区域样式 */
.entries-section {
  margin-top: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
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
  color: #303133;
  font-size: 15px;
}

.entries-total {
  color: #909399;
  font-weight: normal;
  font-size: 13px;
}

.entries-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: #909399;
}

.entries-container {
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

.entries-pagination {
  display: flex;
  justify-content: center;
  padding: 15px 0 5px;
  background: white;
}

.cell-content {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}

:deep(.el-pagination) {
  --el-pagination-button-bg-color: #fff;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
  font-size: 15px;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 10px;
}

/* 弹窗样式优化 */
:deep(.dataset-detail-dialog .el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
