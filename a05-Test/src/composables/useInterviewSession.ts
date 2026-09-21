import { computed, nextTick, onBeforeUnmount, onDeactivated, onMounted, ref } from 'vue'
import { onBeforeRouteLeave, type RouteLocationNormalizedLoaded } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import XFVirtualHuman, { SDKEvents } from '@/libs/avatar-sdk/esm/index.js'
import { fetchAudioBlob, getAvatarConnection, submitAnswer, submitTextAnswer, uploadScreenshot } from '@/api/interview'

export type InterviewPhase =
  | 'idle'
  | 'initializing'
  | 'speaking'
  | 'ready'
  | 'recording'
  | 'submitting'
  | 'finishing'
  | 'finished'
  | 'error'

type Emit = (event: 'interview-end') => void

const FRAME_BYTES = 1280 // 16 kHz * 16 bit * 40 ms
const AUDIO_FRAME = { start: 0, intermediate: 1, end: 2 } as const

export function useInterviewSession(route: RouteLocationNormalizedLoaded, emit: Emit) {
  const phase = ref<InterviewPhase>('idle')
  const phaseBeforePause = ref<InterviewPhase | null>(null)
  const currentSessionId = ref('')
  const questionText = ref('请等待面试官提问...')
  const questionIndex = ref(1)
  const questionTotal = ref(7)
  const answerText = ref('')
  const startupError = ref('')
  const networkOffline = ref(!navigator.onLine)
  const isHumanActive = ref(false)
  const isGeneratingReport = ref(false)
  const isInterviewFinished = ref(false)
  const leaveCount = ref(0)
  const showWarningModal = ref(false)
  const warningReason = ref('')
  const isFormalExam = ref(false)
  const candidateName = ref('')

  const totalSeconds = ref(30 * 60)
  const remainingSeconds = ref(30 * 60)
  let countdownTimer: number | null = null
  let deadlineAt = 0

  const difficulty = ref({ level: 3, label: '中等' })
  const candidate = ref({
    name: '面伴AI',
    desc: '面伴 AI 可根据你的简历内容，结合岗位要求，为你的回答提供专业评估。'
  })
  const metrics = ref([
    { key: 'confidence', name: '自信程度', value: 0, note: '等待语音数据采集...' },
    { key: 'eye', name: '眼神交流', value: 0, note: '等待视频数据采集...' },
    { key: 'rate', name: '表达流畅度', value: 0, note: '等待首轮回答分析...' }
  ])
  const insights = ref([{ title: '建议', text: '回答时尽量使用具体情境、行动和结果。' }])

  const isHumanLoading = computed(() => phase.value === 'initializing')
  const isSpeaking = computed(() => phase.value === 'speaking')
  const isRecording = computed(() => phase.value === 'recording')
  const isSubmitting = computed(() => phase.value === 'submitting')
  const canAnswer = computed(() => phase.value === 'ready' && !networkOffline.value)
  const micOn = computed(() => !isRecording.value)
  const subtitle = computed(() => questionText.value)

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, '0')
    const rest = (seconds % 60).toString().padStart(2, '0')
    return `${minutes}:${rest}`
  }
  const timer = computed(() => ({
    current: formatTime(remainingSeconds.value),
    total: formatTime(totalSeconds.value)
  }))
  const progress = computed(() => ({
    currentQ: questionIndex.value,
    percent: Math.min(100, Math.round(((totalSeconds.value - remainingSeconds.value) / totalSeconds.value) * 100))
  }))

  const humanContainer = ref<HTMLElement | null>(null)
  const videoRef = ref<HTMLVideoElement | null>(null)
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const cameraStream = ref<MediaStream | null>(null)
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])
  const audioLevel = ref(0.2)

  let isDestroyed = false
  let isReconnecting = false
  let isEndingRequested = false
  let human: any = null
  let heartbeatTimer: number | null = null
  let captureTimer: number | null = null
  let animationFrameId: number | null = null
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let recordingStream: MediaStream | null = null
  let screenshotUploadInFlight = false
  let isRequestingMedia = false
  let pcmQueue = new Uint8Array(0)
  let pcmFrameOpen = false
  let playbackFallbackTimer: number | null = null
  let playbackResolve: (() => void) | null = null
  let currentSubmitPromise: Promise<void> | null = null
  let stopRecordingPromise: Promise<void> | null = null
  let resolveRecordingStop: (() => void) | null = null
  const pendingAudioBlob = ref<Blob | null>(null)
  const isRecordDisabled = computed(() => (!canAnswer.value || Boolean(pendingAudioBlob.value)) && !isRecording.value)
  let pendingAudioTurnId = ''
  let pendingTextTurn: { text: string; id: string } | null = null
  let lastLeaveAt = 0

  const sessionKey = () => `interview_bootstrap_${currentSessionId.value}`
  const deadlineKey = () => `interview_deadline_${currentSessionId.value}`
  const createTurnId = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}_${Math.random().toString(16).slice(2)}`

  function persistSessionState(audioUrl = '') {
    sessionStorage.setItem(sessionKey(), JSON.stringify({
      question: questionText.value,
      audioUrl,
      questionNumber: questionIndex.value,
      totalQuestions: questionTotal.value
    }))
  }

  function restoreSessionState() {
    const raw = sessionStorage.getItem(sessionKey())
    if (!raw) {
      questionText.value = sessionStorage.getItem('currentQuestion') || questionText.value
      return sessionStorage.getItem('currentAudioUrl') || ''
    }
    try {
      const state = JSON.parse(raw)
      questionText.value = state.question || questionText.value
      questionIndex.value = Number(state.questionNumber) || 1
      questionTotal.value = Number(state.totalQuestions) || 7
      return state.audioUrl || ''
    } catch {
      sessionStorage.removeItem(sessionKey())
      return ''
    }
  }

  function withTimeout<T>(promise: Promise<T>, milliseconds: number) {
    return new Promise<T>((resolve, reject) => {
      const timerId = window.setTimeout(() => reject(new Error('数字人连接超时')), milliseconds)
      promise.then(resolve, reject).finally(() => window.clearTimeout(timerId))
    })
  }

  const delay = (milliseconds: number) => new Promise(resolve => window.setTimeout(resolve, milliseconds))

  function parseRetryAfterMilliseconds(error: any) {
    const rawValue = error?.response?.headers?.['retry-after']
    if (rawValue === undefined || rawValue === null || rawValue === '') return null

    const seconds = Number(rawValue)
    if (Number.isFinite(seconds)) return Math.max(0, seconds * 1000)

    const retryAt = Date.parse(String(rawValue))
    return Number.isFinite(retryAt) ? Math.max(0, retryAt - Date.now()) : null
  }

  function isUnsupportedAvatarEnvironment(error: any) {
    if (typeof RTCPeerConnection === 'undefined') return true
    const errorName = String(error?.name || '').toLowerCase()
    const message = String(error?.message || error || '').toLowerCase()
    return errorName === 'notsupportederror' ||
      message.includes('h264notsupported') ||
      message.includes('h264 not supported') ||
      message.includes('webrtc not supported') ||
      message.includes('rtcpeerconnection is not defined')
  }

  function getAvatarRetryDelay(error: any, failedAttempt: number) {
    const status = Number(error?.response?.status || 0)

    // 登录失效、无权限、服务未配置以及浏览器能力缺失都不是瞬时故障。
    if ([400, 401, 403, 503].includes(status) ||
      error?.name === 'AvatarCredentialError' ||
      isUnsupportedAvatarEnvironment(error)) return null

    // 除 408/425/429 外的 4xx 通常是请求本身有问题，继续重试没有意义。
    if (status >= 400 && status < 500 && ![408, 425, 429].includes(status)) return null

    if (status === 429) {
      const retryAfter = parseRetryAfterMilliseconds(error)
      if (retryAfter !== null) {
        // 至少等待服务端要求的时间，再追加少量随机抖动，避免客户端同时苏醒。
        return retryAfter + Math.random() * 500
      }
    }

    // Equal Jitter：第 1 次失败等待 1~2 秒，第 2 次失败等待 2~4 秒。
    const exponentialDelay = Math.min(2_000 * 2 ** (failedAttempt - 1), 8_000)
    return exponentialDelay / 2 + Math.random() * exponentialDelay / 2
  }

  function completePlayback() {
    if (playbackFallbackTimer) window.clearTimeout(playbackFallbackTimer)
    playbackFallbackTimer = null
    const resolve = playbackResolve
    playbackResolve = null
    resolve?.()
  }

  function destroyHumanInstance() {
    completePlayback()
    pcmQueue = new Uint8Array(0)
    pcmFrameOpen = false
    if (human) {
      try { human.removeAllListeners?.() } catch {}
      try { human.destroy?.() } catch {}
      human = null
    }
    if (humanContainer.value) humanContainer.value.innerHTML = ''
  }

  async function initDigitalHuman() {
    if (!humanContainer.value || isDestroyed) throw new Error('数字人容器尚未就绪')
    if (typeof RTCPeerConnection === 'undefined') throw new Error('当前浏览器不支持 WebRTC，已降级为文字面试')

    let finalError: unknown
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      if (isDestroyed) throw new Error('页面已经离开')
      destroyHumanInstance()
      let instance: any = null

      try {
        // 获取签名、创建实例和启动 SDK 都属于同一个 Attempt，任一步骤失败都走统一重试判断。
        const connection = await getAvatarConnection()
        if (!connection?.app_id || !connection?.signed_url) {
          const credentialError = new Error('未获取到数字人连接凭证')
          credentialError.name = 'AvatarCredentialError'
          throw credentialError
        }

        instance = new XFVirtualHuman({ useInlinePlayer: true })
        human = instance
        instance.setApiInfo({ appId: connection.app_id, signedUrl: connection.signed_url })
        instance.setGlobalParams({
          stream: { protocol: 'webrtc' },
          avatar: { avatar_id: 'cnr5dg8n2000000003', width: 1280, height: 720 },
          transparent: true,
          background: { type: 'none' },
          tts: { vcn: 'x4_mingge' }
        })

        await withTimeout(instance.start({ wrapper: humanContainer.value }), 15_000)
        if (instance !== human || isDestroyed) throw new Error('数字人实例已经失效')
        // 建连成功后再监听运行期断连，避免启动失败时 disconnected 与外层重试并发重建。
        instance.on(SDKEvents.frame_stop, completePlayback)
        instance.on(SDKEvents.disconnected, () => triggerReconnect())
        isHumanActive.value = true
        startAudioFeeder()
        return
      } catch (error: any) {
        finalError = error
        if (instance === human) {
          destroyHumanInstance()
        } else if (instance) {
          try { instance.removeAllListeners?.() } catch {}
          try { instance.destroy?.() } catch {}
        }

        if (attempt >= 3) break
        const retryDelay = getAvatarRetryDelay(error, attempt)
        if (retryDelay === null) break
        await delay(retryDelay)
      }
    }
    throw finalError instanceof Error ? finalError : new Error('数字人初始化失败')
  }

  function startAudioFeeder() {
    if (heartbeatTimer) window.clearInterval(heartbeatTimer)
    heartbeatTimer = window.setInterval(() => {
      if (!human || isDestroyed || isReconnecting || document.hidden || pcmQueue.length === 0) return

      const isLast = pcmQueue.length <= FRAME_BYTES
      const chunk = new Uint8Array(FRAME_BYTES)
      chunk.set(pcmQueue.slice(0, FRAME_BYTES))
      pcmQueue = pcmQueue.slice(Math.min(FRAME_BYTES, pcmQueue.length))
      const frameStatus = !pcmFrameOpen
        ? AUDIO_FRAME.start
        : isLast ? AUDIO_FRAME.end : AUDIO_FRAME.intermediate
      pcmFrameOpen = !isLast
      const buffer = chunk.buffer.slice(chunk.byteOffset, chunk.byteOffset + chunk.byteLength)

      Promise.resolve(human.writeAudio(buffer, frameStatus)).catch((error: unknown) => {
        if (String(error).includes('InvalidConnect')) triggerReconnect()
      })
    }, 40)
  } 

  async function triggerReconnect() {
    if (isReconnecting || isDestroyed || isInterviewFinished.value) return
    isReconnecting = true
    if (heartbeatTimer) window.clearInterval(heartbeatTimer)
    heartbeatTimer = null
    pcmQueue = new Uint8Array(0)
    pcmFrameOpen = false
    completePlayback()
    try {
      await initDigitalHuman()
      ElMessage.success('面试官连接已恢复')
    } catch {
      isHumanActive.value = false
      ElMessage.warning('数字人暂时离线，仍可使用文字或语音回答')
    } finally {
      isReconnecting = false
      if (phase.value === 'speaking') phase.value = 'ready'
    }
  }

  async function playInterviewAudio(audioBlob: Blob) {
    if (isDestroyed || !human) return
    completePlayback()
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
    const decodeContext = new AudioContextClass({ sampleRate: 16_000 })
    try {
      const audioBuffer = await decodeContext.decodeAudioData(await audioBlob.arrayBuffer())
      const source = audioBuffer.getChannelData(0)
      const pcm16 = new Int16Array(source.length)
      for (let index = 0; index < source.length; index += 1) {
        const sample = Math.max(-1, Math.min(1, source[index]))
        pcm16[index] = sample < 0 ? sample * 0x8000 : sample * 0x7fff
      }

      const silence = new Uint8Array(48_000) // 1.5 秒，避免 SDK 提前收口最后一个口型
      const incoming = new Uint8Array(pcm16.byteLength + silence.byteLength)
      incoming.set(new Uint8Array(pcm16.buffer))
      incoming.set(silence, pcm16.byteLength)
      const combined = new Uint8Array(pcmQueue.length + incoming.length)
      combined.set(pcmQueue)
      combined.set(incoming, pcmQueue.length)
      pcmQueue = combined

      await new Promise<void>(resolve => {
        playbackResolve = resolve
        const expectedMilliseconds = Math.ceil((audioBuffer.duration + 3) * 1000)
        playbackFallbackTimer = window.setTimeout(completePlayback, expectedMilliseconds)
      })
    } finally {
      await decodeContext.close().catch(() => {})
    }
  }

  async function speakAudioUrl(audioUrl: string) {
    if (!audioUrl || !human) return
    phase.value = 'speaking'
    try {
      const blob = await fetchAudioBlob(audioUrl)
      await playInterviewAudio(blob)
    } catch (error) {
      console.error('面试官音频播放失败，降级为文字题目:', error)
      ElMessage.warning('面试官语音加载失败，请按文字题目作答')
    }
  }

  async function startCamera() {
    try {
      const acquired = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false
      })
      if (isDestroyed) {
        acquired.getTracks().forEach(track => track.stop())
        return
      }
      cameraStream.value = acquired
      if (videoRef.value) videoRef.value.srcObject = acquired
      startCaptureTimer()
    } catch (error) {
      console.error('摄像头授权失败:', error)
      ElMessage.warning('摄像头不可用，本次面试将缺少视频维度分析')
    }
  }

  function stopCamera() {
    cameraStream.value?.getTracks().forEach(track => track.stop())
    cameraStream.value = null
    if (videoRef.value) videoRef.value.srcObject = null
    if (captureTimer) window.clearInterval(captureTimer)
    captureTimer = null
  }

  function startCaptureTimer() {
    if (captureTimer) window.clearInterval(captureTimer)
    captureTimer = window.setInterval(async () => {
      if (screenshotUploadInFlight || isDestroyed || document.hidden) return
      const video = videoRef.value
      const canvas = canvasRef.value
      if (!video || !canvas || video.videoWidth === 0) return
      const context = canvas.getContext('2d')
      if (!context) return
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height)
      const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8))
      if (!blob) return
      screenshotUploadInFlight = true
      const formData = new FormData()
      formData.append('session_id', currentSessionId.value)
      formData.append('screenshot', blob, `frame_${Date.now()}.jpg`)
      uploadScreenshot(formData).catch(() => {}).finally(() => { screenshotUploadInFlight = false })
    }, 5000)
  }

  function updateVolume() {
    if (!analyser || isDestroyed) return
    if (isRecording.value) {
      const samples = new Uint8Array(analyser.fftSize)
      analyser.getByteTimeDomainData(samples)
      let sum = 0
      for (const value of samples) {
        const amplitude = (value - 128) / 128
        sum += amplitude * amplitude
      }
      const rms = Math.sqrt(sum / samples.length)
      const target = Math.min(2.5, rms * 10 + 0.2)
      audioLevel.value += (target - audioLevel.value) * 0.3
    } else {
      audioLevel.value += (0.2 - audioLevel.value) * 0.2
    }
    animationFrameId = requestAnimationFrame(updateVolume)
  }

  async function startRecording() {
    if (!canAnswer.value || mediaRecorder.value) return
    isRequestingMedia = true
    try {
      recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      if (isDestroyed) {
        recordingStream.getTracks().forEach(track => track.stop())
        return
      }
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
      audioContext = new AudioContextClass()
      if (audioContext.state === 'suspended') await audioContext.resume()
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      audioContext.createMediaStreamSource(recordingStream).connect(analyser)

      const recorder = new MediaRecorder(recordingStream)
      mediaRecorder.value = recorder
      audioChunks.value = []
      recorder.ondataavailable = event => {
        if (event.data.size > 0) audioChunks.value.push(event.data)
      }
      recorder.onerror = event => {
        console.error('MediaRecorder 录制失败:', event)
        ElMessage.error('录音失败，请重新录制或使用文字回答')
      }
      recorder.onstop = async () => {
        const blob = new Blob(audioChunks.value, { type: recorder.mimeType || 'audio/webm' })
        recordingStream?.getTracks().forEach(track => track.stop())
        recordingStream = null
        mediaRecorder.value = null
        try {
          if (!isDestroyed && blob.size > 0) await handleAudioSubmit(blob)
        } finally {
          resolveRecordingStop?.()
          resolveRecordingStop = null
          stopRecordingPromise = null
        }
      }
      recorder.start(250)
      phase.value = 'recording'
      if (animationFrameId) cancelAnimationFrame(animationFrameId)
      updateVolume()
    } catch (error) {
      recordingStream?.getTracks().forEach(track => track.stop())
      recordingStream = null
      mediaRecorder.value = null
      phase.value = 'ready'
      console.error('无法访问麦克风:', error)
      ElMessage.error('无法访问麦克风，请检查浏览器权限或使用文字回答')
    } finally {
      isRequestingMedia = false
    }
  }

  function stopRecording() {
    const recorder = mediaRecorder.value
    if (!recorder || !['recording', 'paused'].includes(recorder.state)) return Promise.resolve()
    if (!stopRecordingPromise) {
      stopRecordingPromise = new Promise<void>(resolve => { resolveRecordingStop = resolve })
    }
    phase.value = 'submitting'
    recorder.stop()
    if (animationFrameId) cancelAnimationFrame(animationFrameId)
    animationFrameId = null
    audioContext?.close().catch(() => {})
    audioContext = null
    analyser = null
    return stopRecordingPromise
  }

  function toggleMic() {
    if (isRecording.value) void stopRecording()
    else void startRecording()
  }

  function normalizeResponse(response: any) {
    return response?.data?.status ? response.data : response
  }

  function updateMetrics(data: any) {
    const scores = data.scores || {}
    const confidence = Number(data.confidence ?? scores.communication ?? 0)
    const eye = Number(data.eye_contact ?? scores.non_verbal ?? 0)
    const fluency = Number(data.speak_rate ?? scores.logic ?? 0)
    const values = [confidence, eye, fluency]
    values.forEach((value, index) => {
      if (Number.isFinite(value) && value > 0) metrics.value[index].value = Math.min(100, Math.round(value))
    })
    metrics.value[0].note = confidence ? '来自本轮沟通维度评分' : metrics.value[0].note
    metrics.value[1].note = eye ? '来自本轮非语言维度评分' : metrics.value[1].note
    metrics.value[2].note = fluency ? '来自本轮逻辑与表达评分' : metrics.value[2].note
  }

  async function processNextTurn(response: any) {
    if (isDestroyed) return
    const data = normalizeResponse(response)
    if (data?.status !== 'success') throw new Error(data?.message || '提交失败')

    const nextQuestion = data.reply_to_user || data.reply_text || data.reply || '请继续回答当前问题。'
    const nextAction = data.next_action || '追问'
    const isEnd = Boolean(data.is_finished || nextAction === '结束')
    const isRetry = nextAction === '提示重试'

    questionText.value = nextQuestion
    questionTotal.value = Number(data.total_questions) || questionTotal.value
    if (Number(data.question_number)) {
      questionIndex.value = Number(data.question_number)
    } else if (nextAction === '换题' && !isEnd) {
      questionIndex.value = Math.min(questionIndex.value + 1, questionTotal.value)
    }

    updateMetrics(data)
    const analysis = data.suggestion || data.thought_process
    if (analysis) insights.value = [{ title: '实时评估', text: analysis }]
    const scores = data.scores || {}
    const scoreValues = Object.values(scores).map(Number).filter(Number.isFinite)
    const score = scoreValues.length
      ? Math.round(scoreValues.reduce((sum, value) => sum + value, 0) / scoreValues.length)
      : 0
    sessionStorage.setItem(`summary_${currentSessionId.value}`, JSON.stringify({
      score,
      answeredCount: isRetry ? Math.max(0, questionIndex.value - 1) : questionIndex.value,
      totalCount: questionTotal.value,
      analysis: analysis || 'AI 正在整理本轮回答。',
      timeSpent: totalSeconds.value - remainingSeconds.value
    }))

    const replyAudioUrl = data.reply_audio_url || data.reply_audio || ''
    persistSessionState(replyAudioUrl)
    answerText.value = ''
    audioChunks.value = []

    if (isEndingRequested) return
    if (replyAudioUrl) await speakAudioUrl(replyAudioUrl)
    if (isEnd) {
      await finalizeInterview()
    } else {
      phase.value = 'ready'
    }
  }

  async function handleAudioSubmit(blob: Blob) {
    if (currentSubmitPromise) return currentSubmitPromise
    pendingAudioBlob.value = blob
    pendingAudioTurnId ||= createTurnId()
    const previousQuestion = questionText.value
    phase.value = 'submitting'
    questionText.value = 'AI 正在分析您的回答并生成下一题，请稍候...'

    currentSubmitPromise = (async () => {
      try {
        const formData = new FormData()
        formData.append('session_id', currentSessionId.value)
        formData.append('client_turn_id', pendingAudioTurnId)
        formData.append('audio_file', blob, 'record.webm')
        const response = await submitAnswer(formData)
        await processNextTurn(response)
        pendingAudioBlob.value = null
        pendingAudioTurnId = ''
      } catch (error: any) {
        questionText.value = previousQuestion
        if (!isEndingRequested) phase.value = 'ready'
        ElMessage.error(error?.response?.status === 404
          ? '面试会话已过期，请重新发起面试'
          : '答案上传失败，录音已保留，可点击重试')
      }
    })()
    try {
      await currentSubmitPromise
    } finally {
      currentSubmitPromise = null
    }
  }

  async function retryLastAudio() {
    if (pendingAudioBlob.value && !currentSubmitPromise) await handleAudioSubmit(pendingAudioBlob.value)
  }

  async function handleTextSubmit() {
    const text = answerText.value.trim()
    if (!canAnswer.value || !text || currentSubmitPromise) return
    const previousQuestion = questionText.value
    if (!pendingTextTurn || pendingTextTurn.text !== text) {
      pendingTextTurn = { text, id: createTurnId() }
    }
    phase.value = 'submitting'
    questionText.value = 'AI 正在分析您的回答并生成下一题，请稍候...'
    currentSubmitPromise = (async () => {
      try {
        const response = await submitTextAnswer({
          session_id: currentSessionId.value,
          user_text: text,
          client_turn_id: pendingTextTurn?.id
        })
        await processNextTurn(response)
        pendingTextTurn = null
      } catch (error: any) {
        questionText.value = previousQuestion
        phase.value = 'ready'
        ElMessage.error(error?.response?.status === 404 ? '面试会话已过期，请重新发起面试' : '文字答案提交失败，请重试')
      }
    })()
    try {
      await currentSubmitPromise
    } finally {
      currentSubmitPromise = null
    }
  }

  function syncCountdown() {
    if (!deadlineAt || isInterviewFinished.value) return
    remainingSeconds.value = Math.max(0, Math.ceil((deadlineAt - Date.now()) / 1000))
    if (remainingSeconds.value === 0) void endInterview(true)
  }

  function startTimer() {
    if (countdownTimer || isDestroyed) return
    const savedDeadline = Number(sessionStorage.getItem(deadlineKey()))
    deadlineAt = savedDeadline > Date.now() ? savedDeadline : Date.now() + remainingSeconds.value * 1000
    sessionStorage.setItem(deadlineKey(), String(deadlineAt))
    syncCountdown()
    countdownTimer = window.setInterval(syncCountdown, 1000)
  }

  async function finalizeInterview() {
    if (isInterviewFinished.value || isDestroyed) return
    isGeneratingReport.value = true
    phase.value = 'finishing'
    if (countdownTimer) window.clearInterval(countdownTimer)
    countdownTimer = null
    if (heartbeatTimer) window.clearInterval(heartbeatTimer)
    heartbeatTimer = null
    stopCamera()
    sessionStorage.removeItem(deadlineKey())
    isInterviewFinished.value = true
    phase.value = 'finished'
    emit('interview-end')
  }

  async function executeEndInterview() {
    if (isEndingRequested || isInterviewFinished.value) return
    isEndingRequested = true
    if (isRecording.value) await stopRecording()
    if (currentSubmitPromise) await currentSubmitPromise
    await finalizeInterview()
  }

  async function endInterview(isForced = false) {
    if (isForced) {
      ElMessage.warning('面试时间已结束')
      await executeEndInterview()
      return
    }
    try {
      await ElMessageBox.confirm(
        '确认后将提交当前正在上传的答案，并生成完整评估报告。',
        '确认结束面试',
        { confirmButtonText: '确认结束并生成报告', cancelButtonText: '返回继续面试', customClass: 'custom-msg-box' }
      )
      await executeEndInterview()
    } catch {}
  }

  async function activateInterview() {
    if (phase.value === 'initializing' || isDestroyed) return
    startupError.value = ''
    phase.value = 'initializing'
    await nextTick()
    try {
      const [humanResult] = await Promise.allSettled([initDigitalHuman(), startCamera()])
      if (humanResult.status === 'rejected') throw humanResult.reason
      if (isDestroyed) return
      startTimer()
      const openingAudioUrl = restoreSessionState()
      if (openingAudioUrl) await speakAudioUrl(openingAudioUrl)
      if (!isDestroyed) phase.value = 'ready'
    } catch (error: any) {
      isHumanActive.value = false
      startupError.value = error?.message || '数字人初始化失败'
      phase.value = 'error'
    }
  }

  function processLeaveEvent(reason: string) {
    const activePhases: InterviewPhase[] = ['speaking', 'ready', 'recording', 'submitting']
    if (isDestroyed || isRequestingMedia || showWarningModal.value || !activePhases.includes(phase.value)) return
    const now = Date.now()
    if (now - lastLeaveAt < 800) return
    lastLeaveAt = now
    leaveCount.value += 1
    warningReason.value = reason
    showWarningModal.value = true
    if (mediaRecorder.value?.state === 'recording') {
      phaseBeforePause.value = phase.value
      mediaRecorder.value.pause()
    }
    syncCountdown() // 后台会限制定时器，按绝对截止时间校正；正式面试不暂停总时长
  }

  function closeWarningModal() {
    showWarningModal.value = false
    if (mediaRecorder.value?.state === 'paused') mediaRecorder.value.resume()
    phaseBeforePause.value = null
  }

  const handleVisibilityChange = () => {
    if (document.hidden) processLeaveEvent('切换标签页或最小化浏览器')
    else syncCountdown()
  }
  const handleWindowBlur = () => window.setTimeout(() => {
    if (!document.hasFocus()) processLeaveEvent('离开面试窗口焦点')
  }, 200)
  const handleOffline = () => {
    networkOffline.value = true
    ElMessage.warning('网络已断开，录音可继续，恢复网络后再提交')
  }
  const handleOnline = () => {
    networkOffline.value = false
    ElMessage.success('网络已恢复')
  }
  const handleBeforeUnload = (event: BeforeUnloadEvent) => {
    if (isInterviewFinished.value || phase.value === 'idle' || phase.value === 'error') return
    event.preventDefault()
    event.returnValue = ''
  }
  const handlePageHide = (event: PageTransitionEvent) => {
    if (!event.persisted) destroyEverything()
  }

  function destroyEverything() {
    if (isDestroyed) return
    isDestroyed = true
    if (animationFrameId) cancelAnimationFrame(animationFrameId)
    if (heartbeatTimer) window.clearInterval(heartbeatTimer)
    if (countdownTimer) window.clearInterval(countdownTimer)
    if (captureTimer) window.clearInterval(captureTimer)
    completePlayback()
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.onstop = null
      mediaRecorder.value.stop()
    }
    recordingStream?.getTracks().forEach(track => track.stop())
    recordingStream = null
    audioContext?.close().catch(() => {})
    stopCamera()
    destroyHumanInstance()
  }

  onMounted(() => {
    isDestroyed = false
    currentSessionId.value = String(route.params.sessionId || '')
    restoreSessionState()
    try {
      const savedDifficulty = JSON.parse(sessionStorage.getItem('interview_difficulty') || 'null')
      if (savedDifficulty?.level) difficulty.value = savedDifficulty
    } catch {}
    isFormalExam.value = sessionStorage.getItem('isFormalExam') === 'true'
    candidateName.value = sessionStorage.getItem('candidateName') || ''
    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('blur', handleWindowBlur)
    window.addEventListener('offline', handleOffline)
    window.addEventListener('online', handleOnline)
    window.addEventListener('beforeunload', handleBeforeUnload)
    window.addEventListener('pagehide', handlePageHide)
  })

  onBeforeRouteLeave(async (_to, _from, next) => {
    if (isInterviewFinished.value || phase.value === 'idle' || phase.value === 'error') return next()
    try {
      await ElMessageBox.confirm(
        '面试正在进行中，离开会丢失尚未提交的录音，确认离开吗？',
        '确认离开页面',
        { confirmButtonText: '确认离开', cancelButtonText: '继续面试', customClass: 'custom-msg-box' }
      )
      destroyEverything()
      next()
    } catch {
      next(false)
    }
  })

  const removeListeners = () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    window.removeEventListener('blur', handleWindowBlur)
    window.removeEventListener('offline', handleOffline)
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('beforeunload', handleBeforeUnload)
    window.removeEventListener('pagehide', handlePageHide)
    destroyEverything()
  }
  onBeforeUnmount(removeListeners)
  onDeactivated(removeListeners)

  return {
    phase, currentSessionId, questionText, questionIndex, questionTotal, answerText,
    startupError, networkOffline, isHumanActive, isHumanLoading, isSpeaking,
    isRecording, isSubmitting, canAnswer, isRecordDisabled, micOn,
    isGeneratingReport, leaveCount, showWarningModal, warningReason,
    isFormalExam, candidateName, difficulty, candidate, metrics, insights,
    timer, progress, subtitle, humanContainer, videoRef, canvasRef, audioLevel,
    activateInterview, endInterview, toggleMic, stopRecording, handleTextSubmit,
    retryLastAudio, pendingAudioBlob, closeWarningModal
  }
}
