<template>
  <div class="teacher-home">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="28" color="#409EFF"><Reading /></el-icon>
          <h2>校园智慧学习平台 - 教师端</h2>
        </div>
        <div class="header-right">
          <el-avatar :size="40" :src="userStore.user?.profile?.avatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username">{{ userStore.user?.username }} 老师</span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu default-active="/analytics" router>
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
          <div class="page-header">
            <h1><el-icon><DataAnalysis /></el-icon> Quiz 数据分析</h1>
            <p>查看所有课程的 Quiz 答题情况与统计分析</p>
          </div>

          <div v-loading="loading">
            <!-- 总览卡片 -->
            <el-row :gutter="20" class="stats-row">
              <el-col :span="6">
                <el-card class="stat-card primary" shadow="hover">
                  <el-statistic title="课程总数" :value="overview.total_courses">
                    <template #suffix>门</template>
                  </el-statistic>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card success" shadow="hover">
                  <el-statistic title="Quiz 总数" :value="overview.total_quizzes">
                    <template #suffix>份</template>
                  </el-statistic>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card warning" shadow="hover">
                  <el-statistic title="提交总数" :value="overview.total_submissions">
                    <template #suffix>次</template>
                  </el-statistic>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card info" shadow="hover">
                  <el-statistic title="总体平均分" :value="overview.overall_avg_score">
                    <template #suffix>分</template>
                  </el-statistic>
                </el-card>
              </el-col>
            </el-row>

            <!-- 无数据提示 -->
            <el-empty v-if="!courses.length && !loading" description="暂无课程或 Quiz 数据" />

            <!-- 按课程展示 -->
            <div v-for="course in courses" :key="course.id" class="course-section">
              <el-card shadow="never" class="course-card">
                <template #header>
                  <div class="course-header">
                    <div class="course-title-area">
                      <el-icon :size="22" color="#409EFF"><Reading /></el-icon>
                      <h2>{{ course.title }}</h2>
                    </div>
                    <div class="course-tags">
                      <el-tag type="primary">{{ course.quiz_count }} 个 Quiz</el-tag>
                      <el-tag type="success">{{ course.total_submissions }} 次提交</el-tag>
                      <el-tag type="warning">平均分 {{ course.average_score }}</el-tag>
                    </div>
                  </div>
                </template>

                <el-empty v-if="!course.quizzes.length" description="该课程暂无 Quiz" :image-size="60" />

                <!-- Quiz 折叠面板 -->
                <el-collapse v-else v-model="activeCollapse[course.id]">
                  <el-collapse-item
                    v-for="quiz in course.quizzes"
                    :key="quiz.id"
                    :name="quiz.id"
                  >
                    <template #title>
                      <div class="quiz-collapse-title">
                        <span class="quiz-name">{{ quiz.title }}</span>
                        <div class="quiz-meta">
                          <el-tag size="small" :type="quiz.is_published ? 'success' : 'info'">
                            {{ quiz.is_published ? '已发布' : '未发布' }}
                          </el-tag>
                          <el-tag size="small" type="primary">{{ quiz.submission_count }} 次提交</el-tag>
                          <el-tag size="small" type="warning">平均 {{ quiz.average_score }} 分</el-tag>
                        </div>
                      </div>
                    </template>

                    <!-- Quiz 详细分析 -->
                    <div class="quiz-detail">
                      <el-row :gutter="20">
                        <!-- 分数分布 -->
                        <el-col :span="12">
                          <el-card shadow="never" class="inner-card">
                            <template #header><span>📊 分数分布</span></template>
                            <div v-if="quiz.submission_count > 0" class="score-distribution">
                              <div
                                v-for="(count, range) in quiz.score_distribution"
                                :key="range"
                                class="score-bar-row"
                              >
                                <span class="score-label">{{ range }}分</span>
                                <el-progress
                                  :percentage="getPercentage(count, quiz.submission_count)"
                                  :color="getScoreColor(range)"
                                  :stroke-width="18"
                                  :format="() => count + '人'"
                                />
                              </div>
                            </div>
                            <el-empty v-else description="暂无提交数据" :image-size="40" />
                          </el-card>
                        </el-col>

                        <!-- 每题正确率 -->
                        <el-col :span="12">
                          <el-card shadow="never" class="inner-card">
                            <template #header><span>📝 每题正确率</span></template>
                            <div v-if="quiz.question_stats.length" class="question-stats">
                              <div
                                v-for="q in quiz.question_stats"
                                :key="q.order"
                                class="question-bar-row"
                              >
                                <el-tooltip :content="q.question_text" placement="top">
                                  <span class="question-label">第{{ q.order }}题</span>
                                </el-tooltip>
                                <el-progress
                                  :percentage="q.correct_rate"
                                  :color="getCorrectRateColor(q.correct_rate)"
                                  :stroke-width="18"
                                  :format="() => q.correct_rate + '%'"
                                />
                              </div>
                            </div>
                            <el-empty v-else description="暂无题目数据" :image-size="40" />
                          </el-card>
                        </el-col>
                      </el-row>

                      <!-- 学生提交记录表 -->
                      <el-card shadow="never" class="inner-card" style="margin-top: 16px;">
                        <template #header><span>👩‍🎓 学生提交记录</span></template>
                        <el-table
                          v-if="quiz.student_records.length"
                          :data="quiz.student_records"
                          stripe
                          size="small"
                          max-height="300"
                        >
                          <el-table-column prop="student_name" label="学生" width="120" />
                          <el-table-column prop="score" label="得分" width="100" sortable>
                            <template #default="{ row }">
                              <el-tag
                                :type="row.score >= 80 ? 'success' : row.score >= 60 ? 'warning' : 'danger'"
                                size="small"
                              >
                                {{ row.score }}分
                              </el-tag>
                            </template>
                          </el-table-column>
                          <el-table-column label="正确率" width="120" sortable :sort-method="(a, b) => (a.correct_count / a.total_questions) - (b.correct_count / b.total_questions)">
                            <template #default="{ row }">
                              {{ row.correct_count }} / {{ row.total_questions }}
                              ({{ Math.round((row.correct_count / row.total_questions) * 100) }}%)
                            </template>
                          </el-table-column>
                          <el-table-column prop="submitted_at" label="提交时间" sortable>
                            <template #default="{ row }">
                              {{ formatTime(row.submitted_at) }}
                            </template>
                          </el-table-column>
                        </el-table>
                        <el-empty v-else description="暂无提交记录" :image-size="40" />
                      </el-card>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </el-card>
            </div>
          </div>
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
  Reading, HomeFilled, Plus, DataAnalysis, User, Document
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const overview = ref({
  total_courses: 0,
  total_quizzes: 0,
  total_submissions: 0,
  overall_avg_score: 0,
})
const courses = ref([])
const activeCollapse = ref({})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const getPercentage = (count, total) => {
  if (!total) return 0
  return Math.round((count / total) * 100)
}

const getScoreColor = (range) => {
  const colors = {
    '0-59': '#F56C6C',
    '60-69': '#E6A23C',
    '70-79': '#409EFF',
    '80-89': '#67C23A',
    '90-100': '#529b2e',
  }
  return colors[range] || '#409EFF'
}

const getCorrectRateColor = (rate) => {
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  return '#F56C6C'
}

const formatTime = (isoStr) => {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  return d.toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/ai/teacher-analytics/')
    overview.value = res.data.overview
    courses.value = res.data.courses
  } catch (error) {
    console.error('加载数据分析失败:', error)
    ElMessage.error('加载数据分析失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalytics()
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
}

.sidebar {
  background: white;
  border-right: 1px solid #e6e8eb;
}

.sidebar .el-menu {
  border-right: none;
}

.main-content {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 22px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 6px 0;
}

.page-header p {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  border-top: 3px solid;
}

.stat-card.primary { border-color: #409EFF; }
.stat-card.success { border-color: #67C23A; }
.stat-card.warning { border-color: #E6A23C; }
.stat-card.info { border-color: #909399; }

.course-section {
  margin-bottom: 20px;
}

.course-card {
  border-radius: 8px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.course-title-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-title-area h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.course-tags {
  display: flex;
  gap: 8px;
}

.quiz-collapse-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 12px;
}

.quiz-name {
  font-weight: 500;
  color: #303133;
}

.quiz-meta {
  display: flex;
  gap: 6px;
}

.quiz-detail {
  padding: 8px 0;
}

.inner-card {
  background: #fafbfc;
}

.score-distribution, .question-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.score-bar-row, .question-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-label {
  width: 60px;
  font-size: 13px;
  color: #606266;
  text-align: right;
  flex-shrink: 0;
}

.question-label {
  width: 55px;
  font-size: 13px;
  color: #606266;
  text-align: right;
  flex-shrink: 0;
  cursor: pointer;
}

.score-bar-row .el-progress,
.question-bar-row .el-progress {
  flex: 1;
}
</style>
