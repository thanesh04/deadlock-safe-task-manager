# User Manual & Viva Demonstration Guide

## 1. Quick Start Guide

### Launching the Application
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 2. Navigating the Interface

### Dashboard (`/`)
- **System Safety & Deadlock Cards**: Quick overview of whether the system is SAFE/UNSAFE and if any processes are currently deadlocked.
- **Charts**: Visual distribution of process states (Running, Waiting, Deadlocked) and resource utilization bars (Allocated vs Available).
- **Process Quick Table**: Inspect active tasks, their allocated vectors, and terminate processes with one click.

### System Matrices (`/matrices`)
- Inspect the four core Operating Systems vectors and matrices:
  - **Available Vector**: Current unallocated units of each resource.
  - **Allocation Matrix**: Currently held units per process.
  - **Maximum Demand Matrix**: Upper bound resource claims.
  - **Remaining Need Matrix**: Automatically computed via $\text{Need} = \text{Max} - \text{Allocation}$.

### Safety Analysis (`/safety`)
- Click **RUN SAFETY ALGORITHM** to execute Dijkstra's Safety Algorithm.
- The interface displays the final state (SAFE or UNSAFE) and renders a step-by-step trace showing each process evaluated, the Work vector before/after, and whether it could finish.

### Resource Request (`/resource-request`)
- Select a process and enter a request vector.
- Click **Evaluate & Allocate Request** to view the 5-step stepper:
  1. Check $\text{Request} \le \text{Need}$
  2. Check $\text{Request} \le \text{Available}$
  3. Tentative State Simulation
  4. Safety Algorithm Test
  5. Commit or Rollback Decision

### Deadlock Detection & Recovery (`/deadlock-detection`)
- Click **RUN DEADLOCK DETECTION** to test the system without requiring maximum claims.
- If a deadlock exists, the **Deadlock Recovery Panel** unlocks:
  - **Terminate Victim**: Choose a specific process to terminate and reclaim its resources.
  - **Terminate All Deadlocked**: Resolve the deadlock immediately.
  - **Simulated Resource Preemption**: Transfer resources from a holder to a requester and verify if the deadlock is resolved.

### Graphs (`/graphs`)
- **Resource Allocation Graph (RAG)**: Processes (circles) and Resources (rectangles) with allocation and request edges.
- **Wait-For Graph (WFG)**: Process-to-process wait dependencies with highlighted cycles.
- Interactive controls: Pan, Zoom, Fit, Re-layout, and Node Inspector on click.

### Scenarios & Demo Mode (`/scenarios`)
- 7 built-in textbook scenarios:
  1. Safe State
  2. Unsafe State
  3. Two-Process Circular Deadlock
  4. Three-Process Circular Deadlock
  5. Accepted Resource Request
  6. Denied Resource Request
  7. Deadlock Recovery
- One-click **Demo Mode** buttons in the header for viva presentations.

### Real System Monitor (`/monitor`)
- Live host hardware metrics (CPU, RAM, Swap, Windows Process count) using `psutil`.
- Clearly demarcated from simulated algorithms.
