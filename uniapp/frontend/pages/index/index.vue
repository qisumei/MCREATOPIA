<template>
  <!-- 页面根容器 -->
  <view class="container">
    <!-- 顶部英雄区域，带左侧淡入动画 -->
    <view class="hero fade-in-left">
      <!-- 服务器logo，可点击预览 -->
      <image 
        src="/static/logo.png" 
        class="logo zoomable-img" 
        mode="widthFix"  <!-- 宽度自适应，高度按比例缩放 -->
        @click="previewImage('/static/logo.png')"  <!-- 点击预览图片 -->
      ></image>
      <text class="server-title">MCREATOPIA</text>  <!-- 服务器名称 -->
      <text class="server-subtitle">创造 · 探索 · 工业</text>  <!-- 副标题 -->
    </view>

    <!-- 导航网格，带右侧淡入动画 -->
    <view class="grid-nav fade-in-right">
      <!-- 转正申请导航项 -->
      <view class="nav-item" @click="goPage('/pages/whitelist/quiz')">
        <text class="icon">✅</text>
        <text class="label">转正申请</text>
      </view>
      <!-- 服务器须知导航项 -->
      <view class="nav-item" @click="goPage('/pages/rules/rules')">
        <text class="icon">📜</text>
        <text class="label">服务器须知</text>
      </view>
      <!-- 入服指南导航项 -->
      <view class="nav-item" @click="goPage('/pages/guide/guide')">
        <text class="icon">📖</text>
        <text class="label">入服指南</text>
      </view>
      <!-- 模组介绍导航项 -->
      <view class="nav-item" @click="goPage('/pages/mods/mods')">
        <text class="icon">📦</text>
        <text class="label">模组介绍</text>
      </view>
      <!-- 赞助鸣谢导航项 -->
      <view class="nav-item" @click="goPage('/pages/donate/donate')">
        <text class="icon">🙇</text>
        <text class="label">赞助鸣谢</text>
      </view>
      <!-- 登录/注册导航项 -->
      <view class="nav-item" @click="goPage('/pages/login/login')">
        <text class="icon">👤</text>
        <text class="label">登录/注册</text>
      </view>
    </view>

    <!-- 服内摄影展示区域标题 -->
    <view class="section-title">📷 服内摄影</view>
    <!-- 展示卡片 -->
    <view class="showcase">
      <view class="card fade-in-left">
        <!-- 展示图片，可点击预览 -->
        <image 
          src="/static/showcase1.jpg" 
          mode="aspectFill"  
          class="card-img zoomable-img"
          @click="previewImage('/static/showcase1.jpg')"
        ></image><!-- 保持宽高比填充，可能裁剪 -->
        <!-- 卡片内容 -->
        <view class="card-content">
          <text class="card-title">自由的创造环境</text>
          <text class="card-desc">在这里，没有什么是不可能的。从宏伟的建筑到精密的机械，尽情挥洒你的创意。</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  export default {
    methods: {
      // 跳转到指定页面的方法
      goPage(url) {
        uni.navigateTo({ url });  // uni-app页面跳转API
      },
      
      // 预览图片方法（通用）
      previewImage(url) {
        uni.previewImage({
          urls: [url],  // 要预览的图片数组
          current: 0,   // 当前显示第一张
          indicator: 'default'  // 显示指示器
        });
      },
      
      // 处理登录回调数据的方法（从login.vue调用）
      handleLoginHook(data) {
        console.log('捕获到登录数据:', data);
        uni.showLoading({ title: '正在保存数据...' });
        
        // 保存用户数据到本地存储
        uni.setStorageSync('user_uuid', data.token);  // UUID
        uni.setStorageSync('user_name', data.username);  // 用户名
        
        // ✅ 新增：处理白名单状态
        if (data.whitelist) {
          // 保存白名单状态，统一存为字符串
          uni.setStorageSync('is_whitelisted', data.whitelist);
        } else {
          // 默认设置为false
          uni.setStorageSync('is_whitelisted', 'false');
        }
        
        uni.showToast({ title: '登录成功', icon: 'success' });
        
        // 延迟跳转到主页
        setTimeout(() => {
          this.redirectToHome();
        }, 500);
      },
      
      // 重定向到主页（从login.vue调用）
      redirectToHome() {
        uni.reLaunch({
          url: '/pages/home/home'  // 关闭所有页面，打开主页
        });
      }
    },
    
    // 页面加载生命周期
    onLoad(options) {
      // 检查URL是否携带了登录回调参数
      if (options.token) {
        uni.showToast({ title: '登录成功', icon: 'success' });
        
        // 1. 保存Token（UUID）- 使用正确的键名
        uni.setStorageSync('user_uuid', options.token);
        uni.setStorageSync('userToken', options.token);  // 兼容旧键名
        
        // 2. 保存用户名
        if (options.username) {
          uni.setStorageSync('user_name', options.username);
        }
        
        // 3. 保存白名单状态（注意参数名是whitelist，不是whitelisted）
        if (options.whitelist) {
          // 统一存为is_whitelisted，与home.vue保持一致
          uni.setStorageSync('is_whitelisted', options.whitelist);
        }
        
        // 4. 清理URL参数（H5环境）
        // #ifdef H5
        if (window.history.replaceState) {
          // 去除URL中的查询参数，保持地址栏整洁
          window.history.replaceState(null, null, window.location.hash.split('?')[0]);
        }
        // #endif
      }
    }
  }
</script>

<style>
	/* 页面容器 */
	.container {
		min-height: 100vh;
		background-color: #f7f7f7;
		padding-bottom: 40rpx;
	}

	/* Hero 区域样式 */
	.hero {
		height: 450rpx;
		background: linear-gradient(135deg, #333333, #4a4a4a);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: white;
		border-bottom-left-radius: 40rpx;
		border-bottom-right-radius: 40rpx;
		box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.2);
		margin-bottom: 40rpx;
	}
	.logo { width: 180rpx; height: 180rpx; margin-bottom: 20rpx; border-radius: 50%; border: 4rpx solid rgba(255,255,255,0.2); }
	.server-title { font-size: 56rpx; font-weight: bold; letter-spacing: 4rpx; }
	.server-subtitle { font-size: 28rpx; color: #ccc; margin-top: 10rpx; letter-spacing: 2rpx; }
	
	/* 导航宫格样式 */
	.grid-nav {
		display: flex;
		flex-wrap: wrap;
		padding: 0 20rpx;
		margin-top: -60rpx; /* 让导航栏稍微上浮，盖住 Hero 一点点，更有设计感 */
	}
	.nav-item {
		width: 33.33%; /* 3列布局 */
		height: 200rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: #fff;
		border: 1rpx solid #f0f0f0;
		box-sizing: border-box;
		transition: all 0.2s;
	}
	/* 圆角处理：左上、右上、左下、右下 */
	.nav-item:nth-child(1) { border-top-left-radius: 20rpx; }
	.nav-item:nth-child(3) { border-top-right-radius: 20rpx; }
	.nav-item:nth-child(4) { border-bottom-left-radius: 20rpx; }
	.nav-item:nth-child(6) { border-bottom-right-radius: 20rpx; }
	
	.nav-item:active { background-color: #f9f9f9; }
	
	.icon { font-size: 60rpx; margin-bottom: 16rpx; }
	.label { font-size: 28rpx; color: #333; font-weight: 500; }
	
	/* 展示区域样式 */
	.section-title { margin: 40rpx 30rpx 20rpx; font-size: 36rpx; font-weight: bold; color: #333; padding-left: 16rpx; border-left: 8rpx solid #2196f3; }
	.showcase { padding: 0 30rpx; }
	.card { 
		background: #fff; 
		border-radius: 20rpx; 
		overflow: hidden; 
		margin-bottom: 30rpx; 
		box-shadow: 0 8rpx 20rpx rgba(0,0,0,0.06); 
	}
	.card-img { width: 100%; height: 320rpx; }
	.card-content { padding: 30rpx; }
	.card-title { font-size: 34rpx; font-weight: bold; margin-bottom: 16rpx; display: block; color: #333; }
	.card-desc { font-size: 28rpx; color: #666; line-height: 1.6; }
</style>