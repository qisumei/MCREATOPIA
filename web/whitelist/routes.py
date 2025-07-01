# whitelist/routes.py
from flask import Blueprint, render_template, request, session, jsonify, current_app
import json
import os
import sqlite3

whitelist_bp = Blueprint('whitelist', __name__,
                         template_folder='../templates/whitelist',
                         url_prefix='/whitelist')

@whitelist_bp.route('/', methods=['GET', 'POST'])

def whitelist():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            conn = sqlite3.connect(current_app.config['DB_PATH'])
            c = conn.cursor()
            c.execute('SELECT game_id FROM users WHERE username = ?', (username,))
            game_id = c.fetchone()
            conn.close()
            if game_id:
                try:
                    base_dir = current_app.root_path
                    whitelist_path = os.path.join(base_dir, 'static', 'questions.json')
                    with open(whitelist_path, 'r+', encoding='utf-8') as f:
                        whitelist = json.load(f)
                        whitelist.append({'name': game_id[0]})
                        f.seek(0)
                        json.dump(whitelist, f, indent=2, ensure_ascii=False)
                        f.truncate()
                    return jsonify({'message': '已加入白名单'}), 200
                except FileNotFoundError:
                    return jsonify({'error': '白名单文件不存在'}), 404
            return jsonify({'error': '用户数据错误'}), 400
        return jsonify({'error': '未登录'}), 401
    return render_template('whitelist.html')