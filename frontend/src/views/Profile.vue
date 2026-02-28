<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧个人信息 -->
      <el-col :span="8">
        <el-card class="profile-card">
          <div class="avatar-section">
            <el-avatar :size="120">{{ userStore.user?.username?.charAt(0) }}</el-avatar>
            <el-button text type="primary" style="margin-top: 15px">更换头像</el-button>
          </div>
          
          <div class="user-info">
            <h2>{{ userStore.user?.username }}</h2>
            <p class="email">{{ userStore.user?.email }}</p>
            <el-tag type="info">普通会员</el-tag>
          </div>

          <el-divider />

          <div class="stats-grid">
            <div class="stat-item">
              <div class="value">8</div>
              <div class="label">完成课程</div>
            </div>
            <div class="stat-item">
              <div class="value">127</div>
              <div class="label">学习小时</div>
            </div>
            <div class="stat-item">
              <div class="value">15</div>
              <div class="label">连续天数</div>
            </div>
          </div>
        </el-card>

        <el-card class="achievements-card">
          <template #header>
            <div class="card-header">
              <el-icon><Trophy /></el-icon>
              <span>成就徽章</span>
            </div>
          </template>
          <div class="badges-grid">
            <el-tooltip content="完成首个课程" placement="top">
              <div class="badge-item">🎓</div>
            </el-tooltip>
            <el-tooltip content="连续学习7天" placement="top">
              <div class="badge-item">🔥</div>
            </el-tooltip>
            <el-tooltip content="获得5星好评" placement="top">
              <div class="badge-item">⭐</div>
            </el-tooltip>
            <div class="badge-item locked">🔒</div>
            <div class="badge-item locked">🔒</div>
            <div class="badge-item locked">🔒</div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧设置 -->
      <el-col :span="16">
        <el-card class="settings-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="basic">
              <el-form :model="profileForm" label-width="100px">
                <el-form-item label="用户名">
                  <el-input v-model="profileForm.username" />
                </el-form-item>
                <el-form-item label="邮箱">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
                <el-form-item label="手机号">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
                <el-form-item label="个人简介">
                  <el-input
                    v-model="profileForm.bio"
                    type="textarea"
                    :rows="4"
                    placeholder="介绍一下你自己..."
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveProfile">保存修改</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="安全设置" name="security">
              <el-form :model="securityForm" label-width="100px">
                <el-form-item label="当前密码">
                  <el-input v-model="securityForm.currentPassword" type="password" show-password />
                </el-form-item>
                <el-form-item label="新密码">
                  <el-input v-model="securityForm.newPassword" type="password" show-password />
                </el-form-item>
                <el-form-item label="确认密码">
                  <el-input v-model="securityForm.confirmPassword" type="password" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="changePassword">修改密码</el-button>
                </el-form-item>
              </el-form>

              <el-divider />

              <div class="security-options">
                <div class="option-item">
                  <div class="option-info">
                    <h4>两步验证</h4>
                    <p>为您的账户增加额外的安全保护</p>
                  </div>
                  <el-switch v-model="twoFactorEnabled" />
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="学习偏好" name="preferences">
              <el-form label-width="120px">
                <el-form-item label="学习提醒">
                  <el-switch v-model="preferences.notifications" />
                  <span class="form-tip">每天推送学习提醒</span>
                </el-form-item>
                <el-form-item label="自动播放">
                  <el-switch v-model="preferences.autoPlay" />
                  <span class="form-tip">完成一节后自动播放下一节</span>
                </el-form-item>
                <el-form-item label="播放速度">
                  <el-select v-model="preferences.playbackSpeed">
                    <el-option label="0.75x" :value="0.75" />
                    <el-option label="1.0x" :value="1.0" />
                    <el-option label="1.25x" :value="1.25" />
                    <el-option label="1.5x" :value="1.5" />
                    <el-option label="2.0x" :value="2.0" />
                  </el-select>
                </el-form-item>
                <el-form-item label="字幕语言">
                  <el-select v-model="preferences.subtitleLang">
                    <el-option label="中文" value="zh" />
                    <el-option label="英文" value="en" />
                    <el-option label="无字幕" value="none" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="savePreferences">保存设置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Trophy } from '@element-plus/icons-vue'

const userStore = useUserStore()
const activeTab = ref('basic')

const profileForm = ref({
  username: userStore.user?.username || '',
  email: userStore.user?.email || '',
  phone: '',
  bio: ''
})

const securityForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const twoFactorEnabled = ref(false)

const preferences = ref({
  notifications: true,
  autoPlay: true,
  playbackSpeed: 1.0,
  subtitleLang: 'zh'
})

const saveProfile = () => {
  ElMessage.success('个人信息已更新')
}

const changePassword = () => {
  if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  ElMessage.success('密码已修改')
  securityForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

const savePreferences = () => {
  ElMessage.success('学习偏好已保存')
}
</script>

<style scoped>
.profile-page {
  max-width: 1400px;
  margin: 0 auto;
}

.profile-card {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-section {
  padding: 20px 0;
}

.user-info {
  padding: 20px 0;
}

.user-info h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.email {
  color: #909399;
  margin: 10px 0 15px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-item .value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-item .label {
  font-size: 13px;
  color: #909399;
}

.achievements-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.badge-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s;
}

.badge-item:hover {
  transform: scale(1.1);
}

.badge-item.locked {
  background: #f5f7fa;
  opacity: 0.5;
}

.settings-card {
  min-height: 600px;
}

.form-tip {
  margin-left: 10px;
  font-size: 13px;
  color: #909399;
}

.security-options {
  padding: 20px 0;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.option-info h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.option-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}
</style>
