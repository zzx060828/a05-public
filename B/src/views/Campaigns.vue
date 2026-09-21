<template>
  <div class="campaign-page">
    <header class="page-header">
      <div class="header-text">
        <h1 class="page-title">面试场次管理</h1>
        <p class="page-subtitle">配置 RAG 题库对齐用人标准 / Campaign Management</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="showCreate = true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          新建场次
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading-text">加载中...</div>

    <div v-else class="campaign-grid animate-fade-in">
      <div v-for="item in campaigns" :key="item.id" class="campaign-card" @click="goCandidates(item.id)">
        <div class="card-top">
          <span class="status-tag" :class="`status-${item.statusCode}`">
            <span class="status-dot"></span>
            {{ item.statusText }}
          </span>
          <span class="date-text">{{ item.date }}</span>
        </div>

        <h3 class="card-title">{{ item.title }}</h3>

        <div class="card-details">
          <div class="detail-row">
            <span class="label">部门</span>
            <span class="value highlight">{{ item.department }}</span>
          </div>
          <div class="detail-row">
            <span class="label">难度</span>
            <span class="value">{{ item.difficulty }}</span>
          </div>
          <div class="detail-row">
            <span class="label">CMCI 敏感度</span>
            <span class="value" :class="`cmci-${item.cmciLevel}`">{{ item.cmci }}</span>
          </div>
          <div class="detail-row">
            <span class="label">面试上限</span>
            <span class="value number">{{ item.maxParticipants }}</span>
          </div>
          <div class="detail-row" v-if="item.ragId">
            <span class="label">RAG 题库</span>
            <span class="value">{{ item.ragId }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button class="btn-outline-primary flex-1" @click.stop="copyLink(item)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
            复制专属链接
          </button>
        </div>
      </div>

      <div v-if="!campaigns.length" class="empty-text">暂无面试场次，点击"新建场次"创建</div>
    </div>

    <!-- 新建场次弹窗 -->
    <CreateCampaign
      :visible="showCreate"
      @update:visible="showCreate = $event"
      @create="handleCreate"
    />
    <div v-if="newLink" class="new-link-box">
      <p>创建成功！邀请链接：</p>
      <code>{{ newLink }}</code>
      <button class="btn-copy" @click="copyText(newLink)">复制链接</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getJobs, createJob } from '@/api'
import CreateCampaign from './CreateCampaign.vue'

const router = useRouter()

const campaigns = ref([])
const loading = ref(true)
const showCreate = ref(false)
const creating = ref(false)
const newLink = ref('')

const statusMap = { open: { code: 'active', text: '进行中' }, closed: { code: 'closed', text: '已结束' } }
const cmciLevel = v => v >= 0.8 ? 'high' : v >= 0.5 ? 'mid' : 'low'

onMounted(async () => {
  await fetchJobs()
})

async function fetchJobs() {
  loading.value = true
  try {
    const res = await getJobs()
    const jobs = res.data?.jobs || []
    campaigns.value = jobs.map(j => {
      const st = statusMap[j.status] || { code: 'pending', text: j.status }
      return {
        id: j.id,
        title: j.title,
        department: j.department || '未指定',
        difficulty: j.difficulty || 'Medium',
        statusCode: st.code,
        statusText: st.text,
        date: (j.created_at || '').split('T')[0],
        cmci: `${j.cmci_value?.toFixed(2) || '0.75'} (${cmciLevel(j.cmci_value) === 'high' ? '强预警' : cmciLevel(j.cmci_value) === 'mid' ? '中度' : '常规'})`,
        cmciLevel: cmciLevel(j.cmci_value),
        maxParticipants: j.max_participants || 50,
        ragId: j.rag_id || '',
        link: j.invitation_link
      }
    })
  } catch (e) {
    const msg = e.response?.data?.detail || e.message || '网络错误'
    alert('获取场次列表失败：' + msg)
  } finally {
    loading.value = false
  }
}

async function handleCreate(data) {
  creating.value = true
  try {
    const payload = {
      title: data.name,
      department: data.department,
      difficulty: data.difficulty,
      max_participants: data.total,
      cmci_value: data.cmci,
      rag_id: data.ragId
    }
    const res = await createJob(payload)
    newLink.value = res.data?.invitation_link || ''
    showCreate.value = false
    await fetchJobs()
  } catch (e) {
    const msg = e.response?.data?.detail || e.message || '网络错误'
    alert('创建失败：' + msg)
  } finally {
    creating.value = false
  }
}

function goCandidates(id) {
  router.push({ path: '/candidates', query: { job_id: id } })
}

function copyLink(item) {
  copyText(item.link)
}

function copyText(text) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败，请手动复制:\n' + text))
}
</script>

<style scoped>
.campaign-page { padding: 40px; background-color: #f7f9fc; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 32px; }
.page-title { margin: 0; font-size: 28px; color: #2c3e50; font-weight: 700; }
.page-subtitle { margin: 8px 0 0 0; font-size: 14px; color: #7d7d7d; }
.btn-primary { background: #ff8c42; color: white; border: none; padding: 12px 28px; border-radius: 45px; font-weight: 600; font-size: 15px; cursor: pointer; box-shadow: 0 8px 20px rgba(255, 140, 66, 0.25); display: flex; align-items: center; gap: 8px; transition: all 0.3s; }
.btn-primary:hover { background: #da6e2b; transform: translateY(-2px); }
.loading-text, .empty-text { text-align: center; color: #94a3b8; padding: 60px 0; font-size: 16px; }
.campaign-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }
.campaign-card { background: #fff; border-radius: 24px; padding: 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.3s; }
.campaign-card:hover { transform: translateY(-6px); box-shadow: 0 15px 35px rgba(0,0,0,0.06); }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.status-tag { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-active { background: #f0fdf4; color: #10b981; } .status-active .status-dot { background: #10b981; }
.status-pending { background: rgba(70,165,192,0.1); color: #46a5c0; } .status-pending .status-dot { background: #46a5c0; }
.status-closed { background: #f0f4f8; color: #7d7d7d; } .status-closed .status-dot { background: #7d7d7d; }
.date-text { font-size: 13px; color: #a0aec0; font-family: 'Courier New', monospace; }
.card-title { margin: 0 0 20px 0; font-size: 18px; color: #2c3e50; font-weight: 700; }
.card-details { border-top: 1px dashed #eef2f5; padding-top: 20px; display: flex; flex-direction: column; gap: 14px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
.label { color: #7d7d7d; }
.value { color: #2c3e50; font-weight: 500; } .value.highlight { font-weight: 600; } .value.number { font-weight: 700; }
.cmci-high { color: #ff8c42 !important; font-weight: 700; } .cmci-mid { color: #d97706; } .cmci-low { color: #46a5c0; }
.card-actions { margin-top: 24px; padding-top: 20px; border-top: 1px solid #f7f9fc; }
.btn-outline-primary { width: 100%; background: transparent; color: #46a5c0; border: 1px solid rgba(70,165,192,0.3); padding: 10px 0; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.3s; }
.btn-outline-primary:hover { background: rgba(70,165,192,0.05); border-color: #46a5c0; }

.new-link-box { margin-top: 20px; padding: 16px; background: #f0fdf4; border-radius: 8px; }
.new-link-box p { margin: 0 0 8px; font-size: 14px; color: #166534; }
.new-link-box code { display: block; word-break: break-all; font-size: 13px; color: #065f46; background: #d1fae5; padding: 8px; border-radius: 4px; margin-bottom: 8px; }
.btn-copy { padding: 6px 16px; background: #10b981; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
</style>
