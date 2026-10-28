# "What is Real vs. Simulated?": Master Architectural Comparison

This reference document provides an unambiguous, line-by-line categorization of every feature in the **Deadlock-Safe Task Manager**, establishing which components are educational mathematical simulations and which interact with real host hardware.

---

## 1. Master Comparison Matrix

| System Feature / Component | Classification | Where it Lives | Real Host Impact? | Detailed Technical Explanation |
| :--- | :--- | :--- | :--- | :--- |
| **Simulated Processes ($P_0$–$P_4$)** | **SIMULATED** | SQLite table `processes` | **NONE** | Pure database rows modeling theoretical tasks. They have no Windows threads, PIDs, or kernel PCBs. |
| **Simulated Resources ($R_0$–$R_2$)** | **SIMULATED** | SQLite table `resources` | **NONE** | Logical integer counters representing theoretical resource pools (e.g., 10 CPU units, 5 RAM units). |
| **Simulation CPU ($R_0$)** | **SIMULATED** | SQLite integer counter | **NONE** | Allocating or releasing $R_0$ alters an integer in the database; it does not change CPU clock or execution threads. |
| **Simulation RAM ($R_1$)** | **SIMULATED** | SQLite integer counter | **NONE** | Allocating $R_1$ does not invoke Windows virtual memory allocations (`VirtualAlloc`/`malloc`). |
| **Simulation Disk ($R_2$)** | **SIMULATED** | SQLite integer counter | **NONE** | Represents logical I/O channels; does not interact with physical hard drives or SSD controllers. |
| **Allocation Matrix** | **SIMULATED** | SQLite table `allocations` | **NONE** | A 2D integer matrix in memory representing who holds what in the simulation model. |
| **Maximum Demand Matrix** | **SIMULATED** | SQLite table `maximum_needs` | **NONE** | Pre-declared upper bounds required for Banker's Algorithm avoidance logic. |
| **Need Matrix** | **SIMULATED** | Computed dynamically in Python | **NONE** | Calculated dynamically as $\text{Need} = \text{Maximum} - \text{Allocation}$. |
| **Available Vector** | **SIMULATED** | SQLite column `available_instances` | **NONE** | Computed as $\text{Total} - \sum \text{Allocated}$. |
| **Banker's Safety Algorithm** | **SIMULATED** | `algorithms/safety.py` | **NONE** | Pure mathematical algorithm executing in Python memory to search for a safe sequence. |
| **Resource-Request Algorithm** | **SIMULATED** | `algorithms/resource_request.py` | **NONE** | Simulates tentative states in memory, tests safety, and commits or rolls back database entries. |
| **Deadlock Detection Algorithm** | **SIMULATED** | `algorithms/deadlock_detection.py` | **NONE** | Evaluates active simulated requests against available resources to detect circular waits. |
| **Resource Allocation Graph (RAG)** | **SIMULATED** | `algorithms/graph_builder.py` & Cytoscape.js | **NONE** | Visual graph built from simulated database matrices; does not read Windows kernel locks. |
| **Wait-For Graph (WFG)** | **SIMULATED** | `algorithms/wait_for_graph.py` & Cytoscape.js | **NONE** | Process-only dependency graph with automated cycle detection (DFS). |
| **Deadlock Recovery Actions** | **SIMULATED** | `algorithms/recovery.py` | **NONE** | Terminates simulated process records and reclaims database counters. |
| **Host CPU Utilization %** | **REAL** | Host Windows Kernel via `psutil` | **READ-ONLY** | Live physical CPU load measured across all real Windows applications. |
| **Host RAM Utilization (GB)** | **REAL** | Host Windows Kernel via `psutil` | **READ-ONLY** | Actual physical RAM sticks installed on motherboard and live Windows memory usage. |
| **Host Swap Memory %** | **REAL** | Host Windows Kernel via `psutil` | **READ-ONLY** | Live Windows paging file (`pagefile.sys`) usage. |
| **Host Process Count** | **REAL** | Host Windows Kernel via `psutil` | **READ-ONLY** | Actual count of real active Windows processes (e.g., 240+ tasks). |
| **Host CPU Cores / Threads** | **REAL** | Host Windows Kernel via `psutil` | **READ-ONLY** | Physical core and logical hyper-thread count of your processor. |

---

## 2. Key Takeaway for Viva Examiners

> "The core of our project is an **Educational Operating Systems Simulator**. All algorithms (Banker's, Deadlock Detection, RAG, WFG, Recovery) operate strictly on **simulated database models**. 
> 
> The **Host OS Monitor** using `psutil` is an isolated, read-only auxiliary module designed to demonstrate real-time host telemetry without interfering with the mathematical purity of the deadlock algorithms."
