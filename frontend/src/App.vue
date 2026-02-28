<template>
  <div id="app">
    <el-container class="layout-container">
      <el-header v-if="!route.meta.hideHeader" class="header">
        <div class="logo">
          <el-icon :size="28"><School /></el-icon>
          <span>校园智慧学习平台</span>
        </div>
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          :ellipsis="false"
          @select="handleSelect"
          class="nav-menu"
        >
          <el-menu-item v-if="userStore.isLoggedIn && userStore.user" :index="homeRoute">
            {{ userStore.user.user_type === 'teacher' ? '教师端' : '学生端' }}
          </el-menu-item>
          <el-menu-item index="/ai-tutor">AI学习助手</el-menu-item>
        </el-menu>
        <div class="user-area">
          <el-button type="primary" @click="router.push('/login')" v-if="!userStore.isLoggedIn">
            登录
          </el-button>
          <el-dropdown v-else>
            <span class="user-info">
              <el-avatar :size="32">{{ userStore.user.username?.charAt(0) }}</el-avatar>
              <span class="username">{{ userStore.user.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <el-footer v-if="!route.meta.hideFooter" class="footer">
        <p>© 2026 校园智慧学习平台 - 让学习更智能、更高效</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)

const homeRoute = computed(() => {
  if (userStore.user?.user_type === 'teacher') {
    return '/teacher-home'
  }
  return '/student-home'
})

const handleSelect = (key) => {
  router.push(key)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  margin-right: 50px;
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-area {
  margin-left: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.footer {
  text-align: center;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  line-height: 60px;
  color: #909399;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
