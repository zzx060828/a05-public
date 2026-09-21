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
    beforeEnter: (to, from, next) => {
      const isLogin = localStorage.getItem('isLogin') === 'true'
      isLogin ? next() : next('/login')
    },
    meta: {
      requireLayout: true
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
  props: true // 将路由参数作为props传递
  },
  {
  path: '/report/:sessionId',
  name: 'ReportView',
  component: () => import('@/views/Report/ReportView.vue'),
  props: true // 将路由参数作为props传递
  },
    {
    path: '/bank',
    redirect: '/bank/all',
    name: 'Bank',
    component: BankView,
    meta: {
      requireLayout: true
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
      requireLayout: true
    }
  },
      {
    path: '/plan',
    name: 'Plan',
    component: PlanView,
    meta: {
      requireLayout: true
    }
  },
    {
    path: '/record',
    name: 'Record',
    component: RecordView,
    meta: {
      requireLayout: true
    }
  },
  {
  path: '/settings',
  name: 'Settings',
  component: () => import('@/views/Home/HomeView.vue') // 随便指一个或者建个空页面
  },
  {
  path: '/learning-path/:sessionId/:role',
  name: 'LearningPath',
  component: () => import('@/views/Record/LearningPath.vue'),
  props: true,
  query: { from: 'record' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router