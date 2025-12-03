<template>
  <el-dialog v-model="showDialog" title="创建评测任务" :draggable="true" width="500px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input v-model="form.taskName" placeholder="输入任务名称" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="输入任务描述" />
      </el-form-item>
      <el-form-item label="模型选择" v-if="form.type !== 'adversarial'">
        <el-select v-model="form.model" placeholder="选择模型">
          <el-option label="GPT-4v" value="1" />
          <el-option label="Google Gemini 3" value="2" />
          <el-option label="Deepseek-v1" value="3" />
        </el-select>
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
      <el-button @click="showDialog = false">取消</el-button>
      <el-button type="primary" @click="submitEval">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
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

const form = ref({ taskName: '', description: '', model: '', dataset: '', type: '' }) 

/**
 * 统一处理关闭逻辑，通知父组件更新 showEvalDialog 为 false
 */
const handleClose = () => {
    // 触发 update:showDialog 事件，告知父组件将 showEvalDialog 设为 false
    emit('update:showDialog', false) 
    emit('close') 
}

const submitEval = async() => {
  if (!form.value.name || !form.value.dataset || !form.value.type) {
    ElMessage.warning('请选择数据集和评测方式')
    return
  }
  
  // 模拟提交成功
  const requestBody = {
    "name": form.value.taskName,
    "description": form.value.description,
    "method": form.value.type,
    "dataset": form.value.dataset,
    // 只有在评测方式不是 'adversarial' 时，才包含 model 字段
    ...(form.value.type !== 'adversarial' ? { "model": form.value.model } : {})
  };
  if (form.value.type !== 'adversarial' && !form.value.model) {
      ElMessage.warning('请选择模型')
      return
  }
  
  try {
    const response = await fetch('/api/tasks/evaluation-tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (response.ok && response.status === 201) {
      const result = await response.json();
      
      ElMessage.success(`任务 [${result.name}] 创建成功!`);
      
      // 通知父组件任务创建成功，可能需要刷新列表
      emit('task-submitted', result); 
      
      // 提交成功后关闭弹窗
      handleClose();
      
    } else {
      // 处理非 201 状态码，例如 400 Bad Request
      const errorData = await response.json();
      ElMessage.error(`任务创建失败: ${errorData.detail || response.statusText}`);
    }
  } catch (error) {
    // 处理网络错误
    console.error('任务提交网络错误:', error);
    ElMessage.error('网络连接失败，请检查您的网络。');
  }
}
</script>

<style scoped>
/* 无需额外样式，Element Plus 默认模态 + 拖动 */
</style>