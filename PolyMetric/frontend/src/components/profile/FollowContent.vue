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
        <el-button 
          :type="activeType === 'user' ? 'primary' : ''" 
          @click="activeType = 'user'"
        >
          <el-icon><UserFilled /></el-icon>
          关注的用户
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
              type="warning" 
              size="small" 
              :icon="StarFilled"
              @click="handleUnfollowModel(item)"
              :loading="item.unfollowing"
            >
              取消关注
            </el-button>
          </div>
          <div class="card-info">
            <el-tag type="info" size="small">
              <el-icon><OfficeBuilding /></el-icon>
              {{ item.company || '未知公司' }}
            </el-tag>
            <el-tag :type="getCategoryType(item.category)" size="small">
              <el-icon><Cpu /></el-icon>
              {{ getCategoryLabel(item.category) }}
            </el-tag>
            <el-tag type="success" size="small">
              <el-icon><DataLine /></el-icon>
              {{ item.parameter_size || '未知参数量' }}
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
    <div v-else-if="activeType === 'dataset'" class="list">
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
              type="warning" 
              size="small" 
              :icon="StarFilled"
              @click="handleUnfollowDataset(item)"
              :loading="item.unfollowing"
            >
              取消关注
            </el-button>
          </div>
          <div class="card-info">
            <el-tag type="warning" size="small">
              <el-icon><User /></el-icon>
              {{ item.creator_username || '未知上传者' }}
            </el-tag>
            <el-tag type="primary" size="small">
              <el-icon><Collection /></el-icon>
              {{ getDatasetCategoryLabel(item.category) }}
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

    <!-- 用户列表 -->
    <div v-else-if="activeType === 'user'" class="list">
      <el-empty v-if="userList.length === 0" description="暂无关注的用户" />
      <el-card 
        v-for="item in userList" 
        :key="item.id" 
        shadow="hover" 
        class="follow-card user-card"
      >
        <div class="card-content">
          <div class="card-header">
            <div class="title-row">
              <el-avatar :size="40" :src="getFullAvatarUrl(item.avatar)" />
              <div class="user-info">
                <span class="item-name clickable" @click="goToUserProfile(item)">
                  {{ item.username }}
                </span>
                <span class="user-bio">{{ item.bio || '暂无介绍' }}</span>
              </div>
            </div>
            <div class="user-actions">
              <el-button 
                type="primary" 
                size="small" 
                plain
                @click="goToUserProfile(item)"
                :disabled="!item.show_followed_models && !item.show_followed_datasets"
              >
                查看主页
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                :icon="StarFilled"
                @click="handleUnfollowUser(item)"
                :loading="item.unfollowing"
              >
                取消关注
              </el-button>
            </div>
          </div>
          <div class="card-info">
            <el-tag v-if="item.email" type="info" size="small">
              <el-icon><Message /></el-icon>
              {{ item.email }}
            </el-tag>
            <el-tag :type="item.show_followed_models ? 'success' : 'info'" size="small">
              <el-icon v-if="item.show_followed_models"><Unlock /></el-icon>
              <el-icon v-else><Lock /></el-icon>
              模型{{ item.show_followed_models ? '公开' : '私密' }}
            </el-tag>
            <el-tag :type="item.show_followed_datasets ? 'success' : 'info'" size="small">
              <el-icon v-if="item.show_followed_datasets"><Unlock /></el-icon>
              <el-icon v-else><Lock /></el-icon>
              数据集{{ item.show_followed_datasets ? '公开' : '私密' }}
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Box, 
  Folder, 
  OfficeBuilding, 
  DataLine, 
  Calendar,
  User,
  UserFilled,
  Collection,
  Document,
  Loading,
  StarFilled,
  Cpu,
  Message,
  Lock,
  Unlock
} from '@element-plus/icons-vue'
import { getFollowedDatasets, unfollowDataset } from '@/api/datasets'
import { getFollowedModels, unfollowModel } from '@/api/models'
import { getFollowedUsers, unfollowUser } from '@/api/users'

const router = useRouter()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 后端基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:80'

// 处理头像URL，确保是完整路径
const getFullAvatarUrl = (avatar) => {
  if (!avatar) return defaultAvatar
  // 如果已经是完整URL，直接返回
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  // 确保路径以 /media/ 开头
  let path = avatar
  if (!path.startsWith('/')) {
    path = '/' + path
  }
  if (!path.startsWith('/media/')) {
    path = '/media' + path
  }
  return `${API_BASE_URL}${path}`
}

// 当前展示类型：model、dataset 或 user
const activeType = ref('dataset')  // 默认显示数据集
const loading = ref(false)

// 关注列表数据
const modelList = ref([])
const datasetList = ref([])
const userList = ref([])

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

// 数据集分类标签
const getDatasetCategoryLabel = (category) => {
  const map = { image: '图像', text: '文本', multimodal: '多模态' }
  return map[category] || category || '未分类'
}

// 模型分类标签
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

// 获取关注的模型列表
const fetchFollowedModels = async () => {
  loading.value = true
  try {
    const res = await getFollowedModels()
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      modelList.value = res.data.data.map(item => ({ ...item, unfollowing: false }))
    } else if (Array.isArray(res.data)) {
      modelList.value = res.data.map(item => ({ ...item, unfollowing: false }))
    } else {
      modelList.value = []
    }
  } catch (error) {
    console.error('获取关注模型失败:', error)
    ElMessage.error('获取关注列表失败')
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
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasetList.value = res.data.data.map(item => ({ ...item, unfollowing: false }))
    } else if (Array.isArray(res.data)) {
      datasetList.value = res.data.map(item => ({ ...item, unfollowing: false }))
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

// 获取关注的用户列表
const fetchFollowedUsers = async () => {
  loading.value = true
  try {
    const res = await getFollowedUsers()
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      userList.value = res.data.data.map(item => ({ ...item, unfollowing: false }))
    } else if (Array.isArray(res.data)) {
      userList.value = res.data.map(item => ({ ...item, unfollowing: false }))
    } else {
      userList.value = []
    }
  } catch (error) {
    console.error('获取关注用户失败:', error)
    ElMessage.error('获取关注列表失败')
    userList.value = []
  } finally {
    loading.value = false
  }
}

// 取消关注模型
const handleUnfollowModel = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消关注模型「${item.name}」吗？`,
      '取消关注',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    item.unfollowing = true
    const res = await unfollowModel(item.id)
    
    if (res.data?.code === 200 || res.data?.code === 204) {
      ElMessage.success('已取消关注')
      modelList.value = modelList.value.filter(m => m.id !== item.id)
    } else {
      ElMessage.error(res.data?.msg || '取消关注失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消关注失败:', error)
      ElMessage.error('取消关注失败，请稍后重试')
    }
  } finally {
    item.unfollowing = false
  }
}

// 取消关注数据集
const handleUnfollowDataset = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消关注数据集「${item.name}」吗？`,
      '取消关注',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    item.unfollowing = true
    const res = await unfollowDataset(item.id)
    
    if (res.data?.code === 200 || res.data?.code === 204) {
      ElMessage.success('已取消关注')
      datasetList.value = datasetList.value.filter(d => d.id !== item.id)
    } else {
      ElMessage.error(res.data?.msg || '取消关注失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消关注失败:', error)
      ElMessage.error('取消关注失败，请稍后重试')
    }
  } finally {
    item.unfollowing = false
  }
}

// 取消关注用户
const handleUnfollowUser = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消关注用户「${item.username}」吗？`,
      '取消关注',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    item.unfollowing = true
    const res = await unfollowUser(item.id)
    
    if (res.data?.code === 200 || res.data?.code === 204) {
      ElMessage.success('已取消关注')
      userList.value = userList.value.filter(u => u.id !== item.id)
    } else {
      ElMessage.error(res.data?.msg || '取消关注失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消关注失败:', error)
      ElMessage.error('取消关注失败，请稍后重试')
    }
  } finally {
    item.unfollowing = false
  }
}

// 跳转到用户主页
const goToUserProfile = (item) => {
  if (!item.show_followed_models && !item.show_followed_datasets) {
    ElMessage.warning('该用户未公开关注列表')
    return
  }
  router.push(`/user/${item.id}`)
}

// 监听类型切换，加载对应数据
watch(activeType, (newType) => {
  if (newType === 'model') {
    fetchFollowedModels()
  } else if (newType === 'dataset') {
    fetchFollowedDatasets()
  } else if (newType === 'user') {
    fetchFollowedUsers()
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
  color: var(--text-secondary);
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
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.follow-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.follow-card :deep(.el-card__body) {
  padding: 16px;
  background: var(--bg-secondary);
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
  background: linear-gradient(135deg, #1f6bff 0%, var(--bg-secondary) 100%);
  border: 1px solid var(--border-color);
  color: #58a6ff;
}

.dataset-icon {
  background: linear-gradient(135deg, #238636 0%, var(--bg-secondary) 100%);
  border: 1px solid var(--border-color);
  color: #3fb950;
}

.item-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.item-name.clickable {
  cursor: pointer;
  color: var(--accent-color);
}

.item-name.clickable:hover {
  text-decoration: underline;
  color: var(--accent-hover);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-bio {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-actions {
  display: flex;
  gap: 8px;
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
  background-color: var(--bg-body);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

/* Specific Tag Colors if needed, or let Element handle variants with opacity */
.card-info .el-tag--success {
  color: #3fb950;
  border-color: rgba(63, 185, 80, 0.3);
  background-color: rgba(63, 185, 80, 0.1);
}

.card-info .el-tag--warning {
  color: #d29922;
  border-color: rgba(210, 153, 34, 0.3);
  background-color: rgba(210, 153, 34, 0.1);
}

.card-info .el-tag--primary {
  color: #58a6ff;
  border-color: rgba(88, 166, 255, 0.3);
  background-color: rgba(88, 166, 255, 0.1);
}

.card-meta {
  display: flex;
  gap: 20px;
  color: var(--text-secondary);
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

:deep(.el-empty) {
  padding: 40px 0;
  --el-empty-description-color: var(--text-secondary);
}

.user-card .card-header {
  flex-wrap: wrap;
  gap: 10px;
}

@media (max-width: 768px) {
  .user-card .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .user-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>