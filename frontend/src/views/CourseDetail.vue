<template>
  <div class="course-detail">
    <!-- 加载状态 -->
    <div v-if="loading" style="text-align: center; padding: 100px 0;">
      <el-icon class="is-loading" :size="50"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 学生视图：只显示教师信息和课程文件 -->
    <div v-else-if="course && isStudent">
      <el-card class="teacher-info-card">
        <template #header>
          <h2>教师信息</h2>
        </template>
        <div class="teacher-detail">
          <el-avatar :size="80" style="margin-bottom: 20px;">
            {{ instructorName.charAt(0) }}
          </el-avatar>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">
              <strong>{{ instructorName }}</strong>
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ course.instructor?.email || '未设置邮箱' }}
            </el-descriptions-item>
            <el-descriptions-item label="简介">
              {{ instructorTitle }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <el-card class="files-card" style="margin-top: 20px;">
        <template #header>
          <h2>课程文件</h2>
        </template>
        <div class="files-section">
          <el-empty v-if="!courseFiles.length" description="暂无课程文件" />
          <div v-else class="files-list">
            <el-table :data="courseFiles" style="width: 100%">
              <el-table-column prop="file_name" label="文件名" min-width="200">
                <template #default="scope">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-icon :size="20" :color="scope.row.file_type === 'quiz' ? '#E6A23C' : '#333333'">
                      <Link v-if="scope.row.file_type === 'quiz'" />
                      <Document v-else />
                    </el-icon>
                    <span>{{ scope.row.file_name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="file_type_display" label="文件类型" width="120">
                <template #default="scope">
                  <el-tag :type="getFileTypeTag(scope.row.file_type)" size="small">
                    {{ scope.row.file_type_display }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="file_size_display" label="文件大小" width="100">
                <template #default="scope">
                  {{ scope.row.file_type === 'quiz' ? '-' : scope.row.file_size_display }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间" width="180">
                <template #default="scope">
                  {{ formatDateTime(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="scope">
                  <el-button v-if="scope.row.file_type === 'quiz'" type="warning" link @click="downloadFile(scope.row)">
                    <el-icon><Link /></el-icon>
                    开始答题
                  </el-button>
                  <el-button v-else type="primary" link @click="downloadFile(scope.row)">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 教师视图：完整课程信息 -->
    <div v-else-if="course">
      <!-- 课程头部 -->
      <div class="course-header">
      <el-row :gutter="40">
        <el-col :span="16">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/teacher-home' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ course.title }}</el-breadcrumb-item>
          </el-breadcrumb>
          
          <h1>{{ course.title }}</h1>
          
          <div class="meta">
            <span class="rating">
              <el-rate v-model="course.rating" disabled show-score />
              <span>({{ course.reviews_count || 0 }} 评价)</span>
            </span>
            <span>
              <el-icon><User /></el-icon>
              {{ course.students_count || 0 }} 学生
            </span>
            <span>
              <el-icon><Clock /></el-icon>
              {{ courseDuration }}
            </span>
            <el-tag :type="getCategoryType(course.category)">{{ getCategoryLabel(course.category) }}</el-tag>
          </div>

          <div class="instructor-info">
            <el-avatar :size="40">{{ instructorName.charAt(0) }}</el-avatar>
            <div>
              <div class="name">讲师：{{ instructorName }}</div>
              <div class="title">{{ instructorTitle }}</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <el-card class="purchase-card">
            <img :src="courseImage" class="preview-image" />

            <el-button 
              v-if="!isInstructor" 
              type="primary" 
              size="large" 
              style="width: 100%; margin-bottom: 10px"
            >
              申请选课
            </el-button>

            <el-alert
              v-else
              title="您是该课程的讲师"
              type="success"
              :closable="false"
              show-icon
              style="margin-bottom: 10px;"
            />

            <div class="features">
              <div class="feature-item">
                <el-icon><VideoCameraFilled /></el-icon>
                <span>{{ videosCount }} 个视频课程</span>
              </div>
              <div class="feature-item">
                <el-icon><Document /></el-icon>
                <span>{{ resourcesCount }} 个学习资源</span>
              </div>
              <div class="feature-item">
                <el-icon><Timer /></el-icon>
                <span>永久访问</span>
              </div>
              <div class="feature-item">
                <el-icon><ChatDotRound /></el-icon>
                <span>AI导师答疑</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 课程内容tabs -->
    <el-card class="content-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="课程介绍" name="intro">
          <div class="intro-content">
            <div v-if="course.description">
              <p style="white-space: pre-wrap;">{{ course.description }}</p>
            </div>
            <el-empty v-else description="暂无课程介绍" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="课程目录" name="curriculum">
          <div v-if="course.chapters && course.chapters.length > 0">
            <el-collapse v-model="activeChapters">
              <el-collapse-item
                v-for="(chapter, index) in course.chapters"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="chapter-title">
                    <span><strong>第{{ index + 1 }}章</strong> {{ chapter.title }}</span>
                    <span class="chapter-info">{{ chapter.lessons?.length || 0 }} 课时</span>
                  </div>
                </template>
                
                <div class="lessons-list">
                  <div
                    v-for="(lesson, lessonIndex) in chapter.lessons"
                    :key="lessonIndex"
                    class="lesson-item"
                  >
                    <el-icon><VideoPlay /></el-icon>
                    <span class="lesson-title">{{ lesson.title }}</span>
                    <span class="lesson-duration">{{ lesson.duration_minutes }}分钟</span>
                    <el-icon v-if="lesson.is_free" color="#67C23A"><Select /></el-icon>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          <el-empty v-else description="暂无课程目录" />
        </el-tab-pane>

        <el-tab-pane label="学生评价" name="reviews">
          <el-empty description="暂无评价" />
        </el-tab-pane>

        <el-tab-pane label="课程文件" name="files">
          <div class="files-section">
            <el-empty v-if="!courseFiles.length" description="暂无课程文件" />
            <div v-else class="files-list">
              <el-table :data="courseFiles" style="width: 100%">
                <el-table-column prop="file_name" label="文件名" min-width="200">
                  <template #default="scope">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <el-icon :size="20" :color="scope.row.file_type === 'quiz' ? '#E6A23C' : '#333333'">
                        <Link v-if="scope.row.file_type === 'quiz'" />
                        <Document v-else />
                      </el-icon>
                      <span>{{ scope.row.file_name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="file_type_display" label="文件类型" width="120">
                  <template #default="scope">
                    <el-tag :type="getFileTypeTag(scope.row.file_type)" size="small">
                      {{ scope.row.file_type_display }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="file_size_display" label="文件大小" width="100">
                  <template #default="scope">
                    {{ scope.row.file_type === 'quiz' ? '-' : scope.row.file_size_display }}
                  </template>
                </el-table-column>
                <el-table-column prop="uploaded_by_name" label="上传者" width="120" />
                <el-table-column prop="created_at" label="上传时间" width="180">
                  <template #default="scope">
                    {{ formatDateTime(scope.row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" :width="isInstructor ? 180 : 120" fixed="right">
                  <template #default="scope">
                    <el-button v-if="scope.row.file_type === 'quiz'" type="warning" link @click="downloadFile(scope.row)">
                      <el-icon><Link /></el-icon>
                      开始答题
                    </el-button>
                    <el-button v-else type="primary" link @click="downloadFile(scope.row)">
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                    <el-popconfirm
                      v-if="isInstructor"
                      title="确定删除此文件吗？"
                      @confirm="deleteFile(scope.row.id)"
                    >
                      <template #reference>
                        <el-button type="danger" link>
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    </div>

    <!-- 错误状态 -->
    <el-empty v-else description="课程不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import { 
  User, Clock, VideoCameraFilled, Document, Timer, 
  ChatDotRound, VideoPlay, Select, Download, Delete, Loading, Link 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseId = route.params.id

// 如果URL中有tab参数，使用它；否则默认为'intro'
const activeTab = ref(route.query.tab || 'intro')
const activeChapters = ref([0])
const courseFiles = ref([])
const isInstructor = ref(false)
const isStudent = computed(() => userStore.user?.user_type === 'student')
const course = ref(null)
const loading = ref(true)

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

// 计算属性：课程图片
const courseImage = computed(() => {
  if (!course.value) return 'https://via.placeholder.com/400x250/409EFF/FFFFFF?text=Course'
  return course.value.image || 'https://via.placeholder.com/400x250/409EFF/FFFFFF?text=' + encodeURIComponent(course.value.title)
})

// 计算属性：讲师名称
const instructorName = computed(() => {
  if (!course.value?.instructor) return '未知老师'
  return course.value.instructor.username || course.value.instructor.first_name || '老师'
})

// 计算属性：讲师标题
const instructorTitle = computed(() => {
  if (!course.value?.instructor?.profile?.bio) return '课程讲师'
  return course.value.instructor.profile.bio
})

// 计算属性：课程时长
const courseDuration = computed(() => {
  if (!course.value) return '0小时'
  return course.value.duration_hours > 0 ? `${course.value.duration_hours}小时` : '待更新'
})

// 计算属性：视频数量
const videosCount = computed(() => {
  if (!course.value?.chapters) return 0
  return course.value.chapters.reduce((total, chapter) => {
    return total + (chapter.lessons?.length || 0)
  }, 0)
})

// 计算属性：资源数量
const resourcesCount = computed(() => {
  return courseFiles.value.length
})

const getFileTypeTag = (fileType) => {
  const tags = {
    'syllabus': 'danger',
    'material': 'primary',
    'video': 'success',
    'quiz': 'warning',
    'other': 'info'
  }
  return tags[fileType] || 'info'
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadCourseDetails = async () => {
  loading.value = true
  console.log('开始加载课程详情, ID:', courseId)
  try {
    const response = await api.get(`/api/courses/course/${courseId}/`)
    console.log('课程详情加载成功:', response.data)
    course.value = response.data
    // 判断当前用户是否是课程讲师
    isInstructor.value = course.value.instructor?.id === userStore.user?.id
    console.log('是否是讲师:', isInstructor.value)
    // 加载课程文件（CourseDetailSerializer已包含，但为了保持一致性）
    if (course.value.files) {
      courseFiles.value = course.value.files
      console.log('课程文件数量:', courseFiles.value.length)
    }
  } catch (error) {
    console.error('加载课程详情失败:', error)
    ElMessage.error('加载课程信息失败')
  } finally {
    loading.value = false
    console.log('加载完成, loading:', loading.value, 'course:', !!course.value)
  }
}

const loadCourseFiles = async () => {
  try {
    const response = await api.get(`/api/courses/course/${courseId}/files/`)
    courseFiles.value = response.data
  } catch (error) {
    console.error('加载课程文件失败:', error)
  }
}

const downloadFile = (file) => {
  if (file.file_type === 'quiz' && file.quiz_url) {
    // 从quiz_url中提取share_code，使用路由跳转以保持登录状态
    const match = file.quiz_url.match(/\/quiz\/([^/]+)\/?$/)
    if (match) {
      router.push(`/quiz/${match[1]}`)
    } else {
      window.open(file.quiz_url, '_blank')
    }
  } else if (file.file_url) {
    window.open(file.file_url, '_blank')
  } else {
    ElMessage.error('文件链接不可用')
  }
}

const deleteFile = async (fileId) => {
  try {
    await api.delete(`/api/courses/course/${courseId}/delete_file/`, {
      data: { file_id: fileId }
    })
    ElMessage.success('文件删除成功')
    // 重新加载课程详情以更新文件列表
    loadCourseDetails()
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('删除文件失败')
  }
}

onMounted(() => {
  // 根据courseId加载课程详情和文件
  console.log('Loading course:', courseId)
  loadCourseDetails()
})
</script>

<style scoped>
.course-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.teacher-info-card,
.files-card {
  margin-bottom: 20px;
}

.teacher-info-card h2,
.files-card h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.teacher-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.course-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.course-header h1 {
  font-size: 32px;
  margin: 20px 0 10px 0;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 25px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.instructor-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.instructor-info .name {
  font-weight: 500;
  margin-bottom: 4px;
}

.instructor-info .title {
  font-size: 13px;
  opacity: 0.8;
}

.purchase-card {
  position: sticky;
  top: 20px;
}

.preview-image {
  width: 100%;
  border-radius: 4px;
  margin-bottom: 20px;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.current-price {
  font-size: 32px;
  font-weight: bold;
  color: #F56C6C;
}

.original-price {
  font-size: 18px;
  color: #C0C4CC;
  text-decoration: line-through;
}

.features {
  border-top: 1px solid #EBEEF5;
  padding-top: 15px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  color: #606266;
}

.content-card {
  margin-bottom: 20px;
}

.intro-content {
  line-height: 1.8;
  color: #606266;
}

.intro-content h3 {
  color: #303133;
  margin: 20px 0 15px 0;
}

.intro-content ul {
  padding-left: 20px;
}

.intro-content li {
  margin: 8px 0;
}

.chapter-title {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-info {
  color: #909399;
  font-size: 14px;
}

.lessons-list {
  padding: 10px 0;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-bottom: 1px solid #f5f7fa;
  transition: background 0.3s;
}

.lesson-item:hover {
  background: #f5f7fa;
}

.lesson-title {
  flex: 1;
  color: #606266;
}

.lesson-duration {
  color: #909399;
  font-size: 14px;
}

.reviews-section {
  padding: 20px 0;
}

.reviews-summary {
  text-align: center;
  padding: 20px 0;
}

.rating-overview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.rating-score {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
}

.rating-count {
  color: #909399;
  font-size: 14px;
}

.reviews-list {
  max-width: 800px;
  margin: 0 auto;
}

.review-item {
  padding: 20px 0;
  border-bottom: 1px solid #EBEEF5;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.user-info {
  flex: 1;
}

.username {
  font-weight: 500;
  margin-bottom: 5px;
}

.review-date {
  color: #909399;
  font-size: 13px;
}

.review-content {
  color: #606266;
  line-height: 1.6;
  padding-left: 55px;
}
</style>
