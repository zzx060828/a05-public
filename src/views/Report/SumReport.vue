<script setup>
import { onMounted, ref, watch, nextTick } from "vue";
import * as echarts from "echarts";

// 🔴 1. 接收来自 ReportView 传入的真实数据
const props = defineProps({
  scoreList: { type: Array, default: () => [] },
  advantages: { type: Array, default: () => [] },
  disadvantages: { type: Array, default: () => [] }
});

const chartRef = ref(null);
let myChart = null;

// 🔴 2. 更新雷达图的方法（使用真实数据）
const updateChart = async () => {
  await nextTick();
  if (!chartRef.value || !props.scoreList.length) return;
  
  if (!myChart) {
    myChart = echarts.init(chartRef.value, null, { renderer: 'svg' });
  }

  const option = {
    animation: false,
    tooltip: {},
    radar: {
      center: ['40%', '50%'], 
      radius: "55%", // 半径保持小一点，防越界
      indicator: props.scoreList.map(item => ({ name: item.name, max: 100 })),
      splitLine: {
        lineStyle: { color: "#ddd" }
      },
      // 🌟 修复 ECharts 自己的文字过长问题
      axisName: {
        color: '#666',
        fontSize: 13,
      }
    },
    series: [
      {
        type: "radar",
        data: [
          {
            // 使用真实的分数值
            value: props.scoreList.map(item => item.value),
            areaStyle: { opacity: 0.3 }
          }
        ]
      }
    ]
  };

  myChart.setOption(option);
};

// 🔴 3. 监听数据变化，后端数据到了就重绘雷达图
watch(() => props.scoreList, updateChart, { deep: true });

onMounted(() => {
  updateChart();
  window.addEventListener("resize", () => {
    myChart?.resize();
  });
});
</script>

<template>
  <div class="report-container">
    <div class="top-report">
      <div class="chart" ref="chartRef"></div>

      <div class="score-panel">
        <div 
          v-for="item in scoreList" 
          :key="item.name"
          class="score-item"
        >
          <span class="label">{{ item.name }}：</span>
          <span class="value">{{ item.value }} 分</span>
        </div>
        
        <div v-if="!scoreList.length" style="color: #999; text-align: center;">
          AI 正在评估维度得分...
        </div>
      </div>
    </div>

    <div class="analysis-container">
      <div class="advantage-section">
        <h3 class="section-title">优势分析</h3>
        <ul class="analysis-list">
          <li 
            v-for="(advantage, index) in advantages" 
            :key="'advantage-' + index"
            class="analysis-item"
          >
            {{ advantage }}
          </li>
          <li v-if="!advantages.length" class="analysis-item" style="color: #999;">
            分析生成中...
          </li>
        </ul>
      </div>

      <div class="disadvantage-section">
        <h3 class="section-title">待改进项</h3>
        <ul class="analysis-list">
          <li 
            v-for="(disadvantage, index) in disadvantages" 
            :key="'disadvantage-' + index"
            class="analysis-item"
          >
            {{ disadvantage }}
          </li>
          <li v-if="!disadvantages.length" class="analysis-item" style="color: #999;">
            分析生成中...
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ====== 完全保留你的原始样式 ====== */
.report-container {
  display: flex;
  flex-direction: column; 
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 40px;
  border-radius: 16px 16px 0 0;
  width: 100%;
  margin-top: 80px;
}

.top-report {
  width: 100%;
  display: flex;
  flex-wrap: nowrap; /* 绝对不允许换行 */
  justify-content: space-between;
  align-items: center;
}

.chart {
  width: 55%; /* 左边图表死死占住 55% 的地盘 */
  height: 400px;
  flex-shrink: 0; /* 绝对不许被挤压缩水 */
}

.score-panel {
  width: 40%; /* 右边文字死死占住 40% 的地盘 */
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin: 30px 0;
  flex-shrink: 0; /* 同样不许被挤压 */
}

.score-item {
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  white-space: nowrap; /* 文字再长也不许换行 */
}

.label {
  color: #666;
}

.value {
  font-weight: bold;
  color: #363636;
}

.analysis-container {
  display: flex;
  width: 100%;
  gap: 30px;
  margin-top: 30px;
}

.advantage-section, .disadvantage-section {
  flex: 1;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 8px 8px 15px rgba(0,0,0,0.2);
}

.advantage-section {
  background: #A4C7E3;
}

.disadvantage-section {
  background: #F7F5B8;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(0,0,0,0.1);
}

.analysis-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.analysis-item {
  padding: 10px 15px;
  margin: 8px 0;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  font-size: 14px;
  color: #555;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analysis-container {
    flex-direction: column;
  }
  
  .report-container {
    padding: 20px;
  }
}
</style>