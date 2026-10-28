"""
Scheduler Manager.
Maintains in-memory simulation state for the Deadlock-Aware CPU Scheduler,
bridging DB processes/resources and the algorithmic engine.
"""
from typing import Dict, Any, Optional
from algorithms.scheduler import CPUSchedulerEngine, ScheduledTask, load_scheduler_preset
from database.models import Process, Resource

class SchedulerManager:
    _active_engine: Optional[CPUSchedulerEngine] = None
    _active_preset: str = "balanced"

    @classmethod
    def get_engine(cls) -> CPUSchedulerEngine:
        if cls._active_engine is None:
            cls.initialize_preset("balanced", policy="RR", mode="DEADLOCK_AWARE", quantum=2)
        return cls._active_engine

    @classmethod
    def initialize_preset(
        cls,
        preset_name: str,
        policy: str = "RR",
        mode: str = "DEADLOCK_AWARE",
        quantum: int = 2,
        aging_threshold: int = 3,
        aging_enabled: bool = True
    ) -> CPUSchedulerEngine:
        cls._active_preset = preset_name
        engine = load_scheduler_preset(preset_name, policy=policy, mode=mode)
        engine.quantum = max(1, int(quantum))
        engine.aging_threshold = max(1, int(aging_threshold))
        engine.aging_enabled = bool(aging_enabled)
        cls._active_engine = engine
        return engine

    @classmethod
    def initialize_from_db(
        cls,
        policy: str = "RR",
        mode: str = "DEADLOCK_AWARE",
        quantum: int = 2,
        aging_threshold: int = 3,
        aging_enabled: bool = True
    ) -> CPUSchedulerEngine:
        """
        Loads the currently configured database resources and processes into the CPU scheduler.
        """
        resources = Resource.query.all()
        processes = Process.query.all()

        sys_resources = {r.resource_id: r.total_instances for r in resources}
        if not sys_resources:
            # Fallback if DB empty
            return cls.initialize_preset("balanced", policy=policy, mode=mode, quantum=quantum)

        engine = CPUSchedulerEngine(
            system_resources=sys_resources,
            policy=policy,
            quantum=quantum,
            mode=mode,
            aging_threshold=aging_threshold,
            aging_enabled=aging_enabled
        )

        for idx, p in enumerate(processes):
            p_dict = p.to_dict()
            burst = 4 + (idx % 3) * 2  # deterministic burst 4, 6, 8
            arrival = idx
            priority = 1 + (idx % 4)
            max_claim = p_dict.get("maximum", {})

            # Generate realistic resource events based on need
            events = {}
            need = p_dict.get("need", {})
            non_zero_need = {r: amt for r, amt in need.items() if amt > 0}
            if non_zero_need:
                events[1] = {"request": non_zero_need}
                events[burst - 1] = {"release": non_zero_need}

            task = ScheduledTask(
                pid=p.pid,
                name=p.name,
                arrival_time=arrival,
                burst_time=burst,
                priority=priority,
                max_claim=max_claim,
                resource_events=events
            )
            # Pre-populate held resources from DB allocations
            task.held_resources = p_dict.get("allocation", {})
            engine.add_task(task)

        # Deduct initial held allocations from available
        for t in engine.tasks.values():
            for r, amt in t.held_resources.items():
                engine.available_resources[r] = max(0, engine.available_resources.get(r, 0) - amt)

        cls._active_engine = engine
        cls._active_preset = "database"
        return engine

    @classmethod
    def tick(cls) -> Dict[str, Any]:
        engine = cls.get_engine()
        return engine.tick()

    @classmethod
    def run_all(cls, max_ticks: int = 60) -> Dict[str, Any]:
        engine = cls.get_engine()
        return engine.run_all(max_ticks=max_ticks)

    @classmethod
    def reset(cls) -> Dict[str, Any]:
        engine = cls.get_engine()
        policy = engine.policy
        mode = engine.mode
        quantum = engine.quantum
        aging_threshold = engine.aging_threshold
        aging_enabled = engine.aging_enabled

        if cls._active_preset == "database":
            cls.initialize_from_db(
                policy=policy, mode=mode, quantum=quantum,
                aging_threshold=aging_threshold, aging_enabled=aging_enabled
            )
        else:
            cls.initialize_preset(
                cls._active_preset, policy=policy, mode=mode, quantum=quantum,
                aging_threshold=aging_threshold, aging_enabled=aging_enabled
            )
        return cls.get_engine().get_state()
