<template>
  <div class="course-requests">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
          <span>课程申请管理</span>
          <el-badge :value="pendingCount" class="badge">
            <el-button size="small" @click="loadRequests">刷新</el-button>
          </el-badge>
        </div>
      </template>

      <!-- 筛选 -->
      <el-radio-group v-model="filterStatus" @change="filterRequests" class="filter-group">
        <el-radio-button value="all">全部 ({{ allRequests.length }})</el-radio-button>
        <el-radio-button value="pending">待审批 ({{ pendingCount }})</el-radio-button>
        <el-radio-button value="approved">已批准 ({{ approvedCount }})</el-radio-button>
        <el-radio-button value="rejected">已拒绝 ({{ rejectedCount }})</el-radio-button>
      </el-radio-group>

      <!-- 申请列表 -->
      <el-table :data="filteredRequests" style="width: 100%; margin-top: 20px" v-loading="loading">
        <el-table-column label="学生" width="120">
          <template #default="scope">
            <div class="student-info">
              <el-avatar :size="32">
                {{ scope.row.student.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span>{{ scope.row.student.username }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="course.title" label="申请课程" min-width="200" />

        <el-table-column label="申请留言" min-width="250">
          <template #default="scope">
            <el-text v-if="scope.row.message" line-clamp="2">
              {{ scope.row.message }}
            </el-text>
            <el-text v-else type="info">无</el-text>
          </template>
        </el-table-column>

        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <div v-if="scope.row.status === 'pending'" class="action-buttons">
              <el-button
                type="success"
                size="small"
                @click="handleApprove(scope.row)"
                :loading="scope.row.processing"
              >
                批准
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleReject(scope.row)"
                :loading="scope.row.processing"
              >
                拒绝
              </el-button>
            </div>
            <el-text v-else type="info">
              已处理
            </el-text>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredRequests.length === 0 && !loading"
        :description="getEmptyText()"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { Document } from '@element-plus/icons-vue'

const loading = ref(false)
const allRequests = ref([])
const filterStatus = ref('all')

// 过滤后的申请
const filteredRequests = computed(() => {
  if (filterStatus.value === 'all') {
    return allRequests.value
  }
  return allRequests.value.filter(r => r.status === filterStatus.value)
})

// 统计数量
const pendingCount = computed(() => 
  allRequests.value.filter(r => r.status === 'pending').length
)

const approvedCount = computed(() => 
  allRequests.value.filter(r => r.status === 'approved').length
)

const rejectedCount = computed(() => 
  allRequests.value.filter(r => r.status === 'rejected').length
)

// 加载申请列表
const loadRequests = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/courses/course-requests/')
    // API返回分页格式，需要使用results字段
    const requestsData = response.data.results || response.data || []
    allRequests.value = requestsData.map(r => ({
      ...r,
      processing: false
    }))
  } catch (error) {
    console.error('加载申请失败:', error)
    ElMessage.error('加载申请列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选申请
const filterRequests = () => {
  // 由computed自动处理
}

// 批准申请
const handleApprove = async (request) => {
  try {
    await ElMessageBox.confirm(
      `确定批准 ${request.student.username} 加入课程《${request.course.title}》吗？`,
      '批准申请',
      {
        confirmButtonText: '批准',
        cancelButtonText: '取消',
        type: 'success'
      }
    )

    request.processing = true
    
    await api.post(`/api/courses/course-requests/${request.id}/approve/`)
    
    ElMessage.success('已批准申请，学生可以开始学习该课程')
    
    // 刷新列表
    await loadRequests()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批准失败:', error)
      ElMessage.error(error.response?.data?.error || '批准失败')
    }
  } finally {
    request.processing = false
  }
}

// 拒绝申请
const handleReject = async (request) => {
  try {
    await ElMessageBox.confirm(
      `确定拒绝 ${request.student.username} 加入课程《${request.course.title}》吗？`,
      '拒绝申请',
      {
        confirmButtonText: '拒绝',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    request.processing = true
    
    await api.post(`/api/courses/course-requests/${request.id}/reject/`)
    
    ElMessage.success('已拒绝申请')
    
    // 刷新列表
    await loadRequests()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error(error.response?.data?.error || '拒绝失败')
    }
  } finally {
    request.processing = false
  }
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

// 获取空状态文本
const getEmptyText = () => {
  const texts = {
    'all': '暂无申请记录',
    'pending': '暂无待审批的申请',
    'approved': '暂无已批准的申请',
    'rejected': '暂无已拒绝的申请'
  }
  return texts[filterStatus.value] || '暂无数据'
}

onMounted(() => {
  loadRequests()
})
</script>

<style scoped>
.course-requests {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.badge {
  margin-left: auto;
}

.filter-group {
  margin-bottom: 20px;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 5px;
}
</style>
