<template>
  <div class="chat-page">
    <el-card class="chat-container">
      <template #header>
        <div class="header">
          <div class="title">
            <el-icon :size="24"><ChatDotRound /></el-icon>
            <span>学习社区聊天室</span>
          </div>
          <div class="online-count">
            <el-badge :value="onlineUsers" class="item">
              <el-icon :size="20"><User /></el-icon>
            </el-badge>
            <span>在线</span>
          </div>
        </div>
      </template>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message-item', { 'own-message': message.userId === userStore.user?.id }]"
        >
          <div class="message-avatar">
            <el-avatar :size="36">{{ message.username?.charAt(0) || 'U' }}</el-avatar>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="username">{{ message.username }}</span>
              <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="newMessage"
          placeholder="输入消息..."
          @keyup.enter="sendMessage"
          :disabled="!isConnected"
        >
          <template #append>
            <el-button
              :icon="Promotion"
              @click="sendMessage"
              :disabled="!newMessage.trim() || !isConnected"
            />
          </template>
        </el-input>
        <div v-if="!isConnected" class="connection-status">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在连接...</span>
        </div>
      </div>
    </el-card>

    <!-- 在线用户列表 -->
    <el-card class="users-sidebar">
      <template #header>
        <div class="sidebar-header">
          <el-icon><Users /></el-icon>
          <span>在线用户 ({{ onlineUsers }})</span>
        </div>
      </template>
      
      <div class="user-list">
        <div
          v-for="user in onlineUserList"
          :key="user.id"
          class="user-item"
        >
          <el-avatar :size="32">{{ user.username?.charAt(0) }}</el-avatar>
          <span class="username">{{ user.username }}</span>
          <el-tag size="small" type="success">在线</el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { ChatDotRound, User, Users, Promotion, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import websocketService from '@/api/websocket'

const userStore = useUserStore()

const messages = ref([])
const newMessage = ref('')
const messagesContainer = ref(null)
const isConnected = ref(false)
const onlineUsers = ref(0)
const onlineUserList = ref([])

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  } else if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return

  const message = {
    type: 'chat_message',
    content: newMessage.value,
    username: userStore.user?.username,
    userId: userStore.user?.id,
    timestamp: Date.now()
  }

  websocketService.send(message)
  newMessage.value = ''
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'chat_message':
      messages.value.push({
        id: Date.now(),
        content: data.content,
        username: data.username,
        userId: data.userId,
        timestamp: data.timestamp
      })
      scrollToBottom()
      break
    
    case 'user_joined':
      ElMessage.success(`${data.username} 加入了聊天室`)
      onlineUsers.value = data.online_count
      onlineUserList.value = data.online_users || []
      break
    
    case 'user_left':
      ElMessage.info(`${data.username} 离开了聊天室`)
      onlineUsers.value = data.online_count
      onlineUserList.value = data.online_users || []
      break
    
    case 'online_users':
      onlineUsers.value = data.count
      onlineUserList.value = data.users || []
      break
    
    case 'connection_established':
      isConnected.value = true
      ElMessage.success('已连接到聊天室')
      break
  }
}

onMounted(() => {
  // 连接WebSocket
  const token = userStore.token
  if (token) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/chat/'
    websocketService.connect(wsUrl, token)
    websocketService.onMessage(handleWebSocketMessage)
    
    // 检查连接状态
    setTimeout(() => {
      isConnected.value = websocketService.isConnected()
    }, 1000)
  } else {
    ElMessage.error('请先登录')
  }
})

onUnmounted(() => {
  websocketService.removeMessageHandler(handleWebSocketMessage)
  websocketService.disconnect()
})
</script>

<style scoped>
.chat-page {
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

.online-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67C23A;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 400px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: slideIn 0.3s;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message-item.own-message {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 60%;
}

.own-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.own-message .message-header {
  flex-direction: row-reverse;
}

.username {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.timestamp {
  font-size: 11px;
  color: #C0C4CC;
}

.message-text {
  background: white;
  padding: 10px 15px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  line-height: 1.5;
}

.own-message .message-text {
  background: #409EFF;
  color: white;
}

.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #EBEEF5;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  color: #E6A23C;
  font-size: 13px;
}

.users-sidebar {
  width: 280px;
  height: 100%;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-item:hover {
  background: #f5f7fa;
}

.user-item .username {
  flex: 1;
  font-size: 14px;
  color: #303133;
}
</style>
