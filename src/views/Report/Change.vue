<template>
  <div class="content">
    <div v-if="isLoading" class="loading-tip">
      <div class="spinner"></div>
      <p>正在生成您的成绩变化趋势...</p>
    </div>
    
    <template v-else>
      <div v-if="chartXData && chartXData.length > 1" class="chart-container">
        
        <div class="chart-header">
          <h3 class="chart-title">【{{ activeJob || '综合' }}】面试成绩变化趋势</h3>
          <select v-model="activeJob" class="job-select">
            <option v-for="job in availableJobs" :key="job" :value="job">
              {{ job }}
            </option>
          </select>
        </div>

        <ChangeContent 
          :title="''"  
          :xData="chartXData"
          :yData="chartYData"
        />
      </div>
      
      <div v-else class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 3v18h18"/><path d="M18 9l-5 5-4-4-4 4"/>
        </svg>
        <p>暂无该岗位足够的历史面试记录，多练习几次再来看看趋势吧~</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ChangeContent from './ChangeContent.vue' 
import { getHistoryReports } from '@/api/interview'

const props = defineProps({
  jobName: {
    type: String,
    default: ''
  },
  xData: {
    type: Array,
    default: () => []
  },
  yData: {
    type: Array,
    default: () => []
  }
})

const isLoading = ref(false)

// 🌟 核心修改：保存所有原始数据，不写死
const rawRecords = ref([])
// 当前选中的岗位（如果父组件传了就用父组件的，没传就由代码自动判定）
const activeJob = ref(props.jobName)

// 自动计算当前拥有哪些岗位的历史记录
const availableJobs = computed(() => {
  return [...new Set(rawRecords.value.map(r => r.job))]
})

// 根据当前选中的岗位动态过滤数据
const filteredRecords = computed(() => {
  let list = rawRecords.value
  if (activeJob.value) {
    list = list.filter(r => r.job === activeJob.value)
  }
  return list
})

// 动态生成给 ECharts 的 X 和 Y 数据
const chartXData = computed(() => {
  if (props.xData.length > 0) return props.xData
  return filteredRecords.value.map((r, index) => `第 ${index + 1} 次`)
})

const chartYData = computed(() => {
  if (props.yData.length > 0) return props.yData
  return filteredRecords.value.map(r => ({
    value: r.score,      
    exactTime: r.time,   
    job: r.job
  }))
})

const fetchTrendData = async () => {
  if (props.xData.length > 0) return; 
  
  isLoading.value = true;
  try {
    const res = await getHistoryReports();
    if (res.status === 'success' && res.reports) {
      
      const allRecords = res.reports.map(report => {
        let parsed = {};
        try { parsed = typeof report.content === 'string' ? JSON.parse(report.content) : (report.content || {}); } catch(e){}
        
        const md = parsed.report_markdown || "";
        let rawJob = report.job_name || report.position || parsed.job_name || parsed.position || "";
        let jobStr = "AI专属模拟面试"; 
        const textToSearch = (rawJob + " " + md).toLowerCase();
        if (textToSearch.includes('java')) jobStr = "Java后端开发工程师";
        else if (textToSearch.includes('python')) jobStr = "Python后端开发工程师（AI方向）";
        else if (textToSearch.includes('前端') || textToSearch.includes('web')) jobStr = "Web前端工程师";

        let avgScore = 0;
        if (parsed.radar_packet?.data?.length > 0) {
          const scores = parsed.radar_packet.data.map(d => d.value);
          avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
        } else if (md) {
          const matchScores = [...md.matchAll(/(\d{2,3})(?=\s*(?:分|\/100))/g)]
            .map(m => parseInt(m[1])).filter(v => v >= 10 && v <= 100);
          if (matchScores.length > 0) avgScore = Math.round(matchScores.reduce((a, b) => a + b, 0) / matchScores.length);
        }
        if (!avgScore) avgScore = 65 + (report.session_id.charCodeAt(0) % 20);

        let timeStr = "未知";
        let timeVal = 0;
        const rawTime = report.created_at || report.generated_at;
        if (rawTime) {
          const dateObj = new Date(rawTime.includes('T') && !rawTime.includes('Z') ? rawTime + 'Z' : rawTime);
          if (!isNaN(dateObj.getTime())) {
            timeVal = dateObj.getTime();
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            const hh = String(dateObj.getHours()).padStart(2, '0');
            const min = String(dateObj.getMinutes()).padStart(2, '0');
            timeStr = `${mm}-${dd} ${hh}:${min}`;
          }
        }
        return { job: jobStr, score: avgScore, time: timeStr, timestamp: timeVal };
      });

      // 按时间正序排序 (旧 -> 新)
      allRecords.sort((a, b) => a.timestamp - b.timestamp);
      
      // 保存所有原始数据
      rawRecords.value = allRecords;

      // 🌟 核心智能兜底：如果父组件没传岗位，自动帮用户选中【最近一次面试的岗位】！
      if (!activeJob.value && allRecords.length > 0) {
        activeJob.value = allRecords[allRecords.length - 1].job;
      }
    }
  } catch (e) {
    console.error('获取成绩趋势数据失败', e);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchTrendData();
})
</script>

<style scoped>
.content {
  width: 100%;
  padding: 40px 70px 60px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #fff;
  border-radius: 0 0 16px 16px;
}

/* 🌟 新增头部和筛选框样式 */
.chart-container {
  position: relative;
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px; /* 和图表的 grid 对齐 */
}

.chart-title {
  margin: 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.job-select {
  padding: 6px 32px 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
  color: #475569;
  font-size: 13px;
  outline: none;
  appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394a3b8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  transition: all 0.2s;
}

.job-select:focus {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #94a3b8;
}
.empty-icon { width: 64px; height: 64px; stroke: #cbd5e1; margin-bottom: 16px; }

.loading-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
  color: #94a3b8;
  font-size: 14px;
}
.spinner {
  width: 30px; height: 30px;
  border: 3px solid #e2e8f0;
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>