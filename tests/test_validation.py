import pytest
from simulation.validation import SimulationValidator

def test_validate_process_empty_pid():
    valid, msg = SimulationValidator.validate_process_data("", "Task", [])
    assert valid is False
    assert "PID cannot be empty" in msg

def test_validate_process_duplicate_pid():
    valid, msg = SimulationValidator.validate_process_data("P1", "Task", ["P1", "P2"])
    assert valid is False
    assert "already exists" in msg

def test_validate_resource_zero_or_negative():
    valid, msg = SimulationValidator.validate_resource_data("R1", "Memory", 0, [])
    assert valid is False
    assert "at least 1" in msg

def test_validate_matrix_consistency_allocation_exceeds_max():
    available = {'R1': 2}
    total = {'R1': 5}
    allocation = {'P1': {'R1': 3}}
    maximum = {'P1': {'R1': 2}}

    valid, errors = SimulationValidator.validate_matrix_consistency(available, total, allocation, maximum)
    assert valid is False
    assert any("exceeds maximum demand" in e for e in errors)
