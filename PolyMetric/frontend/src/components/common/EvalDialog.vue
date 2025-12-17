<template>
  <el-dialog v-model="isVisible" title="创建评测任务" :draggable="true" width="500px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input v-model="form.taskName" placeholder="输入任务名称" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="输入任务描述" />
      </el-form-item>
      <el-form-item label="模型选择">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedModelName" 
                     placeholder="选择模型" 
                     :loading="modelLoading"
                     style="flex: 1;"> <el-option
              v-for="model in filteredModelsList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            />
          </el-select>

          <el-input 
            v-model="modelSearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="模型二选择" v-if="form.type === 'adversarial'">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedModelName2" 
                     placeholder="选择模型二" 
                     :loading="modelLoading"
                     style="flex: 1;"> <el-option
              v-for="model in filteredModelsList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            />
          </el-select>

          <el-input 
            v-model="modelSearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="数据集">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedDatasetName" 
                     placeholder="选择数据集" 
                     :loading="datasetLoading"
                     style="flex: 1;"> <el-option
              v-for="dataset in filteredDatasetsList"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.name"
            />
          </el-select>

          <el-input 
            v-model="datasetSearchQuery" 
            placeholder="搜索数据集" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
          />
        </div>
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
import { ref, defineProps, defineEmits, computed, onMounted} from 'vue'
import { ElMessage } from 'element-plus'
import { createEvaluationTask, runEvaluationTask } from '@/api/tasks.js'
import { getAllDatasets } from '@/api/datasets.js'
import { getAllModels } from '@/api/models.js' 

// 存储从 API 获取的模型和数据集列表
const modelsList = ref([])
const datasetsList = ref([])

// 加载状态
const modelLoading = ref(false)
const datasetLoading = ref(false)
const modelSearchQuery = ref('')
const datasetSearchQuery = ref('') 

// 1. 接收 props：接收父组件 v-model:showDialog 传入的属性
const props = defineProps({
    showDialog: {
      type: Boolean,
      default: false
    }
})

// 2. 定义 emits：必须定义 update:showDialog，用于通知父组件更新
const emit = defineEmits(['update:showDialog', 'close', 'task-submitted']) 

const form = ref({ taskName: '', description: '', selectedModelName: '', selectedDatasetName: '', type: '' }) 

const isVisible = computed({
    get() {
        return props.showDialog // 从父组件读取值
    },
    set(value) {
        emit('update:showDialog', value) // 向父组件发射事件请求更新
    }
})

/**
 * 获取模型列表
 */
const fetchModels = async () => {
    modelLoading.value = true;
    try {
        const response = await getAllModels();
        if (response.data?.code === 200 && Array.isArray(response.data.data)) {
          modelsList.value = response.data.data
        } else if (Array.isArray(response.data)) {
          modelsList.value = response.data
        }
    } catch (error) {
        ElMessage.error('获取模型列表失败');
        console.error('获取模型列表错误:', error);
    } finally {
        modelLoading.value = false;
    }
}

// 筛选后的模型列表 (计算属性)
const filteredModelsList = computed(() => {
    if (!modelSearchQuery.value) {
        return modelsList.value;
    }
    const query = modelSearchQuery.value.toLowerCase();
    return modelsList.value.filter(model => 
        model.name.toLowerCase().includes(query)
    );
})

/**
 * 获取数据集列表
 */
const fetchDatasets = async () => {
    datasetLoading.value = true;
    try {
        const response = await getAllDatasets();
        if (response.data?.code === 200 && Array.isArray(response.data.data)) {
          datasetsList.value = response.data.data
        } else if (Array.isArray(response.data)) {
          datasetsList.value = response.data
        }
    } catch (error) {
        ElMessage.error('获取数据集列表失败');
        console.error('获取数据集列表错误:', error);
    } finally {
        datasetLoading.value = false;
    }
}

// 筛选后的数据集列表 (计算属性)
const filteredDatasetsList = computed(() => {
    if (!datasetSearchQuery.value) {
        return datasetsList.value;
    }
    const query = datasetSearchQuery.value.toLowerCase();
    return datasetsList.value.filter(dataset => 
        dataset.name.toLowerCase().includes(query)
    );
})

/**
 * 统一处理关闭逻辑，通知父组件更新 showEvalDialog 为 false
 */
const handleClose = () => {
    isVisible.value=false
    // 提交后/关闭时重置表单
    form.value = { taskName: '', description: '', selectedModelName: '', selectedDatasetName: '', type: '' };
    emit('close') 
}

const submitEval = async() => {
    if (!form.value.taskName || !form.value.selectedDatasetName || !form.value.type) {
      ElMessage.warning('请选择数据集和评测方式')
      return
    }
    
    //查找数据集ID
    const selectedDataset = datasetsList.value.find(d => d.name === form.value.selectedDatasetName);
    if (!selectedDataset) {
      ElMessage.error('数据集信息缺失，请重新选择');
      return;
    }

    //查找模型ID
    const selectedModel = modelsList.value.find(m => m.name === form.value.selectedModelName);
    if (form.value.type !== 'adversarial' && !selectedModel) {
      ElMessage.error('模型信息缺失，请重新选择');
      return;
    }

    const selectedModel2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
    if (form.value.type === 'adversarial' && !selectedModel2) {
      ElMessage.error('模型二信息缺失，请重新选择');
      return;
    }

    // 模拟提交成功
    const requestBody = {
      "name": form.value.taskName,
      "description": form.value.description,
      "method": form.value.type,
      "dataset": selectedDataset.id,
      "myModel": selectedModel ? selectedModel.id : null,
      "myModel2": selectedModel2 ? selectedModel2.id : null,

    };
    if (form.value.type == 'adversarial' && !selectedModel2.id) {
        ElMessage.warning('请选择模型')
        return
    }
    
    try {
      const response = await createEvaluationTask(requestBody);

      if (response.status === 201) {
        const result = await response.data;
        
        ElMessage.success(`任务 [${result.name}] 创建成功!`);
        
        // *** 1. 尝试开始评测任务 ***
        try {
            await runEvaluationTask(result.id); // 使用返回的任务 ID
            ElMessage.success(`任务 [${result.name}] 已开始评测!`);
        } catch (runError) {
            console.error('开始评测任务失败:', runError);
            // 任务创建成功但运行失败，仍然给用户提示
            ElMessage.warning(`任务 [${result.name}] 创建成功，但自动开始失败。`);
        }
        
        // *** 2. 通知父组件并关闭弹窗 ***
        emit('task-submitted', result); 
        handleClose();
        
      } else {
        // 处理非 201 状态码，例如 400 Bad Request
        const errorData = await response.data;
        ElMessage.error(`任务创建失败: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      // 处理网络错误
      console.error('任务提交网络错误:', error);
      ElMessage.error('网络连接失败，请检查您的网络。');
    }
}

onMounted(() => {
    fetchModels();
    fetchDatasets();
});
</script>

<style scoped>
/* 无需额外样式，Element Plus 默认模态 + 拖动 */
</style>