<template>
  <div class="assessment-page">
    <main class="main-content">
      <div class="container">
        
        <div v-if="isLoading" class="status-container">
          <div class="loading-spinner"></div>
          <p>AI 导师正在深度分析您的全局表现，为您生成专属突击计划...</p>
        </div>

        <div v-else-if="!hasHistory" class="status-container">
          <p>暂无足够数据。请先完成至少一次全真面试，以解锁专属提升计划。</p>
        </div>

        <template v-else>
          <section class="result-overview">
            <div class="result-charts">
              <div class="chart-container">
                <div class="chart-header">
                  <div class="result-cards-left">全局平均能力</div>
                </div>
                <div class="chart-and-details">
                  <div ref="radarChart" class="radar-chart"></div>
                  
                  <div class="score-details">
                    <div class="score-item" v-for="(item, index) in radarData" :key="index">
                      <span class="score-label">{{ item.name }}</span>
                      <span class="score-value">{{ item.value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="suggestions">
            <h2>
              <span class="icon"><svg t="1773233549553" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4981" width="200" height="200"><path d="M642.160874 894.856008l0 11.1857q0 5.084409 0.508441 11.1857t0.508441 12.202582q-1.016882 19.320755-10.677259 42.200596t-37.116187 33.048659q-11.1857 4.067527-28.981132 11.694141t-53.386296 7.626614q-30.506455 0-50.33565-7.118173t-31.014896-9.151936q-14.236346-3.050645-22.879841-12.711023t-13.219464-21.862959-5.59285-24.913605-1.016882-22.879841l0-31.523337zM862.82423 229.815293q26.438928 62.029791 30.506455 116.94141t-6.101291 101.179742-29.489573 82.875869-40.166832 64.063555-39.14995 45.251241-25.422046 23.896723q-10.168818 9.151936-18.812314 13.727905t-15.253227 7.626614-12.711023 7.118173-12.202582 13.219464q-13.219464 19.320755-20.337637 37.624628t-12.202582 35.590864q-5.084409 14.236346-11.1857 23.388282t-13.219464 16.270109q-8.135055 8.135055-16.270109 13.219464l-223.714002 0q-8.135055-5.084409-15.253227-13.219464-7.118173-7.118173-14.236346-18.303873t-12.202582-28.472691q-10.168818-29.489573-24.913605-47.285005t-38.133069-35.082423q-16.270109-12.202582-37.116187-32.540218t-41.183714-47.793446-38.641509-61.521351-29.489573-74.740814-13.219464-86.943396 9.151936-97.112214q17.286991-81.350546 59.996028-136.770606t95.586892-88.97716 109.314796-48.301887 102.196624-14.744786q47.793446 0 99.654419 13.219464t100.16286 41.183714 88.468719 71.181728 65.588878 104.230387zM760.119166 437.259186q43.725919-177.95432-113.890765-271.507448-26.438928-16.270109-61.521351-25.422046t-71.690169-9.151936-72.707051 9.151936-64.571996 28.472691q-69.147964 47.793446-93.553128 103.721946t-22.3714 117.958292q1.016882 34.573982 11.694141 62.029791t25.422046 49.82721 30.506455 39.14995 27.96425 29.998014q25.422046 26.438928 44.7428 46.268123t30.506455 50.33565q11.1857 29.489573 35.082423 36.099305t44.234359 6.609732q26.438928 0 50.844091-11.694141t34.573982-36.099305q5.084409-14.236346 20.846077-34.573982t47.285005-56.945382q16.270109-19.320755 31.014896-33.5571t27.455809-28.472691 22.3714-31.014896 15.761668-41.183714z" fill="#0ea5e9"></path></svg></span> 
              AI 诊断与建议
            </h2>
            <div class="suggestion-list">
              <div class="suggestion-item" v-for="(suggestion, index) in suggestions" :key="index">
                <h3>{{ index + 1 }}. {{ suggestion.title }}</h3>
                <p>{{ suggestion.description }}</p>
              </div>
            </div>

          </section>

          <section class="practice-plan">
            <div class="plan-header">
              <h2>
                <span class="icon"><svg t="1773233567401" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7186" width="200" height="200"><path d="M254.976 448.512q27.648 0 47.104 19.456t19.456 47.104q0 26.624-19.456 46.592t-47.104 19.968-47.104-19.968-19.456-46.592q0-27.648 19.456-47.104t47.104-19.456zM771.072 66.56q45.056 0 79.872 15.872t58.88 40.96 36.864 56.832 12.8 62.464l0 523.264q0 23.552-10.752 46.08t-28.672 40.96-40.96 29.696-47.616 11.264l0-572.416q0-26.624-10.24-49.664t-27.648-40.448-40.448-27.648-49.664-10.24l-575.488 0q0-22.528 10.24-45.056t27.648-40.96 40.96-29.696 50.176-11.264l514.048 0zM681.984 258.048q46.08 0 65.536 25.088t19.456 67.072l0 603.136q0 25.6-21.504 48.128t-54.272 22.528l-620.544 0q-27.648 0-49.152-22.528t-21.504-54.272l0-614.4q0-32.768 17.92-53.76t47.616-20.992l616.448 0zM640 413.696q0-11.264-7.168-18.432t-18.432-7.168l-461.824 0q-11.264 0-18.432 7.168t-7.168 18.432l0 228.352q9.216 11.264 16.896 25.088t18.944 26.112 29.696 20.992 51.2 8.704q48.128 0 78.336-15.36t53.248-38.912 43.008-50.688 47.616-51.2 68.608-40.96 105.472-18.944l0-93.184z" fill="#0ea5e9"></path></svg></span> 
                7 天专属突击计划 
              </h2>
              <div class="main-focus-badge">
                （核心攻克：{{ weakPoint }}）
              </div>
            </div>

            <div class="plan-list">
              <div class="plan-item" v-for="(item, index) in planData" :key="index">
                <div class="plan-day">第 {{ item.day }} 天</div>
                <div class="plan-content">
                  <h4>{{ item.title }}</h4>
                  
                  <template v-if="item.action || item.focus">
                    <div class="plan-detail-row" v-if="item.action">
                      <span class="tag-badge action-badge">行动</span>
                      <p class="detail-text">{{ item.action }}</p>
                    </div>
                    <div class="plan-detail-row mt-2" v-if="item.focus">
                      <span class="tag-badge focus-badge">重点</span>
                      <p class="detail-text">{{ item.focus }}</p>
                    </div>
                  </template>
                  
                  <p v-else class="detail-text">{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </section>
        </template>
        
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getHistoryReports } from '@/api/interview'

const radarChart = ref(null)

const isLoading = ref(true)
const hasHistory = ref(false)

const radarData = ref([])
const weakPoint = ref('')
const suggestions = ref([])
const planData = ref([])
const summary = ref('')

const processHistoryData = async () => {
  try {
    const res = await getHistoryReports()
    if (!res.reports || res.reports.length === 0) {
      hasHistory.value = false
      isLoading.value = false
      return
    }

    hasHistory.value = true
    const dimensionSums = {}
    const dimensionCounts = {}

    // 1. 动态渲染雷达图数据（保持雷达图逻辑不动）
    res.reports.forEach(report => {
      let content = {}
      try { content = typeof report.content === 'string' ? JSON.parse(report.content) : (report.content || {}) } catch (e) {}
      if (content.radar_packet && content.radar_packet.data) {
        content.radar_packet.data.forEach(d => {
          if (!dimensionSums[d.name]) {
            dimensionSums[d.name] = 0; dimensionCounts[d.name] = 0;
          }
          dimensionSums[d.name] += d.value; dimensionCounts[d.name] += 1;
        })
      }
    })

    if (Object.keys(dimensionSums).length > 0) {
      const averages = []
      for (const [name, sum] of Object.entries(dimensionSums)) {
        averages.push({ name, value: Math.round(sum / dimensionCounts[name]) })
      }
      radarData.value = averages
    }

    // ==========================================
    // 🔴 静态数据完美注入（按照用户给定的内容排版）
    // ==========================================
    
    // 核心短板
    weakPoint.value = "底层原理深度与高压表达";
    
    // 总结
    summary.value = "候选人具备优秀的架构设计能力和业务场景适配能力，但需在底层原理深度和高压表达上重点突破。通过针对性训练，有望在阿里技术面试中脱颖而出。";

    // 面试提升建议
    suggestions.value = [
      { 
        title: "强化底层原理深度", 
        description: "重点恶补Seata AT模式的undo_log实现、RocketMQ事务消息的回查机制源码，避免“描述性回答”。" 
      },
      { 
        title: "提升场景化设计能力", 
        description: "在架构方案中增加“极端场景兜底”（如undo_log膨胀、幂等性失效），体现工程化思维。" 
      },
      { 
        title: "优化高压表达结构", 
        description: "采用“结论先行+分点阐述+案例佐证”的表达方式，避免被追问时逻辑混乱。" 
      }
    ];

    // 后续学习计划 (拆分为行动与重点)
    planData.value = [
      {
        day: "1-2",
        title: "底层原理深度突破",
        action: "精读Seata官方文档中AT模式的实现细节（undo_log表结构、脏写校验逻辑），结合实际项目数据分析undo_log膨胀影响；研究RocketMQ事务消息的源码。",
        focus: "手动模拟Seata AT的全流程（准备、提交、回滚），用伪代码还原undo_log的生成与清理；总结RocketMQ回查失败时的兜底策略。",
        desc: ""
      },
      {
        day: "3-4",
        title: "场景化方案强化",
        action: "针对“AI增值服务”场景，设计一份包含“undo_log清理+幂等性兜底”的完整方案，并量化性能指标；撰写一篇技术博客对比优劣。",
        focus: "模拟面试中刻意加入“边界条件提问”（如“MQ消息重复消费如何处理？”），训练“临场拆解问题”的能力。",
        desc: ""
      },
      {
        day: "5-7",
        title: "高压表达训练",
        action: "录制回答视频，重点观察“停顿次数”“语速稳定性”，并针对高频卡壳问题（如undo_log膨胀）反复练习。",
        focus: "在模拟面试中，针对“底层原理”问题采用“结论先行+分点阐述+案例佐证”的结构回答；准备3个“极端场景兜底”案例以保逻辑清晰。",
        desc: ""
      }
    ];

    isLoading.value = false
    nextTick(() => { initRadarChart() })

  } catch (error) {
    console.error("加载数据失败", error)
    isLoading.value = false
  }
}

// Echarts 渲染逻辑
const initRadarChart = () => {
  if (!radarChart.value) return
  const chart = echarts.init(radarChart.value)
  const option = {
    tooltip: { trigger: 'item' },
    radar: {
      name: { textStyle: { color: '#64748b', fontSize: 13, fontWeight: 'normal' } },
      indicator: radarData.value.map(item => ({ name: item.name, max: 100 })),
      radius: '65%', center: ['50%', '55%']
    },
    series: [{
      name: '全局平均能力', type: 'radar',
      areaStyle: { opacity: 0.4, color: '#6ec0e3' },
      itemStyle: { color: '#6ec0e3', borderColor: '#6ec0e3', borderWidth: 2 },
      lineStyle: { color: '#6ec0e3', width: 2 },
      data: [{ value: radarData.value.map(item => item.value), name: '平均得分' }]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => { chart.resize() })
}

onMounted(() => {
  processHistoryData()
})
</script>

<style scoped>
.container { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 20px; margin-top: 80px; }
.main-content { padding: 40px 0; background: #f8fafc; min-height: calc(100vh - 80px); }
.result-overview { width: 100%; margin-bottom: 40px; }
.result-charts { display: flex; gap: 20px; flex-wrap: wrap; }
.chart-container { flex: 1; background-color: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); min-width: 300px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.result-cards-left{ font-size: 25px; font-weight: bold; color: #2c3e50; }
.chart-and-details { display: flex; gap: 20px; align-items: center; }
.radar-chart { height: 350px; width: 60%; min-width: 300px; }
.score-details { flex: 1; min-width: 200px; }
.score-item { display: flex; justify-content: space-between; padding: 10px 0; margin: 35px 0; border-bottom: 1px solid #eee; }
.score-label { font-size: 18px; color: #64748b; }
.score-value { font-size: 20px; font-weight: bold; color: #6ec0e3; }
.suggestions { margin-bottom: 40px; }
.suggestions h2 { font-size: 28px; color: #2c3e50; margin-bottom: 24px; display: flex; align-items: center; gap: 10px; }
.suggestion-list { display: flex; flex-direction: column; gap: 20px; }
.suggestion-item { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); }
.suggestion-item h3 { font-size: 20px; color: #2c3e50; margin-bottom: 12px; }
.suggestion-item p { font-size: 16px; color: #64748b; line-height: 1.6; }
.practice-plan h2 { font-size: 28px; color: #2c3e50; margin-bottom: 0; display: flex; align-items: center; gap: 10px; }
.plan-list { display: flex; flex-direction: column; gap: 16px; }
.plan-item { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); display: flex; gap: 20px; align-items: flex-start; }
.plan-day { background: #6ec0e3; color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; white-space: nowrap; }
.plan-content h4 { font-size: 18px; color: #2c3e50; margin-bottom: 8px; }
.plan-content p { font-size: 14px; color: #64748b; line-height: 1.5; }
.icon { width: 30px; height: 30px; text-align: center; }

/* 1. 状态提示框 (加载中 / 空数据) */
.status-container {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  color: #64748b;
  font-size: 16px;
  border: 1px dashed #e2e8f0;
}

/* 2. 标题与 Tag 排列 */
.plan-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

/* 3. 靶向目标徽章 */
.focus-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #0369a1;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.mt-2 { margin-top: 8px; }

.plan-detail-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

/* 标签通用基类 */
.tag-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  margin-top: 2px; 
}

.main-focus-badge {
  color: #0284c7;
}

/* 行动标签：清爽冰蓝 */
.action-badge {
  background-color: #e0f2fe;
  color: #0284c7;
  border: 1px solid #bae6fd;
}

/* 重点标签：警示琥珀黄 */
.focus-badge {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

/* 右侧具体内容文本 */
.detail-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
  flex: 1;
}
</style>