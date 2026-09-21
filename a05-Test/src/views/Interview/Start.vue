<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useInterviewSession } from '@/composables/useInterviewSession'

defineOptions({ name: 'InterviewStart' })
const route = useRoute()
const emit = defineEmits(['interview-end'])

const {
  phase,
  questionText,
  questionIndex,
  answerText,
  startupError,
  networkOffline,
  isHumanActive,
  isHumanLoading,
  isSpeaking,
  isRecording,
  isSubmitting,
  canAnswer,
  isRecordDisabled,
  micOn,
  leaveCount,
  showWarningModal,
  warningReason,
  isFormalExam,
  difficulty,
  candidate,
  metrics,
  insights,
  timer,
  progress,
  humanContainer,
  videoRef,
  canvasRef,
  audioLevel,
  activateInterview,
  endInterview,
  toggleMic,
  stopRecording,
  handleTextSubmit,
  retryLastAudio,
  pendingAudioBlob,
  closeWarningModal
} = useInterviewSession(route, emit)
</script>
<template>
  <div class="ami-page light-enterprise-theme">
    <div class="app-shell">
      
      <header class="topbar">
        <div class="topbar-left">
          <span class="status-dot animation-blink"></span>
          <span class="topbar-title">面伴 AI 面试室</span>
        </div>
        <div class="topbar-right">
          <div class="metric-pill">
            <svg class="icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor"><path d="M512 64C264.8 64 64 264.8 64 512s200.8 448 448 448 448-200.8 448-448S759.2 64 512 64z m0 832c-212 0-384-172-384-384s172-384 384-384 384 172 384 384-172 384-384 384z m32-393.6l191.2 110.4-32 55.2L488.8 544H480V256h64v246.4z"></path></svg>
            <span class="timer-text">{{ timer.current }} / {{ timer.total }}</span>
          </div>
          <div class="metric-pill">
            <span class="muted-text">难度</span>
            <div class="difficulty-bars">
              <span class="bar" :class="{ on: difficulty.level >= 1 }"></span>
              <span class="bar" :class="{ on: difficulty.level >= 2 }"></span>
              <span class="bar" :class="{ on: difficulty.level >= 3 }"></span>
              <span class="bar" :class="{ on: difficulty.level >= 4 }"></span>
              <span class="bar" :class="{ on: difficulty.level >= 5 }"></span>
            </div>
          </div>
          <button class="btn-danger-outline" type="button" @click="() => endInterview(false)">结束面试</button>
        </div>
      </header>

      <main class="workspace">
        <section class="stage-area">
          
          <div class="video-container">
            <div class="video-header">
              <div class="speaker-name">专家面试官 (AI)</div>
            </div>

            <div ref="humanContainer" class="digital-human-container"></div>

            <div v-if="isHumanLoading" class="loading-overlay">
              <div class="spinner"></div>
              <p class="loading-text">正在连线面试官...</p>
            </div>

            <div class="user-pip">
              <video ref="videoRef" autoplay muted playsinline class="user-video"></video>
              <canvas ref="canvasRef" style="display: none;"></canvas>
              <div class="pip-label">您</div>
            </div>
          </div>

          <div class="control-console">
            
            <div class="question-header">
              <div class="flex-between w-100">
                <span class="q-badge">问题 {{ questionIndex }}</span>
                <span class="btn-text-primary" aria-live="polite">
                  {{ isSpeaking ? '面试官正在提问' : (isSubmitting ? 'AI 正在分析' : (canAnswer ? '请开始作答' : '准备中')) }}
                </span>
              </div>
              <div class="q-text">{{ questionText }}</div>
            </div>

            <div class="input-workspace">
              <div class="mic-controls">
                <button 
                  class="btn-mic" 
                  :class="{ active: micOn, recording: isRecording }" 
                  @click="toggleMic"
                    :disabled="isRecordDisabled || isSpeaking || isSubmitting || answerText.trim().length > 0"
                >
                  <svg class="icon" viewBox="0 0 1024 1024" width="18" height="18" fill="currentColor"><path d="M544 830.4V960h-64v-129.6c-161.6-16-288-152.8-288-318.4h64c0 140.8 115.2 256 256 256s256-115.2 256-256h64c0 165.6-126.4 302.4-288 318.4zM512 640c70.4 0 128-57.6 128-128V192c0-70.4-57.6-128-128-128s-128 57.6-128 128v320c0 70.4 57.6 128 128 128z"></path></svg>
                  <span v-if="isRecording">录制中...</span>
                  <span v-else-if="answerText.trim().length > 0">清空文字后语音</span>
                  <span v-else>点击使用语音回答</span>
                </button>
                
                <div class="dynamic-wave" v-show="isRecording">
                  <div class="wave-bar" :style="{ transform: `scaleY(${audioLevel * 0.6})` }"></div>
                  <div class="wave-bar" :style="{ transform: `scaleY(${audioLevel * 1.1})` }"></div>
                  <div class="wave-bar" :style="{ transform: `scaleY(${audioLevel * 1.5})` }"></div>
                  <div class="wave-bar" :style="{ transform: `scaleY(${audioLevel * 1.0})` }"></div>
                  <div class="wave-bar" :style="{ transform: `scaleY(${audioLevel * 0.7})` }"></div>
                </div>

                <button v-if="isRecording" class="btn-stop-record ml-auto" @click="stopRecording">结束录制并提交</button>
                <button v-else-if="pendingAudioBlob && canAnswer" class="btn-stop-record ml-auto" @click="retryLastAudio">重试上次上传</button>
              </div>

              <div class="text-input-area">
                <textarea 
                  v-model="answerText" 
                  placeholder="或在此输入文字回答..."
                  :disabled="isRecording || isSpeaking || isSubmitting || !canAnswer"
                ></textarea>
                <button class="btn-send" @click="handleTextSubmit" :disabled="!answerText.trim() || isRecording || isSpeaking || isSubmitting || !canAnswer">
                  {{ isSubmitting ? '提交中...' : '提交答案' }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <aside class="sidebar-panel">
          <div class="panel-card candidate-info">
            <div class="candidate-avatar"></div>
            <div class="candidate-details">
              <div class="name">{{ candidate.name }}</div>
              <div class="desc">{{ candidate.desc }}</div>
            </div>
          </div>

          <div class="panel-card progress-card">
            <div class="flex-between mb-2">
              <span class="panel-title">面试进度</span>
              <span class="highlight-text">{{ progress.percent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progress.percent + '%' }"></div>
            </div>
            <div class="flex-between mt-2 text-xs text-muted">
              <span>已答: {{ progress.currentQ - 1 }} 题</span>
              <span>剩: {{ timer.current }}</span>
            </div>
          </div>

          <div class="metrics-container" v-if="!isFormalExam">
            <div class="panel-title mb-3">实时监控能力</div>
            <div v-for="m in metrics" :key="m.key" class="metric-item">
              <div class="flex-between">
                <span class="metric-name">{{ m.name }}</span>
                <span class="metric-val" :style="{ color: m.value > 80 ? '#10b981' : (m.value > 60 ? '#38c7d6' : '#f59e0b') }">{{ m.value }}%</span>
              </div>
              <div class="metric-track mt-1">
                <div class="metric-fill" :style="{ width: m.value + '%', background: m.value > 80 ? '#10b981' : (m.value > 60 ? '#38c7d6' : '#f59e0b') }"></div>
              </div>
              <div class="metric-note">{{ m.note }}</div>
            </div>
          </div>

          <div class="panel-card insight-box">
            <div class="panel-title mb-2 flex-align-center gap-2">
              AI 实时分析
            </div>
            <div class="insight-list">
              <div v-for="(it, idx) in insights" :key="idx" class="insight-item">
                <strong class="text-dark">{{ it.title }}:</strong> {{ it.text }}
              </div>
            </div>
          </div>
        </aside>
      </main>

      <div v-if="!isHumanActive && !isHumanLoading" class="pre-join-overlay">
        <div class="meeting-modal">
          <div class="modal-header">
            <h2>设备与环境检查</h2>
          </div>
          <div class="modal-body">
            <div class="video-preview-skeleton">
              <svg viewBox="0 0 24 24" width="48" height="48" fill="#cbd5e1"><path d="M15 8v8H5V8h10m1-2H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4V7c0-.55-.45-1-1-1z"/></svg>
            </div>
            <ul class="check-list">
              <li><span class="check-icon">✔</span> 点击进入后申请摄像头权限；首次录音时申请麦克风权限</li>
              <li><span class="check-icon">✔</span> 请确保面部处于画面中央</li>
              <li><span class="check-icon">✔</span> <strong>面试期间请勿切屏</strong>，否则将被记录异常</li>
            </ul>
            <p v-if="startupError" class="text-danger">{{ startupError }}，请检查网络后重试。</p>
            <p v-if="networkOffline" class="text-danger">当前网络不可用。</p>
            <button class="btn-join-meeting" @click="activateInterview">
              {{ phase === 'error' ? '重新连接面试官' : '正式进入面试' }}
            </button>
          </div>
        </div>
      </div>

    </div>

    <div v-if="showWarningModal" class="warning-overlay">
      <div class="warning-modal">
        <div class="warning-icon">
          <svg t="1775530000857" class="w-icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5368" width="200" height="200"><path d="M1001.661867 796.544c48.896 84.906667 7.68 157.013333-87.552 157.013333H110.781867c-97.834667 0-139.050667-69.504-90.112-157.013333l401.664-666.88c48.896-87.552 128.725333-87.552 177.664 0l401.664 666.88zM479.165867 296.533333v341.333334a32 32 0 1 0 64 0v-341.333334a32 32 0 1 0-64 0z m0 469.333334v42.666666a32 32 0 1 0 64 0v-42.666666a32 32 0 1 0-64 0z" fill="#FAAD14" p-id="5369"></path></svg>
        </div>
        <h3 class="warning-title">安全监控提示</h3>
        <p class="warning-desc">
          检测到您刚才 <strong>{{ warningReason }}</strong>！<br/>
          这是第 <span class="highlight">{{ leaveCount }}</span> 次离开面试界面。
        </p>
        <p class="warning-sub">为了保证面试公平性，请全程保持页面专注，切屏记录将被同步至面试报告中。</p>
        <button class="warning-btn" @click="closeWarningModal">我知道了，回到面试</button>
      </div>
    </div>

  </div>
</template>


<style scoped>
/* ================= 全局变量：清爽青蓝 + 奶黄暖色 ================= */
.light-enterprise-theme {
  --bg-app: #f2f8fa;        
  --bg-surface: #ffffff;    
  --bg-surface-hover: #f8fafc;
  --border-color: #e2e8f0;  
  --text-main: #1e293b;     
  --text-muted: #64748b;    
  --accent-cyan: #38a1d6;   
  --accent-cyan-light: #e0f6f8; 
  --accent-cyan-dark: #3188a4;
  --accent-yellow: #fde047; 
  --accent-yellow-bg: #fefce8; 
  --accent-yellow-text: #a16207; 
  --accent-green: #34d399;  
  --accent-red: #f87171;    
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --shadow-card: 0 4px 20px rgba(56, 199, 214, 0.05); 
  
  min-height: 100%; padding: 20px; background-color: var(--bg-app); color: var(--text-main); margin-top: 60px; height: calc(100vh - 60px); box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-shell { width: 100%; max-width: 1440px; height: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; position: relative; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.flex-align-center { display: flex; align-items: center; }
.w-100 { width: 100%; }
.gap-2 { gap: 8px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 12px; }
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.ml-auto { margin-left: auto; }
.text-xs { font-size: 12px; }
.text-muted { color: var(--text-muted); }
.text-white { color: white; }

/* ================= 顶部控制栏 ================= */
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); margin-top: 5px;}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 16px; font-weight: 700; color: var(--accent-cyan-dark); }
.status-dot { width: 10px; height: 10px; background-color: var(--accent-red); border-radius: 50%; }
.animation-blink { animation: blink 2s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.metric-pill { display: flex; align-items: center; gap: 8px; padding: 6px 14px; background: #f8fafc; border: 1px solid var(--border-color); border-radius: 999px; font-size: 14px; color: var(--text-muted); }
.difficulty-bars { display: flex; gap: 3px; }
.difficulty-bars .bar { width: 4px; height: 12px; background: #cbd5e1; border-radius: 2px; }
.difficulty-bars .bar.on { background: var(--accent-cyan); }
.btn-danger-outline { background: white; border: 1px solid #fecaca; color: var(--accent-red); padding: 6px 16px; border-radius: 999px; font-size: 14px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-danger-outline:hover { background: #fef2f2; border-color: var(--accent-red); }

/* ================= 主工作区 ================= */
.workspace { display: flex; flex: 1; gap: 16px; min-height: 0; }
.stage-area { flex: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0; }

/* 🔴 1. 恢复视频容器的绝对 C 位 (flex: 1 占满所有剩余空间) */
.video-container {
  flex: 1; 
  min-height: 350px; /* 保证哪怕屏幕很小，视频也不会太扁 */
  position: relative; background: #1e293b; border-radius: var(--radius-lg); overflow: hidden; 
  box-shadow: var(--shadow-card);
}
.video-header { position: absolute; top: 16px; left: 16px; z-index: 10; background: rgba(255, 255, 255, 0.9); padding: 5px 14px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.5); }
.speaker-name { font-size: 13px; font-weight: 600; color: var(--accent-cyan-dark); }
.digital-human-container { width: 100%; height: 100%; }
:deep(.digital-human-container video), :deep(.digital-human-container canvas) { width: 100% !important; height: 100% !important; object-fit: cover; object-position: center 20%; }
.user-pip { position: absolute; bottom: 20px; right: 20px; width: 180px; height: 120px; background: #000; border-radius: var(--radius-md); border: 2px solid white; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); z-index: 10; }
.user-video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.pip-label { position: absolute; bottom: 6px; left: 6px; background: rgba(0,0,0,0.6); color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px; }

/* 🔴 2. 压缩问答控制台 (不再 flex: 1，只占自己需要的高度) */
.control-console {
  background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); 
  padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; box-shadow: var(--shadow-card);
  flex-shrink: 0; /* 防止被上面的视频挤压变形 */
}

/* 完美左对齐：问题文本上下排布 */
.question-header { display: flex; flex-direction: column; padding-bottom: 12px; border-bottom: 1px dashed var(--border-color); }
.q-badge { display: inline-block; width: fit-content;  color: var(--accent-cyan-dark); border: 1px solid #c8eef1; font-size: 15px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.q-text { font-size: 18px; font-weight: 600; line-height: 1.5; color: var(--text-main); margin-top: 10px; } 
.btn-text-primary { background: transparent; border: none; color: var(--accent-cyan); font-weight: 600; cursor: pointer; font-size: 14px; transition: 0.2s;}
.btn-text-primary:hover { color: var(--accent-cyan-dark); }

.input-workspace { display: flex; flex-direction: column; gap: 12px; }
.mic-controls { display: flex; align-items: center; gap: 12px; }
.btn-mic { display: flex; align-items: center; gap: 8px; background: white; border: 1px solid #cbd5e1; color: var(--text-main); padding: 8px 16px; border-radius: 999px; font-size: 14px; font-weight: 500; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.btn-mic:hover:not(:disabled) { border-color: var(--accent-cyan); color: var(--accent-cyan-dark); background: var(--accent-cyan-light); }
.btn-mic.recording { background: #ecfdf5; border-color: var(--accent-green); color: #059669; }
.btn-mic:disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; border-color: #e2e8f0;}
.btn-stop-record { background: white; color: var(--accent-red); border: 1px solid #fca5a5; padding: 8px 16px; border-radius: 25px; font-weight: 500; cursor: pointer; transition: 0.3s;}
.btn-stop-record:hover{background: #fef2f2; border-color: var(--accent-red);}
.dynamic-wave { display: flex; align-items: center; gap: 4px; height: 20px; margin-left: 12px; }
.wave-bar { width: 4px; height: 10px; background: var(--accent-green); border-radius: 2px; transition: transform 0.05s ease-out; }

/* 🔴 3. 缩小输入框，保持精致感 */
.text-input-area { display: flex; gap: 12px; align-items: flex-end; } 
.text-input-area textarea {
  flex: 1; height: 80px; /* 固定为精巧的高度 */
  background: #f8fafc; border: 1px solid var(--border-color); color: var(--text-main);
  border-radius: var(--radius-sm); padding: 12px 16px; resize: none; font-family: inherit; font-size: 14px; line-height: 1.5; transition: 0.2s;
}
.text-input-area textarea:focus { outline: none; border-color: var(--accent-cyan); background: white;  }
.btn-send {
  height: 44px; /* 与底部对齐，按钮高度适中 */
  background: #47bae1; color: white; border: none; border-radius: var(--radius-sm); padding: 0 24px; font-weight: 600; font-size: 15px; cursor: pointer; transition: 0.3s; 
}
.btn-send:hover:not(:disabled) { background: #59a4bf;  }
.btn-send:disabled { background: #e2e8f0; color: #94a3b8; box-shadow: none; cursor: not-allowed; }

/* ================= 右侧：专业面板 ================= */
.sidebar-panel { width: 340px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.panel-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 16px; box-shadow: var(--shadow-card); }
.panel-title { font-size: 14px; font-weight: 700; color: var(--text-main); }
.highlight-text { color: var(--accent-cyan-dark); font-weight: bold; font-size: 16px; }
.candidate-info { display: flex; align-items: center; gap: 12px; }
.candidate-avatar { width: 48px; height: 48px; background: url(/public/images/AIavatar.png) center/cover; border-radius: 50%; border: 1px solid var(--border-color); 
object-fit: cover;  /* 保证图片按比例裁剪充盈盒子，绝对不拉伸变形 */
  flex-shrink: 0;}
.candidate-details .name { font-size: 15px; font-weight: bold; color: var(--text-main); }
.candidate-details .desc { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.progress-track, .metric-track { height: 6px; background: #f1f5f9; border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--accent-cyan); }
.metrics-container { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 16px; flex: 1; box-shadow: var(--shadow-card); }
.metric-item { margin-bottom: 16px; }
.metric-item:last-child { margin-bottom: 0; }
.metric-name { font-size: 13px; color: var(--text-muted); font-weight: 500; }
.metric-val { font-size: 13px; font-weight: 700; }
.metric-note { font-size: 11px; color: #94a3b8; margin-top: 6px; }

.metric-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 1.2s cubic-bezier(0.25, 1, 0.2, 1), background 0.8s ease;
}
.metric-track {
  height: 6px; 
  background: #e2e8f0; 
  border-radius: 999px; 
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
}

.insight-list { display: flex; flex-direction: column; gap: 10px; }
.insight-item { font-size: 13px; color: var(--accent-yellow-text); line-height: 1.5; background: var(--accent-yellow-bg); border: 1px solid rgba(215, 205, 128, 0.893); padding: 10px 12px; border-radius: 8px; }
.insight-item strong { color: #854d0e; }

/* ================= 准备入场弹窗 ================= */
.pre-join-overlay { position: absolute; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 50; border-radius: var(--radius-lg); }
.meeting-modal { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); width: 420px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-header { padding: 20px; border-bottom: 1px solid var(--border-color); text-align: center; background: #f8fafc; }
.modal-header h2 { margin: 0; font-size: 18px; color: var(--text-main); font-weight: 700; }
.modal-body { padding: 24px; }
.video-preview-skeleton { height: 160px; background: #f1f5f9; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; margin-bottom: 20px; border: 1px dashed #cbd5e1; }
.check-list { list-style: none; padding: 0; margin: 0 0 24px 0; }
.check-list li { color: var(--text-muted); font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
.check-icon { color: var(--accent-cyan); font-weight: bold; }
.btn-join-meeting { width: 100%; background: #4cbdda; color: white; border: none; padding: 12px; border-radius: var(--radius-sm); font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s;  }
.btn-join-meeting:hover { background: #33a4c4;  }

/* ================= 加载中 ================= */
.loading-overlay { position: absolute; inset: 0; background: rgba(255, 255, 255, 0.85); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; backdrop-filter: blur(2px); }
.spinner { width: 40px; height: 40px; border: 3px solid #e0f6f8; border-top-color: var(--accent-cyan); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: var(--text-main); font-size: 14px; font-weight: 600;}

/* ================= 防切屏弹窗样式 ================= */
.warning-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px); /* 磨砂玻璃效果，防止切回来偷看题目 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 必须最高，盖住数字人和视频 */
}

.warning-modal {
  background: #ffffff;
  width: 400px;
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.warning-title {
  margin: 0 0 15px 0;
  font-size: 20px;
  color: #333;
  font-weight: bold;
}

.warning-desc {
  font-size: 16px;
  color: #555;
  line-height: 1.5;
  margin-bottom: 10px;
}

.warning-desc .highlight {
  color: #e74c3c;
  font-weight: bold;
  font-size: 18px;
}

.warning-sub {
  font-size: 13px;
  color: #888;
  margin-bottom: 25px;
  line-height: 1.4;
}

.warning-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  transition: background 0.2s;
}

.warning-btn:hover {
  background: #d23f2f;
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
.w-icon{
  width: 60px;
  height: 60px;
}

/* ==========================================
   🚨 防切屏警告弹窗样式
========================================== */
.warning-overlay {
  position: fixed;
  top: 0; 
  left: 0; 
  width: 100vw; 
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px); /* 背景虚化效果 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 确保弹窗在最顶层 */
}

.warning-modal {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px 24px;
  width: 400px;
  text-align: center;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modal-pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
}

@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}

.warning-icon {
  margin-bottom: 16px;
}

.warning-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.warning-desc {
  font-size: 15px;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 8px;
}

.warning-desc .highlight {
  color: #ef4444; /* 醒目的红色提醒 */
  font-weight: 700;
  font-size: 18px;
  padding: 0 4px;
}

.warning-sub {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 24px;
}

.warning-btn {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
}

.warning-btn:hover {
  background: #d97706;
}

/* ==========================================
   🌊 录音时的动态音浪样式
========================================== */
.dynamic-wave {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 24px;
  margin: 0 16px;
}

.wave-bar {
  width: 4px;
  height: 100%;
  background: #10b981; /* 绿色音浪 */
  border-radius: 2px;
  transform-origin: center;
  /* 平滑的缩放过渡，配合 JS 里的 requestAnimationFrame */
  transition: transform 0.05s linear; 
}

/* ==========================================
   🌟 结束面试/离开页面 确认弹窗的高级样式
   ========================================== */

/* 1. 弹窗主容器重置 */
:global(.custom-msg-box) {
  border-radius: 16px !important;
  overflow: hidden !important;
  padding: 0 !important;
  border: none !important;
  width: 500px !important;
  max-width: 90vw !important;
}

/* 2. 头部浅蓝背景 & 标题文字 */
:global(.custom-msg-box .el-message-box__header) {
  background-color: #eaf5ff !important; /* 浅蓝背景 */
  margin: 0 !important;
  padding: 24px 30px !important;
  border-bottom: 1px solid #eaf5ff !important;
}
:global(.custom-msg-box .el-message-box__title) {
  font-size: 18px !important;
  font-weight: 800 !important;
  color: #111827 !important;
  letter-spacing: 0.5px !important;
  justify-content: flex-start !important;
}

/* 右上角关闭 X 按钮 */
:global(.custom-msg-box .el-message-box__headerbtn) {
  top: 24px !important;
  right: 24px !important;
}
:global(.custom-msg-box .el-message-box__headerbtn .el-message-box__close) {
  color: #111827 !important;
  font-size: 20px !important;
}

/* 3. 中间提示内容区 */
:global(.custom-msg-box .el-message-box__content) {
  padding: 40px 30px !important;
  font-size: 15px !important;
  color: #64748b !important;
  line-height: 1.6 !important;
}
:global(.custom-msg-box .el-message-box__container) {
  align-items: flex-start !important; /* 让文字左对齐，去除默认自带的小图标 */
}
:global(.custom-msg-box .el-message-box__status) {
  display: none !important; /* 隐藏默认的感叹号图标，显得更干净 */
}

/* 4. 底部按钮区域 */
:global(.custom-msg-box .el-message-box__btns) {
  padding: 0 30px 30px 30px !important;
}

/* 所有的按钮基础样式 */
:global(.custom-msg-box .el-message-box__btns .el-button) {
  border-radius: 8px !important;
  padding: 12px 16px !important;
  font-weight: 500 !important;
  height: auto !important;
}

/* 取消/返回按钮 (浅灰色) */
:global(.custom-msg-box .el-message-box__btns .el-button:not(.el-button--primary)) {
  background-color: #e2e8f0 !important;
  border-color: #e2e8f0 !important;
  color: #475569 !important;
}
:global(.custom-msg-box .el-message-box__btns .el-button:not(.el-button--primary):hover) {
  background-color: #cbd5e1 !important;
  border-color: #cbd5e1 !important;
  color: #334155 !important;
}

/* 确认离开/结束按钮 (天际青/亮蓝) */
:global(.custom-msg-box .el-message-box__btns .el-button--primary) {
  background-color: #4cbdda !important;
  border-color: #4cbdda !important;
  color: #ffffff !important;
}
:global(.custom-msg-box .el-message-box__btns .el-button--primary:hover) {
  background-color: #33a4c4 !important;
  border-color: #33a4c4 !important;
}


</style>

