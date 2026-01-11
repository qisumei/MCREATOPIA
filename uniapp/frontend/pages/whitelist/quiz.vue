<template>
  <view class="container">
    <!-- 卡片组件，左滑入动画 -->
    <view class="card fade-in-left">
      <!-- 图标区域 -->
      <view class="icon-area">
        <text class="icon">✅</text>  <!-- 对勾图标 -->
      </view>
      
      <!-- 文字区域 -->
      <view class="text-area">
        <text class="title">申请加入白名单</text>
        <text class="desc">当前服务器已简化审核流程。</text>
        <text class="desc">请点击下方按钮加入 QQ 群，在群公告中查看获取白名单的最新方式。</text>
      </view>
      
      <!-- QQ群加入按钮 -->
      <button class="join-btn" @click="joinQQGroup">
        加入 QQ 群申请
      </button>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        // QQ群跳转链接（包含加密参数）
        qqUrl: "https://qun.qq.com/universal-share/share?ac=1&authKey=%2FJs%2FQMP58ouDPJbq0SnvsD0ICvFBDtBF4633ecZ9DA5qrFl5p2FfdZGK7n7%2BXgfp&busi_data=eyJncm91cENvZGUiOiIxMDM4ODY3NzkzIiwidG9rZW4iOiJaNXVBODc0c1BhdmQwS1lwVW90ZGNoTmZLSG5CN1dkRTJkaEVjclVmbksrUVhSelFDdlF1QjlMbVUxUkVkT2VsIiwidWluIjoiMjMwMjgyNzQ2OCJ9&data=S2wInAh1dyYFuc7v2_1lHux6bazFzw_k_ZN-0yPJp2_eUPa8OwSbrUPzQ1ph4LPcFToCPl1Tr6IHxRG1wG1adw&svctype=4&tempid=h5_group_info"
      }
    },
    
    methods: {
      // 加入QQ群方法
      joinQQGroup() {
        // H5环境：直接跳转
        // #ifdef H5
        window.location.href = this.qqUrl;
        // #endif
        
        // APP环境：使用plus API打开
        // #ifdef APP-PLUS
        plus.runtime.openURL(this.qqUrl);
        // #endif
      }
    }
  }
</script>

<style>
	.container {
		padding: 40rpx;
		min-height: 100vh;
		background-color: #f7f7f7;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.card {
		background: #ffffff;
		width: 100%;
		border-radius: 20rpx;
		padding: 60rpx 40rpx;
		box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.icon-area {
		margin-bottom: 40rpx;
	}
	.icon {
		font-size: 100rpx;
	}

	.text-area {
		margin-bottom: 60rpx;
	}
	.title {
		font-size: 40rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 20rpx;
		display: block;
	}
	.desc {
		font-size: 28rpx;
		color: #666;
		line-height: 1.6;
		display: block;
		margin-bottom: 10rpx;
	}

	.join-btn {
		width: 100%;
		background: linear-gradient(135deg, #12B7F5, #2196f3); /* QQ 风格蓝 */
		color: white;
		border-radius: 50rpx;
		font-size: 32rpx;
		font-weight: bold;
		box-shadow: 0 8rpx 20rpx rgba(33, 150, 243, 0.3);
	}
	.join-btn:active {
		transform: scale(0.98);
		opacity: 0.9;
	}
</style>