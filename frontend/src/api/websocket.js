class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.messageHandlers = []
    this.isConnecting = false
    this.connectionUrl = null
    this.connectionToken = null
    this.shouldReconnect = true
  }

  connect(url, token) {
    const hasActiveConnection = this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)
    const sameConnection = hasActiveConnection && this.connectionUrl === url && this.connectionToken === token

    if (sameConnection) {
      console.log('WebSocket已连接或正在连接')
      return
    }

    if (hasActiveConnection) {
      console.log('检测到登录身份变化，重建WebSocket连接')
      this.shouldReconnect = false
      this.ws.close()
      this.ws = null
    }

    this.isConnecting = true
    this.shouldReconnect = true
    this.reconnectAttempts = 0
    this.connectionUrl = url
    this.connectionToken = token
    const wsUrl = `${url}?token=${token}`
    
    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket连接成功')
        this.reconnectAttempts = 0
        this.isConnecting = false
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.messageHandlers.forEach(handler => handler(data))
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.isConnecting = false
      }

      this.ws.onclose = () => {
        console.log('WebSocket连接关闭')
        this.isConnecting = false
        if (this.shouldReconnect) {
          this.attemptReconnect(url, token)
        }
      }
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
      this.isConnecting = false
    }
  }

  attemptReconnect(url, token) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(url, token)
      }, this.reconnectDelay)
    } else {
      console.error('WebSocket重连次数已达上限')
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
      return true
    } else {
      console.error('WebSocket未连接')
      return false
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler)
  }

  removeMessageHandler(handler) {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
  }

  disconnect() {
    this.reconnectAttempts = this.maxReconnectAttempts // 防止自动重连
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.connectionUrl = null
    this.connectionToken = null
    this.isConnecting = false
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

export default new WebSocketService()
