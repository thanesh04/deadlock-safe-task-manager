"""
Banker's Algorithm implementation for Deadlock Avoidance.
Coordinates the calculation of Need matrices, validation, and executes the Safety Algorithm.
"""
from typing import Dict, List, Any
from algorithms.safety import SafetyAlgorithm

class BankersAlgorithm:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        available: Dict[str, int],
        allocation: Dict[str, Dict[str, int]],
        maximum: Dict[str, Dict[str, int]]
    ):
        self.processes = processes
        self.resources = resources
        self.available = available
        self.allocation = allocation
        self.maximum = maximum
        self.need = self._compute_need()

    def _compute_need(self) -> Dict[str, Dict[str, int]]:
        """Compute Need[i][j] = Maximum[i][j] - Allocation[i][j]"""
        need = {}
        for p in self.processes:
            need[p] = {}
            for r in self.resources:
                max_val = self.maximum.get(p, {}).get(r, 0)
                alloc_val = self.allocation.get(p, {}).get(r, 0)
                need[p][r] = max(0, max_val - alloc_val)
        return need

    def validate_matrices(self) -> List[str]:
        """
        Validates the state:
        - Allocation <= Maximum
        - Total allocated per resource <= Total capacity (if given)
        - Non-negative values
        """
        errors = []
        for r, val in self.available.items():
            if val < 0:
                errors.append(f"Available count for resource '{r}' cannot be negative ({val}).")

        for p in self.processes:
            for r in self.resources:
                alloc = self.allocation.get(p, {}).get(r, 0)
                max_req = self.maximum.get(p, {}).get(r, 0)
                if alloc < 0:
                    errors.append(f"Process '{p}' has negative allocation for '{r}' ({alloc}).")
                if max_req < 0:
                    errors.append(f"Process '{p}' has negative maximum claim for '{r}' ({max_req}).")
                if alloc > max_req:
                    errors.append(f"Process '{p}' allocated ({alloc}) exceeds maximum claim ({max_req}) for '{r}'.")
        return errors

    def is_safe(self) -> Dict[str, Any]:
        """Runs the safety algorithm and returns the safety evaluation."""
        validation_errors = self.validate_matrices()
        if validation_errors:
            return {
                'safe': False,
                'safe_sequence': [],
                'steps': [],
                'validation_errors': validation_errors,
                'summary': f"Validation failed: {'; '.join(validation_errors)}"
            }

        safety_runner = SafetyAlgorithm(
            processes=self.processes,
            resources=self.resources,
            available=self.available,
            allocation=self.allocation,
            maximum=self.maximum,
            need=self.need
        )
        result = safety_runner.run()
        result['need_matrix'] = self.need
        return result
