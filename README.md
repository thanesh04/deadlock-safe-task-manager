# Deadlock-Safe Task Manager

### An Operating Systems-Based Task Manager for Deadlock Detection, Avoidance, and Safe Resource Allocation

---

## 1. Problem Statement & Academic Motivation

In modern multi-programming Operating Systems, multiple concurrent processes compete for a finite set of system resources (CPU cores, memory, disk channels, device locks). When processes request resources held by others while holding resources themselves, circular wait conditions can develop, culminating in a **deadlock** where all involved tasks remain permanently blocked.

Traditional task managers merely display process lists and passive CPU/RAM percentages without explaining or modeling how processes acquire, wait for, or release resources. 

The **Deadlock-Safe Task Manager** bridges this pedagogical gap by providing an interactive, full-stack, algorithmically authentic platform where students and educators can:
1. Model arbitrary multi-instance resources and competing processes.
2. Dynamically execute Dijkstra's **Banker's Safety Algorithm** to verify safe execution sequences.
3. Simulate the **Banker's Resource-Request Algorithm** with tentative allocations, safety checks, and rollbacks.
4. Run independent **Deadlock Detection** on active allocation and request states.
5. Visualize dependencies using **Resource Allocation Graphs (RAG)** and **Wait-For Graphs (WFG)** powered by Cytoscape.js.
6. Execute and observe **Deadlock Recovery** via process termination and simulated resource preemption.

---

## 2. Core Features

- **Dynamic Process & Resource Management**: Create, edit, and delete processes and multi-instance resources with automatic consistency validation.
- **Deadlock-Aware CPU Scheduler & Interactive Gantt Chart**:
  - Full CPU scheduling simulation (Round Robin, SRTF, Preemptive Priority, FCFS) coordinated with Banker's Safety Admission.
  - Interactive, animated Gantt chart with clock ticks, play/pause controls, and instant context-switching upon safety intercepts.
  - **Dynamic Priority Aging**: Prevents process starvation by automatically elevating the priority of tasks blocked by Banker's safety checks.
  - **Process Behavioral Anomaly & Greed Detection**: Computes real-time Greed Index (% of system capacity) and flags resource hoarding.
  - **Deadlock Showdown**: Toggle between Naive allocation (demonstrating real circular wait stalls) and Deadlock-Aware avoidance.
- **Operating Systems Matrices**: Real-time visualization of the Available vector, Allocation matrix, Maximum Demand matrix, and dynamically calculated Need matrix ($\text{Need} = \text{Max} - \text{Alloc}$).
- **Step-by-Step Banker's Algorithm Trace**: Detailed, transparent execution traces showing the Work vector changes at each step and generating the complete safe sequence.
- **Interactive 5-Step Resource-Request Stepper**:
  - Step 1: Check $\text{Request} \le \text{Need}$
  - Step 2: Check $\text{Request} \le \text{Available}$
  - Step 3: Simulate Tentative State
  - Step 4: Run Safety Algorithm on tentative matrices
  - Step 5: Commit if Safe, Roll back if Unsafe
- **Multi-Instance Deadlock Detection**: Separate from avoidance; evaluates active requests without requiring prior maximum claims.
- **Interactive Graphs (Cytoscape.js)**:
  - **Resource Allocation Graph (RAG)**: Circular process nodes, rectangular resource nodes, allocation and request edges.
  - **Wait-For Graph (WFG)**: Process-to-process wait dependencies.
  - **Deadlock Cycle Highlighting**: Automatically identifies and highlights circular wait cycles in bright red.
- **Deadlock Recovery Engine**:
  - Single or multi-process termination with instant resource reclamation.
  - Simulated resource preemption to test resolution without killing processes.
  - Automatic re-detection upon recovery to verify resolution.
- **Predefined Academic Scenarios & 1-Click Demo Mode**:
  - Safe State (Textbook 5 processes, 3 resources)
  - Unsafe State
  - Two-Process Circular Deadlock
  - Three-Process Circular Deadlock
  - Safely Accepted Request
  - Denied Unsafe Request
  - Deadlock Recovery Demo
- **Audit Log & Event History**: Comprehensive chronological log of all simulation actions with real-time search.
- **Isolated Real-System Monitor (psutil)**: Live host hardware telemetry (CPU, RAM, Windows process count), clearly separated from simulated algorithms.

---

## 3. Understanding the Simulation (Real vs. Simulated)

> **CORE CONCEPT**: This project is an **Educational Operating Systems Simulator**. The simulated processes ($P_0$–$P_4$) and resources ($R_0$–$R_2$) are mathematical models stored in an SQLite database. They do NOT interact with your physical Windows kernel or CPU/RAM.

| Concept | Simulation Model | Real Host Hardware Connection |
| :--- | :--- | :--- |
| **Simulated Processes** | Database rows in `processes` table ($P_0, P_1, \dots$). Lifecycle states: `READY`, `RUNNING`, `DEADLOCKED`, `TERMINATED`. | **NONE.** Terminating $P_1$ does not kill any Windows processes. |
| **Simulated Resources** | Discrete integer tokens in `resources` table ($R_0$ CPU Core, $R_1$ Memory, $R_2$ Disk). | **NONE.** Allocating $R_1$ does not occupy physical RAM on your motherboard. |
| **OS Matrices** | Real-time tables for Available, Allocation, Maximum Demand, and dynamically calculated Need ($\text{Need} = \text{Max} - \text{Alloc}$). | **NONE.** Pure mathematical representations of the simulated state. |
| **Banker's Algorithm** | Proactive **Deadlock Avoidance** algorithm verifying safe execution sequences $\langle P_1 \to P_3 \to \dots \rangle$. | **NONE.** Pure in-memory Python algorithmic analysis (`algorithms/safety.py`). |
| **Deadlock Detection** | Reactive detection examining active requests against available resources without requiring maximum claims. | **NONE.** Identifies circular wait sets among simulated processes. |
| **RAG & Wait-For Graphs** | Interactive directed graphs rendered via Cytoscape.js with automated cycle detection (DFS). | **NONE.** Visualizes dependencies between simulated processes and resources. |
| **Predefined Scenarios** | 7 curated textbook scenarios for deterministic, 1-click viva demonstrations. | **NONE.** Stored configurations in `simulation/scenarios.py`. |
| **Real Host OS Monitor** | Live hardware gauges and process count queried via Python's `psutil` library. | **YES (READ-ONLY).** Live Windows CPU %, physical RAM GB, swap %, and active Windows task count. |

---

## 4. Comprehensive Documentation Index

The `docs/` folder contains 21 dedicated guides created specifically for students and examiners:

1. [docs/BITE303P_Project_Report.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/BITE303P_Project_Report.md) - **🎓 OFFICIAL BITE303P ACADEMIC PROJECT REPORT (VIT Specification, 40–45 Pages, Fall 2026-27, Dr. G.N. Vivekananda)**.
2. [docs/project_understanding.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/project_understanding.md) - High-level student-friendly explanation of the project.
3. [docs/project_flow.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/project_flow.md) - End-to-end flowchart from boot to deadlock recovery.
4. [docs/simulated_processes.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/simulated_processes.md) - Deep dive into simulated processes vs. Windows tasks.
5. [docs/simulated_resources.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/simulated_resources.md) - Explanation of $R_0, R_1, R_2$ and resource invariants.
6. [docs/matrices_and_vectors.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/matrices_and_vectors.md) - Mathematical guide to Available, Allocation, Max, and Need.
7. [docs/bankers_algorithm.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/bankers_algorithm.md) - Banker's avoidance theory, Work/Finish vectors, and traces.
8. [docs/resource_request_flow.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/resource_request_flow.md) - The 5-step request decision timeline and rollbacks.
9. [docs/deadlock_detection.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/deadlock_detection.md) - Multi-instance detection algorithm and Coffman conditions.
10. [docs/graphs.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/graphs.md) - Cytoscape.js Resource Allocation and Wait-For Graphs.
11. [docs/predefined_scenarios.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/predefined_scenarios.md) - Breakdown of the 7 built-in textbook scenarios.
12. [docs/deadlock_recovery.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/deadlock_recovery.md) - Process termination and simulated resource preemption.
13. [docs/real_os_monitor.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/real_os_monitor.md) - Low-level host telemetry via `psutil` and architectural isolation.
14. [docs/data_flow_and_database.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/data_flow_and_database.md) - SQLite schema, SQLAlchemy models, and data lifecycle.
15. [docs/demo_guide.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/demo_guide.md) - **10–15 Minute Spoken Script for Teacher/Viva Demonstrations**.
16. [docs/viva_questions.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/viva_questions.md) - **35 Likely Viva Questions & Model Answers**.
17. [docs/real_vs_simulated.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/real_vs_simulated.md) - Feature-by-feature comparison table.
18. [docs/limitations_and_future_scope.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/limitations_and_future_scope.md) - Academic boundaries and realistic enhancements.
19. [docs/scheduler_demonstration_guide.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/scheduler_demonstration_guide.md) - **⭐ Complete Word-for-Word Scheduler Viva Demonstration Script & Technical Walkthrough**.
20. [docs/novelty_and_architectural_link.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/novelty_and_architectural_link.md) - **⭐ Project Novelty Thesis & Architectural Linkage to Deadlock-Safe Task Manager**.
21. [docs/deadlock_aware_scheduler.md](file:///d:/disk%20d/project/Dead-lock%20Safe%20Task%20Manager/docs/deadlock_aware_scheduler.md) - Deadlock-Aware CPU Scheduler, Interactive Gantt Timeline, Dynamic Aging & Anomaly Reference.

---

## 5. Technology Stack

- **Backend**: Python 3.14+, Flask 3.1+, Flask-SQLAlchemy 3.1+, SQLite
- **Algorithms**: Pure Python OS modules (`algorithms/safety.py`, `algorithms/bankers.py`, `algorithms/resource_request.py`, `algorithms/deadlock_detection.py`, `algorithms/recovery.py`, `algorithms/wait_for_graph.py`)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons
- **Visualization**: Cytoscape.js 3.28 (Interactive Graphs), Chart.js 4.4 (State & Resource Utilization)
- **Host Telemetry**: `psutil`
- **Testing**: `pytest` (26 automated test cases)

---

## 4. Project Directory Structure

```
Dead-lock Safe Task Manager/
│
├── app.py                      # Flask Application Factory & Entry Point
├── config.py                   # Configuration (Development & Testing)
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Documentation
├── .gitignore                  # Git Ignore Rules
│
├── database/                   # Database Layer
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy db instance
│   └── models.py               # Process, Resource, Allocation, Request, Log models
│
├── algorithms/                 # Pure OS Algorithm Implementations
│   ├── __init__.py
│   ├── safety.py               # Banker's Safety Algorithm
│   ├── bankers.py              # Avoidance & Matrix Coordinator
│   ├── resource_request.py     # Banker's 5-step Request Evaluation
│   ├── deadlock_detection.py   # Multi-Instance Deadlock Detection
│   ├── wait_for_graph.py       # WFG builder & Cycle Detection (DFS)
│   ├── graph_builder.py        # Cytoscape.js RAG/WFG formatters
│   └── recovery.py             # Termination & Preemption Recovery
│
├── simulation/                 # Simulation Engine & State Sync
│   ├── __init__.py
│   ├── process_manager.py      # Process lifecycle & allocation sync
│   ├── resource_manager.py     # Resource instance pooling & validation
│   ├── simulator.py            # Central orchestrator connecting DB & Algorithms
│   ├── scenarios.py            # Predefined & Custom Scenario Loader
│   └── validation.py           # Integrity & constraint validation
│
├── routes/                     # Presentation & API Layer
│   ├── __init__.py
│   ├── api.py                  # Full REST JSON API
│   ├── dashboard.py            # Dashboard, Matrices, Graphs, Monitor views
│   ├── processes.py            # Process management view
│   ├── resources.py            # Resource pool view
│   ├── algorithms.py           # Safety, Request, & Detection views
│   ├── scenarios.py            # Scenarios catalog view
│   └── logs.py                 # Audit trail view
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Base layout with sidebar, topbar, & demo presets
│   ├── dashboard.html          # Overview dashboard with charts & stat cards
│   ├── processes.html          # Process management & action modals
│   ├── resources.html          # Resource pool management
│   ├── matrices.html           # Allocation, Max, Need, Available tables
│   ├── safety.html             # Safety analysis & step trace
│   ├── resource_request.html   # Banker's request stepper
│   ├── deadlock_detection.html # Deadlock detection & recovery panel
│   ├── graphs.html             # Cytoscape.js RAG & WFG visualization
│   ├── scenarios.html          # Scenarios catalog & custom JSON builder
│   ├── logs.html               # System event history & search
│   ├── monitor.html            # Host OS psutil telemetry
│   ├── documentation.html      # Academic theory & algorithm guide
│   └── settings.html           # Reset & data purge controls
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern OS styling & status badges
│   └── js/
│       ├── dashboard.js        # Dashboard metrics & Chart.js charts
│       ├── processes.js        # Process table & modals
│       ├── resources.js        # Resource CRUD & utilization bars
│       ├── matrices.js         # Dynamic 2D matrix rendering
│       ├── safety.js           # Safety algorithm runner & trace timeline
│       ├── resource_request.js # Request evaluation stepper
│       ├── deadlock_detection.js # Detection & recovery actions
│       ├── graphs.js           # Cytoscape.js graph controllers
│       └── scenarios.js        # Scenario loader & builder
│
├── tests/                      # Automated Test Suite (26 tests)
│   ├── __init__.py
│   ├── test_safety.py          # Safety algorithm tests
│   ├── test_bankers.py         # Matrix validation tests
│   ├── test_resource_request.py# Request evaluation & rollback tests
│   ├── test_deadlock_detection.py # Detection & cycle tests
│   ├── test_recovery.py        # Termination & preemption tests
│   ├── test_process_manager.py # Process lifecycle tests
│   ├── test_resource_manager.py# Resource management tests
│   ├── test_validation.py      # Constraint tests
│   └── test_api.py             # End-to-end REST API integration tests
│
└── docs/                       # Academic Documentation
    ├── architecture.md         # System Architecture & Design
    ├── algorithms.md           # Algorithm Formulations & Complexities
    ├── user_manual.md          # User Manual & Demonstration Guide
    └── testing.md              # Test Suite & Quality Assurance Report
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.14.3)
- Windows PowerShell / Command Prompt / Bash

### Step 1: Clone or Open Workspace
```powershell
cd "d:\disk d\project\Dead-lock Safe Task Manager"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Run Application
```powershell
python app.py
```

### Step 5: Open Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 6. Running Automated Tests

Run the full pytest suite with verbose output:
```powershell
.\venv\Scripts\pytest -v
```

Expected output:
```
tests/test_api.py::test_api_load_scenario_and_safety_check PASSED
tests/test_api.py::test_api_deadlock_scenario_and_recovery PASSED
tests/test_api.py::test_api_system_monitor PASSED
tests/test_bankers.py::test_bankers_need_computation PASSED
tests/test_bankers.py::test_bankers_validation_negative_allocation PASSED
tests/test_bankers.py::test_bankers_validation_allocation_exceeds_maximum PASSED
tests/test_deadlock_detection.py::test_no_deadlock PASSED
tests/test_deadlock_detection.py::test_two_process_deadlock PASSED
tests/test_deadlock_detection.py::test_three_process_deadlock PASSED
tests/test_deadlock_detection.py::test_deadlock_with_one_independent_process PASSED
tests/test_process_manager.py::test_process_lifecycle PASSED
tests/test_recovery.py::test_termination_resolves_deadlock PASSED
tests/test_recovery.py::test_simulated_preemption PASSED
tests/test_resource_manager.py::test_resource_crud_and_safety_checks PASSED
tests/test_resource_request.py::test_safe_resource_request PASSED
tests/test_resource_request.py::test_request_exceeds_need PASSED
tests/test_resource_request.py::test_request_exceeds_available PASSED
tests/test_resource_request.py::test_unsafe_request_denied PASSED
tests/test_safety.py::test_safety_algorithm_safe_state PASSED
tests/test_safety.py::test_safety_algorithm_unsafe_state PASSED
tests/test_safety.py::test_safety_algorithm_single_process_safe PASSED
tests/test_safety.py::test_safety_algorithm_zero_allocation PASSED
tests/test_validation.py::test_validate_process_empty_pid PASSED
tests/test_validation.py::test_validate_process_duplicate_pid PASSED
tests/test_validation.py::test_validate_resource_zero_or_negative PASSED
tests/test_validation.py::test_validate_matrix_consistency_allocation_exceeds_max PASSED

============================= 26 passed in 1.73s ==============================
```

---

## 7. Viva / Demonstration Walkthrough

Use the **Demo Mode** button in the top navigation bar to demonstrate all key OS principles to external examiners:

1. **Demo Safe State**:
   - Loads the textbook 5-process scenario.
   - Automatically navigates to **Safety Analysis**.
   - Click **Run Safety Algorithm** to show the generated sequence: $P_1 \to P_3 \to P_4 \to P_0 \to P_2$.
2. **Demo Unsafe State**:
   - Loads an unsafe state where remaining need exceeds available work.
   - Shows why no safe sequence can be constructed.
3. **Demo Deadlock**:
   - Loads $P_1$ holding $R_1$ requesting $R_2$, and $P_2$ holding $R_2$ requesting $R_1$.
   - Navigates to **Deadlock Detection**.
   - Shows detected deadlocked processes and prompts recovery.
4. **Demo Graph Visualization**:
   - Navigate to **Graphs**.
   - Switch between **Resource Allocation Graph (RAG)** and **Wait-For Graph (WFG)**.
   - View the red highlighted deadlock cycle.
5. **Demo Recovery**:
   - On the Deadlock Detection page, click **Terminate Victim** on $P_1$.
   - Shows the immediate reclamation of resources and verification that the deadlock is resolved.

---

## 8. Academic Integrity & Accuracy

- **Deadlock Avoidance vs. Detection**: Banker's Algorithm is properly categorized as an *avoidance* algorithm based on *a priori* maximum claims. The Deadlock Detection algorithm is implemented as a distinct multi-instance detection algorithm based solely on current allocations and active requests.
- **No Mocked Data**: All safety sequences, matrix states, detection outcomes, graph edges, and recovery steps are dynamically computed mathematically on the fly.
- **Isolated Real-System Telemetry**: Real host hardware stats from `psutil` are clearly separated on their own monitor screen and never fed into simulated process algorithms.

---

## 9. Author

Built for B.Tech Information Technology Operating Systems Project Evaluation.
