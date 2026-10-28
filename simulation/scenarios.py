"""
Predefined and Custom OS Scenarios for Academic Demonstration.
Includes textbook scenarios (Safe State, Unsafe State, Deadlock cycles, etc.).
"""
from typing import Dict, List, Any, Optional
from database.database import db
from database.models import Process, Resource, Allocation, MaximumNeed, ResourceRequest, EventLog, Scenario, ProcessState
from simulation.simulator import Simulator

PREDEFINED_SCENARIOS = {
    "safe_state": {
        "name": "Classic Safe State",
        "description": "Textbook Banker's Algorithm safe state (5 processes P0-P4, 3 resources R0, R1, R2). Demonstrates safe sequence generation.",
        "resources": [
            {"resource_id": "R0", "name": "CPU Core", "total": 10},
            {"resource_id": "R1", "name": "Memory (GB)", "total": 5},
            {"resource_id": "R2", "name": "Disk Channel", "total": 7}
        ],
        "processes": [
            {"pid": "P0", "name": "Web Server", "allocation": {"R0": 0, "R1": 1, "R2": 0}, "maximum": {"R0": 7, "R1": 5, "R2": 3}},
            {"pid": "P1", "name": "Database Worker", "allocation": {"R0": 2, "R1": 0, "R2": 0}, "maximum": {"R0": 3, "R1": 2, "R2": 2}},
            {"pid": "P2", "name": "Analytics Engine", "allocation": {"R0": 3, "R1": 0, "R2": 2}, "maximum": {"R0": 9, "R1": 0, "R2": 2}},
            {"pid": "P3", "name": "Cache Service", "allocation": {"R0": 2, "R1": 1, "R2": 1}, "maximum": {"R0": 2, "R1": 2, "R2": 2}},
            {"pid": "P4", "name": "Backup Agent", "allocation": {"R0": 0, "R1": 0, "R2": 2}, "maximum": {"R0": 4, "R1": 3, "R2": 3}}
        ],
        "requests": []
    },
    "unsafe_state": {
        "name": "Unsafe State (Deadlock Avoidance)",
        "description": "System state where available resources are insufficient to satisfy any remaining process need to completion.",
        "resources": [
            {"resource_id": "R0", "name": "CPU Core", "total": 10},
            {"resource_id": "R1", "name": "Memory (GB)", "total": 5},
            {"resource_id": "R2", "name": "Disk Channel", "total": 7}
        ],
        "processes": [
            {"pid": "P0", "name": "Web Server", "allocation": {"R0": 0, "R1": 3, "R2": 0}, "maximum": {"R0": 7, "R1": 5, "R2": 3}},
            {"pid": "P1", "name": "Database Worker", "allocation": {"R0": 3, "R1": 0, "R2": 2}, "maximum": {"R0": 3, "R1": 2, "R2": 2}},
            {"pid": "P2", "name": "Analytics Engine", "allocation": {"R0": 4, "R1": 0, "R2": 2}, "maximum": {"R0": 9, "R1": 0, "R2": 2}},
            {"pid": "P3", "name": "Cache Service", "allocation": {"R0": 2, "R1": 1, "R2": 1}, "maximum": {"R0": 5, "R1": 2, "R2": 2}},
            {"pid": "P4", "name": "Backup Agent", "allocation": {"R0": 1, "R1": 1, "R2": 2}, "maximum": {"R0": 4, "R1": 3, "R2": 3}}
        ],
        "requests": []
    },
    "two_process_deadlock": {
        "name": "Two-Process Circular Deadlock",
        "description": "Mutual Hold-and-Wait deadlock: P1 holds R1 and requests R2; P2 holds R2 and requests R1.",
        "resources": [
            {"resource_id": "R1", "name": "Scanner", "total": 1},
            {"resource_id": "R2", "name": "Printer", "total": 1}
        ],
        "processes": [
            {"pid": "P1", "name": "Process 1", "allocation": {"R1": 1, "R2": 0}, "maximum": {"R1": 1, "R2": 1}},
            {"pid": "P2", "name": "Process 2", "allocation": {"R1": 0, "R2": 1}, "maximum": {"R1": 1, "R2": 1}}
        ],
        "requests": [
            {"pid": "P1", "request": {"R1": 0, "R2": 1}},
            {"pid": "P2", "request": {"R1": 1, "R2": 0}}
        ]
    },
    "three_process_deadlock": {
        "name": "Three-Process Circular Deadlock",
        "description": "P1 holds R1 and requests R2; P2 holds R2 and requests R3; P3 holds R3 and requests R1.",
        "resources": [
            {"resource_id": "R1", "name": "Resource 1", "total": 1},
            {"resource_id": "R2", "name": "Resource 2", "total": 1},
            {"resource_id": "R3", "name": "Resource 3", "total": 1}
        ],
        "processes": [
            {"pid": "P1", "name": "Task Alpha", "allocation": {"R1": 1, "R2": 0, "R3": 0}, "maximum": {"R1": 1, "R2": 1, "R3": 0}},
            {"pid": "P2", "name": "Task Beta", "allocation": {"R1": 0, "R2": 1, "R3": 0}, "maximum": {"R1": 0, "R2": 1, "R3": 1}},
            {"pid": "P3", "name": "Task Gamma", "allocation": {"R1": 0, "R2": 0, "R3": 1}, "maximum": {"R1": 1, "R2": 0, "R3": 1}}
        ],
        "requests": [
            {"pid": "P1", "request": {"R1": 0, "R2": 1, "R3": 0}},
            {"pid": "P2", "request": {"R1": 0, "R2": 0, "R3": 1}},
            {"pid": "P3", "request": {"R1": 1, "R2": 0, "R3": 0}}
        ]
    },
    "accepted_request": {
        "name": "Safely Granted Request",
        "description": "Process P1 requests (1, 0, 2) in a safe system state. The request is granted because the resulting state is safe.",
        "resources": [
            {"resource_id": "R0", "name": "CPU Core", "total": 10},
            {"resource_id": "R1", "name": "Memory (GB)", "total": 5},
            {"resource_id": "R2", "name": "Disk Channel", "total": 7}
        ],
        "processes": [
            {"pid": "P0", "name": "Web Server", "allocation": {"R0": 0, "R1": 1, "R2": 0}, "maximum": {"R0": 7, "R1": 5, "R2": 3}},
            {"pid": "P1", "name": "Database Worker", "allocation": {"R0": 2, "R1": 0, "R2": 0}, "maximum": {"R0": 3, "R1": 2, "R2": 2}},
            {"pid": "P2", "name": "Analytics Engine", "allocation": {"R0": 3, "R1": 0, "R2": 2}, "maximum": {"R0": 9, "R1": 0, "R2": 2}},
            {"pid": "P3", "name": "Cache Service", "allocation": {"R0": 2, "R1": 1, "R2": 1}, "maximum": {"R0": 2, "R1": 2, "R2": 2}},
            {"pid": "P4", "name": "Backup Agent", "allocation": {"R0": 0, "R1": 0, "R2": 2}, "maximum": {"R0": 4, "R1": 3, "R2": 3}}
        ],
        "requests": [
            {"pid": "P1", "request": {"R0": 1, "R1": 0, "R2": 2}}
        ]
    },
    "rejected_request": {
        "name": "Denied Request (Avoids Unsafe State)",
        "description": "Process P0 requests (0, 2, 0). Even though resources are available, granting it leaves system in an unsafe state.",
        "resources": [
            {"resource_id": "R0", "name": "CPU Core", "total": 10},
            {"resource_id": "R1", "name": "Memory (GB)", "total": 5},
            {"resource_id": "R2", "name": "Disk Channel", "total": 7}
        ],
        "processes": [
            {"pid": "P0", "name": "Web Server", "allocation": {"R0": 0, "R1": 1, "R2": 0}, "maximum": {"R0": 7, "R1": 5, "R2": 3}},
            {"pid": "P1", "name": "Database Worker", "allocation": {"R0": 3, "R1": 0, "R2": 2}, "maximum": {"R0": 3, "R1": 2, "R2": 2}},
            {"pid": "P2", "name": "Analytics Engine", "allocation": {"R0": 3, "R1": 0, "R2": 2}, "maximum": {"R0": 9, "R1": 0, "R2": 2}},
            {"pid": "P3", "name": "Cache Service", "allocation": {"R0": 2, "R1": 1, "R2": 1}, "maximum": {"R0": 2, "R1": 2, "R2": 2}},
            {"pid": "P4", "name": "Backup Agent", "allocation": {"R0": 0, "R1": 0, "R2": 2}, "maximum": {"R0": 4, "R1": 3, "R2": 3}}
        ],
        "requests": [
            {"pid": "P0", "request": {"R0": 0, "R1": 2, "R2": 0}}
        ]
    },
    "deadlock_recovery": {
        "name": "Deadlock Recovery Scenario",
        "description": "A deadlocked system designed to demonstrate recovery via process termination or simulated resource preemption.",
        "resources": [
            {"resource_id": "R1", "name": "GPU Unit", "total": 2},
            {"resource_id": "R2", "name": "Database Connection", "total": 2}
        ],
        "processes": [
            {"pid": "P1", "name": "ML Training Job", "allocation": {"R1": 1, "R2": 0}, "maximum": {"R1": 2, "R2": 1}},
            {"pid": "P2", "name": "Query Engine", "allocation": {"R1": 1, "R2": 1}, "maximum": {"R1": 1, "R2": 2}},
            {"pid": "P3", "name": "ETL Pipeline", "allocation": {"R1": 0, "R2": 1}, "maximum": {"R1": 1, "R2": 1}}
        ],
        "requests": [
            {"pid": "P1", "request": {"R1": 0, "R2": 2}},
            {"pid": "P2", "request": {"R1": 1, "R2": 0}},
            {"pid": "P3", "request": {"R1": 1, "R2": 0}}
        ]
    }
}

class ScenarioManager:
    @staticmethod
    def load_scenario(scenario_key_or_id: str) -> Dict[str, Any]:
        """Loads a predefined scenario or a stored custom scenario."""
        config = None
        scenario_name = ""

        if scenario_key_or_id in PREDEFINED_SCENARIOS:
            config = PREDEFINED_SCENARIOS[scenario_key_or_id]
            scenario_name = config["name"]
        else:
            # Look up in database
            db_scen = Scenario.query.filter((Scenario.id == scenario_key_or_id) | (Scenario.name == scenario_key_or_id)).first()
            if db_scen:
                config = db_scen.configuration
                scenario_name = db_scen.name

        if not config:
            return {"success": False, "message": f"Scenario '{scenario_key_or_id}' not found."}

        # Clear current simulation state
        Simulator.clear_all_data()

        # Create resources
        res_map = {}
        for r_spec in config.get("resources", []):
            rid = r_spec["resource_id"].upper()
            total = int(r_spec["total"])
            res = Resource(
                resource_id=rid,
                name=r_spec.get("name", rid),
                total_instances=total,
                available_instances=total
            )
            db.session.add(res)
            db.session.flush()
            res_map[rid] = res

        # Create processes, maximums, allocations
        proc_map = {}
        for p_spec in config.get("processes", []):
            pid = p_spec["pid"].upper()
            proc = Process(
                pid=pid,
                name=p_spec.get("name", pid),
                state=ProcessState.READY
            )
            db.session.add(proc)
            db.session.flush()
            proc_map[pid] = proc

            allocs = p_spec.get("allocation", {})
            maxims = p_spec.get("maximum", {})

            has_alloc = False
            for rid, res in res_map.items():
                a_val = int(allocs.get(rid, 0))
                m_val = int(maxims.get(rid, a_val))
                db.session.add(Allocation(process_id=proc.id, resource_id=res.id, allocated=a_val))
                db.session.add(MaximumNeed(process_id=proc.id, resource_id=res.id, maximum=m_val))
                res.available_instances -= a_val
                if a_val > 0:
                    has_alloc = True

            proc.state = ProcessState.RUNNING if has_alloc else ProcessState.READY

        # Create requests
        for req_spec in config.get("requests", []):
            pid = req_spec["pid"].upper()
            if pid in proc_map:
                proc = proc_map[pid]
                req_vec = req_spec.get("request", {})
                req_obj = ResourceRequest(
                    process_id=proc.id,
                    request_data=req_vec,
                    status="PENDING",
                    reason="Initial scenario pending request"
                )
                db.session.add(req_obj)
                if any(v > 0 for v in req_vec.values()):
                    proc.state = ProcessState.BLOCKED

        # Log load event
        log = EventLog(
            event_type="SCENARIO_LOADED",
            description=f"Loaded scenario '{scenario_name}'."
        )
        db.session.add(log)
        db.session.commit()

        return {
            "success": True,
            "message": f"Successfully loaded scenario: {scenario_name}",
            "scenario": config
        }

    @staticmethod
    def get_all_scenarios() -> Dict[str, Any]:
        """Returns predefined scenarios and any user-saved scenarios."""
        custom = [s.to_dict() for s in Scenario.query.order_by(Scenario.created_at.desc()).all()]
        return {
            "predefined": PREDEFINED_SCENARIOS,
            "custom": custom
        }

    @staticmethod
    def save_custom_scenario(name: str, description: str, configuration: Dict[str, Any]) -> Tuple[bool, str]:
        if not name or not name.strip():
            return False, "Scenario name is required."

        existing = Scenario.query.filter_by(name=name.strip()).first()
        if existing:
            return False, f"A scenario with name '{name}' already exists."

        scen = Scenario(
            name=name.strip(),
            description=description.strip() if description else "Custom scenario",
            configuration=configuration
        )
        db.session.add(scen)
        db.session.add(EventLog(
            event_type="SCENARIO_SAVED",
            description=f"Saved custom scenario '{name}'."
        ))
        db.session.commit()
        return True, f"Scenario '{name}' saved successfully."
