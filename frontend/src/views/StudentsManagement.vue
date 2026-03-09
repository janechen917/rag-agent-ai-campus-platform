<template>
  <div class="students-management">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>学生管理</h2>
          <p>按课程查看学生规模与学习情况，快速进入课程学生详情页。</p>
        </div>
        <el-button type="primary" :icon="Refresh" @click="loadCourses" :loading="loading">
          刷新
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="课程总数" :value="courses.length">
            <template #suffix>门</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="学生总数" :value="totalStudents">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="平均每课学生" :value="avgStudentsPerCourse" :precision="1">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-empty v-if="!loading && courses.length === 0" description="暂无课程">
        <el-button type="primary" @click="router.push('/create-course')">去创建课程</el-button>
      </el-empty>

      <el-table
        v-else
        v-loading="loading"
        :data="courses"
        style="width: 100%"
      >
        <el-table-column prop="title" label="课程名称" min-width="220" />

        <el-table-column label="分类" width="120">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.category === 'required' ? 'danger' : 'success'">
              {{ scope.row.category_display || scope.row.category }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="students_count" label="学生人数" width="120" sortable>
          <template #default="scope">
            {{ scope.row.students_count || 0 }}
          </template>
        </el-table-column>

        <el-table-column prop="rating" label="评分" width="120" sortable>
          <template #default="scope">
            {{ scope.row.rating || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_published ? 'success' : 'info'" size="small">
              {{ scope.row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="router.push(`/course/${scope.row.id}`)">
              课程详情
            </el-button>
            <el-button
              size="small"
              type="primary"
              :icon="User"
              @click="goToCourseStudents(scope.row.id)"
            >
              管理学生
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, User } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const courses = ref([])

const totalStudents = computed(() => {
  return courses.value.reduce((sum, c) => sum + (c.students_count || 0), 0)
})

const avgStudentsPerCourse = computed(() => {
  if (!courses.value.length) return 0
  return totalStudents.value / courses.value.length
})

const loadCourses = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/courses/course/my_courses/')
    courses.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载教师课程失败:', error)
    ElMessage.error('加载学生管理数据失败')
    courses.value = []
  } finally {
    loading.value = false
  }
}

const goToCourseStudents = (courseId) => {
  router.push(`/course/${courseId}/students`)
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.students-management {
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
  margin: 6px 0 0;
  color: #606266;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}
</style>
