<template>
  <div class="interview-container">
    <!-- 步骤1：初始化界面 -->
    <div v-if="step === 1" class="init-step">
      <h3>AI 多模态面试</h3>
      <p>请点击按钮申请权限并开始面试</p>
      <button @click="initInterview" :disabled="isLoading">
        {{ isLoading ? '申请权限中...' : '开始面试' }}
      </button>
    </div>

    <!-- 步骤2：核心面试界面 -->
    <div v-if="step === 2" class="interview-step">
      <div class="video-container">
        <audio 
          v-if="aiAudioUrl" 
          class="ai-audio" 
          :src="aiAudioUrl" 
          controls 
          autoplay
          @canplay="isAudioPlaying = true"
          @ended="onAudioEnded"
          @error="onAudioError"
        />

        <!-- 候选人摄像头画面 -->
        <video class="self-video" ref="selfVideoRef" autoplay playsinline></video>
        <!-- 截图预览 -->
        <img
          v-if="previewUrl"
          class="snapshot-preview"
          :src="previewUrl"
          alt="最近一次截图"
        />
      </div>

      <div class="control-panel">
        <p class="question">{{ currentQuestion || '请等待面试问题加载...' }}</p>
        <button @click="startRecording" v-if="!isRecording && !isAudioPlaying && !isSubmitting">开始回答</button>
        <button @click="stopRecording" v-else style="background: #f56c6c;" :disabled="isSubmitting">
          {{ isSubmitting ? '提交中...' : `回答完毕 (已录制${Math.floor(recordTime/1000)}s)` }}
        </button>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </div>
    </div>

    <!-- 步骤3：报告生成中 -->
    <div v-if="step === 3" class="loading-step">
      <p>正在提交回答并生成面试报告...</p>
      <div class="spinner"></div>
    </div>

    <!-- 步骤4：报告展示 -->
    <div v-if="step === 4" class="report-step">
      <h3>面试评估报告</h3>
      <div class="report-content" v-html="reportHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { createInterview, submitAnswer, getInterviewReport } from '@/api/interview'

// ---------- 状态管理 ----------
const step = ref(1)
const isLoading = ref(false)
const isSubmitting = ref(false)
const sessionId = ref('')
const currentQuestion = ref('')
const reportHtml = ref('')
const errorMsg = ref('')

// ---------- 新增：AI 音频状态 ----------
const aiAudioUrl = ref('')
const isAudioPlaying = ref(false)

// ---------- DOM 引用 ----------
const selfVideoRef = ref(null)
const mediaRecorder = ref(null)
const audioBlob = ref(null)
const imageBlobs = ref([])
const previewUrl = ref('')

// ---------- 录制状态 ----------
const isRecording = ref(false)
const recordTime = ref(0)
const timer = ref(null)
const captureInterval = 5000

// ---------- 第一步：初始化面试 ----------
const initInterview = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
    if (selfVideoRef.value) {
      selfVideoRef.value.srcObject = stream
      await selfVideoRef.value.play().catch(() => {})
    }

    const interviewConfig = {
      position: 'backend',
      experience: 'middle',
      type: 'technical',
      difficulty: 3
    }

    const result = await createInterview(interviewConfig)
    console.log('【完整后端返回】', JSON.stringify(result, null, 2))

    sessionId.value = result.session_id || result.sessionId
    currentQuestion.value = result.reply_text || result.reply || result.question || '请开始回答第一个问题'
    
    let audioPath = result.reply_audio_url || result.reply_audio || result.audio_url || ''
    console.log('【音频相对路径】', audioPath)
    
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.31.242:8001'
    aiAudioUrl.value = baseURL + (audioPath.startsWith('/') ? audioPath : '/' + audioPath)
    console.log('【最终AI音频URL】', aiAudioUrl.value)

    step.value = 2
  } catch (error) {
    console.error('【初始化面试失败】', error)
    errorMsg.value = '权限申请失败或接口异常：' + (error?.message || error)
  } finally {
    isLoading.value = false
  }
}

// ---------- 第二步：核心 - 音视频采集 ----------
const startRecording = async () => {
  console.log('开始录音函数被调用')
  errorMsg.value = ''
  // 重置之前的 Blob 资源，避免内存泄漏
  if (audioBlob.value) {
    URL.revokeObjectURL(audioBlob.value)
    audioBlob.value = null
  }
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  imageBlobs.value = []

  try {
    // 只录音频流
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    // 视频预览复用 init 中的 stream（假设 selfVideoRef 已赋值）
    if (selfVideoRef.value && !selfVideoRef.value.srcObject) {
      const videoStream = await navigator.mediaDevices.getUserMedia({ video: true })
      selfVideoRef.value.srcObject = videoStream
      await selfVideoRef.value.play().catch(() => {})
    }

    // 确定 mimeType
    let mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
    mediaRecorder.value = new MediaRecorder(audioStream, { mimeType })

    const audioChunks = []
    mediaRecorder.value.ondataavailable = (e) => audioChunks.push(e.data)
    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(audioChunks, { type: mimeType })
      // 延迟停止轨道
      setTimeout(() => {
        audioStream.getTracks().forEach(track => track.stop())
      }, 500)
    }

    mediaRecorder.value.start(1000)
    console.log('录音已启动，状态:', mediaRecorder.value.state)
    isRecording.value = true
    recordTime.value = 0
    startScreenshotTimer(selfVideoRef.value.srcObject)  // 使用视频流截图

    // 启动录制计时
    const timeTimer = setInterval(() => {
      if (isRecording.value) {
        recordTime.value += 1000
      } else {
        clearInterval(timeTimer)
      }
    }, 1000)
  } catch (e) {
    console.error('启动录音失败:', e)
    errorMsg.value = '当前浏览器不支持录音格式或未获取到麦克风权限'
  }
}

const startScreenshotTimer = (stream) => {
  const video = document.createElement('video')
  video.srcObject = stream
  video.play().catch(() => {})
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  canvas.width = 320
  canvas.height = 240
  captureFrame(canvas, ctx, video)
  timer.value = setInterval(() => captureFrame(canvas, ctx, video), captureInterval)
}

const captureFrame = (canvas, ctx, video) => {
  try {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(blob => {
      if (blob) {
        imageBlobs.value.push(blob)
        if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
        previewUrl.value = URL.createObjectURL(blob)
      }
    }, 'image/jpeg', 0.6)
  } catch (e) {
    console.warn('截图失败:', e)
  }
}

const stopRecording = async () => {
  if (!mediaRecorder.value || isSubmitting.value) return
  
  isSubmitting.value = true
  clearInterval(timer.value)
  isRecording.value = false
  errorMsg.value = ''

  try {
    // 停止录制并等待 Blob
    mediaRecorder.value.stop()
    await new Promise(resolve => {
      const checkBlob = () => {
        if (audioBlob.value) resolve()
        else setTimeout(checkBlob, 100)
      }
      checkBlob()
    })

    console.log('【录制停止，Blob 已生成】', audioBlob.value)

    const formData = new FormData()
    formData.append('session_id', sessionId.value)
    
    if (audioBlob.value) {
      const ext = mediaRecorder.value.mimeType.includes('webm') ? '.webm' : '.mp4'
      formData.append('audio_file', audioBlob.value, `audio_${Date.now()}${ext}`)
    }
    
    imageBlobs.value.forEach((blob, index) => {
      formData.append('image_files', blob, `snap_${index + 1}_${Date.now()}.jpg`)
    })

    console.log('【提交的FormData】', [...formData.entries()])

    const response = await submitAnswer(formData)
    console.log('【提交回答-后端返回】', response)

    if (response.next_action === '结束') {
      step.value = 3
      await generateReport()
    } else {
      currentQuestion.value = response.reply_text || response.reply_question || response.reply || '请继续回答下一个问题'
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.31.242:8001'
      let audioPath = response.reply_audio_url || response.reply_audio || response.audio_url || ''
      aiAudioUrl.value = baseURL + (audioPath.startsWith('/') ? audioPath : '/' + audioPath)
      step.value = 2
    }
  } catch (error) {
    console.error('【提交回答失败】', error)
    errorMsg.value = `提交失败：${error.message || '网络超时或服务端异常'}`
    step.value = 2
  } finally {
    isSubmitting.value = false
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  }
}

// ---------- 第三步：生成终极报告 ----------
const generateReport = async () => {
  try {
    const reportData = await getInterviewReport(sessionId.value)
    reportHtml.value = reportData.report_html || reportData.content
    step.value = 4
  } catch (error) {
    console.error('生成报告失败:', error)
    errorMsg.value = '生成报告失败，请重试'
    step.value = 2
    isSubmitting.value = false
  }
}

// ---------- 新增：AI 音频播放结束回调 ----------
const onAudioEnded = () => {
  isAudioPlaying.value = false
  console.log('AI 语音播放完毕，可以开始回答')
}

// 新增：音频加载错误处理
const onAudioError = (e) => {
  console.error('AI音频加载失败', e)
  errorMsg.value = 'AI音频加载失败，请检查网络或后端音频路径'
}

// ---------- 组件卸载：清理资源 ----------
onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  if (audioBlob.value) URL.revokeObjectURL(audioBlob.value)
  if (selfVideoRef.value && selfVideoRef.value.srcObject) {
    selfVideoRef.value.srcObject.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.ai-audio {
  width: 100%;
  margin: 10px 0;
}
.interview-container {
  max-width: 1000px;
  margin: 50px auto;
  font-family: Arial, sans-serif;
}

.init-step {
  text-align: center;
  padding: 50px;
}

button {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.interview-step {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-container {
  position: relative;
  width: 100%;
  height: 450px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.ai-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.self-video {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 200px;
  height: 150px;
  border-radius: 4px;
  border: 2px solid #409eff;
  background: #333;
}

.snapshot-preview {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 160px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  border: 2px solid #67c23a;
  background: #000;
}

.control-panel {
  text-align: center;
}

.question {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.error-msg {
  color: red;
  margin-top: 10px;
}

.loading-step {
  text-align: center;
  padding: 100px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 20px auto;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.report-content {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  line-height: 1.6;
}
</style>