import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLogin: localStorage.getItem('isLogin') === 'true',
    //从 localStorage 读取用户名，没有则显示默认值
    userInfo: {
      avatar: '/images/avatar.png',
      username: localStorage.getItem('username') || '未登录用户',
      registerDate: '2026-02-01', 
      skills: ["HTML", "CSS", "JavaScript", "Vue3", "TypeScript", "Node.js"] 
    }
  }),
  actions: {
    login() {
      this.isLogin = true
      localStorage.setItem('isLogin', 'true')     
      localStorage.setItem('username', this.userInfo.username)
    },
    logout() {
      this.isLogin = false
      localStorage.setItem('isLogin', 'false')
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