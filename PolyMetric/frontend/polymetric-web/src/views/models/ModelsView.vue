<template>
  <div class="model-square">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><Box /></el-icon>
        模型广场
      </h2>
      <p class="subtitle">浏览和发现优质大模型，支持搜索和分类筛选</p>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-bar">
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索模型名称..." 
        :prefix-icon="Search" 
        clearable
        @input="handleLocalFilter"
        @clear="handleLocalFilter"
        style="width: 300px;"
      />
      <el-select 
        v-model="categoryFilter" 
        placeholder="选择类型" 
        clearable
        @change="handleLocalFilter"
        style="width: 150px; margin-left: 15px;"
      >
        <el-option label="全部类型" value="" />
        <el-option label="文本生成" value="text" />
        <el-option label="图像生成" value="image" />
        <el-option label="多模态" value="multimodal" />
        <el-option label="代码生成" value="code" />
      </el-select>
      <el-button :icon="Refresh" @click="resetFilter" style="margin-left: 15px;">重置</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 模型列表 -->
    <div v-else>
      <el-empty v-if="filteredModels.length === 0" description="暂无模型" />
      
      <el-table 
        v-else 
        :data="filteredModels" 
        border 
        stripe
        style="width: 100%;"
      >
        <el-table-column prop="name" label="模型名称" min-width="180">
          <template #default="{ row }">
            <div class="model-name">
              <el-icon><Box /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="company" label="所属公司" width="140">
          <template #default="{ row }">
            {{ row.company || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parameter_size" label="参数量" width="120" align="center">
          <template #default="{ row }">
            {{ row.parameter_size || '未知' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="showDetail(row)">
                详情
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

    <!-- 模型详情弹窗 -->
    <el-dialog v-model="showDetailDialog" :title="currentModel?.name" width="600px">
      <div v-if="detailLoading" class="dialog-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载详情中...</span>
      </div>
      <div class="detail-content" v-else-if="modelDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ modelDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="所属公司">{{ modelDetail.company || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getCategoryType(modelDetail.category)">
              {{ getCategoryLabel(modelDetail.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="参数量">{{ modelDetail.parameter_size || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="发布日期">{{ formatDate(modelDetail.release_date) }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ modelDetail.version || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ modelDetail.description || '暂无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="官方链接" :span="2">
            <el-link v-if="modelDetail.official_url" :href="modelDetail.official_url" target="_blank" type="primary">
              {{ modelDetail.official_url }}
            </el-link>
            <span v-else>暂无</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          :type="modelDetail?.is_followed ? 'warning' : 'info'" 
          :icon="modelDetail?.is_followed ? StarFilled : Star"
          @click="handleToggleFollowInDialog"
          :loading="dialogFollowLoading"
        >
          {{ modelDetail?.is_followed ? '取消关注' : '关注' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Box, Loading, Star, StarFilled } from '@element-plus/icons-vue'
import { getAllModels, getModelDetail, followModel, unfollowModel } from '@/api/models'

// 状态
const loading = ref(false)
const allModels = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')

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
  // 筛选由 computed 自动完成
}

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  fetchAllModels()
}

// 切换关注状态（列表中）
const handleToggleFollow = async (row) => {
  row.followLoading = true
  try {
    if (row.is_followed) {
      // 取消关注
      const res = await unfollowModel(row.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        row.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      // 添加关注
      const res = await followModel(row.id)
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

.model-name {
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
