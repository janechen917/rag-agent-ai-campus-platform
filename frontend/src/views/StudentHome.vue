<template>
  <div class="student-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#333333"><Reading /></el-icon>
          <h2>{{ t('nav.studentTitle') }}</h2>
        </div>
        <div class="header-right">
          <el-select
            v-model="currentLocale"
            size="small"
            style="width: 110px;"
            @change="handleLocaleChange"
          >
            <el-option value="zh-cn" :label="t('language.zhCn')" />
            <el-option value="zh-tw" :label="t('language.zhTw')" />
            <el-option value="en" :label="t('language.en')" />
          </el-select>
          <el-badge :value="notifications" :hidden="notifications === 0" class="item">
            <el-button text class="notification-btn" @click="openNotificationCenter">
              <el-icon :size="24"><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-avatar :size="40" :src="userStore.user?.profile?.avatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username">{{ userStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">{{ t('common.logout') }}</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/student-home">
              <el-icon><HomeFilled /></el-icon>
              <span>{{ t('nav.studentHome') }}</span>
            </el-menu-item>
            <el-menu-item index="/my-learning">
              <el-icon><Reading /></el-icon>
              <span>{{ t('nav.myLearning') }}</span>
            </el-menu-item>
            <el-menu-item index="/search-courses">
              <el-icon><Search /></el-icon>
              <span>{{ t('nav.searchCourses') }}</span>
            </el-menu-item>
            <el-menu-item index="/ai-tutor">
              <el-icon><ChatDotRound /></el-icon>
              <span>{{ t('nav.aiTutor') }}</span>
            </el-menu-item>
            <el-menu-item index="/ai-colosseum">
              <el-icon><Trophy /></el-icon>
              <span>{{ t('nav.aiColosseum') }}</span>
            </el-menu-item>
            <el-menu-item index="/chat">
              <el-icon><ChatLineRound /></el-icon>
              <span>{{ t('nav.communication') }}</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>{{ t('common.profile') }}</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main-content">
          <div class="welcome-banner">
            <h1>{{ t('student.welcome', { name: userStore.user?.username }) }}</h1>
            <p>{{ t('student.subtitle') }}</p>
          </div>

          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic :title="t('student.stats.studyHours')" :value="stats.studyHours">
                  <template #suffix>{{ t('student.stats.hours') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic :title="t('student.stats.coursesCompleted')" :value="stats.coursesCompleted">
                  <template #suffix>{{ t('student.stats.courses') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic :title="t('student.stats.points')" :value="stats.points" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <el-statistic :title="t('student.stats.rank')" :value="stats.rank">
                  <template #suffix>{{ t('student.stats.rankSuffix') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="content-row">
            <el-col :span="16">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ t('student.sections.continueLearning') }}</span>
                  </div>
                </template>
                <div class="course-list">
                  <el-empty v-if="!recentCourses.length" :description="t('student.sections.noCourses')" />
                  <div v-for="course in recentCourses" :key="course.id" class="course-item">
                    <el-avatar shape="square" :size="80" :src="course.image">{{ course.title }}</el-avatar>
                    <div class="course-info">
                      <h3>{{ course.title }}</h3>
                      <p>{{ course.instructor }}</p>
                      <el-progress :percentage="course.progress" />
                    </div>
                    <el-button type="primary" @click="continueLearning(course)">{{ t('student.buttons.continueLearning') }}</el-button>
                  </div>
                </div>
              </el-card>

              <el-card class="section-card" style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>{{ t('student.sections.recommendedCourses') }}</span>
                  </div>
                </template>
                <div class="recommended-courses">
                  <el-empty v-if="!recommendedCourses.length" :description="t('student.sections.noRecommended')" />
                  <el-row :gutter="20">
                    <el-col :span="12" v-for="course in recommendedCourses" :key="course.id">
                      <el-card class="course-card" shadow="hover">
                        <el-image :src="course.image" fit="cover" style="height: 150px;" />
                        <h4>{{ course.title }}</h4>
                        <p class="course-meta">
                          <el-icon><User /></el-icon> {{ course.instructor }}
                          <el-icon style="margin-left: 10px;"><Clock /></el-icon> {{ course.duration }}{{ t('student.stats.hours') }}
                        </p>
                        <div class="course-footer">
                          <el-rate v-model="course.rating" disabled show-score />
                          <el-button type="primary" size="small">{{ t('student.buttons.startLearning') }}</el-button>
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
                    <span>{{ t('student.sections.studyCalendar') }}</span>
                    <el-badge v-if="pendingQuizzes.length" :value="pendingQuizzes.length" type="danger">
                      <span style="font-size:12px;color:#F56C6C;">{{ t('student.sections.pendingQuizzes') }}</span>
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
                    <span>{{ t('student.sections.recentActivities') }}</span>
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

      <el-drawer v-model="notificationDrawerVisible" :title="t('notification.center')" size="420px">
        <el-tabs>
          <el-tab-pane :label="`${t('notification.systemNotifications')} (${pendingQuizzes.length + courseNotifications.length})`" name="system">
            <div v-if="!pendingQuizzes.length && !courseNotifications.length" style="text-align: center; padding: 20px; color: #909399;">
              <el-empty :description="t('notification.noNotifications')" />
            </div>
            <div v-else class="notify-list">
              <!-- 待完成Quiz -->
              <div v-for="quiz in pendingQuizzes" :key="`quiz-${quiz.id}`" class="notify-item">
                <div class="notify-title">
                  <el-tag type="danger" size="small">Quiz</el-tag>
                  {{ quiz.title }}
                </div>
                <div class="notify-meta">{{ t('notification.deadline') }}{{ formatNotifyTime(quiz.end_time) }}</div>
                <el-button size="small" type="primary" text @click="goToQuiz(quiz.share_code)">
                  {{ t('notification.goComplete') }}
                </el-button>
              </div>
              
              <!-- 课程通知 -->
              <div v-for="notice in courseNotifications" :key="`course-${notice.id}`" class="notify-item">
                <div class="notify-title">
                  <el-tag :type="notice.type === 'new_material' ? 'success' : 'info'" size="small">
                    {{ notice.type === 'new_material' ? t('notification.newMaterial') : t('notification.courseNotification') }}
                  </el-tag>
                  {{ notice.title }}
                </div>
                <div class="notify-meta">{{ formatNotifyTime(notice.created_at) }}</div>
                <el-button size="small" type="primary" text @click="viewCourse(notice.course_id)">
                  {{ t('notification.viewCourse') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="`${t('notification.messages')} (${totalUnreadMessages})`" name="messages">
            <div v-if="!unreadConversations.length" style="text-align: center; padding: 20px; color: #909399;">
              <el-empty :description="t('notification.noMessages')" />
            </div>
            <div v-else class="notify-list">
              <div v-for="conv in unreadConversations" :key="`msg-${conv.user.id}`" class="notify-item">
                <div class="notify-title">
                  {{ t('notification.from') }} <el-tag type="info" size="small">{{ conv.user.user_type === 'teacher' ? t('nav.teacherHome') : t('nav.studentHome') }}</el-tag>
                  {{ conv.user.username }}
                </div>
                <div class="notify-meta">
                  <el-badge :value="conv.unread_count" class="item" style="margin-right: 8px;">
                    <span style="color: #909399;">{{ t('notification.unreadMessages') }}</span>
                  </el-badge>
                </div>
                <div class="notify-message" style="margin-bottom: 10px; color: #606266;">{{ conv.last_message }}</div>
                <el-button size="small" type="primary" text @click="goToPrivateChat(conv.user.id)">
                  {{ t('notification.viewMessage') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="t('notification.chatRoom')" name="chat">
            <el-alert
              :title="t('notification.communityChat')"
              type="info"
              :closable="false"
              show-icon
              :description="t('notification.communityChatDesc')"
            />
            <el-button type="primary" style="width: 100%; margin-top: 12px;" @click="goToChatRoom">
              {{ t('notification.enterChatRoom') }}
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
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { 
  Reading, HomeFilled, ChatDotRound, ChatLineRound, User, Clock, Search, Bell, Trophy
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const { t, locale } = useI18n()

const currentLocale = ref(locale.value)

const handleLocaleChange = (lang) => {
  locale.value = lang
  currentLocale.value = lang
  localStorage.setItem('locale', lang)
}
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
