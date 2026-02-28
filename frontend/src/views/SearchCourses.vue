<template>
  <div class="search-courses">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Search /></el-icon>
          <span>搜索课程</span>
        </div>
      </template>

      <el-input
        v-model="searchQuery"
        placeholder="搜索课程名称或教师名字..."
        size="large"
        clearable
        @keyup.enter="searchCourses"
        @clear="clearSearch"
        @input="handleSearchInput"
      >
        <template #append>
          <el-button :icon="Search" @click="searchCourses" :loading="searching">搜索</el-button>
        </template>
      </el-input>
    </el-card>

    <!-- 所有课程 -->
    <div class="results-section">
      <h3 v-if="searchedOnce && currentCourses.length > 0">搜索结果 ({{ currentCourses.length }} 门课程)</h3>
      <h3 v-else-if="!searchedOnce && currentCourses.length > 0">所有课程 ({{ currentCourses.length }} 门课程)</h3>
      <h3 v-else>未找到课程</h3>
      
      <el-row :gutter="20" v-if="currentCourses.length > 0">
        <el-col :span="8" v-for="course in currentCourses" :key="course.id">
          <el-card class="course-card" shadow="hover">
            <img :src="course.image || '/placeholder-course.png'" class="course-image" />
            
            <div class="course-content">
              <h3>{{ course.title }}</h3>
              <p class="description">{{ course.description }}</p>
              
              <div class="instructor">
                <el-icon><User /></el-icon>
                <span>{{ course.instructor_name }}</span>
              </div>
              
              <div class="meta">
                <el-tag :type="getCategoryType(course.category)" size="small">
                  {{ getCategoryLabel(course.category) }}
                </el-tag>
              </div>
              
              <div class="stats">
                <span>
                  <el-icon><UserFilled /></el-icon>
                  {{ course.students_count }} 学生
                </span>
                <span>
                  <el-icon><Star /></el-icon>
                  {{ course.rating }} 分
                </span>
              </div>

              <el-divider />

              <div class="actions">
                <el-button 
                  v-if="!isEnrolled(course.id)"
                  type="primary" 
                  @click="showRequestDialog(course)"
                  :disabled="hasRequested(course.id)"
                >
                  <span v-if="hasRequested(course.id)">已申请</span>
                  <span v-else>申请加入</span>
                </el-button>
                <el-button @click="viewCourseDetail(course.id)">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 我的申请记录 -->
    <el-card class="requests-card" v-if="myRequests.length > 0">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><Document /></el-icon>
          <span>我的申请记录</span>
        </div>
      </template>

      <el-table :data="myRequests" style="width: 100%">
        <el-table-column prop="course.title" label="课程名称" />
        <el-table-column prop="course.instructor_name" label="教师" width="120" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="getStatusType(scope.row.status)"
              size="small"
            >
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'approved'"
              type="success"
              size="small"
              @click="goToCourse(scope.row.course.id)"
            >
              进入课程
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 申请对话框 -->
    <el-dialog
      v-model="requestDialogVisible"
      title="申请加入课程"
      width="500px"
    >
      <el-form :model="requestForm" label-width="80px">
        <el-form-item label="课程名称">
          <el-input :value="selectedCourse?.title" disabled />
        </el-form-item>
        <el-form-item label="教师">
          <el-input :value="selectedCourse?.instructor_name" disabled />
        </el-form-item>
        <el-form-item label="申请留言">
          <el-input
            v-model="requestForm.message"
            type="textarea"
            :rows="4"
            placeholder="请简要说明您的学习目标和期望..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="requestDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRequest" :loading="submitting">
          提交申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import {
  Search, User, UserFilled, Star, Document
} from '@element-plus/icons-vue'

const router = useRouter()

const searchQuery = ref('')
const searching = ref(false)
const allCourses = ref([])
const searchResults = ref([])
const currentCourses = ref([])  // 当前显示的课程（所有课程或搜索结果）
const searchedOnce = ref(false)  // 是否进行过搜索
const myRequests = ref([])
const myEnrollments = ref([])

const requestDialogVisible = ref(false)
const selectedCourse = ref(null)
const requestForm = ref({
  message: ''
})
const submitting = ref(false)

// 获取所有课程
const loadAllCourses = async () => {
  try {
    const response = await api.get('/api/courses/course/')
    allCourses.value = response.data.results || response.data || []
    currentCourses.value = allCourses.value
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败，请重试')
  }
}

// 搜索课程
const searchCourses = async () => {
  if (!searchQuery.value.trim()) {
    // 如果搜索词为空，显示所有课程
    currentCourses.value = allCourses.value
    searchedOnce.value = false
    return
  }

  searching.value = true
  searchedOnce.value = true
  try {
    const response = await api.get('/api/courses/course/search_courses/', {
      params: { q: searchQuery.value }
    })
    searchResults.value = response.data.results || []
    currentCourses.value = searchResults.value
    
    if (searchResults.value.length === 0) {
      ElMessage.info('未找到相关课程')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    searching.value = false
  }
}

// 清空搜索，显示所有课程
const clearSearch = () => {
  searchQuery.value = ''
  searchedOnce.value = false
  currentCourses.value = allCourses.value
}

// 处理搜索输入变化
const handleSearchInput = (value) => {
  if (!value.trim()) {
    clearSearch()
  }
}

// 获取我的申请记录
const loadMyRequests = async () => {
  try {
    // 先尝试使用正确的路径
    const response = await api.get('/api/courses/course-requests/')
    // API返回分页格式，需要使用results字段
    myRequests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取申请记录失败:', error)
    // 如果API不存在，设置为空数组
    myRequests.value = []
  }
}

// 获取我的选课记录
const loadMyEnrollments = async () => {
  try {
    const response = await api.get('/api/courses/course-enrollments/')
    myEnrollments.value = response.data || []
  } catch (error) {
    console.error('获取选课记录失败:', error)
    // 如果API不存在，设置为空数组
    myEnrollments.value = []
  }
}

// 检查是否已经选课
const isEnrolled = (courseId) => {
  return myEnrollments.value.some(e => e.course.id === courseId)
}

// 检查是否已经申请
const hasRequested = (courseId) => {
  return myRequests.value.some(r => r.course.id === courseId && r.status === 'pending')
}

// 显示申请对话框
const showRequestDialog = (course) => {
  selectedCourse.value = course
  requestForm.value.message = ''
  requestDialogVisible.value = true
}

// 提交申请
const submitRequest = async () => {
  submitting.value = true
  try {
    await api.post('/api/courses/course-requests/', {
      course_id: selectedCourse.value.id,
      message: requestForm.value.message
    })
    
    ElMessage.success('申请已提交，请等待教师审批')
    requestDialogVisible.value = false
    
    // 刷新申请记录
    await loadMyRequests()
  } catch (error) {
    console.error('申请失败:', error)
    ElMessage.error(error.response?.data?.error || error.response?.data?.message || '申请失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 查看课程详情
const viewCourseDetail = (courseId) => {
  router.push(`/course/${courseId}`)
}

// 进入课程
const goToCourse = (courseId) => {
  router.push(`/course/${courseId}`)
}

// 获取课程类型
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

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return types[status] || 'info'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(async () => {
  await Promise.all([
    loadAllCourses(),
    loadMyRequests(),
    loadMyEnrollments()
  ])
})
</script>

<style scoped>
.search-courses {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.results-section {
  margin-top: 30px;
}

.results-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.course-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.course-card:hover {
  transform: translateY(-5px);
}

.course-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 15px;
}

.course-content h3 {
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #303133;
}

.description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.instructor {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #909399;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.actions {
  display: flex;
  gap: 10px;
}

.actions .el-button {
  flex: 1;
}

.requests-card {
  margin-top: 30px;
}
</style>
