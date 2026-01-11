<template>
  <view class="page-container">
    <!-- 页面标题 -->
    <view class="section-title">服务器须知</view>
    
    <!-- 内容卡片 -->
    <view class="content-card">
      <!-- 服务器规则列表 -->
      <text class="text-p">1. 禁止使用外挂、作弊客户端 (X-Ray, 飞行等)。</text>
      <text class="text-p">2. 禁止恶意破坏他人建筑、偷窃物品。</text>
      <text class="text-p">3. 请文明交流，禁止刷屏、谩骂。</text>
      <text class="text-p">4. 保持环境整洁，砍树请补种。</text>
      <!-- 高亮提示，显示倒计时 -->
      <text class="text-p highlight">请认真阅读以上内容，{{ countdown > 0 ? countdown + '秒后' : '' }}可继续。</text>
    </view>

    <!-- 继续按钮，倒计时期间禁用 -->
    <button 
      class="btn" 
      :class="{ disabled: countdown > 0 }"  
      @click="handleContinue"
    ><!-- 动态绑定禁用类 -->
      {{ countdown > 0 ? `继续 (${countdown}s)` : '我已阅读并同意' }}
    </button>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        countdown: 10,  // 倒计时秒数
        timer: null     // 定时器引用
      }
    },
    
    // 页面加载时启动倒计时
    onLoad() {
      this.startTimer();
    },
    
    // 页面卸载时清理定时器
    onUnload() {
      if (this.timer) clearInterval(this.timer);
    },
    
    methods: {
      // 启动倒计时定时器
      startTimer() {
        this.timer = setInterval(() => {
          this.countdown--;
          if (this.countdown <= 0) {
            clearInterval(this.timer);  // 倒计时结束，清理定时器
          }
        }, 1000);  // 每秒执行一次
      },
      
      // 处理继续按钮点击
      handleContinue() {
        if (this.countdown > 0) return;  // 倒计时未结束，不执行
        
        // 跳转到登录页面
        uni.navigateTo({ url: '/pages/login/login' });
      }
    }
  }
</script>

<style>
	/* 复用部分通用样式 */
	.page-container { padding: 40rpx; background: #f7f7f7; min-height: 100vh; }
	.section-title { font-size: 48rpx; font-weight: bold; text-align: center; margin-bottom: 40rpx; color: #333; }
	.content-card { background: white; padding: 40rpx; border-radius: 20rpx; margin-bottom: 40rpx; box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.1); }
	.text-p { display: block; margin-bottom: 20rpx; font-size: 30rpx; line-height: 1.6; color: #555; }
	.highlight { color: #ff5722; font-weight: bold; margin-top: 20rpx; }
	
	.btn { background: #2196f3; color: white; border-radius: 50rpx; transition: all 0.3s; }
	/* 禁用状态样式 */
	.btn.disabled { background: #ccc; color: #666; }
</style>