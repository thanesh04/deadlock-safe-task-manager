"""
Deadlock Detection Algorithm for Multiple Instances of Each Resource Type.
Identifies whether any process is currently deadlocked in an active allocation/request state.
Unlike Banker's Algorithm (which uses Maximum and Need for avoidance),
this algorithm directly evaluates active Requests against available resources.
"""
from typing import Dict, List, Any

class DeadlockDetectionAlgorithm:
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
        self.available = {r: int(available.get(r, 0)) for r in self.resources}
        self.allocation = {
            p: {r: int(allocation.get(p, {}).get(r, 0)) for r in self.resources}
            for p in self.processes
        }
        self.request = {
            p: {r: int(request.get(p, {}).get(r, 0)) for r in self.resources}
            for p in self.processes
        }

    def run(self) -> Dict[str, Any]:
        """
        Executes Deadlock Detection.
        
        Returns:
            dict containing:
                deadlock: bool
                deadlocked_processes: list of process IDs
                satisfied_processes: list of process IDs in order of completion
                steps: list of trace dictionaries
                work_initial: dict
                work_final: dict
                finish: dict of process -> bool
                explanation: str
        """
        work = {r: self.available[r] for r in self.resources}
        finish: Dict[str, bool] = {}

        # Step 1: Initialize Finish vector
        # Finish[i] = true if Allocation[i] == 0 for all resources; else false
        initial_zero_alloc = []
        for p in self.processes:
            has_allocation = any(self.allocation[p][r] > 0 for r in self.resources)
            if not has_allocation:
                finish[p] = True
                initial_zero_alloc.append(p)
            else:
                finish[p] = False

        steps: List[Dict[str, Any]] = []
        satisfied_processes: List[str] = []
        step_counter = 1

        if initial_zero_alloc:
            steps.append({
                'step': step_counter,
                'process': ', '.join(initial_zero_alloc),
                'action': 'INITIALIZATION',
                'decision': 'NO_ALLOCATION',
                'finish_state': dict(finish),
                'work': dict(work),
                'explanation': f"Processes with no allocated resources ({', '.join(initial_zero_alloc)}) cannot be part of a deadlock; Finish set to true."
            })
            step_counter += 1

        # Step 2: Iteratively find process where Finish[i] == False and Request[i] <= Work
        while True:
            found = False
            for p in self.processes:
                if finish[p]:
                    continue

                can_satisfy = True
                for r in self.resources:
                    if self.request[p][r] > work[r]:
                        can_satisfy = False
                        break

                if can_satisfy:
                    found = True
                    work_before = dict(work)
                    for r in self.resources:
                        work[r] += self.allocation[p][r]
                    finish[p] = True
                    satisfied_processes.append(p)

                    steps.append({
                        'step': step_counter,
                        'process': p,
                        'action': 'SATISFY_REQUEST',
                        'request': dict(self.request[p]),
                        'work_before': work_before,
                        'allocation': dict(self.allocation[p]),
                        'work_after': dict(work),
                        'decision': 'SATISFIED',
                        'explanation': f"Process {p}'s request {self.request[p]} <= Work {work_before}. Process can finish, releasing allocated resources."
                    })
                    step_counter += 1
                    break

            if not found:
                break

        # Step 3: Identify deadlocked processes
        deadlocked_processes = [p for p in self.processes if not finish[p]]
        has_deadlock = len(deadlocked_processes) > 0

        if has_deadlock:
            explanation = (
                f"DEADLOCK DETECTED! {len(deadlocked_processes)} process(es) "
                f"({', '.join(deadlocked_processes)}) are deadlocked. "
                "Their requests cannot be satisfied by available resources, creating an unresolvable wait condition."
            )
            # Add failure step for each deadlocked process
            for p in deadlocked_processes:
                blocking_resources = [
                    f"{r} (requests {self.request[p][r]} > work {work[r]})"
                    for r in self.resources if self.request[p][r] > work[r]
                ]
                steps.append({
                    'step': step_counter,
                    'process': p,
                    'action': 'DEADLOCKED',
                    'request': dict(self.request[p]),
                    'work': dict(work),
                    'allocation': dict(self.allocation[p]),
                    'decision': 'BLOCKED',
                    'explanation': f"Process {p} is permanently blocked waiting for: {', '.join(blocking_resources)}"
                })
                step_counter += 1
        else:
            explanation = "NO DEADLOCK DETECTED. All process requests can eventually be satisfied."

        return {
            'deadlock': has_deadlock,
            'deadlocked_processes': deadlocked_processes,
            'satisfied_processes': satisfied_processes,
            'steps': steps,
            'work_initial': {r: self.available[r] for r in self.resources},
            'work_final': work,
            'finish': finish,
            'explanation': explanation
        }
