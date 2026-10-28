# Testing & Quality Assurance Report

## 1. Test Suite Summary

The test suite is built using `pytest` and verifies mathematical correctness, data consistency, validation rules, API endpoints, and recovery mechanisms across 26 automated unit and integration tests.

Run tests using:
```bash
.\venv\Scripts\pytest -v
```

---

## 2. Test Coverage Breakdown

### `test_safety.py`
- `test_safety_algorithm_safe_state`: Verifies standard 5-process 3-resource textbook safe state and safe sequence generation.
- `test_safety_algorithm_unsafe_state`: Tests state where available resources are insufficient to satisfy any remaining process need.
- `test_safety_algorithm_single_process_safe`: Verifies single process edge condition.
- `test_safety_algorithm_zero_allocation`: Verifies system where processes hold zero initial allocations.

### `test_bankers.py`
- `test_bankers_need_computation`: Verifies $\text{Need} = \text{Maximum} - \text{Allocation}$.
- `test_bankers_validation_negative_allocation`: Verifies rejection of negative allocation values.
- `test_bankers_validation_allocation_exceeds_maximum`: Verifies error reporting when allocation exceeds maximum claim.

### `test_resource_request.py`
- `test_safe_resource_request`: Validates safely grantable request (P1 requests [1, 0, 2]).
- `test_request_exceeds_need`: Verifies Step 1 rejection when request > need.
- `test_request_exceeds_available`: Verifies Step 2 rejection when request > available.
- `test_unsafe_request_denied`: Verifies Step 4 rollback when request results in an unsafe state.

### `test_deadlock_detection.py`
- `test_no_deadlock`: Verifies detection returns false when all requests can be satisfied.
- `test_two_process_deadlock`: Detects mutual circular wait between P1 and P2.
- `test_three_process_deadlock`: Detects 3-process circular wait (P1 &rarr; P2 &rarr; P3 &rarr; P1).
- `test_deadlock_with_one_independent_process`: Ensures independent process finishes while deadlocked processes are properly identified.

### `test_recovery.py`
- `test_termination_resolves_deadlock`: Verifies victim termination reclaims resources and resolves deadlock.
- `test_simulated_preemption`: Verifies resource transfer between victim and target processes.

### `test_validation.py`
- `test_validate_process_empty_pid`: Rejects empty PID.
- `test_validate_process_duplicate_pid`: Rejects duplicate process identifiers.
- `test_validate_resource_zero_or_negative`: Rejects zero or negative resource capacities.
- `test_validate_matrix_consistency_allocation_exceeds_max`: Validates matrix consistency rules.

### `test_process_manager.py` & `test_resource_manager.py`
- `test_process_lifecycle`: End-to-end process creation, allocation reduction, release, and termination.
- `test_resource_crud_and_safety_checks`: CRUD checks, preventing reduction of total below allocated, preventing deletion of allocated resources.

### `test_api.py`
- `test_api_load_scenario_and_safety_check`: Scenario loading via REST and safety execution.
- `test_api_deadlock_scenario_and_recovery`: Deadlock detection and recovery via REST API.
- `test_api_system_monitor`: Verifies psutil real-system telemetry endpoint.
