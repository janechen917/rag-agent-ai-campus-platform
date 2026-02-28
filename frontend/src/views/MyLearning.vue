<template>
  <div class="my-learning">
    <el-tabs v-model="activeTab" class="learning-tabs">
      <el-tab-pane label="学习中" name="learning">
        <el-empty v-if="learningCourses.length === 0" description="暂无学习中的课程">
          <el-button type="primary" @click="router.push('/search-courses')">去选课</el-button>
        </el-empty>
        <el-row :gutter="20" v-else>
          <el-col :span="8" v-for="enrollment in learningCourses" :key="enrollment.id">
            <el-card class="course-card" shadow="hover" @click="continueLearning(enrollment.course.id)">
              <img :src="enrollment.course.image || 'https://via.placeholder.com/300x180/409EFF/FFFFFF?text=Course'" class="course-image" />
              <div class="course-info">
                <h3>{{ enrollment.course.title }}</h3>
                <div class="progress-section">
                  <div class="progress-text">
                    <span>学习进度</span>
                    <span>{{ enrollment.progress }}%</span>
                  </div>
                  <el-progress :percentage="enrollment.progress" :stroke-width="8" />
                </div>
                <div class="meta">
                  <span>开始时间：{{ formatDate(enrollment.enrolled_at) }}</span>
                </div>
                <el-button type="primary" style="width: 100%; margin-top: 15px">
                  继续学习
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="已完成" name="completed">
        <el-empty v-if="completedCourses.length === 0" description="暂无已完成的课程" />
        <el-row :gutter="20" v-else>
          <el-col :span="8" v-for="enrollment in completedCourses" :key="enrollment.id">
            <el-card class="course-card" shadow="hover">
              <el-tag type="success" class="completed-badge">已完成</el-tag>
              <img :src="enrollment.course.image || 'https://via.placeholder.com/300x180/67C23A/FFFFFF?text=Completed'" class="course-image" />
              <div class="course-info">
                <h3>{{ enrollment.course.title }}</h3>
                <div class="completion-info">
                  <el-icon color="#67C23A" :size="24"><Select /></el-icon>
                  <span>完成于 {{ formatDate(enrollment.completed_at) }}</span>
                </div>
                <div class="actions">
                  <el-button @click="router.push(`/course/${enrollment.course.id}`)">复习课程</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>


      <el-tab-pane label="学习统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="学习中" :value="learningCourses.length">
                <template #suffix>门课程</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="已完成" :value="completedCourses.length">
                <template #suffix>门课程</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="总计" :value="learningCourses.length + completedCourses.length">
                <template #suffix>门课程</template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="info-card" style="margin-top: 20px">
          <template #header>
            <span>学习说明</span>
          </template>
          <div style="padding: 20px; line-height: 2;">
            <p>👉 在“搜索课程”页面选择并申请课程</p>
            <p>👉 教师批准后，课程将显示在“学习中”中</p>
            <p>👉 完成课程学习后，会移至“已完成”</p>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Select } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const activeTab = ref('learning')
const enrollments = ref([])
const loading = ref(false)

// 学习中的课程（进度 < 100%）
const learningCourses = computed(() => {
  return enrollments.value.filter(e => !e.completed && e.progress < 100)
})

// 已完成的课程
const completedCourses = computed(() => {
  return enrollments.value.filter(e => e.completed)
})

// 获取选课数据
const fetchEnrollments = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/courses/course-enrollments/')
    // API返回分页格式，需要使用results字段
    enrollments.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取选课记录失败:', error)
    ElMessage.error('获取课程数据失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const continueLearning = (courseId) => {
  router.push(`/course/${courseId}`)
}

onMounted(() => {
  fetchEnrollments()
})
</script>

<style scoped>
.my-learning {
  max-width: 1400px;
  margin: 0 auto;
}

.learning-tabs {
  background: white;
  padding: 20px;
  border-radius: 8px;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.course-card:hover {
  transform: translateY(-5px);
}

.completed-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 1;
}

.course-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
}

.course-info {
  padding: 15px 0;
}

.course-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.progress-section {
  margin-bottom: 15px;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #909399;
}

.completion-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
  color: #67C23A;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.actions .el-button {
  flex: 1;
}

.course-card-small {
  margin-bottom: 20px;
}

.course-image-small {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.course-info-small {
  padding: 15px 0;
}

.course-info-small h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 15px;
}

.course-info-small .price {
  color: #F56C6C;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-card {
  text-align: center;
}

.chart-card {
  margin-top: 20px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
