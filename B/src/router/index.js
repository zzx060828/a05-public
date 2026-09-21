import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../components/MainLayout.vue'
import { useEnterpriseUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true, roles: ['enterprise'] },
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'campaigns',
        component: () => import('../views/Campaigns.vue'),
      },
      {
        path: 'candidates',
        component: () => import('../views/CandidateList.vue'),
      },
      {
        path: 'audit-detail',
        component: () => import('../views/AuditDetail.vue'),
      },
      {
        path: '/import-questions',
        name: 'ImportQuestions',
        component: () => import('../views/ImportQuestions.vue'),
        meta: { title: '导入题库与智能查重' }, // 如果你的系统有动态标题，可以加上这个
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const C_END_URL = import.meta.env.VITE_C_END_URL || 'http://localhost:5173'

const safeInternalRedirect = (value, fallback) =>
  typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    ? value
    : fallback

router.beforeEach((to) => {
  const userStore = useEnterpriseUserStore()

  if (to.path === '/login' && userStore.hasSession) {
    if (userStore.role === 'candidate') {
      window.location.assign(C_END_URL)
      return false
    }
    if (userStore.role === 'enterprise') {
      return safeInternalRedirect(to.query.redirect, '/dashboard')
    }
  }

  if (!to.matched.some((record) => record.meta.requiresAuth)) return true

  if (!userStore.hasSession) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  const allowedRoles = to.matched.flatMap((record) =>
    Array.isArray(record.meta.roles) ? record.meta.roles : [],
  )
  if (allowedRoles.length && !allowedRoles.includes(userStore.role)) {
    if (userStore.role === 'candidate') {
      window.location.assign(C_END_URL)
      return false
    }
    userStore.logout()
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
