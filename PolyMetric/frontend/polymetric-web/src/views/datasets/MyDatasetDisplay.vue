<template>
  <div class="my-dataset-display">
    <h3>个人数据集展示</h3>
    <el-carousel height="300px">
      <el-carousel-item v-for="i in 3" :key="i">
        <h4>数据集{{ i }} 预览</h4>
        <p>示例内容</p>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<style scoped>
.my-dataset-display { padding: 20px; }
</style>