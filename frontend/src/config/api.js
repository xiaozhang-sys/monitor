import axios from 'axios'

// 读取配置文件中的端口设置
function getApiBaseUrl() {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return '/api'
  }
  
  // 生产环境从配置读取
  const hostname = window.location.hostname
  const backendPort = window.__BACKEND_PORT__ || 8000
  return `http://${hostname}:${backendPort}`
}

function getWebrtcBaseUrl() {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return '/webrtc'
  }
  
  // 生产环境从配置读取
  const hostname = window.location.hostname
  const webrtcPort = window.__WEBRTC_PORT__ || 8090;
  return `http://${hostname}:${webrtcPort}`
}

// API配置
export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  WEBRTC_URL: getWebrtcBaseUrl(),
  TIMEOUT: 10000,
  RETRY_COUNT: 3
}

// 创建axios实例
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api