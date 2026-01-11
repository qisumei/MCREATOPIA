from flask import Flask  # 从 Flask 导入核心应用类
from flask_cors import CORS  # 导入跨域扩展 CORS 用于处理前端跨域请求
from db import close_db  # 导入关闭数据库的回调函数

def create_app():
    app = Flask(__name__)  # 创建 Flask 应用实例
    # ================= 跨域配置 =================
    CORS(app, supports_credentials=True, resources={  # 对整个应用启用 CORS，允许携带凭证（cookies）
        r"/*": {
            "origins": [
                "http://localhost:5173",  # 允许来自 Vite 开发服务器的请求
                "http://localhost:8080",  # 允许来自 HBuilderX 或其他本地 8080 的请求
                "http://127.0.0.1:5173",  # 允许环回地址 5173
                "http://127.0.0.1:8080"  # 允许环回地址 8080
            ]
        }
    })
    # ==========================================

    # ================= 配置 =================
    app.config['CLIENT_ID'] = ""  # 微软 OAuth 客户端 ID
    app.config['CLIENT_SECRET'] = ""  # 微软 OAuth 客户端密钥（注意：敏感信息应在生产中使用环境变量）
    app.config['REDIRECT_URI'] = "http://localhost:21007/callback"  # OAuth 回调地址
    app.config['DB_PATH'] = "database.db"  # 本地 SQLite 数据库路径
    
    # RCON 和 服务器配置
    app.config['RCON_IP'] = "k1.dimc.cloud"  # Minecraft RCON 服务主机
    app.config['RCON_PORT'] = 21014  # RCON 端口
    app.config['RCON_PASSWORD'] = "simibubiwcnm"  # RCON 密码
    app.config['MC_SERVER_IP'] = "k1.dimc.cloud:21015"  # Minecraft 游戏服务器地址（带端口）
    app.config['PORT'] = 21007  # 应用运行端口
    # ==========================================
    
    # ================= 注册蓝图 =================
    from auth.routes import auth_bp  # 导入认证蓝图
    from main.routes import main_bp  # 导入主功能蓝图
    
    app.register_blueprint(auth_bp)  # 注册认证路由
    app.register_blueprint(main_bp)  # 注册主路由

    # 注册数据库清理
    app.teardown_appcontext(close_db)  # 在应用上下文结束时调用 close_db 以关闭数据库连接

    @app.route('/api/health')  # 注册健康检查路由
    def health():
        return {"status": "ok", "version": "2.0.0"}  # 返回简单的健康状态 JSON

    return app  # 返回应用实例

if __name__ == "__main__":  # 仅在作为脚本直接运行时启动开发服务器
    app = create_app()  # 创建应用
    print(f"MCREATOPIA 后端已启动: http://localhost:{app.config['PORT']}")  # 启动提示信息
    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)  # 以调试模式运行在指定端口，监听所有地址