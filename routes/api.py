"""
REST API endpoints for the Deadlock-Safe Task Manager.
"""
from flask import Blueprint, request, jsonify
import psutil
from database.database import db
from database.models import Process, Resource, EventLog, Scenario, ProcessState
from simulation.process_manager import ProcessManager
from simulation.resource_manager import ResourceManager
from simulation.simulator import Simulator
from simulation.scenarios import ScenarioManager

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Process Endpoints ---
@api_bp.route('/processes', methods=['GET'])
def get_processes():
    processes = ProcessManager.get_all_processes()
    return jsonify([p.to_dict() for p in processes]), 200

@api_bp.route('/processes', methods=['POST'])
def create_process():
    data = request.get_json() or {}
    pid = data.get('pid')
    name = data.get('name')
    maximums = data.get('maximum', {})
    allocations = data.get('allocation', {})

    success, msg, proc = ProcessManager.create_process(pid, name, maximums, allocations)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg, 'process': proc.to_dict()}), 201

@api_bp.route('/processes/<int:proc_id>', methods=['DELETE'])
def delete_process(proc_id):
    success, msg = ProcessManager.delete_process(proc_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg}), 200

@api_bp.route('/processes/<int:proc_id>/terminate', methods=['POST'])
def terminate_process(proc_id):
    success, msg, released = ProcessManager.terminate_process(proc_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg, 'released': released}), 200

@api_bp.route('/processes/<int:proc_id>/complete', methods=['POST'])
def complete_process(proc_id):
    success, msg, released = ProcessManager.complete_process(proc_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg, 'released': released}), 200

@api_bp.route('/processes/<int:proc_id>/release', methods=['POST'])
def release_process_resources(proc_id):
    data = request.get_json() or {}
    release_dict = data.get('release', {})
    success, msg = ProcessManager.release_resources(proc_id, release_dict)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg}), 200

# --- Resource Endpoints ---
@api_bp.route('/resources', methods=['GET'])
def get_resources():
    resources = ResourceManager.get_all_resources()
    return jsonify([r.to_dict() for r in resources]), 200

@api_bp.route('/resources', methods=['POST'])
def create_resource():
    data = request.get_json() or {}
    rid = data.get('resource_id')
    name = data.get('name')
    total = data.get('total_instances', 1)

    try:
        total = int(total)
    except (ValueError, TypeError):
        return jsonify({'error': 'Total instances must be an integer.'}), 400

    success, msg, res = ResourceManager.create_resource(rid, name, total)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg, 'resource': res.to_dict()}), 201

@api_bp.route('/resources/<int:res_id>', methods=['PUT', 'POST'])
def update_resource(res_id):
    data = request.get_json() or {}
    name = data.get('name')
    total = data.get('total_instances')

    try:
        total = int(total)
    except (ValueError, TypeError):
        return jsonify({'error': 'Total instances must be an integer.'}), 400

    success, msg = ResourceManager.update_resource(res_id, name, total)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg}), 200

@api_bp.route('/resources/<int:res_id>', methods=['DELETE'])
def delete_resource(res_id):
    success, msg = ResourceManager.delete_resource(res_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg}), 200

# --- System Matrices ---
@api_bp.route('/matrices', methods=['GET'])
def get_matrices():
    matrices = Simulator.get_system_matrices()
    return jsonify(matrices), 200

# --- Banker's Safety Algorithm ---
@api_bp.route('/safety-check', methods=['POST', 'GET'])
def run_safety_check():
    result = Simulator.check_safety()
    return jsonify(result), 200

# --- Banker's Resource Request ---
@api_bp.route('/resource-request', methods=['POST'])
def make_resource_request():
    data = request.get_json() or {}
    pid = data.get('pid')
    request_vector = data.get('request', {})

    if not pid:
        return jsonify({'error': 'Process PID is required.'}), 400

    result = Simulator.process_resource_request(pid, request_vector)
    if not result.get('success', True):
        return jsonify({'error': result.get('message', 'Request processing failed.')}), 400

    return jsonify(result), 200

# --- Deadlock Detection ---
@api_bp.route('/deadlock-detection', methods=['POST', 'GET'])
def run_deadlock_detection():
    result = Simulator.detect_deadlock()
    return jsonify(result), 200

# --- Deadlock Recovery ---
@api_bp.route('/recovery', methods=['POST'])
def recover_deadlock():
    data = request.get_json() or {}
    action_type = data.get('action_type', 'terminate')
    params = data.get('params', {})

    result = Simulator.recover_deadlock(action_type, params)
    return jsonify(result), 200

# --- Graphs Data ---
@api_bp.route('/graphs', methods=['GET'])
def get_graphs():
    graphs_data = Simulator.get_graphs_data()
    return jsonify(graphs_data), 200

# --- Scenario Endpoints ---
@api_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    scenarios = ScenarioManager.get_all_scenarios()
    return jsonify(scenarios), 200

@api_bp.route('/scenarios/load', methods=['POST'])
def load_scenario():
    data = request.get_json() or {}
    scenario_id = data.get('scenario_id')
    if not scenario_id:
        return jsonify({'error': 'Scenario ID or key is required.'}), 400

    result = ScenarioManager.load_scenario(scenario_id)
    if not result.get('success'):
        return jsonify({'error': result.get('message', 'Failed to load scenario.')}), 400
    return jsonify(result), 200

@api_bp.route('/scenarios/save', methods=['POST'])
def save_custom_scenario():
    data = request.get_json() or {}
    name = data.get('name')
    desc = data.get('description', '')
    config = data.get('configuration', {})

    success, msg = ScenarioManager.save_custom_scenario(name, desc, config)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg}), 201

# --- Simulation Reset / Clear ---
@api_bp.route('/simulation/reset', methods=['POST'])
def reset_simulation():
    # Reload default safe state scenario
    result = ScenarioManager.load_scenario('safe_state')
    return jsonify({'message': 'Simulation reset to default safe state scenario.', 'result': result}), 200

@api_bp.route('/simulation/clear', methods=['POST'])
def clear_simulation():
    Simulator.clear_all_data()
    db.session.add(EventLog(event_type="SIMULATION_CLEARED", description="All simulation data cleared."))
    db.session.commit()
    return jsonify({'message': 'All simulation data cleared.'}), 200

# --- Event Logs ---
@api_bp.route('/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    logs = EventLog.query.order_by(EventLog.timestamp.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200

@api_bp.route('/logs', methods=['DELETE'])
def clear_logs():
    EventLog.query.delete()
    db.session.commit()
    return jsonify({'message': 'Logs cleared.'}), 200

# --- Real System Monitor (clearly separated) ---
@api_bp.route('/system-monitor', methods=['GET'])
def get_real_system_monitor():
    """
    Returns actual OS hardware and process metrics using psutil.
    Educational note: Real OS metrics are NEVER fed into the simulated Deadlock/Banker's algorithms.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        os_proc_count = len(psutil.pids())
        disk_usage = psutil.disk_usage('/')

        return jsonify({
            'source': 'REAL_OS_SYSTEM_MONITOR',
            'warning': 'Simulation processes are independent of real OS metrics.',
            'cpu_percent': cpu_percent,
            'cpu_cores_logical': psutil.cpu_count(logical=True),
            'cpu_cores_physical': psutil.cpu_count(logical=False),
            'memory_total_gb': round(virtual_mem.total / (1024**3), 2),
            'memory_used_gb': round(virtual_mem.used / (1024**3), 2),
            'memory_percent': virtual_mem.percent,
            'swap_percent': swap_mem.percent,
            'disk_percent': disk_usage.percent,
            'real_process_count': os_proc_count
        }), 200
    except Exception as e:
        return jsonify({'error': f"Failed to retrieve system metrics: {str(e)}"}), 500
