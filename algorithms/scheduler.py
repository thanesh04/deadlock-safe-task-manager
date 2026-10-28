"""
Deadlock-Aware CPU Scheduler Engine.
Integrates CPU Scheduling algorithms (RR, SRTF, Priority, FCFS) with Banker's Deadlock Avoidance,
Naive Allocation, and Dynamic Aging / Starvation Defense.
"""
from typing import Dict, List, Any, Optional
import copy
from algorithms.bankers import BankersAlgorithm
from algorithms.anomaly_detector import ProcessAnomalyDetector
from algorithms.wait_for_graph import WaitForGraph

class ScheduledTask:
    def __init__(
        self,
        pid: str,
        name: str,
        arrival_time: int,
        burst_time: int,
        priority: int = 3,
        max_claim: Optional[Dict[str, int]] = None,
        resource_events: Optional[Dict[int, Dict[str, Any]]] = None
    ):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst = burst_time
        self.base_priority = priority
        self.priority = priority
        self.aging_boost = 0
        
        self.max_claim = max_claim or {}
        # resource_events: { progress_tick: { 'request': {...}, 'release': {...} } }
        self.resource_events = resource_events or {}
        
        self.held_resources: Dict[str, int] = {r: 0 for r in self.max_claim}
        self.pending_request: Dict[str, int] = {}
        
        self.state = "NOT_ARRIVED"  # NOT_ARRIVED, READY, RUNNING, SAFETY_WAIT, DEADLOCKED, TERMINATED
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time: Optional[int] = None
        self.starvation_ticks = 0
        self.progress_burst = 0  # number of burst ticks executed so far

    def effective_priority(self) -> int:
        """Lower number = higher priority. Aging boost reduces the number."""
        return max(1, self.priority - self.aging_boost)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "remaining_burst": self.remaining_burst,
            "progress_burst": self.progress_burst,
            "base_priority": self.base_priority,
            "priority": self.priority,
            "aging_boost": self.aging_boost,
            "effective_priority": self.effective_priority(),
            "held_resources": dict(self.held_resources),
            "pending_request": dict(self.pending_request),
            "max_claim": dict(self.max_claim),
            "state": self.state,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time,
            "starvation_ticks": self.starvation_ticks
        }


class CPUSchedulerEngine:
    """
    Simulates coordinated CPU dispatching and resource safety enforcement.
    """

    def __init__(
        self,
        system_resources: Dict[str, int],
        policy: str = "RR",
        quantum: int = 2,
        mode: str = "DEADLOCK_AWARE",
        aging_threshold: int = 3,
        aging_enabled: bool = True
    ):
        self.system_resources = copy.deepcopy(system_resources)  # Total capacities
        self.available_resources = copy.deepcopy(system_resources)  # Available instances
        self.policy = policy.upper()  # RR, SRTF, PRIORITY, FCFS
        self.quantum = max(1, int(quantum))
        self.mode = mode.upper()  # DEADLOCK_AWARE or NAIVE
        self.aging_threshold = int(aging_threshold)
        self.aging_enabled = bool(aging_enabled)

        self.clock = 0
        self.tasks: Dict[str, ScheduledTask] = {}
        self.ready_queue: List[str] = []
        self.current_pid: Optional[str] = None
        self.current_quantum_used = 0

        self.gantt_timeline: List[Dict[str, Any]] = []
        self.event_logs: List[Dict[str, Any]] = []
        self.deadlocks_averted_count = 0
        self.context_switch_count = 0
        self.is_completed = False
        self.is_deadlocked = False

    def add_task(self, task: ScheduledTask):
        self.tasks[task.pid] = task
        # Ensure held_resources and max_claim cover all system resources
        for r in self.system_resources:
            task.held_resources.setdefault(r, 0)
            task.max_claim.setdefault(r, 0)

    def _log_event(self, category: str, message: str, level: str = "info"):
        self.event_logs.append({
            "tick": self.clock,
            "category": category,
            "message": message,
            "level": level
        })

    def _check_bankers_safety(self, requester_pid: str, request_vec: Dict[str, int]) -> (bool, List[str], str):
        """
        Runs Banker's algorithm on tentative state:
        Available = Available - Request
        Allocation[requester] = Allocation[requester] + Request
        """
        # 1. Capacity check
        for r, amount in request_vec.items():
            if amount > self.available_resources.get(r, 0):
                return False, [], f"Insufficient available units for {r} (Requested {amount}, Available {self.available_resources.get(r, 0)})"

        # 2. Need check
        task = self.tasks[requester_pid]
        for r, amount in request_vec.items():
            current_alloc = task.held_resources.get(r, 0)
            max_c = task.max_claim.get(r, 0)
            if current_alloc + amount > max_c:
                return False, [], f"Request exceeds declared maximum claim for {r}"

        # 3. Simulate tentative allocation
        tentative_avail = dict(self.available_resources)
        tentative_alloc: Dict[str, Dict[str, int]] = {}
        tentative_max: Dict[str, Dict[str, int]] = {}

        for pid, t in self.tasks.items():
            if t.state != "TERMINATED":
                tentative_alloc[pid] = dict(t.held_resources)
                tentative_max[pid] = dict(t.max_claim)

        # Apply tentative request
        for r, amount in request_vec.items():
            tentative_avail[r] -= amount
            tentative_alloc[requester_pid][r] += amount

        active_pids = list(tentative_alloc.keys())
        res_keys = list(self.system_resources.keys())

        bankers = BankersAlgorithm(
            processes=active_pids,
            resources=res_keys,
            available=tentative_avail,
            allocation=tentative_alloc,
            maximum=tentative_max
        )

        result = bankers.is_safe()
        if result.get("safe", False):
            return True, result.get("safe_sequence", []), "Safe sequence verified"
        else:
            return False, [], "No safe execution sequence exists (Unsafe state averted)"

    def _detect_naive_deadlock(self) -> (bool, List[str]):
        """
        Builds wait-for dependencies under Naive mode and finds cycles using DFS.
        """
        allocations = {pid: t.held_resources for pid, t in self.tasks.items() if t.state != "TERMINATED"}
        requests = {pid: t.pending_request for pid, t in self.tasks.items() if t.state in ["SAFETY_WAIT", "DEADLOCKED"] and t.pending_request}
        
        # Build Wait-For Graph: P_i waits for P_j if P_i needs resource R held by P_j
        wfg = WaitForGraph(
            processes=list(allocations.keys()),
            resources=list(self.system_resources.keys()),
            allocation=allocations,
            request=requests
        )
        analysis = wfg.get_analysis()
        has_cycle = analysis.get("has_cycles", False)
        cycle_nodes = analysis.get("cycle_nodes", [])
        return has_cycle, cycle_nodes

    def _select_next_task(self) -> Optional[str]:
        """
        Selects next candidate process based on scheduling algorithm.
        Considers only READY tasks (or tasks in SAFETY_WAIT if their request can now be safely granted).
        """
        candidate_pids = [
            pid for pid in self.ready_queue 
            if self.tasks[pid].state in ["READY", "RUNNING", "SAFETY_WAIT"]
        ]

        if not candidate_pids:
            return None

        # Filter out tasks in SAFETY_WAIT unless their pending request is now satisfiable and safe
        eligible_pids = []
        for pid in candidate_pids:
            task = self.tasks[pid]
            if task.state == "SAFETY_WAIT":
                # Check if now safe
                if task.pending_request:
                    can_grant = True
                    for r, amt in task.pending_request.items():
                        if amt > self.available_resources.get(r, 0):
                            can_grant = False
                            break
                    if can_grant and self.mode == "DEADLOCK_AWARE":
                        is_safe, _, _ = self._check_bankers_safety(pid, task.pending_request)
                        if is_safe:
                            eligible_pids.append(pid)
                    elif can_grant and self.mode == "NAIVE":
                        eligible_pids.append(pid)
            else:
                eligible_pids.append(pid)

        if not eligible_pids:
            return None

        # Priority / SRTF / FCFS / RR selection
        if self.policy == "PRIORITY":
            # Lowest effective priority value = highest priority
            eligible_pids.sort(key=lambda p: (self.tasks[p].effective_priority(), self.tasks[p].arrival_time))
            return eligible_pids[0]

        elif self.policy == "SRTF":
            # Shortest Remaining Time First
            eligible_pids.sort(key=lambda p: (self.tasks[p].remaining_burst, self.tasks[p].arrival_time))
            return eligible_pids[0]

        elif self.policy == "FCFS":
            eligible_pids.sort(key=lambda p: self.tasks[p].arrival_time)
            return eligible_pids[0]

        else:  # Round Robin (RR)
            # Pick the first eligible process in the ready queue
            for p in self.ready_queue:
                if p in eligible_pids:
                    return p
            return eligible_pids[0]

    def tick(self) -> Dict[str, Any]:
        """
        Advances the simulation by 1 clock tick.
        """
        if self.is_completed:
            return self.get_state()

        current_tick = self.clock
        tick_events: List[str] = []

        # 1. Admit newly arrived processes
        for pid, task in self.tasks.items():
            if task.state == "NOT_ARRIVED" and task.arrival_time <= current_tick:
                task.state = "READY"
                self.ready_queue.append(pid)
                msg = f"Task {pid} ({task.name}) arrived at T={current_tick} (Burst: {task.burst_time}, Priority: {task.priority})"
                tick_events.append(msg)
                self._log_event("SCHEDULER", msg, "info")

        # 2. Check if current task's quantum expired (RR) or needs preemption
        should_switch = False
        if self.current_pid:
            curr_task = self.tasks[self.current_pid]
            if curr_task.state == "RUNNING":
                if self.policy == "RR" and self.current_quantum_used >= self.quantum:
                    should_switch = True
                    curr_task.state = "READY"
                    # Move to tail of ready queue
                    if self.current_pid in self.ready_queue:
                        self.ready_queue.remove(self.current_pid)
                    self.ready_queue.append(self.current_pid)
                    self._log_event("DISPATCHER", f"Quantum ({self.quantum}) expired for {self.current_pid}", "secondary")

        # 3. Pick the task to dispatch for this tick
        next_pid = self._select_next_task()

        if next_pid != self.current_pid and next_pid is not None:
            if self.current_pid and self.tasks[self.current_pid].state == "RUNNING":
                self.tasks[self.current_pid].state = "READY"
            self.current_pid = next_pid
            self.current_quantum_used = 0
            self.context_switch_count += 1
            self._log_event("DISPATCHER", f"Context switched CPU to {next_pid}", "primary")

        # If still no process can run:
        if self.current_pid is None:
            # Check if all tasks are terminated
            all_done = all(t.state == "TERMINATED" for t in self.tasks.values())
            if all_done:
                self.is_completed = True
                self._log_event("SIMULATION", f"All tasks completed at T={current_tick}", "success")
                return self.get_state()

            # Check if naive deadlock stall
            if self.mode == "NAIVE":
                has_cycle, cycle_pids = self._detect_naive_deadlock()
                if has_cycle:
                    self.is_deadlocked = True
                    for cp in cycle_pids:
                        if cp in self.tasks:
                            self.tasks[cp].state = "DEADLOCKED"
                    self._log_event("DEADLOCK", f"Circular Deadlock detected among {cycle_pids}!", "danger")

            # CPU IDLE Tick
            self.gantt_timeline.append({
                "tick": current_tick,
                "pid": "IDLE",
                "name": "CPU Idle",
                "state": "IDLE",
                "note": "No eligible or safe tasks ready"
            })
            self._increment_waiting_times(None)
            self.clock += 1
            return self.get_state()

        # 4. We have an active task for this tick!
        task = self.tasks[self.current_pid]

        # Record initial response time
        if task.response_time is None:
            task.response_time = current_tick - task.arrival_time

        # 5. Check if task has a resource event at this burst progress tick
        progress_point = task.progress_burst
        event_spec = task.resource_events.get(progress_point)

        if event_spec:
            # Handle resource release first if any
            if "release" in event_spec:
                rel_dict = event_spec["release"]
                for r, amt in rel_dict.items():
                    actual_rel = min(task.held_resources.get(r, 0), amt)
                    task.held_resources[r] -= actual_rel
                    self.available_resources[r] += actual_rel
                msg = f"{task.pid} voluntarily released resources: {rel_dict}"
                tick_events.append(msg)
                self._log_event("RESOURCES", msg, "success")

            # Handle resource request
            if "request" in event_spec:
                req_dict = event_spec["request"]
                task.pending_request = copy.deepcopy(req_dict)

                if self.mode == "DEADLOCK_AWARE":
                    is_safe, seq, reason = self._check_bankers_safety(task.pid, req_dict)
                    if is_safe:
                        # Grant allocation
                        for r, amt in req_dict.items():
                            self.available_resources[r] -= amt
                            task.held_resources[r] += amt
                        task.pending_request = {}
                        task.state = "RUNNING"
                        msg = f"Banker's APPROVED request for {task.pid} {req_dict}. Safe seq: {' -> '.join(seq)}"
                        tick_events.append(msg)
                        self._log_event("BANKERS_SAFE", msg, "success")
                    else:
                        # Intercept! Do not grant. Put in SAFETY_WAIT
                        task.state = "SAFETY_WAIT"
                        task.starvation_ticks += 1
                        self.deadlocks_averted_count += 1
                        msg = f"Banker's INTERCEPTED unsafe request by {task.pid} {req_dict}! Blocked to prevent circular wait."
                        tick_events.append(msg)
                        self._log_event("BANKERS_UNSAFE", msg, "warning")

                        # Immediately context switch away from blocked task!
                        self.gantt_timeline.append({
                            "tick": current_tick,
                            "pid": task.pid,
                            "name": task.name,
                            "state": "SAFETY_WAIT",
                            "note": f"Blocked by Banker's ({reason})"
                        })
                        self.current_pid = None
                        self._increment_waiting_times(None)
                        self.clock += 1
                        return self.get_state()

                else:  # NAIVE MODE
                    can_alloc = True
                    for r, amt in req_dict.items():
                        if amt > self.available_resources.get(r, 0):
                            can_alloc = False
                            break
                    if can_alloc:
                        for r, amt in req_dict.items():
                            self.available_resources[r] -= amt
                            task.held_resources[r] += amt
                        task.pending_request = {}
                        task.state = "RUNNING"
                        msg = f"NAIVE Mode blindly granted {req_dict} to {task.pid}."
                        self._log_event("NAIVE_ALLOC", msg, "info")
                    else:
                        task.state = "SAFETY_WAIT"
                        has_cycle, cycle_pids = self._detect_naive_deadlock()
                        if has_cycle:
                            self.is_deadlocked = True
                            for cp in cycle_pids:
                                if cp in self.tasks:
                                    self.tasks[cp].state = "DEADLOCKED"
                            msg = f"DEADLOCK! Circular wait detected: {cycle_pids}"
                            self._log_event("DEADLOCK", msg, "danger")

                        self.gantt_timeline.append({
                            "tick": current_tick,
                            "pid": task.pid,
                            "name": task.name,
                            "state": "DEADLOCKED" if self.is_deadlocked else "SAFETY_WAIT",
                            "note": "Blocked on unavailable resource"
                        })
                        self.current_pid = None
                        self._increment_waiting_times(None)
                        self.clock += 1
                        return self.get_state()

        # 6. Execute CPU cycle for the task
        task.state = "RUNNING"
        task.remaining_burst -= 1
        task.progress_burst += 1
        self.current_quantum_used += 1

        # Reset starvation ticks if successfully running
        task.starvation_ticks = 0

        self.gantt_timeline.append({
            "tick": current_tick,
            "pid": task.pid,
            "name": task.name,
            "state": "RUNNING",
            "note": f"Executing burst tick {task.progress_burst}/{task.burst_time}"
        })

        # 7. Check if task completed
        if task.remaining_burst <= 0:
            task.state = "TERMINATED"
            task.turnaround_time = (current_tick + 1) - task.arrival_time
            # Release all held resources
            for r, amt in list(task.held_resources.items()):
                self.available_resources[r] += amt
                task.held_resources[r] = 0
            if task.pid in self.ready_queue:
                self.ready_queue.remove(task.pid)
            self.current_pid = None
            self.current_quantum_used = 0
            msg = f"Task {task.pid} ({task.name}) COMPLETED at T={current_tick + 1}. All resources reclaimed. Turnaround: {task.turnaround_time} ticks."
            self._log_event("COMPLETION", msg, "success")

        # 8. Increment waiting time and check Aging for other tasks
        self._increment_waiting_times(task.pid if task.state == "RUNNING" else None)

        # 9. Dynamic Aging Check
        if self.aging_enabled:
            for p, t in self.tasks.items():
                if t.state in ["READY", "SAFETY_WAIT"]:
                    if t.starvation_ticks >= self.aging_threshold:
                        # Dynamic Aging boost
                        old_boost = t.aging_boost
                        t.aging_boost += 1
                        msg = f"DYNAMIC AGING: Task {t.pid} boosted priority (Effective: {t.effective_priority()}) after {t.starvation_ticks} wait ticks"
                        self._log_event("AGING", msg, "warning")

        # 10. Check if all tasks have finished
        if all(t.state == "TERMINATED" for t in self.tasks.values()):
            self.is_completed = True

        self.clock += 1
        return self.get_state()

    def _increment_waiting_times(self, running_pid: Optional[str]):
        for pid, task in self.tasks.items():
            if task.state in ["READY", "SAFETY_WAIT"] and pid != running_pid:
                task.waiting_time += 1
                if task.state == "SAFETY_WAIT":
                    task.starvation_ticks += 1

    def run_all(self, max_ticks: int = 100) -> Dict[str, Any]:
        """Runs the simulation until all tasks complete or max ticks reached."""
        while not self.is_completed and not self.is_deadlocked and self.clock < max_ticks:
            self.tick()
        return self.get_state()

    def get_anomalies(self) -> List[Dict[str, Any]]:
        """Runs behavioral anomaly detection across all tasks."""
        reports = []
        for pid, t in self.tasks.items():
            rep = ProcessAnomalyDetector.evaluate_process(
                pid=t.pid,
                state=t.state,
                burst_progress=t.progress_burst / t.burst_time if t.burst_time > 0 else 0,
                held_resources=t.held_resources,
                pending_request=t.pending_request,
                max_claim=t.max_claim,
                total_resources=self.system_resources,
                starvation_ticks=t.starvation_ticks,
                aging_threshold=self.aging_threshold
            )
            reports.append(rep)
        return reports

    def get_metrics(self) -> Dict[str, Any]:
        """Calculates aggregate performance metrics."""
        completed_tasks = [t for t in self.tasks.values() if t.state == "TERMINATED"]
        total_tasks = len(self.tasks)
        
        avg_wait = sum(t.waiting_time for t in self.tasks.values()) / max(1, total_tasks)
        avg_turnaround = sum(t.turnaround_time for t in completed_tasks) / max(1, len(completed_tasks))
        
        non_idle_ticks = sum(1 for g in self.gantt_timeline if g["state"] == "RUNNING")
        cpu_util = (non_idle_ticks / max(1, self.clock)) * 100.0

        throughput = (len(completed_tasks) / max(1, self.clock)) * 10.0  # completed per 10 ticks

        return {
            "clock": self.clock,
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "cpu_utilization_percent": round(cpu_util, 1),
            "average_waiting_time": round(avg_wait, 2),
            "average_turnaround_time": round(avg_turnaround, 2),
            "throughput_per_10_ticks": round(throughput, 2),
            "context_switches": self.context_switch_count,
            "deadlocks_averted": self.deadlocks_averted_count,
            "is_deadlocked": self.is_deadlocked,
            "is_completed": self.is_completed
        }

    def get_state(self) -> Dict[str, Any]:
        """Returns complete serializable snapshot of the scheduler."""
        return {
            "clock": self.clock,
            "policy": self.policy,
            "quantum": self.quantum,
            "mode": self.mode,
            "aging_threshold": self.aging_threshold,
            "aging_enabled": self.aging_enabled,
            "current_pid": self.current_pid,
            "system_resources": self.system_resources,
            "available_resources": self.available_resources,
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "ready_queue": self.ready_queue,
            "gantt_timeline": self.gantt_timeline,
            "event_logs": self.event_logs[-40:],  # last 40 logs
            "metrics": self.get_metrics(),
            "anomalies": self.get_anomalies(),
            "is_completed": self.is_completed,
            "is_deadlocked": self.is_deadlocked
        }


# =========================================================================
# PREDEFINED SCHEDULER SCENARIOS / PRESETS
# =========================================================================
def load_scheduler_preset(preset_name: str, policy: str = "RR", mode: str = "DEADLOCK_AWARE") -> CPUSchedulerEngine:
    """
    Factory function for curated educational scheduling scenarios.
    """
    if preset_name == "starvation_demo":
        # Scenario where a greedy high-demand process gets starved, demonstrating dynamic aging
        engine = CPUSchedulerEngine(
            system_resources={"CPU_Core": 3, "Memory": 4, "Disk": 2},
            policy=policy,
            quantum=2,
            mode=mode,
            aging_threshold=3,
            aging_enabled=True
        )
        engine.add_task(ScheduledTask(
            pid="P0", name="Batch Analytics", arrival_time=0, burst_time=6, priority=4,
            max_claim={"CPU_Core": 2, "Memory": 3, "Disk": 1},
            resource_events={1: {"request": {"CPU_Core": 2, "Memory": 3}}}
        ))
        engine.add_task(ScheduledTask(
            pid="P1", name="Quick Response API", arrival_time=1, burst_time=3, priority=2,
            max_claim={"CPU_Core": 1, "Memory": 1, "Disk": 0},
            resource_events={0: {"request": {"CPU_Core": 1, "Memory": 1}}}
        ))
        engine.add_task(ScheduledTask(
            pid="P2", name="Telemetry Logger", arrival_time=2, burst_time=4, priority=3,
            max_claim={"CPU_Core": 1, "Memory": 1, "Disk": 1},
            resource_events={1: {"request": {"CPU_Core": 1, "Disk": 1}}}
        ))
        return engine

    elif preset_name == "naive_vs_safe":
        # Classic textbook circular wait contention between P0 and P1
        # P0 holds R0 and requests R1; P1 holds R1 and requests R0.
        engine = CPUSchedulerEngine(
            system_resources={"R0_MutexA": 1, "R1_MutexB": 1},
            policy=policy,
            quantum=2,
            mode=mode,
            aging_threshold=3,
            aging_enabled=True
        )
        engine.add_task(ScheduledTask(
            pid="P0", name="Transaction Worker 1", arrival_time=0, burst_time=5, priority=2,
            max_claim={"R0_MutexA": 1, "R1_MutexB": 1},
            resource_events={
                0: {"request": {"R0_MutexA": 1}},
                2: {"request": {"R1_MutexB": 1}}
            }
        ))
        engine.add_task(ScheduledTask(
            pid="P1", name="Transaction Worker 2", arrival_time=1, burst_time=5, priority=2,
            max_claim={"R0_MutexA": 1, "R1_MutexB": 1},
            resource_events={
                0: {"request": {"R1_MutexB": 1}},
                2: {"request": {"R0_MutexA": 1}}
            }
        ))
        engine.add_task(ScheduledTask(
            pid="P2", name="Independent Task", arrival_time=2, burst_time=4, priority=3,
            max_claim={"R0_MutexA": 0, "R1_MutexB": 0},
            resource_events={}
        ))
        return engine

    else:
        # Default: Balanced Multi-Process Contention (5 tasks, 3 resources)
        engine = CPUSchedulerEngine(
            system_resources={"CPU_Core": 3, "Memory_GB": 4, "I/O_Channel": 2},
            policy=policy,
            quantum=2,
            mode=mode,
            aging_threshold=3,
            aging_enabled=True
        )
        engine.add_task(ScheduledTask(
            pid="P0", name="Data Processor", arrival_time=0, burst_time=6, priority=3,
            max_claim={"CPU_Core": 2, "Memory_GB": 2, "I/O_Channel": 1},
            resource_events={
                1: {"request": {"CPU_Core": 1, "Memory_GB": 1}},
                4: {"release": {"Memory_GB": 1}}
            }
        ))
        engine.add_task(ScheduledTask(
            pid="P1", name="Web Service", arrival_time=1, burst_time=4, priority=1,
            max_claim={"CPU_Core": 1, "Memory_GB": 2, "I/O_Channel": 0},
            resource_events={
                0: {"request": {"CPU_Core": 1, "Memory_GB": 1}}
            }
        ))
        engine.add_task(ScheduledTask(
            pid="P2", name="File Indexer", arrival_time=2, burst_time=7, priority=4,
            max_claim={"CPU_Core": 1, "Memory_GB": 1, "I/O_Channel": 2},
            resource_events={
                2: {"request": {"I/O_Channel": 1}},
                5: {"request": {"CPU_Core": 1}}
            }
        ))
        engine.add_task(ScheduledTask(
            pid="P3", name="Auth Gateway", arrival_time=3, burst_time=3, priority=2,
            max_claim={"CPU_Core": 1, "Memory_GB": 1, "I/O_Channel": 0},
            resource_events={
                1: {"request": {"Memory_GB": 1}}
            }
        ))
        return engine
