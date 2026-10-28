"""
Routes and API endpoints for Deadlock-Aware CPU Scheduler.
"""
from flask import Blueprint, render_template, request, jsonify
from simulation.scheduler_manager import SchedulerManager

scheduler_bp = Blueprint('scheduler_page', __name__)

@scheduler_bp.route('/scheduler')
def index():
    return render_template('scheduler.html', active_page='scheduler')

# --- Scheduler REST API Endpoints ---
@scheduler_bp.route('/api/scheduler/state', methods=['GET'])
def get_scheduler_state():
    engine = SchedulerManager.get_engine()
    return jsonify(engine.get_state()), 200

@scheduler_bp.route('/api/scheduler/init', methods=['POST'])
def init_scheduler():
    data = request.get_json() or {}
    preset = data.get('preset', 'balanced')
    policy = data.get('policy', 'RR')
    mode = data.get('mode', 'DEADLOCK_AWARE')
    quantum = int(data.get('quantum', 2))
    aging_threshold = int(data.get('aging_threshold', 3))
    aging_enabled = bool(data.get('aging_enabled', True))

    if preset == 'database':
        engine = SchedulerManager.initialize_from_db(
            policy=policy, mode=mode, quantum=quantum,
            aging_threshold=aging_threshold, aging_enabled=aging_enabled
        )
    else:
        engine = SchedulerManager.initialize_preset(
            preset_name=preset, policy=policy, mode=mode, quantum=quantum,
            aging_threshold=aging_threshold, aging_enabled=aging_enabled
        )

    return jsonify({
        'message': f'Scheduler initialized with preset: {preset}',
        'state': engine.get_state()
    }), 200

@scheduler_bp.route('/api/scheduler/tick', methods=['POST'])
def tick_scheduler():
    state = SchedulerManager.tick()
    return jsonify(state), 200

@scheduler_bp.route('/api/scheduler/run', methods=['POST'])
def run_scheduler():
    data = request.get_json() or {}
    max_ticks = int(data.get('max_ticks', 60))
    state = SchedulerManager.run_all(max_ticks=max_ticks)
    return jsonify(state), 200

@scheduler_bp.route('/api/scheduler/reset', methods=['POST'])
def reset_scheduler():
    state = SchedulerManager.reset()
    return jsonify({
        'message': 'Scheduler simulation reset to initial state.',
        'state': state
    }), 200
