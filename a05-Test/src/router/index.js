import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/Home/HomeView.vue'
import InterviewView from '@/views/Interview/InterviewView.vue'
import Login from '@/views/Login/Login.vue'
import BankView from '@/views/Bank/BankView.vue'
import ProfileView from '@/views/Profile/ProfileView.vue'
import PlanView from '@/views/Plan/PlanView.vue'
import RecordView from '@/views/Record/RecordView.vue' 
import BankCollect from '@/views/Bank/BankCollect.vue'
import BankHistory from '@/views/Bank/BankHistory.vue'
import BankContent from '@/views/Bank/BankContent.vue';
import { useUserStore } from '@/stores/user'


/*import LoginView from '@/views/LoginView.vue'
    

 */

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      requireLayout: true
    }
  },
  {
    path: '/interview',
    name: 'Interview',
    component: InterviewView,
    meta: {
      requireLayout: true,
      requiresAuth: true,
      roles: ['candidate']
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requireLayout: true
    }
  },
  //后端对接
  {
 path: '/interview/session/:sessionId', 
  name: 'InterviewSession',
  component: () => import('@/views/Interview/Detail.vue'),
  props: true,
  meta: { requiresAuth: true, roles: ['candidate'] }
  },
  {
  path: '/report/:sessionId',
  name: 'ReportView',
  component: () => import('@/views/Report/ReportView.vue'),
  props: true,
  meta: { requiresAuth: true, roles: ['candidate'] }
  },
    {
    path: '/bank',
    redirect: '/bank/all',
    name: 'Bank',
    component: BankView,
    meta: {
      requireLayout: true,
      requiresAuth: true,
      roles: ['candidate']
    },
    children: [
        {
        path: '/bank/history',
        name: 'BankHistory',
        component: () => import('@/views/Bank/BankHistory.vue')
        },
        {
        path: '/bank/collect',
        name: 'BankCollect',
        component: BankCollect
        }, 
        {
        path: ':subject', 
        name: 'BankContent',
        component: () => import('@/views/Bank/BankContent.vue')
        },
      ]
  },
    {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: {
      requireLayout: true,
      requiresAuth: true,
      roles: ['candidate']
    }
  },
      {
    path: '/plan',
    name: 'Plan',
    component: PlanView,
    meta: {
      requireLayout: true,
      requiresAuth: true,
      roles: ['candidate']
    }
  },
    {
    path: '/record',
    name: 'Record',
    component: RecordView,
    meta: {
      requireLayout: true,
      requiresAuth: true,
      roles: ['candidate']
    }
  },
  {
  path: '/settings',
  name: 'Settings',
  component: () => import('@/views/Home/HomeView.vue'),
  meta: { requiresAuth: true, roles: ['candidate'] }
  },
  {
    path: '/start',
    name: 'CStart',
    component: () => import('@/views/Interview/CStart.vue'),
    meta: {
      requireLayout: false
    }
  },
  {
    path: '/learning-path/:sessionId/:role',
  name: 'LearningPath',
  component: () => import('@/views/Record/LearningPath.vue'),
  props: true,
  query: { from: 'record' },
  meta: { requiresAuth: true, roles: ['candidate'] }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

const B_END_URL = import.meta.env.VITE_B_END_URL || 'http://localhost:5174'

const safeInternalRedirect = (value, fallback) =>
  typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    ? value
    : fallback

router.beforeEach((to) => {
  const userStore = useUserStore()

  if (to.path === '/login' && userStore.hasSession) {
    if (userStore.role === 'enterprise') {
      window.location.assign(`${B_END_URL}/dashboard`)
      return false
    }
    if (userStore.role === 'candidate') {
      return safeInternalRedirect(to.query.redirect, '/')
    }
  }

  if (!to.meta.requiresAuth) return true

  if (!userStore.hasSession) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  const allowedRoles = Array.isArray(to.meta.roles) ? to.meta.roles : []
  if (allowedRoles.length && !allowedRoles.includes(userStore.role)) {
    if (userStore.role === 'enterprise') {
      window.location.assign(`${B_END_URL}/dashboard`)
      return false
    }
    userStore.logout()
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
