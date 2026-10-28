import pytest
from app import create_app
from config import TestingConfig
from database.database import db

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_api_load_scenario_and_safety_check(client):
    # Load safe state scenario
    res = client.post('/api/scenarios/load', json={'scenario_id': 'safe_state'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # Run safety check
    safety_res = client.post('/api/safety-check')
    assert safety_res.status_code == 200
    s_data = safety_res.get_json()
    assert s_data['safe'] is True
    assert len(s_data['safe_sequence']) == 5

def test_api_deadlock_scenario_and_recovery(client):
    # Load two-process deadlock scenario
    res = client.post('/api/scenarios/load', json={'scenario_id': 'two_process_deadlock'})
    assert res.status_code == 200

    # Run deadlock detection
    det_res = client.post('/api/deadlock-detection')
    assert det_res.status_code == 200
    d_data = det_res.get_json()
    assert d_data['deadlock'] is True
    assert len(d_data['deadlocked_processes']) == 2

    # Recover by terminating one victim
    rec_res = client.post('/api/recovery', json={
        'action_type': 'terminate',
        'params': {'pids': ['P1']}
    })
    assert rec_res.status_code == 200
    r_data = rec_res.get_json()
    assert r_data['deadlock_resolved'] is True

def test_api_system_monitor(client):
    res = client.get('/api/system-monitor')
    assert res.status_code == 200
    data = res.get_json()
    assert data['source'] == 'REAL_OS_SYSTEM_MONITOR'
    assert 'cpu_percent' in data
    assert 'memory_percent' in data
