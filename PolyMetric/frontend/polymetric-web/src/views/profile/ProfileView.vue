<template>
  <div class="profile-view">
    <el-row :gutter="30">
      <el-col :span="8">
        <el-card class="user-info">
          <el-avatar :size="120" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <h2>{{ form.username }}</h2>
          <p>{{ form.intro }}</p>
          <p>邮箱: {{ form.email }}</p>
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
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="头像">
          <el-upload action="#" :auto-upload="false" :show-file-list="false">
            <el-button type="primary" plain>上传头像</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="介绍">
          <el-input type="textarea" v-model="editForm.intro" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import FollowContent from '../../components/profile/FollowContent.vue'
import MyDatasets from '../../components/profile/MyDatasets.vue'
import MyTasks from '../../components/profile/MyTasks.vue'

const activeTab = ref('follow')
const showEdit = ref(false)

const form = reactive({
  username: localStorage.getItem('username') || 'User_name',
  intro: '个人介绍',
  email: localStorage.getItem('email') || 'example@163.com'
})

const editForm = reactive({ ...form })

const saveEdit = () => {
  form.username = editForm.username
  form.intro = editForm.intro
  form.email = editForm.email
  localStorage.setItem('username', form.username)
  localStorage.setItem('email', form.email)
  ElMessage.success('保存成功')
  showEdit.value = false
}
</script>

<style scoped>
.profile-view { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.user-info { text-align: center; background: #fafafa; border-radius: 12px; padding: 20px; color: #333; }
.el-tabs { background: #fafafa; border-radius: 12px; padding: 20px; }
</style>