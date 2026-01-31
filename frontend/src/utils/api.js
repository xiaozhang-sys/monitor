/**
 * 统一的API客户端配置
 * 避免各个页面重复创建axios实例和认证逻辑
 */

import axios from 'axios'
import Cookies from 'js-cookie'

// 创建API客户端实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：添加认证token
api.interceptors.request.use(
  (config) => {
    // 从Cookies获取token，避免Pinia store访问问题
    const token = Cookies.get('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401错误由路由守卫统一处理，这里不再显示提示
    if (error.response?.status === 401) {
      console.warn('认证失败，将由系统统一处理')
      return Promise.reject(error)
    }
    
    // 其他错误继续传递
    return Promise.reject(error)
  }
)

export default api