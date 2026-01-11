<template>
  <!-- 页面根容器 -->
  <view class="container">
    <!-- 第一部分：特别鸣谢区域，使用左滑入动画 -->
    <view class="section fade-in-left">
      <!-- 标题，带左侧蓝色装饰条 -->
      <view class="title">💖 特别鸣谢</view>
      <!-- 横向滚动容器，用于展示鸣谢卡片 -->
      <scroll-view scroll-x class="thanks-scroll">
        <!-- 内部容器，使用flex布局使卡片横向排列 -->
        <view class="scroll-inner">
          <!-- 鸣谢卡片，展示感谢对象 -->
          <view class="thanks-card">服主 Under_p</view>
          <view class="thanks-card">技术 Hiakuyo</view>
          <view class="thanks-card">管理 Team</view>
          <view class="thanks-card">所有玩家</view>
        </view>
      </scroll-view>
    </view>

    <!-- 第二部分：赞助名单区域，使用右滑入动画 -->
    <view class="section fade-in-right">
      <!-- 标题 -->
      <view class="title">赞助名单</view>
      <!-- 网格布局容器，4列 -->
      <view class="grid">
        <!-- 循环生成32个赞助者卡片，v-for是Vue的循环指令 -->
        <view class="grid-item" v-for="i in 32" :key="i">
          赞助者 {{ i }}
        </view>
      </view>
    </view>
  </view>
</template>

<style>
  /* 页面基础样式 */
  .container { padding: 30rpx; }  /* rpx是响应式单位，750rpx等于屏幕宽度 */
  .section { margin-bottom: 60rpx; }  /* 每个部分之间的间距 */
  
  /* 标题样式：蓝色左侧边框，粗体 */
  .title { 
    font-size: 36rpx; 
    font-weight: bold; 
    margin-bottom: 20rpx; 
    padding-left: 20rpx; 
    border-left: 8rpx solid #2196f3; 
  }
  
  /* 横向滚动区域样式 */
  .thanks-scroll { 
    width: 100%;  /* 占满父容器宽度 */
    white-space: nowrap;  /* 禁止换行，保持横向排列 */
  }
  
  /* 滚动内部容器：使用flex布局，设置间距 */
  .scroll-inner { 
    display: flex;  /* 弹性盒子布局 */
    gap: 20rpx;  /* 子元素之间的间距 */
    padding: 10rpx;  /* 内边距 */
  }
  
  /* 鸣谢卡片样式 */
  .thanks-card { 
    width: 240rpx;  /* 固定宽度 */
    height: 140rpx;  /* 固定高度 */
    /* 渐变色背景：从紫色到蓝色 */
    background: linear-gradient(135deg, #6a11cb, #2575fc); 
    color: white;  /* 文字颜色 */
    border-radius: 16rpx;  /* 圆角 */
    display: flex;  /* 使用flex布局居中内容 */
    align-items: center;  /* 垂直居中 */
    justify-content: center;  /* 水平居中 */
    font-weight: bold;  /* 加粗 */
    flex-shrink: 0;  /* 禁止卡片被压缩 */
  }

  /* 网格布局：4列等宽 */
  .grid { 
    display: grid;  /* 网格布局 */
    grid-template-columns: repeat(4, 1fr);  /* 4列，每列等宽 */
    gap: 20rpx;  /* 网格间隙 */
  }
  
  /* 网格项样式 */
  .grid-item { 
    background: white;  /* 白色背景 */
    height: 80rpx;  /* 固定高度 */
    display: flex;  /* 弹性布局 */
    align-items: center;  /* 垂直居中 */
    justify-content: center;  /* 水平居中 */
    border-radius: 10rpx;  /* 圆角 */
    font-size: 24rpx;  /* 字体大小 */
    color: #555;  /* 字体颜色 */
  }
</style>