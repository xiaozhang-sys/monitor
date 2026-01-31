import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'
import Cookies from 'js-cookie'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)
  const token = ref(Cookies.get('token') || null)

  const login = async (username, password) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      const { access_token } = response.data
      token.value = access_token
      Cookies.set('token', access_token, { expires: 1 })
      
      // 获取用户信息
      await checkAuth()
      
      return { success: true }
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || '登录失败' }
    }
  }

  const logout = () => {
    isAuthenticated.value = false
    user.value = null
    token.value = null
    Cookies.remove('token')
  }

  const checkAuth = async () => {
    if (!token.value) {
      // 没有token，不自动登录，等待用户手动登录
      return false
    }
    
    try {
      // 验证现有token是否有效
      const response = await api.get('/devices')
      isAuthenticated.value = true
      user.value = { role: 'admin' }
      return true
    } catch (error) {
      if (error.response?.status === 401) {
        // token无效，清除认证信息
        logout()
      }
      return false
    }
  }

  // 添加标记，表示已经检查过认证状态
  const hasCheckedAuth = computed(() => {
    return isAuthenticated.value || token.value === null
  })

  return {
    isAuthenticated,
    user,
    token,
    login,
    logout,
    checkAuth,
    hasCheckedAuth
  }
})