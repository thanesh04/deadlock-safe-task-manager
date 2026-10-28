import pytest
from app import create_app
from config import TestingConfig
from database.database import db
from database.models import Process, Resource, ProcessState
from simulation.process_manager import ProcessManager
from simulation.resource_manager import ResourceManager

@pytest.fixture
def app_ctx():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        from simulation.simulator import Simulator
        Simulator.clear_all_data()
        yield app
        db.session.remove()
        db.drop_all()

def test_process_lifecycle(app_ctx):
    # 1. Create a resource
    res_ok, _, res = ResourceManager.create_resource("R1", "Memory", 5)
    assert res_ok is True

    # 2. Create process with max=3, alloc=2
    p_ok, _, proc = ProcessManager.create_process("P1", "Worker", maximums={"R1": 3}, allocations={"R1": 2})
    assert p_ok is True
    assert proc.state == ProcessState.RUNNING

    # Verify resource available updated: 5 - 2 = 3
    r = ResourceManager.get_by_resource_id("R1")
    assert r.available_instances == 3

    # 3. Release 1 unit
    rel_ok, _ = ProcessManager.release_resources(proc.id, {"R1": 1})
    assert rel_ok is True
    r = ResourceManager.get_by_resource_id("R1")
    assert r.available_instances == 4

    # 4. Terminate process: releases remaining 1 unit
    term_ok, _, released = ProcessManager.terminate_process(proc.id)
    assert term_ok is True
    assert released["R1"] == 1
    r = ResourceManager.get_by_resource_id("R1")
    assert r.available_instances == 5
    assert proc.state == ProcessState.TERMINATED
