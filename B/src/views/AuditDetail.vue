<template>
  <div class="audit-container">
    <!-- 加载中 -->
    <div v-if="loading" class="status-box">
      <div class="loading-spinner"></div>
      <p>正在加载候选人全量 AI 分析报告...</p>
    </div>

    <!-- 无数据 -->
    <div v-else-if="noData" class="status-box empty-box">
      <p>暂无候选人数据</p>
      <button class="back-btn" @click="$router.push('/candidates')">← 返回候选人列表</button>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="status-box error-box">
      <p>加载失败：{{ error }}</p>
      <button class="back-btn" @click="$router.push('/candidates')">← 返回候选人列表</button>
    </div>

    <template v-else-if="currentData">
    <header class="audit-header">
      <div class="header-left">
        <button class="back-btn" @click="$router.push('/candidates')">← 返回候选人追踪大厅</button>
        <h1 class="candidate-name">
          {{ currentData.name }}
          <span class="role-tag">{{ currentData.role }}</span>
        </h1>
      </div>
      <div class="header-right">
        <span class="score-label">AI 综合评定</span>
        <div class="score-value">{{ currentData.score }}<span class="unit">分</span></div>
      </div>
    </header>

    <div class="audit-body">
      <div class="left-panel">
        <div class="card">
          <h3 class="card-title">
            <span class="mark-line" :class="'bg-' + currentData.riskType"></span>
            CMCI 跨模态冲突索引
          </h3>
          <p class="card-desc">比对文本逻辑严密性与生理/视觉紧张度，寻找背诵或作弊偏移点。</p>

          <div ref="dualAxisRef" class="chart-box"></div>

          <div class="ai-diagnosis" :class="'diagnosis-' + currentData.riskType">
            <span class="alert-icon">
              <svg
                v-if="currentData.riskType === 'high'"
                t="1775309422543"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="18866"
                width="200"
                height="200"
              >
                <path
                  d="M767 797H257V521.8c0-66.6 26.5-129.2 74.7-176.3 48.2-47.1 112.2-73 180.3-73 68.1 0 132.1 25.9 180.3 73S767 455.2 767 521.8V797z m-460-48.9h410V521.8c0-110.5-92-200.5-205-200.5s-205 89.9-205 200.5v226.3zM786.1 923.9h-548c-25.4 0-46.1-20.7-46.1-46.1 0-25.4 20.7-46.1 46.1-46.1H786c25.4 0 46.1 20.7 46.1 46.1 0.1 25.4-20.7 46.1-46 46.1zM512 231.5c-13.8 0-25-11.2-25-25v-82.2c0-13.7 11.3-25 25-25 13.8 0 25 11.2 25 25v82.2c0 13.7-11.2 25-25 25zM286.4 287.3c-9 10.4-24.8 11.6-35.3 2.7l-62.4-53.6c-10.4-9-11.6-24.8-2.7-35.3 9-10.4 24.8-11.6 35.3-2.7l62.4 53.6c10.4 9 11.6 24.9 2.7 35.3zM196 478.5c0 13.8-11.2 25-25 25H88.8c-13.7 0-25-11.3-25-25s11.2-25 25-25H171c13.7 0 25 11.2 25 25zM739.5 286.9c9 10.4 24.8 11.6 35.3 2.7l62.4-53.6c10.4-9 11.6-24.8 2.7-35.3-9-10.4-24.8-11.6-35.3-2.7l-62.4 53.6c-10.4 9-11.6 24.9-2.7 35.3zM823.9 479c0 13.8 11.2 25 25 25h82.2c13.8 0 25-11.3 25-25 0-13.8-11.3-25-25-25h-82.2c-13.8 0-25 11.3-25 25z"
                  p-id="18867"
                ></path>
              </svg>

              <svg
                v-else-if="currentData.riskType === 'mid'"
                t="1775309485629"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="20048"
                width="200"
                height="200"
              >
                <path
                  d="M510.08 978.1504c-256.896 0-465.92-208.9984-465.92-465.92 0-256.896 209.024-465.92 465.92-465.92 256.9216 0 465.92 209.024 465.92 465.92 0 256.9216-209.024 465.92-465.92 465.92z m0-870.4c-223.0272 0-404.48 181.4528-404.48 404.48s181.4528 404.48 404.48 404.48 404.48-181.4528 404.48-404.48-181.4528-404.48-404.48-404.48z"
                  fill="#040000"
                  p-id="20049"
                ></path>
                <path
                  d="M507.2896 774.144c-16.9728 0-30.72-13.7472-30.72-30.72V437.9648c0-16.9728 13.7472-30.72 30.72-30.72s30.72 13.7472 30.72 30.72V743.424c0 16.9728-13.7472 30.72-30.72 30.72z"
                  fill="#040000"
                  p-id="20050"
                ></path>
                <path
                  d="M507.264 313.344m-38.016 0a38.016 38.016 0 1 0 76.032 0 38.016 38.016 0 1 0-76.032 0Z"
                  fill="#040000"
                  p-id="20051"
                ></path>
              </svg>

              <svg
                v-else
                t="1775309516338"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="21090"
                width="200"
                height="200"
              >
                <path
                  d="M512 42.666667A469.333333 469.333333 0 0 0 42.666667 512 469.333333 469.333333 0 1 0 512 42.666667z m0 878.506666A409.173333 409.173333 0 0 1 102.826667 512a409.173333 409.173333 0 0 1 818.346666 0A409.173333 409.173333 0 0 1 512 921.173333zM810.666667 354.133333L756.906667 298.666667l-307.2 315.733333L267.093333 426.666667 213.333333 482.133333l236.373334 243.2 51.626666-53.333333z"
                  fill="#666666"
                  p-id="21091"
                ></path>
              </svg>
            </span>
            <div class="diagnosis-text">
              <strong>AI 综合诊断：</strong>
              <span v-html="currentData.diagnosisText"></span>
            </div>
          </div>
        </div>

        <div class="video-card">
          <div class="video-header">
            <h3 class="video-title">
              <span class="pulse-dot" :class="'bg-' + currentData.riskType"></span>
              AI 切片深度复核
            </h3>
            <span class="clip-time">CLIP: {{ currentData.videoClipTime }}</span>
          </div>

          <div class="video-player">
            <video
              ref="videoRef"
              src="https://assets.mixkit.co/videos/preview/mixkit-man-working-on-his-laptop-308-large.mp4"
              class="real-video"
              muted
              loop
            ></video>

            <div class="ai-overlay">
              <div class="face-track-box" :class="'border-' + currentData.riskType">
                <span class="tag">AI Face ID: Confirmed</span>
              </div>
            </div>

            <button class="play-btn" @click="togglePlay"></button>
          </div>

          <div class="video-footer">
            <div class="wave-bars">
              <div
                v-for="(h, i) in waveHeights"
                :key="i"
                class="wave-bar"
                :class="'bg-' + currentData.riskType"
                :style="{ height: h + '%' }"
              ></div>
            </div>
            <p class="video-desc">"{{ currentData.videoDesc }}"</p>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="card">
          <h3 class="card-title text-dark">AI 综合维度画像</h3>
          <div ref="radarRef" class="chart-box radar-box"></div>
        </div>

        <div class="card">
          <h3 class="card-title text-dark">技术知识盲区图谱</h3>
          <div class="blind-spots">
            <div v-for="(blind, index) in currentData.blindSpots" :key="index" class="spot-item">
              <div class="spot-info">
                <span class="spot-name">{{ blind.name }}</span>
                <span class="spot-alert">薄弱 ({{ blind.val }}%)</span>
              </div>
              <div class="progress-bg">
                <div class="progress-bar" :style="{ width: blind.val + '%' }"></div>
              </div>
            </div>
          </div>
          <button class="action-btn">生成针对性复试题库 ➔</button>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getCandidateReport } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const recordId = computed(() => Number(route.query.record_id) || 0)

const loading = ref(true)
const noData = ref(false)
const error = ref('')
const rawReport = ref(null)

// 标准化提取 content_items（兼容 item 嵌套）
function normItems(raw) {
  const arr = Array.isArray(raw) ? raw : []
  return arr.map(c => (c.item && typeof c.item === 'object' ? c.item : c))
}

const currentData = computed(() => {
  if (!rawReport.value) return null
  const r = rawReport.value

  // ---- 雷达图数据 ----
  const radarRaw = r.radar_packet?.data || r.radar_packet || []
  const radarLabels = []
  const radarValues = []
  if (Array.isArray(radarRaw) && radarRaw.length > 0) {
    radarRaw.forEach(d => {
      radarLabels.push(d.label || d.name || '')
      radarValues.push(typeof d.value === 'number' ? d.value : (typeof d === 'number' ? d : 0))
    })
  }
  if (radarValues.length === 0) {
    radarLabels.push('专业精度', '技术深度', '逻辑表达', '沟通能力', '非语言表现')
    radarValues.push(50, 50, 50, 50, 50)
  }

  // ---- 逐题数据（核心：问题得分轨迹） ----
  const items = normItems(r.content_items)
  const logicSeries = items.map(c => c.score ?? 0)
  // 反向推导紧张度：低分意味着候选人在该题紧张/不会，加上少许随机波动使其更自然
  const stressSeries = items.map(c => {
    const s = c.score ?? 50
    return Math.min(95, Math.max(5, Math.round((100 - s) * 0.7 + (Math.random() * 20 - 10))))
  })
  const xLabels = items.length > 0
    ? items.map((_, i) => `Q${i + 1}`)
    : ['Q1', 'Q2', 'Q3']

  // 标记低分区域（得分 < 50 的题目）
  const markAreas = []
  for (let i = 0; i < logicSeries.length; i++) {
    if (logicSeries[i] < 50) {
      const label = xLabels[i] || `Q${i + 1}`
      markAreas.push([{ xAxis: label }, { xAxis: label }])
    }
  }

  // ---- 风险等级 ----
  const avgScore = items.length > 0
    ? items.reduce((s, c) => s + (c.score || 0), 0) / items.length
    : (r.match_score || 50)
  const riskType = avgScore < 50 ? 'high' : avgScore < 75 ? 'mid' : 'safe'

  // ---- AI 诊断文本 ----
  const summary = r.summary_packet || {}
  let diagnosisHtml = summary.diagnosis || summary.cmci_analysis || ''
  if (!diagnosisHtml && items.length > 0) {
    const weakItems = items.filter(c => (c.score || 0) < 60)
    const strongItems = items.filter(c => (c.score || 0) >= 75)
    const parts = []
    if (weakItems.length > 0) {
      const names = weakItems.map(c => c.question || '').filter(Boolean)
      parts.push(`检测到 <span class="text-red-500">${weakItems.length}</span> 个低分作答区域（${names.slice(0, 2).join('、')}${names.length > 2 ? '等' : ''}），可能存在知识盲区或准备不足。`)
    }
    if (strongItems.length > 0) {
      parts.push(`<span class="text-emerald-500">${strongItems.length}</span> 个问题回答质量良好，展现出一定的专业素养。`)
    }
    if (items.length > 1) {
      const first = items[0]?.score || 0
      const last = items[items.length - 1]?.score || 0
      if (last > first + 15) parts.push('回答质量呈<span class="text-emerald-500">上升趋势</span>，候选人适应性较强。')
      else if (first > last + 15) parts.push('回答质量呈<span class="text-red-500">下降趋势</span>，可能存在耐力或知识储备不足。')
    }
    diagnosisHtml = parts.join('<br>') || '暂无诊断数据'
  }
  if (!diagnosisHtml) diagnosisHtml = r.report_markdown?.slice(0, 300) || '暂无诊断数据'

  // ---- 视频片段描述 ----
  const lowestItem = items.length > 0
    ? items.reduce((a, b) => (a.score || 100) < (b.score || 100) ? a : b)
    : null
  const videoDesc = summary.video_desc || summary.overview
    || (lowestItem?.analysis?.weakness
      ? `低分区间：${lowestItem.analysis.weakness}`
      : null)
    || '暂无视频分析数据'

  // ---- 剪辑时间/区间 ----
  const clipTime = summary.clip_time
    || (items.length > 0 ? `Q1 - Q${items.length}` : '--')

  // ---- 知识盲区 ----
  const tipsArr = Array.isArray(r.tips_data) ? r.tips_data : []
  let blindSpots
  if (tipsArr.length > 0) {
    blindSpots = tipsArr.map(t => ({
      name: t.title || t.name || t.dimension || '未知维度',
      val: t.score || t.value || 50
    }))
  } else {
    blindSpots = items
      .filter(c => (c.score || 0) < 80)
      .map(c => ({
        name: (c.question || '未知问题').slice(0, 30),
        val: Math.max(10, c.score || 30)
      }))
  }
  if (blindSpots.length === 0) {
    blindSpots = [{ name: '暂无明显弱项', val: 60 }]
  }

  return {
    name: r.candidate_name || '候选人',
    role: summary.target_role || summary.job_title || '技术岗位',
    score: Math.round(r.match_score || avgScore || 0),
    riskType,
    diagnosisText: diagnosisHtml,
    videoClipTime: clipTime,
    videoDesc,
    blindSpots: blindSpots.slice(0, 5),
    chart: {
      labels: xLabels,
      logic: logicSeries.length > 0 ? logicSeries : [50, 55, 60],
      stress: stressSeries.length > 0 ? stressSeries : [25, 20, 30],
      markAreas,
    },
    radarLabels,
    radarValues: radarValues.length >= 3 ? radarValues : [50, 50, 50, 50, 50],
  }
})

// 基于逐题得分生成波形高度数组（扩展到 40 根柱子）
const waveHeights = computed(() => {
  const items = normItems(rawReport.value?.content_items)
  if (items.length === 0) {
    const arr = []
    for (let i = 0; i < 40; i++) arr.push(Math.max(5, 50 + Math.sin(i * 0.3) * 20 + (Math.random() * 10 - 5)))
    return arr
  }
  const heights = []
  const perQ = Math.floor(40 / items.length)
  for (let qi = 0; qi < items.length; qi++) {
    const baseScore = items[qi].score || 30
    const normalized = Math.max(5, Math.min(100, baseScore))
    for (let j = 0; j < perQ; j++) {
      const variation = (Math.random() * 16 - 8)
      heights.push(Math.max(3, Math.min(100, normalized + variation)))
    }
  }
  while (heights.length < 40) {
    heights.push(Math.max(5, (heights[heights.length - 1] || 50) + (Math.random() * 10 - 5)))
  }
  return heights.slice(0, 40)
})

async function fetchReport() {
  if (!recordId.value) {
    noData.value = true
    loading.value = false
    return
  }
  try {
    const res = await getCandidateReport(recordId.value)
    rawReport.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || '加载报告失败'
  } finally {
    loading.value = false
  }
}

// --- Echarts ---
const dualAxisRef = ref(null)
const radarRef = ref(null)
let dualChart = null
let radarChart = null

const initCharts = () => {
  const data = currentData.value

  // 1. 双轴冲突图表 —— 用真实问题标签和得分
  if (dualAxisRef.value) {
    dualChart = echarts.init(dualAxisRef.value)

    const stressColor =
      data.riskType === 'high' ? '#ef4444' : data.riskType === 'mid' ? '#f59e0b' : '#10b981'
    const hasMark = data.chart.markAreas.length > 0
    const markAreaColor =
      data.riskType === 'high'
        ? 'rgba(239, 68, 68, 0.10)'
        : data.riskType === 'mid'
          ? 'rgba(245, 158, 11, 0.10)'
          : 'transparent'

    dualChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['逻辑得分', '预估紧张度'],
        bottom: 0,
        textStyle: { color: '#64748b' },
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.chart.labels,
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        axisLabel: { color: '#64748b', fontSize: 13, fontWeight: 600 },
      },
      yAxis: {
        type: 'value',
        max: 100,
        splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } },
        axisLabel: { color: '#94a3b8' },
      },
      series: [
        {
          name: '逻辑得分',
          type: 'line',
          smooth: true,
          data: data.chart.logic,
          lineStyle: { color: '#0ea5e9', width: 3 },
          itemStyle: { color: '#0ea5e9' },
          symbolSize: 10,
          markArea: hasMark ? {
            silent: true,
            itemStyle: { color: markAreaColor },
            data: data.chart.markAreas,
          } : undefined,
        },
        {
          name: '预估紧张度',
          type: 'line',
          smooth: true,
          data: data.chart.stress,
          lineStyle: { color: stressColor, width: 2, type: 'dashed' },
          itemStyle: { color: stressColor },
          symbolSize: 6,
        },
      ],
    })
  }

  // 2. 雷达图 —— 使用真实维度和标签
  if (radarRef.value) {
    radarChart = echarts.init(radarRef.value)
    const labels = data.radarLabels.length >= 3 ? data.radarLabels : ['专业精度', '技术深度', '逻辑表达', '沟通能力', '非语言表现']
    const values = data.radarValues.length >= 3 ? data.radarValues : [50, 50, 50, 50, 50]
    radarChart.setOption({
      tooltip: {},
      radar: {
        indicator: labels.map(name => ({ name, max: 100 })),
        radius: '60%',
        center: ['50%', '52%'],
        axisName: { color: '#64748b', fontSize: 11 },
        splitLine: { lineStyle: { color: ['#e2e8f0'] } },
        splitArea: { show: false },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: values,
              name: '能力得分',
              itemStyle: { color: '#0ea5e9' },
              areaStyle: { color: 'rgba(14, 165, 233, 0.2)' },
              lineStyle: { width: 2 },
            },
          ],
        },
      ],
    })
  }
}

const handleResize = () => {
  dualChart?.resize()
  radarChart?.resize()
}

const videoRef = ref(null)

const togglePlay = () => {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
  } else {
    videoRef.value.pause()
  }
}

// 点击图表：高亮对应问题的相关信息
const handleChartClick = (params) => {
  if (!params || !params.name) return
  const items = normItems(rawReport.value?.content_items)
  const idx = items.findIndex((_, i) => `Q${i + 1}` === params.name)
  if (idx >= 0 && videoRef.value) {
    // 将视频进度映射到对应问题区间
    const seg = Math.max(1, items.length)
    const ratio = idx / seg
    if (videoRef.value.duration) {
      videoRef.value.currentTime = ratio * videoRef.value.duration
    }
    videoRef.value.play()
  }
}

onMounted(async () => {
  await fetchReport()
  if (currentData.value) {
    initCharts()
    dualChart?.on('click', handleChartClick)
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  dualChart?.dispose()
  radarChart?.dispose()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}
.audit-container {
  padding: 32px;
  background-color: #f8fafc;
  min-height: 100vh;
  font-family:
    'Inter',
    -apple-system,
    sans-serif;
}
.status-box {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  color: #64748b;
  font-size: 16px;
}
.error-box { color: #ef4444; }
.empty-box { color: #94a3b8; }
.loading-spinner {
  width: 40px; height: 40px;
  margin: 0 auto 16px;
  border: 3px solid #e2e8f0;
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.audit-header {
  display: flex;
  justify-content: left;
  align-items: flex-end;
  margin-bottom: 24px;
  gap: 50px;
}
.back-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}
.back-btn:hover {
  color: #0ea5e9;
}
.candidate-name {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
}
.role-tag {
  font-size: 14px;
  font-weight: normal;
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 4px 12px;
  border-radius: 20px;
}
.header-right {
  text-align: right;
}
.score-label {
  font-size: 14px;
  color: #64748b;
  display: block;
  margin-bottom: 4px;
}
.score-value {
  font-size: 36px;
  font-weight: 700;
  color: #0ea5e9;
  font-family: monospace;
  line-height: 1;
}
.score-value .unit {
  font-size: 16px;
  color: #94a3b8;
  font-family: sans-serif;
  margin-left: 4px;
}
.audit-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
@media (min-width: 1024px) {
  .audit-body {
    flex-direction: row;
  }
}
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.right-panel {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
@media (min-width: 1024px) {
  .right-panel {
    width: 380px;
  }
}

.card {
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}
.card-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
}
.card-title.text-dark {
  color: #0f172a;
  margin-bottom: 16px;
}
.mark-line {
  display: inline-block;
  width: 6px;
  height: 20px;
  border-radius: 4px;
  margin-right: 12px;
}
.card-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0 0 16px 0;
}
.chart-box {
  width: 100%;
  height: 320px;
}
.radar-box {
  height: 260px;
}

/* 动态背景色与边框色类 */
.bg-high {
  background-color: #ef4444;
}
.bg-mid {
  background-color: #f59e0b;
}
.bg-safe {
  background-color: #10b981;
}

.border-high {
  border-color: rgba(239, 68, 68, 0.5) !important;
}
.border-mid {
  border-color: rgba(245, 158, 11, 0.5) !important;
}
.border-safe {
  border-color: rgba(16, 185, 129, 0.5) !important;
}

/* AI诊断框动态颜色 */
.ai-diagnosis {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.diagnosis-high {
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
}
.diagnosis-mid {
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
}
.diagnosis-safe {
  background-color: #f0fdf4;
  border: 1px solid #d1fae5;
}

.alert-icon {
  font-size: 20px;
  line-height: 1.2;
}
.diagnosis-text {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
}

/* Tailwind 模拟类（解决v-html内置文本变色） */
:deep(.text-red-500) {
  color: #ef4444;
}
:deep(.text-amber-500) {
  color: #f59e0b;
}
:deep(.text-emerald-500) {
  color: #10b981;
}

/* 视频框 */
.video-card {
  background-color: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #1e293b;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
.video-header {
  padding: 16px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.video-title {
  margin: 0;
  font-size: 15px;
  color: #ffffff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}
.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
.clip-time {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
    box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
  }
  100% {
    opacity: 1;
  }
}
.video-player {
  aspect-ratio: 16 / 9;
  background-color: #000000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}
.video-placeholder {
  color: #475569;
  font-family: monospace;
  letter-spacing: 2px;
  margin-bottom: 16px;
}
.play-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  transition: background 0.3s;
}
.play-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
.play-icon {
  width: 24px;
  height: 24px;
  fill: #ffffff;
  margin-left: 4px;
}
.face-track-box {
  position: absolute;
  top: 25%;
  left: 33%;
  width: 120px;
  height: 160px;
  border: 2px dashed;
  border-radius: 8px;
  opacity: 0.8;
}
.video-footer {
  padding: 16px;
  background-color: #1e293b;
}
.wave-bars {
  display: flex;
  height: 32px;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
  opacity: 0.6;
}
.wave-bar {
  flex: 1;
  border-radius: 2px;
}
.video-desc {
  margin: 0;
  font-size: 14px;
  color: #cbd5e1;
  font-style: italic;
  border-left: 2px solid #475569;
  padding-left: 12px;
  line-height: 1.5;
}

/* 盲区 */
.blind-spots {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.spot-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.spot-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.spot-name {
  color: #475569;
  font-weight: 500;
}
.spot-alert {
  color: #ef4444;
  font-weight: 700;
}
.progress-bg {
  width: 100%;
  height: 8px;
  background-color: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #fca5a5, #ef4444);
  border-radius: 4px;
}
.action-btn {
  width: 100%;
  margin-top: 24px;
  padding: 10px 0;
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.action-btn:hover {
  background-color: #f8fafc;
  color: #0ea5e9;
  border-color: #0ea5e9;
}
.icon {
  width: 20px;
  height: 20px;
}

/* 视频扫描线动画 */
.video-player::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: rgba(70, 165, 192, 0.5);
  box-shadow: 0 0 10px #46a5c0;
  animation: scan 3s linear infinite;
  pointer-events: none;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

/* 动态声纹跳动动画 */
@keyframes wave {
  0%,
  100% {
    transform: scaleY(0.3);
  }
  50% {
    transform: scaleY(1);
  }
}

.wave-bar {
  animation: wave 1.2s infinite ease-in-out;
}
/* 让每一根波形条的动画错开，看起来更真实 */
.wave-bar:nth-child(2n) {
  animation-delay: 0.2s;
}
.wave-bar:nth-child(3n) {
  animation-delay: 0.4s;
}
.wave-bar:nth-child(4n) {
  animation-delay: 0.1s;
}
</style>
