// src/api/user.js
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
