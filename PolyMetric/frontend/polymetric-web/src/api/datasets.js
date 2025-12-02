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
 * 请求体: { name, description, category, file_format, is_public }
 */
export function createDataset(data) {
  return request.post("/api/datasets/", data)
}

/**
 * 2. 获取数据集列表
 * 接口: GET /api/datasets/
 */
export function getAllDatasets(params = {}) {
  return request.get("/api/datasets/", { params })
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
 * 注意: 后端 DRF router 自动生成的 URL 是 my_datasets 不是 my
 */
export function getMyDatasets() {
  return request.get("/api/datasets/my_datasets/")
}

/**
 * 7. 下载数据集
 * 接口: GET /api/datasets/{id}/download/
 * 返回: Blob 二进制文件流
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
