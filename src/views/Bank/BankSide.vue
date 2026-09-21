<template>
  <aside class="sidebar">
    
    <nav class="sidebar-nav">
      
      <button 
        class="sidebar-item" 
        :class="{ active: currentSubject === 'all' || $route.path === '/bank' }"
        @click="goToSubject('all')"
      >
        <span class="icon">
          <svg t="1773233258488" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2102" width="200" height="200">
            <path d="M725.290667 725.290667m-213.333334 0a213.333333 213.333333 0 1 0 426.666667 0 213.333333 213.333333 0 1 0-426.666667 0Z" fill="#FFB531" p-id="2103"></path>
            <path d="M789.205333 234.794667m-149.333333 0a149.333333 149.333333 0 1 0 298.666667 0 149.333333 149.333333 0 1 0-298.666667 0Z" fill="#030835" p-id="2104"></path>
            <path d="M235.861333 788.138667m-149.333333 0a149.333333 149.333333 0 1 0 298.666667 0 149.333333 149.333333 0 1 0-298.666667 0Z" fill="#030835" p-id="2105"></path>
            <path d="M298.709333 298.709333m-213.333333 0a213.333333 213.333333 0 1 0 426.666667 0 213.333333 213.333333 0 1 0-426.666667 0Z" fill="#FFB531" p-id="2106"></path>
          </svg>
        </span>
        <span>全部</span>
      </button>

      <button 
        class="sidebar-item" 
        :class="{ active: currentSubject === 'java' }"
        @click="goToSubject('java')"
      >
        <span class="icon">
          <svg t="1773233111338" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1631" width="200" height="200">
            <path d="M938.666667 538.88V640a213.418667 213.418667 0 0 1-213.333334 213.333333H298.666667a213.418667 213.418667 0 0 1-213.333334-213.333333V384a213.418667 213.418667 0 0 1 213.333334-213.333333h20.48a169.557333 169.557333 0 0 1 142.506666 77.226666 169.472 169.472 0 0 0 142.506667 77.653334H725.333333a213.418667 213.418667 0 0 1 213.333334 213.333333z" fill="#FFB531" p-id="1632"></path>
            <path d="M659.882667 640a32.213333 32.213333 0 0 1-32 32h-232.106667a32 32 0 0 1 0-64h232.106667a32.213333 32.213333 0 0 1 32 32z" fill="#030835" p-id="1633"></path>
          </svg>
        </span>
        <span>Java题库</span>
      </button>

      <button 
        class="sidebar-item" 
        :class="{ active: currentSubject === 'python' }"
        @click="goToSubject('python')"
      >
        <span class="icon">
          <svg t="1773233111338" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1631" width="200" height="200">
            <path d="M938.666667 538.88V640a213.418667 213.418667 0 0 1-213.333334 213.333333H298.666667a213.418667 213.418667 0 0 1-213.333334-213.333333V384a213.418667 213.418667 0 0 1 213.333334-213.333333h20.48a169.557333 169.557333 0 0 1 142.506666 77.226666 169.472 169.472 0 0 0 142.506667 77.653334H725.333333a213.418667 213.418667 0 0 1 213.333334 213.333333z" fill="#FFB531" p-id="1632"></path>
            <path d="M659.882667 640a32.213333 32.213333 0 0 1-32 32h-232.106667a32 32 0 0 1 0-64h232.106667a32.213333 32.213333 0 0 1 32 32z" fill="#030835" p-id="1633"></path>
          </svg>
        </span>
        <span>Python题库</span>
      </button>

      <button 
        class="sidebar-item" 
        :class="{ active: currentSubject === 'frontend' }"
        @click="goToSubject('frontend')"
      >
        <span class="icon">
          <svg t="1773233111338" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1631" width="200" height="200">
            <path d="M938.666667 538.88V640a213.418667 213.418667 0 0 1-213.333334 213.333333H298.666667a213.418667 213.418667 0 0 1-213.333334-213.333333V384a213.418667 213.418667 0 0 1 213.333334-213.333333h20.48a169.557333 169.557333 0 0 1 142.506666 77.226666 169.472 169.472 0 0 0 142.506667 77.653334H725.333333a213.418667 213.418667 0 0 1 213.333334 213.333333z" fill="#FFB531" p-id="1632"></path>
            <path d="M659.882667 640a32.213333 32.213333 0 0 1-32 32h-232.106667a32 32 0 0 1 0-64h232.106667a32.213333 32.213333 0 0 1 32 32z" fill="#030835" p-id="1633"></path>
          </svg>
        </span>
        <span>前端题库</span>
      </button>

      <button class="sidebar-item" 
      :class="{ active: $route.path === '/bank/collect' }"
      @click="$router.push('/bank/collect')">
        <span class="icon">
          <svg t="1773233167466" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1788" width="200" height="200">
            <path d="M427.306667 884.181333L347.989333 927.573333a87.424 87.424 0 0 1-128.768-89.898666l18.218667-110.677334a172.629333 172.629333 0 0 0-47.488-149.162666l-79.658667-80.938667a86.613333 86.613333 0 0 1 49.493334-146.432l98.986666-14.976A174.933333 174.933333 0 0 0 390.741333 237.653333l51.285334-108.330666a77.525333 77.525333 0 0 1 139.861333 0l51.285333 108.330666a174.933333 174.933333 0 0 0 132.053334 97.834667l98.986666 14.976a86.613333 86.613333 0 0 1 49.450667 146.432l-79.658667 80.938667a172.629333 172.629333 0 0 0-47.488 149.162666l18.218667 110.677334a87.424 87.424 0 0 1-128.768 89.898666l-79.317333-43.434666a176.426667 176.426667 0 0 0-169.386667 0z" fill="#FFB531" p-id="1789"></path>
            <path d="M320.426667 572.501333a21.248 21.248 0 0 1-15.232-6.357333L257.792 517.973333a72.832 72.832 0 0 1 41.472-123.136l58.88-8.917333a82.645333 82.645333 0 0 0 62.421333-46.250667l30.506667-64.426666a67.498667 67.498667 0 0 1 121.813333 0l30.549334 64.426666a82.645333 82.645333 0 0 0 62.421333 46.250667 21.333333 21.333333 0 1 1-6.4 42.197333 125.226667 125.226667 0 0 1-94.634667-70.186666l-30.506666-64.426667a25.514667 25.514667 0 0 0-44.629334 0l-30.506666 64.426667a125.226667 125.226667 0 0 1-94.634667 70.186666l-58.88 8.917334a30.037333 30.037333 0 0 0-24.576 20.48 29.568 29.568 0 0 0 7.125333 30.549333l47.402667 48.170667a21.333333 21.333333 0 0 1-15.189333 36.266666z" fill="#030835" p-id="1790"></path>
          </svg>
        </span>
        <span>收藏</span>
      </button>

      <button class="sidebar-item" 
      :class="{ active: $route.path === '/bank/history' }"
      @click="$router.push('/bank/history')">
        <span class="icon">
          <svg t="1773233241182" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1945" width="200" height="200">
            <path d="M853.333333 401.493333V725.333333a213.418667 213.418667 0 0 1-213.333333 213.333334H384a213.418667 213.418667 0 0 1-213.333333-213.333334V298.666667a213.418667 213.418667 0 0 1 213.333333-213.333334h153.173333a214.869333 214.869333 0 0 1 151.04 62.293334l102.826667 103.253333A212.053333 212.053333 0 0 1 853.333333 401.493333z" fill="#FFB531" p-id="1946"></path>
            <path d="M726.613333 372.48a32.213333 32.213333 0 0 1-32 32h-43.52a117.546667 117.546667 0 0 1-117.333333-117.333333V243.626667a32 32 0 0 1 64 0v43.52a53.333333 53.333333 0 0 0 53.333333 53.333333h43.52a31.957333 31.957333 0 0 1 32 32zM634.026667 636.16a31.957333 31.957333 0 0 1-32 32H421.546667a32 32 0 0 1 0-64h180.48a31.957333 31.957333 0 0 1 32 32z" fill="#030835" p-id="1947"></path>
          </svg>
        </span>
        <span>浏览历史</span>
      </button>

      <div class="sidebar-avatar">
        <img src="/public/images/avatar.png" alt="">
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 🌟 动态获取当前路由参数，用来控制高亮
const currentSubject = computed(() => route.params.subject)

const goToSubject = (subject) => {
  // 把具体点了啥推到路由地址栏
  router.push(`/bank/${subject}`)
}
</script>

<style scoped>
/* 左侧边栏 */
.sidebar {
  width: 240px;
  height: calc(100vh - 80px);
  position: fixed;
  left: 0;top: 80px;
  background: white;
  padding: 24px 16px;
  border-right: 1px solid #e5e7eb;
}
.sidebar-search {
  display: flex;
  align-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 24px;
  position: relative;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
}
.search-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #67a3d7;
  cursor: pointer;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-bottom: 32px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}
.sidebar-item.active {
  background-color: #67a3d7;
  color: white;
}
.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.btn-primary {
  background-color: #67a3d7;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
}
.sidebar-dropdowns {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.dropdown-btn {
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 12px;
  text-align: left;
  cursor: pointer;
}
.sidebar-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.sidebar-avatar{
  position: absolute;
  bottom: 20px;
  left: 20px;
  border-radius: 50%;
}
.sidebar-avatar img{
  width: 40px;
  height: 40px;
  position: absolute;
  bottom: 10px;
  left: 7px;
  border-radius: 50%;
}
.icon{
  width: 26px;
  height: 26px;
}
</style>