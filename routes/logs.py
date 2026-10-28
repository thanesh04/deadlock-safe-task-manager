from flask import Blueprint, render_template

logs_bp = Blueprint('logs_page', __name__)

@logs_bp.route('/logs')
def index():
    return render_template('logs.html', active_page='logs')
