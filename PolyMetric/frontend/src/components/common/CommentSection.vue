<template>
  <el-dialog
    v-model="visible"
    :title="`评论 (${total})`"
    width="600px"
    class="comment-dialog"
    :close-on-click-modal="false"
    destroy-on-close
    append-to-body
  >
    <div class="comment-container" v-loading="loading">
      <!-- 评论列表区域 -->
      <div 
        class="comment-list" 
        v-infinite-scroll="loadMore"
        :infinite-scroll-disabled="disabled"
        :infinite-scroll-immediate="false"
        :infinite-scroll-distance="20"
      >
        <el-empty v-if="comments.length === 0 && !loading" description="暂无评论，快来抢沙发吧~" />
        
        <div v-for="item in comments" :key="item.id" class="comment-item">
          <div class="comment-avatar">
            <UserPopover :userId="item.user?.id" :username="item.user?.username">
              <el-avatar :size="40" :src="item.user?.avatar || defaultAvatar" class="clickable-avatar" />
            </UserPopover>
          </div>
          <div class="comment-content-box">
            <div class="comment-header">
              <UserPopover :userId="item.user?.id" :username="item.user?.username">
                <span class="username">{{ item.user?.username || '未知用户' }}</span>
              </UserPopover>
              <span class="time">{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="comment-text">{{ item.content }}</div>
            <div class="comment-actions">
              <div 
                class="action-item like-btn" 
                :class="{ active: item.is_liked }"
                @click="handleLike(item)"
              >
                <el-icon><component :is="item.is_liked ? 'StarFilled' : 'Star'" /></el-icon>
                <span>{{ item.likes_count || 0 }}</span>
              </div>
              
              <div 
                v-if="item.is_owner" 
                class="action-item delete-btn"
                @click="handleDelete(item)"
              >
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="loadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon> 加载更多...
        </div>
        <div v-if="noMore && comments.length > 0" class="no-more">
          没有更多评论了
        </div>
      </div>

      <!-- 底部输入框 -->
      <div class="comment-input-area">
        <el-input
          v-model="inputContent"
          type="textarea"
          :rows="2"
          placeholder="发一条友善的评论..."
          resize="none"
          maxlength="200"
          show-word-limit
        />
        <el-button 
          type="primary" 
          class="send-btn" 
          :loading="submitting"
          :disabled="!inputContent.trim()"
          @click="handleSubmit"
        >
          发送
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, StarFilled, Delete, Loading } from '@element-plus/icons-vue'
import { getComments, postComment, deleteComment, toggleCommentLike } from '@/api/comments'
import UserPopover from '@/components/common/UserPopover.vue'

// 使用在线占位图作为默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  targetType: {
    type: String,
    required: true // 'model' or 'dataset'
  },
  targetId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const comments = ref([])
const total = ref(0)
const page = ref(1)
const hasNext = ref(true)
const loadingMore = ref(false)
const submitting = ref(false)
const inputContent = ref('')

const disabled = computed(() => loadingMore.value || !hasNext.value)
const noMore = computed(() => !hasNext.value && !loading.value)

// 监听弹窗打开
watch(() => props.modelValue, (val) => {
  if (val) {
    reset()
    fetchComments()
  }
})

const reset = () => {
  comments.value = []
  page.value = 1
  hasNext.value = true
  total.value = 0
  inputContent.value = ''
}

const fetchComments = async () => {
  if (page.value === 1) loading.value = true
  else loadingMore.value = true

  try {
    const res = await getComments({
      target_type: props.targetType,
      target_id: props.targetId,
      page: page.value,
      page_size: 10
    })
    
    // 适配 API 返回结构
    const data = res.data?.data || {}
    const newComments = data.results || []
    
    if (page.value === 1) {
      comments.value = newComments
    } else {
      comments.value = [...comments.value, ...newComments]
    }
    
    total.value = data.total || 0
    // 如果返回了 has_next 字段则使用，否则通过长度判断
    if (typeof data.has_next !== 'undefined') {
      hasNext.value = data.has_next
    } else {
      hasNext.value = newComments.length === 10
    }
    
    if (hasNext.value) {
      page.value++
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  if (!disabled.value) {
    fetchComments()
  }
}

const handleSubmit = async () => {
  if (!inputContent.value.trim()) return
  
  submitting.value = true
  try {
    const res = await postComment({
      target_type: props.targetType,
      target_id: props.targetId,
      content: inputContent.value
    })
    
    if (res.data?.code === 200 || res.data?.code === 201) {
      ElMessage.success('评论发布成功')
      inputContent.value = ''
      // 重新加载列表（或者手动插入到头部）
      // 这里选择简单粗暴地重置列表，确保数据一致性
      reset()
      fetchComments()
    } else {
      ElMessage.error(res.data?.msg || '发布失败')
    }
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('发布失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

const handleDelete = (item) => {
  ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteComment(item.id)
      ElMessage.success('删除成功')
      // 从列表中移除
      const index = comments.value.findIndex(c => c.id === item.id)
      if (index !== -1) {
        comments.value.splice(index, 1)
        total.value = Math.max(0, total.value - 1)
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleLike = async (item) => {
  try {
    const res = await toggleCommentLike(item.id)
    if (res.data?.code === 200) {
      const data = res.data.data
      item.is_liked = data.is_liked
      item.likes_count = data.likes_count
    }
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录后点赞')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.comment-container {
  display: flex;
  flex-direction: column;
  height: 500px; /* 固定高度 */
}

.comment-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.comment-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content-box {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.username {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.clickable-avatar {
  cursor: pointer;
  transition: opacity 0.2s;
}

.clickable-avatar:hover {
  opacity: 0.8;
}

.time {
  font-size: 12px;
  color: var(--text-secondary);
}

.comment-text {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.5;
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-break: break-all;
}

.comment-actions {
  display: flex;
  gap: 16px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s;
}

.action-item:hover {
  color: var(--primary-color);
}

.like-btn.active {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
}

.loading-more, .no-more {
  text-align: center;
  padding: 10px 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.comment-input-area {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.send-btn {
  align-self: flex-end;
  width: 100px;
}

/* 适配暗黑模式 (假设项目有这些变量) */
:deep(.el-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}
:deep(.el-dialog__title) {
  color: var(--text-primary);
}
:deep(.el-dialog__body) {
  padding-top: 10px;
}
:deep(.el-textarea__inner) {
  background-color: var(--bg-body);
  color: var(--text-primary);
  border-color: var(--border-color);
}
:deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
}
</style>
