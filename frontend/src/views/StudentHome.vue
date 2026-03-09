<template>
  <div class="student-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#333333"><Reading /></el-icon>
          <h2>校园智慧学习平台 - 学生端</h2>
        </div>
        <div class="header-right">
          <el-badge :value="notifications" :hidden="notifications === 0" class="item">
            <el-button text class="notification-btn" @click="openNotificationCenter">
              <el-icon :size="24"><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-avatar :size="40" :src="userStore.user?.profile?.avatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username">{{ userStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/student-home">
              <el-icon><HomeFilled /></el-icon>
              <span>我的主页</span>
            </el-menu-item>
            <el-menu-item index="/my-learning">
              <el-icon><Reading /></el-icon>
              <span>我的学习</span>
            </el-menu-item>
            <el-menu-item index="/search-courses">
              <el-icon><Search /></el-icon>
              <span>搜索课程</span>
            </el-menu-item>
            <el-menu-item index="/ai-tutor">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI学习助手</span>
            </el-menu-item>
            <el-menu-item index="/chat">
              <el-icon><ChatLineRound /></el-icon>
              <span>师生沟通</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>个人资料</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main-content">
          <div class="welcome-banner">
            <h1>欢迎回来，{{ userStore.user?.username }} 同学！</h1>
            <p>继续你的学习之旅，探索知识的海洋</p>
          </div>

          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic title="学习时长" :value="stats.studyHours">
                  <template #suffix>小时</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic title="已学课程" :value="stats.coursesCompleted">
                  <template #suffix>门</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic title="学习积分" :value="stats.points" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic title="学习排名" :value="stats.rank">
                  <template #suffix>名</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="content-row">
            <el-col :span="16">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>继续学习</span>
                  </div>
                </template>
                <div class="course-list">
                  <el-empty v-if="!recentCourses.length" description="暂无进行中的课程" />
                  <div v-for="course in recentCourses" :key="course.id" class="course-item">
                    <el-avatar shape="square" :size="80" :src="course.image">{{ course.title }}</el-avatar>
                    <div class="course-info">
                      <h3>{{ course.title }}</h3>
                      <p>{{ course.instructor }}</p>
                      <el-progress :percentage="course.progress" />
                    </div>
                    <el-button type="primary" @click="continueLearning(course)">继续学习</el-button>
                  </div>
                </div>
              </el-card>

              <el-card class="section-card" style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>推荐课程</span>
                  </div>
                </template>
                <div class="recommended-courses">
                  <el-empty v-if="!recommendedCourses.length" description="暂无推荐课程" />
                  <el-row :gutter="20">
                    <el-col :span="12" v-for="course in recommendedCourses" :key="course.id">
                      <el-card class="course-card" shadow="hover">
                        <el-image :src="course.image" fit="cover" style="height: 150px;" />
                        <h4>{{ course.title }}</h4>
                        <p class="course-meta">
                          <el-icon><User /></el-icon> {{ course.instructor }}
                          <el-icon style="margin-left: 10px;"><Clock /></el-icon> {{ course.duration }}小时
                        </p>
                        <div class="course-footer">
                          <el-rate v-model="course.rating" disabled show-score />
                          <el-button type="primary" size="small">开始学习</el-button>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>学习日历</span>
                    <el-badge v-if="pendingQuizzes.length" :value="pendingQuizzes.length" type="danger">
                      <span style="font-size:12px;color:#F56C6C;">未完成Quiz</span>
                    </el-badge>
                  </div>
                </template>
                <el-calendar v-model="calendarValue">
                  <template #date-cell="{ data }">
                    <div class="calendar-cell" @click="handleDateClick(data.day)">
                      <span class="calendar-day" :class="{ 'is-today': data.isSelected }">{{ data.day.split('-')[2] }}</span>
                      <div class="quiz-badges">
                        <el-tooltip
                          v-for="quiz in getQuizzesForDate(data.day)"
                          :key="quiz.id"
                          :content="quiz.title + ' | DDL: ' + formatDateTime(quiz.end_time)"
                          placement="top"
                        >
                          <el-tag size="small" type="danger" class="quiz-tag" @click.stop="goToQuiz(quiz.share_code)">
                            {{ quiz.title.length > 6 ? quiz.title.slice(0, 6) + '…' : quiz.title }}
                          </el-tag>
                        </el-tooltip>
                      </div>
                    </div>
                  </template>
                </el-calendar>
              </el-card>

              <el-card class="section-card" style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>最近动态</span>
                  </div>
                </template>
                <el-timeline>
                  <el-timeline-item 
                    v-for="activity in recentActivities" 
                    :key="activity.id"
                    :timestamp="activity.time"
                  >
                    {{ activity.content }}
                  </el-timeline-item>
                </el-timeline>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>

      <el-drawer v-model="notificationDrawerVisible" title="通知中心" size="420px">
        <el-tabs>
          <el-tab-pane :label="`系统通知 (${pendingQuizzes.length + courseNotifications.length})`" name="system">
            <div v-if="!pendingQuizzes.length && !courseNotifications.length" style="text-align: center; padding: 20px; color: #909399;">
              <el-empty description="暂无新通知" />
            </div>
            <div v-else class="notify-list">
              <!-- 待完成Quiz -->
              <div v-for="quiz in pendingQuizzes" :key="`quiz-${quiz.id}`" class="notify-item">
                <div class="notify-title">
                  <el-tag type="danger" size="small">Quiz</el-tag>
                  {{ quiz.title }}
                </div>
                <div class="notify-meta">截止时间：{{ formatNotifyTime(quiz.end_time) }}</div>
                <el-button size="small" type="primary" text @click="goToQuiz(quiz.share_code)">
                  去完成
                </el-button>
              </div>
              
              <!-- 课程通知 -->
              <div v-for="notice in courseNotifications" :key="`course-${notice.id}`" class="notify-item">
                <div class="notify-title">
                  <el-tag :type="notice.type === 'new_material' ? 'success' : 'info'" size="small">
                    {{ notice.type === 'new_material' ? '新资料' : '课程通知' }}
                  </el-tag>
                  {{ notice.title }}
                </div>
                <div class="notify-meta">{{ formatNotifyTime(notice.created_at) }}</div>
                <el-button size="small" type="primary" text @click="viewCourse(notice.course_id)">
                  查看课程
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="`私信 (${totalUnreadMessages})`" name="messages">
            <div v-if="!unreadConversations.length" style="text-align: center; padding: 20px; color: #909399;">
              <el-empty description="暂无未读私信" />
            </div>
            <div v-else class="notify-list">
              <div v-for="conv in unreadConversations" :key="`msg-${conv.user.id}`" class="notify-item">
                <div class="notify-title">
                  来自 <el-tag type="info" size="small">{{ conv.user.user_type === 'teacher' ? '教师' : '学生' }}</el-tag>
                  {{ conv.user.username }}
                </div>
                <div class="notify-meta">
                  <el-badge :value="conv.unread_count" class="item" style="margin-right: 8px;">
                    <span style="color: #909399;">未读消息</span>
                  </el-badge>
                </div>
                <div class="notify-message" style="margin-bottom: 10px; color: #606266;">{{ conv.last_message }}</div>
                <el-button size="small" type="primary" text @click="goToPrivateChat(conv.user.id)">
                  查看私信
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="聊天室" name="chat">
            <el-alert
              title="学习社区聊天室"
              type="info"
              :closable="false"
              show-icon
              description="进入学习社区聊天室与教师和同学进行实时交流。"
            />
            <el-button type="primary" style="width: 100%; margin-top: 12px;" @click="goToChatRoom">
              进入学习社区聊天室
            </el-button>
          </el-tab-pane>
        </el-tabs>
      </el-drawer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { 
  Reading, HomeFilled, ChatDotRound, ChatLineRound, User, Clock, Search, Bell
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('/student-home')
const calendarValue = ref(new Date())
const notificationDrawerVisible = ref(false)

// 系统通知数据
const pendingQuizzes = ref([])
const courseNotifications = ref([])
const unreadConversations = ref([])

const totalUnreadMessages = computed(() => {
  return unreadConversations.value.reduce((total, conv) => total + (conv.unread_count || 0), 0)
})

const notifications = computed(() => {
  const quizCount = pendingQuizzes.value.length
  const courseCount = courseNotifications.value.length
  const messageCount = unreadConversations.value.reduce((total, conv) => total + (conv.unread_count || 0), 0)
  return quizCount + courseCount + messageCount
})

const stats = ref({
  studyHours: 0,
  coursesCompleted: 0,
  points: 0,
  rank: 0
})

const recentCourses = ref([])
const recommendedCourses = ref([])
const recentActivities = ref([
  { id: 1, time: '2024-02-27 14:00', content: '完成了Vue 3基础课程第一章' },
  { id: 2, time: '2024-02-27 10:30', content: '参与了Python学习讨论' },
  { id: 3, time: '2024-02-26 16:20', content: '获得了"勤奋学习"徽章' },
])

// 按日期索引 Quiz（key: 'YYYY-MM-DD'）
const quizDDLMap = computed(() => {
  const map = {}
  for (const quiz of pendingQuizzes.value) {
    const dateKey = quiz.end_time.slice(0, 10)
    if (!map[dateKey]) map[dateKey] = []
    map[dateKey].push(quiz)
  }
  return map
})

const getQuizzesForDate = (day) => {
  return quizDDLMap.value[day] || []
}

const formatDateTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const formatNotifyTime = (value) => {
  if (!value) return '刚刚'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '刚刚'
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDateClick = (day) => {
  const quizzes = getQuizzesForDate(day)
  if (quizzes.length > 0) {
    ElMessage.info(`${day} 有 ${quizzes.length} 个Quiz待完成`)
  }
}

const goToQuiz = (shareCode) => {
  router.push(`/quiz/${shareCode}`)
}

const openNotificationCenter = () => {
  notificationDrawerVisible.value = true
}

const goToChatRoom = () => {
  notificationDrawerVisible.value = false
  router.push('/chat')
}

const viewCourse = (courseId) => {
  notificationDrawerVisible.value = false
  router.push(`/course/${courseId}`)
}

const goToPrivateChat = (userId) => {
  notificationDrawerVisible.value = false
  router.push('/chat')
  // 使用setTimeout确保页面加载后再设置用户ID
  setTimeout(() => {
    // 这里会在Chat.vue中被处理
  }, 100)
}

const fetchPendingQuizzes = async () => {
  try {
    const res = await api.get('/api/ai/quiz/pending/')
    pendingQuizzes.value = res.data || []
  } catch (e) {
    console.error('获取待完成Quiz失败:', e)
  }
}

const loadCourseNotifications = async () => {
  try {
    // 这里可以调用后端API来获取课程通知
    // 暂时为空，等待后端实现相关端点
    courseNotifications.value = []
  } catch (e) {
    console.error('加载课程通知失败:', e)
    courseNotifications.value = []
  }
}

const loadUnreadMessages = async () => {
  try {
    const res = await api.get('/api/chat/messages/conversations/')
    const allConversations = Array.isArray(res.data) ? res.data : []
    // 只保留有未读消息的对话
    unreadConversations.value = allConversations.filter(conv => conv.unread_count > 0)
  } catch (e) {
    console.error('加载未读消息失败:', e)
    unreadConversations.value = []
  }
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const continueLearning = (course) => {
  router.push(`/course/${course.id}`)
}

onMounted(async () => {
  await Promise.all([
    fetchPendingQuizzes(),
    loadCourseNotifications(),
    loadUnreadMessages()
  ])
})
</script>

<style scoped>
.student-home {
  height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  color: #333333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.notification-btn {
  padding: 0;
}

.username {
  font-weight: 500;
}

.notify-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notify-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.notify-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.notify-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

.notify-message {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  word-break: break-all;
  max-height: 50px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar {
  background: white;
  box-shadow: 2px 0 4px rgba(0,0,0,0.1);
}

.sidebar :deep(.el-menu) {
  background: white;
}

.sidebar :deep(.el-menu-item) {
  background: white !important;
  color: #303133 !important;
}

.sidebar :deep(.el-menu-item:hover) {
  background: #ecf5ff !important;
  color: #409EFF !important;
}

.sidebar :deep(.el-menu-item.is-active) {
  background: #ecf5ff !important;
  color: #409EFF !important;
}

.sidebar :deep(.el-menu-item i) {
  color: #909399 !important;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.welcome-banner h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.welcome-banner p {
  margin: 0;
  opacity: 0.9;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.course-info {
  flex: 1;
}

.course-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.course-info p {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 14px;
}

.recommended-courses {
  margin-top: 10px;
}

.course-card {
  margin-bottom: 15px;
}

.course-card h4 {
  margin: 10px 0 5px 0;
  font-size: 16px;
}

.course-meta {
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 日历 Quiz DDL 样式 */
.calendar-cell {
  min-height: 60px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 2px 4px;
  width: 100%;
  cursor: pointer;
}

.calendar-day {
  font-size: 14px;
  line-height: 1.6;
}

.quiz-badges {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  margin-top: 2px;
}

.quiz-tag {
  cursor: pointer;
  width: 100%;
  font-size: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.quiz-tag:hover {
  opacity: 0.85;
}
</style>
