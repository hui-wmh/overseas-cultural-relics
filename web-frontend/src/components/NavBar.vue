<template>
  <div class="navbar">
    <div class="navbar-inner">
      <div class="logo" @click="router.push('/')">🏛️ 海外文物知识服务平台</div>
      <div class="nav-links">
        <span @click="router.push('/')">首页</span>
        <span @click="router.push('/artifacts')">文物浏览</span>
        <span @click="router.push('/graph')">知识图谱</span>
        <span @click="router.push('/timeline')">时间轴</span>
        <span @click="router.push('/map')">地图</span>
        <span @click="router.push('/dashboard')">统计看板</span>
        <span @click="router.push('/qa')">智能问答</span>
      </div>
      <div class="nav-right">
        <span v-if="userStore.isLoggedIn" @click="router.push('/profile')">{{ userStore.userInfo.nickname }}</span>
        <span v-else @click="router.push('/login')">登录</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
const router = useRouter()
const userStore = useUserStore()
</script>

<style scoped>
.navbar { background: #1a3a6b; color: white; padding: 0 24px; height: 56px; }
.navbar-inner { max-width: 1200px; margin: 0 auto; height: 100%; display: flex; align-items: center; gap: 32px; }
.logo { font-size: 18px; font-weight: bold; cursor: pointer; white-space: nowrap; }
.nav-links { display: flex; gap: 20px; flex: 1; }
.nav-links span, .nav-right span { cursor: pointer; font-size: 14px; opacity: 0.85; }
.nav-links span:hover, .nav-right span:hover { opacity: 1; }
</style>