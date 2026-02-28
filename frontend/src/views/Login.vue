<template>
  <div class="login-page">
    <!-- 平台介绍区域 -->
    <div class="intro-section">
      <div class="intro-content">
        <h1 class="platform-title">
          <el-icon :size="48"><Reading /></el-icon>
          校园智慧学习平台
        </h1>
        <p class="platform-subtitle">AI驱动的个性化学习体验</p>
        
        <div class="feature-highlights">
          <div class="highlight-item">
            <el-icon :size="32" color="#67C23A"><ChatDotSquare /></el-icon>
            <h3>AI学习导师</h3>
            <p>24/7智能问答辅导</p>
          </div>
          <div class="highlight-item">
            <el-icon :size="32" color="#409EFF"><VideoPlay /></el-icon>
            <h3>丰富课程</h3>
            <p>海量优质学习资源</p>
          </div>
          <div class="highlight-item">
            <el-icon :size="32" color="#F56C6C"><TrophyBase /></el-icon>
            <h3>个性化推荐</h3>
            <p>智能匹配学习路径</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 登录注册区域 -->
    <div class="form-section">
      <el-card class="login-card">
        <template #header>
          <div class="header">
            <h2>欢迎使用</h2>
            <p style="color: #909399; font-size: 14px; margin: 5px 0 0 0;">请登录或注册以继续</p>
          </div>
        </template>

        <el-tabs v-model="activeTab" class="login-tabs">
          <el-tab-pane label="登录" name="login">
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="0">
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="用户名 / 邮箱"
                  :prefix-icon="User"
                  size="large"
                />
              </el-form-item>
            
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  :prefix-icon="Lock"
                  size="large"
                  show-password
                  @keyup.enter="handleLogin"
                />
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                <el-link type="primary" style="float: right">忘记密码？</el-link>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  style="width: 100%"
                  @click="handleLogin"
                  :loading="loading"
                >
                  登录
                </el-button>
              </el-form-item>
            </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="0">
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
              />
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱"
                :prefix-icon="Message"
                size="large"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>

            <el-form-item prop="userType">
              <el-select
                v-model="registerForm.userType"
                placeholder="请选择身份"
                size="large"
                style="width: 100%"
                :prefix-icon="UserFilled"
              >
                <el-option label="👨‍🎓 学生 - 学习课程，使用AI辅导" value="student" />
                <el-option label="👨‍🏫 教师 - 创建课程，管理内容" value="teacher" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-checkbox v-model="registerForm.agree">
                我已阅读并同意 <el-link type="primary">用户协议</el-link> 和 <el-link type="primary">隐私政策</el-link>
              </el-checkbox>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                @click="handleRegister"
                :loading="loading"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <el-divider>或</el-divider>

      <div class="social-login">
        <el-button circle size="large" title="GitHub登录">
          <el-icon><Setting /></el-icon>
        </el-button>
        <el-button circle size="large" title="Google登录">
          <el-icon><Setting /></el-icon>
        </el-button>
        <el-button circle size="large" title="微信登录">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>

      <div class="quick-info">
        <el-alert
          title="体验提示"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p style="margin: 0; font-size: 13px;">
              👨‍🎓 学生账号：访问课程、AI导师、学习讨论<br>
              👨‍🏫 教师账号：创建课程、管理内容、审核申请
            </p>
          </template>
        </el-alert>
      </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, Message, Reading, 
  UserFilled, ChatDotSquare, VideoPlay, 
  TrophyBase, Setting 
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = ref({
  username: '',
  password: '',
  remember: false
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  userType: 'student',
  agree: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  userType: [
    { required: true, message: '请选择身份', trigger: 'change' }
  ]
}

const handleLogin = async () => {
  await loginFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await userStore.login({
          username: loginForm.value.username,
          password: loginForm.value.password
        })
        
        if (result.success) {
          ElMessage.success('登录成功')
          // 根据用户类型跳转到不同页面
          const userType = userStore.user?.user_type || 'student'
          if (userType === 'teacher') {
            router.push('/teacher-home')
          } else {
            router.push('/student-home')
          }
        } else {
          ElMessage.error(result.error)
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerForm.value.agree) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }

  await registerFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await userStore.register({
          username: registerForm.value.username,
          email: registerForm.value.email,
          password: registerForm.value.password,
          user_type: registerForm.value.userType
        })
        
        if (result.success) {
          ElMessage.success('注册成功，请登录')
          activeTab.value = 'login'
        } else {
          ElMessage.error(result.error)
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 平台介绍区域 */
.intro-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: white;
}

.intro-content {
  max-width: 600px;
}

.platform-title {
  font-size: 48px;
  font-weight: bold;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.platform-subtitle {
  font-size: 24px;
  margin: 0 0 60px 0;
  opacity: 0.9;
}

.feature-highlights {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  margin-top: 40px;
}

.highlight-item {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s;
}

.highlight-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.highlight-item h3 {
  margin: 15px 0 8px 0;
  font-size: 18px;
}

.highlight-item p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

/* 表单区域 */
.form-section {
  width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.login-card {
  width: 100%;
  border-radius: 12px;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header {
  text-align: center;
}

.header h2 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.login-tabs {
  margin-top: 20px;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.quick-info {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-page {
    flex-direction: column;
  }
  
  .intro-section {
    padding: 30px 20px;
  }
  
  .platform-title {
    font-size: 32px;
  }
  
  .platform-subtitle {
    font-size: 18px;
    margin-bottom: 30px;
  }
  
  .feature-highlights {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .form-section {
    width: 100%;
    padding: 20px;
  }
}
</style>
