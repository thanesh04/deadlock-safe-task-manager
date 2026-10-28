"""
Unit tests for Deadlock-Aware CPU Scheduler and Process Anomaly Detector.
"""
import pytest
from algorithms.scheduler import CPUSchedulerEngine, ScheduledTask, load_scheduler_preset
from algorithms.anomaly_detector import ProcessAnomalyDetector

def test_anomaly_detector_greed():
    max_claim = {"R0": 3, "R1": 4}
    total = {"R0": 5, "R1": 5}
    greed = ProcessAnomalyDetector.calculate_greed_index(max_claim, total)
    assert greed == 70.0

def test_scheduler_initialization():
    engine = load_scheduler_preset("balanced", policy="RR", mode="DEADLOCK_AWARE")
    state = engine.get_state()
    assert state["clock"] == 0
    assert len(state["tasks"]) == 4
    assert state["policy"] == "RR"
    assert state["mode"] == "DEADLOCK_AWARE"

def test_scheduler_tick_progression():
    engine = load_scheduler_preset("balanced", policy="RR", mode="DEADLOCK_AWARE")
    state_t1 = engine.tick()
    assert state_t1["clock"] == 1
    assert len(state_t1["gantt_timeline"]) == 1
    # At T=0, P0 arrives and runs
    assert state_t1["gantt_timeline"][0]["pid"] == "P0"

def test_scheduler_run_all_completes():
    engine = load_scheduler_preset("balanced", policy="RR", mode="DEADLOCK_AWARE")
    final_state = engine.run_all(max_ticks=50)
    assert final_state["is_completed"] is True
    assert final_state["metrics"]["completed_tasks"] == 4
    assert final_state["metrics"]["cpu_utilization_percent"] > 0

def test_naive_mode_deadlock_detection():
    # In naive mode with naive_vs_safe preset, P0 and P1 will circular wait
    engine = load_scheduler_preset("naive_vs_safe", policy="RR", mode="NAIVE")
    state = engine.run_all(max_ticks=20)
    # Circular wait should trigger deadlock in naive mode
    assert engine.is_deadlocked is True or any(t["state"] == "DEADLOCKED" for t in state["tasks"])

def test_deadlock_aware_prevents_deadlock():
    # In deadlock-aware mode with naive_vs_safe preset, Banker's intercepts and prevents deadlock!
    engine = load_scheduler_preset("naive_vs_safe", policy="RR", mode="DEADLOCK_AWARE")
    state = engine.run_all(max_ticks=30)
    assert state["metrics"]["deadlocks_averted"] > 0
    assert engine.is_deadlocked is False
