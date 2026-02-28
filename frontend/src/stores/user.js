import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const login = async (credentials) => {
    try {
      const response = await api.post('/api/auth/login/', credentials)
      setToken(response.data.token)
      setUser(response.data.user)
      return { success: true }
    } catch (error) {
      console.error('登录错误:', error)
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '登录失败'
      return { success: false, error: errorMsg }
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register/', userData)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('注册错误:', error)
      // 尝试获取详细错误信息
      let errorMsg = '注册失败'
      
      if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
        errorMsg = '网络连接失败，请检查后端服务是否启动（http://localhost:8000）'
      } else if (error.response?.data) {
        const data = error.response.data
        if (typeof data === 'string') {
          errorMsg = data
        } else if (data.error) {
          errorMsg = data.error
        } else if (data.username) {
          errorMsg = `用户名: ${data.username[0]}`
        } else if (data.email) {
          errorMsg = `邮箱: ${data.email[0]}`
        } else if (data.password) {
          errorMsg = `密码: ${data.password[0]}`
        } else {
          errorMsg = data.message || JSON.stringify(data)
        }
      } else if (error.message) {
        errorMsg = error.message
      }
      return { success: false, error: errorMsg }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/api/auth/profile/')
      setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUserProfile,
    setToken,
    setUser
  }
})
