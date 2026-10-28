import pytest
from app import create_app
from config import TestingConfig
from database.database import db
from database.models import Resource
from simulation.resource_manager import ResourceManager
from simulation.process_manager import ProcessManager

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

def test_resource_crud_and_safety_checks(app_ctx):
    # 1. Create resource
    ok, _, res = ResourceManager.create_resource("CPU", "Processor", 4)
    assert ok is True
    assert res.total_instances == 4
    assert res.available_instances == 4

    # 2. Allocate 3 instances to a process
    p_ok, _, proc = ProcessManager.create_process("P1", "Computation", maximums={"CPU": 4}, allocations={"CPU": 3})
    assert p_ok is True

    # 3. Try to reduce total instances below 3 -> should fail
    update_ok, msg = ResourceManager.update_resource(res.id, "Processor", 2)
    assert update_ok is False
    assert "currently allocated" in msg

    # 4. Try to delete resource with active allocation -> should fail
    del_ok, del_msg = ResourceManager.delete_resource(res.id)
    assert del_ok is False
    assert "active allocations" in del_msg

    # 5. Increase total instances to 6 -> should succeed
    update_ok2, _ = ResourceManager.update_resource(res.id, "Processor Multi-core", 6)
    assert update_ok2 is True
    assert res.available_instances == 3  # 6 total - 3 allocated = 3 available
