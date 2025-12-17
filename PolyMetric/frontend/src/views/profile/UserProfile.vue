<template>
  <div class="user-profile">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <el-row v-else :gutter="30">
      <!-- 左侧：用户信息卡片 -->
      <el-col :span="8">
        <el-card class="user-card">
          <div class="avatar-section">
            <el-avatar :size="120" :src="userInfo.avatar || defaultAvatar" />
          </div>
          <h2 class="username">{{ userInfo.username }}</h2>
          <p class="bio">{{ userInfo.bio || '这个人很懒，什么都没写~' }}</p>
          <p class="email" v-if="userInfo.email">
            <el-icon><Message /></el-icon>
            {{ userInfo.email }}
          </p>
          
          <div class="follow-btn">
            <el-button 
              :type="userInfo.is_followed ? 'warning' : 'primary'" 
              round
              :icon="userInfo.is_followed ? StarFilled : Star"
              @click="handleToggleFollow"
              :loading="followLoading"
            >
              {{ userInfo.is_followed ? '取消关注' : '关注 TA' }}
            </el-button>
          </div>

          <!-- 权限状态显示 -->
          <div class="permission-status">
            <div class="permission-item" :class="{ active: userInfo.show_followed_models }">
              <el-icon><Box /></el-icon>
              <span>模型</span>
              <el-icon v-if="userInfo.show_followed_models"><Unlock /></el-icon>
              <el-icon v-else><Lock /></el-icon>
            </div>
            <div class="permission-item" :class="{ active: userInfo.show_followed_datasets }">
              <el-icon><Folder /></el-icon>
              <span>数据集</span>
              <el-icon v-if="userInfo.show_followed_datasets"><Unlock /></el-icon>
              <el-icon v-else><Lock /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：关注内容 -->
      <el-col :span="16">
        <el-card class="content-card">
          <!-- 全部锁定时显示 -->
          <div v-if="!userInfo.show_followed_models && !userInfo.show_followed_datasets" class="locked-content">
            <el-icon :size="64" class="lock-big"><Lock /></el-icon>
            <h3>该用户未公开关注列表</h3>
            <p>用户已将关注的模型和数据集设为私密</p>
          </div>

          <!-- 有权限时显示标签页 -->
          <el-tabs v-else v-model="activeTab" class="follow-tabs">
            <el-tab-pane 
              v-if="userInfo.show_followed_models" 
              label="关注的模型" 
              name="models"
            >
              <div v-if="modelsLoading" class="tab-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
              <div v-else-if="followedModels.length === 0" class="empty-tip">
                <el-empty description="暂无关注的模型" />
              </div>
              <div v-else class="follow-list">
                <el-card 
                  v-for="item in followedModels" 
                  :key="item.id" 
                  shadow="hover" 
                  class="follow-item"
                >
                  <div class="item-header">
                    <el-icon class="type-icon model-icon"><Box /></el-icon>
                    <span class="item-name">{{ item.name }}</span>
                  </div>
                  <div class="item-info">
                    <el-tag type="info" size="small">{{ item.company || '未知公司' }}</el-tag>
                    <el-tag :type="getCategoryType(item.category)" size="small">
                      {{ getCategoryLabel(item.category) }}
                    </el-tag>
                    <el-tag type="success" size="small">{{ item.parameter_size || '未知' }}</el-tag>
                  </div>
                </el-card>
              </div>
            </el-tab-pane>

            <el-tab-pane 
              v-if="userInfo.show_followed_datasets" 
              label="关注的数据集" 
              name="datasets"
            >
              <div v-if="datasetsLoading" class="tab-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
              <div v-else-if="followedDatasets.length === 0" class="empty-tip">
                <el-empty description="暂无关注的数据集" />
              </div>
              <div v-else class="follow-list">
                <el-card 
                  v-for="item in followedDatasets" 
                  :key="item.id" 
                  shadow="hover" 
                  class="follow-item"
                >
                  <div class="item-header">
                    <el-icon class="type-icon dataset-icon"><Folder /></el-icon>
                    <span class="item-name">{{ item.name }}</span>
                  </div>
                  <div class="item-info">
                    <el-tag type="warning" size="small">{{ item.creator_username || '未知' }}</el-tag>
                    <el-tag type="primary" size="small">
                      {{ getDatasetCategoryLabel(item.category) }}
                    </el-tag>
                    <el-tag type="success" size="small">{{ formatFileSize(item.file_size) }}</el-tag>
                  </div>
                </el-card>
              </div>
            </el-tab-pane>

            <!-- 模型权限未开放时显示锁定提示 -->
            <el-tab-pane 
              v-if="!userInfo.show_followed_models && userInfo.show_followed_datasets" 
              name="models-locked"
              disabled
            >
              <template #label>
                <span class="locked-tab">
                  <el-icon><Lock /></el-icon>
                  关注的模型
                </span>
              </template>
            </el-tab-pane>

            <!-- 数据集权限未开放时显示锁定提示 -->
            <el-tab-pane 
              v-if="userInfo.show_followed_models && !userInfo.show_followed_datasets" 
              name="datasets-locked"
              disabled
            >
              <template #label>
                <span class="locked-tab">
                  <el-icon><Lock /></el-icon>
                  关注的数据集
                </span>
              </template>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, Folder, Lock, Unlock, Star, StarFilled, Loading, Message } from '@element-plus/icons-vue'
import { getPublicUserInfo, getUserFollowedModels, getUserFollowedDatasets, followUser, unfollowUser } from '@/api/users'

const route = useRoute()
const router = useRouter()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 状态
const loading = ref(true)
const followLoading = ref(false)
const modelsLoading = ref(false)
const datasetsLoading = ref(false)

// 用户信息
const userInfo = ref({
  id: null,
  username: '',
  avatar: '',
  email: '',
  bio: '',
  show_followed_models: false,
  show_followed_datasets: false,
  is_followed: false
})

// 关注列表
const followedModels = ref([])
const followedDatasets = ref([])

// 当前标签页
const activeTab = ref('')

// 用户ID
const userId = computed(() => route.params.id)

// 分类标签
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

const getDatasetCategoryLabel = (category) => {
  const map = { image: '图像', text: '文本', multimodal: '多模态' }
  return map[category] || category || '未分类'
}

const formatFileSize = (size) => {
  if (!size) return '未知'
  return typeof size === 'number' ? size.toFixed(2) + ' MB' : size
}

// 加载用户信息
const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await getPublicUserInfo(userId.value)
    if (res.data?.code === 200 && res.data.data) {
      userInfo.value = res.data.data
      
      // 设置默认标签页
      if (userInfo.value.show_followed_models) {
        activeTab.value = 'models'
      } else if (userInfo.value.show_followed_datasets) {
        activeTab.value = 'datasets'
      }
    } else {
      ElMessage.error('用户不存在')
      router.push('/home')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
    router.push('/home')
  } finally {
    loading.value = false
  }
}

// 加载关注的模型
const loadFollowedModels = async () => {
  if (!userInfo.value.show_followed_models) return
  
  modelsLoading.value = true
  try {
    const res = await getUserFollowedModels(userId.value)
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      followedModels.value = res.data.data
    }
  } catch (error) {
    console.error('获取关注模型失败:', error)
  } finally {
    modelsLoading.value = false
  }
}

// 加载关注的数据集
const loadFollowedDatasets = async () => {
  if (!userInfo.value.show_followed_datasets) return
  
  datasetsLoading.value = true
  try {
    const res = await getUserFollowedDatasets(userId.value)
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      followedDatasets.value = res.data.data
    }
  } catch (error) {
    console.error('获取关注数据集失败:', error)
  } finally {
    datasetsLoading.value = false
  }
}

// 关注/取消关注用户
const handleToggleFollow = async () => {
  followLoading.value = true
  try {
    if (userInfo.value.is_followed) {
      const res = await unfollowUser(userId.value)
      if (res.data?.code === 200) {
        userInfo.value.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '操作失败')
      }
    } else {
      const res = await followUser(userId.value)
      if (res.data?.code === 200 || res.data?.code === 201) {
        userInfo.value.is_followed = true
        ElMessage.success('关注成功')
      } else {
        ElMessage.error(res.data?.msg || '操作失败')
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
    followLoading.value = false
  }
}

// 监听标签页切换
watch(activeTab, (newTab) => {
  if (newTab === 'models' && followedModels.value.length === 0) {
    loadFollowedModels()
  } else if (newTab === 'datasets' && followedDatasets.value.length === 0) {
    loadFollowedDatasets()
  }
})

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    followedModels.value = []
    followedDatasets.value = []
    loadUserInfo()
  }
})

onMounted(async () => {
  // 检查是否是自己
  const currentUserId = localStorage.getItem('userId')
  if (currentUserId && currentUserId === userId.value) {
    router.push('/profile')
    return
  }
  
  await loadUserInfo()
  
  // 加载默认标签页的数据
  if (activeTab.value === 'models') {
    loadFollowedModels()
  } else if (activeTab.value === 'datasets') {
    loadFollowedDatasets()
  }
})
</script>

<style scoped>
.user-profile {
  padding: 20px;
  min-height: calc(100vh - 140px);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #909399;
}

.loading-container .el-icon {
  margin-bottom: 10px;
}

.user-card {
  text-align: center;
  background: white;
  border-radius: 16px;
  padding: 30px 20px;
}

.avatar-section {
  margin-bottom: 15px;
}

.username {
  margin: 0 0 10px;
  font-size: 24px;
  color: #303133;
}

.bio {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.6;
}

.email {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 20px;
}

.follow-btn {
  margin-bottom: 20px;
}

.permission-status {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #909399;
  padding: 8px 12px;
  border-radius: 20px;
  background: #f5f7fa;
}

.permission-item.active {
  color: #67c23a;
  background: #f0f9eb;
}

.content-card {
  height: 100%;
  min-height: 500px;
  border-radius: 16px;
}

.locked-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.lock-big {
  margin-bottom: 20px;
  color: #c0c4cc;
}

.locked-content h3 {
  margin: 0 0 10px;
  color: #606266;
}

.locked-content p {
  margin: 0;
  font-size: 14px;
}

.follow-tabs {
  min-height: 400px;
}

.tab-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 60px 0;
  color: #909399;
}

.empty-tip {
  padding: 40px 0;
}

.follow-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 0;
}

.follow-item {
  border-radius: 10px;
  transition: all 0.3s;
}

.follow-item:hover {
  transform: translateX(5px);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.type-icon {
  font-size: 20px;
  padding: 6px;
  border-radius: 6px;
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
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.item-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.locked-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #c0c4cc;
}

:deep(.el-tabs__item.is-disabled) {
  cursor: not-allowed;
}
</style>
