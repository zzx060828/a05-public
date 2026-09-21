<script setup>
// 🔴 1. 接收从父组件 (ReportView) 传来的真实视频分析数据
defineProps({
  videoData: {
    type: Array,
    default: () => []
  }
});

// 🔴 2. 动态计算进度条颜色 (90分以上绿，60分以上蓝，其余橙)
// 🔴 2. 动态计算进度条颜色 (使用现代高级渐变色)
const getBarColor = (percent) => {
  // 优秀 (>=80)：翡翠绿渐变，沉稳健康
  if (percent >= 80) return 'linear-gradient(90deg, #34d399 0%, #10b981 100%)'; 
  
  // 良好 (>=60)：科技蓝渐变 (呼应你报告页 loading 的 #0ea5e9)
  if (percent >= 60) return 'linear-gradient(90deg, #7dd3fc 0%, #0ea5e9 100%)'; 
  
  // 待提升 (<60)：琥珀橙渐变，起警示作用但不刺眼
  return 'linear-gradient(90deg, #fcd34d 0%, #f59e0b 100%)'; 
};
</script>

<template>
  <div class="interview-analysis-report">
    <div class="analysis-module">
      <div class="module-title">
        <span class="title-icon">
          <svg t="1773559726915" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1317" width="200" height="200"><path d="M520.61 170.07A123.09 123.09 0 1 0 643.7 293.16a123.23 123.23 0 0 0-123.09-123.09z" fill="#D0D3D8" p-id="1318"></path><path d="M754.59 290.79c0-124.59-101.36-226-226-226h-16.01c-124.59 0-226 101.36-226 226v238.74h468z m-234 185.46c-101 0-183.09-82.13-183.09-183.09s82.13-183.09 183.09-183.09S703.7 192.21 703.7 293.16s-82.14 183.09-183.09 183.09z" fill="#D0D3D8" p-id="1319"></path><path d="M730.83 88.59a284.08 284.08 0 0 0-202.2-83.75h-16.05a286 286 0 0 0-286 286v298.69a286 286 0 0 0 264 285.12v84.51H371.86a30 30 0 0 0 0 60h297.5a30 30 0 0 0 0-60H550.61v-84.51a286 286 0 0 0 264-285.12V290.79a284.08 284.08 0 0 0-83.78-202.2z m-202.2 726.9h-16.05c-124.59 0-226-101.36-226-226v-298.7c0-124.59 101.36-226 226-226h16.05c124.59 0 226 101.36 226 226v298.74c-0.04 124.6-101.4 225.96-226 225.96z" fill="#878A94" p-id="1320"></path><path d="M520.61 110.07c-101 0-183.09 82.13-183.09 183.09s82.13 183.09 183.09 183.09S703.7 394.12 703.7 293.16s-82.14-183.09-183.09-183.09z m0 306.18A123.09 123.09 0 1 1 643.7 293.16a123.23 123.23 0 0 1-123.09 123.09z" fill="#878A94" p-id="1321"></path><path d="M520.61 677.86m-50 0a50 50 0 1 0 100 0 50 50 0 1 0-100 0Z" fill="#D0D3D8" p-id="1322"></path></svg>
        </span>
        <span class="title-text">视频分析</span>
      </div>
      
      <div class="score-items">
        <template v-for="(item, index) in videoData" :key="index">
          <div class="score-item">
            <div class="item-label">{{ item.label }}</div>
            <div class="item-content">
              <div class="progress-bar-wrap">
                <div 
                  class="progress-bar" 
                  :style="{ width: item.percent + '%', background: getBarColor(item.percent) }"
                ></div>
              </div>
              <div class="score-info">
                <span class="score-num">{{ item.score }}/{{ item.total }}</span>
                <span class="score-percent">{{ item.percent }}%</span>
              </div>
            </div>
            <div v-if="item.suggestion" class="suggestion-text">
              {{ item.suggestion }}
            </div>
          </div>
        </template>

        <div v-if="!videoData || videoData.length === 0" style="color: #999; grid-column: 1 / -1;">
          暂无视频分析数据
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ====== 完全保留你的原始样式 ====== */
.interview-analysis-report {
  width: 100%;
  padding: 100px 50px;
  font-family: "Microsoft Yahei", Arial, sans-serif;
  color: #333;
  background: #fff;
}

.analysis-module {
  margin-bottom: 30px;
  padding: 15px 0;
}

.module-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #222;
}

.title-icon {
  font-size: 20px; /* 注意：原代码此处为 20px，与 Voice 略有不同 */
  margin-right: 8px;
}

.title-text {
  line-height: 1;
}

.score-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 20px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-label {
  font-size: 14px;
  color: #666;
  line-height: 1.2;
}

.item-content {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.progress-bar-wrap {
  flex: 1;
  height: 8px; /* 稍微加厚一点点，从 6px 改为 8px，视觉更饱满 */
  background-color: #f1f5f9; /* 底槽颜色改浅一点，更现代 */
  border-radius: 4px; /* 圆角改大 */
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px; /* 圆角同步改大 */
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); /* 让动画更丝滑 */
}
.score-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 60px;
  font-size: 12px;
}

.score-num {
  font-weight: 500;
  color: #333;
  line-height: 1.2;
}

.score-percent {
  color: #999;
  font-size: 11px;
  line-height: 1.2;
}

.suggestion-text {
  /* 🔴 删除了 grid-column 属性 */
  font-size: 12px;
  color: #666;
  padding-left: 2px;
  margin-top: 4px; /* 增加一点上边距让排版更好看 */
  line-height: 1.4;
}

.icon {
  width: 23px;
  height: 23px;
}
</style>