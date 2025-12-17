// src/api/request.js
import axios from "axios";

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1", // 后端 Django 项目地址
  timeout: 5000
});

// 请求拦截器：自动带 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = "Bearer " + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 401 自动刷新 token
service.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Token 已过期 → 用 refresh 刷新
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh = localStorage.getItem("refresh");
      if (refresh) {
        try {
          const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1";
          const res = await axios.post(`${baseURL}/api/users/token/refresh/`, {
            refresh: refresh
          });

          localStorage.setItem("token", res.data.access);
          originalRequest.headers["Authorization"] = "Bearer " + res.data.access;

          return service(originalRequest);
        } catch (e) {
          console.error("刷新 token 失败");
        }
      }
    }

    return Promise.reject(error);
  }
);

export default service;
