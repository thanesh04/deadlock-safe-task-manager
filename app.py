import os
from flask import Flask, render_template, jsonify
from config import Config
from database.database import db
from database.models import Process, Resource, Scenario, EventLog
from simulation.scenarios import ScenarioManager
from routes.api import api_bp
from routes.dashboard import dashboard_bp
from routes.processes import processes_bp
from routes.resources import resources_bp
from routes.algorithms import algorithms_bp
from routes.scenarios import scenarios_bp
from routes.logs import logs_bp
from routes.scheduler import scheduler_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(processes_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(scenarios_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(scheduler_bp)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="<div class='container my-5 text-center'><h1>404</h1><p>Page Not Found</p><a href='/' class='btn btn-primary'>Back to Dashboard</a></div>"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': 'Internal server error occurred.'}), 500

    # Initialize database tables and default initial scenario
    with app.app_context():
        db.create_all()
        # If no resources or processes exist, load default safe state scenario
        if Resource.query.count() == 0 and Process.query.count() == 0:
            ScenarioManager.load_scenario('safe_state')

    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print(" Deadlock-Safe Task Manager - Operating Systems Simulation")
    print(" Server running on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
