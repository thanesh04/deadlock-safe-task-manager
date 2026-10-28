"""
Banker's Resource-Request Algorithm for Deadlock Avoidance.
Evaluates whether a dynamic resource request by process P_i can be safely granted immediately.
"""
from typing import Dict, List, Any
from algorithms.safety import SafetyAlgorithm

class ResourceRequestAlgorithm:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        available: Dict[str, int],
        allocation: Dict[str, Dict[str, int]],
        maximum: Dict[str, Dict[str, int]],
        need: Dict[str, Dict[str, int]]
    ):
        self.processes = processes
        self.resources = resources
        self.available = dict(available)
        self.allocation = {p: dict(allocation.get(p, {})) for p in processes}
        self.maximum = {p: dict(maximum.get(p, {})) for p in processes}
        self.need = {p: dict(need.get(p, {})) for p in processes}

    def evaluate_request(self, pid: str, request: Dict[str, int]) -> Dict[str, Any]:
        """
        Evaluates a request from process `pid`.
        
        Returns a dict with:
            granted: bool
            step_failed: Optional[int] (1, 2, or 4)
            reason: str
            previous_state: dict
            tentative_state: dict
            safety_analysis: dict
            steps_log: list of step evaluations
        """
        steps_log = []
        if pid not in self.processes:
            return {
                'granted': False,
                'step_failed': 0,
                'reason': f"Process '{pid}' does not exist.",
                'steps_log': [{'step': 0, 'status': 'FAILED', 'message': f"Process {pid} not found."}]
            }

        # Normalize request dict to contain all resources
        norm_request = {r: int(request.get(r, 0)) for r in self.resources}
        for r, val in norm_request.items():
            if val < 0:
                return {
                    'granted': False,
                    'step_failed': 0,
                    'reason': f"Request for resource '{r}' cannot be negative ({val}).",
                    'steps_log': [{'step': 0, 'status': 'FAILED', 'message': f"Negative request value for {r}."}]
                }

        # Check for all-zero request
        if all(val == 0 for val in norm_request.values()):
            return {
                'granted': True,
                'step_failed': None,
                'reason': "Request is empty (all zeroes). Granted with no state change.",
                'steps_log': [{'step': 0, 'status': 'PASSED', 'message': "Empty request vector."}]
            }

        # Step 1: Request[i] <= Need[i]
        exceeds_need = []
        for r in self.resources:
            req_val = norm_request[r]
            need_val = self.need[pid].get(r, 0)
            if req_val > need_val:
                exceeds_need.append(f"{r} (requested {req_val} > remaining need {need_val})")

        if exceeds_need:
            step1_msg = f"Request exceeds remaining need: {', '.join(exceeds_need)}. Error: Process has exceeded its maximum claim."
            steps_log.append({
                'step': 1,
                'name': "Check Request <= Need",
                'passed': False,
                'message': step1_msg,
                'request': norm_request,
                'need': dict(self.need[pid])
            })
            return {
                'granted': False,
                'step_failed': 1,
                'reason': step1_msg,
                'steps_log': steps_log
            }

        steps_log.append({
            'step': 1,
            'name': "Check Request <= Need",
            'passed': True,
            'message': f"Request {norm_request} is within remaining claim Need {self.need[pid]}.",
            'request': norm_request,
            'need': dict(self.need[pid])
        })

        # Step 2: Request[i] <= Available
        exceeds_avail = []
        for r in self.resources:
            req_val = norm_request[r]
            avail_val = self.available.get(r, 0)
            if req_val > avail_val:
                exceeds_avail.append(f"{r} (requested {req_val} > available {avail_val})")

        if exceeds_avail:
            step2_msg = f"Insufficient available resources: {', '.join(exceeds_avail)}. Process {pid} must wait."
            steps_log.append({
                'step': 2,
                'name': "Check Request <= Available",
                'passed': False,
                'message': step2_msg,
                'request': norm_request,
                'available': dict(self.available)
            })
            return {
                'granted': False,
                'step_failed': 2,
                'reason': step2_msg,
                'steps_log': steps_log
            }

        steps_log.append({
            'step': 2,
            'name': "Check Request <= Available",
            'passed': True,
            'message': f"Sufficient resources available in system pool for request.",
            'request': norm_request,
            'available': dict(self.available)
        })

        # Step 3: Pretend to allocate requested resources (tentative state)
        tentative_available = dict(self.available)
        tentative_allocation = {p: dict(self.allocation[p]) for p in self.processes}
        tentative_need = {p: dict(self.need[p]) for p in self.processes}

        for r in self.resources:
            tentative_available[r] -= norm_request[r]
            tentative_allocation[pid][r] += norm_request[r]
            tentative_need[pid][r] -= norm_request[r]

        steps_log.append({
            'step': 3,
            'name': "Tentative Allocation",
            'passed': True,
            'message': "Simulated tentative allocation created to test safety.",
            'tentative_available': tentative_available,
            'tentative_allocation': tentative_allocation[pid],
            'tentative_need': tentative_need[pid]
        })

        # Step 4: Run Safety Algorithm on tentative state
        safety_checker = SafetyAlgorithm(
            processes=self.processes,
            resources=self.resources,
            available=tentative_available,
            allocation=tentative_allocation,
            maximum=self.maximum,
            need=tentative_need
        )
        safety_result = safety_checker.run()

        # Step 5: Final Decision
        if safety_result['safe']:
            steps_log.append({
                'step': 5,
                'name': "Safety Verification & Final Decision",
                'passed': True,
                'message': f"Tentative state is SAFE. Safe sequence: {' -> '.join(safety_result['safe_sequence'])}. Request is GRANTED and committed.",
                'safe_sequence': safety_result['safe_sequence']
            })
            return {
                'granted': True,
                'step_failed': None,
                'reason': f"Request safely granted. System remains safe with safe sequence: {' -> '.join(safety_result['safe_sequence'])}",
                'request': norm_request,
                'previous_available': self.available,
                'tentative_available': tentative_available,
                'tentative_allocation': tentative_allocation,
                'tentative_need': tentative_need,
                'safety_analysis': safety_result,
                'steps_log': steps_log
            }
        else:
            steps_log.append({
                'step': 5,
                'name': "Safety Verification & Final Decision",
                'passed': False,
                'message': f"Tentative state is UNSAFE. Granting this request could lead to deadlock. Request is DENIED and rolled back.",
                'safety_steps': safety_result['steps']
            })
            return {
                'granted': False,
                'step_failed': 4,
                'reason': f"Request denied. Granting this request would transition the system into an UNSAFE state.",
                'request': norm_request,
                'previous_available': self.available,
                'safety_analysis': safety_result,
                'steps_log': steps_log
            }
