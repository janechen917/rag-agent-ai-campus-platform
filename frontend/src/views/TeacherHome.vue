<template>
  <div class="teacher-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#333333"><Reading /></el-icon>
          <h2>{{ t('nav.teacherTitle') }}</h2>
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
          <span class="username">{{ userStore.user?.username }}{{ t('teacher.teacherSuffix') }}</span>
          <el-button type="danger" size="small" @click="handleLogout">{{ t('common.logout') }}</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/teacher-home">
              <el-icon><HomeFilled /></el-icon>
              <span>{{ t('nav.teacherHome') }}</span>
            </el-menu-item>
            <el-menu-item index="/my-courses">
              <el-icon><Reading /></el-icon>
              <span>{{ t('nav.myCourses') }}</span>
            </el-menu-item>
            <el-menu-item index="/create-course">
              <el-icon><Plus /></el-icon>
              <span>{{ t('nav.createCourse') }}</span>
            </el-menu-item>
            <el-menu-item index="/course-requests">
              <el-icon><Document /></el-icon>
              <span>{{ t('nav.courseRequests') }}</span>
            </el-menu-item>
            <el-menu-item index="/students">
              <el-icon><User /></el-icon>
              <span>{{ t('nav.studentManagement') }}</span>
            </el-menu-item>
            <el-menu-item index="/ai-tutor">
              <el-icon><ChatDotRound /></el-icon>
              <span>{{ t('nav.aiTeachingAssistant') }}</span>
            </el-menu-item>
            <el-menu-item index="/chat">
              <el-icon><ChatLineRound /></el-icon>
              <span>{{ t('nav.communication') }}</span>
            </el-menu-item>
            <el-menu-item index="/analytics">
              <el-icon><DataAnalysis /></el-icon>
              <span>{{ t('nav.dataAnalysis') }}</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>{{ t('common.profile') }}</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main-content">
          <div class="welcome-banner">
            <h1>{{ t('teacher.welcome', { name: userStore.user?.username }) }}</h1>
            <p>{{ t('teacher.subtitle') }}</p>
          </div>

          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card primary">
                <el-statistic :title="t('teacher.stats.totalCourses')" :value="stats.totalCourses">
                  <template #suffix>{{ t('teacher.stats.courses') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card success">
                <el-statistic :title="t('teacher.stats.totalStudents')" :value="stats.totalStudents">
                  <template #suffix>{{ t('teacher.stats.students') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card warning">
                <el-statistic :title="t('teacher.stats.pendingAssignments')" :value="stats.pendingAssignments">
                  <template #suffix>{{ t('teacher.stats.assignments') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card info">
                <el-statistic :title="t('teacher.stats.avgRating')" :value="stats.avgRating">
                  <template #suffix>{{ t('teacher.stats.ratingScale') }}</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="content-row">
            <el-col :span="16">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ t('teacher.sections.myCourses') }}</span>
                    <el-button type="primary" size="small" @click="$router.push('/create-course')">
                      <el-icon><Plus /></el-icon> {{ t('teacher.buttons.createCourse') }}
                    </el-button>
                  </div>
                </template>
                <div class="course-list">
                  <el-empty v-if="!myCourses.length" :description="t('teacher.sections.noCourses')" />
                  <div v-for="course in myCourses" :key="course.id" class="course-item">
                    <el-avatar shape="square" :size="80" :src="course.image">{{ course.title?.charAt(0) }}</el-avatar>
                    <div class="course-info">
                      <h3>{{ course.title }}</h3>
                      <p>
                        <el-tag size="small" :type="course.category === 'required' ? 'danger' : 'success'">
                          {{ course.category_display }}
                        </el-tag>
                        <span style="margin-left: 10px;">{{ t('teacher.courseInfo.students') }}: {{ course.students_count || 0 }}{{ t('teacher.courseInfo.studentsUnit') }}</span>
                        <span style="margin-left: 10px;">{{ t('teacher.courseInfo.rating') }}: {{ course.rating || 0 }}</span>
                      </p>
                      <el-space>
                        <el-button size="small" @click="viewCourse(course)">{{ t('teacher.buttons.viewDetail') }}</el-button>
                        <el-button size="small" @click="editCourse(course)">{{ t('teacher.buttons.editCourse') }}</el-button>
                        <el-button size="small" type="success" @click="viewStudents(course)">{{ t('teacher.buttons.studentList') }}</el-button>
                      </el-space>
                    </div>
                    <el-tag :type="course.is_published ? 'success' : 'info'" size="large">
                      {{ course.is_published ? t('teacher.courseStatus.published') : t('teacher.courseStatus.unpublished') }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ t('teacher.sections.quickActions') }}</span>
                  </div>
                </template>
                <div class="quick-actions">
                  <el-button type="primary" @click="$router.push('/create-course')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><Plus /></el-icon> {{ t('teacher.buttons.createCourse') }}
                  </el-button>
                  <el-button @click="$router.push('/my-courses')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><Reading /></el-icon> {{ t('teacher.buttons.manageCourses') }}
                  </el-button>
                  <el-button @click="$router.push('/students')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><User /></el-icon> {{ t('teacher.buttons.studentManagement') }}
                  </el-button>
                  <el-button @click="$router.push('/analytics')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><DataAnalysis /></el-icon> {{ t('teacher.buttons.dataAnalysis') }}
                  </el-button>
                  <el-button @click="$router.push('/chat')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><ChatLineRound /></el-icon> {{ t('teacher.buttons.communication') }}
                  </el-button>
                </div>
              </el-card>

              <el-card class="section-card" style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>{{ t('teacher.sections.teachingCalendar') }}</span>
                  </div>
                </template>
                <el-calendar v-model="calendarValue" />
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>

      <el-drawer v-model="notificationDrawerVisible" :title="t('notification.center')" size="420px">
        <el-tabs>
          <el-tab-pane :label="`${t('notification.pendingApproval')} (${pendingRequests.length})`" name="pending">
            <el-empty v-if="!pendingRequests.length" :description="t('notification.noApprovals')" />
            <div v-else class="notify-list">
              <div v-for="request in pendingRequests" :key="request.id" class="notify-item">
                <div class="notify-title">{{ request.student?.username }} 申请加入《{{ request.course?.title }}》</div>
                <div class="notify-meta">{{ t('notification.applyTime') }}{{ formatNotifyTime(request.created_at) }}</div>
                <div v-if="request.message" class="notify-message">{{ t('notification.message') }}{{ request.message }}</div>
              </div>
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 12px;" @click="goToCourseRequests">
              {{ t('notification.approveRequests') }}
            </el-button>
          </el-tab-pane>

          <el-tab-pane :label="`${t('notification.studentReviews')} (${recentReviews.length})`" name="reviews">
            <el-empty v-if="!recentReviews.length" :description="t('notification.noReviews')" />
            <div v-else class="notify-list">
              <div v-for="review in recentReviews" :key="review.notifyId" class="notify-item">
                <div class="notify-title">
                  {{ review.user?.username }} 评价了《{{ review.course_title }}》
                </div>
                <div class="notify-meta">{{ t('notification.ratingScore') }}{{ review.rating }}{{ t('notification.ratingScale') }} · {{ formatNotifyTime(review.created_at) }}</div>
                <div class="notify-message">{{ review.content }}</div>
                <el-button size="small" text type="primary" @click="viewCourseById(review.course_id)">
                  {{ t('notification.viewCourse') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="t('notification.communication')" name="chat">
            <el-alert
              :title="t('notification.teacherCommunicationTitle')"
              type="info"
              :closable="false"
              show-icon
              :description="t('notification.teacherCommunicationDesc')"
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
  Reading, HomeFilled, ChatDotRound, ChatLineRound, User, 
  Plus, DataAnalysis, Bell, Document
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
const activeMenu = ref('/teacher-home')
const calendarValue = ref(new Date())
const notificationDrawerVisible = ref(false)
const pendingRequests = ref([])
const recentReviews = ref([])

const notifications = computed(() => pendingRequests.value.length + recentReviews.value.length)

const stats = ref({
  totalCourses: 0,
  totalStudents: 0,
  pendingAssignments: 0,
  avgRating: 0
})

const myCourses = ref([])

const openNotificationCenter = () => {
  notificationDrawerVisible.value = true
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

const goToCourseRequests = () => {
  notificationDrawerVisible.value = false
  router.push('/course-requests')
}

const goToChatRoom = () => {
  notificationDrawerVisible.value = false
  router.push('/chat')
}

const viewCourseById = (courseId) => {
  notificationDrawerVisible.value = false
  router.push(`/course/${courseId}`)
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const viewCourse = (course) => {
  router.push(`/course/${course.id}`)
}

const editCourse = (course) => {
  router.push(`/edit-course/${course.id}`)
}

const viewStudents = (course) => {
  router.push(`/course/${course.id}/students`)
}

// 加载教师课程数据
const loadMyCourses = async () => {
  try {
    const response = await api.get('/api/courses/course/my_courses/')
    myCourses.value = response.data
    stats.value.totalCourses = response.data.length
    // 计算总学生数
    stats.value.totalStudents = response.data.reduce((total, course) => {
      return total + (course.students_count || 0)
    }, 0)
    return response.data
  } catch (error) {
    console.error('获取课程数据失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('只有教师可以访问此功能')
    } else {
      ElMessage.error('获取课程数据失败，请稍后重试')
    }
    return []
  }
}

const loadNotifications = async (teacherCourses) => {
  // 加载待审批申请
  try {
    const pendingRes = await api.get('/api/courses/course-requests/pending/')
    pendingRequests.value = Array.isArray(pendingRes.data) ? pendingRes.data.slice(0, 10) : []
  } catch (error) {
    console.error('加载待审批申请失败:', error)
    pendingRequests.value = []
  }

  // 加载学生评价
  try {
    const courseIds = (teacherCourses || []).map((course) => course.id)
    if (!courseIds.length) {
      recentReviews.value = []
      return
    }

    const reviewTasks = courseIds.map((courseId) =>
      api
        .get(`/api/courses/course/${courseId}/reviews/`)
        .then((res) => ({ courseId, reviews: Array.isArray(res.data) ? res.data : [] }))
        .catch(() => ({ courseId, reviews: [] }))
    )

    const reviewResults = await Promise.all(reviewTasks)
    const courseNameMap = new Map((teacherCourses || []).map((course) => [course.id, course.title]))

    const mergedReviews = reviewResults
      .flatMap(({ courseId, reviews }) =>
        reviews.map((review) => ({
          ...review,
          course_id: courseId,
          course_title: courseNameMap.get(courseId) || '课程',
          notifyId: `${courseId}-${review.id}`
        }))
      )
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

    recentReviews.value = mergedReviews.slice(0, 10)
  } catch (error) {
    console.error('加载学生评价失败:', error)
    recentReviews.value = []
  }
}

onMounted(async () => {
  const courses = await loadMyCourses()
  await loadNotifications(courses)
})
</script>

<style scoped>
.teacher-home {
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
  padding: 24px 30px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.welcome-banner h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.welcome-banner p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  opacity: 1;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card.primary { border-left: 4px solid #333333; }
.stat-card.success { border-left: 4px solid #67C23A; }
.stat-card.warning { border-left: 4px solid #E6A23C; }
.stat-card.info { border-left: 4px solid #909399; }

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
  margin: 0 0 8px 0;
  font-size: 16px;
}

.course-info p {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
}

.notify-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notify-item {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.notify-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.notify-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.notify-message {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
</style>
