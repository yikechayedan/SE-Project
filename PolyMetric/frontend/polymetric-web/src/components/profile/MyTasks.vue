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
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="任务名称" show-overflow-tooltip />
      
      <el-table-column prop="model" label="模型" width="140" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.method === 'adversarial' ? '' : scope.row.model }}
        </template>
      </el-table-column>
      <el-table-column prop="dataset" label="使用数据集" width="120" show-overflow-tooltip />
      
      <el-table-column prop="method" label="评测方法" width="100">
        <template #default="scope">
          <el-tag :type="getMethodTag(scope.row.method)" size="small">
            {{ formatMethod(scope.row.method) }}
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
      
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            round 
            @click="handleViewReport(scope.row)"
          >
            <el-icon><View /></el-icon>查看详情
          </el-button>
          
          <el-button 
            v-if="scope.row.status !== 'completed'"
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
      <el-form-item label="模型选择" v-if="form.type !== 'adversarial'">
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
      <el-button @click="showEditDialog=false">取消</el-button>
      <el-button type="primary" @click="saveEditTask()">保存</el-button>
    </template>
  </el-dialog>

  <EvalDialog v-model:showDialog="showEvalDialog"
    @close="showEvalDialog = false"
    @task-submitted="handleSubmit()" />

</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { View, Edit, Delete } from '@element-plus/icons-vue';
import EvalDialog from '../common/EvalDialog.vue';
import { getEvaluationTasks, deleteEvaluationTask, updateEvaluationTask } from '@/api/tasks.js';
import { getAllDatasets } from '@/api/datasets.js';
import { getAllModels } from '@/api/models.js';

const router = useRouter();

// ------------------------------------
// 状态与数据
// ------------------------------------
const loading = ref(true);
const tasks = ref([]); // 存放所有任务数据
const modelsList = ref([]);
const datasetsList = ref([]);
const searchQuery = ref(''); // 搜索框输入
const modelLoading = ref(false);
const datasetLoading = ref(false);
const modelSearchQuery = ref('');
const datasetSearchQuery = ref('');
const showEvalDialog = ref(false);
const showEditDialog = ref(false);

// 编辑表单
const form = reactive({
  id: null,
  name: '',
  description: '',
  type: '',
  selectedModelName: '',
  selectedDatasetName: ''
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

// ------------------------------------
// 计算属性
// ------------------------------------
// 过滤任务列表
const filteredTasks = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) {
    return tasks.value;
  }
  return tasks.value.filter(task => 
    task.name.toLowerCase().includes(query) ||
    task.myModel_name.toLowerCase().includes(query) ||
    task.dataset_name.toLowerCase().includes(query)
  );
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

const formatStatus = (status) => {
  const map = {
    pending: '待运行',
    running: '进行中',
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
  };
  return map[status] || '';
};


// ------------------------------------
// 动作处理函数
// ------------------------------------

// 新建任务处理，应该打开弹窗
const handleSubmit = () => {
    fetchTasks(); 
};

// 查看报告/详情
const handleViewReport = (task) => {
  // 跳转到评测报告详情页
  router.push({ 
    name: 'EvalReport', 
    params: { id: task.id } 
  });
};

//编辑任务
const handleEditTask = (task) => {
  showEditDialog.value = true;
  form.id = task.id;
  form.taskName = task.taskName;  
  form.description = task.description;
  form.type = task.method;
  form.selectedModelName = task.myModel_name;
  form.selectedDatasetName = task.dataset_name;
};

const saveEditTask = async () => {
    try{
        const requestBody = {
            name: form.taskName,
            description: form.description,
            method: form.type,
            dataset: datasetsList.value.find(d => d.name === form.selectedDatasetName)?.id,
            ...(form.type !== 'adversarial' ? { myModel: modelsList.value.find(m => m.name === form.selectedModelName)?.id } : {})
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
        await deleteEvaluationTask(task.id);
        ElMessage.success('任务删除成功');
        fetchTasks(); 
    } catch (error) {
        console.error('删除任务失败:', error);
        ElMessage.error(`删除任务失败: ${error.message}`);
    }
};

// ------------------------------------
// 数据加载
// ------------------------------------
const fetchTasks = async () => {
    try {
        const response = await getEvaluationTasks();
        const data = response.data;
        //  格式化所有任务并赋值给 evaluations
        const formattedTasks = data.map(formatTaskDisplay);
        tasks.value = formattedTasks;
        
    } catch (error) {
        console.error('加载评测任务失败:', error);
        ElMessage.error(`加载评测任务失败: ${error.message}`);
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    fetchTasks();
    fetchDatasets();
    fetchModels();
});
</script>

<style scoped>
.my-tasks-container {
  padding: 20px;
}
.action-bar { 
  display: flex;
  align-items: center;
  margin-bottom: 20px; 
}
</style>