import pytest
from algorithms.safety import SafetyAlgorithm

def test_safety_algorithm_safe_state():
    processes = ['P0', 'P1', 'P2', 'P3', 'P4']
    resources = ['R0', 'R1', 'R2']
    available = {'R0': 3, 'R1': 3, 'R2': 2}
    allocation = {
        'P0': {'R0': 0, 'R1': 1, 'R2': 0},
        'P1': {'R0': 2, 'R1': 0, 'R2': 0},
        'P2': {'R0': 3, 'R1': 0, 'R2': 2},
        'P3': {'R0': 2, 'R1': 1, 'R2': 1},
        'P4': {'R0': 0, 'R1': 0, 'R2': 2}
    }
    maximum = {
        'P0': {'R0': 7, 'R1': 5, 'R2': 3},
        'P1': {'R0': 3, 'R1': 2, 'R2': 2},
        'P2': {'R0': 9, 'R1': 0, 'R2': 2},
        'P3': {'R0': 2, 'R1': 2, 'R2': 2},
        'P4': {'R0': 4, 'R1': 3, 'R2': 3}
    }

    algo = SafetyAlgorithm(processes, resources, available, allocation, maximum)
    result = algo.run()

    assert result['safe'] is True
    assert len(result['safe_sequence']) == 5
    assert len(result['unfinished_processes']) == 0
    assert result['safe_sequence'][0] == 'P1'
    assert len(result['steps']) == 5

def test_safety_algorithm_unsafe_state():
    processes = ['P0', 'P1']
    resources = ['R0']
    available = {'R0': 0}
    allocation = {
        'P0': {'R0': 1},
        'P1': {'R0': 1}
    }
    maximum = {
        'P0': {'R0': 2},
        'P1': {'R0': 2}
    }

    algo = SafetyAlgorithm(processes, resources, available, allocation, maximum)
    result = algo.run()

    assert result['safe'] is False
    assert len(result['safe_sequence']) == 0
    assert len(result['unfinished_processes']) == 2

def test_safety_algorithm_single_process_safe():
    processes = ['P0']
    resources = ['R0', 'R1']
    available = {'R0': 2, 'R1': 1}
    allocation = {'P0': {'R0': 1, 'R1': 0}}
    maximum = {'P0': {'R0': 3, 'R1': 1}}

    algo = SafetyAlgorithm(processes, resources, available, allocation, maximum)
    result = algo.run()

    assert result['safe'] is True
    assert result['safe_sequence'] == ['P0']

def test_safety_algorithm_zero_allocation():
    processes = ['P0', 'P1']
    resources = ['R0']
    available = {'R0': 5}
    allocation = {
        'P0': {'R0': 0},
        'P1': {'R0': 0}
    }
    maximum = {
        'P0': {'R0': 3},
        'P1': {'R0': 4}
    }

    algo = SafetyAlgorithm(processes, resources, available, allocation, maximum)
    result = algo.run()

    assert result['safe'] is True
    assert len(result['safe_sequence']) == 2
