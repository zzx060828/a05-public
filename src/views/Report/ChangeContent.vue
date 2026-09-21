<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import * as echarts from "echarts"

const props = defineProps({
  xData: { type: Array, required: true },
  yData: { type: Array, required: true },
  title: { type: String, default: "" }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)

  const option = {
    animation: false,
    title: {
      text: props.title,
      left: "center",
      textStyle: { color: '#1e293b', fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      padding: [12, 16],
      textStyle: { color: '#334155' },
      formatter: function (params) {
        const axisName = params[0].name; 
        const dataPoint = params[0].data; 
        
        return `<div style="font-weight:600;margin-bottom:8px;color:#64748b;font-size:13px;display:flex;justify-content:space-between;gap:16px;">
                  <span>${axisName}</span>
                  <span style="font-weight:400;color:#94a3b8;">${dataPoint.exactTime || ''}</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#0ea5e9;"></span>
                  <span style="font-size:14px;">综合得分: <strong style="color:#0ea5e9;font-size:18px;margin-left:4px;">${dataPoint.value}</strong> 分</span>
                </div>`;
      }
    },
    grid: {
      left: "5%",  // 稍微大一点，比如 5% 或 8%
      right: "5%",
      bottom: "5%",
      top: "20%",
      containLabel: true // 这个必须为 true
    },
    xAxis: {
      type: "category",
      data: props.xData,
      boundaryGap: true,
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', margin: 12, fontSize: 12 }
    },
    yAxis: {
      type: "value",
      min: function(value) { return Math.max(0, value.min - 10); },
      max: 100,
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: [
      {
        // 从 change.vue 传过来的应该是一个包含 value 属性的对象数组
        data: props.yData,
        type: "line",
        smooth: 0.4, 
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#0ea5e9', // 🌟 折线拐点：青蓝色
          borderColor: '#ffffff',
          borderWidth: 2
        },
        lineStyle: {
          width: 4,
          color: '#0ea5e9', // 🌟 主线条：青蓝色
          shadowColor: 'rgba(14, 165, 233, 0.3)', // 🌟 发光阴影
          shadowBlur: 10,
          shadowOffsetY: 5
        },
        areaStyle: {
          // 🌟 底部渐变：由青蓝色变透明
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(14, 165, 233, 0.35)" },
            { offset: 1, color: "rgba(14, 165, 233, 0.02)" }
          ])
        }
      }
    ],
    
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance && chartInstance.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener("resize", resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeChart)
  chartInstance && chartInstance.dispose()
})

watch(
  () => [props.xData, props.yData],
  () => {
    chartInstance && chartInstance.setOption({
      xAxis: { data: props.xData },
      series: [{ data: props.yData }]
    })
  },
  { deep: true }
)
</script>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
}
</style>