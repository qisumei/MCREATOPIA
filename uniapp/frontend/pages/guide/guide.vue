<template>
  <!-- 页面容器 -->
  <view class="container">
    <!-- 卡片组件，使用左滑入动画 -->
    <view class="card fade-in-left">
      <!-- 图标区域 -->
      <view class="icon-area">
        <text class="icon">📖</text>  <!-- 书本图标 -->
      </view>
      
      <!-- 文字区域 -->
      <view class="text-area">
        <text class="title">入服指南</text>  <!-- 主标题 -->
        <!-- 描述文字，分两行显示 -->
        <text class="desc">为了确保信息的实时性和准确性，</text>
        <text class="desc">最新的入服教程已统一托管至腾讯文档。</text>
      </view>
      
      <!-- 按钮：点击打开文档链接 -->
      <button class="doc-btn" @click="openDoc">
        查看在线指南
      </button>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        // 腾讯文档链接，存储在组件的data中
        docUrl: "https://docs.qq.com/doc/DTEdod0dUYnh5R0VV"
      }
    },
    methods: {
      // 打开文档的方法
      openDoc() {
        // #ifdef H5 表示仅在小程序H5平台编译
        // 在H5环境中，使用window.location跳转
        window.location.href = this.docUrl;
        // #endif
        
        // #ifdef APP-PLUS 表示仅在APP平台编译
        // 在APP环境中，使用plus.runtime打开URL
        plus.runtime.openURL(this.docUrl);
        // #endif
      }
    }
  }
</script>

<style>
  /* 页面容器样式 */
  .container {
    padding: 40rpx;  /* 内边距 */
    min-height: 100vh;  /* 最小高度为整个视口高度 */
    background-color: #f7f7f7;  /* 浅灰色背景 */
    display: flex;  /* 弹性布局 */
    align-items: center;  /* 垂直居中 */
    justify-content: center;  /* 水平居中 */
  }

  /* 卡片样式 */
  .card {
    background: #ffffff;  /* 白色背景 */
    width: 100%;  /* 宽度占满父容器 */
    border-radius: 20rpx;  /* 圆角 */
    padding: 60rpx 40rpx;  /* 内边距：上下60，左右40 */
    box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);  /* 阴影效果 */
    display: flex;  /* 弹性布局 */
    flex-direction: column;  /* 垂直排列子元素 */
    align-items: center;  /* 子元素水平居中 */
    text-align: center;  /* 文字居中 */
  }

  /* 图标区域样式 */
  .icon-area {
    margin-bottom: 40rpx;  /* 底部外边距 */
  }
  
  .icon {
    font-size: 100rpx;  /* 大图标尺寸 */
  }

  /* 文字区域样式 */
  .text-area {
    margin-bottom: 60rpx;  /* 底部外边距 */
  }
  
  .title {
    font-size: 40rpx;  /* 标题字体大小 */
    font-weight: bold;  /* 加粗 */
    color: #333;  /* 深灰色 */
    margin-bottom: 20rpx;  /* 底部外边距 */
    display: block;  /* 块级显示 */
  }
  
  .desc {
    font-size: 28rpx;  /* 描述文字大小 */
    color: #666;  /* 中灰色 */
    line-height: 1.6;  /* 行高，增加可读性 */
    display: block;  /* 块级显示，每行独立 */
    margin-bottom: 10rpx;  /* 底部外边距 */
  }

  /* 文档按钮样式 */
  .doc-btn {
    width: 100%;  /* 宽度占满父容器 */
    /* 渐变背景色：浅绿到深绿 */
    background: linear-gradient(135deg, #00C853, #64DD17);
    color: white;  /* 文字颜色 */
    border-radius: 50rpx;  /* 圆形按钮 */
    font-size: 32rpx;  /* 字体大小 */
    font-weight: bold;  /* 加粗 */
    /* 按钮阴影，带绿色色调 */
    box-shadow: 0 8rpx 20rpx rgba(76, 175, 80, 0.3);
  }
  
  /* 按钮点击时的状态 */
  .doc-btn:active {
    transform: scale(0.98);  /* 轻微缩小 */
    opacity: 0.9;  /* 透明度变化 */
  }
</style>