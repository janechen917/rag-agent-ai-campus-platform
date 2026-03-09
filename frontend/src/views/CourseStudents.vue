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
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="学生总数" :value="students.length">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="平均进度" :value="averageProgress" :precision="1">
            <template #suffix>%</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card excellent-card">
          <el-statistic title="优秀学生" :value="excellentStudents">
            <template #suffix>人</template>
            <template #prefix>
              <el-icon color="#67C23A"><TrophyBase /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card attention-card">
          <el-statistic title="需关注" :value="needAttentionStudents">
            <template #suffix>人</template>
            <template #prefix>
              <el-icon color="#F56C6C"><Warning /></el-icon>
            </template>
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

        <el-table-column prop="progress" label="学习进度" width="200" sortable>
          <template #default="scope">
            <div class="progress-wrapper">
              <el-progress 
                :percentage="scope.row.progress || 0" 
                :color="getProgressColor(scope.row.progress)"
                :stroke-width="12"
              />
              <el-tag 
                :type="getProgressTag(scope.row.progress)" 
                size="small" 
                style="margin-left: 10px;"
              >
                {{ getProgressLabel(scope.row.progress) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewStudentProgress(scope.row)">
              详细信息
            </el-button>            <el-button 
              size="small" 
              type="primary" 
              :icon="ChatLineRound"
              @click="sendMessage(scope.row.student)"
            >
              发私信
            </el-button>            <el-popconfirm
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
  ArrowLeft, User, Refresh, ChatLineRound, TrophyBase, Warning
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

// 计算平均进度
const averageProgress = computed(() => {
  if (students.value.length === 0) return 0
  const total = students.value.reduce((sum, student) => sum + (student.progress || 0), 0)
  return total / students.value.length
})

// 优秀学生数量（进度>=80%）
const excellentStudents = computed(() => {
  return students.value.filter(s => (s.progress || 0) >= 80).length
})

// 需关注学生数量（进度<20%）
const needAttentionStudents = computed(() => {
  return students.value.filter(s => (s.progress || 0) < 20).length
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

// 快速发送私信
const sendMessage = (student) => {
  // 跳转到聊天页面，并通过query参数传递学生ID
  router.push({
    path: '/chat',
    query: { userId: student.id, userName: student.username }
  })
  ElMessage.success(`正在打开与 ${student.username} 的私信...`)
}

// 获取进度颜色
const getProgressColor = (progress) => {
  if (progress >= 80) return '#67C23A' // 绿色
  if (progress >= 50) return '#409EFF' // 蓝色
  if (progress >= 20) return '#E6A23C' // 橙色
  return '#F56C6C' // 红色
}

// 获取进度标签类型
const getProgressTag = (progress) => {
  if (progress >= 80) return 'success'
  if (progress >= 50) return ''
  if (progress >= 20) return 'warning'
  return 'danger'
}

// 获取进度标签文字
const getProgressLabel = (progress) => {
  if (progress >= 80) return '优秀'
  if (progress >= 50) return '良好'
  if (progress >= 20) return '一般'
  return '需关注'
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

.progress-wrapper {
  display: flex;
  align-items: center;
}

.excellent-card {
  border-left: 4px solid #67C23A;
}

.attention-card {
  border-left: 4px solid #F56C6C;
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