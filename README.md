# 🎮 MCREATOPIA Minecraft 服务器 Web 管理平台

<div align="center">
  <img src="https://via.placeholder.com/800x200/1e3c72/ffffff?text=MCREATOPIA" alt="MCREATOPIA Banner">
  <p>现代化的Minecraft服务器管理解决方案</p>
</div>

## 🚀 概述

MCREATOPIA 是一个为 Minecraft 服务器设计的现代化 Web 管理平台，提供了玩家账户系统、白名单管理、服务器信息展示和内容分发等功能。基于 Python Flask 框架构建，采用蓝图架构实现模块化开发。

<div align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/flask-2.3.2-blue" alt="Flask">
</div>

## ✨ 功能亮点

| 功能 | 描述 | 
|------|------|
| 🚪 **玩家账户系统** | 安全可靠的注册、登录和会话管理 |
| 📝 **白名单管理** | 玩家一键申请加入服务器白名单 |
| 🏰 **服务器信息展示** | 全面的规则、模组介绍和入服指南 |
| 📁 **静态文件服务** | 高效的CSS/JS/JSON文件托管服务 |
| 📱 **响应式设计** | 在所有设备上完美展示的Minecraft主题界面 |

## 🧩 技术栈

- **后端**: Python Flask + SQLite
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite
- **安全**: Werkzeug 安全工具（密码哈希）
- **架构**: Flask 蓝图模块化设计

## ⚙️ 安装指南

### 前提条件
确保您已安装：
- Python 3.11+
- pip（Python包管理器）

### 1. 克隆仓库
git clone https://github.com/qisumei/MCREATOPIA.git
cd MCREATOPIA

1. 创建虚拟环境（推荐）
# Linux/MacOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# 🎮 MCREATOPIA Minecraft 服务器 Web 管理平台

<div align="center">
  <img src="https://via.placeholder.com/800x200/1e3c72/ffffff?text=MCREATOPIA" alt="MCREATOPIA Banner">
  <p>现代化的Minecraft服务器管理解决方案</p>
</div>

## 🚀 概述

MCREATOPIA 是一个为 Minecraft 服务器设计的现代化 Web 管理平台，提供了玩家账户系统、白名单管理、服务器信息展示和内容分发等功能。基于 Python Flask 框架构建，采用蓝图架构实现模块化开发。

<div align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/flask-2.3.2-blue" alt="Flask">
</div>

## ✨ 功能亮点

| 功能 | 描述 | 
|------|------|
| 🚪 **玩家账户系统** | 安全可靠的注册、登录和会话管理 |
| 📝 **白名单管理** | 玩家一键申请加入服务器白名单 |
| 🏰 **服务器信息展示** | 全面的规则、模组介绍和入服指南 |
| 📁 **静态文件服务** | 高效的CSS/JS/JSON文件托管服务 |
| 🔒 **安全认证** | 密码哈希存储，会话保护和用户隔离 |
| 📱 **响应式设计** | 在所有设备上完美展示的Minecraft主题界面 |

## 🧩 技术栈

- **后端**: Python Flask + SQLite
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite
- **安全**: Werkzeug 安全工具（密码哈希）
- **架构**: Flask 蓝图模块化设计

## ⚙️ 安装指南

### 前提条件
确保您已安装：
- Python 3.8+
- pip（Python包管理器）

1. 克隆仓库
git clone https://github.com/qisumei/MCREATOPIA.git
cd MCREATOPIA

2. 创建虚拟环境（推荐）
# Linux/MacOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

3. 安装依赖
pip install flask werkzeug
4. 初始化数据库
应用会自动创建数据库，如需手动初始化：
python
>>> from app import init_db
>>> init_db()

5. 运行服务器
python app.py

访问 http://localhost:5000 查看应用

🗂️ 项目结构

MCREATOPIA/
├── app.py                 # 主应用入口
├── auth/                  # 认证蓝图
│   ├── __init__.py
│   └── routes.py          # 登录/注册路由
├── main/                  # 主页面蓝图
│   ├── __init__.py
│   └── routes.py          # 主页、规则、模组等路由
├── whitelist/             # 白名单蓝图
│   ├── __init__.py
│   └── routes.py          # 白名单管理路由
├── templates/             # 网页模板
│   ├── auth/              # 认证相关模板
│   │   └── login.html     # 登录/注册页面
│   ├── main/              # 主蓝图模板
│   │   ├── index.html     # 主页
│   │   ├── rules.html     # 服务器规则
│   │   ├── mods.html      # 模组介绍
│   │   ├── guide.html     # 入服指南
│   │   └── donate.html    # 赞助鸣谢
│   └── whitelist/         # 白名单模板
│       └── whitelist.html # 白名单页面
├── static/                # 静态资源
│   ├── css/               # CSS 样式
│   │   └── style.css      # 主样式文件
│   ├── js/                # JavaScript
│   │   └── animation.js   # 动画脚本
│   └── questions.json     # 白名单题库数据文件
└── database.db            #数据库

蓝图路由总结
蓝图  路径  功能
​​auth​​  /auth/login   玩家登录
​​auth​​  /auth/register  玩家注册
​​main​​  / 服务器主页
​​main​​  /rules  服务器规则
​​main​​  /mods 服务器模组介绍
​​main​​  /guide  新玩家入服指南
​​main​​  /donate 赞助鸣谢页面
​​whitelist​​ /whitelist  白名单申请页面

创建新蓝图
mkdir new_feature
touch new_feature/__init__.py
touch new_feature/routes.py
在app.py中注册蓝图
from new_feature.routes import new_bp
app.register_blueprint(new_bp)

📜 许可证
本项目采用 MIT 许可证 - 查看 LICENSE 文件获取详细信息

🙏 鸣谢
感谢 ​​Mojang Studios​​ 开发 Minecraft
感谢 ​​Flask​​ 团队提供出色的Web框架
感谢所有​​贡献者​​和​​玩家​​的支持
特别感谢服务器管理团队的无私奉献

项目状态​​: v1.01
​​最后更新​​: 2025年7月1日