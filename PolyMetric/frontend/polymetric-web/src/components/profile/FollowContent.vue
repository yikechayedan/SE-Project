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
            <el-button 
              type="danger" 
              :icon="StarFilled" 
              circle 
              size="small"
              @click="handleUnfollow('model', item.id)"
              title="取消关注"
            />
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
              关注时间：{{ formatDate(item.followedAt) }}
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
            <el-button 
              type="danger" 
              :icon="StarFilled" 
              circle 
              size="small"
              @click="handleUnfollow('dataset', item.id)"
              title="取消关注"
            />
          </div>
          <div class="card-info">
            <el-tag type="warning" size="small">
              <el-icon><User /></el-icon>
              {{ item.uploader || '未知上传者' }}
            </el-tag>
            <el-tag type="primary" size="small">
              <el-icon><Collection /></el-icon>
              {{ item.category || '未分类' }}
            </el-tag>
            <el-tag type="success" size="small">
              <el-icon><Document /></el-icon>
              {{ item.itemCount || 0 }} 条数据
            </el-tag>
          </div>
          <div class="card-meta">
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              关注时间：{{ formatDate(item.followedAt) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  StarFilled, 
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
import { getFollowedModels, getFollowedDatasets, unfollowModel, unfollowDataset } from '@/api/users'

// 当前展示类型：model 或 dataset
const activeType = ref('model')
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

// 获取关注的模型列表
const fetchFollowedModels = async () => {
  loading.value = true
  try {
    const res = await getFollowedModels()
    modelList.value = res.data || []
  } catch (error) {
    console.error('获取关注模型失败:', error)
    // 后端未实现时显示模拟数据
    modelList.value = [
      { 
        id: 1, 
        name: 'GPT-4', 
        company: 'OpenAI', 
        parameterSize: '1.76T',
        followedAt: '2025-01-15T10:30:00'
      },
      { 
        id: 2, 
        name: 'Claude 3', 
        company: 'Anthropic', 
        parameterSize: '未公开',
        followedAt: '2025-01-20T14:20:00'
      },
      { 
        id: 3, 
        name: 'Gemini Pro', 
        company: 'Google', 
        parameterSize: '未公开',
        followedAt: '2025-02-01T09:00:00'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 获取关注的数据集列表
const fetchFollowedDatasets = async () => {
  loading.value = true
  try {
    const res = await getFollowedDatasets()
    datasetList.value = res.data || []
  } catch (error) {
    console.error('获取关注数据集失败:', error)
    // 后端未实现时显示模拟数据
    datasetList.value = [
      { 
        id: 1, 
        name: 'MMLU', 
        uploader: 'UC Berkeley', 
        category: '综合评测',
        itemCount: 14042,
        followedAt: '2025-01-10T08:00:00'
      },
      { 
        id: 2, 
        name: 'HumanEval', 
        uploader: 'OpenAI', 
        category: '代码生成',
        itemCount: 164,
        followedAt: '2025-01-18T16:30:00'
      },
      { 
        id: 3, 
        name: 'CMMLU', 
        uploader: '清华大学', 
        category: '中文评测',
        itemCount: 11528,
        followedAt: '2025-02-05T11:45:00'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 取消关注
const handleUnfollow = async (type, id) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消关注这个${type === 'model' ? '模型' : '数据集'}吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (type === 'model') {
      await unfollowModel(id)
      modelList.value = modelList.value.filter(item => item.id !== id)
    } else {
      await unfollowDataset(id)
      datasetList.value = datasetList.value.filter(item => item.id !== id)
    }
    
    ElMessage.success('取消关注成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
    }
  }
}

// 监听类型切换，加载对应数据
watch(activeType, (newType) => {
  if (newType === 'model' && modelList.value.length === 0) {
    fetchFollowedModels()
  } else if (newType === 'dataset' && datasetList.value.length === 0) {
    fetchFollowedDatasets()
  }
})

// 初始加载模型列表（默认显示模型）
onMounted(() => {
  fetchFollowedModels()
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

/* 空状态样式 */
:deep(.el-empty) {
  padding: 40px 0;
}
</style>
