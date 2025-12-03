<template>
  <div class="adversarial-eval">
    <h3>对抗评测（人工评测哪边更好）</h3>
    <el-radio-group v-model="choice">
      <el-radio label="A">A 更好</el-radio>
      <el-radio label="B">B 更好</el-radio>
      <el-radio label="tie">平局</el-radio>
    </el-radio-group>
    <el-button type="primary" style="margin-top: 20px;">提交</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const choice = ref('A')
</script>

<style scoped>
.adversarial-eval { padding: 20px; max-width: 500px; margin: 0 auto; }
</style>