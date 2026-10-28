# System Architecture & Technical Design

## 1. Overview

**Deadlock-Safe Task Manager** is an educational, full-stack Operating Systems application designed to demonstrate and visualize real resource allocation, deadlock avoidance (Banker's Algorithm), deadlock detection, and recovery strategies.

---

## 2. Layered Architecture

The application adopts a strictly separated layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                 Presentation / UI Layer                     │
│  HTML5 + Bootstrap 5 + Vanilla JS + Cytoscape.js + Chart.js │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    Routing & API Layer                      │
│             Flask Blueprints (API & Page Views)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Simulation Engine Layer                    │
│   Simulator, ProcessManager, ResourceManager, Scenarios     │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼──────────────┐ ┌──────────────▼──────────────┐
│     OS Algorithms Layer     │ │      Persistence Layer      │
│  - Banker's Safety          │ │  SQLite Database            │
│  - Resource-Request         │ │  SQLAlchemy ORM             │
│  - Deadlock Detection       │ │  Models: Process, Resource, │
│  - Wait-For Graph Cycles    │ │          Allocation, etc.   │
│  - Recovery Strategies      │ └─────────────────────────────┘
└─────────────────────────────┘
```

---

## 3. Directory Layout

- `app.py`: Application entry point and factory function (`create_app`).
- `config.py`: Configuration classes for production and testing.
- `requirements.txt`: Lightweight project dependencies.
- `database/`:
  - `database.py`: SQLAlchemy instance.
  - `models.py`: Data models for Process, Resource, Allocation, MaximumNeed, ResourceRequest, EventLog, Scenario.
- `algorithms/`:
  - `safety.py`: Pure implementation of Dijkstra's Safety Algorithm with step traces.
  - `bankers.py`: Avoidance coordinator and matrix validation.
  - `resource_request.py`: 5-step resource-request algorithm with tentative allocations and rollbacks.
  - `deadlock_detection.py`: Multi-instance deadlock detection algorithm.
  - `wait_for_graph.py`: Directed graph cycle finder (DFS with cycle canonicalization).
  - `graph_builder.py`: Converts state into Cytoscape.js RAG & WFG JSON.
  - `recovery.py`: Process termination and simulated resource preemption.
- `simulation/`:
  - `process_manager.py`: Process lifecycle (create, request, release, terminate, complete).
  - `resource_manager.py`: Resource lifecycle and instance synchronization.
  - `simulator.py`: Central orchestrator between database and algorithms.
  - `scenarios.py`: Predefined catalog and custom scenario loader.
  - `validation.py`: Data consistency rules and constraint checks.
- `routes/`:
  - `api.py`: REST JSON endpoints.
  - `dashboard.py`, `processes.py`, `resources.py`, `algorithms.py`, `scenarios.py`, `logs.py`: Web view routes.
- `templates/`: Jinja2 templates (dashboard, matrices, safety, resource_request, deadlock_detection, graphs, scenarios, logs, monitor, documentation, settings).
- `static/`: CSS styles and dedicated JavaScript controllers for each screen.
- `tests/`: 26 automated unit and integration tests using pytest.
- `docs/`: Academic documentation for viva and project evaluation.

---

## 4. Data Consistency Guarantees

1. **Need Invariance**: Remaining Need is always computed as:
   $$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$
2. **Resource Invariance**: Available instances strictly equal total instances minus the sum of active allocations:
   $$\text{Available}[j] = \text{Total}[j] - \sum_{i} \text{Allocation}[i][j]$$
3. **No Over-allocation**: At no point can $\text{Allocation}[i][j] > \text{Maximum}[i][j]$ or $\sum \text{Allocation}[i][j] > \text{Total}[j]$.
4. **Isolated Host Telemetry**: Hardware metrics from `psutil` are purely informative and never cross into simulated algorithm states.
