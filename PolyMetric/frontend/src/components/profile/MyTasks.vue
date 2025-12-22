<template>
  <div class="my-tasks-container">
    <div class="action-bar">
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索我的评测任务" 
        prefix-icon="Search" 
        style="width: 300px; margin-right: 20px;"
      />
      
      <el-button type="primary" round @click="showEvalDialog = true">新建任务</el-button>
    </div>
    
    <el-table 
      :data="filteredTasks" 
      border 
      style="width: 100%;" 
      v-loading="isTableLoading"
    >
      <el-table-column prop="name" label="任务名称" show-overflow-tooltip />
      
      <el-table-column prop="model" label="模型" show-overflow-tooltip>
        <template #default="{ row }">
              <div class="model-name overflow-container">
                <el-icon><Box /></el-icon>
                <span>{{ row.myModel_name }}</span>
              </div>
            </template>
      </el-table-column>
      <el-table-column prop="dataset" label="使用数据集" show-overflow-tooltip>
        <template #default="{ row }">
              <div class="dataset-name overflow-container">
                <el-icon><Folder /></el-icon>
                <span>{{ row.dataset_name }}</span>
              </div>
            </template>
      </el-table-column>
      
      <el-table-column prop="method" label="评测类型" width="100">
        <template #default="scope">
          <el-tag :type="getMethodTag(scope.row.method)" size="small">
            {{ formatMethod(scope.row.method) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="judge_type" label="评测方式" width="100">
        <template #default="scope">
          <el-tag :type="getTypeTag(scope.row.judge_type)" size="small">
            {{ formatType(scope.row.judge_type) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusTag(scope.row.status)" size="small">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="time" label="更新时间" width="120" />
      
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="scope">
          <el-button 
            v-if="scope.row.status === 'completed'"
            size="small" 
            type="primary" 
            round 
            @click="handleViewReport(scope.row)"
          >
            <el-icon><View /></el-icon>查看详情
          </el-button>

          <el-button 
            v-if="scope.row.status === 'pending'"
            size="small" 
            type="primary" 
            round 
            @click="handleRunEvaluation(scope.row)"
          >
            <el-icon><VideoPlay /></el-icon>生成回答
          </el-button>

          <el-button 
            v-if="scope.row.status === 'awaiting_human_judge'"
            size="small" 
            type="primary" 
            round 
            @click="handleStartEvaluation(scope.row)"
          >
            <el-icon><Stopwatch /></el-icon>人工评测
          </el-button>
          
          <el-button 
            size="small" 
            type="danger" 
            round
            @click="handleDeleteTask(scope.row)"
          >
            <el-icon><Delete /></el-icon>删除
          </el-button>

          <el-button 
            size="small" 
            type="info" 
            round
            @click="handleEditTask(scope.row)"
          >
            <el-icon><Edit /></el-icon>编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination-container"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[5, 10, 20, 50]"
      :total="totalCount"  :background="true"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>

  <el-dialog
    title="编辑评测任务"
    v-model="showEditDialog"
    width="600px">
        <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input v-model="form.taskName" placeholder="输入任务名称" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="输入任务描述" />
      </el-form-item>
      <el-form-item label="评测类型" v-if="form.status === 'pending'">
        <el-radio-group v-model="form.method" >
          <el-radio 
            label="objective" 
            :disabled="isMethodDisabled('objective')"
            @click.prevent="handleRadioClick('objective')"
          >客观评测</el-radio>
          <el-radio 
            label="subjective" 
            :disabled="isMethodDisabled('subjective')"
            @click.prevent="handleRadioClick('subjective')"
          >主观评测</el-radio>
          <el-radio 
            label="adversarial" 
            :disabled="isMethodDisabled('adversarial')"
            @click.prevent="handleRadioClick('adversarial')"
          >对抗评测</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="模型选择" v-if="form.status === 'pending'">
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
      <el-form-item label="模型二选择" v-if="form.method === 'adversarial' && form.status === 'pending'">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.selectedModelName2" 
                     placeholder="选择模型二" 
                     :loading="modelLoading"
                     style="flex: 1;"> <el-option
              v-for="model in filteredModel2sList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            />
          </el-select>

          <el-input 
            v-model="model2SearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="评测方式" v-if="(form.method === 'adversarial' || form.method === 'subjective') && form.status === 'pending'">
        <el-radio-group v-model="form.type">
          <el-radio label="human">人工评测</el-radio>
          <el-radio label="model">模型评测</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="选择裁判模型" v-if="(form.method === 'adversarial' || form.method === 'subjective') && form.type === 'model' && form.status === 'pending'">
        <div style="display: flex; width: 100%;">
          
          <el-select v-model="form.judgeModelName" 
                     placeholder="选择裁判模型" 
                     :loading="modelLoading"
                     style="flex: 1;"> <el-option
              v-for="model in filteredJudgeModelsList"
              :key="model.id"
              :label="model.name"
              :value="model.name"
            />
          </el-select>

          <el-input 
            v-model="judgeModelSearchQuery" 
            placeholder="搜索模型" 
            prefix-icon="Search" 
            style="width: 150px; margin-left: 10px;"
            />
        </div>
      </el-form-item>
      <el-form-item label="数据集" v-if="form.status === 'pending'">
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
      
    </el-form>
    <template #footer>
      <el-button @click="showEditDialog=false">取消</el-button>
      <el-button type="primary" @click="saveEditTask()">保存</el-button>
    </template>
  </el-dialog>

  <EvalDialog v-model:showDialog="showEvalDialog"
    @close="showEvalDialog = false"
    @task-submitted="handleSubmit()" />

</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { View, Edit, Delete, VideoPlay, Stopwatch } from '@element-plus/icons-vue';
import EvalDialog from '../common/EvalDialog.vue';
import { getEvaluationTasks, deleteEvaluationTask, updateEvaluationTask } from '@/api/tasks.js';
import { getAllDatasets } from '@/api/datasets.js';
import { getAllModels } from '@/api/models.js';
import { getUserInfo} from '@/api/users.js'

const router = useRouter();

// ------------------------------------
// 状态与数据
// ------------------------------------
const isTableLoading = ref(true);
const pollTimer = ref(null);
const currentUserId = ref(null);
const myTasks = ref([]); // 存放我的任务数据
const modelsList = ref([]);
const datasetsList = ref([]);
const searchQuery = ref(''); // 搜索框输入
const modelLoading = ref(false);
const datasetLoading = ref(false);
const modelSearchQuery = ref('');
const model2SearchQuery = ref('');
const judgeModelSearchQuery = ref('');
const datasetSearchQuery = ref('');
const showEvalDialog = ref(false);
const showEditDialog = ref(false);
const currentPage = ref(1);
const pageSize = ref(5);

// 编辑表单
const form = reactive({
  id: null,
  name: '',
  description: '',
  type: '',
  status: '',
  selectedModelName: '',
  selectedModelName2: '',
  selectedDatasetName: '',
  judgeModelName: '',
})

const fetchUserID = async () => {
    try {
        const response = await getUserInfo();
        const data = response.data.data;
        currentUserId.value = data.id;
    } catch (error) {
        console.error('获取用户信息失败:', error);
        ElMessage.error(`获取用户信息失败: ${error.message}`);
    }
}

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

const filteredModel2sList = computed(() => {
    if (!model2SearchQuery.value) {
        return modelsList.value;
    }
    const query = model2SearchQuery.value.toLowerCase();
    return modelsList.value.filter(model => 
        model.name.toLowerCase().includes(query)
    );
})

const filteredJudgeModelsList = computed(() => {
    if (!judgeModelSearchQuery.value) {
        return modelsList.value;
    }
    const query = judgeModelSearchQuery.value.toLowerCase();
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
    let list = datasetsList.value;

    // 如果已经选择了评测类型，则只展示该类型的数据集
    if (form.method) {
        list = list.filter(dataset => dataset.evaluation_type === form.method);
    }

    if (!datasetSearchQuery.value) {
        return list;
    }
    const query = datasetSearchQuery.value.toLowerCase();
    return list.filter(dataset => 
        dataset.name.toLowerCase().includes(query)
    );
})

watch(() => form.selectedDatasetName, (newDatasetName) => {
    if (!newDatasetName) return;
    const selectedDataset = datasetsList.value.find(d => d.name === newDatasetName);
    if (selectedDataset && selectedDataset.evaluation_type) {
        if (form.method !== selectedDataset.evaluation_type) {
            form.method = selectedDataset.evaluation_type;
        }
    }
});
// ------------------------------------
// 数据加载
// ------------------------------------
const fetchTasks = async (isSilent = false) => {
    if (!isSilent) isTableLoading.value = true;
    try {
        const response = await getEvaluationTasks();
        const data = response.data;
        //  格式化所有任务并赋值给 evaluations
        const formattedTasks = data.map(formatTaskDisplay);
        myTasks.value = formattedTasks.filter(task => task.creator === currentUserId.value);

        checkPollingNecessity();
        
    } catch (error) {
        console.error('加载评测任务失败:', error);
        if (!isSilent) ElMessage.error(`加载评测任务失败: ${error.message}`);
    } finally {
        if (!isSilent) isTableLoading.value = false;
    }
}

// ------------------------------------
// 计算属性
// ------------------------------------
const isMethodDisabled = (methodType) => {
    if (!form.selectedDatasetName) return false;
    
    const selectedDataset = datasetsList.value.find(d => d.name === form.selectedDatasetName);
    if (selectedDataset && selectedDataset.evaluation_type) {
        return selectedDataset.evaluation_type !== methodType;
    }
    return false;
};

// 过滤任务列表
const filteredTasks = computed(() => {
  const query = searchQuery.value.toLowerCase();
  
  // 1. 先进行关键词过滤
  const searchResult = myTasks.value.filter(task => 
    (task.name || '').toLowerCase().includes(query) ||
    (task.myModel_name || '').toLowerCase().includes(query) ||
    (task.dataset_name || '').toLowerCase().includes(query)
  );

  // 2. 再对过滤后的结果进行分页切片
  const start = (currentPage.value - 1) * pageSize.value;
  const end = currentPage.value * pageSize.value;
  
  return searchResult.slice(start, end);
});

// 获取当前过滤条件下的总条数
const totalCount = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) return myTasks.value.length;
  return myTasks.value.filter(task => 
    (task.name || '').toLowerCase().includes(query) ||
    (task.myModel_name || '').toLowerCase().includes(query) ||
    (task.dataset_name || '').toLowerCase().includes(query)
  ).length;
});

watch(searchQuery, () => {
  currentPage.value = 1;
});

// ------------------------------------
// 格式化函数 (参照 EvaluationHall.vue)
// ------------------------------------

const formatTaskDisplay = (task) => {
   
    return {
        //保持api原有的id
        ...task,
        initiator: task.creator_username,
        taskName: task.name,
        model: task.myModel_name,
        dataset: task.dataset_name,
        time: task.created_at ? new Date(task.created_at).toLocaleDateString() : 'N/A',
    };
};

const formatMethod = (method) => {
  const map = {
    objective: '客观评测',
    subjective: '主观评测',
    adversarial: '对抗评测',
  };
  return map[method] || method;
};

const getMethodTag = (method) => {
  const map = {
    objective: 'success',
    subjective: 'warning',
    adversarial: 'danger',
  };
  return map[method] || '';
};

const formatType = (type) => {
  const map = {
    human: '人工评测',
    model: '模型评测',
  };
  return map[type] || type;
};

const getTypeTag = (type) => {
  const map = {
    human: 'warning',
    model: 'success',
  };
  return map[type] || '';
};

const formatStatus = (status) => {
  const map = {
    pending: '待启动',
    running: '进行中',
    awaiting_human_judge: '待测评',
    completed: '已完成',
    failed: '失败',
  };
  return map[status] || status;
};

const getStatusTag = (status) => {
  const map = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    awaiting_human_judge: 'info',
  };
  return map[status] || '';
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


// ------------------------------------
// 动作处理函数
// ------------------------------------

// 处理每页条数变化
// 1. 处理单选框点击：实现再次点击取消，并拦截被禁用的选项
const handleRadioClick = (val) => {
  if (isMethodDisabled(val)) return;
  
  if (form.method === val) {
    form.method = ''; // 再次点击取消选择
  } else {
    form.method = val;
  }
}

const handleClearDataset = () => {
  form.selectedDatasetName = '';
};

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 切换每页条数时回到第一页
}

// 处理页码变化
const handlePageChange = (val) => {
  currentPage.value = val
}

// 新建任务处理，应该打开弹窗
const handleSubmit = () => {
    fetchTasks(); 
};

// 查看报告/详情
const handleViewReport = (task) => {
  if(task.method === 'objective'){
    router.push({ 
      name: 'EvalReport', 
      params: { taskId: task.id } 
    });
  }
  else if(task.method === 'subjective'){
    router.push({
      name: 'SubjectResult',
      params: { taskId: task.id }
    })
  }
  else if(task.method === 'adversarial'){
      router.push({
        name: 'AdversarialResult',
        params: { taskId: task.id}
      })
  }
};

const handleRunEvaluation = async (task) => {
   try {
        await ElMessageBox.confirm(
            `确认启动任务吗？ 启动后将不能改变评测所用的类型、模型和数据集`,
            '警告',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );
        runEvaluationTask(task.id).then(() => {
            console.log('任务实际在后端启动成功');
        }).catch(err => {
            ElMessage.error('任务启动失败: ' + err.message);
            fetchTasks(true); // 失败了也刷新下状态
        });

        ElMessage.success('正在尝试启动任务...');
        
        startPolling(); 
        
    } catch (error) {
        console.error('逻辑错误:', error);
    }
}

const handleStartEvaluation = (task) => {
  if(task.method === 'subjective') {
    router.push({
      name: 'SubjectiveEval',
      params: { taskId: task.id , reviewerId: currentUserId.value , modelId: task.myModel , datasetId: task.dataset}
    })
  } else if(task.method === 'adversarial'){
    router.push({
      name: 'AdversarialEval',
      params: { taskId: task.id , reviewerId: currentUserId.value, modelId: task.myModel, model2Id: task.myModel_2, datasetId: task.dataset}
    })
  }
}

//编辑任务
const handleEditTask = (task) => {
  showEditDialog.value = true;
  form.id = task.id;
  form.taskName = task.taskName;  
  form.description = task.description;
  form.method = task.method;
  form.status = task.status;
  form.type = task.judge_type
  form.selectedModelName = task.myModel_name;
  form.selectedModelName2 = task.myModel_2_name;
  form.selectedDatasetName = task.dataset_name;
  form.judgeModelName = modelsList.value.find(m => m.id === task.judge_model)?.name;
};

const saveEditTask = async () => {
    try{
        const requestBody = {
            name: form.taskName,
            description: form.description,
            method: form.method,
            judge_type: form.type === "model" ? "model" : "human",
            dataset: datasetsList.value.find(d => d.name === form.selectedDatasetName)?.id || null,
            myModel: modelsList.value.find(d => d.name === form.selectedModelName)?.id || null,
            myModel_2: (form.method === 'adversarial')? modelsList.value.find(d => d.name === form.selectedModelName2)?.id || null : null,
            judge_model: (form.type === 'model')? modelsList.value.find(d => d.name === form.judgeModelName)?.id || null : null
        };
        await updateEvaluationTask(form.id, requestBody);
        ElMessage.success('任务更新成功');
        showEditDialog.value = false;
        fetchTasks();
    } catch(error) {
        console.error('更新任务失败:', error);
        ElMessage.error(`更新任务失败: ${error.message}`);
    }
};

// 删除任务
const handleDeleteTask = async (task) => {
    try{
        await ElMessageBox.confirm(
            `确认删除任务 "${task.name}" 吗？删除后数据不可恢复。`,
            '警告',
            {
                confirmButtonText: '确定删除',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );
        await deleteEvaluationTask(task.id);
        ElMessage.success('任务删除成功');
        fetchTasks(); 
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除任务失败:', error);
            ElMessage.error(`删除任务失败: ${error.message}`);
        } else {
             // 用户点击取消，不做任何操作
             ElMessage.info('已取消删除操作');
        }
    }
};

const checkPollingNecessity = () => {
    const hasActiveTask = myTasks.value.some(
        task => task.status === 'running' || task.status === 'pending'
    );

    if (hasActiveTask) {
        startPolling();
    } else {
        stopPolling();
    }
}

const startPolling = () => {
    if (pollTimer.value) return; // 避免重复启动
    console.log('检测到正在运行的任务，开启轮询...');
    pollTimer.value = setInterval(() => {
        fetchTasks(true); // 传入 true，实现无感知静默更新
    }, 5000); // 每 5 秒轮询一次
}

const stopPolling = () => {
    if (pollTimer.value) {
        clearInterval(pollTimer.value);
        pollTimer.value = null;
        console.log('所有任务已完成或停止，关闭轮询');
    }
}

onMounted(() => {
    fetchTasks(false);
    fetchDatasets();
    fetchModels();
    fetchUserID();
});

onUnmounted(() => {
    stopPolling();
})
</script>

<style scoped>
/* 下拉项容器 */
:deep(.option-item) {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 这一行负责把文字和标签推向两端 */
  width: 100%;
  gap: 12px; /* 这一行确保即使文字很短，也会有最小间距 */
}

/* 确保数据集名称占据剩余空间 */
:deep(.dataset-name-text) {
  flex: 1; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

/* 确保标签不被压缩且有固定边距 */
:deep(.type-tag) {
  flex-shrink: 0;
  min-width: 42px;
  text-align: center;
  margin-left: 8px; /* 额外增加一个左边距保险 */
}

/* 清空选项样式 */
:deep(.clear-item) {
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

.my-tasks-container {
  padding: 20px;
  background: transparent;
}
.action-bar { 
  display: flex;
  align-items: center;
  margin-bottom: 20px; 
}
.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.overflow-container {
  display: flex;
  align-items: center;
  gap: 8px; 
  overflow: hidden; 
}

.ellipsis-content {
  white-space: nowrap; 
  overflow: hidden;    
  text-overflow: ellipsis; 
  flex: 1; 
  display: block; 
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px; 
  margin-bottom: 20px;
  padding: 10px 0;
}


/* Table Dark Theme Overrides */
:deep(.el-table) {
  --el-table-bg-color: #161b22;
  --el-table-tr-bg-color: #161b22;
  --el-table-header-bg-color: #0d1117;
  --el-table-border-color: #30363d;
  --el-table-text-color: #c9d1d9;
  --el-table-header-text-color: #8b949e;
  --el-table-row-hover-bg-color: #1f2428;
}

:deep(.el-table__inner-wrapper::before) {
  background-color: #30363d;
}

:deep(.el-table th) {
  background-color: #0d1117 !important;
  color: #8b949e !important;
  border-bottom: 1px solid #30363d !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid #30363d !important;
}

/* Pagination if present */
:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #1f6bff;
  color: #ffffff;
}
:deep(.el-pagination.is-background .el-pager li) {
  background-color: #161b22;
  color: #8b949e;
  border: 1px solid #30363d;
}

/* Dialog & Form Overrides */
:deep(.el-dialog) {
  background: #161b22;
  border: 1px solid #30363d;
}
:deep(.el-dialog__title) {
  color: #c9d1d9;
}
:deep(.el-form-item__label) {
  color: #8b949e;
}
:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select__wrapper) {
  background-color: #0d1117;
  box-shadow: 0 0 0 1px #30363d inset;
  color: #c9d1d9;
}
:deep(.el-input__inner) {
  color: #c9d1d9;
}
</style>