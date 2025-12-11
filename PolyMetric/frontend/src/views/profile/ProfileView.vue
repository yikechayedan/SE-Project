<template>
  <div class="profile-view">
    <el-row :gutter="30">
      <el-col :span="8">
        <el-card class="user-info">
          <div class="card-hero">
            <div class="avatar-wrap">
              <span class="avatar-glow" />
              <el-avatar :size="110" :src="avatarUrl" />
            </div>
            <div class="name-block">
              <div class="name-line">
                <h2>{{ form.username || '未命名用户' }}</h2>
                <el-tag size="small" effect="dark" type="info">个人主页</el-tag>
              </div>
              <p class="subtitle">{{ form.intro || '暂无个人介绍' }}</p>
            </div>
          </div>

          <el-divider />

          <div class="info-grid">
            <div class="info-item">
              <el-icon><Message /></el-icon>
              <div class="info-text">
                <span class="label">邮箱</span>
                <span class="value">{{ form.email || '未设置' }}</span>
              </div>
            </div>
            <div class="info-item">
              <el-icon><Phone /></el-icon>
              <div class="info-text">
                <span class="label">手机号</span>
                <span class="value">{{ form.phone || '未设置' }}</span>
              </div>
            </div>
            <div class="info-item">
              <el-icon><User /></el-icon>
              <div class="info-text">
                <span class="label">昵称</span>
                <span class="value">{{ form.username || '未设置' }}</span>
              </div>
            </div>
          </div>

          <div class="visibility-row">
            <el-tag :type="form.show_followed_models ? 'success' : 'warning'" effect="light">
              {{ form.show_followed_models ? '模型关注公开' : '模型关注隐藏' }}
            </el-tag>
            <el-tag :type="form.show_followed_datasets ? 'success' : 'warning'" effect="light">
              {{ form.show_followed_datasets ? '数据集关注公开' : '数据集关注隐藏' }}
            </el-tag>
          </div>

          <div class="action-row">
            <el-button type="primary" plain @click="openEditDialog">编辑资料</el-button>
            <el-button plain @click="openPrivacyDialog">
              <el-icon><Setting /></el-icon>
              隐私设置
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="关注" name="follow">
            <FollowContent v-if="activeTab==='follow'"/>
          </el-tab-pane>
          <el-tab-pane label="数据集" name="datasets">
            <MyDatasets v-if="activeTab==='datasets'"/>
          </el-tab-pane>
          <el-tab-pane label="任务" name="tasks">
            <MyTasks v-if="activeTab==='tasks'"/>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEdit" title="编辑个人信息" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="头像">
          <div class="avatar-upload">
            <el-avatar :size="80" :src="previewAvatarUrl" />
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleAvatarChange"
              accept="image/jpeg,image/png,image/gif"
            >
              <el-button type="primary" plain size="small">
                选择头像
              </el-button>
            </el-upload>
          </div>
          <p class="tip">支持 jpg/png/gif 格式，最大 2MB（保存时上传）</p>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
          <p class="tip">（用户名不可修改）</p>
        </el-form-item>
        <el-form-item label="个人介绍" prop="intro">
          <el-input 
            type="textarea" 
            v-model="editForm.intro" 
            placeholder="请输入个人介绍" 
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" maxlength="11" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" :loading="loading" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 隐私设置弹窗 -->
    <el-dialog v-model="showPrivacy" title="隐私设置" width="450px">
      <div class="privacy-settings">
        <p class="privacy-desc">设置您的关注列表对其他用户的可见性</p>
        
        <div class="privacy-item">
          <div class="privacy-label">
            <el-icon><Box /></el-icon>
            <span>公开关注的模型</span>
          </div>
          <el-switch v-model="privacyForm.show_followed_models" />
        </div>
        
        <div class="privacy-item">
          <div class="privacy-label">
            <el-icon><Folder /></el-icon>
            <span>公开关注的数据集</span>
          </div>
          <el-switch v-model="privacyForm.show_followed_datasets" />
        </div>
        
        <el-alert type="info" :closable="false" style="margin-top: 15px;">
          <template #title>
            开启后，其他用户可以在您的主页查看对应的关注列表
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="showPrivacy = false">取消</el-button>
        <el-button type="primary" :loading="privacyLoading" @click="savePrivacy">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Setting, Box, Folder, Message, Phone, User } from '@element-plus/icons-vue'
import { getUserInfo, updateUserInfo, uploadAvatar, updatePrivacySettings } from '@/api/users'
import FollowContent from '../../components/profile/FollowContent.vue'
import MyDatasets from '../../components/profile/MyDatasets.vue'
import MyTasks from '../../components/profile/MyTasks.vue'

const router = useRouter()
const activeTab = ref('follow')
const showEdit = ref(false)
const showPrivacy = ref(false)
const loading = ref(false)
const privacyLoading = ref(false)
const editFormRef = ref(null)

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const form = reactive({
  username: '',
  intro: '',
  email: '',
  phone: '',
  avatar: '',
  show_followed_models: true,
  show_followed_datasets: true
})

const editForm = reactive({
  username: '',
  intro: '',
  email: '',
  phone: ''
})

const privacyForm = reactive({
  show_followed_models: true,
  show_followed_datasets: true
})

// 待上传的头像文件（用于延迟上传）
const pendingAvatarFile = ref(null)
// 预览用的头像URL（本地预览，不需要上传）
const previewAvatarUrlLocal = ref('')

// 计算头像 URL（用于页面展示）
const avatarUrl = computed(() => form.avatar || defaultAvatar)

// 计算编辑弹窗中的头像预览 URL
const previewAvatarUrl = computed(() => {
  // 如果有本地预览图（用户选择了新头像但未保存）
  if (previewAvatarUrlLocal.value) {
    return previewAvatarUrlLocal.value
  }
  // 否则显示当前头像
  return form.avatar || defaultAvatar
})

const editRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ],
  intro: [
    { max: 200, message: '个人介绍不能超过200字', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await fetchUserInfo()
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const res = await getUserInfo()
    
    // 处理后端返回的 { code, msg, data } 格式
    let userData = res.data
    if (res.data?.code === 200 && res.data?.data) {
      userData = res.data.data
    }
    
    form.username = userData.username || ''
    form.intro = userData.bio || ''
    form.email = userData.email || ''
    form.phone = userData.phone || ''
    form.avatar = userData.avatar || ''
    form.show_followed_models = userData.show_followed_models !== false
    form.show_followed_datasets = userData.show_followed_datasets !== false
    
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.clear()
      router.push('/login')
    } else {
      ElMessage.error('获取用户信息失败')
    }
  }
}

// 打开编辑弹窗时，同步数据
const openEditDialog = () => {
  editForm.username = form.username
  editForm.intro = form.intro
  editForm.email = form.email
  editForm.phone = form.phone
  // 清除待上传的头像
  pendingAvatarFile.value = null
  previewAvatarUrlLocal.value = ''
  showEdit.value = true
}

// 取消编辑
const cancelEdit = () => {
  // 清除本地预览
  if (previewAvatarUrlLocal.value) {
    URL.revokeObjectURL(previewAvatarUrlLocal.value)
  }
  pendingAvatarFile.value = null
  previewAvatarUrlLocal.value = ''
  showEdit.value = false
}

// 打开隐私设置弹窗
const openPrivacyDialog = () => {
  privacyForm.show_followed_models = form.show_followed_models
  privacyForm.show_followed_datasets = form.show_followed_datasets
  showPrivacy.value = true
}

// 头像选择处理（不立即上传，仅预览）
const handleAvatarChange = (uploadFile) => {
  const file = uploadFile.raw
  
  // 1. 验证文件格式
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('文件格式不支持，仅支持 jpg/png/gif')
    return
  }
  
  // 2. 验证文件大小（最大 2MB）
  const maxSize = 2 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件过大，最大支持 2MB')
    return
  }
  
  // 3. 保存文件引用，等待保存时上传
  pendingAvatarFile.value = file
  
  // 4. 创建本地预览URL
  if (previewAvatarUrlLocal.value) {
    URL.revokeObjectURL(previewAvatarUrlLocal.value)
  }
  previewAvatarUrlLocal.value = URL.createObjectURL(file)
  
  ElMessage.success('头像已选择，点击保存后生效')
}

// 保存编辑
const saveEdit = () => {
  editFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请输入正确信息')
      return
    }
    
    loading.value = true
    
    try {
      // 1. 如果有待上传的头像，先上传头像
      if (pendingAvatarFile.value) {
        try {
          const avatarRes = await uploadAvatar(pendingAvatarFile.value)
          if (avatarRes.data?.code === 200 && avatarRes.data?.data?.avatar) {
            form.avatar = avatarRes.data.data.avatar
            ElMessage.success('头像上传成功')
          } else {
            ElMessage.warning(avatarRes.data?.msg || '头像上传失败，其他信息仍将保存')
          }
        } catch (avatarError) {
          console.error('头像上传失败:', avatarError)
          ElMessage.warning('头像上传失败，其他信息仍将保存')
        }
      }
      
      // 2. 更新用户基本信息
      const res = await updateUserInfo({
        email: editForm.email,
        phone: editForm.phone,
        bio: editForm.intro
      })
      
      // 处理返回数据
      let updatedData = res.data
      if (res.data?.code === 200 && res.data?.data) {
        updatedData = res.data.data
      }
      
      // 更新本地数据
      if (updatedData.email !== undefined) form.email = updatedData.email
      if (updatedData.phone !== undefined) form.phone = updatedData.phone
      if (updatedData.bio !== undefined) form.intro = updatedData.bio
      
      // 清理
      pendingAvatarFile.value = null
      if (previewAvatarUrlLocal.value) {
        URL.revokeObjectURL(previewAvatarUrlLocal.value)
        previewAvatarUrlLocal.value = ''
      }
      
      ElMessage.success('保存成功')
      showEdit.value = false
      
    } catch (error) {
      console.error('保存失败:', error)
      if (error.response?.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.clear()
        router.push('/login')
      } else if (error.response?.status === 405) {
        // 后端不支持此方法
        ElMessage.error('更新用户资料失败：后端接口不支持此操作')
        console.error('提示：后端 /api/users/me/ 需要支持 PUT/PATCH 方法')
      } else if (error.response?.status === 400) {
        ElMessage.error(error.response?.data?.msg || '输入信息有误')
      } else {
        ElMessage.error('保存失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  })
}

// 保存隐私设置
const savePrivacy = async () => {
  privacyLoading.value = true
  try {
    const res = await updatePrivacySettings({
      show_followed_models: privacyForm.show_followed_models,
      show_followed_datasets: privacyForm.show_followed_datasets
    })
    
    if (res.data?.code === 200) {
      form.show_followed_models = privacyForm.show_followed_models
      form.show_followed_datasets = privacyForm.show_followed_datasets
      ElMessage.success('隐私设置已更新')
      showPrivacy.value = false
    } else {
      ElMessage.error(res.data?.msg || '设置更新失败')
    }
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.clear()
      router.push('/login')
    } else {
      ElMessage.error('设置更新失败，请稍后重试')
    }
  } finally {
    privacyLoading.value = false
  }
}
</script>

<style scoped>
.profile-view {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 45%, #f9fbff 100%);
  border-radius: 14px;
  box-shadow: 0 6px 28px rgba(31, 41, 61, 0.08);
  min-height: 100%;
}

.user-info {
  position: relative;
  overflow: hidden;
  border: none;
  background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(18, 38, 63, 0.06);
  padding: 26px 22px;
}

.user-info::before {
  content: '';
  position: absolute;
  right: -60px;
  top: -80px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle at 30% 30%, rgba(96, 130, 255, 0.18), rgba(96, 130, 255, 0));
  transform: rotate(-12deg);
}

.card-hero {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-wrap {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-glow {
  position: absolute;
  width: 118px;
  height: 118px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(96, 130, 255, 0.15), rgba(96, 130, 255, 0.02));
  filter: blur(2px);
}

.name-block {
  flex: 1;
}

.name-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info h2 {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}

.subtitle {
  margin: 8px 0 0;
  color: #5b667a;
  font-size: 14px;
}

.info-grid {
  margin-top: 12px;
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f6f8fb;
  border-radius: 12px;
  border: 1px solid #eef2f9;
}

.info-item .el-icon {
  font-size: 18px;
  color: #5f8bff;
}

.info-text {
  display: flex;
  flex-direction: column;
}

.label {
  color: #7a869a;
  font-size: 13px;
}

.value {
  color: #1f2d3d;
  font-weight: 600;
}

.visibility-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0 10px;
}

.action-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.el-tabs {
  background: #ffffff;
  border-radius: 14px;
  padding: 16px 20px;
  box-shadow: 0 10px 30px rgba(18, 38, 63, 0.06);
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

/* 隐私设置样式 */
.privacy-settings {
  padding: 10px 0;
}

.privacy-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.privacy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.privacy-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #303133;
}

.privacy-label .el-icon {
  font-size: 18px;
  color: #409eff;
}
</style>

