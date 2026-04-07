import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Index',
    redirect: (to) => {
      const userStore = useUserStore()
      if (userStore.isLoggedIn) {
        const userType = userStore.user?.user_type || 'student'
        return userType === 'teacher' ? '/teacher-home' : '/student-home'
      }
      return '/login'
    }
  },
  {
    path: '/student-home',
    name: 'StudentHome',
    component: () => import('@/views/StudentHome.vue'),
    meta: { title: '学生端首页', requiresAuth: true, requiresRole: 'student', hideHeader: true, hideFooter: true }
  },
  {
    path: '/teacher-home',
    name: 'TeacherHome',
    component: () => import('@/views/TeacherHome.vue'),
    meta: { title: '教师端首页', requiresAuth: true, requiresRole: 'teacher', hideHeader: true, hideFooter: true }
  },
  {
    path: '/create-course',
    name: 'CreateCourse',
    component: () => import('@/views/CreateCourse.vue'),
    meta: { title: '创建课程', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/edit-course/:id',
    name: 'EditCourse',
    component: () => import('@/views/EditCourse.vue'),
    meta: { title: '编辑课程', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/my-courses',
    name: 'MyCourses',
    component: () => import('@/views/TeacherCourses.vue'),
    meta: { title: '我的课程', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/my-learning',
    name: 'MyLearning',
    component: () => import('@/views/MyLearning.vue'),
    meta: { title: '我的学习', requiresAuth: true, requiresRole: 'student' }
  },
  {
    path: '/search-courses',
    name: 'SearchCourses',
    component: () => import('@/views/SearchCourses.vue'),
    meta: { title: '搜索课程', requiresAuth: true, requiresRole: 'student' }
  },
  {
    path: '/course-requests',
    name: 'CourseRequests',
    component: () => import('@/views/CourseRequests.vue'),
    meta: { title: '课程申请管理', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/students',
    name: 'StudentsManagement',
    component: () => import('@/views/StudentsManagement.vue'),
    meta: { title: '学生管理', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/analytics',
    name: 'DataAnalysis',
    component: () => import('@/views/DataAnalysis.vue'),
    meta: { title: '数据分析', requiresAuth: true, requiresRole: 'teacher', hideHeader: true, hideFooter: true }
  },
  {
    path: '/course/:id',
    name: 'CourseDetail',
    component: () => import('@/views/CourseDetail.vue'),
    meta: { title: '课程详情', requiresAuth: true }
  },
  {
    path: '/course/:id/students',
    name: 'CourseStudents',
    component: () => import('@/views/CourseStudents.vue'),
    meta: { title: '课程学生管理', requiresAuth: true, requiresRole: 'teacher' }
  },
  {
    path: '/ai-tutor',
    name: 'AITutor',
    component: () => import('@/views/AITutor.vue'),
    meta: { title: 'AI学习助手', requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { title: '学习社区聊天室', requiresAuth: true }
  },
  {
    path: '/ai-colosseum',
    name: 'AIColosseum',
    component: () => import('@/views/AIColosseum.vue'),
    meta: { title: 'AI辩论场', requiresAuth: true, requiresRole: 'student' }
  },
  {
    path: '/quiz/:shareCode',
    name: 'QuizPage',
    component: () => import('@/views/QuizPage.vue'),
    meta: { title: 'Quiz答题', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', hideHeader: true, hideFooter: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', hideHeader: true, hideFooter: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  document.title = to.meta.title ? `${to.meta.title} - 校园智慧学习平台` : '校园智慧学习平台'
  
  // 如果有 token 但没有用户信息，尝试获取用户信息
  if (userStore.isLoggedIn && !userStore.user) {
    try {
      await userStore.fetchUserProfile()
    } catch (error) {
      // 如果获取用户信息失败，清除 token 并跳转到登录页
      console.error('获取用户信息失败，token 可能已过期')
      userStore.logout()
      if (to.path !== '/login' && to.path !== '/register') {
        next('/login')
        return
      }
    }
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }
  
  // 检查用户角色
  if (to.meta.requiresRole && userStore.isLoggedIn) {
    const userType = userStore.user?.user_type || 'student'
    if (to.meta.requiresRole !== userType) {
      // 角色不匹配，重定向到对应的首页
      const homePage = userType === 'teacher' ? '/teacher-home' : '/student-home'
      next(homePage)
      return
    }
  }
  
  next()
})

export default router
