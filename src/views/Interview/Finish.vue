<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const route = useRoute()
const router = useRouter()

// ===== 核心数据源 =====
const sessionId = route.params.sessionId || route.query.sessionId || ''

const score = ref(0)
const answeredCount = ref(0)
const totalCount = ref(10)
const timeSpentSeconds = ref(0) // 👈 新增：真实耗时（秒）
const analysisSummaryList = ref(['正在加载大模型多维度面评数据...'])

// ===== 💡 智能计算属性 =====

// 1. 动态格式化时长 (将 125 秒转化为 02:05)
const formattedDuration = computed(() => {
  if (!timeSpentSeconds.value) return '00:00'
  const m = Math.floor(timeSpentSeconds.value / 60)
  const s = timeSpentSeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

// 2. 动态判断面试状态 (多维度：题量 + 时长 交叉校验)
const completeStatus = computed(() => {
  // 设定及格线：至少答 3 题，且总时长至少超过 3 分钟 (180秒)
  if (answeredCount.value >= 3 && timeSpentSeconds.value >= 180) {
    return '已完成'
  } 
  // 异常情况 1：答够了 3 题，但时间太短（比如你说的 1分半）
  else if (answeredCount.value >= 3 && timeSpentSeconds.value < 180) {
    return '耗时过短 (疑似敷衍)' 
  } 
  // 异常情况 2：没答够 3 题就跑了
  else if (answeredCount.value > 0 && answeredCount.value < 3) {
    return '提前终止 (样本偏少)'
  } 
  // 异常情况 3：白卷
  else {
    return '未作答退出'
  }
})

// ===== 🏆 视觉动效 (保留了你的分数跳动特效) =====
const animateScore = (targetScore) => {
  const finalScore = parseInt(targetScore) || 0; 
  let currentScore = 0;
  
  if (finalScore === 0) {
    score.value = 0;
    return;
  }

  const interval = setInterval(() => {
    if (currentScore >= finalScore) {
      score.value = finalScore;
      clearInterval(interval);
      return;
    }
    // 缓动算法：越接近目标分数，跳动越慢，非常有质感
    currentScore += Math.ceil((finalScore - currentScore) / 10) || 1;
    score.value = currentScore;
  }, 30);
}

// ===== 📡 获取与解析数据 =====
const getInterviewResult = () => {
  try {
    console.log("🔍 当前路由解析出的 SessionID:", sessionId);
    if (!sessionId) {
      console.error("❌ 路由中没有提取到 sessionId 参数！");
      return;
    }

    const cachedData = sessionStorage.getItem(`summary_${sessionId}`);
    
    if (cachedData) {
      const data = JSON.parse(cachedData);
      console.log("✅ 成功读到结算数据:", data);

      answeredCount.value = data.answeredCount || 0;
      totalCount.value = data.totalCount || 10;
      timeSpentSeconds.value = data.timeSpent || 0; // 👈 接收 Start.vue 传过来的真实耗时
      
      if (data.analysis) {
        analysisSummaryList.value = data.analysis
          .replace(/\*\*/g, '') // 顺手清洗掉大模型可能返回的 Markdown 加粗符号
          .split(/[；。！\n]/)   // 保留了你精妙的中文标点切分法
          .filter(s => s.trim().length > 0);
      }

      animateScore(data.score || 0);

    } else {
      console.warn(`⚠️ 没找到缓存数据: summary_${sessionId}`);
      animateScore(0);
      analysisSummaryList.value = ['暂无分析数据，可能是因为你没有回答问题就直接结束了。'];
    }
  } catch (error) {
    console.error('❌ 解析结果失败：', error);
  } 
}

// ===== 🕹️ 按钮路由操作 =====
const viewDetail = () => {
  if (!sessionId) {
    alert("未获取到会话ID");
    return;
  }

  router.push({
    name: 'ReportView',
    params: { sessionId: sessionId } 
  })
}

const restartInterview = () => {
  if (confirm('确定要进行一次全新的面试吗？')) {
    if (sessionId) sessionStorage.removeItem(`summary_${sessionId}`);
    sessionStorage.removeItem('currentQuestion');
    sessionStorage.removeItem('currentAudioUrl');
    
    router.push('/interview'); 
  }
}

onMounted(() => {
  getInterviewResult()
})
</script>


<template>
  <div class="ami-page light-enterprise-theme">
    <div class="app-shell">
      
      <main class="workspace">
        <div class="report-container">
          
          <div class="report-header">
            <h2 class="title-primary">综合评估报告</h2>
            <p class="subtitle-muted">本次面试数据已归档，以下为多模态 AI 评估摘要。</p>
          </div>

          <div class="report-body">
            <div class="score-card soft-panel fade-in">
              <div class="score-circle-wrapper">
                <div class="score-circle">
                  <div class="score-value">{{ score }}</div>
                  <div class="score-label">总分 / 100</div>
                </div>
              </div>
              
              <div class="score-footer w-100">
                <button class="btn-primary w-100 mb-3" @click="viewDetail">查看详细分析报告</button>
                <button class="btn-outline w-100" @click="restartInterview">重新模拟面试</button>
              </div>
            </div>

            <div class="details-section">
              
              <div class="metrics-grid">
                <div class="metric-box soft-panel fade-in">
                  <div class="metric-label">完成情况</div>
                  <div class="metric-value">
                    <span class="text-dark">{{ answeredCount }}</span>
                    <span class="text-muted text-sm" style="font-weight: 400; margin-left: 6px;">题 / 历时 {{ formattedDuration }}</span>
                  </div>
                </div>
                
                <div class="metric-box soft-panel fade-in">
                  <div class="metric-label">面评状态</div>
                  <div 
                    class="metric-value" 
                    :style="{ color: completeStatus === '已完成' ? 'var(--accent-green)' : (completeStatus === '未作答退出' ? 'var(--accent-red)' : '#f59e0b') }"
                    style="font-size: 22px; font-weight: 500; display: flex; align-items: center; gap: 8px;"
                  >
                    <svg v-if="completeStatus === '已完成'" viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                    <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                    {{ completeStatus }}
                  </div>
                </div>
              </div>

              <div class="analysis-card soft-panel fade-in">
                <div class="card-title">
                  <span class="cyan-bar"></span>
                  结果分析摘要
                </div>
                <div class="analysis-content">
                  <p v-for="(item, index) in analysisSummaryList" :key="index">
                    {{ item }}
                  </p>
                </div>
              </div>

            </div>
          </div>

          <div class="report-footer fade-in">
            <div class="quote-card">
              <div class="quote-icon">
                <svg t="1774755157430" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1176" width="32" height="32"><path d="M499.72 535.65m-356.35 0a356.35 356.35 0 1 0 712.7 0 356.35 356.35 0 1 0-712.7 0Z" fill="#A4DAF6" p-id="1177"></path><path d="M489.98 370.16c10.33 16.69 19.54 34.11 27.21 52.19 1.75 4.13 3.4 8.3 4.99 12.5 0.87 2.3 1.72 4.6 2.54 6.91 0.41 1.16 0.82 2.31 1.22 3.47 0.6 3.19 1.42 2.36 2.46-2.51 0.77-0.5 0.52-0.37-0.75 0.4-0.91 0.47-1.84 0.92-2.78 1.33-1.76 0.75-3.58 1.38-5.4 1.97-4 1.29-8.19 2.42-12.37 2.94-6.43 0.81-12 4.94-12 12 0 5.86 5.53 12.81 12 12 11.71-1.47 25-4.05 34.89-10.94 13.77-9.59 6.91-24.82 2.01-37.4-9.08-23.29-20.14-45.72-33.3-66.98-8.11-13.11-28.88-1.07-20.72 12.11zM324.57 427.58c16.49-22.62 32.97-45.24 49.46-67.86h-20.72c15.64 22.95 31.51 45.74 47.15 68.69 3.64 5.35 10.55 7.74 16.42 4.31 5.3-3.1 7.97-11.04 4.31-16.42-15.64-22.95-31.51-45.74-47.15-68.69-5.38-7.89-15.27-7.48-20.72 0-16.49 22.62-32.97 45.24-49.46 67.86-3.82 5.24-0.89 13.38 4.31 16.42 6.07 3.55 12.59 0.95 16.42-4.31zM599.55 427.58c16.49-22.62 32.97-45.24 49.46-67.86h-20.72c15.64 22.95 31.51 45.74 47.15 68.69 3.64 5.35 10.55 7.74 16.42 4.31 5.3-3.1 7.97-11.04 4.31-16.42-15.64-22.95-31.51-45.74-47.15-68.69-5.38-7.89-15.27-7.48-20.72 0-16.49 22.62-32.97 45.24-49.46 67.86-3.82 5.24-0.89 13.38 4.31 16.42 6.07 3.55 12.59 0.95 16.42-4.31zM340.91 542.4c61.26 4.78 122.66 7.69 184.11 8.64 30.39 0.47 60.79 0.48 91.17 0 7.27-0.11 14.53-0.25 21.8-0.42 3.55-0.08 7.17 0.06 10.71-0.12-0.42 0.02 1.58 0.32 1.44 0.31-0.19 0.15-0.36 0-0.51-0.42 0.99 1.02 1.09 1.11 0.29 0.25 0.74 3.59-0.26-2.28 0.47 1.49-0.44-2.29 0.1 1.59 0.1 1.76 0.03 2.36-0.13 3.45-0.35 4.65-1.14 6.09-3.16 12.07-4.96 18-14.2 46.77-36.46 95.49-80.59 120.86-19.5 11.22-42.1 17.5-64.47 14.28-22.65-3.27-43.1-17.29-59.39-33.52-41.51-41.36-64.55-97.23-86.55-150.48-2.47-5.99-7.96-10.25-14.76-8.38-5.66 1.56-10.87 8.73-8.38 14.76 22.05 53.37 44.7 107.79 83.61 151.41 18.26 20.47 40.62 38.58 67.24 46.6 26.33 7.93 54.53 4.28 79.5-6.37 52.68-22.46 83.05-73.06 101.17-125.07 4.18-11.98 8.81-24.49 10.94-37.02 2.4-14.08-0.42-29.99-15.53-35.43-6.97-2.51-14.7-1.68-21.96-1.52-8.59 0.19-17.18 0.34-25.76 0.46-16.52 0.22-33.03 0.3-49.55 0.25-73.34-0.25-146.66-3.27-219.78-8.98-6.47-0.51-12 5.88-12 12 0 6.91 5.51 11.49 12 12zM120.66 158.36c45.67 33.68 88.3 71.4 127.57 112.36 10.71 11.17 27.67-5.81 16.97-16.97-40.71-42.46-85.09-81.2-132.43-116.11-5.22-3.85-13.39-0.87-16.42 4.31-3.57 6.1-0.93 12.56 4.31 16.42zM86.32 235.08c36.66 26.14 72.54 53.33 107.58 81.6 5.04 4.07 12.04 4.93 16.97 0 4.21-4.21 5.07-12.88 0-16.97-36.63-29.55-74.12-58.03-112.44-85.35-5.28-3.76-13.36-0.93-16.42 4.31-3.52 6.03-0.99 12.64 4.31 16.42zM881.96 150.4c-47.34 34.91-91.71 73.65-132.43 116.11-10.69 11.15 6.26 28.15 16.97 16.97 39.27-40.96 81.9-78.68 127.57-112.36 5.21-3.84 7.82-10.4 4.31-16.42-3-5.14-11.17-8.17-16.42-4.31zM916.3 227.12c-38.32 27.32-75.81 55.8-112.44 85.35-5.05 4.07-4.24 12.73 0 16.97 4.99 4.99 11.91 4.08 16.97 0 35.04-28.27 70.92-55.46 107.58-81.6 5.27-3.76 7.79-10.47 4.31-16.42-3.05-5.21-11.11-8.09-16.42-4.31z" fill="#1D1918" p-id="1178"></path></svg>
              </div>
              <div class="quote-text">
                <span class="font-medium text-yellow-dark">面伴建议：</span>
                每一次复盘都是成长的垫脚石。你在本次面试中展现出的逻辑与表达具备潜力，请继续保持，加油！
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>



<style scoped>
/* ================= 舒展·微质感企业风 ================= */
.light-enterprise-theme {
  --bg-app: #f4f7fa;        
  --bg-surface: #ffffff;    
  --border-color: #e2e8f0;  
  
  --text-main: #334155;     
  --text-muted: #64748b;    
  --text-dark: #0f172a;
  
  --accent-cyan: #38a1d6;   
  --accent-cyan-light: #e0f6f8; 
  --accent-cyan-dark: #3188a4;
  
  --accent-yellow-bg: #fefce8; 
  --accent-yellow-border: #fef08a;
  --accent-yellow-text: #854d0e; 
  
  --accent-green: #10b981;  
  
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  
  min-height: 100%; padding: 20px; background-color: var(--bg-app); color: var(--text-main); margin-top: 60px; height: calc(100vh - 60px); box-sizing: border-box; 
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.app-shell { width: 100%; max-width: 1440px; height: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; position: relative; }
.w-100 { width: 100%; }
.mb-3 { margin-bottom: 12px; }
.text-cyan { color: var(--accent-cyan-dark); }
.text-muted { color: var(--text-muted); }
.text-dark { color: var(--text-dark); }
.text-sm { font-size: 14px; }
.font-medium { font-weight: 600; }
.text-yellow-dark { color: #5788ba; }

/* ================= 主工作区 (去掉顶部后，调整上下居中) ================= */
.workspace { 
  display: flex; flex: 1; justify-content: center; 
  align-items: center; /* 恢复居中，因为没有顶栏了，放在正中间最好看 */
  min-height: 0; 
  overflow-y: auto;
}

.report-container { width: 100%; max-width: 1200px; display: flex; flex-direction: column; gap: 28px; padding-bottom: 40px;}

.report-header { display: flex; flex-direction: column; gap: 8px; margin-bottom: 8px;}
.title-primary { font-size: 26px; font-weight: 600; color: var(--text-dark); margin: 0; letter-spacing: 0.5px; }
.subtitle-muted { font-size: 15px; color: var(--text-muted); margin: 0; }

/* ================= 报告主体 ================= */
.report-body { display: grid; grid-template-columns: 380px 1fr; gap: 28px; } 

.soft-panel { 
  background: var(--bg-surface); 
  border: 1px solid var(--border-color); 
  border-radius: var(--radius-lg); 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); 
}

/* 左侧：分数卡片 */
.score-card { display: flex; flex-direction: column; padding: 48px 36px 36px; align-items: center; justify-content: space-between; }
.score-circle-wrapper { position: relative; margin-bottom: 48px; }

.score-circle { 
  width: 180px; height: 180px; border-radius: 50%; 
  background: white; 
  border: 4px solid var(--accent-cyan-light); 
  border-top: 4px solid var(--accent-cyan); 
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}

.score-value { font-size: 68px; font-weight: 400; color: var(--text-dark); line-height: 1; font-family: "Helvetica Neue", Arial, sans-serif;}
.score-label { font-size: 14px; color: var(--text-muted); margin-top: 10px; font-weight: 500;}

/* 🚨 全新的按钮组样式 */
.btn-primary { 
  background: var(--accent-cyan); color: white; border: none; 
  padding: 14px 24px; border-radius: var(--radius-sm); 
  font-size: 15px; font-weight: 500; cursor: pointer; transition: 0.2s; 
}
.btn-primary:hover { background: var(--accent-cyan-dark); } 

.btn-outline { 
  background: white; border: 1px solid var(--border-color); color: var(--text-main); 
  padding: 14px 24px; border-radius: var(--radius-sm); 
  font-size: 15px; font-weight: 500; cursor: pointer; transition: 0.2s;
}
.btn-outline:hover { background: #f8fafc; border-color: #94a3b8; color: var(--text-dark);}

/* 右侧：指标与分析 */
.details-section { display: flex; flex-direction: column; gap: 28px; } 
.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.metric-box { padding: 28px 36px; } 
.metric-label { font-size: 14px; color: var(--text-muted); margin-bottom: 12px; font-weight: 500; }
.metric-value { font-size: 36px; font-weight: 400; color: var(--text-dark); display: flex; align-items: baseline; gap: 6px; font-family: "Helvetica Neue", Arial, sans-serif;}
.status-success { color: var(--accent-green); font-size: 22px; font-weight: 500; display: flex; align-items: center; gap: 8px; }

/* AI 摘要长卡片 */
.analysis-card { padding: 36px; flex: 1; }
.card-title { font-size: 16px; font-weight: 600; color: var(--text-dark); display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.cyan-bar { width: 4px; height: 16px; background: #c8edf9; border-radius: 2px; }
.analysis-content { font-size: 15px; line-height: 1.8; color: var(--text-main); }
.analysis-content p { margin-bottom: 16px; }
.analysis-content p:last-child { margin-bottom: 0; }

/* ================= 底部：带有头像的温馨寄语 ================= */
.report-footer { margin-top: 8px; }
.quote-card { 
  display: flex; align-items: center; gap: 16px; 
  background: #fffbf9; border: 1px solid #e8d1b2; 
  padding: 16px 24px; border-radius: var(--radius-md); 
}
.quote-icon { display: flex; align-items: center; justify-content: center; }
.quote-text { font-size: 14px; line-height: 1.6; color: var(--text-main); flex: 1;}

/* ================= 柔和入场动画 ================= */
.fade-in { animation: fadeIn 0.5s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>

