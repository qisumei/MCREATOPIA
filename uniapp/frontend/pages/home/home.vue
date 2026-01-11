<template>
	<view class="dashboard-container">
		<view class="sidebar">
			<view class="sidebar-header">
				<text class="logo-text">M C T P</text>
			</view>
			
			<view class="nav-list">
				<view 
					class="nav-item" 
					:class="{ active: currentTab === 'status' }"
					@click="switchTab('status')"
				>
					<text class="icon">📊</text>
					<text>服内状态</text>
				</view>
				
				<view 
					class="nav-item" 
					:class="{ active: currentTab === 'query' }"
					@click="switchTab('query')"
				>
					<text class="icon">🔍</text>
					<text>方块查询</text>
				</view>
				
				<view 
					class="nav-item" 
					:class="{ active: currentTab === 'profile' }"
					@click="switchTab('profile')"
				>
					<text class="icon">🎅</text>
					<text>个人信息</text>
				</view>
			</view>
			
			<view class="sidebar-footer">
			    <view class="user-brief">
			        <image :src="userAvatar" class="avatar" mode="widthFix"></image>
			        <text class="username">{{ username || 'User' }}</text>
			    </view>
			</view>
		</view>

		<scroll-view scroll-y class="main-content">
			
			<view v-if="currentTab === 'status'" class="module-container fade-in">
			    <view class="page-header">
			        <text class="page-title">服务器概览</text>
			        <button class="refresh-bn" @click="fetchServerStatus">刷新</button>
			    </view>
			    
			    <view class="status-grid">
			        <view class="metric-card">
			            <view class="metric-icon tps-color">⚡</view>
			            <view class="metric-info">
			                <text class="metric-label">实时 TPS</text>
			                <text class="metric-value">{{ serverStatus.tps }}</text>
			                <text class="metric-sub">MSPT: {{ serverStatus.mspt }}ms</text>
			            </view>
			        </view>
			        
			        <view class="metric-card">
			            <view class="metric-icon online-color">👥</view>
			            <view class="metric-info">
			                <text class="metric-label">在线玩家</text>
			                <text class="metric-value">{{ serverStatus.online }} / {{ serverStatus.max }}</text>
			                <text class="metric-sub">延迟: {{ serverStatus.latency || '--' }}ms</text>
			            </view>
			        </view>
			    </view>
			
			    <view class="player-section">
			        <text class="section-subtitle">在线玩家列表 ({{ serverStatus.players.length }})</text>
			        
			        <view class="player-grid">
			            <view class="player-card" v-for="(p, index) in serverStatus.players" :key="index">
			                <image :src="p.avatar" class="p-avatar" mode="widthFix"></image>
			                <text class="p-name">{{ p.name }}</text>
			            </view>
			            
			            <view v-if="serverStatus.players.length === 0" class="empty-player">
			                <text>暂无玩家在线</text>
			            </view>
			        </view>
			    </view>
			</view>

			<view v-if="currentTab === 'query'" class="module-container fade-in">
				<view class="query-layout">
					<view class="query-card form-card">
						<view class="card-header">
							<text class="card-title">🔍 查询参数</text>
						</view>
						
						<view class="form-group">
							<text class="label">查询模式</text>
							<picker :range="['具体位置', '范围查询']" @change="e => queryForm.mode = e.detail.value">
								<view class="picker-box">
									{{ queryForm.mode == 0 ? '具体位置（单点）' : '范围查询（周边区域）' }}
								</view>
							</picker>
						</view>
						
						<view class="form-group">
							<text class="label">世界维度</text>
							<picker :range="worlds" range-key="name" @change="e => queryForm.world = worlds[e.detail.value].id">
								<view class="picker-box">
									{{ getWorldName(queryForm.world) }}
								</view>
							</picker>
						</view>
						
						<view class="form-group">
							<text class="label">坐标位置 (XYZ)</text>
							<view class="coord-inputs">
								<input type="number" v-model="queryForm.x" placeholder="X" class="coord-input" />
								<input type="number" v-model="queryForm.y" placeholder="Y" class="coord-input" />
								<input type="number" v-model="queryForm.z" placeholder="Z" class="coord-input" />
							</view>
						</view>
						
						<view class="form-group" v-if="queryForm.mode == 1">
							<text class="label">查询半径 (1-10)</text>
							<input type="number" v-model="queryForm.radius" class="ms-input" />
						</view>
						
						<view class="form-group">
							<text class="label">方块类型 (可选)</text>
							<input type="text" v-model="queryForm.material" placeholder="例如: chest" class="ms-input" />
						</view>
						
						<button class="ms-btn primary" @click="executeQuery" :disabled="loading">
							{{ loading ? '查询中...' : '🚀 执行查询' }}
						</button>
						
						<view class="tips-box">
							<text class="tips-title">查询说明</text>
							<text class="tips-text">• 具体位置：查询单点历史</text>
							<text class="tips-text">• 范围查询：查询周边记录 (最大半径10)</text>
							<text class="tips-text">• 最多显示最新的 100 条记录</text>
						</view>
					</view>
					
					<view class="query-card result-card">
						<view class="card-header border-bottom">
							<text class="card-title">📋 查询结果</text>
							<text class="result-badge">{{ queryResults.length }} 条记录</text>
						</view>
						
						<scroll-view scroll-y class="result-console">
							<text v-if="queryResults.length === 0 && !loading" class="empty-text">等待查询或无数据...</text>
							
							<view v-for="(item, index) in queryResults" :key="index" class="log-item">
								<text class="log-time">[{{ formatTime(item.time) }}]</text>
								<text class="log-coord" v-if="queryForm.mode == 1">({{ item.x }}, {{ item.y }}, {{ item.z }})</text>
								<text class="log-user">{{ item.username || '未知' }}</text>
								<text class="log-action" :class="getActionClass(item.action)">{{ getActionDesc(item.action) }}</text>
								<text class="log-block">{{ item.material }}</text>
							</view>
						</scroll-view>
						
						<view class="console-footer">
							<text>响应时间: {{ responseTime }}ms</text>
							<text>状态: {{ loading ? '请求中' : '就绪' }}</text>
						</view>
					</view>
				</view>
			</view>

			<view v-if="currentTab === 'profile'" class="module-container fade-in">
							<view class="profile-card">
								<view class="profile-header-bg"></view>
								
								<view class="profile-content">
									<image :src="userAvatar" class="profile-avatar" mode="widthFix"></image>
									<view class="profile-names">
										<text class="p-name-big">{{ username || 'User' }}</text>
										<text class="p-uuid">UUID: {{ uuid || '未知' }}</text>
									</view>
									
									<view v-if="opLevel > 0" class="op-badge fade-in">
									            <text class="badge-icon">👑</text>
									            <text class="badge-text">管理员</text>
									        </view>
									
									        <view class="whitelist-badge" :class="isWhitelisted ? 'valid' : 'invalid'">
									            <text class="badge-icon">{{ isWhitelisted ? '✅' : '🚫' }}</text>
									            <text class="badge-text">{{ isWhitelisted ? '已在白名单' : '未获白名单' }}</text>
									        </view>
								</view>
								
								<view class="info-list">
									<view class="info-item">
										<text class="label">账户类型</text>
										<text class="value">微软正版 (OAuth)</text>
									</view>
									<view class="info-item">
										<text class="label">绑定状态</text>
										<text class="value highlight">已绑定</text>
									</view>
									<view class="info-item">
										<text class="label">Under币</text>
										<text class="value highlight">{{underb || 0 }}</text>
									</view>
								</view>
			                    
			                    <button v-if="!isWhitelisted" class="warning-box">
			                        <text>您似乎还未加入白名单，请点击这里前往答题。</text>
			                    </button>
							</view>
						</view>
			
		</scroll-view>
	</view>
</template>

<script>
// 导入封装的请求工具
import { request } from '@/common/request.js';

export default {
  // data函数返回组件的响应式数据
  data() {
    return {
      currentTab: 'status', // 当前激活的标签页，默认显示状态页
      username: '', // 用户名
      loading: false, // 加载状态，用于按钮禁用
      responseTime: 0, // 查询响应时间
      userAvatar: '/static/Steve.png', // 用户头像，默认显示Steve
      uuid: '', // 用户的UUID
      isWhitelisted: false, // 是否在白名单中
      opLevel: 0, // 管理员等级，0表示普通用户
      underb: 0, // 虚拟货币数量
      
      // 服务器状态数据对象
      serverStatus: {
        tps: '--', // 服务器每秒刻数，衡量性能
        mspt: '--', // 每刻毫秒数
        online: 0, // 当前在线人数
        max: 100, // 服务器最大人数上限
        players: [] // 在线玩家列表，包含头像和名字
      },
      
      // 方块查询表单数据
      queryForm: {
        mode: 0, // 0=具体位置，1=范围查询
        world: 'minecraft:overworld', // 默认世界为主世界
        x: '', y: '', z: '', // 坐标值
        radius: 5, // 查询半径
        material: '' // 方块类型，如"chest"
      },
      
      // 世界列表，用于选择器显示
      worlds: [
        { name: '主世界', id: 'minecraft:overworld' },
        { name: '下界', id: 'minecraft:the_nether' },
        { name: '末地', id: 'minecraft:the_end' }
      ],
      
      // 查询结果数组
      queryResults: []
    }
  },
  
  // onLoad是uni-app页面生命周期函数，页面加载时执行
  onLoad(options) {
    // 1. 处理用户名参数
    if(options.username) {
      // 如果URL传入了username，保存到data和本地存储
      this.username = options.username;
      uni.setStorageSync('user_name', options.username);
    } else {
      // 否则从本地存储读取，支持两种键名（兼容旧版本）
      this.username = uni.getStorageSync('user_name') || 
                     uni.getStorageSync('userName') || 'User';
    }

    // 2. 处理UUID参数
    let uuid = options.token ||  // 优先从URL参数获取（登录回调）
              uni.getStorageSync('user_uuid') ||  // 其次从本地存储获取
              uni.getStorageSync('userToken');  // 兼容旧键名
    this.uuid = uuid; 
    
    if (uuid) {
      // 如果有UUID，使用mc-heads.net服务生成头像
      this.userAvatar = `https://mc-heads.net/avatar/${uuid}/64`;
      
      // ✅ 重要：立即去后端查询白名单状态
      this.checkWhitelistStatus(uuid);
      
    } else {
      // 没有UUID，使用默认Steve头像
      this.userAvatar = '/static/Steve.png'; 
      // 没有UUID肯定不是白名单
      this.isWhitelisted = false;
    }
    
    // 3. 页面加载时自动获取服务器状态
    this.fetchServerStatus();
  },
  
  // methods对象包含所有自定义方法
  methods: {
    // 切换侧边栏标签页
    switchTab(tab) {
      this.currentTab = tab; // 更新当前标签页
    },
    
    // 检查白名单状态的方法
    async checkWhitelistStatus(uuid) {
      try {
        // 调用后端接口检查白名单状态
        const res = await request({
          url: '/whitelist/check', // 对应后端的/api/whitelist/check
          method: 'GET',
          data: { uuid: uuid } // 发送UUID作为参数
        });
        
        console.log("白名单检查结果:", res);
        // 更新白名单状态和管理员等级
        this.isWhitelisted = res.whitelisted;
        this.opLevel = res.op_level || 0;
        
      } catch (e) {
        console.error("白名单检查失败:", e);
        this.isWhitelisted = false; // 失败时默认不是白名单
      }
    },
    
    // 获取服务器状态的方法
    async fetchServerStatus() {
      try {
        // 使用Promise.all同时发送两个请求，提高效率
        const [resTPS, resOnline] = await Promise.all([
          request({ url: '/server/tps' }), // 获取TPS数据
          request({ url: '/server/online' }) // 获取在线玩家数据
        ]);
        
        // 更新服务器状态数据
        this.serverStatus.tps = resTPS.tps;
        this.serverStatus.mspt = resTPS.mspt;
        this.serverStatus.online = resOnline.online;
        this.serverStatus.max = resOnline.max;
        this.serverStatus.players = resOnline.players || []; // 防止undefined
        
      } catch (e) {
        // 模拟失败或接口未写好时的默认值（开发阶段使用）
        this.serverStatus.tps = '20.0'; // 理想TPS值
        this.serverStatus.online = '5'; // 模拟在线人数
      }
    },
    
    // 辅助方法：根据世界ID获取世界名称
    getWorldName(id) {
      // 在worlds数组中查找匹配的世界
      const w = this.worlds.find(item => item.id === id);
      return w ? w.name : '未知世界'; // 找不到返回"未知世界"
    },
    
    // 执行方块查询的核心方法
    async executeQuery() {
      // 简单的非空校验
      if(!this.queryForm.x || !this.queryForm.y || !this.queryForm.z) {
        return uni.showToast({ title: '坐标不能为空', icon: 'none' });
      }
      
      this.loading = true; // 开始加载，禁用按钮
      const startTime = Date.now(); // 记录开始时间
      
      try {
        let url = '';
        // 构建请求参数
        let params = {
          x: this.queryForm.x,
          y: this.queryForm.y,
          z: this.queryForm.z,
          world: this.queryForm.world,
          material: this.queryForm.material
        };
        
        // 根据查询模式选择不同的API
        if (this.queryForm.mode == 0) {
          url = '/query-blocks'; // 具体位置查询
        } else {
          url = '/query-range-blocks'; // 范围查询
          params.radius = this.queryForm.radius; // 添加半径参数
        }
        
        // 发送请求
        const res = await request({
          url: url,
          method: 'GET',
          data: params // 参数会作为查询字符串附加到URL
        });
        
        // 处理返回结果，确保是数组
        this.queryResults = Array.isArray(res) ? res : [];
        
        // 如果没有结果，提示用户
        if(this.queryResults.length === 0) {
          uni.showToast({ title: '未查到记录', icon: 'none' });
        }
        
      } catch(e) {
        // 请求失败处理
        uni.showToast({ title: '查询出错', icon: 'none' });
        console.error(e); // 控制台打印错误详情
      } finally {
        // 无论成功失败，都要执行的代码
        this.loading = false; // 结束加载状态
        this.responseTime = Date.now() - startTime; // 计算响应时间
      }
    },
    
    // 格式化时间戳（秒）为可读时间
    formatTime(ts) {
      const date = new Date(ts * 1000); // 转换为毫秒
      // 返回格式：月-日 时:分
      return `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`;
    },
    
    // 根据动作代码返回动作描述
    getActionDesc(code) {
      // 动作代码映射：0=破坏，1=放置，2=使用
      const map = { 0: '破坏', 1: '放置', 2: '使用' };
      return map[code] || '未知'; // 找不到映射返回"未知"
    },
    
    // 根据动作代码返回CSS类名
    getActionClass(code) {
      // 类名映射：破坏=红色系，放置=绿色系，使用=蓝色系
      const map = { 0: 'act-break', 1: 'act-place', 2: 'act-use' };
      return map[code] || ''; // 找不到映射返回空字符串
    }
  }
}
</script>

<style>
	/* 全局布局变量 */
	:root {
		--ms-blue: #0078D4;
		--ms-bg: #F3F2F1;
		--ms-sidebar: #202020;
		--ms-card-bg: #FFFFFF;
	}

	.dashboard-container {
		display: flex;
		height: 100vh;
		background-color: #F3F2F1;
		font-family: "Segoe UI", system-ui, sans-serif;
	}

	/* ============ 侧边栏样式 ============ */
	.sidebar {
		width: 200px; /* 侧边栏宽度 */
		background-color: #ffffff;
		display: flex;
		flex-direction: column;
		border-right: 1px solid #e0e0e0;
		flex-shrink: 0; /* 防止被挤压 */
	}

	.sidebar-header {
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-bottom: 1px solid #f0f0f0;
	}
	.logo-text {
		font-size: 20px;
		font-weight: 900;
		color: #333;
		letter-spacing: 4px;
	}

	.nav-list {
		flex: 1;
		padding: 20px 0;
	}

	.nav-item {
		display: flex;
		align-items: center;
		padding: 15px 25px;
		cursor: pointer;
		color: #666;
		transition: all 0.2s;
		border-left: 4px solid transparent;
	}
	
	.nav-item:hover {
		background-color: #f8f8f8;
	}

	.nav-item.active {
		background-color: #eff6fc;
		color: #0078D4;
		border-left-color: #0078D4;
		font-weight: 600;
	}

	.nav-item .icon {
		margin-right: 15px;
		font-size: 18px;
	}

	.sidebar-footer {
		padding: 20px;
		border-top: 1px solid #f0f0f0;
	}
	.user-brief {
		display: flex;
		align-items: center;
	}
	.avatar {
		width: 32px;
		height: 32px;
		border-radius: 10rpx;
		margin-right: 10px;
		background: #ccc;
	}
	.username {
		font-size: 14px;
		font-weight: bold;
		color: #333;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	/* ============ 主内容区样式 ============ */
	.main-content {
		flex: 1;
		padding: 30px;
		height: 100vh;
		box-sizing: border-box;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
	}
	.page-title {
		font-size: 24px;
		font-weight: 600;
		color: #323130;
	}

	/* === 模块 1: 状态卡片 === */
	.status-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 20px;
	}
	.metric-card {
		background: white;
		padding: 25px;
		border-radius: 4px; /* 微软风格直角 */
		box-shadow: 0 2px 8px rgba(0,0,0,0.05);
		display: flex;
		align-items: center;
	}
	.metric-icon {
		width: 50px;
		height: 50px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
		margin-right: 20px;
	}
	.tps-color { background: #e0f2f1; color: #009688; }
	.online-color { background: #e3f2fd; color: #2196f3; }
	
	.metric-info { display: flex; flex-direction: column; }
	.metric-label { font-size: 14px; color: #666; }
	.metric-value { font-size: 24px; font-weight: bold; color: #333; margin: 4px 0; }
	.metric-sub { font-size: 12px; color: #999; }

	/* === 模块 2: 方块查询 (移植样式) === */
	.query-layout {
		display: flex;
		gap: 20px;
		flex-wrap: wrap; /* 适配小屏幕 */
	}
	
	.query-card {
		background: #1a2a6c; /* 保持你原来的深色风格，或者改为白色以匹配微软风 */
		/* 这里为了保留你的设计，使用深色背景，但做了一些扁平化处理 */
		background: linear-gradient(135deg, #1a2a6c 0%, #2c3e50 100%);
		border-radius: 8px;
		padding: 20px;
		color: #f0f0f0;
		box-shadow: 0 4px 12px rgba(0,0,0,0.15);
	}
	
	.form-card { flex: 1; min-width: 300px; }
	.result-card { flex: 2; min-width: 300px; display: flex; flex-direction: column; max-height: 800px;}

	.card-header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; }
	.card-title { font-size: 18px; font-weight: 600; color: #6e9de4; }
	.result-badge { font-size: 12px; background: rgba(110, 157, 228, 0.2); padding: 2px 8px; border-radius: 10px; }

	.form-group { margin-bottom: 15px; }
	.label { display: block; margin-bottom: 6px; font-size: 14px; color: #c0c0ff; }
	
	/* 输入框样式移植 */
	.ms-input, .picker-box {
		background: rgba(0, 0, 0, 0.3);
		border: 1px solid rgba(110, 157, 228, 0.5);
		color: white;
		padding: 10px;
		border-radius: 4px;
		font-size: 14px;
	}
	.coord-inputs { display: flex; gap: 10px; }
	.coord-input { flex: 1; background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(110, 157, 228, 0.5); color: white; padding: 10px; border-radius: 4px; text-align: center; }

	.ms-btn {
		background: linear-gradient(135deg, #4a6fa5, #6e9de4);
		color: white;
		border: none;
		border-radius: 4px;
		padding: 12px;
		font-size: 16px;
		width: 100%;
		margin-top: 20px;
		cursor: pointer;
	}
	.ms-btn:active { opacity: 0.9; }

	.tips-box { margin-top: 20px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 4px; border-left: 3px solid #6e9de4; }
	.tips-title { color: #6e9de4; font-weight: bold; font-size: 14px; display: block; margin-bottom: 5px; }
	.tips-text { font-size: 12px; color: #ccc; display: block; line-height: 1.5; }

	/* 结果控制台样式 */
	.result-console {
		flex: 1;
		background: rgba(10, 15, 25, 0.5);
		border-radius: 4px;
		padding: 10px;
		overflow-y: auto;
		height: 400px; /* 固定高度以便滚动 */
		font-family: 'Consolas', monospace;
	}
	
	.log-item {
		padding: 8px 0;
		border-bottom: 1px solid rgba(255,255,255,0.05);
		font-size: 13px;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px;
	}
	.log-time { color: #ffa500; }
	.log-coord { color: #6ec5ff; }
	.log-user { color: #4aff4a; font-weight: bold; }
	.log-block { color: #ff6ec7; }
	
	.log-action { padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold; }
	.act-break { background: rgba(220, 53, 69, 0.3); color: #ff6b6b; }
	.act-place { background: rgba(40, 167, 69, 0.3); color: #6bff6b; }
	.act-use   { background: rgba(23, 162, 184, 0.3); color: #6bdfff; }

	.console-footer {
		margin-top: 10px;
		display: flex;
		justify-content: space-between;
		font-size: 12px;
		color: #6e9de4;
	}
	.empty-text { color: #666; text-align: center; display: block; margin-top: 50px; }

	/* === 模块 3: 空状态 === */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 400px;
		color: #999;
	}
	.empty-icon { font-size: 60px; margin-bottom: 20px; }

	/* 动画 */
	.fade-in { animation: fadeIn 0.4s ease-out; }
	@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

	/* 移动端适配 */
	@media (max-width: 768px) {
		.dashboard-container { flex-direction: column; }
		.sidebar { width: 100%; height: auto; border-right: none; border-bottom: 1px solid #ddd; }
		.nav-list { display: flex; overflow-x: auto; padding: 0; }
		.nav-item { flex: 1; justify-content: center; padding: 15px 10px; }
		.nav-item text:last-child { display: none; } /* 手机端只显图标 */
		.sidebar-footer { display: none; }
		.main-content { padding: 15px; }
		.query-layout { flex-direction: column; }
	}
	.refresh-bn{
		width: 10%;
		background: linear-gradient(135deg, #12B7F5, #2196f3); /* QQ 风格蓝 */
		color: white;
		border-radius: 50rpx;
		font-size: 32rpx;
		font-weight: bold;
		box-shadow: 0 4rpx 5rpx rgba(33, 150, 243, 0.3);
	}
	.player-section {
	    margin-top: 30px;
	    background: #ffffff;
	    padding: 20px;
	    border-radius: 4px;
	    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
	}
	
	.section-subtitle {
	    font-size: 16px;
	    font-weight: 600;
	    color: #333;
	    margin-bottom: 20px;
	    display: block;
	    padding-left: 10px;
	    border-left: 4px solid #0078D4; /* 微软蓝装饰条 */
	}
	
	.player-grid {
	    display: flex;
	    flex-wrap: wrap;
	    gap: 15px;
	}
	
	.player-card {
	    display: flex;
	    flex-direction: column;
	    align-items: center;
	    width: 80px; /* 每个格子的宽度 */
	    padding: 10px;
	    border-radius: 8px;
	    transition: background-color 0.2s;
	}
	
	.player-card:hover {
	    background-color: #f3f2f1;
	}
	
	.p-avatar {
	    width: 48px;
	    height: 48px;
	    border-radius: 8px; /* 圆角头像 */
	    background-color: #eee;
	    margin-bottom: 8px;
	    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
	}
	
	.p-name {
	    font-size: 12px;
	    color: #333;
	    text-align: center;
	    word-break: break-all;
	    line-height: 1.2;
	}
	
	.empty-player {
	    width: 100%;
	    padding: 30px;
	    text-align: center;
	    color: #999;
	    font-size: 14px;
	}
	
	/* 个人信息卡片样式 */
	.profile-card {
	    background: #fff;
	    border-radius: 8px;
	    overflow: hidden;
	    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
	}
	
	.profile-header-bg {
	    height: 80px;
	    background: linear-gradient(135deg, #0078D4, #50E3C2);
	}
	
	.profile-content {
	    padding: 0 20px 20px;
	    margin-top: -40px; /* 让头像浮上来 */
	    display: flex;
	    flex-direction: column;
	    align-items: center;
	    border-bottom: 1px solid #eee;
	}
	
	.profile-avatar {
	    width: 80px;
	    height: 80px;
	    border-radius: 12px;
	    border: 4px solid #fff;
	    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
	    margin-bottom: 10px;
	}
	
	.profile-names {
	    text-align: center;
	    margin-bottom: 15px;
	}
	
	.p-name-big {
	    font-size: 24px;
	    font-weight: bold;
	    color: #333;
	    display: block;
	}
	
	.p-uuid {
	    font-size: 12px;
	    color: #999;
	    font-family: monospace;
	}
	
	/* 白名单徽章 */
	.whitelist-badge {
	    display: flex;
	    align-items: center;
	    padding: 6px 16px;
	    border-radius: 20px;
	    font-size: 14px;
	    font-weight: 600;
	}
	
	.whitelist-badge.valid {
	    background-color: #e6fffa;
	    color: #009688;
	    border: 1px solid #b2f5ea;
	}
	
	.whitelist-badge.invalid {
	    background-color: #fff5f5;
	    color: #e53e3e;
	    border: 1px solid #feb2b2;
	}
	
	.badge-icon { margin-right: 6px; }
	
	/* 信息列表 */
	.info-list {
	    padding: 20px;
	}
	
	.info-item {
	    display: flex;
	    justify-content: space-between;
	    padding: 12px 0;
	    border-bottom: 1px solid #f7f7f7;
	    font-size: 14px;
	}
	
	.info-item:last-child { border-bottom: none; }
	.info-item .label { color: #666; }
	.info-item .value { color: #333; font-weight: 500; }
	.info-item .highlight { color: #0078D4; }
	
	.warning-box {
	    margin: 0 20px 20px;
	    padding: 10px;
	    background: #fffbe6;
	    border: 1px solid #ffe58f;
	    border-radius: 4px;
	    font-size: 12px;
	    color: #faad14;
	    text-align: center;
	}
	.badges-row {
	    display: flex;
	    gap: 10px; /* 徽章之间的间距 */
	    flex-wrap: wrap;
	    justify-content: center;
	}
	.op-badge {
	    display: flex;
	    align-items: center;
	    padding: 6px 16px;
	    border-radius: 20px;
	    font-size: 14px;
	    font-weight: 600;
	    
	    background: linear-gradient(135deg, #FFF3E0, #FFE0B2); /* 淡金背景 */
	    color: #F57C00; /* 深橙/金色字体 */
	    border: 1px solid #FFCC80;
	    box-shadow: 0 2px 5px rgba(255, 160, 0, 0.2);
	}
</style>