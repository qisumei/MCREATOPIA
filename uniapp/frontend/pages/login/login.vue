<template>
  <view class="login-container">
    <!-- 登录卡片，左滑入动画 -->
    <view class="login-card fade-in-left">
      <!-- logo区域 -->
      <view class="logo-box">
        <image src="/static/logo.png" class="logo zoomable-img" mode="widthFix" @click="previewLogo"></image>
      </view>
      
      <!-- 标题区域 -->
      <view class="header-text">
        <text class="title">欢迎回到 MCREATOPIA</text>
        <text class="subtitle">请使用购买了 Minecraft 的微软账号登录</text>
      </view>

      <!-- 操作区域 -->
      <view class="action-area">
        <!-- 微软登录按钮，点击后跳转到后端认证 -->
        <button class="btn microsoft-btn" @click="handleMicrosoftLogin" :disabled="loading">
          <image class="ms-icon" src="/static/ODF.png"></image>  <!-- 微软图标 -->
          <text>{{ loading ? '正在连接...' : '使用微软账号登录' }}</text>
        </button>
      </view>

      <!-- 页脚协议声明 -->
      <view class="footer-agreement">
        <text>登录即代表同意</text>
        <text class="link" @click="goRules">《服务器须知》</text>  <!-- 可点击 -->
      </view>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        loading: false,  // 按钮加载状态
        // 后端OAuth认证地址（开发环境）
        backendAuthUrl: 'http://localhost:21007/api/auth/microsoft' 
      }
    },
    
    // 页面加载生命周期
    onLoad(options) {
      // 1. 检查URL是否携带了登录回调参数
      if (options.token && options.username) {
        this.handleLoginHook(options);
        return;  // 处理完直接返回，不再执行自动登录
      }
      
      // 2. 检查本地是否有Cookie（自动登录）
      this.checkAutoLogin();
    },
    
    methods: {
      // === 处理登录回调数据 ===
      handleLoginHook(data) {
        console.log('捕获到登录数据:', data);
        uni.showLoading({ title: '正在保存数据...' });
        
        // 保存用户数据到本地存储
        uni.setStorageSync('user_uuid', data.token);
        uni.setStorageSync('user_name', data.username);
        
        // 保存白名单状态（如果后端返回了）
        if (data.whitelist) {
          uni.setStorageSync('whitelist', data.whitelist);
        }
        
        uni.showToast({ title: '登录成功', icon: 'success' });
        
        // 延迟跳转到主页
        setTimeout(() => {
          this.redirectToHome();
        }, 500);
      },
      
      // === 检查自动登录 ===
      checkAutoLogin() {
        // 从本地存储获取用户信息
        const uuid = uni.getStorageSync('user_uuid');
        const username = uni.getStorageSync('user_name');
        
        // 如果有用户信息，自动跳转到主页
        if (uuid && username) {
          console.log('检测到本地 Cookie，执行自动登录');
          this.redirectToHome();
        }
      },
      
      // === 跳转到主页 ===
      redirectToHome() {
        // 清理URL参数（H5环境）
        // #ifdef H5
        if (window.history.replaceState) {
          // 将URL重置为干净的login路径
          const cleanUrl = window.location.href.split('?')[0];
          window.history.replaceState(null, null, cleanUrl);
        }
        // #endif

        // 使用reLaunch关闭所有页面，防止返回登录页
        uni.reLaunch({
          url: '/pages/home/home'
        });
      },

      // === 发起微软登录 ===
      handleMicrosoftLogin() {
        this.loading = true;  // 开始加载
        uni.showLoading({ title: '跳转中...' });
        
        // H5环境：直接跳转到后端认证
        // #ifdef H5
        window.location.href = this.backendAuthUrl;
        // #endif
        
        // APP环境：使用plus API打开URL
        // #ifdef APP-PLUS
        plus.runtime.openURL(this.backendAuthUrl);
        this.loading = false;  // 重置加载状态
        uni.hideLoading();  // 隐藏加载提示
        // #endif
      },
      
      // 跳转到服务器须知页面
      goRules() {
        uni.navigateTo({ url: '/pages/rules/rules' });
      },
      
      // 预览logo图片
      previewLogo() {
        uni.previewImage({ urls: ['/static/logo.png'] });
      }
    }
  }
</script>

<style>
	/* 保持原样式不变 */
	.login-container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
		padding: 40rpx;
	}

	.login-card {
		width: 100%;
		max-width: 600rpx;
		background: #ffffff;
		border-radius: 32rpx;
		padding: 80rpx 40rpx;
		box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.logo {
		width: 180rpx;
		height: 180rpx;
		border-radius: 50%;
		margin-bottom: 40rpx;
		border: 6rpx solid #fff;
		box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.12);
	}

	.header-text { margin-bottom: 80rpx; }
	.title { font-size: 40rpx; font-weight: bold; color: #333; margin-bottom: 16rpx; display: block; }
	.subtitle { font-size: 26rpx; color: #999; }

	.action-area { width: 100%; padding: 0 20rpx; }
	.microsoft-btn {
		background-color: #2f2f2f;
		color: #fff;
		height: 100rpx;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 30rpx;
		font-weight: 500;
		border: none;
		transition: all 0.3s;
		box-shadow: 0 8rpx 16rpx rgba(47, 47, 47, 0.2);
	}
	.microsoft-btn:active { transform: scale(0.98); background-color: #000; }
	.ms-icon { width: 40rpx;	height: 40rpx;	margin-right: 20rpx; }

	.footer-agreement { margin-top: 60rpx; font-size: 24rpx; color: #ccc; }
	.link { color: #2196f3; text-decoration: underline; margin-left: 10rpx; cursor: pointer; }
</style>