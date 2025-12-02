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
      
      <el-table 
        v-else 
        :data="filteredDatasets" 
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
        <el-table-column prop="creator_username" label="上传者" width="140">
          <template #default="{ row }">
            {{ row.creator_username || '未知' }}
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
    </div>

    <!-- 数据集详情弹窗 -->
    <el-dialog v-model="showDetailDialog" :title="currentDataset?.name" width="600px">
      <div v-if="detailLoading" class="dialog-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载详情中...</span>
      </div>
      <div class="detail-content" v-else-if="datasetDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="数据集名称">{{ datasetDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="上传者">{{ datasetDetail.creator_username || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :type="getCategoryType(datasetDetail.category)">
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Folder, Download, Loading, Star, StarFilled } from '@element-plus/icons-vue'
import { getAllDatasets, getDatasetDetail, downloadDataset, followDataset, unfollowDataset } from '@/api/datasets'

// 状态
const loading = ref(false)
const allDatasets = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const dialogFollowLoading = ref(false)
const currentDataset = ref(null)
const datasetDetail = ref(null)

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
  // 筛选由 computed 自动完成
}

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
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

// 显示详情
const showDetail = async (row) => {
  currentDataset.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  datasetDetail.value = null
  
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

:deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}
</style>
