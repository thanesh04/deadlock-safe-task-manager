import pytest
from algorithms.deadlock_detection import DeadlockDetectionAlgorithm

def test_no_deadlock():
    processes = ['P0', 'P1']
    resources = ['R1']
    available = {'R1': 1}
    allocation = {'P0': {'R1': 1}, 'P1': {'R1': 0}}
    request = {'P0': {'R1': 0}, 'P1': {'R1': 1}}

    detector = DeadlockDetectionAlgorithm(processes, resources, available, allocation, request)
    result = detector.run()

    assert result['deadlock'] is False
    assert len(result['deadlocked_processes']) == 0

def test_two_process_deadlock():
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

    detector = DeadlockDetectionAlgorithm(processes, resources, available, allocation, request)
    result = detector.run()

    assert result['deadlock'] is True
    assert set(result['deadlocked_processes']) == {'P1', 'P2'}

def test_three_process_deadlock():
    processes = ['P1', 'P2', 'P3']
    resources = ['R1', 'R2', 'R3']
    available = {'R1': 0, 'R2': 0, 'R3': 0}
    allocation = {
        'P1': {'R1': 1, 'R2': 0, 'R3': 0},
        'P2': {'R1': 0, 'R2': 1, 'R3': 0},
        'P3': {'R1': 0, 'R2': 0, 'R3': 1}
    }
    request = {
        'P1': {'R1': 0, 'R2': 1, 'R3': 0},
        'P2': {'R1': 0, 'R2': 0, 'R3': 1},
        'P3': {'R1': 1, 'R2': 0, 'R3': 0}
    }

    detector = DeadlockDetectionAlgorithm(processes, resources, available, allocation, request)
    result = detector.run()

    assert result['deadlock'] is True
    assert set(result['deadlocked_processes']) == {'P1', 'P2', 'P3'}

def test_deadlock_with_one_independent_process():
    # P1 and P2 in deadlock, P3 has no request and finishes
    processes = ['P1', 'P2', 'P3']
    resources = ['R1', 'R2']
    available = {'R1': 0, 'R2': 0}
    allocation = {
        'P1': {'R1': 1, 'R2': 0},
        'P2': {'R1': 0, 'R2': 1},
        'P3': {'R1': 0, 'R2': 0}
    }
    request = {
        'P1': {'R1': 0, 'R2': 1},
        'P2': {'R1': 1, 'R2': 0},
        'P3': {'R1': 0, 'R2': 0}
    }

    detector = DeadlockDetectionAlgorithm(processes, resources, available, allocation, request)
    result = detector.run()

    assert result['deadlock'] is True
    assert set(result['deadlocked_processes']) == {'P1', 'P2'}
    assert 'P3' not in result['deadlocked_processes']
