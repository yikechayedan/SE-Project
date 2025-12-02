// src/api/datasets.js
import request from "./request"

/**
 * ========================================
 * 数据集 API - 对接后端实际实现的接口
 * ========================================
 * 
 * 后端返回格式: { code: 200/201, msg: "xxx", data: {...} 或 [...] }
 */

/**
 * 1. 创建数据集 (上传)
 * 接口: POST /api/datasets/
 */
export function createDataset(data) {
  return request.post("/api/datasets/", data)
}

/**
 * 2. 获取数据集列表（带关注状态）
 * 接口: GET /api/datasets/
 * 查询参数: with_follow=true 时返回 is_followed 字段
 */
export function getAllDatasets(params = {}) {
  return request.get("/api/datasets/", { 
    params: { ...params, with_follow: true } 
  })
}

/**
 * 3. 获取数据集详情（带关注状态）
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
    responseType: "blob"
  })
}

/**
 * 8. 审核数据集 (管理员)
 * 接口: POST /api/datasets/{id}/verify/
 */
export function verifyDataset(id, is_verified = true) {
  return request.post("/api/datasets/" + id + "/verify/", { is_verified })
}

// ========== 关注功能 API ==========

/**
 * 9. 关注数据集
 * 接口: POST /api/datasets/{id}/follow/
 */
export function followDataset(id) {
  return request.post("/api/datasets/" + id + "/follow/")
}

/**
 * 10. 取消关注数据集
 * 接口: DELETE /api/datasets/{id}/follow/
 */
export function unfollowDataset(id) {
  return request.delete("/api/datasets/" + id + "/follow/")
}

/**
 * 11. 获取我关注的数据集列表
 * 接口: GET /api/datasets/followed/
 */
export function getFollowedDatasets() {
  return request.get("/api/datasets/followed/")
}
