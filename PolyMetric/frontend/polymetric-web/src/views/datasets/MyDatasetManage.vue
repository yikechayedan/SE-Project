<template>
  <div class="my-dataset-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><FolderOpened /></el-icon>
        我的数据集
      </h2>
      <p class="subtitle">管理您上传的数据集，支持上传、编辑和删除</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" :icon="Upload" @click="showUploadDialog = true">
        上传数据集
      </el-button>
      <el-button :icon="Refresh" @click="fetchMyDatasets">刷新</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 数据集列表 -->
    <div v-else>
      <el-empty v-if="datasets.length === 0" description="您还没有上传任何数据集">
        <el-button type="primary" @click="showUploadDialog = true">立即上传</el-button>
      </el-empty>

      <el-table v-else :data="datasets" border stripe style="width: 100%;">
        <el-table-column prop="name" label="数据集名称" min-width="150">
          <template #default="{ row }">
            <div class="dataset-name">
              <el-icon><Folder /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_format" label="格式" width="70" align="center">
          <template #default="{ row }">
            {{ row.file_format?.toUpperCase() || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="90" align="center">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="sample_count" label="样本数" width="90" align="center">
          <template #default="{ row }">
            {{ row.sample_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="has_file" label="文件" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.has_file ? 'success' : 'info'" size="small">
              {{ row.has_file ? '有' : '无' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="状态" width="130" align="center">
          <template #default="{ row }">
            <div class="status-tags">
              <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
                {{ row.is_public ? '公开' : '私有' }}
              </el-tag>
              <el-tag :type="row.is_verified ? 'success' : 'warning'" size="small">
                {{ row.is_verified ? '已审核' : '待审核' }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="info" size="small" text @click="handlePreview(row)" :disabled="!row.has_file">
                <el-icon><View /></el-icon>预览
              </el-button>
              <el-button type="primary" size="small" text @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="success" size="small" text @click="handleDownload(row)" :disabled="!row.has_file">
                <el-icon><Download /></el-icon>下载
              </el-button>
              <el-button type="danger" size="small" text @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 上传数据集弹窗 -->
    <el-dialog v-model="showUploadDialog" title="上传数据集" width="550px" @close="resetUploadForm">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入数据集名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="uploadForm.description" 
            placeholder="请输入数据集描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="uploadForm.category" placeholder="请选择分类" style="width: 100%;">
            <el-option label="图像数据 (image)" value="image" />
            <el-option label="文本数据 (text)" value="text" />
            <el-option label="多模态数据 (multimodal)" value="multimodal" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件格式" prop="file_format">
          <el-select v-model="uploadForm.file_format" placeholder="请选择文件格式" style="width: 100%;">
            <el-option label="CSV 文件" value="csv" />
            <el-option label="JSON 文件" value="json" />
            <el-option label="ZIP 压缩包" value="zip" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据集文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="dataset-uploader"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :accept="acceptFileTypes"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV、JSON、ZIP 格式，文件大小不超过 100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="uploadForm.is_public" />
          <span class="tip">{{ uploadForm.is_public ? '其他用户可以浏览和下载' : '仅自己可见' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">
          {{ uploading ? '上传中...' : '确认上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑数据集弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑数据集" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入数据集名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="editForm.description" 
            placeholder="请输入数据集描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="是否公开">
          <el-switch v-model="editForm.is_public" />
          <span class="tip">{{ editForm.is_public ? '其他用户可以浏览和下载' : '仅自己可见' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览数据集弹窗 -->
    <el-dialog v-model="showPreviewDialog" :title="`数据预览 - ${currentDataset?.name || ''}`" width="900px">
      <div v-if="loadingPreview" class="loading-container">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="previewData">
        <div class="preview-info">
          <span>格式: {{ previewData.format?.toUpperCase() }}</span>
          <span>总条目: {{ previewData.total }}</span>
          <span>当前显示: {{ previewData.rows?.length || 0 }} 条</span>
        </div>
        <el-table :data="previewData.rows" border stripe max-height="400" v-if="previewData.rows?.length">
          <el-table-column 
            v-for="header in previewData.headers" 
            :key="header" 
            :prop="header" 
            :label="header"
            min-width="120"
            show-overflow-tooltip
          />
        </el-table>
        <el-empty v-else description="暂无数据" />
      </div>
      <div v-else>
        <el-empty description="无法加载预览数据" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  FolderOpened, Folder, Upload, Refresh, Edit, Delete, Download, Loading, View, UploadFilled
} from '@element-plus/icons-vue'
import { getMyDatasets, updateDataset, deleteDataset } from '@/api/datasets'
import request from '@/api/request'

// 状态
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const datasets = ref([])

// 弹窗
const showUploadDialog = ref(false)
const showEditDialog = ref(false)
const showPreviewDialog = ref(false)

// 预览相关
const currentDataset = ref(null)
const previewData = ref(null)
const loadingPreview = ref(false)

// 表单引用
const uploadFormRef = ref(null)
const editFormRef = ref(null)
const uploadRef = ref(null)

// 上传表单
const uploadForm = reactive({
  name: '',
  description: '',
  category: '',
  file_format: '',
  file: null,
  is_public: true
})

// 编辑表单
const editForm = reactive({
  id: null,
  name: '',
  description: '',
  is_public: true
})

// 接受的文件类型
const acceptFileTypes = computed(() => {
  const formatMap = {
    csv: '.csv',
    json: '.json',
    zip: '.zip'
  }
  return formatMap[uploadForm.file_format] || '.csv,.json,.zip'
})

// 表单验证规则
const uploadRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  file_format: [{ required: true, message: '请选择文件格式', trigger: 'change' }]
}

const editRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 工具函数
const getCategoryLabel = (category) => {
  const map = { image: '图像', text: '文本', multimodal: '多模态' }
  return map[category] || category || '未分类'
}

const formatFileSize = (size) => {
  if (!size) return '-'
  return typeof size === 'number' ? size.toFixed(2) + ' MB' : size
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取我的数据集
const fetchMyDatasets = async () => {
  loading.value = true
  try {
    const res = await getMyDatasets()
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasets.value = res.data.data
    } else if (Array.isArray(res.data)) {
      datasets.value = res.data
    } else {
      datasets.value = []
    }
  } catch (error) {
    console.error('获取数据集失败:', error)
    ElMessage.error('获取数据集失败，请稍后重试')
    datasets.value = []
  } finally {
    loading.value = false
  }
}

// 文件选择处理
const handleFileChange = (file) => {
  // 验证文件大小
  if (file.raw.size > 100 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 100MB')
    uploadRef.value?.clearFiles()
    return
  }
  uploadForm.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.file = null
}

// 重置上传表单
const resetUploadForm = () => {
  uploadForm.name = ''
  uploadForm.description = ''
  uploadForm.category = ''
  uploadForm.file_format = ''
  uploadForm.file = null
  uploadForm.is_public = true
  uploadFormRef.value?.resetFields()
  uploadRef.value?.clearFiles()
}

// 提交上传
const submitUpload = async () => {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  uploading.value = true
  try {
    // 使用 FormData 上传文件
    const formData = new FormData()
    formData.append('name', uploadForm.name)
    formData.append('description', uploadForm.description || '')
    formData.append('category', uploadForm.category)
    formData.append('file_format', uploadForm.file_format)
    formData.append('is_public', uploadForm.is_public)
    
    // 如果有文件则添加
    if (uploadForm.file) {
      formData.append('file_path', uploadForm.file)
    }
    
    const res = await request.post('/api/datasets/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000  // 上传文件超时时间设长一点
    })
    
    if (res.data?.code === 201 || res.data?.code === 200) {
      ElMessage.success(res.data.msg || '上传成功')
      showUploadDialog.value = false
      resetUploadForm()
      fetchMyDatasets()
    } else {
      ElMessage.error(res.data?.msg || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.msg || '上传失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

// 编辑
const handleEdit = (row) => {
  editForm.id = row.id
  editForm.name = row.name
  editForm.description = row.description || ''
  editForm.is_public = row.is_public
  showEditDialog.value = true
}

// 提交编辑
const submitEdit = async () => {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const updateData = {
      name: editForm.name,
      description: editForm.description,
      is_public: editForm.is_public
    }
    
    const res = await updateDataset(editForm.id, updateData)
    
    if (res.data?.code === 200) {
      ElMessage.success(res.data.msg || '保存成功')
      showEditDialog.value = false
      fetchMyDatasets()
    } else {
      ElMessage.error(res.data?.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.msg || '保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除数据集「' + row.name + '」吗？此操作不可恢复。',
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    
    const res = await deleteDataset(row.id)
    
    if (res.data?.code === 200) {
      ElMessage.success(res.data.msg || '删除成功')
      fetchMyDatasets()
    } else {
      ElMessage.error(res.data?.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.msg || '删除失败，请稍后重试')
    }
  }
}

// 下载
const handleDownload = async (dataset) => {
  if (!dataset.has_file) {
    ElMessage.warning('该数据集没有上传文件')
    return
  }
  
  try {
    ElMessage.info('开始下载...')
    
    const res = await request.get(`/api/datasets/${dataset.id}/download/`, {
      responseType: 'blob',
      timeout: 120000  // 下载超时2分钟
    })
    
    // 检查是否是错误响应
    if (res.data.type === 'application/json') {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const errorData = JSON.parse(reader.result)
          ElMessage.error(errorData.msg || '下载失败')
        } catch {
          ElMessage.error('下载失败')
        }
      }
      reader.readAsText(res.data)
      return
    }
    
    // 创建 Blob 并触发下载
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${dataset.name}.${dataset.file_format || 'zip'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('数据集文件不存在')
    } else {
      ElMessage.error('下载失败，请稍后重试')
    }
  }
}

// 预览
const handlePreview = async (dataset) => {
  if (!dataset.has_file) {
    ElMessage.warning('该数据集没有上传文件')
    return
  }
  
  currentDataset.value = dataset
  showPreviewDialog.value = true
  loadingPreview.value = true
  previewData.value = null
  
  try {
    const res = await request.get(`/api/datasets/${dataset.id}/preview/`, {
      params: { limit: 20 }
    })
    
    if (res.data?.code === 200) {
      previewData.value = res.data.data
    } else {
      ElMessage.error(res.data?.msg || '预览失败')
    }
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  } finally {
    loadingPreview.value = false
  }
}

// 页面加载
onMounted(() => {
  fetchMyDatasets()
})
</script>

<style scoped>
.my-dataset-manage {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: calc(100vh - 140px);
}

.page-header {
  margin-bottom: 25px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: #303133;
}

.page-header .subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.status-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.action-buttons .el-button {
  padding: 4px 8px;
  margin: 0;
}

.action-buttons .el-button .el-icon {
  margin-right: 2px;
}

.tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.dataset-uploader {
  width: 100%;
}

.dataset-uploader :deep(.el-upload) {
  width: 100%;
}

.dataset-uploader :deep(.el-upload-dragger) {
  width: 100%;
}

.preview-info {
  margin-bottom: 15px;
  color: #606266;
  display: flex;
  gap: 20px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}

:deep(.el-table .cell) {
  padding: 8px;
}
</style>
