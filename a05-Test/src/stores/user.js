import { defineStore } from 'pinia'

let storageSyncInstalled = false

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('userRole') || '',
    userInfo: {
      avatar: '/images/avatar.png',
      username: localStorage.getItem('username') || '未登录用户',
      userId: localStorage.getItem('userId') || '',
      registerDate: '2026-02-01', 
      skills: ["HTML", "CSS", "JavaScript", "Vue3", "TypeScript", "Node.js"] 
    }
  }),
  getters: {
    hasSession: (state) => Boolean(state.token),
    isLogin: (state) => Boolean(state.token && state.role === 'candidate'),
  },
  actions: {
    hydrateFromStorage() {
      this.token = localStorage.getItem('token') || ''
      this.role = localStorage.getItem('userRole') || ''
      this.userInfo.username = localStorage.getItem('username') || '未登录用户'
      this.userInfo.userId = localStorage.getItem('userId') || ''
    },
    enableStorageSync() {
      if (storageSyncInstalled) return
      storageSyncInstalled = true
      window.addEventListener('storage', (event) => {
        if (['token', 'userRole', 'username', 'userId', 'isLogin'].includes(event.key)) {
          this.hydrateFromStorage()
        }
      })
    },
    setSession({ token, role, username, userId }) {
      this.token = token
      this.role = role
      this.userInfo.username = username || '未登录用户'
      this.userInfo.userId = userId ? String(userId) : ''

      localStorage.setItem('token', token)
      localStorage.setItem('userRole', role)
      localStorage.setItem('username', this.userInfo.username)
      localStorage.setItem('userId', this.userInfo.userId)
      localStorage.setItem('isLogin', 'true')
    },
    logout() {
      this.token = ''
      this.role = ''
      this.userInfo.userId = ''
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('userRole')
      localStorage.removeItem('isLogin')
      localStorage.removeItem('username')
      this.userInfo.username = '未登录用户'
    },
    updateUserInfo(newInfo) {
     if (newInfo.username) this.userInfo.username = newInfo.username
      if (newInfo.avatar) this.userInfo.avatar = newInfo.avatar
      if (newInfo.skills) this.userInfo.skills = [...newInfo.skills]
      localStorage.setItem('username', this.userInfo.username)
    }
  }
})
