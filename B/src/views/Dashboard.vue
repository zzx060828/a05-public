<template>
  <div class="b-end-dashboard">
    <header class="page-header">
      <div class="header-text">
        <h1 class="page-title">智能初筛引擎</h1>
        <p class="page-subtitle">核心工作台</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="handleCreate"><span>+</span> 新建面试场次</button>
        <button class="btn-secondary" @click="openImportModal">
          <svg
            viewBox="0 0 24 24"
            width="16"
            height="16"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
            style="margin-right: 6px"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          导入新题库
        </button>
      </div>
    </header>

    <div class="stat-cards-container">
      <div class="stat-card">
        <div class="stat-icon blue-bg">
          <svg
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            width="200"
            height="200"
          >
            <path
              d="M656.532 502.311a235.274 235.274 0 0 1-40.445 40.264c36.946 15.03 71.018 35.668 101.162 60.858C822.216 642.717 897 744.078 897 863h80c0-146.96-88.695-273.234-215.456-327.973C807.735 495.412 837 436.624 837 371c0-119.294-96.707-216-216-216-9.765 0-19.378 0.648-28.799 1.903 36.587 21.833 66.711 53.37 86.819 91.059C725.11 269.735 757 316.643 757 371c0 62.818-42.589 115.688-100.468 131.311z"
              fill="currentColor"
            ></path>
            <path
              d="M573.023 543.952C627.779 501.318 663 434.772 663 360c0-128.682-104.318-233-233-233-128.682 0-233 104.318-233 233 0 74.616 35.074 141.041 89.635 183.685C146.698 600.312 48 737.643 48 898h80c0-166.845 135.041-302 301.5-302S731 731.155 731 898h80c0-160.106-98.388-297.258-237.977-354.048zM583 360c0 84.5-68.5 153-153 153s-153-68.5-153-153 68.5-153 153-153 153 68.5 153 153z"
              fill="currentColor"
            ></path>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-title">累计面试人次</div>
          <div class="stat-value">{{ mockData.overview.totalInterviews.toLocaleString() }}</div>
          <div class="stat-trend positive">↑ 较上周增长 {{ mockData.overview.totalGrowth }}%</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange-bg">
          <svg
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            width="200"
            height="200"
          >
            <path
              d="M506.88 407.04c19.456 0 38.4 4.608 55.296 13.824 7.68 4.096 16.896 1.024 20.992-6.144 4.096-7.68 1.024-16.896-6.144-20.992-21.504-11.264-45.568-17.408-69.632-17.408-52.736 0-101.376 28.16-126.976 73.728-12.288 21.504-18.944 46.08-18.944 71.168 0 79.872 65.536 144.384 145.92 144.384s145.92-65.024 145.92-144.384c0-17.92-3.072-35.84-9.728-52.224-3.072-7.68-11.776-11.776-19.968-8.704-7.68 3.072-11.776 11.776-8.704 19.968 5.12 13.312 7.68 27.136 7.68 40.96 0 62.976-51.712 113.664-115.2 113.664s-115.2-51.2-115.2-113.664c0-19.456 5.12-38.912 14.848-55.808 19.968-36.352 58.368-58.368 99.84-58.368z"
              fill="currentColor"
            ></path>
            <path
              d="M668.16 270.848c4.096-7.168 1.536-16.896-5.632-20.992-47.104-26.624-100.864-40.448-155.648-40.448-173.568 0-314.88 139.776-314.88 311.808s141.312 311.808 314.88 311.808 314.88-139.776 314.88-311.808c0-49.664-12.288-99.328-35.328-143.36-4.096-7.68-13.312-10.24-20.992-6.656-7.68 4.096-10.24 13.312-6.656 20.992 20.992 39.936 31.744 83.456 31.744 129.024 0 154.624-127.488 281.088-284.16 281.088s-283.648-126.464-283.648-281.6S350.208 240.128 506.88 240.128c49.152 0 97.792 12.8 140.288 36.864 7.68 3.584 16.896 1.024 20.992-6.144z"
              fill="currentColor"
            ></path>
            <path
              d="M937.984 320.512c-3.584-7.68-12.8-10.752-20.48-7.168-7.68 3.584-10.752 12.8-7.168 20.48 28.16 58.88 41.984 121.856 41.984 187.392 0 242.688-199.68 440.32-445.44 440.32s-445.44-197.632-445.44-440.32 199.68-440.32 445.44-440.32c72.192 0 143.872 17.408 207.36 50.688 7.68 4.096 16.896 1.024 20.48-6.656 4.096-7.68 1.024-16.896-6.656-20.48-67.072-35.84-143.872-54.784-221.184-54.784-262.656 0-476.16 211.456-476.16 471.04s213.504 471.04 476.16 471.04 476.16-211.456 476.16-471.04c0-70.144-14.848-137.216-45.056-200.192z"
              fill="currentColor"
            ></path>
            <path
              d="M701.44 222.208v92.672l-200.192 200.192c-6.144 6.144-6.144 15.872 0 21.504 3.072 3.072 7.168 4.608 10.752 4.608s7.68-1.536 10.752-4.608l200.192-200.192h97.792c11.776 0 23.552-5.12 31.232-13.824l108.544-119.296c9.216-10.24 11.776-25.088 6.656-37.888-5.12-12.8-16.896-20.992-30.208-21.504l-46.592-2.048-1.536-39.936c-0.512-14.336-9.216-26.112-22.016-31.744-12.8-5.12-26.624-2.048-36.352 7.68l-115.2 113.152c-8.704 7.68-13.824 18.944-13.824 31.232z m30.72 0c0-3.584 1.536-7.168 4.096-9.728l115.2-113.152c0.512-0.512 1.536-1.536 3.584-1.024 1.024 0.512 2.56 1.536 2.56 4.096l3.072 68.096 74.752 3.072c2.048 0 3.072 1.536 3.584 2.56 0.512 1.024 1.024 3.584-1.024 5.632L829.44 301.568c-2.048 2.56-5.632 4.096-8.704 4.096H732.16V222.208z"
              fill="currentColor"
            ></path>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-title">本周完成率</div>
          <div class="stat-value">
            {{ mockData.overview.completionRate }}<span class="unit">%</span>
          </div>
          <div class="stat-trend positive">
            ↑ 较上周提升 {{ mockData.overview.completionGrowth }}%
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon gray-bg">
          <svg
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            width="200"
            height="200"
          >
            <path
              d="M857.034752 164.405248C764.735488 72.105984 642.01728 21.274624 511.488 21.274624c-130.531328 0-253.247488 50.83136-345.546752 143.130624S22.810624 379.420672 22.810624 509.952c0 130.52928 50.83136 253.247488 143.130624 345.546752s215.015424 143.130624 345.546752 143.130624c130.52928 0 253.247488-50.83136 345.546752-143.130624S1000.165376 640.48128 1000.165376 509.952c0-130.531328-50.83136-253.247488-143.130624-345.546752zM511.488 953.716736c-244.692992 0-443.764736-199.071744-443.764736-443.764736S266.795008 66.187264 511.488 66.187264 955.252736 265.259008 955.252736 509.952 756.180992 953.716736 511.488 953.716736z"
              fill="currentColor"
            ></path>
            <path
              d="M500.641792 243.539968h-44.91264v322.17088h322.17088v-44.91264h-277.25824z"
              fill="currentColor"
            ></path>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-title">平均面试时长</div>
          <div class="stat-value">
            {{ mockData.overview.avgDuration }}<span class="unit">min</span>
          </div>
          <div class="stat-trend neutral">- 与上周持平</div>
        </div>
      </div>
    </div>

    <div class="main-grid">
      <div class="card chart-card">
        <h3 class="card-title">当前批次能力均值</h3>
        <div ref="radarChartRef" class="echarts-container"></div>
      </div>

      <div class="card list-card">
        <h3 class="card-title">高频知识盲区 Top 5</h3>
        <div class="blind-spots-list">
          <div v-for="(item, index) in mockData.blindSpots" :key="index" class="spot-item">
            <div class="spot-info">
              <span class="spot-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
              <span class="spot-name">{{ item.name }}</span>
              <span class="spot-percent">{{ item.percent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: item.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card list-card">
        <h3 class="card-title">待办与异常拦截</h3>
        <div class="todo-list">
          <div class="todo-item alert-cmci" v-if="mockData.overview.cheatAlerts > 0">
            <div class="todo-icon-wrapper">
              <svg
                t="1775308878542"
                class="little-icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="14105"
                width="200"
                height="200"
              >
                <path
                  d="M767 797H257V521.8c0-66.6 26.5-129.2 74.7-176.3 48.2-47.1 112.2-73 180.3-73 68.1 0 132.1 25.9 180.3 73S767 455.2 767 521.8V797z m-460-48.9h410V521.8c0-110.5-92-200.5-205-200.5s-205 89.9-205 200.5v226.3zM786.1 923.9h-548c-25.4 0-46.1-20.7-46.1-46.1 0-25.4 20.7-46.1 46.1-46.1H786c25.4 0 46.1 20.7 46.1 46.1 0.1 25.4-20.7 46.1-46 46.1zM512 231.5c-13.8 0-25-11.2-25-25v-82.2c0-13.7 11.3-25 25-25 13.8 0 25 11.2 25 25v82.2c0 13.7-11.2 25-25 25zM286.4 287.3c-9 10.4-24.8 11.6-35.3 2.7l-62.4-53.6c-10.4-9-11.6-24.8-2.7-35.3 9-10.4 24.8-11.6 35.3-2.7l62.4 53.6c10.4 9 11.6 24.9 2.7 35.3zM196 478.5c0 13.8-11.2 25-25 25H88.8c-13.7 0-25-11.3-25-25s11.2-25 25-25H171c13.7 0 25 11.2 25 25zM739.5 286.9c9 10.4 24.8 11.6 35.3 2.7l62.4-53.6c10.4-9 11.6-24.8 2.7-35.3-9-10.4-24.8-11.6-35.3-2.7l-62.4 53.6c-10.4 9-11.6 24.9-2.7 35.3zM823.9 479c0 13.8 11.2 25 25 25h82.2c13.8 0 25-11.3 25-25 0-13.8-11.3-25-25-25h-82.2c-13.8 0-25 11.3-25 25z"
                  p-id="14106"
                ></path>
              </svg>
            </div>
            <div class="todo-content">
              <h4 class="todo-title">
                系统拦截 {{ mockData.overview.cheatAlerts }} 起严重作弊嫌疑
              </h4>
              <p class="todo-desc">触发 CMCI 跨模态冲突，请立即复核！</p>
            </div>
            <button class="btn-outline-danger" @click="goToAuditDetail">立即处理</button>
          </div>
        </div>
      </div>

      <div class="card chart-card">
        <h3 class="card-title">群体抗压水位线趋势 (近7日)</h3>
        <div ref="lineChartRef" class="echarts-container"></div>
      </div>
    </div>

    <CreateCampaign v-model:visible="isModalVisible" @create="handleCampaignCreated" />

    <ImportModal v-model:visible="showImportModal" @success="onImportSuccess" />

    <div v-if="showLinkModal" class="demo-modal-overlay">
      <div class="demo-modal">
        <div class="modal-icon">
          <svg
            t="1775723679967"
            class="pass-icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            p-id="5922"
            width="200"
            height="200"
          >
            <path d="M852.8 261.6l2.3 1.2-2.3-1.2z" fill="#68BB8D" p-id="5923"></path>
            <path
              d="M514.2 99.9c-228.5 0-413.7 185.2-413.7 413.7s185.2 413.7 413.7 413.7S927.8 742 927.8 513.5 742.5 99.9 514.2 99.9zM712 430.7L553 587l-77 75.3c-0.3 0.4-0.7 0.8-1.2 1.3-0.6 0.6-1.3 1.2-2 1.8-4.8 4.6-11.1 7.1-17.8 7.1h-1.1c-7 0-13.5-2.6-18.3-7.4-0.7-0.6-1.3-1.2-1.9-1.7-0.4-0.4-0.7-0.7-1-1.1L304.3 533.9c-10.4-10.4-9.7-28 1.5-39.2 5.7-5.7 13.3-8.9 21-8.9 7 0 13.5 2.6 18.3 7.4l109.4 109.4 58.1-56.8 159.1-156.3c4.8-4.7 11.2-7.2 18.1-7.2 7.8 0 15.5 3.3 21.2 9.1 11 11.4 11.6 29 1 39.3z"
              fill="#68BB8D"
              p-id="5924"
            ></path>
          </svg>
        </div>
        <h3>面试场次已创建</h3>
        <p>请将下方专属考试链接发送给候选人：</p>
        <div class="link-box">
          <input type="text" readonly :value="generatedLink" />
          <button @click="copyLink(generatedLink)">复制</button>
        </div>
        <button class="btn-primary full-btn" @click="showLinkModal = false">完成</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus' // 引入消息提示

// 引入组件
import CreateCampaign from '@/views/CreateCampaign.vue'

// 🌟 改动 3：引入你刚才写的带有 Element Plus 的专业弹窗
// (注意确认这里的路径！如果你存在 views 里就叫这个，如果在 components 就在那)
import ImportModal from '@/views/ImportQuestions.vue'

const router = useRouter()

// --- 弹窗控制 ---
const isModalVisible = ref(false)
const showLinkModal = ref(false)
const generatedLink = ref('')

// 🌟 改动 4：控制导入题库弹窗的显示
const showImportModal = ref(false)

// 打开导入弹窗
const openImportModal = () => {
  showImportModal.value = true
}

// 接收导入成功的事件
const onImportSuccess = () => {
  // 这里可以通过 ElMessage 给用户一个反馈，也可以在这里调用刷新题库数量的接口
  ElMessage({
    message: '题库数据已成功更新！',
    type: 'success',
    duration: 3000,
  })
}

// --- Refs ---
const radarChartRef = ref(null)
const lineChartRef = ref(null)
let radarChart = null
let lineChart = null

// --- 静态 Mock 完整数据 ---
const mockData = reactive({
  overview: {
    totalInterviews: 12450,
    totalGrowth: 12,
    completionRate: 94.2,
    completionGrowth: 2.1,
    avgDuration: 42,
    cheatAlerts: 3,
    audioReviews: 12,
  },
  blindSpots: [
    { name: '微服务架构 (Microservices)', percent: 45 },
    { name: 'JVM 性能调优 (JVM Tuning)', percent: 38 },
    { name: '分布式缓存一致性 (Cache)', percent: 35 },
    { name: '多线程与并发 (Concurrency)', percent: 30 },
    { name: '数据库悲观锁/乐观锁 (DB Locks)', percent: 25 },
  ],
  radarScores: [85, 68, 88, 82, 75],
  stressTrend: [60, 65, 70, 85, 75, 60, 55],
})

// 静态造假的候选人列表
const mockCandidates = ref([
  {
    name: '李明 (已发 offer)',
    role: '高级 Java 工程师',
    time: '2026-04-06 14:30',
    statusClass: 'done',
    statusText: '已完成',
    score: 88,
    link: null,
  },
  {
    name: '王建国',
    role: '前端开发工程师',
    time: '2026-04-05 10:15',
    statusClass: 'done',
    statusText: '已完成',
    score: 72,
    link: null,
  },
])

const handleCreate = () => {
  isModalVisible.value = true
}
const goToCampaigns = () => router.push('/campaigns')
const goToCandidates = () => router.push('/candidates')
const goToAuditDetail = () => router.push('/audit-detail')

const handleCampaignCreated = (data) => {
  console.log('收到漂亮的表单发来的数据：', data)
  generatedLink.value = `http://localhost:5173/start?token=DEMO-${Date.now()}`
  mockCandidates.value.unshift({
    name: '新候选人',
    role: data.name || '默认岗位',
    time: '刚刚',
    statusClass: 'pending',
    statusText: '待面试',
    score: null,
    link: generatedLink.value,
  })
  isModalVisible.value = false
  showLinkModal.value = true
}

const copyLink = (link) => {
  navigator.clipboard.writeText(link)
  alert('链接已复制到剪贴板！可以去无痕窗口打开啦！')
}

const initCharts = () => {
  if (radarChartRef.value) {
    radarChart = echarts.init(radarChartRef.value)
    radarChart.setOption({
      tooltip: {},
      radar: {
        indicator: [
          { name: '逻辑表达', max: 100 },
          { name: '技术深度', max: 100 },
          { name: '沟通能力', max: 100 },
          { name: '专业精度', max: 100 },
          { name: '非语言表现', max: 100 },
        ],
        radius: '65%',
        axisName: { color: '#7d7d7d', fontSize: 13, fontWeight: 500 },
        splitLine: { lineStyle: { color: ['#eef2f5'] } },
        splitArea: { show: false },
        axisLine: { lineStyle: { color: '#eef2f5' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: mockData.radarScores,
              name: '批次均值',
              itemStyle: { color: '#46a5c0' },
              areaStyle: { color: 'rgba(70, 165, 192, 0.2)' },
              lineStyle: { width: 3 },
            },
          ],
        },
      ],
    })
  }

  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value)
    lineChart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.9)',
        borderColor: '#fff',
        textStyle: { color: '#333' },
        extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 8px;',
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#7d7d7d', margin: 12 },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f4f8' } },
        axisLabel: { color: '#7d7d7d' },
      },
      series: [
        {
          name: '平均压力值',
          data: mockData.stressTrend,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: { color: '#46a5c0', borderColor: '#fff', borderWidth: 2 },
          lineStyle: {
            width: 4,
            color: '#46a5c0',
            shadowColor: 'rgba(70,165,192,0.3)',
            shadowBlur: 10,
            shadowOffsetY: 5,
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(70, 165, 192, 0.4)' },
              { offset: 1, color: 'rgba(70, 165, 192, 0.0)' },
            ]),
          },
          markLine: {
            data: [{ yAxis: 80, name: '高压警戒线' }],
            symbol: ['none', 'none'],
            lineStyle: { color: '#ff8c42', type: 'dashed', width: 2 },
            label: { position: 'insideEndTop', formatter: '警戒水位 (80)', color: '#ff8c42' },
          },
        },
      ],
    })
  }
}

const handleResize = () => {
  radarChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
/* 你的原有 Dashboard 样式完全保留 */
.b-end-dashboard {
  padding: 40px;
  background-color: #f7f9fc;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}
.page-title {
  margin: 0;
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.page-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #7d7d7d;
}
.header-actions {
  display: flex;
  gap: 16px;
}
.btn-primary {
  background: #ff8c42;
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 45px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(255, 140, 66, 0.2);
}
.btn-primary:hover {
  background: #f18440;
}

/* 🌟 新增：导入题库使用的次级按钮样式 */
.btn-secondary {
  background: #ffffff;
  color: #46a5c0;
  border: 1px solid #46a5c0;
  padding: 12px 28px;
  border-radius: 45px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}
.btn-secondary:hover {
  background: #f0f8fa;
}

.stat-cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}
.stat-card {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.blue-bg {
  background: rgba(70, 165, 192, 0.1);
  color: #46a5c0;
}
.orange-bg {
  background: rgba(255, 140, 66, 0.1);
  color: #ff8c42;
}
.gray-bg {
  background: #f0f4f8;
  color: #7d7d7d;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-title {
  color: #7d7d7d;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}
.stat-value {
  color: #2c3e50;
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 10px;
}
.stat-value .unit {
  font-size: 16px;
  color: #a0aec0;
  font-weight: normal;
  margin-left: 4px;
}
.stat-trend {
  font-size: 13px;
  font-weight: 600;
}
.stat-trend.positive {
  color: #46a5c0;
}
.stat-trend.neutral {
  color: #7d7d7d;
}
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.card {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
}
.card-title {
  margin: 0 0 24px 0;
  font-size: 18px;
  color: #2c3e50;
  font-weight: 700;
  position: relative;
  padding-left: 14px;
}
.card-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: #46a5c0;
  border-radius: 4px;
}
.echarts-container {
  width: 100%;
  height: 320px;
}
.blind-spots-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  justify-content: center;
}
.spot-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.spot-info {
  display: flex;
  align-items: center;
  font-size: 14px;
}
.spot-rank {
  width: 26px;
  height: 26px;
  line-height: 26px;
  text-align: center;
  border-radius: 8px;
  background: #f0f4f8;
  color: #7d7d7d;
  font-weight: bold;
  font-size: 12px;
  margin-right: 14px;
}
.spot-rank.rank-1 {
  background: rgba(255, 140, 66, 0.15);
  color: #ff8c42;
}
.spot-rank.rank-2 {
  background: rgba(255, 140, 66, 0.1);
  color: #ff8c42;
  opacity: 0.9;
}
.spot-rank.rank-3 {
  background: rgba(255, 140, 66, 0.05);
  color: #ff8c42;
  opacity: 0.8;
}
.spot-name {
  flex: 1;
  color: #2c3e50;
  font-weight: 500;
  font-size: 15px;
}
.spot-percent {
  color: #46a5c0;
  font-weight: bold;
  font-size: 15px;
}
.progress-track {
  width: 100%;
  height: 8px;
  background: #f0f4f8;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6ec6df, #46a5c0);
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.todo-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.todo-item:hover {
  background: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}
.todo-item.alert-cmci {
  background: #fff5f0;
  border-color: rgba(255, 140, 66, 0.2);
}
.todo-item.alert-cmci .todo-title {
  color: #d35400;
}
.todo-item.alert-cmci .todo-desc {
  color: #e67e22;
}
.todo-icon-wrapper {
  font-size: 24px;
  width: 48px;
  height: 48px;
  background: rgba(255, 140, 66, 0.1);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}
.todo-icon-wrapper.normal {
  background: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}
.todo-content {
  flex: 1;
}
.todo-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  color: #2c3e50;
  font-weight: 600;
}
.todo-desc {
  margin: 0;
  font-size: 13px;
  color: #7d7d7d;
  line-height: 1.5;
}
.btn-outline-danger {
  background: #ff8c42;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 45px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(255, 140, 66, 0.2);
}
.btn-outline-danger:hover {
  background: #eb7d38;
}
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  .stat-cards-container {
    grid-template-columns: 1fr;
  }
}
.icon {
  height: 45px;
}
.little-icon {
  width: 26px;
  height: 26px;
  display: block;
}

.demo-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.demo-modal {
  background: white;
  width: 480px;
  padding: 40px 30px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.demo-modal h3 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 22px;
}
.demo-modal p {
  color: #7d7d7d;
  font-size: 14px;
  margin-bottom: 24px;
}
.link-box {
  display: flex;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px;
  margin-bottom: 16px;
}
.link-box input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0 12px;
  color: #2c3e50;
  font-family: monospace;
  outline: none;
}
.link-box button {
  background: #46a5c0;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.modal-tip {
  font-size: 12px;
  color: #e67e22;
  background: #fff3e0;
  padding: 8px;
  border-radius: 6px;
}
.full-btn {
  width: 100%;
  margin-top: 24px;
  justify-content: center;
}
.pass-icon {
  width: 60px;
  height: 60px;
}
</style>
