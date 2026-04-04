import axios from 'axios'
import { ElMessage } from 'element-plus'

// 生产环境使用 VITE_API_BASE_URL 环境变量，开发环境使用 Vite 代理
const getBaseURL = () => {
  if (import.meta.env.PROD) {
    // 生产环境：优先使用环境变量，并去掉尾部/和可能重复的/api
    const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim()
    if (envBase) {
      return envBase.replace(/\/+$/, '').replace(/\/api$/, '')
    }
    // 兜底使用线上后端地址，避免回退到同源 /api 导致 Vercel 重写成静态页
    return 'https://groupprojectteam11back-production.up.railway.app'
  } else {
    // 开发环境：使用 Vite 代理
    return ''
  }
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 300000,  // 300秒，AI Quiz生成需要较长时间
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 防止 baseURL 和 url 同时带 /api，出现 /api/api/xxx
    if (config.baseURL && config.url && /\/api$/.test(config.baseURL) && /^\/api\//.test(config.url)) {
      config.url = config.url.replace(/^\/api/, '')
    }

    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        // 400/403等业务错误由各API调用处自行处理，避免重复toast
        // 仅在没有专门处理的情况下显示通用错误
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
        // default不显示toast，让各API处理器显示具体错误信息
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络后重试')
    } else {
      ElMessage.error('网络错误，请检查您的连接')
    }
    return Promise.reject(error)
  }
)

export default api
