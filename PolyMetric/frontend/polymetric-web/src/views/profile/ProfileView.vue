<template>
  <div class="profile-view">
    <el-row :gutter="30">
      <el-col :span="8">
        <el-card class="user-info">
          <el-avatar :size="120" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <h2>{{ form.username }}</h2>
          <p>{{ form.intro }}</p>
          <p>邮箱: {{ form.email }}</p>
          <p>手机号: {{ form.phone }}</p>
          <el-button type="primary" plain @click="showEdit = true">编辑</el-button>
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
          <el-upload action="#" :auto-upload="false" :show-file-list="false">
            <el-button type="primary" plain>上传头像</el-button>
          </el-upload>
          <p style="font-size: 12px; color: #999;">（暂不支持头像上传，请联系管理员）</p>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
          <p style="font-size: 12px; color: #999;">（用户名不可修改）</p>
        </el-form-item>
        <el-form-item label="介绍" prop="intro">
          <el-input type="textarea" v-model="editForm.intro" placeholder="请输入个人介绍" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import FollowContent from '../../components/profile/FollowContent.vue'
import MyDatasets from '../../components/profile/MyDatasets.vue'
import MyTasks from '../../components/profile/MyTasks.vue'

const activeTab = ref('follow')
const showEdit = ref(false)
const editFormRef = ref(null)

const form = reactive({
  username: '',
  intro: '',
  email: '',
  phone: ''
})

const editForm = reactive({
  username: '',
  intro: '',
  email: '',
  phone: ''
})

const editRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ]
}

// 页面加载时从后端获取用户信息
onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    const response = await fetch('http://127.0.0.1:8000/api/users/me/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      form.username = data.username
      form.intro = data.bio || ''
      form.email = data.email || ''
      form.phone = data.phone || ''
      Object.assign(editForm, form) // 同步到编辑表单
    } else {
      ElMessage.error('获取用户信息失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  }
})

// 保存编辑（调用后端 PUT 接口）
const saveEdit = () => {
  editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          ElMessage.error('请先登录')
          showEdit.value = false
          return
        }
        const response = await fetch('http://127.0.0.1:8000/api/users/me/', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            email: editForm.email,
            phone: editForm.phone,
            bio: editForm.intro
          })
        })
        if (response.ok) {
          const data = await response.json()
          form.email = data.email
          form.phone = data.phone
          form.intro = data.bio
          ElMessage.success('保存成功')
          showEdit.value = false
        } else {
          ElMessage.error('保存失败')
        }
      } catch (error) {
        ElMessage.error('网络错误')
      }
    } else {
      ElMessage.error('请输入正确信息')
    }
  })
}
</script>

<style scoped>
.profile-view { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.user-info { text-align: center; background: #fafafa; border-radius: 12px; padding: 20px; color: #333; }
.el-tabs { background: #fafafa; border-radius: 12px; padding: 20px; }
</style>