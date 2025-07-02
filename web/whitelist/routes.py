# whitelist/routes.py
from flask import Blueprint, render_template, request, session, jsonify, current_app
import sqlite3
import os
import json

whitelist_bp = Blueprint('whitelist', __name__,
                         template_folder='../templates/whitelist',
                         url_prefix='/whitelist')
def load_questions():
    base_dir = current_app.root_path
    quiz_path = os.path.join(base_dir, 'static', 'questions.json')
    try:
        with open(quiz_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f'题库加载失败: {e}')
        return {'questions': []}
# 加载题库
@whitelist_bp.route('/quiz', methods=['GET'])
def get_quiz():
    questions = load_questions().get('questions', [])
    return jsonify({
        'questions': [
            {
                'id': idx,
                'text': q['question'],
                'options': q['options']
            } for idx, q in enumerate(questions)
        ]
    })

# 处理答题提交
@whitelist_bp.route('/submit', methods=['POST'])
def submit_quiz():
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        # 获取用户答案
        user_answers = request.json.get('answers', [])
        questions = load_questions().get('questions', [])
        
        if len(user_answers) != len(questions):
            return jsonify({'error': '答题数量不匹配'}), 400
        
        # 计算得分和错题
        score = 0
        wrong_answers = []
        for idx, (user_ans, q) in enumerate(zip(user_answers, questions)):
            if user_ans == q['correct']:
                score += 1
            else:
                wrong_answers.append({
                    'index': idx + 1,
                    'question': q['question'],
                    'selected': q['options'][user_ans] if user_ans < len(q['options']) else '无效选择',
                    'correct': q['options'][q['correct']]
                })
        
        # 全部正确则添加到白名单
        if score == len(questions):
            conn = sqlite3.connect(current_app.config['DB_PATH'])
            c = conn.cursor()
            c.execute('SELECT game_id FROM users WHERE username = ?', (session['username'],))
            game_id = c.fetchone()
            conn.close()
            
            if not game_id:
                return jsonify({'error': '用户信息缺失'}), 400
            
            try:
                base_dir = current_app.root_path
                whitelist_path = os.path.join(base_dir, 'static', 'whitelist.json')
                
                # 确保白名单文件存在
                if not os.path.exists(whitelist_path):
                    with open(whitelist_path, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                
                with open(whitelist_path, 'r+', encoding='utf-8') as f:
                    whitelist = json.load(f)
                    # 避免重复添加
                    if not any(user['name'] == game_id[0] for user in whitelist):
                        whitelist.append({'name': game_id[0]})
                        f.seek(0)
                        json.dump(whitelist, f, indent=2, ensure_ascii=False)
                        f.truncate()
                
                return jsonify({
                    'success': True,
                    'score': score,
                    'message': '恭喜！满分通过，已加入白名单！'
                })
            except Exception as e:
                current_app.logger.error(f'白名单更新失败: {e}')
                return jsonify({'error': '白名单处理失败'}), 500
        
        return jsonify({
            'success': False,
            'score': score,
            'wrong_answers': wrong_answers,
            'total': len(questions)
        })
    
    except Exception as e:
        current_app.logger.error(f'答题处理异常: {e}')
        return jsonify({'error': '服务器处理错误'}), 500

# 显示答题页面
@whitelist_bp.route('/', methods=['GET'])
def whitelist():
    return render_template('whitelist.html')