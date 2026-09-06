<template>
  <div class="knowledge-base-container">
    <div class="main-layout">
      <!-- 左侧边栏 -->
      <BankSide />
      <!-- 主内容区 -->
      <main class="content">
        <div class="bankcontent">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import BankSide from './BankSide.vue';
import { ref } from 'vue';

// 定义选中的标签索引，默认选中第一个
const activeTab = ref(0);

// 切换标签的方法
const switchTab = (index) => {
  activeTab.value = index;
};
</script>

<style scoped>
/* 全局容器 */
.knowledge-base-container {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f7fa;
  color: #333;
  margin-top: 80px;
}

/* 主布局 */
.main-layout {
  position: relative;
}

.content {
  position: relative;
  width: calc(100% - 240px);
  padding: 24px;
  margin-left: 240px;
}


</style>