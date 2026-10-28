import pytest
from algorithms.recovery import DeadlockRecovery

def test_termination_resolves_deadlock():
    processes = ['P1', 'P2']
    resources = ['R1', 'R2']
    available = {'R1': 0, 'R2': 0}
    allocation = {
        'P1': {'R1': 1, 'R2': 0},
        'P2': {'R1': 0, 'R2': 1}
    }
    request = {
        'P1': {'R1': 0, 'R2': 1},
        'P2': {'R1': 1, 'R2': 0}
    }

    recovery = DeadlockRecovery(processes, resources, available, allocation, request)
    # Terminate P1
    result = recovery.simulate_termination(['P1'])

    assert result['deadlock_resolved'] is True
    assert result['released_resources']['R1'] == 1
    assert result['new_available']['R1'] == 1
    assert 'P1' in result['terminated_processes']

def test_simulated_preemption():
    processes = ['P1', 'P2']
    resources = ['R1', 'R2']
    available = {'R1': 0, 'R2': 0}
    allocation = {
        'P1': {'R1': 1, 'R2': 0},
        'P2': {'R1': 0, 'R2': 1}
    }
    request = {
        'P1': {'R1': 0, 'R2': 1},
        'P2': {'R1': 1, 'R2': 0}
    }

    recovery = DeadlockRecovery(processes, resources, available, allocation, request)
    # Preempt R1 from P1 to P2
    result = recovery.simulate_preemption(victim_pid='P1', target_pid='P2', resource_id='R1', quantity=1)

    assert result['success'] is True
    assert result['preempted_quantity'] == 1
