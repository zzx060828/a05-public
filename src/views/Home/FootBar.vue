<template>
    <div class="foot-bar-container">
    <van-row gutter="20" justify="space-around">
      <van-col span="8">
        <div class="feature-item">
          <van-icon name="description" color="#8bc4d3" size="50px" />
          <div class="feature-title">AI逐题点拨</div>
          <div class="feature-desc">业界领先的大模型技术支持</div>
        </div>
      </van-col>
      <van-col span="8">
        <div class="feature-item">
          <van-icon name="photo" color="#978bd3" size="50px" />
          <div class="feature-title">多模态分析技术</div>
          <div class="feature-desc">同时分析视频、语音和文本内容</div>
        </div>
      </van-col>
      <van-col span="8">
        <div class="feature-item">
          <van-icon name="chart-trending-o" color="#cb7d7d" size="50px" />
          <div class="feature-title">专业评测报告</div>
          <div class="feature-desc">多维度数据分析和改进建议</div>
        </div>
      </van-col>
    </van-row>
  </div>
</template>

<script>
export default {
name: 'FootBar',
}
</script>

<style scoped>
.foot-bar-container {
    width: 100%;
  background-color: #eaeaeae8;
  padding-top: 40px;
  padding-bottom: 27px;

  border-radius: 10px;
}

.feature-item {
  text-align: center;
  color: rgb(0, 0, 0);
}

.feature-title {
  font-size: 30px;
  margin-top: 10px;
}

.feature-desc {
  font-size: 14px;
  margin-top: 5px;
}
</style>