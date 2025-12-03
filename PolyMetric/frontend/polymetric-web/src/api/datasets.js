// src/api/datasets.js
import request from "./request"

/**
 * ========================================
 * 数据集 API - 业界标准实现
 * ========================================
 * 
 * 设计理念：
 * 1. 文件通过 multipart/form-data 上传
 * 2. 后端存储文件到磁盘，数据库只存路径
 * 3. 预览通过动态读取文件实现
 */

/**
 * 1. 创建数据集 (上传)
 * 接口: POST /api/datasets/
 * Content-Type: multipart/form-data
 */
export function createDataset(formData) {
  return request.post("/api/datasets/", formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000
  })
}

/**
 * 2. 获取数据集列表
 * 接口: GET /api/datasets/
 */
export function getAllDatasets(params = {}) {
  return request.get("/api/datasets/", { 
    params: { ...params, with_follow: true } 
  })
}

/**
 * 3. 获取数据集详情
 * 接口: GET /api/datasets/{id}/
 */
export function getDatasetDetail(id) {
  return request.get("/api/datasets/" + id + "/")
}

/**
 * 4. 更新数据集信息
 * 接口: PATCH /api/datasets/{id}/
 */
export function updateDataset(id, data) {
  return request.patch("/api/datasets/" + id + "/", data)
}

/**
 * 5. 删除数据集
 * 接口: DELETE /api/datasets/{id}/
 */
export function deleteDataset(id) {
  return request.delete("/api/datasets/" + id + "/")
}

/**
 * 6. 获取我的数据集
 * 接口: GET /api/datasets/my_datasets/
 */
export function getMyDatasets() {
  return request.get("/api/datasets/my_datasets/")
}

/**
 * 7. 下载数据集
 * 接口: GET /api/datasets/{id}/download/
 */
export function downloadDataset(id) {
  return request.get("/api/datasets/" + id + "/download/", {
    responseType: "blob",
    timeout: 120000
  })
}

/**
 * 8. 预览数据集（业界标准：动态读取文件）
 * 接口: GET /api/datasets/{id}/preview/
 */
export function previewDataset(id, limit = 20) {
  return request.get("/api/datasets/" + id + "/preview/", {
    params: { limit }
  })
}

/**
 * 9. 审核数据集 (管理员)
 * 接口: POST /api/datasets/{id}/verify/
 */
export function verifyDataset(id, is_verified = true) {
  return request.post("/api/datasets/" + id + "/verify/", { is_verified })
}

// ========== 关注功能 API ==========

/**
 * 10. 关注数据集
 * 接口: POST /api/datasets/{id}/follow/
 */
export function followDataset(id) {
  return request.post("/api/datasets/" + id + "/follow/")
}

/**
 * 11. 取消关注数据集
 * 接口: DELETE /api/datasets/{id}/follow/
 */
export function unfollowDataset(id) {
  return request.delete("/api/datasets/" + id + "/follow/")
}

/**
 * 12. 获取我关注的数据集列表
 * 接口: GET /api/datasets/followed/
 */
export function getFollowedDatasets() {
  return request.get("/api/datasets/followed/")
}
