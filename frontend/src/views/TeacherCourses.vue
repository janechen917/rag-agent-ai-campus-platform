<template>
  <div class="teacher-courses">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>我的课程</h2>
          <p>管理您创建的所有课程</p>
        </div>
        <el-button type="primary" size="large" :icon="Plus" @click="$router.push('/create-course')">
          创建新课程
        </el-button>
      </div>
    </el-card>

    <!-- 课程统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="课程总数" :value="myCourses.length">
            <template #suffix>门</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="已发布" :value="publishedCount">
            <template #suffix>门</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="学生总数" :value="totalStudents">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="平均评分" :value="averageRating" :precision="1">
            <template #suffix>分</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 课程列表 -->
    <el-card class="courses-card">
      <el-empty v-if="loading" description="加载中..." />
      <el-empty v-else-if="myCourses.length === 0" description="暂无课程">
        <el-button type="primary" @click="$router.push('/create-course')">创建第一门课程</el-button>
      </el-empty>
      <div v-else class="courses-grid">
        <el-card 
          v-for="course in myCourses" 
          :key="course.id" 
          class="course-card"
          shadow="hover"
        >
          <div class="course-image-wrapper">
            <img 
              :src="course.image || 'https://via.placeholder.com/400x200/409EFF/FFFFFF?text=Course'" 
              class="course-image" 
            />
            <el-tag 
              :type="course.is_published ? 'success' : 'info'" 
              class="publish-tag"
            >
              {{ course.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </div>

          <div class="course-content">
            <h3>{{ course.title }}</h3>
            <p class="description">{{ course.description }}</p>

            <div class="course-meta">
              <el-tag size="small" :type="course.category === 'required' ? 'danger' : 'success'">
                {{ course.category_display }}
              </el-tag>
              <span class="meta-item">
                <el-icon><User /></el-icon>
                {{ course.students_count || 0 }}人
              </span>
              <span class="meta-item" v-if="course.pendingRequests > 0">
                <el-badge :value="course.pendingRequests" :max="99" type="warning">
                  <el-icon><Message /></el-icon>
                  待审批
                </el-badge>
              </span>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ course.duration_hours || 0 }}小时
              </span>
              <span class="meta-item">
                <el-icon><Star /></el-icon>
                {{ course.rating || 0 }}分
              </span>
            </div>

            <!-- 课程文件 -->
            <el-divider />
            <div class="files-section">
              <div class="section-title">
                <el-icon><Folder /></el-icon>
                <span>课程文件</span>
                <el-button 
                  size="small" 
                  type="primary" 
                  link 
                  @click="showUploadDialog(course)"
                  style="margin-left: auto;"
                >
                  <el-icon><Upload /></el-icon>
                  上传文件
                </el-button>
              </div>
              
              <div class="file-list">
                <el-empty 
                  v-if="!course.files || course.files.length === 0" 
                  description="暂无文件" 
                  :image-size="60"
                />
                <div v-else class="files-grid">
                  <div 
                    v-for="file in course.files" 
                    :key="file.id" 
                    class="file-card"
                  >
                    <div class="file-icon">
                      <el-icon :size="24" :color="file.file_type === 'quiz' ? '#E6A23C' : ''">
                        <Link v-if="file.file_type === 'quiz'" />
                        <Document v-else />
                      </el-icon>
                    </div>
                    <div class="file-info">
                      <div class="file-name" :title="file.file_name">{{ file.file_name }}</div>
                      <div class="file-meta">
                        <el-tag :type="getFileTypeTag(file.file_type)" size="small">
                          {{ file.file_type_display }}
                        </el-tag>
                        <span v-if="file.file_type !== 'quiz'" class="file-size">{{ file.file_size_display }}</span>
                      </div>
                      <div class="file-time">{{ formatTime(file.created_at) }}</div>
                    </div>
                    <div class="file-actions">
                      <el-button size="small" type="primary" link @click="downloadFile(file)">
                        <el-icon><Download /></el-icon>
                      </el-button>
                      <el-popconfirm
                        title="确定删除此文件吗？"
                        @confirm="deleteFile(course.id, file.id)"
                      >
                        <template #reference>
                          <el-button size="small" type="danger" link>
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </template>
                      </el-popconfirm>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <el-divider />

            <!-- 操作按钮 -->
            <div class="course-actions">
              <el-button size="small" @click="viewCourse(course.id)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button size="small" type="primary" @click="editCourse(course.id)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="success" @click="viewStudents(course.id)">
                <el-icon><User /></el-icon>
                学生
              </el-button>
              <el-button 
                size="small" 
                :type="course.is_published ? 'warning' : 'info'"
                @click="togglePublish(course)"
              >
                {{ course.is_published ? '取消发布' : '发布' }}
              </el-button>
              <el-popconfirm
                title="确定删除此课程吗？"
                @confirm="deleteCourse(course.id)"
              >
                <template #reference>
                  <el-button size="small" type="danger">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 文件上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传课程文件"
      width="600px"
    >
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文件类型">
          <el-select v-model="uploadForm.file_type" style="width: 100%">
            <el-option label="课程大纲" value="syllabus" />
            <el-option label="课程资料" value="material" />
            <el-option label="视频资料" value="video" />
            <el-option label="Quiz" value="quiz" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <!-- Quiz类型：输入链接 -->
        <template v-if="uploadForm.file_type === 'quiz'">
          <el-form-item label="Quiz名称">
            <el-input v-model="uploadForm.quiz_name" placeholder="输入Quiz名称" />
          </el-form-item>
          <el-form-item label="Quiz链接">
            <el-input v-model="uploadForm.quiz_url" placeholder="粘贴AI助手生成的Quiz分享链接" />
          </el-form-item>
        </template>

        <el-form-item label="文件描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="选填：简单描述文件内容（多个文件将共享此描述）"
          />
        </el-form-item>

        <!-- 非Quiz类型：文件上传 -->
        <el-form-item v-if="uploadForm.file_type !== 'quiz'" label="选择文件">
          <el-upload
            ref="uploadRef"
            :action="`/api/courses/course/${currentCourse?.id}/upload_file/`"
            :headers="{ Authorization: `Token ${userStore.token}` }"
            :data="uploadForm"
            :on-success="handleFileUploadSuccess"
            :on-error="handleUploadError"
            :auto-upload="false"
            :limit="10"
            multiple
            accept=".pdf,.doc,.docx,.zip,.rar,.mp4,.avi,.mov,.ppt,.pptx,.xls,.xlsx,.txt"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择文件（可多选）
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持多个文件上传，单个文件不超过 100MB，最多10个文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="uploading">
          {{ uploadForm.file_type === 'quiz' ? '添加Quiz' : '确定上传' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import api from '@/api'
import {
  Plus, User, Clock, Star, Folder, Document, Files, View, Edit, Delete, Upload, Download, Message, Link
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const myCourses = ref([])
const uploadDialogVisible = ref(false)
const currentCourse = ref(null)
const uploadRef = ref(null)
const uploading = ref(false)
const uploadForm = ref({
  file_type: 'material',
  description: '',
  quiz_url: '',
  quiz_name: ''
})

// 计算统计数据
const publishedCount = computed(() => {
  return myCourses.value.filter(c => c.is_published).length
})

const totalStudents = computed(() => {
  return myCourses.value.reduce((sum, c) => sum + (c.students_count || 0), 0)
})

const averageRating = computed(() => {
  const validRatings = myCourses.value.filter(c => c.rating > 0)
  if (validRatings.length === 0) return 0
  const sum = validRatings.reduce((sum, c) => sum + c.rating, 0)
  return sum / validRatings.length
})

// 加载课程数据
const loadMyCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/courses/course/my_courses/')
    myCourses.value = response.data
    // 为每个课程加载文件列表和待审批申请数量
    for (const course of myCourses.value) {
      // 加载文件列表
      await loadCourseFiles(course.id)
      // 加载待审批申请数量
      await loadPendingRequestsCount(course.id)
    }
  } catch (error) {
    console.error('获取课程失败:', error)
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

// 加载待审批申请数量
const loadPendingRequestsCount = async (courseId) => {
  try {
    const response = await api.get('/api/courses/course-requests/', {
      params: { course: courseId, status: 'pending' }
    })
    const requestsData = response.data.results || response.data || []
    const course = myCourses.value.find(c => c.id === courseId)
    if (course) {
      course.pendingRequests = requestsData.filter(r => r.course.id === courseId && r.status === 'pending').length
    }
  } catch (error) {
    console.error('获取申请数量失败:', error)
  }
}

// 加载课程文件列表
const loadCourseFiles = async (courseId) => {
  try {
    const response = await api.get(`/api/courses/course/${courseId}/files/`)
    const course = myCourses.value.find(c => c.id === courseId)
    if (course) {
      course.files = response.data
    }
  } catch (error) {
    console.error('加载课程文件失败:', error)
  }
}

// 查看课程详情
const viewCourse = (courseId) => {
  router.push({ path: `/course/${courseId}`, query: { tab: 'files' } })
}

// 编辑课程
const editCourse = (courseId) => {
  router.push(`/edit-course/${courseId}`)
}

// 查看学生列表
const viewStudents = (courseId) => {
  router.push(`/course/${courseId}/students`)
}

// 切换发布状态
const togglePublish = async (course) => {
  try {
    const response = await api.patch(`/api/courses/course/${course.id}/`, {
      is_published: !course.is_published
    })
    course.is_published = response.data.is_published
    ElMessage.success(course.is_published ? '课程已发布' : '已取消发布')
  } catch (error) {
    console.error('更新发布状态失败:', error)
    ElMessage.error('操作失败')
  }
}

// 删除课程
const deleteCourse = async (courseId) => {
  try {
    await api.delete(`/api/courses/course/${courseId}/`)
    myCourses.value = myCourses.value.filter(c => c.id !== courseId)
    ElMessage.success('课程已删除')
  } catch (error) {
    console.error('删除课程失败:', error)
    ElMessage.error('删除失败')
  }
}

// 显示上传对话框
const showUploadDialog = (course) => {
  currentCourse.value = course
  uploadForm.value = {
    file_type: 'material',
    description: '',
    quiz_url: '',
    quiz_name: ''
  }
  uploadDialogVisible.value = true
}

// 提交上传
const submitUpload = async () => {
  if (uploadForm.value.file_type === 'quiz') {
    // Quiz类型：提交链接
    if (!uploadForm.value.quiz_url.trim()) {
      ElMessage.warning('请输入Quiz链接')
      return
    }
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file_type', 'quiz')
      formData.append('quiz_url', uploadForm.value.quiz_url)
      formData.append('quiz_name', uploadForm.value.quiz_name || 'Quiz')
      formData.append('description', uploadForm.value.description || '')
      await api.post(`/api/courses/course/${currentCourse.value.id}/upload_file/`, formData)
      ElMessage.success('Quiz链接添加成功')
      uploadDialogVisible.value = false
      if (currentCourse.value) loadCourseFiles(currentCourse.value.id)
    } catch (error) {
      ElMessage.error(error.response?.data?.error || 'Quiz链接添加失败')
    } finally {
      uploading.value = false
    }
  } else {
    // 普通文件上传
    if (uploadRef.value) {
      uploading.value = true
      uploadRef.value.submit()
    }
  }
}

// 文件上传成功
const handleFileUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  // 检查是否所有文件都上传完成
  setTimeout(() => {
    uploading.value = false
    uploadDialogVisible.value = false
    // 重新加载该课程的文件列表
    if (currentCourse.value) {
      loadCourseFiles(currentCourse.value.id)
    }
  }, 500)
}

// 文件上传失败
const handleUploadError = (error) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败，请重试')
  uploading.value = false
}

// 下载文件
const downloadFile = (file) => {
  if (file.file_type === 'quiz' && file.quiz_url) {
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

// 删除文件
const deleteFile = async (courseId, fileId) => {
  try {
    await api.delete(`/api/courses/course/${courseId}/delete_file/`, {
      data: { file_id: fileId }
    })
    ElMessage.success('文件删除成功')
    loadCourseFiles(courseId)
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('删除文件失败')
  }
}

// 获取文件类型标签
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

// 格式化时间
const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

onMounted(() => {
  loadMyCourses()
})
</script>

<style scoped>
.teacher-courses {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #909399;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.courses-card {
  min-height: 400px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

.course-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.course-image-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 15px;
}

.course-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.publish-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.course-content h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #909399;
}

.files-section {
  margin: 15px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.file-list {
  margin-top: 10px;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.file-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  position: relative;
  transition: all 0.2s;
}

.file-card:hover {
  background: #e8eaf0;
  transform: translateY(-2px);
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 8px;
  color: #333333;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.file-time {
  font-size: 12px;
  color: #909399;
}

.file-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
  margin-top: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.file-item > span {
  flex: 1;
  color: #606266;
}

.course-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.course-actions .el-button {
  flex: 1;
  min-width: 80px;
}
</style>
