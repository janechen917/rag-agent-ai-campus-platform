<template>
  <div class="home">
    <el-row :gutter="20">
      <!-- 轮播图 -->
      <el-col :span="24">
        <el-carousel height="400px" class="banner">
          <el-carousel-item v-for="(banner, index) in banners" :key="index">
            <div class="banner-content" :style="{ background: banner.color }">
              <h2>{{ banner.title }}</h2>
              <p>{{ banner.description }}</p>
              <el-button type="primary" size="large" @click="router.push(banner.link)">
                {{ banner.buttonText }}
              </el-button>
            </div>
          </el-carousel-item>
        </el-carousel>
      </el-col>
    </el-row>

    <!-- 特色功能 -->
    <el-row :gutter="20" class="features">
      <el-col :span="24">
        <h2 class="section-title">平台特色</h2>
      </el-col>
      <el-col :span="6" v-for="feature in features" :key="feature.title">
        <el-card class="feature-card" shadow="hover">
          <el-icon :size="48" :color="feature.color">
            <component :is="feature.icon"></component>
          </el-icon>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学习统计 -->
    <el-row :gutter="20" class="stats">
      <el-col :span="24">
        <h2 class="section-title">学习数据</h2>
      </el-col>
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="36" :color="stat.color">
              <component :is="stat.icon"></component>
            </el-icon>
            <div class="stat-info">
              <h2>{{ stat.value }}</h2>
              <p>{{ stat.label }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI功能展示 -->
    <el-row :gutter="20" class="ai-section">
      <el-col :span="24">
        <h2 class="section-title">AI智能学习助手</h2>
      </el-col>
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="24"><Cpu /></el-icon>
              <span>智能问答</span>
            </div>
          </template>
          <p>24/7在线AI学习助手，随时解答学习疑问，提供个性化学习建议和辅导</p>
          <el-button type="primary" @click="router.push('/ai-tutor')">开始使用</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="24"><Search /></el-icon>
              <span>课程探索</span>
            </div>
          </template>
          <p>海量精品课程，涵盖多个学科领域，找到最适合你的学习内容</p>
          <el-button type="primary" @click="router.push('/search-courses')">浏览课程</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const banners = ref([
  {
    title: '欢迎来到校园智慧学习平台',
    description: '利用AI技术，打造个性化智能学习体验',
    buttonText: '开始学习',
    link: '/ai-tutor',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    title: 'AI学习助手',
    description: '24小时智能答疑，让学习更高效',
    buttonText: '体验AI助手',
    link: '/ai-tutor',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  }
])

const features = ref([
  {
    icon: 'Cpu',
    title: 'AI智能辅导',
    description: '智能问答系统，随时随地获取学习帮助',
    color: '#409EFF'
  },
  {
    icon: 'TrendCharts',
    title: '学习追踪',
    description: '记录学习轨迹，智能分析学习效果',
    color: '#E6A23C'
  },
  {
    icon: 'VideoPlay',
    title: '课程资源',
    description: '丰富的课程内容和学习材料',
    color: '#67C23A'
  },
  {
    icon: 'Star',
    title: '个性化推荐',
    description: '智能匹配最适合的学习路径',
    color: '#F56C6C'
  }
])

const stats = ref([
  {
    icon: 'User',
    label: '在线学习者',
    value: '2,345',
    color: '#409EFF'
  },
  {
    icon: 'Reading',
    label: '精品课程',
    value: '186',
    color: '#67C23A'
  },
  {
    icon: 'VideoPlay',
    label: '视频资源',
    value: '8,923',
    color: '#E6A23C'
  },
  {
    icon: 'Star',
    label: 'AI问题解答',
    value: '4,567',
    color: '#F56C6C'
  }
])

onMounted(() => {
  // 如果用户已登录，可以加载个性化数据
  if (userStore.isLoggedIn) {
    // 加载用户学习统计等
  }
})
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
}

.banner {
  margin-bottom: 40px;
  border-radius: 8px;
  overflow: hidden;
}

.banner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
  text-align: center;
  padding: 20px;
}

.banner-content h2 {
  font-size: 42px;
  margin-bottom: 20px;
}

.banner-content p {
  font-size: 20px;
  margin-bottom: 30px;
}

.section-title {
  font-size: 28px;
  margin-bottom: 30px;
  color: #303133;
  text-align: center;
}

.features {
  margin-bottom: 60px;
}

.feature-card {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  margin: 15px 0 10px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
}

.stats {
  margin-bottom: 60px;
}

.stat-card {
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.stat-info h2 {
  font-size: 32px;
  margin: 0;
  color: #303133;
  font-weight: bold;
}

.stat-info p {
  margin: 5px 0 0;
  color: #909399;
  font-size: 14px;
}

.ai-section {
  margin-bottom: 40px;
}

.ai-card {
  text-align: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: bold;
}

.ai-card p {
  margin: 20px 0;
  color: #606266;
  line-height: 1.6;
}
</style>
