"""
Safety Algorithm (Banker's Algorithm Core).
Determines whether a system allocation state is safe or unsafe.
Returns detailed step-by-step execution trace suitable for visualization.
"""
from typing import Dict, List, Any, Optional

class SafetyAlgorithm:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        available: Dict[str, int],
        allocation: Dict[str, Dict[str, int]],
        maximum: Dict[str, Dict[str, int]],
        need: Optional[Dict[str, Dict[str, int]]] = None
    ):
        self.processes = list(processes)
        self.resources = list(resources)
        self.available = {r: int(available.get(r, 0)) for r in self.resources}
        
        # Ensure allocation and maximum have all resources
        self.allocation = {}
        for p in self.processes:
            self.allocation[p] = {r: int(allocation.get(p, {}).get(r, 0)) for r in self.resources}
            
        self.maximum = {}
        for p in self.processes:
            self.maximum[p] = {r: int(maximum.get(p, {}).get(r, 0)) for r in self.resources}
            
        # Calculate Need = Maximum - Allocation if not provided
        self.need = {}
        for p in self.processes:
            self.need[p] = {}
            for r in self.resources:
                if need and p in need and r in need[p]:
                    self.need[p][r] = int(need[p][r])
                else:
                    self.need[p][r] = max(0, self.maximum[p][r] - self.allocation[p][r])

    def run(self) -> Dict[str, Any]:
        """
        Executes the Safety Algorithm.
        
        Returns:
            dict containing:
                safe: bool
                safe_sequence: list of process IDs
                steps: list of trace dictionaries
                work_initial: dict
                work_final: dict
                unfinished_processes: list
                summary: str
        """
        work = {r: self.available[r] for r in self.resources}
        finish = {p: False for p in self.processes}
        safe_sequence: List[str] = []
        steps: List[Dict[str, Any]] = []

        step_counter = 1

        while True:
            found_candidate = False
            for p in self.processes:
                if finish[p]:
                    continue

                # Check if Need[p][r] <= Work[r] for all r
                can_finish = True
                failing_resources = []
                for r in self.resources:
                    if self.need[p][r] > work[r]:
                        can_finish = False
                        failing_resources.append({
                            'resource': r,
                            'need': self.need[p][r],
                            'work': work[r]
                        })

                if can_finish:
                    found_candidate = True
                    work_before = dict(work)
                    
                    # Update work: Work = Work + Allocation[p]
                    for r in self.resources:
                        work[r] += self.allocation[p][r]
                        
                    finish[p] = True
                    safe_sequence.append(p)

                    steps.append({
                        'step': step_counter,
                        'process': p,
                        'work_before': work_before,
                        'need': dict(self.need[p]),
                        'can_finish': True,
                        'allocation': dict(self.allocation[p]),
                        'work_after': dict(work),
                        'decision': 'CAN_FINISH',
                        'explanation': f"Process {p}'s remaining need is satisfyable with current available resources. It completes and releases its allocated resources back to work pool."
                    })
                    step_counter += 1
                    # Break to restart search for next process in round-robin fashion
                    break

            if not found_candidate:
                # No process could finish in this round
                break

        # Check for unfinished processes
        unfinished = [p for p in self.processes if not finish[p]]
        is_safe = len(unfinished) == 0

        # If unsafe, record failure info for remaining processes
        if not is_safe:
            for p in unfinished:
                shortage = {}
                for r in self.resources:
                    if self.need[p][r] > work[r]:
                        shortage[r] = {
                            'needed': self.need[p][r],
                            'available_work': work[r],
                            'deficit': self.need[p][r] - work[r]
                        }
                steps.append({
                    'step': step_counter,
                    'process': p,
                    'work_before': dict(work),
                    'need': dict(self.need[p]),
                    'can_finish': False,
                    'allocation': dict(self.allocation[p]),
                    'work_after': dict(work),
                    'decision': 'CANNOT_FINISH',
                    'explanation': f"Process {p} cannot complete because need exceeds current work vector.",
                    'shortage': shortage
                })
                step_counter += 1

        summary = (
            f"System is in a SAFE state. Safe execution sequence found: {' -> '.join(safe_sequence)}"
            if is_safe else
            f"System is in an UNSAFE state. No complete safe sequence exists. Unfinished processes: {', '.join(unfinished)}"
        )

        return {
            'safe': is_safe,
            'safe_sequence': safe_sequence,
            'steps': steps,
            'work_initial': {r: self.available[r] for r in self.resources},
            'work_final': work,
            'finish': finish,
            'unfinished_processes': unfinished,
            'summary': summary
        }
