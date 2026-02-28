<template>
  <div class="ai-tutor">
    <el-card class="chat-container">
      <template #header>
        <div class="header">
          <div class="title">
            <el-icon :size="24"><Cpu /></el-icon>
            <span>AI智能导师</span>
          </div>
          <div class="header-actions">
            <el-button @click="goBack" :icon="Back" circle title="返回" />
            <el-button @click="clearChat" type="danger" :icon="Delete" circle title="清空对话" />
          </div>
        </div>
      </template>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="avatar">
            <el-avatar v-if="message.role === 'user'" :size="40">
              {{ userStore.user?.username?.charAt(0) || 'U' }}
            </el-avatar>
            <el-avatar v-else :size="40" style="background: #409EFF">
              <el-icon><Cpu /></el-icon>
            </el-avatar>
          </div>
          <div class="content">
            <div class="name">{{ message.role === 'user' ? '你' : 'AI导师' }}</div>
            <div class="text" v-html="formatMessage(message.content)"></div>
            <div class="time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message assistant">
          <div class="avatar">
            <el-avatar :size="40" style="background: #409EFF">
              <el-icon><Cpu /></el-icon>
            </el-avatar>
          </div>
          <div class="content">
            <div class="name">AI导师</div>
            <div class="loading-container">
              <div class="loading">
                <span></span><span></span><span></span>
              </div>
              <div class="loading-text">AI正在思考中，请稍候...</div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="suggestions" v-if="messages.length === 0">
          <el-tag
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="sendMessage(suggestion)"
            class="suggestion-tag"
            type="info"
          >
            {{ suggestion }}
          </el-tag>
        </div>
        
        <div class="input-row">
          <el-input
            v-model="inputMessage"
            :placeholder="messages.length === 0 ? '试试问我一个学习问题...' : '输入你的问题...'"
            @keyup.enter="handleSend"
            :disabled="isLoading"
            type="textarea"
            :rows="2"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            @click="handleSend"
            :loading="isLoading"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 侧边栏 - 相关课程推荐 -->
    <el-card class="sidebar">
      <template #header>
        <div class="sidebar-header">
          <el-icon><MagicStick /></el-icon>
          <span>相关课程推荐</span>
        </div>
      </template>
      
      <div v-if="recommendedCourses.length > 0">
        <div
          v-for="course in recommendedCourses"
          :key="course.id"
          class="recommended-course"
          @click="router.push(`/course/${course.id}`)"
        >
          <h4>{{ course.title }}</h4>
          <p>{{ course.description }}</p>
          <el-tag size="small" :type="getCategoryType(course.category)">
            {{ getCategoryLabel(course.category) }}
          </el-tag>
        </div>
      </div>
      <el-empty v-else description="暂无推荐课程" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Delete, Promotion, Cpu, MagicStick, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const recommendedCourses = ref([])

const suggestions = ref([
  'Python中的列表和元组有什么区别？',
  '如何开始学习前端开发？',
  '解释一下Vue 3的Composition API',
  '什么是RESTful API？'
])

const formatMessage = (content) => {
  return marked(content)
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleSend = () => {
  if (!inputMessage.value.trim()) return
  sendMessage(inputMessage.value)
}

const sendMessage = async (message) => {
  const userMessage = {
    role: 'user',
    content: message,
    timestamp: Date.now()
  }
  
  messages.value.push(userMessage)
  inputMessage.value = ''
  isLoading.value = true
  
  scrollToBottom()

  try {
    // 调用AI API
    const response = await api.post('/api/ai/chat/', {
      message: message,
      history: messages.value.slice(-10) // 发送最近10条消息作为上下文
    })

    const aiMessage = {
      role: 'assistant',
      content: response.data.response,
      timestamp: Date.now()
    }
    
    messages.value.push(aiMessage)
    
    // 获取相关课程推荐
    if (response.data.recommended_courses) {
      recommendedCourses.value = response.data.recommended_courses
    }
  } catch (error) {
    console.error('AI chat error:', error)
    
    let errorContent = '抱歉，出现了一些问题。'
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      errorContent = `抱歉，AI思考时间过长导致超时。这可能是因为：
      
- GitHub Models API响应较慢
- 网络连接不稳定

**建议：** 请稍等片刻后重试，或尝试简化您的问题。`
    } else if (error.response) {
      // 服务器返回错误响应
      switch (error.response.status) {
        case 500:
          errorContent = '抱歉，服务器遇到了问题。AI服务可能暂时不可用，请稍后重试。'
          break
        case 401:
          errorContent = '您的登录已过期，请重新登录后再试。'
          break
        default:
          errorContent = `抱歉，服务器返回错误 (${error.response.status})。请稍后重试。`
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorContent = `网络连接出现问题，无法连接到服务器。请检查：

- 网络连接是否正常
- 后端服务是否正在运行
- 防火墙是否阻止了连接`
    }
    
    // 添加错误提示消息
    const errorMessage = {
      role: 'assistant',
      content: errorContent,
      timestamp: Date.now()
    }
    messages.value.push(errorMessage)
    
    ElMessage.warning('AI响应失败，请查看详情')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const clearChat = () => {
  messages.value = []
  recommendedCourses.value = []
  ElMessage.success('对话已清空')
}

const goBack = () => {
  // 根据用户类型返回相应的首页
  const userType = userStore.user?.user_type
  if (userType === 'teacher') {
    router.push('/teacher-home')
  } else {
    router.push('/student-home')
  }
}

const getCategoryType = (category) => {
  const types = {
    'required': 'danger',
    'elective': 'success'
  }
  return types[category] || 'info'
}

const getCategoryLabel = (category) => {
  const labels = {
    'required': '必修',
    'elective': '选修'
  }
  return labels[category] || category
}

onMounted(() => {
  // 加载历史对话（如果需要）
})
</script>

<style scoped>
.ai-tutor {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 180px);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 400px;
  max-height: calc(100vh - 400px);
}

.message {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message .content {
  max-width: 70%;
}

.message.user .content {
  background: #409EFF;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
}

.message.assistant .content {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message .name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.message.user .name {
  color: rgba(255, 255, 255, 0.8);
}

.message .text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message .text :deep(pre) {
  background: #f4f4f4;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.message .text :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.message .time {
  font-size: 11px;
  color: #C0C4CC;
  margin-top: 5px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading {
  display: flex;
  gap: 5px;
  padding: 10px 0;
}

.loading span {
  width: 8px;
  height: 8px;
  background: #409EFF;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #EBEEF5;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-row .el-input {
  flex: 1;
}

.sidebar {
  width: 320px;
  height: 100%;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.recommended-course {
  padding: 15px;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  transition: background 0.3s;
}

.recommended-course:hover {
  background: #f5f7fa;
}

.recommended-course:last-child {
  border-bottom: none;
}

.recommended-course h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.recommended-course p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.5;
}
</style>
