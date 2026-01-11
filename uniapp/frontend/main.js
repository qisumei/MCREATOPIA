// 引入根组件
import App from './App'

// =======================
// Vue2 环境入口（非 VUE3）
// =======================
// #ifndef VUE3
import Vue from 'vue'                     // 引入 Vue2
import './uni.promisify.adaptor'          // uni-app Promise 适配（Vue2 必须）
Vue.config.productionTip = false          // 关闭生产环境提示
App.mpType = 'app'                        // 指定应用类型

const app = new Vue({
  ...App                                 // 挂载根组件配置
})
app.$mount()                             // 挂载应用
// #endif

// =======================
// Vue3 环境入口（VUE3）
// =======================
// #ifdef VUE3
import { createSSRApp } from 'vue'        // Vue3 创建应用实例（uni-app 统一入口）

export function createApp() {
  const app = createSSRApp(App)           // 创建 Vue3 应用
  return {
    app                                  // 返回给 uni-app 运行时
  }
}
// #endif
