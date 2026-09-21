<template>
  <div class="learning-detail-page">
    <nav class="top-nav">
      <div class="nav-content">
        <button class="back-btn" @click="$router.push('/record')"> <svg class="back-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span class="back-text">返回面试报告</span>
        </button>
      </div>
    </nav>

    <div v-if="isLoading" class="global-loading-container">
      <div class="glass-loading">
        <div class="loader"></div>
        <p>{{ isFromHistory ? '正在还原历史学习路径...' : 'AI 正在为您组装专属知识盲区秘籍...' }}</p>
      </div>
    </div>

    <div v-else class="layout-wrapper animate-fade-in">
      <aside class="sidebar">
        <div class="sticky-box">
          <div class="info-card">
            <div class="badge">
              <svg t="1775274769042" class="icon-custom" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3051" width="200" height="200"><path d="M520.7 98.2L643 345.9l273.4 39.7-197.8 192.9 46.7 272.3-244.6-128.6-244.5 128.6 46.7-272.3L125 385.6l273.5-39.7z" fill="#F0D155" p-id="3052"></path></svg>              
              专属定制</div>
            <h2>提分攻坚路径</h2>
            <p class="subtitle">针对 {{ role || '当前岗位' }} 深度定制</p>
            
            <div class="progress-section">
              <div class="progress-info">
                <span>学习进度</span>
                <span>{{ currentProgress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: currentProgress + '%' }"></div>
              </div>
            </div>
          </div>

          <div class="outline-card">
            <div 
              v-for="(step, index) in dynamicSteps" 
              :key="index"
              class="step-item"
              :class="{ 
                active: activeStep === index,
                'is-done': step.completed 
              }"
              @click="activeStep = index"
            >
              <div class="step-dot"></div>
              <div class="step-text">{{ step.name }}</div>
              
              <span v-if="step.completed" class="check-mark">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
              </span>
            </div>
          </div>
        </div>
      </aside>

      <main class="content-main">
        <div class="content-card">
          <div class="article-header">
            <div class="header-decoration">Step 0{{ activeStep + 1 }}</div>
            <h1>{{ dynamicSteps[activeStep].name }}</h1>
            <div class="meta-info">
              <span>阅读预计: 5 分钟</span>
              <span>•</span>
              <span>岗位: {{ role || '当前岗位' }}</span>
            </div>

            <div v-if="dynamicSteps[activeStep].originQuestion" class="origin-question-box">
              <strong>关联错题：</strong>{{ dynamicSteps[activeStep].originQuestion }}
            </div>
          </div>

          <article class="pro-markdown-body" v-html="renderedMarkdown"></article>

          <div class="content-footer">
            <p>
              <svg t="1775273911006" class="icon-custom" viewBox="0 0 1025 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3752" width="200" height="200"><path d="M290.03041 0.001466a38.124969 38.124969 0 0 0-27.371772 11.241978L11.42487 261.988431a38.124969 38.124969 0 0 0 5.86538 59.142579 219.462961 219.462961 0 0 0 119.751504 35.192279h6.842943l195.51266 244.390825a413.509276 413.509276 0 0 0 71.850902 391.02532 39.591314 39.591314 0 0 0 30.793244 14.663449 39.102532 39.102532 0 0 0 27.860554-11.73076l236.081537-237.0591 255.632803 255.632803a37.147405 37.147405 0 0 0 26.394209 10.753196 37.147405 37.147405 0 0 0 26.394209-63.541614l-256.610366-256.121584 236.081537-237.059101a39.591314 39.591314 0 0 0-3.421472-58.653798 413.509276 413.509276 0 0 0-387.603848-70.873339l-244.390825-195.51266A218.974179 218.974179 0 0 0 321.801218 17.108824 38.124969 38.124969 0 0 0 290.03041 0.001466z m-16.618576 117.307596a149.567185 149.567185 0 0 1 0 23.461519v41.546441l32.259589 25.905427 244.390825 195.51266 34.703497 27.371772 42.035222-13.685886a331.393958 331.393958 0 0 1 270.785034 28.838118l-195.51266 195.512659-48.878165 48.878165-14.663449 14.66345-195.51266 195.51266a330.905177 330.905177 0 0 1-29.815681-271.762598l17.596139-42.524003-27.371772-34.703497-195.51266-244.390825-25.905427-32.259589H117.490488z" fill="#5E5C5C" p-id="3753"></path></svg> 
              建议：重点学习加粗知识点，并尝试在下次模拟面试中使用。
            </p>
            <button class="finish-btn" @click="handleCompleteStep" :disabled="dynamicSteps[activeStep].completed">
              {{ dynamicSteps[activeStep].completed ? '已完成本章学习' : '标记为已完成' }}
            </button>
          </div>
        </div>
      </main>
    </div>

    <div v-if="showSuccessModal" class="success-modal-overlay" @click.self="showSuccessModal = false">
      <div class="success-modal">
        <div class="modal-icon-wrapper">
          <svg class="success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <h3 class="modal-title">恭喜，通关完成！</h3>
        <p class="modal-desc">
          你已扫除全部知识盲区，完成了本次的专属提分路径。<br>
          准备好用全新的状态迎接下一场面试了吗？
        </p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showSuccessModal = false">留在本页</button>
          <button class="btn-confirm" @click="$router.push('/record')">返回历史记录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { marked } from 'marked';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps(['sessionId', 'role']);
const route = useRoute();
const router = useRouter();

const isFromHistory = computed(() => {
  return route.query.from === 'history' || window.location.href.includes('from=history');
});

const isLoading = ref(true);
const activeStep = ref(0);

// 🌟 新增：控制弹窗显示的变量
const showSuccessModal = ref(false);

// 🌟 提取出固定的“面试心法”静态数据，作为压轴内容
const finalStepName = '面试实战与心态';
const finalStepContent = `## 面试实战与心态建议

**先实践后深入**：
遇到没有做过的技术方案，建议先通过快速搭建 Demo 跑通全流程，再结合书籍与源码解析深化理解，面试时才能做到有血有肉。

**应用 STAR 法则**：
在描述项目经历时，务必按照 情境(Situation)、任务(Task)、行动(Action) 和结果(Result) 来组织语言。**一定要有数据支撑**（例如：加载速度提升 30%，内存占用减少 20MB）。

**大方承认盲区**：
遇到不会的底层原理，与其胡乱猜测，不如诚恳说明自己目前了解的深度，并给出一个合理的推理方向。`;

// 默认兜底的大纲（如果没传错题过来）
const dynamicSteps = ref([]);
const stepContents = ref([]);

const renderedMarkdown = computed(() => {
  return marked(stepContents.value[activeStep.value] || "");
});

const currentProgress = computed(() => {
  if (!dynamicSteps.value || dynamicSteps.value.length === 0) return 0;
  const doneCount = dynamicSteps.value.filter(s => s.completed).length;
  return Math.round((doneCount / dynamicSteps.value.length) * 100);
});

const handleCompleteStep = () => {
  if (dynamicSteps.value[activeStep.value].completed) return; // 防止重复点击
  
  dynamicSteps.value[activeStep.value].completed = true;
  
  if (activeStep.value < dynamicSteps.value.length - 1) {
    setTimeout(() => {
      activeStep.value++;
      window.scrollTo({ top: 0, behavior: 'smooth' }); 
    }, 400); 
  } else if (currentProgress.value === 100) {
    setTimeout(() => {
      // 🌟 替换丑陋的 alert 为优雅的自定义弹窗
      showSuccessModal.value = true;
    }, 300); // 稍微延时让进度条跑到 100%
  }
};

onMounted(async () => {
  try {
    const weakDataStr = sessionStorage.getItem(`weak_resources_${props.sessionId}`);
    
    let hasWeakData = false;

    // 🌟 场景 1：有错题数据传过来（完美千人千面）
    if (weakDataStr) {
      const weakItems = JSON.parse(weakDataStr);
      
      if (weakItems && weakItems.length > 0) {
        hasWeakData = true;
        dynamicSteps.value = [];
        stepContents.value = [];

        // 1. 先把所有错题循环塞进去
        weakItems.forEach((item, index) => {
          dynamicSteps.value.push({
            name: `专项突破：问题 ${index + 1}`, // 优化了侧边栏文案，显得更专业
            originQuestion: item.question,  
            completed: false
          });
          
          const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{2B50}\u{2B55}]/gu;
          let cleanMd = (item.resource || '').replace(emojiRegex, '').replace(/  +/g, ' ');
          stepContents.value.push(cleanMd);
        });
        
        // 2. 在最后追加固定的“面试心法”
        dynamicSteps.value.push({ name: finalStepName, completed: false });
        stepContents.value.push(finalStepContent);
        
        marked.setOptions({ gfm: true, breaks: true });
      }
    }

    // 🌟 场景 2：没传错题过来（全局大纲兜底）
    if (!hasWeakData) {
      const response = await axios.get('http://127.0.0.1:8001/api/rag/recommend_resources', {
        params: {
          session_id: props.sessionId,
          role: props.role
        }
      });
      
      if (response.data.status === 'success') {
        marked.setOptions({ gfm: true, breaks: true });
        const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{2B50}\u{2B55}]/gu;
        let cleanMd = response.data.resources.replace(emojiRegex, '').replace(/  +/g, ' ');
        
        // 兜底时：Step 1 是全局进阶资料，Step 2 是面试心法
        dynamicSteps.value = [
          { name: '核心架构进阶', completed: false },
          { name: finalStepName, completed: false }
        ];
        stepContents.value = [cleanMd, finalStepContent];
      }
    }
  } catch (error) {
    if (stepContents.value.length === 0) {
      stepContents.value.push("### 内容获取失败\n\n数据同步超时，请稍后刷新重试。");
      dynamicSteps.value.push({ name: '加载失败', completed: false });
    }
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
/* 保持你原本所有的样式不变 */
.learning-detail-page {
  background-color: #f6f8fa;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  padding-top: 80px; 
}

.top-nav {
  position: fixed;
  top: 80px; 
  left: 0;
  width: 100%;
  height: 56px;
  background: transparent; 
  z-index: 90;
  display: flex;
  align-items: center;
}

.nav-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

.back-btn {
  background: none;
  border: none;
  color: #4b5563; 
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px; 
  transition: all 0.2s;
  padding: 0; 
}
.back-btn:hover { color: #4e6fb5; transform: translateX(-4px); }
.back-icon { display: block; }
.back-text { line-height: 1; }

.global-loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 140px); 
  width: 100%;
}

.layout-wrapper {
  max-width: 1200px;
  margin: 20px auto 40px; 
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
  padding: 0 40px;
}

.sidebar .sticky-box { position: sticky; top: 156px; }

.info-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 20px;
  padding: 24px;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.badge {
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  width: max-content;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-card h2 { margin: 0; font-size: 18px; }
.subtitle { opacity: 0.7; font-size: 12px; margin: 8px 0 20px; }

.progress-info { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
.progress-bar { height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden; }
.progress-fill { 
  height: 100%; 
  background: #5492f5; 
  border-radius: 3px; 
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); 
}

.outline-card {
  margin-top: 20px;
  background: white;
  border-radius: 16px;
  padding: 8px;
  border: 1px solid #e5e7eb;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.step-item:hover { background: #f9fafb; }
.step-item.active { background: #f0f7ff; color: #4465ac; font-weight: 600; }
.step-item.is-done .step-dot { background: #4fb88c; }
.step-item.is-done .step-text { color: #4fb88c; }

.step-dot { width: 8px; height: 8px; background: #cbd5e1; border-radius: 50%; transition: all 0.3s; }
.active .step-dot { background: #2d56ad; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1); }

.check-mark { 
  margin-left: auto; 
  color: #328f75; 
  display: flex; 
  align-items: center; 
}

.content-card {
  background: white;
  border-radius: 24px;
  padding: 48px; 
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.article-header { border-bottom: 1px solid #f3f4f6; padding-bottom: 24px; margin-bottom: 32px; }
.header-decoration { color: #4573be; font-weight: 800; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.article-header h1 { font-size: 28px; margin: 0; color: #111827; }
.meta-info { margin-top: 12px; font-size: 13px; color: #9ca3af; }

/* 原错题样式 */
.origin-question-box {
  margin-top: 20px;
  padding: 12px 16px;
  background-color: #f1f5f9;
  border-left: 4px solid #38bdf8;
  border-radius: 6px;
  font-size: 14px;
  color: #334155;
  line-height: 1.6;
}
.origin-question-box strong {
  color: #0284c7;
}

.pro-markdown-body :deep(h2) { 
  font-size: 20px; 
  color: #1e293b; 
  margin-top: 32px; 
  padding-bottom: 8px; 
  border-bottom: 1px solid #f1f5f9; 
  display: flex;
  align-items: center;
}
.pro-markdown-body :deep(h2)::before {
  content: '';
  display: inline-block;
  width: 5px;
  height: 18px;
  background: #3891c1;
  border-radius: 4px;
  margin-right: 12px;
}

.pro-markdown-body :deep(p) { line-height: 1.8; color: #4b5563; font-size: 15px; margin: 16px 0; }
.pro-markdown-body :deep(strong) { color: #111827; font-weight: 600; background: linear-gradient(180deg, transparent 70%, #dbeafe 0); }
.pro-markdown-body :deep(blockquote) { margin: 24px 0; padding: 16px 24px; background: #f8fafc; border-left: 4px solid #3e5e92; border-radius: 4px; color: #334155; }
.pro-markdown-body :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 12px; overflow-x: auto; margin: 20px 0; }

.finish-btn {
  margin-top: 40px;
  width: 100%;
  padding: 14px;
  background: #749fd3;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.finish-btn:hover:not(:disabled) { background: #4676b2; }
.finish-btn:disabled { background: #9ca3af; cursor: not-allowed; opacity: 0.8; }

.glass-loading { display: flex; flex-direction: column; align-items: center; padding: 100px 0; color: #94a3b8; }
.loader { width: 32px; height: 32px; border: 3px solid #e5e7eb; border-top-color: #658bc9; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.4s ease-out; }

.icon-custom { width: 15px; height: 15px; margin-right: 5px; }
.icon { width: 15px; height: 15px; }


/* ========================================= */
/* 🌟 新增：优雅的通关弹窗样式 */
/* ========================================= */

.success-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: overlay-fade-in 0.3s ease-out;
}

.success-modal {
  background: #ffffff;
  width: 420px;
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modal-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-icon-wrapper {
  width: 64px;
  height: 64px;
  background: #dcfce7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 0 0 8px rgba(220, 252, 231, 0.5);
}

.success-icon {
  width: 32px;
  height: 32px;
  color: #16a34a;
}

.modal-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px;
}

.modal-desc {
  font-size: 15px;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 32px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 12px 0;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f1f5f9;
  color: #475569;
}
.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-confirm {
  background: #5492f5;
  color: #ffffff;
}
.btn-confirm:hover {
  background: #3e7de6;
}

@keyframes overlay-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-pop {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>