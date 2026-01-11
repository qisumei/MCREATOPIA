<script>
	// 导出默认配置对象
	export default {
		// uni-app应用生命周期函数：应用启动时触发
		onLaunch: function() {
			console.log('App Launch') // 在控制台输出启动日志，用于调试
		}
	}
</script>

<style>
	/* 全局样式，整个应用都会生效 */
	
	/* 1. 定义动画关键帧 */
	@keyframes fadeInLeft {
		from { 
			opacity: 0;           /* 完全透明 */
			transform: translateX(-40rpx); /* 从左侧40rpx位置开始 */
		}
		to { 
			opacity: 1;           /* 完全不透明 */
			transform: translateX(0);     /* 移动到正常位置 */
		}
	}
	
	@keyframes fadeInRight {
		from { 
			opacity: 0; 
			transform: translateX(40rpx); /* 从右侧40rpx位置开始 */
		}
		to { 
			opacity: 1; 
			transform: translateX(0); 
		}
	}
	
	/* 可缩放图片的通用样式类 */
	.zoomable-img {
		/* 过渡效果：0.3秒完成，使用自定义缓动函数 */
		transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), 
		            box-shadow 0.3s ease;
		cursor: pointer; /* 鼠标指针变为手型，表示可点击 */
	}
	
	/* 鼠标悬停时的效果（仅在支持:hover的平台上生效） */
	.zoomable-img:hover {
		transform: scale(1.25);       /* 放大1.25倍 */
		/* 添加阴影效果，增加立体感 */
		box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
		z-index: 10;      /* 提高层级，确保放大时不被其他元素遮挡 */
		position: relative; /* 相对定位，使z-index生效 */
	}

	/* 2. 定义动画类，在HTML元素中添加这些类名即可使用动画 */
	.fade-in-left {
		animation: fadeInLeft 0.8s ease-out forwards; /* 使用fadeInLeft动画，0.8秒，ease-out缓动，forwards保持最终状态 */
	}
	
	.fade-in-right {
		animation: fadeInRight 0.8s ease-out forwards;
	}

	/* 3. 全局页面样式：page是uni-app中每个页面的根元素 */
	page {
		background-color: #f0f0f0;     /* 页面背景色 */
		font-family: system-ui, -apple-system, sans-serif; /* 字体栈，兼容各系统 */
	}
</style>