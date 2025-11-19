<template>
  <el-dialog v-model="showDialog" title="创建评测任务" :draggable="true" width="500px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="数据集">
        <el-select v-model="form.dataset" placeholder="选择数据集">
          <el-option label="数学数据集" value="math" />
          <el-option label="视觉数据集" value="vision" />
          <el-option label="默认数据集" value="default" />
        </el-select>
      </el-form-item>
      <el-form-item label="评测方式">
        <el-radio-group v-model="form.type">
          <el-radio label="objective">客观评测</el-radio>
          <el-radio label="subjective">主观评测</el-radio>
          <el-radio label="adversarial">对抗评测</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog = false">取消</el-button>
      <el-button type="primary" @click="submitEval">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'

const showDialog = ref(false)
const form = ref({ dataset: '', type: '' })
const emit = defineEmits(['close'])

const submitEval = () => {
  if (!form.value.dataset || !form.value.type) {
    ElMessage.warning('请选择数据集和评测方式')
    return
  }
  // 模拟存储到数据库（后续替换 fetch API）
  localStorage.setItem('lastEval', JSON.stringify(form.value))
  ElMessage.success('任务创建成功，已提交到数据库')
  showDialog.value = false
  emit('close')
}
</script>

<style scoped>
/* 无需额外样式，Element Plus 默认模态 + 拖动 */
</style>