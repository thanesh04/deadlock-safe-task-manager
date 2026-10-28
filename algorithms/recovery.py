"""
Deadlock Recovery Strategies:
1. Process Termination (single or multiple)
2. Resource Preemption (simulation)

Provides evaluation of recovery outcomes and recalculation of deadlock state.
"""
from typing import Dict, List, Any, Optional
from algorithms.deadlock_detection import DeadlockDetectionAlgorithm

class DeadlockRecovery:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        available: Dict[str, int],
        allocation: Dict[str, Dict[str, int]],
        request: Dict[str, Dict[str, int]]
    ):
        self.processes = list(processes)
        self.resources = list(resources)
        self.available = dict(available)
        self.allocation = {p: dict(allocation.get(p, {})) for p in self.processes}
        self.request = {p: dict(request.get(p, {})) for p in self.processes}

    def simulate_termination(self, pids_to_terminate: List[str]) -> Dict[str, Any]:
        """
        Simulates terminating one or more processes.
        Releases all allocated resources to Available, clears their requests and allocations.
        Re-runs deadlock detection to verify if the deadlock is resolved.
        """
        new_available = dict(self.available)
        new_allocation = {p: dict(self.allocation[p]) for p in self.processes}
        new_request = {p: dict(self.request[p]) for p in self.processes}
        released_resources = {r: 0 for r in self.resources}

        valid_terminated = []
        for pid in pids_to_terminate:
            if pid not in self.processes:
                continue
            valid_terminated.append(pid)
            # Reclaim allocated resources
            for r in self.resources:
                held = new_allocation[pid].get(r, 0)
                new_available[r] += held
                released_resources[r] += held
                new_allocation[pid][r] = 0
                new_request[pid][r] = 0

        # Remaining active processes
        remaining_processes = [p for p in self.processes if p not in valid_terminated]

        # Re-run Deadlock Detection on new state
        detection = DeadlockDetectionAlgorithm(
            processes=remaining_processes,
            resources=self.resources,
            available=new_available,
            allocation=new_allocation,
            request=new_request
        )
        detection_result = detection.run()

        is_resolved = not detection_result['deadlock']

        return {
            'action': 'PROCESS_TERMINATION',
            'terminated_processes': valid_terminated,
            'released_resources': released_resources,
            'new_available': new_available,
            'deadlock_resolved': is_resolved,
            'remaining_deadlocked': detection_result['deadlocked_processes'],
            'new_detection_result': detection_result,
            'message': (
                f"Successfully terminated {', '.join(valid_terminated)}. "
                f"Released {released_resources}. Deadlock is "
                + ("RESOLVED!" if is_resolved else "STILL PERSISTENT. Further recovery needed.")
            )
        }

    def simulate_preemption(
        self,
        victim_pid: str,
        target_pid: str,
        resource_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Simulated Resource Preemption.
        Transfers 'quantity' of 'resource_id' from 'victim_pid' to 'target_pid'.
        Clearly marked as a SIMULATION for educational demonstration.
        """
        if victim_pid not in self.processes or target_pid not in self.processes:
            return {
                'success': False,
                'message': "Invalid victim or target process."
            }

        victim_held = self.allocation[victim_pid].get(resource_id, 0)
        target_needed = self.request[target_pid].get(resource_id, 0)

        preempt_qty = min(quantity, victim_held, target_needed)
        if preempt_qty <= 0:
            return {
                'success': False,
                'message': f"Cannot preempt {quantity} units of {resource_id}. Victim holds {victim_held}, target requests {target_needed}."
            }

        new_allocation = {p: dict(self.allocation[p]) for p in self.processes}
        new_request = {p: dict(self.request[p]) for p in self.processes}

        new_allocation[victim_pid][resource_id] -= preempt_qty
        new_allocation[target_pid][resource_id] += preempt_qty
        new_request[target_pid][resource_id] -= preempt_qty

        # Re-run Deadlock Detection
        detection = DeadlockDetectionAlgorithm(
            processes=self.processes,
            resources=self.resources,
            available=self.available,
            allocation=new_allocation,
            request=new_request
        )
        detection_result = detection.run()
        is_resolved = not detection_result['deadlock']

        return {
            'action': 'RESOURCE_PREEMPTION_SIMULATION',
            'is_simulation': True,
            'success': True,
            'victim_process': victim_pid,
            'target_process': target_pid,
            'resource': resource_id,
            'preempted_quantity': preempt_qty,
            'deadlock_resolved': is_resolved,
            'remaining_deadlocked': detection_result['deadlocked_processes'],
            'new_detection_result': detection_result,
            'message': (
                f"[SIMULATION] Preempted {preempt_qty} unit(s) of {resource_id} from {victim_pid} to {target_pid}. "
                f"Deadlock is " + ("RESOLVED!" if is_resolved else "STILL PRESENT.")
            )
        }
