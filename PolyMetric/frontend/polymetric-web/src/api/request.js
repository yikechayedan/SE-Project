// src/api/request.js
import axios from "axios";

const service = axios.create({
  baseURL: "http://127.0.0.1:8000", // 后端 Django 项目地址
  timeout: 5000
});

// 请求拦截器：自动带 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access");
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
          const res = await axios.post("http://127.0.0.1:8000/api/users/token/refresh/", {
            refresh: refresh
          });

          localStorage.setItem("access", res.data.access);
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
