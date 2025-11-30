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

// 修改个人资料
export function updateUserInfo(data) {
  return request.put("/api/users/me/", data);
}

// 修改密码
export function changePassword(data) {
  return request.put("/api/users/change_password/", data);
}

// 退出登录
export function logout(refresh) {
  return request.post("/api/users/logout/", { refresh });
}

// ========== 忘记密码相关 API ==========

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

// ========== 关注相关 API ==========

/**
 * 获取用户关注的模型列表
 */
export function getFollowedModels() {
  return request.get("/api/users/followed-models/");
}

/**
 * 获取用户关注的数据集列表
 */
export function getFollowedDatasets() {
  return request.get("/api/users/followed-datasets/");
}

/**
 * 取消关注模型
 * @param {number} modelId - 模型ID
 */
export function unfollowModel(modelId) {
  return request.delete(`/api/users/followed-models/${modelId}/`);
}

/**
 * 取消关注数据集
 * @param {number} datasetId - 数据集ID
 */
export function unfollowDataset(datasetId) {
  return request.delete(`/api/users/followed-datasets/${datasetId}/`);
}

// ========== 头像上传 API ==========

/**
 * 上传用户头像
 * @param {File} file - 图片文件对象
 * 
 * 后端接口：POST /api/users/avatar/
 * Content-Type: multipart/form-data
 * 
 * 文件限制:
 * - 最大文件大小: 2MB
 * - 支持格式: jpg, jpeg, png, gif
 * 
 * 响应: { 
 *   "code": 200, 
 *   "msg": "头像上传成功",
 *   "data": { "avatar": "http://127.0.0.1:8000/media/avatars/user_1_xxx.png" }
 * }
 */
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)
  return request.post('/api/users/avatar/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
