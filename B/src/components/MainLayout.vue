<template>
  <div class="layout-wrapper">
    <aside class="sidebar">
      <div class="logo-box">
        <img src="/public/favicon.ico" alt="Logo" class="logo" />
        <span class="logo-text">面伴</span>
      </div>

      <nav class="nav-menu">
        <router-link to="/dashboard" class="nav-item">
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          工作台看板
        </router-link>
        <router-link to="/campaigns" class="nav-item">
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          场次管理
        </router-link>
        <router-link to="/candidates" class="nav-item">
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          候选人追踪
        </router-link>
        <router-link to="/audit-detail" class="nav-item">
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          AI 审计报告
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <Transition name="menu-fade">
          <div
            v-show="showMenu"
            class="user-popover-menu"
            @mouseenter="handleMenuEnter"
            @mouseleave="handleMenuLeave"
            v-click-outside="handleClickOutside"
          >
            <div class="menu-header">
              <span class="menu-user-email">{{ userEmail || '未绑定邮箱' }}</span>
              <svg
                v-if="isLocked"
                class="lock-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M20 6L9 17l-5-5"></path>
              </svg>
            </div>

            <button class="menu-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              个人设置
            </button>

            <div class="menu-divider"></div>

            <button class="menu-item text-danger" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              退出登录
            </button>
          </div>
        </Transition>

        <div
          class="user-info"
          :class="{ 'menu-active': showMenu }"
          @mouseenter="handleTriggerEnter"
          @mouseleave="handleTriggerLeave"
          @click.stop="toggleLock"
        >
          <div class="avatar">HR</div>
          <div class="user-text">
            <div class="name">{{ userName }}</div>
            <div class="role">{{ userCompany }}</div>
          </div>
          <svg
            class="dropdown-icon"
            :class="{ rotated: showMenu }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
    </aside>

    <main class="main-container">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMe } from '@/api'
import { useEnterpriseUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useEnterpriseUserStore()

// --- 企业用户真实信息 ---
const userName = ref('企业管理员')
const userEmail = ref('')
const userCompany = ref('声貌智面')

onMounted(async () => {
  try {
    const res = await getMe()
    const data = res.data
    userStore.setProfile(data)
    if (data.company_name) userCompany.value = data.company_name
    if (data.email) userEmail.value = data.email
    if (data.company_name) userName.value = data.company_name
  } catch (e) {
    // token 失效或网络错误，保持默认值
  }
})

// --- 🌟 核心状态逻辑 ---
const isHovering = ref(false)
const isLocked = ref(false)

// 只要处于 hover 或者锁定状态之一，菜单就显示
const showMenu = computed(() => isHovering.value || isLocked.value)

// 鼠标进入触发区（头像盒子）
const handleTriggerEnter = () => {
  isHovering.value = true
}

// 鼠标离开触发区
const handleTriggerLeave = () => {
  // 我们延迟一小会儿，防止鼠标移向菜单的过程中菜单消失
  setTimeout(() => {
    isHovering.value = false
  }, 100)
}

// 鼠标进入菜单区 (保持 hover 状态为 true)
const handleMenuEnter = () => {
  isHovering.value = true
}

// 鼠标离开菜单区
const handleMenuLeave = () => {
  isHovering.value = false
}

// 点击头像区域：切换锁定状态
const toggleLock = () => {
  isLocked.value = !isLocked.value
}

// 点击屏幕其他区域：取消锁定并关闭菜单
const handleClickOutside = () => {
  if (isLocked.value) {
    isLocked.value = false
    isHovering.value = false // 确保彻底关闭
  }
}

// --- 业务逻辑 ---
const handleLogout = () => {
  if (confirm('确定要退出当前企业账号吗？')) {
    userStore.logout()
    router.push('/login')
  }
}

// --- 🌟 自定义指令：处理点击外部 ---
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function (event) {
      // 检查点击的元素是不是弹窗本身，或者是不是触发按钮(头像盒子)
      // 如果都不是，说明点击了外部
      const triggerEl = document.querySelector('.user-info')
      if (!(el === event.target || el.contains(event.target) || triggerEl.contains(event.target))) {
        binding.value(event)
      }
    }
    document.body.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.clickOutsideEvent)
  },
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f7f9fc;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}
.sidebar {
  width: 260px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 32px 20px 24px;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
  border-right: 1px solid #eef2f5;
  z-index: 10;
  position: relative;
}
.logo-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px 40px;
}
.logo {
  width: 36px;
  height: 36px;
}
.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  color: #7d7d7d;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-size: 15px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}
.nav-icon {
  width: 20px;
  height: 20px;
  transition: color 0.3s ease;
}
.nav-item:hover {
  background: #f7f9fc;
  color: #46a5c0;
}
.router-link-active {
  background: rgba(70, 165, 192, 0.08) !important;
  color: #46a5c0 !important;
  font-weight: 600;
}
.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: #46a5c0;
  border-radius: 0 4px 4px 0;
}
.sidebar-footer {
  padding-top: 16px;
  position: relative;
}

/* ================= 用户信息卡片 ================= */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f7f9fc;
  border-radius: 14px;
  border: 1px solid #eef2f5;
  transition: all 0.3s;
  cursor: pointer;
  user-select: none;
}
.user-info:hover,
.user-info.menu-active {
  border-color: #46a5c0;
  background: #fff;
  box-shadow: 0 4px 12px rgba(70, 165, 192, 0.08);
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6ec6df, #46a5c0);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}
.user-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.user-text .name {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}
.user-text .role {
  font-size: 12px;
  color: #a0aec0;
}
.dropdown-icon {
  width: 16px;
  height: 16px;
  color: #a0aec0;
  transition: transform 0.3s;
}
.dropdown-icon.rotated {
  transform: rotate(180deg);
  color: #46a5c0;
}

/* ================= 弹出菜单 ================= */
.user-popover-menu {
  position: absolute;
  bottom: 80px;
  left: 0;
  width: 100%;
  background: #ffffff;
  border-radius: 16px;
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.08),
    0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  padding: 8px;
  display: flex;
  flex-direction: column;
  z-index: 100;
}
.user-popover-menu::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 24px;
  width: 12px;
  height: 12px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
  transform: rotate(45deg);
}

.menu-header {
  padding: 8px 12px 12px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.menu-user-email {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}
/* 将锁换成了低调的绿色勾 */
.lock-icon {
  width: 14px;
  height: 14px;
  color: #10b981;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.menu-item svg {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}
.menu-item:hover {
  background: #f8fafc;
  color: #1e293b;
}
.menu-item:hover svg {
  opacity: 1;
}

.text-danger:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
}
.text-danger:hover svg {
  color: #ef4444;
}

.menu-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 4px 0;
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}
.main-container {
  flex: 1;
  overflow-y: auto;
  position: relative;
  background: #f7f9fc;
}
</style>
