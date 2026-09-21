<template>
  <div class="ai-interview-container">
    <div class="content-wrapper">
      <h1 class="main-title">AI Interview</h1>
<div class="semicircle-wrapper">
        <!-- 主半圆 -->
        <div class="semicircle main-semicircle"></div>
        <!-- 叠加的装饰半圆 -->
        <div class="semicircle overlay-semicircle"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 仅需基础结构，无需额外逻辑
</script>

<style scoped>
.ai-interview-container {
  width: 100vw;
  height: 100vh;
  background-color:#ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 190px;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 20px 20px;
}

.main-title {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 16em;
  font-weight: 700;
  color: #000000;
  margin: 0 0 60px 0;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.gradient-shapes {
  position: relative;
  width: 100%;
  max-width: 900px;
  height: 300px;
}

.shape {
  position: absolute;
  bottom: 0;
  border-radius: 50% 50% 0 0;
  filter: blur(10px);
  opacity: 0.8;

}

.shape-1 {
  left: 0;
  width: 70%;
  height: 100%;
  background: linear-gradient(135deg, #42a5f5, #bed1da);
}

.shape-2 {
  left: 5%;
  width: 65%;
  height: 90%;
  background: linear-gradient(135deg, #29b6f6, #bfc3df);
}

.shape-3 {
  right: 0;
  width: 70%;
  height: 100%;
  background: linear-gradient(135deg, #ff9800, #e6c4c2);
}

.shape-4 {
  right: 5%;
  width: 65%;
  height: 90%;
  background: linear-gradient(135deg, #ffb74d, #e91e63);
}
</style>