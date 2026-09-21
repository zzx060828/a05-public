<template>
  <div class="content-section">
    <div 
      v-for="(item, index) in evaluations" 
      :key="index"
      class="question-card"
    >
      <div class="question-header" @click="toggleExpand(index)">
        <h3 :class="{ 'low-score': item.score < 75 }">
          问题 {{ index + 1 }}：{{ item.question }}
          <span class="inline-score-badge" :class="item.score < 75 ? 'badge-danger' : 'badge-safe'">
            {{ item.score }} 分
          </span>
        </h3>
        <div class="toggle-btn" :class="{ 'rotate': expandedSet.has(index) }">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>

      <transition name="expand">
        <div class="question-body" v-show="expandedSet.has(index)">
          <div class="body-inner">
            
            <div class="block analysis">
              <h4>问题解析</h4>
              <div class="parsed-analysis">
                <template v-if="getParsedAnalysis(item.analysis).isObject">
                  <p v-if="getParsedAnalysis(item.analysis).highlight">
                    <strong class="icon-text-row">
                      <svg t="1774697828515" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4711" width="200" height="200"><path d="M512 64c247.136 0 448 200.864 448 448s-200.864 448-448 448S64 759.136 64 512 264.864 64 512 64z m0 832c211.968 0 384-172.032 384-384S723.968 128 512 128 128 300.032 128 512s172.032 384 384 384z m96-480a64 64 0 1 1 128 0 64 64 0 0 1-128 0zM288 416a64 64 0 1 1 128 0 64 64 0 0 1-128 0z m407.68 170.848c17.184 11.2 22.4 34.336 11.2 51.52A229.44 229.44 0 0 1 512 745.152a229.44 229.44 0 0 1-194.88-106.784 37.408 37.408 0 0 1 11.2-51.52 37.408 37.408 0 0 1 51.52 11.2A155.904 155.904 0 0 0 512 670.464c53.76 0 103.04-26.88 132.16-72.416 11.2-17.184 34.336-22.4 51.52-11.2z" fill="#000000" p-id="4712"></path></svg>
                      亮点：
                    </strong><br>
                    {{ getParsedAnalysis(item.analysis).highlight }}
                  </p>
                  <p v-if="getParsedAnalysis(item.analysis).weakness">
                    <strong class="icon-text-row">
                      <svg t="1774697871159" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4866" width="200" height="200"><path d="M512 64c247.136 0 448 200.864 448 448s-200.864 448-448 448S64 759.136 64 512 264.864 64 512 64z m0 832c211.968 0 384-172.032 384-384S723.968 128 512 128 128 300.032 128 512s172.032 384 384 384z m96-480a64 64 0 1 1 128 0 64 64 0 0 1-128 0zM288 416a64 64 0 1 1 128 0 64 64 0 0 1-128 0z m407.68 323.2c-17.184 11.2-40.32 5.984-51.52-11.2A155.904 155.904 0 0 0 512 655.616c-53.76 0-103.04 26.88-132.16 72.448-11.2 17.152-34.336 22.4-51.52 11.2a37.408 37.408 0 0 1-11.2-51.52A229.44 229.44 0 0 1 512 580.928a229.44 229.44 0 0 1 194.88 106.784c11.2 17.152 5.984 40.32-11.2 51.52z" fill="#000000" p-id="4867"></path></svg> 
                      不足：
                    </strong><br>
                    {{ getParsedAnalysis(item.analysis).weakness }}
                  </p>
                </template>
                <p v-else>{{ getParsedAnalysis(item.analysis).raw }}</p>
              </div>
            </div>

            <div class="block reference" v-if="item.referenceAnswer">
              <h4>参考答案</h4>
              <p>{{ item.referenceAnswer }}</p>
            </div>

            <div class="block answer">
              <h4>你的回答</h4>
              <p>{{ item.userAnswer || '未提取到有效回答' }}</p>
            </div>

            <div class="block feedback">
              <h4>评估反馈</h4>
              <p>{{ item.feedback || '暂无反馈' }}</p>
            </div>

            <div v-if="item.score < 85 && item.resource" class="resource-cta-card">
              <div class="cta-header">
                <div class="cta-title">
                  <span>发现知识盲区，已为您生成攻坚资料</span>
                </div>
                <div class="cta-score">本题仅得 <strong class="text-red">{{ item.score }}</strong> 分</div>
              </div>
              
              <div class="cta-body">
                <p class="cta-excerpt">{{ getExcerpt(item.resource) }}</p>
                
                <button class="btn-jump-plan" @click="goToLearningPath">
                  前往 [ 记录 ] -学习资源查阅完整资料
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </button>
              </div>
            </div>

          </div> </div> </transition>
    </div> </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // 👈 1. 确保引入了 useRouter
import { useRoute } from 'vue-router'; // 🌟 1. 确保引入了 useRoute

const route = useRoute();
const router = useRouter(); //
const props = defineProps({
  evaluations: {
    type: Array,
    default: () => []
  }
});

// 🔴 记录哪些问题被展开了 (默认全都收起)
const expandedSet = ref(new Set());

// 点击展开/收起问题逻辑
const toggleExpand = (index) => {
  if (expandedSet.value.has(index)) {
    expandedSet.value.delete(index); // 收起
  } else {
    expandedSet.value.add(index);    // 展开
  }
};

// 🔴 智能解析 analysis，消灭 JSON 字符串，分离亮点与不足
const getParsedAnalysis = (analysisData) => {
  if (!analysisData) return { isObject: false, raw: "暂无解析" };
  
  if (typeof analysisData === 'object') {
    return {
      isObject: true,
      highlight: analysisData.highlight || '',
      weakness: analysisData.weakness || ''
    };
  }
  
  try {
    const obj = JSON.parse(analysisData);
    return {
      isObject: true,
      highlight: obj.highlight || '',
      weakness: obj.weakness || ''
    };
  } catch (e) {
    return { isObject: false, raw: analysisData };
  }
};


// 🌟 新增：提取 Markdown 纯文本摘要 (去掉 # * 等符号)
const getExcerpt = (mdText) => {
  if (!mdText) return '';
  // 利用正则去掉 markdown 的特殊符号，只保留纯文本
  const plainText = mdText.replace(/[#*`>-]/g, '').replace(/\n/g, ' ').trim();
  return plainText.length > 80 ? plainText.substring(0, 80) + '...' : plainText;
};

// 🌟 新增：跳转到练习计划页面
const goToLearningPath = () => {
  // 过滤错题
  const weakQuestions = props.evaluations.filter(item => item.score < 85 && item.resource);
  
  // 获取当前页面的 sessionId (兼容 params 或 query 传参)
  const currentSessionId = route.params.sessionId || route.query.sessionId;
  
  // 🌟 核心修复：把 sessionId 拼接到 Key 上，实现数据隔离！
  if (currentSessionId) {
    sessionStorage.setItem(`weak_resources_${currentSessionId}`, JSON.stringify(weakQuestions));
  }
  
  // 带着当前 sessionId 跳转到练习计划页 (假设你的路由叫 /record 或 /plan)
  router.push({ path: '/record', query: { sessionId: currentSessionId } }); 
};

</script>

<style scoped>
/* ====== 100% 还原你的原生配色与结构 ====== */
.content-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
  background: #ffffff;
}

.question-card {
  background: #ffffff;
  padding: 28px 60px;
  transition: all 0.3s ease;
}

/* 改造 H3 为可点击的触发器 */
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  
}
.question-header h3 {
  line-height: 1.6; /* 💡 撑开多行文本的间距，防止标签顶到上一行 */
  margin: 0; /* 确保没有多余的默认 margin 干扰 */
}
.question-card h3.low-score {
  color: #ef4444; /* 醒目的红色题干 */
}

.inline-score-badge {
  display: inline-flex; /* 💡 改用 inline-flex，内部文本绝对居中 */
  align-items: center;
  justify-content: center;
  height: 24px; /* 固定高度，让标签形状更规整 */
  font-size: 13px;
  padding: 0 10px;
  border-radius: 12px;
  margin-left: 8px;
  font-weight: 600;
  
  /* 💡 核心对齐逻辑 */
  vertical-align: middle; 
  transform: translateY(-1px); /* 仅做视觉微调，去掉之前的 -2px */
  white-space: nowrap; /* 强制不换行，防止分数和“分”字断开 */
}

/* 低于 75 分的红色警告样式 */
.badge-danger {
  color: #ef4444;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
}

/* 75 分及以上的安全样式（这里用了清新的蓝绿色，符合你的整体风格） */
.badge-safe {
  color: #0ea5e9; 
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
}
/* 右侧小箭头 */
.toggle-btn {
  color: #222;
  transition: transform 0.5s ease;
}

.toggle-btn.rotate {
  transform: rotate(180deg);
  color: #61b6d6;
}

/* 下拉内容区 */
.question-body {
  overflow: hidden;
}

.body-inner {
  padding-top: 24px;
}

.block {
  margin-bottom: 20px;
}

.block h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}

/* 你的原始颜色搭配 */
.analysis h4, .reference h4{
  color: #3f3f3f;
}

.analysis p, .reference p {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.7;
  color: #555;
  background: #ebebeb;
  padding: 14px 16px;
  border-radius: 10px;
  margin-bottom: 12px; 
}

.answer h4{
  color: #61b6d6;
}

.answer p{
  font-size: 14px;
  font-weight: 600;
  line-height: 1.7;
  color: #555;
  padding: 14px 16px;
  border-radius: 10px;
  background: #d0ebff;
}

.feedback h4 {
  color: #00B894;
}

.feedback p {
  background: rgba(0, 184, 148, 0.08);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.7;
  color: #555;
  padding: 14px 16px;
  border-radius: 10px;
}

/* 折叠丝滑过渡动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.35s ease-in-out;
  max-height: 2500px; /* 增加整体卡片的最大高度，防止被截断 */
  opacity: 1;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

/* 图标 + 文字 垂直居中对齐 */
.icon-text-row {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.icon{
  width: 17px;
  height: 17px;
}

/* ================= 🌟 新增：专属资源推送框 高级样式 ================= */
.resource-push-box {
  margin-top: 24px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #0ea5e9; /* 科技蓝左边框 */
  border-radius: 8px;
  overflow: hidden; /* 防止内容溢出圆角 */
}

/* 头部：可点击区域 */
.resource-header {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background-color: #f0f9ff; /* 极淡的蓝底，诱导点击 */
  transition: background-color 0.2s ease;
}

.resource-header:hover {
  background-color: #e0f2fe; /* 鼠标悬浮反馈 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  font-size: 15px;
  font-weight: 600;
  color: #0369a1; /* 深蓝色标题 */
}

.score-tag {
  font-size: 13px;
  color: #64748b;
  margin-left: 4px;
}

.text-red {
  color: #ef4444;
  font-size: 14px;
  margin: 0 2px;
}

/* 旋转小箭头 */
.resource-toggle-icon {
  color: #0ea5e9;
  transition: transform 0.3s ease;
}

.resource-toggle-icon.rotate {
  transform: rotate(180deg);
}

/* 内容主体 */
.resource-body {
  border-top: 1px dashed #cbd5e1; /* 展开后与头部的分割线 */
  background-color: #ffffff;
}

.resource-content {
  padding: 20px;
}

/* 动画过渡 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
  max-height: 1500px; /* Markdown 内容可能很长 */
  opacity: 1;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ================= 🌟 高级引流卡片样式 (CTA Card) ================= */
.resource-cta-card {
  margin-top: 24px;
  background: linear-gradient(to right, #f8fafc, #f0f9ff);
  border: 1px solid #bae6fd;
  border-radius: 10px;
  overflow: hidden;
}

.cta-header {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0f2fe;
}

.cta-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #0284c7; /* 主题蓝 */
}

.cta-score {
  font-size: 13px;
  color: #64748b;
  background: #ffffff;
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
}

.text-red {
  color: #ef4444;
  font-weight: 700;
  font-size: 14px;
  margin: 0 2px;
}

.cta-body {
  padding: 16px 20px;
}

.cta-excerpt {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
  background: #ffffff;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #cbd5e1;
}

/* 漂亮的跳转按钮 */
.btn-jump-plan {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #68bde4;
  color: #ffffff;
  border: none;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-jump-plan:hover {
  background-color: #409ecd;
}

.btn-jump-plan:active {
  transform: translateY(0);
}
</style>