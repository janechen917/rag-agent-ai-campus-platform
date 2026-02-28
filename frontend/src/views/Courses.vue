<template>
  <div class="courses-page">
    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="selectedCategory" placeholder="课程分类" clearable @change="filterCourses">
            <el-option label="全部" value="" />
            <el-option label="必修" value="required" />
            <el-option label="选修" value="elective" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="sortBy" placeholder="排序方式" @change="sortCourses">
            <el-option label="最新" value="newest" />
            <el-option label="最热" value="popular" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 课程列表 -->
    <el-row :gutter="20" class="courses-grid">
      <el-col :span="6" v-for="course in displayedCourses" :key="course.id">
        <el-card class="course-card" shadow="hover" @click="viewCourse(course.id)">
          <img :src="course.image" class="course-image" />
          <div class="course-content">
            <h3>{{ course.title }}</h3>
            <p class="description">{{ course.description }}</p>
            
            <div class="instructor">
              <el-avatar :size="24">{{ course.instructor?.charAt(0) }}</el-avatar>
              <span>{{ course.instructor }}</span>
            </div>
            
            <div class="meta">
              <div class="stats">
                <span>
                  <el-icon><User /></el-icon>
                  {{ course.students }}
                </span>
                <span>
                  <el-icon><Clock /></el-icon>
                  {{ course.duration }}
                </span>
              </div>
              <el-tag :type="getCategoryType(course.category)" size="small">
                {{ getCategoryLabel(course.category) }}
              </el-tag>
            </div>
            
            <el-divider />
            
            <div class="footer">
              <el-button type="primary" size="small" style="width: 100%">立即学习</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredCourses.length"
        :page-sizes="[8, 16, 24, 32]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, User, Clock } from '@element-plus/icons-vue'

const router = useRouter()

const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('newest')
const currentPage = ref(1)
const pageSize = ref(8)

const courses = ref([
  {
    id: 1,
    title: 'Python编程基础',
    description: '从零开始学习Python编程语言，掌握基础语法和核心概念',
    image: 'https://via.placeholder.com/300x200/409EFF/FFFFFF?text=Python',
    category: 'required',
    instructor: '张老师',
    students: 1234,
    duration: '20小时',
    rating: 4.8
  },
  {
    id: 2,
    title: 'Vue 3 实战开发',
    description: '掌握Vue3框架和现代前端开发技术栈',
    image: 'https://via.placeholder.com/300x200/67C23A/FFFFFF?text=Vue3',
    category: 'elective',
    instructor: '李老师',
    students: 856,
    duration: '30小时',
    rating: 4.9
  },
  {
    id: 3,
    title: 'Django REST API开发',
    description: '构建强大的后端RESTful API服务',
    image: 'https://via.placeholder.com/300x200/E6A23C/FFFFFF?text=Django',
    category: 'required',
    instructor: '王老师',
    students: 642,
    duration: '25小时',
    rating: 4.7
  },
  {
    id: 4,
    title: 'AI机器学习入门',
    description: '探索人工智能和机器学习的奥秘',
    image: 'https://via.placeholder.com/300x200/F56C6C/FFFFFF?text=AI+ML',
    category: 'elective',
    instructor: '陈老师',
    students: 489,
    duration: '40小时',
    price: 399,
    rating: 4.9
  },
  {
    id: 5,
    title: 'JavaScript高级编程',
    description: '深入理解JavaScript核心原理和高级特性',
    image: 'https://via.placeholder.com/300x200/F39C12/FFFFFF?text=JavaScript',
    category: 'required',
    instructor: '赵老师',
    students: 921,
    duration: '35小时',
    rating: 4.8
  },
  {
    id: 6,
    title: 'React全栈开发',
    description: '使用React构建现代化Web应用',
    image: 'https://via.placeholder.com/300x200/61DAFB/FFFFFF?text=React',
    category: 'elective',
    instructor: '刘老师',
    students: 756,
    duration: '28小时',
    rating: 4.7
  },
  {
    id: 7,
    title: 'Node.js后端开发',
    description: '使用Node.js构建高性能服务端应用',
    image: 'https://via.placeholder.com/300x200/68A063/FFFFFF?text=NodeJS',
    category: 'required',
    instructor: '周老师',
    students: 634,
    duration: '26小时',
    rating: 4.6
  },
  {
    id: 8,
    title: '深度学习实战',
    description: '从理论到实践，掌握深度学习技术',
    image: 'https://via.placeholder.com/300x200/8E44AD/FFFFFF?text=Deep+Learning',
    category: 'elective',
    instructor: '吴老师',
    students: 412,
    duration: '45小时',
    rating: 4.9
  }
])

const filteredCourses = computed(() => {
  let result = courses.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(course => 
      course.title.toLowerCase().includes(query) ||
      course.description.toLowerCase().includes(query)
    )
  }

  // 分类过滤
  if (selectedCategory.value) {
    result = result.filter(course => course.category === selectedCategory.value)
  }

  // 排序
  switch (sortBy.value) {
    case 'popular':
      result = [...result].sort((a, b) => b.students - a.students)
      break
    case 'newest':
    default:
      // 保持原顺序
      break
  }

  return result
})

const displayedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCourses.value.slice(start, end)
})

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

const handleSearch = () => {
  currentPage.value = 1
}

const filterCourses = () => {
  currentPage.value = 1
}

const sortCourses = () => {
  currentPage.value = 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const viewCourse = (id) => {
  router.push(`/course/${id}`)
}

onMounted(() => {
  // 可以在这里从API加载课程数据
})
</script>

<style scoped>
.courses-page {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
}

.courses-grid {
  min-height: 500px;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
  height: 100%;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.course-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px 4px 0 0;
}

.course-content {
  padding: 15px;
}

.course-content h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.description {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 12px;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.instructor {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #909399;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stats {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #909399;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current {
  color: #F56C6C;
  font-size: 22px;
  font-weight: bold;
}

.original {
  color: #C0C4CC;
  font-size: 14px;
  text-decoration: line-through;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
