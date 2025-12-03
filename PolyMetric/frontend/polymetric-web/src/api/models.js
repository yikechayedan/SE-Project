import request from './request'

// ==================== 模型列表 ====================

/**
 * 获取所有模型列表（带关注状态）
 * @param {Object} params - 查询参数 { category, search, ordering }
 */
export function getAllModels(params = {}) {
  return request.get("/api/models/", { 
    params: { ...params, with_follow: true } 
  })
}

/**
 * 获取模型详情
 * @param {number} id - 模型ID
 */
export function getModelDetail(id) {
  return request.get("/api/models/" + id + "/")
}

// ==================== 模型关注 ====================

/**
 * 关注模型
 * @param {number} id - 模型ID
 */
export function followModel(id) {
  return request.post("/api/models/" + id + "/follow/")
}

/**
 * 取消关注模型
 * @param {number} id - 模型ID
 */
export function unfollowModel(id) {
  return request.delete("/api/models/" + id + "/follow/")
}

/**
 * 获取用户关注的模型列表
 */
export function getFollowedModels() {
  return request.get("/api/models/followed/")
}
