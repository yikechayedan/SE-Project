<template>
  <el-dialog v-model="isVisible" title="创建评测任务" :draggable="true" width="500px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input v-model="form.taskName" placeholder="输入任务名称" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="输入任务描述" />
      </el-form-item>
      <el-form-item label="评测类型">
        <el-radio-group v-model="form.method">
          <el-radio 
            v-for="opt in methodOptions" 
            :key="opt.value"
            :label="opt.value"
            :disabled="isMethodDisabled(opt.value)"
            @click.prevent="handleRadioClick(opt.value)"
          >
            {{ opt.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="数据集" >
        <div style="display: flex; width: 100%;">
          
          <el-select 
            v-model="form.selectedDatasetName" 
            placeholder="选择数据集" 
            :loading="datasetLoading"
            style="flex: 1;"
            popper-class="dataset-select-popper" 
          >
            <el-option value="" label="清除选择" @click="handleClearDataset">
              <div class="option-item clear-item">
                <el-icon><CircleClose /></el-icon>
                <span>清除当前选择</span>
              </div>
            </el-option>
            
            <el-option
              v-for="dataset in filteredDatasetsList"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.name"
            >
              <div class="option-item" :title="dataset.name">
                <span class="dataset-name-text">{{ dataset.name }}</span>
                <el-tag 
                  :type="getCategoryTag(dataset.category)" 
                  size="small" 
                  effect="plain"
                  class="type-tag"
                >
                  {{ formatCategoryName(dataset.category) }}
                </el-tag>
                <el-tag 
                  :type="getMethodTag(dataset.evaluation_type)" 
                  size="small" 
                  effect="plain"
                  class="type-tag"
                >
                  {{ formatMethodName(dataset.evaluation_type) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>

          <el-input 
            v-model="datasetSearchQuery" 
            placeholder="搜索数据集" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
          />
        </div>
      </el-form-item>
      <el-form-item label="模型选择">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedModelName" 
              placeholder="选择模型" 
              :loading="modelLoading"
              style="flex: 1;"
              popper-class="dataset-select-popper" 
          > 
              <el-option value="" label="清除选择" @click="handleClearModel1">
                <div class="option-item clear-item">
                  <el-icon><CircleClose /></el-icon>
                  <span>清除当前选择</span>
                </div>
              </el-option>
              
              <el-option
                v-for="model in filteredModelsList"
                :key="model.id"
                :label="model.name"
                :value="model.name"
              >
                <div class="option-item" :title="model.name">
                  <span class="dataset-name-text">{{ model.name }}</span>
                  <el-tag 
                    :type="getCategoryTag(model.category)" 
                    size="small" 
                    effect="plain"
                    class="type-tag"
                  >
                    {{ formatModelCategoryName(model.category) }}
                  </el-tag>
                </div>
              </el-option>

          </el-select>

          <el-input 
            v-model="modelSearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="模型二选择" v-if="form.method === 'adversarial'">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedModelName2" 
              placeholder="选择模型二" 
              :loading="modelLoading"
              style="flex: 1;"
              popper-class="dataset-select-popper"
          >
            <el-option value="" label="清除选择" @click="handleClearModel2">
                <div class="option-item clear-item">
                  <el-icon><CircleClose /></el-icon>
                  <span>清除当前选择</span>
                </div>
              </el-option>

            <el-option
              v-for="model in filteredModel2sList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            >
              <div class="option-item" :title="model.name">
                  <span class="dataset-name-text">{{ model.name }}</span>
                  <el-tag 
                    :type="getCategoryTag(model.category)" 
                    size="small" 
                    effect="plain"
                    class="type-tag"
                  >
                    {{ formatModelCategoryName(model.category) }}
                  </el-tag>
                </div>
            </el-option>


          </el-select>

          <el-input 
            v-model="modelSearchQuery2" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="评测方式" v-if="form.method === 'adversarial' || form.method === 'subjective'">
        <el-radio-group v-model="form.type">
          <el-radio label="human">人工评测</el-radio>
          <el-radio label="model">模型评测</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="选择裁判模型" v-if="(form.method === 'adversarial' || form.method === 'subjective') && form.type === 'model'">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.judgeModelName" 
                     placeholder="选择裁判模型" 
                     :loading="modelLoading"
                     style="flex: 1;"
                     popper-class="dataset-select-popper"
          > 
            <el-option
              v-for="model in filteredJudgeModelsList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            >
              <div class="option-item" :title="model.name">
                <span class="dataset-name-text">{{ model.name }}</span>
                <el-tag 
                  :type="getCategoryTag(model.category)" 
                  size="small" 
                  effect="plain"
                  class="type-tag"
                >
                  {{ formatModelCategoryName(model.category) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>

          <el-input 
            v-model="judgeModelSearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      
      
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="submitEval">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, onMounted, watch} from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, CircleClose } from '@element-plus/icons-vue'
import { createEvaluationTask } from '@/api/tasks.js'
import { getAllDatasets } from '@/api/datasets.js'
import { getAllModels } from '@/api/models.js' 
import { getUserInfo } from '@/api/users.js'

// 存储从 API 获取的模型和数据集列表
const modelsList = ref([])
const datasetsList = ref([])

// 加载状态
const modelLoading = ref(false)
const datasetLoading = ref(false)
const modelSearchQuery = ref('')
const modelSearchQuery2 = ref('')
const judgeModelSearchQuery = ref('')
const datasetSearchQuery = ref('') 
const router = useRouter()
const currentUserId = ref(null)

const fetchUserID = async () => {
    try {
        const response = await getUserInfo();
        const data = response.data.data;
        currentUserId.value = data.id;
    } catch (error) {
        console.error('获取用户信息失败:', error);
    }
}

// 1. 接收 props：接收父组件 v-model:showDialog 传入的属性
const props = defineProps({
    showDialog: {
      type: Boolean,
      default: false
    }
})

// 2. 定义 emits：必须定义 update:showDialog，用于通知父组件更新
const emit = defineEmits(['update:showDialog', 'close', 'task-submitted']) 

const form = ref({
    taskName: '',
    description: '', 
    selectedModelName: '',
    selectedModelName2: '', 
    selectedDatasetName: '', 
    method: '', 
    type: '', 
    judgeModelName: '' }) 

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
    let list = modelsList.value;
    const selectedDataset = datasetsList.value.find(d => d.name === form.value.selectedDatasetName);
    
    // [Rule] 对抗评测中，如果模型二选了生图模型，模型一也必须是生图模型
    if (form.value.method === "adversarial" && form.value.selectedModelName2) {
        const m2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
        if (m2 && m2.category === 'image') {
            list = list.filter(m => m.category === 'image');
        }
    }

    if (selectedDataset) {
        // 根据数据集的评测类型过滤模型
        list = list.filter(model => {
           return (selectedDataset.category === "image" || selectedDataset.category === "multimodal" || selectedDataset.category === "multimodel") ?
                model.category === "multimodal" :
                true ;
        });
    }
    if (!modelSearchQuery.value) {
        return list;
    }
    const query = modelSearchQuery.value.toLowerCase();
    return list.filter(model => 
        model.name.toLowerCase().includes(query)
    );
})

const filteredModel2sList = computed(() => {
    let list = modelsList.value;
    
    // [Rule] 对抗评测中，如果模型一选了生图模型，模型二也必须是生图模型
    if (form.value.method === "adversarial" && form.value.selectedModelName) {
        const m1 = modelsList.value.find(m => m.name === form.value.selectedModelName);
        if (m1 && m1.category === 'image') {
            list = list.filter(m => m.category === 'image');
        }
    }

    const selectedDataset = datasetsList.value.find(d => d.name === form.value.selectedDatasetName);
    if (selectedDataset) {
        // 根据数据集的评测类型过滤模型
        list = list.filter(model => {
           return (selectedDataset.category === "image" || selectedDataset.category === "multimodal" || selectedDataset.category === "multimodel") ?
                model.category === "multimodal" :
                true ;
        });
    }

    if (!modelSearchQuery2.value) {
        return list;
    }
    const query = modelSearchQuery2.value.toLowerCase();
    return list.filter(model => 
        model.name.toLowerCase().includes(query)
    );
})

const filteredJudgeModelsList = computed(() => {
    let list = modelsList.value;

    const m1 = modelsList.value.find(m => m.name === form.value.selectedModelName);
    const m2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
    const isT2I = (m1 && m1.category === "image") || (m2 && m2.category === "image");

    // [Rule] 如果涉及生图模型评测，裁判必须是多模态识别模型
    if (isT2I) {
        list = list.filter(m => m.category === "multimodal");
    }

    if (!judgeModelSearchQuery.value) {
        return list;
    }
    const query = judgeModelSearchQuery.value.toLowerCase();
    return list.filter(model => 
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
    let list = datasetsList.value;
    const selectedModel = modelsList.value.find(m => m.name === form.value.selectedModelName);
    const selectedModel2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
    
    // [New] 如果选了生图模型，强制只能选文本数据集 (Prompt)
    const isImageModel = (selectedModel && selectedModel.category === 'image') || 
                         (selectedModel2 && selectedModel2.category === 'image');
    
    if (isImageModel) {
        list = list.filter(d => d.category === 'text');
    } else if(selectedModel || selectedModel2){
      list = list.filter(dataset => {
          const isModelText = (selectedModel && selectedModel.category === "text");
          const isModel2Text = (selectedModel2 && selectedModel2.category === "text");
          if(isModelText || isModel2Text){
              return dataset.category === "text";
          }
          return true;
      })
    }

    if (form.value.method) {
        list = list.filter(dataset => {
          return dataset.evaluation_type === form.value.method;
        });
    }

    if (!datasetSearchQuery.value) {
        return list;
    }
    const query = datasetSearchQuery.value.toLowerCase();
    return list.filter(dataset => 
        dataset.name.toLowerCase().includes(query)
    );
})

// 监听数据集选择的变化
watch(() => form.value.selectedDatasetName, (newDatasetName) => {
    if (!newDatasetName) return;

    // 找到当前选中的数据集对象
    const selectedDataset = datasetsList.value.find(d => d.name === newDatasetName);
    
    if (selectedDataset && selectedDataset.evaluation_type) {
        // 如果当前选中的类型和数据集类型不符，或者还没选类型，则自动切换类型
        if (form.value.method !== selectedDataset.evaluation_type) {
            form.value.method = selectedDataset.evaluation_type;
        }
    }
});

// 清除数据集的选择
const handleClearDataset = () => {
  form.value.selectedDatasetName = '';
};

// [New] 监听模型选择，处理生图模型的自动冲突解决
watch([() => form.value.selectedModelName, () => form.value.selectedModelName2], ([m1, m2]) => {
    const model1 = modelsList.value.find(m => m.name === m1);
    const model2 = modelsList.value.find(m => m.name === m2);
    const isImageModel = (model1 && model1.category === 'image') || (model2 && model2.category === 'image');

    if (isImageModel) {
        // 1. 如果当前是客观评测，自动清空（因为生图模型不支持）
        if (form.value.method === 'objective') {
            form.value.method = '';
        }
        // 2. 如果当前选中的数据集不是文本类型，自动清空
        const selectedDataset = datasetsList.value.find(d => d.name === form.value.selectedDatasetName);
        if (selectedDataset && selectedDataset.category !== 'text') {
            form.value.selectedDatasetName = '';
        }
    }
});

const handleClearModel1 = () => {
  form.value.selectedModelName = '';
};

const handleClearModel2 = () => {
  form.value.selectedModelName2 = '';
};

const methodOptions = [
  { label: '客观评测', value: 'objective' },
  { label: '主观评测', value: 'subjective' },
  { label: '对抗评测', value: 'adversarial' }
]

// 处理单选框点击：实现再次点击取消
const handleRadioClick = (val) => {
  // 如果该项已被禁用（受数据集锁定），则不响应点击
  if (isMethodDisabled(val)) return;

  if (form.value.method === val) {
    form.value.method = ''; // 再次点击已选中的，设为空
  } else {
    form.value.method = val; // 点击未选中的，正常赋值
  }
}

// 判定评测类型是否应该被禁用
const isMethodDisabled = (methodType) => {
    // 1. 根据数据集锁定
    if (form.value.selectedDatasetName) {
        const selectedDataset = datasetsList.value.find(d => d.name === form.value.selectedDatasetName);
        if (selectedDataset && selectedDataset.evaluation_type) {
            if (selectedDataset.evaluation_type !== methodType) return true;
        }
    }

    // 2. 根据模型锁定 (新逻辑：生图模型不支持客观评测)
    const selectedModel = modelsList.value.find(m => m.name === form.value.selectedModelName);
    const selectedModel2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
    const isImageModel = (selectedModel && selectedModel.category === 'image') || 
                         (selectedModel2 && selectedModel2.category === 'image');
    
    if (isImageModel && methodType === 'objective') {
        return true;
    }

    return false;
};

// 获取标签颜色类型
const getMethodTag = (method) => {
  const map = {
    objective: 'success',
    subjective: 'warning',
    adversarial: 'danger',
  };
  return map[method] || 'info';
};

// 格式化名称显示
const formatMethodName = (method) => {
  const map = {
    objective: '客观',
    subjective: '主观',
    adversarial: '对抗',
  };
  return map[method] || method;
};

const getCategoryTag = (category) => {
  const map = {
    text: 'primary',
    image: 'success',
    multimodel: 'warning',
    multimodal: 'warning',
  };
  return map[category] || 'info';
};

const formatCategoryName = (category) => {
  const map = {
    text: '文本',
    image: '图像',
    multimodel: '多模态',
    multimodal: '多模态',
  };
  return map[category] || category;
};

const formatModelCategoryName = (category) => {
  const map = {
    text: '文本',
    image: '生成图像',
    multimodel: '多模态识别',
    multimodal: '多模态识别',
  };
  return map[category] || category;
};

/**
 * 统一处理关闭逻辑，通知父组件更新 showEvalDialog 为 false
 */
const handleClose = () => {
    isVisible.value=false
    // 提交后/关闭时重置表单
    form.value = { 
      taskName: '', 
      description: '', 
      selectedModelName: '', 
      selectedModelName2: '',
      selectedDatasetName: '', 
      method: 'objective',
      type: 'model',
      judgeModelName: ''
    };
    emit('close') 
}

const submitEval = async() => {
    if (!form.value.taskName || !form.value.selectedDatasetName || !form.value.method) {
      ElMessage.warning('请填写任务名称、选择数据集和评测方式')
      return
    }

    if ((form.value.method === 'subjective' || form.value.method === 'adversarial') && !form.value.type) {
      ElMessage.warning('请选择评测方式（人工或模型）')
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
    if (!selectedModel) {
      ElMessage.error('请选择评测模型');
      return;
    }

    let selectedModel2 = null;
    if (form.value.method === 'adversarial') {
      selectedModel2 = modelsList.value.find(m => m.name === form.value.selectedModelName2);
      if (!selectedModel2) {
        ElMessage.error('请选择模型二');
        return;
      }
      // [Fix] 对抗评测禁止选择相同模型
      if (selectedModel && selectedModel2 && selectedModel.id === selectedModel2.id) {
        ElMessage.warning('对抗评测中，模型一和模型二不能相同');
        return;
      }
    }

    let selectedJudgeModel = null;
    if ((form.value.method === 'adversarial' || form.value.method === 'subjective') && form.value.type === 'model') {
      selectedJudgeModel = modelsList.value.find(m => m.name === form.value.judgeModelName);
      if (!selectedJudgeModel) {
        ElMessage.error('请选择裁判模型');
        return;
      }
      
      // [Rule Check] 裁判模型不能是生图模型
      if (selectedJudgeModel.category === 'image') {
        ElMessage.error('裁判模型不能是生图模型');
        return;
      }

      // [Rule Check] 生图模型必须配多模态裁判
      const isT2I = selectedModel.category === "image" || (selectedModel2 && selectedModel2.category === "image");
      if (isT2I && selectedJudgeModel.category !== "multimodal") {
        ElMessage.error('生图评测必须选择多模态识别模型作为裁判');
        return;
      }
    }

    const requestBody = {
      "name": form.value.taskName,
      "description": form.value.description,
      "method": form.value.method,
      "dataset": selectedDataset.id,
      "myModel": selectedModel.id,
      "myModel_2": selectedModel2 ? selectedModel2.id : null,
      "judge_model": selectedJudgeModel ? selectedJudgeModel.id : null
    };

    // 只有非客观评测才需要 judge_type 字段
    if (form.value.method !== 'objective') {
      requestBody.judge_type = form.value.type === "model" ? "model" : "human";
    }
    
    try {
      const response = await createEvaluationTask(requestBody);

      if (response.status === 201) {
        const result = response.data.data || response.data;
        
        ElMessage.success(`任务 [${form.value.taskName}] 创建成功!`);
        
        emit('task-submitted', result); 
        handleClose();
        
      } else if (response.status === 200 && response.data.is_duplicate) {
        // --- 处理重复任务 ---
        const existingTaskId = response.data.task_id;
        ElMessage.info(response.data.msg || "检测到近期已有相同任务，正在为您跳转到报告...");
        
        // 【关键修复】必须在 handleClose 之前获取 method，否则 handleClose 会重置表单为 objective
        const method = form.value.method;
        
        handleClose();
        
        // 根据评测类型跳转到不同的结果页
        if (method === 'objective') {
          router.push({ name: 'EvalReport', params: { taskId: existingTaskId } });
        } else if (method === 'subjective') {
          router.push({ name: 'SubjectResult', params: { taskId: existingTaskId } });
        } else if (method === 'adversarial') {
          if (form.value.type === 'model') {
             router.push({ name: 'AdversarialResult', params: { taskId: existingTaskId } });
          } else {
             router.push({ 
              name: 'AdversarialEval', 
              params: { 
                taskId: existingTaskId,
                reviewerId: currentUserId.value,
                modelId: selectedModel.id,
                model2Id: selectedModel2.id,
                datasetId: selectedDataset.id
              } 
            });
          }
        }
        
      } else {
        const errorData = response.data;
        ElMessage.error(`任务创建失败: ${errorData.detail || errorData.msg || response.statusText}`);
      }
    } catch (error) {
      console.error('任务提交网络错误:', error);
      const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '网络连接失败，请检查您的网络。';
      ElMessage.error(errorMsg);
    }
}

onMounted(() => {
    fetchModels();
    fetchDatasets();
    fetchUserID();
});
</script>

<style scoped>
/* 下拉项容器 */
.option-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px; /* 间距固定 */
}

/* 数据集名称样式：自动截断 */
.dataset-name-text {
  flex: 1; /* 占据剩余空间 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

/* 标签样式：固定宽度不收缩 */
.type-tag {
  flex-shrink: 0; /* 防止名称长时标签被挤压 */
  min-width: 42px;
  text-align: center;
}

/* 清空选项样式 */
.clear-item {
  color: var(--el-color-info);
  font-weight: 500;
  justify-content: flex-start;
  gap: 8px;
}

/* 深度调整 Element 原生样式 */
:deep(.el-select-dropdown__item) {
  padding: 0 12px;
  height: 38px;
  line-height: 38px;
}

/* 提高鼠标悬停时的区分度 */
:deep(.el-select-dropdown__item.hover) {
  background-color: var(--bg-hover);
}

/* Dialog Theme Overrides */
:deep(.el-dialog) {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
  font-weight: 600;
}

:deep(.el-dialog__body) {
  color: var(--text-primary);
  padding: 20px 24px 24px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-secondary);
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: var(--accent-color);
}

/* Form Item Label */
:deep(.el-form-item__label) {
  color: var(--text-primary);
}

/* Input Fields */
:deep(.el-input__wrapper) {
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}

/* Radio Buttons */
:deep(.el-radio__label) {
  color: var(--text-primary);
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: var(--accent-color);
}
</style>