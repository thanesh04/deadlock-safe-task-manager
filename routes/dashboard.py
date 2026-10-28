from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html', active_page='dashboard')

@dashboard_bp.route('/matrices')
def matrices_view():
    return render_template('matrices.html', active_page='matrices')

@dashboard_bp.route('/graphs')
def graphs_view():
    return render_template('graphs.html', active_page='graphs')

@dashboard_bp.route('/monitor')
def monitor_view():
    return render_template('monitor.html', active_page='monitor')

@dashboard_bp.route('/documentation')
def documentation_view():
    return render_template('documentation.html', active_page='documentation')

@dashboard_bp.route('/settings')
def settings_view():
    return render_template('settings.html', active_page='settings')
