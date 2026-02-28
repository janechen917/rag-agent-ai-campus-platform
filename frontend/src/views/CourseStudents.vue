<template>
  <div class="course-students">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>课程学生管理</h2>
          <p v-if="courseInfo">{{ courseInfo.title }} - 学生名单</p>
        </div>
        <el-button @click="$router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </el-card>

    <!-- 学生统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="24">
        <el-card class="stat-card">
          <el-statistic title="学生总数" :value="students.length">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生列表 -->
    <el-card class="students-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><User /></el-icon>
          <span>学生列表</span>
          <el-button size="small" @click="refreshStudents">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table 
        :data="filteredStudents" 
        style="width: 100%" 
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="student.username" label="学生姓名" min-width="120">
          <template #default="scope">
            <div class="student-info">
              <el-avatar :size="32">
                {{ scope.row.student.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <div>
                <div class="student-name">{{ scope.row.student.username }}</div>
                <div class="student-email">{{ scope.row.student.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="enrolled_at" label="加入时间" width="180" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.enrolled_at) }}
          </template>
        </el-table-column>



        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewStudentProgress(scope.row)">
              详细信息
            </el-button>
            <el-popconfirm
              title="确定移除该学生吗？"
              @confirm="removeStudent(scope.row)"
            >
              <template #reference>
                <el-button size="small" type="danger">
                  移除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="students.length === 0 && !loading"
        description="暂无学生"
      />
    </el-card>

    <!-- 学生详细信息对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="学生详细信息"
      width="800px"
    >
      <div v-if="selectedStudent" class="student-detail">
        <div class="student-header">
          <el-avatar :size="60">
            {{ selectedStudent.student.username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="student-info">
            <h3>{{ selectedStudent.student.username }}</h3>
            <p>{{ selectedStudent.student.email }}</p>
          </div>
        </div>

        <el-divider />

        <el-descriptions title="学生信息" :column="1" border>
          <el-descriptions-item label="加入时间">
            {{ formatDate(selectedStudent.enrolled_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="progressDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, User, Refresh
} from '@element-plus/icons-vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const students = ref([])
const courseInfo = ref(null)
const progressDialogVisible = ref(false)
const selectedStudent = ref(null)

// 计算属性
const filteredStudents = computed(() => {
  return students.value
})



// 获取课程信息
const fetchCourseInfo = async () => {
  try {
    const response = await api.get(`/api/courses/course/${route.params.id}/`)
    courseInfo.value = response.data
  } catch (error) {
    console.error('获取课程信息失败:', error)
    ElMessage.error('获取课程信息失败')
  }
}

// 获取学生列表
const fetchStudents = async () => {
  loading.value = true
  try {
    const response = await api.get(`/api/courses/course/${route.params.id}/students/`)
    // API返回直接数组格式
    students.value = response.data || []
  } catch (error) {
    console.error('获取学生列表失败:', error)
    ElMessage.error('获取学生列表失败')
    students.value = []
  } finally {
    loading.value = false
  }
}

// 刷新学生列表
const refreshStudents = async () => {
  await fetchStudents()
}

// 查看学生详细信息
const viewStudentProgress = (student) => {
  selectedStudent.value = student
  progressDialogVisible.value = true
}

// 移除学生
const removeStudent = async (student) => {
  try {
    await api.delete(`/api/courses/course/${route.params.id}/remove-student/`, {
      data: { enrollment_id: student.id }
    })
    ElMessage.success('学生已移除')
    await fetchStudents()
  } catch (error) {
    console.error('移除学生失败:', error)
    ElMessage.error('移除学生失败')
  }
}

// 处理排序
const handleSortChange = ({ prop, order }) => {
  // 可以在这里添加排序逻辑
  console.log('排序:', prop, order)
}



// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(async () => {
  await Promise.all([
    fetchCourseInfo(),
    fetchStudents()
  ])
})
</script>

<style scoped>
.course-students {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
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
  margin: 0;
  color: #303133;
}

.header-content p {
  margin: 5px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.students-card .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.students-card .card-header .el-button {
  margin-left: auto;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-name {
  font-weight: 500;
  color: #303133;
}

.student-email {
  font-size: 12px;
  color: #909399;
}



.student-detail .student-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.student-detail .student-info h3 {
  margin: 0 0 5px 0;
}

.student-detail .student-info p {
  margin: 0 0 10px 0;
  color: #606266;
}
</style>