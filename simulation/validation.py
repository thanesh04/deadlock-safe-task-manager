"""
Data consistency and constraints validation for processes, resources, and allocations.
"""
from typing import Dict, List, Tuple, Any

class SimulationValidator:
    @staticmethod
    def validate_process_data(pid: str, name: str, existing_pids: List[str]) -> Tuple[bool, str]:
        if not pid or not pid.strip():
            return False, "PID cannot be empty."
        pid = pid.strip().upper()
        if not name or not name.strip():
            return False, "Process name cannot be empty."
        if pid in [p.upper() for p in existing_pids]:
            return False, f"Process with PID '{pid}' already exists."
        return True, ""

    @staticmethod
    def validate_resource_data(resource_id: str, name: str, total_instances: int, existing_rids: List[str]) -> Tuple[bool, str]:
        if not resource_id or not resource_id.strip():
            return False, "Resource ID cannot be empty."
        resource_id = resource_id.strip().upper()
        if not name or not name.strip():
            return False, "Resource name cannot be empty."
        if resource_id in [r.upper() for r in existing_rids]:
            return False, f"Resource with ID '{resource_id}' already exists."
        if total_instances < 1:
            return False, "Total instances must be at least 1."
        return True, ""

    @staticmethod
    def validate_matrix_consistency(
        available: Dict[str, int],
        total: Dict[str, int],
        allocation: Dict[str, Dict[str, int]],
        maximum: Dict[str, Dict[str, int]]
    ) -> Tuple[bool, List[str]]:
        errors = []

        # Check total allocation per resource
        for rid, tot in total.items():
            allocated_sum = sum(allocation.get(p, {}).get(rid, 0) for p in allocation)
            avail = available.get(rid, 0)
            if allocated_sum + avail != tot:
                errors.append(f"Resource {rid} mismatch: Allocated ({allocated_sum}) + Available ({avail}) != Total ({tot})")
            if allocated_sum > tot:
                errors.append(f"Resource {rid} over-allocated: Allocated {allocated_sum} > Total {tot}")
            if avail < 0:
                errors.append(f"Resource {rid} has negative available count: {avail}")

        # Check allocation <= maximum
        for p, alloc_dict in allocation.items():
            for rid, alloc_val in alloc_dict.items():
                max_val = maximum.get(p, {}).get(rid, 0)
                if alloc_val < 0:
                    errors.append(f"Process {p} has negative allocation for {rid}: {alloc_val}")
                if max_val < 0:
                    errors.append(f"Process {p} has negative maximum demand for {rid}: {max_val}")
                if alloc_val > max_val:
                    errors.append(f"Process {p} allocation ({alloc_val}) exceeds maximum demand ({max_val}) for {rid}")

        return len(errors) == 0, errors
