<template>
  <div class="evaluation-hall">
    <h3>评测主页面</h3>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" @click.native="$router.push('/evaluation/objective')">
          <h4>客观评测</h4>
          <p>自动化评分</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click.native="$router.push('/evaluation/subjective')">
          <h4>主观评测</h4>
          <p>0-10 分</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click.native="$router.push('/evaluation/adversarial')">
          <h4>对抗评测</h4>
          <p>比较优劣</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.evaluation-hall { padding: 20px; }
.el-card { cursor: pointer; text-align: center; }
</style>