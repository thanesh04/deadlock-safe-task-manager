"""
Integration tests for Scheduler Flask routes and endpoints.
"""
import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_scheduler_page_loads(client):
    response = client.get('/scheduler')
    assert response.status_code == 200
    assert b"CPU & Task Scheduler" in response.data or b"CPU &amp; Task Scheduler" in response.data

def test_api_scheduler_state(client):
    response = client.get('/api/scheduler/state')
    assert response.status_code == 200
    data = response.get_json()
    assert "clock" in data
    assert "tasks" in data
    assert "metrics" in data

def test_api_scheduler_tick(client):
    # Reset first
    client.post('/api/scheduler/init', json={'preset': 'balanced', 'policy': 'RR', 'mode': 'DEADLOCK_AWARE'})
    response = client.post('/api/scheduler/tick')
    assert response.status_code == 200
    data = response.get_json()
    assert data["clock"] == 1
    assert len(data["gantt_timeline"]) == 1

def test_api_scheduler_run_all(client):
    client.post('/api/scheduler/init', json={'preset': 'balanced', 'policy': 'RR', 'mode': 'DEADLOCK_AWARE'})
    response = client.post('/api/scheduler/run', json={'max_ticks': 40})
    assert response.status_code == 200
    data = response.get_json()
    assert data["clock"] > 1
    assert data["is_completed"] is True

def test_api_scheduler_init_modes(client):
    # Naive mode
    res = client.post('/api/scheduler/init', json={'preset': 'naive_vs_safe', 'policy': 'RR', 'mode': 'NAIVE'})
    assert res.status_code == 200
    assert res.get_json()["state"]["mode"] == "NAIVE"

    # Deadlock aware mode
    res2 = client.post('/api/scheduler/init', json={'preset': 'starvation_demo', 'policy': 'PRIORITY', 'mode': 'DEADLOCK_AWARE'})
    assert res2.status_code == 200
    assert res2.get_json()["state"]["policy"] == "PRIORITY"
