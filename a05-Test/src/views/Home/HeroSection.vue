<template>
    <div class="container">
        
      <div class="left-container">
         <div class="sentense"><h1><span style="color: #46a5c0;padding: 5px;">精准</span>模拟，自信登场</h1>
        <h1>把紧张提前消灭</h1>
         <h1>offer等<span style="color: #46a5c0;font-size: larger;padding-left: 3px;">你</span>来拿 ！</h1>
        </div>
      <div class="comment">
        <div class="comment-tip">练得熟・温柔引导夯实基础</div>
        <div class="comment-tip">评得准・复刻真实考场反馈</div>
        <div class="comment-tip last">悟得透・多维分析高效提升</div>
      </div>
      <!-- 未登录：显示「立即体验」按钮 -->
      <button 
        v-if="!userStore.isLogin" 
        class="main-experience-btn"
        @click="handleExperienceClick"
      >
        立即体验
      </button>
      <!-- 已登录：显示「开始模拟」按钮 -->
      <button 
        v-else 
        class="main-simulate-btn"
        @click="handleSimulateClick"
      >
        开始模拟
      </button>


    </div>
     <div class="right-container">
      <img src="../../assets/images/bg/banner.png" alt="">
     </div>
   </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const handleExperienceClick = () => {
  router.push('/login')
}

const handleSimulateClick = () => {
  router.push('/interview')
}

</script>

<style scoped>
.container{
    display: flex;
    height: calc(100vh - 270px);
    align-items: center;
    justify-content: center;
    gap:80px;
    padding-bottom: 20px;
    margin-top: 80px;
}
.sentense{
    font-size: 25px;
}
.comment{
  margin-top: 20px;
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  color: #7d7d7d;
}
.comment-tip{
  border-right: 1px solid #7d7d7d;
  padding-right: 10px;
  font-size: 15px;
}
.comment .last{
  border-right: none;
}
button {
  background: #ff8c42;
  border-radius: 45px;
  font-weight: 600;
  font-size: 20px;
  transition: 0.3s;
  padding: 10px 60px;      
  border: none;        
  cursor: pointer;      
  margin-top: 40px;
  color: #ffffff;
}

.right-container{
    border-radius: 30px;
    overflow: hidden;
}
.right-container img{
    width:800px;
    /*height: 300px;*/
}
.main-experience-btn:hover{
  background: #da6e2b;

}
.main-simulate-btn:hover{
  background: #da6e2b;
}
</style>