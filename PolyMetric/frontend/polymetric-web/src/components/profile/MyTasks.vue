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
      
      <el-table-column prop="model_name" label="模型" width="150" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.method === 'adversarial' ? '' : scope.row.model_name }}
        </template>
      </el-table-column>
      <el-table-column prop="dataset_name" label="使用数据集" width="150" show-overflow-tooltip />
      
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
      
      <el-table-column prop="updated_at" label="更新时间" width="160" />
      
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            link 
            @click="handleViewReport(scope.row)"
          >
            查看详情
          </el-button>
          
          <el-button 
            v-if="scope.row.status !== 'completed'"
            size="small" 
            type="danger" 
            link
            @click="handleDeleteTask(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <EvalDialog v-model:showDialog="showEvalDialog"
    @close="showEvalDialog = false"
    @task-submitted="handleSubmit()" />

</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import EvalDialog from '../common/EvalDialog.vue';
// 假设的 API 导入
// import { getMyTasksList, deleteTask } from '@/api/tasks'; 

const router = useRouter();

// ------------------------------------
// 状态与数据
// ------------------------------------
const loading = ref(true);
const tasks = ref([]); // 存放所有任务数据
const searchQuery = ref(''); // 搜索框输入
const showEvalDialog = ref(false);

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
    task.model_name.toLowerCase().includes(query) ||
    task.dataset_name.toLowerCase().includes(query)
  );
});

// ------------------------------------
// 格式化函数 (参照 EvaluationHall.vue)
// ------------------------------------

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

// 假设的新建任务处理，应该打开弹窗
const handleSubmit = () => {
    fetchTasks(); 
};

// 查看报告/详情
const handleViewReport = (task) => {
  // 跳转到评测报告详情页
  router.push({ 
    name: 'EvalReport', 
    params: { id: task.id } // 假设路由参数是 id
  });
};

// 删除任务（需要后端接口支持）
const handleDeleteTask = async (task) => {
    ElMessage.error(`删除任务 ${task.name} 的逻辑待实现...`);
    // try {
    //     await deleteTask(task.id);
    //     ElMessage.success('任务删除成功');
    //     fetchTasks(); // 重新加载列表
    // } catch (error) {
    //     ElMessage.error('任务删除失败');
    // }
};

// ------------------------------------
// 数据加载
// ------------------------------------
const fetchTasks = async () => {
    loading.value = true;
    try {
        // 🚀 真实 API 调用（请取消注释并使用实际的 API 函数）
        // const response = await getMyTasksList();
        // tasks.value = response.data;
        
        // 调试/占位数据 (请替换为真实的 API 响应结构)
        tasks.value = [
            { id: 1, name: 'GPT-4 图像分类', model_name: 'GPT-4V', dataset_name: 'COCO 2017', method: 'objective', status: 'completed', updated_at: '2025-12-03T10:00:00Z' },
            { id: 2, name: 'LLama2 逻辑推理', model_name: 'Code Llama', dataset_name: 'MATH', method: 'subjective', status: 'pending', updated_at: '2025-12-01T15:30:00Z' },
            { id: 3, name: '模型A vs 模型B 对抗评测', model_name: '', dataset_name: 'Adversarial Set', method: 'adversarial', status: 'running', updated_at: '2025-12-04T09:00:00Z' },
        ];
        
    } catch (error) {
        ElMessage.error('加载个人任务列表失败');
        console.error(error);
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    fetchTasks();
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