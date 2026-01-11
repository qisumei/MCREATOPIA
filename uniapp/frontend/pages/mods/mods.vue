<template>
  <view class="page-container">
    <!-- 页面标题 -->
    <view class="section-title">模组介绍</view>
    
    <!-- 模组卡片网格 -->
    <view class="mod-grid">
      <!-- 循环渲染每个模组 -->
      <view class="mod-card" v-for="(mod, index) in modList" :key="index">
        <!-- 模组图标 -->
        <view class="mod-icon">📦</view>
        <!-- 模组信息 -->
        <view class="mod-info">
          <text class="mod-name">{{ mod.name }}</text>  <!-- 模组名称 -->
          <text class="mod-desc">{{ mod.desc }}</text>  <!-- 模组描述 -->
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        // 模组列表（静态数据，未来可改为API获取）
        modList: [
          { name: '机械动力 (Create)', desc: '体验齿轮与蒸汽的浪漫，构建自动化工厂。' },
          { name: '车万女仆', desc: '可爱至极的女仆与应力解决方案。' },
          { name: '农夫乐事', desc: '享受耕种与烹饪的乐趣，砧板真好用。' },
          { name: 'VPB枪械', desc: '享受热兵器带来的快感。' }
        ]
      }
    }
  }
</script>
<style>
	.page-container { padding: 30rpx; background: #f0f0f0; min-height: 100vh; }
	.mod-grid { display: flex; flex-direction: column; gap: 30rpx; }
	.mod-card { 
		background: white; 
		padding: 30rpx; 
		border-radius: 16rpx; 
		display: flex; 
		align-items: center;
		box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
	}
	.mod-icon { font-size: 60rpx; margin-right: 30rpx; }
	.mod-info { flex: 1; }
	.mod-name { font-size: 34rpx; font-weight: bold; color: #333; display: block; margin-bottom: 10rpx; }
	.mod-desc { font-size: 26rpx; color: #666; line-height: 1.4; }
</style>