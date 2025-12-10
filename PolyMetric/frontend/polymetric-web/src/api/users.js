// src/api/users.js
import request from "./request";

// 注册
export function register(data) {
  return request.post("/api/users/register/", data);
}

// 登录
export function login(data) {
  return request.post("/api/users/login/", data);
}

// 获取个人信息
export function getUserInfo() {
  return request.get("/api/users/me/");
}

// 修改个人资料（使用 PATCH 方法）
export function updateUserInfo(data) {
  return request.patch("/api/users/me/", data);
}

// 修改密码
export function changePassword(data) {
  return request.put("/api/users/change_password/", data);
}

// 退出登录
export function logout(refresh) {
  return request.post("/api/users/logout/", { refresh });
}


/**
 * 发送密码重置验证码到邮箱
 * @param {string} email - 用户邮箱
 */
export function sendResetCode(email) {
  return request.post("/api/users/forgot-password/", { email });
}

/**
 * 验证密码重置验证码
 * @param {string} email - 用户邮箱
 * @param {string} code - 验证码
 */
export function verifyResetCode(email, code) {
  return request.post("/api/users/verify-code/", { email, code });
}

/**
 * 重置密码（设置新密码）
 * @param {string} email - 用户邮箱
 * @param {string} code - 验证码
 * @param {string} password - 新密码
 */
export function resetPassword(email, code, password) {
  return request.post("/api/users/reset-password/", { email, code, password });
}

// ========== 头像上传 ==========

export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)
  return request.post('/api/users/avatar/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ========== 关注模型/数据集 API（复用现有接口）==========

/**
 * 获取关注的模型列表
 * @param {number} userId - 可选，不传则获取自己的，传了获取指定用户的
 */
export function getFollowedModels(userId = null) {
  if (userId) {
    return request.get("/api/models/followed/", { params: { user_id: userId } });
  }
  return request.get("/api/models/followed/");
}

/**
 * 获取关注的数据集列表
 * @param {number} userId - 可选，不传则获取自己的，传了获取指定用户的
 */
export function getFollowedDatasets(userId = null) {
  if (userId) {
    return request.get("/api/datasets/followed/", { params: { user_id: userId } });
  }
  return request.get("/api/datasets/followed/");
}

/**
 * 取消关注模型（复用模型模块的 API）
 * @param {number} modelId - 模型ID
 */
export function unfollowModel(modelId) {
  return request.delete(`/api/models/${modelId}/follow/`);
}

/**
 * 取消关注数据集（复用数据集模块的 API）
 * @param {number} datasetId - 数据集ID
 */
export function unfollowDataset(datasetId) {
  return request.delete(`/api/datasets/${datasetId}/follow/`);
}

// ========== 用户关注用户 API ==========

/**
 * 获取其他用户的公开信息
 * @param {number} userId - 用户ID
 */
export function getPublicUserInfo(userId) {
  return request.get(`/api/users/${userId}/public/`);
}

/**
 * 关注用户
 * @param {number} userId - 要关注的用户ID
 */
export function followUser(userId) {
  return request.post(`/api/users/${userId}/follow/`);
}

/**
 * 取消关注用户
 * @param {number} userId - 要取消关注的用户ID
 */
export function unfollowUser(userId) {
  return request.delete(`/api/users/${userId}/follow/`);
}

/**
 * 获取当前用户关注的用户列表
 */
export function getFollowedUsers() {
  return request.get("/api/users/followed/");
}

/**
 * 获取某用户的关注者列表（粉丝）
 * @param {number} userId - 用户ID
 */
export function getUserFollowers(userId) {
  return request.get(`/api/users/${userId}/followers/`);
}

/**
 * 更新用户隐私设置
 * @param {object} settings - 隐私设置 { show_followed_models: boolean, show_followed_datasets: boolean }
 */
export function updatePrivacySettings(settings) {
  return request.put("/api/users/privacy/", settings);
}

// ========== 兼容性别名（复用上面的函数）==========

/**
 * 获取某用户关注的模型（别名，兼容旧调用）
 * @param {number} userId - 用户ID
 */
export function getUserFollowedModels(userId) {
  return getFollowedModels(userId);
}

/**
 * 获取某用户关注的数据集（别名，兼容旧调用）
 * @param {number} userId - 用户ID
 */
export function getUserFollowedDatasets(userId) {
  return getFollowedDatasets(userId);
}
