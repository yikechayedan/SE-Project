<template>
  <div class="follow">
    <!-- 切换按钮 -->
    <div class="tab-switch">
      <el-button-group>
        <el-button 
          :type="activeType === 'model' ? 'primary' : ''" 
          @click="activeType = 'model'"
        >
          <el-icon><Box /></el-icon>
          关注的模型
        </el-button>
        <el-button 
          :type="activeType === 'dataset' ? 'primary' : ''" 
          @click="activeType = 'dataset'"
        >
          <el-icon><Folder /></el-icon>
          关注的数据集
        </el-button>
      </el-button-group>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 模型列表 -->
    <div v-else-if="activeType === 'model'" class="list">
      <el-empty v-if="modelList.length === 0" description="暂无关注的模型" />
      <el-card 
        v-for="item in modelList" 
        :key="item.id" 
        shadow="hover" 
        class="follow-card"
      >
        <div class="card-content">
          <div class="card-header">
            <div class="title-row">
              <el-icon class="type-icon model-icon"><Box /></el-icon>
              <span class="item-name">{{ item.name }}</span>
            </div>
          </div>
          <div class="card-info">
            <el-tag type="info" size="small">
              <el-icon><OfficeBuilding /></el-icon>
              {{ item.company || '未知公司' }}
            </el-tag>
            <el-tag type="success" size="small">
              <el-icon><DataLine /></el-icon>
              {{ item.parameterSize || '未知' }} 参数
            </el-tag>
          </div>
          <div class="card-meta">
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              关注时间：{{ formatDate(item.followed_at) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 数据集列表 -->
    <div v-else class="list">
      <el-empty v-if="datasetList.length === 0" description="暂无关注的数据集" />
      <el-card 
        v-for="item in datasetList" 
        :key="item.id" 
        shadow="hover" 
        class="follow-card"
      >
        <div class="card-content">
          <div class="card-header">
            <div class="title-row">
              <el-icon class="type-icon dataset-icon"><Folder /></el-icon>
              <span class="item-name">{{ item.name }}</span>
            </div>
          </div>
          <div class="card-info">
            <el-tag type="warning" size="small">
              <el-icon><User /></el-icon>
              {{ item.creator_username || '未知上传者' }}
            </el-tag>
            <el-tag type="primary" size="small">
              <el-icon><Collection /></el-icon>
              {{ getCategoryLabel(item.category) }}
            </el-tag>
            <el-tag type="success" size="small">
              <el-icon><Document /></el-icon>
              {{ formatFileSize(item.file_size) }}
            </el-tag>
          </div>
          <div class="card-meta">
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              关注时间：{{ formatDate(item.followed_at) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Box, 
  Folder, 
  OfficeBuilding, 
  DataLine, 
  Calendar,
  User,
  Collection,
  Document,
  Loading
} from '@element-plus/icons-vue'
import { getFollowedDatasets } from '@/api/datasets'

// 当前展示类型：model 或 dataset
const activeType = ref('dataset')  // 默认显示数据集
const loading = ref(false)

// 关注列表数据
const modelList = ref([])
const datasetList = ref([])

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '未知'
  return typeof size === 'number' ? size.toFixed(2) + ' MB' : size
}

// 分类标签
const getCategoryLabel = (category) => {
  const map = { image: '图像', text: '文本', multimodal: '多模态' }
  return map[category] || category || '未分类'
}

// 获取关注的模型列表（暂未实现后端）
const fetchFollowedModels = async () => {
  loading.value = true
  try {
    // TODO: 后端实现后替换为真实 API
    modelList.value = []
  } catch (error) {
    console.error('获取关注模型失败:', error)
    modelList.value = []
  } finally {
    loading.value = false
  }
}

// 获取关注的数据集列表
const fetchFollowedDatasets = async () => {
  loading.value = true
  try {
    const res = await getFollowedDatasets()
    // 后端返回格式: { code: 200, msg: "查询成功", data: [...] }
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasetList.value = res.data.data
    } else if (Array.isArray(res.data)) {
      datasetList.value = res.data
    } else {
      datasetList.value = []
    }
  } catch (error) {
    console.error('获取关注数据集失败:', error)
    ElMessage.error('获取关注列表失败')
    datasetList.value = []
  } finally {
    loading.value = false
  }
}

// 监听类型切换，加载对应数据
watch(activeType, (newType) => {
  if (newType === 'model') {
    fetchFollowedModels()
  } else if (newType === 'dataset') {
    fetchFollowedDatasets()
  }
})

// 初始加载数据集列表
onMounted(() => {
  fetchFollowedDatasets()
})
</script>

<style scoped>
.follow {
  min-height: 300px;
}

.tab-switch {
  margin-bottom: 20px;
  text-align: center;
}

.tab-switch .el-button {
  padding: 10px 20px;
}

.tab-switch .el-icon {
  margin-right: 5px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.follow-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.follow-card:hover {
  transform: translateY(-2px);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-icon {
  font-size: 24px;
  padding: 8px;
  border-radius: 8px;
}

.model-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.dataset-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.item-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.card-info .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 13px;
}

.card-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

:deep(.el-empty) {
  padding: 40px 0;
}
</style>
