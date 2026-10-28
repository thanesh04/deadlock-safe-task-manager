from flask import Blueprint, render_template

processes_bp = Blueprint('processes_page', __name__)

@processes_bp.route('/processes')
def index():
    return render_template('processes.html', active_page='processes')
