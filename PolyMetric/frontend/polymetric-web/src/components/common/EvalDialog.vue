<template>
  <el-dialog 
    :model-value="showDialog" 
    @update:modelValue="$emit('update:showDialog', $event)"
    @close="handleClose" 
    title="创建评测任务" 
    :draggable="true" 
    width="500px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input v-model="form.taskName" placeholder="输入任务名称" />
      </el-form-item>
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
      <el-button @click="handleClose">取消</el-button> 
      <el-button type="primary" @click="submitEval">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'

// 1. 接收 props：接收父组件 v-model:showDialog 传入的属性
const props = defineProps({
  showDialog: {
    type: Boolean,
    default: false
  }
})

// 2. 定义 emits：必须定义 update:showDialog，用于通知父组件更新
const emit = defineEmits(['update:showDialog', 'close']) 

const form = ref({ taskName: '', dataset: '', type: '' }) 

/**
 * 统一处理关闭逻辑，通知父组件更新 showEvalDialog 为 false
 */
const handleClose = () => {
    // 触发 update:showDialog 事件，告知父组件将 showEvalDialog 设为 false
    emit('update:showDialog', false) 
    emit('close') 
}

const submitEval = () => {
  if (!form.value.dataset || !form.value.type) {
    ElMessage.warning('请选择数据集和评测方式')
    return
  }
  
  // 模拟提交成功
  ElMessage.success('任务创建成功')
  
  // 提交成功后关闭弹窗
  handleClose()
}
</script>

<style scoped>
/* 无需额外样式，Element Plus 默认模态 + 拖动 */
</style>