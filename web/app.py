# app.py
from flask import Flask, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sk-114514'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['DB_PATH'] = os.path.join(BASE_DIR, 'database.db')

# 初始化数据库
def init_db():
    conn = sqlite3.connect(app.config['DB_PATH'])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# 延迟导入蓝图 - 解决循环导入问题
# 必须在创建app后导入蓝图
from auth.routes import auth_bp
from main.routes import main_bp
from whitelist.routes import whitelist_bp

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(whitelist_bp)

init_db()
@app.route('/test')
def test():
    return "应用程序配置正确！"
if __name__ == '__main__':
    app.run(debug=True)