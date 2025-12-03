<template>
  <div class="objective-eval">
    <h3>客观评测页面</h3>
    <el-form>
      <el-form-item label="模型">
        <el-select v-model="form.model" placeholder="选择模型">
          <el-option label="Model1" value="model1" />
        </el-select>
      </el-form-item>
      <el-form-item label="数据集">
        <el-select v-model="form.dataset" placeholder="选择数据集">
          <el-option label="Dataset1" value="dataset1" />
        </el-select>
      </el-form-item>
      <el-button type="primary">启动评测</el-button>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
const form = reactive({ model: '', dataset: '' })
</script>

<style scoped>
.objective-eval { padding: 20px; max-width: 500px; margin: 0 auto; }
</style>