"""
Process Manager: CRUD and lifecycle operations for simulated processes.
"""
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional
from database.database import db
from database.models import Process, Resource, Allocation, MaximumNeed, ResourceRequest, EventLog, ProcessState
from simulation.validation import SimulationValidator
from simulation.resource_manager import ResourceManager
from algorithms.resource_request import ResourceRequestAlgorithm

class ProcessManager:
    @staticmethod
    def get_all_processes() -> List[Process]:
        return Process.query.order_by(Process.pid).all()

    @staticmethod
    def get_by_id(proc_id: int) -> Optional[Process]:
        return db.session.get(Process, proc_id)

    @staticmethod
    def get_by_pid(pid: str) -> Optional[Process]:
        return Process.query.filter_by(pid=pid.upper()).first()

    @staticmethod
    def create_process(
        pid: str,
        name: str,
        maximums: Optional[Dict[str, int]] = None,
        allocations: Optional[Dict[str, int]] = None
    ) -> Tuple[bool, str, Optional[Process]]:
        pid = pid.strip().upper()
        existing = [p.pid for p in Process.query.all()]
        valid, msg = SimulationValidator.validate_process_data(pid, name, existing)
        if not valid:
            return False, msg, None

        resources = Resource.query.all()
        res_map = {r.resource_id: r for r in resources}

        # Check maximums and allocations validity against resource totals
        maximums = maximums or {}
        allocations = allocations or {}

        for rid, val in maximums.items():
            if val < 0:
                return False, f"Maximum demand for {rid} cannot be negative.", None
            if rid in res_map and val > res_map[rid].total_instances:
                return False, f"Maximum demand {val} for {rid} exceeds system total capacity ({res_map[rid].total_instances}).", None

        for rid, val in allocations.items():
            if val < 0:
                return False, f"Allocation for {rid} cannot be negative.", None
            max_val = maximums.get(rid, 0)
            if val > max_val:
                return False, f"Allocation {val} for {rid} exceeds maximum demand {max_val}.", None
            if rid in res_map and val > res_map[rid].available_instances:
                return False, f"Allocation {val} for {rid} exceeds available capacity ({res_map[rid].available_instances}).", None

        process = Process(
            pid=pid,
            name=name.strip(),
            state=ProcessState.READY
        )
        db.session.add(process)
        db.session.flush()

        for r in resources:
            m_val = maximums.get(r.resource_id, 0)
            a_val = allocations.get(r.resource_id, 0)
            db.session.add(MaximumNeed(process_id=process.id, resource_id=r.id, maximum=m_val))
            db.session.add(Allocation(process_id=process.id, resource_id=r.id, allocated=a_val))
            r.available_instances -= a_val

        # Update process initial state
        has_alloc = any(allocations.get(r.resource_id, 0) > 0 for r in resources)
        process.state = ProcessState.RUNNING if has_alloc else ProcessState.READY

        log = EventLog(
            event_type="PROCESS_CREATED",
            description=f"Created process '{name}' ({pid}) with state {process.state}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Process {pid} created successfully.", process

    @staticmethod
    def terminate_process(proc_id: int) -> Tuple[bool, str, Dict[str, int]]:
        process = db.session.get(Process, proc_id)
        if not process:
            return False, "Process not found.", {}

        released = {}
        for a in process.allocations:
            qty = a.allocated
            if qty > 0:
                a.resource.available_instances += qty
                released[a.resource.resource_id] = qty
                a.allocated = 0

        process.state = ProcessState.TERMINATED
        process.completed_at = datetime.now(timezone.utc)

        # Clear pending requests
        for req in process.requests:
            if req.status == 'PENDING':
                req.status = 'CANCELLED'
                req.reason = 'Process terminated.'

        log = EventLog(
            event_type="PROCESS_TERMINATED",
            description=f"Terminated process {process.pid}. Released resources: {released}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Process {process.pid} terminated.", released

    @staticmethod
    def complete_process(proc_id: int) -> Tuple[bool, str, Dict[str, int]]:
        process = db.session.get(Process, proc_id)
        if not process:
            return False, "Process not found.", {}

        released = {}
        for a in process.allocations:
            qty = a.allocated
            if qty > 0:
                a.resource.available_instances += qty
                released[a.resource.resource_id] = qty
                a.allocated = 0

        process.state = ProcessState.COMPLETED
        process.completed_at = datetime.now(timezone.utc)

        # Clear pending requests
        for req in process.requests:
            if req.status == 'PENDING':
                req.status = 'COMPLETED'
                req.reason = 'Process completed execution successfully.'

        log = EventLog(
            event_type="PROCESS_COMPLETED",
            description=f"Process {process.pid} completed successfully. Released resources: {released}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Process {process.pid} completed.", released

    @staticmethod
    def release_resources(proc_id: int, release_dict: Dict[str, int]) -> Tuple[bool, str]:
        process = db.session.get(Process, proc_id)
        if not process:
            return False, "Process not found."

        alloc_map = {a.resource.resource_id: a for a in process.allocations if a.resource}
        for rid, qty in release_dict.items():
            if qty < 0:
                return False, f"Release quantity for {rid} cannot be negative."
            if rid not in alloc_map:
                return False, f"Resource {rid} is not associated with process."
            if qty > alloc_map[rid].allocated:
                return False, f"Cannot release {qty} units of {rid}; only {alloc_map[rid].allocated} currently allocated."

        # Apply release
        for rid, qty in release_dict.items():
            alloc_map[rid].allocated -= qty
            alloc_map[rid].resource.available_instances += qty

        # Update process state if needed
        total_remaining = sum(a.allocated for a in process.allocations)
        if total_remaining == 0 and process.state == ProcessState.RUNNING:
            process.state = ProcessState.READY

        log = EventLog(
            event_type="RESOURCE_RELEASED",
            description=f"Process {process.pid} released resources: {release_dict}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Resources released successfully for process {process.pid}."

    @staticmethod
    def delete_process(proc_id: int) -> Tuple[bool, str]:
        process = db.session.get(Process, proc_id)
        if not process:
            return False, "Process not found."

        pid = process.pid
        # Release any held resources before deletion
        for a in process.allocations:
            if a.allocated > 0 and a.resource:
                a.resource.available_instances += a.allocated

        db.session.delete(process)
        log = EventLog(
            event_type="PROCESS_DELETED",
            description=f"Deleted process {pid} and restored resources."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Process {pid} deleted."
