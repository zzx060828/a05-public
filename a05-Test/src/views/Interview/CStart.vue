<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { createInterview } from '@/api/interview'

const route = useRoute()
const router = useRouter()

const token = ref('')
const jobTitle = ref('')
const requirements = ref('')
const candidateName = ref('')
const isLoading = ref(true)
const errorMsg = ref('')
const isLoggingIn = ref(false)
const isStarting = ref(false)

onMounted(async () => {
  token.value = route.query.token || ''

  // 从登录页回来，恢复 token
  if (!token.value) {
    const savedToken = sessionStorage.getItem('candidate_token')
    if (savedToken) {
      token.value = savedToken
      // 用保存的 URL 参数替换，去掉 query 参数避免暴露 token
      router.replace({ query: { token: savedToken } })
    }
  }

  if (!token.value) {
    errorMsg.value = '缺少面试令牌，请联系HR获取正确的面试链接。'
    isLoading.value = false
    return
  }

  try {
    const res = await apiClient.get(`/api/c_api/verify_token/${token.value}`)
    if (res.data?.status === 'success') {
      jobTitle.value = res.data.job_title || ''
      requirements.value = res.data.requirements || ''
      candidateName.value = res.data.candidate_name || localStorage.getItem('username') || ''
    } else {
      errorMsg.value = res.data?.message || '无效的面试链接'
    }
  } catch {
    errorMsg.value = '验证链接失败，请检查网络或联系HR。'
  } finally {
    isLoading.value = false
  }

  // 从登录页回来后自动进入面试
  const isLogin = localStorage.getItem('isLogin') === 'true'
  if (isLogin && sessionStorage.getItem('isFormalExam') === 'true') {
    startInterview()
  }
})

function goToLogin() {
  isLoggingIn.value = true
  sessionStorage.setItem('candidate_token', token.value)
  sessionStorage.setItem('candidate_job', jobTitle.value)
  sessionStorage.setItem('isFormalExam', 'true')
  router.push('/login')
}

async function startInterview() {
  const isLogin = localStorage.getItem('isLogin') === 'true'
  if (!isLogin) {
    goToLogin()
    return
  }

  isStarting.value = true
  sessionStorage.setItem('candidate_token', token.value)
  sessionStorage.setItem('candidate_job', jobTitle.value)
  sessionStorage.setItem('isFormalExam', 'true')

  try {
    const response = await createInterview({
      token: token.value,
      position: jobTitle.value || '技术岗位',
      type: 'formal',
      difficulty: 3
    })

    const interviewId = response.sessionId || response.session_id
    if (!interviewId) {
      alert('创建面试失败，未获取到面试ID')
      return
    }

    // 存入开场白
    const firstQuestion = response.reply_text || response.reply || '你好，请先做一个简单的自我介绍。'
    sessionStorage.setItem('currentQuestion', firstQuestion)

    const firstAudioUrl = response.reply_audio_url
    if (firstAudioUrl) {
      sessionStorage.setItem('currentAudioUrl', firstAudioUrl)
    }

    sessionStorage.setItem(`interview_bootstrap_${interviewId}`, JSON.stringify({
      question: firstQuestion,
      audioUrl: firstAudioUrl || '',
      questionNumber: response.question_number || 1,
      totalQuestions: response.total_questions || 7
    }))

    router.push(`/interview/session/${interviewId}`)
  } catch (e) {
    console.error('创建面试失败:', e)
    alert('创建面试失败，请重试')
  } finally {
    isStarting.value = false
  }
}
</script>

<template>
  <div class="cstart-page">
    <div class="cstart-card" v-if="!isLoading && !errorMsg">
      <div class="cstart-header">
        <div class="cstart-logo">面伴 AI</div>
        <span class="cstart-badge">正式面试邀请</span>
      </div>

      <div class="cstart-body">
        <h2>{{ jobTitle || '技术岗位面试' }}</h2>
        <p v-if="candidateName" class="candidate-name">候选人：{{ candidateName }}</p>

        <div class="requirements-box" v-if="requirements">
          <h4>岗位要求</h4>
          <pre>{{ requirements }}</pre>
        </div>

        <div class="cstart-tips">
          <h4>面试须知</h4>
          <ul>
            <li>请确保摄像头和麦克风正常工作</li>
            <li>面试过程中请勿切换页面，否则将被记录</li>
            <li>面试时长约30分钟，请合理安排时间</li>
          </ul>
        </div>

        <div class="cstart-actions">
          <button class="btn-start" @click="startInterview" :disabled="isLoggingIn || isStarting">
            {{ isStarting ? '正在创建面试...' : isLoggingIn ? '跳转登录中...' : '进入面试' }}
          </button>
        </div>
      </div>
    </div>

    <div class="cstart-loading" v-if="isLoading">
      <div class="spinner"></div>
      <p>正在验证面试链接...</p>
    </div>

    <div class="cstart-error" v-if="errorMsg">
      <div class="error-icon">!</div>
      <p>{{ errorMsg }}</p>
    </div>
  </div>
</template>

<style scoped>
.cstart-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 50%, #ecfdf5 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.cstart-card {
  width: 520px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-50px) scale(0.9); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.cstart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #e0f2ff;
}

.cstart-logo {
  color: #164a81;
  font-size: 18px;
  font-weight: 600;
}

.cstart-badge {
  background: #43C9E2;
  color: #fff;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.cstart-body {
  padding: 24px;
}

.cstart-body h2 {
  margin: 0 0 6px;
  font-size: 20px;
  color: #1e293b;
  font-weight: 600;
}

.candidate-name {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 20px;
}

.requirements-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.requirements-box h4, .cstart-tips h4 {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.requirements-box pre {
  margin: 0;
  font-size: 14px;
  color: #475569;
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.6;
}

.cstart-tips {
  margin-bottom: 20px;
}

.cstart-tips ul {
  margin: 0;
  padding-left: 20px;
  color: #64748b;
  font-size: 14px;
  line-height: 2;
}

.cstart-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn-start {
  width: 100%;
  padding: 12px;
  background: #43C9E2;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-start:hover {
  background: #3ab4cc;
  box-shadow: 0 4px 12px rgba(67, 201, 226, 0.3);
}
.btn-start:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.cstart-loading, .cstart-error {
  text-align: center;
  color: #475569;
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid #d4f0f8;
  border-top-color: #43C9E2;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-icon {
  width: 48px; height: 48px;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 50%;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
</style>
