from routes.api import api_bp
from routes.dashboard import dashboard_bp
from routes.processes import processes_bp
from routes.resources import resources_bp
from routes.algorithms import algorithms_bp
from routes.scenarios import scenarios_bp
from routes.logs import logs_bp

__all__ = [
    'api_bp',
    'dashboard_bp',
    'processes_bp',
    'resources_bp',
    'algorithms_bp',
    'scenarios_bp',
    'logs_bp'
]
