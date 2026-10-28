from flask import Blueprint, render_template

resources_bp = Blueprint('resources_page', __name__)

@resources_bp.route('/resources')
def index():
    return render_template('resources.html', active_page='resources')
