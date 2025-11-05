<template>
  <div class="dashboard">
    <h3>正在运行的任务</h3>
    <el-card class="task-card">
      <template #header>
        <div class="card-header">
          <span>任务名称</span>
          <el-tag type="primary">进行中</el-tag>
        </div>
      </template>
      <p><strong>发起人：</strong>wang</p>
      <p><strong>数据集：</strong>math_dataset</p>
      <p><strong>手机号：</strong>86-1582590695</p>
    </el-card>

    <el-button type="primary" style="margin-top: 20px">查看任务历史记录</el-button>
  </div>
</template>

<style scoped>
.dashboard { padding: 20px; }
.task-card { max-width: 500px; margin: 20px 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>