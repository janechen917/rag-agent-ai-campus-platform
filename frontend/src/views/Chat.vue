<template>
  <div class="chat-page">
    <el-card class="users-sidebar">
      <template #header>
        <div class="sidebar-header">
          <el-icon><UserFilled /></el-icon>
          <span>私信联系人</span>
        </div>
      </template>

      <div class="user-list">
        <div
          v-for="item in contacts"
          :key="item.id"
          :class="['user-item', { active: selectedUserId === item.id }]"
          @click="selectPrivateUser(item)"
        >
          <el-badge :value="item.unread_count || 0" :hidden="!item.unread_count" class="contact-badge">
            <div :class="['avatar-ring', item.user_type === 'teacher' ? 'teacher' : 'student']">
              <el-avatar :size="32">{{ item.username?.charAt(0) }}</el-avatar>
            </div>
          </el-badge>
          <div class="user-content">
            <div class="user-row">
              <span class="username">{{ item.username }}</span>
              <el-tag size="small" type="info">{{ item.user_type === 'teacher' ? '教师' : '学生' }}</el-tag>
            </div>
            <div class="last-msg">{{ item.last_message || '暂无会话' }}</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="chat-container">
      <template #header>
        <div class="header">
          <div class="title">
            <el-icon :size="24"><ChatDotRound /></el-icon>
            <span>学习社区与私信</span>
          </div>
          <div class="online-count">
            <el-badge :value="onlineUsers" class="item">
              <el-icon :size="20"><User /></el-icon>
            </el-badge>
            <span>在线</span>
          </div>
        </div>
        <el-tabs v-model="activeTab" class="tab-switch">
          <el-tab-pane label="公共聊天室" name="public" />
          <el-tab-pane label="私信" name="private" />
        </el-tabs>
      </template>

      <div v-if="activeTab === 'public'" class="course-selector">
        <el-select
          v-model="selectedCourseId"
          placeholder="请选择课程聊天室"
          @change="joinCourseRoom"
          style="width: 100%"
        >
          <el-option
            v-for="course in userCourses"
            :key="course.id"
            :label="course.title"
            :value="course.id"
          />
        </el-select>
      </div>

      <div v-if="activeTab === 'public'" class="chat-messages" ref="publicMessagesContainer">
        <el-empty v-if="!selectedCourseId" description="请先选择一个课程聊天室" />
        <div
          v-for="message in publicMessages"
          :key="`public-${message.id}`"
          :class="['message-item', { 'own-message': message.userId === userStore.user?.id }]"
        >
          <div :class="['message-avatar', 'avatar-ring', publicMessageRole(message)]">
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

      <div v-else class="chat-messages" ref="privateMessagesContainer">
        <el-empty v-if="!selectedUserId" description="请先从左侧选择一个联系人开始私信" />
        <template v-else>
          <div class="private-header">
            当前会话：{{ selectedUser?.username }}
          </div>
          <div
            v-for="message in currentPrivateMessages"
            :key="`private-${message.id}`"
            :class="['message-item', { 'own-message': message.sender?.id === userStore.user?.id }]"
          >
            <div :class="['message-avatar', 'avatar-ring', privateMessageRole(message)]">
              <el-avatar :size="36">{{ message.sender?.username?.charAt(0) || 'U' }}</el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="username">{{ message.sender?.username }}</span>
                <span class="timestamp">{{ formatTime(message.created_at || message.timestamp) }}</span>
              </div>
              <div class="message-text">{{ message.content }}</div>
            </div>
          </div>
        </template>
      </div>

      <div class="input-area">
        <el-input
          v-model="newMessage"
          :placeholder="activeTab === 'public' ? '输入公共消息...' : '输入私信内容...'"
          @keyup.enter="sendMessage"
          :disabled="!isConnected || (activeTab === 'private' && !selectedUserId)"
        >
          <template #append>
            <el-button
              :icon="Promotion"
              @click="sendMessage"
              :disabled="!newMessage.trim() || !isConnected || (activeTab === 'private' && !selectedUserId)"
            />
          </template>
        </el-input>
        <div v-if="!isConnected" class="connection-status">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在连接...</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ChatDotRound, User, UserFilled, Promotion, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import websocketService from '@/api/websocket'
import api from '@/api'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('private')
const newMessage = ref('')
const isConnected = ref(false)
const userCourses = ref([])
const selectedCourseId = ref(null)


const publicMessages = ref([])
const publicMessagesContainer = ref(null)
const privateMessagesContainer = ref(null)

const onlineUsers = ref(0)

const contacts = ref([])
const selectedUserId = ref(null)
const privateMessagesMap = ref({})
const outgoingQueue = ref([])
const messageTimeoutHandles = new Map()

const selectedUser = computed(() => contacts.value.find((u) => u.id === selectedUserId.value) || null)
const currentPrivateMessages = computed(() => privateMessagesMap.value[selectedUserId.value] || [])

const publicMessageRole = (message) => {
  if (message.userType) return message.userType === 'teacher' ? 'teacher' : 'student'
  if (message.userId === userStore.user?.id) return userStore.user?.user_type === 'teacher' ? 'teacher' : 'student'
  return 'student'
}

const privateMessageRole = (message) => {
  const userType = message.sender?.user_type
  if (userType) return userType === 'teacher' ? 'teacher' : 'student'
  if (message.sender?.id === userStore.user?.id) return userStore.user?.user_type === 'teacher' ? 'teacher' : 'student'
  return selectedUser.value?.user_type === 'teacher' ? 'teacher' : 'student'
}

const createClientMessageId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

const pushQueueItem = ({ clientMessageId, target, content }) => {
  outgoingQueue.value.unshift({
    clientMessageId,
    target,
    content,
    status: 'sending',
    createdAt: Date.now()
  })
  outgoingQueue.value = outgoingQueue.value.slice(0, 20)

  const timeoutId = window.setTimeout(() => {
    failQueueItem(clientMessageId, `${target}发送失败，请重试`)
  }, 8000)
  messageTimeoutHandles.set(clientMessageId, timeoutId)
}

const removeQueueItem = (clientMessageId) => {
  const timeoutId = messageTimeoutHandles.get(clientMessageId)
  if (timeoutId) {
    window.clearTimeout(timeoutId)
    messageTimeoutHandles.delete(clientMessageId)
  }

  outgoingQueue.value = outgoingQueue.value.filter((item) => item.clientMessageId !== clientMessageId)
}

const removeTempMessage = (clientMessageId) => {
  publicMessages.value = publicMessages.value.filter(
    (message) => !(message.clientMessageId === clientMessageId && String(message.id).startsWith('temp-'))
  )

  Object.keys(privateMessagesMap.value).forEach((peerId) => {
    privateMessagesMap.value[peerId] = privateMessagesMap.value[peerId].filter(
      (message) => !(message.clientMessageId === clientMessageId && String(message.id).startsWith('temp-'))
    )
  })
}

const markQueueItemSent = (clientMessageId) => {
  removeQueueItem(clientMessageId)
}

const failQueueItem = (clientMessageId, message = '发送失败，请重试') => {
  const queueItem = outgoingQueue.value.find((item) => item.clientMessageId === clientMessageId)
  if (!queueItem) return

  removeQueueItem(clientMessageId)
  removeTempMessage(clientMessageId)
  ElMessage.error(message)
}

const failAllPendingQueueItems = (message = '发送失败，请重试') => {
  const pendingIds = outgoingQueue.value.map((item) => item.clientMessageId)
  pendingIds.forEach((clientMessageId) => {
    removeQueueItem(clientMessageId)
    removeTempMessage(clientMessageId)
  })

  if (pendingIds.length) {
    ElMessage.error(message)
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '刚刚'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    const target = activeTab.value === 'public' ? publicMessagesContainer.value : privateMessagesContainer.value
    if (target) {
      target.scrollTop = target.scrollHeight
    }
  })
}

const updateContactMeta = (peerId, content, unreadDelta = 0) => {
  const idx = contacts.value.findIndex((u) => u.id === peerId)
  if (idx === -1) return

  const target = { ...contacts.value[idx] }
  target.last_message = content
  if (unreadDelta !== 0) {
    target.unread_count = Math.max(0, (target.unread_count || 0) + unreadDelta)
  }

  contacts.value.splice(idx, 1)
  contacts.value.unshift(target)
}

const appendPrivateMessage = (message) => {
  const peer = message.sender?.id === userStore.user?.id ? message.receiver : message.sender
  if (!peer?.id) return

  if (!privateMessagesMap.value[peer.id]) {
    privateMessagesMap.value[peer.id] = []
  }

  privateMessagesMap.value[peer.id].push(message)

  const isIncoming = message.sender?.id !== userStore.user?.id
  const shouldIncreaseUnread = isIncoming && selectedUserId.value !== peer.id
  updateContactMeta(peer.id, message.content, shouldIncreaseUnread ? 1 : 0)

  if (selectedUserId.value === peer.id) {
    scrollToBottom()
  }
}

const markConversationRead = async (peerId) => {
  if (!peerId) return
  try {
    await api.post('/api/chat/messages/mark_conversation_read/', { user_id: peerId })
    const contact = contacts.value.find((u) => u.id === peerId)
    if (contact) contact.unread_count = 0
    websocketService.send({ type: 'mark_private_read', peerId })
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const loadContacts = async () => {
  try {
    const [usersRes, conversationsRes] = await Promise.all([
      api.get('/api/chat/messages/users/'),
      api.get('/api/chat/messages/conversations/')
    ])

    const conversationMap = new Map(
      (conversationsRes.data || []).map((item) => [item.user.id, item])
    )

    const merged = (usersRes.data || []).map((user) => {
      const conv = conversationMap.get(user.id)
      return {
        ...user,
        last_message: conv?.last_message || '',
        last_message_at: conv?.last_message_at || null,
        unread_count: conv?.unread_count || 0,
      }
    })

    merged.sort((a, b) => {
      const at = a.last_message_at ? new Date(a.last_message_at).getTime() : 0
      const bt = b.last_message_at ? new Date(b.last_message_at).getTime() : 0
      return bt - at
    })

    contacts.value = merged
  } catch (error) {
    console.error('加载联系人失败:', error)
    ElMessage.error('加载私信联系人失败')
  }
}

const openConversationFromRoute = async () => {
  const routeUserId = Number(route.query.userId)
  if (!routeUserId) return

  const targetUser = contacts.value.find((user) => user.id === routeUserId)
  if (!targetUser) return

  await selectPrivateUser(targetUser)
}

const selectPrivateUser = async (user) => {
  selectedUserId.value = user.id
  activeTab.value = 'private'

  if (!privateMessagesMap.value[user.id]) {
    try {
      const res = await api.get('/api/chat/messages/conversation/', {
        params: { user_id: user.id }
      })
      privateMessagesMap.value[user.id] = Array.isArray(res.data) ? res.data : []
    } catch (error) {
      console.error('加载会话失败:', error)
      ElMessage.error('加载会话失败')
      privateMessagesMap.value[user.id] = []
    }
  }

  await markConversationRead(user.id)
  scrollToBottom()
}

const sendMessage = () => {
  const content = newMessage.value.trim()
  if (!content) return

  const connected = websocketService.isConnected()
  isConnected.value = connected
  if (!connected) {
    ElMessage.warning('聊天室连接中，请稍后再试')
    return
  }

  // 如果是公共聊天室，检查是否已选择课程
  if (activeTab.value === 'public' && !selectedCourseId.value) {
    ElMessage.warning('请先选择课程聊天室')
    return
  }

  const clientMessageId = createClientMessageId()

  if (activeTab.value === 'public') {
    publicMessages.value.push({
      id: `temp-${clientMessageId}`,
      clientMessageId,
      content,
      username: userStore.user?.username,
      userId: userStore.user?.id,
      userType: userStore.user?.user_type,
      timestamp: new Date().toISOString()
    })

    pushQueueItem({ clientMessageId, target: '公共聊天室', content })
    const sent = websocketService.send({
      type: 'chat_message',
      clientMessageId,
      content,
      username: userStore.user?.username,
      userId: userStore.user?.id,
      timestamp: Date.now()
    })
    if (!sent) failQueueItem(clientMessageId, '公共消息发送失败，请重试')
  } else {
    if (!selectedUserId.value) {
      ElMessage.warning('请先选择私信联系人')
      return
    }

    const peer = selectedUser.value
    if (!privateMessagesMap.value[selectedUserId.value]) {
      privateMessagesMap.value[selectedUserId.value] = []
    }
    privateMessagesMap.value[selectedUserId.value].push({
      id: `temp-${clientMessageId}`,
      clientMessageId,
      content,
      sender: { id: userStore.user?.id, username: userStore.user?.username, user_type: userStore.user?.user_type },
      receiver: { id: selectedUserId.value, username: peer?.username, user_type: peer?.user_type },
      is_read: false,
      created_at: new Date().toISOString()
    })

    pushQueueItem({ clientMessageId, target: `私信 ${peer?.username || ''}`.trim(), content })
    const sent = websocketService.send({
      type: 'private_message',
      clientMessageId,
      receiverId: selectedUserId.value,
      content,
    })
    if (!sent) failQueueItem(clientMessageId, `私信 ${peer?.username || ''} 发送失败，请重试`)
  }

  newMessage.value = ''
  scrollToBottom()
}

const loadUserCourses = async () => {
  try {
    const res = await api.get('/api/chat/messages/user_courses/')
    userCourses.value = res.data || []
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
  }
}

const joinCourseRoom = async () => {
  if (!selectedCourseId.value) return

  publicMessages.value = []

  const joined = websocketService.send({
    type: 'join_course_room',
    courseId: selectedCourseId.value,
  })

  if (!joined) {
    ElMessage.warning('聊天室尚未连接，请稍后重试')
    return
  }

  try {
    const res = await api.get('/api/chat/messages/course_messages/', {
      params: { course_id: selectedCourseId.value },
    })
    publicMessages.value = (res.data || []).map((msg) => ({
      id: msg.id,
      content: msg.content,
      username: msg.sender?.username || '未知用户',
      userId: msg.sender?.id,
      timestamp: msg.created_at,
      userType: msg.sender?.user_type,
      courseId: msg.course || msg.course_id,
    }))
    scrollToBottom()
  } catch (error) {
    console.error('加载课程消息失败:', error)
    ElMessage.error('加载课程消息失败')
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'chat_message':
      if (!selectedCourseId.value || Number(data.courseId) !== Number(selectedCourseId.value)) {
        break
      }

      if (data.clientMessageId) {
        publicMessages.value = publicMessages.value.filter(
          (msg) => !(msg.clientMessageId === data.clientMessageId && String(msg.id).startsWith('temp-'))
        )
        markQueueItemSent(data.clientMessageId)
      }

      publicMessages.value.push({
        id: data.id || Date.now(),
        clientMessageId: data.clientMessageId,
        content: data.content,
        username: data.username,
        userId: data.userId,
        userType: data.userType,
        timestamp: data.timestamp,
        courseId: data.courseId,
      })
      if (activeTab.value === 'public') scrollToBottom()
      break

    case 'joined_course_room':
      break

    case 'left_course_room':
      break

    case 'private_message':
      if (data.clientMessageId) {
        markQueueItemSent(data.clientMessageId)
        const peerId = data.sender?.id === userStore.user?.id ? data.receiver?.id : data.sender?.id
        if (peerId && privateMessagesMap.value[peerId]) {
          privateMessagesMap.value[peerId] = privateMessagesMap.value[peerId].filter(
            (msg) => !(msg.clientMessageId === data.clientMessageId && String(msg.id).startsWith('temp-'))
          )
        }
      }
      appendPrivateMessage({
        id: data.id,
        clientMessageId: data.clientMessageId,
        content: data.content,
        sender: data.sender,
        receiver: data.receiver,
        is_read: data.is_read,
        created_at: data.timestamp,
      })

      if (selectedUserId.value && (data.sender?.id === selectedUserId.value || data.receiver?.id === selectedUserId.value)) {
        markConversationRead(selectedUserId.value)
      }
      break

    case 'private_read':
      if (!data.peerId || !privateMessagesMap.value[data.peerId]) break
      privateMessagesMap.value[data.peerId] = privateMessagesMap.value[data.peerId].map((msg) => {
        if (msg.sender?.id === userStore.user?.id) {
          return { ...msg, is_read: true }
        }
        return msg
      })
      break

    case 'online_users':
      onlineUsers.value = data.count
      break

    case 'connection_established':
      isConnected.value = true
      if (selectedCourseId.value) joinCourseRoom()
      break

    case 'error':
      failAllPendingQueueItems(data.message || '发送失败')
      break

    default:
      break
  }
}

onMounted(async () => {
  const token = userStore.token || localStorage.getItem('token')
  if (!token) {
    ElMessage.error('请先登录')
    router.push('/login')
    return
  }

  // 先校验 token 是否可用，避免 WebSocket 在握手前即被服务端拒绝。
  try {
    await api.get('/api/auth/profile/')
  } catch (error) {
    ElMessage.error('登录状态已失效，请重新登录')
    userStore.logout()
    router.push('/login')
    return
  }

  await Promise.all([loadContacts(), loadUserCourses()])
  await openConversationFromRoute()

  if (userCourses.value.length === 1) {
    selectedCourseId.value = userCourses.value[0].id
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const backendHttpBase = (import.meta.env.VITE_API_BASE_URL || 'https://groupprojectteam11back-production.up.railway.app')
    .trim()
    .replace(/\/+$/, '')
    .replace(/\/api$/, '')
  const backendWsBase = backendHttpBase.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
  const defaultWsUrl = import.meta.env.PROD
    ? `${backendWsBase}/ws/chat/`
    : `${protocol}://${window.location.host}/ws/chat/`
  const wsUrl = import.meta.env.VITE_WS_URL || defaultWsUrl

  websocketService.connect(wsUrl, token)
  websocketService.onMessage(handleWebSocketMessage)

  setTimeout(() => {
    isConnected.value = websocketService.isConnected()
    if (isConnected.value && selectedCourseId.value) {
      joinCourseRoom()
    }
  }, 1000)
})


onUnmounted(() => {
  messageTimeoutHandles.forEach((timeoutId) => window.clearTimeout(timeoutId))
  messageTimeoutHandles.clear()
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

.users-sidebar {
  width: 320px;
  height: 100%;
  background: white;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  background: white;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  cursor: pointer;
  background: white;
  color: #303133;
}

.user-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.user-item.active {
  border-color: #409eff;
  background: #ecf5ff;
  color: #303133;
}

.user-content {
  flex: 1;
  min-width: 0;
}

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.last-msg {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  font-weight: 600;
  font-size: 18px;
}

.online-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
}

.tab-switch {
  margin-top: 10px;
}

.course-selector {
  margin-bottom: 12px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 400px;
}

.private-header {
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.own-message {
  flex-direction: row-reverse;
}

.own-message .message-content {
  text-align: right;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.avatar-ring {
  border: 2px solid transparent;
  border-radius: 50%;
  padding: 2px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.message-avatar.avatar-ring {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  align-self: flex-start;
}

.contact-badge .avatar-ring {
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
}

.avatar-ring.teacher {
  border-color: #e6a23c;
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.22);
}

.avatar-ring.student {
  border-color: #333333;
  box-shadow: 0 0 0 3px rgba(51, 51, 51, 0.15);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.own-message .message-header {
  justify-content: flex-end;
}

.username {
  font-weight: 500;
  color: #303133;
}

.timestamp {
  font-size: 12px;
  color: #909399;
}

.message-text {
  display: inline-block;
  padding: 10px 14px;
  background: #fff;
  border-radius: 12px;
  color: #303133;
  word-break: break-word;
}

.own-message .message-text {
  background: #409EFF;
  color: #fff;
}

.input-area {
  margin-top: 20px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  color: #e6a23c;
  font-size: 13px;
}

.queue-panel {
  margin-top: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px;
  background: #fff;
}

.queue-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 600;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.queue-target {
  color: #909399;
  white-space: nowrap;
}

.queue-content {
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1024px) {
  .chat-page {
    flex-direction: column;
    height: auto;
  }

  .users-sidebar {
    width: 100%;
  }
}
</style>
