import { defineStore } from 'pinia'

let storageSyncInstalled = false

export const useEnterpriseUserStore = defineStore('enterprise-user', {
  state: () => ({
    token: localStorage.getItem('hr_token') || '',
    role: localStorage.getItem('hr_role') || '',
    profile: {
      email: localStorage.getItem('hr_email') || '',
      companyName: localStorage.getItem('hr_company') || '',
    },
  }),
  getters: {
    hasSession: (state) => Boolean(state.token),
    isAuthenticated: (state) => Boolean(state.token && state.role === 'enterprise'),
  },
  actions: {
    hydrateFromStorage() {
      this.token = localStorage.getItem('hr_token') || ''
      this.role = localStorage.getItem('hr_role') || ''
      this.profile.email = localStorage.getItem('hr_email') || ''
      this.profile.companyName = localStorage.getItem('hr_company') || ''
    },
    enableStorageSync() {
      if (storageSyncInstalled) return
      storageSyncInstalled = true
      window.addEventListener('storage', (event) => {
        if (['hr_token', 'hr_role', 'hr_email', 'hr_company'].includes(event.key)) {
          this.hydrateFromStorage()
        }
      })
    },
    setSession({ token, role, email }) {
      this.token = token
      this.role = role
      this.profile.email = email || ''
      localStorage.setItem('hr_token', token)
      localStorage.setItem('hr_role', role)
      localStorage.setItem('hr_email', this.profile.email)
    },
    setProfile(profile) {
      this.profile.email = profile.email || this.profile.email
      this.profile.companyName = profile.company_name || this.profile.companyName
      localStorage.setItem('hr_email', this.profile.email)
      localStorage.setItem('hr_company', this.profile.companyName)
    },
    logout() {
      this.token = ''
      this.role = ''
      this.profile = { email: '', companyName: '' }
      localStorage.removeItem('hr_token')
      localStorage.removeItem('hr_role')
      localStorage.removeItem('hr_email')
      localStorage.removeItem('hr_company')
    },
  },
})
