<template>
  <el-config-provider :locale="elLocale">
  <div id="app">
    <el-container class="layout-container">
      <el-header v-if="!route.meta.hideHeader" class="header">
        <div class="logo">
          <el-icon :size="28"><School /></el-icon>
          <span>{{ t('common.platformTitle') }}</span>
        </div>
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          :ellipsis="false"
          @select="handleSelect"
          class="nav-menu"
        >
          <el-menu-item v-if="userStore.isLoggedIn && userStore.user" :index="homeRoute">
            {{ userStore.user.user_type === 'teacher' ? t('nav.teacherTitle').split(' - ')[1] : t('nav.studentTitle').split(' - ')[1] }}
          </el-menu-item>
          <el-menu-item index="/ai-tutor">{{ t('nav.aiTutor') }}</el-menu-item>
        </el-menu>
        <div class="user-area">
          <el-select
            v-model="currentLocale"
            size="small"
            style="width: 110px; margin-right: 12px;"
            @change="handleLocaleChange"
          >
            <el-option value="zh-cn" :label="t('language.zhCn')" />
            <el-option value="zh-tw" :label="t('language.zhTw')" />
            <el-option value="en" :label="t('language.en')" />
          </el-select>
          <el-button type="primary" @click="router.push('/login')" v-if="!userStore.isLoggedIn">
            {{ t('common.login') }}
          </el-button>
          <el-dropdown v-else>
            <span class="user-info">
              <el-avatar :size="32">{{ userStore.user.username?.charAt(0) }}</el-avatar>
              <span class="username">{{ userStore.user.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">{{ t('common.profile') }}</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">{{ t('common.logout') }}</el-dropdown-item>
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
        <p>© 2026 {{ t('common.platformTitle') }}</p>
      </el-footer>
    </el-container>
  </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElConfigProvider } from 'element-plus'
import elZhCn from 'element-plus/dist/locale/zh-cn.mjs'
import elZhTw from 'element-plus/dist/locale/zh-tw.mjs'
import elEn from 'element-plus/dist/locale/en.mjs'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { t, locale } = useI18n()

const currentLocale = ref(locale.value)

const elLocaleMap = { 'zh-cn': elZhCn, 'zh-tw': elZhTw, 'en': elEn }
const elLocale = computed(() => elLocaleMap[currentLocale.value] || elZhCn)

const handleLocaleChange = (lang) => {
  locale.value = lang
  currentLocale.value = lang
  localStorage.setItem('locale', lang)
}

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

/* 全局 Primary 按钮和交互元素样式 */
:deep(.el-button--primary) {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

:deep(.el-button--primary:hover) {
  background-color: #66b1ff !important;
  border-color: #66b1ff !important;
}

:deep(.el-button--primary:active) {
  background-color: #3a8ee6 !important;
  border-color: #3a8ee6 !important;
}

/* Primary link */
:deep(.el-button.is-text.is-link.el-button--primary) {
  color: #409EFF !important;
}

:deep(.el-button.is-text.is-link.el-button--primary:hover) {
  color: #66b1ff !important;
}

/* 其他UI元素 - Input focus, Tabs active 等 */
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

:deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: #409EFF !important;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF !important;
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
