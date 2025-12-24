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
        <el-table-column prop="evaluation_type" label="评测类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getEvaluationTypeType(row.evaluation_type)">
              {{ getEvaluationTypeLabel(row.evaluation_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capability_dimension" label="能力维度" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getCapabilityType(row.capability_dimension)" effect="plain">
              {{ getCapabilityLabel(row.capability_dimension) }}
            </el-tag>
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
        <el-table-column prop="is_public" label="公开状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="审核状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
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
        <el-form-item label="测评类型" prop="evaluation_type">
          <el-select v-model="uploadForm.evaluation_type" placeholder="请选择测评类型" style="width: 100%;">
            <el-option label="主观测评 (Subjective)" value="subjective" />
            <el-option label="客观测评 (Objective)" value="objective" />
            <el-option label="对抗测评 (Adversarial)" value="adversarial" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件格式" prop="file_format">
          <el-select v-model="uploadForm.file_format" placeholder="请选择文件格式" style="width: 100%;">
            <el-option 
              v-for="item in availableFileFormats" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
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
        <div class="dialog-footer-actions">
           <el-button type="warning" plain link :icon="QuestionFilled" @click="showInstructionsDialog = true" style="float: left;">
            查看上传须知
          </el-button>
          <span>
            <el-button @click="showUploadDialog = false">取消</el-button>
            <el-button type="primary" :loading="uploading" @click="submitUpload">
              {{ uploading ? '上传中...' : '确认上传' }}
            </el-button>
          </span>
        </div>
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
      <div v-else-if="previewEntries.length > 0">
        <div class="preview-info">
          <span>总条目: {{ previewTotal }} 条</span>
          <span>当前页: {{ previewCurrentPage }} / {{ Math.ceil(previewTotal / previewPageSize) || 1 }}</span>
          <span>每页: {{ previewPageSize }} 条</span>
        </div>
        
        <!-- 数据表格 -->
        <el-table :data="previewEntries" border stripe max-height="400" size="small">
          <el-table-column 
            v-for="field in previewFields" 
            :key="field" 
            :prop="field" 
            :label="field"
            :min-width="getFieldWidth(field)"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="cell-content">{{ formatCellValue(row[field]) }}</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div class="preview-pagination" v-if="previewTotal > 0">
          <el-pagination
            v-model:current-page="previewCurrentPage"
            :page-size="previewPageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="previewTotal"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePreviewSizeChange"
            @current-change="handlePreviewPageChange"
            small
          />
          
          <!-- 快速跳转 Goto 功能 -->
          <div class="goto-container">
            <span>跳转至:</span>
            <el-input-number 
              v-model="gotoPage" 
              :min="1" 
              :max="Math.ceil(previewTotal / previewPageSize) || 1" 
              size="small"
              controls-position="right"
              style="width: 100px; margin: 0 8px;"
            />
            <el-button size="small" type="primary" @click="handleGotoPage">Go</el-button>
          </div>
        </div>
      </div>
      <div v-else>
        <el-empty description="暂无数据条目或不支持预览该格式" :image-size="80" />
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 上传须知弹窗 -->
    <el-dialog v-model="showInstructionsDialog" title="📄 数据集上传须知" width="650px">
      <div class="instructions-content">
        <el-alert
          title="重要提示：不按规定格式上传将导致无法评测，后果自负！"
          type="error"
          show-icon
          :closable="false"
          style="margin-bottom: 20px;"
        />
        
        <h4>1. 文件基础要求</h4>
        <ul>
          <li><strong>格式支持：</strong>CSV, JSON, ZIP</li>
          <li><strong>文件大小：</strong>最大不超过 100MB</li>
          <li><strong>数据结构：</strong>无论何种格式，解析后的数据必须是对象数组（List of Objects）。</li>
        </ul>

        <el-divider />

        <h4>2. 字段要求（根据测评类型）</h4>
        <p>您的数据集中的每条数据（Item）必须包含以下字段，否则系统将报错：</p>
        
        <table class="requirements-table">
          <thead>
            <tr>
              <th>测评类型</th>
              <th>必需字段</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><el-tag type="success" size="small">主观测评</el-tag></td>
              <td><code>input</code>, <code>reference</code></td>
              <td><strong>input</strong>: 问题/提示词<br><strong>reference</strong>: 参考答案</td>
            </tr>
            <tr>
              <td><el-tag type="primary" size="small">客观测评</el-tag></td>
              <td><code>input</code>, <code>answer</code></td>
              <td><strong>input</strong>: 题目内容<br><strong>answer</strong>: 标准答案 (如 "A", "True")</td>
            </tr>
            <tr>
              <td><el-tag type="danger" size="small">对抗测评</el-tag></td>
              <td><code>input</code></td>
              <td><strong>input</strong>: 问题/提示词</td>
            </tr>
          </tbody>
        </table>

        <el-divider />

        <h4>3. 智能能力维度分类</h4>
        <p class="auto-class-note">
          <el-icon><Opportunity /></el-icon>
          <strong>无需手动选择维度：</strong>系统会自动分析您数据集的内容，通过大模型将其归类为以下四个维度之一：
        </p>
        <div class="dimension-tags">
           <el-tag effect="plain">语言理解 (Language)</el-tag>
           <el-tag effect="plain" type="warning">数学推理 (Math)</el-tag>
           <el-tag effect="plain" type="success">代码能力 (Code)</el-tag>
           <el-tag effect="plain" type="info">多模态 (Multimodal)</el-tag>
        </div>

        <el-divider />

        <h4>4. 特殊格式说明</h4>
        <ul>
          <li><strong>JSON 文件：</strong>必须是标准的 JSON 数组格式，例如 <code>[{"input": "...", "answer": "..."}, ...]</code>。</li>
          <li><strong>CSV 文件：</strong>第一行必须是表头（Header），且表头名称必须包含上述必需字段（区分大小写）。</li>
          <li><strong>ZIP 压缩包：</strong>
            <ul>
              <li>必须包含一个 JSON 文件（推荐命名为 <code>data.json</code>）。</li>
              <li>如果是<strong>图像数据集</strong>，图片文件需直接放在 ZIP 根目录或子目录中。</li>
            </ul>
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button type="primary" @click="showInstructionsDialog = false">我已知晓</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  FolderOpened, Folder, Upload, Refresh, Edit, Delete, Download, Loading, View, UploadFilled, QuestionFilled, Opportunity
} from '@element-plus/icons-vue'
import { getMyDatasets, updateDataset, deleteDataset, getDatasetEntries } from '@/api/datasets'
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
const showInstructionsDialog = ref(false)

// 预览相关 - 参考 DatasetSquare.vue 的实现
const currentDataset = ref(null)
const loadingPreview = ref(false)
const previewEntries = ref([])  // 当前页的条目数据
const previewFields = ref([])   // 字段列表
const previewCurrentPage = ref(1)
const previewPageSize = ref(10)
const previewTotal = ref(0)
const gotoPage = ref(1)

// 表单引用
const uploadFormRef = ref(null)
const editFormRef = ref(null)
const uploadRef = ref(null)

// 上传表单
const uploadForm = reactive({
  name: '',
  description: '',
  category: '',
  evaluation_type: 'subjective',
  file_format: '',
  file: null,
  is_public: true
})

// 动态计算可选的文件格式
const availableFileFormats = computed(() => {
  const common = [
    { label: 'CSV 文件', value: 'csv' },
    { label: 'ZIP 压缩包', value: 'zip' }
  ]
  if (uploadForm.category === 'image' || uploadForm.category === 'multimodal') {
    return common
  }
  return [
    ...common,
    { label: 'JSON 文件', value: 'json' }
  ]
})

// 监听分类变化，如果当前格式不再可选范围内则重置
watch(() => uploadForm.category, (newCategory) => {
  if (['image', 'multimodal'].includes(newCategory) && uploadForm.file_format === 'json') {
    uploadForm.file_format = ''
  }
})

// 编辑表单
const editForm = reactive({
  id: null,
  name: '',
  description: '',
  is_public: true
})

// 接受的文件类型 (为了防止浏览器拖拽限制，这里允许所有支持的格式)
const acceptFileTypes = '.csv,.json,.zip'

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
const getStatusLabel = (status) => {
  const map = {
    'pending': '待审核',
    'passed': '通过审核',
    'rejected': '未通过'
  }
  return map[status] || '未知状态'
}

const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'passed': 'success',
    'rejected': 'danger'
  }
  return map[status] || ''
}

const getCategoryLabel = (category) => {
  const map = { image: '图像', text: '文本', multimodal: '多模态' }
  return map[category] || category || '未分类'
}

const getEvaluationTypeLabel = (type) => {
  const labels = {
    'subjective': '主观测评',
    'objective': '客观测评',
    'adversarial': '对抗测评'
  }
  return labels[type] || '未知类型'
}

const getEvaluationTypeType = (type) => {
  const types = {
    'subjective': 'success',
    'objective': 'primary', 
    'adversarial': 'danger'
  }
  return types[type] || 'info'
}

const getCapabilityLabel = (dim) => {
  const labels = {
    'language': '语言理解',
    'math': '数学推理',
    'code': '代码能力',
    'multimodal': '多模态',
    'reasoning': '逻辑推理'
  }
  return labels[dim] || dim || '综合'
}

const getCapabilityType = (dim) => {
  const types = {
    'language': '',
    'math': 'warning',
    'code': 'success',
    'multimodal': 'info',
    'reasoning': 'warning'
  }
  return types[dim] || 'info'
}

const formatFileSize = (size) => {
  if (size === 0) return '0 B'
  if (!size) return '-'
  
  if (size < 0.001) {
    return (size * 1024 * 1024).toFixed(0) + ' B'
  } else if (size < 1) {
    return (size * 1024).toFixed(2) + ' KB'
  } else {
    return size.toFixed(2) + ' MB'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 根据字段名获取列宽度 - 复用 DatasetSquare.vue 的逻辑
const getFieldWidth = (field) => {
  const fieldLower = field.toLowerCase()
  if (fieldLower.includes('content') || fieldLower.includes('text') || 
      fieldLower.includes('answer') || fieldLower.includes('question') ||
      fieldLower.includes('description') || fieldLower.includes('prompt')) {
    return 200
  }
  if (fieldLower === 'id' || fieldLower.includes('_id')) {
    return 60
  }
  return 120
}

// 格式化单元格值 - 复用 DatasetSquare.vue 的逻辑
const formatCellValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  if (typeof value === 'boolean') return value ? '是' : '否'
  return String(value)
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
  if (file.raw.size > 100 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 100MB')
    uploadRef.value?.clearFiles()
    return
  }
  uploadForm.file = file.raw
  
  // 自动识别格式
  const name = file.name.toLowerCase()
  let detectedFormat = ''
  if (name.endsWith('.csv')) {
    detectedFormat = 'csv'
  } else if (name.endsWith('.json')) {
    detectedFormat = 'json'
  } else if (name.endsWith('.zip')) {
    detectedFormat = 'zip'
  }
  
  // 如果识别出的格式在当前分类的可选范围内，则自动选中
  if (detectedFormat) {
    const isImageOrMulti = ['image', 'multimodal'].includes(uploadForm.category)
    if (isImageOrMulti && detectedFormat === 'json') {
      ElMessage.warning('图像或多模态数据集通常需要以 ZIP 格式上传以包含图片文件')
    } else {
      uploadForm.file_format = detectedFormat
    }
  }
  
  // 如果还没填名称，自动填入文件名(去后缀)
  if (!uploadForm.name) {
    const fileName = file.name.substring(0, file.name.lastIndexOf('.'))
    uploadForm.name = fileName.substring(0, 50) // 限制长度
  }
}

const handleFileRemove = () => {
  uploadForm.file = null
}

// 重置上传表单
const resetUploadForm = () => {
  uploadForm.name = ''
  uploadForm.description = ''
  uploadForm.category = ''
  uploadForm.evaluation_type = 'subjective'
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
    const formData = new FormData()
    formData.append('name', uploadForm.name)
    formData.append('description', uploadForm.description || '')
    formData.append('category', uploadForm.category)
    formData.append('evaluation_type', uploadForm.evaluation_type)
    formData.append('file_format', uploadForm.file_format)
    formData.append('is_public', uploadForm.is_public)
    
    if (uploadForm.file) {
      formData.append('file_path', uploadForm.file)
    }
    
    const res = await request.post('/api/datasets/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000
    })
    
    if (res.data?.code === 201 || res.data?.code === 200) {
      ElMessage.success(res.data.msg || '上传成功，请等待审核')
      showUploadDialog.value = false
      resetUploadForm()
      fetchMyDatasets()
    } else {
      ElMessage.error(res.data?.msg || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    let errorMsg = '上传失败，请稍后重试'
    if (error.response?.data) {
      const resData = error.response.data
      // 如果有具体的业务错误消息
      if (resData.msg) errorMsg = resData.msg
      // 如果有详细的字段错误信息 (DRF 格式)
      if (resData.data) {
        const details = resData.data
        const firstKey = Object.keys(details)[0]
        if (firstKey) {
          const firstError = Array.isArray(details[firstKey]) ? details[firstKey][0] : details[firstKey]
          errorMsg += `: ${firstError}`
        }
      }
    }
    ElMessage.error(errorMsg)
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
      timeout: 120000
    })
    
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

// ============ 预览功能 - 参考 DatasetSquare.vue 实现 ============

// 打开预览弹窗
const handlePreview = async (dataset) => {
  if (!dataset.has_file) {
    ElMessage.warning('该数据集没有上传文件')
    return
  }
  
  currentDataset.value = dataset
  showPreviewDialog.value = true
  
  // 重置分页状态
  previewCurrentPage.value = 1
  previewPageSize.value = 10
  previewTotal.value = 0
  previewEntries.value = []
  previewFields.value = []
  gotoPage.value = 1
  
  // 获取第一页数据
  await fetchPreviewEntries(1)
}

// 获取预览数据（分页）- 复用 DatasetSquare.vue 中 fetchDatasetEntries 的逻辑
const fetchPreviewEntries = async (page = 1) => {
  if (!currentDataset.value) return
  
  loadingPreview.value = true
  previewCurrentPage.value = page
  
  try {
    const res = await getDatasetEntries(currentDataset.value.id, {
      page: page,
      page_size: previewPageSize.value
    })
    
    // 后端返回格式: { code: 200, msg: "查询成功", data: { entries: [...], total: 100, fields: [...] } }
    if (res.data?.code === 200 && res.data.data) {
      const { entries, total, fields } = res.data.data
      previewEntries.value = entries || []
      previewTotal.value = total || 0
      
      // 如果后端返回了字段列表则使用，否则从第一条数据中提取
      if (fields && fields.length > 0) {
        previewFields.value = fields
      } else if (entries && entries.length > 0) {
        previewFields.value = Object.keys(entries[0])
      } else {
        previewFields.value = []
      }
    } else {
      previewEntries.value = []
      previewTotal.value = 0
      previewFields.value = []
    }
  } catch (error) {
    console.error('获取预览数据失败:', error)
    // 不显示错误提示，可能是格式不支持
    previewEntries.value = []
    previewTotal.value = 0
    previewFields.value = []
  } finally {
    loadingPreview.value = false
  }
}

// 分页 - 页码改变
const handlePreviewPageChange = (page) => {
  gotoPage.value = page
  fetchPreviewEntries(page)
}

// 分页 - 每页条数改变
const handlePreviewSizeChange = (size) => {
  previewPageSize.value = size
  previewCurrentPage.value = 1
  gotoPage.value = 1
  fetchPreviewEntries(1)
}

// 分页 - 跳转到指定页
const handleGotoPage = () => {
  const totalPages = Math.ceil(previewTotal.value / previewPageSize.value) || 1
  const page = Math.max(1, Math.min(gotoPage.value, totalPages))
  if (page !== previewCurrentPage.value) {
    previewCurrentPage.value = page
    fetchPreviewEntries(page)
  }
}

// 页面加载
onMounted(() => {
  fetchMyDatasets()
})
</script>

<style scoped>
.my-datasets-container {
  padding: 20px;
  background: transparent;
  min-height: 100%;
}

.dataset-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.dataset-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.dataset-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  border-color: var(--accent-color);
}

.card-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-body);
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-content {
  padding: 15px;
  flex: 1;
}

.desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 15px;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.card-actions {
  padding: 10px 15px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: var(--bg-body);
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  background: var(--bg-body);
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: var(--accent-color);
  background: var(--bg-secondary);
}

.upload-tip {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 12px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 300px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  grid-column: 1 / -1;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

/* Dialog Dark Overrides */
:deep(.el-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
}

:deep(.el-form-item__label) {
  color: var(--text-secondary);
}

:deep(.el-input__wrapper) {
  background-color: var(--bg-body);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

:deep(.el-textarea__inner) {
  background-color: var(--bg-body);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  color: var(--text-primary);
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-upload-dragger) {
  background-color: var(--bg-body);
  border-color: var(--border-color);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--accent-color);
  background-color: var(--bg-secondary);
}

.instructions-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.instructions-content h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: var(--text-primary);
  font-weight: 600;
}

.instructions-content ul {
  padding-left: 20px;
  margin-bottom: 15px;
  color: var(--text-secondary);
}

.instructions-content li {
  margin-bottom: 5px;
}

.requirements-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 13px;
}

.requirements-table th,
.requirements-table td {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
}

.requirements-table th {
  background-color: var(--bg-body);
  color: var(--text-primary);
  font-weight: 600;
}

.requirements-table td {
  color: var(--text-secondary);
}

.requirements-table code {
  background-color: var(--bg-body);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--accent-color);
  border: 1px solid var(--border-color);
}

.auto-class-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.dimension-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

:deep(.el-upload__text) {
  color: var(--text-primary);
}
:deep(.el-upload__text em) {
  color: var(--accent-color);
}
:deep(.el-upload__tip) {
  color: var(--text-secondary);
}
</style>
