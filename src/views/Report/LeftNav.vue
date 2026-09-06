<template>
  <div class="side-navigation">
    <div class="nav-header">
      <h2 class="nav-title">面试评估报告</h2>
    </div>
    <ul class="nav-menu">
      <li 
        v-for="item in navItems" 
        :key="item.id"
        class="nav-item"
        :class="{ active: activeItem === item.id }"
        @click="handleNavClick(item)"
      >
        <i :class="item.icon" class="nav-icon"></i>
        <span class="nav-text">{{ item.title }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 接收激活项
const props = defineProps({
  activeItem: {
    type: String,
    default: 'overview'
  }
})

// 使用 emit 通知父组件
const emits = defineEmits(['nav-change'])

// 导航菜单项 - 必须与 ReportView 中的 sections.id 匹配
const navItems = [
  { id: 'sum', title: '总体概览', icon: 'icon-overview' },
  { id: 'content', title: '内容评估', icon: 'icon-technical' },
  { id: 'voice', title: '音频分析', icon: 'icon-experience' },
  { id: 'video', title: '视频分析', icon: 'icon-improvement' },
  { id: 'encourage', title: '提升建议', icon: 'icon-summary' },
  { id: 'change', title: '面试变化', icon: 'icon-change' }
]

// 处理导航点击事件
const handleNavClick = (item) => {
  // 更新激活项
  emits('nav-change', item)
}
</script>

<style scoped>
.side-navigation {
  width: 250px;
  height: 60%;
  background: #f5f5f5;
  color: rgb(19, 19, 19);
  padding: 20px 0;
  position: fixed;
  left: 70px;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 15px 0 0 15px; /* 只保留左上和左下圆角 */
  overflow-y: auto;
}

.nav-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgb(67, 67, 67);
  margin-bottom: 20px;
}

.nav-title {
  margin: 0 ;
  text-align: center;
  font-size: 1.4rem;
  font-weight: 700;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.5);
    border-radius: 15px 0 0 15px;
}

/* 默认状态下菜单项的文字为灰色 */
.nav-item:not(.active) .nav-text {
  color: #919191;
}

/* 激活状态的菜单项 */
.nav-item.active {
  background: rgba(255,255,255);
  border-radius: 15px 0 0 15px;
}

/* 激活状态下的文字为黑色 */
.nav-item.active .nav-text {
  color: #333; /* 黑色 */
  font-weight: 700; /* 可选：让选中的文字更粗 */
}

.nav-icon {
  margin-right: 12px;
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 18px;
  font-weight: 600; /* 默认较细的字体 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .side-navigation {
    width: 70px;
  }
  
  .nav-text {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 16px 0;
  }
  
  .nav-icon {
    margin-right: 0;
  }
}
</style>