<template>
  <el-popover
    ref="popoverRef"
    :visible="visible"
    placement="bottom-start"
    :width="300"
    trigger="click"
    popper-class="user-popover-popper"
    @show="handleShow"
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
      <!-- 关闭按钮 -->
      <el-icon class="close-btn" @click="closePopover"><Close /></el-icon>
      
      <!-- 用户头像和基本信息 -->
      <div class="user-header">
        <el-avatar :size="64" :src="userInfo.avatar || defaultAvatar" class="user-avatar" />
        <div class="user-basic">
          <h4 class="user-name">
            {{ userInfo.username || username }}
            <el-tag v-if="isSelf" size="small" type="success" class="self-tag">我</el-tag>
          </h4>
          <p class="user-email">
            <el-icon><Message /></el-icon>
            {{ userInfo.email || '邮箱未公开' }}
          </p>
        </div>
      </div>
      
      <!-- 个人简介 -->
      <div class="user-bio">
        <p>{{ userInfo.bio || '这个人很懒，什么都没写~' }}</p>
      </div>

      <!-- 隐私权限状态（非自己才显示） -->
      <div class="user-permissions" v-if="!isSelf">
        <div class="permission-item" :class="{ 'is-public': userInfo.show_followed_models }">
          <el-icon class="permission-icon"><Box /></el-icon>
          <span class="permission-text">关注的模型</span>
          <el-icon v-if="userInfo.show_followed_models" class="status-icon unlock"><Unlock /></el-icon>
          <el-icon v-else class="status-icon lock"><Lock /></el-icon>
        </div>
        <div class="permission-item" :class="{ 'is-public': userInfo.show_followed_datasets }">
          <el-icon class="permission-icon"><Folder /></el-icon>
          <span class="permission-text">关注的数据集</span>
          <el-icon v-if="userInfo.show_followed_datasets" class="status-icon unlock"><Unlock /></el-icon>
          <el-icon v-else class="status-icon lock"><Lock /></el-icon>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="user-actions">
        <el-button 
          v-if="!isSelf"
          :type="userInfo.is_followed ? 'warning' : 'primary'" 
          size="small"
          :icon="userInfo.is_followed ? StarFilled : Star"
          @click="handleToggleFollow"
          :loading="followLoading"
          round
        >
          {{ userInfo.is_followed ? '取消关注' : '关注' }}
        </el-button>
        <el-button 
          type="primary" 
          size="small" 
          plain
          :icon="User"
          @click="goToProfile"
          round
        >
          {{ isSelf ? '进入个人中心' : '查看主页' }}
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, Folder, Lock, Unlock, Star, StarFilled, User, Message, Close } from '@element-plus/icons-vue'
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
const popoverRef = ref(null)
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

// 关闭弹窗
const closePopover = () => {
  visible.value = false
}

// 点击外部关闭弹窗
const handleClickOutside = (event) => {
  if (!visible.value) return
  
  // 检查点击是否在弹窗内部
  const popoverEl = document.querySelector('.user-popover-popper')
  const referenceEl = popoverRef.value?.$el?.querySelector('.username-link')
  
  if (popoverEl && popoverEl.contains(event.target)) {
    return // 点击在弹窗内部，不关闭
  }
  if (referenceEl && referenceEl.contains(event.target)) {
    return // 点击在触发元素上，不关闭（由 handleClick 处理）
  }
  
  // 点击在外部，关闭弹窗
  visible.value = false
}

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
  if (isSelf.value) {
    ElMessage.warning('不能关注自己哦')
    return
  }
  
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

// 生命周期钩子 - 添加全局点击监听
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.username-link {
  color: var(--accent-color);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.username-link:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.username-link.is-self {
  color: var(--success-color);
}

.username-link.is-self:hover {
  color: var(--success-color);
}

.user-popover {
  padding: 5px;
  position: relative;
  /* Ensure parent inherits dark theme */
  color: var(--text-primary);
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  color: var(--danger-color);
  background: rgba(248, 81, 73, 0.1);
}

/* 用户头部信息 */
.user-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
  padding-right: 20px;
}

.user-avatar {
  flex-shrink: 0;
  border: 2px solid var(--border-color);
}

.user-basic {
  flex: 1;
  min-width: 0;
}

.user-name {
  margin: 0 0 6px;
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.self-tag {
  font-size: 10px;
  padding: 0 6px;
  height: 18px;
  line-height: 16px;
}

.user-email {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 个人简介 */
.user-bio {
  padding: 10px 12px;
  background: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 12px;
}

.user-bio p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  word-break: break-word;
}

/* 权限状态 */
.user-permissions {
  margin-bottom: 15px;
  padding: 10px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: all 0.2s;
  background: var(--bg-body);
  border: 1px solid transparent;
}

.permission-item:last-child {
  margin-bottom: 0;
}

.permission-item.is-public {
  background: rgba(35, 134, 54, 0.1);
  border-color: rgba(35, 134, 54, 0.2);
}

.permission-icon {
  font-size: 14px;
  color: var(--text-secondary);
}

.permission-item.is-public .permission-icon {
  color: var(--success-color);
}

.permission-text {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
}

.status-icon {
  font-size: 14px;
}

.status-icon.lock {
  color: var(--text-secondary);
}

.status-icon.unlock {
  color: var(--success-color);
}

/* 操作按钮 */
.user-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.user-actions .el-button {
  flex: 1;
}
</style>