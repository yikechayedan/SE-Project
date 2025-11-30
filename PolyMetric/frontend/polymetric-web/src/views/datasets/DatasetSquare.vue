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
        <el-table-column prop="uploader" label="上传者" width="140">
          <template #default="{ row }">
            {{ row.uploader || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="100" align="center">
          <template #default="{ row }">
            {{ row.file_size }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="showDetail(row)">
                详情
              </el-button>
              <el-button type="success" size="small" @click="handleDownload(row)">
                下载
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
          <el-descriptions-item label="上传者">{{ datasetDetail.uploader || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :type="getCategoryType(datasetDetail.category)">
              {{ getCategoryLabel(datasetDetail.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件格式">{{ datasetDetail.file_format || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="是否公开">{{ datasetDetail.is_public ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ datasetDetail.file_size || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(datasetDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(datasetDetail.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ datasetDetail.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
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
import { Search, Refresh, Folder, Download, Loading } from '@element-plus/icons-vue'
import { getAllDatasets, getDatasetDetail } from '@/api/datasets'

// 状态
const loading = ref(false)
const allDatasets = ref([])  // 存储从后端获取的所有数据集（本地缓存）
const searchQuery = ref('')
const categoryFilter = ref('')

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const currentDataset = ref(null)
const datasetDetail = ref(null)

// 本地筛选后的数据集（计算属性）
const filteredDatasets = computed(() => {
  let result = allDatasets.value
  
  // 按名称搜索（本地筛选）
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    result = result.filter(item => 
      item.name.toLowerCase().includes(keyword)
    )
  }
  
  // 按分类筛选（本地筛选）
  if (categoryFilter.value) {
    result = result.filter(item => item.category === categoryFilter.value)
  }
  
  return result
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取分类标签类型
// 分类英文转中文
const getCategoryLabel = (category) => {
  const labels = {
    'image': '图像',
    'text': '文本',
    'multimodal': '多模态'
  }
  return labels[category] || '未分类'
}

const getCategoryType = (category) => {
  const types = {
    'image': 'primary',
    'text': 'success',
    'multimodal': 'warning',
    
    
  }
  return types[category] || ''
}

// 从后端获取所有数据集（进入页面时调用）
const fetchAllDatasets = async () => {
  loading.value = true
  try {
    const data = await getAllDatasets()
    allDatasets.value = data
  } catch (error) {
    console.error('获取数据集列表失败:', error)
    ElMessage.error('获取数据集列表失败')
    allDatasets.value = []
  } finally {
    loading.value = false
  }
}

// 本地筛选（输入时触发，不访问后端）
const handleLocalFilter = () => {
  // 筛选由 computed 自动完成，这里可以添加额外逻辑
}

// 重置筛选（访问后端刷新数据）
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  fetchAllDatasets()  // 重新从后端获取数据
}

// 显示详情（访问后端获取完整信息）
const showDetail = async (row) => {
  currentDataset.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  datasetDetail.value = null
  
  try {
    const data = await getDatasetDetail(row.id)
    datasetDetail.value = data
  } catch (error) {
    console.error('获取数据集详情失败:', error)
    ElMessage.error('获取详情失败')
    // 降级显示列表中的基本信息
    datasetDetail.value = row
  } finally {
    detailLoading.value = false
  }
}

// 下载数据集（暂无逻辑）
const handleDownload = (dataset) => {
  ElMessage.info(`下载功能开发中：${dataset.name}`)
}

// 初始化：进入页面时获取所有数据集
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
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.loading-container .el-icon {
  margin-bottom: 10px;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

/* 操作按钮对齐 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-buttons .el-button {
  margin: 0;
}

.detail-content {
  padding: 10px 0;
}

.dialog-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #909399;
}

.dialog-loading .el-icon {
  margin-bottom: 10px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}
</style>
