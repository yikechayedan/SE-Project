// src/api/datasets.js
import request from './request'

/**
 * 字段映射：后端字段 → 前端字段
 * 后端 creator → 前端 uploader
 * 后端 sample_count → 前端 item_count
 */
const mapDatasetFields = (item) => ({
  id: item.id,
  name: item.name,
  uploader: item.creator,           // creator → uploader
  category: item.category,
  item_count: item.sample_count,    // sample_count → item_count
  file_size: item.file_size ? `${item.file_size}MB` : '未知',  // 数字 → 字符串带单位
  file_format: item.file_format,
  description: item.description,
  is_public: item.is_public,
  is_verified: item.is_verified,
  created_at: item.created_at,
  updated_at: item.updated_at
})

// 获取所有数据集（带字段映射）
export async function getAllDatasets() {
  const res = await request.get('/api/datasets/')
  if (res.data) {
    res.data = res.data.map(mapDatasetFields)
  }
  return res
}

// 获取数据集详情（带字段映射）
export async function getDatasetDetail(id) {
  const res = await request.get(`/api/datasets/${id}/`)
  if (res.data) {
    res.data = mapDatasetFields(res.data)
  }
  return res
}

// 获取我的数据集
export async function getMyDatasets() {
  const res = await request.get('/api/datasets/my_datasets/')
  if (res.data) {
    res.data = res.data.map(mapDatasetFields)
  }
  return res
}

// 创建/上传数据集
export function createDataset(data) {
  return request.post('/api/datasets/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 更新数据集
export function updateDataset(id, data) {
  return request.put(`/api/datasets/${id}/`, data)
}

// 删除数据集
export function deleteDataset(id) {
  return request.delete(`/api/datasets/${id}/`)
}

// 下载数据集
export function downloadDataset(id) {
  return request.get(`/api/datasets/${id}/download/`, {
    responseType: 'blob'
  })
}
