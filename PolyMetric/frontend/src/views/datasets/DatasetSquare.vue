<template>
  <div class="dataset-square">
    <div class="hero">
      <div class="hero-left">
        <div class="title-row">
          <div class="badge">数据集广场</div>
          <h2>评测数据集榜单</h2>
        </div>
        <p class="subtitle">优先展示高质量、已审核、被关注的数据集，像榜单一样浏览。</p>
        <div class="hero-stats">
          <div class="stat-card type-total">
            <div class="label">已收录</div>
            <div class="value">{{ filteredDatasets.length }}</div>
            <div class="hint">数据集数量</div>
          </div>
          <div class="stat-card type-verified">
            <div class="label">已审核</div>
            <div class="value">{{ verifiedCount }}</div>
            <div class="hint">通过审核</div>
          </div>
          <div class="stat-card type-star">
            <div class="label">总点赞</div>
            <div class="value">{{ totalStars }}</div>
            <div class="hint">全站热度</div>
          </div>
          <div class="stat-card type-followed">
            <div class="label">已关注</div>
            <div class="value">{{ followedCount }}</div>
            <div class="hint">你的关注</div>
          </div>
          <div class="stat-card type-image">
            <div class="label">图像</div>
            <div class="value">{{ imageDatasetCount }}</div>
            <div class="hint">Image</div>
          </div>
          <div class="stat-card type-text">
            <div class="label">文本</div>
            <div class="value">{{ textDatasetCount }}</div>
            <div class="hint">Text</div>
          </div>
          <div class="stat-card type-multi">
            <div class="label">多模态</div>
            <div class="value">{{ multimodalDatasetCount }}</div>
            <div class="hint">Multi</div>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="mini-rank" v-if="rankedTop3.length">
          <div class="mini-title">Top 3</div>
          <div class="mini-item" v-for="item in rankedTop3" :key="item.id">
            <span class="mini-rank-num">#{{ item._rank }}</span>
            <div class="mini-info">
              <div class="mini-name">{{ item.name }}</div>
              <div class="mini-tags">
                <el-tag size="small" effect="dark" :type="getCategoryType(item.category)">
                  {{ getCategoryLabel(item.category) }}
                </el-tag>
                <el-tag size="small" effect="plain">{{ formatFileSize(item.file_size) }}</el-tag>
                <span class="mini-star"><el-icon><StarFilled /></el-icon>{{ item.star_count }}</span>
              </div>
            </div>
            <el-button link type="primary" size="small" @click="showDetail(item)">详情</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索数据集名称..."
          :prefix-icon="Search"
          clearable
          @input="handleLocalFilter"
          @clear="handleLocalFilter"
          class="filter-input"
        />
        <el-select
          v-model="categoryFilter"
          placeholder="选择分类"
          clearable
          @change="handleLocalFilter"
          class="filter-select"
        >
          <el-option label="全部分类" value="" />
          <el-option label="图像" value="image" />
          <el-option label="文本" value="text" />
          <el-option label="多模态" value="multimodal" />
        </el-select>
        <el-checkbox 
          v-model="onlyFollowed" 
          label="仅看已关注" 
          border 
          @change="handleLocalFilter"
          class="filter-checkbox" 
        />
        <el-button :icon="Refresh" @click="resetFilter">重置</el-button>
        <el-button type="primary" :icon="Upload" @click="showUploadDialog = true">上传数据集</el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else>
      <el-empty v-if="filteredDatasets.length === 0" description="暂无数据集" />

      <div v-else class="board-list">
        <div
          v-for="item in paginatedRankedDatasets"
          :key="item.id"
          class="board-row"
          :class="{ 'top-row': item._rank <= 3 }"
        >
          <div class="rank">
            <span>#{{ item._rank }}</span>
          </div>
          <div class="meta">
            <div class="name-line">
              <el-icon><Folder /></el-icon>
              <span class="name">{{ item.name }}</span>
              <el-tag size="small" :type="getCategoryType(item.category)">{{ getCategoryLabel(item.category) }}</el-tag>
              <el-tag size="small" :type="getEvaluationTypeType(item.evaluation_type)">{{ getEvaluationTypeLabel(item.evaluation_type) }}</el-tag>
            </div>
            <div class="meta-sub">
              <span>上传者: 
                <UserPopover :user-id="item.creator_id" :username="item.creator_username" v-if="item.creator_id" />
                <span v-else>{{ item.creator_username || '未知' }}</span>
              </span>
              <span class="dot" />
              <span>{{ formatFileSize(item.file_size) }}</span>
            </div>
          </div>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">点赞热度</div>
              <div class="metric-value star-val">
                <el-icon><StarFilled /></el-icon>
                <span>{{ item.star_count }}</span>
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">审核状态</div>
              <div class="metric-value" :class="{ on: item.is_verified }">{{ item.is_verified ? '已审核' : '待审核' }}</div>
            </div>
          </div>
          <div class="actions">
            <el-button type="primary" size="small" @click="showDetail(item)">详情</el-button>
            <el-button type="success" size="small" :icon="Download" @click="handleDownload(item)">下载</el-button>
            <el-button
              type="primary"
              plain
              size="small"
              :icon="ChatDotRound"
              @click="handleShowComments(item)"
            >
              评论
            </el-button>
            <el-button
              :type="item.is_starred ? 'danger' : 'default'"
              size="small"
              :icon="item.is_starred ? StarFilled : Star"
              @click="handleToggleStar(item)"
              :loading="item.starLoading"
              class="star-btn"
            >
              {{ item.is_starred ? '已点赞' : '点赞' }}
            </el-button>
            <el-button
              :type="item.is_followed ? 'warning' : 'info'"
              size="small"
              :icon="item.is_followed ? Opportunity : Star"
              @click="handleToggleFollow(item)"
              :loading="item.followLoading"
            >
              {{ item.is_followed ? '已关注' : '关注' }}
            </el-button>
          </div>
        </div>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="filteredDatasets.length"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 数据集详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      :title="currentDataset?.name" 
      width="900px"
      :close-on-click-modal="false"
      class="dataset-detail-dialog"
    >
      <div v-if="detailLoading" class="dialog-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载详情中...</span>
      </div>
      
      <div class="detail-content" v-else-if="datasetDetail">
        <div class="detail-header-stats">
           <div class="d-stat">
              <span class="label">热度</span>
              <span class="value"><el-icon><StarFilled /></el-icon> {{ datasetDetail.star_count }}</span>
           </div>
        </div>
        <!-- 基本信息区域 -->
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="基本信息" name="info">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="数据集名称">{{ datasetDetail.name }}</el-descriptions-item>
              <el-descriptions-item label="上传者">
                <UserPopover :user-id="datasetDetail.creator_id" :username="datasetDetail.creator_username" v-if="datasetDetail.creator_id" />
                <span v-else>{{ datasetDetail.creator_username || '未知' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="分类">
                <el-tag :type="getCategoryType(datasetDetail.category)" size="small">
                  {{ getCategoryLabel(datasetDetail.category) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="评测类型">
                <el-tag :type="getEvaluationTypeType(datasetDetail.evaluation_type)" size="small">
                  {{ getEvaluationTypeLabel(datasetDetail.evaluation_type) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="能力维度">
                <el-tag :type="getCapabilityType(datasetDetail.capability_dimension)" size="small" effect="dark">
                  {{ getCapabilityLabel(datasetDetail.capability_dimension) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="文件格式">{{ datasetDetail.file_format || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(datasetDetail.file_size) }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="datasetDetail.is_verified ? 'success' : 'warning'" size="small">
                  {{ datasetDetail.is_verified ? '已审核' : '待审核' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(datasetDetail.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(datasetDetail.updated_at) }}</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">
                {{ datasetDetail.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>
        </el-collapse>

        <!-- 数据条目预览区域 -->
        <div class="entries-section">
          <div class="entries-header">
            <h4>
              <el-icon><Document /></el-icon>
              数据条目预览
              <span class="entries-total" v-if="entriesTotal > 0">（共 {{ entriesTotal }} 条）</span>
            </h4>
            <el-button 
              size="small" 
              :icon="Refresh" 
              @click="fetchDatasetEntries(1)"
              :loading="entriesLoading"
            >
              刷新
            </el-button>
          </div>

          <div v-if="entriesLoading" class="entries-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载数据条目中...</span>
          </div>

          <div v-else-if="datasetEntries.length > 0" class="entries-container">
            <el-table 
              :data="datasetEntries" 
              border 
              stripe 
              size="small"
              max-height="350"
              style="width: 100%;"
            >
              <el-table-column 
                v-for="field in entryFields" 
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

            <div class="entries-pagination">
              <el-pagination
                v-model:current-page="entriesCurrentPage"
                :page-size="entriesPageSize"
                :total="entriesTotal"
                :background="true"
                layout="prev, pager, next, jumper"
                @current-change="handleEntriesPageChange"
                small
              />
            </div>
          </div>

          <el-empty v-else description="暂无数据条目或不支持预览该格式" :image-size="80" />
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          :type="datasetDetail?.is_starred ? 'danger' : 'default'" 
          :icon="datasetDetail?.is_starred ? StarFilled : Star"
          @click="handleToggleStarInDialog"
          :loading="dialogStarLoading"
        >
          {{ datasetDetail?.is_starred ? '取消点赞' : '点赞' }}
        </el-button>
        <el-button 
          :type="datasetDetail?.is_followed ? 'warning' : 'info'" 
          :icon="datasetDetail?.is_followed ? Opportunity : Star"
          @click="handleToggleFollowInDialog"
          :loading="dialogFollowLoading"
        >
          {{ datasetDetail?.is_followed ? '取消关注' : '关注' }}
        </el-button>
        <el-button type="success" :icon="Download" @click="handleDownload(currentDataset)">
          下载数据集
        </el-button>
      </template>
    </el-dialog>

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

    <!-- 评论组件 -->
    <CommentSection
      v-model="showCommentDialog"
      target-type="dataset"
      :target-id="currentCommentDatasetId"
    />

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
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Folder, Download, Loading, Star, StarFilled, Document, User, Opportunity, ChatDotRound, UploadFilled, QuestionFilled } from '@element-plus/icons-vue'
import UserPopover from '@/components/common/UserPopover.vue'
import { getAllDatasets, getDatasetDetail, downloadDataset, followDataset, unfollowDataset, getDatasetEntries, starDataset, unstarDataset, createDataset } from '@/api/datasets'
import CommentSection from '@/components/common/CommentSection.vue'

// 状态
const loading = ref(false)
const allDatasets = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const onlyFollowed = ref(false)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(5)

// 详情弹窗
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const dialogFollowLoading = ref(false)
const dialogStarLoading = ref(false)
const currentDataset = ref(null)
const datasetDetail = ref(null)
const activeCollapse = ref(['info'])  // 默认展开基本信息

// 评论弹窗
const showCommentDialog = ref(false)
const currentCommentDatasetId = ref(null)

// 上传相关状态
const showUploadDialog = ref(false)
const showInstructionsDialog = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const uploadFormRef = ref(null)

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
  if (uploadForm.category === 'image' || uploadForm.category === 'multimodal') {
    // 图像和多模态强制要求 ZIP (以包含物理图片文件)
    return [
      { label: 'ZIP 压缩包', value: 'zip' }
    ]
  }
  // 文本数据支持全部三种格式
  return [
    { label: 'CSV 文件', value: 'csv' },
    { label: 'JSON 文件', value: 'json' },
    { label: 'ZIP 压缩包', value: 'zip' }
  ]
})

// 监听分类变化，如果当前格式不再可选范围内则重置
watch(() => uploadForm.category, (newCategory) => {
  const formats = availableFileFormats.value.map(f => f.value)
  if (!formats.includes(uploadForm.file_format)) {
    uploadForm.file_format = ''
  }
})

// 接受的文件类型 (根据分类动态限制)
const acceptFileTypes = computed(() => {
  if (uploadForm.category === 'image' || uploadForm.category === 'multimodal') {
    return '.zip'
  }
  return '.csv,.json,.zip'
})

const uploadRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  file_format: [{ required: true, message: '请选择文件格式', trigger: 'change' }]
}

// 智能文件处理：拖拽文件后自动识别格式
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

const submitUpload = async () => {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  if (!uploadForm.file) {
    ElMessage.warning('请上传数据集文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('name', uploadForm.name)
    formData.append('description', uploadForm.description || '')
    formData.append('category', uploadForm.category)
    formData.append('evaluation_type', uploadForm.evaluation_type)
    formData.append('file_format', uploadForm.file_format)
    formData.append('is_public', uploadForm.is_public)
    formData.append('file_path', uploadForm.file)
    
    const res = await createDataset(formData)
    
    if (res.data?.code === 201 || res.data?.code === 200) {
      ElMessage.success(res.data.msg || '上传成功')
      showUploadDialog.value = false
      resetUploadForm()
      // 刷新列表
      fetchAllDatasets()
    } else {
      console.error('Upload failed with response:', res.data)
      let errorMsg = res.data?.msg || '上传失败'
      if (res.data?.data) {
        const firstKey = Object.keys(res.data.data)[0]
        if (firstKey) {
          const detail = Array.isArray(res.data.data[firstKey]) ? res.data.data[firstKey][0] : res.data.data[firstKey]
          errorMsg += `: ${detail}`
        }
      }
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('上传失败:', error)
    let errorMsg = '上传失败，请稍后重试'
    if (error.response?.data) {
      const resData = error.response.data
      if (resData.msg) errorMsg = resData.msg
      if (resData.data) {
        const firstKey = Object.keys(resData.data)[0]
        if (firstKey) {
          const detail = Array.isArray(resData.data[firstKey]) ? resData.data[firstKey][0] : resData.data[firstKey]
          errorMsg += `: ${detail}`
        }
      }
    }
    ElMessage.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

// 显示评论
const handleShowComments = (row) => {
  currentCommentDatasetId.value = row.id
  showCommentDialog.value = true
}

// 数据条目相关状态
const entriesLoading = ref(false)
const datasetEntries = ref([])
const entryFields = ref([])  // 动态字段列表
const entriesCurrentPage = ref(1)
const entriesPageSize = ref(10)
const entriesTotal = ref(0)

// 本地筛选后的数据集（并排序：关注 > 热度 > 上传时间）
const filteredDatasets = computed(() => {
  let result = allDatasets.value
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    result = result.filter(item => item.name.toLowerCase().includes(keyword))
  }
  if (categoryFilter.value) {
    result = result.filter(item => item.category === categoryFilter.value)
  }
  if (onlyFollowed.value) {
    result = result.filter(item => item.is_followed)
  }
  
  // 排序：关注 > 热度 > 上传时间
  return result.sort((a, b) => {
    // 1. Followed (is_followed) - true first
    if (a.is_followed !== b.is_followed) {
      return a.is_followed ? -1 : 1
    }
    // 2. Heat (star_count) - desc
    const starA = a.star_count || 0
    const starB = b.star_count || 0
    if (starA !== starB) return starB - starA

    // 3. Upload Time (created_at) - desc (newer first)
    const dateA = new Date(a.created_at || 0).getTime()
    const dateB = new Date(b.created_at || 0).getTime()
    return dateB - dateA
  })
})

// 榜单派生数据
const verifiedCount = computed(() => filteredDatasets.value.filter(item => item.is_verified).length)
const followedCount = computed(() => allDatasets.value.filter(item => item.is_followed).length)
const totalStars = computed(() => allDatasets.value.reduce((acc, m) => acc + (m.star_count || 0), 0))

// 各类型数量统计
const imageDatasetCount = computed(() => allDatasets.value.filter(d => d.category === 'image').length)
const textDatasetCount = computed(() => allDatasets.value.filter(d => d.category === 'text').length)
const multimodalDatasetCount = computed(() => allDatasets.value.filter(d => d.category === 'multimodal').length)

const rankedDatasets = computed(() => filteredDatasets.value.map((item, idx) => ({ ...item, _rank: idx + 1 })))
const paginatedRankedDatasets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rankedDatasets.value.slice(start, end)
})

// Top 3 逻辑：按 热度 (star_count) 排序
const rankedTop3 = computed(() => {
  const sorted = [...allDatasets.value].sort((a, b) => {
    // Heat (star_count) - desc
    const starA = a.star_count || 0
    const starB = b.star_count || 0
    return starB - starA
  })
  return sorted.slice(0, 3).map((item, idx) => ({ ...item, _rank: idx + 1 }))
})

// 监听筛选条件变化，重置到第一页
watch([searchQuery, categoryFilter, onlyFollowed], () => {
  currentPage.value = 1
})

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 切换每页条数时回到第一页
}

// 处理页码变化
const handlePageChange = (val) => {
  currentPage.value = val
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size === 0) return '0 B'
  if (!size) return '未知'
  
  // size is in MB from backend
  if (size < 0.001) {
    // Less than 1KB -> Bytes
    return (size * 1024 * 1024).toFixed(0) + ' B'
  } else if (size < 1) {
    // Less than 1MB -> KB
    return (size * 1024).toFixed(2) + ' KB'
  } else {
    // MB
    return size.toFixed(2) + ' MB'
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 分类英文转中文
const getCategoryLabel = (category) => {
  const labels = {
    'image': '图像',
    'text': '文本',
    'multimodal': '多模态'
  }
  return labels[category] || category || '未分类'
}

const getCategoryType = (category) => {
  const types = {
    'image': 'primary',
    'text': 'success',
    'multimodal': 'warning'
  }
  return types[category] || ''
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

// 根据字段名获取列宽度
const getFieldWidth = (field) => {
  const fieldLower = field.toLowerCase()
  // 长文本字段给更多宽度
  if (fieldLower.includes('content') || fieldLower.includes('text') || 
      fieldLower.includes('answer') || fieldLower.includes('question') ||
      fieldLower.includes('description') || fieldLower.includes('prompt')) {
    return 200
  }
  // ID 和短字段
  if (fieldLower === 'id' || fieldLower.includes('_id')) {
    return 60
  }
  // 默认宽度
  return 120
}

// 格式化单元格值
const formatCellValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  if (typeof value === 'boolean') return value ? '是' : '否'
  return String(value)
}

// 从后端获取所有数据集（带关注状态）
const fetchAllDatasets = async () => {
  loading.value = true
  try {
    const res = await getAllDatasets()
    // 后端返回格式: { code: 200, msg: "查询成功", data: [...] }
    let datasets = []
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      datasets = res.data.data
    } else if (Array.isArray(res.data)) {
      datasets = res.data
    }
    // 为每个数据集添加 followLoading 状态
    allDatasets.value = datasets.map(item => ({
      ...item,
      is_followed: item.is_followed || false,
      is_starred: item.is_starred || false,
      star_count: item.star_count || 0,
      followLoading: false,
      starLoading: false
    }))
  } catch (error) {
    console.error('获取数据集列表失败:', error)
    ElMessage.error('获取数据集列表失败')
    allDatasets.value = []
  } finally {
    loading.value = false
  }
}

// 本地筛选
const handleLocalFilter = () => {
  // 筛选由 computed 自动完成，页码重置由 watch 处理
}

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  onlyFollowed.value = false
  currentPage.value = 1
  fetchAllDatasets()
}

// 切换点赞状态
const handleToggleStar = async (row) => {
  const originalItem = allDatasets.value.find(d => d.id === row.id)
  if (!originalItem) return
  
  originalItem.starLoading = true
  try {
    if (originalItem.is_starred) {
      const res = await unstarDataset(originalItem.id)
      if (res.data?.code === 200) {
        originalItem.is_starred = false
        originalItem.star_count = res.data.data?.star_count ?? (originalItem.star_count - 1)
        ElMessage.success('已取消点赞')
      }
    } else {
      const res = await starDataset(originalItem.id)
      if (res.data?.code === 201 || res.data?.code === 200) {
        originalItem.is_starred = true
        originalItem.star_count = res.data.data?.star_count ?? (originalItem.star_count + 1)
        ElMessage.success('感谢点赞！')
      }
    }
  } catch (error) {
    if (error.response?.status === 401) ElMessage.warning('请先登录')
    else ElMessage.error('操作失败')
  } finally {
    originalItem.starLoading = false
  }
}

// 切换点赞状态（弹窗中）
const handleToggleStarInDialog = async () => {
  if (!datasetDetail.value) return
  dialogStarLoading.value = true
  try {
    if (datasetDetail.value.is_starred) {
      const res = await unstarDataset(datasetDetail.value.id)
      if (res.data?.code === 200) {
        datasetDetail.value.is_starred = false
        datasetDetail.value.star_count = res.data.data?.star_count ?? (datasetDetail.value.star_count - 1)
        // 同步列表
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
        if (item) {
          item.is_starred = false
          item.star_count = datasetDetail.value.star_count
        }
        ElMessage.success('已取消点赞')
      }
    } else {
      const res = await starDataset(datasetDetail.value.id)
      if (res.data?.code === 201 || res.data?.code === 200) {
        datasetDetail.value.is_starred = true
        datasetDetail.value.star_count = res.data.data?.star_count ?? (datasetDetail.value.star_count + 1)
        // 同步列表
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
        if (item) {
          item.is_starred = true
          item.star_count = datasetDetail.value.star_count
        }
        ElMessage.success('感谢点赞！')
      }
    }
  } catch (error) {
    if (error.response?.status === 401) ElMessage.warning('请先登录')
    else ElMessage.error('操作失败')
  } finally {
    dialogStarLoading.value = false
  }
}

// 切换关注状态（列表中）
const handleToggleFollow = async (row) => {
  // 从原始数组中找到对应的数据集对象
  const originalItem = allDatasets.value.find(d => d.id === row.id)
  if (!originalItem) return
  
  originalItem.followLoading = true
  try {
    if (originalItem.is_followed) {
      // 取消关注
      const res = await unfollowDataset(originalItem.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        originalItem.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      // 添加关注
      const res = await followDataset(originalItem.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        originalItem.is_followed = true
        ElMessage.success('关注成功')
      } else {
        ElMessage.error(res.data?.msg || '关注失败')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    originalItem.followLoading = false
  }
}

// 切换关注状态（弹窗中）
const handleToggleFollowInDialog = async () => {
  if (!datasetDetail.value) return
  
  dialogFollowLoading.value = true
  try {
    if (datasetDetail.value.is_followed) {
      const res = await unfollowDataset(datasetDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 204) {
        datasetDetail.value.is_followed = false
        // 同步更新列表中的状态
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
        if (item) item.is_followed = false
        ElMessage.success('已取消关注')
      } else {
        ElMessage.error(res.data?.msg || '取消关注失败')
      }
    } else {
      const res = await followDataset(datasetDetail.value.id)
      if (res.data?.code === 200 || res.data?.code === 201) {
        datasetDetail.value.is_followed = true
        // 同步更新列表中的状态
        const item = allDatasets.value.find(d => d.id === datasetDetail.value.id)
        if (item) item.is_followed = true
        ElMessage.success('关注成功')
      } else {
        ElMessage.error(res.data?.msg || '关注失败')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    dialogFollowLoading.value = false
  }
}

// 获取数据集条目（分页）
const fetchDatasetEntries = async (page = 1) => {
  if (!currentDataset.value) return
  
  entriesLoading.value = true
  entriesCurrentPage.value = page
  
  try {
    const res = await getDatasetEntries(currentDataset.value.id, {
      page: page,
      page_size: entriesPageSize.value
    })
    
    // 后端返回格式: { code: 200, msg: "查询成功", data: { entries: [...], total: 100, fields: [...] } }
    if (res.data?.code === 200 && res.data.data) {
      const { entries, total, fields } = res.data.data
      datasetEntries.value = entries || []
      entriesTotal.value = total || 0
      // 如果后端返回了字段列表则使用，否则从第一条数据中提取
      if (fields && fields.length > 0) {
        entryFields.value = fields
      } else if (entries && entries.length > 0) {
        entryFields.value = Object.keys(entries[0])
      } else {
        entryFields.value = []
      }
    } else {
      datasetEntries.value = []
      entriesTotal.value = 0
      entryFields.value = []
    }
  } catch (error) {
    console.error('获取数据条目失败:', error)
    // 不显示错误提示，可能是格式不支持
    datasetEntries.value = []
    entriesTotal.value = 0
    entryFields.value = []
  } finally {
    entriesLoading.value = false
  }
}

// 处理条目分页变化
const handleEntriesPageChange = (page) => {
  fetchDatasetEntries(page)
}

// 显示详情
const showDetail = async (row) => {
  currentDataset.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  datasetDetail.value = null
  
  // 重置条目状态
  datasetEntries.value = []
  entryFields.value = []
  entriesTotal.value = 0
  entriesCurrentPage.value = 1
  
  try {
    const res = await getDatasetDetail(row.id)
    // 后端返回格式: { code: 200, msg: "查询成功", data: {...} }
    if (res.data?.code === 200 && res.data.data) {
      datasetDetail.value = {
        ...res.data.data,
        is_followed: row.is_followed, // 从列表中继承关注状态
        is_starred: row.is_starred,
        star_count: row.star_count
      }
    } else {
      datasetDetail.value = row
    }
    
    // 加载数据条目
    fetchDatasetEntries(1)
  } catch (error) {
    console.error('获取数据集详情失败:', error)
    ElMessage.error('获取详情失败')
    datasetDetail.value = row
  } finally {
    detailLoading.value = false
  }
}

// 下载数据集 - 调用 GET /api/datasets/{id}/download/
const handleDownload = async (dataset) => {
  if (!dataset) return
  
  try {
    ElMessage.info('开始下载...')
    const res = await downloadDataset(dataset.id)
    
    // 检查是否返回了错误信息
    if (res.data?.type === 'application/json') {
      const reader = new FileReader()
      reader.onload = () => {
        const errorData = JSON.parse(reader.result)
        ElMessage.error(errorData.msg || '下载失败')
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
    if (error.response?.status === 403) {
      ElMessage.error('无权限下载该数据集')
    } else {
      ElMessage.error('下载失败，请稍后重试')
    }
  }
}

onMounted(() => {
  fetchAllDatasets()
})
</script>

<style scoped>
.dataset-square {
  padding: 24px;
  background: transparent;
  min-height: calc(100vh - 140px);
}

.hero {
  display: flex;
  gap: 18px;
  align-items: stretch;
  margin-bottom: 16px;
}

.hero-left {
  flex: 1;
  background: var(--header-gradient);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 14px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
}

.hero-left::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -40px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(35, 134, 54, 0.15), transparent 70%);
  pointer-events: none;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  background: rgba(35, 134, 54, 0.15);
  border: 1px solid rgba(35, 134, 54, 0.4);
  color: var(--success-color);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  letter-spacing: 1px;
}

.hero-left h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(35, 134, 54, 0.3);
}

.subtitle {
  margin: 4px 0 14px;
  color: var(--text-secondary);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-card {
  background: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 10px 12px;
  transition: border-color 0.2s;
}

.stat-card.type-total {
  border-left: 3px solid var(--text-primary);
}
.stat-card.type-verified {
  border-left: 3px solid var(--success-color);
}
.stat-card.type-star {
  border-left: 3px solid #f56c6c; /* Danger/Red for stars */
}
.stat-card.type-followed {
  border-left: 3px solid #ffc107; /* Gold/Yellow for favorites */
}

.stat-card.type-star:hover { border-color: #f56c6c; background: rgba(245, 108, 108, 0.05); }
.stat-card.type-star .value { color: #f56c6c; }

.stat-card.type-image {
  border-left: 3px solid var(--el-color-primary);
}
.stat-card.type-text {
  border-left: 3px solid var(--el-color-success);
}
.stat-card.type-multi {
  border-left: 3px solid var(--el-color-warning);
}

.stat-card.type-image:hover { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.stat-card.type-text:hover { border-color: var(--el-color-success); background: var(--el-color-success-light-9); }
.stat-card.type-multi:hover { border-color: var(--el-color-warning); background: var(--el-color-warning-light-9); }

.stat-card.type-image .value { color: var(--el-color-primary); }
.stat-card.type-text .value { color: var(--el-color-success); }
.stat-card.type-multi .value { color: var(--el-color-warning); }

.mini-star {
  font-size: 12px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
}

.star-val {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f56c6c !important;
}

.star-btn:hover {
  background-color: #f56c6c22 !important;
}

.detail-header-stats {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.d-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.d-stat .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.d-stat .value {
  font-size: 18px;
  font-weight: 700;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}


.stat-card .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-card .value {
  font-size: 22px;
  font-weight: 700;
  margin: 6px 0 2px;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

.stat-card .hint {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.8;
}

.hero-right {
  width: 320px;
}

.mini-rank {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 14px;
  height: 100%;
}

.mini-title {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.mini-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.mini-item:last-child {
  border-bottom: none;
}

.mini-rank-num {
  font-weight: 700;
  color: var(--success-color);
  font-family: 'Share Tech Mono', monospace;
}

.mini-name {
  font-weight: 600;
  color: var(--text-primary);
}

.mini-tags {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.filter-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-input,
.filter-select {
  width: 260px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: var(--text-secondary);
}

.board-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.board-row {
  display: grid;
  grid-template-columns: 80px 1.3fr 1fr 400px;
  gap: 16px;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 14px 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.board-row:hover {
  transform: translateY(-2px);
  border-color: var(--success-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.board-row.top-row {
  background: linear-gradient(90deg, rgba(35, 134, 54, 0.05) 0%, var(--bg-secondary) 100%);
  border-color: rgba(35, 134, 54, 0.3);
}

.rank span {
  font-size: 20px;
  font-weight: 800;
  color: var(--success-color);
  font-family: 'Share Tech Mono', monospace;
}

.meta .name-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta .name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.meta-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  margin-top: 6px;
  font-size: 13px;
}

.meta-sub .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-color);
  display: inline-block;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 12px;
}

.metric {
  background: var(--bg-body);
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-value {
  margin-top: 6px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-value.on {
  color: var(--success-color);
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 6px;
  padding: 8px 0 4px;
}

/* Pagination Dark Mode Override */
:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--accent-color);
  color: #ffffff;
}

:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.dialog-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  color: var(--text-secondary);
}

.detail-content {
  padding: 10px 0;
}

/* 数据条目区域 */
.entries-section {
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  background: var(--bg-body);
}

.entries-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.entries-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-size: 15px;
}

.entries-total {
  color: var(--text-secondary);
  font-weight: normal;
  font-size: 13px;
}

.entries-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--text-secondary);
}

.entries-container {
  background: var(--bg-secondary);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.entries-pagination {
  display: flex;
  justify-content: center;
  padding: 15px 0 5px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.cell-content {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

/* Table Dark Theme Overrides for Entries */
:deep(.el-table) {
  --el-table-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-secondary);
  --el-table-header-bg-color: var(--bg-body);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  --el-table-row-hover-bg-color: var(--bg-hover);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
}

:deep(.el-table th) {
  background-color: var(--bg-body) !important;
  color: var(--text-secondary) !important;
  border-bottom: 1px solid var(--border-color) !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-color) !important;
}

/* Collapse Dark Overrides */
:deep(.el-collapse) {
  border-color: var(--border-color);
}
:deep(.el-collapse-item__header) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-color: var(--border-color);
}
:deep(.el-collapse-item__content) {
  background-color: var(--bg-body);
  color: var(--text-secondary);
  padding-bottom: 10px;
}
:deep(.el-descriptions__label) {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}
:deep(.el-descriptions__content) {
  background-color: var(--bg-body) !important;
  color: var(--text-primary) !important;
}
:deep(.el-descriptions__cell) {
  border-color: var(--border-color) !important;
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
</style>

