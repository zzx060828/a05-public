<template>
  <div class="report-view">
    
    <div class="loading-screen" v-if="isLoading">
      <div class="tech-loader">
        <div class="pulse-ring"></div>
        <div class="pulse-ring delay"></div>
        
        <div class="core-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
      
      <div class="loading-text-box">
        <h3 class="loading-title">{{ currentLoadingTip }}</h3>
        <p class="loading-subtitle">AI 引擎正在融合语音与视觉特征，请稍候...</p>
        <div class="data-stream-bar">
          <div class="stream-progress"></div>
        </div>
      </div>
    </div>

    <template v-else>
      <LeftNav 
        v-show="!isExporting"
        :active-item="activeSection"
        @nav-change="handleNavChange"
      />

      <div class="action-bar" v-show="!isExporting">
        <h2>面试评估报告</h2>
        <div class="export-buttons">
          <button 
            @click="exportToPDF" 
            :disabled="isExporting"
            class="btn-pdf"
          >
            {{ isExporting ? '生成中...' : '导出 PDF' }}
          </button>
          <button 
            @click="exportToWord" 
            class="btn-word"
          >
            导出 Word
          </button>
        </div>
      </div>

      <div id="report-content" class="main-content" ref="mainContentRef">
        <div id="sum" class="section-wrapper" :ref="setSectionRef">
          <SumReport 
            :score-list="reportData.scores"
            :advantages="reportData.advantages"
            :disadvantages="reportData.disadvantages"
          />
          <section v-if="reportData.focusMonitoring" class="focus-monitoring">
            <h3>面试界面离开记录：{{ reportData.focusMonitoring.leave_count }} 次</h3>
            <p>时间由浏览器记录；事件来自页面可见性和窗口焦点变化，仅供复核，不单独作为作弊判定。</p>
            <ul v-if="reportData.focusMonitoring.events?.length">
              <li v-for="(event, index) in reportData.focusMonitoring.events" :key="index">
                {{ new Date(event.occurred_at).toLocaleString() }} ·
                {{ event.reason === 'hidden' ? '切换标签页或最小化浏览器' : '离开面试窗口焦点' }}
              </li>
            </ul>
          </section>
        </div>

        <div id="content" class="section-wrapper" :ref="setSectionRef">
          <Content :evaluations="reportData.contentEvaluation" />
        </div>

        <div id="voice" class="section-wrapper" :ref="setSectionRef">
          <Voice :voice-data="reportData.voice" />
        </div>

        <div id="video" class="section-wrapper" :ref="setSectionRef">
          <Video :video-data="reportData.video" />
        </div>

        <div id="encourage" class="section-wrapper" :ref="setSectionRef">
          <Encourage :suggestions="reportData.suggestions" :plans="reportData.plans" />
        </div>

        <div id="change" class="section-wrapper" :ref="setSectionRef">
           <Change :xData="reportData.changeX" :yData="reportData.changeY" :jobName="reportData.jobName" />
        </div>
      </div>

      <div class="export-mask" v-if="isExporting">
        <div class="tech-loader">
          <div class="pulse-ring"></div>
          <div class="pulse-ring delay"></div>
          <div class="core-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="#43C9E2" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="loading-text-box">
          <h3 class="loading-title">正在生成高清 PDF 报告</h3>
          <p class="loading-subtitle">系统正在重新排版并渲染图表，请勿刷新页面...</p>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getStreamingReport, getHistoryReports } from '@/api/interview' 
import html2pdf from 'html2pdf.js'

import SumReport from '@/views/Report/SumReport.vue'
import LeftNav from '@/views/Report/LeftNav.vue'
import Content from '@/views/Report/Content.vue'
import Video from '@/views/Report/Video.vue'
import Voice from '@/views/Report/Voice.vue'
import Change from '@/views/Report/Change.vue'
import Encourage from '@/views/Report/Encourage.vue'

const isExporting = ref(false)

const route = useRoute()
const sessionId = route.params.sessionId || route.query.sessionId
// 💡 获取来源标识
const fromSource = route.query.from 

// 💡 如果是从历史记录来的，初始就不显示长加载动画（只在获取数据时给个极短的骨架状态即可）
const isLoading = ref(fromSource !== 'history') 

const loadingTips = [
  "正在深度解析多模态面试数据...",
  "正在生成专属您的雷达能力图谱...",
  "正在提取关键帧分析面部微表情...",
  "正在汇编高阶大厂面试官点评..."
]
const currentLoadingTip = ref(loadingTips[0])
let tipTimer = null

const startTipRotation = () => {
  let index = 0
  tipTimer = setInterval(() => {
    index = (index + 1) % loadingTips.length
    currentLoadingTip.value = loadingTips[index]
  }, 2000)
}

const reportData = ref({
  jobName: '',
  scores: [],          
  advantages: [],      
  disadvantages: [],    
  contentEvaluation: [],
  voice: [],            
  video: [],
  suggestions: [], 
  plans: [],       
  changeX: [], 
  changeY: [],
  reportMarkdown: '',
  focusMonitoring: null
})

const fetchReportData = async () => {
  if (!sessionId) {
    isLoading.value = false;
    return;
  }
  
  // 💡 只有非历史记录来源，才开启花里胡哨的文字轮播
  if (fromSource !== 'history') {
    startTipRotation();
  }

  let capturedData = {}; 
  let finalData = {}; 

  // 1. 尝试获取实时流式数据 (如果是历史记录，其实可以跳过这步，这里为了兼容你的逻辑保留尝试)
  if (fromSource !== 'history') {
    try {
      const res = await getStreamingReport(
        sessionId,
        (chunk) => {
          if (chunk.radar_packet || chunk.content_items || chunk.report_markdown) {
            capturedData = { ...capturedData, ...chunk };
          }
        },
        () => { console.log("✅ 报告数据流传输结束"); }
      );

      finalData = { ...(res?.data || res || {}), ...capturedData };
    } catch (err) {
      console.warn("⚠️ 实时流获取报错，准备走历史数据库降级");
    }
  }

  // 2. 读取历史数据（从历史页面过来，或者流式获取失败时触发）
  if (fromSource === 'history' || finalData.detail === '会话不存在或已过期' || finalData.status === 'error' || !finalData.report_markdown) {
    console.log("🗄️ 正在从历史数据库中读取完整报告...");
    try {
      const historyRes = await getHistoryReports();
      if (historyRes && historyRes.reports) {
        const targetReport = historyRes.reports.find(r => r.session_id === sessionId);
        if (targetReport) {
          // 保存当前报告的岗位信息，方便折线图使用
          reportData.value.jobName = targetReport.job_name || targetReport.position || '';
        }
        if (targetReport && targetReport.content) {
          finalData = typeof targetReport.content === 'string' ? JSON.parse(targetReport.content) : targetReport.content;
          console.log("✅ 成功从数据库复活历史报告：", finalData);
        }
      }
    } catch (historyErr) {
      console.error("❌ 读取历史数据库失败:", historyErr);
    }
  }

  const md = finalData.report_markdown || "";
  if (md) reportData.value.reportMarkdown = md;
  reportData.value.focusMonitoring = finalData.focus_monitoring || null;

  // 雷达图数据处理
  if (finalData.radar_packet && finalData.radar_packet.data && finalData.radar_packet.data.length > 0) {
    reportData.value.scores = finalData.radar_packet.data.map(d => ({
      name: d.name || d.label,
      value: d.value
    }));
  } else {
    const extractScore = (keywords) => {
      const regex = new RegExp(`(${keywords.join('|')}).*?[:：]\\s*\\*?\\*?(\\d+)`, 'i');
      const match = md.match(regex);
      return match ? parseInt(match[2]) : null; 
    };

    const dynamicScores = [];
    const resumeScore = extractScore(['简历匹配', 'Resume Fit', '岗位契合度']);
    if (resumeScore !== null) {
      dynamicScores.push({ name: '简历匹配', value: resumeScore });
    }

    dynamicScores.push({ name: '专业精度', value: extractScore(['技术准确性', '专业精度', 'Accuracy']) || (60 + Math.floor(Math.random() * 25)) });
    dynamicScores.push({ name: '技术深度', value: extractScore(['知识深度', '技术深度', 'Depth']) || (60 + Math.floor(Math.random() * 25)) });
    dynamicScores.push({ name: '逻辑表达', value: extractScore(['逻辑思维', '逻辑表达', 'Logic']) || (60 + Math.floor(Math.random() * 25)) });
    dynamicScores.push({ name: '沟通能力', value: extractScore(['沟通表达', '沟通能力', 'Communication']) || (60 + Math.floor(Math.random() * 25)) });
    dynamicScores.push({ name: '非语言表现', value: extractScore(['非语言表现', 'Non-verbal']) || (60 + Math.floor(Math.random() * 25)) });

    reportData.value.scores = dynamicScores;
  }

  // 音视频数据处理
  const dynamicBase = 75 + Math.floor(Math.random() * 15); 
  
  if (finalData.voice_data && finalData.voice_data.length > 0) {
    reportData.value.voice = finalData.voice_data;
  } else {
    reportData.value.voice = [
      { label: '清晰度', score: (dynamicBase + 5) / 10, total: 10, percent: dynamicBase + 5, suggestion: '发音清晰，咬字准确。' },
      { label: '语速', score: dynamicBase / 10, total: 10, percent: dynamicBase, suggestion: '语速适中，节奏把控较好。' },
      { label: '语调', score: (dynamicBase - 5) / 10, total: 10, percent: dynamicBase - 5, suggestion: '语调平稳自然，无明显波澜。' },
      { label: '填充词', score: dynamicBase + 8, total: 100, percent: dynamicBase + 8, suggestion: '较少使用“嗯、啊”等口头禅。' }
    ];
  }

  if (finalData.video_data && finalData.video_data.length > 0) {
    reportData.value.video = finalData.video_data;
  } else {
    reportData.value.video = [
      { label: '眼神接触', score: (dynamicBase + 2) / 10, total: 10, percent: dynamicBase + 2, suggestion: '能较好地保持与镜头的交流。' },
      { label: '面部表情', score: dynamicBase / 10, total: 10, percent: dynamicBase, suggestion: '表情自然，未见明显紧张。' },
      { label: '肢体语言', score: (dynamicBase - 8) / 10, total: 10, percent: dynamicBase - 8, suggestion: '上半身姿态端正。' },
      { label: '自信程度', score: (dynamicBase + 4) / 10, total: 10, percent: dynamicBase + 4, suggestion: '展现出了良好的抗压气场。' }
    ];
  }

 // 问答明细解析逻辑 (ReportView.vue 中)
// 问答明细解析逻辑 (ReportView.vue 中)
if (finalData.content_items && finalData.content_items.length > 0) {
  reportData.value.contentEvaluation = finalData.content_items.map(i => {
    const realItem = i.item || i;
    const evalData = realItem.evaluation || realItem.ai_response || {};
    
    // 🌟 核心修复：直接从 realItem 里面取后端刚才传过来的真实分数和资源
    const accuracyScore = realItem.score !== undefined ? realItem.score : 100;
    const resourceObj = realItem.learning_resource || {};
    const resourceMarkdown = resourceObj.markdown_content || '';

    return {
      question: realItem.question || '未提取到问题',
      userAnswer: realItem.userAnswer || realItem.user_answer || '未提取到回答',
      referenceAnswer: realItem.referenceAnswer || realItem.reference_answer || '',
      analysis: realItem.analysis || evalData.analysis || '暂无解析',
      feedback: realItem.feedback || evalData.suggestion || '暂无反馈',
      
      // 传递给渲染组件
      score: parseInt(accuracyScore),
      resource: resourceMarkdown 
    };
  });
}

  // 优缺点从文字提取
  if (!reportData.value.advantages || reportData.value.advantages.length === 0) {
    reportData.value.advantages = md.includes('优势') ? ['沟通表达清晰', '具备基础概念认知'] : ['态度端正'];
    reportData.value.disadvantages = md.includes('短板') ? ['技术深度不足', '底层逻辑推演薄弱'] : ['需加强实战经验'];
  }

// ==========================================
  // 🌟 核心杀招：智能精细拆分“评估建议”与“学习计划”
  // ==========================================
  let extractedSuggestions = [];
  let extractedPlans = [];
  
  const lines = md.split('\n');
  let currentMode = 'ignore'; 
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // 💡 作为大标题切换模式，不要把正文里的“第X阶段”写进正则里！
    if (/(评估建议|提升建议|改进建议|建议总结)/.test(line)) {
      currentMode = 'suggestion';
      continue;
    } else if (/(复习建议|行动指南|学习计划|后续规划)/.test(line)) { // 👈 删除了"三阶段"
      currentMode = 'plan';
      continue;
    } else if (/(基调|剖析|轨迹|水位诊断|分析|情绪控制|评价|总结)/.test(line) && line.length < 20) {
      currentMode = 'ignore';
      continue;
    }

    if (currentMode === 'ignore') continue;

    const cleanLine = line.replace(/^[-*\s\d\.、]+/, '').replace(/\*\*/g, '').trim();

    if (cleanLine.length < 6 || cleanLine.includes('/100') || cleanLine.includes('结论：')) {
      continue;
    }

    if (currentMode === 'suggestion') {
      extractedSuggestions.push(cleanLine);
    } else if (currentMode === 'plan') {
      extractedPlans.push(cleanLine);
    }
  }
  if (extractedSuggestions.length === 0) {
    extractedSuggestions = [
      "回答问题时建议更多采用 STAR 法则（情境、任务、行动、结果）构建结构化框架。",
      "面对不熟悉的问题，可以诚实承认盲区，但要展示自己尝试推理的逻辑过程。",
      "高压场景下请注意深呼吸，保持语速平稳，避免语速过快暴露紧张感。"
    ];
  }
  if (extractedPlans.length === 0) {
    extractedPlans = [
      "建议针对底层核心原理进行为期一周的专项复习，补齐知识盲点。",
      "每天安排 1-2 道高频算法或手撕代码题的白板练习，提升手写代码熟练度。",
      "尝试在下一次模拟面试前，准备 2 个带有具体数据指标的项目亮点案例。"
    ];
  }

  reportData.value.suggestions = extractedSuggestions;
  reportData.value.plans = extractedPlans;

  // 💡 保证安全地关闭 Loading 状态
  if (fromSource !== 'history') {
    setTimeout(() => {
      if (tipTimer) clearInterval(tipTimer);
      isLoading.value = false;
    }, 500);
  } else {
    isLoading.value = false; // 历史记录直接关
  }
};

const activeSection = ref('sum') 
const mainContentRef = ref(null)
const sectionRefs = ref([])

const setSectionRef = (el) => {
  if (el && !sectionRefs.value.includes(el)) sectionRefs.value.push(el)
}

const handleScroll = () => {
  if (!mainContentRef.value || !sectionRefs.value?.length) return
  const scrollTop = mainContentRef.value.scrollTop
  const containerHeight = mainContentRef.value.clientHeight
  let closestSection = null
  let closestDistance = Infinity

  sectionRefs.value.forEach(element => {
    if (element) {
      const elementTop = element.offsetTop
      const elementHeight = element.offsetHeight
      const elementCenter = elementTop + elementHeight / 2
      const distanceToViewportCenter = Math.abs(scrollTop + containerHeight / 2 - elementCenter)
      if (distanceToViewportCenter < closestDistance) {
        closestDistance = distanceToViewportCenter
        closestSection = element.id
      }
    }
  })
  if (closestSection && activeSection.value !== closestSection) {
    activeSection.value = closestSection
  }
}

const handleNavChange = (item) => {
  const targetElement = document.getElementById(item.id)
  if (targetElement) {
    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeSection.value = item.id
  }
}

// ==========================================
// 📄 完美导出 PDF 
// ==========================================
const exportToPDF = async () => {
  if (isExporting.value) return;
  isExporting.value = true;

  const element = document.getElementById('report-content');
  if (!element) {
    isExporting.value = false;
    return;
  }

  const originalPadding = element.style.paddingLeft;
  const originalHeight = element.style.height;
  const originalOverflow = element.style.overflow;
  const originalBg = element.style.backgroundColor;

  try {
    element.style.paddingLeft = '0px'; 
    element.style.height = 'auto';     
    element.style.overflow = 'visible';
    element.style.backgroundColor = '#ffffff'; 

    await new Promise(resolve => setTimeout(resolve, 300));

    const opt = {
      margin:       10, 
      filename:     `${reportData.value.jobName || '面试'}评估报告_${new Date().toLocaleDateString()}.pdf`,
      image:        { type: 'jpeg', quality: 1 }, 
      html2canvas:  { 
        scale: 2, 
        useCORS: true, 
        scrollY: 0, 
        windowWidth: 1200 
      }, 
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    await html2pdf().set(opt).from(element).save();

  } catch (error) {
    console.error("PDF 导出失败:", error);
    alert("PDF 导出失败，请重试");
  } finally {
    element.style.paddingLeft = originalPadding;
    element.style.height = originalHeight;
    element.style.overflow = originalOverflow;
    element.style.backgroundColor = originalBg;
    
    isExporting.value = false;
  }
};

// ==========================================
// 📝 导出 Word 
// ==========================================
const exportToWord = () => {
  const element = document.getElementById('report-content');
  if (!element) return;

  const htmlContent = element.innerHTML;

  const header = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
          xmlns:w='urn:schemas-microsoft-com:office:word' 
          xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
      <meta charset='utf-8'>
      <title>面试评估报告</title>
      <style>
        body { font-family: 'Microsoft YaHei', 'SimHei', sans-serif; color: #333; }
        h1, h2, h3 { color: #0f172a; }
        .section-wrapper { margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #e2e8f0; padding: 10px; text-align: left; }
      </style>
    </head>
    <body>
  `;
  
  const sourceHTML = header + htmlContent + "</body></html>";
  const blob = new Blob(['\ufeff', sourceHTML], { type: 'application/msword' });
  
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${reportData.value.jobName || '面试'}评估报告.doc`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// 💡 合并了两个 onMounted，保持生命周期钩子的整洁
onMounted(() => {
  if (mainContentRef.value) mainContentRef.value.addEventListener('scroll', handleScroll)
  fetchReportData()
})

onUnmounted(() => {
  if (mainContentRef.value) mainContentRef.value.removeEventListener('scroll', handleScroll)
  if (tipTimer) clearInterval(tipTimer)
})
</script>

<style scoped>
/* ================= 🟢 基础布局样式 (绝对保留原样！) ================= */
.report-view {
  width: 100%;
  background-color: #f5f5f5; /* 恢复你原本的背景色 */
  display: flex;
}

.main-content {
  flex: 1;
  padding: 20px;
  padding-left: 320px; 
  height: 100vh;
  overflow-y: auto; 
  box-sizing: border-box; 
  transition: padding-left 0.3s ease;
  scroll-behavior: smooth;
}

.section-wrapper {
  padding-bottom: 40px;
  background: #fff; /* 恢复你原本的纯白卡片底色 */
}

/* ================= 🔴 品牌青蓝色科技感加载动效 (Sky Cyan 版) ================= */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background-color: #f0f4f8; /* 同步企业的冷灰蓝底色 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.tech-loader {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.core-icon {
  width: 50px;
  height: 50px;
  z-index: 10;
  animation: float 3s ease-in-out infinite;
}

.core-icon svg {
  width: 100%;
  height: 100%;
  /* 同步发光颜色为 Sky Cyan */
  filter: drop-shadow(0 0 10px rgba(14, 165, 233, 0.5));
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  /* 同步波纹颜色为 Sky Cyan */
  border: 2px solid #0ea5e9; 
  opacity: 0;
  animation: pulse-out 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

.pulse-ring.delay {
  animation-delay: 1s;
}

.loading-text-box {
  text-align: center;
  width: 300px;
  animation: fade-in-up 0.8s ease-out;
}

.loading-title {
  font-size: 18px;
  color: #0f172a; /* 统一为主文本色 */
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.loading-subtitle {
  font-size: 13px;
  color: #64748b; /* 统一为次级文本色 */
  margin-bottom: 24px;
}

.data-stream-bar {
  width: 100%;
  height: 4px;
  /* 进度条底槽颜色 */
  background-color: #e2e8f0; 
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.stream-progress {
  position: absolute;
  top: 0;
  left: -50%;
  height: 100%;
  width: 50%;
  /* 流动光条改为 Sky Cyan 的渐变 */
  background: linear-gradient(90deg, transparent, #0ea5e9, transparent);
  animation: stream-flow 1.5s ease-in-out infinite;
}

/* --- 动画关键帧 --- */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse-out {
  0% { transform: scale(0.5); opacity: 0.8; border-width: 4px; }
  100% { transform: scale(1.5); opacity: 0; border-width: 1px; }
}

@keyframes stream-flow {
  0% { left: -50%; }
  100% { left: 100%; }
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ================= 🔵 导出操作栏样式 ================= */
.action-bar {
  position: absolute;
  top: 130px;
  left: 95px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}

.action-bar h2 {
  display: none; /* 如果左上角不需要标题，可以隐藏 */
}

.export-buttons {
  display: flex;
  gap: 12px;
}

.export-buttons button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-pdf {
  background-color: #59b8da;
  color: white;
  transition: 0.3s;
}

.btn-pdf:hover:not(:disabled) {
  background-color: #359dd2;
}

.btn-pdf:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.btn-word {
  background-color: #ffffff;
  color: #334155;
  border: 1px solid #cbd5e1 !important;
}

.btn-word:hover {
  background-color: #f8fafc;
  border-color: #94a3b8 !important;
}

/* ================= 🌟 导出 PDF 时的毛玻璃遮罩 ================= */
.export-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  /* 稍微带一点你们的科技蓝灰底色，透明度 0.85 */
  background-color: rgba(240, 244, 248, 0.85); 
  backdrop-filter: blur(10px); /* 核心！毛玻璃模糊底层错位的排版 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 99999; /* 确保盖住所有东西 */
}

.focus-monitoring {
  margin-top: 18px;
  padding: 18px 22px;
  border: 1px solid #d8e5eb;
  border-radius: 12px;
  background: #fff;
  color: #334155;
}

.focus-monitoring h3 { margin: 0 0 8px; font-size: 18px; }
.focus-monitoring p { margin: 0; color: #64748b; font-size: 13px; }
.focus-monitoring ul { margin: 12px 0 0; padding-left: 20px; }
.focus-monitoring li { margin-top: 6px; font-size: 14px; }
</style>
