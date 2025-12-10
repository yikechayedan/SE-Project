<template>
  <el-popover
    :visible="visible"
    placement="bottom-start"
    :width="280"
    trigger="click"
    @show="handleShow"
    @hide="visible = false"
  >
    <template #reference>
      <span 
        class="username-link" 
        @click.stop="handleClick"
        :class="{ 'is-self': isSelf }"
      >
        <slot>{{ username }}</slot>
      </span>
    </template>

    <!-- 弹窗内容 -->
    <div class="user-popover" v-loading="loading">
      <div class="user-header">
        <el-avatar :size="60" :src="userInfo.avatar || defaultAvatar" />
        <div class="user-basic">
          <h4>{{ userInfo.username || username }}</h4>
          <p class="email">{{ userInfo.email || '邮箱未公开' }}</p>
        </div>
      </div>
      
      <div class="user-intro">
        <p>{{ userInfo.bio || '这个人很懒，什么都没写~' }}</p>
      </div>

      <div class="user-permissions" v-if="!isSelf">
        <div class="permission-item">
          <el-icon><Box /></el-icon>
          <span>关注的模型</span>
          <el-icon v-if="!userInfo.show_followed_models" class="lock-icon"><Lock /></el-icon>
          <el-icon v-else class="unlock-icon"><Unlock /></el-icon>
        </div>
        <div class="permission-item">
          <el-icon><Folder /></el-icon>
          <span>关注的数据集</span>
          <el-icon v-if="!userInfo.show_followed_datasets" class="lock-icon"><Lock /></el-icon>
          <el-icon v-else class="unlock-icon"><Unlock /></el-icon>
        </div>
      </div>

      <div class="user-actions">
        <el-button 
          v-if="!isSelf"
          :type="userInfo.is_followed ? 'warning' : 'primary'" 
          size="small"
          :icon="userInfo.is_followed ? StarFilled : Star"
          @click="handleToggleFollow"
          :loading="followLoading"
        >
          {{ userInfo.is_followed ? '取消关注' : '关注' }}
        </el-button>
        <el-button 
          type="primary" 
          size="small" 
          plain
          :icon="User"
          @click="goToProfile"
          :disabled="!canViewProfile"
        >
          {{ isSelf ? '我的主页' : '查看主页' }}
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, Folder, Lock, Unlock, Star, StarFilled, User } from '@element-plus/icons-vue'
import { getPublicUserInfo, followUser, unfollowUser } from '@/api/users'

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  },
  username: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const visible = ref(false)
const loading = ref(false)
const followLoading = ref(false)

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

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

// 判断是否是自己
const currentUserId = computed(() => {
  const id = localStorage.getItem('userId')
  return id ? parseInt(id) : null
})

const isSelf = computed(() => {
  return currentUserId.value && currentUserId.value === parseInt(props.userId)
})

// 是否可以查看主页（自己 或者 至少有一个权限开放）
const canViewProfile = computed(() => {
  if (isSelf.value) return true
  return userInfo.value.show_followed_models || userInfo.value.show_followed_datasets
})

// 点击用户名
const handleClick = () => {
  visible.value = !visible.value
}

// 弹窗显示时加载用户信息
const handleShow = async () => {
  if (isSelf.value) {
    // 如果是自己，从本地获取基本信息
    userInfo.value = {
      id: currentUserId.value,
      username: localStorage.getItem('username') || props.username,
      avatar: localStorage.getItem('avatar') || '',
      email: localStorage.getItem('email') || '',
      bio: localStorage.getItem('bio') || '',
      show_followed_models: true,
      show_followed_datasets: true,
      is_followed: false
    }
    return
  }

  loading.value = true
  try {
    const res = await getPublicUserInfo(props.userId)
    if (res.data?.code === 200 && res.data.data) {
      userInfo.value = res.data.data
    } else {
      userInfo.value.username = props.username
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    userInfo.value.username = props.username
  } finally {
    loading.value = false
  }
}

// 关注/取消关注用户
const handleToggleFollow = async () => {
  followLoading.value = true
  try {
    if (userInfo.value.is_followed) {
      const res = await unfollowUser(props.userId)
      if (res.data?.code === 200) {
        userInfo.value.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '操作失败')
      }
    } else {
      const res = await followUser(props.userId)
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

// 跳转到用户主页
const goToProfile = () => {
  visible.value = false
  if (isSelf.value) {
    router.push('/profile')
  } else {
    router.push(`/user/${props.userId}`)
  }
}
</script>

<style scoped>
.username-link {
  color: #409eff;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.username-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.username-link.is-self {
  color: #67c23a;
}

.user-popover {
  padding: 5px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.user-basic h4 {
  margin: 0 0 5px;
  font-size: 16px;
  color: #303133;
}

.user-basic .email {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.user-intro {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 12px;
}

.user-intro p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.user-permissions {
  margin-bottom: 12px;
  padding: 8px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  font-size: 13px;
  color: #606266;
}

.permission-item span {
  flex: 1;
}

.lock-icon {
  color: #909399;
}

.unlock-icon {
  color: #67c23a;
}

.user-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}
</style>
