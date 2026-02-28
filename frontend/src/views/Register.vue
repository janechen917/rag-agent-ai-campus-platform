<!-- 注册页面可以复用登录页面的设计 -->
<template>
  <div>
    <!-- 此页面可以重定向到登录页面的注册标签 -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.replace('/login')
})
</script>
