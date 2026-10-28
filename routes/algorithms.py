from flask import Blueprint, render_template

algorithms_bp = Blueprint('algorithms_page', __name__)

@algorithms_bp.route('/safety')
def safety_view():
    return render_template('safety.html', active_page='safety')

@algorithms_bp.route('/resource-request')
def resource_request_view():
    return render_template('resource_request.html', active_page='resource_request')

@algorithms_bp.route('/deadlock-detection')
def deadlock_detection_view():
    return render_template('deadlock_detection.html', active_page='deadlock_detection')
