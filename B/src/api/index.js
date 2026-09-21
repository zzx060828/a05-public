import axios from 'axios'

let isRedirectingToLogin = false

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('hr_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    const isLoginRequest = err.config?.url?.includes('/auth/login')
    if (err.response?.status === 401 && !isLoginRequest && !isRedirectingToLogin) {
      isRedirectingToLogin = true
      localStorage.removeItem('hr_token')
      localStorage.removeItem('hr_role')
      localStorage.removeItem('hr_email')
      localStorage.removeItem('hr_company')
      const redirect = `${window.location.pathname}${window.location.search}`
      window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`)
    }
    return Promise.reject(err)
  }
)

// 岗位
export const getJobs = () => api.get('/jobs')
export const createJob = data => api.post('/jobs', data)

// 候选人
export const getCandidates = (jobId, page = 1, pageSize = 10) =>
  api.get(`/jobs/${jobId}/candidates`, { params: { page, page_size: pageSize } })
export const getCandidateReport = recordId =>
  api.get(`/records/${recordId}/report`)

// 认证
export const login = data => api.post('/auth/login', data)
export const register = data => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

// 题库导入
export const importCheck = file => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/questions/import-check', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const importConfirmed = data => api.post('/questions/import-confirmed', data)

export default api
