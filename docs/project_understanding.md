# Project Understanding: Deadlock-Safe Task Manager

## 1. What is Deadlock-Safe Task Manager?

**Deadlock-Safe Task Manager** is an educational, full-stack Operating Systems (OS) web application. It models how an operating system allocates shared, limited resources to concurrent processes, evaluates whether resource requests can lead to system deadlock, detects existing circular wait deadlocks, visualizes these dependencies using interactive graphs, and provides recovery mechanisms.

The full academic subtitle of the project is:
> **An Operating Systems-Based Task Manager for Deadlock Detection, Avoidance and Safe Resource Allocation**

---

## 2. Why Was This Project Built?

In typical modern desktop task managers (like the Windows Task Manager or macOS Activity Monitor), users only observe **passive telemetry**: CPU usage percentage, current RAM consumption, and a list of process names with their PIDs. 

However, standard task managers do **not**:
- Show how processes declare their maximum resource demands.
- Prevent unsafe resource allocations that could freeze applications.
- Run Dijkstra's Banker's Algorithm to verify whether a safe sequence exists.
- Construct Resource Allocation Graphs (RAG) or Wait-For Graphs (WFG).
- Expose why processes are blocked or waiting on specific shared resources.

This project was built for a **B.Tech Information Technology Operating Systems coursework project** to transform abstract theoretical OS textbook concepts into a tangible, visual, and interactive software system.

---

## 3. What Operating Systems Concepts Are Demonstrated?

1. **Deadlock Avoidance**:
   - Banker's Safety Algorithm (finding a safe execution sequence $\langle P_0, P_1, \dots, P_n \rangle$).
   - Banker's Resource-Request Algorithm (dynamic 5-step test before committing allocations).
2. **Deadlock Detection**:
   - Multi-instance deadlock detection algorithm examining current allocations and active requests without needing maximum claim declarations.
3. **The 4 Necessary Coffman Conditions for Deadlock**:
   - Mutual Exclusion
   - Hold and Wait
   - No Preemption
   - Circular Wait
4. **Graph-Based Deadlock Modeling**:
   - **Resource Allocation Graph (RAG)**: Bipartite graph of process nodes and resource nodes with assignment ($R_j \to P_i$) and request ($P_i \to R_j$) edges.
   - **Wait-For Graph (WFG)**: Process-only directed graph ($P_i \to P_j$) where cycles signify circular waiting.
5. **Deadlock Recovery**:
   - Process termination (aborting victim processes to reclaim held resources).
   - Simulated resource preemption (transferring a unit of a resource from a holder to a requester).
6. **Operating Systems Matrices**:
   - Available Vector: $\text{Available}[m]$
   - Allocation Matrix: $\text{Allocation}[n][m]$
   - Maximum Demand Matrix: $\text{Maximum}[n][m]$
   - Remaining Need Matrix: $\text{Need}[n][m] = \text{Maximum}[n][m] - \text{Allocation}[n][m]$

---
   

## 4. What is Simulated?

**Everything inside the simulation engine is simulated:**
- **Processes ($P_0, P_1, P_2, \dots$)**: These are database records created in the SQLite database (`Process` model). They do not correspond to running `.exe` programs on your Windows machine.
- **Resources ($R_0, R_1, R_2$, CPU Core, Memory, Disk Channel)**: These are logical counters with integer instance quantities (e.g., 10 units of CPU, 5 units of Memory).
- **Allocations & Maximum Claims**: Mathematical integers stored in SQLite tables (`allocations`, `maximum_needs`).
- **Resource Requests & Releases**: Updates to the database counters and in-memory matrices.
- **Process Termination & Completion**: Updating the `state` field of a database row to `TERMINATED` or `COMPLETED`.

---

## 5. What is Actually Connected to the Host Computer?

Only one specific page is connected to your actual host computer hardware:
- **The "Real Host OS Monitor" page** (`/monitor`, backed by `GET /api/system-monitor`).
- This page uses Python's standard `psutil` library to read:
  - Host CPU utilization percentage (`psutil.cpu_percent()`).
  - Host physical core count and logical processor count (`psutil.cpu_count()`).
  - Host physical RAM total, used, and utilization percentage (`psutil.virtual_memory()`).
  - Host swap file memory utilization (`psutil.swap_memory()`).
  - Count of actual active Windows processes running on your PC (`len(psutil.pids())`).

---

## 6. What is NOT Connected to the Host Computer?

- **The simulated processes ($P_0, P_1, P_2, \dots$) have zero connection to Windows processes.**
- **The Banker's Algorithm has zero connection to Windows kernel scheduling.**
- Terminating process $P_1$ on the dashboard will **never** kill Chrome, VS Code, or any Windows system process.
- Requesting 5 units of Memory ($R_1$) will **never** consume real RAM from your physical RAM sticks.
- Releasing CPU units in the simulation will **never** alter your processor's clock frequency or actual core usage.

---

## 7. Simulated Processes vs. Real Windows Processes

| Property | Simulated Process (e.g., $P_1$) | Real Windows Process (e.g., `chrome.exe`) |
| :--- | :--- | :--- |
| **Where it lives** | Row in SQLite table `processes` | Windows kernel task list / Process Control Block (PCB) |
| **Identifier** | Logical PID string (`P0`, `P1`, `P2`) | Windows numeric PID (e.g., `14280`) |
| **Execution** | Mathematical model in Python memory | Native machine code running on CPU hardware |
| **State transitions** | Updated by Flask algorithms (`READY`, `RUNNING`, `WAITING`, `DEADLOCKED`, `TERMINATED`) | Managed by Windows NT Kernel scheduler |
| **Termination effect** | Sets `state = "TERMINATED"`, adds held integers back to Available pool | Reclaims memory pages, closes OS handles, stops thread execution |

---

## 8. Simulated Resources vs. Real Hardware Resources

| Property | Simulated Resource (e.g., $R_0$) | Real Hardware Resource (e.g., Core i7) |
| :--- | :--- | :--- |
| **Nature** | Integer quantity in database table `resources` | Physical silicon circuit or DRAM capacitor |
| **Capacity** | Set by user or scenario (e.g., `total_instances = 10`) | Fixed hardware specification (e.g., 16 GB DDR4) |
| **Allocation** | Incrementing an integer counter in table `allocations` | Memory Management Unit (MMU) page table mapping or OS lock |
| **Failure Mode** | Algorithm returns `safe: false` or `deadlock: true` | Hardware thermal throttling, OS freeze, out-of-memory crash |

---

## 9. Simulated OS State vs. Real OS State

- **Simulated OS State**: A pure mathematical tuple $(Available, Allocation, Maximum, Need, Request)$. It represents an idealized multi-programming operating system as described in textbooks by Abraham Silberschatz, Peter Galvin, and Greg Gagne.
- **Real OS State**: The actual runtime environment of your physical Windows laptop/desktop (background services, drivers, graphics threads, network sockets).

---

## 10. Complete Data Flow Through the Application

```
   User Browser Interface (Dashboard, Matrices, Graphs, Demos)
                    │
                    │ HTTP Requests (GET / POST / DELETE)
                    ▼
     Flask Web Server & REST API (`routes/api.py`, `app.py`)
                    │
                    │ Dispatches request to Simulation Layer
                    ▼
   Simulation Coordinator (`simulation/simulator.py`, `process_manager.py`)
         │                                          │
         │ Updates/Queries                          │ Invokes Pure Math
         ▼                                          ▼
   SQLite Database (`instance/database.db`)   OS Algorithms (`algorithms/`)
   - `processes`                              - `safety.py` (Banker's Safety)
   - `resources`                              - `resource_request.py` (Request Stepper)
   - `allocations`                            - `deadlock_detection.py` (Detection)
   - `maximum_needs`                          - `wait_for_graph.py` (Cycle Finder)
   - `resource_requests`                      - `recovery.py` (Termination/Preemption)
   - `event_logs`                             - `graph_builder.py` (Cytoscape JSON)
         │                                          │
         └──────────────────┬───────────────────────┘
                            │ Formats JSON Response
                            ▼
              Client Browser Visualizations
        - Cytoscape.js renders interactive graphs (RAG / WFG)
        - Chart.js renders state and utilization charts
        - Dynamic tables render matrices and step-by-step traces
```

---

## Summary for Examiners and Teachers

> "Our project is an educational Operating Systems simulator. The processes ($P_0$–$P_4$) and resources ($R_0$–$R_2$) are mathematical models stored in an SQLite database, allowing us to demonstrate Banker's Algorithm, Deadlock Detection, Resource Allocation Graphs, and Deadlock Recovery with complete transparency and control. The host monitor page using `psutil` is an auxiliary feature demonstrating live hardware inspection, kept strictly separate from the theoretical algorithms."
