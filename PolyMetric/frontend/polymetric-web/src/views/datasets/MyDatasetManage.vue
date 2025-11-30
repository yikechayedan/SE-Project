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
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category || '未分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="item_count" label="数据量" width="100">
          <template #default="{ row }">
            {{ row.item_count || 0 }} 条
          </template>
        </el-table-column>
        <el-table-column prop="download_count" label="下载量" width="100">
          <template #default="{ row }">
            {{ row.download_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" :icon="Edit" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="success" size="small" :icon="Download" @click="handleDownload(row)">
              下载
            </el-button>
            <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(row)">
              删除
            </el-button>
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
        <el-form-item label="分类" prop="category">
          <el-select v-model="uploadForm.category" placeholder="请选择分类" style="width: 100%;">
            <el-option label="综合评测" value="综合评测" />
            <el-option label="代码生成" value="代码生成" />
            <el-option label="中文评测" value="中文评测" />
            <el-option label="数学推理" value="数学推理" />
            <el-option label="视觉理解" value="视觉理解" />
            <el-option label="其他" value="其他" />
          </el-select>
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
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="uploadForm.is_public" />
          <span class="tip">{{ uploadForm.is_public ? '其他用户可以浏览和下载' : '仅自己可见' }}</span>
        </el-form-item>
        <el-form-item label="数据集文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".zip,.csv,.json,.jsonl"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .zip、.csv、.json、.jsonl 格式，单文件最大 100MB
              </div>
            </template>
          </el-upload>
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
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="请选择分类" style="width: 100%;">
            <el-option label="综合评测" value="综合评测" />
            <el-option label="代码生成" value="代码生成" />
            <el-option label="中文评测" value="中文评测" />
            <el-option label="数学推理" value="数学推理" />
            <el-option label="视觉理解" value="视觉理解" />
            <el-option label="其他" value="其他" />
          </el-select>
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
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  FolderOpened, Folder, Upload, Refresh, Edit, Delete, Download, Loading, UploadFilled 
} from '@element-plus/icons-vue'
import { getMyDatasets, createDataset, updateDataset, deleteDataset, downloadDataset } from '@/api/datasets'

// 状态
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const datasets = ref([])

// 弹窗
const showUploadDialog = ref(false)
const showEditDialog = ref(false)

// 表单引用
const uploadFormRef = ref(null)
const editFormRef = ref(null)
const uploadRef = ref(null)

// 上传表单
const uploadForm = reactive({
  name: '',
  category: '',
  description: '',
  is_public: true,
  file: null
})

// 编辑表单
const editForm = reactive({
  id: null,
  name: '',
  category: '',
  description: '',
  is_public: true
})

// 表单验证规则
const uploadRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

const editRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取我的数据集
const fetchMyDatasets = async () => {
  loading.value = true
  try {
    const res = await getMyDatasets()
    if (res.data?.results) {
      datasets.value = res.data.results
    } else if (Array.isArray(res.data)) {
      datasets.value = res.data
    } else {
      datasets.value = []
    }
  } catch (error) {
    console.error('获取数据集失败:', error)
    // 模拟数据
    datasets.value = [
      { id: 1, name: '我的测试集1', category: '综合评测', item_count: 1000, download_count: 50, is_public: true, created_at: '2025-01-20' },
      { id: 2, name: '私有数据集', category: '代码生成', item_count: 500, download_count: 0, is_public: false, created_at: '2025-02-01' },
    ]
  } finally {
    loading.value = false
  }
}

// 文件选择
const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.file = null
}

// 重置上传表单
const resetUploadForm = () => {
  uploadForm.name = ''
  uploadForm.category = ''
  uploadForm.description = ''
  uploadForm.is_public = true
  uploadForm.file = null
  uploadFormRef.value?.resetFields()
}

// 提交上传
const submitUpload = async () => {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('name', uploadForm.name)
    formData.append('category', uploadForm.category)
    formData.append('description', uploadForm.description)
    formData.append('is_public', uploadForm.is_public)
    formData.append('file', uploadForm.file)
    
    await createDataset(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    resetUploadForm()
    fetchMyDatasets()
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
  editForm.category = row.category
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
    await updateDataset(editForm.id, {
      name: editForm.name,
      category: editForm.category,
      description: editForm.description,
      is_public: editForm.is_public
    })
    ElMessage.success('保存成功')
    showEditDialog.value = false
    fetchMyDatasets()
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
      `确定要删除数据集「${row.name}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDataset(row.id)
    ElMessage.success('删除成功')
    fetchMyDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// 下载
const handleDownload = async (dataset) => {
  try {
    ElMessage.info('开始下载...')
    const res = await downloadDataset(dataset.id)
    
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${dataset.name}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请稍后重试')
  }
}

// 初始化
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

.tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
