<template>
  <div class="teacher-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#333333"><Reading /></el-icon>
          <h2>校园智慧学习平台 - 教师端</h2>
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
          <span class="username">{{ userStore.user?.username }} 老师</span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/teacher-home">
              <el-icon><HomeFilled /></el-icon>
              <span>教学主页</span>
            </el-menu-item>
            <el-menu-item index="/my-courses">
              <el-icon><Reading /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
            <el-menu-item index="/create-course">
              <el-icon><Plus /></el-icon>
              <span>创建课程</span>
            </el-menu-item>
            <el-menu-item index="/course-requests">
              <el-icon><Document /></el-icon>
              <span>课程申请</span>
            </el-menu-item>
            <el-menu-item index="/students">
              <el-icon><User /></el-icon>
              <span>学生管理</span>
            </el-menu-item>
            <el-menu-item index="/ai-tutor">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI教学助手</span>
            </el-menu-item>
            <el-menu-item index="/chat">
              <el-icon><ChatLineRound /></el-icon>
              <span>师生沟通</span>
            </el-menu-item>
            <el-menu-item index="/analytics">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据分析</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>个人资料</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main-content">
          <div class="welcome-banner">
            <h1>尊敬的 {{ userStore.user?.username }} 老师，您好！</h1>
            <p>用心教学，传播知识，成就未来</p>
          </div>

          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card primary">
                <el-statistic title="开设课程" :value="stats.totalCourses">
                  <template #suffix>门</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card success">
                <el-statistic title="学生总数" :value="stats.totalStudents">
                  <template #suffix>人</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card warning">
                <el-statistic title="待批改作业" :value="stats.pendingAssignments">
                  <template #suffix>份</template>
                </el-statistic>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card info">
                <el-statistic title="平均评分" :value="stats.avgRating">
                  <template #suffix>/ 5.0</template>
                </el-statistic>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="content-row">
            <el-col :span="16">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>我的课程</span>
                    <el-button type="primary" size="small" @click="$router.push('/create-course')">
                      <el-icon><Plus /></el-icon> 创建新课程
                    </el-button>
                  </div>
                </template>
                <div class="course-list">
                  <el-empty v-if="!myCourses.length" description="暂无课程" />
                  <div v-for="course in myCourses" :key="course.id" class="course-item">
                    <el-avatar shape="square" :size="80" :src="course.image">{{ course.title?.charAt(0) }}</el-avatar>
                    <div class="course-info">
                      <h3>{{ course.title }}</h3>
                      <p>
                        <el-tag size="small" :type="course.category === 'required' ? 'danger' : 'success'">
                          {{ course.category_display }}
                        </el-tag>
                        <span style="margin-left: 10px;">学生: {{ course.students_count || 0 }}人</span>
                        <span style="margin-left: 10px;">评分: {{ course.rating || 0 }}</span>
                      </p>
                      <el-space>
                        <el-button size="small" @click="viewCourse(course)">查看详情</el-button>
                        <el-button size="small" @click="editCourse(course)">编辑课程</el-button>
                        <el-button size="small" type="success" @click="viewStudents(course)">学生列表</el-button>
                      </el-space>
                    </div>
                    <el-tag :type="course.is_published ? 'success' : 'info'" size="large">
                      {{ course.is_published ? '已发布' : '未发布' }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="section-card">
                <template #header>
                  <div class="card-header">
                    <span>快捷操作</span>
                  </div>
                </template>
                <div class="quick-actions">
                  <el-button type="primary" @click="$router.push('/create-course')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><Plus /></el-icon> 创建新课程
                  </el-button>
                  <el-button @click="$router.push('/my-courses')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><Reading /></el-icon> 管理课程
                  </el-button>
                  <el-button @click="$router.push('/students')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><User /></el-icon> 学生管理
                  </el-button>
                  <el-button @click="$router.push('/analytics')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><DataAnalysis /></el-icon> 数据分析
                  </el-button>
                  <el-button @click="$router.push('/chat')" style="width: 100%; margin-bottom: 10px;">
                    <el-icon><ChatLineRound /></el-icon> 师生沟通
                  </el-button>
                </div>
              </el-card>

              <el-card class="section-card" style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>教学日历</span>
                  </div>
                </template>
                <el-calendar v-model="calendarValue" />
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>

      <el-drawer v-model="notificationDrawerVisible" title="通知中心" size="420px">
        <el-tabs>
          <el-tab-pane :label="`待审批 (${pendingRequests.length})`" name="pending">
            <el-empty v-if="!pendingRequests.length" description="暂无待审批申请" />
            <div v-else class="notify-list">
              <div v-for="request in pendingRequests" :key="request.id" class="notify-item">
                <div class="notify-title">{{ request.student?.username }} 申请加入《{{ request.course?.title }}》</div>
                <div class="notify-meta">申请时间：{{ formatNotifyTime(request.created_at) }}</div>
                <div v-if="request.message" class="notify-message">留言：{{ request.message }}</div>
              </div>
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 12px;" @click="goToCourseRequests">
              去审批课程申请
            </el-button>
          </el-tab-pane>

          <el-tab-pane :label="`学生评价 (${recentReviews.length})`" name="reviews">
            <el-empty v-if="!recentReviews.length" description="暂无新的学生评价" />
            <div v-else class="notify-list">
              <div v-for="review in recentReviews" :key="review.notifyId" class="notify-item">
                <div class="notify-title">
                  {{ review.user?.username }} 评价了《{{ review.course_title }}》
                </div>
                <div class="notify-meta">评分：{{ review.rating }}/5 · {{ formatNotifyTime(review.created_at) }}</div>
                <div class="notify-message">{{ review.content }}</div>
                <el-button size="small" text type="primary" @click="viewCourseById(review.course_id)">
                  查看课程
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="沟通" name="chat">
            <el-alert
              title="师生沟通入口"
              type="info"
              :closable="false"
              show-icon
              description="当前系统已支持学习社区聊天室，可与学生实时交流。"
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
  Reading, HomeFilled, ChatDotRound, ChatLineRound, User, 
  Plus, DataAnalysis, Bell, Document
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
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
