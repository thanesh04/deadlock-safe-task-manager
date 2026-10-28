import pytest
from algorithms.bankers import BankersAlgorithm

def test_bankers_need_computation():
    processes = ['P0']
    resources = ['R0', 'R1']
    available = {'R0': 2, 'R1': 2}
    allocation = {'P0': {'R0': 1, 'R1': 2}}
    maximum = {'P0': {'R0': 4, 'R1': 5}}

    bankers = BankersAlgorithm(processes, resources, available, allocation, maximum)
    assert bankers.need['P0']['R0'] == 3
    assert bankers.need['P0']['R1'] == 3

def test_bankers_validation_negative_allocation():
    processes = ['P0']
    resources = ['R0']
    available = {'R0': 1}
    allocation = {'P0': {'R0': -1}}
    maximum = {'P0': {'R0': 2}}

    bankers = BankersAlgorithm(processes, resources, available, allocation, maximum)
    errors = bankers.validate_matrices()
    assert len(errors) > 0
    assert "negative allocation" in errors[0]

def test_bankers_validation_allocation_exceeds_maximum():
    processes = ['P0']
    resources = ['R0']
    available = {'R0': 5}
    allocation = {'P0': {'R0': 4}}
    maximum = {'P0': {'R0': 2}}

    bankers = BankersAlgorithm(processes, resources, available, allocation, maximum)
    errors = bankers.validate_matrices()
    assert len(errors) > 0
    assert "exceeds maximum claim" in errors[0]
