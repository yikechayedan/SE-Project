<template>
  <div class="my-datasets">
    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" :icon="Upload" size="small" @click="goToManage">
        上传数据集
      </el-button>
      <el-button :icon="Folder" size="small" @click="goToManage">
        管理全部
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 数据集卡片列表 -->
    <div v-else>
      <el-empty v-if="datasets.length === 0" description="暂无数据集" :image-size="80">
        <el-button type="primary" size="small" @click="goToManage">立即上传</el-button>
      </el-empty>

      <el-row :gutter="15" v-else>
        <el-col :span="8" v-for="item in datasets.slice(0, 6)" :key="item.id">
          <el-card shadow="hover" class="dataset-card" @click="showDetail(item)">
            <div class="card-icon">
              <el-icon :size="28"><Folder /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-name">{{ item.name }}</div>
              <div class="card-meta">
                <el-tag size="small" :type="item.is_public ? 'success' : 'info'">
                  {{ item.is_public ? '公开' : '私有' }}
                </el-tag>
                <span class="item-count">{{ formatFileSize(item.file_size) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 查看更多 -->
      <div v-if="datasets.length > 6" class="view-more">
        <el-button type="primary" link @click="goToManage">
          查看全部 {{ datasets.length }} 个数据集 →
        </el-button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetailDialog" :title="currentDataset?.name" width="500px">
      <el-descriptions :column="1" border v-if="currentDataset">
        <el-descriptions-item label="分类">{{ currentDataset.category || '未分类' }}</el-descriptions-item>
        <el-descriptions-item label="文件格式">{{ currentDataset.file_format || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatFileSize(currentDataset.file_size) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentDataset.is_public ? 'success' : 'info'">
            {{ currentDataset.is_public ? '公开' : '私有' }}
          </el-tag>
          <el-tag :type="currentDataset.is_verified ? 'success' : 'warning'" style="margin-left: 5px;">
            {{ currentDataset.is_verified ? '已审核' : '待审核' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentDataset.description || '暂无描述' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="goToManage">前往管理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Folder, Upload, Loading } from '@element-plus/icons-vue'
import { getMyDatasets } from '@/api/datasets'

const router = useRouter()
const loading = ref(false)
const datasets = ref([])
const showDetailDialog = ref(false)
const currentDataset = ref(null)

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '未知'
  return typeof size === 'number' ? `${size.toFixed(2)} MB` : size
}

// 获取我的数据集
const fetchMyDatasets = async () => {
  loading.value = true
  try {
    const res = await getMyDatasets()
    // 后端返回格式: { code: 200, msg: "查询成功", data: [...] }
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasets.value = res.data.data
    } else if (Array.isArray(res.data)) {
      datasets.value = res.data
    } else {
      datasets.value = []
    }
  } catch (error) {
    console.error('获取数据集失败:', error)
    datasets.value = []
  } finally {
    loading.value = false
  }
}

// 显示详情
const showDetail = (item) => {
  currentDataset.value = item
  showDetailDialog.value = true
}

// 跳转到管理页面
const goToManage = () => {
  router.push('/datasets/my')
}

onMounted(() => {
  fetchMyDatasets()
})
</script>

<style scoped>
.my-datasets {
  min-height: 200px;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #8b949e;
}

.loading-container .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.dataset-card {
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
  background: #161b22;
  border: 1px solid #30363d;
}

.dataset-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  border-color: #58a6ff;
}

.dataset-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: #161b22;
}

.card-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #1f6bff 0%, #161b22 100%);
  border: 1px solid #30363d;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #58a6ff;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-weight: 600;
  color: #c9d1d9;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-count {
  font-size: 12px;
  color: #8b949e;
}

.view-more {
  text-align: center;
  margin-top: 10px;
}

/* Dark Theme Overrides for Dialog/Descriptions */
:deep(.el-descriptions__label) {
  background-color: #161b22 !important;
  color: #8b949e !important;
}
:deep(.el-descriptions__content) {
  background-color: #0d1117 !important;
  color: #c9d1d9 !important;
}
:deep(.el-descriptions__cell) {
  border-color: #30363d !important;
}
:deep(.el-dialog__body) {
  padding-top: 10px;
}
</style>
