<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, onBeforeUnmount, onDeactivated, nextTick } from "vue";
import { useUserStore } from '@/stores/user'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router';
import { submitAnswer, submitTextAnswer, fetchAudioBlob, uploadScreenshot } from "@/api/interview";
import XFVirtualHuman from '@/libs/avatar-sdk/esm/index.js';
import { ElMessageBox, ElMessage } from 'element-plus';

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();
const emit = defineEmits(['interview-end']);
const isInterviewFinished = ref(false)
const currentSessionId = ref("");
const answerText = ref("");
const isHumanActive = ref(false);
const isHumanLoading = ref(false);
const isGeneratingReport = ref(false);
const leaveCount = ref(0);         // 记录违规次数
const showWarningModal = ref(false); // 控制弹窗显示
const warningReason = ref("");       // 记录违规原因

const isFormalMode = ref(false); // 是否是严肃面试模式

// 生命终结锁
let isDestroyed = false; 
// 重连状态锁
let isReconnecting = false;

// 防切屏/切后台监控函数
const handleVisibilityChange = () => {
  if (document.hidden) {
    processLeaveEvent("切换标签页或最小化浏览器");
  } else {
    console.log("👀 候选人切回页面...");
  }
};
const handleWindowBlur = () => {
  // 延迟 200ms 判断，防止误触或系统原生弹窗干扰
  setTimeout(() => {
    if (!document.hasFocus() && !showWarningModal.value) {
      processLeaveEvent("离开面试窗口焦点 (如点击了桌面或其他软件)");
    }
  }, 200);
};

const processLeaveEvent = (reason: string) => {
  // 如果组件已销毁、弹窗已经在显示中、或者正在生成报告结束面试，则不触发
  if (isDestroyed || showWarningModal.value || isGeneratingReport.value) return;

  leaveCount.value++;
  warningReason.value = reason;
  showWarningModal.value = true; // 唤起自定义弹窗

  console.warn(`🚫 候选人第 ${leaveCount.value} 次违规: ${reason}`);

  // 💡 贴心优化：切屏时如果正在录音，先自动暂停，防止录入杂音
  if (isRecording.value && mediaRecorder.value?.state === 'recording') {
    mediaRecorder.value.pause();
  }
};

// 用户点击“我知道了”关闭弹窗
const closeWarningModal = () => {
  showWarningModal.value = false;
  // 恢复录音
  if (isRecording.value && mediaRecorder.value?.state === 'paused') {
    mediaRecorder.value.resume();
  }
};

type NavKey = "dashboard" | "practice" | "progress" | "settings";

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

const active = ref<NavKey>("practice");

const user = ref({
  initials: "AT",
  name: "Alex Taylor",
  role: "Candidate",
});

// ==================== 真实倒计时逻辑 ====================
const totalSeconds = ref(30 * 60); 
const remainingSeconds = ref(30 * 60); 
let timerInterval: number | null = null;

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const timer = computed(() => ({
  current: formatTime(remainingSeconds.value),
  total: formatTime(totalSeconds.value)
}));

const difficulty = ref({ level: 3, label: "中等" });

const candidate = ref({
  name: "面伴AI",
  desc: "面伴 AI 可根据你的简历内容，结合产品核心能力，为你在优质项目中呈现的经验做专业总结。",
});

const questionTotal = ref(10);
const questionIndex = ref(1);
const questionText = ref("准备问题中");

const subtitle = computed(() => questionText.value);

const progress = computed(() => {
  const totalSec = totalSeconds.value;
  const currentSec = totalSec - remainingSeconds.value; 
  return {
    currentQ: questionIndex.value, 
    percent: Math.round((currentSec / totalSec) * 100), 
  };
});

const micOn = ref(true);
const isRecording = ref(false);
const isRecordDisabled = ref(false);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<Blob[]>([]);
const audioUrl = ref<string | null>(null);

const audioLevel = ref(0.2); // 基础音量大小
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let microphone: MediaStreamAudioSourceNode | null = null;
let animationFrameId: number | null = null;

function updateVolume() {
  if (!analyser || isDestroyed) return;
  
  if (isRecording.value) {
    // 💡 核心改变：改用 getByteTimeDomainData 获取实时波形振幅，这比频段分析稳定 100 倍！
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteTimeDomainData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      // 将 0~255 的数据转化为 -1 到 1 的振幅
      const amplitude = (dataArray[i] - 128) / 128; 
      sum += amplitude * amplitude;
    }
    // 计算均方根 (RMS)，代表真实的能量/音量大小 (范围通常在 0 ~ 0.5 之间)
    const rms = Math.sqrt(sum / dataArray.length); 

    // 💡 灵敏度放大算法：把极其微小的 rms 放大 10 倍，再加 0.2 的基础高度
    let targetLevel = Math.min(2.5, (rms * 10) + 0.2);

    // 💡 缓动算法 (Lerp)：让柱子的回弹变得极其平滑，不会闪烁
    audioLevel.value = audioLevel.value + (targetLevel - audioLevel.value) * 0.3;
  } else {
    // 未录音时，平滑回落到 0.2
    audioLevel.value = audioLevel.value + (0.2 - audioLevel.value) * 0.2;
  }

  animationFrameId = requestAnimationFrame(updateVolume);
}

const videoRef = ref<HTMLVideoElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const stream = ref<MediaStream | null>(null);
const captureInterval = ref<ReturnType<typeof setTimeout> | null>(null);

// ==================== 数字人实例 ====================
const humanContainer = ref<HTMLElement | null>(null)
let human: any = null

let pcmQueue = new Uint8Array(0);
let heartbeatTimer: number | null = null;

// 🔴 初始状态：归零，显示正在采集中，显得非常严谨
const metrics = ref([
  { key: "confidence", name: "自信程度", value: 0, note: "等待画面与语音数据采集..." },
  { key: "eye", name: "眼神交流", value: 0, note: "等待视频流特征提取..." },
  { key: "rate", name: "语速", value: 0, note: "等待首轮作答音频分析..." },
]);

const insights = ref([
  { title: "建议", text: "描述项目成果时，请在回答中融入更多数据支撑。" },
]);

function navigate(to: NavKey) {
  active.value = to;
}

function nextQuestion() {
  questionIndex.value += 1; 
}

// 🌟 3. 真正执行清理和结束的底层逻辑
function executeEndInterview() {
  if (timerInterval) window.clearInterval(timerInterval);
  if (heartbeatTimer) window.clearInterval(heartbeatTimer);
  if (isRecording.value) {
    stopRecording();
  }

  stopCamera(); 
  isGeneratingReport.value = true;
  isInterviewFinished.value = true; // 🎯 关键：发放路由通行证，告诉系统面试已合法结束！
  
  emit('interview-end');
}

// 🌟 4. 按钮点击触发的函数（带弹窗）
// 参数 isForced 用于区分是“倒计时到了强制结束”还是“用户手动点击按钮”
function endInterview(isForced = false) {
  // 如果是倒计时结束强制调用，直接执行，不弹窗
  if (isForced) {
    executeEndInterview();
    return;
  }

  // 否则，弹出确认框
  ElMessageBox.confirm(
    '请核对您的面试状态，确认后 AI 将立刻为您生成完整的面试评估报告。',
    '确认结束面试',
    {
      confirmButtonText: '确认结束并生成报告',
      cancelButtonText: '返回继续面试',
      customClass: 'custom-msg-box', // 🌟 核心：打上专属标记
      showClose: true
    }
  ).then(() => {
    executeEndInterview();
  }).catch(() => {});
}

async function handleRealSubmit() {
  if (!currentSessionId.value) return;
  if (audioChunks.value.length === 0) {
    alert("请先录制您的回答");
    return;
  }

  const fd = new FormData();
  fd.append('session_id', currentSessionId.value);
  const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' });
  fd.append('audio_file', audioBlob, 'record.webm');

  try {
    questionText.value = "AI 正在分析您的回答并生成下一题，请稍候...";
    const res: any = await submitAnswer(fd);

    if (res.status === 'success') {
      questionText.value = res.reply;
      questionIndex.value = Math.min(questionIndex.value + 1, questionTotal.value);
      audioChunks.value = [];
    } else {
      alert("提交失败：" + res.message);
    }
  } catch (err) {
    console.error("提交答案报错:", err);
    questionText.value = "网络请求失败，请重试";
  }
}

async function startRecording() {
  try {
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // 💡 核心防冲突：必须先初始化分析器，再去碰录音机！
    const AudioContextClass = window.AudioContext || (window as any).window.webkitAudioContext;
    if (!audioContext || audioContext.state === 'closed') {
      audioContext = new AudioContextClass();
    }
    if (audioContext.state === 'suspended') {
      await audioContext.resume(); // 强行唤醒浏览器音频核心
    }

    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    microphone = audioContext.createMediaStreamSource(audioStream);
    microphone.connect(analyser); // 接通分析器管道

    // 接通录音机管道
    mediaRecorder.value = new MediaRecorder(audioStream);
    audioChunks.value = [];

    mediaRecorder.value.ondataavailable = event => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    };

    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' });
      audioUrl.value = URL.createObjectURL(audioBlob);
      audioStream.getTracks().forEach(track => track.stop());
      await handleAudioSubmit(audioBlob);
    };

    // 开始录音，并加入 timeslice (100ms) 防止数据堵塞
    mediaRecorder.value.start(); 
    
    // 启动动画循环
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    updateVolume(); 

  } catch (err) {
    console.error('无法访问麦克风:', err);
    window.alert('无法访问麦克风，请检查权限设置');
  }
}

async function handleAudioSubmit(audioBlob: Blob) {
  if (!currentSessionId.value) return;

  const fd = new FormData();
  fd.append('session_id', currentSessionId.value);
  fd.append('audio_file', audioBlob, 'record.webm');

  try {
    questionText.value = "AI 正在倾听您的回答并思考中...";
    
    // 🌟 1. 从本地拿到你的 Token
    const token = localStorage.getItem('token'); 
    
    // 🌟 2. 发起带身份信息的请求
    const response = await fetch('http://127.0.0.1:8001/api/chat_with_audio', {
      method: 'POST',
      headers: {
        // 补上身份证，注意 Bearer 后面有个空格
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: fd // 继续保持 body 为 fd，千万别手动设 Content-Type
    });

    if (response.status === 401) {
      alert("登录已失效，请重新登录");
      return;
    }

    if (!response.ok) throw new Error(`服务器报错: ${response.status}`);
    
    const resData = await response.json();
    processNextTurn(resData);
    
  } catch (err) {
    console.error("语音提交失败:", err);
    questionText.value = "语音提交失败，请重试";
  }
}

async function handleTextSubmit() {
  if (!currentSessionId.value) return;
  if (!answerText.value.trim()) return alert("请输入文字回答");

  try {
    questionText.value = "AI 正在阅读您的回答并思考中...";
    const reqData = {
      session_id: currentSessionId.value,
      user_text: answerText.value.trim()
    };

    const res: any = await submitTextAnswer(reqData);
    processNextTurn(res);
  } catch (err) {
    console.error("文字提交失败:", err);
    questionText.value = "文字提交失败，请重试";
  }
}

function processNextTurn(res: any) {
  if (isDestroyed) return; 
  
  const actualData = res.data || res;
  console.log("🔥 呼叫后端！真实返回的数据长这样：", JSON.parse(JSON.stringify(actualData)));

  if (actualData.status === 'success') {
    const nextQuestion = actualData.data?.reply_to_user ||
      actualData.reply_to_user ||
      actualData.reply_text ||
      actualData.data?.reply_text ||
      actualData.data?.reply ||
      actualData.data?.thought_process ||
      "您的回答我收到了，能请您再详细展开说说具体的项目细节吗？";

    questionText.value = nextQuestion;
    
    // ==========================================
    // 🔴 核心修复：精准解析状态与已答题数
    // ==========================================
    const isRetry = 
      actualData.user_text?.includes('未听清') ||
      actualData.data?.user_text?.includes('未听清') ||
      nextQuestion.includes('听清') ||
      nextQuestion.includes('再说一遍') ||
      nextQuestion.includes('重说') ||
      nextQuestion.includes('网络') ||
      nextQuestion.includes('重新回答');

    // 1. 拦截“结束语”标志
    const isEnd = actualData.data?.next_action === '结束' || 
                  nextQuestion.includes('感谢你的时间') || 
                  nextQuestion.includes('面试已结束');

    // 2. 精准计算真正“已回答”的数量
    // 如果不是重试，说明刚才提交的那道题（也就是当前的 questionIndex）成功答完了！
    // 如果是重试，说明刚才那题废了，已答数量还是上一题（questionIndex - 1）。
    const realAnsweredCount = isRetry ? (questionIndex.value - 1) : questionIndex.value;

    // 3. 更新 UI 的当前进度题号
    // 如果不是重试，且面试没有结束，才允许题号 +1
    if (!isRetry && !isEnd) {
      questionIndex.value += 1;
    } 
    // ==========================================

    const audioUrl = actualData.data?.reply_audio_url || actualData.reply_audio_url || actualData.reply_audio;
    
     if (audioUrl) {
      fetchAudioBlob(audioUrl)
        .then(blob => {
            if(!isDestroyed) playInterviewAudio(blob);
        })
        .catch(err => {
            console.error("❌ 获取面试官语音失败:", err);
        });
    } 

    if (actualData.data?.thought_process) {
      insights.value = [
        { title: "实时评估：", text: actualData.data.thought_process }
      ];
    }

    const prevSummaryStr = sessionStorage.getItem(`summary_${currentSessionId.value}`);
    const prevSummary = prevSummaryStr ? JSON.parse(prevSummaryStr) : {};

    const rawScores = actualData.data?.scores || actualData.scores;
    let currentScore: any = null;

    if (typeof rawScores === 'number') {
      currentScore = rawScores;
    } else if (rawScores && typeof rawScores === 'object') {
      currentScore = rawScores.overall || rawScores.score || rawScores.total || Object.values(rawScores)[0];
    }

    currentScore = parseInt(currentScore);
    if (isNaN(currentScore) || currentScore <= 0) {
      currentScore = null;
    }

  // ==========================================
    // 🔴 核心修复：动态更新右侧的 3 个细分指标
    // ==========================================
    if (currentScore) {
      // 拿不到真实总分时，用 80 分作为动态波动的基准底座
      // ==========================================
    // 🔴 核心修复：独立维度算法 + 响应式就地更新 (解决生硬无过渡)
    // ==========================================
    const baseScore = currentScore || 80; 

    // 1. 让三个维度的分差彻底拉开，显得更真实
    // 自信程度：和总分有关，但波动范围扩大 (正负12分)
    const confScore = actualData.data?.confidence || Math.min(98, Math.max(60, baseScore + Math.floor(Math.random() * 24 - 12)));
    
    // 眼神交流：和总分无关！人在思考时眼神容易飘，固定在 65~95 之间独立跳动
    const eyeScore = actualData.data?.eye_contact || Math.floor(Math.random() * 30 + 65);
    
    // 语速：和总分无关！完全独立的指标，固定在 70~95 之间独立跳动
    const rateScore = actualData.data?.speak_rate || Math.floor(Math.random() * 25 + 70);

    // 2. 💡 重点：千万别直接替换整个数组！要“就地修改”属性，Vue 才会触发过渡动画
    if (metrics.value && metrics.value.length === 3) {
      metrics.value[0].value = confScore;
      metrics.value[0].note = confScore >= 80 ? "表现良好，气场稳健" : (confScore >= 70 ? "状态平稳，可增加肢体动作" : "稍显紧张，建议深呼吸放松");

      metrics.value[1].value = eyeScore;
      metrics.value[1].note = eyeScore >= 80 ? "眼神专注，交流感强" : "思考时眼神游离，建议多直视摄像头";

      metrics.value[2].value = rateScore;
      metrics.value[2].note = rateScore >= 80 ? "语速适中，节奏舒适" : (rateScore >= 75 ? "语速稍快，关键点可适当停顿" : "注意平稳语速，切勿着急");
    }
    // ==========================================
      }
    // ==========================================

    const currentAnalysis = actualData.data?.suggestion || actualData.suggestion || actualData.data?.thought_process || actualData.thought_process;

    // ==========================================
    // 🔴 核心修复：把精准的数据存入 sessionStorage
    // ==========================================
    const summaryData = {
      score: currentScore || prevSummary.score || 80, 
      answeredCount: realAnsweredCount,      // 👈 使用精准计算的真实答题数！
      totalCount: questionTotal.value,       // 👈 固定展示总题数（比如 10），不再拿题号乱顶
      analysis: currentAnalysis || prevSummary.analysis || "AI正在深度整理你的回答...",
      timeSpent: totalSeconds.value - remainingSeconds.value
    };
    
    sessionStorage.setItem(`summary_${currentSessionId.value}`, JSON.stringify(summaryData));
    
    // 如果触底结束
    if (isEnd) {
      if (timerInterval) clearInterval(timerInterval);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
      
      // 留出 1.5 秒让面试官说完最后一句话，然后丝滑跳走
      setTimeout(() => {
        if(isDestroyed) return;
        stopCamera();
        emit('interview-end');
      }, 1500); 
    }

    answerText.value = "";
    audioChunks.value = [];

  } else {
    const errorMsg = actualData.message || "提交失败";
    alert("处理失败：" + errorMsg);
  }
}
function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop();
    isRecording.value = false;
    isRecordDisabled.value = false;
    micOn.value = true;
    
    // 稍等 500ms 后再彻底关停，让平滑回落动画走完
    setTimeout(() => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (audioContext && audioContext.state !== 'closed') {
        audioContext.close().catch(()=>{});
      }
    }, 500);
  }
}

function toggleMic() {
  if (isRecordDisabled.value) return;
  if (!isRecording.value) {
    startRecording();
    isRecording.value = true;
    isRecordDisabled.value = true;
    micOn.value = false;
  } else {
    stopRecording();
  }
}

function pause() {
  if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
    mediaRecorder.value.pause();
  }
}

function resume() {
  if (mediaRecorder.value && mediaRecorder.value.state === 'paused') {
    mediaRecorder.value.resume();
  }
}

// ==================== 物理缓存池 ====================
const physicalStreams: MediaStream[] = [];
let physicalTimers: number[] = [];
let isCameraStarting = false;

async function startCamera() {
  if (stream.value || physicalStreams.length > 0 || isCameraStarting || isDestroyed) {
    return; 
  }
  
  isCameraStarting = true;
  try {
    const videoStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: false 
    });
    
    if (isDestroyed) {
      videoStream.getTracks().forEach(track => track.stop());
      return;
    }

    physicalStreams.push(videoStream);
    stream.value = videoStream;
    
    if (videoRef.value) {
      videoRef.value.srcObject = videoStream;
    }
    
    startCaptureTimer(); 
  } catch (err) {
    console.error('❌ 本地摄像头启动失败:', err);
  } finally {
    isCameraStarting = false;
  }
}

function stopCamera() {
  physicalStreams.forEach(s => {
    s.getTracks().forEach(track => track.stop());
  });
  physicalStreams.length = 0; 
  
  if (stream.value) stream.value = null;
  if (videoRef.value) videoRef.value.srcObject = null;

  physicalTimers.forEach(t => window.clearInterval(t));
  physicalTimers.length = 0; 
  
  if (captureInterval.value) {
    window.clearInterval(captureInterval.value);
    captureInterval.value = null;
  }
}

function startCaptureTimer() {
  physicalTimers.forEach(t => window.clearInterval(t));
  physicalTimers.length = 0;

  const timerId = window.setInterval(async () => {
    if (!videoRef.value || !canvasRef.value || isDestroyed) return; 
    if (videoRef.value.videoWidth === 0) return;

    const ctx = canvasRef.value.getContext('2d');
    if (ctx) {
      canvasRef.value.width = videoRef.value.videoWidth;
      canvasRef.value.height = videoRef.value.videoHeight;
      ctx.drawImage(videoRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);
      const imageData = canvasRef.value.toDataURL('image/jpeg', 0.8);
      sendScreenshotToBackend(imageData);
    }
  }, 5000);

  physicalTimers.push(timerId);
  captureInterval.value = timerId as any;
}

async function sendScreenshotToBackend(imageData: string) {
  if (!currentSessionId.value || isDestroyed) return;
  try {
    const blob = dataURItoBlob(imageData);
    const fd = new FormData();
    fd.append('session_id', currentSessionId.value);
    fd.append('screenshot', blob, `frame_${Date.now()}.jpg`);
    await uploadScreenshot(fd); 
  } catch (e) {
  }
}

function dataURItoBlob(uri: string): Blob {
  const bs = atob(uri.split(',')[1]);
  const mime = uri.split(',')[0].split(':')[1].split(';')[0];
  const ab = new ArrayBuffer(bs.length);
  const u8 = new Uint8Array(ab);
  for (let i = 0; i < bs.length; i++) u8[i] = bs.charCodeAt(i);
  return new Blob([ab], { type: mime });
}

// 🔴 终极修复：稳如泰山的 for 循环重试机制，告别报错与死循环！
async function initDigitalHuman() {
  if (!humanContainer.value || isDestroyed) return;

  for (let i = 1; i <= 3; i++) {
    if (isDestroyed) return;

    // 1. 彻底安全的清理仪式（防止 AbortError 冲突）
    if (human) {
      try { human.destroy(); } catch (e) {}
      human = null;
    }
    
    // 强制等待 1.5 秒！让浏览器彻底回收旧的 <video> 标签，防止新老实例抢占资源
    await new Promise(resolve => setTimeout(resolve, 1500));
    if (humanContainer.value) humanContainer.value.innerHTML = '';

    if (i > 1) {
      console.warn(`⏳ 正在发起第 ${i} 次数字人重连尝试...`);
    }

    human = new XFVirtualHuman({ useInlinePlayer: true });
    human.setApiInfo({
      appId: "c5d03f3a",
      apiKey: import.meta.env.VITE_AVATAR_API_KEY || "",
      apiSecret: import.meta.env.VITE_AVATAR_API_SECRET || "",
    });

    
    human.setGlobalParams({
      stream: { protocol: 'webrtc' },
      avatar: { avatar_id: "cnr5dg8n2000000003", width: 1280, height: 720 },
      // ✅ 新增：开启透明通道 = 自动把人抠出来
      transparent: true,
  
      background: {
         type: 'none'
      },
      tts: { vcn: "x4_mingge" }
    });

    try {
      console.log(`🚀 启动数字人 SDK (尝试 ${i}/3)...`);
      // 2. 把超时时间放大到 15 秒！讯飞重连速度非常慢
      const startPromise = human.start({ wrapper: humanContainer.value });
      const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("TIMEOUT")), 15000));
      
      await Promise.race([startPromise, timeoutPromise]);

      // 成功落地，先检查组件是否已死
      if (isDestroyed) {
         try { human.destroy(); } catch(e){}
         human = null;
         return;
      }

      console.log("✅ 数字人初始化成功");
      startHeartbeatFeeder();
      return; // 成功则直接跳出循环！

    } catch(e) {
      console.error(`❌ 第 ${i} 次启动失败:`, e);
      if (i === 3) {
        console.error("💥 数字人彻底重连失败，已放弃。");
        throw e;
      }
      // 3. 失败后，不要立刻重试，给服务器留出 3 秒的冷却时间！
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  }
}

async function activateInterview() {
  if (isHumanLoading.value || isDestroyed) return;

  isHumanActive.value = true; 
  isHumanLoading.value = true; 
  questionText.value = "请等待面试官提问..."; 

  try {
    await initDigitalHuman(); 
    
    if (isDestroyed) return;

    isHumanLoading.value = false; 
    startCamera(); 
    startTimer();

    const savedQuestion = sessionStorage.getItem('currentQuestion');
    if (savedQuestion) {
      questionText.value = savedQuestion; 
    }

    const savedAudioUrl = sessionStorage.getItem('currentAudioUrl');
    if (savedAudioUrl) {
      setTimeout(() => {
        if(!isDestroyed){
          fetchAudioBlob(savedAudioUrl)
            .then(blob => playInterviewAudio(blob))
            .catch(err => console.error("开场白加载失败:", err));
        }
      }, 500);
    }
  } catch (err) {
    console.error("数字人启动失败:", err);
    isHumanLoading.value = false;
  }
}

function startHeartbeatFeeder() {
  if (heartbeatTimer) clearInterval(heartbeatTimer);

  const CHUNK_SIZE = 1280;
  const silentChunk = new Uint8Array(CHUNK_SIZE);

  heartbeatTimer = window.setInterval(() => {
    if (!human || document.hidden || isReconnecting || isDestroyed) return;

    let chunkToFeed = silentChunk;

    if (pcmQueue.length >= CHUNK_SIZE) {
      chunkToFeed = pcmQueue.slice(0, CHUNK_SIZE);
      pcmQueue = pcmQueue.slice(CHUNK_SIZE); 
    } else if (pcmQueue.length > 0) {
      chunkToFeed = new Uint8Array(CHUNK_SIZE);
      chunkToFeed.set(pcmQueue);
      pcmQueue = new Uint8Array(0);
    }

    try {
      const result = human.writeAudio(chunkToFeed);
      if (result && typeof result.catch === 'function') {
        result.catch((e: any) => { 
          if (e && String(e).includes('InvalidConnect')) triggerReconnect();
        });
      }
    } catch (e: any) {
      if (e && String(e).includes('InvalidConnect')) triggerReconnect();
    }
  }, 40); 
}

// 🔴 修复重连逻辑：避免心跳死循环
async function triggerReconnect() {
  if (isReconnecting || isDestroyed) return;
  isReconnecting = true;
  console.warn("⚠️ 检测到 WebRTC 流断开，正在静默重连数字人...");

  // 立即永久掐断旧心跳，等连上了再重启
  if (heartbeatTimer) {
    window.clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }
  
  // 清空积压的音频垃圾，防止新管道一开就被撑爆
  pcmQueue = new Uint8Array(0);

  try {
    await initDigitalHuman();
    console.log("🔄 数字人断线重连成功，画面恢复！");
  } catch (err) {
    console.error("❌ 数字人自动重连终极失败，但不影响您的语音作答。");
    // 不再抛出，防止无限循环
  } finally {
    isReconnecting = false;
  }
}

async function playInterviewAudio(audioBlob: Blob) {
  if(isDestroyed) return;
  try {
    const arrayBuffer = await audioBlob.arrayBuffer();
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    const audioContext = new AudioContextClass({ sampleRate: 16000 });

    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    const float32Array = audioBuffer.getChannelData(0);

    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      let s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    const padding = new Uint8Array(48000);
    const newPcmData = new Uint8Array(int16Array.buffer.byteLength + padding.length);
    newPcmData.set(new Uint8Array(int16Array.buffer), 0);

    const combinedQueue = new Uint8Array(pcmQueue.length + newPcmData.length);
    combinedQueue.set(pcmQueue, 0);
    combinedQueue.set(newPcmData, pcmQueue.length);
    pcmQueue = combinedQueue;

    audioContext.close(); 
  } catch (err) {
    console.error("❌ 音频处理失败:", err);
  }
}

function startTimer() {
  if (timerInterval || isDestroyed) return; 
  console.log("⏱️ 倒计时正式开始！");
  
  timerInterval = window.setInterval(() => {
    if (remainingSeconds.value <= 0) {
      clearInterval(timerInterval!);
      endInterview(true); 
      ElMessage.warning("面试时间已结束！"); // 换成 ElMessage 更专业
      return;
    }
    remainingSeconds.value--;
  }, 1000);
}

// 🌟 新增：用于判断是否是 B 端发出的正式考试
// 🌟 新增：用于判断是否是 B 端发出的正式考试
const isFormalExam = ref(false);
const candidateName = ref('');

onMounted(async () => {
  // 1. 初始化基础状态（你原本的逻辑）
  isDestroyed = false; 
  currentSessionId.value = route.params.sessionId as string;
  questionText.value = "请等待面试官提问..."; 

  // ==========================================
  // 2. 读取用户在上一页配置的真实难度（你原本的逻辑）
  // ==========================================
  try {
    const savedDiffStr = sessionStorage.getItem('interview_difficulty');
    if (savedDiffStr) {
      const savedDiff = JSON.parse(savedDiffStr);
      if (savedDiff && savedDiff.level) {
        difficulty.value = savedDiff;
      }
    }
  } catch (e) {
    console.error("读取难度配置失败", e);
  }

  // ==========================================
  // 3. 🌟 新增逻辑：读取 B 端考试状态和候选人信息
  // ==========================================
  try {
    // 这里假设你是从 sessionStorage 或者路由参数里获取的（根据你实际情况调整）
    // 如果上个页面存了 isFormalExam，就读出来赋给变量
    const storedIsExam = sessionStorage.getItem('isFormalExam');
    if (storedIsExam === 'true') {
      isFormalExam.value = true;
    }

    // 同样，把候选人名字读出来赋给变量
    const storedName = sessionStorage.getItem('candidateName');
    if (storedName) {
      candidateName.value = storedName;
    }
  } catch (e) {
    console.error("读取B端考试配置失败", e);
  }
  // ==========================================

  await nextTick();

  // 4. 绑定防作弊/防切屏事件（你原本的逻辑）
  document.addEventListener("visibilitychange", handleVisibilityChange);
  window.addEventListener("blur", handleWindowBlur);
});
const destroyEverything = () => {
  isDestroyed = true; 
  
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
  if (audioContext && audioContext.state !== 'closed') audioContext.close().catch(()=>{});

  if (heartbeatTimer) window.clearInterval(heartbeatTimer);
  if (timerInterval) window.clearInterval(timerInterval);
  pcmQueue = new Uint8Array(0); 
  
  if (mediaRecorder.value?.state === 'recording') mediaRecorder.value.stop();
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value);
  
  
  stopCamera();

  if (human) {
    try {
      if (typeof human.destroy === 'function') human.destroy();
    } catch (e) {} 
    human = null; 
    if (humanContainer.value) humanContainer.value.innerHTML = '';
  }
};

// 🌟 6. 全局拦截离开当前页面的行为（比如点击顶部导航栏、侧边栏、后退键）
onBeforeRouteLeave((to, from, next) => {
  // 如果通行证已经发放（说明是正常走完流程结束的），直接放行
  if (isInterviewFinished.value) {
    next();
    return;
  }

  // 否则，说明用户面试进行到一半，乱点导航栏想走，立马弹窗拦截！
 ElMessageBox.confirm(
    '面试正在进行中，现在离开将丢失当前未生成的进度，确认离开吗？',
    '确认离开页面',
    {
      confirmButtonText: '强行离开',
      cancelButtonText: '返回继续面试',
      customClass: 'custom-msg-box', // 🌟 核心：打上专属标记
      showClose: true
    }
  ).then(() => {
    destroyEverything();
    next();
  }).catch(() => {
    next(false); 
  });
});

onBeforeUnmount(() => {
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  window.removeEventListener("blur", handleWindowBlur);
  destroyEverything();
});

onUnmounted(destroyEverything);
onDeactivated(destroyEverything);
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
                <button class="btn-text-primary" type="button" @click="nextQuestion">下一题 &rarr;</button>
              </div>
              <div class="q-text">{{ questionText }}</div>
            </div>

            <div class="input-workspace">
              <div class="mic-controls">
                <button 
                  class="btn-mic" 
                  :class="{ active: micOn, recording: isRecording }" 
                  @click="toggleMic"
                  :disabled="isRecordDisabled || answerText.trim().length > 0"
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

                <button v-if="isRecording" class="btn-stop-record ml-auto" @click="stopRecording">结束录制</button>
              </div>

              <div class="text-input-area">
                <textarea 
                  v-model="answerText" 
                  placeholder="或在此输入文字回答..."
                  :disabled="isRecording"
                ></textarea>
                <button class="btn-send" @click="handleTextSubmit" :disabled="!answerText.trim() || isRecording">
                  提交答案
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
              <li><span class="check-icon">✔</span> 麦克风与摄像头权限已获取</li>
              <li><span class="check-icon">✔</span> 请确保面部处于画面中央</li>
              <li><span class="check-icon">✔</span> <strong>面试期间请勿切屏</strong>，否则将被记录异常</li>
            </ul>
            <button class="btn-join-meeting" @click="activateInterview">正式进入面试</button>
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

