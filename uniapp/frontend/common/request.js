const BASE_URL = 'http://localhost:21007/api'; 

export const request = (options) => {
	return new Promise((resolve, reject) => {
		// 1. 从本地存储获取之前保存的 Cookie
		const userCookie = uni.getStorageSync('user_cookie');
		
		// 2. 准备请求头
		let header = {
			'Content-Type': 'application/json',
			...options.header
		};
		
		// 3. 如果有 Cookie，手动加到 Header 里
		if (userCookie) {
			header['Cookie'] = userCookie;
		}

		uni.request({
			url: BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data || {},
			header: header, // 使用处理后的 header
			withCredentials: true, // H5 模式下需要这个
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
				} else {
					// 如果是 401，说明 Cookie 失效或未登录
					if (res.statusCode === 401) {
						uni.showToast({ title: '请先登录', icon: 'none' });
						// 可选：自动跳转回登录页
						// uni.navigateTo({ url: '/pages/login/login' });
					} else {
						uni.showToast({ title: res.data.error || '请求失败', icon: 'none' });
					}
					reject(res.data);
				}
			},
			fail: (err) => {
				uni.showToast({ title: '网络连接失败', icon: 'none' });
				reject(err);
			}
		});
	});
};