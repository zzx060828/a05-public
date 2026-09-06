<template>
  <div class="yearly-records-page">

    <!-- 标题 -->
    <h1 class="page-title">面试报告记录</h1>

    <!-- 卡片容器 -->
    <div class="records-container">
      <div 
        v-for="(record, index) in recordList" 
        :key="index"
        :class="['record-card', `record-${record.num}`]"
      >
        <div class="glow-circle" :class="{ 'hoyo-mix': record.type === 'hoyo' }">
              <div class="num">第<span style="font-size: 2.8rem;color: #3b9dc7;">{{ record.num }}</span>次报告</div>
              <div class="score">综合得分：{{ record.score }}</div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>

const recordList = [
  { num: 1, score:85 }, 
  { num: 2, score:60 }, 
  { num: 3, score:72 }, 
  { num: 4, score:97 }, 
  { num: 5, score:86 }, 
  { num: 6, score:92 }, 
];
</script>

<style scoped lang="scss">
.yearly-records-page {
  position: relative;
  z-index: 1;
  width: 100%;
  min-height: 100vh;  /* 确保最小高度为视口高度 */ 
  background-color: #f5fcff;
  margin-top: 80px;
  color: rgb(255, 255, 255);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.page-title {
  position: relative;
  z-index: 10;
  text-align: center;
  font-size: 2.8rem;
  font-weight: 600;
  margin: 4rem 0 3rem;
  text-shadow: 0 0 10px rgba(255,255,255,0.3);
  color: #1e294d;
  padding-top: 10px;
} 

.records-container {
  position: relative;
  z-index: 5;
  width: 90%;
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  padding: 0 2rem;

  .record-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;

    .num {
      font-size: 1.7rem;
      font-weight: 500;
      position: relative;
      z-index: 2;
      color: #000;
    }

    .score {
      font-size: 1.3rem;
      opacity: 0.9;
      position: relative;
      z-index: 2;
      color: #000;
    }

.glow-circle {
  width: 180px;
  height: 180px;
  border-radius: 49% 51% 53% 47% / 50% 48% 52% 50%;
  background: rgb(56, 86, 132);
  box-shadow: 0 0 30px 10px rgba(21, 56, 117, 0.4);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  transition: all 0.3s ease;
  cursor: pointer;

  // 中间白色区域
  &::before {
    content: '';
    width: 140px;
    height: 140px;
    margin: auto;
    border-radius: 48% 52% 60% 46% / 49% 51% 60% 50%;
    background-color: #fff;
    z-index: 1;
  }

  // 第一层缠绕线（虚线）
  &::after {
    content: '';
    width: 190px;
    height: 190px;
    position: absolute;
    border: 2px dashed rgba(33, 40, 116, 0.6);
    border-radius: 47% 53% 55% 45% / 51% 49% 50% 48%;
    z-index: 0;
    // 旋转角度，模拟缠绕
    transform: rotate(15deg);
    animation: rotate-line 20s linear infinite;
  }

  // 第二层缠绕线（实线）- 新增伪元素（需额外套一层div，或用父元素伪元素）
  &:nth-child(n) {
    &::before {
      // 这里用父元素伪元素补充第二层线，或给glow-circle套一个div
      content: '';
      width: 170px;
      height: 170px;
      position: absolute;
      border: 1px solid rgba(255, 255, 255, 0.4);
      border-radius: 52% 48% 46% 54% / 48% 52% 47% 51%;
      z-index: 0;
      transform: rotate(-25deg);
      animation: rotate-line-reverse 25s linear infinite;
    }
  }

  &:hover {
    border-radius: 51% 49% 47% 53% / 48% 52% 49% 51%;
    background: rgb(60, 102, 171);
    box-shadow: 0 0 40px 15px rgba(13, 60, 115, 0.6);
    transform: scale(1.05);
  }
}

// 缠绕线旋转动画（可选，增强动态感）
@keyframes rotate-line {
  0% { transform: rotate(15deg); }
  100% { transform: rotate(375deg); }
}
@keyframes rotate-line-reverse {
  0% { transform: rotate(-25deg); }
  100% { transform: rotate(-385deg); }
}
  }

  // 动态适配布局（和原图对齐）
  .record-1 { grid-area: 1 / 1 / 2 / 2; }
  .record-2 { grid-area: 1 / 2 / 2 / 3; }
  .record-3 { grid-area: 2 / 1 / 3 / 3; justify-self: center; }
  .record-4 { grid-area: 3 / 1 / 4 / 2; }
  .record-5 { grid-area: 3 / 2 / 4 / 3; }
  // 新增年份只需加一行布局，比如：
  // .singer-2020 { grid-area: 4 / 1 / 5 / 2; }
}

</style>