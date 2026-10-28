import pytest
from algorithms.resource_request import ResourceRequestAlgorithm

@pytest.fixture
def standard_system():
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
    need = {
        p: {r: maximum[p][r] - allocation[p][r] for r in resources}
        for p in processes
    }
    return {
        'processes': processes,
        'resources': resources,
        'available': available,
        'allocation': allocation,
        'maximum': maximum,
        'need': need
    }

def test_safe_resource_request(standard_system):
    req_algo = ResourceRequestAlgorithm(**standard_system)
    # P1 requests (1, 0, 2)
    result = req_algo.evaluate_request('P1', {'R0': 1, 'R1': 0, 'R2': 2})
    assert result['granted'] is True
    assert result['step_failed'] is None
    assert 'safe_sequence' in result['safety_analysis']

def test_request_exceeds_need(standard_system):
    req_algo = ResourceRequestAlgorithm(**standard_system)
    # P1 need for R1 is 2, requesting 3 exceeds need
    result = req_algo.evaluate_request('P1', {'R0': 0, 'R1': 3, 'R2': 0})
    assert result['granted'] is False
    assert result['step_failed'] == 1
    assert "exceeds remaining need" in result['reason']

def test_request_exceeds_available(standard_system):
    req_algo = ResourceRequestAlgorithm(**standard_system)
    # P0 requests (0, 4, 0). Available R1 is only 3.
    result = req_algo.evaluate_request('P0', {'R0': 0, 'R1': 4, 'R2': 0})
    assert result['granted'] is False
    assert result['step_failed'] == 2
    assert "Insufficient available resources" in result['reason']

def test_unsafe_request_denied(standard_system):
    req_algo = ResourceRequestAlgorithm(**standard_system)
    # P0 requests (0, 3, 0). Need is (7, 4, 3) so 3 <= 4; Avail R1 is 3 >= 3.
    # But granting this leaves Available = (3, 0, 2) where every process needs R1 > 0!
    # Hence it causes an unsafe state and must be denied!
    result = req_algo.evaluate_request('P0', {'R0': 0, 'R1': 3, 'R2': 0})
    assert result['granted'] is False
    assert result['step_failed'] == 4
    assert "UNSAFE" in result['reason']
