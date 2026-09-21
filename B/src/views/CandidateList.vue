<template>
  <div class="candidate-list-page">
    <header class="page-header">
      <div class="header-text">
        <h1 class="page-title">候选人追踪</h1>
        <p v-if="jobTitle" class="page-subtitle">{{ jobTitle }} {{ jobDept ? '· ' + jobDept : '' }}</p>
      </div>
    </header>

    <div v-if="loading" class="loading-text">加载中...</div>

    <div v-else-if="fetchError" class="error-box">
      <p>{{ fetchError }}</p>
      <button class="back-link" @click="$router.push('/campaigns')">← 返回场次管理</button>
    </div>

    <div v-else class="list-card animate-fade-in">
      <table v-if="candidates.length" class="data-table">
        <thead>
          <tr>
            <th>候选人</th>
            <th>匹配得分</th>
            <th>面试时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in candidates" :key="c.record_id">
            <td>{{ c.candidate_name }}</td>
            <td>
              <span class="score-badge" :class="scoreClass(c.score)">{{ c.score }} 分</span>
            </td>
            <td>{{ formatDate(c.generated_at) }}</td>
            <td>
              <button class="action-link" @click="viewDetail(c.record_id)">查看报告</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-text">暂无候选人数据</div>

      <div v-if="total > pageSize" class="pagination">
        <button :disabled="page <= 1" @click="page--; fetchCandidates()">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
        <button :disabled="page >= Math.ceil(total / pageSize)" @click="page++; fetchCandidates()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCandidates } from '@/api'

const route = useRoute()
const router = useRouter()

const jobId = ref(route.query.job_id || '')
const jobTitle = ref('')
const jobDept = ref('')
const candidates = ref([])
const loading = ref(true)
const fetchError = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

onMounted(() => {
  if (jobId.value) fetchCandidates()
  else { loading.value = false; fetchError.value = '缺少岗位ID参数，请从场次管理页面进入' }
})

async function fetchCandidates() {
  loading.value = true
  try {
    const res = await getCandidates(jobId.value, page.value, pageSize.value)
    const data = res.data || {}
    jobTitle.value = data.title || ''
    jobDept.value = data.department || ''
    total.value = data.total || 0
    candidates.value = (data.items || []).map(c => ({
      ...c,
      score: typeof c.score === 'number' ? Math.round(c.score) : (parseFloat(c.score) || 0)
    }))
  } catch (e) {
    const status = e.response?.status
    if (status === 404) fetchError.value = '未找到该岗位或无权访问'
    else if (status === 401) fetchError.value = '登录已过期，请重新登录'
    else fetchError.value = '加载失败：' + (e.response?.data?.detail || e.message || '网络错误')
  } finally {
    loading.value = false
  }
}

function scoreClass(s) {
  if (s >= 80) return 'score-high'
  if (s >= 60) return 'score-mid'
  return 'score-low'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function viewDetail(recordId) {
  router.push({ path: '/audit-detail', query: { record_id: recordId } })
}
</script>

<style scoped>
.candidate-list-page { padding: 40px; background-color: #f7f9fc; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
.page-header { margin-bottom: 32px; }
.page-title { margin: 0; font-size: 28px; color: #2c3e50; font-weight: 700; }
.page-subtitle { margin: 8px 0 0; font-size: 14px; color: #7d7d7d; }
.loading-text, .empty-text { text-align: center; color: #94a3b8; padding: 60px 0; font-size: 16px; }
.error-box { text-align: center; padding: 60px 0; color: #ef4444; font-size: 16px; background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
.back-link { display: inline-block; margin-top: 16px; background: none; border: none; color: #46a5c0; font-size: 14px; cursor: pointer; }
.list-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 12px 16px; font-size: 13px; color: #94a3b8; font-weight: 600; border-bottom: 2px solid #f1f5f9; }
.data-table td { padding: 16px; font-size: 14px; color: #334155; border-bottom: 1px solid #f8fafc; }
.score-badge { font-weight: 700; }
.score-high { color: #10b981; } .score-mid { color: #f59e0b; } .score-low { color: #ef4444; }
.action-link { background: transparent; border: none; color: #46a5c0; cursor: pointer; font-size: 14px; font-weight: 500; }
.action-link:hover { color: #ff8c42; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; }
.pagination button { padding: 6px 16px; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
</style>
