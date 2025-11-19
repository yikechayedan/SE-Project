<template>
  <div class="subjective-eval">
    <h3>主观评测（人工打分0-10）</h3>
    <el-slider v-model="score" :max="10" show-input />
    <el-button type="primary" style="margin-top: 20px;">提交</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const score = ref(5)
</script>

<style scoped>
.subjective-eval { padding: 20px; max-width: 500px; margin: 0 auto; }
</style>