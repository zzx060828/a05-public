<template>
  <header class="navbar">
    <div class="container">
      <!-- Logo -->
      <div class="logo" @click="goHome">
        <img src="/public/favicon.ico" alt=""> 面伴——你的专属面试官
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-links">
        <RouterLink 
          to="/" 
          class="nav-item"
          :class="{ active: $route.path === '/' }"
        >
          首页
        </RouterLink>
        <RouterLink 
          to="/bank/all" 
          class="nav-item"
          :class="{ active: $route.path.startsWith('/bank') }"
        >
          题库
        </RouterLink>
        <RouterLink 
          to="/record" 
          class="nav-item"
          :class="{ active: $route.path === '/record' }"
        >
          记录
        </RouterLink>
        <RouterLink 
          to="/plan" 
          class="nav-item"
          :class="{ active: $route.path === '/plan' }"
        >
          练习计划
        </RouterLink>

        <!--未登录-->
        <button v-if="!userStore.isLogin" class="cta-btn" @click="handleExperienceClick">
          开始体验
        </button>

        <!--已经登录-->
        <div v-else class="user-avatar">
          <div class="user-info" @click="handleAvatarClick">
            <router-link to="/profile">
              <img :src="userStore.userInfo.avatar" alt="用户头像" class="avatar-img">
            </router-link>
            <router-link to="/profile" class="username-link">
              <span class="username">{{ userStore.userInfo.username }}</span>
            </router-link>
          </div>
          <!-- 下拉盒：作为user-avatar的子元素 -->
          <div class="avatar-dropdown">
            <ul>
              <li><router-link to="/profile">个人中心</router-link></li>
              <li><router-link to="/settings">设置</router-link></li>
              <li @click="handleLogout" style="padding-left: 23px;">退出登录</li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// Logo 点击返回首页
const goHome = () => {
  router.push('/')
}

// 点击「立即体验」（未登录状态）：跳转到登录页
const handleExperienceClick = () => {
  router.push('/login')
}

// 点击头像：仅触发下拉盒显示（无需逻辑，hover已处理）
const handleAvatarClick = () => {}

// 退出登录逻辑（补充）
const handleLogout = () => {
  userStore.logout() // 假设你的store有退出方法
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  width: 100vw;
  color: #3984a4;
  background: white;
  height: 80px;
  border-bottom: 1px solid #e0e0e0; 
  z-index: 100;
}

.container {
  width: 100%;
  margin: 0 auto;
  padding: 18px 150px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center; 
  gap: 10px;
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
  letter-spacing: 1px;
}
.logo img{
  width: 35px;
  height: 35px;
}
.nav-links {
  display: flex;
  gap: 32px;
  align-items: center;
}

/* 导航项样式（保留你的原有逻辑） */
.nav-item {
  position: relative;
  padding: 5px 30px;
  border-radius: 35px;
  color: #6ec0e3;
  text-decoration: none;
  font-weight: 600;
  font-size: 18px;
  transition: color 0.5s;
  z-index: 1;
  cursor: pointer;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background: #6ec0e3;
  border-radius: 35px;
  transition: width 0.5s ease;
  z-index: -1;
}

.nav-item:hover::before,
.nav-item.active::before {
  width: 100%;
}

.nav-item.active,
.nav-item:hover {
  color: #ffffff;
}

.nav-links .cta-btn {
  background: #ff8c42;
  padding: 8px 18px;
  border-radius: 6px;
  font-weight: 600;
  transition: 0.3s;
  color: #ffffff;
  border: none;
  cursor: pointer;
}

.nav-links .cta-btn:hover {
  background: #ff8c42;
  color: #ffffff;
  transform: scale(1.2);
}

/* ========== 核心修复：头像和下拉盒样式 ========== */
.nav-links .user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  position: relative; /* 关键：作为下拉盒的定位参考！ */
  z-index: 9999; /* 确保下拉盒不被遮挡 */
}

.nav-links .user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.nav-links .avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: none;
}

.nav-links .username {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}


.username-link {
  text-decoration: none;
}

/* 下拉盒样式：核心修复定位和显示逻辑 */
.avatar-dropdown {
  position: absolute;
  top: calc(100% + 8px); 
  right: 0; 
  z-index: 9999;
  width: 120px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 8px 0;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
}

.avatar-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.avatar-dropdown li {
  padding: 0;
  margin: 0;
}

.avatar-dropdown li a,
.avatar-dropdown li {
  display: block;
  padding: 6px 12px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.avatar-dropdown li:hover {
  background-color: #f5f5f5;
}

.avatar-dropdown::before {
  content: "";
  position: absolute;
  /* 定位在盒子顶部居中 */
  top: -12px;       /* 向上偏移，大小为 border-width 的两倍左右 */
  left: 43px;
  transform: translateX(-50%);
  /* 核心：用 border 画三角形 */
  border-width: 6px; /* 三角形的大小 */
  border-style: solid;
  border-color: transparent transparent #ffffff transparent; 
}
/* 核心修复：hover user-avatar时显示下拉盒 */
.user-avatar:hover .avatar-dropdown {
  opacity: 1;
  visibility: visible; /* 只写一次，去掉重复的hidden */
}
</style>