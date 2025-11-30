// src/api/datasets.js
import request from './request'

/**
 * 字段映射：后端字段 → 前端字段
 * 
 * 后端返回格式: { code: 200, msg: "xxx", data: [...] }
 * - creator_username → uploader
 * - file_size: 数字(MB) → 加单位显示
 */
const mapDatasetFields = (item) => ({
  id: item.id,
  name: item.name,
  uploader: item.creator_username,
  category: item.category,
  file_size: item.file_size ? `${item.file_size}MB` : '未知',
  file_format: item.file_format,
  file_url: item.file_url,
  description: item.description,
  is_public: item.is_public,
  is_verified: item.is_verified,
  creator_id: item.creator,
  created_at: item.created_at,
  updated_at: item.updated_at
})

// 获取所有数据集列表
export async function getAllDatasets() {
  const res = await request.get('/api/datasets/')
  // res.data 是 axios 返回的 response.data，即 { code, msg, data }
  // res.data.data 才是真正的数据集数组
  if (res.data && res.data.data) {
    return res.data.data.map(mapDatasetFields)
  }
  return []
}

// 获取数据集详情
export async function getDatasetDetail(id) {
  const res = await request.get(`/api/datasets/${id}/`)
  if (res.data && res.data.data) {
    return mapDatasetFields(res.data.data)
  }
  return null
}

// 获取我的数据集
export async function getMyDatasets() {
  const res = await request.get('/api/datasets/my/')
  if (res.data && res.data.data) {
    return res.data.data.map(mapDatasetFields)
  }
  return []
}

// 创建/上传数据集
export function createDataset(data) {
  return request.post('/api/datasets/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 更新数据集（后端用 PATCH）
export function updateDataset(id, data) {
  return request.patch(`/api/datasets/${id}/`, data)
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
