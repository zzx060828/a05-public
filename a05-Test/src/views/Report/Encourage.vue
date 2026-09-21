<template>
  <div class="interview-tips">
    <div class="tips-layout">
      <div class="tips-column">
        <h3 class="column-title">
          <span class="icon"><svg t="1773233549553" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4981" width="200" height="200"><path d="M642.160874 894.856008l0 11.1857q0 5.084409 0.508441 11.1857t0.508441 12.202582q-1.016882 19.320755-10.677259 42.200596t-37.116187 33.048659q-11.1857 4.067527-28.981132 11.694141t-53.386296 7.626614q-30.506455 0-50.33565-7.118173t-31.014896-9.151936q-14.236346-3.050645-22.879841-12.711023t-13.219464-21.862959-5.59285-24.913605-1.016882-22.879841l0-31.523337zM862.82423 229.815293q26.438928 62.029791 30.506455 116.94141t-6.101291 101.179742-29.489573 82.875869-40.166832 64.063555-39.14995 45.251241-25.422046 23.896723q-10.168818 9.151936-18.812314 13.727905t-15.253227 7.626614-12.711023 7.118173-12.202582 13.219464q-13.219464 19.320755-20.337637 37.624628t-12.202582 35.590864q-5.084409 14.236346-11.1857 23.388282t-13.219464 16.270109q-8.135055 8.135055-16.270109 13.219464l-223.714002 0q-8.135055-5.084409-15.253227-13.219464-7.118173-7.118173-14.236346-18.303873t-12.202582-28.472691q-10.168818-29.489573-24.913605-47.285005t-38.133069-35.082423q-16.270109-12.202582-37.116187-32.540218t-41.183714-47.793446-38.641509-61.521351-29.489573-74.740814-13.219464-86.943396 9.151936-97.112214q17.286991-81.350546 59.996028-136.770606t95.586892-88.97716 109.314796-48.301887 102.196624-14.744786q47.793446 0 99.654419 13.219464t100.16286 41.183714 88.468719 71.181728 65.588878 104.230387zM760.119166 437.259186q43.725919-177.95432-113.890765-271.507448-26.438928-16.270109-61.521351-25.422046t-71.690169-9.151936-72.707051 9.151936-64.571996 28.472691q-69.147964 47.793446-93.553128 103.721946t-22.3714 117.958292q1.016882 34.573982 11.694141 62.029791t25.422046 49.82721 30.506455 39.14995 27.96425 29.998014q25.422046 26.438928 44.7428 46.268123t30.506455 50.33565q11.1857 29.489573 35.082423 36.099305t44.234359 6.609732q26.438928 0 50.844091-11.694141t34.573982-36.099305q5.084409-14.236346 20.846077-34.573982t47.285005-56.945382q16.270109-19.320755 31.014896-33.5571t27.455809-28.472691 22.3714-31.014896 15.761668-41.183714z" fill="#333"></path></svg></span>  
          面试提升建议</h3>
        <div class="advice-content">
          <div class="tips-list">
            <div 
              class="tips-item" 
              v-for="(tip, index) in suggestions" 
              :key="'suggest-' + index"
            >
              <span class="tips-icon">
                <svg t="1774698282118" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8009" width="200" height="200"><path d="M886.4 240c-12.8-12.8-32-12.8-44.8 0L364.8 716.8l-182.4-182.4c-12.8-12.8-32-12.8-44.8 0-12.8 12.8-12.8 32 0 44.8l204.8 204.8c6.4 6.4 12.8 9.6 22.4 9.6 9.6 0 16-3.2 22.4-9.6L886.4 284.8c12.8-12.8 12.8-32 0-44.8z" fill="#333" p-id="8010"></path></svg>
              </span>
              <span class="tips-content">{{ tip }}</span>
            </div>

            <div v-if="!suggestions || suggestions.length === 0" class="empty-tip">
              AI 正在为您生成专属提升建议...
            </div>
          </div>
        </div>
      </div>

      <div class="tips-column">
        <h3 class="column-title">
          <span class="icon"><svg t="1773233567401" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7186" width="200" height="200"><path d="M254.976 448.512q27.648 0 47.104 19.456t19.456 47.104q0 26.624-19.456 46.592t-47.104 19.968-47.104-19.968-19.456-46.592q0-27.648 19.456-47.104t47.104-19.456zM771.072 66.56q45.056 0 79.872 15.872t58.88 40.96 36.864 56.832 12.8 62.464l0 523.264q0 23.552-10.752 46.08t-28.672 40.96-40.96 29.696-47.616 11.264l0-572.416q0-26.624-10.24-49.664t-27.648-40.448-40.448-27.648-49.664-10.24l-575.488 0q0-22.528 10.24-45.056t27.648-40.96 40.96-29.696 50.176-11.264l514.048 0zM681.984 258.048q46.08 0 65.536 25.088t19.456 67.072l0 603.136q0 25.6-21.504 48.128t-54.272 22.528l-620.544 0q-27.648 0-49.152-22.528t-21.504-54.272l0-614.4q0-32.768 17.92-53.76t47.616-20.992l616.448 0zM640 413.696q0-11.264-7.168-18.432t-18.432-7.168l-461.824 0q-11.264 0-18.432 7.168t-7.168 18.432l0 228.352q9.216 11.264 16.896 25.088t18.944 26.112 29.696 20.992 51.2 8.704q48.128 0 78.336-15.36t53.248-38.912 43.008-50.688 47.616-51.2 68.608-40.96 105.472-18.944l0-93.184z" fill="#333"></path></svg></span> 
           后续学习计划</h3>
        <div class="advice-content">
          <div class="tips-list">
  <div 
    v-for="(plan, index) in plans" 
    :key="'plan-' + index"
    class="tips-item" 
    :class="{ 
      'stage-title': plan.includes('阶段'), 
      'action-task': !plan.includes('阶段') 
    }"
  >
    <span class="tips-icon" v-if="!plan.includes('阶段')">
      <svg t="1774698282118" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8009" width="200" height="200"><path d="M886.4 240c-12.8-12.8-32-12.8-44.8 0L364.8 716.8l-182.4-182.4c-12.8-12.8-32-12.8-44.8 0-12.8 12.8-12.8 32 0 44.8l204.8 204.8c6.4 6.4 12.8 9.6 22.4 9.6 9.6 0 16-3.2 22.4-9.6L886.4 284.8c12.8-12.8 12.8-32 0-44.8z" fill="#140304" p-id="8010"></path></svg>
    </span>
    

    <span class="tips-content">{{ plan }}</span>
  </div>

  <div v-if="!plans || plans.length === 0" class="empty-tip">
    AI 正在为您规划后续学习路径...
  </div>
</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 🔴 接收来自父组件的数据，分为建议和计划两个数组
defineProps({
  suggestions: {
    type: Array,
    default: () => []
  },
  plans: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
/* ====== 极简线框风：细黑边框 + 充足留白 ====== */

.tips-layout {
  display: flex;
  flex-direction: column;
  grid-template-columns: 1fr 1fr; 
  gap: 40px; /* 🌟 边框外侧留白：加大了左右两栏的间距 */
  margin: 0 40px; /* 🌟 边框外侧留白：距离页面边缘的距离 */
  align-items: start; /* 🌟 保持顶部对齐，绝不强制拉伸高度，让底部自然留白 */
}

.tips-column {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.column-title {
  display: flex; /* 🌟 开启 flex 布局 */
  align-items: center; /* 🌟 保证 icon 和文字垂直居中对齐 */
  gap: 10px; /* 🌟 图标和文字之间的间距 */
  font-size: 18px;
  color: #333; 
  margin: 0 0 16px 4px;
  font-weight: 600;
}

.advice-content {
  background: #ffffff; /* 🌟 纯白背景，告别灰蓝 */
  border-radius: 12px;
  padding: 24px 32px; /* 🌟 边框内侧留白：左右加宽到 32px，文字不贴边 */
  border: 1px solid #333; /* 🌟 细黑边框，干净利落 */
}

/* 建议列表 */
.tips-list {
  display: flex;
  flex-direction: column;
  gap: 8px; 
}

/* 单个建议项 */
.tips-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 14.5px;
  color: #444; /* 文字颜色稍微调深，压得住纯白底色 */
  line-height: 1.7;
  padding: 12px 0; 
  border-bottom: 1px dashed #e0e0e0; /* 极淡的虚线分割，不喧宾夺主 */
}
.tips-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* 建议图标 */
.tips-icon {
  margin-top: 4px;
  flex-shrink: 0;
}

/* 建议内容 */
.tips-content {
  flex: 1;
}

.icon {
  width: 15px;
  height: 15px;
}

.empty-tip {
  color: #999;
  text-align: center;
  padding: 30px 0;
  font-size: 14px;
}
.column-title .icon {
  display: inline-flex; /* 消除 span 默认的行高空白 */
  align-items: center;
  justify-content: center;
  width: 22px; /* 适当控制包裹体大小 */
  height: 22px;
}

/* 🌟 直接修改 SVG 标签的颜色 */
.column-title svg {
  width: 20px;
  height: 20px;
  fill: #333; 
}

/* ================= 进阶：学习计划层级化样式 ================= */

/* 1. 阶段大标题样式：色块化、加粗、顶开间距 */
.tips-item.stage-title {
  border-left: 4px solid #43C9E2; /* 面伴主题色：左侧高亮竖线 */
  border-bottom: none; /* 去掉下划虚线 */
  padding: 3px 16px;
  margin-top: 24px; /* 距离上一个阶段拉开很大距离 */
  border-radius: 0 8px 8px 0;
  
  font-weight: 600;
  font-size: 15.5px;
  color: #164a81; /* 深蓝色文字 */
  align-items: center;
}

/* 第一个阶段不需要太大的顶部间距 */
.tips-item.stage-title:first-child {
  margin-top: 0;
}

/* 阶段标题前面的 Emoji 靶心微调 */
.stage-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 2. 具体行动任务样式：向右缩进、弱化颜色 */
.tips-item.action-task {
  margin-left: 20px; /* 🌟 关键：向右缩进，体现包含关系 */
  padding-left: 10px;
  color: #4b5563;
  font-size: 14px;
}

  </style>

