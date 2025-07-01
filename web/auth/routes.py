# auth/routes.py
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

auth_bp = Blueprint('auth', __name__, 
                    template_folder='../templates/auth',
                    url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(current_app.config['DB_PATH'])
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('whitelist.whitelist'))
        return jsonify({'error': '用户名或密码错误'}), 401
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        game_id = request.form['game_id']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return jsonify({'error': '密码不一致'}), 400
        conn = sqlite3.connect(current_app.config['DB_PATH'])
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (game_id, username, password) VALUES (?, ?, ?)',
                      (game_id, username, generate_password_hash(password)))
            conn.commit()
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            return jsonify({'error': '用户名已存在'}), 400
        finally:
            conn.close()
    return render_template('login.html')