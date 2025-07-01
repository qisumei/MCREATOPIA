# main/routes.py
from flask import Blueprint, render_template, send_from_directory, current_app

main_bp = Blueprint('main', __name__,
                    template_folder='../templates/main')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/rules')
def rules():
    return render_template('rules.html')

@main_bp.route('/mods')
def mods():
    return render_template('mods.html')

@main_bp.route('/guide')
def guide():
    return render_template('guide.html')

@main_bp.route('/donate')
def donate():
    return render_template('donate.html')

@main_bp.route('/static/questions.json')
def serve_questions():
    return send_from_directory(current_app.static_folder, 'questions.json')