<template>
  <div class="page-shell">
    <section class="ai-banner">
      <div class="ai-banner-bg-blob blob-left"></div>
      <div class="ai-banner-bg-blob blob-right"></div>

      <div class="ai-banner-inner">
        <!-- 左侧文案区 -->
        <div class="ai-banner-left">
          <div class="ai-banner-pill">
            <span class="dot"></span>
            {{ bannerData.pillText }}
          </div>
          <h1 class="ai-banner-title">
            <span v-html="formatTitle(bannerData.title)"></span>
          </h1>
          <p class="ai-banner-sub">
            {{ bannerData.subtitle }}
          </p>
          <div class="ai-banner-cta-row">
            <button
              class="ai-banner-primary-btn"
              type="button"
              @click="handlePrimaryClick"
            >
              {{ bannerData.primaryBtn }}
            </button>
            <button
              class="ai-banner-secondary-btn"
              type="button"
              @click="handleSecondaryClick"
            >
              {{ bannerData.secondaryBtn }}
            </button>
          </div>
          <div class="ai-banner-meta">
            <div class="meta-item">
              <span class="meta-label">{{ bannerData.meta.label1 }}</span>
              <span class="meta-value">{{ bannerData.meta.value1 }}</span>
            </div>
            <div class="meta-divider"></div>
            <div class="meta-item">
              <span class="meta-label">{{ bannerData.meta.label2 }}</span>
              <span class="meta-value">{{ bannerData.meta.value2 }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧创意视觉区 -->
        <div class="ai-banner-right">
          <!-- 模拟对话卡片 -->
          <div class="ai-card chat-card interviewer">
            <div class="chat-tag">{{ chatData.interviewer.tag }}</div>
            <p class="chat-text">
              {{ chatData.interviewer.text }}
            </p>
            <span class="chat-meta">{{ chatData.interviewer.meta }}</span>
          </div>

          <div class="ai-card chat-card candidate">
            <div class="chat-avatar">{{ chatData.candidate.avatar }}</div>
            <p class="chat-text">
              {{ chatData.candidate.text }}
            </p>
          </div>

          <!-- 漂浮评分卡 -->
          <div class="ai-card score-card">
            <div class="score-header">
              <span class="score-label">{{ scoreData.label }}</span>
              <span class="score-value">{{ scoreData.total }}</span>
            </div>
            <div
              v-for="(item, index) in scoreData.items"
              :key="index"
              class="score-bar-row"
            >
              <span class="score-bar-label">{{ item.label }}</span>
              <div class="score-bar-track">
                <div
                  class="score-bar-fill"
                  :class="{ soft: item.soft }"
                  :style="{ width: item.percentage + '%' }"
                ></div>
              </div>
            </div>
            <div class="score-tag-row">
              <span
                v-for="(tag, index) in scoreData.tags"
                :key="index"
                class="score-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 右上角小胶囊统计 -->
          <div class="ai-card stat-chip">
            <span class="stat-dot"></span>
            <div class="stat-text" v-html="formatStatText(statData)"></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// Banner 数据
const bannerData = ref({
  pillText: "AI 模拟面试 · 帮你提前适应真实战场",
  title: "用一场温柔而犀利的\nAI 面试，发现你的下一步提升",
  subtitle:
    "低压却不低质的面试演练：模拟真实面试官的提问节奏、追问方式与评分标准，在安全环境中暴露问题、打磨表达。",
  primaryBtn: "立即开始 20 分钟快速体验",
  secondaryBtn: "查看典型题目示例",
  meta: {
    label1: "支持岗位",
    value1: "前端 / 后端 / 算法 / 产品",
    label2: "平均练习时长",
    value2: "每轮约 30 分钟",
  },
});

// 对话数据
const chatData = ref({
  interviewer: {
    tag: "AI 面试官",
    text: "如果让你设计一个可复用的「筛选面板」组件，你会如何划分状态和职责？",
    meta: "技术深度 · 预计回答 2 分钟",
  },
  candidate: {
    avatar: "你",
    text: "我会先拆分出一个容器组件和若干基础输入组件，并将核心筛选状态提升到上层管理……",
  },
});

// 评分数据
const scoreData = ref({
  label: "本题评分（示例）",
  total: "84 / 100",
  items: [
    { label: "技术深度", percentage: 78, soft: false },
    { label: "表达结构", percentage: 88, soft: true },
  ],
  tags: ["拆分合理", "可补充更多边界情况"],
});

// 统计数据
const statData = ref({
  count: 3,
  message: "下次自动生成更贴合你的题目",
});

// 格式化标题（支持高亮）
const formatTitle = (text) => {
  // 修复：替换换行符并高亮特定文字
  let formatted = text.replace(/\n/g, "<br />");
  formatted = formatted.replace(/温柔而犀利/, '<span class="highlighted-text">温柔而犀利</span>');
  return formatted;
};

// 格式化统计文本
const formatStatText = (data) => {
  return `已完成 <strong> ${data.count} 轮 </strong> 模拟面试<br />${data.message}`;
};

// 按钮点击处理
const handlePrimaryClick = () => {
  console.log("开始快速体验");
  alert("开始 20 分钟快速体验！");
  // 这里可以跳转到配置页面或面试页面
  // window.location.href = '/interview-config';
};

const handleSecondaryClick = () => {
  console.log("查看题目示例");
  alert("查看典型题目示例");
  // 这里可以显示题目示例弹窗或跳转
};

// 组件挂载后的动画效果
onMounted(() => {
  // 可以在这里添加一些动画效果
  console.log("Banner 页面已加载");
});
</script>

<style scoped>
:root {
  --blue-soft: #e0f2ff;
  --blue-main: #bae6fd;
  --blue-accent: #38bdf8;
  --indigo-soft: #c7d2fe;
  --indigo-accent: #818cf8;
  --mint-soft: #99f6e4;
  --text-main: #0f172a;
  --text-muted: #4b5563;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.page-shell {
  width: 100%;
  max-width: 1120px;
}

/* AI 模拟面试 Banner 开始 */
.ai-banner {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 28px 30px;
  background: radial-gradient(circle at 0% 0%, #e0f2ff 0, #f4f7ff 42%, #ebf3ff 100%);
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 22px 55px rgba(148, 163, 184, 0.35);
  color: var(--text-main);
}

/* 背景柔和马卡龙色块 */
.ai-banner-bg-blob {
  position: absolute;
  border-radius: 999px;
  filter: blur(26px);
  opacity: 0.7;
  pointer-events: none;
  mix-blend-mode: multiply;
}

.ai-banner-bg-blob.blob-left {
  width: 280px;
  height: 280px;
  left: -80px;
  bottom: -80px;
  background: radial-gradient(circle at 30% 30%, #c7e3ff, #a5d8ff, var(--mint-soft));
}

.ai-banner-bg-blob.blob-right {
  width: 320px;
  height: 320px;
  right: -60px;
  top: -120px;
  background: radial-gradient(circle at 40% 40%, #d1c4ff, var(--indigo-soft), #bae6fd);
}

.ai-banner-inner {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.1fr);
  gap: 28px;
  z-index: 1;
}

/* 左侧文案区 */
.ai-banner-left {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ai-banner-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.5);
  font-size: 12px;
  color: #334155;
}

.ai-banner-pill .dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, var(--blue-accent), #0ea5e9);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.9);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.ai-banner-title {
  font-size: 26px;
  line-height: 1.35;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--text-main);
}

.ai-banner-title span {
  background: linear-gradient(120deg, var(--blue-accent), var(--indigo-accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* 添加高亮文字样式 */
.ai-banner-title .highlighted-text {
  background: linear-gradient(120deg, var(--blue-accent), var(--indigo-accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.ai-banner-sub {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-muted);
  max-width: 36rem;
}

.ai-banner-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
}

.ai-banner-primary-btn,
.ai-banner-secondary-btn {
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  outline: none;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.ai-banner-primary-btn {
  background: linear-gradient(135deg, var(--blue-accent), var(--indigo-accent));
  color: #f9fafb;
  box-shadow: 0 14px 30px rgba(59, 130, 246, 0.35);
}

.ai-banner-primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 35px rgba(59, 130, 246, 0.45);
}

.ai-banner-primary-btn:active {
  transform: translateY(0);
}

.ai-banner-secondary-btn {
  background: rgba(255, 255, 255, 0.85);
  color: #1e293b;
  border: 1px solid rgba(148, 163, 184, 0.6);
}

.ai-banner-secondary-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--blue-accent);
  transform: translateY(-1px);
}

.ai-banner-meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.4);
  font-size: 11px;
  color: #6b7280;
  margin-top: 4px;
}

.ai-banner-meta .meta-item {
  display: flex;
  flex-direction: column;
}

.ai-banner-meta .meta-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 10px;
}

.ai-banner-meta .meta-value {
  font-weight: 500;
  color: #1f2933;
}

.ai-banner-meta .meta-divider {
  width: 1px;
  height: 26px;
  background: rgba(148, 163, 184, 0.5);
}

/* 右侧创意视觉区 */
.ai-banner-right {
  position: relative;
  min-height: 220px;
}

/* 公共卡片样式 */
.ai-card {
  position: absolute;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 16px 35px rgba(148, 163, 184, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.35);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ai-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px rgba(148, 163, 184, 0.5);
}

/* 对话卡片 */
.chat-card {
  max-width: 280px;
  padding: 10px 12px 9px;
  font-size: 12px;
  color: #1f2937;
}

.chat-card.interviewer {
  top: 4px;
  left: 6%;
}

.chat-card.candidate {
  bottom: 6px;
  right: 12%;
  background: rgba(240, 249, 255, 0.96);
}

.chat-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(219, 234, 254, 0.95);
  color: #1d4ed8;
  font-size: 10px;
  font-weight: 500;
  margin-bottom: 5px;
}

.chat-text {
  line-height: 1.6;
}

.chat-meta {
  font-size: 10px;
  color: #6b7280;
  margin-top: 4px;
}

.chat-avatar {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: linear-gradient(135deg, #bae6fd, #a5b4fc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 5px;
}

/* 评分卡片 */
.score-card {
  right: 0;
  top: 40%;
  transform: translateY(-50%);
  width: 210px;
  padding: 10px 11px 9px;
  font-size: 11px;
  color: var(--text-main);
  background: rgba(252, 252, 255, 0.98);
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.score-label {
  font-size: 10px;
  color: #6b7280;
}

.score-value {
  font-weight: 600;
  color: #2563eb;
}

.score-bar-row {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px;
  align-items: center;
  margin-bottom: 4px;
}

.score-bar-label {
  font-size: 10px;
  color: #6b7280;
}

.score-bar-track {
  height: 5px;
  border-radius: 999px;
  background: #e5edff;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--blue-accent), var(--indigo-accent));
  transition: width 0.6s ease;
}

.score-bar-fill.soft {
  background: linear-gradient(90deg, #6ee7b7, var(--blue-accent));
}

.score-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.score-tag {
  padding: 2px 6px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #1d4ed8;
  font-size: 10px;
}

/* 右上角统计胶囊 */
.stat-chip {
  top: -4px;
  right: 8%;
  border-radius: 999px;
  padding: 6px 10px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 10px;
  max-width: 220px;
}

.stat-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #4ade80, #22c55e);
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.9);
  animation: pulse 2s ease-in-out infinite;
}

.stat-text strong {
  color: #2563eb;
}

/* 响应式适配 */
@media (max-width: 960px) {
  .ai-banner-inner {
    grid-template-columns: minmax(0, 1fr);
    gap: 20px;
  }

  .ai-banner-right {
    min-height: 230px;
  }

  .ai-card.chat-card.interviewer {
    top: 0;
    left: 4%;
  }

  .ai-card.chat-card.candidate {
    bottom: 0;
    right: 10%;
  }

  .score-card {
    top: 52%;
    right: 6%;
  }
}

@media (max-width: 640px) {
  .ai-banner {
    padding: 20px 16px;
    border-radius: 18px;
  }

  .ai-banner-title {
    font-size: 22px;
  }

  .ai-banner-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .ai-banner-meta .meta-divider {
    display: none;
  }

  .ai-banner-right {
    min-height: 220px;
  }

  .ai-card {
    transform: none !important;
  }

  .stat-chip {
    right: 6%;
  }
}
</style>