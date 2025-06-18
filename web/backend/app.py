from flask import Flask, request, session, redirect, url_for, render_template, jsonify, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sk-114514'
#路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('whitelist'))
        return jsonify({'error': '用户名或密码错误'}), 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        game_id = request.form['game_id']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return jsonify({'error': '密码不一致'}), 400
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (game_id, username, password) VALUES (?, ?, ?)',
                      (game_id, username, generate_password_hash(password)))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return jsonify({'error': '用户名已存在'}), 400
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/whitelist', methods=['GET', 'POST'])
def whitelist():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT game_id FROM users WHERE username = ?', (username,))
            game_id = c.fetchone()
            conn.close()
            if game_id:
                try:
                    whitelist_path = os.path.join(BASE_DIR, 'templates', 'questions.json')
                    with open(whitelist_path, 'r+') as f:
                        whitelist = json.load(f)
                        whitelist.append({'name': game_id[0]})
                        f.seek(0)
                        json.dump(whitelist, f, indent=2)
                    return jsonify({'message': '已加入白名单'}), 200
                except FileNotFoundError:
                    return jsonify({'error': '白名单文件不存在'}), 404
            return jsonify({'error': '用户数据错误'}), 400
        return jsonify({'error': '未登录'}), 401
    return render_template('whitelist.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/mods')
def mods():
    return render_template('mods.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/static/questions.json')
def serve_questions():
    return send_from_directory(app.static_folder, 'questions.json')
if __name__ == '__main__':
    app.run(debug=True)