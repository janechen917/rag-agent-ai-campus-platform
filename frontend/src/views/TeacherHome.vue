<template>
  <div class="teacher-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#409EFF"><Reading /></el-icon>
          <h2>校园智慧学习平台 - 教师端</h2>
        </div>
        <div class="header-right">
          <el-badge :value="notifications" class="item">
            <el-icon :size="24"><Bell /></el-icon>
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
            <el-menu-item index="/ai-assistant">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI教学助手</span>
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
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
const notifications = ref(5)

const stats = ref({
  totalCourses: 0,
  totalStudents: 0,
  pendingAssignments: 0,
  avgRating: 0
})

const myCourses = ref([])

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
  } catch (error) {
    console.error('获取课程数据失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('只有教师可以访问此功能')
    } else {
      ElMessage.error('获取课程数据失败，请稍后重试')
    }
  }
}

onMounted(() => {
  loadMyCourses()
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
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  font-weight: 500;
}

.sidebar {
  background: white;
  box-shadow: 2px 0 4px rgba(0,0,0,0.1);
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.welcome-banner {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

.stat-card.primary { border-left: 4px solid #409EFF; }
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
</style>
