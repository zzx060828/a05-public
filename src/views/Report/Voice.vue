<script setup>
// 🔴 1. 接收从父组件 (ReportView) 传来的真实音频分析数据
defineProps({
  voiceData: {
    type: Array,
    default: () => []
  }
});

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
          <svg t="1773559577631" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1159" width="200" height="200"><path d="M455.9 244a30 30 0 0 1-30 30H249.22v-60H425.9a30 30 0 0 1 30 30zM455.9 447.39a30 30 0 0 1-30 30H249.22v-60H425.9a30 30 0 0 1 30 30zM775.66 214v60h-177a30 30 0 0 1 0-60h177zM775.66 417.4v60h-177a30 30 0 0 1 0-60h177z" fill="#D0D3D8" p-id="1160"></path><path d="M685.66 13.36H339.22a90.1 90.1 0 0 0-90 90V588a90.1 90.1 0 0 0 90 90h143.32v272.64H379.95a30 30 0 0 0 0 60h265.31a30 30 0 0 0 0-60H542.54V678h143.12a90.1 90.1 0 0 0 90-90V103.36a90.1 90.1 0 0 0-90-90z m30 574.67a30 30 0 0 1-30 30H339.22a30 30 0 0 1-30-30V103.36a30 30 0 0 1 30-30h346.44a30 30 0 0 1 30 30z" fill="#878A94" p-id="1161"></path></svg>
        </span>
        <span class="title-text">音频分析</span>
      </div>
      
      <div class="score-items">
        <template v-for="(item, index) in voiceData" :key="index">
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

        <div v-if="!voiceData.length" style="color: #999; grid-column: 1 / -1;">
          暂无音频分析数据
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ====== 完全保留你的原始样式 ====== */
.interview-analysis-report {
  width: 100%;
  padding: 80px 50px;
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
  font-size: 2px;
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

@media (max-width: 768px) {
  .score-items {
    grid-template-columns: 1fr;
  }
  .module-title {
    font-size: 16px;
  }
  .suggestion-text {
    font-size: 11px;
  }
}

.icon {
  width: 23px;
  height: 23px;
}
</style>