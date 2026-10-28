from flask import Blueprint, render_template

scenarios_bp = Blueprint('scenarios_page', __name__)

@scenarios_bp.route('/scenarios')
def index():
    return render_template('scenarios.html', active_page='scenarios')
