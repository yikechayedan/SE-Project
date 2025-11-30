<template>
  <div class="profile-view">
    <el-row :gutter="30">
      <el-col :span="8">
        <el-card class="user-info">
          <el-avatar :size="120" :src="avatarUrl" />
          <h2>{{ form.username }}</h2>
          <p>{{ form.intro || '暂无个人介绍' }}</p>
          <p>邮箱: {{ form.email || '未设置' }}</p>
          <p>手机号: {{ form.phone || '未设置' }}</p>
          <el-button type="primary" plain @click="openEditDialog">编辑</el-button>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="关注" name="follow">
            <FollowContent />
          </el-tab-pane>
          <el-tab-pane label="数据集" name="datasets">
            <MyDatasets />
          </el-tab-pane>
          <el-tab-pane label="任务" name="tasks">
            <MyTasks />
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEdit" title="编辑个人信息" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="头像">
          <div class="avatar-upload">
            <el-avatar :size="80" :src="avatarUrl" />
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleAvatarChange"
              accept="image/jpeg,image/png,image/gif"
              :disabled="avatarUploading"
            >
              <el-button type="primary" plain size="small" :loading="avatarUploading">
                {{ avatarUploading ? '上传中...' : '上传头像' }}
              </el-button>
            </el-upload>
          </div>
          <p class="tip">支持 jpg/png/gif 格式，最大 2MB</p>
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
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserInfo, updateUserInfo, uploadAvatar } from '@/api/users'
import FollowContent from '../../components/profile/FollowContent.vue'
import MyDatasets from '../../components/profile/MyDatasets.vue'
import MyTasks from '../../components/profile/MyTasks.vue'

const router = useRouter()
const activeTab = ref('follow')
const showEdit = ref(false)
const loading = ref(false)
const avatarUploading = ref(false)
const editFormRef = ref(null)

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const form = reactive({
  username: '',
  intro: '',
  email: '',
  phone: '',
  avatar: ''
})

const editForm = reactive({
  username: '',
  intro: '',
  email: '',
  phone: ''
})

// 计算头像 URL
const avatarUrl = computed(() => form.avatar || defaultAvatar)

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
    const data = res.data
    
    form.username = data.username || ''
    form.intro = data.bio || ''
    form.email = data.email || ''
    form.phone = data.phone || ''
    form.avatar = data.avatar || ''
    
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
  showEdit.value = true
}

// 头像上传处理
const handleAvatarChange = async (uploadFile) => {
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
  
  // 3. 上传到后端
  avatarUploading.value = true
  try {
    const res = await uploadAvatar(file)
    
    // 根据后端返回格式处理
    if (res.data && res.data.code === 200) {
      form.avatar = res.data.data.avatar
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error(res.data?.msg || '上传失败')
    }
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.clear()
      router.push('/login')
    } else if (error.response?.status === 413) {
      ElMessage.error('文件过大，最大支持 2MB')
    } else {
      ElMessage.error(error.response?.data?.msg || '头像上传失败')
    }
  } finally {
    avatarUploading.value = false
  }
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
      const res = await updateUserInfo({
        email: editForm.email,
        phone: editForm.phone,
        bio: editForm.intro
      })
      
      const data = res.data
      // 更新本地数据
      form.email = data.email || ''
      form.phone = data.phone || ''
      form.intro = data.bio || ''
      
      ElMessage.success('保存成功')
      showEdit.value = false
      
    } catch (error) {
      if (error.response?.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.clear()
        router.push('/login')
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
</script>

<style scoped>
.profile-view { 
  padding: 20px; 
  background: white; 
  border-radius: 8px; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
  height: 100%; 
}

.user-info { 
  text-align: center; 
  background: #fafafa; 
  border-radius: 12px; 
  padding: 30px 20px; 
  color: #333; 
}

.user-info h2 {
  margin: 15px 0 10px;
  font-size: 22px;
}

.user-info p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

.el-tabs { 
  background: #fafafa; 
  border-radius: 12px; 
  padding: 20px; 
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
</style>
