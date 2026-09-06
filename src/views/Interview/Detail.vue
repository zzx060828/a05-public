<template>
  <div class="interview-container">
    <Start v-if="!isFinished" @interview-end="handleInterviewEnd" />
    <Finish v-else :session-id="currentSessionId" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Start from './Start.vue'
import Finish from '../Interview/Finish.vue'

const route = useRoute()
const isFinished = ref(false) // 是否面试结束的开关
const currentSessionId = ref("")

onMounted(() => {
  currentSessionId.value = route.params.sessionId
})

// 接收来自 Start 组件的“面试结束”信号
const handleInterviewEnd = () => {
  isFinished.value = true
}
</script>