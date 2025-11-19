<template>
  <div class="profile-page">
    <el-row :gutter="30">
      <el-col :span="8">
        <el-card class="user-card">
          <div class="avatar">
            <el-avatar :size="120" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          </div>
          <h2 style="margin:20px 0 10px;color:#333;">User_name</h2>
          <p style="color:#999;margin-bottom:20px;">个人介绍</p>
          <el-button type="primary" plain round>编辑资料</el-button>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card style="height:100%;">
          <el-tabs v-model="activeTab" class="custom-tabs">
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FollowContent from '../../components/profile/FollowContent.vue'
import MyDatasets from '../../components/profile/MyDatasets.vue'
import MyTasks from '../../components/profile/MyTasks.vue'

const activeTab = ref('follow')
</script>

<style scoped>
.profile-page { padding: 20px; }
.user-card { text-align: center; height: 100%; background: white; border-radius: 16px; }
.custom-tabs :deep(.el-tabs__item) { color: #ccc; }
.custom-tabs :deep(.el-tabs__item.is-active) { color: #409eff; }
</style>